"""Render the TM3-008 human-readable bundle from approved machine evidence only."""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from evidence_plan import EvidenceAssessment, read_approved_csv
from report_renderer import (
    ControlNodeView, ControlRelationshipLine, ControlRelationshipView,
    CoreSignal, CoverageSignal, ExperimentReport, MainlineVerification,
    SemanticTimelineEvent, render_report_bundle,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/TM3-008"
MACHINE = OUT / "machine_evidence"


def read_csv(name: str) -> list[dict[str, str]]:
    with (MACHINE / name).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def read_json(name: str) -> dict:
    return json.loads((MACHINE / name).read_text(encoding="utf-8"))


def assessments() -> tuple[EvidenceAssessment, ...]:
    return tuple(EvidenceAssessment(row["requirement_id"], row["status"],
                                    row["evidence_summary"], row["limitation"])
                 for row in read_csv("evidence_assessment.csv"))


def semantic_events() -> tuple[SemanticTimelineEvent, ...]:
    rows = {row["event_id"]: row for row in read_csv("key_events.csv")}
    specs = (
        ("E00", "起始状态", ("UI_readyForDrive", "VCLEFT_frontLatchStatus", "VCSEC_simpleLockStatus",
                              "BMS_contactorState", "PCS_dcdc12VSupportStatus"), "建立CAN内部起始参考状态。"),
        ("E01", "开关门与落锁", ("VCLEFT_frontLatchStatus",), "驾驶门闩反馈进入打开状态。"),
        ("E02", "开关门与落锁", ("VCLEFT_frontLatchStatus",), "驾驶门闩反馈回到关闭状态。"),
        ("E03", "开关门与落锁", ("VCSEC_lockRequestType", "VCSEC_simpleLockStatus",
                                    "VCSEC_vehicleLockStatus"), "形成CAN域内NFC落锁候选与锁止反馈。"),
        ("E04", "需求/消费者状态退出", ("UI_readyForDrive",), "Ready消费者状态候选退出。"),
        ("E05", "最终下电执行", ("VCFRONT_vehiclePowerState",), "车辆供电系统结果候选进入OFF。"),
        ("E06", "最终下电执行", ("BMS_contactorState",), "高压总接触器开始打开。"),
        ("E07", "最终下电执行", ("PCS_dcdc12VSupportStatus",), "DCDC低压支持最终退出。"),
        ("E08", "最终下电执行", ("HVP_packContPositiveState", "HVP_packContNegativeState"),
         "正负接触器候选进入打开过程。"),
        ("E09", "高压物理响应候选", ("PCS_dcdcHvBusDischargeStatus",), "PCS放电执行状态候选激活。"),
        ("E10", "最终下电执行", ("BMS_contactorState",), "BMS总接触器进入OPEN。"),
        ("E11", "高压物理响应候选", ("BMS_packVoltage",), "0x132电压字段快速下降。"),
        ("E12", "高压物理响应候选", ("PCS_dcdcHvBusDischargeStatus",), "PCS放电执行状态候选结束。"),
        ("E13", "最终下电执行", ("HVP_packContPositiveState", "HVP_packContNegativeState"),
         "正负接触器候选进入OPEN。"),
        ("E14", "网络分层退出", ("BMS_hvsBusAsleep",), "BMS消费者视角的总线休眠候选出现。"),
        ("E15", "末段通信静默", ("NetworkFrameRate_derived", "CanIdLastSeenTime_derived"),
         "当前采集域进入末段无帧窗口。"),
        ("E16", "末段通信静默", ("NetworkFrameRate_derived",), "声明的TM3-008采集窗口结束。"),
    )
    result = []
    for event_id, phase, refs, significance in specs:
        row = rows[event_id]
        result.append(SemanticTimelineEvent(
            row["time_s"].rstrip("0").rstrip("."), row["event"], (row["observed"],), refs,
            significance, row["boundary"], phase,
            "stable_window" if event_id == "E16" else "event",
        ))
    return tuple(result)


def coverage_signals(plan) -> tuple[CoverageSignal, ...]:
    coverage = {row["signal_key"]: row for row in read_csv("approved_candidate_coverage.csv")}
    validation = {row["signal_key"]: row for row in read_csv("signal_validation_assessment.csv")}
    result = []
    for approved in sorted(plan.signals, key=lambda item: item.effective_order):
        if approved.has_position("EXCLUDE"):
            continue
        row = coverage[approved.signal_key]
        maturity = validation[approved.signal_key]["post_validation_maturity"]
        observed = row["observed"] or "无有效观测"
        changed = "未观察" if row["readability"] == "NO_FRAME" else (
            "是" if int(row["transition_count"] or 0) > 1 else "否/未形成变化证据")
        result.append(CoverageSignal(
            approved.signal_key, observed, changed, f"{row['readability']}；{maturity}",
            f"用于{approved.evidence_requirement}的{approved.effective_role}证据。",
            "DERIVED" if approved.can_id == "derived" else "DBC",
            approved.effective_role, approved.message, validation[approved.signal_key]["evidence"],
            approved.effective_order,
        ))
    return tuple(result)


def core_signals(plan) -> tuple[CoreSignal, ...]:
    coverage = {row["signal_key"]: row for row in read_csv("approved_candidate_coverage.csv")}
    validation = {row["signal_key"]: row for row in read_csv("signal_validation_assessment.csv")}
    result = []
    for approved in sorted(plan.signals, key=lambda item: item.effective_order):
        if not approved.has_position("CORE_SIGNAL_TABLE"):
            continue
        row = coverage[approved.signal_key]
        observed = row["observed"] or "无有效观测"
        changed = "未观察" if row["readability"] == "NO_FRAME" else (
            "是" if int(row["transition_count"] or 0) > 1 else "否/未形成变化证据")
        result.append(CoreSignal(
            approved.signal_key, observed, changed,
            f"{row['readability']}；{validation[approved.signal_key]['post_validation_maturity']}",
            f"承担{approved.evidence_requirement}中的{approved.effective_role}；不得超过Approved角色解释。",
        ))
    return tuple(result)


def build_report():
    plan = read_approved_csv(OUT / "evidence_plan_approved.csv")
    integrity = read_json("asc_integrity.json")
    summary = read_json("analysis_summary.json")
    report = ExperimentReport(
        experiment_id="TM3-008",
        title="TM3-008 关门落锁完整下电：车型条件化基线分析",
        metadata_lines=(
            "用途：正常基线数据采集；评价关门、NFC落锁后的条件化下电过程，不作车辆故障判断。",
            "车辆：Tesla Model 3，上海产2021款，2021年5月出厂，标准续航，55 kWh，后驱。",
            f"完成状态：{summary['completion_status']}；范围：{plan.scope}。",
            "ASC正式Analysis Window为0–660秒；脚本为0–600秒，时间覆盖满足并有60秒余量。",
        ),
        facts=(
            "CAN内部观察到驾驶门CLOSED→OPENED→CLOSED；关门后保持UNLOCKED，随后ACTIVE_NFC_LOCK与两项LOCKED反馈同步出现。",
            "落锁后，UI Ready消费者状态先退出；GTW分域asleep候选随后出现；最终vehiclePowerState进入OFF，高压接触器与DCDC执行退出。",
            "BMS总接触器在282.2451秒进入OPENING、282.5436秒进入OPEN；0x20A正负接触器候选在282.3549秒进入OPENING、283.3549秒进入OPEN。",
            "295.8383秒为当前采集域最后一帧，至660秒保持无帧，共364.1617秒；该事实只描述当前采集域。",
        ),
        control_relationship=ControlRelationshipView(
            (ControlNodeView("车身门闩与锁止反馈", "直接观测"),
             ControlNodeView("离座、请求与许可层", "本次无直接观测"),
             ControlNodeView("Ready消费者/车辆供电结果", "部分可观测"),
             ControlNodeView("高压接触器与DCDC执行", "直接观测"),
             ControlNodeView("下游母线物理响应", "部分可观测"),
             ControlNodeView("当前采集域通信退出", "直接观测")),
            "接触器状态、放电候选和0x132电压字段形成时序交叉支持，但下游母线定量语义未闭环。",
            "DCDC支持最终转IDLE，低压电流候选归零；无外部12V实测。",
            ("时间顺序不自动升级为ECU内部控制因果。",),
        ),
        diagnostic_conclusion=(
            "本次建立了关门未锁、NFC落锁/锁止反馈、Ready消费者状态退出、高压/DCDC最终退出及采集域静默的条件化CAN基线。",
            "完整请求—许可—执行链尚未建立；实验完成状态保持PARTIAL。",
        ),
        evidence_boundaries=(),
        recommendations=(
            "保留本次已支持的关门落锁、高压/DCDC执行及网络退出过程证据。",
            "如需闭合ER-05，最小补采应增加可靠接触器下游高压母线物理测量或经独立验证的定量Signal。",
            "如需闭合ER-09/ER-10，应补充现场记录/App时间锚点与不少于10分钟的连续无干预静默观察。",
            "当前不进入车辆故障诊断树，也不修改共享方法论。",
        ),
        timeline_signal_keys=tuple(row.signal_key for row in plan.signals
                                   if row.has_position("CORE_TIMELINE")),
        timeline=(), analysis_tables=(), core_signals=core_signals(plan),
        readability_issues=(
            "VCLEFT_frontOccupancyStatus、DI_gear、DI_systemState无帧；VCFRONT_12vStatusForDrive有帧但当前MUX/DBC下不可读。",
            "BMS_hvState、PCS_dcdcMainState、PCS_dcdcHvBusVolt均为SEMANTIC_VALIDATION_FAILED，不解释为车辆故障。",
            "UI_lockRequest全程IDLE，不能解释为钥匙卡落锁REQUEST，也不能独立满足ER-03。",
            "0x20A正负接触器候选仅在TM3-008范围内STRONGLY_SUPPORTED，保留多DBC边界。",
        ),
        audit_lines=(
            f"ASC输入：{integrity['source_asc_path']}；SHA-256：{integrity['source_asc_sha256']}。",
            f"脚本输入：{integrity['collection_script_path']}；SHA-256：{integrity['collection_script_sha256']}。",
            f"正式窗口：0–660秒；有效帧{integrity['interval_parsed_frame_count']}，CAN ID {integrity['unique_can_id_count']}，损坏帧{integrity['interval_malformed_frame_count']}。",
            f"Approved Plan SHA-256：{integrity['approved_plan_sha256']}；有效Candidate 32项，Exclude 1项。",
            "分析入口：.venv\\Scripts\\python.exe src\\analyze_tm3_008.py。",
            "展示入口：.venv\\Scripts\\python.exe src\\render_tm3_008.py；只读取Approved Plan与machine_evidence。",
            "共享Renderer执行结构校验；正式四件套不包含原始逐帧字段。",
        ),
        assessments=assessments(), timeline_profile="WAKE_HV", judgment_heading="基线结论",
        semantic_timeline_events=semantic_events(), coverage_signals=coverage_signals(plan),
        control_mainline=("门闩开关反馈", "NFC落锁与锁止结果", "Ready/供电结果退出",
                          "高压接触器与DCDC执行", "网络分层退出", "采集域末段静默"),
        mainline_verification=(
            MainlineVerification("门闩开关反馈", ("VCLEFT_frontLatchStatus",), "CLOSED→OPENED→CLOSED已直接观察。", "占座/离座无直接证据。"),
            MainlineVerification("NFC落锁与锁止结果", ("VCSEC_lockRequestType", "VCSEC_simpleLockStatus", "VCSEC_vehicleLockStatus"), "CAN域内请求类型候选和状态反馈同步。", "外部刷卡与声光反馈属于ER-10 GAP。"),
            MainlineVerification("Ready/供电结果退出", ("UI_readyForDrive", "VCFRONT_vehiclePowerState"), "消费者状态与系统结果的退出顺序已观察。", "两者均不是直接下电REQUEST/PERMISSION/COMMAND。"),
            MainlineVerification("高压接触器与DCDC执行", ("BMS_contactorState", "HVP_packContPositiveState", "HVP_packContNegativeState", "PCS_dcdc12VSupportStatus"), "接触器及DCDC最终退出获得多信号支持。", "下游高压母线定量响应仍为GAP。"),
            MainlineVerification("网络分层退出", ("GTW_chBusAsleep", "GTW_VEHBusAsleep", "BMS_hvsBusAsleep", "CanIdLastSeenTime_derived"), "分域候选与逐ID Last Seen共同支持分层退出。", "不等同ECU断电。"),
            MainlineVerification("采集域末段静默", ("NetworkFrameRate_derived", "ActiveCanIdCount_derived"), "295.8383–660秒为0帧/0活跃ID。", "仅364.1617秒，未满足ER-09不少于10分钟要求。"),
        ),
        global_evidence_boundaries=(
            "Planned Time、CAN Observed Time与缺失的Observed Event Time严格分开；不反推人工动作精确时间。",
            "当前采集域通信静默不得表述为整车全部ECU下电或整车完全休眠。",
            "ER-10外部现场证据GAP保持不变，任何CAN Candidate均不能替代。",
            "PCS_dcdcHvBusVolt语义验证失败；0x132电压字段物理位置冲突，ER-05下游母线证据保持不足。",
            "结论限定为TM3-008、THIS_EXPERIMENT_ONLY，不迁移为车型级永久Signal语义。",
        ),
        control_relationship_lines=(
            ControlRelationshipLine("实测状态推进", "门开 → 门关 → NFC落锁/LOCKED → Ready消费者退出 → 分域asleep候选 → OFF → 接触器/DCDC退出 → 采集域静默", ("VCLEFT_frontLatchStatus", "VCSEC_lockRequestType", "VCSEC_simpleLockStatus", "UI_readyForDrive", "VCFRONT_vehiclePowerState", "BMS_contactorState", "PCS_dcdc12VSupportStatus", "NetworkFrameRate_derived"), "只表达CAN内部实际顺序，不主张完整控制因果。"),
            ControlRelationshipLine("高压执行与物理响应", "总接触器及正负接触器候选打开；放电状态候选短时ACTIVE；0x132电压字段快速下降", ("BMS_contactorState", "HVP_packContPositiveState", "HVP_packContNegativeState", "PCS_dcdcHvBusDischargeStatus", "BMS_packVoltage"), "可靠下游母线定量Signal缺失。"),
            ControlRelationshipLine("低压能源响应", "DCDC支持最终ACTIVE→IDLE，低压输出电流候选归零", ("PCS_dcdc12VSupportStatus", "PCS_dcdcLvBusVolt", "PCS_dcdcLvOutputCurrent"), "无外部12V测量。"),
        ),
    )
    return plan, report


def main() -> None:
    plan, report = build_report()
    (MACHINE / "report_view_model.json").write_text(
        json.dumps(asdict(report), ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    outputs = render_report_bundle(plan, report, OUT)
    aliases = {
        "timeline": OUT / "TM3-008_采集时间线与关键Signal.md",
        "coverage": OUT / "TM3-008_DBC关键Signal覆盖与可读性.md",
        "audit": OUT / "TM3-008_工程审计.md",
    }
    for key, alias in aliases.items():
        alias.write_bytes(outputs[key].read_bytes())
    paths = {**outputs, **{f"requested_{key}": value for key, value in aliases.items()}}
    hashes = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in paths.values()}
    (MACHINE / "report_bundle_verification.json").write_text(
        json.dumps({"renderer": "shared report_renderer.py", "profile": report.timeline_profile,
                    "contract_validation": "PASSED", "files": hashes},
                   ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    for name in ("asc_integrity.json", "analysis_summary.json"):
        state = read_json(name)
        state["formal_report_bundle_generated"] = True
        (MACHINE / name).write_text(
            json.dumps(state, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
