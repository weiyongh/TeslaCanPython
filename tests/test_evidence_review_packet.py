import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]
from evidence_review_packet import REFERENCE_LABEL, build_review_packet


def dump(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


class EvidenceReviewPacketTest(unittest.TestCase):
    def fixture(self, root: Path):
        obs = [
            {"observation_id": "K1", "source_space": "KNOWN", "can_id": "0x1", "signal_name": "xRequest", "message_name": "M", "unit": "A", "change_count": 1, "raw_refs": [{"line_number": 1}]},
            {"observation_id": "R1", "source_space": "RESIDUAL", "bus_key": "ch1:0x2", "payload_cardinality": 2, "bit_transitions": [1], "raw_refs": []},
            {"observation_id": "U1", "source_space": "UNKNOWN", "bus_key": "ch1:0x3", "payload_cardinality": 3, "bit_transitions": [2], "raw_refs": []},
        ]
        package = {
            "experiment_context": {"experiment_id": "SYN"}, "package_id": "P", "package_hash": "h",
            "observations": obs,
            "semantic_evidence_questions": [{"evidence_requirement_ref": "ER-01", "semantic_need": "Identify request without substituting actual.", "sufficiency_rule": "Direct request required."}],
            "semantic_search_intents": [{"intent_id": "I1", "evidence_requirement_ref": "ER-01"}],
            "retrieval_results": [{"intent_id": "I1", "retrieved": [{"observation_ref": "K1"}, {"observation_ref": "R1"}, {"observation_ref": "U1"}]}],
            "l3_context": {"evidence_requirements": [{"evidence_requirement_id": "ER-01", "statement": "Identify request."}]},
        }
        finding = {"finding_id": "F1", "observation_refs": ["K1"], "candidate_refs": [], "control_tree_ref": "CT1", "fact_bindings": [{"claim_class": "OBSERVED", "statement": "The field changed."}], "evidence_requirement_mapping": [{"evidence_requirement_ref": "ER-01", "status": "PARTIAL_SUPPORT"}], "evidence_gaps": [{"gap_id": "G1", "missing_evidence_type": "DIRECT_REQUEST", "reason": "Request semantics remain unvalidated."}]}
        reasoning = {"result_id": "RR", "findings": [finding], "external_review_decisions": ["FORBIDDEN_SENTINEL"]}
        mapping = {"approval_state": "NOT_APPROVED", "bindings": [{"binding_id": "EB-0001", "finding_id": "F1", "evidence_requirement_refs": ["ER-01"], "observation_refs": ["K1"], "observation_provenance": [{"observation_ref": "K1", "provenance_class": "DIRECT_INTENT_RETRIEVAL"}], "candidate_refs": [], "semantic_status": "VALIDATION_REQUIRED", "confidence": "LOW", "promotion_state": "HUMAN_REVIEW_REQUIRED", "uncertainty_flags": ["PHASE_FEATURE_UNAVAILABLE", "RELATIONSHIP_FEATURE_UNAVAILABLE"], "evidence_gaps": finding["evidence_gaps"], "raw_reference_closure": ["ASC-L1"], "provenance": {"reasoning_input_package_id": "P", "reasoning_input_package_hash": "h", "reasoning_result_id": "RR"}}]}
        contexts = {"observation_contexts": [{"observation_ref": x, "provenance": {"unavailable_reasons": ["RELATIONSHIP_FEATURE_UNAVAILABLE"]}} for x in ("K1", "R1", "U1")]}
        for name, value in (("semantic_reasoning_input.json", package), ("semantic_reasoning_output.json", reasoning), ("evidence_mapping_draft.json", mapping), ("observation_contexts.json", contexts), ("runtime_audit.json", {"exit_status": "AWAITING_EVIDENCE_REVIEW", "asc_parse_count": 1})):
            dump(root / name, value)
        return package, reasoning, mapping

    def test_downstream_packet_preserves_frozen_inputs_and_boundaries(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); package, reasoning, mapping = self.fixture(root)
            before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir()}
            markdown, meta = build_review_packet(root)
            after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir()}
            self.assertEqual(before, after)
            self.assertEqual(package, json.loads((root / "semantic_reasoning_input.json").read_text()))
            self.assertEqual(reasoning, json.loads((root / "semantic_reasoning_output.json").read_text()))
            self.assertEqual(mapping, json.loads((root / "evidence_mapping_draft.json").read_text()))
            self.assertEqual({"KNOWN": 1, "RESIDUAL": 1, "UNKNOWN": 1}, meta["displayed_unique_observation_counts"])
            self.assertIn(REFERENCE_LABEL, markdown)
            self.assertIn("UNNAMED OBSERVATION", markdown)
            self.assertIn("Phase Feature: **UNAVAILABLE**", markdown)
            self.assertIn("Relationship Evidence: **CURRENTLY LIMITED**", markdown)
            self.assertIn("planned procedure times are not human action times", markdown)
            self.assertNotIn("FORBIDDEN_SENTINEL", markdown)
            self.assertFalse(meta["human_review_submitted"])
            self.assertFalse(meta["approved_evidence_generated"])
            self.assertFalse(meta["analysis_input"])

    def test_all_references_must_resolve_and_state_must_remain_waiting(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); self.fixture(root)
            mapping = json.loads((root / "evidence_mapping_draft.json").read_text())
            mapping["bindings"][0]["observation_refs"] = ["MISSING"]
            dump(root / "evidence_mapping_draft.json", mapping)
            with self.assertRaisesRegex(ValueError, "UNRESOLVED_OBSERVATION_REF"):
                build_review_packet(root)
            self.fixture(root)
            dump(root / "runtime_audit.json", {"exit_status": "APPROVED"})
            with self.assertRaisesRegex(ValueError, "REQUIRES_AWAITING"):
                build_review_packet(root)


if __name__ == "__main__": unittest.main()
