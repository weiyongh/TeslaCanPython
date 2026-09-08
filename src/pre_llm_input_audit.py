"""从冻结 Reasoning Input 生成只读的 LLM 前分析输入审计。"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


AUDIT_VERSION = "pre-llm-analysis-input-audit-v1"
UNRECORDED = "冻结运行中未记录"
DBC_NOTICE = "DBC REFERENCE METADATA — 仅供参考，不是 Evidence"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _flat(value: Any) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|").strip()


def _behavior(observation: dict[str, Any], context: dict[str, Any]) -> str:
    behavior = context.get("behavior", {})
    parts = []
    for label, value in (
        ("稳定性", observation.get("stability_class") or behavior.get("stability_class")),
        ("变化次数", observation.get("change_count", behavior.get("change_count"))),
        ("最小值", observation.get("minimum")),
        ("最大值", observation.get("maximum")),
        ("首次变化", observation.get("first_change_time_s", behavior.get("first_change_time_s"))),
        ("末次变化", observation.get("last_change_time_s", behavior.get("last_change_time_s"))),
    ):
        if value is not None:
            suffix = " s（CAN Observed Time）" if label in {"首次变化", "末次变化"} else ""
            parts.append(f"{label}={value}{suffix}")
    if observation.get("sequence"):
        seq = observation["sequence"][:8]
        parts.append("序列=" + " → ".join(map(str, seq)) + (" …" if len(observation["sequence"]) > 8 else ""))
    if not parts:
        parts.append(f"payload 基数={observation.get('payload_cardinality')}; bit transitions={sum(observation.get('bit_transitions', []))}")
    return "；".join(parts)


def _dbc(observation: dict[str, Any]) -> str:
    if not observation.get("signal_name"):
        return "NONE / UNKNOWN / NOT DEFINED"
    values = [observation.get("message_name"), observation.get("signal_name")]
    if observation.get("unit"):
        values.append(f"unit={observation['unit']}")
    if observation.get("enum_definition"):
        values.append("enum=" + json.dumps(observation["enum_definition"], ensure_ascii=False, sort_keys=True))
    return " / ".join(_flat(x) for x in values if x)


def _model_visibility(runtime: dict[str, Any]) -> dict[str, Any]:
    return {
        "provider": runtime.get("model_provider") or UNRECORDED,
        "model_name": runtime.get("model_name") or UNRECORDED,
        "model_identity": runtime.get("reasoning_model_identity") or UNRECORDED,
        "effort": runtime.get("reasoning_effort") or UNRECORDED,
        "llm_calls_in_frozen_run": runtime.get("reasoning_call_count", UNRECORDED),
        "follow_up_calls_in_frozen_run": runtime.get("follow_up_count", UNRECORDED),
    }


def build_pre_llm_audit(run_dir: Path) -> tuple[str, dict[str, Any]]:
    paths = {
        "reasoning_input": run_dir / "semantic_reasoning_input.json",
        "reasoning_output": run_dir / "semantic_reasoning_output.json",
        "evidence_mapping": run_dir / "evidence_mapping_draft.json",
        "runtime_audit": run_dir / "runtime_audit.json",
    }
    optional_sources = {
        "experiment_procedure": run_dir / "experiment_procedure.json",
        "semantic_questions": run_dir / "semantic_evidence_questions.json",
        "semantic_intents": run_dir / "semantic_search_intents.json",
        "retrieval_results": run_dir / "semantic_retrieval_results.json",
        "observation_contexts": run_dir / "observation_contexts.json",
    }
    paths.update({name: path for name, path in optional_sources.items() if path.is_file()})
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise ValueError("PRE_LLM_AUDIT_SOURCE_MISSING:" + ",".join(missing))
    hashes_before = {name: _sha(path) for name, path in paths.items()}
    package = _load(paths["reasoning_input"])
    runtime = _load(paths["runtime_audit"])
    if runtime.get("exit_status") != "AWAITING_EVIDENCE_REVIEW":
        raise ValueError("PRE_LLM_AUDIT_REQUIRES_AWAITING_EVIDENCE_REVIEW")

    questions = package.get("semantic_evidence_questions", [])
    evidence_rows = package.get("per_question_evidence", [])
    if len(questions) != len(evidence_rows):
        raise ValueError("QUESTION_EVIDENCE_CARDINALITY_MISMATCH")
    observations = {row["observation_id"]: row for row in package.get("observations", [])}
    contexts = {row["observation_ref"]: row for row in package.get("observation_contexts", [])}
    intents = {row["intent_id"]: row for row in package.get("semantic_search_intents", [])}
    retrievals = {row["intent_id"]: row for row in package.get("retrieval_results", [])}
    requirements = {row["evidence_requirement_id"]: row for row in package["l3_context"]["evidence_requirements"]}
    procedures = {row["phase_id"]: row for row in package.get("experiment_procedure", {}).get("planned_phases", [])}
    evidence_by_question = {row["evidence_question_ref"]: row for row in evidence_rows}
    model = _model_visibility(runtime)

    all_refs: list[str] = []
    retrieval_rows = 0
    for result in retrievals.values():
        retrieval_rows += len(result.get("retrieved", []))
    lines = [
        f"# {package['experiment_context']['experiment_id']} LLM 前分析输入审计",
        "",
        "> 这是 LLM 前输入可见性产物，不是 Human Evidence Review，不是 Approved Evidence。",
        "",
        "## 总览", "",
        f"- Experiment / Run ID：`{package['experiment_context']['experiment_id']}` / `{runtime.get('run_id', UNRECORDED)}`",
        f"- Reasoning Package ID：`{package.get('package_id')}`",
        f"- Package Hash：`{package.get('package_hash')}`",
        f"- Evidence Requirement / Semantic Question：{len(requirements)} / {len(questions)}",
        f"- Retrieval 总行数：{retrieval_rows}",
        f"- Unique Observation：{len(observations)}",
        f"- Model Provider：{model['provider']}",
        f"- Model Name：{model['model_name']}",
        f"- Model Identity：{model['model_identity']}",
        f"- Reasoning / Effort：{model['effort']}",
        f"- 冻结运行 LLM Call：{model['llm_calls_in_frozen_run']}",
        f"- 冻结运行 Follow-up Call：{model['follow_up_calls_in_frozen_run']}",
        "- 本次审计新增 LLM Call：0", "",
        "### Source Artifact 与 Hash", "",
    ]
    lines.extend(f"- `{path.name}`：`{hashes_before[name]}`" for name, path in paths.items())
    lines.extend([
        "", "## 实际 LLM Payload 可见性", "",
        "冻结运行未保留可证明的最终 LLM Call Payload。", "",
        "冻结运行没有保存可核验的 System / Developer Instruction、Provider、真实 Model Name、Effort 或最终请求 envelope；当前代码也没有可证明与当时调用完全相同的确定性 Call Builder。因此本产物不声称重建 Exact Payload。", "",
        "最接近调用边界、可验证的权威 Pre-call Object 是：", "",
        "- `semantic_reasoning_input.json` 根对象：JSON Pointer `/`",
        f"- Package ID / Hash：`{package.get('package_id')}` / `{package.get('package_hash')}`",
        "- Canonical request envelope：不可证明，未生成近似 envelope。", "",
    ])

    for q_index, question in enumerate(questions):
        qid = question["question_id"]
        er = question["evidence_requirement_ref"]
        evidence = evidence_by_question.get(qid)
        if evidence is None:
            raise ValueError(f"MISSING_PER_QUESTION_EVIDENCE:{qid}")
        intent_id = evidence["intent_ref"]
        if intent_id not in intents or intent_id not in retrievals:
            raise ValueError(f"UNRESOLVED_INTENT_REF:{intent_id}")
        retrieval_by_ref = {row["observation_ref"]: row for row in retrievals[intent_id].get("retrieved", [])}
        provenance_groups = (
            ("direct_observation_refs", "DIRECT_INTENT_RETRIEVAL"),
            ("cross_intent_supplements", "CROSS_INTENT_SUPPLEMENT"),
            ("global_context_only", "GLOBAL_CONTEXT_ONLY"),
        )
        supplied: list[tuple[str, str, dict[str, Any]]] = []
        for field, default_provenance in provenance_groups:
            for value in evidence.get(field, []):
                ref = value if isinstance(value, str) else value.get("observation_ref")
                if ref not in observations:
                    raise ValueError(f"UNRESOLVED_OBSERVATION_REF:{qid}:{ref}")
                supplied.append((ref, default_provenance, retrieval_by_ref.get(ref, {})))
                all_refs.append(ref)
        phase_refs = question.get("planned_phase_refs", [])
        phase_text = []
        for ref in phase_refs:
            phase = procedures.get(ref)
            if not phase:
                raise ValueError(f"UNRESOLVED_PROCEDURE_REF:{qid}:{ref}")
            phase_text.append(f"`{ref}`（{phase.get('action') or phase.get('label') or phase.get('name') or '冻结输入中未记录动作'}；{phase.get('start_s')}–{phase.get('end_s')} s；PLANNED_TIME）")
        lines.extend([
            f"## {er} — {question['semantic_need'].rstrip('.')}", "",
            "### A. 语义目标", "",
            f"- ER：`{er}`",
            f"- Control Tree Reference：`{', '.join(question.get('control_tree_refs', [])) or 'NONE'}`",
            f"- Semantic Evidence Question：{question['semantic_need']}",
            f"- Sufficiency / Semantic Boundary：{question.get('sufficiency_rule') or '冻结输入中未记录'}",
            f"- Candidate Role（未确认）：`{', '.join(question.get('candidate_roles', [])) or 'NONE'}`",
            f"- Forbidden Substitution：`{', '.join(question.get('forbidden_substitutions', [])) or 'NONE'}`",
            f"- Collection Script / Planned Procedure Context：{'; '.join(phase_text) or '本 ER 未关联 planned phase'}`".rstrip("`"),
            "- 时间边界：`PLANNED_TIME_IS_NOT_OBSERVED_EVENT_TIME`", "",
            "### B. 实际送入 LLM 的 Observation", "",
            "| Observation | Space | CAN ID / Bus | Message / Signal | DBC 参考 | ASC 实际行为 | Retrieval Provenance |",
            "|---|---|---|---|---|---|---|",
        ])
        for ref, provenance, retrieval in supplied:
            obs, ctx = observations[ref], contexts.get(ref, {})
            identity = f"{obs.get('message_name') or '—'} / {obs.get('signal_name') or 'UNNAMED'}"
            reasons = ", ".join(retrieval.get("retrieval_reasons", [])) or provenance
            lines.append("| " + " | ".join(map(_flat, [ref, obs.get("source_space"), obs.get("can_id") or obs.get("bus_key"), identity, _dbc(obs), _behavior(obs, ctx), f"{provenance}; {reasons}"])) + " |")
        if not supplied:
            lines.append("| NONE | — | — | — | — | 本 ER 没有实际送入的 Observation | — |")
        lines.extend(["", f"### C. 为什么进入输入（{DBC_NOTICE}）", ""])
        for ref, provenance, retrieval in supplied:
            matches = retrieval.get("context_matches", {})
            lines.append(f"- `{ref}`：provenance=`{provenance}`；eligibility_path=`{retrieval.get('eligibility_path', '冻结输入中未记录')}`；retrieval_reasons=`{', '.join(retrieval.get('retrieval_reasons', [])) or '冻结输入中未记录'}`；context_matches=`{json.dumps(matches, ensure_ascii=False, sort_keys=True)}`。不据此确认 Semantic Role。")
        lines.extend(["", "### D. LLM 获得的 Structured Context", ""])
        for ref, _, _ in supplied:
            ctx = contexts.get(ref, {})
            phase = ctx.get("phase_alignment", {})
            lines.extend([
                f"- `{ref}` identity_hint：`{json.dumps(ctx.get('identity_hint', {}), ensure_ascii=False, sort_keys=True)}`",
                f"- `{ref}` behavior：`{json.dumps(ctx.get('behavior', {}), ensure_ascii=False, sort_keys=True)}`",
                f"- `{ref}` planned phase alignment：`{json.dumps(phase.get('planned', []), ensure_ascii=False, sort_keys=True)}`",
                f"- `{ref}` Phase Feature：`{phase.get('observed_event_phase', 'UNAVAILABLE')}`",
                f"- `{ref}` Relationship Feature：`{', '.join(ctx.get('provenance', {}).get('unavailable_reasons', [])) or '冻结输入中未记录'}`",
            ])
        lines.extend(["", "### E. 精确输入追溯", "",
                      f"- Question：`/semantic_evidence_questions/{q_index}`",
                      f"- Per-question evidence：`/per_question_evidence/{q_index}`",
                      f"- Intent：`/semantic_search_intents/{list(intents).index(intent_id)}` (`{intent_id}`)",
                      f"- Retrieval result：`/retrieval_results/{list(retrievals).index(intent_id)}`",
                      "- Observation objects：" + ", ".join(f"`/observations/{list(observations).index(ref)}` → `{ref}`" for ref, _, _ in supplied),
                      "- Observation contexts：" + ", ".join(f"`/observation_contexts/{list(contexts).index(ref)}` → `{ref}`" for ref, _, _ in supplied), ""])

    spaces = Counter(observations[ref].get("source_space", "UNKNOWN") for ref in set(all_refs))
    lines.extend([
        "## LLM 没有收到什么", "",
        "以下边界可由冻结输入直接证明：", "",
        "- 完整 synchronized cross-signal Relationship Feature：未提供；冻结输入标记为 `RELATIONSHIP_FEATURE_UNAVAILABLE`。",
        "- Observed Human Event Timestamp：未提供；只有 planned procedure context，且明确为 `PLANNED_TIME_IS_NOT_OBSERVED_EVENT_TIME`。",
        "- Frozen Trace Store / CAN region detail：未提供；相关 context 标记为 `TRACE_STORE_UNAVAILABLE` / `CAN_REGION_DETAIL_UNAVAILABLE`。",
        "- 原采集没有独立记录的车外物理量或人工操作事实：未由 DBC 名称、planned time 或历史报告补造。",
        "- External Golden Review Decision：不在 `semantic_reasoning_input.json` 中。",
        "- Approved Evidence、Assessment、Final Report Conclusion：不在该 Pre-call Object 中。",
        "- Phase 3B.2.4 Review Packet：是后生成的下游展示产物，不在冻结 Reasoning Input 中。", "",
        "## 审计边界", "",
        "本产物只呈现冻结输入，不新增 ranking、Signal whitelist、Semantic Role、relationship、Finding 或 review decision。所有 DBC 内容均为 Reference Metadata。", "",
    ])
    hashes_after = {name: _sha(path) for name, path in paths.items()}
    if hashes_before != hashes_after:
        raise RuntimeError("FROZEN_SOURCE_ARTIFACT_CHANGED")
    metadata = {
        "audit_version": AUDIT_VERSION,
        "status": "AWAITING_EVIDENCE_REVIEW",
        "frozen_run": runtime.get("run_id"),
        "reasoning_package_id": package.get("package_id"),
        "reasoning_package_hash": package.get("package_hash"),
        "er_count": len(requirements),
        "semantic_question_count": len(questions),
        "retrieval_row_count": retrieval_rows,
        "unique_observation_count": len(set(all_refs)),
        "source_space_counts": {key: spaces.get(key, 0) for key in ("KNOWN", "RESIDUAL", "UNKNOWN")},
        "exact_final_llm_payload_recoverable": False,
        "model_visibility": model,
        "source_hashes_before": hashes_before,
        "source_hashes_after": hashes_after,
        "asc_reread": False,
        "asc_parse_delta": 0,
        "retrieval_rerun": False,
        "reasoning_rerun": False,
        "llm_calls_for_audit": 0,
        "finding_changed": False,
        "evidence_mapping_changed": False,
        "approved_evidence_generated": False,
        "downstream_artifacts_generated": False,
    }
    return "\n".join(lines).rstrip() + "\n", metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--metadata-output", type=Path)
    args = parser.parse_args()
    markdown, metadata = build_pre_llm_audit(args.run_dir)
    output = args.output or args.run_dir / f"{metadata['frozen_run'].split('-')[0]}_pre_llm_analysis_input_audit.md"
    output.write_text(markdown, encoding="utf-8")
    if args.metadata_output:
        args.metadata_output.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), **metadata}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
