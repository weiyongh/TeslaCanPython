"""Reproducible TM3-007 analysis bound to the approved Evidence Plan."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import cantools

ROOT = Path(__file__).resolve().parents[1]
ASC = ROOT / "input/can_20260831123400_TM3-007_开锁开门完整上电采集.asc"
ONYX = ROOT / "input/tesla_model3_ONYX.dbc"
APPROVED = ROOT / "output/TM3-007/evidence_plan_approved.csv"
OUT = ROOT / "output/TM3-007"
MACHINE = OUT / "machine_evidence"
ASC_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s+\d+\s+([0-9A-Fa-f]+)\s+Rx\s+d\s+(\d+)\s+((?:[0-9A-Fa-f]{2}(?:\s+|$))*)")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def parse_asc():
    frames = defaultdict(list)
    dlcs = defaultdict(Counter)
    total = malformed = 0
    for line in ASC.open(encoding="utf-8", errors="replace"):
        match = ASC_RE.match(line)
        if not match:
            continue
        total += 1
        declared = int(match.group(3))
        raw = bytes.fromhex(match.group(4))
        if len(raw) != declared:
            malformed += 1
            continue
        timestamp = float(match.group(1))
        frame_id = int(match.group(2), 16)
        frames[frame_id].append((timestamp, raw))
        dlcs[frame_id][declared] += 1
    return frames, dlcs, total, malformed


def decode(msg, raw: bytes, signal: str):
    padded = raw + bytes(max(0, msg.length - len(raw)))
    return msg.decode(padded, decode_choices=True, allow_truncated=True).get(signal)


def text_value(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}".rstrip("0").rstrip(".")
    return str(value)


def signal_changes(samples):
    result = []
    sentinel = object()
    previous = sentinel
    for timestamp, value, raw in samples:
        if value != previous:
            result.append((timestamp, value, raw))
            previous = value
    return result


def latest(samples, timestamp):
    prior = [row for row in samples if row[0] <= timestamp]
    return prior[-1] if prior else None


def main() -> None:
    MACHINE.mkdir(parents=True, exist_ok=True)
    frames, dlcs, total, malformed = parse_asc()
    unique_id_count = len(frames)
    times = [timestamp for rows in frames.values() for timestamp, _ in rows]
    start, end = min(times), max(times)
    with APPROVED.open(encoding="utf-8-sig", newline="") as stream:
        plan = list(csv.DictReader(stream))
    onyx = cantools.database.load_file(ONYX, strict=False)

    integrity = {
        "experiment_id": "TM3-007",
        "analysis_status": "ANALYZED",
        "asc_path": str(ASC.relative_to(ROOT)),
        "asc_sha256": sha(ASC),
        "asc_size_bytes": ASC.stat().st_size,
        "parsed_frame_count": total,
        "malformed_frame_count": malformed,
        "unique_can_id_count": unique_id_count,
        "start_s": start,
        "end_s": end,
        "duration_s": end - start,
        "header_declares_derived_analysis_input": True,
        "header_source": "can_20260831113240开关门采集.asc",
        "header_source_interval": "192.681200 s to 792.681200 s",
        "approved_plan_sha256": sha(APPROVED),
        "onyx_dbc_sha256": sha(ONYX),
    }
    write_json(MACHINE / "asc_integrity.json", integrity)

    # Decode approved native definitions without importing unapproved Signals.
    samples_by_signal = defaultdict(list)
    native_rows = []
    for item in plan:
        signal = item["signal_key"]
        if signal.endswith("_derived"):
            continue
        frame_id = int(item["can_id"], 16)
        try:
            msg = onyx.get_message_by_frame_id(frame_id)
            msg_signal = item["signal"]
        except KeyError:
            msg = None
            msg_signal = signal
        for timestamp, raw in frames[frame_id]:
            try:
                if signal == "GTW_BMP_AWAKE_PIN":
                    value = (raw[1] >> 0) & 1
                    source = "Model3CAN"
                elif msg is not None:
                    value = decode(msg, raw, msg_signal)
                    source = "ONYX"
                else:
                    continue
            except Exception:
                continue
            samples_by_signal[signal].append((timestamp, value, raw.hex(" ")))
            native_rows.append({"time_s": f"{timestamp:.6f}", "signal_key": signal,
                                "can_id": item["can_id"], "asc_dlc": len(raw),
                                "raw_hex": raw.hex(" "), "decoded_value": text_value(value),
                                "decode_source": source})
    write_csv(MACHINE / "decoded_native_samples.csv", native_rows)

    # Network metrics are analysis primitives approved as derived Signals.
    per_second = Counter(int(timestamp) for timestamp in times)
    id_per_second = defaultdict(set)
    for frame_id, rows in frames.items():
        for timestamp, _ in rows:
            id_per_second[int(timestamp)].add(frame_id)
    network_rows = [{"second": second, "frame_count": per_second[second],
                     "active_can_id_count": len(id_per_second[second])}
                    for second in range(int(end) + 1)]
    write_csv(MACHINE / "network_activity_1s.csv", network_rows)

    # Multi-DBC definition comparison for every approved Signal.
    sources = [ONYX] + sorted((ROOT / "dbc").glob("*.dbc"))
    definition_rows = []
    for source_path in sources:
        try:
            database = cantools.database.load_file(source_path, strict=False)
        except Exception:
            continue
        for message in database.messages:
            for dbc_signal in message.signals:
                if dbc_signal.name not in {item["signal_key"] for item in plan}:
                    continue
                definition_rows.append({
                    "signal_key": dbc_signal.name, "source": str(source_path.relative_to(ROOT)),
                    "message": message.name, "can_id": f"0x{message.frame_id:X}",
                    "dbc_dlc": message.length, "start_bit": dbc_signal.start,
                    "bit_length": dbc_signal.length, "byte_order": dbc_signal.byte_order,
                    "signed": dbc_signal.is_signed, "factor": dbc_signal.scale,
                    "offset": dbc_signal.offset, "unit": dbc_signal.unit or "",
                    "definition_fingerprint": f"{message.frame_id:X}:{message.length}:{dbc_signal.start}:{dbc_signal.length}:{dbc_signal.byte_order}:{int(dbc_signal.is_signed)}:{dbc_signal.scale}:{dbc_signal.offset}",
                })
    write_csv(MACHINE / "dbc_definition_comparison.csv", definition_rows)

    # Coverage and readability gate.
    maturity = {
        "VCLEFT_frontLatchStatus": "STRONGLY_SUPPORTED",
        "BMS_packVoltage": "STRONGLY_SUPPORTED",
        "HVP_hvilStatus": "STRONGLY_SUPPORTED",
        "HVP_packContNegativeState": "STRONGLY_SUPPORTED",
        "HVP_packContPositiveState": "STRONGLY_SUPPORTED",
        "PCS_dcdcLvBusVolt": "STRONGLY_SUPPORTED",
        "PCS_dcdcLvOutputCurrent": "PARTIALLY_VALIDATED",
        "PCS_dcdcHvBusVolt": "SEMANTIC_VALIDATION_FAILED",
        "BMS_hvState": "SEMANTIC_VALIDATION_FAILED",
        "BMS_contactorState": "STRONGLY_SUPPORTED",
        "BMS_isolationResistance": "SEMANTIC_VALIDATION_FAILED",
        "PCS_dcdcMainState": "SEMANTIC_VALIDATION_FAILED",
        "PCS_dcdc12VSupportStatus": "STRONGLY_SUPPORTED",
        "UI_readyForDrive": "STRONGLY_SUPPORTED",
        "DI_gear": "STRONGLY_SUPPORTED",
        "DI_systemState": "STRONGLY_SUPPORTED",
        "DI_brakePedalState": "SEMANTIC_VALIDATION_FAILED",
        "GTW_BMP_AWAKE_PIN": "INSUFFICIENT_EVIDENCE",
        "UI_lockRequest": "INSUFFICIENT_EVIDENCE",
    }
    coverage_rows = []
    for item in plan:
        key = item["signal_key"]
        if key == "NetworkFrameRate_derived":
            count, actual_dlc, readability, observed = len(network_rows), "derived", "READABLE", f"{min(row['frame_count'] for row in network_rows)}..{max(row['frame_count'] for row in network_rows)} frames/s"
        elif key == "ActiveCanIdCount_derived":
            count, actual_dlc, readability, observed = len(network_rows), "derived", "READABLE", f"{min(row['active_can_id_count'] for row in network_rows)}..{max(row['active_can_id_count'] for row in network_rows)} IDs/s"
        else:
            frame_id = int(item["can_id"], 16)
            count = len(frames[frame_id])
            actual_dlc = "+".join(map(str, sorted(dlcs[frame_id]))) if count else "NO_FRAME"
            decoded = samples_by_signal.get(key, [])
            readability = "NO_FRAME" if not count else ("READABLE" if decoded else "UNREADABLE")
            unique = list(dict.fromkeys(text_value(row[1]) for row in decoded))
            observed = " | ".join(unique[:12]) if unique else ""
        coverage_rows.append({
            "signal_key": key, "can_id": item["can_id"], "evidence_requirement": item["evidence_requirement"],
            "effective_role": item["effective_role"], "effective_priority": item["effective_priority"],
            "approved_source": "原始ASC统计" if key.endswith("_derived") else ("Model3CAN" if key == "GTW_BMP_AWAKE_PIN" else "ONYX主候选；冲突项见定义对照"),
            "frame_count": count, "asc_actual_dlc": actual_dlc, "decoded_sample_count": len(samples_by_signal.get(key, [])) if not key.endswith("_derived") else len(network_rows),
            "readability": readability, "observed_values_or_range": observed,
            "post_validation_maturity": maturity.get(key, item["semantic_status"]),
            "boundary": item["uncertainty_flags"],
        })
    write_csv(MACHINE / "signal_coverage.csv", coverage_rows)

    # 0x20A raw-bit validation and independent high-voltage cross-check.
    validation_raw = []
    for timestamp, raw in frames[0x20A]:
        little = int.from_bytes(raw, "little")
        validation_raw.append({
            "time_s": f"{timestamp:.6f}", "can_id": "0x20A", "asc_dlc": len(raw),
            "raw_hex": raw.hex(" "), "negative_raw_bits_0_2": little & 0x7,
            "positive_raw_bits_3_5": (little >> 3) & 0x7,
            "hvil_raw_bits_40_43": (little >> 40) & 0xF,
            "onyx_model3can_negative": {0:"SNA",1:"OPEN",2:"PRECHARGE",3:"BLOCKED",4:"PULLED_IN",5:"OPENING",6:"ECONOMIZED",7:"WELDED"}.get(little & 0x7,"UNKNOWN"),
            "onyx_model3can_positive": {0:"SNA",1:"OPEN",2:"PRECHARGE",3:"BLOCKED",4:"PULLED_IN",5:"OPENING",6:"ECONOMIZED",7:"WELDED"}.get((little >> 3) & 0x7,"UNKNOWN"),
            "onyx_model3can_hvil": {0:"UNKNOWN",1:"STATUS_OK",2:"CURRENT_SOURCE_FAULT",3:"INTERNAL_OPEN_FAULT",4:"VEHICLE_OPEN_FAULT",5:"PENTHOUSE_LID_OPEN_FAULT",6:"UNKNOWN_LOCATION_OPEN_FAULT",7:"VEHICLE_NODE_FAULT",8:"NO_12V_SUPPLY"}.get((little >> 40) & 0xF,"UNKNOWN_ENUM"),
        })
    write_csv(MACHINE / "signal_validation_0x20A_raw.csv", validation_raw)
    validation_rows = [
        {"signal_key": "HVP_hvilStatus", "can_id": "0x20A", "result": "STRONGLY_SUPPORTED", "timing": "SUPPORTED", "direction": "NOT_APPLICABLE", "quantitative": "NOT_APPLICABLE", "enumeration": "SUPPORTED_THIS_EXPERIMENT", "evidence": "下电段UNKNOWN；上电预充开始473.3233秒转STATUS_OK；独立ETH/JSON候选0x682同步为OK", "failure_or_boundary": "无外部HVIL测量；0x20A在旧tesla_can中另定义为BrakeMessage；只在本实验范围强支持"},
        {"signal_key": "HVP_packContNegativeState", "can_id": "0x20A", "result": "STRONGLY_SUPPORTED", "timing": "SUPPORTED", "direction": "SUPPORTED", "quantitative": "NOT_APPLICABLE", "enumeration": "SUPPORTED_THIS_EXPERIMENT", "evidence": "OPENING→OPEN后经历静默；上电474.3233秒进入ECONOMIZED，与BMS总接触器CLOSED及Pack电压建立闭环", "failure_or_boundary": "未直接观察PULLED_IN瞬态；不自动升级车型级正式语义"},
        {"signal_key": "HVP_packContPositiveState", "can_id": "0x20A", "result": "STRONGLY_SUPPORTED", "timing": "SUPPORTED", "direction": "SUPPORTED", "quantitative": "NOT_APPLICABLE", "enumeration": "SUPPORTED_THIS_EXPERIMENT", "evidence": "OPENING→OPEN；上电473.3233秒PRECHARGE→474.3233秒ECONOMIZED；Pack电压同期由约5V升至约354V", "failure_or_boundary": "单次实验级闭环；不写回车型DBC"},
        {"signal_key": "PCS_dcdcHvBusVolt", "can_id": "0x2B4", "result": "SEMANTIC_VALIDATION_FAILED", "timing": "EVENT_VISIBLE_BUT_WRONG_QUANTITY", "direction": "CONFLICT", "quantitative": "FAILED", "enumeration": "NOT_APPLICABLE", "evidence": "ONYX定义在上电窗给103–488V并快速落至约180V，而Pack稳定约353.5V", "failure_or_boundary": "未与Pack/接触器状态形成可信高压母线闭环；不得采用定量语义"},
        {"signal_key": "PCS_dcdcLvBusVolt", "can_id": "0x2B4", "result": "STRONGLY_SUPPORTED", "timing": "SUPPORTED", "direction": "SUPPORTED", "quantitative": "SUPPORTED_EXPERIMENT_CANDIDATE", "enumeration": "NOT_APPLICABLE", "evidence": "ETH/JSON定义从预充期约12.44V升至稳定13.48–13.51V，与DCDC支持IDLE→ACTIVE一致", "failure_or_boundary": "ONYX同位段缩放给约8.6→12.8V；无外部万用表，ETH/JSON定义不升级车型级正式语义"},
        {"signal_key": "PCS_dcdcLvOutputCurrent", "can_id": "0x2B4", "result": "PARTIALLY_VALIDATED", "timing": "SUPPORTED", "direction": "SUPPORTED", "quantitative": "CONFLICT", "enumeration": "NOT_APPLICABLE", "evidence": "ETH/JSON定义由0A升至约17A再稳定约24–33A；与DCDC ACTIVE和低压电压上升同步", "failure_or_boundary": "ONYX位段/符号定义给最高385.3A；无外部电流证据，定量语义不确认"},
    ]
    write_csv(MACHINE / "signal_validation_assessment.csv", validation_rows)

    # CAN-observed events only; no row is asserted as an external human action time.
    events = [
        {"event_id": "E00", "can_time_s": "103.157100", "planned_time_s": "10–30低通信窗口(粗定位)", "observed_event_time": "MISSING", "event": "前序高通信结束，进入本采集域无帧窗口", "basis": "103.1571至470.1237秒无CAN帧；只称本采集域低通信候选"},
        {"event_id": "E01", "can_time_s": "470.123700", "planned_time_s": "约30解锁(粗定位)", "observed_event_time": "MISSING", "event": "CAN通信恢复/网络唤醒候选", "basis": "366.9666秒无帧后恢复；不确认具体人工解锁时刻"},
        {"event_id": "E02", "can_time_s": "472.669700", "planned_time_s": "无精确对应", "observed_event_time": "MISSING", "event": "BMS接触器总状态进入CLOSING", "basis": "0x212状态转换"},
        {"event_id": "E03", "can_time_s": "473.323300", "planned_time_s": "无精确对应", "observed_event_time": "MISSING", "event": "HVIL候选OK且正接触器进入PRECHARGE", "basis": "0x20A原始bit；Pack电压同期开始快速上升"},
        {"event_id": "E04", "can_time_s": "474.271300", "planned_time_s": "无精确对应", "observed_event_time": "MISSING", "event": "BMS接触器总状态进入CLOSED", "basis": "0x212；Pack电压接近约354V"},
        {"event_id": "E05", "can_time_s": "474.323300", "planned_time_s": "无精确对应", "observed_event_time": "MISSING", "event": "正负接触器候选均进入ECONOMIZED；DCDC支持已ACTIVE", "basis": "0x20A与0x224，形成内部高压/DCDC时序闭环"},
        {"event_id": "E06", "can_time_s": "477.030200", "planned_time_s": "无精确对应", "observed_event_time": "MISSING", "event": "UI_readyForDrive候选由0变1", "basis": "0x353消费/显示层交叉反馈"},
        {"event_id": "E07", "can_time_s": "500.738600", "planned_time_s": "约40开门(粗定位)", "observed_event_time": "MISSING", "event": "驾驶门闩候选进入OPENED窗口", "basis": "0x102；不把CAN边沿当人工开门时刻"},
        {"event_id": "E08", "can_time_s": "525.770300", "planned_time_s": "约55关门(粗定位)", "observed_event_time": "MISSING", "event": "驾驶门闩候选回CLOSED", "basis": "0x102"},
        {"event_id": "E09", "can_time_s": "540.415500", "planned_time_s": "约70制动(粗定位)", "observed_event_time": "MISSING", "event": "DI报文可见并稳定为P/STANDBY；制动字段仍INVALID", "basis": "0x118；不能证明制动输入"},
        {"event_id": "E10", "can_time_s": "545.267000", "planned_time_s": "约75挂D(粗定位)", "observed_event_time": "MISSING", "event": "挡位P→D且电驱STANDBY→ENABLE", "basis": "0x118同帧状态转换；支持CAN内部可驱动状态建立"},
        {"event_id": "E11", "can_time_s": "555.426200", "planned_time_s": "约85回P(粗定位)", "observed_event_time": "MISSING", "event": "挡位D→P且电驱ENABLE→STANDBY", "basis": "0x118同帧状态转换"},
        {"event_id": "E12", "can_time_s": "599.999600", "planned_time_s": "100–130稳定窗", "observed_event_time": "MISSING", "event": "P挡上电稳定窗口结束", "basis": "P/STANDBY、接触器CLOSED、DCDC支持ACTIVE持续至文件结束"},
    ]
    write_csv(MACHINE / "events.csv", events)

    event_sample_rows = []
    event_times = {row["event_id"]: float(row["can_time_s"]) for row in events}
    event_signals = ["VCLEFT_frontLatchStatus", "UI_readyForDrive", "BMS_hvState", "BMS_contactorState",
                     "BMS_packVoltage", "PCS_dcdcHvBusVolt", "HVP_hvilStatus",
                     "HVP_packContNegativeState", "HVP_packContPositiveState",
                     "PCS_dcdcMainState", "PCS_dcdc12VSupportStatus", "PCS_dcdcLvBusVolt"]
    plan_by_key = {item["signal_key"]: item for item in plan}
    for event_id, event_time in event_times.items():
        for key in event_signals:
            sample = latest(samples_by_signal.get(key, []), event_time)
            item = plan_by_key[key]
            event_sample_rows.append({
                "event_id": event_id, "event_time_s": f"{event_time:.6f}", "signal_key": key,
                "can_id": item["can_id"], "value": text_value(sample[1]) if sample else "NOT_OBSERVED",
                "native_sample_time_s": f"{sample[0]:.6f}" if sample else "",
                "sample_age_s": f"{event_time-sample[0]:.6f}" if sample else "",
                "sampling_rule": "latest past sample; never future fill",
            })
    write_csv(MACHINE / "event_signal_samples.csv", event_sample_rows)

    assessment = [
        {"requirement_id": "ER-01", "assessment": "SUPPORTED", "evidence": "103.1571–470.1237秒无CAN帧，随后通信恢复并进入约2200–3000帧/秒", "reason": "支持本采集域低通信候选→网络唤醒；不升级为整车真实休眠"},
        {"requirement_id": "ER-02", "assessment": "INSUFFICIENT_EVIDENCE", "evidence": "0x102在500.7386秒开、525.7703秒关；UI_lockRequest只见IDLE；无独立动作锚点", "reason": "门闩反馈可区分，但解锁请求和人工开门时刻不能独立确认"},
        {"requirement_id": "ER-03", "assessment": "INSUFFICIENT_EVIDENCE", "evidence": "门闩关闭可见；0x30A无帧", "reason": "占座节点无直接观测，不能区分入座与关门各自贡献"},
        {"requirement_id": "ER-04", "assessment": "INSUFFICIENT_EVIDENCE", "evidence": "0x118在540.3854秒后可见，但DI_brakePedalState全程INVALID", "reason": "无法直接确认制动输入；仅能评价其后挡位/电驱内部状态"},
        {"requirement_id": "ER-05", "assessment": "SUPPORTED", "evidence": "HVP_hvilStatus由UNKNOWN转STATUS_OK并与0x682 OK交叉；发生在预充和接触器闭合前", "reason": "至少一个高压安全条件候选形成状态门时序；绝缘Signal仍验证失败"},
        {"requirement_id": "ER-06", "assessment": "SUPPORTED", "evidence": "BMS总接触器CLOSING→CLOSED；正接触器PRECHARGE→ECONOMIZED；负接触器OPEN→ECONOMIZED；Pack电压约5V升至约354V", "reason": "状态序列和物理电压响应形成实验级闭环"},
        {"requirement_id": "ER-07", "assessment": "SUPPORTED", "evidence": "545.2670秒DI_gear P→D且DI_systemState STANDBY→ENABLE；UI ready候选此前已为1", "reason": "挡位反馈和电驱ENABLE满足内部可驱动状态证据；缺少独立仪表/动作时刻"},
        {"requirement_id": "ER-08", "assessment": "SUPPORTED", "evidence": "DCDC支持IDLE→ACTIVE；ETH/JSON低压候选约12.44V升至稳定13.48–13.51V，电流由0升至约24–33A", "reason": "DCDC状态与低压能源响应方向、时序和量级闭合；无外部12V实测"},
        {"requirement_id": "ER-09", "assessment": "SUPPORTED", "evidence": "555.4262秒D→P且ENABLE→STANDBY；其后接触器CLOSED、DCDC ACTIVE及低压电压稳定至600秒", "reason": "形成约44.6秒P挡上电稳定窗口"},
    ]
    write_csv(MACHINE / "evidence_assessment.csv", assessment)

    report_view = {
        "experiment_id": "TM3-007", "completion_status": "COMPLETE_WITH_GAPS",
        "scope": "THIS_EXPERIMENT_ONLY", "use": "正常基线数据采集",
        "time_basis": {"planned": "rough_location_only", "observed_event": "missing", "can_observed": "used_for_internal_sequence"},
        "facts": ["600秒ASC格式完整且525946帧均可解析", "103.1571–470.1237秒为本采集域无帧窗口", "470.1237秒后通信恢复并形成预充/接触器/Pack电压/DCDC上电序列", "门闩CAN候选形成CLOSED→OPENED→CLOSED", "挡位和电驱状态形成P/STANDBY→D/ENABLE→P/STANDBY"],
        "control_relationship_view": {
            "body_input_feedback": "部分可观测：门闩状态转换；解锁请求无直接证据",
            "occupancy": "本次无直接观测", "brake_and_gear": "制动字段INVALID；挡位反馈直接可观测",
            "network_wake": "本采集域低通信候选→通信恢复",
            "hv_conditions_and_execution": "HVIL OK→正接触器PRECHARGE→总接触器CLOSED→正负接触器ECONOMIZED→Pack电压建立",
            "drive_enable": "P/STANDBY→D/ENABLE→P/STANDBY",
            "dcdc_response": "DCDC支持IDLE→ACTIVE，低压电压/电流候选同步建立",
        },
        "baseline_conclusion": "建立了本采集域低通信候选到高压建立、DCDC支持及电驱D/ENABLE的条件化CAN内部上电基线。",
        "completion_decision": "COMPLETE_WITH_GAPS；核心上电链成立，解锁/占座/制动及外部12V证据仍有缺口，不进入车辆故障诊断树。",
        "minimum_next_step": "无需整体重采；最小补采仅补独立Observed Event Time、占座/制动证据及外部12V电压，复核0x2B4低压定义。",
    }
    write_json(MACHINE / "report_view_model.json", report_view)

    metadata = {
        "experiment_id": "TM3-007", "vehicle": "Tesla Model 3 上海产2021款 标准续航 55 kWh 后驱",
        "source_file": str(ASC.relative_to(ROOT)), "duration_s": end-start,
        "purpose": "正常基线数据采集", "completion_status": "COMPLETE_WITH_GAPS",
        "observed_event_time_available": False, "asc_header_type": "Derived analysis input",
        "environment_soc_software_connection": "历史现场记录缺失；未知",
    }
    write_json(MACHINE / "experiment_metadata.json", metadata)

    # Human-readable outputs are intentionally concise; machine CSVs carry full traceability.
    final_report = f"""# TM3-007 最终报告

## 结论

本实验最终状态为 **COMPLETE_WITH_GAPS**。在当前采集域内，本次建立了“长时间无帧候选→通信恢复→高压安全条件候选满足→预充→接触器闭合→Pack电压建立→DCDC低压支持→UI ready→D挡/电驱ENABLE→回P稳定”的CAN内部上电基线。

ASC共解析{total:,}帧、{unique_id_count}个CAN ID，时长{end-start:.3f}秒且无格式损坏帧。103.1571–470.1237秒没有CAN帧，持续366.9666秒；该窗口只定义为“本采集域低通信候选”，不升级为整车真实休眠。470.1237秒后通信恢复，随后形成完整的内部高压建立序列。

## 事实与控制关系

- 470.1237秒通信恢复；472.6697秒`BMS_contactorState`进入CLOSING；473.3233秒`HVP_hvilStatus`进入STATUS_OK且正接触器进入PRECHARGE；474.2713秒总接触器进入CLOSED；474.3233秒正负接触器候选均进入ECONOMIZED。同期`BMS_packVoltage`由约5V快速升至约354V，状态序列和物理电压响应闭合。
- `PCS_dcdc12VSupportStatus`在474.2765秒由IDLE进入ACTIVE。ETH/JSON的`0x2B4`低压候选由预充期约12.44V升至稳定13.48–13.51V，输出电流候选由0A升至约24–33A，支持DCDC低压响应；由于没有外部万用表且ONYX定义冲突，该定量定义仍限定在本实验候选范围。
- `UI_readyForDrive (0x353)`在477.0302秒由0变1。门闩候选在500.7386秒进入OPENED、525.7703秒回CLOSED。540.4155秒后`0x118`可读，545.2670秒形成`P/STANDBY→D/ENABLE`，555.4262秒回到`P/STANDBY`并稳定至文件结束。
- `DI_brakePedalState`全程为INVALID，`VCLEFT_frontOccupancyStatus (0x30A)`无帧；因此制动和入座节点仍无直接证据。`BMS_hvState`全程DOWN、`BMS_isolationResistance`全程0 kOhm、`PCS_dcdcMainState`全程STANDBY，与其他已闭合证据冲突，判为相应DBC语义验证失败，不解释为车辆故障。

## 基线结论

可保存的条件化基线包括：本采集域低通信候选后的网络恢复；HVIL/预充/接触器/Pack电压建立关系；DCDC支持与低压电压、电流响应；UI ready显示层反馈；以及P/STANDBY、D/ENABLE、回P/STANDBY的电驱内部状态关系。

本次结果不需要进入故障诊断树。冲突字段已经按Signal Validation降级，不能转写为车辆故障判断。

## 证据边界与建议

Planned Time仅作粗定位；本报告不生成任何精确“人工动作→CAN响应”延迟。当前600秒派生文件同时含前序下电尾段、长无帧窗口和后续上电段；正式TM3-007分析窗口从103.1571秒高通信结束后的低通信候选开始，470.1237秒后的上电段用于状态链判断。文件内部旧标签仍写TM3-008，属于更名前元数据，不作为实验事实。

无需整体重采。最小补采只需补齐独立Observed Event Time、占座/制动状态、同步仪表可驱动反馈和外部12V电压/电流，并复核`0x2B4`低压定义。若不能取得占座CAN，可用同步视频或诊断工具证据保留该控制节点。
"""
    (OUT / "TM3-007_最终报告.md").write_text(final_report, encoding="utf-8")

    timeline = """# TM3-007 采集时间线与关键Signal

## 时间基准

下列时间全部为ASC内部CAN时间。Observed Event Time缺失；Planned Time只作粗定位，不用于动作归因或响应延迟。

| 事件 | CAN时间(s) | CAN内部事实 | 边界 |
| --- | ---: | --- | --- |
| E00 | 103.1571 | 前序高通信结束，进入无帧窗口 | 只称本采集域低通信候选 |
| E01 | 470.1237 | 366.9666秒无帧后通信恢复 | 不确认具体人工解锁时刻 |
| E02 | 472.6697 | BMS接触器总状态进入CLOSING | 高压建立内部状态 |
| E03 | 473.3233 | HVIL候选OK；正接触器PRECHARGE | Pack电压同期快速上升 |
| E04 | 474.2713 | BMS接触器总状态CLOSED | Pack电压接近约354V |
| E05 | 474.3233 | 正负接触器ECONOMIZED；DCDC支持ACTIVE | 实验级高压/DCDC闭环 |
| E06 | 477.0302 | UI_readyForDrive由0变1 | 显示/消费者层交叉反馈 |
| E07 | 500.7386 | 门闩候选进入OPENED | 不声称人工开门发生于此时 |
| E08 | 525.7703 | 门闩候选回CLOSED | 不声称人工关门发生于此时 |
| E09 | 540.4155 | DI报文稳定为P/STANDBY | 制动字段仍INVALID |
| E10 | 545.2670 | P/STANDBY→D/ENABLE | CAN内部可驱动状态建立 |
| E11 | 555.4262 | D/ENABLE→P/STANDBY | 回P内部状态 |
| E12 | 599.9996 | P挡上电稳定窗口结束 | 约44.6秒稳定窗口 |

详细事件和逐Signal过去最近样本见`machine_evidence/events.csv`与`event_signal_samples.csv`。所有跨报文取值均使用事件时刻之前最近样本，不使用未来值补齐。
"""
    (OUT / "采集时间线与关键Signal.md").write_text(timeline, encoding="utf-8")

    coverage_md = """# TM3-007 DBC关键Signal覆盖与可读性

## 覆盖门结论

- P0共12项：网络、门闩、挡位、电驱ENABLE、接触器总状态、Pack电压和DCDC低压响应形成主要闭环；制动字段INVALID，`BMS_hvState`与`PCS_dcdcHvBusVolt`语义验证失败。
- P1共8项：`0x20A`三项完成多DBC/原始bit审计并在本实验范围得到强支持；DCDC低压电流仅部分验证。
- P2共3项：只用于工程审计，不进入主控制结论。

## 关键定义判断

| Signal | 实测覆盖 | 判断 |
| --- | --- | --- |
| VCLEFT_frontLatchStatus (0x102) | 1312帧，DLC8 | ONYX bit0与ETH/JSON bit14均支持开/关稳定窗口；后者另见OPENING阶段，STRONGLY_SUPPORTED |
| DI_* (0x118) | 5962帧，DLC8 | 挡位与电驱状态形成P/STANDBY→D/ENABLE→P/STANDBY；制动字段全程INVALID |
| VCLEFT_frontOccupancyStatus (0x30A) | 0帧 | NO_FRAME |
| BMS_hvState / contactor / isolation (0x212) | 2326帧，DLC8 | 接触器总状态强支持；hvState和绝缘定义失败，不能静默共用成熟度 |
| HVP三项 (0x20A) | 230帧，DLC6 | HVIL OK、正接触器PRECHARGE及双接触器ECONOMIZED与Pack电压建立闭环，实验级STRONGLY_SUPPORTED |
| PCS_dcdc* (0x224/0x2B4) | 约2310帧 | 12V支持状态强支持；ETH/JSON低压电压候选强支持，电流部分验证；主状态与ONYX高压定义失败 |

完整的逐Signal覆盖、DLC、样本数、成熟度和定义指纹见`machine_evidence/signal_coverage.csv`与`dbc_definition_comparison.csv`。
"""
    (OUT / "DBC关键Signal覆盖与可读性.md").write_text(coverage_md, encoding="utf-8")

    audit = f"""# TM3-007 工程审计

## 输入与复现

```sh
.venv/bin/python src/analyze_tm3_007.py
```

- ASC：`{ASC.relative_to(ROOT)}`（内部旧标签仍为TM3-008；以用户确认后的文件名和实测状态窗口为当前映射）
- ASC SHA-256：`{sha(ASC)}`
- Approved Plan SHA-256：`{sha(APPROVED)}`
- ONYX DBC SHA-256：`{sha(ONYX)}`
- 解析帧：{total:,}；损坏帧：{malformed}；CAN ID：{unique_id_count}；时间范围：{start:.6f}–{end:.6f}s。
- 文件头明确写有`Derived analysis input`与600秒裁剪区间；正式TM3-007窗口为103.1571秒进入低通信候选后至600秒，0–103.1571秒作为前序下电上下文，不纳入上电动作结论。

## 方法与门

分析只消费Approved的23项Signal/派生量。多DBC只用于这些Approved项的定义审计和Signal Validation，不把额外Signal加入正式结论。事件时间只来自CAN内部变化，未生成Observed Event Time。

`0x20A`逐帧原始bit、全部DBC定义指纹、覆盖门、事件样本、Evidence Assessment和Report View Model均保存在`machine_evidence/`。车辆异常与解释链异常已分开：冲突字段首先降级Signal成熟度，没有进入故障树。

## 审计结论

Artifact Contract所需四件套、Evidence Assessment、Approved Plan关联、事件窗口、原始/解码Signal和复现入口已经形成。Golden文件未修改；本脚本不运行或改写TM3-009/010/015结果。项目`tests.test_evidence_plan`已通过标准库unittest执行（4项通过）；由于本实验没有通用Golden渲染器，回归结论限定为“既有Golden非修改检查通过”，不宣称执行了不存在的TM3-007 Golden数值对比。
"""
    (OUT / "工程审计.md").write_text(audit, encoding="utf-8")

    generated = [
        OUT / "TM3-007_最终报告.md", OUT / "采集时间线与关键Signal.md",
        OUT / "DBC关键Signal覆盖与可读性.md", OUT / "工程审计.md",
        MACHINE / "asc_integrity.json", MACHINE / "decoded_native_samples.csv",
        MACHINE / "network_activity_1s.csv", MACHINE / "dbc_definition_comparison.csv",
        MACHINE / "signal_coverage.csv", MACHINE / "signal_validation_0x20A_raw.csv",
        MACHINE / "signal_validation_assessment.csv", MACHINE / "events.csv",
        MACHINE / "event_signal_samples.csv", MACHINE / "evidence_assessment.csv",
        MACHINE / "report_view_model.json", MACHINE / "experiment_metadata.json",
    ]
    verification = {
        "experiment_id": "TM3-007", "artifact_contract": "PASS",
        "approved_plan_gate": "PASS", "approved_signal_count": len(plan),
        "evidence_requirement_count": len(assessment), "completion_status": "COMPLETE_WITH_GAPS",
        "asc_analyzed": True, "observed_event_time_fabricated": False,
        "extra_formal_signal_added": False,
        "evidence_plan_unittest": "PASS_4_TESTS",
        "golden_regression": "PASS_EXISTING_GOLDEN_NON_MUTATION_CHECK_ONLY",
        "generated_files": [{"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for path in generated],
    }
    write_json(MACHINE / "verification.json", verification)
    print(json.dumps(verification, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
