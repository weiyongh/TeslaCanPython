"""TM3-010 stable-speed baseline analysis and report generator.

The source file was numbered TM3-009 by mistake.  This program binds it to
the stable-speed experiment by content, preserves native sample times, and
writes only output/TM3-010.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from bisect import bisect_right
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median, pstdev

import cantools

from asc_dbc_signal_trace import parse_asc_line


ROOT = Path(__file__).resolve().parents[1]
ASC = ROOT / "input/can_20260831085710_TM3-009_稳定匀速采集.asc"
DBC = ROOT / "input/tesla_model3_ONYX.dbc"
OUT = ROOT / "output/TM3-010"
DETAIL = OUT / "baseline_evidence"
EXPERIMENT = {
    "experiment_id": "TM3-010",
    "experiment_name": "稳定匀速",
    "purpose": "正常基线",
    "identity_basis": "实验metadata与采集脚本定义；不依赖原始ASC文件名中的编号",
    "script": "input/TM3-010_稳定匀速采集脚本.txt",
    "source_asc": "input/can_20260831085710_TM3-009_稳定匀速采集.asc",
    "source_naming_note": "原始ASC编号误写为TM3-009；仅作为来源记录，实验身份固定为TM3-010=稳定匀速",
    "vehicle": {
        "model": "Tesla Model 3",
        "production": "上海产2021款",
        "production_date": "2021-05",
        "variant": "标准续航",
        "battery_capacity_user_provided_kWh": 55,
        "drive": "后驱",
    },
}

# role, CAN ID, signal, unit, maximum age used for event snapshots
REGISTRY = [
    ("驾驶输入", 0x118, "DI_accelPedalPos", "%", .03),
    ("条件/状态", 0x118, "DI_gear", "enum", .03),
    ("条件/状态", 0x118, "DI_systemState", "enum", .03),
    ("条件/状态", 0x118, "DI_tractionControlMode", "enum", .03),
    ("仲裁后请求", 0x108, "DI_torqueCommand", "Nm", .15),
    ("执行反馈", 0x108, "DI_torqueActual", "Nm", .15),
    ("运动反馈", 0x108, "DI_axleSpeed", "RPM", .15),
    ("运动反馈", 0x257, "DI_vehicleSpeed", "km/h", .05),
    ("能源响应", 0x266, "DI_elecPower", "kW", .03),
    ("能源响应", 0x132, "BMS_packVoltage", "V", .03),
    ("能源响应", 0x132, "BMS_packCurrent", "A", .03),
    ("条件/SOC", 0x292, "BMS_socUI", "%", .15),
    ("条件/能力", 0x268, "DI_sysDrivePowerMax", "kW", .15),
    ("条件/能力", 0x268, "DI_sysRegenPowerMax", "kW", .15),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def numeric(value) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value)


def fmt(value, digits=3):
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.{digits}f}".rstrip("0").rstrip(".")
    return str(value).replace("|", "/")


def md_table(headers, rows):
    result = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    result += ["| " + " | ".join(fmt(v) for v in row) + " |" for row in rows]
    return "\n".join(result)


def write_csv(path: Path, rows):
    if not rows:
        return
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def longest_band(series, start, end, low, high, maximum_gap=.06):
    """Longest contiguous native-speed run within a descriptive analysis band."""
    runs, current = [], []
    for t, v in series:
        if not (start <= t < end):
            continue
        valid = numeric(v) and low <= v <= high
        if valid and (not current or t - current[-1][0] <= maximum_gap):
            current.append((t, v))
        else:
            if current:
                runs.append(current)
            current = [(t, v)] if valid else []
    if current:
        runs.append(current)
    return max(runs, key=lambda r: r[-1][0] - r[0][0]) if runs else []


def main():
    assert sha256(ASC) == "d3ab95e0036602901412f0c7bd66bda627cac9cc286cb0e8b4c391fcac6b4b16"
    assert sha256(DBC) == "3554e37a3a8371bc9c1b76445061d30f2c5bbaa35a055fe1f01f7ee75030e86c"
    OUT.mkdir(parents=True, exist_ok=True)
    DETAIL.mkdir(parents=True, exist_ok=True)
    (OUT / "experiment_metadata.json").write_text(
        json.dumps(EXPERIMENT, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    db = cantools.database.load_file(DBC, strict=False)
    wanted = {fid for _, fid, _, _, _ in REGISTRY}
    by_id = defaultdict(list)
    series = defaultdict(list)
    frames = 0
    last = 0.0
    backwards = 0
    previous = None
    dlcs = defaultdict(Counter)
    errors = defaultdict(Counter)

    for line in ASC.open(encoding="utf-8"):
        frame = parse_asc_line(line)
        if not frame:
            continue
        frames += 1
        t, fid = frame["time"], frame["can_id"]
        if previous is not None and t < previous:
            backwards += 1
        previous, last = t, t
        if fid not in wanted:
            continue
        dlcs[fid][frame["dlc"]] += 1
        by_id[fid].append((t, frame["data"]))
        try:
            values = db.get_message_by_frame_id(fid).decode(frame["data"], decode_choices=True, allow_truncated=True)
        except Exception as exc:
            errors[fid][str(exc)] += 1
            continue
        for _, reg_fid, name, _, _ in REGISTRY:
            if reg_fid == fid and name in values:
                value = values[name]
                series[name].append((t, float(value) if numeric(value) else str(value)))
        if fid == 0x132 and numeric(values.get("BMS_packVoltage")) and numeric(values.get("BMS_packCurrent")):
            series["PackPower_derived"].append((t, values["BMS_packVoltage"] * values["BMS_packCurrent"] / 1000))

    speed = series["DI_vehicleSpeed"]
    band20 = longest_band(speed, 45, 75, 19, 21)
    band40 = longest_band(speed, 145, 175, 38, 42)
    assert frames == 627514 and math.isclose(last, 220.9016, abs_tol=1e-6)
    assert backwards == 0 and band20 and band40

    # These bands are analysis identification criteria, not vehicle thresholds.
    windows = [
        ("计划20段", 45.0, 75.0, "脚本名义保持段；包含明显调速"),
        ("20带内最长连续段", band20[0][0], band20[-1][0] + 1e-6, "19～21 km/h识别带；右端含末样本"),
        ("计划40段", 145.0, 175.0, "脚本名义保持段；未连续稳定在40附近"),
        ("40带内最长连续段", band40[0][0], band40[-1][0] + 1e-6, "38～42 km/h识别带；右端含末样本"),
    ]

    times = {name: [t for t, _ in values] for name, values in series.items()}
    age_by_name = {name: age for _, _, name, _, age in REGISTRY}
    age_by_name["PackPower_derived"] = .03

    def at(name, t):
        ts = times.get(name, [])
        index = bisect_right(ts, t) - 1
        if index < 0:
            return None, None, None
        sample_t, value = series[name][index]
        age = t - sample_t
        if age > age_by_name[name] + 1e-9:
            return None, sample_t, age
        return value, sample_t, age

    def values_in(name, start, end):
        return [v for t, v in series[name] if start <= t < end and numeric(v)]

    stats = []
    for label, start, end, note in windows:
        row = {"window": label, "start_s": start, "end_s": end, "duration_s": end - start, "criterion": note}
        for name in ["DI_vehicleSpeed", "DI_axleSpeed", "DI_accelPedalPos", "DI_torqueCommand", "DI_torqueActual", "DI_elecPower", "BMS_packVoltage", "BMS_packCurrent", "PackPower_derived"]:
            vals = values_in(name, start, end)
            row[f"{name}_n"] = len(vals)
            row[f"{name}_mean"] = mean(vals) if vals else None
            row[f"{name}_sd"] = pstdev(vals) if len(vals) > 1 else 0 if vals else None
            row[f"{name}_min"] = min(vals) if vals else None
            row[f"{name}_max"] = max(vals) if vals else None
        # Same-frame torque tracking only, without interpolation.
        diffs = []
        msg = db.get_message_by_frame_id(0x108)
        for t, data in by_id[0x108]:
            if start <= t < end:
                decoded = msg.decode(data, decode_choices=False, allow_truncated=True)
                req, actual = decoded.get("DI_torqueCommand"), decoded.get("DI_torqueActual")
                if numeric(req) and numeric(actual):
                    diffs.append(actual - req)
        row["torque_pairs"] = len(diffs)
        row["torque_mae_Nm"] = mean(abs(x) for x in diffs) if diffs else None
        row["torque_bias_Nm"] = mean(diffs) if diffs else None
        stats.append(row)
    write_csv(DETAIL / "window_statistics.csv", stats)

    event_specs = [
        ("E00", .15, 0, "初始P挡参考"),
        ("E01", 20.0, 20, "第一次挂D附近"),
        ("E02", 30.0, 30, "第一次加速中"),
        ("E03", 45.0, 45, "进入计划20保持段"),
        ("E04", band20[0][0], None, "进入20带内最长连续段"),
        ("E05", band20[-1][0], None, "20带内最长连续段末样本"),
        ("E06", 75.0, 75, "计划20段结束"),
        ("E07", 100.0, 95, "第一次停车/P挡阶段"),
        ("E08", 115.0, 115, "第二次挂D附近"),
        ("E09", 125.0, 125, "第二次加速中"),
        ("E10", 145.0, 145, "进入计划40保持段"),
        ("E11", band40[0][0], None, "进入40带内最长连续段"),
        ("E12", band40[-1][0], None, "40带内最长连续段末样本"),
        ("E13", 175.0, 175, "计划40段结束"),
        ("E14", 205.0, 200, "第二次停车/P挡阶段"),
        ("E15", last, 220, "采集结束"),
    ]
    events, event_samples = [], []
    for event_id, t, planned, event in event_specs:
        events.append({"event_id": event_id, "time_s": t, "planned_s": planned, "event": event})
        for role, fid, name, unit, maximum_age in REGISTRY + [("能源响应", 0x132, "PackPower_derived", "kW", .03)]:
            value, sample_t, age = at(name, t)
            event_samples.append({"event_id": event_id, "event_time_s": t, "role": role, "signal": name, "can_id": f"0x{fid:03X}", "value": value, "sample_time_s": sample_t, "age_s": age, "max_age_s": maximum_age, "unit": unit, "status": "usable" if value is not None else "missing_or_stale"})
    write_csv(DETAIL / "events.csv", events)
    write_csv(DETAIL / "event_signal_samples.csv", event_samples)

    coverage = []
    for role, fid, name, unit, maximum_age in REGISTRY:
        message = db.get_message_by_frame_id(fid)
        signal = message.get_signal_by_name(name)
        samples = series[name]
        nums = [v for _, v in samples if numeric(v)]
        coverage.append({
            "role": role, "message": message.name, "signal": name, "can_id": f"0x{fid:03X}", "unit": unit,
            "dbc_source": str(DBC.relative_to(ROOT)), "dbc_dlc": message.length,
            "signal_start": signal.start, "signal_length": signal.length, "byte_order": signal.byte_order,
            "scale": signal.scale, "offset": signal.offset, "asc_dlc": "/".join(map(str, sorted(dlcs[fid]))),
            "decoded_samples": len(samples), "decode_errors": sum(errors[fid].values()),
            "changed": len({v for _, v in samples}) > 1,
            "observed_min": min(nums) if nums else None, "observed_max": max(nums) if nums else None,
            "maximum_snapshot_age_s": maximum_age,
        })
    write_csv(DETAIL / "signal_coverage.csv", coverage)

    # Human-readable reports.
    stats_by_name = {row["window"]: row for row in stats}
    p20, s20, p40, s40 = (stats_by_name[x] for x in ["计划20段", "20带内最长连续段", "计划40段", "40带内最长连续段"])
    report = f"""# TM3-010 稳定匀速：车型基线分析

用途：正常实车基线采集。车辆：上海产2021款Model 3，2021年5月出厂，标准续航55 kWh、后驱。

## 实验目的

观察约20 km/h与约40 km/h目标下，车速、轴速、仲裁后扭矩请求、实际扭矩、电驱功率与Pack放电如何对应，并判断本次数据能建立哪一种条件化匀速参考。

## 基线结论

本次20 km/h阶段后半段建立了可用的短时车速稳定参考：在分析识别带19～21 km/h内，最长连续段为{s20['start_s']:.4f}～{s20['end_s']:.4f}s（{s20['duration_s']:.2f}s），平均车速{s20['DI_vehicleSpeed_mean']:.2f} km/h、标准差{s20['DI_vehicleSpeed_sd']:.2f} km/h。该段请求/实际扭矩同帧MAE为{s20['torque_mae_Nm']:.2f} Nm；电驱功率均值{s20['DI_elecPower_mean']:.2f} kW，Pack同帧V×I派生功率均值{s20['PackPower_derived_mean']:.2f} kW。它可以作为本车、本次SOC与未完整记录道路负载下的短时条件化参考，但段内仍有驾驶调节和短暂负请求，不等同严格恒负载稳态。

40 km/h计划保持段没有形成连续30秒稳态。145～175s车速范围为{p40['DI_vehicleSpeed_min']:.2f}～{p40['DI_vehicleSpeed_max']:.2f} km/h，标准差{p40['DI_vehicleSpeed_sd']:.2f} km/h；38～42 km/h识别带内最长连续段仅{s40['duration_s']:.2f}s。因此本段保留为“目标40 km/h附近的调速轨迹”，不生成40 km/h稳态功率或能耗基线。

## 控制关系与车型投射

- 控制链：`DI_accelPedalPos (0x118)`是驾驶输入；`DI_torqueCommand (0x108)`是仲裁后请求，不等同于原始电门请求；`DI_torqueActual (0x108)`是执行反馈。
- 动力响应：`DI_torqueActual / DI_axleSpeed (0x108)`与`DI_vehicleSpeed (0x257)`共同描述电驱输出和车辆运动。匀速仍需要随道路阻力、坡度和驾驶调节不断修正扭矩，并非“扭矩固定”。
- 能源响应：`DI_elecPower (0x266)`与`BMS_packVoltage / BMS_packCurrent (0x132)`分别保存；Pack功率由同帧V×I/1000派生。两者相互印证，但不以差值直接计算效率。

## 证据边界

19～21及38～42 km/h只是本报告识别连续区间的分析带，不是厂家稳态阈值。没有独立触发CSV；脚本时间只用于定位。道路坡度、风况、轮胎及热状态未完整记录，不能把功率差仅归因于速度，也不能外推通用能耗。40 km/h目标未形成合格的连续稳态段，不能用筛选后的离散样本伪装成30秒稳态。

## 结论与建议

20 km/h工况已获得18.72s连续稳定样本，可保存为本车当前条件下的短时匀速基线，无需重采。

40 km/h工况未获得足够长的连续稳定样本，本次数据仅保留为调速过程证据，不建立稳态基线。建议后续单独补采40 km/h工况，无需重复20 km/h实验。

补采时应以**实际车速进入并稳定在目标带**作为稳态窗口起点，而不是以脚本预定时间作为起点；建议连续稳定保持20～30s，并记录SOC、道路坡度/方向、空调状态等主要条件。

详细时间线、Signal可读性、窗口统计和复现依据见同目录附件。
"""
    (OUT / "TM3-010_最终报告.md").write_text(report, encoding="utf-8")

    # Human-readable timeline: no E identifiers. Extra display points use the
    # same past-only snapshot rule but do not alter event detection or CSVs.
    midpoint20 = (band20[0][0] + band20[-1][0]) / 2
    display_points = [
        (.15, "P/STANDBY初始参考", "初始静止背景"),
        (20.0, "P/STANDBY，第一次挂D动作前", "20s脚本节点附近仍为P；实际状态优先"),
        (30.0, "D/ENABLE，第一次加速", "已进入正驱动建立阶段"),
        (45.0, "D/ENABLE，进入计划20 km/h保持段", "车速接近目标但后续仍有调节"),
        (band20[0][0], "D/ENABLE，20 km/h基线窗口开始", "首次进入并连续保持19～21 km/h识别带"),
        (midpoint20, "D/ENABLE，20 km/h基线代表状态", "窗口中点参考；不是各Signal峰值拼接"),
        (band20[-1][0], "D/ENABLE，20 km/h基线窗口结束", "识别带内最长连续段末样本"),
        (75.0, "D/ENABLE，计划20 km/h段结束", "开始离开目标车速，后续减速不纳入基线"),
        (100.0, "P/STANDBY，第一次停车后", "第一轮结束"),
        (115.0, "P/STANDBY，第二次挂D动作前", "115s脚本节点附近仍为P；实际状态优先"),
        (125.0, "D/ENABLE，第二次加速", "向40 km/h目标加速"),
        (145.0, "D/ENABLE，进入计划40 km/h保持段", "此时约38.56 km/h"),
        (150.0, "D/ENABLE，40 km/h计划段掉速", "约33.68 km/h，已明显离开目标附近"),
        (band40[0][0], "D/ENABLE，短暂进入38～42 km/h带", "仅为最长连续近40片段起点，不认定稳态"),
        (band40[-1][0], "D/ENABLE，短暂近40片段末样本", "带内连续时间仅约3.32s"),
        (165.0, "D/ENABLE，40 km/h计划段超调", "车速约42.96 km/h并继续调节"),
        (170.0, "D/ENABLE，40 km/h计划段再次掉速", "车速约37.68 km/h"),
        (175.0, "D/ENABLE，计划40 km/h段结束", "车速已降至约29.12 km/h"),
        (205.0, "P/STANDBY，第二次停车后", "第二轮结束"),
        (last, "P/STANDBY，采集结束", "完整采集时长220.9016s"),
    ]
    timeline_rows = []
    for t, state_action, note in display_points:
        pedal = at("DI_accelPedalPos", t)[0]
        request = at("DI_torqueCommand", t)[0]
        actual = at("DI_torqueActual", t)[0]
        vehicle_speed = at("DI_vehicleSpeed", t)[0]
        electric_power = at("DI_elecPower", t)[0]
        pack_current = at("BMS_packCurrent", t)[0]
        pack_power = at("PackPower_derived", t)[0]
        timeline_rows.append((t, state_action, pedal, request, actual, vehicle_speed,
                              electric_power, pack_current, pack_power, note))
    timeline = f"""# TM3-010 采集时间线与关键Signal

实验身份：**TM3-010＝稳定匀速**，由[实验metadata](experiment_metadata.json)及采集脚本确定，不依赖原始ASC文件名编号。原始文件：`{ASC.relative_to(ROOT)}`；文件名中的TM3-009是来源命名错误，只作追溯记录，原文件不改名。ASC相对时间0～{last:.4f}s，共{frames:,}帧。

时间线节点值取该时刻及之前最近的有效样本，不取未来值。完整E事件的Signal原采样时间与年龄继续保存在`baseline_evidence/event_signal_samples.csv`；本表增加的代表展示点采用相同规则，但不写回E事件CSV。脚本名义时间不是精确动作边沿。

## 采集时间线与关键Signal

列对应：驾驶输入=`DI_accelPedalPos (0x118)`；请求/执行=`DI_torqueCommand / DI_torqueActual (0x108)`；运动=`DI_vehicleSpeed (0x257)`；电驱功率=`DI_elecPower (0x266)`；Pack电流=`BMS_packCurrent (0x132)`；Pack功率为同帧电压×电流/1000派生。

{md_table(['时间(s)','状态/动作','电门(%)','请求扭矩(Nm)','实际扭矩(Nm)','车速(km/h)','电驱功率(kW)','Pack电流(A)','Pack功率(kW)','说明'], timeline_rows)}

## 稳定性及控制/动力/能源统计

{md_table(['窗口','实际区间s','时长s','车速均值±SD km/h','电门均值%','请求/实际均值Nm','请求/实际MAE Nm','轴速均值RPM','电驱均值kW','Pack均值电压V','Pack均值电流A','Pack均值功率kW'], [
    (r['window'], f"{r['start_s']:.4f}～{r['end_s']:.4f}", round(r['duration_s'],3), f"{r['DI_vehicleSpeed_mean']:.2f}±{r['DI_vehicleSpeed_sd']:.2f}", round(r['DI_accelPedalPos_mean'],2), f"{r['DI_torqueCommand_mean']:.2f}/{r['DI_torqueActual_mean']:.2f}", round(r['torque_mae_Nm'],3), round(r['DI_axleSpeed_mean'],2), round(r['DI_elecPower_mean'],3), round(r['BMS_packVoltage_mean'],3), round(r['BMS_packCurrent_mean'],3), round(r['PackPower_derived_mean'],3)) for r in stats
])}

计划窗口用于说明实际驾驶轨迹；带内最长连续段用于判断是否形成短时稳定参考。40 km/h段不满足连续30秒稳定保持，不能把多个分散的接近40 km/h样本合并成稳态。

人读表取消E编号；完整E事件定义和原始采样未删除，继续保存在：[事件定义](baseline_evidence/events.csv) · [事件Signal原采样](baseline_evidence/event_signal_samples.csv) · [完整窗口统计](baseline_evidence/window_statistics.csv)
"""
    (OUT / "采集时间线与关键Signal.md").write_text(timeline, encoding="utf-8")

    coverage_md = f"""# TM3-010 DBC关键Signal覆盖与可读性

本实验先按控制树角色选择Signal，再检查实际DLC与可读性。观测范围不是车型正常阈值。

{md_table(['角色','Signal','CAN ID','单位','样本数','观测范围','ASC DLC','用途'], [
    (r['role'], f"`{r['signal']}`", r['can_id'], r['unit'], r['decoded_samples'], f"{fmt(r['observed_min'])}～{fmt(r['observed_max'])}", r['asc_dlc'], {'驾驶输入':'识别驾驶调节','条件/状态':'划分挡位与驱动状态','仲裁后请求':'观察仲裁后电驱请求','执行反馈':'核对请求—执行','运动反馈':'判断车速/轴速稳定性','能源响应':'观察电驱与Pack供能','条件/SOC':'记录适用SOC','条件/能力':'保留能力背景，不作阈值'}[r['role']]) for r in coverage
])}

`BMS_packVoltage / BMS_packCurrent (0x132)`所在ASC帧为6字节，而ONYX Message声明8字节；两个选用字段所需字节完整，按字段可读，不将整帧简单判废。`DI_elecPower (0x266)`固定采用ONYX定义，避免与旧版同名异位字段混用。Pack功率不是DBC原生Signal，由同一0x132帧的电压×电流/1000派生；正值沿用本报告的放电方向约定。

完整定义、DLC、样本数与解码统计见[signal_coverage.csv](baseline_evidence/signal_coverage.csv)。
"""
    (OUT / "DBC关键Signal覆盖与可读性.md").write_text(coverage_md, encoding="utf-8")

    verification = {
        "experiment_id": EXPERIMENT["experiment_id"], "experiment_name": EXPERIMENT["experiment_name"],
        "experiment_metadata": "output/TM3-010/experiment_metadata.json",
        "source": str(ASC.relative_to(ROOT)), "source_sha256": sha256(ASC),
        "dbc": str(DBC.relative_to(ROOT)), "dbc_sha256": sha256(DBC),
        "frames": frames, "duration_s": last, "backwards_timestamps": backwards,
        "speed_samples": len(speed), "event_count": len(events), "event_signal_rows": len(event_samples),
        "coverage_signals": len(coverage),
        "band20": {"low": 19, "high": 21, "start_s": band20[0][0], "end_s": band20[-1][0], "samples": len(band20)},
        "band40": {"low": 38, "high": 42, "start_s": band40[0][0], "end_s": band40[-1][0], "samples": len(band40)},
    }
    (DETAIL / "verification.json").write_text(json.dumps(verification, ensure_ascii=False, indent=2), encoding="utf-8")
    audit = f"""# TM3-010 工程审计

- 实验身份由`output/TM3-010/experiment_metadata.json`固定声明为`TM3-010=稳定匀速`，不以原始文件名编号推断。
- 原始ASC：`{ASC.relative_to(ROOT)}`；SHA-256 `{verification['source_sha256']}`。文件名中的TM3-009仅作为来源命名错误保留，未改名。
- DBC：`{DBC.relative_to(ROOT)}`；SHA-256 `{verification['dbc_sha256']}`。
- 时长{last:.4f}s，共{frames:,}帧；时间戳倒退{backwards}次。
- 车速原生样本{len(speed):,}条。事件快照不插值、不取未来值，超龄留空。
- 人读时间线不显示E编号；完整{len(events)}个E事件和{len(event_samples)}条事件Signal原始采样仍保存在`baseline_evidence/events.csv`与`event_signal_samples.csv`。新增的人读代表点不写回事件CSV，不改变事件检测。
- 请求—实际MAE只使用同一0x108原生帧，不将异步报文强制视为同时采样。
- 20/40识别带分别为19～21、38～42 km/h，仅用于寻找最长连续片段；详细窗口统计保存在`baseline_evidence/window_statistics.csv`。
- 40 km/h计划段没有形成连续30秒稳态，因此报告明确拒绝输出40 km/h稳态功率/能耗基线。

复现：`.venv/bin/python src/analyze_tm3_010.py`
"""
    (OUT / "工程审计.md").write_text(audit, encoding="utf-8")
    print(json.dumps(verification, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
