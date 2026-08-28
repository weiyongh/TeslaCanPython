"""Reproducible static battery baseline extraction for TM3-006."""

from collections import defaultdict
import csv
import re
from pathlib import Path

import cantools

from asc_dbc_signal_trace import parse_asc_line


ROOT = Path(__file__).resolve().parents[1]
ASC = ROOT / "input" / "can_20260827141104_TM3-006_动力电池静态基线采集.asc"
DBC = ROOT / "input" / "tesla_model3_ONYX.dbc"
OUT = ROOT / "output" / "TM3-006" / "TM3-006_动力电池信号采样.csv"

EXPLICIT = {
    "BMS_packVoltage", "BMS_packCurrent", "BMS_currentUnfiltered",
    "BMS_socMin", "BMS_socUI", "BMS_socMax", "BMS_socAvg",
    "BMS_initialFullPackEnergy", "BMS_nominalFullPackEnergy",
    "BMS_nominalEnergyRemaining", "BMS_idealEnergyRemaining",
    "BMS_energyBuffer", "BMS_expectedEnergyRemaining", "BMS_energyToChargeComplete",
    "BMS_brickVoltageMax", "BMS_brickVoltageMin",
    "BMS_brickNumVoltageMax", "BMS_brickNumVoltageMin",
    "BMS_packTMin", "BMS_packTMax", "BMS_minPackTemperature",
    "BMS_maxChargeCurrent", "BMS_maxDischargeCurrent",
    "BMS_maxDischargePower", "BMS_maxRegenPower", "BMS_powerLimitsState",
    "BMS_minBusVoltage", "BMS_maxBusVoltage",
    "BMS_contactorState", "BMS_isolationResistance",
    "BMS_notEnoughPowerForDrive", "BMS_notEnoughPowerForSupport",
    "HVP_packContactorSetState", "HVP_fcContactorSetState", "HVP_hvilStatus",
    "HVP_packVoltage", "HVP_dcLinkVoltage", "HVP_battery12V",
    "DI_gear", "DI_systemState", "DI_torqueCommand", "DI_torqueActual", "DI_axleSpeed",
}


def main():
    db = cantools.database.load_file(DBC, database_format="dbc", strict=False)
    wanted_by_id = defaultdict(set)
    messages = {}
    for message in db.messages:
        chosen = {
            signal.name for signal in message.signals
            if signal.name in EXPLICIT
            or re.fullmatch(r"BMS_brick\d+", signal.name)
            or signal.name.startswith("BMS_a")
            or signal.name.startswith("HVP_w")
        }
        if chosen:
            wanted_by_id[message.frame_id].update(chosen)
            messages[message.frame_id] = message

    series = defaultdict(list)
    errors = defaultdict(int)
    with ASC.open("r", encoding="utf-8", errors="replace") as source:
        for line in source:
            frame = parse_asc_line(line)
            if not frame or frame["can_id"] not in wanted_by_id:
                continue
            try:
                if frame["can_id"] == 0x252:
                    # The source DBC overlaps BMS_hvacPowerBudget with other
                    # fields. The two non-overlapping 16-bit power limits are
                    # decoded directly from their documented little-endian bits.
                    raw = int.from_bytes(frame["data"], "little")
                    values = {
                        "BMS_maxRegenPower": (raw & 0xFFFF) * 0.01,
                        "BMS_maxDischargePower": ((raw >> 16) & 0xFFFF) * 0.01,
                        "BMS_maxStationaryHeatPower": ((raw >> 32) & 0x3FF) * 0.01,
                        "BMS_powerLimitsState": float((raw >> 48) & 0x1),
                    }
                else:
                    values = messages[frame["can_id"]].decode(
                        frame["data"], decode_choices=True, allow_truncated=True
                    )
            except Exception:
                errors[frame["can_id"]] += 1
                continue
            for signal in wanted_by_id[frame["can_id"]]:
                if signal in values:
                    value = values[signal]
                    if isinstance(value, (int, float)):
                        value = float(value)
                    series[signal].append((frame["time"], value))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(("signal", "time_s", "value"))
        for signal, samples in sorted(series.items()):
            for timestamp, value in samples:
                writer.writerow((signal, f"{timestamp:.6f}", value))

    print("FRAMES_ERRORS", {f"0x{k:X}": v for k, v in errors.items()})
    for signal in sorted(EXPLICIT):
        samples = series.get(signal, [])
        numeric = [(t, v) for t, v in samples if isinstance(v, float)]
        if numeric:
            vals = [v for _, v in numeric]
            print(f"RANGE {signal} n={len(vals)} min={min(vals):.6f} max={max(vals):.6f} avg={sum(vals)/len(vals):.6f}")
        elif samples:
            print(f"VALUES {signal} {sorted({str(v) for _, v in samples})}")
        else:
            print(f"MISSING {signal}")

    for start, end, label in ((10, 40, "stable1"), (40, 70, "stable2"), (70, 90, "stable3")):
        print(f"WINDOW {label}")
        for signal in (
            "BMS_packVoltage", "BMS_packCurrent", "BMS_socAvg", "BMS_socUI",
            "BMS_brickVoltageMax", "BMS_brickVoltageMin",
            "BMS_maxChargeCurrent", "BMS_maxDischargeCurrent",
            "HVP_packVoltage", "HVP_dcLinkVoltage", "HVP_battery12V",
        ):
            vals = [v for t, v in series.get(signal, []) if start <= t <= end and isinstance(v, float)]
            if vals:
                print(f"  {signal}: min={min(vals):.6f} max={max(vals):.6f} avg={sum(vals)/len(vals):.6f}")

    bricks = {
        signal: [v for _, v in samples if isinstance(v, float)]
        for signal, samples in series.items() if re.fullmatch(r"BMS_brick\d+", signal)
    }
    brick_means = {signal: sum(vals) / len(vals) for signal, vals in bricks.items() if vals}
    print(f"BRICKS decoded={len(brick_means)}")
    if brick_means:
        valid_bricks = {signal: value for signal, value in brick_means.items() if 2.5 <= value <= 4.5}
        invalid_bricks = {signal: value for signal, value in brick_means.items() if signal not in valid_bricks}
        low = min(valid_bricks.items(), key=lambda x: x[1])
        high = max(valid_bricks.items(), key=lambda x: x[1])
        print(f"BRICKS_VALID {len(valid_bricks)} INVALID_OR_UNUSED {len(invalid_bricks)}")
        print("BRICKS_INVALID", sorted(invalid_bricks.items()))
        print(f"BRICK_MEAN_LOW {low[0]} {low[1]:.6f}")
        print(f"BRICK_MEAN_HIGH {high[0]} {high[1]:.6f}")
        print(f"BRICK_MEAN_SPREAD {high[1] - low[1]:.6f}")
        all_values = [v for signal, vals in bricks.items() if signal in valid_bricks for v in vals]
        print(f"BRICK_ALL min={min(all_values):.6f} max={max(all_values):.6f}")

    active_alerts = []
    for signal, samples in series.items():
        if re.match(r"^(BMS_a|HVP_w)\d{3}_", signal):
            numeric = [v for _, v in samples if isinstance(v, float)]
            if numeric and max(numeric) != 0:
                active_alerts.append((signal, min(numeric), max(numeric)))
    print("ACTIVE_ALERTS", active_alerts)


if __name__ == "__main__":
    main()
