from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]
from evidence_mapping_adapter import map_findings


class EvidenceMappingAdapterTest(unittest.TestCase):
    def test_mapping_never_approves_and_limits_auto_eligibility(self):
        package = {"package_id": "P", "package_hash": "h", "experiment_context": {"experiment_id": "S"}, "observations": [{"observation_id": "O", "raw_refs": []}]}
        output = {"result_id": "R", "findings": [
            {"finding_id": "F1", "proposed_role": "REQUEST", "observation_refs": ["O"], "observation_provenance": [{"observation_ref": "O", "provenance_class": "DIRECT_INTENT_RETRIEVAL"}], "fact_bindings": [{"claim_class": "OBSERVED"}], "signal_validation_needed": True},
            {"finding_id": "F2", "proposed_role": "TECHNICAL_FACT", "observation_refs": ["O"], "fact_bindings": [{"claim_class": "OBSERVED"}], "signal_validation_needed": False},
            {"finding_id": "F3", "proposed_role": "UNRESOLVED", "model_interaction": "NO_SAFE_MAPPING", "observation_refs": [], "fact_bindings": [], "signal_validation_needed": True},
        ]}
        result = map_findings(package, output)
        states = [row["promotion_state"] for row in result["bindings"]]
        self.assertEqual(["HUMAN_REVIEW_REQUIRED", "AUTO_ELIGIBLE_TECHNICAL_FACT", "HOLD_UNRESOLVED"], states)
        self.assertNotIn("APPROVED_EVIDENCE", states)
        self.assertEqual("NOT_APPROVED", result["approval_state"])
        self.assertEqual(
            output["findings"][0]["observation_provenance"],
            result["bindings"][0]["observation_provenance"],
        )


if __name__ == "__main__": unittest.main()
