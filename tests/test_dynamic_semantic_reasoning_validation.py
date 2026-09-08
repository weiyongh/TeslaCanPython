import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from spikes.dynamic_semantic_reasoning_validation import object_hash, validate_input, validate_output


ARTIFACT_DIR = ROOT / "output" / "TM3-015" / "reasoning_spike"


class DynamicSemanticReasoningValidationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = json.loads((ARTIFACT_DIR / "reasoning_input.json").read_text(encoding="utf-8"))
        cls.output = json.loads((ARTIFACT_DIR / "reasoning_output.json").read_text(encoding="utf-8"))
        cls.comparison = json.loads((ARTIFACT_DIR / "hidden_comparison.json").read_text(encoding="utf-8"))

    def test_frozen_input_hash_and_source_traceability(self):
        payload = copy.deepcopy(self.package)
        expected = payload["package_hash"]
        payload["package_hash"] = ""
        self.assertEqual(expected, object_hash(payload))
        self.assertEqual([], validate_input(self.package))
        self.assertNotIn("planned_actions", self.package["experiment_context"])
        self.assertNotIn("采集脚本", json.dumps(self.package, ensure_ascii=False))
        self.assertEqual(10, len(self.package["l3_context"]["evidence_requirements"]))
        for group in ("control_mainlines", "control_tree_nodes", "evidence_requirements"):
            self.assertTrue(all(row.get("source_ref") or row.get("fingerprint") for row in self.package["l3_context"][group]))

    def test_frozen_output_passes_program_validator_and_follow_up_limit(self):
        self.assertEqual([], validate_output(self.package, self.output))
        self.assertEqual(1, len(self.output["initial_reasoning"]["validation_requests"]))
        self.assertEqual([], self.output["updated_reasoning"]["validation_requests"])
        self.assertEqual("UPDATED_REASONING_COMPLETE_FROZEN", self.output["overall_status"])

    def test_validator_rejects_hallucinated_observation_reference(self):
        changed = copy.deepcopy(self.output)
        changed["updated_reasoning"]["findings"][0]["observation_refs"].append("O-NOT-IN-PACKAGE")
        errors = validate_output(self.package, changed)
        self.assertTrue(any("UNKNOWN_OBSERVATION_REFS:O-NOT-IN-PACKAGE" in error for error in errors))

    def test_validator_rejects_missing_contract_field(self):
        changed = copy.deepcopy(self.output)
        del changed["updated_reasoning"]["findings"][0]["alternative_explanations"]
        errors = validate_output(self.package, changed)
        self.assertTrue(any("REQUIRED_FIELD_MISSING:alternative_explanations" in error for error in errors))

    def test_hidden_comparison_uses_frozen_output_hash(self):
        self.assertEqual(object_hash(self.output), self.comparison["reasoning_output_sha256_at_unlock"])
        self.assertEqual(10, self.comparison["compatible_er_count"])
        self.assertTrue(all(self.comparison["semantic_checks"].values()))

    def test_blinding_limitation_is_explicit(self):
        self.assertFalse(self.output["audit_metadata"]["strict_cognitive_blinding"])
        self.assertIn("prior exposure", self.comparison["blindness_caveat"])


if __name__ == "__main__":
    unittest.main()
