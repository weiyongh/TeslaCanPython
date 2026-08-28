"""Generate a compact, reproducible regeneration summary for TM3-005."""

from collections import defaultdict
import csv
from pathlib import Path

import cantools

from analyze_tm3_004 import TARGETS, number, signed_le
from asc_dbc_signal_trace import parse_asc_line


ROOT = Path(__file__).resolve().parents[1]
ASC = ROOT / "input" / "can_20260827140713_TM3-005_低速松电门回收采集.asc"
DBC = ROOT / "input" / "tesla_model3_ONYX.dbc"
OUT = ROOT / "output" / "TM3-005" / "TM3-005_关键链路采样.csv"


def main():
    db = cantools.database.load_file(DBC, database_format="dbc", strict=False)
    messages = {frame_id: db.get_message_by_frame_id(frame_id) for frame_id in TARGETS}
    series = defaultdict(list)
    errors = defaultdict(int)

    with ASC.open("r", encoding="utf-8", errors="replace") as source:
        for line in source:
            frame = parse_asc_line(line)
            if not frame or frame["can_id"] not in TARGETS:
                continue
            try:
                if frame["can_id"] == 0x1D8:
                    values = {
                        "DIS_torqueCommand": signed_le(frame["data"], 8, 15) * 0.1,
                        "DIS_torqueActual": signed_le(frame["data"], 24, 13) * 2.0,
                        "DIS_axleSpeed": signed_le(frame["data"], 40, 16) * 0.1,
                    }
                else:
                    values = messages[frame["can_id"]].decode(
                        frame["data"], decode_choices=True, allow_truncated=True
                    )
            except Exception:
                errors[frame["can_id"]] += 1
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

    print("DECODE_ERRORS", {f"0x{k:X}": v for k, v in errors.items()})
    for start, end, label in ((35, 55, "regen1"), (90, 110, "regen2")):
        print(f"WINDOW {label} {start}-{end}")
        for signal in (
            "DI_accelPedalPos", "DI_torqueCommand", "DI_torqueActual", "DI_axleSpeed",
            "DI_vehicleSpeed", "DI_elecPower", "BMS_packVoltage", "BMS_packCurrent",
            "BMS_maxChargeCurrent", "HVP_dcLinkVoltage",
        ):
            vals = [(t, v) for t, v in series.get(signal, []) if start <= t <= end and isinstance(v, float)]
            if vals:
                minimum = min(vals, key=lambda x: x[1])
                maximum = max(vals, key=lambda x: x[1])
                print(f"  {signal}: min={minimum[1]:.4f}@{minimum[0]:.6f} max={maximum[1]:.4f}@{maximum[0]:.6f}")

    for signal in ("DI_accelPedalPos", "DI_torqueCommand", "DI_torqueActual", "BMS_packCurrent", "DI_elecPower", "DI_vehicleSpeed"):
        print("ZERO_OR_NEGATIVE_TRANSITIONS", signal)
        previous = None
        for timestamp, value in series.get(signal, []):
            if not isinstance(value, float):
                continue
            if previous is not None and previous > 0 and value <= 0:
                print(f"  {timestamp:.6f} prev={previous} value={value}")
            previous = value

    for signal in ("DI_gear", "DI_systemState", "VCLEFT_brakeSwitchPressed"):
        print("CHANGES", signal)
        previous = object()
        for timestamp, value in series.get(signal, []):
            if str(value) != str(previous):
                print(f"  {timestamp:.6f} {value}")
                previous = value


if __name__ == "__main__":
    main()
