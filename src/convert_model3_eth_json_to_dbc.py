"""Convert Model3_ETH.compact.json into an optional reference DBC.

The generated database is never an authoritative or mandatory vehicle DBC.
Big-endian start-bit notation is adapted from an existing same-ID/same-name
DBC definition where possible and explicitly audited otherwise.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, OrderedDict
from pathlib import Path

import cantools
from cantools.database.can import Database, Message, Signal
from cantools.database.conversion import BaseConversion

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "dbc/Model3_ETH.compact.json"
TARGET = ROOT / "dbc/Model3_ETH_json_reference_optional.dbc"
MANIFEST = ROOT / "dbc/Model3_ETH_json_reference_optional.manifest.json"
AUDIT = ROOT / "dbc/Model3_ETH_json_reference_optional_conversion_audit.csv"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source=json.loads(SOURCE.read_text(encoding="utf-8"))
    references={}
    for path in sorted((ROOT/"dbc").glob("*.dbc"))+[ROOT/"input/tesla_model3_ONYX.dbc"]:
        if path==TARGET: continue
        try: db=cantools.database.load_file(path,database_format="dbc",strict=False)
        except Exception: continue
        for message in db.messages:
            for signal in message.signals:
                references.setdefault((message.frame_id,signal.name),[]).append((path,signal))

    messages=[]; audit=[]; policy_counts=Counter()
    for message_name,item in source["messages"].items():
        fid=int(item["message_id"]); mux_names=[n for n,s in item.get("signals",{}).items() if s.get("is_muxer")]
        mux_name=mux_names[0] if mux_names else None
        signals=[]
        for name,data in item.get("signals",{}).items():
            json_endian=data.get("endianness","LITTLE")
            byte_order="little_endian" if json_endian=="LITTLE" else "big_endian"
            start=int(data.get("start_position",0)); policy="JSON_DIRECT"
            reference_source=""
            if byte_order=="big_endian" and (fid,name) in references:
                # DBC Motorola start-bit notation is not the same convention as
                # the compact JSON position. Reuse a known local representation.
                ref_path,ref_signal=references[(fid,name)][0]
                start=ref_signal.start; byte_order=ref_signal.byte_order
                policy="LOCAL_DBC_START_BIT_ADAPTATION"
                reference_source=str(ref_path.relative_to(ROOT))
            elif byte_order=="big_endian":
                policy="JSON_BIG_ENDIAN_UNVERIFIED_START"
            choices=data.get("value_description") or {}
            ordered=OrderedDict()
            for label,value in choices.items():
                try: ordered[int(value)]=str(label)
                except (TypeError,ValueError): pass
            conversion=BaseConversion.factory(scale=float(data.get("scale",1)),offset=float(data.get("offset",0)),choices=ordered or None,is_float=False)
            signal=Signal(
                name=name,start=start,length=int(data["width"]),byte_order=byte_order,
                is_signed=data.get("signedness")=="SIGNED",conversion=conversion,
                minimum=data.get("min"),maximum=data.get("max"),unit=data.get("units") or None,
                comment=f"REFERENCE_OPTIONAL; source={SOURCE.name}; json_start_position={data.get('start_position')}; conversion_policy={policy}",
                receivers=list(data.get("receivers",[])),is_multiplexer=bool(data.get("is_muxer")),
                multiplexer_ids=[int(data["mux_id"])] if "mux_id" in data else None,
                multiplexer_signal=mux_name if "mux_id" in data else None,
            )
            signals.append(signal); policy_counts[policy]+=1
            audit.append(dict(message=message_name,can_id=f"0x{fid:X}",signal=name,
                              json_start_position=data.get("start_position"),dbc_start_bit=start,
                              json_endianness=json_endian,dbc_byte_order=byte_order,
                              bit_length=data["width"],conversion_policy=policy,
                              reference_source=reference_source,mux_id=data.get("mux_id","")))
        messages.append(Message(
            frame_id=fid,name=message_name,length=int(item["length_bytes"]),signals=signals,
            comment=(f"REFERENCE_OPTIONAL converted from {SOURCE.name}; product={source.get('product')}; "
                     f"version={source.get('version')}; bus={source.get('busMetadata',{}).get('name')}; "
                     "not an authoritative vehicle definition"),
            senders=list(item.get("senders",[])),send_type=item.get("send_type"),
            cycle_time=item.get("cycle_time"),strict=False,sort_signals=None,
        ))
    database=Database(messages=messages,version=f"JSON_REFERENCE_OPTIONAL_{source.get('version','unknown')}",strict=False,sort_signals=None)
    cantools.database.dump_file(database,TARGET,database_format="dbc",encoding="utf-8",sort_signals=None)

    # Mandatory round-trip validation.
    loaded=cantools.database.load_file(TARGET,database_format="dbc",strict=False)
    loaded_signals=sum(len(m.signals) for m in loaded.messages)
    with AUDIT.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(audit[0])); w.writeheader(); w.writerows(audit)
    manifest=dict(
        status="REFERENCE_OPTIONAL",mandatory=False,authoritative=False,
        source=str(SOURCE.relative_to(ROOT)),source_sha256=sha(SOURCE),
        source_product=source.get("product"),source_version=source.get("version"),
        source_bus=source.get("busMetadata",{}).get("name"),
        output=str(TARGET.relative_to(ROOT)),output_sha256=sha(TARGET),
        messages_expected=len(messages),messages_roundtrip=len(loaded.messages),
        signals_expected=len(audit),signals_roundtrip=loaded_signals,
        conversion_policy_counts=dict(policy_counts),
        roundtrip_pass=len(messages)==len(loaded.messages) and len(audit)==loaded_signals,
        usage_boundary=("Candidate parsing source only. Compare ID/DLC/bit layout/mux and validate against "
                        "experiment events before using a signal in Evidence Assessment."),
    )
    MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(manifest,ensure_ascii=False,indent=2))


if __name__=="__main__": main()
