"""Prepare, render, and finalize an Acquisition Context.

This tool deliberately stops before CAN payload analysis.  It reads the
VoiceRunner contract, file-level ASC timing, and evidence resources; AI or a
human supplies recognition values in the persisted to-review JSON.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import tempfile
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


CONTEXT_SCHEMA_VERSION = "acquisition-context-v1"
SUPPORTED_VOICERUNNER_SCHEMA = 1
CSV_HEADER = [
    "event_id",
    "action",
    "plan_time_s",
    "status",
    "session_script_time_us",
    "skip_script_time_us",
    "clock_iso",
    "clock_epoch_ms",
]
REVIEW_STATUSES = {"PENDING", "ACCEPTED", "CORRECTED", "REJECTED", "HUMAN_ADDED"}
FINAL_STATUSES = REVIEW_STATUSES - {"PENDING"}
ROOT = Path(__file__).resolve().parents[2]


class AcquisitionContextError(ValueError):
    """A readable input, review, or finalization error."""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AcquisitionContextError(f"cannot read UTF-8 JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AcquisitionContextError(f"expected JSON object: {path}")
    return value


def _relative(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()


def _fingerprint(path: Path, package_dir: Path) -> dict[str, Any]:
    stat = path.stat()
    return {
        "path": _relative(path, package_dir),
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }


def _unique(values: Iterable[str], field: str) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    if duplicates:
        raise AcquisitionContextError(f"{field}: duplicate IDs: {sorted(duplicates)}")


def inspect_package(package_dir: str | Path) -> dict[str, Any]:
    """Inspect package files without interpreting CAN payloads."""
    package = Path(package_dir).resolve()
    if not package.is_dir():
        raise AcquisitionContextError(f"package directory does not exist: {package}")

    session_path = package / "session.json"
    csv_path = package / "event_timeline.csv"
    missing = [p.name for p in (session_path, csv_path) if not p.is_file()]
    if missing:
        raise AcquisitionContextError(f"package missing required files: {missing}")

    markers = sorted(
        path
        for path in package.iterdir()
        if path.is_file()
        and not path.suffix
        and path.name not in {"session", "event_timeline"}
        and path.stat().st_size == 0
    )
    if len(markers) != 1:
        raise AcquisitionContextError(
            f"vehicle marker: expected one empty extensionless file, found {len(markers)}"
        )

    photos = sorted((package / "photos").glob("*")) if (package / "photos").is_dir() else []
    audio = sorted((package / "audio").glob("*")) if (package / "audio").is_dir() else []
    asc_files = sorted((package / "can").glob("*.asc")) if (package / "can").is_dir() else []
    return {
        "package_dir": package,
        "session_path": session_path,
        "csv_path": csv_path,
        "vehicle_marker": markers[0],
        "photo_files": [p for p in photos if p.is_file()],
        "audio_files": [p for p in audio if p.is_file()],
        "asc_files": [p for p in asc_files if p.is_file()],
    }


def _optional_int(value: str, field: str) -> int | None:
    if value == "":
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise AcquisitionContextError(f"{field}: expected integer or empty") from exc


def read_voicerunner(package_dir: str | Path) -> dict[str, Any]:
    """Read the v1 VoiceRunner JSON and CSV identity/relationship contract."""
    package = Path(package_dir).resolve()
    session = _read_json(package / "session.json")
    if session.get("schema_version") != SUPPORTED_VOICERUNNER_SCHEMA:
        raise AcquisitionContextError(
            f"session.schema_version: unsupported {session.get('schema_version')!r}"
        )
    session_meta = session.get("session")
    if not isinstance(session_meta, dict):
        raise AcquisitionContextError("session.session: expected object")
    events = session.get("events")
    photos = session.get("photos")
    notes = session.get("notes")
    audio = session.get("audio_recording")
    if not isinstance(events, list) or not isinstance(photos, list) or not isinstance(notes, list):
        raise AcquisitionContextError("session: events, photos, and notes must be arrays")
    if not isinstance(audio, dict):
        raise AcquisitionContextError("session.audio_recording: expected object")

    event_ids = [str(item.get("event_id", "")) for item in events if isinstance(item, dict)]
    if len(event_ids) != len(events) or any(not value for value in event_ids):
        raise AcquisitionContextError("session.events: every Event needs event_id")
    _unique(event_ids, "session.events")

    with (package / "event_timeline.csv").open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != CSV_HEADER:
            raise AcquisitionContextError(
                f"event_timeline.csv: unexpected header {reader.fieldnames!r}"
            )
        timeline = list(reader)
    csv_ids = [row["event_id"] for row in timeline]
    _unique(csv_ids, "event_timeline.csv")
    if csv_ids != event_ids:
        raise AcquisitionContextError("VoiceRunner JSON/CSV Event IDs or order do not match")

    for index, (event, row) in enumerate(zip(events, timeline)):
        if not isinstance(event, dict):
            raise AcquisitionContextError(f"session.events[{index}]: expected object")
        csv_time = _optional_int(row["session_script_time_us"], f"csv[{index}].session_script_time_us")
        if csv_time != event.get("trigger_script_time_us"):
            raise AcquisitionContextError(f"Event {row['event_id']}: JSON/CSV trigger time differs")

    return {
        "schema_version": session["schema_version"],
        "app_version": session.get("app_version"),
        "session": session_meta,
        "events": events,
        "photos": photos,
        "notes": notes,
        "audio_recording": audio,
        "timeline": timeline,
    }


_ASC_DATE_RE = re.compile(
    r"^date\s+\w+\s+(\w+)\s+(\d{1,2})\s+(\d{2}):(\d{2}):(\d{2})\s+(AM|PM)\s+(\d{4})$",
    re.IGNORECASE,
)
_ASC_OFFSET_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s+")
_MONTHS = {name: index for index, name in enumerate(
    ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"), 1
)}


def read_asc_time_info(asc_path: str | Path, tz: timezone | None = None) -> dict[str, Any]:
    """Read ASC header and final relative timestamp, never CAN payload fields."""
    path = Path(asc_path)
    if not path.is_file():
        raise AcquisitionContextError(f"ASC file does not exist: {path}")
    header: str | None = None
    first_offset: float | None = None
    last_offset: float | None = None
    try:
        with path.open(encoding="utf-8", errors="replace") as stream:
            for line in stream:
                stripped = line.strip()
                if header is None and stripped.lower().startswith("date "):
                    header = stripped
                match = _ASC_OFFSET_RE.match(line)
                if match:
                    offset = float(match.group(1))
                    if first_offset is None:
                        first_offset = offset
                    last_offset = offset
    except OSError as exc:
        raise AcquisitionContextError(f"cannot read ASC {path}: {exc}") from exc
    if header is None or first_offset is None or last_offset is None:
        raise AcquisitionContextError(f"ASC basic timing unavailable: {path}")
    match = _ASC_DATE_RE.match(header)
    if not match or match.group(1).title() not in _MONTHS:
        raise AcquisitionContextError(f"ASC date header unsupported: {header!r}")
    month, day, hour, minute, second, am_pm, year = match.groups()
    hour_number = int(hour) % 12 + (12 if am_pm.upper() == "PM" else 0)
    start = datetime(
        int(year), _MONTHS[month.title()], int(day), hour_number, int(minute), int(second),
        tzinfo=tz,
    ) + timedelta(seconds=first_offset)
    end = datetime(
        int(year), _MONTHS[month.title()], int(day), hour_number, int(minute), int(second),
        tzinfo=tz,
    ) + timedelta(seconds=last_offset)
    return {
        "start_clock": start.isoformat(timespec="milliseconds"),
        "end_clock": end.isoformat(timespec="milliseconds"),
        "first_offset_s": first_offset,
        "last_offset_s": last_offset,
        "duration_s": last_offset - first_offset,
    }


def _timezone_from_iso(value: Any) -> timezone | None:
    if not isinstance(value, str):
        return None
    try:
        offset = datetime.fromisoformat(value).utcoffset()
        return timezone(offset) if offset is not None else None
    except ValueError:
        return None


def _collection_identity(source_script_name: Any, package_name: str) -> tuple[str, str]:
    source = source_script_name if isinstance(source_script_name, str) else ""
    stem = Path(source).stem if source else package_name.split("__", 1)[0]
    if "_" in stem:
        case_id, chinese_name = stem.split("_", 1)
    else:
        case_id, chinese_name = stem, stem
    return case_id, chinese_name


def _empty_value() -> list[dict[str, Any]]:
    return []


def build_review_context(package_dir: str | Path) -> dict[str, Any]:
    """Build the persisted deterministic context used by Recognition."""
    package_info = inspect_package(package_dir)
    package = package_info["package_dir"]
    voice = read_voicerunner(package)
    session_meta = voice["session"]
    case_id, collection_name = _collection_identity(
        session_meta.get("source_script_name"), package.name
    )
    vehicle_id = package_info["vehicle_marker"].name
    round_id = session_meta.get("session_id")
    if not isinstance(round_id, str) or not round_id:
        raise AcquisitionContextError("session.session_id: expected non-empty string")

    issues: list[str] = []
    photos_by_name = {path.name: path for path in package_info["photo_files"]}
    event_map: dict[str, dict[str, Any]] = {}
    timeline_by_id = {row["event_id"]: row for row in voice["timeline"]}
    for event in voice["events"]:
        event_id = event["event_id"]
        row = timeline_by_id[event_id]
        event_map[event_id] = {
            "event_id": event_id,
            "event_sequence": event.get("event_sequence"),
            "title": event.get("action"),
            "detail": event.get("action_detail"),
            "plan_time_s": event.get("plan_time_s"),
            "status": event.get("status"),
            "actual_clock": row.get("clock_iso") or None,
            "actual_script_time_us": _optional_int(
                row.get("session_script_time_us", ""), f"timeline[{event_id}]"
            ),
            "resources": [],
        }

    photo_to_event: dict[str, str] = {}
    for photo in voice["photos"]:
        if not isinstance(photo, dict):
            raise AcquisitionContextError("session.photos: expected objects")
        photo_id = photo.get("photo_id")
        event_id = photo.get("event_id")
        file_name = photo.get("file_name")
        if not all(isinstance(v, str) and v for v in (photo_id, event_id, file_name)):
            raise AcquisitionContextError("session.photos: invalid photo identity")
        if event_id not in event_map:
            raise AcquisitionContextError(f"photo {photo_id}: unknown Event {event_id}")
        photo_to_event[photo_id] = event_id
        file_path = photos_by_name.get(file_name)
        if file_path is None:
            issues.append(f"photo file missing: {file_name}")
        event_map[event_id]["resources"].append({
            "resource_id": photo_id,
            "type": "PHOTO",
            "target_id": event_id,
            "file": f"photos/{file_name}",
            "clock": photo.get("captured_clock"),
            "script_time_us": photo.get("captured_script_time_us"),
            "file_status": "AVAILABLE" if file_path else "UNAVAILABLE",
            "values": _empty_value(),
        })

    for note in voice["notes"]:
        if not isinstance(note, dict):
            raise AcquisitionContextError("session.notes: expected objects")
        note_id = note.get("note_id")
        target_type = note.get("target_type")
        target_id = note.get("target_id")
        if target_type == "EVENT":
            event_id = target_id
        elif target_type == "PHOTO":
            event_id = photo_to_event.get(str(target_id))
        else:
            raise AcquisitionContextError(f"note {note_id}: unsupported target_type")
        if not isinstance(event_id, str) or event_id not in event_map:
            raise AcquisitionContextError(f"note {note_id}: target does not resolve to Event")
        event_map[event_id]["resources"].append({
            "resource_id": note_id,
            "type": "NOTE",
            "target_id": target_id,
            "target_type": target_type,
            "text": note.get("text"),
            "clock": note.get("updated_clock") or note.get("created_clock"),
            "deleted": bool(note.get("deleted")),
            "values": _empty_value(),
        })

    audio = deepcopy(voice["audio_recording"])
    audio_file_name = audio.get("file_name")
    if isinstance(audio_file_name, str) and audio_file_name:
        matching_audio = next(
            (path for path in package_info["audio_files"] if path.name == audio_file_name), None
        )
        audio["file"] = f"audio/{audio_file_name}"
        audio["file_status"] = "AVAILABLE" if matching_audio else "UNAVAILABLE"
        if matching_audio is None:
            issues.append(f"audio file missing: {audio_file_name}")

    tz = _timezone_from_iso(session_meta.get("start_clock"))
    asc_entries = []
    for asc_path in package_info["asc_files"]:
        try:
            timing = read_asc_time_info(asc_path, tz)
        except AcquisitionContextError as exc:
            issues.append(str(exc))
            timing = None
        asc_entries.append({
            "file": _relative(asc_path, package),
            "time": timing,
            "fingerprint": _fingerprint(asc_path, package),
        })
    if not asc_entries:
        issues.append("no ASC files found")

    source_paths = [
        package_info["vehicle_marker"], package_info["session_path"], package_info["csv_path"],
        *package_info["photo_files"], *package_info["audio_files"], *package_info["asc_files"],
    ]
    return {
        "schema_version": CONTEXT_SCHEMA_VERSION,
        "review_status": "DRAFT",
        "reviewer": None,
        "reviewed_at": None,
        "package": {
            "name": package.name,
            "path": package.as_posix(),
            "collection_name": collection_name,
            "source_files": [_fingerprint(path, package) for path in source_paths],
        },
        "validation": {
            "status": "WARNING" if issues else "PASS",
            "issues": issues,
            "voicerunner": {
                "schema_version": voice["schema_version"],
                "app_version": voice["app_version"],
                "start_clock": session_meta.get("start_clock"),
                "end_clock": session_meta.get("end_clock"),
                "duration_s": (
                    session_meta.get("end_script_time_us") / 1_000_000
                    if isinstance(session_meta.get("end_script_time_us"), int) else None
                ),
            },
            "asc_files": asc_entries,
        },
        "round": {
            "round_id": round_id,
            "case_id": case_id,
            "vehicle_id": vehicle_id,
            "source_script_name": session_meta.get("source_script_name"),
            "audio_recording": audio,
            "events": list(event_map.values()),
        },
    }


def _atomic_json_write(value: Mapping[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", newline="\n", dir=output_path.parent,
        prefix=f".{output_path.name}.", suffix=".tmp", delete=False,
    ) as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        temporary = Path(stream.name)
    temporary.replace(output_path)


def write_toreview_json(context: Mapping[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    _atomic_json_write(context, path)
    return path


def _md_cell(value: Any) -> str:
    if value is None:
        text = ""
    elif isinstance(value, (dict, list, bool, int, float)):
        text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    else:
        text = str(value)
    return text.replace("\\", "\\\\").replace("|", "\\|").replace("\r\n", "<br>").replace("\n", "<br>")


def _review_image_path(context_path: Path, package_path: Path, resource_file: str) -> str:
    target = package_path / resource_file
    try:
        return Path(__import__("os").path.relpath(target, context_path.parent)).as_posix()
    except ValueError:
        return target.as_posix()


def render_review_markdown(context: Mapping[str, Any], output_path: str | Path) -> Path:
    """Render the stable, human-editable no-UI review document."""
    output = Path(output_path)
    package = context.get("package", {})
    round_data = context.get("round", {})
    validation = context.get("validation", {})
    package_path = Path(str(package.get("path", "")))
    lines = [
        "# Recognition Values Review",
        "",
        "<!-- ACQUISITION_CONTEXT_REVIEW_V1 -->",
        "",
        "## Round",
        "",
        "| 字段 | 内容 |",
        "|---|---|",
        f"| 采集名称 | {_md_cell(package.get('collection_name'))} |",
        f"| Acquisition Package | `{_md_cell(package.get('name'))}` |",
        f"| Round | `{_md_cell(round_data.get('round_id'))}` |",
        f"| Vehicle | `{_md_cell(round_data.get('vehicle_id'))}` |",
        f"| Validation | `{_md_cell(validation.get('status'))}` |",
        f"| Review Status | `{_md_cell(context.get('review_status', 'DRAFT'))}` |",
        f"| Reviewer | {_md_cell(context.get('reviewer'))} |",
        f"| Reviewed At | {_md_cell(context.get('reviewed_at'))} |",
        "",
        "保留AI识别值和值位置；人工修改确认值、审核状态和审核备注。全部完成后将Review Status改为`APPROVED`。",
        "",
    ]
    issues = validation.get("issues") or []
    if issues:
        lines.extend(["### Validation Issues", ""])
        lines.extend(f"- {_md_cell(issue)}" for issue in issues)
        lines.append("")

    for event in round_data.get("events", []):
        event_id = event.get("event_id")
        lines.extend([
            f"## Event {event_id}：{event.get('title') or ''}",
            "",
            f"<!-- EVENT:{event_id} -->",
            "",
            f"- 实际时间：`{event.get('actual_clock') or ''}`",
            f"- 状态：`{event.get('status') or ''}`",
            "",
        ])
        for resource in event.get("resources", []):
            resource_id = resource.get("resource_id")
            resource_type = resource.get("type")
            lines.extend([
                f"### Resource {resource_id}（{resource_type}）",
                "",
                f"<!-- RESOURCE:{resource_id} -->",
                "",
            ])
            if resource_type == "PHOTO":
                file_name = resource.get("file", "")
                lines.extend([
                    f"- 文件：`{_md_cell(file_name)}`",
                    f"- 拍摄时间：`{_md_cell(resource.get('clock'))}`",
                    "- 图片预览：",
                    "",
                    f"![img]({_review_image_path(output, package_path, file_name)})",
                    "",
                ])
            elif resource_type == "NOTE":
                lines.extend([
                    f"- 来源：`{_md_cell(resource.get('target_id'))}`",
                    f"- 原文：{_md_cell(resource.get('text'))}",
                    "",
                ])
            elif resource_type == "AUDIO":
                lines.extend([
                    f"- 文件：`{_md_cell(resource.get('file'))}`",
                    f"- 片段：`{_md_cell(resource.get('segment'))}`",
                    f"- 转写：{_md_cell(resource.get('transcript'))}",
                    "",
                ])
            lines.extend([
                "| Value ID | 名称 | AI识别值 | 单位 | 值位置 | 人工确认值 | 审核状态 | 审核备注 |",
                "|---|---|---|---|---|---|---|---|",
            ])
            for value in resource.get("values", []):
                cells = [
                    value.get("value_id"), value.get("name"), value.get("ai_value"),
                    value.get("unit"), value.get("source_location"),
                    value.get("confirmed_value"), value.get("review_status", "PENDING"),
                    value.get("review_comment"),
                ]
                lines.append("| " + " | ".join(_md_cell(cell) for cell in cells) + " |")
            lines.append("")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write("\n".join(lines).rstrip() + "\n")
    return output


def _split_md_row(line: str) -> list[str]:
    text = line.strip()
    if not text.startswith("|") or not text.endswith("|"):
        return []
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for char in text[1:-1]:
        if escaped:
            current.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == "|":
            cells.append("".join(current).strip().replace("<br>", "\n"))
            current = []
        else:
            current.append(char)
    cells.append("".join(current).strip().replace("<br>", "\n"))
    return cells


def _unquote(value: str) -> str:
    return value[1:-1] if len(value) >= 2 and value.startswith("`") and value.endswith("`") else value


def _scalar(value: str) -> Any:
    value = _unquote(value.strip())
    if value == "":
        return None
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return value
    return parsed if not isinstance(parsed, (dict, list)) else value


def parse_review_markdown(review_path: str | Path) -> dict[str, Any]:
    """Parse the constrained tables emitted by render_review_markdown."""
    path = Path(review_path)
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise AcquisitionContextError(f"cannot read Review Markdown: {exc}") from exc
    if "<!-- ACQUISITION_CONTEXT_REVIEW_V1 -->" not in lines:
        raise AcquisitionContextError("Review Markdown marker is missing")

    metadata: dict[str, Any] = {}
    values: list[dict[str, Any]] = []
    current_event: str | None = None
    current_resource: str | None = None
    in_values = False
    for line in lines:
        if line.startswith("<!-- EVENT:") and line.endswith(" -->"):
            current_event = line[len("<!-- EVENT:"):-len(" -->")]
            current_resource = None
            in_values = False
            continue
        if line.startswith("<!-- RESOURCE:") and line.endswith(" -->"):
            current_resource = line[len("<!-- RESOURCE:"):-len(" -->")]
            in_values = False
            continue
        cells = _split_md_row(line)
        if cells[:2] == ["Value ID", "名称"]:
            in_values = True
            continue
        if cells and all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        if in_values and cells:
            if len(cells) != 8:
                raise AcquisitionContextError(f"Review value row needs 8 columns: {line}")
            if not cells[0]:
                continue
            values.append({
                "event_id": current_event,
                "resource_id": current_resource,
                "value_id": _unquote(cells[0]),
                "name": _scalar(cells[1]),
                "ai_value": _scalar(cells[2]),
                "unit": _scalar(cells[3]),
                "source_location": _scalar(cells[4]),
                "confirmed_value": _scalar(cells[5]),
                "review_status": _unquote(cells[6]),
                "review_comment": _scalar(cells[7]),
            })
            continue
        if cells and len(cells) == 2 and cells[0] in {
            "采集名称", "Acquisition Package", "Round", "Vehicle", "Validation",
            "Review Status", "Reviewer", "Reviewed At",
        }:
            metadata[cells[0]] = _scalar(cells[1])
    return {"metadata": metadata, "values": values}


def _resource_index(context: Mapping[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for event in context.get("round", {}).get("events", []):
        event_id = event.get("event_id")
        for resource in event.get("resources", []):
            key = (event_id, resource.get("resource_id"))
            if key in index:
                raise AcquisitionContextError(f"duplicate Resource: {key}")
            index[key] = resource
    return index


def _verify_fingerprints(context: Mapping[str, Any]) -> None:
    package = context.get("package", {})
    package_path = Path(str(package.get("path", "")))
    for item in package.get("source_files", []):
        path = package_path / item["path"]
        if not path.is_file():
            raise AcquisitionContextError(f"source changed: missing {item['path']}")
        current = _fingerprint(path, package_path)
        if current["size"] != item.get("size") or current["mtime_ns"] != item.get("mtime_ns"):
            raise AcquisitionContextError(f"source changed: {item['path']}")


def validate_approved_review(
    toreview: Mapping[str, Any], review: Mapping[str, Any]
) -> dict[tuple[str, str], list[dict[str, Any]]]:
    metadata = review.get("metadata", {})
    if metadata.get("Review Status") != "APPROVED":
        raise AcquisitionContextError("Review Status must be APPROVED")
    expected = {
        "Acquisition Package": toreview.get("package", {}).get("name"),
        "Round": toreview.get("round", {}).get("round_id"),
        "Vehicle": toreview.get("round", {}).get("vehicle_id"),
    }
    for field, value in expected.items():
        if metadata.get(field) != value:
            raise AcquisitionContextError(f"Review {field} does not match to-review JSON")

    resources = _resource_index(toreview)
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {key: [] for key in resources}
    value_ids: list[str] = []
    for value in review.get("values", []):
        key = (value.get("event_id"), value.get("resource_id"))
        if key not in resources:
            raise AcquisitionContextError(f"Review Value references unknown Resource: {key}")
        status = value.get("review_status")
        if status not in FINAL_STATUSES:
            raise AcquisitionContextError(
                f"Value {value.get('value_id')}: invalid or pending review_status {status!r}"
            )
        if status != "REJECTED" and value.get("confirmed_value") is None:
            raise AcquisitionContextError(f"Value {value.get('value_id')}: confirmed value required")
        value_ids.append(str(value.get("value_id")))
        grouped[key].append(value)
    if any(not value or value == "None" for value in value_ids):
        raise AcquisitionContextError("every reviewed Value needs Value ID")
    _unique(value_ids, "Review Values")

    original_by_id: dict[str, dict[str, Any]] = {}
    for resource in resources.values():
        for value in resource.get("values", []):
            original_by_id[str(value.get("value_id"))] = value
    reviewed_by_id = {value["value_id"]: value for values in grouped.values() for value in values}
    missing = sorted(set(original_by_id) - set(reviewed_by_id))
    if missing:
        raise AcquisitionContextError(f"Review removed existing Values: {missing}")
    for value_id, original in original_by_id.items():
        reviewed = reviewed_by_id[value_id]
        for field in ("name", "ai_value", "unit", "source_location"):
            if reviewed.get(field) != original.get(field):
                raise AcquisitionContextError(f"Value {value_id}: immutable {field} changed")
    for value_id, reviewed in reviewed_by_id.items():
        if value_id not in original_by_id and reviewed.get("review_status") != "HUMAN_ADDED":
            raise AcquisitionContextError(f"Value {value_id}: new row must be HUMAN_ADDED")
    return grouped


def write_context_json(
    toreview: Mapping[str, Any], review: Mapping[str, Any], output_path: str | Path
) -> Path:
    _verify_fingerprints(toreview)
    grouped = validate_approved_review(toreview, review)
    final = deepcopy(toreview)
    final["review_status"] = "APPROVED"
    final["reviewer"] = review["metadata"].get("Reviewer")
    final["reviewed_at"] = review["metadata"].get("Reviewed At")
    for event in final["round"]["events"]:
        for resource in event["resources"]:
            key = (event["event_id"], resource["resource_id"])
            values = []
            for value in grouped[key]:
                cleaned = {k: v for k, v in value.items() if k not in {"event_id", "resource_id"}}
                cleaned["effective_value"] = (
                    None if cleaned["review_status"] == "REJECTED" else cleaned["confirmed_value"]
                )
                values.append(cleaned)
            resource["values"] = values
    path = Path(output_path)
    _atomic_json_write(final, path)
    return path


def _default_output_dir(package: Path) -> Path:
    return ROOT / "output" / "acquisition_context" / package.name


def _load_toreview(path: Path) -> dict[str, Any]:
    value = _read_json(path)
    if value.get("schema_version") != CONTEXT_SCHEMA_VERSION:
        raise AcquisitionContextError("unsupported acquisition context schema_version")
    return value


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("package_dir", type=Path)
    prepare_parser.add_argument("--output-dir", type=Path)
    render_parser = subparsers.add_parser("render-review")
    render_parser.add_argument("toreview_json", type=Path)
    render_parser.add_argument("--output", type=Path)
    finalize_parser = subparsers.add_parser("finalize")
    finalize_parser.add_argument("toreview_json", type=Path)
    finalize_parser.add_argument("review_markdown", type=Path)
    finalize_parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            context = build_review_context(args.package_dir)
            output_dir = args.output_dir or _default_output_dir(args.package_dir.resolve())
            output = write_toreview_json(context, output_dir / "acquisition_context_toreview.json")
            event_count = len(context["round"]["events"])
            resource_count = sum(len(event["resources"]) for event in context["round"]["events"])
            print(f"{output} ({event_count} Events, {resource_count} Resources)")
        elif args.command == "render-review":
            context = _load_toreview(args.toreview_json)
            output = args.output or args.toreview_json.with_name("recog_values_review.md")
            render_review_markdown(context, output)
            value_count = sum(
                len(resource.get("values", []))
                for event in context["round"]["events"] for resource in event["resources"]
            )
            print(f"{output} ({value_count} Values)")
        else:
            context = _load_toreview(args.toreview_json)
            review = parse_review_markdown(args.review_markdown)
            output = args.output or args.toreview_json.with_name("acquisition_context.json")
            write_context_json(context, review, output)
            print(output)
    except AcquisitionContextError as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
