"""Isolated Phase 2.6 dynamic semantic-reasoning validation for TM3-015.

This spike imports the Phase 2.5 discovery kernel, builds a frozen reasoning
package from pre-analysis sources, validates a bounded LLM result, executes at
most one deterministic follow-up, and performs a post-freeze hidden comparison.
It is intentionally disconnected from Evidence Plan, RVM, renderer, and formal
report generation.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re
from statistics import mean
import sys
from typing import Any

import cantools

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from spikes.semantic_coverage_residual_discovery import parse_asc_line, run_spike


ROOT = Path(__file__).resolve().parents[1]
ASC = ROOT / "input" / "can_20260831102614_TM3-015_直流快充采集.asc"
DBC = ROOT / "input" / "tesla_model3_ONYX.dbc"
PRIOR_CONTEXT = ROOT / "output" / "TM3-015" / "evidence_plan_context.md"
PRIOR_GUIDE = ROOT / "doc" / "TM3-015_016扫码充电采集指导.md"
SCHEMA = ROOT / "spikes" / "contracts" / "semantic_reasoning_v1.schema.json"

CONTRACT_VERSION = "semantic-reasoning-v1"
PACKAGE_ID = "SRP-TM3-015-DCFC-v1"
ALLOWED_FOLLOW_UP = {"TARGETED_WINDOW_STATS"}
ER_STATUSES = {"DIRECT_SUPPORT", "PARTIAL_SUPPORT", "CONTRADICTION", "UNRELATED", "INSUFFICIENT"}
CLAIM_CLASSES = {"OBSERVED", "DERIVED", "INFERRED", "UNSUPPORTED"}
CAUSALITY_STATUSES = {
    "TEMPORAL_ASSOCIATION_ONLY", "CONTROL_RELATION_SUPPORTED",
    "CAUSALITY_NOT_ESTABLISHED", "NOT_APPLICABLE",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def object_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def source_ref(path: Path, anchors: list[str]) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": sha256_file(path),
        "anchors": anchors,
    }


CONTROL_NODES = [
    ("CT-DCFC-01", "连接检测与锁止", "车辆识别充电连接、线缆与锁止状态。"),
    ("CT-DCFC-02", "可见通信与协商", "当前车内CAN域可见的EVSE类型、通信或协商状态。"),
    ("CT-DCFC-03", "整车、电池与安全条件", "挡位、整车、电池及安全条件背景。"),
    ("CT-DCFC-04", "车辆侧充电条件判断与许可", "车辆内部许可节点；缺少直接Signal时必须保留缺口。"),
    ("CT-DCFC-05", "高压直流充电状态", "高压充电状态、接触器和相关执行状态。"),
    ("CT-DCFC-06", "直流电压建立", "CP侧可见直流电压建立；不等同桩内部许可。"),
    ("CT-DCFC-07", "直流电流建立", "CP和Pack侧电流响应建立。"),
    ("CT-DCFC-08", "短时稳定运行", "条件化短稳态，不外推峰值或全SOC曲线。"),
    ("CT-DCFC-09", "停止请求候选", "外部停止之后车辆侧可见的停止请求或状态候选。"),
    ("CT-DCFC-10", "电流与充电状态退出", "输出电流退出及车辆充电状态退出。"),
    ("CT-DCFC-11", "连接释放", "锁止释放和拔枪收尾；安全事实依赖外部证据。"),
    ("CT-ENERGY-01", "能源交叉验证", "CP侧与Pack侧电压、电流、功率的边界化交叉验证。"),
    ("CT-THERMAL-01", "热管理独立副线", "Pack热状态、请求、执行反馈与温度响应。"),
]

EVIDENCE_REQUIREMENTS = [
    ("ER-01", "区分充电口开启与插枪/锁止。", "至少需要外部事件时间；CAN状态只能作为车型投射。"),
    ("ER-02", "车辆识别直流连接并进入可见协商过程。", "多个同层状态顺序一致；单一位不足以确认完整握手。"),
    ("ER-03", "车辆侧条件/许可与高压直流充电状态建立。", "许可/状态须与电流建立相容；单一接触器枚举不充分。"),
    ("ER-04", "实际直流电流建立并与CP及Pack能源响应对应。", "以电流建立定义启动；方向、量级和时序相容。"),
    ("ER-05", "形成可描述的短时充电窗口。", "连续20至30秒相对稳定；否则只分析启动或爬升。"),
    ("ER-06", "停止请求后输出电流和充电状态退出。", "需要实际停止入口；分析请求、退出和持续归零。"),
    ("ER-07", "枪锁释放与拔枪形成独立收尾。", "安全操作实录为主；CAN不得代替安全确认。"),
    ("ER-08", "记录条件、能力和告警边界。", "只作为工况背景；告警计数不能单独形成故障判断。"),
    ("ER-09", "记录整车状态门作为充电条件背景。", "只说明状态共存，不反推OEM完整许可规则。"),
    ("ER-10", "Pack热状态、请求与执行响应形成独立副线。", "先验证DBC适配，再分析请求、目标、执行和温度响应。"),
]

PRIOR_SIGNALS = {
    "CP_chargeDoorOpen", "CP_chargeCablePresent", "CP_chargeCableSecured",
    "CP_chargeCableState", "CP_latchState", "CP_evseChargeType", "CP_gbState",
    "CP_evseRequest", "CP_evseAccept", "CP_hvChargeStatus", "CP_stopChargeRequest",
    "CP_evseOutputDcVoltage", "CP_evseOutputDcCurrent",
    "BMS_chargeRequest", "BMS_uiChargeStatus", "BMS_hvState", "BMS_contactorState",
    "BMS_packVoltage", "BMS_packCurrent", "BMS_chgPowerAvailable",
    "BMS_maxChargeCurrent", "BMS_socUI", "DI_gear", "DI_systemState",
    "UI_chargeEnableRequest", "HVP_fcContactorSetState", "HVP_packContactorSetState",
    "BMS_modelTMax", "BMS_flowRequest", "BMS_inletActiveCoolTargetT",
    "BMS_inletActiveHeatTargetT", "VCFRONT_tempCoolantBatInlet",
    "VCFRONT_coolantFlowBatTarget", "VCFRONT_coolantFlowBatActual",
    "VCFRONT_pumpBatteryRPMTarget", "VCFRONT_pumpBatteryRPMActual",
}


def make_prior() -> dict[str, Any]:
    context_ref = source_ref(PRIOR_CONTEXT, ["§2 实验目的与系统边界", "§3 Control Relationship View", "§4 Evidence Requirements", "§5 关键审核边界"])
    guide_ref = source_ref(PRIOR_GUIDE, ["目标证据链", "直流快充", "采集与分析注意事项"])
    nodes = []
    for node_id, name, definition in CONTROL_NODES:
        node = {
            "node_id": node_id,
            "name": name,
            "definition": definition,
            "source_ref": context_ref,
        }
        node["fingerprint"] = object_hash({k: node[k] for k in ("node_id", "name", "definition")})[:16]
        nodes.append(node)
    requirements = []
    for requirement_id, statement, sufficiency in EVIDENCE_REQUIREMENTS:
        requirement = {
            "evidence_requirement_id": requirement_id,
            "statement": statement,
            "sufficiency_rule": sufficiency,
            "source_ref": context_ref,
        }
        requirement["fingerprint"] = object_hash({
            "id": requirement_id, "statement": statement, "sufficiency": sufficiency,
        })[:16]
        requirements.append(requirement)
    return {
        "position": "PROBLEM_DOMAIN_SEMANTIC_PRIOR_NOT_OBSERVATION_WHITELIST",
        "system": "直流快充系统",
        "system_boundary": {
            "inside": ["车辆充电口与连接检测", "车辆侧充电状态与许可", "BMS高压及Pack响应", "可见低压与热状态"],
            "outside": ["人工操作", "运营商平台与支付网络", "桩内部控制", "车内CAN不可见协议", "桩端物理测量"],
        },
        "control_mainlines": [
            {
                "mainline_id": "CML-DCFC-START",
                "node_refs": [f"CT-DCFC-{index:02d}" for index in range(1, 9)],
                "source_ref": context_ref,
            },
            {
                "mainline_id": "CML-DCFC-STOP",
                "node_refs": ["CT-DCFC-09", "CT-DCFC-10", "CT-DCFC-11"],
                "source_ref": context_ref,
            },
            {
                "mainline_id": "CML-DCFC-ENERGY",
                "node_refs": ["CT-ENERGY-01"],
                "source_ref": guide_ref,
            },
            {
                "mainline_id": "CML-DCFC-THERMAL",
                "node_refs": ["CT-THERMAL-01"],
                "source_ref": context_ref,
            },
        ],
        "control_tree_nodes": nodes,
        "evidence_requirements": requirements,
        "known_dbc_uncertainties": [
            {"uncertainty_id": "DU-01", "statement": "CP连接、协商和输出定义来自社区DBC，实车语义未经自动确认。", "source_ref": context_ref},
            {"uncertainty_id": "DU-02", "statement": "CP_gbState存在跨DBC位段和位宽差异。", "source_ref": context_ref},
            {"uncertainty_id": "DU-03", "statement": "0x27D在不同DBC中存在严重节点绑定冲突。", "source_ref": context_ref},
            {"uncertainty_id": "DU-04", "statement": "BMS_packCurrent存在符号与偏置定义差异。", "source_ref": context_ref},
            {"uncertainty_id": "DU-05", "statement": "CP与Pack属于不同测量边界，不能直接推算充电效率。", "source_ref": context_ref},
            {"uncertainty_id": "DU-06", "statement": "热管理Signal须先验证DBC适配和MUX适用性。", "source_ref": context_ref},
        ],
        "source_refs": [context_ref, guide_ref],
    }


def observation_id(signal_key: str) -> str:
    return "O-" + hashlib.sha256(signal_key.encode("utf-8")).hexdigest()[:12].upper()


def select_observations(discovery: dict[str, Any]) -> list[dict[str, Any]]:
    coverage_by_bus: dict[str, set[str]] = {}
    for row in discovery["dbc_coverage"]:
        coverage_by_bus.setdefault(row["bus_key"], set()).add(row["coverage_class"])
    ranked = []
    relevant_pattern = re.compile(
        r"(?:charge|evse|cable|latch|contactor|pack(?:current|voltage)|soc|thermal|coolant|pump|compressor|hvstate)",
        re.IGNORECASE,
    )
    for summary in discovery["signal_summaries"]:
        score = 0
        if summary["signal_name"] in PRIOR_SIGNALS:
            score += 100
        if relevant_pattern.search(summary["signal_name"]):
            score += 45
        if summary["change_count"]:
            score += 25
        if summary["sna_count"] or summary["out_of_dbc_range_count"]:
            score += 15
        if not score:
            continue
        ranked.append((score, summary))
    ranked.sort(key=lambda item: (-item[0], -item[1]["change_count"], item[1]["signal_name"]))
    selected = []
    for _, summary in ranked[:120]:
        coverage = sorted(coverage_by_bus.get(summary["bus_key"], {"UNMATCHED"}))
        flags = []
        if coverage != ["MATCHED"]:
            flags.append("DBC_COVERAGE_" + "+".join(coverage))
        if summary["sna_count"]:
            flags.append("SNA_OR_INVALID_PRESENT")
        if summary["out_of_dbc_range_count"]:
            flags.append("OUT_OF_DBC_RANGE")
        semantic_status = "VALIDATION_REQUIRED" if flags else "UNVALIDATED"
        selected.append({
            "observation_id": observation_id(summary["signal_key"]),
            "observation_class": "DIRECTLY_OBSERVED",
            "signal_ref": {
                "signal_key": summary["signal_key"],
                "signal_name": summary["signal_name"],
                "bus_key": summary["bus_key"],
                "dbc_source": summary["dbc_source"],
                "definition_fingerprint": summary["definition_fingerprint"],
                "unit": summary["unit"],
            },
            "semantic_status": semantic_status,
            "dbc_coverage": coverage,
            "observed_summary": (
                f"{summary['sample_count']} samples; {summary['change_count']} changes; "
                f"range={summary['minimum']}..{summary['maximum']}; current={summary['current_value']}"
            ),
            "state_changes": {
                "first_change_can_time_s": summary["first_change_time_s"],
                "last_change_can_time_s": summary["last_change_time_s"],
                "sequence_prefix": summary["sequence"],
            },
            "deterministic_metrics": {
                key: summary[key] for key in (
                    "sample_count", "minimum", "maximum", "mean", "standard_deviation",
                    "cardinality", "change_count", "stability_class", "sna_count",
                    "out_of_dbc_range_count", "current_value",
                )
            },
            "raw_refs": summary["raw_refs"],
            "quality_flags": flags,
        })
    return selected


def build_input(output: Path, discovery_cache: Path | None = None) -> dict[str, Any]:
    if discovery_cache:
        discovery = json.loads(discovery_cache.read_text(encoding="utf-8"))
    else:
        discovery = run_spike(
            ASC, [DBC],
            domain="直流快充L3语义域；L3是Semantic Prior而非Observation Whitelist",
            conditions=["P挡", "车辆已唤醒", "起始未插枪", "直流快充短时采集"],
            windows=[
                {"label": "planned_background", "start_s": 0.0, "end_s": 20.0},
                {"label": "planned_connection", "start_s": 20.0, "end_s": 60.0},
                {"label": "planned_authorization", "start_s": 60.0, "end_s": 120.0},
                {"label": "planned_charge", "start_s": 120.0, "end_s": 240.0},
                {"label": "planned_stop_release", "start_s": 240.0, "end_s": 300.0},
            ],
        )
    prior = make_prior()
    observations = select_observations(discovery)
    observation_by_signal_key = {
        row["signal_ref"]["signal_key"]: row["observation_id"] for row in observations
    }
    candidates = []
    for candidate in discovery["llm_package"]["candidates"]:
        item = dict(candidate)
        item["observation_refs"] = [
            observation_by_signal_key[ref]
            for ref in candidate.get("related_observation_refs", [])
            if ref in observation_by_signal_key
        ]
        item["kernel_related_refs"] = item.pop("related_observation_refs", [])
        candidates.append(item)
    relations = []
    for candidate in candidates:
        if candidate["candidate_type"] not in {"MIN_MAX_ORDER_VIOLATION", "SIGNAL_FAMILY_SUM_VS_TOTAL"}:
            continue
        relations.append({
            "relation_id": "R-" + candidate["candidate_id"],
            "relation_type": candidate["candidate_type"],
            "input_refs": candidate["observation_refs"] or [candidate["candidate_id"]],
            "deterministic_result": candidate["metrics"],
            "tolerance": None,
            "status": "CONFLICT" if "VIOLATION" in candidate["candidate_type"] else "CLOSURE_CANDIDATE",
            "raw_refs": candidate["raw_refs"],
        })
    dynamic = [row for row in observations if row["state_changes"]["first_change_can_time_s"] is not None]
    dynamic.sort(key=lambda row: (
        0 if row["signal_ref"]["signal_name"] in PRIOR_SIGNALS else 1,
        row["state_changes"]["first_change_can_time_s"], row["signal_ref"]["signal_name"],
    ))
    can_events = [
        {
            "event_id": "EA-" + row["observation_id"][2:],
            "event_type": "SIGNAL_FIRST_CHANGE",
            "time_type": "CAN_OBSERVED_TIME",
            "time_s": row["state_changes"]["first_change_can_time_s"],
            "source": "CAN_OBSERVED_STATE",
            "time_uncertainty_s": None,
            "description": f"{row['signal_ref']['signal_name']} first decoded change; physical semantics remain {row['semantic_status']}",
            "observation_refs": [row["observation_id"]],
            "raw_refs": row["raw_refs"][:2],
        }
        for row in dynamic[:40]
    ]
    package = {
        "contract_version": CONTRACT_VERSION,
        "package_id": PACKAGE_ID,
        "package_hash": "",
        "experiment_context": {
            "experiment_id": "TM3-015",
            "experiment_goal": "验证直流快充启动、稳定运行与停止退出的L3语义映射和证据缺口。",
            "purpose": "NORMAL_BASELINE_DYNAMIC_SEMANTIC_VALIDATION_SPIKE",
            "analysis_mode": "EVENT_DRIVEN",
            "vehicle_context": "Tesla Model 3 上海产2021款 标准续航 55 kWh 后驱",
            "collection_conditions": ["P挡", "车辆已唤醒", "开始时未插枪", "短时直流快充"],
            "observed_event_time_status": "MISSING",
            "known_limitations": [
                "计划时间不是人工实际事件时间。",
                "CAN状态变化不能反推人工插枪、扫码、停止或拔枪时刻。",
                "当前车内CAN域不覆盖桩内部控制和完整协议。",
            ],
            "source_artifacts": [
                {"role": "ASC", "path": str(ASC.relative_to(ROOT)), "sha256": sha256_file(ASC)},
                {"role": "DBC", "path": str(DBC.relative_to(ROOT)), "sha256": sha256_file(DBC)},
            ],
        },
        "l3_context": prior,
        "discovery_summary": {
            "kernel": "spikes.semantic_coverage_residual_discovery.run_spike",
            "kernel_schema_version": discovery["schema_version"],
            "asc_integrity": discovery["asc_integrity"],
            "coverage_summary": discovery["coverage_summary"],
            "bus_variant_count": len(discovery["bus_inventory"]),
            "decoded_signal_summary_count": len(discovery["signal_summaries"]),
            "compressed_candidate_count": len(discovery["candidates"]),
            "llm_candidate_count": len(candidates),
        },
        "event_anchors": can_events,
        "observations": observations,
        "candidates": candidates,
        "consistency_results": relations,
        "validation_states": [],
        "allowed_follow_up_operations": [
            {
                "operation": "TARGETED_WINDOW_STATS",
                "maximum_requests": 1,
                "description": "Re-decode referenced known signals in one bounded ASC window and return deterministic values/transitions.",
            }
        ],
        "reasoning_rules": [
            "L3 is a semantic prior, not an observation whitelist.",
            "Do not treat planned time as observed event time.",
            "Do not infer human action time from CAN state changes.",
            "Temporal order does not establish causality.",
            "Do not invent missing request, permission, protocol, or charger-internal evidence.",
            "DBC names and decoded values remain unvalidated semantics unless independent evidence supports them.",
            "Unknown and residual candidates may use NO_SAFE_MAPPING.",
            "Use only numeric values present in observation, relation, candidate, or follow-up objects.",
        ],
        "hidden_comparison_policy": {
            "status": "LOCKED_UNTIL_REASONING_OUTPUT_FROZEN",
            "forbidden_initial_sources": [
                "output/TM3-015/TM3-015_最终报告.md",
                "output/TM3-015/events.csv",
                "output/TM3-015/evidence_assessment.csv",
                "output/TM3-015/energy_dbc_adaptation/",
                "output/TM3-015/analysis_audit.json",
            ],
        },
    }
    package["package_hash"] = object_hash({**package, "package_hash": ""})
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(package, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return package


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_input(package: dict[str, Any]) -> list[str]:
    errors = []
    expected_hash = object_hash({**package, "package_hash": ""})
    if package.get("package_hash") != expected_hash:
        errors.append("INPUT_PACKAGE_HASH_MISMATCH")
    serialized = json.dumps(package, ensure_ascii=False)
    for forbidden in package["hidden_comparison_policy"]["forbidden_initial_sources"]:
        occurrences = serialized.count(forbidden)
        if occurrences != 1:
            errors.append(f"FORBIDDEN_SOURCE_REFERENCE_COUNT:{forbidden}:{occurrences}")
    if package["experiment_context"].get("observed_event_time_status") != "MISSING":
        errors.append("OBSERVED_EVENT_TIME_MUST_REMAIN_MISSING")
    for source in package["l3_context"]["source_refs"]:
        if not source.get("sha256") or not source.get("anchors"):
            errors.append("L3_SOURCE_WITHOUT_FINGERPRINT_OR_ANCHOR")
    return errors


def reference_sets(package: dict[str, Any], output: dict[str, Any] | None = None) -> dict[str, set[str]]:
    refs = {
        "observations": {row["observation_id"] for row in package["observations"]},
        "candidates": {row["candidate_id"] for row in package["candidates"]},
        "relations": {row["relation_id"] for row in package["consistency_results"]},
        "events": {row["event_id"] for row in package["event_anchors"]},
        "nodes": {row["node_id"] for row in package["l3_context"]["control_tree_nodes"]},
        "requirements": {row["evidence_requirement_id"] for row in package["l3_context"]["evidence_requirements"]},
    }
    refs["all_input"] = set().union(*refs.values())
    if output and output.get("follow_up_result"):
        refs["follow_up"] = {output["follow_up_result"].get("result_id", "")}
        refs["all_input"].update(refs["follow_up"])
    return refs


def validate_output(package: dict[str, Any], output: dict[str, Any]) -> list[str]:
    errors = validate_input(package)
    required_output = {
        "contract_version", "result_id", "input_package_id", "input_package_hash",
        "initial_reasoning", "follow_up_result", "updated_reasoning", "audit_metadata",
    }
    required_pass = {"pass_id", "findings", "validation_requests"}
    required_finding = {
        "finding_id", "candidate_refs", "observation_refs", "relation_refs", "event_refs",
        "fact_bindings", "l3_domain_mapping", "control_tree_mapping",
        "evidence_requirement_mapping", "relationship_kind", "causality_status",
        "semantic_hypothesis", "alternative_explanations", "model_interaction",
        "supported_claims", "unsupported_claims", "missing_evidence",
        "signal_validation_needed", "minimum_next_check", "uncertainty", "confidence",
        "trace_refs",
    }
    for key in sorted(required_output - set(output)):
        errors.append(f"OUTPUT_REQUIRED_FIELD_MISSING:{key}")
    if output.get("contract_version") != CONTRACT_VERSION:
        errors.append("OUTPUT_CONTRACT_VERSION_MISMATCH")
    if output.get("input_package_id") != package["package_id"]:
        errors.append("OUTPUT_PACKAGE_ID_MISMATCH")
    if output.get("input_package_hash") != package["package_hash"]:
        errors.append("OUTPUT_PACKAGE_HASH_MISMATCH")
    refs = reference_sets(package, output)
    initial_requests = output.get("initial_reasoning", {}).get("validation_requests", [])
    updated_requests = output.get("updated_reasoning", {}).get("validation_requests", [])
    if len(initial_requests) > 1 or updated_requests:
        errors.append("FOLLOW_UP_LIMIT_EXCEEDED")
    for request in initial_requests:
        if request.get("operation") not in ALLOWED_FOLLOW_UP:
            errors.append(f"FOLLOW_UP_OPERATION_NOT_ALLOWED:{request.get('operation')}")
        for ref in request.get("input_refs", []):
            if ref not in refs["observations"]:
                errors.append(f"FOLLOW_UP_UNKNOWN_OBSERVATION:{ref}")
    for pass_name in ("initial_reasoning", "updated_reasoning"):
        reasoning_pass = output.get(pass_name, {})
        for key in sorted(required_pass - set(reasoning_pass)):
            errors.append(f"{pass_name}:REQUIRED_FIELD_MISSING:{key}")
        for finding in reasoning_pass.get("findings", []):
            finding_id = finding.get("finding_id", "MISSING")
            for key in sorted(required_finding - set(finding)):
                errors.append(f"{finding_id}:REQUIRED_FIELD_MISSING:{key}")
            for field, ref_type in (
                ("candidate_refs", "candidates"), ("observation_refs", "observations"),
                ("relation_refs", "relations"), ("event_refs", "events"),
            ):
                for ref in finding.get(field, []):
                    if ref not in refs[ref_type]:
                        errors.append(f"{finding_id}:UNKNOWN_{field.upper()}:{ref}")
            mapping = finding.get("control_tree_mapping", {})
            node_ref = mapping.get("node_ref")
            if node_ref not in refs["nodes"] | {"NO_SAFE_MAPPING"}:
                errors.append(f"{finding_id}:UNKNOWN_CONTROL_NODE:{node_ref}")
            for item in finding.get("evidence_requirement_mapping", []):
                er = item.get("evidence_requirement_ref")
                if er not in refs["requirements"]:
                    errors.append(f"{finding_id}:UNKNOWN_EVIDENCE_REQUIREMENT:{er}")
                if item.get("status") not in ER_STATUSES:
                    errors.append(f"{finding_id}:INVALID_ER_STATUS:{item.get('status')}")
                for ref in item.get("basis_refs", []):
                    if ref not in refs["all_input"]:
                        errors.append(f"{finding_id}:UNKNOWN_ER_BASIS:{ref}")
            if finding.get("causality_status") not in CAUSALITY_STATUSES:
                errors.append(f"{finding_id}:INVALID_CAUSALITY_STATUS")
            for fact in finding.get("fact_bindings", []):
                claim_class = fact.get("claim_class")
                support = fact.get("support_refs", [])
                if claim_class not in CLAIM_CLASSES:
                    errors.append(f"{finding_id}:INVALID_CLAIM_CLASS:{claim_class}")
                if claim_class == "OBSERVED" and not support:
                    errors.append(f"{finding_id}:OBSERVED_WITHOUT_REFERENCE")
                if claim_class == "DERIVED" and not support:
                    errors.append(f"{finding_id}:DERIVED_WITHOUT_REFERENCE")
                if claim_class in {"OBSERVED", "DERIVED"}:
                    for ref in support:
                        if ref not in refs["all_input"]:
                            errors.append(f"{finding_id}:UNKNOWN_FACT_REFERENCE:{ref}")
            inferred = any(x.get("claim_class") == "INFERRED" for x in finding.get("fact_bindings", []))
            if inferred and not finding.get("alternative_explanations"):
                errors.append(f"{finding_id}:INFERENCE_WITHOUT_ALTERNATIVE")
            for ref in finding.get("trace_refs", []):
                if ref not in refs["all_input"]:
                    errors.append(f"{finding_id}:UNKNOWN_TRACE_REF:{ref}")
    return sorted(set(errors))


def execute_follow_up(package: dict[str, Any], output: dict[str, Any]) -> dict[str, Any]:
    requests = output["initial_reasoning"].get("validation_requests", [])
    if len(requests) != 1:
        raise ValueError("exactly one initial follow-up request is required for this run")
    request = requests[0]
    if request["operation"] != "TARGETED_WINDOW_STATS":
        raise ValueError("unsupported follow-up operation")
    observations = {row["observation_id"]: row for row in package["observations"]}
    selected = [observations[ref] for ref in request["input_refs"]]
    start_s = float(request["parameters"]["start_s"])
    end_s = float(request["parameters"]["end_s"])
    database = cantools.database.load_file(DBC, strict=False)
    targets: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for observation in selected:
        bus_key = observation["signal_ref"]["bus_key"]
        match = re.fullmatch(r"ch([^:]+):0x([0-9A-F]+)(x?)", bus_key)
        if not match:
            raise ValueError(f"invalid bus key {bus_key}")
        frame_format = "EXTENDED" if match.group(3) else "STANDARD"
        targets.setdefault((frame_format, int(match.group(2), 16)), []).append(observation)
    accumulators = {
        row["observation_id"]: {"values": [], "transitions": [], "previous": None}
        for row in selected
    }
    with ASC.open(encoding="utf-8", errors="replace") as source:
        for line_number, line in enumerate(source, 1):
            frame = parse_asc_line(line, line_number)
            if frame is None or not (start_s <= frame.time_s <= end_s):
                continue
            frame_targets = targets.get((frame.bus_key.frame_format, frame.bus_key.can_id))
            if not frame_targets:
                continue
            try:
                message = database.get_message_by_frame_id(frame.bus_key.can_id)
                decoded = message.decode(frame.data, decode_choices=True, allow_truncated=True)
            except Exception:
                continue
            for observation in frame_targets:
                name = observation["signal_ref"]["signal_name"]
                if name not in decoded:
                    continue
                value = decoded[name]
                acc = accumulators[observation["observation_id"]]
                acc["values"].append((frame.time_s, value, frame.raw_ref()))
                display = str(value)
                if acc["previous"] is not None and display != acc["previous"] and len(acc["transitions"]) < 32:
                    acc["transitions"].append({"can_time_s": frame.time_s, "value": display, "raw_ref": frame.raw_ref()})
                acc["previous"] = display
    results = []
    for observation in selected:
        acc = accumulators[observation["observation_id"]]
        values = acc["values"]
        numeric = [float(value) for _, value, _ in values if isinstance(value, (int, float)) and math.isfinite(float(value))]
        results.append({
            "observation_ref": observation["observation_id"],
            "signal_name": observation["signal_ref"]["signal_name"],
            "window_s": [start_s, end_s],
            "sample_count": len(values),
            "first_value": str(values[0][1]) if values else None,
            "last_value": str(values[-1][1]) if values else None,
            "minimum": min(numeric) if numeric else None,
            "maximum": max(numeric) if numeric else None,
            "mean": mean(numeric) if numeric else None,
            "transitions": acc["transitions"],
            "first_raw_ref": values[0][2] if values else None,
            "last_raw_ref": values[-1][2] if values else None,
        })
    return {
        "request_id": request["request_id"],
        "operation": request["operation"],
        "result_id": "FU-" + object_hash({"request": request, "results": results})[:16].upper(),
        "method": "Fresh ASC decode using the current DBC; bounded inclusive time window; transitions capped at 32 per signal.",
        "parameters": request["parameters"],
        "results": results,
        "limitations": [
            "All returned times are CAN_OBSERVED_TIME.",
            "No returned transition is an independently observed human event.",
            "DBC semantic and quantitative validity is not upgraded by this calculation.",
        ],
    }


def hidden_compare(package: dict[str, Any], output: dict[str, Any]) -> dict[str, Any]:
    evidence_path = ROOT / "output" / "TM3-015" / "evidence_assessment.csv"
    events_path = ROOT / "output" / "TM3-015" / "events.csv"
    energy_path = ROOT / "output" / "TM3-015" / "energy_dbc_adaptation" / "energy_chain_summary.json"
    report_path = ROOT / "output" / "TM3-015" / "TM3-015_最终报告.md"
    with evidence_path.open(encoding="utf-8-sig", newline="") as source:
        historical_er = {row["requirement_id"]: row for row in csv.DictReader(source)}
    # Updated findings are deltas over the immutable initial pass.  Start with
    # the initial ER assessment and replace only ERs revisited after follow-up.
    llm_er: dict[str, list[str]] = {}
    for finding in output["initial_reasoning"]["findings"]:
        for mapping in finding["evidence_requirement_mapping"]:
            llm_er.setdefault(mapping["evidence_requirement_ref"], []).append(mapping["status"])
    updated_er: dict[str, list[str]] = {}
    for finding in output["updated_reasoning"]["findings"]:
        for mapping in finding["evidence_requirement_mapping"]:
            updated_er.setdefault(mapping["evidence_requirement_ref"], []).append(mapping["status"])
    llm_er.update(updated_er)
    rows = []
    matches = 0
    for er_id in sorted(historical_er):
        predicted = sorted(set(llm_er.get(er_id, [])))
        historical = historical_er[er_id]["status"]
        compatible = (
            historical == "SUPPORTED" and bool(set(predicted) & {"DIRECT_SUPPORT", "PARTIAL_SUPPORT"})
        ) or (
            historical == "INSUFFICIENT_EVIDENCE" and bool(set(predicted) & {"INSUFFICIENT", "PARTIAL_SUPPORT", "CONTRADICTION"})
        ) or (
            historical == "NOT_OBSERVED" and bool(set(predicted) & {"INSUFFICIENT", "UNRELATED"})
        )
        matches += int(compatible)
        rows.append({
            "evidence_requirement_id": er_id,
            "llm_statuses": predicted,
            "historical_status": historical,
            "compatible": compatible,
            "historical_limitation": historical_er[er_id]["limitation"],
        })
    updated = output["updated_reasoning"]
    output_text = json.dumps(updated, ensure_ascii=False)
    unsupported_text = " ".join(
        claim
        for finding in updated["findings"]
        for claim in finding.get("unsupported_claims", [])
    )
    semantic_checks = {
        "separates_cp_current_timing_from_quantitative_validity": all(token in output_text for token in ("CP_evseOutputDcCurrent", "定量", "时序")),
        "recognizes_pack_energy_closure": all(token in output_text for token in ("Pack", "闭环")),
        "separates_capability_from_actual": all(token in output_text for token in ("Capability", "Actual")),
        "keeps_external_event_time_gap": "人工实际事件时间" in output_text or "外部事件时间" in output_text,
        "does_not_claim_complete_permission_protocol": (
            ("许可" in unsupported_text or "Permission" in unsupported_text)
            and ("协议" in unsupported_text or "Protocol" in unsupported_text)
        ),
    }
    energy = load_json(energy_path)
    return {
        "comparison_id": "HC-TM3-015-v1",
        "reasoning_output_sha256_at_unlock": object_hash(output),
        "unlock_condition": "reasoning_output existed, input/output validation completed, and output hash was frozen before these files were read by the comparison command",
        "historical_sources": [
            {"path": str(path.relative_to(ROOT)), "sha256": sha256_file(path)}
            for path in (report_path, events_path, evidence_path, energy_path)
        ],
        "evidence_requirement_comparison": rows,
        "compatible_er_count": matches,
        "total_er_count": len(rows),
        "semantic_checks": semantic_checks,
        "historical_numeric_reference": {
            "stable_window_s": energy["stable_window_s"],
            "pack_power_smooth_kw": energy["pack_power_smooth_kw"],
            "cp_power_onyx_kw": energy["cp_power_onyx_kw"],
            "external_charger_evidence_found": energy["external_charger_evidence_found"],
        },
        "blindness_caveat": "The artifact input excludes historical results, but the executing root-agent conversation had prior exposure during sample selection; strict cognitive blinding was not achieved.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build-input")
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--discovery-cache", type=Path)
    validate = subparsers.add_parser("validate")
    validate.add_argument("--input", type=Path, required=True)
    validate.add_argument("--output", type=Path, required=True)
    follow_up = subparsers.add_parser("follow-up")
    follow_up.add_argument("--input", type=Path, required=True)
    follow_up.add_argument("--output", type=Path, required=True)
    hidden = subparsers.add_parser("hidden-compare")
    hidden.add_argument("--input", type=Path, required=True)
    hidden.add_argument("--output", type=Path, required=True)
    hidden.add_argument("--comparison", type=Path, required=True)
    args = parser.parse_args()

    if args.command == "build-input":
        package = build_input(args.output, args.discovery_cache)
        print(json.dumps({
            "output": str(args.output), "package_id": package["package_id"],
            "package_hash": package["package_hash"], "input_validation_errors": validate_input(package),
            "observations": len(package["observations"]), "candidates": len(package["candidates"]),
        }, ensure_ascii=False, indent=2))
    elif args.command == "validate":
        package, output = load_json(args.input), load_json(args.output)
        errors = validate_output(package, output)
        print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
        raise SystemExit(1 if errors else 0)
    elif args.command == "follow-up":
        package, output = load_json(args.input), load_json(args.output)
        result = execute_follow_up(package, output)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    elif args.command == "hidden-compare":
        package, output = load_json(args.input), load_json(args.output)
        errors = validate_output(package, output)
        if errors:
            raise SystemExit("refusing hidden comparison because validation failed: " + "; ".join(errors))
        comparison = hidden_compare(package, output)
        args.comparison.parent.mkdir(parents=True, exist_ok=True)
        args.comparison.write_text(json.dumps(comparison, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({
            "comparison": str(args.comparison), "compatible_er_count": comparison["compatible_er_count"],
            "total_er_count": comparison["total_er_count"], "semantic_checks": comparison["semantic_checks"],
        }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
