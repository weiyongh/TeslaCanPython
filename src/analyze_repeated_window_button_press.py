"""利用右后自动下降前的重复误按，筛选短脉冲按钮输入候选。"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


def parse(line):
    parts = line.split()
    if len(parts) < 7:
        return None
    try:
        timestamp = float(parts[0])
        frame_id = int(parts[2].removesuffix("x").removesuffix("X"), 16)
        marker = next(i for i, item in enumerate(parts) if item.lower() == "d")
        dlc = int(parts[marker + 1])
        data = bytes(int(x, 16) for x in parts[marker + 2:marker + 2 + dlc])
        return timestamp, frame_id, data if len(data) == dlc else None
    except (ValueError, IndexError, StopIteration):
        return None


def collect(path: Path):
    series = defaultdict(list)
    with path.open("r", encoding="utf-8", errors="ignore") as source:
        for line in source:
            item = parse(line)
            if item and item[2] is not None:
                timestamp, frame_id, data = item
                series[frame_id].append((timestamp, data))
    return series


def bit_events(items):
    events = defaultdict(list)
    previous = None
    for timestamp, data in items:
        if previous is not None and len(previous) == len(data):
            for byte, changed in enumerate(a ^ b for a, b in zip(previous, data)):
                for bit in range(8):
                    if changed & (1 << bit):
                        events[byte * 8 + bit].append(
                            (timestamp, (previous[byte] >> bit) & 1, (data[byte] >> bit) & 1)
                        )
        previous = data
    return events


def pulse_count(events, start, end, max_width=0.8):
    selected = [event for event in events if start <= event[0] <= end]
    pulses = []
    for left, right in zip(selected, selected[1:]):
        if left[1] != left[2] and right[1] == left[2] and right[2] == left[1]:
            width = right[0] - left[0]
            if 0 < width <= max_width:
                pulses.append((left[0], right[0], width, left[2]))
    # 相邻边沿会共享，只有每两条构成一次完整脉冲。
    non_overlapping = []
    last_end = -1.0
    for pulse in pulses:
        if pulse[0] >= last_end:
            non_overlapping.append(pulse)
            last_end = pulse[1]
    return selected, non_overlapping


def main():
    input_dir = Path("input")
    files = {
        "右后": input_dir / "can_20260825100842_右后车窗物理按钮开关窗采集.asc",
        "右前": input_dir / "can_20260825100448_右前车窗物理按钮开关窗采集.asc",
        "左后": input_dir / "can_20260825101206_左后车窗物理按钮开关窗采集.asc",
        "基线": input_dir / "can_20260825095914_整车无操作基准数据采集.asc",
    }
    all_series = {name: collect(path) for name, path in files.items()}
    all_events = {
        name: {frame_id: bit_events(items) for frame_id, items in series.items()}
        for name, series in all_series.items()
    }
    rows = []
    # 脚本57秒自动下降；适度放宽以容纳连续误按和人为时差。
    burst_start, burst_end = 55.0, 60.0
    for frame_id, frame_events in all_events["右后"].items():
        for bit, events in frame_events.items():
            selected, pulses = pulse_count(events, burst_start, burst_end)
            if len(pulses) < 2:
                continue
            controls = {}
            for name in ("右前", "左后", "基线"):
                other = all_events[name].get(frame_id, {}).get(bit, [])
                other_selected, other_pulses = pulse_count(other, burst_start, burst_end)
                controls[name] = (len(other_selected), len(other_pulses))
            outside = sum(1 for event in events if not burst_start <= event[0] <= burst_end)
            score = len(pulses) * 30 + len(selected) * 2 - outside * 0.15
            score -= sum(value[1] * 10 for value in controls.values())
            rows.append({
                "score": score, "can_id": frame_id, "bit": bit,
                "edges": len(selected), "pulses": len(pulses), "outside_edges": outside,
                "right_front_pulses": controls["右前"][1],
                "left_rear_pulses": controls["左后"][1], "baseline_pulses": controls["基线"][1],
                "pulse_times": "; ".join(f"{a:.4f}-{b:.4f}({w:.3f}s)" for a, b, w, _ in pulses),
            })
    rows.sort(key=lambda row: (-row["score"], row["can_id"], row["bit"]))
    out = Path("output")
    out.mkdir(exist_ok=True)
    csv_path = out / "右后车窗连续误按按钮候选.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as target:
        fields = list(rows[0]) if rows else ["score", "can_id", "bit"]
        writer = csv.DictWriter(target, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            cooked = dict(row)
            cooked["score"] = f'{row["score"]:.3f}'
            cooked["can_id"] = f'0x{row["can_id"]:X}'
            cooked["bit"] = f'B{row["bit"]//8}.b{row["bit"]%8}'
            writer.writerow(cooked)
    report = out / "右后车窗连续误按按钮分析报告.md"
    lines = ["# 右后车窗连续误按按钮分析", "",
             "分析窗口为55–60秒，目标是寻找短时间内重复出现的完整bit脉冲。", "",
             "| 排名 | 得分 | ID | Byte.Bit | 边沿 | 完整短脉冲 | 窗口外边沿 | 右前同段 | 左后同段 | 基线同段 | 脉冲时间 |",
             "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for index, row in enumerate(rows[:40], 1):
        lines.append(f'| {index} | {row["score"]:.2f} | 0x{row["can_id"]:X} | B{row["bit"]//8}.b{row["bit"]%8} | '
                     f'{row["edges"]} | {row["pulses"]} | {row["outside_edges"]} | {row["right_front_pulses"]} | '
                     f'{row["left_rear_pulses"]} | {row["baseline_pulses"]} | {row["pulse_times"]} |')
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report)
    print(csv_path)


if __name__ == "__main__":
    main()
