import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from semantic_reasoning_contract import CONTRACT_VERSION, fingerprint, validate_reasoning_input, validate_reasoning_output


def input_package():
    value = {
        "contract_version": CONTRACT_VERSION,
        "source_observation_package_id": "OP-1",
        "source_observation_package_hash": "a" * 64,
        "experiment_context": {"experiment_id": "SYN", "time_policy": {}},
        "l3_context": {
            "control_tree_nodes": [{"node_id": "CT-1"}],
            "evidence_requirements": [{"evidence_requirement_id": "ER-REQUEST", "statement": "direct Request"}],
        },
        "event_anchors": [{"event_id": "EA-1", "source": "PLANNED_ONLY", "time_type": "PLANNED_TIME"}],
        "observations": [{"observation_id": "SO-1", "signal_name": "fooRequest", "raw_refs": []}],
        "candidates": [{"candidate_id": "C1"}],
        "consistency_results": [], "validation_states": [],
        "allowed_follow_up_operations": [],
        "reference_manifest": {
            "observation_refs": ["SO-1"], "candidate_refs": ["C1"], "relation_refs": [],
            "event_refs": ["EA-1"], "control_tree_refs": ["CT-1"],
            "evidence_requirement_refs": ["ER-REQUEST"], "raw_refs": [],
        },
        "independence_policy": {}, "fingerprints": {}, "package_id": "RP-1",
    }
    value["package_hash"] = fingerprint(value)
    return value


def output():
    package = input_package()
    return {
        "contract_version": CONTRACT_VERSION, "result_id": "R1",
        "input_package_id": package["package_id"], "input_package_hash": package["package_hash"],
        "follow_up_requests": [],
        "findings": [{
            "finding_id": "F1", "observation_refs": ["SO-1"], "candidate_refs": ["C1"],
            "event_refs": [], "fact_bindings": [{"claim_class": "OBSERVED", "support_refs": ["SO-1"], "statement": "field exists"}],
            "control_tree_ref": "CT-1", "evidence_requirement_mapping": [],
            "proposed_role": "REQUEST", "semantic_status": "UNVALIDATED",
            "causality_status": "CAUSALITY_NOT_ESTABLISHED", "model_interaction": "INSUFFICIENT_TO_MAP",
            "evidence_gaps": [{"gap_id": "G1"}], "signal_validation_needed": True,
        }],
    }


class SemanticReasoningContractTest(unittest.TestCase):
    def test_valid_minimal_contract(self):
        self.assertEqual([], validate_reasoning_input(input_package()))
        self.assertEqual([], validate_reasoning_output(input_package(), output()))

    def test_unknown_references_rejected(self):
        for field, value, marker in (
            ("observation_refs", ["BAD"], "UNKNOWN_OBSERVATION"),
            ("candidate_refs", ["BAD"], "UNKNOWN_CANDIDATE"),
            ("control_tree_ref", "BAD", "UNKNOWN_CONTROL_TREE"),
        ):
            changed = output(); changed["findings"][0][field] = value
            self.assertTrue(any(marker in item for item in validate_reasoning_output(input_package(), changed)))
        changed = output(); changed["findings"][0]["evidence_requirement_mapping"] = [{"evidence_requirement_ref": "BAD", "status": "PARTIAL_SUPPORT"}]
        self.assertTrue(any("UNKNOWN_ER" in item for item in validate_reasoning_output(input_package(), changed)))

    def test_role_time_causality_and_approval_boundaries(self):
        changed = output(); changed["findings"][0]["semantic_status"] = "CONFIRMED"
        self.assertTrue(any("HIGH_RISK" in item for item in validate_reasoning_output(input_package(), changed)))
        changed = output(); changed["findings"][0]["proposed_role"] = "ACTUAL"; changed["findings"][0]["evidence_requirement_mapping"] = [{"evidence_requirement_ref": "ER-REQUEST", "status": "DIRECT_SUPPORT"}]
        self.assertTrue(any("ACTUAL_SATISFIES_REQUEST" in item for item in validate_reasoning_output(input_package(), changed)))
        changed = output(); changed["findings"][0]["event_refs"] = ["EA-1"]; changed["findings"][0]["observed_latency_claimed"] = True
        self.assertTrue(any("PLANNED_TIME" in item for item in validate_reasoning_output(input_package(), changed)))
        changed = output(); changed["findings"][0]["causality_status"] = "CAUSALITY_CONFIRMED"
        self.assertTrue(any("INVALID_CAUSALITY" in item for item in validate_reasoning_output(input_package(), changed)))
        changed = output(); changed["findings"][0]["promotion_state"] = "APPROVED_EVIDENCE"
        self.assertTrue(any("MARKED_APPROVED" in item for item in validate_reasoning_output(input_package(), changed)))

    def test_followup_duplicate_and_leakage_rejected(self):
        changed = output(); changed["follow_up_requests"] = [{"operation": "ASC_READ"}]
        self.assertIn("FOLLOW_UP_NOT_ALLOWED", validate_reasoning_output(input_package(), changed))
        changed = output(); changed["findings"].append(copy.deepcopy(changed["findings"][0]))
        errors = validate_reasoning_output(input_package(), changed)
        self.assertIn("DUPLICATE_OR_MISSING_FINDING_ID", errors)
        self.assertIn("DUPLICATE_OR_MISSING_GAP_ID", errors)
        package = input_package(); package["expected_answer"] = "leak"; package["package_hash"] = fingerprint({k:v for k,v in package.items() if k != "package_hash"})
        self.assertTrue(any("LEAKAGE" in item for item in validate_reasoning_input(package)))

    def test_invented_numeric_statistic_rejected(self):
        changed = output(); changed["findings"][0]["fact_bindings"][0]["statement"] = "observed 999.5"
        self.assertTrue(any("CREATED_NUMERIC" in item for item in validate_reasoning_output(input_package(), changed)))


if __name__ == "__main__": unittest.main()
