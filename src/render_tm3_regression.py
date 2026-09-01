"""Freeze/migrate TM3-009 and TM3-010 through the minimal approved-plan renderer."""
from __future__ import annotations

import csv
from pathlib import Path

from evidence_plan import (DraftSignalEvidence, EvidenceAssessment, ReviewOverride, approve_plan,
                           write_approved_csv, write_draft_csv, write_review_csv)
from report_renderer import (ControlNodeView, ControlRelationshipView, CoreSignal,
                             ExperimentReport, Table, TimelineEvent, render_report_bundle)

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _draft(exp: str, coverage: list[dict[str, str]]) -> list[DraftSignalEvidence]:
    config = {
        "DI_accelPedalPos": ("驾驶输入", "P0", "CORE_TIMELINE+CORE_SIGNAL_TABLE", 10, "已确认", "HIGH", ""),
        "DI_gear": ("状态门", "P2", "CONDITION_SUMMARY+CORE_SIGNAL_TABLE", 20, "已确认", "HIGH", ""),
        "DI_systemState": ("状态门", "P2", "CONDITION_SUMMARY+CORE_SIGNAL_TABLE", 30, "已确认", "HIGH", ""),
        "DI_tractionControlMode": ("状态门", "P2", "CONDITION_SUMMARY+CORE_SIGNAL_TABLE", 40, "强候选", "MEDIUM", "STATE_APPLICABILITY_UNCERTAIN"),
        "DI_torqueCommand": ("仲裁后请求", "P0", "CORE_TIMELINE+CORE_SIGNAL_TABLE", 50, "已确认", "HIGH", ""),
        "DI_torqueActual": ("执行反馈", "P0", "CORE_TIMELINE+CORE_SIGNAL_TABLE", 60, "已确认", "HIGH", ""),
        "DI_axleSpeed": ("运动反馈", "P0", "CORE_TIMELINE+CORE_SIGNAL_TABLE", 70, "已确认", "MEDIUM", "REPORT_POSITION_AMBIGUOUS"),
        "DI_vehicleSpeed": ("物理结果", "P0", "CORE_TIMELINE+CORE_SIGNAL_TABLE", 80, "已确认", "HIGH", ""),
        "DI_elecPower": ("能源交叉验证", "P1", "CORE_TIMELINE+CORE_SIGNAL_TABLE", 90, "强候选", "MEDIUM", "DBC_VERSION_CONFLICT+CROSS_MAINLINE_EVIDENCE"),
        "BMS_packVoltage": ("能源交叉验证", "P1", "CORE_TIMELINE+CORE_SIGNAL_TABLE", 100, "已确认", "MEDIUM", "REPORT_POSITION_AMBIGUOUS"),
        "BMS_packCurrent": ("能源交叉验证", "P1", "CORE_TIMELINE+CORE_SIGNAL_TABLE", 110, "已确认", "HIGH", "CROSS_MAINLINE_EVIDENCE"),
        "BMS_socUI": ("状态条件", "P2", "CONDITION_SUMMARY+CORE_SIGNAL_TABLE", 120, "已确认", "HIGH", ""),
        "DI_sysDrivePowerMax": ("能力背景", "P2", "CAPABILITY_SUMMARY+CORE_SIGNAL_TABLE", 130, "强候选", "MEDIUM", "PROXY_OBSERVATION"),
        "DI_sysRegenPowerMax": ("能力背景", "P2", "CAPABILITY_SUMMARY+CORE_SIGNAL_TABLE", 140, "强候选", "MEDIUM", "PROXY_OBSERVATION"),
    }
    by_signal = {row["signal"]: row for row in coverage}
    result = []
    for signal, values in config.items():
        role, priority, position, order, semantic, confidence, flags = values
        source = by_signal[signal]
        result.append(DraftSignalEvidence(
            exp, signal, signal, source["message"], source["can_id"], source["unit"],
            "建立稳定匀速的输入—请求—执行—运动主线及能源/条件证据",
            role, priority, position, order,
            "由本次稳定匀速命题、车辆电驱边界、控制链和能源交叉验证线推导",
            semantic, confidence, flags, "YES" if flags else "NO"))
    result.append(DraftSignalEvidence(
        exp, "PackPower_derived", "Pack功率(同帧V×I派生)", "BMS_hvBusStatus", "0x132", "kW",
        "以Pack侧功率交叉验证电驱能源响应", "能源交叉验证", "P1",
        "CORE_TIMELINE+ANALYSIS_WINDOW", 115, "由同一0x132帧的电压和电流计算，不是DBC原生Signal",
        "已确认", "HIGH", "", "NO"))
    return result


def tm3_010_plan(out: Path):
    coverage = read_csv(out / "baseline_evidence/signal_coverage.csv")
    draft = _draft("TM3-010", coverage)
    reviews = [
        ReviewOverride("TM3-010", "DI_tractionControlMode", "ACCEPT", human_reason="保留为状态门背景。", reviewer="人工模拟审核", reviewed_at="2026-09-01"),
        ReviewOverride("TM3-010", "DI_axleSpeed", "OVERRIDE", override_priority="P1", override_report_position="ANALYSIS_WINDOW+CORE_SIGNAL_TABLE", human_reason="轴速用于窗口统计与运动交叉验证，不占用固定人读主时间线列。", reviewer="人工模拟审核", reviewed_at="2026-09-01"),
        ReviewOverride("TM3-010", "DI_elecPower", "ACCEPT", human_reason="保留为能源交叉验证主观测。", reviewer="人工模拟审核", reviewed_at="2026-09-01"),
        ReviewOverride("TM3-010", "BMS_packVoltage", "OVERRIDE", override_priority="P2", override_report_position="ANALYSIS_WINDOW+CORE_SIGNAL_TABLE", human_reason="电压进入稳定窗口统计，不单占主时间线列。", reviewer="人工模拟审核", reviewed_at="2026-09-01"),
        ReviewOverride("TM3-010", "BMS_packCurrent", "ACCEPT", human_reason="Pack电流保留在核心时间线和能源基线。", reviewer="人工模拟审核", reviewed_at="2026-09-01"),
        ReviewOverride("TM3-010", "DI_sysDrivePowerMax", "ACCEPT", human_reason="作为能力背景，不提升为主链。", reviewer="人工模拟审核", reviewed_at="2026-09-01"),
        ReviewOverride("TM3-010", "DI_sysRegenPowerMax", "ACCEPT", human_reason="作为能力背景，不提升为主链。", reviewer="人工模拟审核", reviewed_at="2026-09-01"),
    ]
    plan = approve_plan(draft, reviews)
    write_draft_csv(out / "evidence_plan_draft.csv", draft)
    write_review_csv(out / "evidence_plan_review_overrides.csv", reviews)
    write_approved_csv(out / "evidence_plan_approved.csv", plan)
    context = """# TM3-010 Evidence Plan Context

- 用途：正常基线采集；实验身份由metadata确定为`TM3-010=稳定匀速`，ASC文件编号误写仅作来源记录。
- 实验目的：建立约20 km/h和约40 km/h稳定匀速条件化基线。
- 系统边界：车辆电驱控制系统；20/40 km/h是驾驶员/实验目标，不是电驱控制器内部车速目标。
- 主验证线：外部驾驶输入→仲裁后扭矩请求→实际扭矩→车辆运动。
- 交叉验证线：电驱功率↔Pack电流/同帧V×I功率；挡位、系统状态、SOC、驱动/回收能力为条件背景。
- 本文件与审核结果仅对本实验有效，不写回车型知识。
"""
    (out / "evidence_plan_context.md").write_text(context, encoding="utf-8")
    rows = []
    for x in draft:
        rows.append((x.signal, x.suggested_role, x.suggested_priority, x.suggested_report_position,
                     x.derivation_reason, x.semantic_status, x.confidence,
                     "需要：" + x.uncertainty_flags if x.review_required == "YES" else "无需"))
    from report_renderer import _table
    md = "# TM3-010 待审Signal证据表\n\n" + _table(
        ("Signal", "本实验角色", "建议优先级", "建议报告位置", "推导理由", "语义状态", "判断置信度", "人工审核"), rows) + "\n"
    (out / "待审Signal证据表.md").write_text(md, encoding="utf-8")
    return plan


TM3_010_PURPOSES = {
    "DI_accelPedalPos": "识别驾驶输入及匀速调节。",
    "DI_gear": "确认实验处于D挡驱动状态。",
    "DI_systemState": "确认驱动系统处于实验适用状态。",
    "DI_tractionControlMode": "观察牵引控制状态，避免把特殊介入误作正常稳态。",
    "DI_torqueCommand": "观察仲裁后的电驱扭矩请求。",
    "DI_torqueActual": "与同帧请求比较，验证执行跟随。",
    "DI_axleSpeed": "提供动力侧运动反馈，并与扭矩同帧对应。",
    "DI_vehicleSpeed": "识别目标速度带、连续稳定窗口及速度波动。",
    "DI_elecPower": "提供电驱能源侧响应。",
    "BMS_packVoltage": "记录高压背景，并与Pack电流同帧派生Pack功率。",
    "BMS_packCurrent": "观察Pack充放电方向和幅度，并参与同帧Pack功率计算。",
    "BMS_socUI": "记录当前实验SOC适用条件。",
    "DI_sysDrivePowerMax": "作为驱动能力背景观察，不直接解释为本次实际限制阈值。",
    "DI_sysRegenPowerMax": "作为回收能力背景观察，不直接解释为本次实际限制阈值。",
}


def _core_signals(plan, coverage, purposes=None):
    source = {row["signal"]: row for row in coverage}
    items = []
    for approved in plan.signals:
        if not approved.has_position("CORE_SIGNAL_TABLE"):
            continue
        row = source[approved.signal_key]
        low = row.get("observed_min") or row.get("valid_range") or "—"
        high = row.get("observed_max") or ""
        observed = f"{low}～{high}" if high else low
        decoded = row.get("decoded_samples") or row.get("decoded") or "0"
        errors = row.get("decode_errors") or row.get("invalid") or "0"
        status = "可读" if int(float(decoded or 0)) > 0 else "不可读/无帧"
        if int(float(errors or 0)) > 0:
            status += "（含INVALID/错误）"
        purpose = (purposes or {}).get(approved.signal_key) or row.get("purpose") or approved.evidence_requirement
        items.append(CoreSignal(approved.signal_key, observed, row.get("changed", "—"), status, purpose))
    return tuple(items)


TM3_010_TIMELINE = (
    (0.15,"P/STANDBY，采集开始","0","0","0","0","0","1.3","0.452","初始静止"),
    (20,"P/STANDBY，静置","0","0","0","0","0","1.1","0.382","保持静止"),
    (30,"D/ENABLE，开始加速","8","682","708","3.12","3","9.5","3.296","进入20 km/h调速"),
    (45,"D/ENABLE，进入计划20段","8","-86","-90","20.64","-1.5","-3","-1.043","仍在驾驶调节"),
    (56.276,"D/ENABLE，20 km/h基线窗口开始","12.4","178","178","19.04","3","10.4","3.602","19～21 km/h连续段起点"),
    (65.636,"D/ENABLE，20 km/h代表状态","12.4","92","92","20.88","1.5","6","2.080","短时条件化基线代表点"),
    (74.995,"D/ENABLE，20 km/h基线窗口结束","0","-22","-12","20.48","-0.5","0.9","0.313","连续稳定样本18.72 s"),
    (100,"P/STANDBY，停车间隔","0","0","0","0","0","1.9","0.660","两段之间静止"),
    (125,"D/ENABLE，开始加速","10.4","790","816","4.32","4","13.7","4.745","进入40 km/h调速"),
    (145,"D/ENABLE，进入计划40段","12","-178","-178","38.56","-5.5","-14.7","-5.110","到达目标附近但未稳定"),
    (150,"D/ENABLE，速度回落","19.2","100","100","33.68","3","10","3.464","明显调速"),
    (158.149,"D/ENABLE，进入38～42带","22.8","328","328","38","10.5","33.1","11.407","最长带内连续段开始"),
    (161.469,"D/ENABLE，离开38～42带","20.8","220","208","42","8","25.2","8.688","仅连续3.32 s"),
    (165,"D/ENABLE，速度超调","16.8","-8","-8","42.96","-0.5","0.9","0.312","超过识别带"),
    (170,"D/ENABLE，速度再次回落","12","-172","-172","37.68","-5.5","-13.9","-4.840","未形成稳态"),
    (175,"D/ENABLE，计划40段结束","0","-596","-606","29.12","-14","-38.1","-13.334","30 s计划段范围29.12～43.44"),
    (220.902,"P/STANDBY，采集结束","0","0","0","0","0","1.2","0.416","结束"),
)


def tm3_010_report(plan, out):
    cov = read_csv(out / "baseline_evidence/signal_coverage.csv")
    timeline = tuple(TimelineEvent(*row) for row in TM3_010_TIMELINE)
    stats = Table("稳定性及控制/动力/能源统计",
        ("分析窗口","时间(s)","持续(s)","车速均值±SD(km/h)","请求/实际MAE(Nm)","电驱平均功率(kW)","Pack平均电压(V)","Pack平均电流(A)","Pack平均功率(kW)","基线判断"),
        (("20 km/h带内最长连续段","56.2764～74.9953","18.72","20.60±0.45","0.30","1.70","346.78","6.50","2.25","有效短时条件化基线"),
         ("40 km/h计划段","145～175","30.00","37.18±3.71","1.23","0.81","346.61","4.35","1.48","范围29.12～43.44，不满足稳态"),
         ("40 km/h带内最长连续段","158.1487～161.4694","3.32","40.16±1.18","0.76","9.72","344.59","30.67","10.57","过短，不建立稳态基线")))
    report = ExperimentReport("TM3-010", "TM3-010 稳定匀速：车型基线分析",
        ("用途：正常实车基线采集。", "车辆：上海产2021款Model 3，标准续航55 kWh、后驱。", "实验身份由metadata确定；原始ASC编号误写仅作来源记录。"),
        ("20 km/h识别带最长连续段56.2764～74.9953 s，共18.72 s，平均20.60 km/h、标准差0.45 km/h。", "该段请求/实际扭矩同帧MAE 0.30 Nm；电驱平均功率1.70 kW，Pack同帧V×I平均功率2.25 kW。", "40 km/h计划段145～175 s车速29.12～43.44 km/h、标准差3.71 km/h；38～42 km/h最长连续段仅3.32 s。"),
        ControlRelationshipView((
            ControlNodeView("驾驶输入", "直接观测"),
            ControlNodeView("状态/条件/能力判断", "部分可观测"),
            ControlNodeView("仲裁/决策", "本次无直接观测"),
            ControlNodeView("仲裁后扭矩请求", "直接观测"),
            ControlNodeView("执行反馈", "直接观测"),
            ControlNodeView("车辆运动", "直接观测"),
        ), "实际扭矩 → 轴速/车速。", "电驱功率 ↔ Pack电流/电压/同帧V×I功率。",
        ("20/40 km/h是驾驶员实验目标，不是电驱控制器内部车速目标。",)),
        ("20 km/h短时条件化基线有效。", "40 km/h未满足稳态条件，仅保留为调速过程证据，不建立稳态基线。"),
        ("识别带不是厂家稳态阈值；道路坡度、风况、轮胎及热状态未完整记录。", "段内仍有驾驶调节和短暂负请求，不等同严格恒负载稳态。"),
        ("20 km/h工况无需重采。", "仅补采40 km/h稳定段，无需重复20 km/h实验。", "补采以实际车速进入并稳定在目标带为起点，连续保持20～30 s，并记录SOC、道路坡度/方向和空调状态。", "当前无需进入故障诊断树；先完成缺失的40 km/h正常基线。"),
        ("DI_accelPedalPos","DI_torqueCommand","DI_torqueActual","DI_vehicleSpeed","DI_elecPower","BMS_packCurrent","PackPower_derived"), timeline, (stats,), _core_signals(plan, cov, TM3_010_PURPOSES),
        ("DBC版本差异、INVALID与字段长度细节见baseline_evidence CSV。",),
        ("原始ASC：input/can_20260831085710_TM3-009_稳定匀速采集.asc（文件编号误写）。", "ASC SHA-256：d3ab95e0036602901412f0c7bd66bda627cac9cc286cb0e8b4c391fcac6b4b16。", "分析窗口与关键数值沿用已验收TM3-010结果，未重新识别。", "事件和逐Signal采样：baseline_evidence/events.csv、event_signal_samples.csv。"),
        assessments=(EvidenceAssessment("20_KMH_CONDITIONAL_BASELINE", "SUPPORTED", "18.72 s连续稳定样本满足本次短时条件化基线判据。"), EvidenceAssessment("40_KMH_STEADY_BASELINE", "INSUFFICIENT_EVIDENCE", "38～42 km/h最长连续段仅3.32 s。", "仅保留调速轨迹，需局部补采。")))
    render_report_bundle(plan, report, out)


def tm3_009_plan(out):
    cov = read_csv(out / "baseline_evidence/signal_coverage.csv")
    base = _draft("TM3-009", [x for x in cov if x["signal"] in {"DI_accelPedalPos","DI_gear","DI_systemState","DI_tractionControlMode","DI_torqueCommand","DI_torqueActual","DI_axleSpeed","DI_vehicleSpeed","DI_elecPower","BMS_packVoltage","BMS_packCurrent","BMS_socUI","DI_sysDrivePowerMax","DI_sysRegenPowerMax"}])
    # 009 is a frozen migration sample: remove uncertainty by explicit experiment-local acceptance.
    reviews = [ReviewOverride("TM3-009", x.signal_key, "ACCEPT", human_reason="沿用TM3-009已验收Signal角色。", reviewer="冻结样本迁移", reviewed_at="2026-09-01") for x in base if x.review_required == "YES"]
    plan = approve_plan(base, reviews)
    write_approved_csv(out / "evidence_plan_approved.csv", plan)
    return plan


def tm3_009_report(plan, out):
    cov = read_csv(out / "baseline_evidence/signal_coverage.csv")
    events = read_csv(out / "baseline_evidence/events.csv")
    samples = read_csv(out / "baseline_evidence/event_signal_samples.csv")
    grouped = {}
    for row in samples:
        grouped.setdefault(row["event_id"], {})[row["signal"]] = row["value"]
    timeline = []
    for event in events:
        values = grouped.get(event["event_id"], {})
        def v(name): return values.get(name, "—")
        def vn(name):
            raw = v(name)
            try:
                return f"{float(raw):.3f}".rstrip("0").rstrip(".")
            except (ValueError, TypeError):
                return raw
        gear = v("DI_gear"); state = v("DI_systemState")
        action = f"{gear}/{state}，{event['event']}" if gear != "—" else event["event"]
        try: pack = f"{float(v('BMS_packVoltage')) * float(v('BMS_packCurrent')) / 1000:.3f}"
        except (ValueError, TypeError): pack = "—"
        timeline.append(TimelineEvent(float(event["time_s"]), action, vn("DI_accelPedalPos"),
            vn("DI_torqueCommand"), vn("DI_torqueActual"), vn("DI_vehicleSpeed"), vn("DI_elecPower"),
            vn("BMS_packCurrent"), pack, event["criterion"]))
    stats = Table("两次实际加速窗口统计",
        ("窗口","时间(s)","电门峰值(%)","请求/实际峰值(Nm)","请求/实际MAE(Nm)","电驱功率峰值(kW)","Pack电流峰值(A)"),
        (("第一次加速","27.4225～44.9230","25.6","684 / 710","2.34","13.5","41.0"),
         ("第二次加速","102.0783～120.1169","21.2","554 / 558","2.58","9.0","28.1")))
    report = ExperimentReport("TM3-009", "TM3-009 中等负载加速：车型基线分析",
        ("用途：正常实车基线采集。", "车辆：上海产2021款Model 3，标准续航55 kWh、后驱。"),
        ("两次加速均观察到电门增加、请求扭矩上升、实际扭矩跟随，车辆速度及电池输出相应增加。", "两实际加速窗口请求/实际扭矩MAE分别为2.34/2.58 Nm。", "第一次输入、电驱功率和Pack放电峰值均高于第二次，变化方向一致。"),
        ControlRelationshipView((
            ControlNodeView("驾驶输入", "直接观测"),
            ControlNodeView("状态/条件/能力判断", "部分可观测"),
            ControlNodeView("仲裁/决策", "本次无直接观测"),
            ControlNodeView("仲裁后扭矩请求", "直接观测"),
            ControlNodeView("执行反馈", "直接观测"),
            ControlNodeView("车辆运动", "直接观测"),
        ), "实际扭矩 → 轴速/车速。", "电驱功率上升 ↔ Pack放电上升。",
        ("能源证据独立交叉验证，不串接成车辆运动后的单一因果链。",)),
        ("本次加速范围内，后电驱请求—执行、运动及能源响应符合预期，可作为车型动态基线证据。", "低速补踩制动是独立控制工况，不并入加速跟随统计。"),
        ("各峰值不要求同刻，不用峰值比值推算效率。", "未测得轮端摩擦制动力，不把制动力分配策略写成已确认。"),
        ("两组中等负载加速动态基线有效，无需为本实验整体重采。", "如继续验证制动交互，仅补采带轮端/制动执行量的低速专项，不重复两次加速。", "当前作为正常基线保留，不进入故障原因确认。"),
        ("DI_accelPedalPos","DI_torqueCommand","DI_torqueActual","DI_vehicleSpeed","DI_elecPower","BMS_packCurrent","PackPower_derived"), tuple(timeline), (stats,), _core_signals(plan, cov),
        ("制动DBC版本差异、缺帧和不可读项保留在工程审计。",),
        ("原始ASC：input/can_20260831090233_TM3-010_中等负载加速采集.asc。", "ASC SHA-256：c9f378fa919ead3fb7464395d1b33b92c97a1ffca156371191bfc4545bf3b4e6。", "分析窗口、关键数值及低速制动判断沿用已验收TM3-009结果。", "完整E事件编号和原始采样继续保留于baseline_evidence CSV。"),
        assessments=(EvidenceAssessment("ACCELERATION_REQUEST_ACTUAL_RESPONSE", "SUPPORTED", "两次窗口请求—实际跟随及运动、能源响应支持动态基线。"), EvidenceAssessment("BRAKE_FORCE_ALLOCATION", "INSUFFICIENT_EVIDENCE", "低速制动交互已观察，但缺少轮端摩擦制动力。")))
    render_report_bundle(plan, report, out)


def main():
    out10 = ROOT / "output/TM3-010"
    plan10 = tm3_010_plan(out10)
    tm3_010_report(plan10, out10)
    out09 = ROOT / "output/TM3-009/report_v1"
    plan09 = tm3_009_plan(out09)
    tm3_009_report(plan09, out09)


if __name__ == "__main__":
    main()
