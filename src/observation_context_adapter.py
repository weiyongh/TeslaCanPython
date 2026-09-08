"""Deterministic L3 + procedure + frozen-observation context for semantic retrieval."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from analysis_charter import canonical_json


CONTEXT_VERSION = "observation-context-v1"
PROCEDURE_VERSION = "experiment-procedure-v1"

ROLE_TERMS = {
    "REQUEST": {"request", "target", "command", "demand"},
    "CAPABILITY": {"capability", "available", "limit", "maximum", "minimum", "allowed"},
    "ACTUAL": {"actual", "output", "feedback", "measurement", "response"},
    "PERMISSION": {"permission", "permit", "allow", "enable", "gate", "safety"},
    "STATE": {"state", "status", "condition", "confirmation"},
    "TIMING_ONLY": {"transition", "timing", "sequence", "change"},
}

DOMAIN_TERMS = {
    "INTERFACE": {"interface", "connector", "connect", "connected", "plug", "port", "proximity", "latch", "lock", "unlock", "cc1", "cc2"},
    "AUX_WAKE": {"auxiliary", "wake", "awake", "lowvoltage", "lv", "supply"},
    "COMMUNICATION": {"communication", "handshake", "protocol", "version", "parameter", "online", "initialize", "initialization"},
    "ELECTRICAL": {"charge", "charging", "evse", "pack", "battery", "voltage", "current", "power", "dc"},
    "EVSE_BOUNDARY": {"evse", "charger", "cable", "pilot"},
    "VEHICLE_BOUNDARY": {"vehicle", "battery", "pack", "bms"},
    "HV_PATH": {"highvoltage", "hv", "hvil", "contactor", "insulation", "precharge", "path"},
    "THERMAL": {"thermal", "temperature", "cool", "cooling", "heat", "heating", "hvac"},
    "PROTECTION": {"protection", "fault", "warning", "limit", "retry", "safe", "safety"},
    "STOP": {"stop", "exit", "disconnect", "unlock", "open", "closeout", "sleep"},
}

GENERIC_WORDS = {"the", "and", "from", "with", "without", "within", "where", "identify", "distinguish", "separately", "evidence", "observable", "validated", "current"}


def _hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def load_procedure(path: Path, experiment_id: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("procedure_version") != PROCEDURE_VERSION:
        raise ValueError("PROCEDURE_CONTRACT_FAILURE: unsupported version")
    if value.get("experiment_id") != experiment_id:
        raise ValueError("PROCEDURE_CONTRACT_FAILURE: experiment mismatch")
    source = value.get("source", {})
    source_path = path.parents[1] / source.get("ref", "")
    if not source_path.is_file():
        raise ValueError("PROCEDURE_CONTRACT_FAILURE: source missing")
    if hashlib.sha256(source_path.read_bytes()).hexdigest() != source.get("sha256"):
        raise ValueError("PROCEDURE_CONTRACT_FAILURE: source hash mismatch")
    if value.get("time_semantics", {}).get("all_phase_times_are") != "PLANNED_TIME":
        raise ValueError("PROCEDURE_CONTRACT_FAILURE: planned-time type required")
    return value


def _words(text: str) -> set[str]:
    split = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    return {x.lower() for x in re.findall(r"[A-Za-z][A-Za-z0-9]+", split)} - GENERIC_WORDS


def _question_concepts(text: str) -> list[str]:
    normalized = text.lower().replace("causality from proximity", "causality from temporal nearness")
    words = _words(normalized)
    concepts = [name for name, terms in DOMAIN_TERMS.items() if words & terms]
    concepts = [x for x in concepts if x not in {"EVSE_BOUNDARY", "VEHICLE_BOUNDARY"}]
    target = normalized.split(" without ", 1)[0]
    if "evse capability" in target:
        concepts.append("EVSE_BOUNDARY")
    elif "vehicle capability" in target or "vehicle request" in target:
        concepts.append("VEHICLE_BOUNDARY")
    if "evse actual" in target and "pack actual" in target:
        concepts.extend(["EVSE_BOUNDARY", "VEHICLE_BOUNDARY"])
    return concepts or ["ELECTRICAL"]


def _question_roles(statement: str) -> list[str]:
    lowered = statement.lower()
    if "continuous" in lowered:
        return ["CAPABILITY", "REQUEST", "ACTUAL"]
    if "controlled stop" in lowered:
        return ["REQUEST", "ACTUAL", "STATE"]
    if "thermal state" in lowered or "protection monitoring" in lowered:
        return ["CAPABILITY", "REQUEST", "STATE"]
    if "high-voltage path" in lowered:
        return ["REQUEST", "ACTUAL", "STATE"]
    if lowered.startswith("identify permission"):
        return ["PERMISSION", "STATE"]
    if lowered.startswith("identify vehicle request"):
        return ["REQUEST"]
    if lowered.startswith("identify") and "capability" in lowered:
        return ["CAPABILITY"]
    if lowered.startswith("distinguish evse actual"):
        return ["ACTUAL"]
    if "communication" in lowered:
        return ["TIMING_ONLY"]
    if "lock request" in lowered:
        return ["REQUEST", "STATE"]
    return ["STATE"]


def build_evidence_questions(l3_context: dict[str, Any], procedure: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = l3_context["control_tree_nodes"]
    questions = []
    for er in l3_context["evidence_requirements"]:
        er_id = er["evidence_requirement_id"]
        text = f"{er.get('statement', '')} {er.get('sufficiency_rule', '')}"
        concepts = _question_concepts(text)
        roles = _question_roles(er.get("statement", ""))
        node_refs = []
        for node in nodes:
            node_words = _words(f"{node.get('name', '')} {node.get('definition', '')}")
            if any(node_words & DOMAIN_TERMS[c] for c in concepts):
                node_refs.append(node["node_id"])
        phase_refs = [
            phase["phase_id"] for phase in procedure["planned_phases"]
            if set(phase["semantic_tags"]) & set(concepts + roles)
        ]
        forbidden = sorted({role for role in ("CAPABILITY", "REQUEST", "ACTUAL", "PERMISSION") if role not in roles})
        questions.append({
            "question_id": f"SEQ-{er_id}",
            "evidence_requirement_ref": er_id,
            "control_tree_refs": node_refs,
            "semantic_need": er["statement"],
            "sufficiency_rule": er.get("sufficiency_rule", ""),
            "candidate_roles": roles,
            "domain_concepts": concepts,
            "forbidden_substitutions": forbidden,
            "planned_phase_refs": phase_refs,
            "time_limitation": "PLANNED_TIME_IS_NOT_OBSERVED_EVENT_TIME",
            "allowed_outcomes": ["SUPPORT", "PARTIAL", "CONTRADICT", "UNKNOWN_CANDIDATE", "IRRELEVANT", "GAP"],
        })
    return questions


def _normalized(package: dict[str, Any]) -> list[tuple[str, str, dict[str, Any]]]:
    rows = []
    for signal in package["signal_summaries"]:
        ref = "SO-" + hashlib.sha256(signal["signal_key"].encode()).hexdigest()[:12].upper()
        rows.append((ref, "KNOWN", signal))
    residual = {(x["bus_key"], x["dlc"]) for x in package["residual_summaries"]}
    unknown = {(x["bus_key"], x["dlc"]) for x in package["unknown_summaries"]}
    for raw in package["observations"]:
        key = (raw["bus_key"], raw["dlc"])
        if key in residual:
            rows.append((raw["observation_id"], "RESIDUAL", raw))
        if key in unknown:
            rows.append((raw["observation_id"], "UNKNOWN", raw))
    return rows


def _phase_alignment(payload: dict[str, Any], procedure: dict[str, Any]) -> list[dict[str, Any]]:
    times = [payload.get("first_change_time_s"), payload.get("last_change_time_s")]
    if times == [None, None]:
        times = [payload.get("first_time_s"), payload.get("last_time_s")]
    times = [x for x in times if isinstance(x, (int, float))]
    aligned = []
    for phase in procedure["planned_phases"]:
        start, end = phase["start_s"], phase["end_s"]
        hits = [x for x in times if x >= start and (end is None or x < end)]
        if hits:
            aligned.append({"planned_phase_ref": phase["phase_id"], "basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "time_type": "PLANNED_TIME_CONTEXT_ONLY"})
    return aligned


def build_observation_contexts(package: dict[str, Any], procedure: dict[str, Any]) -> list[dict[str, Any]]:
    contexts = []
    for ref, source_space, payload in _normalized(package):
        changes = payload.get("change_count")
        if changes is None:
            changes = sum(int(x) for x in payload.get("bit_transitions", []))
        cardinality = payload.get("cardinality", payload.get("payload_cardinality"))
        behavior_tags = []
        if changes:
            behavior_tags.append("DYNAMIC")
        if isinstance(cardinality, int) and 1 < cardinality <= 16:
            behavior_tags.append("LOW_CARDINALITY")
        if source_space != "KNOWN" and changes:
            behavior_tags.append("UNNAMED_ACTIVITY")
        contexts.append({
            "observation_ref": ref,
            "source_space": source_space,
            "identity_hint": {
                "bus_key": payload.get("bus_key"),
                "dbc_name_hint": payload.get("signal_name"),
                "message_name_hint": payload.get("message_name"),
                "unit": payload.get("unit"),
                "dbc_source": payload.get("dbc_source"),
                "semantic_validation_state": "UNVALIDATED",
            },
            "behavior": {
                "tags": behavior_tags,
                "change_count": changes,
                "cardinality": cardinality,
                "first_change_time_s": payload.get("first_change_time_s"),
                "last_change_time_s": payload.get("last_change_time_s"),
                "stability_class": payload.get("stability_class"),
                "anomaly_flags": [x for x, present in (
                    ("SNA_PRESENT", payload.get("sna_count", 0)),
                    ("INVALID_PRESENT", payload.get("invalid_count", 0)),
                    ("OUT_OF_RANGE_PRESENT", payload.get("out_of_dbc_range_count", 0)),
                ) if present],
                "availability": "FROZEN_AGGREGATE_ONLY",
            },
            "phase_alignment": {
                "planned": _phase_alignment(payload, procedure),
                "observed_event_phase": "OBSERVED_EVENT_PHASE_UNAVAILABLE",
                "can_region_detail": "CAN_REGION_DETAIL_UNAVAILABLE",
            },
            "relationships": [],
            "provenance": {
                "frozen_package_id": package.get("package_id", "UNSPECIFIED-FROZEN-PACKAGE"),
                "derivation_method": CONTEXT_VERSION,
                "unavailable_reasons": ["TRACE_STORE_UNAVAILABLE", "RELATIONSHIP_FEATURE_UNAVAILABLE"],
            },
        })
    return contexts


def build_context_bundle(package: dict[str, Any], l3_context: dict[str, Any], procedure: dict[str, Any]) -> dict[str, Any]:
    questions = build_evidence_questions(l3_context, procedure)
    contexts = build_observation_contexts(package, procedure)
    value = {
        "context_version": CONTEXT_VERSION,
        "procedure": procedure,
        "evidence_questions": questions,
        "observation_contexts": contexts,
        "relationship_context": {
            "relations": [],
            "availability": "RELATIONSHIP_FEATURE_UNAVAILABLE",
            "reason": "Frozen aggregate package has no trace store for general cross-observation relations."
        },
        "time_context": {
            "planned_phase_status": "AVAILABLE",
            "observed_event_phase_status": procedure["time_semantics"]["observed_event_phase_status"],
            "can_region_status": "CAN_REGION_DETAIL_UNAVAILABLE"
        },
    }
    value["context_hash"] = _hash(value)
    return value
