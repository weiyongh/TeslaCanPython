"""Map validated findings to review-only Evidence Binding drafts."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any

from semantic_reasoning_contract import HIGH_RISK_ROLES, fingerprint


def map_findings(package: dict[str, Any], output: dict[str, Any]) -> dict[str, Any]:
    bindings = []
    raw_by_observation = {
        row["observation_id"]: [f"ASC-L{ref['line_number']}" for ref in row.get("raw_refs", [])]
        for row in package["observations"]
    }
    for index, finding in enumerate(output.get("findings", []), 1):
        role = finding.get("proposed_role", "UNRESOLVED")
        if finding.get("model_interaction") in {"NO_SAFE_MAPPING", "INSUFFICIENT_TO_MAP", "OUTSIDE_CURRENT_SCOPE"}:
            promotion = "HOLD_UNRESOLVED"
            reason = "Finding has no safe semantic mapping."
        elif role == "TECHNICAL_FACT" and all(
            fact.get("claim_class") in {"OBSERVED", "DERIVED"} for fact in finding.get("fact_bindings", [])
        ):
            promotion = "AUTO_ELIGIBLE_TECHNICAL_FACT"
            reason = "Only deterministic technical identity/statistics are proposed; approval has not occurred."
        elif role in HIGH_RISK_ROLES or finding.get("signal_validation_needed"):
            promotion = "HUMAN_REVIEW_REQUIRED"
            reason = "Semantic role or Signal Validation requires human review."
        else:
            promotion = "DRAFT_MAPPING"
            reason = "Draft semantic mapping awaits review."
        observation_refs = finding.get("observation_refs", [])
        bindings.append({
            "binding_id": f"EB-{index:04d}",
            "experiment_id": package["experiment_context"]["experiment_id"],
            "finding_id": finding["finding_id"],
            "observation_refs": observation_refs,
            "observation_provenance": finding.get("observation_provenance", []),
            "candidate_refs": finding.get("candidate_refs", []),
            "evidence_requirement_refs": [
                row["evidence_requirement_ref"] for row in finding.get("evidence_requirement_mapping", [])
            ],
            "proposed_role": role,
            "epistemic_classes": sorted({row["claim_class"] for row in finding.get("fact_bindings", [])}),
            "semantic_status": finding.get("semantic_status", "UNVALIDATED"),
            "validation_state": "PENDING_REVIEW",
            "confidence": finding.get("confidence", "LOW"),
            "uncertainty_flags": finding.get("uncertainty_flags", []),
            "alternatives": finding.get("alternative_explanations", []),
            "evidence_gaps": finding.get("evidence_gaps", []),
            "raw_reference_closure": sorted({ref for obs in observation_refs for ref in raw_by_observation.get(obs, [])}),
            "promotion_state": promotion,
            "review_required": promotion != "AUTO_ELIGIBLE_TECHNICAL_FACT",
            "promotion_reason": reason,
            "provenance": {
                "reasoning_input_package_id": package["package_id"],
                "reasoning_input_package_hash": package["package_hash"],
                "reasoning_result_id": output["result_id"],
            },
        })
    result = {
        "mapping_version": "evidence-mapping-draft-v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "approval_state": "NOT_APPROVED",
        "bindings": bindings,
        "promotion_state_counts": dict(Counter(row["promotion_state"] for row in bindings)),
    }
    result["mapping_hash"] = fingerprint(result)
    return result
