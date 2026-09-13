import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from tooling.acquisition_context import (  # noqa: E402
    AcquisitionContextError,
    build_review_context,
    parse_review_markdown,
    render_review_markdown,
    write_context_json,
)


class AcquisitionContextTest(unittest.TestCase):
    def make_package(self, root: Path) -> Path:
        package = root / "L3-Test-Demo_测试采集__20260911_120000_000__S0001"
        (package / "photos").mkdir(parents=True)
        (package / "can").mkdir()
        (package / "TESLA-TEST").touch()
        (package / "photos" / "E01-P01_测试.jpg").write_bytes(b"jpeg")
        session = {
            "schema_version": 1,
            "app_version": "0.2.0",
            "session": {
                "session_id": "S0001",
                "source_script_name": "L3-Test-Demo_测试采集.txt",
                "start_clock": "2026-09-11T12:00:00.000+08:00",
                "end_clock": "2026-09-11T12:00:10.000+08:00",
                "end_script_time_us": 10000000,
            },
            "events": [{
                "event_id": "E01", "event_sequence": 1, "action": "测试",
                "action_detail": "记录页面", "plan_time_s": 0, "status": "triggered",
                "trigger_script_time_us": 1000, "skip_script_time_us": None,
            }],
            "photos": [{
                "photo_id": "E01-P01", "event_id": "E01", "photo_sequence": 1,
                "captured_clock": "2026-09-11T12:00:01.000+08:00",
                "captured_script_time_us": 1000000, "file_name": "E01-P01_测试.jpg",
                "content_uri": "content://test", "file_status": "AVAILABLE",
            }],
            "notes": [],
            "audio_recording": {"enabled": False, "status": "DISABLED", "file_name": None},
        }
        (package / "session.json").write_text(
            json.dumps(session, ensure_ascii=False), encoding="utf-8"
        )
        (package / "event_timeline.csv").write_text(
            "event_id,action,plan_time_s,status,session_script_time_us,skip_script_time_us,clock_iso,clock_epoch_ms\n"
            'E01,测试,0,triggered,1000,,"2026-09-11T12:00:00.001+08:00",1789099200001\n',
            encoding="utf-8",
        )
        (package / "can" / "test.asc").write_text(
            "date Fri Sep 11 12:00:00 PM 2026\n"
            "base hex timestamps absolute\n"
            "0.000000 1 100 Rx d 1 00\n"
            "9.500000 1 100 Rx d 1 00\n"
            "End Triggerblock\n",
            encoding="utf-8",
        )
        return package

    def add_value(self, context):
        context["round"]["events"][0]["resources"][0]["values"] = [{
            "value_id": "E01-P01-V01",
            "name": "电压",
            "ai_value": 220.5,
            "unit": "V",
            "source_location": "画面中部|电压后",
            "confirmed_value": 220.5,
            "review_status": "PENDING",
            "review_comment": None,
        }]

    def test_prepare_reads_identity_resources_and_asc_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            context = build_review_context(self.make_package(Path(tmp)))
            self.assertEqual("L3-Test-Demo", context["round"]["case_id"])
            self.assertEqual("测试采集", context["package"]["collection_name"])
            self.assertEqual("TESLA-TEST", context["round"]["vehicle_id"])
            self.assertEqual(1, len(context["round"]["events"]))
            self.assertEqual(1, len(context["round"]["events"][0]["resources"]))
            self.assertEqual(9.5, context["validation"]["asc_files"][0]["time"]["duration_s"])

    def test_review_render_and_finalize(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            context = build_review_context(self.make_package(root))
            self.add_value(context)
            review_path = root / "recog_values_review.md"
            render_review_markdown(context, review_path)
            rendered = review_path.read_text(encoding="utf-8")
            self.assertIn("![img](", rendered)
            self.assertIn("画面中部\\|电压后", rendered)

            with self.assertRaisesRegex(AcquisitionContextError, "must be APPROVED"):
                write_context_json(context, parse_review_markdown(review_path), root / "final.json")

            approved = rendered.replace("`DRAFT`", "`APPROVED`", 1).replace(
                "| PENDING |", "| ACCEPTED |"
            )
            review_path.write_text(approved, encoding="utf-8")
            write_context_json(context, parse_review_markdown(review_path), root / "final.json")
            final = json.loads((root / "final.json").read_text(encoding="utf-8"))
            value = final["round"]["events"][0]["resources"][0]["values"][0]
            self.assertEqual("APPROVED", final["review_status"])
            self.assertEqual(220.5, value["effective_value"])
            self.assertEqual("画面中部|电压后", value["source_location"])

    def test_changed_source_blocks_finalize(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = self.make_package(root)
            context = build_review_context(package)
            review_path = root / "review.md"
            render_review_markdown(context, review_path)
            review_path.write_text(
                review_path.read_text(encoding="utf-8").replace("`DRAFT`", "`APPROVED`", 1),
                encoding="utf-8",
            )
            (package / "event_timeline.csv").write_text("changed", encoding="utf-8")
            with self.assertRaisesRegex(AcquisitionContextError, "source changed"):
                write_context_json(context, parse_review_markdown(review_path), root / "final.json")

    def test_s0009_integration_shape(self):
        package = ROOT / "input" / "L3-Charge-Slow-FullCycle_慢充全过程采集__20260911_133727_858__S0009"
        if not package.is_dir():
            self.skipTest("S0009 input is not available")
        context = build_review_context(package)
        self.assertEqual(11, len(context["round"]["events"]))
        self.assertEqual(
            9,
            sum(len(event["resources"]) for event in context["round"]["events"]),
        )
        self.assertEqual(2, len(context["validation"]["asc_files"]))
        self.assertEqual("DISABLED", context["round"]["audio_recording"]["status"])


if __name__ == "__main__":
    unittest.main()
