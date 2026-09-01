import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evidence_plan import DraftSignalEvidence, ReviewOverride, approve_plan


def row(flags="", required="NO"):
    return DraftSignalEvidence("T", "speed", "speed", "msg", "0x1", "km/h", "motion",
        "物理结果", "P0", "CORE_TIMELINE+CORE_SIGNAL_TABLE", 1, "direct", "已确认", "HIGH", flags, required)


class EvidencePlanTest(unittest.TestCase):
    def test_unreviewed_uncertainty_blocks_approval(self):
        with self.assertRaisesRegex(ValueError, "unreviewed uncertain"):
            approve_plan([row("PROXY_OBSERVATION", "YES")], [])

    def test_override_preserves_suggestion_and_changes_effective(self):
        review = ReviewOverride("T", "speed", "OVERRIDE", override_priority="P1",
            override_report_position="ANALYSIS_WINDOW+CORE_SIGNAL_TABLE", human_reason="reviewed",
            reviewer="human", reviewed_at="2026-09-01")
        approved = approve_plan([row("REPORT_POSITION_AMBIGUOUS", "YES")], [review]).signals[0]
        self.assertEqual("P0", approved.suggested_priority)
        self.assertEqual("P1", approved.effective_priority)
        self.assertEqual("THIS_EXPERIMENT_ONLY", approved.scope)
        self.assertEqual("HUMAN", approved.decision_source)

    def test_uncertainty_requires_review_flag(self):
        with self.assertRaisesRegex(ValueError, "must require review"):
            row("PROXY_OBSERVATION", "NO").validate()


if __name__ == "__main__":
    unittest.main()
