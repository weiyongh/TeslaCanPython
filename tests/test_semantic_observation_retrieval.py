import copy
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]
from semantic_observation_retrieval import build_search_intents, retrieve


def package():
    base_raw = {"channel": "1", "frame_format": "STANDARD", "can_id": "0x200", "dlc": 1, "frame_count": 4, "first_time_s": 0, "last_time_s": 3, "directions": {"RX": 4}, "payload_cardinality": 2, "byte_cardinality": [2], "changing_bits": [0], "bit_ones": [2]*8, "bit_transitions": [3]+[0]*7, "raw_refs": [{"line_number": 1}], "coverage_state": "UNMATCHED", "coverage_reasons": [], "definition_sources": [], "residual_changing_bits": []}
    unknown = {"observation_id": "OBS-U", "observation_kind": "BUS_VARIANT", "bus_key": "ch1:0x200", **base_raw}
    residual = {"observation_id": "OBS-R", "observation_kind": "BUS_VARIANT", "bus_key": "ch1:0x201", **{**base_raw, "can_id": "0x201", "coverage_state": "PARTIAL", "residual_changing_bits": [0]}}
    known = {"signal_key": "k", "signal_name": "meaningless_alpha", "message_name": "m", "unit": "", "enum_definition": {}, "dbc_source": "d", "bus_key": "ch1:0x100", "change_count": 9, "cardinality": 2, "raw_refs": []}
    misleading = {"signal_key": "r", "signal_name": "perfectRequestName", "message_name": "m", "unit": "", "enum_definition": {}, "dbc_source": "d", "bus_key": "ch1:0x101", "change_count": 1, "cardinality": 1, "raw_refs": []}
    return {"package_hash": "h", "signal_summaries": [known, misleading], "observations": [unknown, residual], "residual_summaries": [residual], "unknown_summaries": [unknown], "candidates": []}


L3 = {"control_tree_nodes": [{"node_id": "CT", "definition": "vehicle request and state"}], "evidence_requirements": [{"evidence_requirement_id": "ER-1", "statement": "Observe vehicle Request and state during establishment"}]}


class SemanticObservationRetrievalTest(unittest.TestCase):
    def test_intents_are_l3_er_driven_and_have_no_expected_answer(self):
        intents = build_search_intents(L3, {"experiment_id": "S"})
        self.assertTrue(all(row["evidence_requirement_refs"] == ["ER-1"] for row in intents))
        self.assertNotIn("expected_signal_role", str(intents))

    def test_behavior_only_known_residual_unknown_compete_above_threshold(self):
        result = retrieve(package(), L3, {"experiment_id": "S"})
        request_result = result["results"][0]
        spaces = {row["source_space"] for row in request_result["retrieved"]}
        self.assertEqual({"KNOWN", "RESIDUAL", "UNKNOWN"}, spaces)
        refs = {row["observation_ref"] for row in request_result["retrieved"]}
        self.assertIn("OBS-U", refs)
        unnamed = next(row for row in request_result["retrieved"] if row["observation_ref"] == "OBS-U")
        self.assertIn("OBSERVED_EVENT_PHASE_UNAVAILABLE", unnamed["unavailable_features"])
        self.assertIn("CAN_REGION_DETAIL_UNAVAILABLE", unnamed["unavailable_features"])
        self.assertIn("RELATIONSHIP_FEATURE_UNAVAILABLE", unnamed["unavailable_features"])

    def test_quota_does_not_force_below_threshold_and_hash_is_deterministic(self):
        value = package(); value["observations"] = []; value["unknown_summaries"] = []; value["residual_summaries"] = []
        first = retrieve(value, L3, {"experiment_id": "S"}); second = retrieve(value, L3, {"experiment_id": "S"})
        self.assertEqual(first["retrieval_output_hash"], second["retrieval_output_hash"])
        self.assertTrue(all("UNKNOWN" not in row["source_space_counts"] for row in first["results"]))

    def test_misleading_name_is_retrieval_feature_not_confirmation(self):
        result = retrieve(package(), L3, {"experiment_id": "S"})
        selected = result["results"][0]["retrieved"]
        request = next(row for row in selected if row["source_space"] == "KNOWN" and row["eligibility_path"] == "BEHAVIOR_EXPLORATORY")
        self.assertEqual("UNCONFIRMED", request["semantic_role_status"])

    def test_no_evidence_is_explicit(self):
        value = package(); value["signal_summaries"] = []; value["observations"] = []; value["residual_summaries"] = []; value["unknown_summaries"] = []
        result = retrieve(value, L3, {"experiment_id": "S"})
        self.assertTrue(all(row["no_suitable_observation"] for row in result["results"]))


if __name__ == "__main__": unittest.main()
