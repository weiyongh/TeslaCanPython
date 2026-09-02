"""Cross-check TM3-015 signal definitions across every local DBC.

This is a dictionary/version audit only. It never promotes a candidate or
changes the experiment-approved evidence role.
"""
from __future__ import annotations

import csv
import re
import sys
from collections import Counter
from pathlib import Path

import cantools

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/TM3-015/dbc_all_sources_audit"
ASC = ROOT / "input/can_20260831102614_TM3-015_直流快充采集.asc"
sys.path.insert(0, str(ROOT / "src"))
from evidence_plan import read_approved_csv

ASC_RE = re.compile(r"^\s*\d+(?:\.\d+)?\s+\d+\s+([0-9A-Fa-f]+)\s+Rx\s+d\s+(\d+)")
RELEVANT = re.compile(
    r"charge|charging|chg|evse|gbdc|supercharg|precharge|contactor|hvil|isolation|"
    r"pack.*temp|thermal|coolant.*bat|pumpbattery|chiller|compressor|hpmode|"
    r"activeheatingbattery|pintemperature", re.I,
)


def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def signal_row(source, message, signal):
    return dict(
        dbc_source=str(source.relative_to(ROOT)), can_id=f"0x{message.frame_id:X}",
        message=message.name, dbc_dlc=message.length, signal=signal.name,
        start_bit=signal.start, bit_length=signal.length, byte_order=signal.byte_order,
        signed=signal.is_signed, scale=signal.scale, offset=signal.offset,
        unit=signal.unit or "", multiplexer_signal=signal.multiplexer_signal or "",
        multiplexer_ids="/".join(map(str, signal.multiplexer_ids or [])),
    )


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    paths=sorted((ROOT/"dbc").glob("*.dbc"))+[ROOT/"input/tesla_model3_ONYX.dbc"]
    databases=[]; load_errors=[]
    for path in paths:
        try: databases.append((path,cantools.database.load_file(path,database_format="dbc",strict=False)))
        except Exception as exc: load_errors.append(dict(dbc_source=str(path.relative_to(ROOT)),error=str(exc)))

    asc_counts=Counter(); asc_dlcs={}
    with ASC.open(encoding="utf-8",errors="replace") as f:
        for line in f:
            m=ASC_RE.match(line)
            if m:
                fid=int(m.group(1),16); asc_counts[fid]+=1; asc_dlcs.setdefault(fid,set()).add(int(m.group(2)))

    plan=read_approved_csv(ROOT/"output/TM3-015/evidence_plan_approved.csv")
    approved_names={x.signal for x in plan.signals if not x.signal_key.endswith("_derived")}
    approved_ids={int(x.can_id,16) for x in plan.signals}

    exact=[]; same_id=[]; extras=[]
    for source,db in databases:
        for message in db.messages:
            for signal in message.signals:
                row=signal_row(source,message,signal)
                row["asc_frame_count"]=asc_counts[message.frame_id]
                row["asc_dlc"]="/".join(map(str,sorted(asc_dlcs.get(message.frame_id,set()))))
                if signal.name in approved_names: exact.append(row.copy())
                if message.frame_id in approved_ids: same_id.append(row.copy())
                if (RELEVANT.search(signal.name) or RELEVANT.search(message.name)) and signal.name not in approved_names and asc_counts[message.frame_id]:
                    extras.append(row.copy())

    fingerprints={}
    for row in exact:
        fingerprints.setdefault(row["signal"],set()).add(tuple(row[k] for k in ["can_id","dbc_dlc","start_bit","bit_length","byte_order","signed","scale","offset","unit","multiplexer_ids"]))
    conflicts=[]
    for name,defs in sorted(fingerprints.items()):
        if len(defs)>1:
            conflicts.append(dict(signal=name,definition_variants=len(defs),sources=sum(r["signal"]==name for r in exact),status="DBC_DEFINITION_CONFLICT"))

    write_csv(OUT/"approved_signal_definition_comparison.csv",exact)
    write_csv(OUT/"approved_can_id_all_signal_definitions.csv",same_id)
    write_csv(OUT/"additional_relevant_candidates_with_asc_frames.csv",extras)
    write_csv(OUT/"definition_conflicts.csv",conflicts)
    if load_errors: write_csv(OUT/"dbc_load_errors.csv",load_errors)

    by_source=Counter(r["dbc_source"] for r in exact)
    extra_names=sorted({r["signal"] for r in extras})
    lines=[
        "# TM3-015 全本地DBC横向定义审计", "",
        f"- 扫描DBC：{len(paths)}份；成功加载{len(databases)}份；失败{len(load_errors)}份。",
        f"- Approved原生Signal：{len(approved_names)}个；找到精确定义{len(exact)}条。",
        f"- 存在两个及以上不同定义指纹的Approved Signal：{len(conflicts)}个。",
        f"- 在本ASC确有报文、名称与充电/热管理相关但未进入Approved的额外Signal：{len(extra_names)}个（{len(extras)}条跨DBC定义）。", "",
        "## 各DBC命中Approved Signal", "",
        "| DBC | 定义条数 |", "| --- | ---: |",
        *[f"| `{k}` | {v} |" for k,v in sorted(by_source.items())], "",
        "## 定义冲突", "",
        "| Signal | 定义变体 | 来源定义数 |", "| --- | ---: | ---: |",
        *[f"| `{r['signal']}` | {r['definition_variants']} | {r['sources']} |" for r in conflicts], "",
        "完整位段、缩放、偏置、符号、单位及复用定义见`approved_signal_definition_comparison.csv`。冲突只说明字典版本不一致，不自动说明车辆异常。", "",
        "## 额外候选边界", "",
        "额外候选只因名称相关且本ASC中存在对应CAN ID而列出，未经过控制树角色审核，不进入TM3-015既有Assessment或结论。完整列表见`additional_relevant_candidates_with_asc_frames.csv`。",
    ]
    (OUT/"全本地DBC横向定义审计.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(f"dbcs={len(paths)} loaded={len(databases)} errors={len(load_errors)}")
    print(f"exact_definitions={len(exact)} conflicts={len(conflicts)} extra_unique={len(extra_names)} extra_rows={len(extras)}")


if __name__ == "__main__": main()
