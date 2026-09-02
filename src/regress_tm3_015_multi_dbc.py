"""Generate a non-destructive TM3-015 multi-DBC regression report set."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "output/TM3-015"
SOURCE = BASE / "dbc_all_sources_audit/multi_dbc_validation"
OUT = BASE / "regression_multi_dbc"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows, fields=None):
    if not rows:
        return
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields or list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    approved_path = BASE / "evidence_plan_approved.csv"
    approved = list(csv.DictReader(approved_path.open(encoding="utf-8-sig")))
    fields = list(approved[0])
    supplemental = [
        ("HVP_fcLinkAllowedToEnergize", "HVP_fcLinkAllowedToEnergize", "ID20AHVP_contactorState", "0x20A", "enum", "ER-03", "高压直流充电许可/安全条件候选", "P1", 191, "快充链路允许上电类型（实验候选；不等于OEM完整许可）"),
        ("BMS_fcContactorRequest", "BMS_fcContactorRequest", "ID232BMS_contactorRequest", "0x232", "enum", "ER-03", "快充接触器请求候选", "P1", 192, "BMS快充接触器开闭请求（其他DBC候选，主体层级待继续验证）"),
        ("HVP_fcContPositiveAuxOpen", "HVP_fcContPositiveAuxOpen", "ID20AHVP_contactorState", "0x20A", "bool", "ER-03", "快充接触器反馈候选", "P1", 193, "快充正极接触器辅助触点开路反馈（其他DBC候选）"),
        ("HVP_fcContNegativeAuxOpen", "HVP_fcContNegativeAuxOpen", "ID20AHVP_contactorState", "0x20A", "bool", "ER-03", "快充接触器反馈候选", "P1", 194, "快充负极接触器辅助触点开路反馈（其他DBC候选）"),
        ("CP_hvChargeStatus_log", "CP_hvChargeStatus_log", "ID43DCP_chargeStatusLog", "0x43D", "enum", "ER-03", "高压充电阶段候选", "P1", 195, "高压充电阶段日志状态（其他DBC候选，枚举须保留实验边界）"),
        ("FC_statusCode", "FC_statusCode", "ID214FastChargeVA", "0x214", "enum", "ER-02", "可见通信/快充状态候选", "P1", 196, "快充设备或适配器状态码（请求主体及枚举语义待验证）"),
        ("FC_dcVoltage", "FC_dcVoltage", "ID214FastChargeVA", "0x214", "V", "ER-04", "直流输出交叉验证", "P1", 197, "另一DBC定义的快充直流电压（时序候选，定量待交叉验证）"),
        ("FC_dcCurrent", "FC_dcCurrent", "ID214FastChargeVA", "0x214", "A", "ER-04", "直流输出交叉验证", "P1", 198, "另一DBC定义的快充直流电流（时序候选，幅值冲突未解决）"),
        ("TotalChargeKWh3D2", "TotalChargeKWh3D2", "ID3D2TotalChargeDischarge", "0x3D2", "kWh", "ER-08", "能源交叉验证", "P2", 199, "车辆累计充入电量计数（其他DBC候选，仅作能源交叉验证）"),
    ]
    effective = [dict(r) for r in approved]
    for key, signal, message, can_id, unit, er, role, priority, order, chinese in supplemental:
        row = {k: "" for k in fields}
        row.update(experiment_id="TM3-015", plan_status="EFFECTIVE_SUPPLEMENTAL",
                   scope="THIS_EXPERIMENT_ONLY", signal_key=key, signal=signal,
                   message=message, can_id=can_id, unit=unit,
                   evidence_requirement=er, suggested_role=role,
                   suggested_priority=priority, suggested_report_position="SUPPLEMENTAL_TIMELINE+SIGNAL_TABLE",
                   suggested_order=order, derivation_reason="多DBC回归补充候选",
                   semantic_status="实验候选", confidence="MEDIUM",
                   uncertainty_flags="NON_ONYX_OR_MULTI_DBC_SEMANTIC_CANDIDATE",
                   review_required="YES", review_decision="REGRESSION_TRIAL",
                   effective_role=role, effective_priority=priority,
                   effective_report_position="SUPPLEMENTAL_TIMELINE+SIGNAL_TABLE",
                   effective_order=order, decision_source="USER_AUTHORIZED_MULTI_DBC_REGRESSION",
                   human_reason="用户授权使用多DBC候选重新生成并试运行；不覆盖原Approved",
                   reviewer="用户", reviewed_at="2026-09-01", chinese_semantic=chinese)
        effective.append(row)
    write_csv(OUT / "evidence_plan_effective_multi_dbc.csv", effective, fields)

    assessments = list(csv.DictReader((BASE / "evidence_assessment.csv").open(encoding="utf-8-sig")))
    for row in assessments:
        if row["requirement_id"] == "ER-02":
            row["evidence_summary"] += "；补充FC_statusCode在115.328s进入准备态候选、133.029s进入运行态候选、245.836s退出"
            row["limitation"] = "协商细节仍不足；状态码主体和枚举语义尚未完全确认"
        elif row["requirement_id"] == "ER-03":
            row["status"] = "SUPPORTED"
            row["evidence_summary"] = "多DBC补充显示：115.845s允许DC链路上电；134.515s快充接触器请求闭合；134.847s正负辅助触点闭合；CP日志139.525s进入ENABLED；随后电压、电流建立"
            row["limitation"] = "支持本次高压充电状态链存在，不确认OEM完整许可条件、控制器内部算法或车型级永久语义"
        elif row["requirement_id"] == "ER-04":
            row["evidence_summary"] += "；FC_dcVoltage/current分别在140.030s/145.030s建立并于246.236s归零，提供独立时序交叉验证"
            row["limitation"] = "多套电流幅值仍冲突，只支持建立/退出时序，不形成准确功率或效率结论"
        elif row["requirement_id"] == "ER-06":
            row["evidence_summary"] += "；BMS快充接触器请求246.518s转OPEN、辅助触点246.848s反馈OPEN"
    write_csv(OUT / "evidence_assessment_multi_dbc.csv", assessments)

    events = [
        ("R00", "115.3280", "快充状态准备候选", "FC_statusCode 0→6"),
        ("R01", "115.8453", "DC链路允许上电候选", "HVP_fcLinkAllowedToEnergize NONE→DC"),
        ("R02", "133.0273", "EVSE测试通过候选", "CP_hvChargeStatus_log TEST_PASSED"),
        ("R03", "134.5149", "快充接触器闭合请求", "BMS_fcContactorRequest OPEN→CLOSE"),
        ("R04", "134.8465", "快充接触器辅助反馈闭合", "正/负AuxOpen 1→0"),
        ("R05", "139.5253", "高压充电使能阶段", "CP_hvChargeStatus_log → ENABLED"),
        ("R06", "140.0299", "FC直流电压建立", "FC_dcVoltage 0→346.88 V"),
        ("R07", "145.0303", "FC直流电流建立", "FC_dcCurrent 0→54.49 A并继续爬升"),
        ("R08", "245.8359", "快充状态退出", "FC_statusCode → 0"),
        ("R09", "246.2327", "高压充电阶段退出", "CP_hvChargeStatus_log ENABLED→CONNECTED"),
        ("R10", "246.2355", "FC电压电流归零", "FC_dcVoltage/current → 0"),
        ("R11", "246.5176", "快充接触器打开请求", "BMS_fcContactorRequest CLOSE→OPEN"),
        ("R12", "246.8477", "快充接触器辅助反馈打开", "正/负AuxOpen 0→1；DC允许回NONE"),
    ]
    write_csv(OUT / "multi_dbc_events.csv", [dict(event_id=a,time_s=b,event=c,basis=d) for a,b,c,d in events])

    timeline = ["# TM3-015 多DBC回归时间线", "",
                "以下为既有时间线的补充视图，不以外部扫码/支付事件替代车辆内部节点。", "",
                "| 事件 | 时间(s) | 候选状态/动作 | 数据判据 |", "| --- | ---: | --- | --- |",
                *[f"| {a} | {b} | {c} | {d} |" for a,b,c,d in events], "",
                "主链补充解释：`DC链路允许上电候选 → 快充接触器闭合请求 → 辅助触点闭合反馈 → 高压充电ENABLED候选 → 直流电压建立 → 直流电流建立`。",
                "停止侧顺序为：`状态退出/电流归零 → 接触器打开请求 → 辅助触点打开反馈`。该顺序只对TM3-015成立。"]
    (OUT / "采集时间线与关键Signal_多DBC回归.md").write_text("\n".join(timeline)+"\n", encoding="utf-8")

    report = """# TM3-015 直流快充基线分析报告（多DBC回归版）

## 回归结论

多DBC联合解析增强了TM3-015车辆内部高压充电状态链的可观测性。除原来已经成立的“直流电流建立—短稳态—停止退出”外，本次能够在实验范围内补充“DC链路允许上电候选—快充接触器闭合请求—辅助触点闭合反馈—高压充电阶段ENABLED—电压建立—电流建立”的顺序证据。

原结论中“许可只能由下游电流间接证明”应修订为：本次已经获得许可/安全条件至高压执行之间的**部分直接候选证据**，但仍不能确认OEM完整充电许可规则、控制器内部判断条件或所有Signal的车型级永久语义。

## 关键事实与控制关系

- `HVP_fcLinkAllowedToEnergize`在115.8453s由NONE进入DC；这是快充链路允许上电类型候选，不等于平台扫码或支付接受。
- `BMS_fcContactorRequest`在134.5149s由OPEN进入CLOSE；正、负快充接触器辅助开路位在134.8465s由1变0，形成请求—反馈候选对应。
- `CP_hvChargeStatus_log`依次经历CONNECTED、STANDBY、EVSE_TEST_ACTIVE、TEST_PASSED和ENABLED，并在139.5253s进入ENABLED。
- `FC_dcVoltage`在140.0299s建立；`FC_dcCurrent`在145.0303s建立。二者在246.2355s同时归零。
- 停止后，快充接触器请求在246.5176s转OPEN，辅助触点在246.8477s反馈打开，DC链路允许状态同时回NONE。
- `TotalChargeKWh3D2`在电流建立后由14620.356增加至14622.296 kWh，停止后不再增加，可作为独立能源方向交叉验证。

## 仍未解决的证据冲突

`FC_dcCurrent`稳定段约218.55A，而既有`BMS_packCurrent`约193.88A、`CP_evseOutputDcCurrent`约128.11A。三套定义的建立和退出时序一致，但幅值不闭合，因此不能据此计算充电功率、效率或确认哪一套缩放是车型正确值。`0x27D/0x2BD`桩能力限值继续保持工程审计EXCLUDE。

Pack最低温度、部分针脚温度和热管理替代定义仍出现SNA、复用页混杂或不合理范围。多DBC回归没有形成可靠的Pack热状态—请求—执行—温度响应闭环。

## 基线结论与边界

本次可保存的基线范围扩大为：高压充电阶段候选状态、快充接触器请求—辅助反馈顺序、直流电压/电流建立与退出、59.5s短稳态、SOC及累计充电量方向。完整协商、OEM许可逻辑、定量功率和热管理闭环仍为证据不足。

本回归不覆盖原始Approved Plan和原报告；补充Signal均标记`THIS_EXPERIMENT_ONLY`。其他DBC中的位段可解不等于车型语义已确认，后续跨实验复现后才能考虑车型级候选知识。
"""
    (OUT / "TM3-015_最终报告_多DBC回归.md").write_text(report, encoding="utf-8")

    diff = """# TM3-015 原版与多DBC回归版差异

| 项目 | 原版 | 多DBC回归版 |
| --- | --- | --- |
| 车辆内部许可/高压链 | 主要依靠下游电流间接证明 | 获得DC允许、接触器请求、辅助反馈及高压阶段日志的部分直接候选证据 |
| ER-03 | INSUFFICIENT_EVIDENCE | SUPPORTED（实验候选边界） |
| 直流建立/退出 | 单一CP定义与Pack交叉 | 新增FC定义及接触器链交叉，时序置信度提高 |
| 定量功率 | 不成立 | 仍不成立；新增FC电流后出现第三套幅值 |
| 热管理闭环 | 不足 | 不变 |
| 是否需要整体重采 | 否 | 否 |
"""
    (OUT / "regression_diff.md").write_text(diff, encoding="utf-8")
    manifest = {
        "experiment_id": "TM3-015", "regression": "MULTI_DBC_V1",
        "scope": "THIS_EXPERIMENT_ONLY", "original_files_overwritten": False,
        "approved_plan_sha256": sha(approved_path),
        "multi_dbc_decode_summary_sha256": sha(SOURCE / "all_relevant_decode_summary.csv"),
        "effective_plan_sha256": sha(OUT / "evidence_plan_effective_multi_dbc.csv"),
        "assessment_sha256": sha(OUT / "evidence_assessment_multi_dbc.csv"),
        "result": "PASS_WITH_EXPECTED_CONCLUSION_UPDATE",
    }
    (OUT / "regression_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
