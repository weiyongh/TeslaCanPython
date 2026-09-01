"""Compare same-frame torque request/feedback around actual brake episodes.

Run after analyze_tm3_009.py and audit_brake_dbcs.py; no raw data/DBC edits.
"""
import csv
import json
from bisect import bisect_right
from collections import defaultdict
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'output/TM3-009'
OUT = BASE/'braking'


def main():
    OUT.mkdir(exist_ok=True)
    series=defaultdict(list)
    with (BASE/'signal_samples.csv').open(encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            try: v=float(row['value'])
            except ValueError: v=row['value']
            series[row['signal']].append((float(row['time_s']),v))
    with (BASE/'dbc_brake_audit/input_rod_samples.csv').open(encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            t=float(row['time_s'])
            for key in ('rod_mm','apply','internal_state'):
                series[key].append((t,float(row[key]) if key=='rod_mm' else row[key]))
    times={s:[t for t,v in a] for s,a in series.items()}

    def at(s,t,max_age):
        i=bisect_right(times[s],t)-1
        if i<0 or t-times[s][i]>max_age:return None,None
        return series[s][i][1],round(t-times[s][i],6)

    actual=dict(series['DI_torqueActual'])
    rows=[]
    for t,request in series['DI_torqueCommand']:
        feedback=actual.get(t)
        if not isinstance(request,float) or not isinstance(feedback,float):continue
        row=dict(time_s=t,request_Nm=request,actual_Nm=feedback,error_Nm=feedback-request)
        for s,age in [('rod_mm',.08),('apply',.08),('internal_state',.08),
                      ('DI_vehicleSpeed',.05),('DI_accelPedalPos',.03),
                      ('VCLEFT_brakeSwitchPressed',.15),('DI_elecPower',.03),
                      ('derived_packPower_kW',.03),('DI_gear',.03)]:
            v,a=at(s,t,age);row[s]=v;row[s+'_age_s']=a
        rows.append(row)
    with (OUT/'torque_aligned_brake.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

    episodes=json.loads((BASE/'dbc_brake_audit/input_rod_episodes.json').read_text())
    def metrics(a,b):
        r=[x for x in rows if a<=x['time_s']<b]
        if not r:return None
        counts={label:sum(test(x['request_Nm']) for x in r) for label,test in
            [('positive',lambda v:v>0),('zero',lambda v:v==0),('negative',lambda v:v<0)]}
        out=dict(start_s=a,end_s=b,n=len(r),first=r[0],last=r[-1],request_sign_counts=counts,
            mean_error_Nm=mean(x['error_Nm'] for x in r),
            mae_Nm=mean(abs(x['error_Nm']) for x in r),
            max_error_sample=max(r,key=lambda x:abs(x['error_Nm'])),
            sign_disagreement_n=sum((x['request_Nm']>0)-(x['request_Nm']<0)!=(x['actual_Nm']>0)-(x['actual_Nm']<0) for x in r))
        for k in ('request_Nm','actual_Nm','rod_mm','DI_vehicleSpeed','derived_packPower_kW'):
            v=[x[k] for x in r if isinstance(x[k],float)]
            out[k+'_range']=[min(v),max(v)] if v else None
        # Chronological sign changes, including zero, without smoothing/deadband.
        edges=[];prev=None
        for x in r:
            sign=(x['request_Nm']>0)-(x['request_Nm']<0)
            if sign!=prev:edges.append(dict(time_s=x['time_s'],request_Nm=x['request_Nm'],actual_Nm=x['actual_Nm']));prev=sign
        out['request_sign_edges']=edges
        return out
    output=[]
    for e in episodes:
        a,b=e['start_s'],e['end_s']
        output.append(dict(episode=e,pre_1s=metrics(a-1,a),during=metrics(a,b),
            first_1s=metrics(a,min(a+1,b)),post_1s=metrics(b,b+1)))
    # Separate moving braking from the larger applied-brake episodes that extend into P.
    windows={'first_stop_moving':(75.0361,78.5391),'creep_reapply':(98.0368,99.9574),
             'second_stop_moving':(148.4381,150.434)}
    summary=dict(reference='IBST_driverBrakeApply transitions; rod is input displacement, not force.',
        alignment='Native same-frame 0x108 torque pairs; other signals use past-only bounded-age samples. No physical-delay claim.',
        episodes=output,moving_windows={k:metrics(*v) for k,v in windows.items()})
    # Descriptive phases from this capture's request/feedback trajectory;
    # these are not universal fault thresholds or controller state definitions.
    summary['transient_phases']={name:metrics(a,b) for name,a,b in (
        ('request_peak_to_feedback_peak',98.2595,98.6593),
        ('descending_request_large_positive_error',98.6593,99.5592),
        ('trough_convergence_sample',99.5592,99.6594),
        ('release_request_recovery',99.6594,99.959),
        ('post_release_low_speed_drive',99.959,102.0),
        ('acceleration_run1',27.4225,44.923),
        ('acceleration_run2',102.0783,120.1169),
    )}
    (OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    for k,v in summary['moving_windows'].items():
        print(k,json.dumps({key:value for key,value in v.items() if key not in ('first','last','max_error_sample')},ensure_ascii=False))
        print('MAX_ERROR',v['max_error_sample'])


if __name__=='__main__':main()
