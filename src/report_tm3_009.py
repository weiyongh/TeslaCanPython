"""TM3-009 regression report layer, using L3 v1.0's body/audit separation.

Run: .venv/bin/python src/report_tm3_009.py
Rechecks raw frames against existing audits. Writes ONLY report_v1/; retains
all existing decoders, DBCs, raw captures, reports and engineering audits.
Conclusions are specific to this regression capture, not a general classifier.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from bisect import bisect_right
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

import cantools
from asc_dbc_signal_trace import parse_asc_line

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'output/TM3-009'
OUT = BASE / 'report_v1'
ASC = ROOT / 'input/can_20260831090233_TM3-010_中等负载加速采集.asc'
DBC = ROOT / 'input/tesla_model3_ONYX.dbc'
ROD_DBC = ROOT / 'dbc/Model3CAN.dbc'
SPEC = ROOT / 'L3新能源实车数据诊断分析规范_v1.0.md'
FIELDS = {
    0x118: ('DI_accelPedalPos', 'DI_gear', 'DI_systemState'),
    0x257: ('DI_vehicleSpeed',),
    0x266: ('DI_elecPower',),
    0x132: ('BMS_packCurrent', 'BMS_packVoltage'),
    0x3C2: ('VCLEFT_brakeSwitchPressed',),
    0x39D: ('IBST_sInputRodDriver', 'IBST_driverBrakeApply', 'IBST_internalState'),
}


def require(condition, message):
    if not condition:
        raise RuntimeError('Regression verification failed: ' + message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def numeric(v):
    return isinstance(v, (int, float)) and math.isfinite(v)


def statistics(rows):
    require(bool(rows), 'empty statistics window')
    errors = [r['actual_Nm'] - r['request_Nm'] for r in rows]
    return dict(n=len(rows), sum_abs_error_Nm=sum(abs(e) for e in errors),
                mae_Nm=mean(abs(e) for e in errors), mean_error_Nm=mean(errors),
                max_abs_error_Nm=max(abs(e) for e in errors),
                first_s=rows[0]['time_s'], last_s=rows[-1]['time_s'])


def write_csv(name, rows):
    require(bool(rows), name + ' is empty')
    with (OUT / name).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    # Pin narrative conclusions to the reviewed capture/definitions. Fail rather
    # than silently apply Model 3 conclusions to another source or changed DBC.
    require(digest(ASC) == 'c9f378fa919ead3fb7464395d1b33b92c97a1ffca156371191bfc4545bf3b4e6', 'capture changed')
    require(digest(DBC) == '3554e37a3a8371bc9c1b76445061d30f2c5bbaa35a055fe1f01f7ee75030e86c', 'ONYX changed')
    old_summary = load(BASE / 'summary.json')
    brake_summary = load(BASE / 'braking/summary.json')
    inventory = load(BASE / 'dbc_brake_audit/inventory.json')
    expected_rod = next(r['sha256'] for r in inventory if r['file'] == ROD_DBC.name)
    require(digest(ROD_DBC) == expected_rod, 'rod DBC differs from prior audit')
    require(SPEC.exists(), 'report specification missing')

    protected = [ASC, DBC, ROD_DBC, SPEC]
    protected += [ROOT/'src'/name for name in (
        'analyze_tm3_009.py', 'analyze_tm3_009_braking.py', 'audit_brake_dbcs.py')]
    protected += [p for p in BASE.rglob('*') if p.is_file() and OUT not in p.parents]
    before = {str(p.relative_to(ROOT)): digest(p) for p in protected}
    db = cantools.database.load_file(DBC, strict=False)
    rod_db = cantools.database.load_file(ROD_DBC, strict=False)
    series = defaultdict(list)
    torque, rod_native = [], []
    counts = Counter()
    for line in ASC.open(encoding='utf-8'):
        frame = parse_asc_line(line)
        if not frame:
            continue
        fid, t = frame['can_id'], frame['time']
        counts[fid] += 1
        if fid not in FIELDS and fid != 0x108:
            continue
        source = rod_db if fid == 0x39D else db
        values = source.get_message_by_frame_id(fid).decode(
            frame['data'], decode_choices=True, allow_truncated=True)
        if fid == 0x108:
            req, actual = values['DI_torqueCommand'], values['DI_torqueActual']
            if numeric(req) and numeric(actual):
                torque.append(dict(time_s=t, raw_108=frame['data'].hex(' '),
                                   request_Nm=float(req), actual_Nm=float(actual)))
            continue
        for signal in FIELDS[fid]:
            if signal in values:
                v = values[signal]
                series[signal].append((t, float(v) if numeric(v) else str(v)))
        if fid == 0x39D:
            rod = float(values['IBST_sInputRodDriver'])
            raw = (int.from_bytes(frame['data'], 'little') >> 21) & 4095
            require(rod == raw / 64 - 5, 'rod raw-bit cross-check')
            rod_native.append(dict(time_s=t, raw_39D=frame['data'].hex(' '),
                                   rod_mm=rod, apply=str(values['IBST_driverBrakeApply'])))
    times = {s: [t for t, _ in samples] for s, samples in series.items()}

    def at(signal, t, max_age):
        i = bisect_right(times[signal], t) - 1
        if i < 0 or t - times[signal][i] > max_age:
            return None, None
        return series[signal][i][1], times[signal][i]

    rows = []
    for pair in torque:
        row = dict(pair)
        t = pair['time_s']
        row['error_Nm'] = pair['actual_Nm'] - pair['request_Nm']
        for name, field, age in (
            ('rod_mm', 'IBST_sInputRodDriver', .08),
            ('apply', 'IBST_driverBrakeApply', .08),
            ('pedal_pct', 'DI_accelPedalPos', .03),
            ('speed_kmh', 'DI_vehicleSpeed', .05),
            ('gear', 'DI_gear', .03),
            ('brake_switch', 'VCLEFT_brakeSwitchPressed', .25),
        ):
            row[name], row[name + '_sample_s'] = at(field, t, age)
        rows.append(row)

    comparisons, memberships, peaks = [], [], []
    drive_windows = []
    drive_start = None
    for t, value in series['DI_gear']:
        if value == 'D' and drive_start is None:
            drive_start = t
        elif value != 'D' and drive_start is not None:
            drive_windows.append((drive_start, t))
            drive_start = None
    require(len(drive_windows) == len(old_summary['runs']) == 2,
            'raw D windows do not match the two reviewed runs')
    for i, run in enumerate(old_summary['runs'], 1):
        # Match the prior implementation exactly: pedal onset is a start bound,
        # NOT a requirement that the pedal remain nonzero at every sample.
        start, end = run['pedal_onset_s'], run['drive_window'][1]
        speed_end = run['first_30kmh_s']
        raw_start, raw_end = drive_windows[i-1]
        raw_onset = next(t for t,v in series['DI_accelPedalPos']
                         if raw_start <= t < raw_end and numeric(v) and v > 0)
        raw_speed_end = next(t for t,v in series['DI_vehicleSpeed']
                             if raw_onset <= t < raw_end and numeric(v) and v >= 30)
        require((raw_start,raw_end) == tuple(run['drive_window']) and
                (raw_onset,raw_speed_end) == (start,speed_end), 'raw action bounds differ')
        old = [r for r in rows if start <= r['time_s'] < end and
               r['request_Nm'] > 0 and r['brake_switch'] == 0]
        new = [r for r in rows if start <= r['time_s'] < speed_end]
        old_times = {r['time_s'] for r in old}
        new_times = {r['time_s'] for r in new}
        require(new_times <= old_times, f'run{i} acceleration is not a subset')
        # Window-only new calculation has no brake/sign filter, but check whether
        # every included sample actually meets those conditions in this capture.
        require(all(r['request_Nm'] > 0 and r['brake_switch'] == 0 and
                    r['apply'] == 'BRAKES_NOT_APPLIED' and r['gear'] == 'D'
                    for r in new), f'run{i} acceleration state differs')
        old_stats, new_stats = statistics(old), statistics(new)
        for computed, prior in ((old_stats, run['positive_torque_no_brake_tracking']),
                                (new_stats, brake_summary['transient_phases'][f'acceleration_run{i}'])):
            require(computed['n'] == prior['n'] and
                    math.isclose(computed['mae_Nm'], prior['mae_Nm'], abs_tol=1e-10),
                    f'run{i} prior MAE does not reproduce')
        extra = [r for r in old if r['time_s'] not in new_times]
        comparisons.append(dict(run=i, start_s=start, old_end_s=end, new_end_s=speed_end,
                                old=old_stats, new=new_stats, extra=statistics(extra)))
        for r in rows:
            if start <= r['time_s'] < end:
                memberships.append(dict(run=i, **r, included_old=r['time_s'] in old_times,
                                        included_new=r['time_s'] in new_times))
        p = {s: max(v for t,v in samples if start <= t < speed_end and numeric(v))
             for s,samples in series.items() if s in ('DI_accelPedalPos','DI_elecPower','BMS_packCurrent')}
        p['request_Nm'] = max(r['request_Nm'] for r in new)
        p['actual_Nm'] = max(r['actual_Nm'] for r in new)
        peaks.append(p)

    event = [r for r in rows if 97.5 <= r['time_s'] < 102]
    lookup = {r['time_s']: r for r in event}
    # A reviewed chronological sequence, verified against raw same-frame pairs.
    expected = [(98.0593,342,368),(98.2595,382,388),(98.6593,364,426),
                (98.7592,344,412),(99.4592,62,104),(99.5592,62,64),
                (99.6594,110,90),(99.8592,256,260),(99.959,332,330)]
    key_rows = []
    for t, req, actual in expected:
        r = lookup[t]
        require((r['request_Nm'],r['actual_Nm']) == (req,actual), 'event sequence changed')
        key_rows.append(r)
    applied = [r for r in event if r['apply'] == 'DRIVER_APPLYING_BRAKES']
    require(all(r['request_Nm'] > 0 and r['pedal_pct'] == 0 and r['gear'] == 'D'
                for r in applied), 'low-speed brake state differs')
    require(lookup[99.6594]['apply'] == 'DRIVER_APPLYING_BRAKES' and
            lookup[99.6594]['rod_mm'] < lookup[99.4592]['rod_mm'] and
            lookup[99.6594]['request_Nm'] > lookup[99.4592]['request_Nm'],
            'request recovery during release not supported')
    large = [r for r in event if 98.6593 <= r['time_s'] <= 99.4592]
    require(len(large)==9 and all(r['error_Nm'] >= 40 for r in large), 'transient interval changed')
    recovery = [r for r in event if 99.959 <= r['time_s'] < 102]
    require(lookup[99.5592]['error_Nm'] == 2, 'local reconvergence absent')
    phases = dict(large_difference=statistics(large), recovery=statistics(recovery))

    OUT.mkdir(exist_ok=True)
    write_csv('mae_sample_membership.csv', memberships)
    write_csv('brake_event_torque_samples.csv', event)
    write_csv('brake_event_rod_native.csv', [r for r in rod_native if 97.5 <= r['time_s'] < 102])
    verification = dict(source_sha256=digest(ASC), dbc_sha256=digest(DBC),
                        rod_dbc_sha256=digest(ROD_DBC), specification_sha256=digest(SPEC),
                        mae_comparisons=comparisons, brake_key_samples=key_rows,
                        transient_phases=phases, raw_reproduction_passed=True,
                        brake_torque_ids_present={f'0x{i:X}':counts[i] for i in (0x145,0x185)})
    (OUT/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
    render(comparisons, peaks, key_rows, phases)
    require(all((ROOT/p).is_file() and digest(ROOT/p)==sha for p,sha in before.items()),
            'an existing source/audit was changed')
    (OUT/'preserved_files.json').write_text(json.dumps(before,ensure_ascii=False,indent=2)+'\n')
    print(f'Reproduced both MAE definitions and native brake sequence; preserved {len(before)} existing files.')
    print(OUT/'TM3-009_最终报告.md')


def render(comparisons, peaks, key_rows, phases):
    first, second = comparisons
    # Front matter contains answers, not decoder bookkeeping.
    report = f'''# TM3-009 中等负载加速：车型基线分析

用途：正常实车基线采集，建立Model 3控制树的车型通信证据。车辆：上海产2021款，2021年5月出厂，标准续航55 kWh、后驱。

## 第一层：诊断正文

### 1. 实验目的

验证驾驶输入变化后，仲裁后的电驱请求、实际扭矩、车辆运动与电池输出如何对应，形成带工况条件的动态参考样本。

### 2. 诊断总结

**两次加速均观察到：电门增加，请求扭矩随之上升，实际扭矩跟随，车辆速度及电池输出相应增加。本次加速范围内，后电驱请求—执行、运动及能源响应符合预期，可作为车型动态基线证据。**

第一次输入较强，请求、实际扭矩及电驱功率、Pack放电也更高。**两次差异可由驾驶输入及操作不同解释，本次未发现加速主链持续性不跟随。**

### 3. 三个实验问题

1. **请求变化后实际能否跟随？——是。** 两个实际加速窗口内，平均绝对差分别约{first['new']['mae_Nm']:.2f}/{second['new']['mae_Nm']:.2f} Nm，结合轨迹观察，实际随请求变化。
2. **执行后车辆运动与电池输出是否对应？——是。** 轴速/车速、电驱功率及Pack放电随加速增加。
3. **两次差异来自哪里？——驾驶输入及工况差异。** 第一次电门、电驱功率及Pack放电峰值均更高，变化方向一致。

### 4. 关键证据链

控制链：

```text
驾驶输入
   ↓
状态 / 条件 / 能力 / 仲裁
   ↓
仲裁后的扭矩请求
   ↓
实际扭矩
   ↓
车辆运动
```

同时验证：

- **动力响应：实际扭矩 → 轴速 / 车速。**
- **能源响应：电驱功率↑ ↔ Pack放电↑。**

控制关系与能源证据分别呈现、相互印证。仲裁层是控制关系中的必要层级，本次观察其输入与输出，未直接测得所有内部仲裁变量。

| 关键证据 | 第一次加速 | 第二次加速 |
|---|---:|---:|
| 电门峰值 | {peaks[0]['DI_accelPedalPos']:.1f}% | {peaks[1]['DI_accelPedalPos']:.1f}% |
| 请求 / 实际扭矩峰值 | {peaks[0]['request_Nm']:.0f} / {peaks[0]['actual_Nm']:.0f} Nm | {peaks[1]['request_Nm']:.0f} / {peaks[1]['actual_Nm']:.0f} Nm |
| 电驱功率峰值 | {peaks[0]['DI_elecPower']:.1f} kW | {peaks[1]['DI_elecPower']:.1f} kW |
| Pack放电电流峰值 | {peaks[0]['BMS_packCurrent']:.1f} A | {peaks[1]['BMS_packCurrent']:.1f} A |

各峰值不要求同刻；结论依据包括完整事件轨迹，不用峰值比值推算效率。

### 5. 独立控制工况：98～100秒低速补踩制动

该段是**D挡、零电门、已有低速正驱动背景下的制动交互**，不并入加速跟随统计。

逐样本过程是：**制动输入增加初期，请求仍继续上升；随后正请求由约382降到62 Nm，但未归零；输入杆行程回落、制动状态尚未解除时，请求已开始恢复。** 因此准确措辞是“释放过程中恢复”，而不是“完全释放后才恢复”。

较大请求—实际差值集中在请求下降阶段约0.8秒，随后局部收窄；恢复阶段差值总体缩小，未延续为后续加速的持续偏离。这是不同控制状态下的动态参考案例，不以整窗均值与加速段直接比较得出故障判断。

车辆在正电机扭矩下仍减速，结合制动输入，摩擦制动很可能已参与。现有数据没有轮端摩擦制动量，因此不将这项解释提升为已确认的制动力分配策略。时间对应支持上述过程描述，不单独证明制动输入是请求变化的唯一原因。

### 6. 基线贡献

保留两组实际加速窗口，分别建立控制关系、动力响应与能源响应的车型参考，并保留三者的时间对应证据；速度保持段含继续加速和回收修正，不作为严格稳态能耗基线；低速补踩单列为交互工况。字段和样本挂接到已有控制树变量，供后续诊断树核对使用，不据此新增零散分支。

## 第二层：工程审计附件

正文仅保留影响结论的关键限制。所有窗口、字段、版本和复算依据见[工程审计](工程审计.md)。原有底层分析和审计文件保持不变，本层新增核查结果供追溯。
'''
    (OUT/'TM3-009_最终报告.md').write_text(report,encoding='utf-8')
    lines = ['# TM3-009 最终报告工程审计', '', '## 1. 两组MAE的独立原帧复算', '',
             'MAE = 同一0x108原生帧内 |实际−请求| 的算术平均；不插值、不重采样、不做时移补偿。两组数据均复算正确。', '',
             '| 次数/口径 | 候选窗口（左闭右开，秒） | 入选样本数 | 绝对差总和（Nm） | MAE（Nm） |',
             '|---|---|---:|---:|---:|']
    for c in comparisons:
        for key in ('old','new'):
            x=c[key]; end=c['old_end_s'] if key=='old' else c['new_end_s']
            label='旧：正驱动筛选' if key=='old' else '新：首次30之前'
            lines.append(f"| {c['run']} / {label} | [{c['start_s']:.4f}, {end:.4f}) | {x['n']} | {x['sum_abs_error_Nm']:.0f} | {x['mae_Nm']:.9f} |")
    lines += ['', '**旧口径的完整条件：** 从首次电门非零时刻起，到该次回P挡前；请求>0；VCLEFT制动开关的最近过去样本为0、年龄≤250 ms；请求/实际均为有效数值。没有逐样本要求电门>0，没有速度稳定条件，没有IBST制动状态条件，也没有按实际扭矩正负筛选。旧口径不能称为“纯加速”或“稳态”。', '',
              '**新口径的完整条件：** 从首次电门非零到首次车速≥30 km/h前，取全部有效同帧请求/实际样本。计算本身只按时间窗和数值有效性筛选，不另外筛请求符号或制动状态。本次逐样本核实这些样本恰好全部请求>0、VCLEFT开关为0、IBST为未施加制动、D挡，均属于旧集合的子集。', '',
              '| 旧口径比新口径多出的后续样本 | 数量 | 绝对差总和（Nm） | 该部分MAE（Nm） |',
              '|---|---:|---:|---:|']
    for c in comparisons:
        x=c['extra']; lines.append(f"| 第{c['run']}次 | {x['n']} | {x['sum_abs_error_Nm']:.0f} | {x['mae_Nm']:.6f} |")
    lines += ['', '旧口径含后续较小差值的正驱动调速样本，因此平均值下降。该差异来自窗口和筛选定义，不是数据矛盾，也不是车辆或算法精度发生改变。正文统一用新口径，旧口径保留作工程追溯。每行是否入选两个集合见[样本成员表](mae_sample_membership.csv)。', '',
              '## 2. 98～100秒逐样本核查', '',
              '扭矩同帧配对；行程/IBST状态取最近过去样本，最大年龄80 ms；电门30 ms、车速50 ms。下表每行的行程与扭矩不是强行视为同一采样时刻，完整CSV保留各自原始时间。表内电门均为0、挡位均为D。', '',
              '| 扭矩时间（秒） | 行程（mm） | IBST施加状态 | 请求（Nm） | 实际（Nm） | 实际−请求（Nm） | 车速（km/h） |',
              '|---|---:|---|---:|---:|---:|---:|']
    for r in key_rows:
        state='ON' if r['apply']=='DRIVER_APPLYING_BRAKES' else 'OFF'
        lines.append(f"| {r['time_s']:.4f} | {r['rod_mm']:.6f} | {state} | {r['request_Nm']:.0f} | {r['actual_Nm']:.0f} | {r['error_Nm']:.0f} | {r['speed_kmh']:.2f} |")
    lines += ['', 'IBST状态ON为98.0368～99.9574秒；原生行程峰值3.9375 mm在98.6767秒。请求98.2595秒达382 Nm，随后总体下降到99.4592/99.5592秒的62 Nm。99.6594秒行程已回落至3.09375 mm、IBST仍为ON，请求已升至110 Nm。这直接修正了“完全释放后才恢复”的措辞。', '',
              '98.6593～99.4592秒有9个扭矩样本，实际−请求为+42～+68 Nm，首末间隔0.7999秒；不能把它说成单个边沿噪声。99.5592秒差值局部收敛到+2 Nm。之后请求再次变化，99.959～102秒MAE约'+f"{phases['recovery']['mae_Nm']:.2f}"+' Nm、最大22 Nm，仍非恒定请求稳态。第二次正式加速MAE为2.58 Nm，说明较大差值未持续到该阶段。', '',
              '“先增加、后下降、释放中恢复”是样本过程；“蠕行需求受到制动与车速状态共同仲裁”是控制关系解释。不得从这次样本确认单一仲裁算法、输入到输出的固定比例或真实内部延迟。', '',
              '[完整扭矩时间轴及状态对齐](brake_event_torque_samples.csv) · [原生行程帧](brake_event_rod_native.csv) · [机器可读核查结果](verification.json)', '',
              '## 3. 数据、定义与采样', '',
              '- 原始ASC：`input/can_20260831090233_TM3-010_中等负载加速采集.asc`；文件编号与工况脚本对调，未改名。时长169.9696秒，共483,669帧。',
              '- 主链使用`input/tesla_model3_ONYX.dbc`；0x39D使用`dbc/Model3CAN.dbc`。本层从原始ASC复算，与现有审计相互核对；完整哈希见verification.json。',
              '- 0x108请求/实际扭矩约100 ms；0x118电门/状态约10 ms；0x257车速约20 ms；0x132电池和0x266电驱功率约10 ms；0x39D行程约40 ms。显示小数精度不代表控制延迟精度。',
              '- 0x132实际6字节/ONYX定义8字节，电压和电流在完整字段范围内；0x268实际5字节。0x39D实车5字节，Model3CAN匹配，ONYX的3字节定义缺行程字段。',
              '- 0x118的DI_brakePedalState全程INVALID，不用于制动判定；0x252有定义重叠导致解码失败；0x145/0x185未采到。保留原始缺失与失败信息，不以它们作正驱动链结论的前提。',
              '- 不同DBC的助力器自检枚举冲突，不据此判断短路/自检状态。完整对比见下方原审计。',
              '- 当前数据未建立厂家验收阈值，不能把本次MAE当成车型通用限值。环境、温度、坡度及停止模式未完整记录，样本带本次工况使用。Pack功率是同帧V×I派生量，行程是输入杆位移，不是脚踩力。', '',
              '## 4. 车型投射与已有审计入口', '',
              '| 控制树量 | 车型CAN字段 |', '|---|---|',
              '| 电门/挡位/状态 | 0x118 DI_accelPedalPos / DI_gear / DI_systemState |',
              '| 仲裁后的电驱请求/实际反馈/轴速 | 0x108 DI_torqueCommand / DI_torqueActual / DI_axleSpeed |',
              '| 车辆运动 | 0x257 DI_vehicleSpeed |',
              '| 电驱及电池供能 | 0x266 DI_elecPower；0x132 BMS_packVoltage / BMS_packCurrent |',
              '| 制动输入 | 0x39D IBST_sInputRodDriver / IBST_driverBrakeApply；0x3C2 VCLEFT_brakeSwitchPressed |', '',
              '- [主链原审计](../summary.json)、[原生信号](../signal_samples.csv)、[100ms网格](../aligned_100ms.csv)、[状态边沿](../signal_edges.csv)。',
              '- [制动原审计](../braking/summary.json)、[制动原对齐](../braking/torque_aligned_brake.csv)。',
              '- [DBC全目录规格比较](../dbc_brake_audit/制动DBC规格对比.md)、[版本清单](../dbc_brake_audit/inventory.json)、[解码核查](../dbc_brake_audit/decode_checks.json)。',
              '- [历史四层报告](../TM3-009_中等负载加速_四层诊断复核.md)保留；本目录是v1.0两层输出。', '',
              '## 5. 运行与回归自检', '',
              '```sh', '.venv/bin/python src/report_tm3_009.py', '```', '',
              '该入口仅新增/更新report_v1目录，不调用旧脚本覆盖已有输出。源数据身份、两组MAE及样本数、制动关键样本和恢复状态均有回归校验；不满足时停止生成适用于本样本的结论。运行前后校验原有文件哈希，清单见preserved_files.json。', '',
              '既有底层程序analyze_tm3_009.py、audit_brake_dbcs.py、analyze_tm3_009_braking.py保留不变，可以继续独立使用。该报告层是固定回归样本的证据呈现，不宣称已实现通用自动诊断分类。', '']
    (OUT/'工程审计.md').write_text('\n'.join(lines),encoding='utf-8')


if __name__ == '__main__':
    main()
