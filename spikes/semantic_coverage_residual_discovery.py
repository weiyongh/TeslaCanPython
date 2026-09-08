"""Isolated semantic-coverage and residual-discovery spike.

This module intentionally does not participate in the approved Evidence Plan,
RVM, renderer, or report lifecycle.  It produces machine observations and
traceable discovery candidates for review before any formal evidence decision.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass, field
import hashlib
import json
import math
from pathlib import Path
import re
from statistics import median
from typing import Any, Iterable

import cantools


MAX_UNIQUE_VALUES = 256
MAX_SEQUENCE_VALUES = 512
MAX_RAW_REFS = 8
MAX_CANDIDATES_PER_TYPE = 25
MAX_CANDIDATES_TOTAL = 120
MAX_LLM_CANDIDATES = 40


@dataclass(frozen=True, order=True)
class BusKey:
    channel: str
    frame_format: str
    can_id: int

    def text(self) -> str:
        suffix = "x" if self.frame_format == "EXTENDED" else ""
        return f"ch{self.channel}:0x{self.can_id:X}{suffix}"


@dataclass(frozen=True)
class AscFrame:
    time_s: float
    bus_key: BusKey
    direction: str
    dlc: int
    data: bytes
    line_number: int

    def raw_ref(self) -> dict[str, Any]:
        return {
            "line_number": self.line_number,
            "time_s": round(self.time_s, 6),
            "bus_key": self.bus_key.text(),
            "dlc": self.dlc,
            "raw_hex": self.data.hex(" "),
        }


def parse_asc_line(line: str, line_number: int = 0) -> AscFrame | None:
    """Parse a classic Vector ASC data line while preserving bus identity."""
    parts = line.strip().split()
    if len(parts) < 7:
        return None
    try:
        time_s = float(parts[0])
    except ValueError:
        return None
    channel = parts[1]
    can_id_token = parts[2]
    is_extended = can_id_token.lower().endswith("x")
    if is_extended:
        can_id_token = can_id_token[:-1]
    try:
        can_id = int(can_id_token, 16)
    except ValueError:
        return None
    marker = next((index for index, token in enumerate(parts) if token.lower() == "d"), -1)
    if marker < 0 or marker + 1 >= len(parts):
        return None
    try:
        dlc = int(parts[marker + 1])
    except ValueError:
        return None
    raw_tokens = parts[marker + 2:marker + 2 + dlc]
    if len(raw_tokens) != dlc:
        return None
    try:
        data = bytes(int(token, 16) for token in raw_tokens)
    except (ValueError, OverflowError):
        return None
    direction = parts[3].upper() if len(parts) > 3 else "UNKNOWN"
    return AscFrame(
        time_s=time_s,
        bus_key=BusKey(channel, "EXTENDED" if is_extended else "STANDARD", can_id),
        direction=direction,
        dlc=dlc,
        data=data,
        line_number=line_number,
    )


def _add_bounded(target: list[Any], value: Any, limit: int) -> None:
    if len(target) < limit:
        target.append(value)


@dataclass
class RawVariantSummary:
    bus_key: BusKey
    dlc: int
    frame_count: int = 0
    first_time_s: float | None = None
    last_time_s: float | None = None
    directions: Counter = field(default_factory=Counter)
    payload_values: set[bytes] = field(default_factory=set)
    payload_cardinality_capped: bool = False
    byte_values: list[set[int]] = field(default_factory=list)
    bit_ones: list[int] = field(default_factory=list)
    bit_transitions: list[int] = field(default_factory=list)
    bit_transition_times: list[list[float]] = field(default_factory=list)
    previous: bytes | None = None
    raw_refs: list[dict[str, Any]] = field(default_factory=list)

    def add(self, frame: AscFrame) -> None:
        if not self.byte_values:
            self.byte_values = [set() for _ in range(self.dlc)]
            self.bit_ones = [0 for _ in range(self.dlc * 8)]
            self.bit_transitions = [0 for _ in range(self.dlc * 8)]
            self.bit_transition_times = [[] for _ in range(self.dlc * 8)]
        self.frame_count += 1
        self.first_time_s = frame.time_s if self.first_time_s is None else self.first_time_s
        self.last_time_s = frame.time_s
        self.directions[frame.direction] += 1
        if len(self.payload_values) < MAX_UNIQUE_VALUES:
            self.payload_values.add(frame.data)
        elif frame.data not in self.payload_values:
            self.payload_cardinality_capped = True
        for byte_index, byte in enumerate(frame.data):
            if len(self.byte_values[byte_index]) < MAX_UNIQUE_VALUES:
                self.byte_values[byte_index].add(byte)
            for bit in range(8):
                absolute = byte_index * 8 + bit
                self.bit_ones[absolute] += (byte >> bit) & 1
        if self.previous is not None:
            for byte_index, (old, new) in enumerate(zip(self.previous, frame.data)):
                changed = old ^ new
                for bit in range(8):
                    if changed & (1 << bit):
                        absolute = byte_index * 8 + bit
                        self.bit_transitions[absolute] += 1
                        _add_bounded(self.bit_transition_times[absolute], frame.time_s, 64)
        if not self.raw_refs:
            self.raw_refs.append(frame.raw_ref())
        elif self.previous != frame.data and len(self.raw_refs) < MAX_RAW_REFS - 1:
            self.raw_refs.append(frame.raw_ref())
        self.previous = frame.data

    def finish(self, last_ref: dict[str, Any] | None) -> dict[str, Any]:
        refs = list(self.raw_refs)
        if last_ref and (not refs or refs[-1]["line_number"] != last_ref["line_number"]):
            refs.append(last_ref)
        changing_bits = [index for index, count in enumerate(self.bit_transitions) if count]
        return {
            "bus_key": self.bus_key.text(),
            "channel": self.bus_key.channel,
            "frame_format": self.bus_key.frame_format,
            "can_id": f"0x{self.bus_key.can_id:X}",
            "dlc": self.dlc,
            "frame_count": self.frame_count,
            "first_time_s": self.first_time_s,
            "last_time_s": self.last_time_s,
            "directions": dict(self.directions),
            "payload_cardinality": (
                f">={MAX_UNIQUE_VALUES}" if self.payload_cardinality_capped else len(self.payload_values)
            ),
            "byte_cardinality": [len(values) for values in self.byte_values],
            "changing_bits": changing_bits,
            "bit_ones": self.bit_ones,
            "bit_transitions": self.bit_transitions,
            "bit_transition_times": self.bit_transition_times,
            "raw_refs": refs,
        }


@dataclass
class SignalAccumulator:
    signal_key: str
    signal_name: str
    message_name: str
    bus_key: BusKey
    dbc_source: str
    definition_fingerprint: str
    unit: str
    enum_definition: dict[str, str]
    mux_context: str
    minimum_defined: float | None
    maximum_defined: float | None
    sample_count: int = 0
    numeric_count: int = 0
    invalid_count: int = 0
    sna_count: int = 0
    out_of_range_count: int = 0
    first_time_s: float | None = None
    last_time_s: float | None = None
    minimum: float | None = None
    maximum: float | None = None
    numeric_sum: float = 0.0
    numeric_sum_sq: float = 0.0
    unique_values: set[str] = field(default_factory=set)
    cardinality_capped: bool = False
    value_counts: Counter | None = field(default_factory=Counter)
    previous_value: str | None = None
    change_count: int = 0
    first_change_time_s: float | None = None
    last_change_time_s: float | None = None
    transition_times: list[float] = field(default_factory=list)
    sequence: list[str] = field(default_factory=list)
    raw_refs: list[dict[str, Any]] = field(default_factory=list)
    min_ref: dict[str, Any] | None = None
    max_ref: dict[str, Any] | None = None
    last_ref: dict[str, Any] | None = None

    def add(self, value: Any, frame: AscFrame) -> None:
        display = str(value)
        self.sample_count += 1
        self.first_time_s = frame.time_s if self.first_time_s is None else self.first_time_s
        self.last_time_s = frame.time_s
        self.last_ref = frame.raw_ref()
        upper = display.upper()
        if any(marker in upper for marker in ("SNA", "INVALID", "UNKNOWN", "NOT_AVAILABLE")):
            self.sna_count += 1
        if isinstance(value, (int, float)) and math.isfinite(float(value)):
            numeric = float(value)
            self.numeric_count += 1
            self.numeric_sum += numeric
            self.numeric_sum_sq += numeric * numeric
            if self.minimum is None or numeric < self.minimum:
                self.minimum, self.min_ref = numeric, frame.raw_ref()
            if self.maximum is None or numeric > self.maximum:
                self.maximum, self.max_ref = numeric, frame.raw_ref()
            if self.minimum_defined is not None and numeric < self.minimum_defined - 1e-12:
                self.out_of_range_count += 1
            if self.maximum_defined is not None and numeric > self.maximum_defined + 1e-12:
                self.out_of_range_count += 1
        if len(self.unique_values) < MAX_UNIQUE_VALUES:
            self.unique_values.add(display)
        elif display not in self.unique_values:
            self.cardinality_capped = True
            self.value_counts = None
        if self.value_counts is not None:
            self.value_counts[display] += 1
        if self.previous_value is not None and display != self.previous_value:
            self.change_count += 1
            self.first_change_time_s = frame.time_s if self.first_change_time_s is None else self.first_change_time_s
            self.last_change_time_s = frame.time_s
            _add_bounded(self.transition_times, frame.time_s, MAX_SEQUENCE_VALUES)
            _add_bounded(self.raw_refs, frame.raw_ref(), MAX_RAW_REFS)
        if not self.sequence or self.sequence[-1] != display:
            _add_bounded(self.sequence, display, MAX_SEQUENCE_VALUES)
        if not self.raw_refs:
            self.raw_refs.append(frame.raw_ref())
        self.previous_value = display

    def finish(self) -> dict[str, Any]:
        cardinality: int | str = len(self.unique_values)
        if self.cardinality_capped:
            cardinality = f">={MAX_UNIQUE_VALUES}"
        dominant = None
        if self.value_counts and self.sample_count:
            dominant = max(self.value_counts.values()) / self.sample_count
        mean = self.numeric_sum / self.numeric_count if self.numeric_count else None
        standard_deviation = None
        if self.numeric_count:
            variance = max(0.0, self.numeric_sum_sq / self.numeric_count - mean * mean)
            standard_deviation = math.sqrt(variance)
        stability = "NON_NUMERIC"
        if self.numeric_count:
            if len(self.unique_values) == 1:
                stability = "CONSTANT"
            elif len(self.unique_values) <= 8 and not self.cardinality_capped:
                stability = "LOW_CARDINALITY"
            elif self.minimum is not None and self.maximum is not None:
                scale = max(abs(mean or 0.0), 1.0)
                stability = "NEAR_CONSTANT" if self.maximum - self.minimum <= 0.001 * scale else "DYNAMIC"
        elif len(self.unique_values) <= 8:
            stability = "LOW_CARDINALITY"
        refs = []
        seen = set()
        for ref in [*self.raw_refs, self.min_ref, self.max_ref, self.last_ref]:
            if ref and ref["line_number"] not in seen:
                refs.append(ref)
                seen.add(ref["line_number"])
        return {
            "signal_key": self.signal_key,
            "signal_name": self.signal_name,
            "message_name": self.message_name,
            "bus_key": self.bus_key.text(),
            "channel": self.bus_key.channel,
            "can_id": f"0x{self.bus_key.can_id:X}",
            "frame_format": self.bus_key.frame_format,
            "dbc_source": self.dbc_source,
            "definition_fingerprint": self.definition_fingerprint,
            "unit": self.unit,
            "enum_definition": self.enum_definition,
            "mux_context": self.mux_context,
            "sample_count": self.sample_count,
            "numeric_count": self.numeric_count,
            "invalid_count": self.invalid_count,
            "first_time_s": self.first_time_s,
            "last_time_s": self.last_time_s,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "mean": mean,
            "standard_deviation": standard_deviation,
            "cardinality": cardinality,
            "dominant_value_ratio": dominant,
            "change_count": self.change_count,
            "first_change_time_s": self.first_change_time_s,
            "last_change_time_s": self.last_change_time_s,
            "current_value": self.previous_value,
            "transition_times": self.transition_times,
            "sequence": self.sequence,
            "stability_class": stability,
            "sna_count": self.sna_count,
            "out_of_dbc_range_count": self.out_of_range_count,
            "dbc_minimum": self.minimum_defined,
            "dbc_maximum": self.maximum_defined,
            "raw_refs": refs,
        }


def signal_bit_indices(signal: Any) -> set[int]:
    """Return payload bit indices using DBC little-bit numbering."""
    bits = set()
    current = int(signal.start)
    for _ in range(int(signal.length)):
        bits.add(current)
        if signal.byte_order == "little_endian":
            current += 1
        else:
            current = current + 15 if current % 8 == 0 else current - 1
    return bits


def signal_fingerprint(signal: Any) -> str:
    value = {
        "start": signal.start,
        "length": signal.length,
        "byte_order": signal.byte_order,
        "signed": signal.is_signed,
        "scale": signal.scale,
        "offset": signal.offset,
        "unit": signal.unit,
        "is_multiplexer": signal.is_multiplexer,
        "multiplexer_signal": signal.multiplexer_signal,
        "multiplexer_ids": signal.multiplexer_ids,
    }
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def message_fingerprint(message: Any) -> str:
    rows = [(signal.name, signal_fingerprint(signal)) for signal in message.signals]
    raw = json.dumps([message.length, rows], sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _choices(signal: Any) -> dict[str, str]:
    return {str(key): str(value) for key, value in (signal.choices or {}).items()}


def _mux_context(signal: Any) -> str:
    if signal.is_multiplexer:
        return "SELECTOR"
    if signal.multiplexer_signal:
        ids = "/".join(str(value) for value in signal.multiplexer_ids or ())
        return f"{signal.multiplexer_signal}={ids}"
    return "NONE"


def _message_min_max_pairs(message: Any) -> list[tuple[str, str]]:
    names = {signal.name for signal in message.signals}
    pairs = set()
    for name in names:
        replacements = []
        if name.endswith("Min"):
            replacements.append(name[:-3] + "Max")
        if name.endswith("_min"):
            replacements.append(name[:-4] + "_max")
        if "Minimum" in name:
            replacements.append(name.replace("Minimum", "Maximum"))
        for maximum in replacements:
            if maximum in names:
                pairs.add((name, maximum))
    return sorted(pairs)


def _candidate(candidate_type: str, source_space: str, target: Any, bus_key: str | None,
               observed_summary: str, metrics: dict[str, Any], raw_refs: list[dict[str, Any]],
               *, score: float, quality_flags: Iterable[str] = (),
               related: Iterable[str] = ()) -> dict[str, Any]:
    return {
        "candidate_id": "",
        "discovery_mode": "STATIC",
        "source_space": source_space,
        "candidate_type": candidate_type,
        "bus_key": bus_key,
        "dlc_scope": sorted({ref["dlc"] for ref in raw_refs}),
        "target": target,
        "dbc_coverage": None,
        "time_scope": {
            "start_s": min((ref["time_s"] for ref in raw_refs), default=None),
            "end_s": max((ref["time_s"] for ref in raw_refs), default=None),
        },
        "event_ref": None,
        "pattern_type": candidate_type,
        "observed_summary": observed_summary,
        "metrics": metrics,
        "related_observation_refs": list(related),
        "raw_refs": raw_refs[:MAX_RAW_REFS],
        "quality_flags": sorted(set(quality_flags)),
        "ranking_score": round(float(score), 3),
    }


def _periodicity(times: list[float]) -> dict[str, Any] | None:
    if len(times) < 5:
        return None
    gaps = [right - left for left, right in zip(times, times[1:]) if right > left]
    if len(gaps) < 4:
        return None
    center = median(gaps)
    if center <= 0:
        return None
    mean_gap = sum(gaps) / len(gaps)
    cv = math.sqrt(sum((gap - mean_gap) ** 2 for gap in gaps) / len(gaps)) / mean_gap
    return {"median_interval_s": center, "interval_cv": cv, "observed_intervals": len(gaps)}


def _family_key(name: str) -> tuple[str, int] | None:
    match = re.match(r"^(.*?)(\d+)$", name)
    return (match.group(1), int(match.group(2))) if match else None


def _compress_candidates(candidates: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    unique = {}
    for item in candidates:
        signature = json.dumps(
            [item["candidate_type"], item["bus_key"], item["target"], item["observed_summary"]],
            sort_keys=True, ensure_ascii=False, default=str,
        )
        existing = unique.get(signature)
        if existing is None or item["ranking_score"] > existing["ranking_score"]:
            unique[signature] = item
    grouped = defaultdict(list)
    for item in unique.values():
        grouped[item["candidate_type"]].append(item)
    kept = []
    discarded = {}
    for candidate_type, rows in grouped.items():
        rows.sort(key=lambda item: (-item["ranking_score"], str(item["target"])))
        kept.extend(rows[:MAX_CANDIDATES_PER_TYPE])
        discarded[candidate_type] = max(0, len(rows) - MAX_CANDIDATES_PER_TYPE)
    kept.sort(key=lambda item: (-item["ranking_score"], item["candidate_type"], str(item["target"])))
    if len(kept) > MAX_CANDIDATES_TOTAL:
        discarded["TOTAL_LIMIT"] = len(kept) - MAX_CANDIDATES_TOTAL
        kept = _balanced_candidate_selection(kept, MAX_CANDIDATES_TOTAL)
        kept.sort(key=lambda item: (-item["ranking_score"], item["candidate_type"], str(item["target"])))
    for index, item in enumerate(kept, 1):
        item["candidate_id"] = f"C{index:04d}"
    return kept, discarded


def _balanced_candidate_selection(candidates: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    """Keep high-ranked examples without allowing one candidate class to consume the package."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        grouped[candidate["candidate_type"]].append(candidate)
    for rows in grouped.values():
        rows.sort(key=lambda item: (-item["ranking_score"], str(item["target"])))
    ordered_types = sorted(
        grouped,
        key=lambda kind: (-grouped[kind][0]["ranking_score"], kind),
    )
    selected: list[dict[str, Any]] = []
    depth = 0
    while len(selected) < limit:
        added = False
        for candidate_type in ordered_types:
            rows = grouped[candidate_type]
            if depth < len(rows):
                selected.append(rows[depth])
                added = True
                if len(selected) == limit:
                    break
        if not added:
            break
        depth += 1
    return selected


def run_spike(asc_path: Path, dbc_paths: list[Path], *, domain: str,
              conditions: list[str], windows: list[dict[str, Any]]) -> dict[str, Any]:
    databases = [(path, cantools.database.load_file(path, strict=False)) for path in dbc_paths]
    definitions: dict[tuple[str, int], list[tuple[Path, Any]]] = defaultdict(list)
    for path, database in databases:
        for message in database.messages:
            key = ("EXTENDED" if message.is_extended_frame else "STANDARD", message.frame_id)
            definitions[key].append((path, message))

    raw_variants: dict[tuple[BusKey, int], RawVariantSummary] = {}
    last_raw_refs: dict[tuple[BusKey, int], dict[str, Any]] = {}
    signal_accumulators: dict[str, SignalAccumulator] = {}
    decode_stats: dict[tuple[BusKey, int, str], Counter] = defaultdict(Counter)
    covered_bits: dict[tuple[BusKey, int, str], set[int]] = defaultdict(set)
    min_max_checks: dict[tuple[str, str, str], dict[str, Any]] = defaultdict(
        lambda: {"comparisons": 0, "violations": 0, "raw_refs": []}
    )
    parsed_frames = 0
    malformed_lines = 0
    first_time = last_time = None
    digest = hashlib.sha256()
    with asc_path.open("rb") as binary:
        for chunk in iter(lambda: binary.read(1024 * 1024), b""):
            digest.update(chunk)
    with asc_path.open(encoding="utf-8", errors="replace") as source:
        for line_number, line in enumerate(source, 1):
            frame = parse_asc_line(line, line_number)
            if frame is None:
                if line.strip() and line.lstrip()[:1].isdigit():
                    malformed_lines += 1
                continue
            parsed_frames += 1
            first_time = frame.time_s if first_time is None else min(first_time, frame.time_s)
            last_time = frame.time_s if last_time is None else max(last_time, frame.time_s)
            variant_key = (frame.bus_key, frame.dlc)
            raw = raw_variants.setdefault(
                variant_key, RawVariantSummary(frame.bus_key, frame.dlc)
            )
            raw.add(frame)
            last_raw_refs[variant_key] = frame.raw_ref()
            frame_definitions = definitions.get((frame.bus_key.frame_format, frame.bus_key.can_id), [])
            for dbc_path, message in frame_definitions:
                source_key = str(dbc_path)
                stat_key = (frame.bus_key, frame.dlc, source_key)
                decode_stats[stat_key]["attempted"] += 1
                try:
                    decoded = message.decode(
                        frame.data, decode_choices=True, scaling=True, allow_truncated=True
                    )
                except Exception:
                    decode_stats[stat_key]["failed"] += 1
                    continue
                decode_stats[stat_key]["succeeded"] += 1
                by_name = {signal.name: signal for signal in message.signals}
                for signal_name, value in decoded.items():
                    signal = by_name.get(signal_name)
                    if signal is None:
                        continue
                    covered_bits[stat_key].update(
                        bit for bit in signal_bit_indices(signal) if bit < frame.dlc * 8
                    )
                    key = f"{source_key}|{frame.bus_key.text()}|{signal_name}"
                    accumulator = signal_accumulators.get(key)
                    if accumulator is None:
                        accumulator = SignalAccumulator(
                            signal_key=key,
                            signal_name=signal_name,
                            message_name=message.name,
                            bus_key=frame.bus_key,
                            dbc_source=source_key,
                            definition_fingerprint=signal_fingerprint(signal),
                            unit=signal.unit or "",
                            enum_definition=_choices(signal),
                            mux_context=_mux_context(signal),
                            minimum_defined=signal.minimum,
                            maximum_defined=signal.maximum,
                        )
                        signal_accumulators[key] = accumulator
                    accumulator.add(value, frame)
                for minimum_name, maximum_name in _message_min_max_pairs(message):
                    minimum_value, maximum_value = decoded.get(minimum_name), decoded.get(maximum_name)
                    if not isinstance(minimum_value, (int, float)) or not isinstance(maximum_value, (int, float)):
                        continue
                    check_key = (source_key, minimum_name, maximum_name)
                    check = min_max_checks[check_key]
                    check["comparisons"] += 1
                    if float(maximum_value) < float(minimum_value):
                        check["violations"] += 1
                        _add_bounded(check["raw_refs"], frame.raw_ref(), MAX_RAW_REFS)

    raw_summaries = [
        raw.finish(last_raw_refs.get(key)) for key, raw in sorted(raw_variants.items())
    ]
    raw_by_variant = {(row["bus_key"], row["dlc"]): row for row in raw_summaries}
    coverage_rows = []
    coverage_lookup = {}
    for (bus_key, dlc), raw in sorted(raw_variants.items()):
        matches = definitions.get((bus_key.frame_format, bus_key.can_id), [])
        reasons = []
        residual = set(index for index, count in enumerate(raw.bit_transitions) if count)
        source_details = []
        fingerprints = set()
        if not matches:
            coverage_class = "UNMATCHED"
            semantic_status = "UNVALIDATED"
            reasons.append("NO_DBC_MESSAGE_FOR_BUS_KEY")
        else:
            for dbc_path, message in matches:
                source_key = str(dbc_path)
                stats = decode_stats[(bus_key, dlc, source_key)]
                bits = covered_bits[(bus_key, dlc, source_key)]
                residual -= bits
                fingerprint = message_fingerprint(message)
                fingerprints.add(fingerprint)
                source_details.append({
                    "dbc_source": source_key,
                    "message_name": message.name,
                    "message_dlc": message.length,
                    "definition_fingerprint": fingerprint,
                    "attempted": stats["attempted"],
                    "succeeded": stats["succeeded"],
                    "failed": stats["failed"],
                    "covered_bits_observed": sorted(bits),
                })
            succeeded = sum(item["succeeded"] for item in source_details)
            failed = sum(item["failed"] for item in source_details)
            if succeeded == 0:
                coverage_class = "INVALID"
                semantic_status = "VALIDATION_REQUIRED"
                reasons.append("NO_DEFINITION_DECODED_OBSERVED_DLC")
            elif len(fingerprints) > 1:
                coverage_class = "CONFLICTED"
                semantic_status = "VALIDATION_REQUIRED"
                reasons.append("MULTIPLE_INCOMPATIBLE_MESSAGE_DEFINITIONS")
            elif failed or residual or any(item["message_dlc"] != dlc for item in source_details):
                coverage_class = "PARTIAL"
                semantic_status = "UNVALIDATED"
                if failed:
                    reasons.append("SOME_DECODE_FAILURES")
                if residual:
                    reasons.append("CHANGING_RESIDUAL_BITS")
                if any(item["message_dlc"] != dlc for item in source_details):
                    reasons.append("OBSERVED_DLC_DIFFERS_FROM_DBC_MESSAGE_DLC")
            else:
                coverage_class = "MATCHED"
                semantic_status = "UNVALIDATED"
        row = {
            "bus_key": bus_key.text(),
            "channel": bus_key.channel,
            "frame_format": bus_key.frame_format,
            "can_id": f"0x{bus_key.can_id:X}",
            "observed_dlc": dlc,
            "frame_count": raw.frame_count,
            "coverage_class": coverage_class,
            "semantic_status": semantic_status,
            "coverage_reasons": reasons,
            "residual_changing_bits": sorted(residual),
            "definition_sources": source_details,
        }
        coverage_rows.append(row)
        coverage_lookup[(bus_key.text(), dlc)] = row

    signal_summaries = [acc.finish() for acc in signal_accumulators.values()]
    signal_summaries.sort(key=lambda row: (row["signal_name"], row["bus_key"], row["dbc_source"]))
    summaries_by_message = defaultdict(list)
    for summary in signal_summaries:
        summaries_by_message[(summary["dbc_source"], summary["bus_key"], summary["message_name"])].append(summary)
    candidates = []
    for summary in signal_summaries:
        refs = summary["raw_refs"]
        if summary["sna_count"] or summary["out_of_dbc_range_count"]:
            candidates.append(_candidate(
                "INVALID_OR_OUT_OF_RANGE", "KNOWN", summary["signal_name"], summary["bus_key"],
                f"{summary['signal_name']}包含SNA/INVALID或超出DBC范围的观测。",
                {"sna_count": summary["sna_count"], "out_of_dbc_range_count": summary["out_of_dbc_range_count"]},
                refs, score=88, quality_flags=("DBC_SEMANTIC_VALIDATION_REQUIRED",),
                related=(summary["signal_key"],),
            ))
        if summary["numeric_count"] and summary["stability_class"] == "CONSTANT":
            value = summary["minimum"]
            at_boundary = (
                value == 0
                or (summary["dbc_minimum"] is not None and abs(value - summary["dbc_minimum"]) < 1e-12)
                or (summary["dbc_maximum"] is not None and abs(value - summary["dbc_maximum"]) < 1e-12)
            )
            if at_boundary and summary["unit"]:
                candidates.append(_candidate(
                    "FIXED_BOUNDARY_VALUE", "KNOWN", summary["signal_name"], summary["bus_key"],
                    f"{summary['signal_name']}在全部{summary['sample_count']}个样本中固定为{value} {summary['unit']}。",
                    {"value": value, "sample_count": summary["sample_count"], "unit": summary["unit"]},
                    refs, score=55, quality_flags=("PLACEHOLDER_OR_REAL_STATE_UNRESOLVED",),
                    related=(summary["signal_key"],),
                ))
                context = []
                context_refs = list(refs)
                related = [summary["signal_key"]]
                peers = summaries_by_message[(summary["dbc_source"], summary["bus_key"], summary["message_name"])]
                for peer in peers:
                    if peer["signal_key"] == summary["signal_key"] or peer["sample_count"] == 0:
                        continue
                    peer_cardinality = peer["cardinality"] if isinstance(peer["cardinality"], int) else MAX_UNIQUE_VALUES
                    if peer_cardinality > 8:
                        continue
                    context.append({
                        "signal": peer["signal_name"],
                        "unit": peer["unit"],
                        "stability_class": peer["stability_class"],
                        "minimum": peer["minimum"],
                        "maximum": peer["maximum"],
                        "sequence": peer["sequence"][:8],
                    })
                    related.append(peer["signal_key"])
                    context_refs.extend(peer["raw_refs"][:1])
                if context:
                    candidates.append(_candidate(
                        "FIXED_PHYSICAL_BOUNDARY_CONTEXT", "KNOWN", summary["signal_name"], summary["bus_key"],
                        f"{summary['signal_name']}固定在物理量边界值；同一DBC报文存在可供语义核对的低离散度状态上下文。",
                        {
                            "boundary_value": value,
                            "unit": summary["unit"],
                            "same_message_context": context[:12],
                        },
                        context_refs[:MAX_RAW_REFS], score=91,
                        quality_flags=("PHYSICAL_BOUNDARY_REQUIRES_CONTEXTUAL_SIGNAL_VALIDATION",),
                        related=related[:16],
                    ))
        cardinality = summary["cardinality"] if isinstance(summary["cardinality"], int) else MAX_UNIQUE_VALUES
        periodic = _periodicity(summary["transition_times"])
        if periodic and cardinality <= 8 and periodic["interval_cv"] <= 0.12:
            alert_like = bool(re.search(
                r"(?:watchdog|fault|error|warning|warn|alarm|alert|invalid|failure)",
                summary["signal_name"], re.IGNORECASE,
            ))
            candidates.append(_candidate(
                "PERIODIC_ALERT_LIKE" if alert_like else "PERIODIC_LOW_CARDINALITY",
                "KNOWN", summary["signal_name"], summary["bus_key"],
                f"{summary['signal_name']}以低离散度、近固定周期反复切换。",
                {**periodic, "cardinality": cardinality, "sequence": summary["sequence"][:16]},
                refs, score=(92 if alert_like else 80) - periodic["interval_cv"] * 20,
                quality_flags=(("ALERT_LABEL_PERIODIC_SEMANTIC_CONFLICT",) if alert_like else
                               ("PAGING_COUNTER_OR_REAL_STATE_UNRESOLVED",)),
                related=(summary["signal_key"],),
            ))

    for (source_key, minimum_name, maximum_name), check in min_max_checks.items():
        if check["violations"]:
            related = [
                row["signal_key"] for row in signal_summaries
                if row["dbc_source"] == source_key and row["signal_name"] in {minimum_name, maximum_name}
            ]
            bus_key = next((row["bus_key"] for row in signal_summaries if row["signal_key"] in related), None)
            candidates.append(_candidate(
                "MIN_MAX_ORDER_VIOLATION", "KNOWN", [minimum_name, maximum_name], bus_key,
                f"{maximum_name}在同帧比较中低于{minimum_name}。",
                {"comparisons": check["comparisons"], "violations": check["violations"]},
                check["raw_refs"], score=98, quality_flags=("PHYSICAL_OR_DBC_SEMANTIC_CONFLICT",),
                related=related,
            ))

    families = defaultdict(list)
    for summary in signal_summaries:
        family = _family_key(summary["signal_name"])
        if family and summary["numeric_count"]:
            families[(family[0], summary["unit"], summary["dbc_source"])].append((family[1], summary))
    for (prefix, unit, source_key), members in families.items():
        if len(members) < 4:
            continue
        members.sort(key=lambda item: item[0])
        means = [item[1]["mean"] for item in members if item[1]["mean"] is not None]
        if not means:
            continue
        center = median(means)
        deviations = [abs(value - center) for value in means]
        mad = median(deviations)
        threshold = max(mad * 10, abs(center) * 0.2, 1e-9)
        outliers = [
            {"signal": summary["signal_name"], "mean": summary["mean"]}
            for _, summary in members if abs(summary["mean"] - center) > threshold
        ]
        family_refs = [ref for _, row in members for ref in row["raw_refs"][:1]][:MAX_RAW_REFS]
        related = [row["signal_key"] for _, row in members]
        if outliers:
            candidates.append(_candidate(
                "SIGNAL_FAMILY_OUTLIER", "KNOWN", prefix + "*", None,
                f"编号Signal族{prefix}*共{len(members)}项，其中{len(outliers)}项显著偏离族中位数。",
                {"member_count": len(members), "family_median": center, "mad": mad, "outliers": outliers},
                family_refs, score=94, quality_flags=("PLACEHOLDER_OR_INVALID_CHANNEL_CANDIDATE",),
                related=related,
            ))
        positive = [value for value in means if value > 0]
        if len(positive) >= 4 and unit:
            family_sum = sum(positive)
            totals = []
            prefix_tokens = set(re.findall(r"[A-Za-z]+", prefix.lower()))
            for other in signal_summaries:
                if other["dbc_source"] != source_key or other["unit"] != unit or other["mean"] is None:
                    continue
                if other["signal_key"] in related:
                    continue
                name_tokens = set(re.findall(r"[A-Za-z]+", other["signal_name"].lower()))
                if name_tokens & prefix_tokens or any(token in other["signal_name"].lower() for token in ("pack", "total")):
                    delta = abs(other["mean"] - family_sum)
                    totals.append({
                        "signal": other["signal_name"], "mean": other["mean"],
                        "absolute_difference": delta,
                        "relative_difference": delta / abs(other["mean"]) if other["mean"] else None,
                    })
            totals.sort(key=lambda item: item["absolute_difference"])
            if totals:
                closest = totals[0]
                score = 90 if closest["relative_difference"] is not None and closest["relative_difference"] <= 0.05 else 65
                candidates.append(_candidate(
                    "SIGNAL_FAMILY_SUM_VS_TOTAL", "KNOWN", prefix + "*", None,
                    f"{len(positive)}项正值族成员均值之和为{family_sum:.6g} {unit}；存在同单位总量候选。",
                    {"family_sum": family_sum, "positive_members": len(positive), "closest_totals": totals[:5]},
                    family_refs, score=score, quality_flags=("STRUCTURAL_RELATION_REQUIRES_SEMANTIC_REVIEW",),
                    related=[*related, *[row["signal"] for row in totals[:5]]],
                ))

    for row in raw_summaries:
        coverage = coverage_lookup[(row["bus_key"], row["dlc"])]
        residual_bits = coverage["residual_changing_bits"]
        if residual_bits:
            refs = row["raw_refs"]
            candidates.append(_candidate(
                "RESIDUAL_BIT_ACTIVITY", "RESIDUAL", residual_bits, row["bus_key"],
                f"{row['bus_key']} DLC {row['dlc']}存在{len(residual_bits)}个发生变化但未被当前DBC解释的bit。",
                {"residual_bits": residual_bits, "frame_count": row["frame_count"]}, refs,
                score=72 + min(15, len(residual_bits)), quality_flags=("RAW_SEMANTICS_UNKNOWN",),
            ))
        if coverage["coverage_class"] == "UNMATCHED":
            payload_cardinality = row["payload_cardinality"]
            if isinstance(payload_cardinality, int) and payload_cardinality <= 8:
                candidates.append(_candidate(
                    "UNKNOWN_LOW_CARDINALITY_PAYLOAD", "UNKNOWN", "payload", row["bus_key"],
                    f"未匹配报文{row['bus_key']}仅观察到{payload_cardinality}种payload。",
                    {"payload_cardinality": payload_cardinality, "frame_count": row["frame_count"]},
                    row["raw_refs"], score=58, quality_flags=("RAW_SEMANTICS_UNKNOWN",),
                ))
            for bit, times in enumerate(row["bit_transition_times"]):
                periodic = _periodicity(times)
                if periodic and periodic["interval_cv"] <= 0.12:
                    candidates.append(_candidate(
                        "UNKNOWN_PERIODIC_BIT", "UNKNOWN", f"bit{bit}", row["bus_key"],
                        f"未匹配报文{row['bus_key']}的bit{bit}近固定周期切换。",
                        periodic, row["raw_refs"], score=70 - periodic["interval_cv"] * 10,
                        quality_flags=("COUNTER_HEARTBEAT_OR_PAGING_CANDIDATE",),
                    ))

    candidates, discarded = _compress_candidates(candidates)
    for candidate in candidates:
        if candidate["bus_key"] is not None:
            matching = [
                row for row in coverage_rows if row["bus_key"] == candidate["bus_key"]
                and (not candidate["dlc_scope"] or row["observed_dlc"] in candidate["dlc_scope"])
            ]
            candidate["dbc_coverage"] = sorted({row["coverage_class"] for row in matching})

    llm_candidates = _balanced_candidate_selection(candidates, MAX_LLM_CANDIDATES)
    llm_candidates.sort(key=lambda item: (-item["ranking_score"], item["candidate_type"], str(item["target"])))
    candidate_signal_keys = {
        reference for item in llm_candidates
        for reference in item["related_observation_refs"] if "|" in reference
    }
    selected_summaries = [row for row in signal_summaries if row["signal_key"] in candidate_signal_keys]
    stable_context = [
        row for row in signal_summaries
        if row["stability_class"] in {"CONSTANT", "NEAR_CONSTANT"} and row["unit"]
        and row["signal_key"] not in candidate_signal_keys
    ]
    stable_context.sort(key=lambda row: (-row["sample_count"], row["signal_name"]))
    selected_summaries.extend(stable_context[:30])

    def public_signal_summary(row: dict[str, Any]) -> dict[str, Any]:
        result = dict(row)
        result.pop("transition_times", None)
        result["sequence"] = result["sequence"][:16]
        return result

    public_raw_summaries = []
    for row in raw_summaries:
        public_row = dict(row)
        public_row.pop("bit_transition_times", None)
        public_raw_summaries.append(public_row)
    public_signal_summaries = [public_signal_summary(row) for row in signal_summaries]
    selected_summaries = [public_signal_summary(row) for row in selected_summaries[:80]]

    coverage_counts = Counter(row["coverage_class"] for row in coverage_rows)
    return {
        "schema_version": "semantic-coverage-residual-discovery-spike-v1",
        "run_metadata": {
            "mode": "STATIC",
            "formal_evidence": False,
            "asc_path": str(asc_path),
            "dbc_paths": [str(path) for path in dbc_paths],
            "domain": domain,
            "conditions": conditions,
            "static_observation_windows": windows,
            "historical_report_used_as_input": False,
        },
        "asc_integrity": {
            "sha256": digest.hexdigest(),
            "size_bytes": asc_path.stat().st_size,
            "parsed_frame_count": parsed_frames,
            "malformed_candidate_lines": malformed_lines,
            "first_time_s": first_time,
            "last_time_s": last_time,
        },
        "bus_inventory": public_raw_summaries,
        "dbc_coverage": coverage_rows,
        "coverage_summary": dict(coverage_counts),
        "signal_summaries": public_signal_summaries,
        "static_consistency_results": [
            item for item in candidates if item["source_space"] == "KNOWN"
        ],
        "residual_summaries": [
            item for item in candidates if item["source_space"] in {"RESIDUAL", "UNKNOWN"}
        ],
        "candidates": candidates,
        "candidate_compression": {
            "kept": len(candidates),
            "discarded_by_limit": discarded,
            "llm_candidate_limit": MAX_LLM_CANDIDATES,
        },
        "llm_package": {
            "domain": domain,
            "conditions": conditions,
            "discovery_mode": "STATIC",
            "event_anchors": [],
            "time_discipline": "Static observation windows are not vehicle events.",
            "coverage_summary": dict(coverage_counts),
            "candidates": llm_candidates,
            "supporting_signal_summaries": selected_summaries,
            "semantic_rules": [
                "DBC matched does not mean semantic validity is confirmed.",
                "Describe observations separately from interpretations.",
                "Correlation, proximity, or consistency does not by itself establish causality.",
                "Physical or semantic conflicts require Signal Validation before formal use.",
            ],
        },
    }


def _parse_window(value: str) -> dict[str, Any]:
    try:
        label, start, end = value.split(":", 2)
        return {"label": label, "start_s": float(start), "end_s": float(end)}
    except ValueError as error:
        raise argparse.ArgumentTypeError("window must be LABEL:START:END") from error


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asc", type=Path, required=True)
    parser.add_argument("--dbc", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--domain", required=True)
    parser.add_argument("--condition", action="append", default=[])
    parser.add_argument("--window", action="append", type=_parse_window, default=[])
    args = parser.parse_args()
    result = run_spike(
        args.asc, args.dbc, domain=args.domain,
        conditions=args.condition, windows=args.window,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "output": str(args.output),
        "parsed_frames": result["asc_integrity"]["parsed_frame_count"],
        "bus_variants": len(result["bus_inventory"]),
        "coverage": result["coverage_summary"],
        "signal_summaries": len(result["signal_summaries"]),
        "candidates": len(result["candidates"]),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
