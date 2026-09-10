"""Validate an Acquisition Plan and render a VoiceRunner script.

The module deliberately performs no L3 reasoning and contains no Case-specific
generation rules.  AI or a human supplies Event semantics; this module only
loads the frozen Case contract, validates structural references, and renders a
deterministic script.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "acquisition-plan-v1"
CASE_ID_RE = re.compile(r"\*\*Case ID：\*\*\s*`([^`]+)`")
STEP_RE = re.compile(r"^\s*(\d+)s(?:（[^）]*）)?\s+(.+?)\s*$")
TOP_LEVEL_FIELDS = {"schema_version", "case_id", "contract_ref", "events"}
EVENT_FIELDS = {"planned_time_s", "title", "instruction_lines", "or_refs"}
CHINESE_CHAR_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")


class AcquisitionPlanError(ValueError):
    """A deterministic contract, plan, or rendering validation failure."""


@dataclass(frozen=True)
class CaseContract:
    case_id: str
    er_ids: tuple[str, ...]
    or_to_er: Mapping[str, str]
    source_path: Path

    @property
    def or_ids(self) -> tuple[str, ...]:
        return tuple(self.or_to_er)


@dataclass(frozen=True)
class AcquisitionEvent:
    planned_time_s: int
    title: str
    instruction_lines: tuple[str, ...]
    or_refs: tuple[str, ...]


@dataclass(frozen=True)
class AcquisitionPlan:
    schema_version: str
    case_id: str
    contract_ref: str
    events: tuple[AcquisitionEvent, ...]


def _table_cells(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return [cell.strip() for cell in stripped[1:-1].split("|")]


def _duplicates(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def read_case_contract(path: str | Path) -> CaseContract:
    """Read the structural identity and ER/OR relations from an approved contract."""
    source_path = Path(path)
    if source_path.suffix.lower() != ".md":
        raise AcquisitionPlanError(f"contract: expected Markdown file: {source_path}")
    if not source_path.is_file():
        raise AcquisitionPlanError(f"contract: file does not exist: {source_path}")

    text = source_path.read_text(encoding="utf-8")
    case_ids = CASE_ID_RE.findall(text)
    if len(case_ids) != 1:
        raise AcquisitionPlanError(
            f"contract.case_id: expected exactly one Case ID, found {len(case_ids)}"
        )
    if not re.search(r"\*\*当前状态：\*\*[^\n]*已审核通过", text):
        raise AcquisitionPlanError("contract.status: Case contract is not marked 已审核通过")

    er_ids: list[str] = []
    or_to_er: dict[str, str] = {}
    for line_number, line in enumerate(text.splitlines(), start=1):
        cells = _table_cells(line)
        if not cells:
            continue
        if re.fullmatch(r"ER-\d+", cells[0]):
            if len(cells) >= 2 and re.fullmatch(r"OR-\d+\.\d+", cells[1]):
                or_id = cells[1]
                if or_id in or_to_er:
                    raise AcquisitionPlanError(
                        f"contract.or[{or_id}]: duplicate at line {line_number}"
                    )
                or_to_er[or_id] = cells[0]
            elif len(cells) >= 3:
                er_ids.append(cells[0])

    duplicate_ers = _duplicates(er_ids)
    if duplicate_ers:
        raise AcquisitionPlanError(f"contract.er: duplicate IDs: {duplicate_ers}")
    if not er_ids:
        raise AcquisitionPlanError("contract.er: Evidence Requirements table is missing or empty")
    if not or_to_er:
        raise AcquisitionPlanError("contract.or: Observable Requirements table is missing or empty")

    er_set = set(er_ids)
    missing_ers = sorted(set(or_to_er.values()) - er_set)
    if missing_ers:
        raise AcquisitionPlanError(
            f"contract.or: references unknown Evidence Requirements: {missing_ers}"
        )
    return CaseContract(case_ids[0], tuple(er_ids), or_to_er, source_path)


def _require_object(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise AcquisitionPlanError(f"{field}: expected object")
    return value


def _check_fields(value: Mapping[str, Any], allowed: set[str], field: str) -> None:
    unknown = sorted(set(value) - allowed)
    missing = sorted(allowed - set(value))
    if unknown:
        raise AcquisitionPlanError(f"{field}: unknown fields: {unknown}")
    if missing:
        raise AcquisitionPlanError(f"{field}: missing fields: {missing}")


def _string(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise AcquisitionPlanError(f"{field}: expected string")
    return value


def _string_list(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise AcquisitionPlanError(f"{field}: expected array")
    return tuple(_string(item, f"{field}[{index}]") for index, item in enumerate(value))


def load_acquisition_plan(path: str | Path) -> AcquisitionPlan:
    """Load the strict acquisition-plan-v1 JSON shape without adding defaults."""
    source_path = Path(path)
    if not source_path.is_file():
        raise AcquisitionPlanError(f"plan: file does not exist: {source_path}")
    try:
        raw = json.loads(source_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AcquisitionPlanError(f"plan: invalid UTF-8 JSON: {exc}") from exc

    root = _require_object(raw, "plan")
    _check_fields(root, TOP_LEVEL_FIELDS, "plan")
    raw_events = root["events"]
    if not isinstance(raw_events, list):
        raise AcquisitionPlanError("plan.events: expected array")

    events: list[AcquisitionEvent] = []
    for index, item in enumerate(raw_events):
        field = f"plan.events[{index}]"
        event = _require_object(item, field)
        _check_fields(event, EVENT_FIELDS, field)
        planned_time = event["planned_time_s"]
        if not isinstance(planned_time, int) or isinstance(planned_time, bool):
            raise AcquisitionPlanError(f"{field}.planned_time_s: expected integer")
        events.append(
            AcquisitionEvent(
                planned_time_s=planned_time,
                title=_string(event["title"], f"{field}.title"),
                instruction_lines=_string_list(
                    event["instruction_lines"], f"{field}.instruction_lines"
                ),
                or_refs=_string_list(event["or_refs"], f"{field}.or_refs"),
            )
        )

    return AcquisitionPlan(
        schema_version=_string(root["schema_version"], "plan.schema_version"),
        case_id=_string(root["case_id"], "plan.case_id"),
        contract_ref=_string(root["contract_ref"], "plan.contract_ref"),
        events=tuple(events),
    )


def validate_acquisition_plan(contract: CaseContract, plan: AcquisitionPlan) -> None:
    """Validate the plan shape, ordering, references, and complete OR coverage."""
    if plan.schema_version != SCHEMA_VERSION:
        raise AcquisitionPlanError(
            f"plan.schema_version: expected {SCHEMA_VERSION!r}, got {plan.schema_version!r}"
        )
    if plan.case_id != contract.case_id:
        raise AcquisitionPlanError(
            f"plan.case_id: {plan.case_id!r} does not match contract {contract.case_id!r}"
        )

    contract_ref = plan.contract_ref.strip()
    ref_path = PurePosixPath(contract_ref)
    if (
        not contract_ref
        or ref_path.is_absolute()
        or ".." in ref_path.parts
        or ref_path.suffix.lower() != ".md"
    ):
        raise AcquisitionPlanError(
            "plan.contract_ref: expected a workspace-relative Markdown path without '..'"
        )
    if not plan.events:
        raise AcquisitionPlanError("plan.events: at least one Event is required")
    if plan.events[0].planned_time_s != 0:
        raise AcquisitionPlanError("plan.events[0].planned_time_s: first Event must start at 0")

    known_or_ids = set(contract.or_ids)
    covered_or_ids: set[str] = set()
    previous_time = -1
    for index, event in enumerate(plan.events):
        field = f"plan.events[{index}]"
        if event.planned_time_s < 0:
            raise AcquisitionPlanError(f"{field}.planned_time_s: must be non-negative")
        if event.planned_time_s <= previous_time:
            raise AcquisitionPlanError(f"{field}.planned_time_s: must be strictly increasing")
        previous_time = event.planned_time_s

        if not event.title.strip():
            raise AcquisitionPlanError(f"{field}.title: must not be empty")
        if "\n" in event.title or "\r" in event.title:
            raise AcquisitionPlanError(f"{field}.title: must be a single line")
        for line_index, line in enumerate(event.instruction_lines):
            line_field = f"{field}.instruction_lines[{line_index}]"
            if not line.strip():
                raise AcquisitionPlanError(f"{line_field}: must not be empty")
            if "\n" in line or "\r" in line:
                raise AcquisitionPlanError(f"{line_field}: must be a single line")
            if STEP_RE.fullmatch(line):
                raise AcquisitionPlanError(
                    f"{line_field}: would be parsed as a VoiceRunner Event"
                )

        duplicate_refs = _duplicates(event.or_refs)
        if duplicate_refs:
            raise AcquisitionPlanError(f"{field}.or_refs: duplicate IDs: {duplicate_refs}")
        unknown_refs = sorted(set(event.or_refs) - known_or_ids)
        if unknown_refs:
            raise AcquisitionPlanError(f"{field}.or_refs: unknown IDs: {unknown_refs}")
        covered_or_ids.update(event.or_refs)

    uncovered = sorted(known_or_ids - covered_or_ids)
    if uncovered:
        raise AcquisitionPlanError(f"plan.events.or_refs: uncovered OR IDs: {uncovered}")


def _parse_voice_runner_script(text: str) -> tuple[tuple[int, str, tuple[str, ...]], ...]:
    parsed: list[tuple[int, str, tuple[str, ...]]] = []
    current_time: int | None = None
    current_title = ""
    current_lines: list[str] = []

    def finish() -> None:
        nonlocal current_time, current_title, current_lines
        if current_time is not None:
            parsed.append((current_time, current_title, tuple(current_lines)))

    for raw_line in text.splitlines():
        if not raw_line.strip():
            continue
        match = STEP_RE.fullmatch(raw_line)
        if match:
            finish()
            current_time = int(match.group(1))
            current_title = match.group(2)
            current_lines = []
        else:
            if current_time is None:
                raise AcquisitionPlanError("rendered_script: detail appears before first Event")
            current_lines.append(raw_line.strip())
    finish()
    return tuple(parsed)


def render_voice_runner_script(plan: AcquisitionPlan) -> str:
    """Render deterministic UTF-8/LF VoiceRunner TXT content and verify round-trip."""
    blocks: list[str] = []
    for event in plan.events:
        step_prefix = f"{event.planned_time_s:02d}s".ljust(6)
        lines = [f"{step_prefix}{event.title.strip()}"]
        lines.extend(f"      {line.strip()}" for line in event.instruction_lines)
        blocks.append("\n".join(lines))
    rendered = "\n\n".join(blocks) + "\n"

    expected = tuple(
        (event.planned_time_s, event.title.strip(), tuple(x.strip() for x in event.instruction_lines))
        for event in plan.events
    )
    actual = _parse_voice_runner_script(rendered)
    if actual != expected:
        raise AcquisitionPlanError("rendered_script: VoiceRunner round-trip mismatch")
    return rendered


def validate_script_output_path(plan: AcquisitionPlan, output_path: str | Path) -> None:
    """Validate the Case prefix and Chinese collection-name convention."""
    filename = Path(output_path).name
    prefix = f"{plan.case_id}_"
    suffix = "采集.txt"
    if not filename.startswith(prefix) or not filename.endswith(suffix):
        raise AcquisitionPlanError(
            f"output.name: expected '{plan.case_id}_<中文名>采集.txt', got {filename!r}"
        )
    chinese_name = filename[len(prefix) : -len(suffix)]
    if not chinese_name or not CHINESE_CHAR_RE.search(chinese_name):
        raise AcquisitionPlanError(
            "output.name: Chinese business name before '采集.txt' must be non-empty "
            "and contain Chinese characters"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate an Acquisition Plan and render a VoiceRunner script."
    )
    parser.add_argument("--plan", required=True, type=Path, help="Acquisition Plan JSON")
    parser.add_argument("--output", required=True, type=Path, help="Output VoiceRunner TXT")
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=Path.cwd(),
        help="Root used to resolve contract_ref (default: current directory)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        plan = load_acquisition_plan(args.plan)
        contract_path = args.workspace_root / PurePosixPath(plan.contract_ref)
        contract = read_case_contract(contract_path)
        validate_acquisition_plan(contract, plan)
        validate_script_output_path(plan, args.output)
        script = render_voice_runner_script(plan)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(script, encoding="utf-8")
    except (AcquisitionPlanError, OSError) as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
    print(f"OK: {len(plan.events)} events -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
