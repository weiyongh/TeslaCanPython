"""Audit Model3_ETH.compact.json against the TM3-015 ASC and local DBCs."""
from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import cantools

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "dbc/Model3_ETH.compact.json"
ASC = ROOT / "input/can_20260831102614_TM3-015_直流快充采集.asc"
ONYX = ROOT / "input/tesla_model3_ONYX.dbc"
OUT = ROOT / "output/TM3-015/dbc_all_sources_audit/eth_json_validation"
ASC_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s+\d+\s+([0-9A-Fa-f]+)\s+Rx\s+d\s+(\d+)\s*((?:[0-9A-Fa-f]{2}(?:\s+|$))*)")
RELEVANT = re.compile(
    r"charge|charging|chg|evse|fastcharge|precharge|contactor|hvil|isolation|"
    r"pack.*temp|thermal|coolant.*bat|pumpbattery|chiller|compressor|"
    r"activeheat|pintemp|chargeport|dccurrent|dcvoltage", re.I,
)
PHASES = [("PRE",0,110),("PREP",115.3,139.9),("RAMP",140,160),
          ("STEADY",173.7,233.2),("STOP",244.5,247),("POST",247,299.8)]
EVENTS = [("ui_charge",115.3922),("contactor_request",134.5149),
          ("dc_voltage",140.0299),("dc_current",145.0303),
          ("stop",245.7336),("current_zero",246.2355),("contactor_open",246.5176)]


def write_csv(path, rows):
    if not rows: return
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def raw_little(data, start, width, signed):
    value=(int.from_bytes(data,"little") >> start) & ((1 << width)-1)
    if signed and value & (1 << (width-1)): value -= 1 << width
    return value


def summary(values):
    if not values: return ""
    nums=sorted(float(v) for _,v in values)
    n=len(nums); return f"{(nums[n//2] if n%2 else (nums[n//2-1]+nums[n//2])/2):.6g}"


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    spec=json.loads(SOURCE.read_text(encoding="utf-8"))
    messages=spec["messages"]
    frames=defaultdict(list); dlcs=defaultdict(Counter)
    with ASC.open(encoding="utf-8",errors="replace") as f:
        for line in f:
            m=ASC_RE.match(line)
            if not m: continue
            raw=bytes.fromhex(m.group(4)); declared=int(m.group(3))
            if len(raw)!=declared: continue
            fid=int(m.group(2),16); frames[fid].append((float(m.group(1)),raw)); dlcs[fid][declared]+=1

    db_paths=sorted((ROOT/"dbc").glob("*.dbc"))+[ONYX]
    dbs=[]
    for p in db_paths:
        try: dbs.append((p,cantools.database.load_file(p,database_format="dbc",strict=False)))
        except Exception: pass
    all_dbc_names={s.name for _,db in dbs for msg in db.messages for s in msg.signals}
    onyx_db=next(db for p,db in dbs if p==ONYX)
    onyx_names={s.name for msg in onyx_db.messages for s in msg.signals}
    fingerprints=defaultdict(set)
    for p,db in dbs:
        for msg in db.messages:
            for s in msg.signals:
                fingerprints[s.name].add((msg.frame_id,msg.length,s.start,s.length,s.byte_order,s.is_signed,float(s.scale),float(s.offset)))

    rows=[]; transitions=[]
    for msg_name,msg in messages.items():
        fid=int(msg["message_id"]); msg_len=int(msg["length_bytes"])
        muxers={name:s for name,s in msg.get("signals",{}).items() if s.get("is_muxer")}
        mux_values={}
        for name,s in muxers.items():
            if s.get("endianness") == "LITTLE":
                mux_values[name]=[(t,raw_little(raw,int(s["start_position"]),int(s["width"]),False)) for t,raw in frames[fid] if len(raw)*8 >= int(s["start_position"])+int(s["width"])]
        for sig_name,sig in msg.get("signals",{}).items():
            relevant=bool(RELEVANT.search(sig_name) or RELEVANT.search(msg_name))
            endian=sig.get("endianness","")
            start=int(sig.get("start_position",0)); width=int(sig.get("width",0))
            signed=sig.get("signedness")=="SIGNED"; scale=float(sig.get("scale",1)); offset=float(sig.get("offset",0))
            values=[]; mux_skipped=0
            if endian=="LITTLE" and width:
                mux_id=sig.get("mux_id")
                muxer=next(iter(muxers.values()),None)
                for t,raw in frames[fid]:
                    if len(raw)*8 < start+width: continue
                    if mux_id is not None and muxer is not None:
                        mv=raw_little(raw,int(muxer["start_position"]),int(muxer["width"]),False)
                        if mv != int(mux_id): mux_skipped+=1; continue
                    values.append((t,raw_little(raw,start,width,signed)*scale+offset))
            distinct={str(v) for _,v in values}; changes=[]; prev=object()
            for t,v in values:
                key=str(v)
                if key!=prev: changes.append((t,key)); prev=key
            near=[]
            for event,et in EVENTS:
                hits=[(abs(t-et),t,v) for t,v in changes if abs(t-et)<=2]
                if hits:
                    _,t,v=min(hits); near.append(f"{event}:{t:.3f}={v}")
            json_fp=(fid,msg_len,start,width,"little_endian" if endian=="LITTLE" else "big_endian",signed,scale,offset)
            if sig_name not in all_dbc_names: match="JSON_ONLY_NAME"
            elif json_fp in fingerprints[sig_name]: match="EXACT_DBC_DEFINITION_MATCH"
            else: match="SAME_NAME_DIFFERENT_DEFINITION"
            row=dict(
                json_source=str(SOURCE.relative_to(ROOT)), bus=spec.get("busMetadata",{}).get("name",""),
                message=msg_name, can_id=f"0x{fid:X}", message_id_decimal=fid,
                json_dlc=msg_len, asc_dlc="/".join(map(str,sorted(dlcs[fid]))), asc_frames=len(frames[fid]),
                signal=sig_name, relevant="YES" if relevant else "NO", onyx_has_same_name="YES" if sig_name in onyx_names else "NO",
                dbc_comparison=match, start_bit=start, bit_length=width, endianness=endian,
                signedness=sig.get("signedness",""), scale=scale, offset=offset, unit=sig.get("units","") or "",
                mux_id=sig.get("mux_id",""), decoded_count=len(values), mux_skipped=mux_skipped,
                distinct_count=len(distinct), transition_count=max(0,len(changes)-1),
                first_value=str(values[0][1]) if values else "", last_value=str(values[-1][1]) if values else "",
                min_value=min((v for _,v in values),default=""),max_value=max((v for _,v in values),default=""),
                event_near_transition=";".join(near),
                **{f"phase_{name}":summary([(t,v) for t,v in values if a<=t<b]) for name,a,b in PHASES},
            )
            rows.append(row)
            if relevant and values:
                for t,v in changes: transitions.append(dict(signal=sig_name,can_id=f"0x{fid:X}",message=msg_name,time_s=f"{t:.6f}",value=v))

    covered=[r for r in rows if r["asc_frames"]]
    relevant=[r for r in covered if r["relevant"]=="YES"]
    json_only=[r for r in relevant if r["onyx_has_same_name"]=="NO"]
    dynamic=[r for r in json_only if r["distinct_count"]>1]
    eventful=[r for r in dynamic if r["event_near_transition"]]
    write_csv(OUT/"json_all_signal_comparison.csv",rows)
    write_csv(OUT/"json_asc_covered_relevant_signals.csv",relevant)
    write_csv(OUT/"json_onyx_missing_relevant_signals.csv",json_only)
    write_csv(OUT/"json_onyx_missing_dynamic_event_candidates.csv",eventful)
    write_csv(OUT/"json_relevant_transitions.csv",transitions)
    lines=["# TM3-015 Model3_ETH JSON字典审计","",
           f"- JSON产品/版本：`{spec.get('product','')}` / `{spec.get('version','')}`；总线：`{spec.get('busMetadata',{}).get('name','')}`。",
           f"- JSON消息：{len(messages)}；Signal：{len(rows)}。",
           f"- 与本ASC报文ID有交集：{len({r['can_id'] for r in covered})}个消息、{len(covered)}个Signal定义。",
           f"- 充电/高压/热管理相关且ASC有报文：{len(relevant)}个定义。",
           f"- 其中ONYX无同名Signal：{len(json_only)}个；动态：{len(dynamic)}个；关键事件±2秒有转换：{len(eventful)}个。","",
           "## ONYX缺失且有事件近邻转换的候选","",
           "| Signal | CAN ID | JSON消息 | 阶段中值 PRE/PREP/RAMP/STEADY/STOP/POST | 事件近邻 |","| --- | --- | --- | --- | --- |",
           *[f"| `{r['signal']}` | {r['can_id']} | `{r['message']}` | {r['phase_PRE']} / {r['phase_PREP']} / {r['phase_RAMP']} / {r['phase_STEADY']} / {r['phase_STOP']} / {r['phase_POST']} | {r['event_near_transition']} |" for r in eventful],"",
           "JSON位段可解只表示候选可读。该文件标记为ETH/caneth字典，是否与本车当前网关版本完全一致仍须由DLC、事件方向和物理闭环验证。"]
    (OUT/"Model3_ETH_JSON字典审计.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(dict(messages=len(messages),signals=len(rows),covered_messages=len({r['can_id'] for r in covered}),covered_signals=len(covered),relevant=len(relevant),onyx_missing_relevant=len(json_only),onyx_missing_dynamic=len(dynamic),onyx_missing_eventful=len(eventful)),ensure_ascii=False))


if __name__=="__main__": main()
