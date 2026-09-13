#!/usr/bin/env python3
"""S0009 DBC-independent CAN field reconnaissance.

This script deliberately consumes only ASC bytes and externally supplied event
windows.  It does not import cantools or read any DBC / prior signal mapping.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import median


LINE_RE = re.compile(
    r"^\s*(?P<t>\d+\.\d+)\s+\d+\s+(?P<id>[0-9A-Fa-f]+)\s+\w+\s+d\s+"
    r"(?P<dlc>\d+)\s+(?P<data>(?:[0-9A-Fa-f]{2}\s*)+)$"
)
DATE_RE = re.compile(r"^date\s+(.+)$")


@dataclass(frozen=True)
class Frame:
    t: float
    can_id: int
    data: bytes


STAGES = {
    "BASELINE": (5.0, 35.0),
    "DOOR_OPEN": (43.0, 57.0),
    "CONNECTED_IDLE": (70.0, 150.0),
    "CHARGING": (250.0, 370.0),
    "STOPPED_CONNECTED": (400.0, 435.0),
    "UNLOCKED_CONNECTED": (447.0, 465.0),
    "UNPLUGGED": (480.0, 535.0),
}

EVENTS = {
    "OPEN_DOOR": 40.04,
    "PLUG": 60.04,
    "START_REQUEST": 160.02,
    "STOP": 380.10,
    "UNLOCK": 440.06,
    "UNPLUG": 470.10,
}


def parse_header_time(path: Path) -> datetime:
    with path.open(errors="replace") as handle:
        line = handle.readline().strip()
    match = DATE_RE.match(line)
    if not match:
        raise ValueError(f"missing ASC date header: {path}")
    return datetime.strptime(match.group(1), "%a %b %d %I:%M:%S %p %Y")


def parse_asc(paths: list[Path]) -> tuple[list[Frame], list[dict]]:
    starts = [parse_header_time(path) for path in paths]
    origin = min(starts)
    frames: list[Frame] = []
    segments: list[dict] = []
    for path, start in sorted(zip(paths, starts), key=lambda pair: pair[1]):
        offset = (start - origin).total_seconds()
        count = 0
        local_end = 0.0
        with path.open(errors="replace") as handle:
            for line in handle:
                match = LINE_RE.match(line.rstrip())
                if not match:
                    continue
                local_t = float(match.group("t"))
                raw = bytes.fromhex(match.group("data"))
                dlc = int(match.group("dlc"))
                if len(raw) != dlc:
                    continue
                frames.append(Frame(offset + local_t, int(match.group("id"), 16), raw))
                count += 1
                local_end = local_t
        segments.append({"file": str(path), "offset_s": offset, "duration_s": local_end, "frames": count})
    frames.sort(key=lambda frame: frame.t)
    return frames, segments


def stage_name(t: float) -> str | None:
    for name, (lo, hi) in STAGES.items():
        if lo <= t <= hi:
            return name
    return None


def mode_and_purity(values: list[int]) -> tuple[int | None, float]:
    if not values:
        return None, 0.0
    value, count = Counter(values).most_common(1)[0]
    return value, count / len(values)


def bit_rows(frames: list[Frame]) -> list[dict]:
    buckets: dict[tuple[int, int, int], dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    for frame in frames:
        stage = stage_name(frame.t)
        if stage is None:
            continue
        for byte_index, byte in enumerate(frame.data):
            for bit in range(8):
                buckets[(frame.can_id, len(frame.data), byte_index * 8 + bit)][stage].append((byte >> bit) & 1)

    rows = []
    for (can_id, dlc, bit), stage_values in buckets.items():
        modes = {}
        purities = {}
        for stage in STAGES:
            modes[stage], purities[stage] = mode_and_purity(stage_values.get(stage, []))
        if any(modes[s] is None for s in STAGES):
            continue
        min_purity = min(purities.values())
        pattern = "".join(str(modes[s]) for s in STAGES)
        if len(set(pattern)) == 1 or min_purity < 0.90:
            continue
        rows.append({
            "can_id": f"0x{can_id:03X}", "dlc": dlc,
            "byte": bit // 8, "bit": bit % 8,
            "pattern": pattern, "min_stage_purity": round(min_purity, 6),
            **{stage.lower(): modes[stage] for stage in STAGES},
        })
    return sorted(rows, key=lambda row: (-row["min_stage_purity"], row["can_id"], row["byte"], row["bit"]))


ROLE_PATTERNS = {
    "door_cycle": lambda p: p[1] != p[0] and p[1] == p[2] == p[3] == p[4] and p[5] == p[6] == p[0],
    "connection_cycle": lambda p: p[2] == p[3] == p[4] == p[5] and p[2] != p[0] and p[6] == p[0],
    "charge_execution": lambda p: p[3] != p[2] and p[3] != p[4] and p[2] == p[4],
    "session_until_unplug": lambda p: p[3] == p[4] == p[5] and p[3] != p[2] and p[6] == p[2],
    "unlock_window": lambda p: p[5] != p[4] and p[6] == p[0],
}


def role_rows(bits: list[dict]) -> list[dict]:
    rows = []
    stage_keys = [stage.lower() for stage in STAGES]
    for row in bits:
        pattern = [row[key] for key in stage_keys]
        roles = [name for name, predicate in ROLE_PATTERNS.items() if predicate(pattern)]
        if roles:
            rows.append({**row, "roles": ";".join(roles)})
    return rows


def transition_rows(frames: list[Frame], role_bits: list[dict]) -> list[dict]:
    wanted = {(int(row["can_id"], 16), row["byte"] * 8 + row["bit"]) for row in role_bits}
    series: dict[tuple[int, int], list[tuple[float, int]]] = defaultdict(list)
    last = {}
    for frame in frames:
        for bit in range(len(frame.data) * 8):
            key = (frame.can_id, bit)
            if key not in wanted:
                continue
            value = (frame.data[bit // 8] >> (bit % 8)) & 1
            if last.get(key) != value:
                series[key].append((frame.t, value))
                last[key] = value
    rows = []
    for (can_id, bit), changes in series.items():
        for event, event_t in EVENTS.items():
            nearby = [(t, value) for t, value in changes if event_t - 8 <= t <= event_t + 20]
            if not nearby:
                continue
            nearest = min(nearby, key=lambda item: abs(item[0] - event_t))
            rows.append({
                "can_id": f"0x{can_id:03X}", "byte": bit // 8, "bit": bit % 8,
                "event": event, "event_t_s": event_t,
                "transition_t_s": round(nearest[0], 6), "delay_s": round(nearest[0] - event_t, 6),
                "new_value": nearest[1], "nearby_transition_count": len(nearby),
            })
    return sorted(rows, key=lambda row: (row["event_t_s"], abs(row["delay_s"]), row["can_id"]))


def decode_value(data: bytes, start: int, width: int, endian: str, signed: bool) -> int:
    chunk = data[start:start + width]
    return int.from_bytes(chunk, byteorder=endian, signed=signed)


def continuous_rows(frames: list[Frame]) -> list[dict]:
    grouped: dict[tuple[int, int], list[Frame]] = defaultdict(list)
    for frame in frames:
        if stage_name(frame.t):
            grouped[(frame.can_id, len(frame.data))].append(frame)
    rows = []
    for (can_id, dlc), group in grouped.items():
        if len(group) < 50:
            continue
        for width in (1, 2):
            for start in range(dlc - width + 1):
                variants = [("little", False)] if width == 1 else [("little", False), ("little", True), ("big", False), ("big", True)]
                for endian, signed in variants:
                    by_stage = defaultdict(list)
                    all_values = []
                    for frame in group:
                        value = decode_value(frame.data, start, width, endian, signed)
                        by_stage[stage_name(frame.t)].append(value)
                        all_values.append(value)
                    if any(not by_stage[stage] for stage in STAGES):
                        continue
                    unique = len(set(all_values))
                    if unique < 8:
                        continue
                    med = {stage: median(by_stage[stage]) for stage in STAGES}
                    charge_delta = abs(med["CHARGING"] - med["CONNECTED_IDLE"])
                    stop_delta = abs(med["CHARGING"] - med["STOPPED_CONNECTED"])
                    unplug_delta = abs(med["STOPPED_CONNECTED"] - med["UNPLUGGED"])
                    spread = max(all_values) - min(all_values)
                    if spread == 0:
                        continue
                    score = (charge_delta + stop_delta) / spread
                    if score < 0.10:
                        continue
                    diffs = [abs(b - a) for a, b in zip(all_values, all_values[1:])]
                    smooth = 1.0 - min(1.0, median(diffs) / max(1.0, spread))
                    rows.append({
                        "can_id": f"0x{can_id:03X}", "dlc": dlc, "start_byte": start,
                        "width_bytes": width, "endian": endian, "signed": signed,
                        "unique_values": unique, "range": spread,
                        "charge_contrast_score": round(score, 6), "smoothness": round(smooth, 6),
                        "connected_idle_median": med["CONNECTED_IDLE"], "charging_median": med["CHARGING"],
                        "stopped_connected_median": med["STOPPED_CONNECTED"], "unplugged_median": med["UNPLUGGED"],
                        "unplug_contrast": unplug_delta,
                    })
    return sorted(rows, key=lambda row: (-row["charge_contrast_score"], -row["smoothness"], row["can_id"]))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--asc", type=Path, nargs="+", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    frames, segments = parse_asc(args.asc)
    bits = bit_rows(frames)
    roles = role_rows(bits)
    transitions = transition_rows(frames, roles)
    continuous = continuous_rows(frames)
    write_csv(args.out / "01_all_stable_changing_bits.csv", bits)
    write_csv(args.out / "02_role_candidates.csv", roles)
    write_csv(args.out / "03_event_transitions.csv", transitions)
    write_csv(args.out / "04_continuous_candidates.csv", continuous)
    ids = Counter(frame.can_id for frame in frames)
    manifest = {
        "mode": "STRICT_DBC_INDEPENDENT_RECONNAISSANCE",
        "inputs": [str(path) for path in args.asc],
        "forbidden_inputs": ["DBC", "Yi hit points", "prior Signal mappings", "prior ASC payloads"],
        "segments": segments,
        "frame_count": len(frames), "can_id_count": len(ids),
        "time_start_s": frames[0].t, "time_end_s": frames[-1].t,
        "stages": STAGES, "events": EVENTS,
        "outputs": {
            "stable_changing_bits": len(bits), "role_candidates": len(roles),
            "event_transition_rows": len(transitions), "continuous_candidates": len(continuous),
        },
    }
    (args.out / "00_run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
