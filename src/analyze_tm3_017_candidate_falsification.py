#!/usr/bin/env python3
"""Falsify and group TM3-017 anonymous raw candidates without semantic inputs."""

from __future__ import annotations

import csv
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASC = ROOT / "input/TM3-017_语音执行脚本__20260915_190425_266__S0030/can/can_20260915190403_TM3-017_S0030.asc"
IN_CANDIDATES = ROOT / "output/TM3-017/machine_evidence/blind_raw_candidates.csv"
OUT = ROOT / "output/TM3-017/candidate_review"
WINDOWS = {
    "W1": (5.0, 75.0),
    "W2": (90.763, 208.268),
    "W3": (227.478, 330.0),
}
EVENTS = {"fall": 78.322, "rise": 208.268}
LINE_RE = re.compile(
    r"^(\d+\.\d+)\s+\d+\s+([0-9A-Fa-f]+)\s+Rx\s+d\s+(\d+)\s+((?:[0-9A-Fa-f]{2}\s*)+)$"
)


def key_text(key: tuple[int, int, int]) -> str:
    return f"0x{key[0]:X}/DLC{key[1]}/B{key[2]}"


def parse() -> tuple[list[tuple[float, int, bytes]], dict[tuple[int, int, int], dict[str, str]]]:
    candidates: dict[tuple[int, int, int], dict[str, str]] = {}
    with IN_CANDIDATES.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            key = (int(row["can_id"], 16), int(row["dlc"]), int(row["byte_offset_zero_based"]))
            candidates[key] = row
    frames: list[tuple[float, int, bytes]] = []
    with ASC.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            match = LINE_RE.match(line.strip())
            if match:
                dlc = int(match.group(3))
                frames.append(
                    (float(match.group(1)), int(match.group(2), 16), bytes.fromhex(match.group(4))[:dlc])
                )
    return frames, candidates


def pearson(left: list[float], right: list[float]) -> float:
    lm, rm = statistics.fmean(left), statistics.fmean(right)
    ln = [value - lm for value in left]
    rn = [value - rm for value in right]
    denominator = math.sqrt(sum(value * value for value in ln) * sum(value * value for value in rn))
    return sum(a * b for a, b in zip(ln, rn)) / denominator if denominator else 0.0


def held_grid(series: list[tuple[float, int]], start: float = 70.0, end: float = 235.0) -> list[float]:
    grid = [start + index * 0.1 for index in range(round((end - start) / 0.1) + 1)]
    output: list[float] = []
    index = 0
    value = series[0][1]
    for timestamp in grid:
        while index + 1 < len(series) and series[index + 1][0] <= timestamp:
            index += 1
            value = series[index][1]
        output.append(float(value))
    return output


def first_crossing(
    series: list[tuple[float, int]], event: float, end: float, origin: float, target: float, fraction: float
) -> float | None:
    threshold = origin + fraction * (target - origin)
    increasing = target > origin
    for timestamp, value in series:
        if event <= timestamp <= end and ((increasing and value >= threshold) or (not increasing and value <= threshold)):
            return round(timestamp - event, 6)
    return None


def main() -> None:
    frames, candidates = parse()
    series: dict[tuple[int, int, int], list[tuple[float, int]]] = defaultdict(list)
    payloads: dict[int, list[tuple[float, bytes]]] = defaultdict(list)
    for timestamp, can_id, payload in frames:
        payloads[can_id].append((timestamp, payload))
        for offset, value in enumerate(payload):
            key = (can_id, len(payload), offset)
            if key in candidates:
                series[key].append((timestamp, value))

    definite_counter = set()
    for key, values in series.items():
        window_values = [value for timestamp, value in values if WINDOWS["W2"][0] <= timestamp <= WINDOWS["W2"][1]]
        deltas = [(b - a) % 256 for a, b in zip(window_values, window_values[1:]) if a != b]
        if len(set(window_values)) >= 8 and deltas:
            _, count = Counter(deltas).most_common(1)[0]
            if count / len(deltas) >= 0.90:
                definite_counter.add(key)

    invariant_mux = {(0x123, 8, offset) for offset in (2, 3, 4, 7)}
    cyclic_or_multipage = {
        (0x330, 8, 1), (0x330, 8, 7), (0x372, 8, 4), (0x372, 8, 5),
        (0x420, 8, 6), (0x4E2, 8, 1), (0x752, 8, 5), (0x7AA, 8, 3),
        (0x300, 8, 2), (0x3E9, 8, 1), (0x3E9, 8, 2),
    }
    priority_1 = {
        (0x333, 5, 1), (0x252, 8, 4), (0x204, 8, 4), (0x132, 6, 2), (0x292, 8, 6),
    }
    priority_2 = {
        (0x472, 8, 1), (0x212, 8, 5), (0x212, 8, 2), (0x204, 8, 2),
        (0x204, 8, 3), (0x264, 6, 2), (0x264, 6, 3), (0x2A3, 7, 4),
        (0x252, 8, 5),
    }
    priority_3 = {(0x22A, 4, 2), (0x2A3, 7, 1), (0x2A7, 8, 5), (0x2D2, 8, 0)}

    review_rows: list[dict[str, object]] = []
    transition_rows: list[dict[str, object]] = []
    for key, original in candidates.items():
        medians = [float(original[f"w{i}_median_raw"]) for i in (1, 2, 3)]
        ranges = [float(original[f"w{i}_range_raw"]) for i in (1, 2, 3)]
        mode_fractions = [float(original[f"w{i}_mode_fraction"]) for i in (1, 2, 3)]
        values = [value for timestamp, value in series[key] if WINDOWS["W2"][0] <= timestamp <= WINDOWS["W2"][1]]
        deltas = [(b - a) % 256 for a, b in zip(values, values[1:]) if a != b]
        top_delta, top_delta_count = Counter(deltas).most_common(1)[0] if deltas else (None, 0)
        counter_fraction = top_delta_count / len(deltas) if deltas else 0.0
        xor_fall = int(medians[0]) ^ int(medians[1])
        xor_rise = int(medians[1]) ^ int(medians[2])

        if key in invariant_mux:
            decision, priority = "REJECT_BYTE_LEVEL", "X"
            reason = "完整payload在三个窗口相同并按两页交替；中位数差异由奇偶样本数翻转造成"
        elif key in definite_counter:
            decision, priority = "REJECT_COUNTER_OR_CYCLE", "X"
            reason = f"W2内非零步进的主模差为{top_delta}，占{counter_fraction:.3f}；窗口中位数是相位/时间位置伪影"
        elif key in cyclic_or_multipage:
            decision, priority = "REJECT_PERIODIC_OR_MULTIPAGE", "X"
            reason = "窗口内持续多页/周期切换或宽范围循环，byte中位数不足以形成阶跃证据"
        elif key in priority_1:
            decision, priority = "RETAIN", "P1"
            reason = "三窗口低离散、两侧方向相反且回到初始附近，并具有连续边沿轨迹"
        elif key in priority_2:
            decision, priority = "RETAIN_WITH_FIELD_BOUNDARY", "P2"
            reason = "可逆窗口关系成立，但相邻byte共同变化、脉冲占空或两侧动态不对称，单byte解释不充分"
        elif key in priority_3:
            decision, priority = "DOWNRANK", "P3"
            reason = "变化较小、窗口内存在额外层级或恢复偏差，当前不能排除慢漂移或偶然共变"
        else:
            decision, priority = "REJECT_WEAK", "X"
            reason = "未通过稳定性、周期性或可逆边沿复核"

        review_rows.append({
            "candidate": key_text(key),
            "decision": decision,
            "priority": priority,
            "w1_w2_w3_median_raw": "/".join(f"{value:g}" for value in medians),
            "w1_w2_w3_range_raw": "/".join(f"{value:g}" for value in ranges),
            "w1_w2_w3_mode_fraction": "/".join(f"{value:.3f}" for value in mode_fractions),
            "fall_xor_mask_hex": f"0x{xor_fall:02X}",
            "rise_xor_mask_hex": f"0x{xor_rise:02X}",
            "w2_unique_raw": len(set(values)),
            "dominant_nonzero_mod_delta": top_delta,
            "dominant_delta_fraction": round(counter_fraction, 6),
            "reason": reason,
            "semantic_status": "ANONYMOUS_RAW_ONLY",
        })

        if priority in {"P1", "P2"} and key != (0x252, 8, 5):
            fall = [first_crossing(series[key], EVENTS["fall"], 100.0, medians[0], medians[1], fraction) for fraction in (0.1, 0.5, 0.9)]
            rise = [first_crossing(series[key], EVENTS["rise"], 240.0, medians[1], medians[2], fraction) for fraction in (0.1, 0.5, 0.9)]
            transition_rows.append({
                "candidate": key_text(key),
                "priority": priority,
                "fall_t10_after_E03_s": fall[0],
                "fall_t50_after_E03_s": fall[1],
                "fall_t90_after_E03_s": fall[2],
                "rise_t10_after_E06_s": rise[0],
                "rise_t50_after_E06_s": rise[1],
                "rise_t90_after_E06_s": rise[2],
                "timing_anchor_boundary": "VOICE_CUE_NOT_MANUAL_COMPLETION",
            })

    review_rows.sort(key=lambda row: ({"P1": 0, "P2": 1, "P3": 2, "X": 3}[str(row["priority"])], str(row["candidate"])))
    transition_rows.sort(key=lambda row: ({"P1": 0, "P2": 1}[str(row["priority"])], str(row["candidate"])))

    retained = [key for key in candidates if key in priority_1 | priority_2]
    grids = {key: held_grid(series[key]) for key in retained}
    pair_rows: list[dict[str, object]] = []
    for index, left in enumerate(retained):
        for right in retained[index + 1:]:
            correlation = pearson(grids[left], grids[right])
            if correlation >= 0.985:
                relation = "SAME_CAN_ID_ADJACENT" if left[0] == right[0] and abs(left[2] - right[2]) == 1 else "SYNCHRONOUS_TRAJECTORY"
                pair_rows.append({
                    "candidate_a": key_text(left), "candidate_b": key_text(right),
                    "pearson_100ms_hold": round(correlation, 6), "relationship": relation,
                    "boundary": "correlation does not prove shared field, derivation, causation, or semantic identity",
                })
    pair_rows.sort(key=lambda row: -float(row["pearson_100ms_hold"]))

    groups = [
        {"group_id": "G-A", "dynamic_class": "EARLY_REVERSIBLE", "members": "0x333/DLC5/B1;0x252/DLC8/B4-B5;0x472/DLC8/B1(+B2);0x212/DLC8/B5", "observation": "两侧提示后约2至6秒完成主要变化；稳态返回性强", "boundary": "成员可能是同源、派生或共同受第三变量驱动，当前不可区分"},
        {"group_id": "G-B", "dynamic_class": "INTERMEDIATE_REVERSIBLE", "members": "0x292/DLC8/B6", "observation": "调低侧约2至5秒、恢复侧约5至7秒形成主要变化", "boundary": "单一候选类别，不推定角色"},
        {"group_id": "G-C", "dynamic_class": "LATE_GRADUAL_REVERSIBLE", "members": "0x204/DLC8/B4;0x132/DLC6/B2;0x264/DLC6/B2-B3;0x212/DLC8/B2;0x2A3/DLC7/B4", "observation": "调低侧较早下降；恢复侧主要变化集中在提示后约10至17秒", "boundary": "不同ID高度同步但不证明同源或物理量相同"},
        {"group_id": "G-D", "dynamic_class": "SAME_FRAME_FIELD_BOUNDARY_UNRESOLVED", "members": "0x204/DLC8/B2-B4;0x264/DLC6/B2-B3;0x252/DLC8/B4-B5;0x472/DLC8/B1-B2", "observation": "相邻byte在窗口或边沿共同变化，但部分byte恢复轨迹不同", "boundary": "不能选择单byte、固定多byte字节序或bitfield解释"},
        {"group_id": "G-E", "dynamic_class": "BINARY_OR_DUTY_COCHANGE", "members": "0x2A3/DLC7/B1;0x3E9/DLC8/B1-B2", "observation": "高低窗口的占空或分支比例变化", "boundary": "byte级统计受周期/分支影响，只保留低优先级完整payload观察"},
        {"group_id": "G-X", "dynamic_class": "FALSIFIED_BYTE_MEDIAN", "members": "所有REJECT_*候选", "observation": "计数、循环、复用页、交替payload或窗口相位造成伪高低高", "boundary": "淘汰的是本轮byte单点解释，不等于整个CAN ID无信息"},
    ]

    OUT.mkdir(parents=True, exist_ok=True)
    outputs = [
        ("candidate_falsification_review.csv", review_rows),
        ("transition_metrics.csv", transition_rows),
        ("candidate_relationships.csv", pair_rows),
        ("behavioral_groups.csv", groups),
    ]
    for filename, rows in outputs:
        with (OUT / filename).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    counts = Counter(str(row["priority"]) for row in review_rows)
    audit = {
        "experiment": "TM3-017", "round": "S0030",
        "analysis_mode": "STRICT_NO_DBC_RAW_PAYLOAD_ONLY",
        "input_candidate_count": len(candidates), "priority_counts": dict(counts),
        "counter_or_cycle_detected": len(definite_counter),
        "retained_pair_correlation_threshold": 0.985,
        "time_grid": "100 ms held-last-value, ASC 70-235 s",
        "windows": WINDOWS, "event_cues": EVENTS,
        "limitations": [
            "Priority ranks raw behavioral usefulness only.",
            "No name, scale, unit, role, ECU, causality, or field byte order is assigned.",
            "A rejected byte does not invalidate its complete CAN payload.",
            "Event cues are not manual action-completion timestamps.",
        ],
    }
    (OUT / "candidate_review_audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
