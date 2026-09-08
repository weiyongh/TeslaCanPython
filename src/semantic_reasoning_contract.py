"""Formal bounded semantic-reasoning contract for Phase 3B.2."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any

from analysis_charter import AnalysisCharter, canonical_json, resolve_repo_path
from observation_package import validate_package
from semantic_observation_retrieval import retrieve


CONTRACT_VERSION = "formal-semantic-reasoning-v1"
EPISTEMIC_CLASSES = {"OBSERVED", "DERIVED", "INFERRED", "UNSUPPORTED"}
MODEL_INTERACTIONS = {
    "SUPPORTS_CURRENT_MODEL", "EXTENDS_CURRENT_MODEL", "CHALLENGES_CURRENT_MODEL",
    "OUTSIDE_CURRENT_MODEL", "INSUFFICIENT_TO_MAP", "NO_SAFE_MAPPING", "OUTSIDE_CURRENT_SCOPE",
}
CAUSALITY = {
    "TEMPORAL_ASSOCIATION_ONLY", "CONTROL_RELATION_SUPPORTED",
    "CAUSALITY_NOT_ESTABLISHED", "NOT_APPLICABLE",
}
HIGH_RISK_ROLES = {"REQUEST", "PERMISSION", "CAPABILITY", "ACTUAL", "STATE", "TIMING_ONLY", "PROTOCOL"}
FORBIDDEN_KEYS = {
    "expected_answer", "expected_reasoning_path", "expected_evidence_gap",
    "expected_er_status", "reasoning_impact", "hidden_comparison", "benchmark_score",
    "prior_reasoning_output", "historical_conclusion",
    "known_correct_signal_name", "expected_signal_mapping", "expected_signal_role",
    "expected_candidate_id", "expected_retrieval_result",
}
FORBIDDEN_PHRASES = (
    "本数据应该发现", "先找 Capability", "expected reasoning path",
    "expected Evidence Gap", "expected conclusion",
)


def fingerprint(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def _walk_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        return set(value) | set().union(*(_walk_keys(item) for item in value.values()), set())
    if isinstance(value, list):
        return set().union(*(_walk_keys(item) for item in value), set())
    return set()


def build_reasoning_input(
    observation_package: dict[str, Any], charter: AnalysisCharter, repo_root: Path,
    retrieval_bundle: dict[str, Any] | None = None,
) -> dict[str, Any]:
    validate_package(observation_package)
    if observation_package["experiment_id"] != charter.experiment_id:
        raise ValueError("REASONING_INPUT_CONTRACT_FAILURE: experiment mismatch")
    if not charter.semantic_context_ref:
        raise ValueError("REASONING_INPUT_CONTRACT_FAILURE: semantic_context_ref missing")
    semantic_path = resolve_repo_path(repo_root, charter.semantic_context_ref)
    semantic_source = json.loads(semantic_path.read_text(encoding="utf-8"))
    l3_context = semantic_source.get("l3_context")
    if not isinstance(l3_context, dict):
        raise ValueError("REASONING_INPUT_CONTRACT_FAILURE: l3_context missing")

    experiment_context = {
        "experiment_id": charter.experiment_id, "purpose": charter.purpose,
        "system_scope": charter.system_scope, "analysis_scope": charter.analysis_scope,
        "time_policy": charter.time_policy,
    }
    retrieval_bundle = retrieval_bundle or retrieve(observation_package, l3_context, experiment_context)
    context_bundle = retrieval_bundle["context_bundle"]
    wanted_refs = set(retrieval_bundle["selected_observation_refs"])
    observations = []
    for source in observation_package["signal_summaries"]:
        ref = "SO-" + hashlib.sha256(source["signal_key"].encode()).hexdigest()[:12].upper()
        if ref in wanted_refs:
            row = dict(source); row["observation_id"] = ref; row["source_collection"] = "signal_summaries"; row["source_space"] = "KNOWN"
            observations.append(row)
    for source in observation_package["observations"]:
        if source["observation_id"] in wanted_refs:
            row = dict(source); row["source_collection"] = "observations"
            residual_keys = {(x["bus_key"], x["dlc"]) for x in observation_package["residual_summaries"]}
            row["source_space"] = "RESIDUAL" if (row["bus_key"], row["dlc"]) in residual_keys else "UNKNOWN"
            observations.append(row)
    observations.sort(key=lambda row: retrieval_bundle["selected_observation_refs"].index(row["observation_id"]))

    wanted_candidates = {ref for result in retrieval_bundle["results"] for item in result["retrieved"] for ref in item["candidate_refs"]}
    candidates = [dict(row) for row in observation_package["candidates"] if row["candidate_id"] in wanted_candidates]
    events = []
    for row in observations:
        if row.get("first_change_time_s") is not None:
            events.append({
                "event_id": "EA-" + row["observation_id"][3:],
                "time_type": "CAN_OBSERVED_TIME",
                "source": "CAN_OBSERVED_STATE",
                "time_s": row["first_change_time_s"],
                "description": "First decoded value change; not a human action timestamp.",
                "observation_refs": [row["observation_id"]],
            })
        if len(events) >= 40:
            break
    consistency = []
    refs_by_candidate: dict[str, set[str]] = {}
    for result in retrieval_bundle["results"]:
        for item in result["retrieved"]:
            for candidate_ref in item["candidate_refs"]:
                refs_by_candidate.setdefault(candidate_ref, set()).add(item["observation_ref"])
    for candidate in candidates:
        if candidate.get("source_space") == "KNOWN":
            consistency.append({
                "relation_id": "REL-" + candidate["candidate_id"],
                "candidate_ref": candidate["candidate_id"],
                "observation_refs": sorted(refs_by_candidate.get(candidate["candidate_id"], set())),
                "deterministic_summary": candidate["observed_summary"],
                "semantic_status": "VALIDATION_REQUIRED",
            })

    package = {
        "contract_version": CONTRACT_VERSION,
        "source_observation_package_id": observation_package["package_id"],
        "source_observation_package_hash": observation_package["package_hash"],
        "experiment_context": experiment_context,
        "experiment_procedure": context_bundle["procedure"],
        "semantic_evidence_questions": context_bundle["evidence_questions"],
        "observation_contexts": [
            row for row in context_bundle["observation_contexts"]
            if row["observation_ref"] in wanted_refs
        ],
        "per_question_evidence": [{
            "evidence_question_ref": result["evidence_question_ref"],
            "intent_ref": result["intent_id"],
            "direct_observation_refs": [row["observation_ref"] for row in result["retrieved"]],
            "cross_intent_supplements": result["cross_intent_supplements"],
            "global_context_only": result["global_context_only"],
        } for result in retrieval_bundle["results"]],
        "observation_context_hash": context_bundle["context_hash"],
        "l3_context": l3_context,
        "semantic_search_intents": retrieval_bundle["intents"],
        "retrieval_results": retrieval_bundle["results"],
        "retrieval_fingerprints": {"input": retrieval_bundle["retrieval_input_hash"], "output": retrieval_bundle["retrieval_output_hash"], "version": retrieval_bundle["retrieval_version"]},
        "event_anchors": events,
        "observations": observations,
        "candidates": candidates,
        "consistency_results": consistency,
        "validation_states": [
            {"observation_ref": row["observation_id"], "state": "UNVALIDATED", "source_space": row["source_space"]}
            for row in observations
        ],
        "allowed_follow_up_operations": [],
        "reference_manifest": {
            "observation_refs": [row["observation_id"] for row in observations],
            "candidate_refs": [row["candidate_id"] for row in candidates],
            "relation_refs": [row["relation_id"] for row in consistency],
            "event_refs": [row["event_id"] for row in events],
            "control_tree_refs": [row["node_id"] for row in l3_context["control_tree_nodes"]],
            "evidence_requirement_refs": [
                row["evidence_requirement_id"] for row in l3_context["evidence_requirements"]
            ],
            "evidence_question_refs": [
                row["question_id"] for row in context_bundle["evidence_questions"]
            ],
            "raw_refs": sorted({
                f"ASC-L{ref['line_number']}" for row in observations for ref in row.get("raw_refs", [])
            }),
        },
        "independence_policy": {
            "historical_results_allowed": False,
            "raw_asc_access_allowed": False,
            "dbc_name_confirms_semantic_role": False,
            "candidate_is_observation_space": False,
            "semantic_prior_is_reasoning_script": False,
        },
        "fingerprints": {
            "semantic_prior": fingerprint(l3_context),
            "control_tree": fingerprint(l3_context["control_tree_nodes"]),
            "evidence_requirements": fingerprint(l3_context["evidence_requirements"]),
        },
    }
    content_hash = fingerprint(package)
    package["package_id"] = f"{charter.experiment_id}-reasoning-{content_hash[:16]}"
    package["package_hash"] = fingerprint(package)
    errors = validate_reasoning_input(package)
    if errors:
        raise ValueError(";".join(errors))
    return package


def validate_reasoning_input(package: dict[str, Any]) -> list[str]:
    errors = []
    body = dict(package)
    stored = body.pop("package_hash", None)
    if stored != fingerprint(body):
        errors.append("REASONING_INPUT_HASH_MISMATCH")
    leaked = sorted(_walk_keys(package) & FORBIDDEN_KEYS)
    if leaked:
        errors.append("SEMANTIC_PRIOR_LEAKAGE_KEYS:" + ",".join(leaked))
    serialized = json.dumps(package, ensure_ascii=False)
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in serialized.lower():
            errors.append("SEMANTIC_PRIOR_LEAKAGE_PHRASE:" + phrase)
    if package.get("allowed_follow_up_operations") != []:
        errors.append("FOLLOW_UP_POLICY_NOT_ZERO")
    manifest = package.get("reference_manifest", {})
    for field, rows, key in (
        ("observation_refs", package.get("observations", []), "observation_id"),
        ("candidate_refs", package.get("candidates", []), "candidate_id"),
        ("event_refs", package.get("event_anchors", []), "event_id"),
    ):
        if set(manifest.get(field, [])) != {row[key] for row in rows}:
            errors.append("REFERENCE_MANIFEST_MISMATCH:" + field)
    return sorted(set(errors))


def validate_reasoning_output(package: dict[str, Any], output: dict[str, Any]) -> list[str]:
    errors = validate_reasoning_input(package)
    if output.get("contract_version") != CONTRACT_VERSION:
        errors.append("OUTPUT_CONTRACT_VERSION_MISMATCH")
    if output.get("input_package_id") != package.get("package_id"):
        errors.append("OUTPUT_PACKAGE_ID_MISMATCH")
    if output.get("input_package_hash") != package.get("package_hash"):
        errors.append("OUTPUT_PACKAGE_HASH_MISMATCH")
    if output.get("follow_up_requests"):
        errors.append("FOLLOW_UP_NOT_ALLOWED")
    refs = package["reference_manifest"]
    allowed = set().union(*(set(value) for value in refs.values()))
    observation_refs = set(refs["observation_refs"])
    candidate_refs = set(refs["candidate_refs"])
    node_refs = set(refs["control_tree_refs"])
    er_refs = set(refs["evidence_requirement_refs"])
    event_by_id = {row["event_id"]: row for row in package["event_anchors"]}
    er_by_id = {row["evidence_requirement_id"]: row for row in package["l3_context"]["evidence_requirements"]}
    ref_objects = {
        **{row["observation_id"]: row for row in package["observations"]},
        **{row["candidate_id"]: row for row in package["candidates"]},
        **event_by_id,
    }
    finding_ids = set()
    gap_ids = set()
    direct_by_er = {
        question["evidence_requirement_ref"]: set(row["direct_observation_refs"])
        for question, row in zip(package.get("semantic_evidence_questions", []), package.get("per_question_evidence", []))
    }
    for finding in output.get("findings", []):
        finding_id = finding.get("finding_id")
        if not finding_id or finding_id in finding_ids:
            errors.append("DUPLICATE_OR_MISSING_FINDING_ID")
        finding_ids.add(finding_id)
        observation_refs_in_finding = set(finding.get("observation_refs", []))
        provenance_rows = finding.get("observation_provenance", [])
        if package.get("per_question_evidence") and {row.get("observation_ref") for row in provenance_rows} != observation_refs_in_finding:
            errors.append(f"{finding_id}:OBSERVATION_PROVENANCE_CLOSURE_MISMATCH")
        mapped_ers = {row.get("evidence_requirement_ref") for row in finding.get("evidence_requirement_mapping", [])}
        for provenance in provenance_rows:
            provenance_class = provenance.get("provenance_class")
            ref = provenance.get("observation_ref")
            if provenance_class not in {"DIRECT_INTENT_RETRIEVAL", "CROSS_INTENT_SUPPLEMENT", "GLOBAL_CONTEXT_ONLY"}:
                errors.append(f"{finding_id}:INVALID_OBSERVATION_PROVENANCE")
            elif provenance_class == "DIRECT_INTENT_RETRIEVAL" and mapped_ers and not any(ref in direct_by_er.get(er, set()) for er in mapped_ers):
                errors.append(f"{finding_id}:DIRECT_PROVENANCE_NOT_IN_MAPPED_ER")
            elif provenance_class == "CROSS_INTENT_SUPPLEMENT" and not all(provenance.get(key) for key in ("origin_intent_ref", "current_evidence_requirement_ref", "supplementary_reason")):
                errors.append(f"{finding_id}:INCOMPLETE_CROSS_INTENT_PROVENANCE")
        if finding.get("promotion_state") == "APPROVED_EVIDENCE" or finding.get("approved_evidence"):
            errors.append(f"{finding_id}:FINDING_MARKED_APPROVED")
        for ref in finding.get("observation_refs", []):
            if ref not in observation_refs:
                errors.append(f"{finding_id}:UNKNOWN_OBSERVATION_REF:{ref}")
        for ref in finding.get("candidate_refs", []):
            if ref not in candidate_refs:
                errors.append(f"{finding_id}:UNKNOWN_CANDIDATE_REF:{ref}")
        node = finding.get("control_tree_ref")
        if node not in node_refs | {"NO_SAFE_MAPPING", "OUTSIDE_CURRENT_SCOPE"}:
            errors.append(f"{finding_id}:UNKNOWN_CONTROL_TREE_REF:{node}")
        role = finding.get("proposed_role")
        status = finding.get("semantic_status")
        if role in HIGH_RISK_ROLES and status == "CONFIRMED":
            errors.append(f"{finding_id}:UNVALIDATED_HIGH_RISK_ROLE_CONFIRMED")
        if finding.get("causality_status") not in CAUSALITY:
            errors.append(f"{finding_id}:INVALID_CAUSALITY_STATUS")
        for event_ref in finding.get("event_refs", []):
            event = event_by_id.get(event_ref)
            if not event:
                errors.append(f"{finding_id}:UNKNOWN_EVENT_REF:{event_ref}")
            elif event["source"] == "CAN_OBSERVED_STATE" and finding.get("human_action_time_confirmed"):
                errors.append(f"{finding_id}:CAN_STATE_AS_HUMAN_ACTION")
            elif event["source"] == "PLANNED_ONLY" and finding.get("observed_latency_claimed"):
                errors.append(f"{finding_id}:PLANNED_TIME_AS_OBSERVED_LATENCY")
        for fact in finding.get("fact_bindings", []):
            if fact.get("claim_class") not in EPISTEMIC_CLASSES:
                errors.append(f"{finding_id}:INVALID_EPISTEMIC_CLASS")
            supports = fact.get("support_refs", [])
            if fact.get("claim_class") in {"OBSERVED", "DERIVED"} and not supports:
                errors.append(f"{finding_id}:SUPPORTED_FACT_WITHOUT_REF")
            for ref in supports:
                if ref not in allowed:
                    errors.append(f"{finding_id}:UNKNOWN_FACT_REF:{ref}")
            if fact.get("claim_class") in {"OBSERVED", "DERIVED"}:
                claimed_numbers = set(re.findall(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?", fact.get("statement", "")))
                source_text = json.dumps([ref_objects.get(ref, {}) for ref in supports], ensure_ascii=False)
                source_numbers = set(re.findall(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?", source_text))
                if not claimed_numbers <= source_numbers:
                    errors.append(f"{finding_id}:LLM_CREATED_NUMERIC_STATISTIC")
        for mapping in finding.get("evidence_requirement_mapping", []):
            er = mapping.get("evidence_requirement_ref")
            if er not in er_refs:
                errors.append(f"{finding_id}:UNKNOWN_ER_REF:{er}")
            elif role == "ACTUAL" and mapping.get("status") == "DIRECT_SUPPORT" and "request" in json.dumps(er_by_id[er], ensure_ascii=False).lower():
                errors.append(f"{finding_id}:ACTUAL_SATISFIES_REQUEST_ER")
        if finding.get("model_interaction") not in MODEL_INTERACTIONS:
            errors.append(f"{finding_id}:INVALID_MODEL_INTERACTION")
        for gap in finding.get("evidence_gaps", []):
            gap_id = gap.get("gap_id")
            if not gap_id or gap_id in gap_ids:
                errors.append("DUPLICATE_OR_MISSING_GAP_ID")
            gap_ids.add(gap_id)
        if finding.get("semantic_status") == "CONTRADICTED" and not any(
            fact.get("claim_class") in {"OBSERVED", "DERIVED"} for fact in finding.get("fact_bindings", [])
        ):
            errors.append(f"{finding_id}:CONTRADICTION_WITHOUT_SUPPORT")
    return sorted(set(errors))


def freeze_json(value: dict[str, Any], path: Path) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
