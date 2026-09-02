"""Reproducible TM3-008 ASC analysis bound to the Approved Evidence Plan.

This experiment uses the standard TM3-008 ASC derived from source interval
0..660 s, preserving the 600 s collection script plus its 60 s pre-lock phase.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import cantools

from evidence_plan import read_approved_csv


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ASC = ROOT / "input/can_20260831113240_TM3-008_关门落锁完整下电采集.asc"
COLLECTION_SCRIPT = ROOT / "input/TM3-008_关门落锁完整下电采集脚本.txt"
COMBINED_ASC = ROOT / "input/can_20260831113240开关门采集.asc"
SOURCE_START_S = 0.0
SOURCE_END_S = 660.0
ONYX = ROOT / "input/tesla_model3_ONYX.dbc"
APPROVED = ROOT / "output/TM3-008/evidence_plan_approved.csv"
MACHINE = ROOT / "output/TM3-008/machine_evidence"
ASC_RE = re.compile(
    r"^\s*(\d+(?:\.\d+)?)\s+\d+\s+([0-9A-Fa-f]+)\s+Rx\s+d\s+(\d+)\s+"
    r"((?:[0-9A-Fa-f]{2}(?:\s+|$))*)"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def text_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.9f}".rstrip("0").rstrip(".")
    return str(value)


def parse_source_interval():
    frames: dict[int, list[tuple[float, float, bytes]]] = defaultdict(list)
    dlcs: dict[int, Counter] = defaultdict(Counter)
    source_frame_lines = interval_frame_lines = malformed_source = malformed_interval = 0
    first_source = last_source = None
    for line in SOURCE_ASC.open(encoding="utf-8", errors="replace"):
        match = ASC_RE.match(line)
        if not match:
            continue
        source_frame_lines += 1
        source_time = float(match.group(1))
        declared = int(match.group(3))
        raw = bytes.fromhex(match.group(4))
        if len(raw) != declared:
            malformed_source += 1
            if SOURCE_START_S <= source_time <= SOURCE_END_S:
                malformed_interval += 1
            continue
        if source_time < SOURCE_START_S or source_time > SOURCE_END_S:
            continue
        interval_frame_lines += 1
        relative_time = source_time - SOURCE_START_S
        frame_id = int(match.group(2), 16)
        frames[frame_id].append((relative_time, source_time, raw))
        dlcs[frame_id][declared] += 1
        first_source = source_time if first_source is None else min(first_source, source_time)
        last_source = source_time if last_source is None else max(last_source, source_time)
    return frames, dlcs, {
        "source_frame_line_count": source_frame_lines,
        "source_malformed_frame_count": malformed_source,
        "interval_parsed_frame_count": interval_frame_lines,
        "interval_malformed_frame_count": malformed_interval,
        "interval_first_source_frame_s": first_source,
        "interval_last_source_frame_s": last_source,
    }


def decode_message_signal(message, raw: bytes, signal_name: str):
    adjusted = raw[: message.length] + bytes(max(0, message.length - len(raw)))
    return message.decode(adjusted, decode_choices=True, allow_truncated=True).get(signal_name)


def compact_observed(samples: list[tuple[float, object, str]]) -> str:
    if not samples:
        return ""
    values = [item[1] for item in samples]
    numeric = [float(value) for value in values if isinstance(value, (int, float))]
    if len(numeric) == len(values) and len(set(numeric)) > 12:
        return f"{min(numeric):.6f}..{max(numeric):.6f}"
    unique = list(dict.fromkeys(text_value(value) for value in values))
    return " | ".join(unique[:20])


def transition_rows(signal_key: str, samples: list[tuple[float, object, str]]) -> list[dict]:
    rows = []
    sentinel = object()
    previous = sentinel
    for timestamp, value, raw_hex in samples:
        if value != previous:
            rows.append({
                "time_s": f"{timestamp:.6f}", "signal_key": signal_key,
                "value": text_value(value), "raw_hex": raw_hex,
            })
            previous = value
    return rows


def first_value_time(samples, wanted: str) -> float | None:
    for timestamp, value, _raw in samples:
        if text_value(value) == wanted:
            return timestamp
    return None


def first_value_time_after(samples, wanted: str, after_s: float) -> float | None:
    for timestamp, value, _raw in samples:
        if timestamp >= after_s and text_value(value) == wanted:
            return timestamp
    return None


def first_numeric_below(samples, threshold: float, after_s: float = 0.0) -> float | None:
    for timestamp, value, _raw in samples:
        if timestamp >= after_s and isinstance(value, (int, float)) and float(value) < threshold:
            return timestamp
    return None


def window_numeric(samples, start_s: float, end_s: float) -> dict[str, object]:
    values = [float(value) for timestamp, value, _raw in samples
              if start_s <= timestamp < end_s and isinstance(value, (int, float))]
    if not values:
        return {"count": 0, "min": None, "max": None, "mean": None}
    return {
        "count": len(values), "min": min(values), "max": max(values),
        "mean": statistics.mean(values),
    }


def main() -> None:
    plan = read_approved_csv(APPROVED)
    active = [row for row in plan.signals if row.effective_report_position != "EXCLUDE"]
    excluded = [row for row in plan.signals if row.effective_report_position == "EXCLUDE"]
    frames, dlcs, parse_stats = parse_source_interval()
    times = [time_s for rows in frames.values() for time_s, _source_time, _raw in rows]
    if not times:
        raise RuntimeError("TM3-008 source interval contains no valid frames")
    start_s, end_s = min(times), max(times)
    MACHINE.mkdir(parents=True, exist_ok=True)

    source_header = SOURCE_ASC.read_text(encoding="utf-8", errors="replace").splitlines()[:7]
    integrity = {
        "experiment_id": "TM3-008",
        "analysis_status": "ASC_PARSED_SIGNAL_ANALYSIS_IN_PROGRESS",
        "approved_plan_status": plan.plan_status,
        "approved_plan_scope": plan.scope,
        "approved_plan_sha256": sha256(APPROVED),
        "approved_active_candidate_count": len(active),
        "approved_excluded_candidate_count": len(excluded),
        "source_asc_path": str(SOURCE_ASC.relative_to(ROOT)),
        "source_asc_sha256": sha256(SOURCE_ASC),
        "source_asc_size_bytes": SOURCE_ASC.stat().st_size,
        "source_interval_s": [SOURCE_START_S, SOURCE_END_S],
        "input_file_declared_interval_s": [SOURCE_START_S, SOURCE_END_S],
        "collection_script_path": str(COLLECTION_SCRIPT.relative_to(ROOT)),
        "collection_script_sha256": sha256(COLLECTION_SCRIPT),
        "collection_script_duration_s": 600.0,
        "declared_interval_covers_script": (SOURCE_END_S - SOURCE_START_S) >= 600.0,
        "declared_interval_margin_after_script_s": (SOURCE_END_S - SOURCE_START_S) - 600.0,
        "timestamps_rebased_to_interval_start": True,
        "interval_start_s": start_s,
        "interval_end_s": end_s,
        "interval_observed_duration_s": end_s - start_s,
        "interval_nominal_duration_s": SOURCE_END_S - SOURCE_START_S,
        "unique_can_id_count": len(frames),
        **parse_stats,
        "combined_asc_path": str(COMBINED_ASC.relative_to(ROOT)),
        "combined_asc_sha256": sha256(COMBINED_ASC),
        "source_file_header": source_header,
        "input_identity_decision": (
            "The standard TM3-008 ASC is the sole ASC input. Its declared source "
            "interval is 0..660 s, covering the collection script's 0..600 s timeline "
            "with 60 s margin. The last CAN frame is earlier because the capture domain "
            "becomes silent; this is not treated as evidence that the declared file "
            "interval ended at the last frame timestamp."
        ),
        "onyx_dbc_sha256": sha256(ONYX),
    }
    write_json(MACHINE / "asc_integrity.json", integrity)

    onyx = cantools.database.load_file(ONYX, strict=False)
    samples_by_signal: dict[str, list[tuple[float, object, str]]] = defaultdict(list)
    native_rows: list[dict] = []
    decode_errors = Counter()
    for approved in active:
        if approved.can_id == "derived":
            continue
        frame_id = int(approved.can_id, 16)
        try:
            message = onyx.get_message_by_frame_id(frame_id)
        except KeyError:
            decode_errors[approved.signal_key] += len(frames[frame_id])
            continue
        for relative_time, source_time, raw in frames[frame_id]:
            try:
                value = decode_message_signal(message, raw, approved.signal)
            except Exception:
                decode_errors[approved.signal_key] += 1
                continue
            if value is None:
                decode_errors[approved.signal_key] += 1
                continue
            raw_hex = raw.hex(" ")
            samples_by_signal[approved.signal_key].append((relative_time, value, raw_hex))
            native_rows.append({
                "time_s": f"{relative_time:.6f}",
                "source_time_s": f"{source_time:.6f}",
                "signal_key": approved.signal_key,
                "can_id": approved.can_id,
                "asc_dlc": len(raw),
                "raw_hex": raw_hex,
                "decoded_value": text_value(value),
                "decode_source": "input/tesla_model3_ONYX.dbc",
            })
    write_csv(MACHINE / "decoded_approved_samples.csv", native_rows)

    # Network system-result evidence, strictly limited to this capture domain.
    per_second = Counter(int(time_s) for time_s in times)
    ids_per_second: dict[int, set[int]] = defaultdict(set)
    for frame_id, rows in frames.items():
        for time_s, _source_time, _raw in rows:
            ids_per_second[int(time_s)].add(frame_id)
    network_rows = [
        {
            "second": second,
            "frame_count": per_second[second],
            "active_can_id_count": len(ids_per_second[second]),
        }
        for second in range(0, int(SOURCE_END_S - SOURCE_START_S) + 1)
    ]
    write_csv(MACHINE / "network_activity_1s.csv", network_rows)
    last_seen_rows = []
    for frame_id, rows in sorted(frames.items()):
        if not rows:
            continue
        first, last = rows[0], rows[-1]
        last_seen_rows.append({
            "can_id": f"0x{frame_id:X}", "frame_count": len(rows),
            "asc_dlcs": "+".join(str(x) for x in sorted(dlcs[frame_id])),
            "first_seen_s": f"{first[0]:.6f}", "last_seen_s": f"{last[0]:.6f}",
            "source_last_seen_s": f"{last[1]:.6f}",
        })
    write_csv(MACHINE / "can_id_lifetime.csv", last_seen_rows)

    # Definition audit for every active Approved native candidate.
    approved_names = {row.signal for row in active if row.can_id != "derived"}
    dbc_sources = [ONYX] + sorted((ROOT / "dbc").glob("*.dbc"))
    definition_rows = []
    definition_decode_rows = []
    for dbc_path in dbc_sources:
        try:
            database = cantools.database.load_file(dbc_path, strict=False)
        except Exception:
            continue
        for message in database.messages:
            matching = [signal for signal in message.signals if signal.name in approved_names]
            for dbc_signal in matching:
                fingerprint = (
                    f"{message.frame_id:X}:{message.length}:{dbc_signal.start}:{dbc_signal.length}:"
                    f"{dbc_signal.byte_order}:{int(dbc_signal.is_signed)}:{dbc_signal.scale}:{dbc_signal.offset}"
                )
                actual_rows = frames.get(message.frame_id, [])
                decoded_values = []
                errors = 0
                for relative_time, _source_time, raw in actual_rows:
                    try:
                        value = decode_message_signal(message, raw, dbc_signal.name)
                    except Exception:
                        errors += 1
                        continue
                    if value is not None:
                        decoded_values.append((relative_time, value))
                definition_rows.append({
                    "signal_key": dbc_signal.name,
                    "source": str(dbc_path.relative_to(ROOT)),
                    "message": message.name,
                    "can_id": f"0x{message.frame_id:X}", "dbc_dlc": message.length,
                    "start_bit": dbc_signal.start, "bit_length": dbc_signal.length,
                    "byte_order": dbc_signal.byte_order, "signed": dbc_signal.is_signed,
                    "factor": dbc_signal.scale, "offset": dbc_signal.offset,
                    "unit": dbc_signal.unit or "", "definition_fingerprint": fingerprint,
                })
                definition_decode_rows.append({
                    "signal_key": dbc_signal.name,
                    "source": str(dbc_path.relative_to(ROOT)),
                    "can_id": f"0x{message.frame_id:X}", "definition_fingerprint": fingerprint,
                    "asc_frame_count": len(actual_rows),
                    "asc_dlcs": "+".join(str(x) for x in sorted(dlcs[message.frame_id])) or "NO_FRAME",
                    "decoded_count": len(decoded_values), "decode_error_count": errors,
                    "first_value": text_value(decoded_values[0][1]) if decoded_values else "",
                    "last_value": text_value(decoded_values[-1][1]) if decoded_values else "",
                    "observed": compact_observed([(time_s, value, "") for time_s, value in decoded_values]),
                })
    write_csv(MACHINE / "dbc_definition_comparison.csv", definition_rows)
    write_csv(MACHINE / "multi_dbc_decode_summary.csv", definition_decode_rows)

    summary_rows = []
    coverage_rows = []
    transition_output = []
    for approved in plan.signals:
        if approved.effective_report_position == "EXCLUDE":
            coverage_rows.append({
                "signal_key": approved.signal_key, "can_id": approved.can_id,
                "evidence_requirement": approved.evidence_requirement,
                "effective_role": approved.effective_role,
                "effective_priority": approved.effective_priority,
                "frame_count": 0, "asc_actual_dlc": "NOT_ANALYZED",
                "decoded_sample_count": 0, "readability": "EXCLUDED_NOT_ANALYZED",
                "first_value": "", "last_value": "", "observed": "",
                "transition_count": 0, "draft_maturity": approved.semantic_status,
                "analysis_note": approved.human_reason,
            })
            continue
        if approved.signal_key == "NetworkFrameRate_derived":
            values = [row["frame_count"] for row in network_rows]
            coverage_rows.append({
                "signal_key": approved.signal_key, "can_id": "derived",
                "evidence_requirement": approved.evidence_requirement,
                "effective_role": approved.effective_role,
                "effective_priority": approved.effective_priority,
                "frame_count": len(network_rows), "asc_actual_dlc": "derived",
                "decoded_sample_count": len(network_rows), "readability": "READABLE",
                "first_value": values[0], "last_value": values[-1],
                "observed": f"{min(values)}..{max(values)} frames/s",
                "transition_count": "", "draft_maturity": approved.semantic_status,
                "analysis_note": "CURRENT_CAPTURE_DOMAIN_ONLY",
            })
            continue
        if approved.signal_key == "ActiveCanIdCount_derived":
            values = [row["active_can_id_count"] for row in network_rows]
            coverage_rows.append({
                "signal_key": approved.signal_key, "can_id": "derived",
                "evidence_requirement": approved.evidence_requirement,
                "effective_role": approved.effective_role,
                "effective_priority": approved.effective_priority,
                "frame_count": len(network_rows), "asc_actual_dlc": "derived",
                "decoded_sample_count": len(network_rows), "readability": "READABLE",
                "first_value": values[0], "last_value": values[-1],
                "observed": f"{min(values)}..{max(values)} IDs/s",
                "transition_count": "", "draft_maturity": approved.semantic_status,
                "analysis_note": "CURRENT_CAPTURE_DOMAIN_ONLY",
            })
            continue
        if approved.signal_key == "CanIdLastSeenTime_derived":
            last_values = [float(row["last_seen_s"]) for row in last_seen_rows]
            coverage_rows.append({
                "signal_key": approved.signal_key, "can_id": "derived",
                "evidence_requirement": approved.evidence_requirement,
                "effective_role": approved.effective_role,
                "effective_priority": approved.effective_priority,
                "frame_count": len(last_seen_rows), "asc_actual_dlc": "derived",
                "decoded_sample_count": len(last_seen_rows), "readability": "READABLE",
                "first_value": f"{min(last_values):.6f}", "last_value": f"{max(last_values):.6f}",
                "observed": f"{min(last_values):.6f}..{max(last_values):.6f} s",
                "transition_count": "", "draft_maturity": approved.semantic_status,
                "analysis_note": "MESSAGE_LAST_SEEN_IS_NOT_ECU_POWER_OFF",
            })
            continue
        frame_id = int(approved.can_id, 16)
        samples = samples_by_signal.get(approved.signal_key, [])
        transitions = transition_rows(approved.signal_key, samples)
        if len(transitions) <= 5000:
            transition_output.extend(transitions)
        first_value = text_value(samples[0][1]) if samples else ""
        last_value = text_value(samples[-1][1]) if samples else ""
        actual_dlc = "+".join(str(x) for x in sorted(dlcs[frame_id])) or "NO_FRAME"
        readability = "NO_FRAME" if not frames[frame_id] else ("READABLE" if samples else "UNREADABLE")
        coverage_rows.append({
            "signal_key": approved.signal_key, "can_id": approved.can_id,
            "evidence_requirement": approved.evidence_requirement,
            "effective_role": approved.effective_role,
            "effective_priority": approved.effective_priority,
            "frame_count": len(frames[frame_id]), "asc_actual_dlc": actual_dlc,
            "decoded_sample_count": len(samples), "readability": readability,
            "first_value": first_value, "last_value": last_value,
            "observed": compact_observed(samples), "transition_count": len(transitions),
            "draft_maturity": approved.semantic_status,
            "analysis_note": f"decode_errors={decode_errors[approved.signal_key]}",
        })
        summary_rows.append({
            "signal_key": approved.signal_key, "can_id": approved.can_id,
            "first_time_s": f"{samples[0][0]:.6f}" if samples else "",
            "last_time_s": f"{samples[-1][0]:.6f}" if samples else "",
            "first_value": first_value, "last_value": last_value,
            "observed": compact_observed(samples), "transition_count": len(transitions),
        })
    write_csv(MACHINE / "approved_candidate_coverage.csv", coverage_rows)
    write_csv(MACHINE / "signal_summary.csv", summary_rows)
    write_csv(MACHINE / "categorical_transitions.csv", transition_output)

    # Preserve the Approved 0x20A raw-bit view without selecting a conflicting DBC conclusion.
    raw_20a = []
    for relative_time, source_time, raw in frames.get(0x20A, []):
        little = int.from_bytes(raw, "little")
        raw_20a.append({
            "time_s": f"{relative_time:.6f}", "source_time_s": f"{source_time:.6f}",
            "asc_dlc": len(raw), "raw_hex": raw.hex(" "),
            "bits_0_2": little & 0x7, "bits_3_5": (little >> 3) & 0x7,
        })
    write_csv(MACHINE / "signal_validation_0x20A_raw.csv", raw_20a)

    # Experiment-specific state reconstruction.  These events are derived from
    # observed transitions, never from the planned script timestamps.
    power_off = first_value_time(samples_by_signal["VCFRONT_vehiclePowerState"], "OFF")
    bms_opening = first_value_time(samples_by_signal["BMS_contactorState"], "OPENING")
    bms_open = first_value_time(samples_by_signal["BMS_contactorState"], "OPEN")
    positive_opening = first_value_time(samples_by_signal["HVP_packContPositiveState"], "OPENING")
    positive_open = first_value_time(samples_by_signal["HVP_packContPositiveState"], "OPEN")
    negative_opening = first_value_time(samples_by_signal["HVP_packContNegativeState"], "OPENING")
    negative_open = first_value_time(samples_by_signal["HVP_packContNegativeState"], "OPEN")
    dcdc_idle = first_value_time_after(
        samples_by_signal["PCS_dcdc12VSupportStatus"], "IDLE", power_off or 0.0
    )
    discharge_active = first_value_time(samples_by_signal["PCS_dcdcHvBusDischargeStatus"], "ACTIVE")
    discharge_idle_after = next(
        (timestamp for timestamp, value, _raw in samples_by_signal["PCS_dcdcHvBusDischargeStatus"]
         if discharge_active is not None and timestamp > discharge_active and text_value(value) == "IDLE"),
        None,
    )
    bms_bus_asleep = first_value_time(samples_by_signal["BMS_hvsBusAsleep"], "1")
    silence_start_s = end_s
    silence_end_s = SOURCE_END_S
    longest_gap_s = silence_end_s - silence_start_s
    voltage_below_60 = first_numeric_below(samples_by_signal["BMS_packVoltage"], 60.0, 80.0)
    voltage_below_15 = first_numeric_below(samples_by_signal["BMS_packVoltage"], 15.0, 80.0)
    door_open = first_value_time(samples_by_signal["VCLEFT_frontLatchStatus"], "OPENED")
    door_closed = first_value_time_after(samples_by_signal["VCLEFT_frontLatchStatus"], "CLOSED", door_open or 0.0)
    lock_request = first_value_time(samples_by_signal["VCSEC_lockRequestType"], "ACTIVE_NFC_LOCK")
    lock_confirmed = first_value_time(samples_by_signal["VCSEC_simpleLockStatus"], "LOCKED")
    ready_exit = first_value_time(samples_by_signal["UI_readyForDrive"], "0")

    expected_event_values = [power_off, bms_opening, dcdc_idle, positive_opening,
                             negative_opening, discharge_active, bms_open,
                             positive_open, negative_open, bms_bus_asleep]
    if any(value is None for value in expected_event_values):
        raise RuntimeError("required observed transition missing during TM3-008 reconstruction")
    key_events = [
        {"event_id": "E00", "time_s": f"{start_s:.6f}", "event": "分析区间开始",
         "evidence": "UI_readyForDrive、门闩、VCSEC锁状态、BMS接触器、DCDC支持",
         "observed": "Ready候选为1、门闩CLOSED、车辆UNLOCKED、接触器CLOSED、DCDC支持ACTIVE",
         "boundary": "DI_gear无可解样本，P挡仍缺直接CAN证据"},
        {"event_id": "E01", "time_s": f"{door_open:.6f}", "event": "驾驶门打开",
         "evidence": "VCLEFT_frontLatchStatus", "observed": "CLOSED→OPENED",
         "boundary": "无占座Signal，不能单独证明人员已经离座"},
        {"event_id": "E02", "time_s": f"{door_closed:.6f}", "event": "驾驶门关闭",
         "evidence": "VCLEFT_frontLatchStatus", "observed": "OPENED→CLOSED",
         "boundary": "门闩反馈，不等于落锁"},
        {"event_id": "E03", "time_s": f"{lock_request:.6f}", "event": "NFC锁止请求候选及锁止反馈",
         "evidence": "VCSEC_lockRequestType+VCSEC_simpleLockStatus+VCSEC_vehicleLockStatus",
         "observed": "ACTIVE_NFC_LOCK；UNLOCKED→LOCKED；ACTIVE_NFC_UNLOCKED→ACTIVE_NFC_LOCKED",
         "boundary": "CAN内部时序支持；ER-10外部刷卡/灯光/声音记录仍缺失"},
        {"event_id": "E04", "time_s": f"{ready_exit:.6f}", "event": "Ready消费者状态候选退出",
         "evidence": "UI_readyForDrive", "observed": "1→0",
         "boundary": "CONSUMER_STATE，不作为许可或控制命令"},
        {"event_id": "E05", "time_s": f"{power_off:.6f}", "event": "车辆供电阶段候选进入OFF",
         "evidence": "VCFRONT_vehiclePowerState", "observed": "CONDITIONING→OFF",
         "boundary": "SYSTEM_RESULT候选，不是下电REQUEST或COMMAND"},
        {"event_id": "E06", "time_s": f"{bms_opening:.6f}", "event": "BMS总接触器开始打开",
         "evidence": "BMS_contactorState", "observed": "CLOSED→OPENING", "boundary": "BMS总状态"},
        {"event_id": "E07", "time_s": f"{dcdc_idle:.6f}", "event": "12V支持状态退出",
         "evidence": "PCS_dcdc12VSupportStatus", "observed": "ACTIVE→IDLE",
         "boundary": "PCS内部状态；外部12V未测"},
        {"event_id": "E08", "time_s": f"{positive_opening:.6f}", "event": "正负接触器候选进入OPENING",
         "evidence": "HVP_packContPositiveState+HVP_packContNegativeState",
         "observed": "ECONOMIZED→OPENING", "boundary": "0x20A实验级多DBC验证"},
        {"event_id": "E09", "time_s": f"{discharge_active:.6f}", "event": "PCS母线放电状态候选激活",
         "evidence": "PCS_dcdcHvBusDischargeStatus", "observed": "IDLE→ACTIVE",
         "boundary": "执行状态候选，不证明母线已去电"},
        {"event_id": "E10", "time_s": f"{bms_open:.6f}", "event": "BMS总接触器打开",
         "evidence": "BMS_contactorState", "observed": "OPENING→OPEN", "boundary": "BMS总状态"},
        {"event_id": "E11", "time_s": f"{voltage_below_60:.6f}", "event": "0x132电压字段快速下降",
         "evidence": "BMS_packVoltage", "observed": "由约353.5 V降至60 V以下并继续下降",
         "boundary": "缩放/动态可信；Pack端物理定位与实测矛盾，不能沿用名称"},
        {"event_id": "E12", "time_s": f"{discharge_idle_after:.6f}", "event": "PCS母线放电状态候选返回IDLE",
         "evidence": "PCS_dcdcHvBusDischargeStatus", "observed": "ACTIVE→IDLE",
         "boundary": "PCS_dcdcHvBusVolt定义失败，不能据此确认下游母线终值"},
        {"event_id": "E13", "time_s": f"{positive_open:.6f}", "event": "正负接触器候选进入OPEN",
         "evidence": "HVP_packContPositiveState+HVP_packContNegativeState", "observed": "OPENING→OPEN",
         "boundary": "0x20A实验级多DBC验证"},
        {"event_id": "E14", "time_s": f"{bms_bus_asleep:.6f}", "event": "BMS发布总线休眠候选",
         "evidence": "BMS_hvsBusAsleep", "observed": "0→1",
         "boundary": "BMS消费者视角，不代表整车全部网络"},
        {"event_id": "E15", "time_s": f"{silence_start_s:.6f}", "event": "本采集域最后一帧/进入末段静默",
         "evidence": "NetworkFrameRate_derived+CanIdLastSeenTime_derived", "observed": "最后一帧后通信为0",
         "boundary": "当前采集域静默候选"},
        {"event_id": "E16", "time_s": f"{silence_end_s:.6f}", "event": "计划采集窗口结束",
         "evidence": "TM3-008拆分边界", "observed": "末段未见通信恢复",
         "boundary": "结束时刻来自用户确认和拆分合同，不是CAN事件"},
    ]
    write_csv(MACHINE / "key_events.csv", key_events)

    phases = [
        ("W00", "起始可用/开关门/落锁", start_s, lock_confirmed),
        ("W01", "落锁后需求与网络分层退出", lock_confirmed, power_off),
        ("W02", "高压与DCDC最终退出", power_off, positive_open),
        ("W03", "接触器打开后网络尾段", positive_open, silence_start_s),
        ("W04", "采集域末段静默", silence_start_s, silence_end_s),
    ]
    phase_rows = []
    for phase_id, label, left, right in phases:
        seconds = [row for row in network_rows if left <= int(row["second"]) < right]
        phase_rows.append({
            "phase_id": phase_id, "phase": label, "start_s": f"{left:.6f}", "end_s": f"{right:.6f}",
            "duration_s": f"{right-left:.6f}",
            "mean_frames_per_s": f"{statistics.mean([row['frame_count'] for row in seconds]):.3f}" if seconds else "",
            "min_frames_per_s": min((row["frame_count"] for row in seconds), default=""),
            "max_frames_per_s": max((row["frame_count"] for row in seconds), default=""),
            "mean_active_ids_per_s": f"{statistics.mean([row['active_can_id_count'] for row in seconds]):.3f}" if seconds else "",
            "boundary": "CURRENT_CAPTURE_DOMAIN_ONLY",
        })
    write_csv(MACHINE / "analysis_windows.csv", phase_rows)

    pre_silence_lifetime_rows = []
    for frame_id, rows in sorted(frames.items()):
        before = [row for row in rows if row[0] <= silence_start_s]
        after = [row for row in rows if row[0] >= silence_end_s]
        if not before:
            continue
        pre_silence_lifetime_rows.append({
            "can_id": f"0x{frame_id:X}", "pre_silence_frame_count": len(before),
            "last_seen_before_silence_s": f"{before[-1][0]:.6f}",
            "first_seen_after_silence_s": f"{after[0][0]:.6f}" if after else "",
            "returned_after_silence": "YES" if after else "NO",
        })
    write_csv(MACHINE / "can_id_pre_silence_lifetime.csv", pre_silence_lifetime_rows)

    # Resolve the useful 0x2B4 low-voltage candidates against the actual DLC 6
    # ETH/JSON definition, while retaining the failed ONYX high-voltage candidate.
    eth_path = ROOT / "dbc/Model3_ETH_json_reference_optional.dbc"
    eth = cantools.database.load_file(eth_path, strict=False)
    eth_2b4 = eth.get_message_by_frame_id(0x2B4)
    alt_samples = defaultdict(list)
    alt_rows = []
    for time_s, source_time, raw in frames[0x2B4]:
        for name in ("PCS_dcdcLvBusVolt", "PCS_dcdcLvOutputCurrent"):
            value = decode_message_signal(eth_2b4, raw, name)
            alt_samples[name].append((time_s, value, raw.hex(" ")))
            alt_rows.append({
                "time_s": f"{time_s:.6f}", "source_time_s": f"{source_time:.6f}",
                "signal_key": name, "can_id": "0x2B4", "asc_dlc": len(raw),
                "raw_hex": raw.hex(" "), "decoded_value": text_value(value),
                "decode_source": str(eth_path.relative_to(ROOT)),
                "definition_fingerprint": (
                    "2B4:6:0:13:little_endian:0:0.01:0" if name == "PCS_dcdcLvBusVolt"
                    else "2B4:6:32:13:little_endian:1:0.1:0"
                ),
            })
    write_csv(MACHINE / "validated_0x2B4_low_voltage_samples.csv", alt_rows)
    validation_window_rows = []
    validation_windows = [("powered", 0.0, lock_confirmed), ("shutdown", power_off, positive_open),
                          ("post_open", positive_open, silence_start_s),
                          ("terminal_silence", silence_start_s, silence_end_s)]
    for label, left, right in validation_windows:
        for key in ("BMS_packVoltage", "PCS_dcdcHvBusVolt"):
            stats = window_numeric(samples_by_signal[key], left, right)
            validation_window_rows.append({"window": label, "start_s": left, "end_s": right,
                                           "signal_key": key, "decode_source": "ONYX", **stats})
        for key in ("PCS_dcdcLvBusVolt", "PCS_dcdcLvOutputCurrent"):
            stats = window_numeric(alt_samples[key], left, right)
            validation_window_rows.append({"window": label, "start_s": left, "end_s": right,
                                           "signal_key": key, "decode_source": "ETH_JSON_DLC6", **stats})
    write_csv(MACHINE / "signal_validation_window_stats.csv", validation_window_rows)

    maturity = {
        "NetworkFrameRate_derived": ("PARTIALLY_VALIDATED", "采集域通信量可信；不外推整车网络"),
        "ActiveCanIdCount_derived": ("PARTIALLY_VALIDATED", "采集域活跃ID数可信；不等同ECU数量"),
        "CanIdLastSeenTime_derived": ("PARTIALLY_VALIDATED", "报文最后出现时间可信；不等同ECU断电"),
        "VCLEFT_frontOccupancyStatus": ("INSUFFICIENT_EVIDENCE", "0x30A无帧"),
        "VCLEFT_frontLatchStatus": ("STRONGLY_SUPPORTED", "CLOSED-OPENED-CLOSED与采集脚本动作顺序一致"),
        "VCSEC_lockRequestType": ("STRONGLY_SUPPORTED", "ACTIVE_NFC_LOCK与两项锁状态在同一时刻转为LOCKED"),
        "VCSEC_simpleLockStatus": ("STRONGLY_SUPPORTED", "关门后保持UNLOCKED，NFC锁止候选出现时转LOCKED"),
        "VCSEC_vehicleLockStatus": ("PARTIALLY_VALIDATED", "与simple状态和NFC锁止候选同向；不作为独立机械反馈"),
        "UI_lockRequest": ("INSUFFICIENT_EVIDENCE", "有帧但全程IDLE；不代表钥匙卡落锁REQUEST，也不能独立满足ER-03"),
        "DI_gear": ("INSUFFICIENT_EVIDENCE", "本片段无可解样本，P挡缺直接CAN证据"),
        "DI_systemState": ("INSUFFICIENT_EVIDENCE", "本片段无可解样本"),
        "UI_readyForDrive": ("PARTIALLY_VALIDATED", "起始为1并于落锁后转0；仅作消费者状态，不作为许可源"),
        "VCFRONT_vehiclePowerState": ("PARTIALLY_VALIDATED", "CONDITIONING到OFF先于接触器退出；仅作SYSTEM_RESULT"),
        "VCFRONT_12vStatusForDrive": ("INSUFFICIENT_EVIDENCE", "0x3A1有帧但ONYX MUX下未解出该Signal"),
        "BMS_hvState": ("SEMANTIC_VALIDATION_FAILED", "接触器由CLOSED经OPENING转OPEN期间全程均为DOWN"),
        "BMS_contactorState": ("STRONGLY_SUPPORTED", "本下电窗口观察到CLOSED-OPENING-OPEN完整转换"),
        "HVP_packContPositiveState": ("STRONGLY_SUPPORTED", "0x20A DLC6原始bit与总接触器及电压变化闭环；保留实验范围"),
        "HVP_packContNegativeState": ("STRONGLY_SUPPORTED", "0x20A DLC6原始bit与总接触器及电压变化闭环；保留实验范围"),
        "BMS_packVoltage": ("PARTIALLY_VALIDATED", "0.01 V缩放及高压下降/恢复动态可信；Pack端物理定位不成立或未确认"),
        "PCS_dcdcHvBusVolt": ("SEMANTIC_VALIDATION_FAILED", "0x2B4实际DLC6而候选DLC5；值在0.15到590.77 V非物理跳变且不闭合"),
        "PCS_dcdcHvBusDischargeStatus": ("PARTIALLY_VALIDATED", "IDLE-ACTIVE-IDLE与0x132电压快速下降时序一致；不证明终值"),
        "PCS_dcdcMainState": ("SEMANTIC_VALIDATION_FAILED", "12V支持ACTIVE-IDLE-ACTIVE-IDLE变化期间全程STANDBY"),
        "PCS_dcdc12VSupportStatus": ("STRONGLY_SUPPORTED", "最终ACTIVE-IDLE紧随vehiclePowerState OFF，且低压输出电流候选归零"),
        "PCS_dcdcLvBusVolt": ("PARTIALLY_VALIDATED", "采用ETH/JSON DLC6定义后约7.77到14.06 V；动态可用但无外部12V标定"),
        "PCS_dcdcLvOutputCurrent": ("PARTIALLY_VALIDATED", "采用ETH/JSON DLC6 signed定义后约0到385.3 A且最终退出归零；无外部标定"),
        "BMS_nmGoingToSleep": ("INSUFFICIENT_EVIDENCE", "全程0，未观察转换"),
        "BMS_hvsBusAsleep": ("PARTIALLY_VALIDATED", "0到1发生在静默前；仅BMS消费者视角"),
        "BMS_nmKeepAwakeReason": ("TIMING_ONLY_VALID", "CTRS_CLOSED到NONE_SNA与接触器退出同步；原因枚举无独立确认"),
        "GTW_nmGoingToSleep": ("INSUFFICIENT_EVIDENCE", "全程0，未观察转换"),
        "GTW_VEHBusAsleep": ("PARTIALLY_VALIDATED", "0到1发生于末段静默前；仅GTW消费者视角，不能代表整车网络"),
        "GTW_chBusAsleep": ("PARTIALLY_VALIDATED", "0到1发生于末段静默前；CH域边界及整车外推未确认"),
        "GTW_nmKeepAwakeReason": ("INSUFFICIENT_EVIDENCE", "全程NONE_SNA，不能解释退出或再唤醒"),
    }
    validation_rows = []
    for approved in active:
        result, evidence = maturity[approved.signal_key]
        validation_rows.append({
            "signal_key": approved.signal_key, "can_id": approved.can_id,
            "effective_priority": approved.effective_priority,
            "effective_role": approved.effective_role,
            "pre_analysis_maturity": approved.semantic_status,
            "post_validation_maturity": result, "evidence": evidence,
            "scope": "TM3-008_THIS_EXPERIMENT_ONLY",
        })
    write_csv(MACHINE / "signal_validation_assessment.csv", validation_rows)

    assessments = [
        {"requirement_id": "ER-01", "status": "INSUFFICIENT_EVIDENCE",
         "evidence_summary": "区间起始UI_readyForDrive=1、门闩CLOSED、车辆UNLOCKED、BMS接触器CLOSED、DCDC支持ACTIVE且通信活跃。",
         "limitation": "Ready、高压和DCDC起始状态有CAN支持，但DI_gear无样本，P挡及外部READY事实仍缺口。"},
        {"requirement_id": "ER-02", "status": "INSUFFICIENT_EVIDENCE",
         "evidence_summary": f"驾驶门在{door_open:.4f}秒CLOSED→OPENED，并在{door_closed:.4f}秒OPENED→CLOSED。",
         "limitation": "开关门反馈已观察；VCLEFT_frontOccupancyStatus无帧，离座动作及Observed Event Time不能由门闩替代。"},
        {"requirement_id": "ER-03", "status": "SUPPORTED",
         "evidence_summary": f"关门后车辆维持UNLOCKED；{lock_request:.4f}秒VCSEC_lockRequestType出现ACTIVE_NFC_LOCK，simple/vehicle锁状态同步转为LOCKED。",
         "limitation": "支持CAN域内关门未锁与NFC落锁/反馈的区分；UI_lockRequest全程IDLE且不承担钥匙卡REQUEST，外部灯光/声音反馈仍属ER-10 GAP。"},
        {"requirement_id": "ER-04", "status": "INSUFFICIENT_EVIDENCE",
         "evidence_summary": f"UI_readyForDrive在{ready_exit:.4f}秒由1转0；VCFRONT_vehiclePowerState在{power_off:.4f}秒由CONDITIONING转OFF，随后接触器与DCDC退出。",
         "limitation": "观察到消费者状态和系统结果，但没有直接下电REQUEST/PERMISSION/COMMAND；BMS_hvState语义验证失败。"},
        {"requirement_id": "ER-05", "status": "INSUFFICIENT_EVIDENCE",
         "evidence_summary": f"BMS总接触器{bms_opening:.4f}秒OPENING、{bms_open:.4f}秒OPEN；0x20A正负接触器{positive_opening:.4f}秒OPENING、{positive_open:.4f}秒OPEN；放电候选{discharge_active:.4f}到{discharge_idle_after:.4f}秒ACTIVE；0x132电压字段快速下降。",
         "limitation": "PCS_dcdcHvBusVolt继续SEMANTIC_VALIDATION_FAILED；0x132字段的Pack端物理定位与下降行为冲突，因此接触器执行已支持，但下游母线定量物理响应仍为GAP。"},
        {"requirement_id": "ER-06", "status": "SUPPORTED",
         "evidence_summary": f"PCS_dcdc12VSupportStatus曾在175.4707到185.2708秒短暂IDLE后恢复ACTIVE，并在{dcdc_idle:.4f}秒最终转IDLE；DLC6低压输出电流候选随后归零，母线电压候选约7.77到14.06 V。",
         "limitation": "仅支持PCS侧DCDC/低压响应；PCS_dcdcMainState语义失败，且没有外部12 V测量。"},
        {"requirement_id": "ER-07", "status": "INSUFFICIENT_EVIDENCE",
         "evidence_summary": "可重建门开→门关→NFC落锁/锁止反馈→Ready消费者状态退出→GTW分域asleep候选→SYSTEM_RESULT OFF→接触器/DCDC退出→BMS总线休眠候选→末段静默的实际顺序。",
         "limitation": "占座以及直接需求/许可/命令层仍缺失，不能形成完整请求—许可—执行链，也不从时间先后推断控制因果。"},
        {"requirement_id": "ER-08", "status": "SUPPORTED",
         "evidence_summary": f"GTW chBus/VEHBus asleep候选分别于146.3140/170.5162秒转1；各ID分层停止发布，BMS_hvsBusAsleep于{bms_bus_asleep:.4f}秒转1，{silence_start_s:.4f}秒最后一帧后无通信。",
         "limitation": "只证明当前采集域分层退出；逐ID最后出现不等于ECU断电，GTW asleep字段不代表整车全部网络。"},
        {"requirement_id": "ER-09", "status": "NOT_OBSERVED",
         "evidence_summary": f"观察到从最后一帧{silence_start_s:.4f}秒到计划截止{silence_end_s:.4f}秒、持续{longest_gap_s:.4f}秒的采集域末段静默，期间未见恢复通信。",
         "limitation": "连续静默仅约6.07分钟，未达到不少于10分钟要求；结束边界来自拆分合同，且无外部无干预记录。"},
        {"requirement_id": "ER-10", "status": "INSUFFICIENT_EVIDENCE",
         "evidence_summary": "未发现现场记录或App实际触发时间CSV。",
         "limitation": "CAN Candidate不得替代Observed Event、外部落锁反馈、钥匙/App无干预记录或停止采集方式。"},
    ]
    write_csv(MACHINE / "evidence_assessment.csv", assessments)

    analysis_summary = {
        "experiment_id": "TM3-008", "analysis_status": "EVIDENCE_ASSESSED",
        "completion_status": "PARTIAL", "approved_scope": plan.scope,
        "source_interval_s": [SOURCE_START_S, SOURCE_END_S],
        "observed_down_sequence_s": {
            "vehicle_power_state_off": power_off, "bms_contactor_opening": bms_opening,
            "dcdc_support_idle": dcdc_idle, "hvp_contactors_opening": positive_opening,
            "hv_bus_discharge_candidate_active": discharge_active,
            "bms_contactor_open": bms_open, "voltage_candidate_below_60v": voltage_below_60,
            "voltage_candidate_below_15v": voltage_below_15,
            "hvp_contactors_open": positive_open, "bms_bus_asleep_candidate": bms_bus_asleep,
            "capture_domain_silence_start": silence_start_s,
            "capture_domain_silence_observation_end": silence_end_s,
        },
        "capture_domain_silence_duration_s": longest_gap_s,
        "supported_requirements": ["ER-03", "ER-06", "ER-08"],
        "insufficient_requirements": ["ER-01", "ER-02", "ER-04", "ER-05", "ER-07", "ER-10"],
        "not_observed_requirements": ["ER-09"],
        "key_conflicts": [
            "BMS_hvState remains DOWN across CLOSED/OPENING/OPEN contactor transitions.",
            "PCS_dcdcMainState remains STANDBY across DCDC support exit transitions.",
            "PCS_dcdcHvBusVolt uses a DLC5 definition against DLC6 frames and produces nonphysical discontinuities.",
            "BMS_packVoltage scaling follows high-voltage collapse/restore, but its Pack-side physical location is contradicted or unconfirmed.",
        ],
        "external_evidence_gap_er10": True,
        "formal_report_bundle_generated": False,
    }
    write_json(MACHINE / "analysis_summary.json", analysis_summary)

    integrity["analysis_status"] = "EVIDENCE_ASSESSED"
    integrity["evidence_assessment_count"] = len(assessments)
    integrity["formal_report_bundle_generated"] = False
    write_json(MACHINE / "asc_integrity.json", integrity)

    print(json.dumps({
        "parsed_frames": len(times), "unique_ids": integrity["unique_can_id_count"],
        "relative_start_s": start_s, "relative_end_s": end_s,
        "active_candidates": len(active), "excluded_candidates": len(excluded),
        "decoded_rows": len(native_rows), "network_seconds": len(network_rows),
        "longest_gap_s": longest_gap_s,
        "evidence_assessments": {row["requirement_id"]: row["status"] for row in assessments},
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
