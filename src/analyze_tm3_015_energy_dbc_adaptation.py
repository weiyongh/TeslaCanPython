"""Focused TM3-015 energy-chain DBC adaptation audit."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ASC=ROOT/"input/can_20260831102614_TM3-015_直流快充采集.asc"
OUT=ROOT/"output/TM3-015/energy_dbc_adaptation"
ASC_RE=re.compile(r"^\s*(\d+(?:\.\d+)?)\s+\d+\s+([0-9A-Fa-f]+)\s+Rx\s+d\s+(\d+)\s*((?:[0-9A-Fa-f]{2}(?:\s+|$))*)")
STABLE=(173.73,233.23)


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def bits(raw,start,length,signed=False):
    value=(int.from_bytes(raw,"little")>>start)&((1<<length)-1)
    if signed and value&(1<<(length-1)): value-=1<<length
    return value
def mean(values): return statistics.fmean(values)
def write_csv(path,rows):
    if not rows:return
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    frames=defaultdict(list);dlcs=defaultdict(Counter)
    with ASC.open(encoding="utf-8",errors="replace") as f:
        for line in f:
            m=ASC_RE.match(line)
            if not m:continue
            raw=bytes.fromhex(m.group(4));declared=int(m.group(3))
            if len(raw)!=declared:continue
            fid=int(m.group(2),16);t=float(m.group(1));frames[fid].append((t,raw));dlcs[fid][declared]+=1
    rows=[]
    for t,raw in frames[0x29D]:
        if not STABLE[0]<=t<=STABLE[1]:continue
        current_raw=bits(raw,0,15,True);voltage_raw=bits(raw,16,13,False)
        rows.append(dict(time_s=f"{t:.6f}",can_id="0x29D",raw_hex=raw.hex(" "),asc_dlc=len(raw),
                         current_raw_s15=current_raw,current_onyx_a=current_raw*0.0732467,
                         current_factor_0_1_a=current_raw*0.1,current_factor_0_125_a=current_raw*0.125,
                         voltage_raw_u13=voltage_raw,voltage_onyx_v=voltage_raw*0.0732422,
                         fifth_byte=raw[4] if len(raw)>4 else ""))
    write_csv(OUT/"0x29D_stable_raw_decode.csv",rows)
    pack=[]
    for t,raw in frames[0x132]:
        if not STABLE[0]<=t<=STABLE[1]:continue
        voltage_raw=bits(raw,0,16);smooth_s15=bits(raw,16,15,True);smooth_s16=bits(raw,16,16,True);unfiltered=bits(raw,32,16,True)
        pack.append(dict(time_s=f"{t:.6f}",can_id="0x132",raw_hex=raw.hex(" "),asc_dlc=len(raw),
                         voltage_raw_u16=voltage_raw,voltage_v=voltage_raw*0.01,
                         smooth_raw_s15=smooth_s15,smooth_onyx_a=smooth_s15*-0.1,
                         smooth_raw_s16=smooth_s16,smooth_json_a=smooth_s16*0.1,
                         unfiltered_raw_s16=unfiltered,unfiltered_model3can_a=unfiltered*-0.05+822))
    write_csv(OUT/"0x132_stable_raw_decode.csv",pack)
    available=[]
    for t,raw in frames[0x212]:
        if not STABLE[0]<=t<=STABLE[1]:continue
        r38=bits(raw,38,11);r40=bits(raw,40,11)
        available.append(dict(time_s=f"{t:.6f}",can_id="0x212",raw_hex=raw.hex(" "),asc_dlc=len(raw),
                              raw_start38=r38,onyx_start38_kw=r38*0.125,
                              raw_start40=r40,model3can_start40_kw=r40*0.125))
    write_csv(OUT/"BMS_chgPowerAvailable_definition_comparison.csv",available)

    cp_i=mean([float(r["current_onyx_a"]) for r in rows]);cp_v=mean([float(r["voltage_onyx_v"]) for r in rows])
    pack_v=mean([float(r["voltage_v"]) for r in pack]);smooth=-mean([float(r["smooth_onyx_a"]) for r in pack])
    raw_current=-mean([float(r["unfiltered_model3can_a"]) for r in pack])
    json_current=mean([float(r["smooth_json_a"]) for r in pack])
    p_pack_smooth=pack_v*smooth/1000;p_pack_raw=pack_v*raw_current/1000;p_cp=cp_v*cp_i/1000
    avail38=mean([float(r["onyx_start38_kw"]) for r in available]);avail40=mean([float(r["model3can_start40_kw"]) for r in available])
    cp_raw=mean([float(r["current_raw_s15"]) for r in rows]);factor_to_pack=smooth/cp_raw
    duration=STABLE[1]-STABLE[0];soc_delta=30.5-28.2;soc_nominal_kwh=soc_delta/100*55
    soc_power=soc_nominal_kwh/(duration/3600)

    # Independent cumulative energy counter from Model3CAN candidate definition.
    counter=[]
    for t,raw in frames[0x3D2]:
        if STABLE[0]<=t<=STABLE[1]: counter.append((t,bits(raw,32,32)*0.001))
    counter_delta=counter[-1][1]-counter[0][1] if len(counter)>1 else None
    counter_duration=counter[-1][0]-counter[0][0] if len(counter)>1 else None
    counter_power=counter_delta/(counter_duration/3600) if counter_duration else None

    definition_rows=[
        dict(item="0x29D CP current",source="ONYX / Model3CAN",dbc_dlc=4,asc_dlc="5",start_bit=0,bit_length=15,signed="SIGNED",factor=0.0732467,offset=0,result=f"{cp_i:.3f} A",assessment="TIMING_VALID_QUANTITATIVE_UNVERIFIED"),
        dict(item="0x132 Pack smooth current",source="ONYX",dbc_dlc=8,asc_dlc="6",start_bit=16,bit_length=15,signed="SIGNED",factor=-0.1,offset=0,result=f"{-smooth:.3f} A raw sign",assessment="MAGNITUDE_SUPPORTED_SIGN_CONVENTION_SOURCE_DEPENDENT"),
        dict(item="0x132 Pack smooth current",source="Model3 ETH JSON",dbc_dlc=8,asc_dlc="6",start_bit=16,bit_length=16,signed="SIGNED",factor=0.1,offset=0,result=f"{json_current:.3f} A charge-positive",assessment="MAGNITUDE_SUPPORTED_SIGN_CONVENTION_SOURCE_DEPENDENT"),
        dict(item="0x132 Pack unfiltered current",source="Model3CAN",dbc_dlc=8,asc_dlc="6",start_bit=32,bit_length=16,signed="SIGNED",factor=-0.05,offset=822,result=f"{-raw_current:.3f} A raw sign",assessment="INDEPENDENT_FIELD_CONFIRMS_MAGNITUDE"),
        dict(item="BMS_chgPowerAvailable",source="ONYX",dbc_dlc=8,asc_dlc="8",start_bit=38,bit_length=11,signed="UNSIGNED",factor=0.125,offset=0,result=f"{avail38:.3f} kW",assessment="BIT_POSITION_ADAPTATION_FAILED"),
        dict(item="BMS_chgPowerAvailable",source="Model3CAN",dbc_dlc=8,asc_dlc="8",start_bit=40,bit_length=11,signed="UNSIGNED",factor=0.125,offset=0,result=f"{avail40:.3f} kW",assessment="PLAUSIBLE_AVAILABLE_POWER_CANDIDATE"),
    ]
    write_csv(OUT/"definition_assessment.csv",definition_rows)
    summary=dict(
        asc_sha256=sha(ASC),stable_window_s=list(STABLE),stable_duration_s=duration,
        frame_counts={hex(k):len(frames[k]) for k in (0x29D,0x132,0x212)},
        asc_dlcs={hex(k):dict(dlcs[k]) for k in (0x29D,0x132,0x212)},
        cp_current_onyx_a=cp_i,cp_voltage_onyx_v=cp_v,cp_power_onyx_kw=p_cp,
        pack_voltage_v=pack_v,pack_smooth_charge_positive_a=smooth,
        pack_unfiltered_charge_positive_a=raw_current,pack_power_smooth_kw=p_pack_smooth,
        pack_power_unfiltered_kw=p_pack_raw,available_onyx_start38_kw=avail38,
        available_model3can_start40_kw=avail40,cp_factor_required_to_match_pack=factor_to_pack,
        soc_delta_ui_pct=soc_delta,soc_55kwh_sanity_energy_kwh=soc_nominal_kwh,
        soc_55kwh_sanity_power_kw=soc_power,cumulative_charge_counter_delta_kwh=counter_delta,
        cumulative_charge_counter_duration_s=counter_duration,cumulative_charge_counter_power_kw=counter_power,
        external_charger_evidence_found=False,
    )
    (OUT/"energy_chain_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=="__main__":main()
