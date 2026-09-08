import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]
from pre_llm_input_audit import DBC_NOTICE, UNRECORDED, build_pre_llm_audit


def write(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


class PreLlmInputAuditTest(unittest.TestCase):
    def fixture(self, root: Path):
        observations = [
            {"observation_id": "K", "source_space": "KNOWN", "can_id": "0x1", "message_name": "M", "signal_name": "named", "change_count": 1},
            {"observation_id": "R", "source_space": "RESIDUAL", "bus_key": "ch1:0x2", "payload_cardinality": 2, "bit_transitions": [1]},
            {"observation_id": "U", "source_space": "UNKNOWN", "bus_key": "ch1:0x3", "payload_cardinality": 2, "bit_transitions": [2]},
        ]
        contexts = [{"observation_ref": ref, "identity_hint": {}, "behavior": {}, "phase_alignment": {"planned": [], "observed_event_phase": "OBSERVED_EVENT_PHASE_UNAVAILABLE"}, "provenance": {"unavailable_reasons": ["TRACE_STORE_UNAVAILABLE", "RELATIONSHIP_FEATURE_UNAVAILABLE"]}} for ref in ("K", "R", "U")]
        package = {
            "experiment_context": {"experiment_id": "SYN"}, "package_id": "P", "package_hash": "h",
            "l3_context": {"evidence_requirements": [{"evidence_requirement_id": "ER-01", "statement": "目标"}]},
            "semantic_evidence_questions": [{"question_id": "Q1", "evidence_requirement_ref": "ER-01", "control_tree_refs": ["CT1"], "semantic_need": "识别目标", "sufficiency_rule": "需要直接证据", "candidate_roles": ["STATE"], "forbidden_substitutions": ["ACTUAL"], "planned_phase_refs": ["PP1"]}],
            "experiment_procedure": {"planned_phases": [{"phase_id": "PP1", "label": "计划阶段", "start_s": 0, "end_s": 1}]},
            "per_question_evidence": [{"evidence_question_ref": "Q1", "intent_ref": "I1", "direct_observation_refs": ["K", "R", "U"], "cross_intent_supplements": [], "global_context_only": []}],
            "semantic_search_intents": [{"intent_id": "I1"}],
            "retrieval_results": [{"intent_id": "I1", "retrieved": [{"observation_ref": ref, "eligibility_path": "PATH", "retrieval_reasons": ["ROUTE"], "context_matches": {}} for ref in ("K", "R", "U")]}],
            "observations": observations, "observation_contexts": contexts,
            "external_golden_review": "MUST_NOT_APPEAR",
        }
        output = {"findings": [{"finding_id": "F1"}]}
        mapping = {"approval_state": "NOT_APPROVED", "mapping_hash": "mh"}
        runtime = {"run_id": "RUN", "exit_status": "AWAITING_EVIDENCE_REVIEW", "asc_parse_count": 1, "reasoning_call_count": 1, "follow_up_count": 0}
        for name, value in (("semantic_reasoning_input.json", package), ("semantic_reasoning_output.json", output), ("evidence_mapping_draft.json", mapping), ("runtime_audit.json", runtime)):
            write(root / name, value)
        return package, output, mapping

    def test_exact_frozen_er_input_and_boundaries_are_visible_without_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); package, output, mapping = self.fixture(root)
            before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir()}
            markdown, meta = build_pre_llm_audit(root)
            after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir()}
            self.assertEqual(before, after)
            self.assertEqual(package, json.loads((root / "semantic_reasoning_input.json").read_text()))
            self.assertEqual(output, json.loads((root / "semantic_reasoning_output.json").read_text()))
            self.assertEqual(mapping, json.loads((root / "evidence_mapping_draft.json").read_text()))
            self.assertEqual(1, meta["er_count"])
            self.assertEqual(3, meta["unique_observation_count"])
            self.assertEqual({"KNOWN": 1, "RESIDUAL": 1, "UNKNOWN": 1}, meta["source_space_counts"])
            self.assertTrue(all(ref in markdown for ref in ("K", "R", "U")))
            self.assertIn(DBC_NOTICE, markdown)
            self.assertIn("UNNAMED", markdown)
            self.assertIn("OBSERVED_EVENT_PHASE_UNAVAILABLE", markdown)
            self.assertIn("RELATIONSHIP_FEATURE_UNAVAILABLE", markdown)
            self.assertIn("PLANNED_TIME_IS_NOT_OBSERVED_EVENT_TIME", markdown)
            self.assertNotIn("MUST_NOT_APPEAR", markdown)
            self.assertFalse(meta["exact_final_llm_payload_recoverable"])
            self.assertIn("冻结运行未保留可证明的最终 LLM Call Payload", markdown)
            self.assertEqual(UNRECORDED, meta["model_visibility"]["provider"])

    def test_no_analysis_or_downstream_execution_and_reference_closure(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); self.fixture(root)
            _, meta = build_pre_llm_audit(root)
            self.assertFalse(meta["asc_reread"])
            self.assertEqual(0, meta["asc_parse_delta"])
            self.assertFalse(meta["retrieval_rerun"])
            self.assertFalse(meta["reasoning_rerun"])
            self.assertEqual(0, meta["llm_calls_for_audit"])
            self.assertFalse(meta["finding_changed"])
            self.assertFalse(meta["evidence_mapping_changed"])
            self.assertFalse(meta["approved_evidence_generated"])
            self.assertFalse(meta["downstream_artifacts_generated"])
            package = json.loads((root / "semantic_reasoning_input.json").read_text())
            package["per_question_evidence"][0]["direct_observation_refs"] = ["MISSING"]
            write(root / "semantic_reasoning_input.json", package)
            with self.assertRaisesRegex(ValueError, "UNRESOLVED_OBSERVATION_REF"):
                build_pre_llm_audit(root)


if __name__ == "__main__": unittest.main()
