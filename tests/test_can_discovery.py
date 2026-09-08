import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from can_discovery import discover


DBC_A = '''VERSION ""
NS_ :
BS_:
BU_: ECU
BO_ 256 Standard: 2 ECU
 SG_ value : 0|8@1+ (1,0) [0|255] "" ECU
BO_ 257 Partial: 2 ECU
 SG_ low : 0|1@1+ (1,0) [0|1] "" ECU
 SG_ high : 8|8@1+ (1,0) [0|255] "" ECU
'''

DBC_B = '''VERSION ""
NS_ :
BS_:
BU_: ECU
BO_ 256 Conflicting: 2 ECU
 SG_ value : 0|8@1+ (2,0) [0|510] "" ECU
'''


class FormalCanDiscoveryTest(unittest.TestCase):
    def test_identity_dlc_unmatched_partial_conflict_and_malformed_disposition(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            asc = folder / "input.asc"
            dbc_a = folder / "a.dbc"
            dbc_b = folder / "b.dbc"
            dbc_a.write_text(DBC_A, encoding="utf-8")
            dbc_b.write_text(DBC_B, encoding="utf-8")
            asc.write_text(
                "0.000000 1 100 Rx d 1 00\n"
                "0.100000 1 100 Rx d 2 01 00\n"
                "0.200000 2 100 Rx d 1 02\n"
                "0.300000 1 100x Rx d 1 03\n"
                "0.400000 1 101 Rx d 1 00\n"
                "0.500000 1 101 Rx d 1 02\n"
                "0.600000 1 200 Rx d 1 00\n"
                "0.700000 1 200 Rx d 1 01\n"
                "9.000000 broken\n",
                encoding="utf-8",
            )
            result = discover(
                asc, [dbc_a, dbc_b], experiment_id="SYNTHETIC",
                purpose="contract", known_signal_hints=("does_not_exist",),
            )

        keys = {row["bus_key"] for row in result["observations"]}
        self.assertIn("ch1:0x100", keys)
        self.assertIn("ch2:0x100", keys)
        self.assertIn("ch1:0x100x", keys)
        self.assertIn("ch1:0x200", keys)
        dlcs = {row["dlc"] for row in result["observations"] if row["bus_key"] == "ch1:0x100"}
        self.assertEqual({1, 2}, dlcs)
        coverage = {(row["bus_key"], row["observed_dlc"]): row for row in result["coverage"]}
        self.assertEqual("CONFLICTED", coverage[("ch1:0x100", 2)]["coverage_class"])
        self.assertEqual(2, len(coverage[("ch1:0x100", 2)]["definition_sources"]))
        self.assertEqual("PARTIAL", coverage[("ch1:0x101", 1)]["coverage_class"])
        self.assertEqual("UNMATCHED", coverage[("ch1:0x200", 1)]["coverage_class"])
        self.assertEqual("UNMATCHED", coverage[("ch1:0x100x", 1)]["coverage_class"])
        self.assertTrue(result["closure"]["closed"])
        self.assertEqual(1, result["asc_integrity"]["abnormal_line_count"])
        self.assertTrue(any(row.get("reason") == "MALFORMED_OR_UNSUPPORTED_RECORD" for row in result["dispositions"]))
        self.assertTrue(any(row.get("disposition_kind") == "SIGNAL_DECODE" for row in result["dispositions"]))
        self.assertEqual(["does_not_exist"], result["known_signal_hints_recorded_not_applied_as_filter"])
        self.assertTrue(result["raw_reference_manifest"])

    def test_candidate_cap_does_not_remove_unhinted_observations(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            asc = folder / "input.asc"
            dbc = folder / "empty.dbc"
            dbc.write_text('VERSION ""\nNS_ :\nBS_:\nBU_: ECU\n', encoding="utf-8")
            rows = []
            for can_id in range(0x300, 0x310):
                rows.append(f"0.000000 1 {can_id:X} Rx d 1 00")
                rows.append(f"0.100000 1 {can_id:X} Rx d 1 01")
            asc.write_text("\n".join(rows) + "\n", encoding="utf-8")
            with mock.patch("spikes.semantic_coverage_residual_discovery.MAX_CANDIDATES_PER_TYPE", 1), \
                 mock.patch("spikes.semantic_coverage_residual_discovery.MAX_CANDIDATES_TOTAL", 1):
                result = discover(
                    asc, [dbc], experiment_id="SYNTHETIC",
                    purpose="contract", known_signal_hints=("hint_only",),
                )

        self.assertEqual(16, len(result["observations"]))
        self.assertEqual(1, len(result["candidates"]))
        self.assertGreater(result["candidate_compression"]["discarded_total"], 0)
        self.assertEqual(16, result["candidate_compression"]["observation_count_after_compression"])
        self.assertIn("ch1:0x30F", {row["bus_key"] for row in result["observations"]})


if __name__ == "__main__":
    unittest.main()
