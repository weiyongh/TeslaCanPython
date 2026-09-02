"""Render TM3-015 evidence assessment after the approved coverage gate."""
from __future__ import annotations

import csv
import hashlib
import json
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/TM3-015"
ASC = ROOT / "input/can_20260831102614_TM3-015_直流快充采集.asc"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def table(headers, rows):
    return "\n".join([
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
        *("| " + " | ".join(map(str, row)) + " |" for row in rows),
    ])


def main():
    coverage = list(csv.DictReader((OUT / "dbc_coverage_gate.csv").open(encoding="utf-8-sig")))
    samples = defaultdict(list)
    with (OUT / "decoded_native_samples.csv").open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            try: value = float(row["value"])
            except ValueError: value = row["value"]
            samples[row["signal_key"]].append((float(row["time_s"]), value))

    def after(key, start, pred):
        return next((t for t, v in samples[key] if t >= start and pred(v)), None)

    def stats(key, start, end, transform=lambda x: x):
        vals = [transform(v) for t, v in samples[key] if start <= t <= end and isinstance(v, (int, float))]
        return dict(n=len(vals), min=min(vals), mean=statistics.fmean(vals), max=max(vals))

    t_charge_ui = after("BMS_uiChargeStatus", 60, lambda v: v == 3)
    t_contactor_close = after("BMS_contactorState", 130, lambda v: v == 4)
    t_voltage = after("CP_evseOutputDcVoltage", 100, lambda v: v > 10)
    t_cp_current = after("CP_evseOutputDcCurrent", 100, lambda v: v > 1)
    t_stop_candidate = after("CP_stopChargeRequest", 240, lambda v: v == 1)
    t_cp_zero = after("CP_evseOutputDcCurrent", t_stop_candidate, lambda v: v == 0)
    t_ui_exit = after("BMS_uiChargeStatus", 240, lambda v: v != 3)
    t_type_exit = after("CP_evseChargeType", 240, lambda v: v == 0)

    stable = (173.73, 233.23)
    cp_i = stats("CP_evseOutputDcCurrent", *stable)
    cp_v = stats("CP_evseOutputDcVoltage", *stable)
    pack_i = stats("BMS_packCurrent", *stable, transform=lambda x: -x)  # human: into Pack positive
    pack_v = stats("BMS_packVoltage", *stable)
    soc = stats("BMS_socUI", *stable)
    model_tmax = stats("BMS_modelTMax", *stable)
    cp_power = cp_v["mean"] * cp_i["mean"] / 1000
    pack_power = pack_v["mean"] * pack_i["mean"] / 1000

    events = [
        ("E00", 0.0, "采集开始/充前背景", "脚本零点；CP输出电压电流均为0"),
        ("E01", 20.7178, "充电口动作窗口", "锁止候选先变化；DoorOpen候选仅短脉冲，语义未通过"),
        ("E02", 39.7192, "插枪/连接识别窗口", "EVSE类型候选0→1；线缆Present/Secured方向与名称冲突"),
        ("E03", t_charge_ui, "车辆充电状态建立", "BMS_uiChargeStatus 2→3；尚未建立直流电流"),
        ("E04", t_contactor_close, "接触器重新闭合", "BMS_contactorState回到4；仅作为部分高压证据"),
        ("E05", t_voltage, "CP侧候选直流电压建立", "电压先建立，不能定义实际充电开始"),
        ("E06", t_cp_current, "直流电流开始建立", "CP电流首次>1 A；Pack原始电流同步转为充电方向"),
        ("E07", stable[0], "短稳态窗口开始", "数据状态稳定后选取，不采用脚本预定时间"),
        ("E08", t_stop_candidate, "停止候选事件", "CP_stopChargeRequest出现；缺少独立实际停止触发记录"),
        ("E09", t_cp_zero, "CP直流输出退出", f"停止候选后约{t_cp_zero-t_stop_candidate:.3f}s降为0"),
        ("E10", t_ui_exit, "车辆充电状态退出", "BMS_uiChargeStatus 3→2"),
        ("E11", t_type_exit, "连接类型退出窗口", "EVSE类型候选1→0；实际解锁/拔枪时刻无独立记录"),
    ]
    with (OUT / "events.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w=csv.writer(f); w.writerow(["event_id","time_s","event","basis"]); w.writerows(events)

    assessments = [
        ("ER-01","INSUFFICIENT_EVIDENCE","开口/插枪附近有位变化，但DoorOpen为短脉冲，CablePresent/Secured方向与名称冲突","SEMANTIC_VALIDATION_FAILED；保留原始边沿，不确认字段名称语义"),
        ("ER-02","INSUFFICIENT_EVIDENCE","EVSE类型候选在插枪窗0→1，但数字通信、Request、Accept、gbState全程0","未观察到足以还原协商顺序的车辆内部Signal"),
        ("ER-03","INSUFFICIENT_EVIDENCE","UI充电状态及接触器转换可见，后续确有电流；但0x13D无帧、BMS_chargeRequest恒0、BMS_hvState轮转异常","只能由下游结果间接支持许可已形成，不能确认条件判断/许可节点"),
        ("ER-04","SUPPORTED","CP候选电压约140.028s建立、电流145.028s建立；Pack电流同步进入充电方向","方向和时序成立；CP/Pack缩放定量不一致，不形成准确功率或效率结论"),
        ("ER-05","SUPPORTED",f"173.73–233.23s取得59.50s短稳态；CP候选电流{cp_i['mean']:.3f}A，SOC {soc['min']:.1f}%→{soc['max']:.1f}%","条件化短稳态有效；不代表峰值、全SOC曲线或长期能力"),
        ("ER-06","SUPPORTED",f"停止候选{t_stop_candidate:.4f}s后，CP电流{t_cp_zero:.4f}s归0，UI状态{t_ui_exit:.4f}s退出","两个停止Signal语义仍未完全确认；结论依赖状态和电流退出闭环"),
        ("ER-07","INSUFFICIENT_EVIDENCE","连接类型约273.534s退出，锁止/门候选随后变化","无独立解锁和拔枪实际时刻，且Cable/Latch语义未通过"),
        ("ER-08","SUPPORTED",f"SOC、低压及部分热状态有覆盖；SOC由27.5%升至31.0%","多个温度/能力字段语义失败，不能把所有解码值当有效条件"),
        ("ER-09","INSUFFICIENT_EVIDENCE","DI_gear仅解码为7=SNA；DI_systemState在电流阶段为1=IDLE","只记录状态共存；挡位条件本次无有效DBC证据"),
        ("ER-10","INSUFFICIENT_EVIDENCE","BMS_modelTMax 33.5→35.0°C候选可读；多项温度目标/执行字段存在SNA、越界、无帧或不合理突变","热管理执行器覆盖得到验证，但请求—执行—温度闭环尚不足；SEMANTIC_VALIDATION_FAILED项不得解释"),
    ]
    with (OUT / "evidence_assessment.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w=csv.writer(f); w.writerow(["requirement_id","status","evidence_summary","limitation"]); w.writerows(assessments)

    failed = [r for r in coverage if r["readability"] in {"NO_FRAME","MUX_NOT_OBSERVED_OR_UNREADABLE"}]
    dbc_md = [
        "# TM3-015 DBC关键Signal覆盖与可读性", "",
        f"- ASC：`{ASC.relative_to(ROOT)}`；SHA-256 `{sha(ASC)}`。",
        "- 主DBC：`input/tesla_model3_ONYX.dbc`；Approved范围：`THIS_EXPERIMENT_ONLY`。",
        "- 技术可解码不等于语义成立；完整逐Signal数据见`dbc_coverage_gate.csv`。", "",
        "## 覆盖门失败项", "",
        table(["Signal","CAN ID","结果","Assessment"], [(r["signal"],r["can_id"],r["readability"],"INSUFFICIENT_EVIDENCE / SEMANTIC_VALIDATION_FAILED") for r in failed]), "",
        "## 关键语义验证结果", "",
        table(["Signal组","结果","边界"], [
            ("CP_chargeCablePresent / Secured / DoorOpen","未通过名称语义验证","开口/插枪边沿方向与名称不一致"),
            ("CP_digitalCommsEstablished / evseRequest / evseAccept / gbState","未观察到变化","不能证明内部协商顺序"),
            ("BMS_hvState","未通过当前DBC适配","出现不合理快速枚举轮转"),
            ("CP_evseOutputDcCurrent / Voltage","时序可用；缩放待验证","能定位建立/退出；不能确认准确功率"),
            ("BMS_packCurrent / Voltage","方向/时序可用；定量冲突","人读充入为正；原始负号和换算保留审计"),
            ("BMS_modelTMax","候选可用","33.5→35.0°C；仍保持候选"),
            ("BMS_modelTMin / minPackTemperature / CP针脚温度","未通过","SNA/不合理范围，不进入温度结论"),
            ("热管理泵/阀/Chiller/压缩机/模式","部分技术可读","不据名称形成请求—执行结论"),
        ]), "",
        "## Approved关键Signal逐项覆盖", "",
        table(["角色","Signal","中文语义","CAN ID","DBC/需要/ASC DLC","解码/帧","可读性"], [
            (r["role"],r["signal"],r["chinese_semantic"],r["can_id"],
             f"{r['dbc_dlc'] or '-'}/{r['signal_required_dlc'] or '-'}/{r['asc_dlc'] or '-'}",
             f"{r['decoded_count']}/{r['frame_count']}",r["readability"])
            for r in coverage
        ]), "",
        "## DBC冲突排除", "",
        "`0x27D`在ONYX中为`APS_eacMonitor`，替代DBC中却是`CP_dcChargeLimits`；`0x2BD`仅替代DBC定义。三项能力字段继续仅作版本适配审计，不进入结论。",
    ]
    (OUT / "DBC关键Signal覆盖与可读性.md").write_text("\n".join(dbc_md)+"\n", encoding="utf-8")

    timeline_md = [
        "# TM3-015 采集时间线与关键Signal", "",
        "时间均为ASC相对秒。未取得独立实际事件表/触发CSV，脚本名义时间只用于定位；下表是数据识别时刻，不能当作扫码平台的内部响应延迟。", "",
        table(["事件","ASC时间(s)","状态/动作","数据判据"], [(e,f"{t:.4f}",name,basis) for e,t,name,basis in events]), "",
        "## 短稳态（173.73–233.23s）", "",
        table(["量","范围/均值","结论边界"], [
            ("CP输出电流候选",f"{cp_i['min']:.3f}–{cp_i['max']:.3f} A；均值{cp_i['mean']:.3f} A","时序稳定，缩放待验证"),
            ("CP输出电压候选",f"{cp_v['min']:.3f}–{cp_v['max']:.3f} V；均值{cp_v['mean']:.3f} V","不能单独定义充电开始"),
            ("CP派生功率",f"约{cp_power:.2f} kW","仅候选定义派生"),
            ("Pack电流（人读充入为正）",f"{pack_i['min']:.1f}–{pack_i['max']:.1f} A；均值{pack_i['mean']:.2f} A","原始DBC为负；定量与CP不一致"),
            ("Pack电压",f"{pack_v['min']:.2f}–{pack_v['max']:.2f} V；均值{pack_v['mean']:.2f} V","过滤建立瞬态异常值"),
            ("Pack派生功率",f"约{pack_power:.2f} kW","不得与CP功率计算效率"),
            ("SOC",f"{soc['min']:.1f}%→{soc['max']:.1f}%","条件化短时变化"),
            ("BMS_modelTMax候选",f"{model_tmax['min']:.1f}–{model_tmax['max']:.1f}°C","保持候选语义"),
        ]), "",
        f"CP与Pack派生功率相差约{abs(pack_power-cp_power):.2f} kW，超出可直接归因于一般辅助负载/显示滤波的范围；本次不建立功率效率基线。",
    ]
    (OUT / "采集时间线与关键Signal.md").write_text("\n".join(timeline_md)+"\n", encoding="utf-8")

    final_md = f"""# TM3-015 直流快充基线分析报告

## 结论

本次采集完成了**直流充电电流建立、短时运行和主动停止退出**的条件化时序基线，但没有完成车辆内部协商/许可Signal的完整车型映射，也没有形成可用的定量功率或热管理控制闭环。

车辆侧可见充电状态约在{t_charge_ui:.4f}s建立；CP侧候选直流电压约{t_voltage:.4f}s出现，实际直流电流约{t_cp_current:.4f}s开始建立。173.73–233.23s形成59.50s短稳态，CP电流候选均值{cp_i['mean']:.3f}A，SOC由{soc['min']:.1f}%升至{soc['max']:.1f}%。停止候选约{t_stop_candidate:.4f}s出现，CP输出电流在{t_cp_zero:.4f}s归零，车辆充电状态在{t_ui_exit:.4f}s退出。该段支持“充电状态建立—电流建立—短稳态—停止—电流退出”的车型时序基线。

## 控制关系

边界外扫码、付款和平台接受没有被写成车辆内部控制节点。当前可确认的是外部操作窗口与车辆可观测响应的时间对应；车辆内部主链中的连接/协商和许可层仍有明显缺口：`CP_digitalCommsEstablished`、`CP_evseRequest`、`CP_evseAccept`和`CP_gbState`全程不变，`0x13D`无帧，`BMS_chargeRequest`恒0，`BMS_hvState`按当前DBC出现不合理轮转。因此“许可已经形成”只能由后续电流执行间接证明，不能确认具体请求主体、判断条件或协议状态顺序。

能源响应方向成立，但定量定义冲突。稳定段CP派生约{cp_power:.2f}kW，Pack按当前DBC和“充入为正”换算约{pack_power:.2f}kW，`BMS_chgPowerAvailable`约35.9kW；三者不能形成可信的Request—Available—Actual定量对应。本次只保留建立/退出方向和各自原始值，不计算效率。

热管理方面，`BMS_modelTMax`候选由33.5°C升至35.0°C；但最低温度、接口针脚温度、多个BMS目标值及冷却液温度出现SNA、越界或不合理突变，压缩机请求无帧，Chiller目标复用页未观察到。泵、阀和部分模式字段只能保存为技术覆盖或过程证据，尚不足以建立“Pack热状态—请求—执行—温度响应”闭环。

## 基线有效性与建议

- 可保存为基线：直流电流建立/爬升、59.5s短稳态、主动停止后电流退出及UI状态退出的时序；SOC条件和`BMS_modelTMax`候选变化。
- 仅保留为过程证据：连接/锁止候选位、内部协商候选、许可候选、定量功率、热管理执行器字段。
- 不需要整体重采。若要补齐连接释放，最小补采只需同步记录实际插枪、锁止、停止、解锁和拔枪时刻，并保留停止前10s至拔枪后30s。
- 若要验证定量能源链，需同步保存桩屏/订单的电压、电流、功率，并优先解决`0x29D`和`0x132`缩放/符号冲突；在此之前不进入效率判断。
- 若要验证热管理副线，应在DBC适配后针对稳定快充保留至少60s，记录SOC、Pack温度、环境温度、充前预热、空调和桩功率条件；无需重复本次已合格的停止段。
- 当前不因候选Signal失败进入车辆故障诊断树；这些失败首先属于DBC适配和观测覆盖问题。

## 证据边界

本报告使用社区ONYX DBC，不是Tesla官方定义。外部实际事件表和桩屏记录尚未随ASC提供；脚本时间不能替代真实扫码、停止或拔枪时刻。所有`INSUFFICIENT_EVIDENCE / SEMANTIC_VALIDATION_FAILED`项均未为维持Evidence Plan而强行解释。完整Assessment见`evidence_assessment.csv`。
"""
    (OUT / "TM3-015_最终报告.md").write_text(final_md, encoding="utf-8")

    audit = {
        "source": str(ASC.relative_to(ROOT)), "source_sha256": sha(ASC),
        "approved_plan_sha256": sha(OUT / "evidence_plan_approved.csv"),
        "coverage_gate_sha256": sha(OUT / "dbc_coverage_gate.csv"),
        "human_power_sign": "charge_into_pack_positive",
        "raw_data_modified": False,
        "stable_window_s": list(stable),
        "cp_power_candidate_kw": cp_power,
        "pack_power_candidate_kw": pack_power,
    }
    (OUT / "analysis_audit.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(audit,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
