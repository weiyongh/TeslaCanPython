#!/usr/bin/env python3
"""Cross-check TM3-017 anonymous candidates against approved S0009 raw assets."""

from __future__ import annotations

import csv
import json
import re
import statistics
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
S9_DIR = ROOT / "input/L3-Charge-Slow-FullCycle_慢充全过程采集__20260911_133727_858__S0009"
S9_CONTEXT = ROOT / "output/acquisition_context/L3-Charge-Slow-FullCycle_慢充全过程采集__20260911_133727_858__S0009/acquisition_context.json"
REVIEW = ROOT / "output/TM3-017/candidate_review/candidate_falsification_review.csv"
OUT = ROOT / "output/TM3-017/candidate_review/cross_round"
LINE_RE = re.compile(
    r"^(\d+\.\d+)\s+\d+\s+([0-9A-Fa-f]+)\s+Rx\s+d\s+(\d+)\s+((?:[0-9A-Fa-f]{2}\s*)+)$"
)

# Seconds relative to S0009 first ASC clock (13:37:27.000+08:00).
WINDOWS = {
    "S9_PRE": (5.0, 50.0),
    "S9_CONNECTED_NOT_CHARGING": (105.0, 155.0),
    "S9_CHARGING_HIGH": (250.0, 315.0),
    "S9_STOPPED_CONNECTED": (335.0, 430.0),
    "S9_UNLOCKED_CONNECTED": (448.0, 465.0),
    "S9_UNPLUGGED": (475.0, 530.0),
}
PHOTO_POINTS = {
    "S9_APP_LOW_1": 195.388,
    "S9_APP_LOW_2": 203.424,
    "S9_APP_HIGH": 240.933,
    "S9_VEHICLE_HIGH": 246.171,
    "S9_VEHICLE_STOPPED": 394.541,
}


def label(key: tuple[int, int, int]) -> str:
    return f"0x{key[0]:X}/DLC{key[1]}/B{key[2]}"


def main() -> None:
    context = json.loads(S9_CONTEXT.read_text(encoding="utf-8"))
    if context.get("review_status") != "APPROVED" or context["round"]["round_id"] != "S0009":
        raise SystemExit("S0009 approved Acquisition Context is required")
    candidates: dict[tuple[int, int, int], dict[str, str]] = {}
    with REVIEW.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            if row["priority"] not in {"P1", "P2"}:
                continue
            parts = row["candidate"].split("/")
            key = (int(parts[0], 16), int(parts[1][3:]), int(parts[2][1:]))
            candidates[key] = row

    series: dict[tuple[int, int, int], list[tuple[float, int]]] = defaultdict(list)
    files = [(S9_DIR / "can/can_20260911133648.asc", 0.0), (S9_DIR / "can/can_20260911133648_2.asc", 443.0)]
    for path, offset in files:
        with path.open(encoding="utf-8", errors="replace") as stream:
            for line in stream:
                match = LINE_RE.match(line.strip())
                if not match:
                    continue
                timestamp = offset + float(match.group(1))
                can_id, dlc = int(match.group(2), 16), int(match.group(3))
                payload = bytes.fromhex(match.group(4))[:dlc]
                for key in candidates:
                    if (can_id, dlc) == key[:2]:
                        series[key].append((timestamp, payload[key[2]]))

    snapshot_rows: list[dict[str, object]] = []
    for key, source in candidates.items():
        values = series.get(key, [])
        row: dict[str, object] = {"candidate": label(key), "s0030_priority": source["priority"]}
        for name, (start, end) in WINDOWS.items():
            selected = [value for timestamp, value in values if start <= timestamp <= end]
            row[f"{name}_median"] = statistics.median(selected) if selected else None
            row[f"{name}_min"] = min(selected) if selected else None
            row[f"{name}_max"] = max(selected) if selected else None
        for name, target in PHOTO_POINTS.items():
            nearest = min(values, key=lambda item: abs(item[0] - target)) if values else None
            within_tolerance = nearest is not None and abs(nearest[0] - target) <= 0.5
            row[f"{name}_raw"] = nearest[1] if within_tolerance else None
            row[f"{name}_offset_s"] = round(nearest[0] - target, 6) if within_tolerance else None
        snapshot_rows.append(row)

    ordering = {
        "0x132/DLC6/B2": ("P1-A", "多状态+晚渐变", "跨Round保留；S0009非充电约247、建立过程低位后高位约180、停止后回到约247"),
        "0x204/DLC8/B4": ("P1-A", "零基线+晚渐变", "跨Round保留；非充电为0、S0009充电建立时渐升至约160、停止后回0"),
        "0x292/DLC8/B6": ("P1-B", "零基线+中间渐变", "跨Round保留；非充电为0、建立时两段渐升、停止后回0"),
        "0x252/DLC8/B4": ("P1-B", "早期门槛+稳定层级", "跨Round保留；非充电为0、建立早期跳至244、停止后回0"),
        "0x333/DLC5/B1": ("P1-C", "早期多状态", "保留但后移；未充电时也可为16，S0009建立早期16→32，停止连接时为5，拔枪后回16"),
        "0x204/DLC8/B2": ("P2", "同帧边界未决", "与B3在充电稳态接近，但非充电时B2=0而B3=255；简单副本假设被否定"),
        "0x204/DLC8/B3": ("P2", "同帧边界未决", "与B2在充电稳态接近，但非充电时分离；不得合并为副本"),
        "0x212/DLC8/B2": ("P2", "渐变+状态层级", "非充电为0，建立过程分段渐升，停止后回0"),
        "0x212/DLC8/B5": ("P2", "渐变+状态层级", "非充电为255，充电过程进入另一层级，不能与B2视为换算副本"),
        "0x252/DLC8/B5": ("P2", "相邻byte独立性", "B4非充电回0时B5仍有168/128等层级；固定双byte字段假设缺乏支持"),
        "0x264/DLC6/B2": ("P2", "同帧渐变", "与B3共同变化但轨迹和非充电层级不同；组合边界未决"),
        "0x264/DLC6/B3": ("P2", "同帧渐变", "与B2共同变化但不是数值副本；组合边界未决"),
        "0x2A3/DLC7/B4": ("P2-", "发送域受限", "在S0009非充电窗口缺帧且停止后仍保持18；不能作为通用停止响应候选"),
        "0x472/DLC8/B1": ("P2-", "早期多状态", "S0009建立阶段经历0→低位→高位，但多数非充电窗口也维持37；只保留特定边沿价值"),
    }
    review_rows = []
    for row in snapshot_rows:
        rank, behavior, conclusion = ordering[row["candidate"]]
        review_rows.append({
            "candidate": row["candidate"], "cross_round_rank": rank,
            "behavioral_class": behavior, "cross_round_conclusion": conclusion,
            "semantic_status": "ANONYMOUS_RAW_ONLY",
        })
    review_rows.sort(key=lambda row: (row["cross_round_rank"], row["candidate"]))

    OUT.mkdir(parents=True, exist_ok=True)
    for filename, rows in [("s0009_raw_snapshots.csv", snapshot_rows), ("cross_round_candidate_review.csv", review_rows)]:
        with (OUT / filename).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    audit = {
        "analysis_mode": "STRICT_NO_DBC_RAW_PAYLOAD_ONLY",
        "primary_round": "S0030", "comparison_round": "S0009",
        "comparison_context": str(S9_CONTEXT.relative_to(ROOT)),
        "comparison_context_status": context["review_status"],
        "candidate_count": len(candidates), "windows": WINDOWS, "photo_points": PHOTO_POINTS,
        "split_asc_timebase": "second ASC origin is +443.000 s from first origin; file gap 442.372-443.000 s retained",
        "boundary": "Cross-round raw behavior only; no name, unit, scale, role, ECU, causality, or field encoding is assigned.",
    }
    (OUT / "cross_round_audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
