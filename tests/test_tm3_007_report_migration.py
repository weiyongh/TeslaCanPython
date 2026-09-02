import csv
import hashlib
import inspect
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from render_tm3_007 import build_report
import report_renderer
from report_renderer import render_report_bundle, validate_report_bundle


MACHINE_HASHES = {
    "asc_integrity.json": "238b3d3894cd50ad8504908f07026792283fbc49b5fe7f0d31396084b0d13e3f",
    "dbc_definition_comparison.csv": "bf2af516fd7b748b29fd24a27ee09ff4a8bb77b4f88b1b4ba25a3b7ed24a823c",
    "decoded_native_samples.csv": "7545947976181d106ccb13143a73b8592e643cc08ee2b881bd4f9780702f887c",
    "event_signal_samples.csv": "d51460828b1ed66307ffb7a34ec5414b0306c94204cc76db7d287f66d761fcf7",
    "events.csv": "30c1a232e0e1d348114b1b2c4ff7507e2f01894db9223b7097688c87005c762c",
    "evidence_assessment.csv": "02a1f6375fcd21ae20c3e7c255f1652e3a1aacfdd4a58c60190986ffe379b0de",
    "experiment_metadata.json": "4996f745d69dba4dd7f79dbbf1846cb4fd83245f2bdbf80c9aa274a4cc348344",
    "network_activity_1s.csv": "d7fa3231495a6c603d6cb5e6a0848e145c16974aba7cbd35be48db4de4912e97",
    "report_view_model.json": "df6abd8eeb2879bc30dc40d081ec4a0be5ad5deac237717d5fe1d66ed984518d",
    "signal_coverage.csv": "9f5a24b749d6944a9511e8925484d3066a48db51b1c48104c4fda1487be58fb9",
    "signal_validation_0x20A_raw.csv": "facc5411bcba8231ea97752c3ed93ab5c09548d8acccdeef8c8350a6d8b3ad49",
    "signal_validation_assessment.csv": "490bf4ca0516cea70d477a33061485bb16f0e8443ccf7c261547b82677bdbb4f",
    "verification.json": "2c3b6d0e74dd43becf549e700f8f1e0b259baa46d51d15b9c42233ee274afe63",
}
LIFECYCLE_HASHES = {
    "evidence_plan_approved.csv": "96fd4e9cc4becbb8f334ccc02c902f9389fa035d0d786db21005d0728f50201f",
    "evidence_plan_context.md": "4bab948987bac2f3ed714b6467d213811aed2fe4b57cd4e02daca04b63b59276",
    "evidence_plan_draft.csv": "0e351ed161a4299d23cdceaa32813f5f26ae785cf5263c3fe45f3140626457eb",
    "evidence_plan_review_overrides.csv": "6f27560267956305295af35c0bc7a615854f3fdb606ba20345adcd44fb0d39b8",
    "待审Signal证据表.md": "b42be6600383f182289175cceb3a88f01409655c748ac2535caba90b5ab434e0",
}
FORMAL_REPORT_HASHES = {
    "TM3-007_最终报告.md": "f9d7b041e96c10b58c614cbb7b02e4c180b4658436aeec67275aa4c8a6b08f53",
    "采集时间线与关键Signal.md": "07a8220aa17157028cc2c2eb49fe4877d63a33c55c8290977e9cb661a1dc4145",
    "DBC关键Signal覆盖与可读性.md": "19724017e1dfaf1f50156ff8da285edbf93ab1e9b88365727ba556833d437569",
    "工程审计.md": "54506040e4c1d81723d47a7435620e9871c91d5dd7e8dbb0c4c586545bd64d98",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class Tm3007ReportMigrationTest(unittest.TestCase):
    def test_source_machine_evidence_and_lifecycle_files_are_frozen(self):
        machine = ROOT / "output/TM3-007/machine_evidence"
        self.assertEqual(set(MACHINE_HASHES), {path.name for path in machine.iterdir() if path.is_file()})
        for name, expected in MACHINE_HASHES.items():
            self.assertEqual(expected, sha256(machine / name), name)
        folder = ROOT / "output/TM3-007"
        for name, expected in LIFECYCLE_HASHES.items():
            self.assertEqual(expected, sha256(folder / name), name)

    def test_formal_v3_bundle_is_frozen(self):
        folder = ROOT / "output/TM3-007"
        for name, expected in FORMAL_REPORT_HASHES.items():
            self.assertEqual(expected, sha256(folder / name), name)

    def test_formal_v3_bundle_is_reproducible_through_shared_renderer(self):
        plan, report = build_report()
        with tempfile.TemporaryDirectory() as temp:
            rendered = Path(temp)
            render_report_bundle(plan, report, rendered)
            formal = ROOT / "output/TM3-007"
            for name in FORMAL_REPORT_HASHES:
                self.assertEqual((formal / name).read_bytes(), (rendered / name).read_bytes(), name)

    def test_formal_and_historical_preview_status_is_unambiguous(self):
        formal = (ROOT / "output/TM3-007/README.md").read_text(encoding="utf-8")
        self.assertIn("FROZEN / COMPLETE_WITH_GAPS", formal)
        self.assertIn("当前正式四件套", formal)
        for folder in ("TM3-007_preview", "TM3-007_preview_v2"):
            text = (ROOT / "output" / folder / "README.md").read_text(encoding="utf-8")
            self.assertIn("HISTORICAL_PREVIEW / NOT_CURRENT", text)
            self.assertIn("output/TM3-007/", text)

    def test_adapter_preserves_assessment_rows_exactly(self):
        _plan, report = build_report()
        path = ROOT / "output/TM3-007/machine_evidence/evidence_assessment.csv"
        with path.open(encoding="utf-8-sig", newline="") as stream:
            expected = [(row["requirement_id"], row["assessment"], row["evidence"], row["reason"])
                        for row in csv.DictReader(stream)]
        actual = [(row.requirement_id, row.status, row.evidence_summary, row.limitation)
                  for row in report.assessments]
        self.assertEqual(expected, actual)
        self.assertEqual(9, len(actual))

    def test_adapter_uses_wake_hv_and_approved_core_order(self):
        plan, report = build_report()
        self.assertEqual("WAKE_HV", report.timeline_profile)
        self.assertEqual("基线结论", report.judgment_heading)
        self.assertFalse(report.profile_timeline_rows)
        self.assertEqual(13, len(report.semantic_timeline_events))
        approved = [row.signal_key for row in sorted(plan.signals, key=lambda row: row.effective_order)
                    if row.has_position("CORE_SIGNAL_TABLE")]
        self.assertEqual(approved, [row.signal_key for row in report.core_signals])
        self.assertEqual(
            [row.signal_key for row in sorted(plan.signals, key=lambda row: row.effective_order)],
            [row.signal_key for row in report.coverage_signals],
        )
        self.assertEqual(23, len(report.coverage_signals))
        self.assertEqual(2, sum(row.evidence_kind == "DERIVED" for row in report.coverage_signals))

    def test_adapter_separates_mainline_verification_and_global_boundaries(self):
        plan, report = build_report()
        self.assertEqual(7, len(report.control_mainline))
        self.assertEqual(report.control_mainline,
                         tuple(row.node for row in report.mainline_verification))
        approved = plan.by_key()
        for item in report.mainline_verification:
            self.assertTrue(item.signal_refs)
            self.assertTrue(all(key in approved for key in item.signal_refs))
        self.assertNotIn("UI_readyForDrive", report.control_mainline)
        self.assertNotIn("门闩", " → ".join(report.control_mainline))
        self.assertNotIn("占座", " → ".join(report.control_mainline))
        self.assertNotIn("制动", " → ".join(report.control_mainline))
        self.assertEqual(report.evidence_boundaries, report.global_evidence_boundaries)

    def test_adapter_preserves_all_13_event_times_refs_and_groups_hv_sequence(self):
        _plan, report = build_report()
        path = ROOT / "output/TM3-007/machine_evidence/events.csv"
        with path.open(encoding="utf-8-sig", newline="") as stream:
            expected_times = [row["can_time_s"].rstrip("0").rstrip(".") for row in csv.DictReader(stream)]
        self.assertEqual(expected_times, [row.time for row in report.semantic_timeline_events])
        hv = [row for row in report.semantic_timeline_events if row.phase == "高压建立序列"]
        self.assertEqual(["472.6697", "473.3233", "474.2713", "474.3233"],
                         [row.time for row in hv])
        self.assertEqual("stable_window", report.semantic_timeline_events[-1].event_type)

    def test_v3_control_relationship_is_layered_without_new_dc_link_evidence(self):
        plan, report = build_report()
        labels = [row.label for row in report.control_relationship_lines]
        self.assertEqual([
            "系统进入/状态推进主线", "高压控制链", "高压物理响应",
            "低压能源响应/交叉验证", "可驱动状态及结果反馈",
        ], labels)
        physical = next(row for row in report.control_relationship_lines
                        if row.label == "高压物理响应")
        self.assertEqual(("BMS_packVoltage",), physical.signal_refs)
        self.assertIn("不是接触器下游DC Link电压", physical.note)
        self.assertNotIn("HVP_dcLinkVoltageFiltered", plan.by_key())
        ready = next(row for row in report.control_relationship_lines
                     if row.label == "可驱动状态及结果反馈")
        self.assertIn("不解释为驱动许可源头", ready.note)

    def test_v3_renderer_is_generic_not_tm3_007_hardcoded(self):
        self.assertNotIn("TM3-007", inspect.getsource(report_renderer))

    def test_adapter_bundle_passes_golden_contract(self):
        plan, report = build_report()
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            render_report_bundle(plan, report, folder)
            validate_report_bundle("TM3-007", folder, "WAKE_HV")
            timeline = (folder / "采集时间线与关键Signal.md").read_text(encoding="utf-8")
            self.assertIn("## 实际时间线", timeline)
            self.assertNotIn("## 人读主时间线", timeline)
            self.assertEqual(1, timeline.count("| 阶段 | CAN时间/窗口 | 实际变化 | Signal / CAN ID |"))
            self.assertNotIn("### 高压建立序列", timeline)
            self.assertNotIn("| 时间(s)", timeline)
            self.assertIn("高压互锁候选转为正常，正接触器进入预充", timeline)
            self.assertIn("`HVP_hvilStatus` / `0x20A`", timeline)
            self.assertIn("`BMS_packVoltage` / `0x132`", timeline)
            main = timeline.split("## 0x20A既有Signal Validation迁移", 1)[0]
            for forbidden in ("Event ID", "事件ID", "raw sample time", "原始采样时间",
                              "Signal age", "DLC", "per-frame decode status"):
                self.assertNotIn(forbidden, main)
            self.assertIn("0x20A既有Signal Validation迁移", timeline)
            coverage = (folder / "DBC关键Signal覆盖与可读性.md").read_text(encoding="utf-8")
            self.assertIn("| 序号 | Signal | 控制含义 | Message | CAN ID | 单位 |", coverage)
            self.assertIn("### 非DBC派生证据", coverage)
            self.assertIn("| 序号 | 派生证据 | 派生含义 | 来源/统计对象 |", coverage)
            for row in plan.signals:
                self.assertIn(row.signal, coverage)


if __name__ == "__main__":
    unittest.main()
