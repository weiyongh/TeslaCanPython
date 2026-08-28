"""无 DBC 分析车窗通风 ASC，筛选可重复、可逆的 CAN 字节和 bit。

示例：
    python src/analyze_window_vent.py \
        input/can_车窗通风采集脚本.txt input/can_20260824154441.asc
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from statistics import median


TIME_LINE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*s\s*(.*)$", re.I)


@dataclass(frozen=True)
class Action:
    time: float
    title: str
    kind: str


@dataclass
class FrameSeries:
    dlc_counts: Counter[int] = field(default_factory=Counter)
    count: int = 0
    first_time: float | None = None
    last_time: float | None = None
    previous: bytes | None = None
    bit_transitions: list[list[float]] = field(default_factory=list)
    window_bit_ones: dict[int, list[int]] = field(default_factory=dict)
    window_bit_totals: dict[int, list[int]] = field(default_factory=dict)
    window_bytes: dict[int, list[Counter[int]]] = field(default_factory=dict)


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def parse_actions(path: Path) -> tuple[list[Action], float]:
    points: list[tuple[float, str]] = []
    for line in read_text(path).splitlines():
        match = TIME_LINE.match(line)
        if match:
            points.append((float(match.group(1)), match.group(2).strip()))
    if not points:
        raise ValueError(f"采集脚本中没有找到时间点：{path}")
    actions: list[Action] = []
    for timestamp, title in points:
        if re.search(r"打开.*(?:车窗|通风)|(?:车窗|通风).*打开", title):
            actions.append(Action(timestamp, title, "通风"))
        elif re.search(r"关闭.*车窗|车窗.*关闭", title):
            actions.append(Action(timestamp, title, "关闭"))
    if not any(a.kind == "通风" for a in actions) or not any(a.kind == "关闭" for a in actions):
        raise ValueError("没有同时识别到通风和关闭动作")
    return actions, max(time for time, _ in points)


def parse_asc_line(line: str) -> tuple[float, int, bytes] | None:
    parts = line.split()
    if len(parts) < 7:
        return None
    try:
        timestamp = float(parts[0])
        frame_id = int(parts[2].rstrip("xX"), 16)
        marker = next(i for i, value in enumerate(parts) if value.lower() == "d")
        dlc = int(parts[marker + 1])
        raw = parts[marker + 2:marker + 2 + dlc]
        if len(raw) != dlc:
            return None
        return timestamp, frame_id, bytes(int(value, 16) for value in raw)
    except (ValueError, StopIteration, IndexError):
        return None


def make_state_windows(actions: list[Action], end_time: float, settle: float, edge: float):
    """动作前后留出边缘，建立交替的全关/通风稳定窗口。"""
    ordered = sorted(actions, key=lambda item: item.time)
    windows: list[tuple[float, float, str]] = []
    state = "关闭"
    cursor = 0.0
    for action in ordered:
        start, end = cursor + edge, action.time - edge
        if end > start:
            windows.append((start, end, state))
        cursor = action.time + settle
        state = action.kind
    if end_time - edge > cursor:
        windows.append((cursor, end_time - edge, state))
    return windows


def active_window(timestamp: float, windows: list[tuple[float, float, str]]) -> int | None:
    for index, (start, end, _) in enumerate(windows):
        if start <= timestamp <= end:
            return index
    return None


def collect(asc: Path, windows: list[tuple[float, float, str]]) -> tuple[dict[int, FrameSeries], int]:
    series: dict[int, FrameSeries] = defaultdict(FrameSeries)
    total = 0
    with asc.open("r", encoding="utf-8", errors="ignore") as source:
        for line in source:
            parsed = parse_asc_line(line)
            if parsed is None:
                continue
            timestamp, frame_id, data = parsed
            total += 1
            item = series[frame_id]
            item.count += 1
            item.dlc_counts[len(data)] += 1
            item.first_time = timestamp if item.first_time is None else item.first_time
            item.last_time = timestamp
            bits = len(data) * 8
            if len(item.bit_transitions) < bits:
                item.bit_transitions.extend([] for _ in range(bits - len(item.bit_transitions)))
            if item.previous is not None and len(item.previous) == len(data):
                xor = int.from_bytes(item.previous, "little") ^ int.from_bytes(data, "little")
                for bit in range(bits):
                    if xor & (1 << bit):
                        item.bit_transitions[bit].append(timestamp)
            item.previous = data

            index = active_window(timestamp, windows)
            if index is not None:
                ones = item.window_bit_ones.setdefault(index, [])
                totals = item.window_bit_totals.setdefault(index, [])
                byte_counts = item.window_bytes.setdefault(index, [])
                if len(ones) < bits:
                    ones.extend([0] * (bits - len(ones)))
                    totals.extend([0] * (bits - len(totals)))
                if len(byte_counts) < len(data):
                    byte_counts.extend(Counter() for _ in range(len(data) - len(byte_counts)))
                value = int.from_bytes(data, "little")
                for bit in range(bits):
                    ones[bit] += (value >> bit) & 1
                    totals[bit] += 1
                for byte_index, byte in enumerate(data):
                    byte_counts[byte_index][byte] += 1
    return series, total


def majority_bit(item: FrameSeries, window: int, bit: int) -> tuple[int, float] | None:
    totals = item.window_bit_totals.get(window)
    if not totals or bit >= len(totals) or totals[bit] == 0:
        return None
    ratio = item.window_bit_ones[window][bit] / totals[bit]
    return (1 if ratio >= 0.5 else 0), max(ratio, 1 - ratio)


def nearby_transitions(times: list[float], action: Action, response: float) -> list[float]:
    return [value for value in times if action.time - 0.25 <= value <= action.time + response]


def rank_bits(series, windows, actions, response, min_purity):
    rows = []
    vent_windows = [i for i, value in enumerate(windows) if value[2] == "通风"]
    close_windows = [i for i, value in enumerate(windows) if value[2] == "关闭"]
    action_ranges = [(a.time - .25, a.time + response) for a in actions]
    for frame_id, item in series.items():
        for bit, transitions in enumerate(item.bit_transitions):
            states = {i: majority_bit(item, i, bit) for i in range(len(windows))}
            if any(states[i] is None for i in vent_windows + close_windows):
                continue
            vent_values = [states[i][0] for i in vent_windows]
            close_values = [states[i][0] for i in close_windows]
            purities = [states[i][1] for i in vent_windows + close_windows]
            reversible = len(set(vent_values)) == len(set(close_values)) == 1 and vent_values[0] != close_values[0]
            hits = [nearby_transitions(transitions, action, response) for action in actions]
            hit_count = sum(bool(value) for value in hits)
            unrelated = sum(not any(start <= value <= end for start, end in action_ranges) for value in transitions)
            if not reversible and hit_count < max(2, len(actions) - 1):
                continue
            purity = sum(purities) / len(purities)
            if reversible and purity >= min_purity:
                delays = [min(values, key=lambda t: abs(t - action.time)) - action.time for values, action in zip(hits, actions) if values]
                score = 60 + purity * 20 + hit_count * 5 - min(20, unrelated * .15)
                category = "稳定状态"
            else:
                # 短脉冲候选：重复命中动作，但稳定区间不要求保持不同状态。
                delays = [min(values) - action.time for values, action in zip(hits, actions) if values]
                score = hit_count * 8 - min(20, unrelated * .2)
                category = "瞬时请求候选"
            rows.append({
                "score": score, "category": category, "frame_id": frame_id,
                "dlc": item.dlc_counts.most_common(1)[0][0], "bit": bit,
                "byte": bit // 8, "bit_in_byte": bit % 8,
                "closed": close_values[0] if len(set(close_values)) == 1 else "不一致",
                "vent": vent_values[0] if len(set(vent_values)) == 1 else "不一致",
                "purity": purity, "hits": hit_count, "unrelated": unrelated,
                "delay": median(delays) if delays else None,
            })
    return sorted(rows, key=lambda row: (-row["score"], row["frame_id"], row["bit"]))


def rank_bytes(series, windows, min_purity):
    rows = []
    vent_windows = [i for i, value in enumerate(windows) if value[2] == "通风"]
    close_windows = [i for i, value in enumerate(windows) if value[2] == "关闭"]
    for frame_id, item in series.items():
        dlc = item.dlc_counts.most_common(1)[0][0]
        for byte_index in range(dlc):
            values, purities = {}, {}
            valid = True
            for i in vent_windows + close_windows:
                counters = item.window_bytes.get(i)
                if not counters or byte_index >= len(counters) or not counters[byte_index]:
                    valid = False
                    break
                value, count = counters[byte_index].most_common(1)[0]
                values[i] = value
                purities[i] = count / sum(counters[byte_index].values())
            if not valid:
                continue
            vent = [values[i] for i in vent_windows]
            close = [values[i] for i in close_windows]
            purity = sum(purities.values()) / len(purities)
            if len(set(vent)) == len(set(close)) == 1 and vent[0] != close[0] and purity >= min_purity:
                rows.append({"score": 50 + purity * 20, "frame_id": frame_id, "dlc": dlc,
                             "byte": byte_index, "closed": close[0], "vent": vent[0], "purity": purity})
    return sorted(rows, key=lambda row: (-row["score"], row["frame_id"], row["byte"]))


def write_outputs(report_path, csv_path, script, asc, windows, actions, bits, byte_rows, total, top):
    with csv_path.open("w", encoding="utf-8-sig", newline="") as target:
        columns = ["rank", "score", "category", "can_id", "dlc", "byte", "bit_in_byte", "absolute_bit",
                   "closed_value", "vent_value", "stable_purity", "action_hits", "unrelated_transitions", "median_delay_s"]
        writer = csv.DictWriter(target, fieldnames=columns)
        writer.writeheader()
        for rank, row in enumerate(bits, 1):
            writer.writerow({"rank": rank, "score": f'{row["score"]:.2f}', "category": row["category"],
                             "can_id": f'0x{row["frame_id"]:X}', "dlc": row["dlc"], "byte": row["byte"],
                             "bit_in_byte": row["bit_in_byte"], "absolute_bit": row["bit"],
                             "closed_value": row["closed"], "vent_value": row["vent"],
                             "stable_purity": f'{row["purity"]:.4f}', "action_hits": row["hits"],
                             "unrelated_transitions": row["unrelated"],
                             "median_delay_s": "" if row["delay"] is None else f'{row["delay"]:.6f}'})
    lines = ["# 车窗通风 CAN 无 DBC 分析报告", "", f"- 采集脚本：`{script}`", f"- ASC：`{asc}`",
             f"- 有效 CAN 帧：{total:,}", "", "## 稳定分析窗口", "",
             "| 状态 | 开始(s) | 结束(s) |", "|---|---:|---:|"]
    for start, end, state in windows:
        lines.append(f"| {state} | {start:.3f} | {end:.3f} |")
    lines += ["", "## bit 候选排名", "",
              "`Byte` 和 `Bit` 均从 0 开始；Bit 是该 Byte 内的位序（LSB=0）。", "",
              "| 排名 | 得分 | 类型 | CAN ID | Byte.Bit | 全关 | 通风 | 稳定纯度 | 动作命中 | 背景翻转 | 延迟中位数(s) |",
              "|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for rank, row in enumerate(bits[:top], 1):
        delay = "—" if row["delay"] is None else f'{row["delay"]:+.4f}'
        lines.append(f'| {rank} | {row["score"]:.2f} | {row["category"]} | 0x{row["frame_id"]:X} | B{row["byte"]}.b{row["bit_in_byte"]} | {row["closed"]} | {row["vent"]} | {row["purity"]:.1%} | {row["hits"]}/{len(actions)} | {row["unrelated"]} | {delay} |')
    lines += ["", "## 整字节稳定候选", "", "| 排名 | CAN ID | Byte | 全关(hex) | 通风(hex) | 稳定纯度 |",
              "|---:|---:|---:|---:|---:|---:|"]
    for rank, row in enumerate(byte_rows[:top], 1):
        lines.append(f'| {rank} | 0x{row["frame_id"]:X} | B{row["byte"]} | {row["closed"]:02X} | {row["vent"]:02X} | {row["purity"]:.1%} |')
    lines += ["", "## 判读提示", "", "- 稳定状态候选可用于寻找车窗位置、到位或运动状态。",
              "- 瞬时请求候选只表示动作附近重复翻转，仍需结合原始帧确认脉冲方向。",
              "- 时间相关不等于因果；建议用单窗、仅唤醒、开关门等负对照继续验证。",
              "- CSV 包含全部候选，Markdown 仅展示指定数量。", ""]
    report_path.write_text("\n".join(lines), encoding="utf-8-sig")


def main() -> int:
    parser = argparse.ArgumentParser(description="无 DBC 分析车窗通风 ASC 的 CAN ID、Byte 和 Bit 候选")
    parser.add_argument("script", type=Path, help="车窗通风采集脚本")
    parser.add_argument("asc", type=Path, help="Vector ASC 文件")
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    parser.add_argument("--settle", type=float, default=5.0, help="动作后等待稳定的秒数")
    parser.add_argument("--edge", type=float, default=2.0, help="稳定窗口边缘排除秒数")
    parser.add_argument("--response", type=float, default=5.0, help="动作响应观察秒数")
    parser.add_argument("--min-purity", type=float, default=.95, help="稳定值最低占比")
    parser.add_argument("--top", type=int, default=30, help="报告最多展示候选数")
    args = parser.parse_args()
    for path in (args.script, args.asc):
        if not path.is_file():
            raise FileNotFoundError(f"输入文件不存在：{path}")
    if args.settle < 0 or args.edge < 0 or args.response <= 0 or not 0.5 <= args.min_purity <= 1:
        raise ValueError("参数范围无效")
    actions, end_time = parse_actions(args.script)
    windows = make_state_windows(actions, end_time, args.settle, args.edge)
    series, total = collect(args.asc, windows)
    bits = rank_bits(series, windows, actions, args.response, args.min_purity)
    bytes_ranked = rank_bytes(series, windows, args.min_purity)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    stem = args.asc.stem
    report = args.output_dir / f"{stem}_车窗通风分析报告.md"
    csv_path = args.output_dir / f"{stem}_车窗通风bit候选.csv"
    write_outputs(report, csv_path, args.script, args.asc, windows, actions, bits, bytes_ranked, total, args.top)
    print(f"分析完成：{total:,} 帧，{len(series)} 个 CAN ID，{len(bits)} 个 bit 候选")
    print(f"报告：{report}")
    print(f"明细：{csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
