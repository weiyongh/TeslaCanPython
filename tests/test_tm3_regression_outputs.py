import csv
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from report_renderer import validate_report_bundle
from evidence_plan import read_approved_csv
from render_tm3_regression import tm3_009_report, tm3_010_report


class FrozenTm3OutputTest(unittest.TestCase):
    FOLDERS = (("TM3-009", ROOT / "output/TM3-009/report_v1"),
               ("TM3-010", ROOT / "output/TM3-010"))

    def test_tm3_009_and_010_have_four_common_outputs(self):
        for exp, folder in self.FOLDERS:
            for name in (f"{exp}_最终报告.md", "采集时间线与关键Signal.md", "DBC关键Signal覆盖与可读性.md", "工程审计.md"):
                self.assertTrue((folder / name).is_file(), name)

    def test_current_renderer_reproduces_009_010_golden_byte_identically(self):
        renderers = {"TM3-009": tm3_009_report, "TM3-010": tm3_010_report}
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for exp, golden in self.FOLDERS:
                out = root / exp
                shutil.copytree(golden / "baseline_evidence", out / "baseline_evidence")
                plan = read_approved_csv(golden / "evidence_plan_approved.csv")
                renderers[exp](plan, out)
                for name in (f"{exp}_最终报告.md", "采集时间线与关键Signal.md",
                             "DBC关键Signal覆盖与可读性.md", "工程审计.md"):
                    self.assertEqual((golden / name).read_bytes(), (out / name).read_bytes(),
                                     f"{exp}/{name}")

    def test_human_timeline_contract(self):
        expected = "| 时间(s) | 状态/动作 | 电门(%) | 请求扭矩(Nm) | 实际扭矩(Nm) | 车速(km/h) | 电驱功率(kW) | Pack电流(A) | Pack功率(kW) | 备注 |"
        for path in (ROOT / "output/TM3-009/report_v1/采集时间线与关键Signal.md", ROOT / "output/TM3-010/采集时间线与关键Signal.md"):
            text = path.read_text(encoding="utf-8")
            self.assertIn(expected, text)
            header = next(line for line in text.splitlines() if line.startswith("| 时间(s)"))
            self.assertNotIn("E00", header)
            self.assertNotIn("Signal age", header)
            self.assertNotIn("DLC", header)

    def test_tm3_010_frozen_conclusion(self):
        text = (ROOT / "output/TM3-010/TM3-010_最终报告.md").read_text(encoding="utf-8")
        for phrase in ("20 km/h短时条件化基线有效", "40 km/h未满足稳态条件", "仅补采40 km/h稳定段，无需重复20 km/h实验"):
            self.assertIn(phrase, text)
        self.assertIn("状态/条件/能力判断", text)
        self.assertIn("仲裁/决策（本次无直接观测）", text)
        self.assertIn("动力/物理响应", text)
        self.assertIn("能源交叉验证", text)
        self.assertIn("20/40 km/h是驾驶员实验目标，不是电驱控制器内部车速目标", text)
        self.assertNotIn("。；", text)

    def test_tm3_010_signal_purposes_are_signal_specific(self):
        text = (ROOT / "output/TM3-010/DBC关键Signal覆盖与可读性.md").read_text(encoding="utf-8")
        self.assertIn("识别驾驶输入及匀速调节", text)
        self.assertIn("确认实验处于D挡驱动状态", text)
        self.assertIn("识别目标速度带、连续稳定窗口及速度波动", text)
        self.assertNotIn("建立稳定匀速的输入—请求—执行—运动主线及能源/条件证据", text)
        rows = [line for line in text.splitlines() if line.startswith("| ")][2:]
        purposes = [row.split("|")[-2].strip() for row in rows]
        self.assertGreater(len(set(purposes)), 8)

    def test_golden_markdown_has_no_binary_float_tail(self):
        for path in (ROOT / "output/TM3-009/report_v1/采集时间线与关键Signal.md",
                     ROOT / "output/TM3-010/DBC关键Signal覆盖与可读性.md"):
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"\d+\.\d{10,}")

    def test_tm3_010_review_and_scope(self):
        folder = ROOT / "output/TM3-010"
        for name in ("evidence_plan_context.md", "evidence_plan_draft.csv", "待审Signal证据表.md", "evidence_plan_review_overrides.csv", "evidence_plan_approved.csv"):
            self.assertTrue((folder / name).is_file(), name)
        with (folder / "evidence_plan_approved.csv").open(encoding="utf-8-sig") as stream:
            rows = list(csv.DictReader(stream))
        self.assertTrue(rows)
        self.assertEqual({"THIS_EXPERIMENT_ONLY"}, {x["scope"] for x in rows})
        axle = next(x for x in rows if x["signal_key"] == "DI_axleSpeed")
        self.assertEqual("P0", axle["suggested_priority"])
        self.assertEqual("P1", axle["effective_priority"])
        self.assertEqual("HUMAN", axle["decision_source"])
        self.assertFalse(any(x["review_required"] == "YES" and not x["reviewer"] for x in rows))

    def test_golden_fixed_sections_and_order(self):
        final_expected = ["## 实验信息与适用范围", "## 事实与关键证据", "## 控制关系",
                          "## 诊断判断", "### Evidence Assessment", "## 证据边界",
                          "## 结论与下一步建议"]
        for exp, folder in self.FOLDERS:
            final = (folder / f"{exp}_最终报告.md").read_text(encoding="utf-8")
            headings = [line for line in final.splitlines()
                        if line.startswith("## ") or line.startswith("### ")]
            positions = [headings.index(item) for item in final_expected]
            self.assertEqual(positions, sorted(positions))
            coverage = (folder / "DBC关键Signal覆盖与可读性.md").read_text(encoding="utf-8")
            self.assertEqual(["## 核心Signal表", "## DBC异常与可读性说明"],
                [line for line in coverage.splitlines() if line.startswith("## ")])
            self.assertIn("| 控制树角色 | Signal | Message | CAN ID | 单位 | 本次观测范围/状态 | 是否变化 | 解码状态 | 本次用途 |", coverage)
            audit = (folder / "工程审计.md").read_text(encoding="utf-8")
            self.assertEqual(["## Evidence Plan状态", "## 数据与复现", "## 工程字段边界"],
                [line for line in audit.splitlines() if line.startswith("## ")])

    def test_golden_core_signal_order_follows_effective_order(self):
        for _exp, folder in self.FOLDERS:
            with (folder / "evidence_plan_approved.csv").open(encoding="utf-8-sig") as stream:
                approved = [row for row in csv.DictReader(stream) if "CORE_SIGNAL_TABLE" in row["effective_report_position"]]
            expected = [row["signal"] for row in sorted(approved, key=lambda row: int(row["effective_order"]))]
            coverage = (folder / "DBC关键Signal覆盖与可读性.md").read_text(encoding="utf-8")
            data_rows = [line for line in coverage.splitlines() if line.startswith("| ")][2:]
            actual = [line.split("|")[2].strip() for line in data_rows]
            self.assertEqual(expected, actual)

    def test_all_current_shared_renderer_completed_tm3_pass_contract_validator(self):
        # TM3-007 is intentionally excluded until the explicitly approved phase-two
        # rerender; this stage must not rewrite its existing reports or machine evidence.
        for exp, folder in self.FOLDERS:
            validate_report_bundle(exp, folder, "DRIVE")


if __name__ == "__main__":
    unittest.main()
