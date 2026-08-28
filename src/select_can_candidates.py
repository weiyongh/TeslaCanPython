"""按采集脚本中的事件时间，盲选 CAN ID，再用可选 DBC 辅助解释。

候选评分永远来自原始 CAN 数据。DBC 只标记已知 Message，不参与盲分数，
从而让同一套流程可以迁移到没有 DBC 的车型。
"""

from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import cantools

from analyze_driver_window_button import (
    motion_windows,
    penalize_periodic_bits,
    rank_motion_activity,
    stable_windows,
)
from analyze_window_vent import Action, collect, rank_bits
from extract_scripted_signals import Step, parse_asc_line, parse_steps


SUPPORTED_PROFILES = ("generic-event", "window")


@dataclass
class Evidence:
    profile: str
    role: str
    score: float
    frame_id: int
    bit: int | None
    metrics: dict[str, Any] = field(default_factory=dict)


def parse_profiles(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        for item in value.split(","):
            name = item.strip().lower()
            if name and name not in result:
                result.append(name)
    unknown = [name for name in result if name not in SUPPORTED_PROFILES]
    if unknown:
        raise ValueError(
            f"未知 profile：{', '.join(unknown)}；可选：{', '.join(SUPPORTED_PROFILES)}"
        )
    return result or ["generic-event"]


def event_steps(steps: list[Step]) -> list[Step]:
    actions = [step for step in steps if step.is_action]
    return actions or steps


def in_any_window(timestamp: float, windows: list[tuple[float, float]]) -> bool:
    return any(start <= timestamp <= end for start, end in windows)


def periodic_cv(times: list[float]) -> float | None:
    intervals = [right - left for left, right in zip(times, times[1:])]
    if len(intervals) < 3:
        return None
    mean = statistics.fmean(intervals)
    return statistics.pstdev(intervals) / mean if mean else 0.0


def generic_event_evidence(
    raw_series,
    actions: list[Step],
    pre_offset: float,
    post_offset: float,
    *,
    profile: str = "generic-event",
    role: str = "事件附近变化",
) -> list[Evidence]:
    """寻找在多个事件窗口附近重复翻转、但背景翻转较少的 bit。"""
    windows = [(step.time - pre_offset, step.time + post_offset) for step in actions]
    # 事件窗口可能重叠，按区间并集计算真实持续时间，避免重复计时。
    merged_windows: list[list[float]] = []
    for start, end in sorted(windows):
        if merged_windows and start <= merged_windows[-1][1]:
            merged_windows[-1][1] = max(merged_windows[-1][1], end)
        else:
            merged_windows.append([start, end])
    inside_duration = sum(end - start for start, end in merged_windows)
    capture_end = max((item.last_time or 0.0) for item in raw_series.values())
    capture_start = min((item.first_time or 0.0) for item in raw_series.values())
    outside_duration = max(0.001, capture_end - capture_start - inside_duration)
    evidence: list[Evidence] = []
    minimum_hits = 1 if len(actions) == 1 else 2
    for frame_id, item in raw_series.items():
        for bit, times in enumerate(item.bit_transitions):
            if not times:
                continue
            hits = []
            proximity = 0.0
            width = max(pre_offset, post_offset, 1e-6)
            for index, step in enumerate(actions):
                nearby = [time for time in times if windows[index][0] <= time <= windows[index][1]]
                if nearby:
                    nearest = min(nearby, key=lambda time: abs(time - step.time))
                    hits.append(index)
                    proximity += max(0.0, 1.0 - abs(nearest - step.time) / width)
            if len(hits) < minimum_hits:
                continue
            inside = sum(in_any_window(time, windows) for time in times)
            background = len(times) - inside
            inside_rate = inside / max(inside_duration, 0.001)
            outside_rate = background / outside_duration
            enrichment = (inside_rate + 0.01) / (outside_rate + 0.01)
            # 高频计数器会命中几乎所有事件，但事件内外翻转率接近，必须在这里淘汰。
            if enrichment < 3.0 and background > 2:
                continue
            cv = periodic_cv(times)
            coverage = len(hits) / len(actions)
            proximity_ratio = proximity / len(hits)
            enrichment_score = min(1.0, math.log2(max(enrichment, 1.0)) / 5.0)
            cleanliness = inside / max(1, inside + background)
            # 角色内0-100分：只使用该事件组自身作为分母。
            score = (
                coverage * 45.0
                + proximity_ratio * 15.0
                + enrichment_score * 25.0
                + cleanliness * 15.0
            )
            if cv is not None and cv < 0.15:
                score -= 30.0
            if score <= 0:
                continue
            evidence.append(Evidence(
                profile=profile,
                role=role,
                score=score,
                frame_id=frame_id,
                bit=bit,
                metrics={
                    "event_hits": len(hits),
                    "event_total": len(actions),
                    "event_coverage": coverage,
                    "inside_transitions": inside,
                    "outside_transitions": background,
                    "activity_enrichment": enrichment,
                    "period_cv": cv,
                },
            ))
    return sorted(evidence, key=lambda row: (-row.score, row.frame_id, row.bit or 0))


def window_event_groups(actions: list[Step]) -> list[tuple[str, list[Step]]]:
    """按方向、阶段和手动/自动语义建立可重复的车窗事件子组。"""
    buckets: dict[tuple[str, str, str], list[Step]] = defaultdict(list)
    for step in actions:
        title = step.title
        direction = "下降" if "下降" in title else "上升" if "上升" in title else "未知方向"
        phase = "松开" if "松开" in title or "释放" in title else "触发"
        mode = "自动" if "自动" in title or "到底" in title else "手动"
        buckets[(mode, direction, phase)].append(step)

    groups: list[tuple[str, list[Step]]] = []
    seen: set[tuple[float, ...]] = set()

    def add(label: str, items: list[Step]) -> None:
        signature = tuple(step.time for step in items)
        if len(items) >= 2 and signature not in seen:
            groups.append((label, items))
            seen.add(signature)

    for (mode, direction, phase), items in buckets.items():
        add(f"{mode}{direction}{phase}", items)

    # 同一物理方向可能由手动和自动档共用一个原始 bit，因此额外建立跨模式方向组。
    for direction in ("下降", "上升"):
        for phase in ("触发", "松开"):
            items = [
                step for (mode, item_direction, item_phase), values in buckets.items()
                if item_direction == direction and item_phase == phase
                for step in values
            ]
            add(f"{direction}{phase}", sorted(items, key=lambda step: step.time))
    return groups


def window_evidence(raw_series, steps: list[Step], actions: list[Step],
                    pre_offset: float, post_offset: float):
    """车窗 profile：稳定状态、按钮瞬时变化和运动过程分别评分。"""
    stable_ranges = stable_windows(steps)
    motion_ranges = motion_windows(steps)
    evidence: list[Evidence] = []
    for label, group in window_event_groups(actions):
        evidence.extend(generic_event_evidence(
            raw_series, group, pre_offset, post_offset,
            profile="window", role=f"按钮事件:{label}",
        ))
    if stable_ranges:
        raw_actions = [Action(step.time, step.title, "按钮") for step in actions]
        rows = rank_bits(raw_series, stable_ranges, raw_actions,
                         max(pre_offset, post_offset), 0.95)
        rows = penalize_periodic_bits(rows, raw_series)
        for row in rows:
            # 通用事件 profile 已用窗口内外翻转率处理按钮脉冲；这里仅保留
            # window profile 独有的稳定状态证据，避免弱瞬时规则淹没结果。
            if row["category"] != "稳定状态":
                continue
            evidence.append(Evidence(
                profile="window",
                role=row["category"],
                score=row["score"],
                frame_id=row["frame_id"],
                bit=row["bit"],
                metrics={
                    "event_hits": row["hits"],
                    "event_total": len(actions),
                    "outside_transitions": row["unrelated"],
                    "stable_purity": row["purity"],
                },
            ))
    if motion_ranges:
        motion_rows, _ = rank_motion_activity(raw_series, motion_ranges)
        for row in motion_rows:
            evidence.append(Evidence(
                profile="window",
                role="运动过程",
                score=row["score"],
                frame_id=row["frame_id"],
                bit=row["bit"],
                metrics={
                    "event_hits": row["hits"],
                    "event_total": len(motion_ranges),
                    "inside_transitions": row["inside"],
                    "outside_transitions": row["outside"],
                    "activity_enrichment": row["enrichment"],
                },
            ))
    return evidence, stable_ranges, motion_ranges


def aggregate_ids(evidence: list[Evidence]) -> list[dict[str, Any]]:
    """按并集汇总 profile；保留每个来源的独立最高分，不做跨 profile 累加。"""
    groups: dict[int, list[Evidence]] = defaultdict(list)
    for row in evidence:
        groups[row.frame_id].append(row)
    result = []
    for frame_id, rows in groups.items():
        best_by_source: dict[str, Evidence] = {}
        for row in rows:
            key = f"{row.profile}:{row.role}"
            if key not in best_by_source or row.score > best_by_source[key].score:
                best_by_source[key] = row
        best = max(best_by_source.values(), key=lambda row: row.score)
        profiles = sorted({row.profile for row in rows})
        roles = sorted({row.role for row in rows})
        # 并集排序以最佳盲分为主体；多 profile 命中只给小幅证据广度奖励。
        aggregate_score = best.score + max(0, len(profiles) - 1) * 3.0
        result.append({
            "frame_id": frame_id,
            "score": aggregate_score,
            "blind_best_score": best.score,
            "best_bit": best.bit,
            "profiles": profiles,
            "roles": roles,
            "sources": sorted(best_by_source),
            "evidence_count": len(rows),
        })
    return sorted(result, key=lambda row: (-row["score"], row["frame_id"]))


def load_dbc_labels(path: Path | None) -> dict[int, str]:
    if path is None:
        return {}
    database = cantools.database.load_file(path, database_format="dbc", strict=False)
    return {message.frame_id: message.name for message in database.messages}


def write_id_csv(path: Path, rows, dbc_labels: dict[int, str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as target:
        writer = csv.writer(target)
        writer.writerow([
            "rank", "blind_score", "can_id", "profiles", "roles", "best_byte",
            "best_bit_in_byte", "evidence_count", "dbc_known", "dbc_message", "sources",
        ])
        for rank, row in enumerate(rows, 1):
            bit = row["best_bit"]
            writer.writerow([
                rank, f'{row["score"]:.3f}', f'0x{row["frame_id"]:X}',
                "|".join(row["profiles"]), "|".join(row["roles"]),
                "" if bit is None else bit // 8, "" if bit is None else bit % 8,
                row["evidence_count"], "yes" if row["frame_id"] in dbc_labels else "no",
                dbc_labels.get(row["frame_id"], ""), "|".join(row["sources"]),
            ])


def write_evidence_csv(path: Path, rows: list[Evidence], dbc_labels: dict[int, str]) -> None:
    metric_names = sorted({name for row in rows for name in row.metrics})
    columns = ["profile", "role", "score", "can_id", "byte", "bit_in_byte", "dbc_message", *metric_names]
    with path.open("w", encoding="utf-8-sig", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=columns)
        writer.writeheader()
        for row in sorted(rows, key=lambda item: (-item.score, item.frame_id, item.bit or 0)):
            record = {
                "profile": row.profile, "role": row.role, "score": f"{row.score:.3f}",
                "can_id": f"0x{row.frame_id:X}",
                "byte": "" if row.bit is None else row.bit // 8,
                "bit_in_byte": "" if row.bit is None else row.bit % 8,
                "dbc_message": dbc_labels.get(row.frame_id, ""),
            }
            record.update(row.metrics)
            writer.writerow(record)


def write_event_matrix(path: Path, rows, raw_series, actions: list[Step], pre: float, post: float):
    with path.open("w", encoding="utf-8-sig", newline="") as target:
        writer = csv.writer(target)
        headers = [f"{step.time:g}s {step.title}" for step in actions]
        writer.writerow(["rank", "can_id", *headers])
        for rank, row in enumerate(rows, 1):
            item = raw_series[row["frame_id"]]
            values = []
            for step in actions:
                per_bit = [
                    sum(step.time - pre <= timestamp <= step.time + post for timestamp in times)
                    for times in item.bit_transitions
                ]
                changed_bits = sum(count > 0 for count in per_bit)
                transitions = sum(per_bit)
                values.append(f"{changed_bits}bit/{transitions}次")
            writer.writerow([rank, f'0x{row["frame_id"]:X}', *values])


def write_savvycan_slice(path: Path, asc: Path, candidate_ids: set[int], windows):
    """保留 ASC 头信息及候选 ID 在事件小窗口内的帧，时间戳保持原样。"""
    with asc.open("r", encoding="utf-8", errors="ignore") as source, path.open("w", encoding="utf-8") as target:
        for line in source:
            parsed = parse_asc_line(line)
            if parsed is None:
                target.write(line)
                continue
            timestamp, frame_id, _ = parsed
            if frame_id in candidate_ids and in_any_window(timestamp, windows):
                target.write(line)


def write_report(path: Path, args, profiles, steps, actions, rows, evidence, dbc_labels,
                 stable_ranges, motion_ranges, outputs) -> None:
    lines = [
        "# 事件驱动 CAN 候选 ID 报告", "",
        f"- ASC：`{args.asc}`", f"- 采集脚本：`{args.script}`",
        f"- Profile：`{', '.join(profiles)}`",
        f"- 事件偏移：前 {args.pre_offset:g}s / 后 {args.post_offset:g}s",
        f"- 最低盲分阈值：{args.min_blind_score:g}",
        f"- DBC：`{args.dbc if args.dbc else '未提供'}`",
        "- 评分原则：DBC 不参与盲分数，只用于标记已知 Message。", "",
        "## 分轨评分原则", "",
        "- 记录/稳定窗口：评价不同稳定状态的可分性、重复纯度和背景翻转。",
        "- 按钮事件子组：只以同方向、同阶段事件为分母；覆盖率45%、时间接近度15%、活动富集25%、背景纯净度15%。",
        "- 运动窗口：评价运动窗口命中数、窗口内外翻转率和活动富集。",
        "- 综合并集：使用候选在各角色中的最佳盲分，不把所有时间点或不同角色分数直接累加。", "",
        "## 事件时间点", "", "| 时间(s) | 类型 | 描述 |", "|---:|---|---|",
    ]
    action_set = set(actions)
    for step in steps:
        lines.append(f"| {step.time:.3f} | {'事件' if step in action_set else '记录'} | {step.title} |")
    if stable_ranges:
        lines += ["", "## Window稳定窗口", "", "| 状态 | 开始 | 结束 |", "|---|---:|---:|"]
        for start, end, state in stable_ranges:
            lines.append(f"| {state} | {start:.3f} | {end:.3f} |")
    if motion_ranges:
        lines += ["", "## Window运动窗口", "", "| 方向 | 开始 | 结束 |", "|---|---:|---:|"]
        for start, end, direction in motion_ranges:
            lines.append(f"| {direction} | {start:.3f} | {end:.3f} |")
    lines += [
        "", "## 候选 ID 并集", "",
        "多个 profile 独立评分并取并集；`来源` 保留候选由哪个 profile/角色产生。", "",
        "| 排名 | 盲分数 | CAN ID | Profile | 推测角色 | 最佳Byte.Bit | DBC | 来源 |",
        "|---:|---:|---:|---|---|---:|---|---|",
    ]
    for rank, row in enumerate(rows[:args.top], 1):
        bit = row["best_bit"]
        bit_text = "—" if bit is None else f"B{bit // 8}.b{bit % 8}"
        lines.append(
            f'| {rank} | {row["score"]:.2f} | 0x{row["frame_id"]:X} | '
            f'{", ".join(row["profiles"])} | {", ".join(row["roles"])} | {bit_text} | '
            f'{dbc_labels.get(row["frame_id"], "—")} | {", ".join(row["sources"])} |'
        )
    role_tracks = [
        ("按钮事件候选", lambda row: row.role.startswith("按钮事件:")),
        ("运动过程候选", lambda row: row.role == "运动过程"),
        ("稳定状态候选", lambda row: row.role == "稳定状态"),
        ("通用事件候选", lambda row: row.profile == "generic-event"),
    ]
    for title, predicate in role_tracks:
        selected = [row for row in evidence if predicate(row)]
        best_by_id: dict[int, Evidence] = {}
        for row in selected:
            if row.frame_id not in best_by_id or row.score > best_by_id[row.frame_id].score:
                best_by_id[row.frame_id] = row
        ranked = sorted(best_by_id.values(), key=lambda row: (-row.score, row.frame_id))
        if not ranked:
            continue
        lines += ["", f"## {title}", "", "| 排名 | 角色内分数 | CAN ID | Byte.Bit | 命中 | 窗口内/外翻转 | DBC |", "|---:|---:|---:|---:|---:|---:|---|"]
        for rank, row in enumerate(ranked[:10], 1):
            bit_text = "—" if row.bit is None else f"B{row.bit // 8}.b{row.bit % 8}"
            hits = row.metrics.get("event_hits", "—")
            total = row.metrics.get("event_total", "—")
            inside = row.metrics.get("inside_transitions", "—")
            outside = row.metrics.get("outside_transitions", "—")
            lines.append(
                f"| {rank} | {row.score:.2f} | 0x{row.frame_id:X} | {bit_text} | "
                f"{hits}/{total} | {inside}/{outside} | {dbc_labels.get(row.frame_id, '—')} |"
            )
    lines += ["", "## 输出文件", ""]
    lines.extend(f"- `{item}`" for item in outputs)
    lines += [
        "", "## SavvyCAN复核建议", "",
        "1. 加载事件窗口 ASC；该文件只保留排名靠前的候选 ID 和事件附近帧。",
        "2. 在 Frame Data Analysis 中检查最佳 Byte.Bit 所在字节。",
        "3. 在 Flow View 中启用时间戳和窗口同步，核对重复动作是否复现。",
        "4. DBC 命中仅用于解释；未知 ID 仍按盲分数和重复性判断。", "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8-sig")


def main() -> int:
    parser = argparse.ArgumentParser(description="按采集脚本事件时间遴选 CAN ID，支持复合 profile")
    parser.add_argument("asc", type=Path, help="ASC 采集文件（所有输出命名的根）")
    parser.add_argument("script", type=Path, help="带秒数时间点的采集脚本")
    parser.add_argument("--profile", action="append", default=[], help="可重复或逗号分隔：generic-event, window")
    parser.add_argument("--pre-offset", type=float, default=0.5, help="事件前窗口秒数")
    parser.add_argument("--post-offset", type=float, default=1.0, help="事件后窗口秒数")
    parser.add_argument("--dbc", type=Path, help="可选 DBC；只做命中标记，不参与盲评分")
    parser.add_argument("--top", type=int, default=30, help="汇总和 SavvyCAN 切片保留的候选 ID 数")
    parser.add_argument("--min-blind-score", type=float, default=60.0,
                        help="候选 ID 最低综合盲分；默认60")
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    args = parser.parse_args()
    if args.pre_offset < 0 or args.post_offset < 0:
        raise ValueError("时间偏移不能为负数")
    if args.top < 1:
        raise ValueError("--top 必须大于0")
    for path in (args.asc, args.script, args.dbc):
        if path is not None and not path.is_file():
            raise FileNotFoundError(f"输入文件不存在：{path}")

    profiles = parse_profiles(args.profile)
    steps = parse_steps(args.script)
    actions = event_steps(steps)
    # collect 需要窗口来采集稳定统计；取 window profile 的稳定窗口，否则仅采集全局转换。
    window_stable = stable_windows(steps) if "window" in profiles else []
    raw_series, frame_count = collect(args.asc, window_stable)
    evidence: list[Evidence] = []
    stable_ranges, motion_ranges = [], []
    if "generic-event" in profiles:
        evidence.extend(generic_event_evidence(
            raw_series, actions, args.pre_offset, args.post_offset
        ))
    if "window" in profiles:
        window_rows, stable_ranges, motion_ranges = window_evidence(
            raw_series, steps, actions, args.pre_offset, args.post_offset
        )
        evidence.extend(window_rows)
    if not evidence:
        raise ValueError("没有产生候选；请检查时间点、偏移量或更换 profile")

    all_rows = aggregate_ids(evidence)
    rows = [row for row in all_rows if row["score"] >= args.min_blind_score]
    if not rows:
        raise ValueError(
            f"没有候选达到盲分阈值 {args.min_blind_score:g}；请降低 --min-blind-score"
        )
    visible_ids = {row["frame_id"] for row in rows}
    evidence = [row for row in evidence if row.frame_id in visible_ids]
    dbc_labels = load_dbc_labels(args.dbc)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    run_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = f"{args.asc.stem}_{run_stamp}"
    report = args.output_dir / f"{prefix}_候选分析报告.md"
    id_csv = args.output_dir / f"{prefix}_候选ID汇总.csv"
    evidence_csv = args.output_dir / f"{prefix}_候选ByteBit明细.csv"
    matrix_csv = args.output_dir / f"{prefix}_事件矩阵.csv"
    savvycan_asc = args.output_dir / f"{prefix}_SavvyCAN事件窗口.asc"
    write_id_csv(id_csv, rows, dbc_labels)
    write_evidence_csv(evidence_csv, evidence, dbc_labels)
    write_event_matrix(matrix_csv, rows[:args.top], raw_series, actions,
                       args.pre_offset, args.post_offset)
    event_windows = [(step.time - args.pre_offset, step.time + args.post_offset) for step in actions]
    write_savvycan_slice(savvycan_asc, args.asc,
                         {row["frame_id"] for row in rows[:args.top]}, event_windows)
    outputs = [id_csv, evidence_csv, matrix_csv, savvycan_asc]
    write_report(report, args, profiles, steps, actions, rows, evidence, dbc_labels,
                 stable_ranges, motion_ranges, outputs)
    print(
        f"分析完成：{frame_count:,} 帧，阈值前候选 {len(all_rows)} 个，"
        f"盲分>={args.min_blind_score:g} 候选 {len(rows)} 个，profile={','.join(profiles)}"
    )
    print(f"报告：{report}")
    for output in outputs:
        print(f"输出：{output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
