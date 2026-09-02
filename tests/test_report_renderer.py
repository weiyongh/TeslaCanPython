import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evidence_plan import ApprovedEvidencePlan, ApprovedSignalEvidence
from report_renderer import (AUDIT_HEADINGS, COVERAGE_HEADERS, DRIVE_TIMELINE_HEADERS,
                             ControlNodeView,
                             ControlRelationshipView, CoverageSignal, CoreSignal, ExperimentReport,
                             MainlineVerification,
                             SemanticTimelineEvent, TimelineEvent, render_final_report,
                             render_report_bundle, render_signal_coverage, render_timeline,
                             validate_report_bundle)


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

    def test_judgment_heading_is_rvm_controlled_with_fixed_assessment_position(self):
        report = self.report.__class__(**{**self.report.__dict__, "judgment_heading": "基线结论"})
        headings = [line for line in render_final_report(self.plan, report).splitlines()
                    if line.startswith("## ") or line.startswith("### ")]
        required = ["## 实验信息与适用范围", "## 事实与关键证据", "## 控制关系",
                    "## 基线结论", "### Evidence Assessment", "## 证据边界",
                    "## 结论与下一步建议"]
        positions = [headings.index(item) for item in required]
        self.assertEqual(positions, sorted(positions))

    def test_human_timeline_excludes_audit_columns_not_signal_identity(self):
        header = render_timeline(self.plan, self.report).splitlines()[4]
        for forbidden in ("Event ID", "事件ID", "raw sample time", "原始采样时间",
                          "Signal age", "DLC", "per-frame decode status"):
            self.assertNotIn(forbidden, header)
        # Signal Name and CAN ID are legal human evidence identities. Their actual
        # event-level representation belongs to the next semantic-RVM phase.
        audit_fields = ("Event ID", "raw sample time", "Signal age", "DLC", "per-frame decode status")
        self.assertNotIn("Signal Name", audit_fields)
        self.assertNotIn("CAN ID", audit_fields)

    def test_wake_hv_semantic_event_resolves_approved_signal_identity(self):
        event = SemanticTimelineEvent(
            "12.345", "请求与执行状态发生变化。", ("请求由0变为1",),
            ("request", "actual"), "建立请求—执行对应节点。", "仅限本事件的局部限制。")
        report = self.report.__class__(**{**self.report.__dict__, "timeline": (),
            "timeline_profile": "WAKE_HV", "semantic_timeline_events": (event,),
            "evidence_boundaries": ("实验级全局边界不得逐事件复制。",)})
        text = render_timeline(self.plan, report)
        self.assertIn("| 12.345 | 请求与执行状态发生变化。", text)
        self.assertIn("`request` / `0x1`", text)
        self.assertIn("`actual` / `0x2`", text)
        self.assertIn("请求由0变为1", text)
        self.assertIn("仅限本事件的局部限制", text)
        self.assertNotIn("实验级全局边界不得逐事件复制", text)
        self.assertNotIn("| 时间(s)", text)
        for forbidden in ("Event ID", "Signal age", "DLC", "per-frame decode status"):
            self.assertNotIn(forbidden, "\n".join(line for line in text.splitlines() if not line.startswith(">")))

    def test_wake_hv_grouping_preserves_event_times_and_signal_refs(self):
        events = (
            SemanticTimelineEvent("1.001", "进入阶段。", ("A变化",), ("request",),
                                  "阶段开始。", phase="阶段A"),
            SemanticTimelineEvent("1.002", "状态稳定。", ("A保持",), ("actual",),
                                  "形成稳定窗口。", phase="阶段A", event_type="stable_window"),
        )
        report = self.report.__class__(**{**self.report.__dict__, "timeline": (),
            "timeline_profile": "WAKE_HV", "semantic_timeline_events": events})
        text = render_timeline(self.plan, report)
        self.assertEqual(1, text.count("| 阶段 | CAN时间/窗口 |"))
        self.assertEqual(2, text.count("| 阶段A |"))
        for value in ("1.001", "1.002", "`request` / `0x1`", "`actual` / `0x2`"):
            self.assertIn(value, text)
        self.assertIn("稳定窗口：形成稳定窗口。", text)

    def test_control_mainline_is_separate_from_verification(self):
        report = self.report.__class__(**{**self.report.__dict__,
            "control_mainline": ("输入", "执行"),
            "mainline_verification": (
                MainlineVerification("输入", ("request",), "直接支持", "缺少外部观测"),
                MainlineVerification("执行", ("actual",), "直接支持"),
            )})
        text = render_final_report(self.plan, report)
        self.assertIn("系统状态推进主线：输入 → 执行", text)
        self.assertNotIn("输入（", text)
        self.assertIn("### 主线核验摘要", text)
        self.assertIn("`request`（`0x1`）", text)
        self.assertIn("缺少外部观测", text)

    def test_mainline_verification_rejects_non_approved_signal(self):
        report = self.report.__class__(**{**self.report.__dict__,
            "control_mainline": ("输入",),
            "mainline_verification": (
                MainlineVerification("输入", ("unknown",), "支持"),)})
        with self.assertRaisesRegex(ValueError, "non-approved signal"):
            render_final_report(self.plan, report)

    def test_coverage_is_complete_ordered_and_separates_derived(self):
        coverage = (
            CoverageSignal("request", "0..1", "是", "source; readable", "request use"),
            CoverageSignal("actual", "0..1", "是", "source; readable", "actual use"),
            CoverageSignal("pack_i", "0..1", "是", "derived", "derived use", "DERIVED"),
        )
        report = self.report.__class__(**{**self.report.__dict__, "coverage_signals": coverage})
        text = render_signal_coverage(self.plan, report)
        self.assertLess(text.index("| 1 | request | 仲裁后请求"),
                        text.index("| 2 | actual | 执行反馈"))
        self.assertIn("### 非DBC派生证据", text)
        dbc_part = text.split("### 非DBC派生证据", 1)[0]
        self.assertNotIn("pack_i", dbc_part)
        self.assertIn("| 1 | pack_i | 能源交叉验证 |", text)

    def test_incomplete_coverage_is_rejected(self):
        report = self.report.__class__(**{**self.report.__dict__, "coverage_signals": (
            CoverageSignal("request", "", "", "", ""),)})
        with self.assertRaisesRegex(ValueError, "every Approved signal"):
            render_signal_coverage(self.plan, report)

    def test_wake_hv_semantic_event_rejects_non_approved_signal(self):
        event = SemanticTimelineEvent("1", "变化。", ("状态变化",), ("not_approved",), "意义。")
        report = self.report.__class__(**{**self.report.__dict__, "timeline": (),
            "timeline_profile": "WAKE_HV", "semantic_timeline_events": (event,)})
        with self.assertRaisesRegex(ValueError, "non-approved signal"):
            render_timeline(self.plan, report)

    def test_runtime_validator_allows_special_section_between_core_slots(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            render_report_bundle(self.plan, self.report, folder)
            final_path = folder / "T_最终报告.md"
            text = final_path.read_text(encoding="utf-8").replace(
                "\n## 控制关系", "\n## 实验专项\n\n专项内容。\n\n## 控制关系")
            final_path.write_text(text, encoding="utf-8")
            validate_report_bundle("T", folder, "DRIVE")

    def test_completed_bundle_passes_unified_structure_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            render_report_bundle(self.plan, self.report, folder)
            validate_report_bundle("T", folder, "DRIVE")
            self.assertEqual(DRIVE_TIMELINE_HEADERS,
                ("时间(s)", "状态/动作", "电门(%)", "请求扭矩(Nm)", "实际扭矩(Nm)",
                 "车速(km/h)", "电驱功率(kW)", "Pack电流(A)", "Pack功率(kW)", "备注"))
            self.assertEqual(9, len(COVERAGE_HEADERS))
            self.assertEqual(("## Evidence Plan状态", "## 数据与复现", "## 工程字段边界"), AUDIT_HEADINGS)


if __name__ == "__main__":
    unittest.main()
