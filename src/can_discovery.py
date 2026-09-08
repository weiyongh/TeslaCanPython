"""Formal deterministic CAN discovery interface for pipeline discovery-v1.

Phase 3B.1 deliberately reuses the validated Phase 2.5 scanner behind this
stable interface.  The spike remains the implementation backend for now; this
module owns formal admission normalization and Observation Space invariants.
"""
from __future__ import annotations

from collections import Counter
import hashlib
from pathlib import Path
from typing import Any

import cantools

from spikes.semantic_coverage_residual_discovery import run_spike, signal_fingerprint


DISCOVERY_ALGORITHM_VERSION = "formal-can-discovery-v1+spike-kernel-v1"
LIMITS_PROFILE = {
    "unique_values_per_observation": 256,
    "raw_refs_per_observation": 8,
    "candidates_per_type": 25,
    "candidates_total": 120,
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _dbc_fingerprints(paths: list[Path]) -> list[dict[str, Any]]:
    return [
        {"ref": str(path), "sha256": _sha256(path), "file_size": path.stat().st_size}
        for path in paths
    ]


def discover(
    asc_path: Path,
    dbc_paths: list[Path],
    *,
    experiment_id: str,
    purpose: str,
    known_signal_hints: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Run one semantic parse and return normalized formal observations.

    ``known_signal_hints`` is recorded only.  It is intentionally not passed to
    the scanner and therefore cannot restrict frames, coverage, or observations.
    """
    if not asc_path.is_file():
        raise FileNotFoundError(f"ASC not found: {asc_path}")
    missing_dbcs = [str(path) for path in dbc_paths if not path.is_file()]
    if missing_dbcs:
        raise FileNotFoundError(f"DBC not found: {', '.join(missing_dbcs)}")

    spike = run_spike(
        asc_path,
        dbc_paths,
        domain=purpose,
        conditions=[],
        windows=[],
    )
    integrity = spike["asc_integrity"]
    inventory = spike["bus_inventory"]
    coverage = spike["dbc_coverage"]
    coverage_by_variant = {
        (row["bus_key"], row["observed_dlc"]): row for row in coverage
    }

    observations = []
    residual = []
    unknown = []
    raw_manifest = []
    for index, raw in enumerate(inventory, 1):
        key = (raw["bus_key"], raw["dlc"])
        cov = coverage_by_variant[key]
        observation_id = f"OBS-{index:04d}"
        observation = {
            "observation_id": observation_id,
            "observation_kind": "BUS_VARIANT",
            **raw,
            "coverage_state": cov["coverage_class"],
            "coverage_reasons": cov["coverage_reasons"],
            "definition_sources": cov["definition_sources"],
            "residual_changing_bits": cov["residual_changing_bits"],
        }
        observations.append(observation)
        for raw_index, ref in enumerate(raw["raw_refs"], 1):
            raw_manifest.append({
                "raw_reference_id": f"{observation_id}-R{raw_index:02d}",
                "observation_id": observation_id,
                "asc_sha256": integrity["sha256"],
                **ref,
            })
        if cov["coverage_class"] == "UNMATCHED":
            unknown.append(observation)
        elif cov["residual_changing_bits"]:
            residual.append(observation)

    parsed_bus_keys = {row["bus_key"] for row in inventory}
    observed_bus_keys = {row["bus_key"] for row in observations}
    missing_bus_keys = sorted(parsed_bus_keys - observed_bus_keys)
    dispositions = []
    if missing_bus_keys:
        dispositions.extend({"bus_key": key, "reason": "OBSERVATION_BUILD_FAILURE"} for key in missing_bus_keys)
    malformed = int(integrity.get("malformed_candidate_lines", 0))
    if malformed:
        dispositions.append({
            "record_scope": "ASC_LINES",
            "reason": "MALFORMED_OR_UNSUPPORTED_RECORD",
            "count": malformed,
        })

    summarized_signals = {
        (row["bus_key"], row["dbc_source"], row["signal_name"])
        for row in spike["signal_summaries"]
    }
    definitions_by_source_and_message = {}
    for dbc_path in dbc_paths:
        database = cantools.database.load_file(dbc_path, strict=False)
        for message in database.messages:
            definitions_by_source_and_message[(str(dbc_path), message.name)] = message
    for row in coverage:
        for source in row["definition_sources"]:
            message = definitions_by_source_and_message.get(
                (source["dbc_source"], source["message_name"])
            )
            if message is None:
                continue
            for signal in message.signals:
                identity = (row["bus_key"], source["dbc_source"], signal.name)
                if identity in summarized_signals:
                    continue
                dispositions.append({
                    "disposition_kind": "SIGNAL_DECODE",
                    "bus_key": row["bus_key"],
                    "observed_dlc": row["observed_dlc"],
                    "dbc_source": source["dbc_source"],
                    "message_name": source["message_name"],
                    "signal_name": signal.name,
                    "definition_fingerprint": signal_fingerprint(signal),
                    "reason": (
                        "MESSAGE_DECODE_FAILED_FOR_OBSERVED_DLC"
                        if source["succeeded"] == 0
                        else "SIGNAL_NOT_PRESENT_IN_OBSERVED_MUX_OR_TRUNCATED_DECODE"
                    ),
                })

    if missing_bus_keys:
        raise RuntimeError(f"OBSERVATION_COVERAGE_FAILURE: {missing_bus_keys}")

    channels = sorted({row["channel"] for row in inventory})
    frame_formats = sorted({row["frame_format"] for row in inventory})
    admission = {
        "asc_identity": str(asc_path),
        "sha256": integrity["sha256"],
        "file_size": integrity["size_bytes"],
        "parsed_frame_count": integrity["parsed_frame_count"],
        "abnormal_line_count": malformed,
        "first_timestamp": integrity["first_time_s"],
        "last_timestamp": integrity["last_time_s"],
        "channels": channels,
        "frame_formats": frame_formats,
        "admission_status": "ADMITTED",
    }
    discarded = spike["candidate_compression"]["discarded_by_limit"]
    return {
        "experiment_id": experiment_id,
        "asc_integrity": admission,
        "dbc_fingerprints": _dbc_fingerprints(dbc_paths),
        "discovery_algorithm_version": DISCOVERY_ALGORITHM_VERSION,
        "limits_profile": LIMITS_PROFILE,
        "bus_inventory": inventory,
        "observations": observations,
        "coverage": coverage,
        "signal_summaries": spike["signal_summaries"],
        "residual_summaries": residual,
        "unknown_summaries": unknown,
        "candidates": spike["candidates"],
        "dispositions": dispositions,
        "raw_reference_manifest": raw_manifest,
        "candidate_compression": {
            **spike["candidate_compression"],
            "discarded_total": sum(discarded.values()),
            "observation_count_after_compression": len(observations),
        },
        "known_signal_hints_recorded_not_applied_as_filter": list(known_signal_hints),
        "closure": {
            "parsed_bus_key_count": len(parsed_bus_keys),
            "observed_bus_key_count": len(observed_bus_keys),
            "disposed_bus_key_count": len(missing_bus_keys),
            "missing_bus_keys": missing_bus_keys,
            "closed": not missing_bus_keys,
        },
        "coverage_counts": dict(Counter(row["coverage_class"] for row in coverage)),
        "asc_parse_count": 1,
    }
