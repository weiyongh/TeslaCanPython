"""Validate TM3-015 candidate signals against every local DBC.

This is a supplemental dictionary/semantic audit.  It does not mutate the
experiment-approved Evidence Plan or promote a vehicle-level signal meaning.
"""
from __future__ import annotations

import csv
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import cantools

ROOT = Path(__file__).resolve().parents[1]
ASC = ROOT / "input/can_20260831102614_TM3-015_直流快充采集.asc"
ONYX = ROOT / "input/tesla_model3_ONYX.dbc"
OUT = ROOT / "output/TM3-015/dbc_all_sources_audit/multi_dbc_validation"
ASC_RE = re.compile(
    r"^\s*(?P<t>\d+(?:\.\d+)?)\s+\d+\s+(?P<id>[0-9A-Fa-f]+)\s+Rx\s+d\s+"
    r"(?P<dlc>\d+)\s*(?P<data>(?:[0-9A-Fa-f]{2}(?:\s+|$))*)"
)
RELEVANT = re.compile(
    r"charge|charging|chg|evse|gbdc|fastcharge|precharge|contactor|hvil|isolation|"
    r"pack.*temp|thermal|coolant.*bat|pumpbattery|chiller|compressor|hpmode|"
    r"activeheatingbattery|pintemperature|chargeport", re.I,
)
FOCUS = re.compile(
    r"^(HVP_fc|HVP_hvil|HVP_packCont|BMS_fcContactorRequest|BMS_packContactorRequest|"
    r"FC_|VCSEC_chargePort|CP_chargeCableState|CP_hvChargeStatus_log|"
    r"CP_chargeDoorOpenUI|CP_digitalCommsAttempts|CP_gbdcChargeAttempts|"
    r"CP_vehiclePrechargeRequired|CP_evseOutputDcCurrentStale|CP_pilot|CP_proximity|"
    r"BMS_isolationResistance|BMS_packTMax|BMS_packTMin|BMS_maxChargeCurrent|"
    r"VCFRONT_bmsHvChargeEnable|UI_chargeEnableRequest|TotalChargeKWh3D2|"
    r"BMS_kwhDcChargeTotalModule)"
)
PHASES = [
    ("PRE", 0.0, 110.0), ("UI_CHARGE_BEFORE_DC", 115.4, 139.9),
    ("DC_RAMP", 140.0, 160.0), ("STEADY", 173.7, 233.2),
    ("STOP_EDGE", 244.5, 247.0), ("POST", 247.0, 299.8),
]
EVENTS = [("ui_charge", 115.3922), ("dc_voltage", 140.0275),
          ("dc_current", 145.0277), ("stop", 245.7336),
          ("current_zero", 246.2332), ("ui_exit", 246.3925)]


def scalar(value):
    if hasattr(value, "value"):
        return int(value.value)
    return value if isinstance(value, (int, float, str, bool)) else str(value)


def summarize(values):
    if not values:
        return ""
    nums = [float(v) for _, v in values if isinstance(v, (int, float)) and math.isfinite(float(v))]
    if len(nums) == len(values):
        nums.sort()
        mid = len(nums) // 2
        med = nums[mid] if len(nums) % 2 else (nums[mid - 1] + nums[mid]) / 2
        return f"{med:.6g}"
    counts = Counter(str(v) for _, v in values)
    return counts.most_common(1)[0][0]


def transitions(values):
    result = []
    previous = object()
    for t, value in values:
        key = str(value)
        if key != previous:
            result.append((t, key)); previous = key
    return result


def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    frames = defaultdict(list); asc_dlcs = defaultdict(Counter)
    with ASC.open(encoding="utf-8", errors="replace") as source:
        for line in source:
            match = ASC_RE.match(line)
            if not match:
                continue
            fid = int(match.group("id"), 16); raw = bytes.fromhex(match.group("data"))
            if len(raw) != int(match.group("dlc")):
                continue
            frames[fid].append((float(match.group("t")), raw)); asc_dlcs[fid][len(raw)] += 1

    paths = sorted((ROOT / "dbc").glob("*.dbc")) + [ONYX]
    databases = [(p, cantools.database.load_file(p, database_format="dbc", strict=False)) for p in paths]
    onyx_db = next(db for path, db in databases if path == ONYX)
    onyx_names = {s.name for m in onyx_db.messages for s in m.signals}
    rows = []
    traces = []
    for path, db in databases:
        for message in db.messages:
            if message.frame_id not in frames:
                continue
            for signal in message.signals:
                if not (RELEVANT.search(signal.name) or FOCUS.search(signal.name)):
                    continue
                values = []
                errors = 0
                for t, raw in frames[message.frame_id]:
                    payload = raw[:message.length]
                    if len(payload) < message.length:
                        payload += bytes(message.length - len(payload))
                    try:
                        decoded = message.decode(payload, decode_choices=False, allow_truncated=False)
                    except (ValueError, cantools.database.errors.DecodeError):
                        errors += 1; continue
                    if signal.name in decoded:
                        values.append((t, scalar(decoded[signal.name])))
                unique = {str(v) for _, v in values}; ts = transitions(values)
                phase_values = {}
                for name, start, end in PHASES:
                    phase_values[name] = summarize([(t, v) for t, v in values if start <= t < end])
                nearest = []
                for event, event_t in EVENTS:
                    around = [(abs(t-event_t), t, v) for t, v in ts if abs(t-event_t) <= 2.0]
                    if around:
                        _, t, value = min(around)
                        nearest.append(f"{event}:{t:.3f}={value}")
                if not frames[message.frame_id]:
                    readability = "NO_FRAME"
                elif not values:
                    readability = "UNREADABLE_OR_MUX_NOT_OBSERVED"
                elif signal.multiplexer_ids is not None and len(values) < len(frames[message.frame_id]):
                    readability = "READABLE_ON_MUX_PAGE"
                elif len(values) < len(frames[message.frame_id]):
                    readability = "PARTIAL_DECODE"
                else:
                    readability = "READABLE"
                row = dict(
                    dbc_source=str(path.relative_to(ROOT)), can_id=f"0x{message.frame_id:X}",
                    message=message.name, dbc_dlc=message.length,
                    asc_dlc="/".join(map(str, sorted(asc_dlcs[message.frame_id]))),
                    asc_frames=len(frames[message.frame_id]), signal=signal.name,
                    onyx_has_same_name="YES" if signal.name in onyx_names else "NO",
                    start_bit=signal.start, bit_length=signal.length,
                    byte_order=signal.byte_order, signed=signal.is_signed,
                    scale=signal.scale, offset=signal.offset, unit=signal.unit or "",
                    multiplexer_ids="/".join(map(str, signal.multiplexer_ids or [])),
                    decoded_count=len(values), decode_errors=errors,
                    distinct_count=len(unique), transition_count=max(0, len(ts)-1),
                    first_value=str(values[0][1]) if values else "",
                    last_value=str(values[-1][1]) if values else "",
                    min_value=min((float(v) for _, v in values if isinstance(v, (int,float))), default=""),
                    max_value=max((float(v) for _, v in values if isinstance(v, (int,float))), default=""),
                    readability=readability, focus_candidate="YES" if FOCUS.search(signal.name) else "NO",
                    event_near_transition=";".join(nearest),
                    **{f"phase_{k}": v for k, v in phase_values.items()},
                )
                rows.append(row)
                if FOCUS.search(signal.name):
                    for t, value in ts:
                        traces.append(dict(dbc_source=row["dbc_source"], can_id=row["can_id"],
                                           message=message.name, signal=signal.name,
                                           time_s=f"{t:.6f}", value=value))

    write_csv(OUT / "all_relevant_decode_summary.csv", rows)
    write_csv(OUT / "focus_candidate_decode_summary.csv", [r for r in rows if r["focus_candidate"] == "YES"])
    write_csv(OUT / "onyx_missing_decode_summary.csv", [r for r in rows if r["onyx_has_same_name"] == "NO"])
    write_csv(OUT / "focus_candidate_transitions.csv", traces)
    focus = [r for r in rows if r["focus_candidate"] == "YES"]
    missing = [r for r in rows if r["onyx_has_same_name"] == "NO"]
    dynamic = [r for r in focus if r["distinct_count"] > 1]
    eventful = [r for r in dynamic if r["event_near_transition"]]
    lines = [
        "# TM3-015 多DBC候选解析验证", "",
        "本输出仅扩大候选命中与语义验证范围，不修改既有Approved Evidence Plan。", "",
        f"- 扫描DBC：{len(databases)}份。",
        f"- 相关定义解析结果：{len(rows)}条。",
        f"- ONYX无同名Signal的定义：{len(missing)}条。",
        f"- 聚焦高价值候选：{len(focus)}条；其中动态{len(dynamic)}条，关键事件±2秒存在转换{len(eventful)}条。", "",
        "## 有事件近邻转换的聚焦候选", "",
        "| Signal | CAN ID | DBC | ONYX同名 | 事件近邻转换 |", "| --- | --- | --- | --- | --- |",
        *[f"| `{r['signal']}` | {r['can_id']} | `{r['dbc_source']}` | {r['onyx_has_same_name']} | {r['event_near_transition']} |" for r in eventful], "",
        "事件近邻只用于筛选，不单独证明控制语义；需要结合状态方向、相邻节点及定义冲突人工评估。",
    ]
    (OUT / "多DBC候选解析验证.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"rows={len(rows)} focus={len(focus)} dynamic={len(dynamic)} eventful={len(eventful)} onyx_missing={len(missing)}")


if __name__ == "__main__":
    main()
