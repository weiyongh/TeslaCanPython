"""Render a downstream-only Human Evidence Review Packet from frozen artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


PACKET_VERSION = "human-evidence-review-packet-v1"
REFERENCE_LABEL = "REFERENCE — NOT EVIDENCE BY ITSELF"
RELATIONSHIP_LIMITATION = (
    "The frozen Observation Package does not contain synchronized cross-signal "
    "relationship features required to establish this relation."
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _one_line(value: Any) -> str:
    return str(value).replace("\n", " ").strip()


def _observation_summary(observation: dict[str, Any]) -> str:
    parts: list[str] = []
    stability = observation.get("stability_class")
    changes = observation.get("change_count")
    if stability:
        parts.append(f"stability={stability}")
    if changes is not None:
        parts.append(f"changes={changes}")
    if observation.get("minimum") is not None or observation.get("maximum") is not None:
        parts.append(f"range={observation.get('minimum')}..{observation.get('maximum')}")
    if observation.get("first_change_time_s") is not None:
        parts.append(f"first change={observation['first_change_time_s']} s (CAN observed state time)")
    if observation.get("last_change_time_s") is not None:
        parts.append(f"last change={observation['last_change_time_s']} s (CAN observed state time)")
    sequence = observation.get("sequence")
    if sequence:
        shown = sequence[:8]
        suffix = " …" if len(sequence) > len(shown) else ""
        parts.append("sequence=" + " → ".join(map(str, shown)) + suffix)
    if not parts:
        transitions = sum(int(x) for x in observation.get("bit_transitions", []))
        cardinality = observation.get("payload_cardinality")
        parts.append(f"raw payload cardinality={cardinality}; bit transitions={transitions}")
    return "; ".join(parts)


def _dbc_reference(observation: dict[str, Any]) -> str:
    if not observation.get("signal_name"):
        return "NONE / UNKNOWN / NOT DEFINED"
    fields = [observation.get("message_name"), observation.get("signal_name")]
    if observation.get("unit"):
        fields.append(f"unit={observation['unit']}")
    if observation.get("enum_definition"):
        fields.append("enum=" + json.dumps(observation["enum_definition"], ensure_ascii=False, sort_keys=True))
    return " / ".join(_one_line(x) for x in fields if x)


def _observation_row(ref: str, observation: dict[str, Any], provenance: str) -> list[str]:
    return [
        ref,
        observation.get("source_space", "UNKNOWN"),
        observation.get("can_id") or observation.get("bus_key") or "—",
        observation.get("message_name") or "—",
        observation.get("signal_name") or "UNNAMED OBSERVATION",
        _dbc_reference(observation),
        _observation_summary(observation),
        provenance,
    ]


def _table(rows: list[list[str]]) -> list[str]:
    header = ["Observation", "Space", "CAN / Bus", "Message", "Signal", "DBC semantic", "Frozen behavior", "Provenance"]
    result = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    result.extend("| " + " | ".join(_one_line(x).replace("|", "\\|") for x in row) + " |" for row in rows)
    return result


def build_review_packet(run_dir: Path) -> tuple[str, dict[str, Any]]:
    paths = {
        "input": run_dir / "semantic_reasoning_input.json",
        "output": run_dir / "semantic_reasoning_output.json",
        "mapping": run_dir / "evidence_mapping_draft.json",
        "contexts": run_dir / "observation_contexts.json",
        "audit": run_dir / "runtime_audit.json",
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise ValueError("REVIEW_PACKET_INPUT_MISSING:" + ",".join(missing))
    before_hashes = {name: _sha256(path) for name, path in paths.items()}
    package, reasoning, mapping, contexts, audit = (_load(paths[name]) for name in ("input", "output", "mapping", "contexts", "audit"))
    if audit.get("exit_status") != "AWAITING_EVIDENCE_REVIEW":
        raise ValueError("REVIEW_PACKET_REQUIRES_AWAITING_EVIDENCE_REVIEW")
    if mapping.get("approval_state") != "NOT_APPROVED":
        raise ValueError("REVIEW_PACKET_REQUIRES_UNAPPROVED_MAPPING")

    observations = {row["observation_id"]: row for row in package["observations"]}
    findings = {row["finding_id"]: row for row in reasoning["findings"]}
    questions = {row["evidence_requirement_ref"]: row for row in package["semantic_evidence_questions"]}
    requirements = {row["evidence_requirement_id"]: row for row in package["l3_context"]["evidence_requirements"]}
    context_by_ref = {row["observation_ref"]: row for row in contexts["observation_contexts"]}
    retrieval_by_er: dict[str, list[dict[str, Any]]] = {}
    question_er = {row["question_id"]: row["evidence_requirement_ref"] for row in package["semantic_evidence_questions"] if row.get("question_id")}
    intent_er = {}
    for row in package["semantic_search_intents"]:
        er_refs = row.get("evidence_requirement_refs", [])
        er = row.get("evidence_requirement_ref") or (er_refs[0] if len(er_refs) == 1 else None)
        er = er or question_er.get(row.get("evidence_question_ref"))
        if er not in requirements:
            raise ValueError(f"UNRESOLVED_INTENT_ER_REF:{row['intent_id']}")
        intent_er[row["intent_id"]] = er
    for result in package["retrieval_results"]:
        retrieval_by_er[intent_er[result["intent_id"]]] = result.get("retrieved", [])

    lines = [
        f"# {package['experiment_context']['experiment_id']} Evidence Review Packet",
        "",
        f"> Packet version: `{PACKET_VERSION}`  ",
        "> Status: `AWAITING_EVIDENCE_REVIEW`  ",
        "> Downstream presentation only — not analysis input, not Approved Evidence, and not a human review submission.",
        "",
        "## Reading boundary",
        "",
        f"DBC sections are labelled **{REFERENCE_LABEL}**. A DBC name is a decode/semantic hint, not proof of a role. "
        "CAN timestamps below are observed CAN-state times; planned procedure times are not human action times.",
        "",
    ]
    displayed: dict[str, str] = {}
    cards_with_dbc = cards_without_dbc = cards_with_gap = cards_relationship = cards_collection = 0

    for binding in mapping["bindings"]:
        finding = findings.get(binding["finding_id"])
        if finding is None:
            raise ValueError(f"UNRESOLVED_FINDING_REF:{binding['finding_id']}")
        er_refs = binding.get("evidence_requirement_refs", [])
        if len(er_refs) != 1 or er_refs[0] not in requirements or er_refs[0] not in questions:
            raise ValueError(f"UNRESOLVED_ER_REF:{binding['binding_id']}")
        er = er_refs[0]
        question, requirement = questions[er], requirements[er]
        for ref in binding.get("observation_refs", []):
            if ref not in observations:
                raise ValueError(f"UNRESOLVED_OBSERVATION_REF:{ref}")
        direct_provenance = {row["observation_ref"]: row["provenance_class"] for row in binding.get("observation_provenance", [])}
        direct_rows = [_observation_row(ref, observations[ref], direct_provenance.get(ref, "BINDING_REFERENCE")) for ref in binding.get("observation_refs", [])]
        other = [row for row in retrieval_by_er.get(er, []) if row["observation_ref"] not in set(binding.get("observation_refs", []))]
        other_rows = []
        for row in other:
            ref = row["observation_ref"]
            if ref not in observations:
                raise ValueError(f"UNRESOLVED_DISPLAY_OBSERVATION_REF:{ref}")
            other_rows.append(_observation_row(ref, observations[ref], "RETRIEVED CANDIDATE — NOT FINDING EVIDENCE"))

        all_card_refs = binding.get("observation_refs", []) + [row["observation_ref"] for row in other]
        for ref in all_card_refs:
            displayed[ref] = observations[ref].get("source_space", "UNKNOWN")
        has_dbc = any(observations[ref].get("signal_name") for ref in all_card_refs)
        cards_with_dbc += int(has_dbc)
        cards_without_dbc += int(not has_dbc)
        gaps = finding.get("evidence_gaps", [])
        cards_with_gap += int(bool(gaps))
        relationship_limited = "RELATIONSHIP_FEATURE_UNAVAILABLE" in binding.get("uncertainty_flags", [])
        collection_limited = "PHASE_FEATURE_UNAVAILABLE" in binding.get("uncertainty_flags", [])
        cards_relationship += int(relationship_limited)
        cards_collection += int(collection_limited)
        mapping_row = next((row for row in finding.get("evidence_requirement_mapping", []) if row.get("evidence_requirement_ref") == er), {})
        title = question["semantic_need"].rstrip(".")
        lines.extend([
            f"## {er} — {title}", "",
            f"- Control Tree: `{finding.get('control_tree_ref', 'NO_SAFE_MAPPING')}`",
            f"- Binding / Finding: `{binding['binding_id']}` / `{finding['finding_id']}`",
            f"- Semantic status / confidence: `{binding.get('semantic_status')}` / `{binding.get('confidence')}`",
            f"- Program review state: `{binding.get('promotion_state')}`; human disposition: **UNSET**",
            "", "### L3 question", "",
            requirement.get("statement", question["semantic_need"]), "",
            f"Sufficiency boundary: {question.get('sufficiency_rule') or 'No additional frozen sufficiency rule.'}", "",
            "### Direct Finding evidence", "",
        ])
        lines.extend(_table(direct_rows) if direct_rows else ["No Observation is directly bound to this Finding."])
        lines.extend(["", "### Other retrieved candidates", "",
                      "These remain visible for review but were **not** used as Finding support.", ""])
        lines.extend(_table(other_rows) if other_rows else ["No additional retrieved candidate."])
        lines.extend(["", f"### DBC Semantic Reference — {REFERENCE_LABEL}", ""])
        dbc_items = [f"- `{ref}`: {_dbc_reference(observations[ref])}" for ref in all_card_refs if observations[ref].get("signal_name")]
        lines.extend(dbc_items or ["No DBC semantic name is defined for the displayed Observation(s)."])
        lines.extend(["", "This is **REFERENCE ONLY — NOT OBSERVED CONTROL CHAIN — NOT APPROVED EVIDENCE**.", "",
                      "### ASC observed behavior", ""])
        if direct_rows:
            lines.extend(f"- `{ref}`: {_observation_summary(observations[ref])}" for ref in binding["observation_refs"])
        else:
            lines.append("No directly bound frozen behavior.")
        unavailable = sorted({reason for ref in all_card_refs for reason in context_by_ref.get(ref, {}).get("provenance", {}).get("unavailable_reasons", [])})
        if collection_limited:
            lines.append("- Phase Feature: **UNAVAILABLE**. Planned windows provide context only and do not establish observed human event time.")
        if relationship_limited or "RELATIONSHIP_FEATURE_UNAVAILABLE" in unavailable:
            lines.append(f"- Relationship Evidence: **CURRENTLY LIMITED**. {RELATIONSHIP_LIMITATION}")
        lines.extend(["", "### AI interpretation", ""])
        lines.extend(f"- **{fact.get('claim_class', 'INFERRED')}**: {fact.get('statement', '')}" for fact in finding.get("fact_bindings", []))
        lines.extend(["", "### Currently supported", ""])
        if mapping_row.get("status") in {"DIRECT_SUPPORT", "PARTIAL_SUPPORT"}:
            lines.append(f"- ✓ Program mapping status is `{mapping_row['status']}` for the bounded statement above; Signal Validation remains required.")
        else:
            lines.append("- No direct semantic support is accepted by the program; displayed observations remain candidates only.")
        lines.extend(["", "### Not established", ""])
        lines.extend(f"- ✗ {gap.get('reason', 'The required semantic evidence remains incomplete.')}" for gap in gaps)
        if not gaps:
            lines.append("- No separate formal gap is recorded; this does not promote the Finding to Approved Evidence.")
        lines.extend(["", "### Evidence gap", ""])
        if gaps:
            for gap in gaps:
                lines.extend([f"- Gap: `{gap.get('gap_id')}`", f"- Missing evidence type: `{gap.get('missing_evidence_type', 'UNSPECIFIED')}`", f"- Why it matters: {gap.get('reason')}"])
        else:
            lines.append("No formal gap object is recorded.")
        if collection_limited:
            lines.extend(["", "### Collection limitation", "",
                          "The collection predates the current Evidence architecture. Missing physical measurements or human event timestamps are not reconstructed from DBC labels or planned times."])
        lines.extend(["", "### Audit trace", "",
                      f"- Observation refs: `{', '.join(binding.get('observation_refs', [])) or 'NONE'}`",
                      f"- Candidate refs: `{', '.join(binding.get('candidate_refs', [])) or 'NONE'}`",
                      f"- Raw ASC refs: `{', '.join(binding.get('raw_reference_closure', [])) or 'NONE'}`",
                      f"- Reasoning package: `{binding['provenance']['reasoning_input_package_id']}` / `{binding['provenance']['reasoning_input_package_hash']}`",
                      f"- Reasoning result: `{binding['provenance']['reasoning_result_id']}`", ""])

    after_hashes = {name: _sha256(path) for name, path in paths.items()}
    if after_hashes != before_hashes:
        raise RuntimeError("FROZEN_ARTIFACT_MUTATION_DETECTED")
    source_counts = Counter(displayed.values())
    metadata = {
        "packet_version": PACKET_VERSION,
        "experiment_id": package["experiment_context"]["experiment_id"],
        "status": "AWAITING_EVIDENCE_REVIEW",
        "card_count": len(mapping["bindings"]),
        "displayed_unique_observation_counts": {key: source_counts.get(key, 0) for key in ("KNOWN", "RESIDUAL", "UNKNOWN")},
        "cards_with_dbc_reference": cards_with_dbc,
        "cards_without_dbc_reference": cards_without_dbc,
        "cards_with_evidence_gap": cards_with_gap,
        "cards_with_relationship_limitation": cards_relationship,
        "cards_with_collection_limitation": cards_collection,
        "source_artifact_hashes": before_hashes,
        "human_review_submitted": False,
        "approved_evidence_generated": False,
        "analysis_input": False,
    }
    return "\n".join(lines).rstrip() + "\n", metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--metadata-output", type=Path)
    args = parser.parse_args()
    markdown, metadata = build_review_packet(args.run_dir)
    output = args.output or args.run_dir / f"{metadata['experiment_id']}_evidence_review_packet.md"
    output.write_text(markdown, encoding="utf-8")
    if args.metadata_output:
        args.metadata_output.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": metadata["status"], "output": str(output), **metadata}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
