"""Generate a compact, reproducible signal summary for TM3-004."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import cantools

from asc_dbc_signal_trace import parse_asc_line


ROOT = Path(__file__).resolve().parents[1]
ASC = ROOT / "input" / "can_20260827135814_TM3-004_低速加速采集.asc"
DBC = ROOT / "input" / "tesla_model3_ONYX.dbc"
OUT = ROOT / "output" / "TM3-004" / "TM3-004_关键链路采样.csv"

TARGETS = {
    0x118: ("DI_accelPedalPos", "DI_gear", "DI_systemState"),
    0x108: ("DI_torqueCommand", "DI_torqueActual", "DI_axleSpeed", "DI_slavePedalPos"),
    0x257: ("DI_vehicleSpeed", "DI_uiSpeed"),
    0x266: ("DI_elecPower",),
    0x1D8: ("DIS_torqueCommand", "DIS_torqueActual", "DIS_axleSpeed", "DIS_frontSlavePedalPos"),
    0x132: ("BMS_packVoltage", "BMS_packCurrent", "BMS_currentUnfiltered"),
    0x2D2: ("BMS_maxDischargeCurrent", "BMS_maxChargeCurrent"),
    0x268: ("DI_sysDrivePowerMax", "DI_sysRegenPowerMax"),
    0x7AA: ("HVP_packVoltage", "HVP_dcLinkVoltage", "HVP_shuntCurrentDebug"),
    0x3C2: ("VCLEFT_brakeSwitchPressed",),
    0x229: ("SCCM_gearStalkStatus", "SCCM_parkButtonStatus"),
    0x3C5: ("DIS_a154_resolver",),
}


def number(value):
    return float(value) if isinstance(value, (int, float)) else value


def signed_le(data: bytes, start: int, length: int) -> int:
    raw = (int.from_bytes(data, "little") >> start) & ((1 << length) - 1)
    return raw - (1 << length) if raw & (1 << (length - 1)) else raw


def main():
    db = cantools.database.load_file(DBC, database_format="dbc", strict=False)
    messages = {frame_id: db.get_message_by_frame_id(frame_id) for frame_id in TARGETS}
    series = defaultdict(list)
    decode_errors = defaultdict(int)
    first_decode_error = {}

    with ASC.open("r", encoding="utf-8", errors="replace") as source:
        for line in source:
            frame = parse_asc_line(line)
            if not frame or frame["can_id"] not in TARGETS:
                continue
            message = messages[frame["can_id"]]
            try:
                if frame["can_id"] == 0x1D8:
                    # The source DBC overlaps the pedal byte and checksum byte,
                    # which cantools refuses to unpack. The non-overlapping
                    # torque/speed fields are decoded directly from the DBC bits.
                    values = {
                        "DIS_torqueCommand": signed_le(frame["data"], 8, 15) * 0.1,
                        "DIS_torqueActual": signed_le(frame["data"], 24, 13) * 2.0,
                        "DIS_axleSpeed": signed_le(frame["data"], 40, 16) * 0.1,
                    }
                else:
                    values = message.decode(
                        frame["data"], decode_choices=True, allow_truncated=True
                    )
            except Exception as exc:
                decode_errors[frame["can_id"]] += 1
                first_decode_error.setdefault(
                    frame["can_id"],
                    (frame["dlc"], frame["data"].hex(" "), repr(exc)),
                )
                continue
            for signal in TARGETS[frame["can_id"]]:
                if signal in values:
                    series[signal].append((frame["time"], number(values[signal])))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(("signal", "time_s", "value"))
        for signal, samples in series.items():
            for timestamp, value in samples:
                writer.writerow((signal, f"{timestamp:.6f}", value))

    print("DECODE_ERRORS", {f"0x{k:X}": v for k, v in decode_errors.items()})
    print("FIRST_DECODE_ERRORS", {f"0x{k:X}": v for k, v in first_decode_error.items()})
    for signal, samples in series.items():
        numeric = [(t, v) for t, v in samples if isinstance(v, float)]
        if numeric:
            vals = [v for _, v in numeric]
            print(f"RANGE {signal}: n={len(vals)} min={min(vals):.4f} max={max(vals):.4f}")

    for start, end, label in ((30, 60, "run1"), (95, 125, "run2")):
        print(f"WINDOW {label} {start}-{end}")
        for signal in (
            "DI_accelPedalPos", "DI_torqueCommand", "DI_torqueActual", "DI_axleSpeed",
            "DI_vehicleSpeed", "DI_elecPower", "DIS_torqueCommand", "DIS_torqueActual",
            "BMS_packVoltage", "BMS_packCurrent", "HVP_dcLinkVoltage",
        ):
            vals = [(t, v) for t, v in series.get(signal, []) if start <= t <= end and isinstance(v, float)]
            if vals:
                print(f"  {signal}: min={min(v for _, v in vals):.4f} max={max(v for _, v in vals):.4f}")

    for threshold_signal, threshold in (
        ("DI_accelPedalPos", 0.0),
        ("DI_torqueCommand", 0.0),
        ("DI_torqueActual", 0.0),
        ("DI_axleSpeed", 5.0),
        ("DI_vehicleSpeed", 0.5),
    ):
        samples = series.get(threshold_signal, [])
        print("ONSETS", threshold_signal)
        active = False
        for timestamp, value in samples:
            if not isinstance(value, float):
                continue
            now = value > threshold
            if now and not active:
                print(f"  {timestamp:.6f} value={value}")
            active = now

    for signal in ("DI_gear", "DI_systemState", "VCLEFT_brakeSwitchPressed", "SCCM_gearStalkStatus", "SCCM_parkButtonStatus"):
        print("CHANGES", signal)
        previous = object()
        for timestamp, value in series.get(signal, []):
            if str(value) != str(previous):
                print(f"  {timestamp:.6f} {value}")
                previous = value


if __name__ == "__main__":
    main()
