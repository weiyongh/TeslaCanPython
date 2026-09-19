"""Build a flat CSV inventory from DBC and compact JSON definitions.

The input/output contract is documented in:
~/Downloads/DBC_Atlas_Task1_CAN_Definition_Inventory_V0.1.md
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


CSV_FIELDS = [
	"dbc_source",
	"source_format",
	"vehicle_family",
	"bus_name",
	"message_id_dec",
	"message_id_hex",
	"message_name",
	"message_sender",
	"message_length",
	"message_cycle_time",
	"message_send_type",
	"signal_name",
	"signal_name_cn",
	"business_domain",
	"signal_role",
	"signal_receivers",
	"start_bit",
	"signal_length",
	"byte_order",
	"signedness",
	"factor",
	"offset",
	"minimum",
	"maximum",
	"unit",
	"enum_values",
	"is_multiplexed",
	"multiplexer_value",
	"comment",
]


def _text(value: Any) -> str:
	if value is None:
		return ""
	if isinstance(value, bool):
		return str(value).lower()
	return str(value)


def _join_values(values: Any) -> str:
	if values is None:
		return ""
	if isinstance(values, str):
		return values
	if isinstance(values, dict):
		return "|".join(
			f"{_text(key)}={_text(value)}" for key, value in sorted(values.items(), key=lambda item: str(item[0]))
		)
	if isinstance(values, (list, tuple, set)):
		return "|".join(_text(value) for value in values)
	return _text(values)


def _comment_text(comment: Any) -> str:
	if isinstance(comment, dict):
		return "|".join(f"{key}={value}" for key, value in sorted(comment.items()))
	return _text(comment)


def _vehicle_family(source: Path) -> str:
	for part in source.parts:
		if part in {"Model3", "ModelS", "ModelX", "ModelY"}:
			return part
	return ""


def _message_id(value: Any) -> int:
	if isinstance(value, str):
		return int(value, 0)
	return int(value)


def _base_record(source: Path, input_root: Path, source_format: str, bus_name: Any) -> dict[str, str]:
	return {
		"dbc_source": source.relative_to(input_root).as_posix(),
		"source_format": source_format,
		"vehicle_family": _vehicle_family(source.relative_to(input_root)),
		"bus_name": _text(bus_name),
		"signal_name_cn": "",
		"business_domain": "",
		"signal_role": "",
	}


def _dbc_records(source: Path, input_root: Path) -> list[dict[str, str]]:
	try:
		import cantools
	except ImportError as exc:
		raise RuntimeError("cantools is required to parse DBC files; install requirements.txt") from exc

	database_format = "dbc" if source.name.lower().endswith(".dbc.txt") else None
	database = cantools.database.load_file(str(source), database_format=database_format, strict=False)
	records: list[dict[str, str]] = []
	for message in database.messages:
		message_id = int(message.frame_id)
		senders = getattr(message, "senders", None) or []
		for signal in message.signals:
			choices = getattr(signal, "choices", None)
			multiplexer_value = getattr(signal, "multiplexer_ids", None)
			record = _base_record(source, input_root, "DBC", "")
			record.update(
				{
					"message_id_dec": _text(message_id),
					"message_id_hex": f"0x{message_id:X}",
					"message_name": _text(message.name),
					"message_sender": _join_values(senders),
					"message_length": _text(message.length),
					"message_cycle_time": _text(getattr(message, "cycle_time", None)),
					"message_send_type": _text(getattr(message, "send_type", None)),
					"signal_name": _text(signal.name),
					"signal_receivers": _join_values(getattr(signal, "receivers", None)),
					"start_bit": _text(signal.start),
					"signal_length": _text(signal.length),
					"byte_order": _text(getattr(signal, "byte_order", None)),
					"signedness": "signed" if signal.is_signed else "unsigned",
					"factor": _text(signal.scale),
					"offset": _text(signal.offset),
					"minimum": _text(signal.minimum),
					"maximum": _text(signal.maximum),
					"unit": _text(signal.unit),
					"enum_values": _join_values(choices),
					"is_multiplexed": _text(bool(getattr(signal, "is_multiplexer", False) or multiplexer_value)),
					"multiplexer_value": _join_values(multiplexer_value),
					"comment": _comment_text(getattr(signal, "comment", None)),
				}
			)
			records.append(record)
	return records


def _json_records(source: Path, input_root: Path) -> list[dict[str, str]] | None:
	try:
		payload = json.loads(source.read_text(encoding="utf-8"))
	except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
		raise RuntimeError(f"invalid JSON: {exc}") from exc

	if not isinstance(payload, dict) or not isinstance(payload.get("messages"), dict):
		return None

	messages = payload["messages"]
	if not messages or not any(isinstance(value, dict) and "signals" in value for value in messages.values()):
		return None

	bus_metadata = payload.get("busMetadata")
	bus_name = bus_metadata.get("name") if isinstance(bus_metadata, dict) else ""
	records: list[dict[str, str]] = []
	for message_name, message in messages.items():
		if not isinstance(message, dict) or not isinstance(message.get("signals"), dict):
			continue
		if "message_id" not in message:
			raise ValueError(f"message {message_name!r} has no message_id")
		message_id = _message_id(message["message_id"])
		senders = message.get("senders")
		if senders is None and message.get("originNode") is not None:
			senders = [message["originNode"]]
		for signal_name, signal in message["signals"].items():
			if not isinstance(signal, dict):
				raise ValueError(f"signal {message_name}.{signal_name} is not an object")
			multiplexer_value = signal.get("multiplexer_value", signal.get("multiplexer_ids"))
			record = _base_record(source, input_root, "JSON", bus_name)
			record.update(
				{
					"message_id_dec": _text(message_id),
					"message_id_hex": f"0x{message_id:X}",
					"message_name": _text(message_name),
					"message_sender": _join_values(senders),
					"message_length": _text(message.get("length_bytes")),
					"message_cycle_time": _text(message.get("cycle_time")),
					"message_send_type": _text(message.get("send_type", signal.get("send_type"))),
					"signal_name": _text(signal_name),
					"signal_receivers": _join_values(signal.get("receivers")),
					"start_bit": _text(signal.get("start_position")),
					"signal_length": _text(signal.get("width")),
					"byte_order": _text(signal.get("endianness")),
					"signedness": _text(signal.get("signedness")),
					"factor": _text(signal.get("scale")),
					"offset": _text(signal.get("offset")),
					"minimum": _text(signal.get("min")),
					"maximum": _text(signal.get("max")),
					"unit": _text(signal.get("units")),
					"enum_values": _join_values(signal.get("value_description")),
					"is_multiplexed": _text(multiplexer_value is not None or signal.get("multiplexer") is not None),
					"multiplexer_value": _join_values(multiplexer_value),
					"comment": _comment_text(signal.get("comment", message.get("comment"))),
				}
			)
			records.append(record)
	return records


def _candidate_files(input_root: Path) -> Iterable[Path]:
	for path in sorted(input_root.rglob("*")):
		if path.is_file() and (path.suffix.lower() in {".dbc", ".json"} or path.name.lower().endswith(".dbc.txt")):
			yield path


def _basename_duplicates(files: Iterable[Path], input_root: Path) -> dict[str, list[str]]:
	grouped: dict[str, list[str]] = defaultdict(list)
	for path in files:
		grouped[path.name].append(path.relative_to(input_root).as_posix())
	return {name: paths for name, paths in grouped.items() if len(paths) > 1}


def build_inventory(input_root: Path, output_dir: Path) -> tuple[int, dict[str, int]]:
	input_root = input_root.resolve()
	output_dir.mkdir(parents=True, exist_ok=True)
	files = list(_candidate_files(input_root))
	duplicates = _basename_duplicates(files, input_root)
	records: list[dict[str, str]] = []
	statuses: list[str] = []

	for source in files:
		relative = source.relative_to(input_root).as_posix()
		try:
			if source.suffix.lower() == ".json":
				parsed = _json_records(source, input_root)
				if parsed is None:
					statuses.append(f"SKIPPED\t{relative}\tnot a recognized CAN Definition JSON")
					continue
			else:
				parsed = _dbc_records(source, input_root)
			records.extend(parsed)
			statuses.append(f"PARSED\t{relative}\t{len(parsed)} signal rows")
		except Exception as exc:  # Keep one malformed source from stopping the inventory.
			statuses.append(f"FAILED\t{relative}\t{type(exc).__name__}: {exc}")

	records.sort(
		key=lambda record: (
			int(record["message_id_dec"]),
			record["dbc_source"],
			int(record["start_bit"]) if record["start_bit"].isdigit() else -1,
			record["signal_name"],
		)
	)
	inventory_path = output_dir / "dbc_inventory.csv"
	with inventory_path.open("w", encoding="utf-8", newline="") as handle:
		writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, lineterminator="\n")
		writer.writeheader()
		writer.writerows(records)

	log_path = output_dir / "dbc_inventory_errors.log"
	with log_path.open("w", encoding="utf-8", newline="") as handle:
		handle.write("DBC Inventory execution log\n")
		handle.write(f"input_root\t{input_root}\n")
		handle.write(f"scanned_files\t{len(files)}\n")
		for status in statuses:
			handle.write(status + "\n")
		if duplicates:
			handle.write("BASENAME_DUPLICATES\n")
			for name, paths in sorted(duplicates.items()):
				handle.write(f"{name}\t" + "\t".join(paths) + "\n")
		handle.write(f"signal_rows\t{len(records)}\n")

	counts = {
		"scanned": len(files),
		"parsed": sum(status.startswith("PARSED") for status in statuses),
		"skipped": sum(status.startswith("SKIPPED") for status in statuses),
		"failed": sum(status.startswith("FAILED") for status in statuses),
		"duplicate_groups": len(duplicates),
	}
	return len(records), counts


def main(argv: list[str] | None = None) -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--input-root", type=Path, default=Path(__file__).resolve().parents[1] / "dbc")
	parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1] / "output")
	args = parser.parse_args(argv)
	try:
		row_count, counts = build_inventory(args.input_root, args.output_dir)
	except (OSError, ValueError) as exc:
		print(f"error: {exc}", file=sys.stderr)
		return 1
	print(
		"scanned={scanned} parsed={parsed} skipped={skipped} failed={failed} "
		"basename_duplicate_groups={duplicate_groups} signal_rows={rows}".format(
			rows=row_count, **counts
		)
	)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())