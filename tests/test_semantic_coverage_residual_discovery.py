import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from spikes.semantic_coverage_residual_discovery import parse_asc_line, run_spike


DBC_TEXT = """VERSION ""

NS_ :

BS_:

BU_: ECU

BO_ 256 KnownMessage: 1 ECU
 SG_ known : 0|1@1+ (1,0) [0|1] "" ECU

BO_ 2147483905 ExtendedMessage: 1 ECU
 SG_ extended_known : 0|1@1+ (1,0) [0|1] "" ECU

BO_ 258 ContextMessage: 1 ECU
 SG_ isolationResistance : 0|4@1+ (1,0) [0|15] "kohm" ECU
 SG_ contactorState : 4|1@1+ (1,0) [0|1] "" ECU

BO_ 259 AlertMessage: 1 ECU
 SG_ WatchdogReset : 0|1@1+ (1,0) [0|1] "" ECU
"""


class SemanticCoverageResidualDiscoveryTest(unittest.TestCase):
    def test_parser_preserves_channel_and_extended_identity(self):
        frame = parse_asc_line("0.100000 2 101x Rx d 1 01", 7)
        self.assertIsNotNone(frame)
        self.assertEqual("2", frame.bus_key.channel)
        self.assertEqual("EXTENDED", frame.bus_key.frame_format)
        self.assertEqual(0x101, frame.bus_key.can_id)
        self.assertEqual(7, frame.raw_ref()["line_number"])

    def test_spike_covers_known_partial_unknown_and_static_patterns(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            dbc = folder / "test.dbc"
            asc = folder / "test.asc"
            dbc.write_text(DBC_TEXT, encoding="utf-8")
            rows = []
            for index in range(8):
                value = 0 if index % 2 == 0 else 1
                rows.append(f"{index * 0.5:.6f} 1 100 Rx d 1 {value:02X}")
            rows += [
                "4.000000 2 100 Rx d 1 00",
                "4.500000 2 100 Rx d 1 03",
                "5.000000 1 200 Rx d 1 00",
                "5.500000 1 200 Rx d 1 01",
                "6.000000 2 101x Rx d 1 00",
                "6.500000 2 101x Rx d 1 01",
            ]
            for index in range(12):
                rows.append(f"{7 + index * 0.5:.6f} 1 102 Rx d 1 10")
                rows.append(f"{7 + index * 0.5:.6f} 1 103 Rx d 1 {index % 2:02X}")
            asc.write_text("\n".join(rows) + "\n", encoding="utf-8")
            result = run_spike(
                asc, [dbc], domain="test", conditions=["static"], windows=[]
            )

        self.assertEqual(len(rows), result["asc_integrity"]["parsed_frame_count"])
        by_key = {(row["bus_key"], row["observed_dlc"]): row for row in result["dbc_coverage"]}
        self.assertEqual("MATCHED", by_key[("ch1:0x100", 1)]["coverage_class"])
        self.assertEqual("PARTIAL", by_key[("ch2:0x100", 1)]["coverage_class"])
        self.assertEqual([1], by_key[("ch2:0x100", 1)]["residual_changing_bits"])
        self.assertEqual("UNMATCHED", by_key[("ch1:0x200", 1)]["coverage_class"])
        self.assertEqual("MATCHED", by_key[("ch2:0x101x", 1)]["coverage_class"])
        types = {row["candidate_type"] for row in result["candidates"]}
        self.assertIn("PERIODIC_LOW_CARDINALITY", types)
        self.assertIn("RESIDUAL_BIT_ACTIVITY", types)
        self.assertIn("UNKNOWN_LOW_CARDINALITY_PAYLOAD", types)
        self.assertIn("FIXED_PHYSICAL_BOUNDARY_CONTEXT", types)
        self.assertIn("PERIODIC_ALERT_LIKE", types)
        llm_types = {row["candidate_type"] for row in result["llm_package"]["candidates"]}
        self.assertIn("FIXED_PHYSICAL_BOUNDARY_CONTEXT", llm_types)
        self.assertIn("PERIODIC_ALERT_LIKE", llm_types)
        self.assertTrue(all(row["event_ref"] is None for row in result["candidates"]))
        self.assertTrue(all(row["raw_refs"] for row in result["candidates"]))
        self.assertEqual([], result["llm_package"]["event_anchors"])
        known = next(row for row in result["signal_summaries"] if row["signal_name"] == "known")
        self.assertEqual("1", known["current_value"])
        json.dumps(result, allow_nan=False)


if __name__ == "__main__":
    unittest.main()
