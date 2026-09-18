#!/usr/bin/env python3
"""Reproduce TM3-017 S0030 blind raw-payload observations without any DBC input."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASC = ROOT / "input/TM3-017_语音执行脚本__20260915_190425_266__S0030/can/can_20260915190403_TM3-017_S0030.asc"
OUT = ROOT / "output/TM3-017/machine_evidence"
ASC_CLOCK = "2026-09-15T19:04:27.000+08:00"

# Windows are fixed from actual photo/Event clocks, with action edges excluded.
WINDOWS = {
    "W1_INITIAL_HIGH": (5.0, 75.0),
    "W2_LOW": (90.763, 208.268),
    "W3_RECOVERED_HIGH": (227.478, 330.0),
}
EVENTS = {"E03_LOWER_CUE": 78.322, "E06_RESTORE_CUE": 208.268}
LINE_RE = re.compile(
    r"^(\d+\.\d+)\s+\d+\s+([0-9A-Fa-f]+)\s+Rx\s+d\s+(\d+)\s+((?:[0-9A-Fa-f]{2}\s*)+)$"
)


def parse_asc() -> list[tuple[float, int, bytes]]:
    frames: list[tuple[float, int, bytes]] = []
    with ASC.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            match = LINE_RE.match(line.strip())
            if not match:
                continue
            timestamp = float(match.group(1))
            can_id = int(match.group(2), 16)
            dlc = int(match.group(3))
            payload = bytes.fromhex(match.group(4))[:dlc]
            frames.append((timestamp, can_id, payload))
    return frames


def median(values: list[int]) -> float:
    return float(statistics.median(values))


def main() -> None:
    frames = parse_asc()
    if not frames:
        raise SystemExit("no ASC frames parsed")
    by_position: dict[tuple[int, int, int], dict[str, list[int]]] = defaultdict(
        lambda: defaultdict(list)
    )
    series: dict[tuple[int, int, int], list[tuple[float, int]]] = defaultdict(list)
    for timestamp, can_id, payload in frames:
        for offset, value in enumerate(payload):
            key = (can_id, len(payload), offset)
            series[key].append((timestamp, value))
            for window_name, (start, end) in WINDOWS.items():
                if start <= timestamp <= end:
                    by_position[key][window_name].append(value)

    rows: list[dict[str, object]] = []
    for (can_id, dlc, offset), window_data in by_position.items():
        if not all(len(window_data[name]) >= 10 for name in WINDOWS):
            continue
        medians = {name: median(window_data[name]) for name in WINDOWS}
        ranges = {name: max(window_data[name]) - min(window_data[name]) for name in WINDOWS}
        modes = {name: Counter(window_data[name]).most_common(1)[0][0] for name in WINDOWS}
        mode_fractions = {
            name: Counter(window_data[name]).most_common(1)[0][1] / len(window_data[name])
            for name in WINDOWS
        }
        down = medians["W1_INITIAL_HIGH"] - medians["W2_LOW"]
        up = medians["W3_RECOVERED_HIGH"] - medians["W2_LOW"]
        return_error = abs(medians["W3_RECOVERED_HIGH"] - medians["W1_INITIAL_HIGH"])
        if down < 2 or up < 2 or return_error > max(2.0, 0.15 * max(down, up)):
            continue
        rows.append(
            {
                "can_id": f"0x{can_id:X}",
                "dlc": dlc,
                "byte_offset_zero_based": offset,
                "w1_median_raw": medians["W1_INITIAL_HIGH"],
                "w2_median_raw": medians["W2_LOW"],
                "w3_median_raw": medians["W3_RECOVERED_HIGH"],
                "w1_mode_raw": modes["W1_INITIAL_HIGH"],
                "w2_mode_raw": modes["W2_LOW"],
                "w3_mode_raw": modes["W3_RECOVERED_HIGH"],
                "w1_range_raw": ranges["W1_INITIAL_HIGH"],
                "w2_range_raw": ranges["W2_LOW"],
                "w3_range_raw": ranges["W3_RECOVERED_HIGH"],
                "w1_mode_fraction": round(mode_fractions["W1_INITIAL_HIGH"], 6),
                "w2_mode_fraction": round(mode_fractions["W2_LOW"], 6),
                "w3_mode_fraction": round(mode_fractions["W3_RECOVERED_HIGH"], 6),
                "down_raw": down,
                "up_raw": up,
                "return_error_raw": return_error,
                "behavior_only": "HIGH_LOW_HIGH_RAW_BYTE",
            }
        )
    rows.sort(key=lambda row: (-min(float(row["down_raw"]), float(row["up_raw"])), row["can_id"], row["byte_offset_zero_based"]))

    OUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUT / "blind_raw_candidates.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    selected = [(0x333, 5, 1), (0x252, 8, 4), (0x204, 8, 4), (0x132, 6, 2)]
    transitions: dict[str, list[dict[str, object]]] = {}
    for can_id, dlc, offset in selected:
        key = (can_id, dlc, offset)
        changes: list[dict[str, object]] = []
        prior = None
        for timestamp, value in series.get(key, []):
            if not (75.0 <= timestamp <= 90.0 or 205.0 <= timestamp <= 230.0):
                continue
            if value != prior:
                changes.append({"asc_time_s": timestamp, "raw_value": value})
                prior = value
        transitions[f"0x{can_id:X}/dlc{dlc}/byte{offset}"] = changes

    summary = {
        "experiment": "TM3-017",
        "round": "S0030",
        "vehicle": "TESLA-M3-SOP5",
        "analysis_mode": "STRICT_NO_DBC_RAW_PAYLOAD_ONLY",
        "asc": {
            "path": str(ASC.relative_to(ROOT)),
            "sha256": hashlib.sha256(ASC.read_bytes()).hexdigest(),
            "clock_origin": ASC_CLOCK,
            "first_timestamp_s": frames[0][0],
            "last_timestamp_s": frames[-1][0],
            "duration_s": frames[-1][0] - frames[0][0],
            "frame_count": len(frames),
            "can_id_count": len({can_id for _, can_id, _ in frames}),
        },
        "event_cues_asc_time_s": EVENTS,
        "analysis_windows_asc_time_s": WINDOWS,
        "window_boundary_basis": {
            "W1_INITIAL_HIGH": "within ASC coverage and before E03; E01-P01 at 32.854 s confirms 32 A actual/setting",
            "W2_LOW": "starts at E03-P01 photo 90.763 s confirming 16 A actual/setting; ends at E06 cue",
            "W3_RECOVERED_HIGH": "starts at E06-P02 photo 227.478 s confirming 32 A actual/setting; excludes E06-P01 intermediate 21 A at 221.583 s",
        },
        "candidate_rule": "raw byte median HIGH-LOW-HIGH, both directional deltas >=2, recovered return error <= max(2, 15% of larger delta)",
        "candidate_count": len(rows),
        "selected_raw_transition_traces": transitions,
        "semantic_boundary": "CAN IDs and byte offsets are anonymous raw observations; no Signal name, scale, unit, request/actual role, ECU ownership, or causal identity is assigned.",
    }
    (OUT / "blind_raw_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(csv_path)
    print(OUT / "blind_raw_summary.json")
    print(f"frames={len(frames)} ids={summary['asc']['can_id_count']} candidates={len(rows)}")


if __name__ == "__main__":
    main()
