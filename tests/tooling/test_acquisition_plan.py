import json
import re
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from tooling.acquisition_plan import (  # noqa: E402
    AcquisitionEvent,
    AcquisitionPlan,
    AcquisitionPlanError,
    load_acquisition_plan,
    main,
    read_case_contract,
    render_voice_runner_script,
    validate_acquisition_plan,
    validate_script_output_path,
)


CASE_DIR = ROOT / "doc" / "L3采集Case" / "交流慢充"
FULL_CONTRACT_REF = "doc/L3采集Case/交流慢充/L3-Charge-Slow-FullCycle_Case契约.md"
CURRENT_CONTRACT_REF = (
    "doc/L3采集Case/交流慢充/L3-Charge-Slow-CurrentControl_Case契约.md"
)


def reference_script(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"## \d+\. VoiceRunner脚本Reference\s+```text\n(.*?)```", text, re.DOTALL)
    if not match:
        raise AssertionError(f"VoiceRunner reference block not found: {path}")
    return match.group(1).rstrip() + "\n"


def events_from_reference(script: str, or_refs_by_time: dict[int, tuple[str, ...]]):
    events = []
    current_time = None
    current_title = ""
    current_lines = []

    def finish():
        if current_time is not None:
            events.append(
                AcquisitionEvent(
                    current_time,
                    current_title,
                    tuple(current_lines),
                    or_refs_by_time.get(current_time, ()),
                )
            )

    for line in script.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r"\s*(\d+)s\s+(.+?)\s*", line)
        if match:
            finish()
            current_time = int(match.group(1))
            current_title = match.group(2)
            current_lines = []
        else:
            current_lines.append(line.strip())
    finish()
    return tuple(events)


FULL_OR_REFS = {
    0: ("OR-01.1",),
    60: ("OR-01.2",),
    100: ("OR-02.1",),
    160: ("OR-02.2", "OR-03.2"),
    240: ("OR-03.1", "OR-04.1", "OR-04.2", "OR-05.1", "OR-05.2"),
    320: ("OR-06.1", "OR-06.2"),
    380: ("OR-07.1", "OR-07.2"),
    440: ("OR-07.2",),
    470: ("OR-07.3",),
}

CURRENT_OR_REFS = {
    0: ("OR-06.2", "OR-06.3"),
    30: ("OR-01.1", "OR-01.2", "OR-02.1"),
    70: ("OR-02.2", "OR-02.3", "OR-03.2"),
    130: ("OR-03.1", "OR-03.3", "OR-04.1", "OR-04.2"),
    190: ("OR-05.1", "OR-05.3"),
    250: ("OR-05.2", "OR-06.1"),
}


def make_reference_plan(contract_ref: str, case_id: str, reference_name: str, refs):
    script = reference_script(CASE_DIR / reference_name)
    return (
        AcquisitionPlan(
            "acquisition-plan-v1",
            case_id,
            contract_ref,
            events_from_reference(script, refs),
        ),
        script,
    )


class AcquisitionPlanReferenceTest(unittest.TestCase):
    def test_full_cycle_uses_shared_path_and_matches_reference(self):
        contract = read_case_contract(ROOT / FULL_CONTRACT_REF)
        plan, expected = make_reference_plan(
            FULL_CONTRACT_REF,
            "L3-Charge-Slow-FullCycle",
            "L3-Charge-Slow-FullCycle_脚本Reference.md",
            FULL_OR_REFS,
        )
        validate_acquisition_plan(contract, plan)
        self.assertEqual(expected, render_voice_runner_script(plan))

    def test_current_control_uses_shared_path_and_matches_reference(self):
        contract = read_case_contract(ROOT / CURRENT_CONTRACT_REF)
        plan, expected = make_reference_plan(
            CURRENT_CONTRACT_REF,
            "L3-Charge-Slow-CurrentControl",
            "L3-Charge-Slow-CurrentControl_脚本Reference.md",
            CURRENT_OR_REFS,
        )
        validate_acquisition_plan(contract, plan)
        self.assertEqual(expected, render_voice_runner_script(plan))

    def test_contract_parser_reads_er_or_relationships(self):
        contract = read_case_contract(ROOT / FULL_CONTRACT_REF)
        self.assertEqual(7, len(contract.er_ids))
        self.assertEqual(15, len(contract.or_ids))
        self.assertEqual("ER-07", contract.or_to_er["OR-07.3"])


class AcquisitionPlanValidationTest(unittest.TestCase):
    def setUp(self):
        self.contract = read_case_contract(ROOT / CURRENT_CONTRACT_REF)
        self.plan, _ = make_reference_plan(
            CURRENT_CONTRACT_REF,
            "L3-Charge-Slow-CurrentControl",
            "L3-Charge-Slow-CurrentControl_脚本Reference.md",
            CURRENT_OR_REFS,
        )

    def test_uncovered_or_is_rejected(self):
        events = tuple(
            AcquisitionEvent(
                event.planned_time_s,
                event.title,
                event.instruction_lines,
                tuple(ref for ref in event.or_refs if ref != "OR-06.1"),
            )
            for event in self.plan.events
        )
        invalid = AcquisitionPlan(
            self.plan.schema_version, self.plan.case_id, self.plan.contract_ref, events
        )
        with self.assertRaisesRegex(AcquisitionPlanError, r"uncovered OR IDs.*OR-06\.1"):
            validate_acquisition_plan(self.contract, invalid)

    def test_event_detail_that_looks_like_step_is_rejected(self):
        first = self.plan.events[0]
        events = (
            AcquisitionEvent(
                first.planned_time_s,
                first.title,
                first.instruction_lines + ("20s 伪步骤",),
                first.or_refs,
            ),
        ) + self.plan.events[1:]
        invalid = AcquisitionPlan(
            self.plan.schema_version, self.plan.case_id, self.plan.contract_ref, events
        )
        with self.assertRaisesRegex(AcquisitionPlanError, "parsed as a VoiceRunner Event"):
            validate_acquisition_plan(self.contract, invalid)

    def test_loader_rejects_unknown_fields_instead_of_accepting_vehicle(self):
        payload = {
            "schema_version": "acquisition-plan-v1",
            "case_id": self.plan.case_id,
            "contract_ref": self.plan.contract_ref,
            "events": [],
            "vehicle_id": "TESLA-M3-SOP5",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(AcquisitionPlanError, "unknown fields.*vehicle_id"):
                load_acquisition_plan(path)

    def test_loader_and_validator_accept_minimal_json(self):
        payload = {
            "schema_version": self.plan.schema_version,
            "case_id": self.plan.case_id,
            "contract_ref": self.plan.contract_ref,
            "events": [
                {
                    "planned_time_s": event.planned_time_s,
                    "title": event.title,
                    "instruction_lines": list(event.instruction_lines),
                    "or_refs": list(event.or_refs),
                }
                for event in self.plan.events
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.json"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            loaded = load_acquisition_plan(path)
        validate_acquisition_plan(self.contract, loaded)
        self.assertEqual(self.plan, loaded)

    def test_cli_writes_valid_reference_script(self):
        payload = {
            "schema_version": self.plan.schema_version,
            "case_id": self.plan.case_id,
            "contract_ref": self.plan.contract_ref,
            "events": [
                {
                    "planned_time_s": event.planned_time_s,
                    "title": event.title,
                    "instruction_lines": list(event.instruction_lines),
                    "or_refs": list(event.or_refs),
                }
                for event in self.plan.events
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            plan_path = Path(directory) / "plan.json"
            output_path = Path(directory) / "L3-Charge-Slow-CurrentControl_慢充电流控制采集.txt"
            plan_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            result = main(
                [
                    "--plan",
                    str(plan_path),
                    "--output",
                    str(output_path),
                    "--workspace-root",
                    str(ROOT),
                ]
            )
            self.assertEqual(0, result)
            self.assertEqual(render_voice_runner_script(self.plan), output_path.read_text())

    def test_output_name_requires_case_prefix_and_chinese_collection_suffix(self):
        valid = Path("output/L3-Charge-Slow-CurrentControl_慢充电流控制采集.txt")
        validate_script_output_path(self.plan, valid)
        with self.assertRaisesRegex(AcquisitionPlanError, "output.name"):
            validate_script_output_path(self.plan, "慢充电流控制采集.txt")
        with self.assertRaisesRegex(AcquisitionPlanError, "output.name"):
            validate_script_output_path(
                self.plan, "L3-Charge-Slow-CurrentControl_CurrentControl采集.txt"
            )


if __name__ == "__main__":
    unittest.main()
