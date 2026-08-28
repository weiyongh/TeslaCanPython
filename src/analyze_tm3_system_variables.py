"""Summarize diagnostic system/boundary variables from a scripted TM3 ASC capture."""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import median

import cantools


ASC_RE = re.compile(
    r"^\s*(?P<t>\d+(?:\.\d+)?)\s+\d+\s+(?P<id>[0-9A-Fa-f]+)x?\s+Rx\s+d\s+"
    r"(?P<dlc>\d+)\s+(?P<data>(?:[0-9A-Fa-f]{2}\s*)+)"
)

CATEGORY_PATTERNS = {
    "vehicle_state": re.compile(r"ready|vehicleState|driveState|gear|parkBrake", re.I),
    "brake_input": re.compile(r"brakePedal|brakeSwitch|driverBrake|brakeApply", re.I),
    "hv_safety": re.compile(r"contactor|precharge|hvil|isolation|packVoltage|busVoltage|hvAvailable", re.I),
    "battery_state": re.compile(r"packCurrent|soc(?:Min|Max|Avg|UI)?$|packTMin|packTMax|minPackTemperature|brickVoltage", re.I),
    "battery_boundary": re.compile(r"max(?:Discharge|Charge|Regen).*(?:Current|Power)|limitDischargePower|batteryPower", re.I),
    "drive_command_feedback": re.compile(r"torqueCommand|torqueActual|systemTorqueCommand|axleSpeed|motorSpeed", re.I),
    "drive_boundary": re.compile(r"limitDriveTorque|limitRegenTorque|limitMotorSpeed|limitRotorTemp|pwrSat|tqSat|pedalMinTorque|pedalMaxTorque", re.I),
    "resolver_position": re.compile(r"resolver|loadAngle|internalAngle|rotorFlux|rotorMaxMagnetTemp", re.I),
}

WINDOWS = {
    "pre_stable": (10.0, 18.0),
    "door_open": (20.5, 27.0),
    "door_closed": (31.0, 38.0),
    "brake_pressed": (40.5, 44.5),
    "post_brake": (46.0, 49.5),
    "final_stable": (50.0, 69.0),
}


@dataclass
class Sample:
    time: float
    value: object


def scalar(value: object) -> float | str:
    if isinstance(value, (int, float)):
        return float(value)
    return str(value)


def summarize(values: list[object]) -> tuple[str, str, str, int]:
    if not values:
        return "", "", "", 0
    changes = sum(a != b for a, b in zip(values, values[1:]))
    numeric = [float(v) for v in values if isinstance(v, (int, float))]
    if len(numeric) == len(values):
        return f"{median(numeric):.6g}", f"{min(numeric):.6g}", f"{max(numeric):.6g}", changes
    counts: dict[str, int] = defaultdict(int)
    for value in values:
        counts[str(value)] += 1
    mode = max(counts, key=counts.get)
    return mode, "", "", changes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("asc", type=Path)
    parser.add_argument("dbc", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    db = cantools.database.load_file(args.dbc, database_format="dbc", strict=False)
    messages = {m.frame_id: m for m in db.messages}
    selected: dict[tuple[int, str], str] = {}
    category_defs: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for message in db.messages:
        for signal in message.signals:
            for category, pattern in CATEGORY_PATTERNS.items():
                if pattern.search(signal.name):
                    key = (message.frame_id, signal.name)
                    selected[key] = category
                    category_defs[category].append(key)
                    break

    samples: dict[tuple[int, str], list[Sample]] = defaultdict(list)
    seen_ids: set[int] = set()
    total_frames = 0
    decoded_frames = 0
    with args.asc.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            match = ASC_RE.match(line)
            if not match:
                continue
            total_frames += 1
            timestamp = float(match.group("t"))
            frame_id = int(match.group("id"), 16)
            seen_ids.add(frame_id)
            message = messages.get(frame_id)
            if message is None:
                continue
            data = bytes.fromhex(match.group("data"))[: int(match.group("dlc"))]
            if len(data) != message.length:
                continue
            try:
                decoded = message.decode(data, decode_choices=True, scaling=True)
            except Exception:
                continue
            decoded_frames += 1
            for name, value in decoded.items():
                key = (frame_id, name)
                if key in selected:
                    samples[key].append(Sample(timestamp, scalar(value)))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    csv_path = args.output.with_suffix(".csv")
    rows: list[dict[str, object]] = []
    for category in CATEGORY_PATTERNS:
        for frame_id, signal_name in sorted(category_defs[category]):
            message = messages[frame_id]
            signal_samples = samples.get((frame_id, signal_name), [])
            for window_name, (start, end) in WINDOWS.items():
                values = [s.value for s in signal_samples if start <= s.time <= end]
                center, minimum, maximum, changes = summarize(values)
                rows.append({
                    "category": category,
                    "can_id": f"0x{frame_id:03X}",
                    "message": message.name,
                    "signal": signal_name,
                    "dbc_id_seen": "yes" if frame_id in seen_ids else "no",
                    "decoded_samples": len(signal_samples),
                    "window": window_name,
                    "center_or_mode": center,
                    "min": minimum,
                    "max": maximum,
                    "changes": changes,
                })
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# TM3 system and boundary variable coverage",
        "",
        f"- ASC frames: {total_frames}",
        f"- DBC decoded frames: {decoded_frames}",
        f"- Observed CAN IDs: {len(seen_ids)}",
        "",
    ]
    for category in CATEGORY_PATTERNS:
        definitions = category_defs[category]
        observed = [key for key in definitions if key in samples]
        lines.extend([
            f"## {category}",
            "",
            f"- DBC definitions: {len(definitions)}",
            f"- Signals decoded in this capture: {len(observed)}",
            "",
            "| CAN ID | Message | Signal | pre | brake | post/final |",
            "|---:|---|---|---:|---:|---:|",
        ])
        for frame_id, signal_name in observed:
            ss = samples[(frame_id, signal_name)]
            vals = []
            for window in ("pre_stable", "brake_pressed", "final_stable"):
                start, end = WINDOWS[window]
                center, _, _, _ = summarize([s.value for s in ss if start <= s.time <= end])
                vals.append(center or "-")
            lines.append(f"| 0x{frame_id:03X} | {messages[frame_id].name} | {signal_name} | {vals[0]} | {vals[1]} | {vals[2]} |")
        if not observed:
            lines.append("| - | - | No matching DBC signal decoded | - | - | - |")
        lines.append("")
    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(args.output)
    print(csv_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
