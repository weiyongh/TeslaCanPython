"""Context-aware semantic retrieval over a frozen Observation Package."""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import re
from typing import Any

from analysis_charter import canonical_json
from observation_context_adapter import DOMAIN_TERMS, ROLE_TERMS, build_context_bundle, build_evidence_questions


RETRIEVAL_VERSION = "semantic-observation-retrieval-v2-context"
PER_INTENT_LIMIT = 8
GLOBAL_LIMIT = 120
SOURCE_LIMITS = {"KNOWN": 6, "RESIDUAL": 1, "UNKNOWN": 1}


def _hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def _words(value: Any) -> set[str]:
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", str(value or ""))
    return {x.lower() for x in re.findall(r"[A-Za-z][A-Za-z0-9]+", text)}


def _term_hits(words: set[str], terms: set[str]) -> set[str]:
    return {term for term in terms if any(word == term or word.startswith(term) for word in words)}


def _fallback_procedure(experiment_context: dict[str, Any]) -> dict[str, Any]:
    return {
        "procedure_version": "experiment-procedure-v1",
        "experiment_id": experiment_context.get("experiment_id"),
        "source": {"ref": None, "sha256": None},
        "time_semantics": {"all_phase_times_are": "PLANNED_TIME", "observed_event_phase_status": "OBSERVED_EVENT_PHASE_UNAVAILABLE"},
        "initial_conditions": [], "planned_phases": [],
        "procedure_constraints": ["PROCEDURE_CONTEXT_UNAVAILABLE"],
    }


def build_search_intents(l3_context: dict[str, Any], experiment_context: dict[str, Any], procedure: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    questions = build_evidence_questions(l3_context, procedure or _fallback_procedure(experiment_context))
    return [{
        "intent_id": "SSI-" + q["evidence_requirement_ref"],
        "evidence_question_ref": q["question_id"],
        "control_tree_refs": q["control_tree_refs"],
        "evidence_requirement_refs": [q["evidence_requirement_ref"]],
        "semantic_roles": q["candidate_roles"],
        "semantic_need": q["semantic_need"],
        "domain_concepts": q["domain_concepts"],
        "forbidden_substitutions": q["forbidden_substitutions"],
        "planned_phase_refs": q["planned_phase_refs"],
        "experiment_context_ref": experiment_context.get("experiment_id"),
        "allowed_outcomes": q["allowed_outcomes"],
    } for q in questions]


def _semantic_compatibility(intent: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    identity = context["identity_hint"]
    words = _words(identity.get("dbc_name_hint")) | _words(identity.get("message_name_hint"))
    role_hits = sorted({term for role in intent["semantic_roles"] for term in _term_hits(words, set(ROLE_TERMS.get(role, ())))})
    concept_hits = {concept: sorted(_term_hits(words, DOMAIN_TERMS.get(concept, set()))) for concept in intent["domain_concepts"]}
    domain_hits = sorted({term for hits in concept_hits.values() for term in hits})
    specialized = [concept for concept in intent["domain_concepts"] if concept not in {"ELECTRICAL", "EVSE_BOUNDARY", "VEHICLE_BOUNDARY"}]
    boundary_concepts = [concept for concept in intent["domain_concepts"] if concept in {"EVSE_BOUNDARY", "VEHICLE_BOUNDARY"}]
    relevant_concepts = intent["domain_concepts"] if len(specialized) >= 3 else (specialized or ["ELECTRICAL"])
    relevant_domain_hits = sorted({term for concept in relevant_concepts for term in concept_hits.get(concept, [])})
    boundary_hits = sorted({term for concept in boundary_concepts for term in concept_hits.get(concept, [])})
    competing_concepts = {"INTERFACE", "AUX_WAKE", "COMMUNICATION", "HV_PATH", "THERMAL", "PROTECTION", "STOP"}
    off_domain_hits = sorted({term for concept in competing_concepts - set(intent["domain_concepts"]) for term in _term_hits(words, DOMAIN_TERMS[concept])} - set(role_hits) - set(relevant_domain_hits) - set(boundary_hits))
    if "INTERFACE" in intent["domain_concepts"]:
        strong_interface = _term_hits(words, {"connector", "plug", "port", "proximity", "latch"})
        if not strong_interface:
            relevant_domain_hits = []
    system_scope_hits = _term_hits(words, DOMAIN_TERMS["ELECTRICAL"] | DOMAIN_TERMS["HV_PATH"] | DOMAIN_TERMS["INTERFACE"] | DOMAIN_TERMS["THERMAL"])
    protection_only = "PROTECTION" in specialized and not system_scope_hits
    unit = str(identity.get("unit") or "").lower()
    dimension_match = bool(unit in {"a", "v", "w", "kw"} and "ELECTRICAL" in intent["domain_concepts"])
    behavior = context["behavior"]["tags"]
    phase_hits = sorted({row["planned_phase_ref"] for row in context["phase_alignment"]["planned"]} & set(intent["planned_phase_refs"]))

    if context["source_space"] != "KNOWN" and "UNNAMED_ACTIVITY" in behavior:
        path, tier = "UNNAMED_BEHAVIOR_CONTEXT", 2 if phase_hits else 1
    elif relevant_domain_hits and role_hits and (not boundary_concepts or boundary_hits) and not protection_only and not off_domain_hits:
        path, tier = "SEMANTIC_CONTEXT_COMPATIBLE", 4
    elif relevant_domain_hits and (len(relevant_domain_hits) >= 2 or dimension_match) and "DYNAMIC" in behavior and not off_domain_hits:
        path, tier = "PROCEDURE_ALIGNED_DOMAIN_HINT", 3
    elif dimension_match and not specialized and "DYNAMIC" in behavior:
        path, tier = "PHYSICAL_DIMENSION_BEHAVIOR", 3
    elif "DYNAMIC" in behavior and "LOW_CARDINALITY" in behavior:
        path, tier = "BEHAVIOR_EXPLORATORY", 1
    else:
        path, tier = "NO_COMPATIBLE_PATH", 0
    score = tier * 100 + len(relevant_domain_hits) * 10 + len(boundary_hits) * 6 + len(role_hits) * 4 + len(phase_hits) * 2 + int(dimension_match)
    return {"eligibility_path": path, "path_tier": tier, "score": score, "domain_hits": domain_hits, "matched_concepts": sorted(concept for concept, hits in concept_hits.items() if hits), "role_hits": role_hits, "planned_phase_hits": phase_hits, "dimension_match": dimension_match, "behavior_tags": behavior}


def retrieve(package: dict[str, Any], l3_context: dict[str, Any], experiment_context: dict[str, Any], context_bundle: dict[str, Any] | None = None) -> dict[str, Any]:
    context_bundle = context_bundle or build_context_bundle(package, l3_context, _fallback_procedure(experiment_context))
    intents = build_search_intents(l3_context, experiment_context, context_bundle["procedure"])
    contexts = context_bundle["observation_contexts"]
    candidates_by_bus = defaultdict(list)
    for candidate in package["candidates"]:
        if candidate.get("bus_key"):
            candidates_by_bus[(candidate["source_space"], candidate["bus_key"])].append(candidate["candidate_id"])

    results, selected_global, selected_seen = [], [], set()
    for intent in intents:
        eligible = []
        for context in contexts:
            match = _semantic_compatibility(intent, context)
            if match["path_tier"] == 0:
                continue
            bus_key = context["identity_hint"].get("bus_key")
            eligible.append({
                "observation_ref": context["observation_ref"], "source_space": context["source_space"],
                "score": match["score"], "eligibility_path": match["eligibility_path"],
                "ranking_components": {"path_tier": match["path_tier"], "domain_hit_count": len(match["domain_hits"]), "role_hit_count": len(match["role_hits"]), "planned_phase_hit_count": len(match["planned_phase_hits"]), "dimension_match": int(match["dimension_match"])},
                "retrieval_reasons": [match["eligibility_path"]],
                "context_matches": {"domain_terms": match["domain_hits"], "domain_concepts": match["matched_concepts"], "role_terms": match["role_hits"], "planned_phase_refs": match["planned_phase_hits"], "behavior_tags": match["behavior_tags"]},
                "unavailable_features": ["OBSERVED_EVENT_PHASE_UNAVAILABLE", "CAN_REGION_DETAIL_UNAVAILABLE", "RELATIONSHIP_FEATURE_UNAVAILABLE"],
                "semantic_role_status": "UNCONFIRMED", "provenance_class": "DIRECT_INTENT_RETRIEVAL",
                "origin_intent_ref": intent["intent_id"],
                "candidate_refs": candidates_by_bus.get((context["source_space"], bus_key), [])[:4],
            })
        eligible.sort(key=lambda row: (-row["ranking_components"]["path_tier"], -row["score"], row["source_space"], row["observation_ref"]))
        source_counts, chosen, exploratory_known = Counter(), [], 0
        for concept in intent["domain_concepts"]:
            row = next((item for item in eligible if item["source_space"] == "KNOWN" and concept in item["context_matches"]["domain_concepts"] and item not in chosen), None)
            if row is not None and source_counts["KNOWN"] < SOURCE_LIMITS["KNOWN"]:
                chosen.append(row); source_counts["KNOWN"] += 1
        for row in eligible:
            if row in chosen:
                continue
            space = row["source_space"]
            if source_counts[space] >= SOURCE_LIMITS[space]:
                continue
            if space == "KNOWN" and row["eligibility_path"] == "BEHAVIOR_EXPLORATORY":
                if exploratory_known >= 1:
                    continue
                exploratory_known += 1
            chosen.append(row); source_counts[space] += 1
            if len(chosen) >= PER_INTENT_LIMIT:
                break
        for row in chosen:
            if row["observation_ref"] not in selected_seen and len(selected_global) < GLOBAL_LIMIT:
                selected_global.append(row["observation_ref"]); selected_seen.add(row["observation_ref"])
        results.append({
            "intent_id": intent["intent_id"], "evidence_question_ref": intent["evidence_question_ref"],
            "retrieved": chosen, "cross_intent_supplements": [], "global_context_only": [],
            "source_space_counts": dict(source_counts), "eligible_count": len(eligible),
            "truncated_count": max(0, len(eligible) - len(chosen)),
            "below_context_gate_count": len(contexts) - len(eligible),
            "below_threshold_count": len(contexts) - len(eligible), "no_suitable_observation": not chosen,
            "global_limit_excluded_count": 0,
        })
    core = {"retrieval_version": RETRIEVAL_VERSION, "intents": intents, "results": results, "selected_observation_refs": selected_global}
    input_value = {"observation_package_hash": package["package_hash"], "l3_context": l3_context, "experiment_context": experiment_context, "context_hash": context_bundle["context_hash"]}
    return {**core, "context_bundle": context_bundle, "retrieval_input_hash": _hash(input_value), "retrieval_output_hash": _hash(core), "limits": {"per_intent": PER_INTENT_LIMIT, "global": GLOBAL_LIMIT, "source_limits": SOURCE_LIMITS, "eligibility_model": "PATH_TIER_THEN_CONTEXT_ORDER"}}
