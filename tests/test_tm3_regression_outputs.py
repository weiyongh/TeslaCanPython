import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class FrozenTm3OutputTest(unittest.TestCase):
    def test_tm3_009_and_010_have_four_common_outputs(self):
        for exp, folder in (("TM3-009", ROOT / "output/TM3-009/report_v1"), ("TM3-010", ROOT / "output/TM3-010")):
            for name in (f"{exp}_最终报告.md", "采集时间线与关键Signal.md", "DBC关键Signal覆盖与可读性.md", "工程审计.md"):
                self.assertTrue((folder / name).is_file(), name)

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


if __name__ == "__main__":
    unittest.main()
