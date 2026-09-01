import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evidence_plan import ApprovedEvidencePlan, ApprovedSignalEvidence
from report_renderer import (ControlNodeView, ControlRelationshipView, CoreSignal,
                             ExperimentReport, TimelineEvent, render_final_report,
                             render_signal_coverage, render_timeline)


def approved(key, signal, role, priority, position, order, can_id):
    return ApprovedSignalEvidence("T", "APPROVED", "THIS_EXPERIMENT_ONLY", key, signal, "msg", can_id, "u", "req",
        role, priority, position, order, "why", "confirmed", "HIGH", "", "NO", "AUTO_ACCEPT",
        role, priority, position, order, "CODEX", "", "", "")


class RendererTest(unittest.TestCase):
    def setUp(self):
        rows = (
            approved("actual", "actual", "执行反馈", "P0", "CORE_TIMELINE+CORE_SIGNAL_TABLE", 20, "0x2"),
            approved("request", "request", "仲裁后请求", "P1", "CORE_TIMELINE+CORE_SIGNAL_TABLE", 10, "0x1"),
            approved("pack_i", "pack_i", "能源交叉验证", "P2", "CORE_TIMELINE+CORE_SIGNAL_TABLE", 30, "0x3"),
        )
        self.plan = ApprovedEvidencePlan("T", "APPROVED", "THIS_EXPERIMENT_ONLY", rows)
        relationship = ControlRelationshipView((
            ControlNodeView("输入", "直接观测"),
            ControlNodeView("条件/能力", "本次无直接观测"),
            ControlNodeView("决策", "由上下游证据间接支持"),
            ControlNodeView("执行", "直接观测"),
        ), "执行→物理结果", "能源A↔能源B")
        self.report = ExperimentReport("T", "title", (), (), relationship, (), (), (),
            ("request", "actual", "pack_i"),
            (TimelineEvent(1, "act", "1", "2", "3", "4", "5", "6", "7", "note"),), (),
            (CoreSignal("actual", "1", "是", "可读", "x"), CoreSignal("request", "1", "是", "可读", "x"), CoreSignal("pack_i", "1", "是", "可读", "x")), (), ())

    def test_timeline_fixed_order_and_no_engineering_fields(self):
        text = render_timeline(self.plan, self.report)
        header = text.splitlines()[4]
        self.assertEqual("| 时间(s) | 状态/动作 | 电门(%) | 请求扭矩(Nm) | 实际扭矩(Nm) | 车速(km/h) | 电驱功率(kW) | Pack电流(A) | Pack功率(kW) | 备注 |", header)
        self.assertNotIn("事件ID", header)
        self.assertNotIn("Signal age", header)
        self.assertNotIn("DLC", header)

    def test_signal_order_comes_only_from_approved_plan(self):
        text = render_signal_coverage(self.plan, self.report)
        self.assertLess(text.index("| 仲裁后请求 | request"), text.index("| 执行反馈 | actual"))
        self.assertLess(text.index("| 执行反馈 | actual"), text.index("| 能源交叉验证 | pack_i"))

    def test_unapproved_core_signal_is_rejected(self):
        bad = self.report.__class__(**{**self.report.__dict__, "core_signals": self.report.core_signals + (CoreSignal("new", "", "", "", ""),)})
        with self.assertRaisesRegex(ValueError, "not approved"):
            render_signal_coverage(self.plan, bad)

    def test_control_relationship_is_upstream_view_not_signal_list(self):
        text = render_final_report(self.plan, self.report)
        self.assertIn("条件/能力（本次无直接观测）", text)
        self.assertIn("决策（由上下游证据间接支持）", text)
        self.assertIn("动力/物理响应：执行→物理结果", text)
        self.assertIn("能源交叉验证：能源A↔能源B", text)
        self.assertNotIn("request → actual → pack_i", text)

    def test_assessment_punctuation_is_normalized(self):
        from evidence_plan import EvidenceAssessment
        report = self.report.__class__(**{**self.report.__dict__, "assessments": (
            EvidenceAssessment("R", "INSUFFICIENT_EVIDENCE", "仅3.32 s。", "需要补采。"),)})
        text = render_final_report(self.plan, report)
        self.assertNotIn("。；", text)
        self.assertIn("仅3.32 s；边界：需要补采。", text)

    def test_float_tail_is_removed_from_human_markdown(self):
        report = self.report.__class__(**{**self.report.__dict__, "timeline": (
            TimelineEvent(1, "act", motion="-0.1599999999999966", pack_current="-38.300000000000004"),)})
        text = render_timeline(self.plan, report)
        self.assertIn("-0.16", text)
        self.assertIn("-38.3", text)
        self.assertNotIn("999999999", text)


if __name__ == "__main__":
    unittest.main()
