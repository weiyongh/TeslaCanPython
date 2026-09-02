"""Pure presentation migration for TM3-007.

This adapter reads only the approved plan and existing report-layer machine
evidence.  It must never read ASC/DBC inputs or perform evidence assessment.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

from evidence_plan import EvidenceAssessment, read_approved_csv
from report_renderer import (
    ControlNodeView,
    ControlRelationshipLine,
    ControlRelationshipView,
    CoverageSignal,
    CoreSignal,
    ExperimentReport,
    MainlineVerification,
    SemanticTimelineEvent,
    Table,
    render_report_bundle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output/TM3-007"
MACHINE = OUTPUT / "machine_evidence"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _semantic_timeline_events() -> tuple[SemanticTimelineEvent, ...]:
    events = _csv(MACHINE / "events.csv")
    presentation = {
        "E00": (
            "采集域进入长时间无帧窗口。",
            ("网络帧率降为0",),
            ("NetworkFrameRate_derived",),
            "形成后续通信恢复的采集域内前置状态。",
            "",
        ),
        "E01": (
            "长时间无帧后，CAN通信恢复。",
            ("网络帧率由0恢复", "活跃CAN ID重新出现"),
            ("NetworkFrameRate_derived", "ActiveCanIdCount_derived"),
            "标志本采集域内部上电状态链开始。",
            "没有独立Observed Event Time，不确认具体人工解锁时刻。",
        ),
        "E02": (
            "BMS总接触器进入闭合过程。",
            ("BMS接触器总状态进入CLOSING", "Pack电压开始建立"),
            ("BMS_contactorState", "BMS_packVoltage"),
            "高压建立执行序列开始。",
            "",
        ),
        "E03": (
            "高压互锁候选转为正常，正接触器进入预充。",
            ("HVIL由UNKNOWN转为STATUS_OK", "正接触器由OPEN转为PRECHARGE"),
            ("HVP_hvilStatus", "HVP_packContPositiveState", "BMS_packVoltage"),
            "安全条件候选满足后进入预充阶段，Pack电压同期上升。",
            "0x20A语义仅在本实验既有Signal Validation边界内成立。",
        ),
        "E04": (
            "BMS总接触器闭合，Pack电压建立至约354 V。",
            ("接触器总状态由CLOSING转为CLOSED", "Pack电压升至353.51 V"),
            ("BMS_contactorState", "BMS_packVoltage"),
            "总接触器状态与Pack侧物理电压响应形成实验级闭环。",
            "",
        ),
        "E05": (
            "正负接触器候选进入保持状态，DCDC低压支持激活。",
            ("正接触器由PRECHARGE转为ECONOMIZED", "负接触器由OPEN转为ECONOMIZED",
             "12V支持由IDLE转为ACTIVE"),
            ("HVP_packContPositiveState", "HVP_packContNegativeState", "PCS_dcdc12VSupportStatus"),
            "高压接触器序列完成，并进入DCDC低压支持阶段。",
            "0x20A接触器语义不自动升级为车型级正式定义。",
        ),
        "E06": (
            "用户界面可驱动候选由0变为1。",
            ("UI ready候选由0转为1",),
            ("UI_readyForDrive",),
            "提供高压建立后的显示/消费者层交叉反馈。",
            "该Signal是显示层候选，不作为驱动许可源头。",
        ),
        "E07": (
            "驾驶门闩反馈进入OPENED。",
            ("驾驶门闩由CLOSED转为OPENED",),
            ("VCLEFT_frontLatchStatus",),
            "确认门闩反馈能够区分开门状态。",
            "该CAN边沿不是独立人工开门时刻。",
        ),
        "E08": (
            "驾驶门闩反馈回到CLOSED。",
            ("驾驶门闩由OPENED转为CLOSED",),
            ("VCLEFT_frontLatchStatus",),
            "形成CLOSED→OPENED→CLOSED门闩状态序列。",
            "该CAN边沿不是独立人工关门时刻。",
        ),
        "E09": (
            "电驱状态报文出现并稳定为P/STANDBY。",
            ("挡位反馈可读为P", "电驱状态可读为STANDBY", "制动字段仍为INVALID"),
            ("DI_gear", "DI_systemState", "DI_brakePedalState"),
            "建立挂D前的电驱内部参考状态。",
            "制动输入不能由本事件确认。",
        ),
        "E10": (
            "挡位进入D，电驱状态同步进入ENABLE。",
            ("挡位由P转为D", "电驱状态由STANDBY转为ENABLE"),
            ("DI_gear", "DI_systemState"),
            "形成CAN内部可驱动状态建立节点。",
            "",
        ),
        "E11": (
            "挡位回到P，电驱状态同步回到STANDBY。",
            ("挡位由D转为P", "电驱状态由ENABLE转为STANDBY"),
            ("DI_gear", "DI_systemState"),
            "形成可驱动状态退出节点。",
            "",
        ),
        "E12": (
            "P挡上电状态保持至采集结束。",
            ("P/STANDBY保持", "接触器CLOSED保持", "12V支持ACTIVE保持"),
            ("DI_gear", "DI_systemState", "BMS_contactorState", "PCS_dcdc12VSupportStatus"),
            "形成约44.6秒P挡上电稳定窗口。",
            "",
        ),
    }
    result = []
    phases = {
        "E00": "低通信候选与通信恢复", "E01": "低通信候选与通信恢复",
        "E02": "高压建立序列", "E03": "高压建立序列",
        "E04": "高压建立序列", "E05": "高压建立序列",
        "E06": "Ready/车身反馈", "E07": "Ready/车身反馈", "E08": "Ready/车身反馈",
        "E09": "D/ENABLE进入与返回P", "E10": "D/ENABLE进入与返回P",
        "E11": "D/ENABLE进入与返回P", "E12": "结束稳定窗口",
    }
    for event in events:
        summary, changes, refs, significance, limitation = presentation[event["event_id"]]
        result.append(SemanticTimelineEvent(
            event["can_time_s"].rstrip("0").rstrip("."), summary, changes, refs,
            significance, limitation, phases[event["event_id"]],
            "stable_window" if event["event_id"] == "E12" else "event",
        ))
    return tuple(result)


def _assessments() -> tuple[EvidenceAssessment, ...]:
    return tuple(EvidenceAssessment(row["requirement_id"], row["assessment"],
                                    row["evidence"], row["reason"])
                 for row in _csv(MACHINE / "evidence_assessment.csv"))


def _core_signals(plan) -> tuple[CoreSignal, ...]:
    coverage = {row["signal_key"]: row for row in _csv(MACHINE / "signal_coverage.csv")}
    changed = {
        "VCLEFT_frontLatchStatus": "是",
        "VCLEFT_frontOccupancyStatus": "未观察",
        "DI_brakePedalState": "否（全程INVALID）",
        "DI_gear": "是",
    }
    purpose = {
        "VCLEFT_frontLatchStatus": "记录门闩CLOSED→OPENED→CLOSED反馈；不作为人工动作时刻。",
        "VCLEFT_frontOccupancyStatus": "检查入座条件节点覆盖；本次无帧，仅保留证据缺口。",
        "DI_brakePedalState": "检查制动条件输入；全程INVALID，不用于证明制动动作。",
        "DI_gear": "记录P→D→P挡位反馈，并与电驱状态链交叉验证。",
    }
    items = []
    for approved in sorted(plan.signals, key=lambda row: row.effective_order):
        if not approved.has_position("CORE_SIGNAL_TABLE"):
            continue
        row = coverage[approved.signal_key]
        observed = row["observed_values_or_range"] or "无有效观测"
        decode = f"{row['readability']}；{row['post_validation_maturity']}"
        items.append(CoreSignal(approved.signal_key, observed, changed[approved.signal_key],
                                decode, purpose[approved.signal_key]))
    return tuple(items)


def _coverage_signals(plan) -> tuple[CoverageSignal, ...]:
    """Map every Approved item from existing coverage evidence; do not reassess it."""
    coverage = {row["signal_key"]: row for row in _csv(MACHINE / "signal_coverage.csv")}
    presentation_order = {
        "NetworkFrameRate_derived": 10, "ActiveCanIdCount_derived": 20,
        "GTW_BMP_AWAKE_PIN": 30, "DI_keepAliveRequest": 40, "UI_lockRequest": 50,
        "HVP_hvilStatus": 60, "BMS_isolationResistance": 70,
        "BMS_contactorState": 80, "HVP_packContPositiveState": 90,
        "HVP_packContNegativeState": 100, "BMS_packVoltage": 110,
        "PCS_dcdcHvBusVolt": 120, "BMS_hvState": 130,
        "PCS_dcdc12VSupportStatus": 140, "PCS_dcdcMainState": 150,
        "PCS_dcdcLvBusVolt": 160, "PCS_dcdcLvOutputCurrent": 170,
        "UI_readyForDrive": 180, "VCLEFT_frontLatchStatus": 190,
        "VCLEFT_frontOccupancyStatus": 200, "DI_brakePedalState": 210,
        "DI_gear": 220, "DI_systemState": 230,
    }
    items = []
    for approved in sorted(plan.signals, key=lambda row: row.effective_order):
        row = coverage[approved.signal_key]
        observed = row["observed_values_or_range"] or "无有效观测"
        if row["readability"] == "NO_FRAME":
            changed = "未观察"
        elif " | " in observed or ".." in observed:
            changed = "是"
        else:
            changed = "否/未形成变化证据"
        decode = f"{row['readability']}；{row['post_validation_maturity']}"
        purpose = f"用于{approved.evidence_requirement}的{approved.effective_role}证据。"
        items.append(CoverageSignal(
            approved.signal_key, observed, changed, decode, purpose,
            "DERIVED" if approved.can_id == "derived" else "DBC",
            approved.effective_role, row["approved_source"], row["boundary"],
            presentation_order[approved.signal_key],
        ))
    return tuple(items)


def _validation_table() -> Table:
    rows = [row for row in _csv(MACHINE / "signal_validation_assessment.csv")
            if row["can_id"] == "0x20A"]
    return Table(
        "0x20A既有Signal Validation迁移",
        ("Signal", "既有结果", "时序", "方向", "枚举", "既有证据与边界"),
        tuple((row["signal_key"], row["result"], row["timing"], row["direction"],
               row["enumeration"], f"{row['evidence']}；{row['failure_or_boundary']}") for row in rows),
    )


def build_report() -> tuple[object, ExperimentReport]:
    plan = read_approved_csv(OUTPUT / "evidence_plan_approved.csv")
    view = _json(MACHINE / "report_view_model.json")
    metadata = _json(MACHINE / "experiment_metadata.json")
    integrity = _json(MACHINE / "asc_integrity.json")
    relationship = view["control_relationship_view"]
    report = ExperimentReport(
        experiment_id="TM3-007",
        title="TM3-007 开锁开门完整上电：车型条件化基线分析",
        metadata_lines=(
            f"用途：{view['use']}。",
            f"车辆：{metadata['vehicle']}。",
            f"完成状态：{view['completion_status']}；范围：{view['scope']}。",
        ),
        facts=tuple(view["facts"]),
        control_relationship=ControlRelationshipView(
            (
                ControlNodeView("车身输入/门闩反馈", "部分可观测"),
                ControlNodeView("占座与制动条件", "本次无直接观测"),
                ControlNodeView("本采集域网络恢复", "直接观测"),
                ControlNodeView("高压安全条件与接触器执行", "部分可观测"),
                ControlNodeView("可驱动状态", "部分可观测"),
            ),
            relationship["hv_conditions_and_execution"] + "。",
            relationship["dcdc_response"] + "。",
            (),
        ),
        diagnostic_conclusion=(view["baseline_conclusion"],
                               f"本实验完成状态为{view['completion_status']}。"),
        evidence_boundaries=(
            "独立Observed Event Time缺失；Planned Time只能用于粗定位。",
            "不把CAN变化反推为人工动作时间，不形成精确“人工动作→CAN响应”延迟。",
            "103.1571–470.1237秒只称为本采集域低通信候选，不称为整车真实休眠。",
            "结论限定为既有证据支持的CAN内部状态转换、顺序和条件化状态链。",
            "制动字段INVALID、占座报文无帧；解锁请求和外部12V实测缺失。",
            "0x20A仅迁移本实验既有Signal Validation结果，不升级车型级语义。",
        ),
        recommendations=(view["minimum_next_step"], "当前不进入车辆故障诊断树。"),
        timeline_signal_keys=tuple(row.signal_key for row in plan.signals
                                   if row.has_position("CORE_TIMELINE")),
        timeline=(),
        analysis_tables=(),
        core_signals=_core_signals(plan),
        readability_issues=(
            "BMS_hvState全程DOWN、BMS_isolationResistance全程0 kOhm、PCS_dcdcMainState全程STANDBY：既有结论均为SEMANTIC_VALIDATION_FAILED，不解释为车辆故障。",
            "0x20A三项保留多DBC/DLC冲突边界；实验级结果见时间线专项表和machine_evidence/signal_validation_assessment.csv。",
            "PCS_dcdcHvBusVolt定量语义验证失败；PCS_dcdcLvBusVolt为实验候选，PCS_dcdcLvOutputCurrent仅部分验证。",
        ),
        audit_lines=(
            f"既有分析输入记录：{metadata['source_file']}；本迁移器未读取该ASC。",
            f"既有ASC SHA-256记录：{integrity['asc_sha256']}；解析帧{integrity['parsed_frame_count']}，损坏帧{integrity['malformed_frame_count']}。",
            f"Approved Plan SHA-256记录：{integrity['approved_plan_sha256']}。",
            "展示输入：machine_evidence/report_view_model.json、events.csv、event_signal_samples.csv、signal_coverage.csv、evidence_assessment.csv、signal_validation_assessment.csv。",
            "生成入口：python3 src/render_tm3_007.py；仅执行Report View Model适配与共享Renderer输出。",
        ),
        special_tables=(_validation_table(),),
        assessments=_assessments(),
        timeline_profile="WAKE_HV",
        profile_timeline_rows=(),
        judgment_heading="基线结论",
        semantic_timeline_events=_semantic_timeline_events(),
        control_mainline=(
            "本采集域通信恢复", "高压安全条件候选满足", "预充/接触器执行",
            "Pack高压建立", "DCDC低压支持", "可驱动状态建立", "返回P/STANDBY稳定状态",
        ),
        mainline_verification=(
            MainlineVerification(
                "本采集域通信恢复",
                ("NetworkFrameRate_derived", "ActiveCanIdCount_derived"),
                "采集域内通信变化PARTIALLY_VALIDATED。",
                "不确认整车真实休眠/唤醒，不反推人工解锁时刻。",
            ),
            MainlineVerification(
                "高压安全条件候选满足", ("HVP_hvilStatus",),
                "本实验既有结果STRONGLY_SUPPORTED。",
                "0x20A多DBC并列验证；无独立HVIL外部观测。",
            ),
            MainlineVerification(
                "预充/接触器执行",
                ("BMS_contactorState", "HVP_packContPositiveState", "HVP_packContNegativeState"),
                "本实验既有结果STRONGLY_SUPPORTED。",
                "0x20A结果不升级为车型级正式语义。",
            ),
            MainlineVerification(
                "Pack高压建立", ("BMS_packVoltage",),
                "Pack侧物理响应STRONGLY_SUPPORTED。",
                "不等同于所有下游高压母线均已独立验证。",
            ),
            MainlineVerification(
                "DCDC低压支持",
                ("PCS_dcdc12VSupportStatus", "PCS_dcdcLvBusVolt", "PCS_dcdcLvOutputCurrent"),
                "支持状态与低压电压STRONGLY_SUPPORTED；输出电流PARTIALLY_VALIDATED。",
                "无外部12V测量；0x2B4存在定义差异。",
            ),
            MainlineVerification(
                "可驱动状态建立", ("DI_gear", "DI_systemState", "UI_readyForDrive"),
                "挡位/电驱状态及显示层交叉反馈均为STRONGLY_SUPPORTED。",
                "UI_readyForDrive只作显示/消费层交叉反馈，不作为控制许可源头。",
            ),
            MainlineVerification(
                "返回P/STANDBY稳定状态", ("DI_gear", "DI_systemState"),
                "CAN内部返回状态STRONGLY_SUPPORTED。",
                "不反推驾驶员动作精确时刻。",
            ),
        ),
        global_evidence_boundaries=(
            "独立Observed Event Time缺失；Planned Time只能用于粗定位。",
            "不把CAN变化反推为人工动作时间，不形成精确“人工动作→CAN响应”延迟。",
            "103.1571–470.1237秒只称为本采集域低通信候选，不称为整车真实休眠。",
            "结论限定为既有证据支持的CAN内部状态转换、顺序和条件化状态链。",
            "制动字段INVALID、占座报文无帧；解锁请求和外部12V实测缺失。",
            "0x20A仅迁移本实验既有Signal Validation结果，不升级车型级语义。",
        ),
        coverage_signals=_coverage_signals(plan),
        control_relationship_lines=(
            ControlRelationshipLine(
                "系统进入/状态推进主线",
                "本采集域低通信候选 → 通信恢复 → 高压建立 → D/ENABLE → 返回P/STANDBY稳定",
                ("NetworkFrameRate_derived", "ActiveCanIdCount_derived", "DI_gear", "DI_systemState"),
                "这是实测CAN状态推进，不等同于已经证明整车真实唤醒或ECU内部完整控制算法。",
            ),
            ControlRelationshipLine(
                "高压控制链",
                "HVIL候选转为STATUS_OK → 正接触器候选进入PRECHARGE → BMS总接触器CLOSING/CLOSED → 正负接触器候选进入ECONOMIZED",
                ("HVP_hvilStatus", "HVP_packContPositiveState", "BMS_contactorState",
                 "HVP_packContNegativeState"),
            ),
            ControlRelationshipLine(
                "高压物理响应",
                "Pack端电压约5 V → 约354 V",
                ("BMS_packVoltage",),
                "BMS_packVoltage是Pack端反馈，不是接触器下游DC Link电压；当前Approved范围没有独立DC Link电压证据。",
            ),
            ControlRelationshipLine(
                "低压能源响应/交叉验证",
                "DCDC支持IDLE → ACTIVE；PCS侧低压电压/电流候选同步建立",
                ("PCS_dcdc12VSupportStatus", "PCS_dcdcLvBusVolt", "PCS_dcdcLvOutputCurrent"),
                "无外部12V仪表实测，0x2B4定义差异继续保留。",
            ),
            ControlRelationshipLine(
                "可驱动状态及结果反馈",
                "UI Ready候选0 → 1；其后挡位P → D且电驱STANDBY → ENABLE，最终返回P/STANDBY",
                ("UI_readyForDrive", "DI_gear", "DI_systemState"),
                "UI_readyForDrive仅作显示/消费层交叉反馈，不解释为驱动许可源头。",
            ),
        ),
    )
    return plan, report


def main() -> None:
    plan, report = build_report()
    render_report_bundle(plan, report, OUTPUT)


if __name__ == "__main__":
    main()
