"""驾驶门物理按钮开关窗：DBC Signal 与未知 CAN ID 混合分析。"""

from __future__ import annotations

import argparse
import csv
import math
import re
import statistics
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import cantools

from analyze_window_vent import Action, collect, rank_bits
from extract_scripted_signals import (
    Candidate,
    parse_asc_line,
    parse_steps,
    score_candidates,
    write_csv,
    write_message_trace,
    write_report,
)
from extract_window_signals import (
    decode_window_signals,
    inspect_asc,
    prepare_window_messages,
)


def parse_can_id(text: str) -> int:
    return int(text.strip().lower().removeprefix("0x"), 16)


def stable_windows(steps) -> list[tuple[float, float, str]]:
    """从“稳定状态开始”记录点建立窗口，并映射为关闭/通风两类。"""
    result = []
    for index, step in enumerate(steps):
        if "稳定状态" not in step.title:
            continue
        if "全关" in step.title:
            state = "关闭"
        elif "全开" in step.title or "部分开启" in step.title:
            state = "通风"  # 复用通用二态盲分析器；此处泛指“非全关”。
        else:
            continue
        next_time = steps[index + 1].time if index + 1 < len(steps) else step.time + 8
        start, end = step.time + 1.0, next_time - 1.0
        if end > start:
            result.append((start, end, state))
    return result


def motion_windows(steps) -> list[tuple[float, float, str]]:
    """从每次按钮按下到下一稳定记录建立玻璃执行过程窗口。"""
    result = []
    for index, step in enumerate(steps):
        if not step.is_action or not ("按下" in step.title or "提起" in step.title):
            continue
        direction = "下降" if "下降" in step.title else "上升" if "上升" in step.title else "未知"
        following_stable = next(
            (item for item in steps[index + 1:] if "稳定状态" in item.title), None
        )
        if following_stable and following_stable.time > step.time:
            result.append((step.time, following_stable.time, direction))
    return result


def raw_id_trace(asc_path: Path, frame_id: int):
    frame_count = 0
    dlcs: Counter[int] = Counter()
    first: tuple[float, bytes] | None = None
    previous: bytes | None = None
    changes: list[tuple[float, bytes, bytes]] = []
    with asc_path.open("r", encoding="utf-8", errors="ignore") as source:
        for line in source:
            parsed = parse_asc_line(line)
            if parsed is None:
                continue
            timestamp, current_id, data = parsed
            if current_id != frame_id:
                continue
            frame_count += 1
            dlcs[len(data)] += 1
            if first is None:
                first = (timestamp, data)
            if previous is not None and previous != data:
                changes.append((timestamp, previous, data))
            previous = data
    return frame_count, dlcs, first, changes


def stable_payloads(asc_path: Path, frame_id: int, windows):
    counters = [Counter() for _ in windows]
    with asc_path.open("r", encoding="utf-8", errors="ignore") as source:
        for line in source:
            parsed = parse_asc_line(line)
            if parsed is None:
                continue
            timestamp, current_id, data = parsed
            if current_id != frame_id:
                continue
            for index, (start, end, _) in enumerate(windows):
                if start <= timestamp <= end:
                    counters[index][data] += 1
                    break
    rows = []
    for window, values in zip(windows, counters):
        if values:
            payload, count = values.most_common(1)[0]
            rows.append((*window, payload, count / sum(values.values()), sum(values.values())))
        else:
            rows.append((*window, None, 0.0, 0))
    return rows


def write_blind_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    columns = ["rank", "score", "category", "can_id", "dlc", "byte", "bit_in_byte",
               "closed_value", "open_value", "stable_purity", "action_hits",
               "unrelated_transitions", "median_delay_s"]
    with path.open("w", encoding="utf-8-sig", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=columns)
        writer.writeheader()
        for rank, row in enumerate(rows, 1):
            writer.writerow({
                "rank": rank, "score": f'{row["score"]:.3f}', "category": row["category"],
                "can_id": f'0x{row["frame_id"]:X}', "dlc": row["dlc"], "byte": row["byte"],
                "bit_in_byte": row["bit_in_byte"], "closed_value": row["closed"],
                "open_value": row["vent"], "stable_purity": f'{row["purity"]:.4f}',
                "action_hits": row["hits"], "unrelated_transitions": row["unrelated"],
                "median_delay_s": "" if row["delay"] is None else f'{row["delay"]:.6f}',
            })


def penalize_periodic_bits(rows, raw_series):
    """降低等周期计数器/时钟位权重，防止其碰巧匹配交替稳定窗口。"""
    for row in rows:
        times = raw_series[row["frame_id"]].bit_transitions[row["bit"]]
        intervals = [right - left for left, right in zip(times, times[1:])]
        if len(intervals) < 3:
            row["period_cv"] = None
            continue
        mean = statistics.fmean(intervals)
        cv = statistics.pstdev(intervals) / mean if mean else 0.0
        row["period_cv"] = cv
        if cv < 0.15:
            row["score"] -= 60.0
            row["category"] = "周期字段（降权）"
    return sorted(rows, key=lambda row: (-row["score"], row["frame_id"], row["bit"]))


def rank_motion_activity(raw_series, windows):
    """筛选翻转活动集中在升降执行窗口内的 bit，并按 CAN ID 汇总。"""
    if not windows:
        return [], []
    end_time = max((item.last_time or 0.0) for item in raw_series.values())
    inside_duration = sum(end - start for start, end, _ in windows)
    outside_duration = max(0.001, end_time - inside_duration)
    rows = []
    for frame_id, item in raw_series.items():
        for bit, times in enumerate(item.bit_transitions):
            hits, inside, outside = set(), 0, 0
            for timestamp in times:
                matched = next((i for i, (start, end, _) in enumerate(windows)
                                if start <= timestamp <= end), None)
                if matched is None:
                    outside += 1
                else:
                    inside += 1
                    hits.add(matched)
            if len(hits) < max(3, len(windows) - 1) or inside < 4:
                continue
            inside_rate = inside / inside_duration
            outside_rate = outside / outside_duration
            enrichment = (inside_rate + .01) / (outside_rate + .01)
            if enrichment < 4:
                continue
            intervals = [right - left for left, right in zip(times, times[1:])]
            if len(intervals) >= 3:
                mean = statistics.fmean(intervals)
                cv = statistics.pstdev(intervals) / mean if mean else 0.0
                if cv < .15:
                    continue
            score = len(hits) * 10 + min(30, math.log2(enrichment) * 5) - math.log1p(outside) * 2
            rows.append({"score": score, "frame_id": frame_id, "bit": bit,
                         "byte": bit // 8, "bit_in_byte": bit % 8,
                         "hits": len(hits), "inside": inside, "outside": outside,
                         "enrichment": enrichment})
    rows.sort(key=lambda row: (-row["score"], row["frame_id"], row["bit"]))
    grouped = {}
    for row in rows:
        group = grouped.setdefault(row["frame_id"], {
            "frame_id": row["frame_id"], "score": row["score"],
            "responsive_bits": 0, "max_hits": row["hits"],
            "max_enrichment": row["enrichment"], "best_bit": row["bit"],
            "inside": row["inside"], "outside": row["outside"],
        })
        group["responsive_bits"] += 1
        group["max_enrichment"] = max(group["max_enrichment"], row["enrichment"])
    groups = sorted(grouped.values(), key=lambda row: (-row["score"], row["frame_id"]))
    return rows, groups


def write_motion_csv(path: Path, rows) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(["rank", "score", "can_id", "byte", "bit_in_byte", "motion_hits",
                         "inside_transitions", "outside_transitions", "activity_enrichment"])
        for rank, row in enumerate(rows, 1):
            writer.writerow([rank, f'{row["score"]:.3f}', f'0x{row["frame_id"]:X}',
                             row["byte"], row["bit_in_byte"], row["hits"], row["inside"],
                             row["outside"], f'{row["enrichment"]:.3f}'])


def append_hybrid_report(report_path, windows, blind_rows, motion_ranges, motion_groups,
                         verify_id, verify_stats, stable_rows, action_count):
    frame_count, dlcs, first, changes = verify_stats
    stable_candidates = [row for row in blind_rows if row["category"] == "稳定状态"]
    transient_candidates = [row for row in blind_rows if row["category"] == "瞬时请求候选"]
    lines = [
        "", "## 无 DBC 稳定状态 bit 候选", "",
        "该排名使用脚本中的全关、部分开启和全开稳定区间，并排除检测到的等周期字段。`Byte.Bit` 从 0 开始，Bit 0 为最低位。", "",
        "| 排名 | 得分 | CAN ID | Byte.Bit | 全关 | 非全关 | 稳定纯度 | 动作命中 | 背景翻转 |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, row in enumerate(stable_candidates[:30], 1):
        lines.append(
            f'| {rank} | {row["score"]:.2f} | 0x{row["frame_id"]:X} | '
            f'B{row["byte"]}.b{row["bit_in_byte"]} | {row["closed"]} | {row["vent"]} | '
            f'{row["purity"]:.1%} | {row["hits"]}/{action_count} | {row["unrelated"]} |'
        )
    if not stable_candidates:
        lines.append("| — | — | — | — | — | — | — | — | — |")
        lines.extend(["", "本次没有找到同时满足全部全关/非全关稳定窗口、且排除周期特征后的高可信未知 bit。"])
    lines.extend([
        "", "### 动作附近瞬时 bit（低可信辅助项）", "",
        "这些 bit 只因在密集的按钮动作窗口附近变化而入选，可能包含计数器、校验和和总线活动，不应直接命名为车窗 Signal。", "",
        "| 排名 | 得分 | CAN ID | Byte.Bit | 动作命中 | 背景翻转 |",
        "|---:|---:|---:|---:|---:|---:|",
    ])
    for rank, row in enumerate(transient_candidates[:10], 1):
        lines.append(f'| {rank} | {row["score"]:.2f} | 0x{row["frame_id"]:X} | B{row["byte"]}.b{row["bit_in_byte"]} | {row["hits"]}/{action_count} | {row["unrelated"]} |')
    lines.extend([
        "", "## 按钮后的升降执行过程分析", "",
        "该分析比较运动窗口和非运动时间的 bit 翻转率，不要求最终稳定值不同。富集倍数越高，活动越集中在玻璃运动期间。", "",
        "### 运动窗口", "", "| 方向 | 开始(s) | 结束(s) |", "|---|---:|---:|",
    ])
    for start, end, direction in motion_ranges:
        lines.append(f"| {direction} | {start:.3f} | {end:.3f} |")
    lines.extend([
        "", "### 执行过程候选 CAN ID", "",
        "| 排名 | CAN ID | 最佳Byte.Bit | 得分 | 运动命中 | 最大富集 | 响应bit数 | 窗口内翻转 | 窗口外翻转 |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for rank, row in enumerate(motion_groups[:20], 1):
        lines.append(
            f'| {rank} | 0x{row["frame_id"]:X} | B{row["best_bit"]//8}.b{row["best_bit"]%8} | '
            f'{row["score"]:.2f} | {row["max_hits"]}/{len(motion_ranges)} | {row["max_enrichment"]:.1f}× | '
            f'{row["responsive_bits"]} | {row["inside"]} | {row["outside"]} |'
        )
    lines.extend([
        "", "> 这些是电机、编码器、速度、电流或关联校验字段的候选，不等同于已经确认的玻璃位置 ID。",
        "> 同一报文内需要继续区分真实数据字段、滚动计数器和校验和。", "",
    ])
    lines.extend([
        "", f"## 指定未知 ID 核验：0x{verify_id:X}", "",
        f"- 帧数：{frame_count:,}",
        f"- DLC：{', '.join(f'{dlc}({count}帧)' for dlc, count in dlcs.most_common()) or '无数据'}",
        f"- 初始帧：{'无数据' if first is None else f'{first[0]:.6f}s / {first[1].hex(" ").upper()}'}",
        f"- Payload 变化事件：{len(changes)}", "",
        "### 稳定窗口主 Payload", "",
        "| 预期状态 | 开始(s) | 结束(s) | 主 Payload | 纯度 | 帧数 |",
        "|---|---:|---:|---|---:|---:|",
    ])
    for start, end, state, payload, purity, count in stable_rows:
        raw = "—" if payload is None else payload.hex(" ").upper()
        lines.append(f"| {'全关' if state == '关闭' else '非全关'} | {start:.3f} | {end:.3f} | {raw} | {purity:.1%} | {count} |")
    lines.extend(["", "### Payload 变化时间线", "", "| 时间(s) | 变化前 | 变化后 | XOR |", "|---:|---|---|---|"])
    for timestamp, before, after in changes:
        xor = int.from_bytes(before, "little") ^ int.from_bytes(after, "little")
        lines.append(f'| {timestamp:.6f} | {before.hex(" ").upper()} | {after.hex(" ").upper()} | 0x{xor:0{len(after)*2}X} |')
    lines.extend([
        "", "### 核验原则", "",
        "- 指定 ID 即使未被 DBC 收录也会完整报告，不会被丢弃。",
        "- 如果脚本标记为全关但 Payload 仍呈现非全关值，报告保留该矛盾，不会强行修正。",
        "- DBC Signal 用于确认按钮输入；未知 bit 用于寻找位置、运动或汇总状态，两类证据分开呈现。", "",
    ])
    with report_path.open("a", encoding="utf-8") as target:
        target.write("\n".join(lines))


def write_raw_trace(path: Path, frame_id: int, stats) -> None:
    frame_count, dlcs, first, changes = stats
    lines = [f"CAN ID: 0x{frame_id:X}", f"帧数: {frame_count}",
             f"DLC: {dict(dlcs)}", ""]
    if first:
        lines.append(f"初始 {first[0]:.6f}s  {first[1].hex(' ').upper()}")
    for timestamp, before, after in changes:
        xor = int.from_bytes(before, "little") ^ int.from_bytes(after, "little")
        lines.append(f'{timestamp:.6f}s  {before.hex(" ").upper()} -> {after.hex(" ").upper()}  XOR=0x{xor:0{len(after)*2}X}')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def main() -> int:
    parser = argparse.ArgumentParser(description="驾驶门物理按钮开关窗的 DBC + 未知 ID 混合分析")
    parser.add_argument("script", type=Path)
    parser.add_argument("asc", type=Path)
    parser.add_argument("dbc", type=Path)
    parser.add_argument("--verify-id", default="0x1FA", help="额外核验的未定义 CAN ID")
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    parser.add_argument("--tolerance", type=float, default=2.0)
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args()
    for path in (args.script, args.asc, args.dbc):
        if not path.is_file():
            raise FileNotFoundError(f"输入文件不存在：{path}")
    verify_id = parse_can_id(args.verify_id)
    steps = parse_steps(args.script)
    action_steps = [step for step in steps if step.is_action]
    windows = stable_windows(steps)
    motion_ranges = motion_windows(steps)
    if not action_steps or not windows:
        raise ValueError("采集脚本中没有识别出动作或稳定状态窗口")

    database = cantools.database.load_file(args.dbc, database_format="dbc", strict=False)
    frame_count, observed_dlcs = inspect_asc(args.asc)
    window_messages, _ = prepare_window_messages(database, observed_dlcs)
    dbc_traces, decoded_count = decode_window_signals(args.asc, window_messages)
    dbc_candidates: list[Candidate] = score_candidates(
        dbc_traces, database, action_steps, args.tolerance, None
    )[:args.top]

    raw_series, _ = collect(args.asc, windows)
    raw_actions = [Action(step.time, step.title, "按钮") for step in action_steps]
    blind_rows = rank_bits(raw_series, windows, raw_actions, args.tolerance, .95)
    blind_rows = penalize_periodic_bits(blind_rows, raw_series)
    motion_rows, motion_groups = rank_motion_activity(raw_series, motion_ranges)
    verify_stats = raw_id_trace(args.asc, verify_id)
    stable_rows = stable_payloads(args.asc, verify_id, windows)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    stem = args.asc.stem
    report = args.output_dir / f"{stem}_驾驶窗按钮混合分析报告.md"
    dbc_csv = args.output_dir / f"{stem}_驾驶窗DBC信号明细.csv"
    blind_csv = args.output_dir / f"{stem}_驾驶窗未知bit候选.csv"
    motion_csv = args.output_dir / f"{stem}_驾驶窗执行过程候选.csv"
    raw_trace = args.output_dir / f"{stem}_0x{verify_id:X}_原始变化追踪.txt"
    write_report(report, args.script, args.asc, args.dbc, steps, dbc_candidates,
                 args.tolerance, frame_count, decoded_count)
    append_hybrid_report(report, windows, blind_rows, motion_ranges, motion_groups,
                         verify_id, verify_stats,
                         stable_rows, len(action_steps))
    write_csv(dbc_csv, dbc_candidates)
    write_blind_csv(blind_csv, blind_rows)
    write_motion_csv(motion_csv, motion_rows)
    write_raw_trace(raw_trace, verify_id, verify_stats)

    message_trace = None
    if dbc_candidates:
        message = database.get_message_by_frame_id(dbc_candidates[0].frame_id)
        message_trace = args.output_dir / (
            f"asc_dbc_driver_window_trace_{stem}_0x{message.frame_id:X}_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        write_message_trace(message_trace, args.asc, message,
                            min(s.time for s in steps), max(s.time for s in steps), None)
    print(f"ASC帧：{frame_count:,}，DBC Window候选：{len(dbc_candidates)}，未知bit候选：{len(blind_rows)}，执行过程ID：{len(motion_groups)}")
    print(f"报告：{report}\nDBC明细：{dbc_csv}\n未知bit明细：{blind_csv}\n执行过程明细：{motion_csv}\n0x{verify_id:X}追踪：{raw_trace}")
    if message_trace:
        print(f"DBC Message追踪：{message_trace}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
