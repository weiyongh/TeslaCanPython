import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from can_evidence_utils import *


class CanEvidenceUtilsTest(unittest.TestCase):
    def test_latest_past_and_age_never_look_forward(self):
        samples = [TimedValue(1.0, 10), TimedValue(2.0, 20)]
        selected = latest_past_sample(samples, 1.5)
        self.assertEqual(10, selected.value)
        self.assertAlmostEqual(0.5, signal_age_s(1.5, selected))

    def test_same_frame_calculations(self):
        self.assertEqual((10.0, 12.0, 2.0), same_frame_pair({"r": 10, "a": 12}, "r", "a"))
        self.assertAlmostEqual(3.6, pack_power_kw_same_frame({"v": 360, "i": 10}, "v", "i"))

    def test_continuous_windows(self):
        self.assertEqual([(0.0, 0.2, 3), (1.0, 1.1, 2)], continuous_windows([0, .1, .2, 1, 1.1], .2))

    def test_readability_and_hash(self):
        self.assertEqual("NO_FRAME", dbc_field_readability(frame_count=0, decoded_count=0))
        self.assertEqual("DLC_MISMATCH", dbc_field_readability(frame_count=1, decoded_count=0, dbc_dlc=8, asc_dlc=5))
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "a.asc"
            path.write_bytes(b"a\nb\n")
            result = asc_integrity(path)
            self.assertEqual(2, result["line_count"])
            self.assertEqual(4, result["size_bytes"])


if __name__ == "__main__":
    unittest.main()
