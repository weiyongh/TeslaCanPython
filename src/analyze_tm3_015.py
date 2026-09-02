"""TM3-015 DC fast-charge analysis.

Stage order is enforced in code: approved plan -> ASC/DBC coverage and semantic
readability -> event timing -> Evidence Assessment. This first implementation
produces the coverage gate and decoded native samples; later stages consume only
signals that pass this gate.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import cantools

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from evidence_plan import read_approved_csv

ASC = ROOT / "input/can_20260831102614_TM3-015_直流快充采集.asc"
DBC = ROOT / "input/tesla_model3_ONYX.dbc"
ALT_DBC = ROOT / "dbc/Model3CAN.dbc"
OUT = ROOT / "output/TM3-015"
ASC_RE = re.compile(
    r"^\s*(?P<t>\d+(?:\.\d+)?)\s+\d+\s+(?P<id>[0-9A-Fa-f]+)\s+Rx\s+d\s+"
    r"(?P<dlc>\d+)\s*(?P<data>(?:[0-9A-Fa-f]{2}(?:\s+|$))*)"
)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(1024 * 1024):
            h.update(block)
    return h.hexdigest()


def scalar(value):
    if hasattr(value, "value"):
        return int(value.value)
    if isinstance(value, (int, float, str, bool)):
        return value
    return str(value)


def required_dlc(signal) -> int:
    if signal.byte_order == "little_endian":
        return math.ceil((signal.start + signal.length) / 8)
    # Conservative for the selected plan; report the DBC message length for
    # Motorola fields rather than claiming partial-DLC readability.
    return signal.message.length if hasattr(signal, "message") else 8


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    plan = read_approved_csv(OUT / "evidence_plan_approved.csv")
    db = cantools.database.load_file(DBC, database_format="dbc", strict=False)
    alt = cantools.database.load_file(ALT_DBC, database_format="dbc", strict=False)

    frames = defaultdict(list)
    dlcs = defaultdict(Counter)
    count = 0
    last = 0.0
    with ASC.open(encoding="utf-8", errors="replace") as source:
        for line in source:
            match = ASC_RE.match(line)
            if not match:
                continue
            t = float(match.group("t"))
            fid = int(match.group("id"), 16)
            data = bytes.fromhex(match.group("data"))
            declared = int(match.group("dlc"))
            if declared != len(data):
                continue
            frames[fid].append((t, data))
            dlcs[fid][declared] += 1
            count += 1
            last = t

    decoded_rows = []
    coverage = []
    for item in plan.signals:
        if item.effective_report_position == "EXCLUDE":
            continue
        fid = int(item.can_id, 16)
        if item.signal_key.endswith("_derived"):
            coverage.append(dict(
                signal_key=item.signal_key, signal=item.signal,
                chinese_semantic=item.chinese_semantic, role=item.effective_role,
                priority=item.effective_priority, can_id=item.can_id,
                message=item.message, dbc_source="DERIVED", dbc_dlc="",
                signal_required_dlc="", asc_dlc="/".join(map(str, sorted(dlcs[fid]))),
                frame_count=len(frames[fid]), decoded_count=0, distinct_count=0,
                first_time_s="", last_time_s="", min_value="", max_value="",
                readability="DERIVED_AFTER_INPUT_VALIDATION",
                semantic_validation="PENDING_INPUT_VALIDATION",
            ))
            continue
        try:
            message = db.get_message_by_frame_id(fid)
            signal = message.get_signal_by_name(item.signal)
        except KeyError:
            coverage.append(dict(
                signal_key=item.signal_key, signal=item.signal,
                chinese_semantic=item.chinese_semantic, role=item.effective_role,
                priority=item.effective_priority, can_id=item.can_id,
                message=item.message, dbc_source=str(DBC.relative_to(ROOT)),
                dbc_dlc="", signal_required_dlc="",
                asc_dlc="/".join(map(str, sorted(dlcs[fid]))),
                frame_count=len(frames[fid]), decoded_count=0, distinct_count=0,
                first_time_s="", last_time_s="", min_value="", max_value="",
                readability="DBC_SIGNAL_MISSING",
                semantic_validation="SEMANTIC_VALIDATION_FAILED",
            ))
            continue
        need = required_dlc(signal)
        values = []
        for t, raw in frames[fid]:
            if len(raw) < need:
                continue
            payload = raw[:message.length]
            if len(payload) < message.length:
                payload += bytes(message.length - len(payload))
            try:
                decoded = message.decode(payload, decode_choices=False, allow_truncated=False)
            except (ValueError, cantools.database.errors.DecodeError):
                continue
            if item.signal not in decoded:
                continue
            value = scalar(decoded[item.signal])
            values.append((t, value))
            decoded_rows.append(dict(
                time_s=f"{t:.6f}", can_id=item.can_id, message=message.name,
                signal_key=item.signal_key, signal=item.signal,
                chinese_semantic=item.chinese_semantic, value=value,
                unit=item.unit, raw_dlc=len(raw), dbc_source=str(DBC.relative_to(ROOT)),
            ))
        numeric = [float(v) for _, v in values if isinstance(v, (int, float))]
        distinct = {str(v) for _, v in values}
        frame_count = len(frames[fid])
        if not frame_count:
            readability = "NO_FRAME"
        elif not values:
            readability = "MUX_NOT_OBSERVED_OR_UNREADABLE"
        elif len(values) < frame_count and signal.multiplexer_ids is not None:
            readability = "READABLE_ON_MUX_PAGE"
        elif len(values) < frame_count:
            readability = "PARTIAL_DLC_OR_DECODE"
        else:
            readability = "READABLE"
        coverage.append(dict(
            signal_key=item.signal_key, signal=item.signal,
            chinese_semantic=item.chinese_semantic, role=item.effective_role,
            priority=item.effective_priority, can_id=item.can_id,
            message=message.name, dbc_source=str(DBC.relative_to(ROOT)),
            dbc_dlc=message.length, signal_required_dlc=need,
            asc_dlc="/".join(map(str, sorted(dlcs[fid]))), frame_count=frame_count,
            decoded_count=len(values), distinct_count=len(distinct),
            first_time_s=f"{values[0][0]:.6f}" if values else "",
            last_time_s=f"{values[-1][0]:.6f}" if values else "",
            min_value=min(numeric) if numeric else "",
            max_value=max(numeric) if numeric else "",
            readability=readability,
            semantic_validation="PENDING_EVENT_VALIDATION" if values else "SEMANTIC_VALIDATION_FAILED",
        ))

    excluded_audit = []
    for item in plan.signals:
        if item.effective_report_position != "EXCLUDE":
            continue
        fid = int(item.can_id, 16)
        def name(database):
            try:
                return database.get_message_by_frame_id(fid).name
            except KeyError:
                return "MISSING"
        excluded_audit.append(dict(
            signal=item.signal, chinese_semantic=item.chinese_semantic,
            can_id=item.can_id, asc_frames=len(frames[fid]),
            asc_dlc="/".join(map(str, sorted(dlcs[fid]))),
            onyx_message=name(db), alternate_message=name(alt),
            disposition="EXCLUDED_FROM_CONCLUSION_DBC_AUDIT_ONLY",
        ))

    def write_csv(path, rows):
        if not rows:
            return
        with path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader(); writer.writerows(rows)

    write_csv(OUT / "dbc_coverage_gate.csv", coverage)
    write_csv(OUT / "decoded_native_samples.csv", decoded_rows)
    write_csv(OUT / "excluded_dbc_conflict_audit.csv", excluded_audit)
    verification = dict(
        experiment_id="TM3-015", source=str(ASC.relative_to(ROOT)),
        source_sha256=sha(ASC), dbc=str(DBC.relative_to(ROOT)), dbc_sha256=sha(DBC),
        approved_plan_sha256=sha(OUT / "evidence_plan_approved.csv"),
        frame_count=count, duration_s=last, unique_can_ids=len(frames),
        approved_rows=len(plan.signals), active_rows=sum(x.effective_report_position != "EXCLUDE" for x in plan.signals),
        excluded_rows=sum(x.effective_report_position == "EXCLUDE" for x in plan.signals),
        decoded_sample_rows=len(decoded_rows),
        readability_counts=dict(Counter(x["readability"] for x in coverage)),
    )
    (OUT / "coverage_verification.json").write_text(
        json.dumps(verification, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(verification, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
