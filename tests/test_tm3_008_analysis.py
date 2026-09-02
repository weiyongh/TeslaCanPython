import csv
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evidence_plan import read_approved_csv


class Tm3008AnalysisTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output = ROOT / "output/TM3-008"
        cls.machine = cls.output / "machine_evidence"

    def read_csv(self, name):
        with (self.machine / name).open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))

    def test_approved_gate_and_candidate_disposition(self):
        plan = read_approved_csv(self.output / "evidence_plan_approved.csv")
        active = [row for row in plan.signals if row.effective_report_position != "EXCLUDE"]
        excluded = [row.signal_key for row in plan.signals if row.effective_report_position == "EXCLUDE"]
        self.assertEqual(32, len(active))
        self.assertEqual(["VCFRONT_vehicleStatusDBG"], excluded)

    def test_input_identity_and_integrity_are_explicit(self):
        integrity = json.loads((self.machine / "asc_integrity.json").read_text(encoding="utf-8"))
        self.assertEqual("EVIDENCE_ASSESSED", integrity["analysis_status"])
        self.assertEqual([0.0, 660.0], integrity["source_interval_s"])
        self.assertEqual(592949, integrity["interval_parsed_frame_count"])
        self.assertEqual(0, integrity["interval_malformed_frame_count"])
        self.assertEqual(284, integrity["unique_can_id_count"])
        self.assertEqual([0.0, 660.0], integrity["input_file_declared_interval_s"])
        self.assertTrue(integrity["declared_interval_covers_script"])
        self.assertEqual(60.0, integrity["declared_interval_margin_after_script_s"])
        self.assertTrue(any("Derived analysis input: TM3-008" in line
                            for line in integrity["source_file_header"]))
        self.assertTrue(integrity["formal_report_bundle_generated"])

    def test_observed_shutdown_sequence_is_monotonic(self):
        events = {row["event_id"]: float(row["time_s"]) for row in self.read_csv("key_events.csv")}
        ordered = [events[f"E{i:02d}"] for i in range(17)]
        self.assertEqual(ordered, sorted(ordered))
        self.assertAlmostEqual(7.9845, events["E01"], places=4)
        self.assertAlmostEqual(33.3626, events["E03"], places=4)
        self.assertAlmostEqual(295.8383, events["E15"], places=4)
        self.assertAlmostEqual(660.0, events["E16"], places=4)

    def test_signal_validation_boundaries_are_preserved(self):
        rows = {row["signal_key"]: row for row in self.read_csv("signal_validation_assessment.csv")}
        self.assertEqual("INSUFFICIENT_EVIDENCE", rows["UI_lockRequest"]["post_validation_maturity"])
        self.assertEqual("SEMANTIC_VALIDATION_FAILED", rows["BMS_hvState"]["post_validation_maturity"])
        self.assertEqual("SEMANTIC_VALIDATION_FAILED", rows["PCS_dcdcMainState"]["post_validation_maturity"])
        self.assertEqual("SEMANTIC_VALIDATION_FAILED", rows["PCS_dcdcHvBusVolt"]["post_validation_maturity"])
        self.assertEqual("PARTIALLY_VALIDATED", rows["BMS_packVoltage"]["post_validation_maturity"])
        self.assertEqual("STRONGLY_SUPPORTED", rows["HVP_packContPositiveState"]["post_validation_maturity"])
        self.assertEqual("STRONGLY_SUPPORTED", rows["HVP_packContNegativeState"]["post_validation_maturity"])

    def test_evidence_assessment_is_complete_and_er10_remains_gap(self):
        rows = {row["requirement_id"]: row for row in self.read_csv("evidence_assessment.csv")}
        self.assertEqual({f"ER-{number:02d}" for number in range(1, 11)}, set(rows))
        self.assertEqual("SUPPORTED", rows["ER-06"]["status"])
        self.assertEqual("SUPPORTED", rows["ER-08"]["status"])
        self.assertEqual("SUPPORTED", rows["ER-03"]["status"])
        self.assertEqual("NOT_OBSERVED", rows["ER-09"]["status"])
        self.assertEqual("INSUFFICIENT_EVIDENCE", rows["ER-10"]["status"])
        self.assertIn("不得替代", rows["ER-10"]["limitation"])

    def test_formal_report_bundle_was_generated(self):
        from report_renderer import validate_report_bundle
        for name in ("TM3-008_最终报告.md", "采集时间线与关键Signal.md",
                     "DBC关键Signal覆盖与可读性.md", "工程审计.md",
                     "TM3-008_采集时间线与关键Signal.md",
                     "TM3-008_DBC关键Signal覆盖与可读性.md", "TM3-008_工程审计.md"):
            self.assertTrue((self.output / name).exists(), name)
        validate_report_bundle("TM3-008", self.output, "WAKE_HV")


if __name__ == "__main__":
    unittest.main()
