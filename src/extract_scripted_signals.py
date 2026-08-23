"""按标准采集脚本，从 ASC 中自动提取与操作步骤相关的 DBC Signal。

示例：
    python src/extract_scripted_signals.py ^
        input/can_开门关门采集脚本.txt ^
        input/can_20260823164405.asc ^
        input/tesla_model3_ONYX.dbc

默认在 output 目录生成 Markdown 报告和 CSV 明细。
"""

from __future__ import annotations

import argparse
import csv
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import cantools


TIME_LINE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*s\s*(.*)$", re.IGNORECASE)


@dataclass(frozen=True)
class Step:
    time: float
    title: str
    details: tuple[str, ...]
    is_action: bool


@dataclass(frozen=True)
class Sample:
    time: float
    value: Any


@dataclass
class Candidate:
    frame_id: int
    message_name: str
    signal_name: str
    unit: str
    event_rows: list[dict[str, Any]]
    matched_actions: int
    consistency: float
    unrelated_changes: int
    score: float


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            pass
    return path.read_text(encoding="utf-8", errors="replace")


def parse_steps(path: Path) -> list[Step]:
    """解析“时间s + 描述”形式的采集脚本。"""
    blocks: list[tuple[float, list[str]]] = []
    current: tuple[float, list[str]] | None = None

    for raw_line in read_text(path).splitlines():
        line = raw_line.strip()
        match = TIME_LINE.match(line)
        if match:
            if current:
                blocks.append(current)
            current = (float(match.group(1)), [match.group(2).strip()])
        elif current and line:
            current[1].append(line)
    if current:
        blocks.append(current)

    if not blocks:
        raise ValueError(f"采集脚本中没有找到类似 '25s 打开驾驶门' 的时间点：{path}")

    steps: list[Step] = []
    for timestamp, lines in blocks:
        title = lines[0] or "未命名步骤"
        # 只以时间行上的首要指令判断动作，避免把“保持驾驶门打开”误判为开门动作。
        is_action = bool(re.search(r"(?:再次)?(?:打开|关闭|按下|松开|踩下|释放|切换|插入|拔出)", title))
        steps.append(Step(timestamp, title, tuple(lines[1:]), is_action))
    return steps


def parse_asc_line(line: str) -> tuple[float, int, bytes] | None:
    parts = line.split()
    if len(parts) < 7:
        return None
    try:
        timestamp = float(parts[0])
        can_id_text = parts[2].removesuffix("x").removesuffix("X")
        frame_id = int(can_id_text, 16)
    except ValueError:
        return None
    try:
        data_marker = next(i for i, item in enumerate(parts) if item.lower() == "d")
        dlc = int(parts[data_marker + 1])
        data_items = parts[data_marker + 2 : data_marker + 2 + dlc]
        if len(data_items) != dlc:
            return None
        data = bytes(int(item, 16) for item in data_items)
    except (StopIteration, ValueError, IndexError):
        return None
    return timestamp, frame_id, data


def normalized_value(value: Any) -> Any:
    """将 cantools 的枚举值变成可比较、可输出的普通值。"""
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def decode_asc(asc_path: Path, database: cantools.database.Database) -> tuple[dict[tuple[int, str], list[Sample]], int, int]:
    traces: dict[tuple[int, str], list[Sample]] = defaultdict(list)
    frame_count = 0
    decoded_count = 0

    with asc_path.open("r", encoding="utf-8", errors="ignore") as asc_file:
        for line in asc_file:
            parsed = parse_asc_line(line)
            if parsed is None:
                continue
            timestamp, frame_id, data = parsed
            frame_count += 1
            try:
                message = database.get_message_by_frame_id(frame_id)
            except KeyError:
                continue
            if len(data) != message.length:
                continue
            try:
                values = message.decode(data, decode_choices=True, scaling=True)
            except (ValueError, cantools.database.errors.DecodeError):
                continue
            decoded_count += 1
            for name, value in values.items():
                key = (frame_id, name)
                plain_value = normalized_value(value)
                samples = traces[key]
                # 周期报文只保留首次取值和变化点，显著减少内存并直接形成状态轨迹。
                if not samples or samples[-1].value != plain_value:
                    samples.append(Sample(timestamp, plain_value))
    return traces, frame_count, decoded_count


def value_at(samples: list[Sample], timestamp: float) -> Any | None:
    """返回 timestamp 时刻最近一次已知值。"""
    left, right = 0, len(samples)
    while left < right:
        middle = (left + right) // 2
        if samples[middle].time <= timestamp:
            left = middle + 1
        else:
            right = middle
    return samples[left - 1].value if left else None


def changes_near(samples: list[Sample], timestamp: float, tolerance: float) -> list[Sample]:
    return [item for item in samples[1:] if abs(item.time - timestamp) <= tolerance]


def transition_key(before: Any, after: Any) -> tuple[str, str]:
    return str(before), str(after)


def score_candidates(
    traces: dict[tuple[int, str], list[Sample]],
    database: cantools.database.Database,
    actions: list[Step],
    tolerance: float,
    exclude_pattern: re.Pattern[str] | None = None,
) -> list[Candidate]:
    candidates: list[Candidate] = []
    action_times = [step.time for step in actions]

    for (frame_id, signal_name), samples in traces.items():
        if len(samples) < 2:
            continue
        message = database.get_message_by_frame_id(frame_id)
        match_text = f"{message.name}.{signal_name}"
        if exclude_pattern and (
            exclude_pattern.search(signal_name)
            or exclude_pattern.search(message.name)
            or exclude_pattern.search(match_text)
        ):
            continue
        signal = message.get_signal_by_name(signal_name)
        rows: list[dict[str, Any]] = []

        for step in actions:
            nearby = changes_near(samples, step.time, tolerance)
            if nearby:
                nearest = min(nearby, key=lambda item: abs(item.time - step.time))
                before = value_at(samples, nearest.time - 1e-9)
                after = nearest.value
                delta = nearest.time - step.time
                rows.append({
                    "step": step,
                    "matched": True,
                    "change_time": nearest.time,
                    "delta": delta,
                    "before": before,
                    "after": after,
                })
            else:
                rows.append({
                    "step": step,
                    "matched": False,
                    "change_time": None,
                    "delta": None,
                    "before": value_at(samples, step.time - tolerance),
                    "after": value_at(samples, step.time + tolerance),
                })

        matched = sum(row["matched"] for row in rows)
        if matched < 2:
            continue

        # 重复执行同名动作时，相同方向的值变化会提高一致性。
        groups: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for row in rows:
            if row["matched"]:
                title = re.sub(r"^(?:再次|第二次|第\s*\d+\s*次)", "", row["step"].title)
                groups[title].append(transition_key(row["before"], row["after"]))
        consistent_pairs = 0
        possible_pairs = 0
        for transitions in groups.values():
            if len(transitions) > 1:
                possible_pairs += len(transitions)
                consistent_pairs += Counter(transitions).most_common(1)[0][1]
        consistency = consistent_pairs / possible_pairs if possible_pairs else 0.5

        unrelated = sum(
            1 for sample in samples[1:]
            if not any(abs(sample.time - event_time) <= tolerance for event_time in action_times)
        )
        proximity = sum(
            max(0.0, 1.0 - abs(row["delta"]) / tolerance)
            for row in rows if row["matched"]
        )
        name_bonus = 1.5 if re.search(r"door|latch|closure|open|close", signal_name, re.I) else 0.0
        # 高频计数器几乎必然会“碰巧”经过每个动作窗口；对背景变化数采用
        # 对数惩罚，既压低周期计数器，也不过度排斥随动作产生少量波动的模拟量。
        score = matched * 3.0 + proximity + consistency * 3.0 + name_bonus - math.log1p(unrelated) * 1.2
        candidates.append(Candidate(
            frame_id=frame_id,
            message_name=message.name,
            signal_name=signal_name,
            unit=signal.unit or "",
            event_rows=rows,
            matched_actions=matched,
            consistency=consistency,
            unrelated_changes=unrelated,
            score=score,
        ))

    return sorted(candidates, key=lambda item: (-item.score, item.frame_id, item.signal_name))


def display_value(value: Any, unit: str = "") -> str:
    if value is None:
        return "无数据"
    if isinstance(value, float):
        text = f"{value:.6g}" if math.isfinite(value) else str(value)
    else:
        text = str(value)
    return f"{text} {unit}".strip()


def write_csv(path: Path, candidates: Iterable[Candidate]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["rank", "score", "can_id", "message", "signal", "unit", "step_time_s", "step", "matched", "change_time_s", "offset_s", "before", "after"])
        for rank, candidate in enumerate(candidates, 1):
            for row in candidate.event_rows:
                writer.writerow([
                    rank, f"{candidate.score:.3f}", f"0x{candidate.frame_id:X}",
                    candidate.message_name, candidate.signal_name, candidate.unit,
                    f"{row['step'].time:.3f}", row["step"].title,
                    "yes" if row["matched"] else "no",
                    "" if row["change_time"] is None else f"{row['change_time']:.6f}",
                    "" if row["delta"] is None else f"{row['delta']:+.6f}",
                    display_value(row["before"]), display_value(row["after"]),
                ])


def signal_is_excluded(
    pattern: re.Pattern[str] | None, message_name: str, signal_name: str
) -> bool:
    if pattern is None:
        return False
    return bool(
        pattern.search(signal_name)
        or pattern.search(message_name)
        or pattern.search(f"{message_name}.{signal_name}")
    )


def write_message_trace(
    path: Path,
    asc_path: Path,
    message: cantools.database.can.Message,
    start_time: float,
    end_time: float,
    exclude_pattern: re.Pattern[str] | None,
) -> tuple[int, int, int]:
    """输出一个 Message 的全 Signal 变化时间线，并返回帧/解码/事件数。"""
    frame_count = decode_count = event_count = 0
    previous: dict[str, Any] | None = None
    previous_event_time: float | None = None
    output: list[str] = [
        "=" * 120,
        "ASC / DBC Message 全Signal状态时间线",
        "=" * 120,
        f"CAN ID       : 0x{message.frame_id:03X}",
        f"Message Name : {message.name}",
        f"DBC DLC      : {message.length}",
        f"Signal Count : {len(message.signals)}",
        f"时间范围     : {start_time:.3f} ～ {end_time:.3f} 秒",
        f"排除正则     : {exclude_pattern.pattern if exclude_pattern else '-'}",
        "",
    ]

    with asc_path.open("r", encoding="utf-8", errors="ignore") as asc_file:
        for line in asc_file:
            parsed = parse_asc_line(line)
            if parsed is None:
                continue
            timestamp, frame_id, data = parsed
            if timestamp < start_time:
                continue
            if timestamp > end_time:
                break
            if frame_id != message.frame_id:
                continue
            frame_count += 1
            if len(data) != message.length:
                continue
            try:
                decoded = message.decode(data, decode_choices=True, scaling=True)
            except (ValueError, cantools.database.errors.DecodeError):
                continue
            decode_count += 1
            current = {
                name: normalized_value(value)
                for name, value in decoded.items()
                if not signal_is_excluded(exclude_pattern, message.name, name)
            }
            if previous is None:
                output.extend([
                    "=" * 120,
                    f"初始状态 @ {timestamp:.6f} 秒",
                    "=" * 120,
                ])
                for name, value in current.items():
                    output.append(f"{name:<42} = {display_value(value)}")
                output.append("")
                previous = current
                continue

            changes = [
                (name, previous[name], value)
                for name, value in current.items()
                if name in previous and previous[name] != value
            ]
            if changes:
                event_count += 1
                delta = 0.0 if previous_event_time is None else timestamp - previous_event_time
                output.extend([
                    "-" * 120,
                    f"[EVENT {event_count:03d}] TIME = {timestamp:.6f} s    ΔT = {delta:.6f} s",
                    "RAW  = " + " ".join(f"{byte:02X}" for byte in data),
                    "",
                ])
                for name, old_value, new_value in changes:
                    output.append(
                        f"  {name:<40} {display_value(old_value)}  ->  {display_value(new_value)}"
                    )
                output.append("")
                previous_event_time = timestamp
            previous = current

    output.extend([
        "=" * 120,
        "统计",
        "=" * 120,
        f"匹配到该ID帧数 : {frame_count}",
        f"成功解码帧数   : {decode_count}",
        f"状态变化事件数 : {event_count}",
        "=" * 120,
    ])
    path.write_text("\n".join(output) + "\n", encoding="utf-8-sig")
    return frame_count, decode_count, event_count


def write_report(
    path: Path,
    script_path: Path,
    asc_path: Path,
    dbc_path: Path,
    steps: list[Step],
    candidates: list[Candidate],
    tolerance: float,
    frame_count: int,
    decoded_count: int,
) -> None:
    lines = [
        "# ASC 采集步骤与关键信号提取报告", "",
        f"- 采集脚本：`{script_path}`",
        f"- ASC：`{asc_path}`",
        f"- DBC：`{dbc_path}`",
        f"- 动作匹配容差：±{tolerance:g} 秒",
        f"- ASC 数据帧：{frame_count}，DBC 成功解码：{decoded_count}", "",
        "## 采集步骤", "",
        "| 时间(s) | 类型 | 步骤 | 说明 |", "|---:|---|---|---|",
    ]
    for step in steps:
        details = "；".join(step.details).replace("|", "\\|")
        lines.append(f"| {step.time:g} | {'关键动作' if step.is_action else '记录/保持'} | {step.title} | {details} |")

    lines.extend(["", "## 候选关键信号排名", "",
                  "候选信号按动作命中数、时间接近程度、重复动作一致性及背景变化量综合排序。", "",
                  "| 排名 | 得分 | CAN ID | Message | Signal | 动作命中 | 一致性 | 背景变化 |",
                  "|---:|---:|---:|---|---|---:|---:|---:|"])
    for rank, item in enumerate(candidates, 1):
        lines.append(f"| {rank} | {item.score:.2f} | 0x{item.frame_id:X} | {item.message_name} | {item.signal_name} | {item.matched_actions}/{len([s for s in steps if s.is_action])} | {item.consistency:.0%} | {item.unrelated_changes} |")

    lines.extend(["", "## 关键步骤对应 Signal 数据", ""])
    for rank, item in enumerate(candidates, 1):
        lines.extend([
            f"### {rank}. 0x{item.frame_id:X} / {item.message_name} / {item.signal_name}", "",
            "| 脚本时间(s) | 步骤 | 实际变化时间(s) | 偏移(s) | 变化前 | 变化后 |",
            "|---:|---|---:|---:|---|---|",
        ])
        for row in item.event_rows:
            change_time = "—" if row["change_time"] is None else f"{row['change_time']:.6f}"
            delta = "—" if row["delta"] is None else f"{row['delta']:+.6f}"
            lines.append(f"| {row['step'].time:g} | {row['step'].title} | {change_time} | {delta} | {display_value(row['before'], item.unit)} | {display_value(row['after'], item.unit)} |")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8-sig")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="根据标准采集脚本，从 ASC 自动筛选动作相关 DBC Signal")
    parser.add_argument("script", type=Path, help="标准采集脚本 txt 文件")
    parser.add_argument("asc", type=Path, help="原始 CAN ASC 文件")
    parser.add_argument("dbc", type=Path, help="DBC 文件")
    parser.add_argument("--output-dir", type=Path, default=Path("output"), help="输出目录（默认 output）")
    parser.add_argument("--tolerance", type=float, default=2.0, help="动作点前后匹配容差秒数（默认 2）")
    parser.add_argument("--top", type=int, default=10, help="最多输出候选 Signal 数（默认 10）")
    parser.add_argument(
        "--exclude-regex",
        help="排除 Message/Signal 的正则表达式，例如 'mirrorTilt|temperature'",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    for path in (args.script, args.asc, args.dbc):
        if not path.is_file():
            raise FileNotFoundError(f"输入文件不存在：{path}")
    if args.tolerance <= 0 or args.top <= 0:
        raise ValueError("--tolerance 和 --top 必须大于 0")
    try:
        exclude_pattern = re.compile(args.exclude_regex, re.IGNORECASE) if args.exclude_regex else None
    except re.error as error:
        raise ValueError(f"--exclude-regex 不是有效的正则表达式：{error}") from error

    steps = parse_steps(args.script)
    actions = [step for step in steps if step.is_action]
    if not actions:
        raise ValueError("采集脚本中没有识别出关键动作")
    database = cantools.database.load_file(args.dbc, database_format="dbc", strict=False)
    traces, frame_count, decoded_count = decode_asc(args.asc, database)
    candidates = score_candidates(
        traces, database, actions, args.tolerance, exclude_pattern
    )[: args.top]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    stem = args.asc.stem
    report_path = args.output_dir / f"{stem}_关键步骤信号报告.md"
    csv_path = args.output_dir / f"{stem}_关键步骤信号明细.csv"
    write_report(report_path, args.script, args.asc, args.dbc, steps, candidates, args.tolerance, frame_count, decoded_count)
    write_csv(csv_path, candidates)

    trace_path: Path | None = None
    if candidates:
        trace_message = database.get_message_by_frame_id(candidates[0].frame_id)
        run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        trace_path = args.output_dir / (
            f"asc_dbc_message_trace_{stem}_0x{trace_message.frame_id:X}_{run_timestamp}.txt"
        )
        write_message_trace(
            trace_path,
            args.asc,
            trace_message,
            min(step.time for step in steps),
            max(step.time for step in steps),
            exclude_pattern,
        )

    print(f"采集步骤：{len(steps)}，关键动作：{len(actions)}")
    print(f"ASC 数据帧：{frame_count}，DBC 成功解码：{decoded_count}")
    print(f"候选 Signal：{len(candidates)}")
    print(f"报告：{report_path}")
    print(f"明细：{csv_path}")
    if trace_path:
        print(f"Message追踪：{trace_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
