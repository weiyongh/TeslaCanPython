"""Versioned Phase 3 formal pipeline entry; Phase 3B.1 stops after Discovery."""
from __future__ import annotations

import argparse
import shutil
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis_charter import AnalysisCharter, resolve_repo_path
from can_discovery import discover
from observation_package import build_package, freeze_package
from runtime_audit import write_runtime_audit
from semantic_reasoning_contract import (
    build_reasoning_input, fingerprint, freeze_json,
    validate_reasoning_input, validate_reasoning_output,
)
from evidence_mapping_adapter import map_findings
from semantic_observation_retrieval import retrieve
from observation_context_adapter import build_context_bundle, load_procedure


PIPELINE_VERSION = "discovery-v1"
REASONING_PIPELINE_VERSION = "reasoning-v1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def execute_discovery(charter_path: Path, output_root: Path | None = None) -> tuple[Path, dict]:
    started_wall = time.perf_counter()
    started_at = _utc_now()
    charter = AnalysisCharter.load(charter_path)
    asc_path = resolve_repo_path(ROOT, charter.asc_ref)
    dbc_paths = [resolve_repo_path(ROOT, ref) for ref in charter.dbc_refs]
    permitted = set(charter.allowed_data_sources)
    referenced = {charter.asc_ref, *charter.dbc_refs}
    if not referenced <= permitted:
        raise ValueError("ASC_ADMISSION_FAILURE: refs absent from allowed_data_sources")

    run_id = f"{datetime.now().strftime('%Y%m%dT%H%M%S')}-{uuid.uuid4().hex[:8]}"
    run_dir = (output_root or ROOT / "output" / charter.experiment_id / "pipeline_v3") / run_id
    discovery = discover(
        asc_path,
        dbc_paths,
        experiment_id=charter.experiment_id,
        purpose=charter.purpose,
        known_signal_hints=charter.known_signal_hints,
    )
    package = build_package(
        discovery,
        charter_ref=str(charter_path),
        charter_hash=charter.fingerprint,
    )
    package_path = run_dir / "observation_package.json"
    freeze_package(package, package_path)
    ended_at = _utc_now()
    audit = {
        "pipeline_version": PIPELINE_VERSION,
        "run_id": run_id,
        "experiment_id": charter.experiment_id,
        "analysis_charter_hash": charter.fingerprint,
        "asc_hash": discovery["asc_integrity"]["sha256"],
        "dbc_fingerprints": discovery["dbc_fingerprints"],
        "discovery_algorithm_version": discovery["discovery_algorithm_version"],
        "discovery_fingerprint": package["collection_fingerprints"]["observations_sha256"],
        "parsed_frame_count": discovery["asc_integrity"]["parsed_frame_count"],
        "bus_key_count": discovery["closure"]["parsed_bus_key_count"],
        "observation_count": len(discovery["observations"]),
        "disposition_count": len(discovery["dispositions"]),
        "coverage_counts": discovery["coverage_counts"],
        "known_count": len(discovery["signal_summaries"]),
        "residual_count": len(discovery["residual_summaries"]),
        "unknown_count": len(discovery["unknown_summaries"]),
        "candidate_count": len(discovery["candidates"]),
        "candidate_discard_count": discovery["candidate_compression"]["discarded_total"],
        "asc_parse_count": discovery["asc_parse_count"],
        "stage_start": started_at,
        "stage_end": ended_at,
        "wall_clock_seconds": round(time.perf_counter() - started_wall, 6),
        "package_hash": package["package_hash"],
        "exit_status": "DISCOVERY_COMPLETE",
        "legacy_or_new_path": "NEW_EXPLICIT_VERSIONED_PATH",
        "llm_calls": 0,
        "semantic_reasoning_calls": 0,
        "evidence_mapping_calls": 0,
        "renderer_calls": 0,
    }
    write_runtime_audit(audit, run_dir / "runtime_audit.json")
    return run_dir, audit


def prepare_reasoning(
    charter_path: Path,
    run_dir: Path,
    output_run_dir: Path | None = None,
) -> tuple[dict, dict]:
    source_run_dir = run_dir
    if output_run_dir is not None:
        if output_run_dir.exists():
            raise FileExistsError(f"replay output already exists: {output_run_dir}")
        output_run_dir.mkdir(parents=True)
        for filename in ("observation_package.json", "runtime_audit.json"):
            shutil.copy2(source_run_dir / filename, output_run_dir / filename)
        run_dir = output_run_dir
    package_path = run_dir / "observation_package.json"
    audit_path = run_dir / "runtime_audit.json"
    observation = json.loads(package_path.read_text(encoding="utf-8"))
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    if audit.get("exit_status") not in {"DISCOVERY_COMPLETE", "REASONING_INPUT_FROZEN", "AWAITING_EVIDENCE_REVIEW"}:
        raise ValueError("REASONING_INPUT_CONTRACT_FAILURE: DISCOVERY_COMPLETE required")
    charter = AnalysisCharter.load(charter_path)
    if output_run_dir is not None:
        audit["run_id"] = run_dir.name
        audit["replay_source_run"] = str(source_run_dir)
        audit["asc_reparse_for_replay"] = 0
    semantic_source = json.loads(resolve_repo_path(ROOT, charter.semantic_context_ref).read_text(encoding="utf-8"))
    experiment_context = {"experiment_id": charter.experiment_id, "purpose": charter.purpose, "system_scope": charter.system_scope, "analysis_scope": charter.analysis_scope, "time_policy": charter.time_policy, "experiment_procedure_ref": charter.experiment_procedure_ref}
    if not charter.experiment_procedure_ref:
        raise ValueError("REASONING_INPUT_CONTRACT_FAILURE: experiment_procedure_ref missing")
    procedure_path = resolve_repo_path(ROOT, charter.experiment_procedure_ref)
    procedure = load_procedure(procedure_path, charter.experiment_id)
    context_bundle = build_context_bundle(observation, semantic_source["l3_context"], procedure)
    retrieval_bundle = retrieve(observation, semantic_source["l3_context"], experiment_context, context_bundle)
    freeze_json(procedure, run_dir / "experiment_procedure.json")
    freeze_json({"context_version": context_bundle["context_version"], "context_hash": context_bundle["context_hash"], "observation_contexts": context_bundle["observation_contexts"]}, run_dir / "observation_contexts.json")
    freeze_json({"context_version": context_bundle["context_version"], "evidence_questions": context_bundle["evidence_questions"]}, run_dir / "semantic_evidence_questions.json")
    freeze_json({"retrieval_version": retrieval_bundle["retrieval_version"], "intents": retrieval_bundle["intents"]}, run_dir / "semantic_search_intents.json")
    freeze_json({"retrieval_version": retrieval_bundle["retrieval_version"], "results": retrieval_bundle["results"], "selected_observation_refs": retrieval_bundle["selected_observation_refs"]}, run_dir / "semantic_retrieval_results.json")
    freeze_json({
        **{k: retrieval_bundle[k] for k in ("retrieval_version", "retrieval_input_hash", "retrieval_output_hash", "limits")},
        "intent_audit": [{
            key: result[key] for key in ("intent_id", "source_space_counts", "eligible_count", "below_threshold_count", "truncated_count", "global_limit_excluded_count", "no_suitable_observation")
        } for result in retrieval_bundle["results"]],
        "selected_observation_count": len(retrieval_bundle["selected_observation_refs"]),
    }, run_dir / "semantic_retrieval_audit.json")
    audit["exit_status"] = "SEMANTIC_RETRIEVAL_COMPLETE"
    reasoning_input = build_reasoning_input(observation, charter, ROOT, retrieval_bundle)
    freeze_json(reasoning_input, run_dir / "semantic_reasoning_input.json")
    audit.update({
        "pipeline_version": REASONING_PIPELINE_VERSION,
        "reasoning_input_package_id": reasoning_input["package_id"],
        "reasoning_input_package_hash": reasoning_input["package_hash"],
        "semantic_prior_fingerprint": reasoning_input["fingerprints"]["semantic_prior"],
        "control_tree_fingerprint": reasoning_input["fingerprints"]["control_tree"],
        "evidence_requirement_fingerprint": reasoning_input["fingerprints"]["evidence_requirements"],
        "reasoning_call_count": 0,
        "follow_up_count": 0,
        "retrieval_version": retrieval_bundle["retrieval_version"],
        "retrieval_input_hash": retrieval_bundle["retrieval_input_hash"],
        "retrieval_output_hash": retrieval_bundle["retrieval_output_hash"],
        "retrieved_observation_count": len(retrieval_bundle["selected_observation_refs"]),
        "experiment_procedure_hash": procedure["source"]["sha256"],
        "observation_context_hash": context_bundle["context_hash"],
        "semantic_evidence_question_count": len(context_bundle["evidence_questions"]),
        "exit_status": "REASONING_INPUT_FROZEN",
    })
    write_runtime_audit(audit, audit_path)
    return reasoning_input, audit


def complete_reasoning(run_dir: Path, output_path: Path, *, model_identity: str) -> tuple[dict, dict]:
    started = time.perf_counter()
    reasoning_start = _utc_now()
    input_path = run_dir / "semantic_reasoning_input.json"
    audit_path = run_dir / "runtime_audit.json"
    package = json.loads(input_path.read_text(encoding="utf-8"))
    output = json.loads(output_path.read_text(encoding="utf-8"))
    validation_started = time.perf_counter()
    errors = validate_reasoning_output(package, output)
    validation_seconds = time.perf_counter() - validation_started
    validation = {
        "validation_version": "formal-semantic-validation-v1",
        "valid": not errors,
        "errors": errors,
        "unknown_reference_count": sum("UNKNOWN_" in error for error in errors),
        "validated_at": _utc_now(),
    }
    freeze_json(validation, run_dir / "semantic_reasoning_validation.json")
    if errors:
        raise ValueError("SEMANTIC_REASONING_FAILURE: " + ";".join(errors))
    canonical_output = run_dir / "semantic_reasoning_output.json"
    if output_path.resolve() != canonical_output.resolve():
        freeze_json(output, canonical_output)
    mapping_start = _utc_now()
    mapping_started = time.perf_counter()
    mapping = map_findings(package, output)
    freeze_json(mapping, run_dir / "evidence_mapping_draft.json")
    mapping_end = _utc_now()
    mapping_seconds = time.perf_counter() - mapping_started
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    audit.update({
        "reasoning_model_identity": model_identity,
        "reasoning_call_count": 1,
        "follow_up_count": output.get("audit_metadata", {}).get("follow_up_count", 0),
        "reasoning_output_hash": fingerprint(output),
        "reasoning_reference_validation": "PASS",
        "unknown_reference_count": 0,
        "finding_count": len(output.get("findings", [])),
        "evidence_binding_draft_count": len(mapping["bindings"]),
        "promotion_state_counts": mapping["promotion_state_counts"],
        "reasoning_start": reasoning_start,
        "reasoning_end": mapping_start,
        "reasoning_runtime_seconds": None,
        "reasoning_runtime_note": "Model executed outside the Python orchestrator; exact model-only runtime unavailable.",
        "validation_runtime_seconds": round(validation_seconds, 6),
        "mapping_start": mapping_start,
        "mapping_end": mapping_end,
        "mapping_runtime_seconds": round(mapping_seconds, 6),
        "completion_wall_clock_seconds": round(time.perf_counter() - started, 6),
        "asc_parse_count_after_reasoning": audit["asc_parse_count"],
        "exit_status": "AWAITING_EVIDENCE_REVIEW",
    })
    write_runtime_audit(audit, audit_path)
    return mapping, audit


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pipeline-version", default="legacy")
    parser.add_argument("--charter", type=Path)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--stage", choices=("freeze-input", "validate-map"))
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--output-run-dir", type=Path)
    parser.add_argument("--reasoning-output", type=Path)
    parser.add_argument("--model-identity", default="unspecified-bounded-model")
    args = parser.parse_args()
    if args.pipeline_version == "legacy":
        print(json.dumps({
            "status": "LEGACY_UNCHANGED",
            "message": "No formal pipeline selected; use the existing experiment analyzer.",
        }))
        return
    if args.pipeline_version == REASONING_PIPELINE_VERSION:
        if not args.charter or not args.run_dir or not args.stage:
            parser.error("reasoning-v1 requires --charter, --run-dir, and --stage")
        if args.stage == "freeze-input":
            package, audit = prepare_reasoning(args.charter, args.run_dir, args.output_run_dir)
            print(json.dumps({"status": audit["exit_status"], "package_id": package["package_id"], "package_hash": package["package_hash"]}, indent=2))
        else:
            if not args.reasoning_output:
                parser.error("validate-map requires --reasoning-output")
            mapping, audit = complete_reasoning(args.run_dir, args.reasoning_output, model_identity=args.model_identity)
            print(json.dumps({"status": audit["exit_status"], "bindings": len(mapping["bindings"])}, indent=2))
        return
    if args.pipeline_version != PIPELINE_VERSION:
        parser.error(f"unsupported pipeline version: {args.pipeline_version}")
    if args.charter is None:
        parser.error("--charter is required for discovery-v1")
    run_dir, audit = execute_discovery(args.charter, args.output_root)
    print(json.dumps({"run_dir": str(run_dir), **audit}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
