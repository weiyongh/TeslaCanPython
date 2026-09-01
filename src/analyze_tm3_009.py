"""TM3-009: decode native samples and audit actual driving windows.

Run: .venv/bin/python src/analyze_tm3_009.py
The source filename has the experiment numbers reversed; preserve raw data.
"""
from __future__ import annotations

import csv
import hashlib
import json
from bisect import bisect_right
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median
from math import pi

import cantools
from asc_dbc_signal_trace import parse_asc_line

ROOT = Path(__file__).resolve().parents[1]
ASC = ROOT / 'input/can_20260831090233_TM3-010_中等负载加速采集.asc'
DBC = ROOT / 'input/tesla_model3_ONYX.dbc'
OUT = ROOT / 'output/TM3-009'
TARGETS = {
    0x118: ('DI_accelPedalPos', 'DI_gear', 'DI_systemState', 'DI_brakePedalState', 'DI_driveBlocked', 'DI_tractionControlMode'),
    0x108: ('DI_torqueCommand', 'DI_torqueActual', 'DI_axleSpeed'),
    0x257: ('DI_vehicleSpeed',),
    0x266: ('DI_elecPower',),
    0x132: ('BMS_packVoltage', 'BMS_packCurrent'),
    0x252: ('BMS_maxDischargePower', 'BMS_maxRegenPower'),
    0x292: ('BMS_socUI', 'BMS_socMin', 'BMS_socMax'),
    0x2D2: ('BMS_maxDischargeCurrent', 'BMS_maxChargeCurrent'),
    0x268: ('DI_sysDrivePowerMax', 'DI_sysRegenPowerMax'),
    0x3C2: ('VCLEFT_brakeSwitchPressed', 'VCLEFT_brakePressed'),
}


def write_csv(name, fields, rows):
    with (OUT / name).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    db = cantools.database.load_file(DBC, strict=False)
    series = defaultdict(list)
    errors, dlcs = Counter(), Counter()
    frame_times = defaultdict(list)
    torque_pairs = []
    all_first = all_last = None
    frames = 0
    for line in ASC.open(encoding='utf-8'):
        frame = parse_asc_line(line)
        if not frame:
            continue
        t, fid = frame['time'], frame['can_id']
        if all_first is None:
            all_first = t
        all_last = t
        frames += 1
        if fid not in TARGETS:
            continue
        frame_times[fid].append(t)
        dlcs[f'{fid:03X}/{frame["dlc"]}'] += 1
        try:
            values = db.get_message_by_frame_id(fid).decode(frame['data'], decode_choices=True, allow_truncated=True)
        except Exception as exc:
            errors[f'{fid:03X}: {exc}'] += 1
            continue
        values = {k: float(v) if isinstance(v, (int, float)) else str(v) for k, v in values.items()}
        for signal in TARGETS[fid]:
            if signal in values:
                series[signal].append((t, values[signal]))
        if fid == 0x108 and all(isinstance(values.get(s), float) for s in ('DI_torqueCommand', 'DI_torqueActual')):
            torque_pairs.append((t, values['DI_torqueCommand'], values['DI_torqueActual']))
            if isinstance(values.get('DI_axleSpeed'), float):
                series['derived_axleMechanicalPower_kW'].append((t, values['DI_torqueActual'] * values['DI_axleSpeed'] * 2 * pi / 60000))
        if fid == 0x132 and all(isinstance(values.get(s), float) for s in ('BMS_packVoltage', 'BMS_packCurrent')):
            series['derived_packPower_kW'].append((t, values['BMS_packVoltage'] * values['BMS_packCurrent'] / 1000))

    times = {s: [t for t, _ in rows] for s, rows in series.items()}

    def at(signal, t, max_age=0.25):
        i = bisect_right(times.get(signal, []), t) - 1
        if i < 0 or t - times[signal][i] > max_age:
            return None
        return series[signal][i][1]

    def stats(signal, start, end):
        vals = [(t, v) for t, v in series[signal] if start <= t < end and isinstance(v, float)]
        if not vals:
            return None
        peak = max(vals, key=lambda x: x[1])
        return dict(n=len(vals), min=min(v for _, v in vals), max=peak[1], mean=mean(v for _, v in vals), peak_s=peak[0])

    def intervals(signal, predicate):
        result, start = [], None
        for t, v in series[signal]:
            active = predicate(v)
            if active and start is None:
                start = t
            elif not active and start is not None:
                result.append([start, t])
                start = None
        if start is not None:
            result.append([start, all_last])
        return result

    edges = []
    for s in ('DI_gear', 'DI_systemState', 'DI_brakePedalState', 'DI_driveBlocked', 'DI_tractionControlMode', 'VCLEFT_brakeSwitchPressed', 'VCLEFT_brakePressed'):
        previous = None
        for t, v in series[s]:
            if v != previous:
                edges.append(dict(signal=s, time_s=t, value=v))
                previous = v
    write_csv('signal_edges.csv', ['signal', 'time_s', 'value'], sorted(edges, key=lambda r: (r['time_s'], r['signal'])))
    write_csv('signal_samples.csv', ['signal', 'time_s', 'value'], (dict(signal=s, time_s=t, value=v) for s, rows in series.items() for t, v in rows))
    grid = []
    for i in range(int(all_last * 10) + 1):
        t = i / 10
        row = {'time_s': t, **{s: at(s, t) for s in series}}
        grid.append(row)
    write_csv('aligned_100ms.csv', ['time_s', *series], grid)

    drives = intervals('DI_gear', lambda v: v == 'D')
    runs = []
    for start, end in drives:
        onset = next((t for t, v in series['DI_accelPedalPos'] if start <= t < end and isinstance(v, float) and v > 0), None)
        if onset is None:
            continue
        run = dict(drive_window=[start, end], pedal_onset_s=onset)
        run['speed_at_pedal_onset_kmh'] = at('DI_vehicleSpeed', onset)
        for signal, threshold in (('DI_torqueCommand', 0), ('DI_torqueActual', 0), ('DI_vehicleSpeed', 0.5), ('DI_axleSpeed', 5)):
            # Search the whole D window: this capture moves before pedal input.
            run[signal + '_onset_s'] = next((t for t, v in series[signal] if start <= t < end and isinstance(v, float) and v > threshold), None)
        run['first_30kmh_s'] = next((t for t, v in series['DI_vehicleSpeed'] if onset <= t < end and isinstance(v, float) and v >= 30), None)
        run['stats'] = {s: stats(s, onset, end) for s in series if any(isinstance(v, float) for _, v in series[s])}
        differences = [actual - request for t, request, actual in torque_pairs if onset <= t < end and request > 0 and at('VCLEFT_brakeSwitchPressed', t) == 0]
        run['positive_torque_no_brake_tracking'] = dict(n=len(differences), mean_error_Nm=mean(differences), mae_Nm=mean(abs(v) for v in differences), max_abs_error_Nm=max(abs(v) for v in differences)) if differences else None
        runs.append(run)
    plan_windows = []
    for start, end in ((45, 55), (120, 130)):
        rows = [r for r in grid if start <= r['time_s'] < end]
        # Speed-band occupancy alone is NOT proof of a steady-state window.
        valid = [r for r in rows if isinstance(r.get('DI_vehicleSpeed'), float) and r.get('VCLEFT_brakeSwitchPressed') == 0 and abs(r['DI_vehicleSpeed'] - 30) <= 2]
        plan_windows.append(dict(window=[start, end], speed=stats('DI_vehicleSpeed', start, end), eligible_30plusminus2_no_brake_s=len(valid)*0.1))
    summary = dict(
        source=str(ASC.relative_to(ROOT)), sha256=hashlib.sha256(ASC.read_bytes()).hexdigest(),
        dbc_sha256=hashlib.sha256(DBC.read_bytes()).hexdigest(), frames=frames,
        duration_s=all_last-all_first, decode_errors=dict(errors), dlcs=dict(dlcs),
        frame_periods={f'{k:03X}': dict(n=len(v), median_s=median(b-a for a,b in zip(v,v[1:])), max_gap_s=max(b-a for a,b in zip(v,v[1:]))) for k,v in frame_times.items() if len(v)>1},
        missing_signals=[s for names in TARGETS.values() for s in names if not series[s]],
        runs=runs, planned_hold_windows=plan_windows,
        brake_reference='VCLEFT_brakeSwitchPressed; DI_brakePedalState remains INVALID and is excluded',
        brake_intervals=intervals('VCLEFT_brakeSwitchPressed', lambda v:v==1),
        pedal_intervals=intervals('DI_accelPedalPos', lambda v:isinstance(v,float) and v>0),
        moving_intervals=intervals('DI_vehicleSpeed', lambda v:isinstance(v,float) and v>0.5),
        negative_torque_intervals=intervals('DI_torqueCommand', lambda v:isinstance(v,float) and v<0),
        analysis_windows={f'{a}-{b}': {s:stats(s,a,b) for s in ('DI_vehicleSpeed','DI_accelPedalPos','DI_torqueCommand','DI_torqueActual','DI_elecPower','BMS_packVoltage','BMS_packCurrent','derived_packPower_kW')} for a,b in ((10,19),(85,93),(27.4225,44.923),(102.0783,120.1169),(60,71),(72.019,75.1087),(140.4659,149.0341))},
        global_stats={s:stats(s, all_first, all_last+0.001) for s in series if any(isinstance(v,float) for _,v in series[s])},
    )
    (OUT/'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('global_stats',)},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
