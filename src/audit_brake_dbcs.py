"""Compare local Tesla brake definitions and match them to TM3-009.

Run .venv/bin/python src/audit_brake_dbcs.py. No DBC is modified.
"""
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import cantools
from asc_dbc_signal_trace import parse_asc_line

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/TM3-009/dbc_brake_audit'
ASC = ROOT / 'input/can_20260831090233_TM3-010_中等负载加速采集.asc'
TERMS = re.compile(r'brak|brk|ibst|iboost|hydraul|cylinder|pressure|pedal|decel|inputrod|outputrod|travel|stroke|force|制动|刹车', re.I)
CORE = {0x118, 0x145, 0x185, 0x39D, 0x3C2, 0x2F1, 0x7FF, 0x135, 0x20A, 0x1F8}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    databases, inventory, definitions, hits = {}, [], [], []
    for p in sorted((ROOT / 'dbc').iterdir()):
        if not p.is_file() or not (p.name.endswith('.dbc') or p.name.endswith('.dbc.txt')):
            continue
        # Also inspect the generic Tesla files, but keep them a separate group.
        if '车窗' in p.name:
            continue
        raw = p.read_bytes()
        info = dict(file=p.name, sha256=hashlib.sha256(raw).hexdigest(), model3='model3' in p.name.lower())
        try:
            db = cantools.database.load_file(p, database_format='dbc', strict=False)
            databases[p.name] = db
            info['messages'] = len(db.messages)
        except Exception as exc:
            info['error'] = str(exc)
            inventory.append(info)
            continue
        inventory.append(info)
        for n, line in enumerate(raw.decode('utf-8', errors='replace').splitlines(), 1):
            if TERMS.search(line):
                hits.append(dict(file=p.name, line=n, text=line))
        for m in db.messages:
            for s in m.signals:
                if not TERMS.search(s.name + ' ' + (s.comment or '') + ' ' + m.name):
                    continue
                definitions.append(dict(file=p.name, id=f'0x{m.frame_id:03X}', message=m.name,
                    dlc=m.length, signal=s.name, start=s.start, length=s.length,
                    byte_order=s.byte_order, signed=s.is_signed, scale=s.scale, offset=s.offset,
                    minimum=s.minimum, maximum=s.maximum, unit=s.unit,
                    mux=s.multiplexer_signal, mux_ids=s.multiplexer_ids,
                    choices={str(k):str(v) for k,v in (s.choices or {}).items()},
                    comment=s.comment, message_comment=m.comment))

    counts, dlcs, frames = Counter(), defaultdict(Counter), defaultdict(list)
    relevant_ids = {int(d['id'],16) for d in definitions}
    for line in ASC.open(encoding='utf-8'):
        f = parse_asc_line(line)
        if not f:
            continue
        fid=f['can_id']; counts[fid]+=1; dlcs[fid][f['dlc']]+=1
        if fid in relevant_ids:
            frames[fid].append(f)
    for d in definitions:
        fid=int(d['id'],16)
        d['asc_frames']=counts[fid]
        d['asc_dlcs']=dict(dlcs[fid])
    checks=[]
    for name, db in databases.items():
        # Do not apply generic/other-platform Tesla semantics to this Model 3.
        if 'model3' not in name.lower():
            continue
        for m in db.messages:
            if m.frame_id not in CORE:
                continue
            selected=[s.name for s in m.signals if TERMS.search(s.name)]
            if not selected:
                continue
            values=defaultdict(list); errors=Counter(); mismatch=0
            for f in frames[m.frame_id]:
                mismatch+=len(f['data'])!=m.length
                try:
                    decoded=m.decode(f['data'], decode_choices=True, allow_truncated=True)
                except Exception as exc:
                    errors[str(exc)]+=1
                    continue
                for s in selected:
                    if s in decoded:
                        v=decoded[s]
                        values[s].append((f['time'],float(v) if isinstance(v,(int,float)) else str(v)))
            stat={}
            for s, vals in values.items():
                nums=[v for _,v in vals if isinstance(v,float)]
                stat[s]=dict(n=len(vals), minimum=min(nums) if nums else None,
                    maximum=max(nums) if nums else None,
                    categories=dict(Counter(v for _,v in vals if not isinstance(v,float))))
            checks.append(dict(file=name,id=f'0x{m.frame_id:03X}',frames=counts[m.frame_id],
                dbc_dlc=m.length,asc_dlcs=dict(dlcs[m.frame_id]),dlc_mismatch_frames=mismatch,
                decode_errors=dict(errors),signals=stat))
    def save(name, obj):
        (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    save('inventory.json',inventory)
    save('definitions.json',definitions)
    save('text_hits.json',hits)
    save('decode_checks.json',checks)
    save('asc_id_counts.json',{f'0x{k:03X}':v for k,v in sorted(counts.items())})
    rod_rows=[]
    model=databases['Model3CAN.dbc'].get_message_by_frame_id(0x39D)
    for f in frames[0x39D]:
        v=model.decode(f['data'],decode_choices=True)
        raw=(int.from_bytes(f['data'],'little')>>21)&0xFFF
        rod=float(v['IBST_sInputRodDriver'])
        assert rod==raw/64-5
        for other in ('Model3CAN.dbc.txt','tesla_model3_party.dbc'):
            assert databases[other].get_message_by_frame_id(0x39D).decode(f['data'])['IBST_sInputRodDriver']==rod
        rod_rows.append(dict(time_s=f['time'],raw_hex=f['data'].hex(' '),raw_rod=raw,
            rod_mm=rod,apply=str(v['IBST_driverBrakeApply']),internal_state=str(v['IBST_internalState'])))
    with (OUT/'input_rod_samples.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rod_rows[0]));w.writeheader();w.writerows(rod_rows)
    episodes=[];current=[]
    for row in rod_rows:
        if row['apply']=='DRIVER_APPLYING_BRAKES':
            current.append(row)
        elif current:
            peak=max(current,key=lambda r:r['rod_mm'])
            episodes.append(dict(start_s=current[0]['time_s'],end_s=row['time_s'],
                peak_mm=peak['rod_mm'],peak_s=peak['time_s'],peak_raw=peak['raw_hex']))
            current=[]
    if current:
        peak=max(current,key=lambda r:r['rod_mm'])
        episodes.append(dict(start_s=current[0]['time_s'],end_s=None,
            peak_mm=peak['rod_mm'],peak_s=peak['time_s'],peak_raw=peak['raw_hex']))
    save('input_rod_episodes.json',episodes)
    print('INPUT_ROD_EPISODES',json.dumps(episodes,ensure_ascii=False))
    with (OUT/'definitions.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(definitions[0]));w.writeheader()
        for d in definitions:
            w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in d.items()})
    print('Files',len(inventory),'Model3',sum(i['model3'] for i in inventory),'definitions',len(definitions))
    print('IDs',{f'0x{k:03X}':{'count':counts[k],'dlc':dict(dlcs[k])} for k in sorted(CORE)})
    for c in checks:
        if c['file'] in ('Model3CAN.dbc','tesla_model3_ONYX.dbc.txt') and c['id'] in ('0x2F1','0x7FF','0x39D'):
            print(json.dumps(c,ensure_ascii=False))


if __name__=='__main__':
    main()
