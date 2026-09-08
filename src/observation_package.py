"""Freeze and validate the Phase 3B.1 Observation Package."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from analysis_charter import canonical_json


PACKAGE_VERSION = "observation-package-v1"


def build_package(discovery: dict[str, Any], *, charter_ref: str, charter_hash: str) -> dict[str, Any]:
    package = {
        "package_version": PACKAGE_VERSION,
        "experiment_id": discovery["experiment_id"],
        "analysis_charter": {"ref": charter_ref, "sha256": charter_hash},
        "asc_integrity": discovery["asc_integrity"],
        "dbc_fingerprints": discovery["dbc_fingerprints"],
        "discovery_algorithm_version": discovery["discovery_algorithm_version"],
        "limits_profile": discovery["limits_profile"],
        "bus_inventory": discovery["bus_inventory"],
        "observations": discovery["observations"],
        "coverage": discovery["coverage"],
        "signal_summaries": discovery["signal_summaries"],
        "residual_summaries": discovery["residual_summaries"],
        "unknown_summaries": discovery["unknown_summaries"],
        "candidates": discovery["candidates"],
        "dispositions": discovery["dispositions"],
        "raw_reference_manifest": discovery["raw_reference_manifest"],
        "candidate_compression": discovery["candidate_compression"],
        "collection_fingerprints": {
            "bus_inventory_sha256": _fingerprint(discovery["bus_inventory"]),
            "observations_sha256": _fingerprint(discovery["observations"]),
            "coverage_sha256": _fingerprint(discovery["coverage"]),
            "signal_summaries_sha256": _fingerprint(discovery["signal_summaries"]),
            "residual_summaries_sha256": _fingerprint(discovery["residual_summaries"]),
            "unknown_summaries_sha256": _fingerprint(discovery["unknown_summaries"]),
            "candidates_sha256": _fingerprint(discovery["candidates"]),
        },
        "closure": discovery["closure"],
        "known_signal_hints_recorded_not_applied_as_filter": discovery[
            "known_signal_hints_recorded_not_applied_as_filter"
        ],
    }
    content_hash = _fingerprint(package)
    package["package_id"] = f"{package['experiment_id']}-discovery-{content_hash[:16]}"
    package["package_hash"] = _fingerprint(package)
    return package


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def validate_package(package: dict[str, Any]) -> None:
    stored_hash = package.get("package_hash")
    body = dict(package)
    body.pop("package_hash", None)
    if stored_hash != _fingerprint(body):
        raise ValueError("PACKAGE_FREEZE_FAILURE: package hash mismatch")
    if not package.get("closure", {}).get("closed"):
        raise ValueError("OBSERVATION_COVERAGE_FAILURE: closure is open")
    observations = package["observations"]
    candidate_refs = {
        ref
        for candidate in package["candidates"]
        for ref in candidate.get("related_observation_refs", [])
        if ref.startswith("OBS-")
    }
    observation_ids = {row["observation_id"] for row in observations}
    if not candidate_refs <= observation_ids:
        raise ValueError("TRACEABILITY_FAILURE: candidate has unknown Observation reference")
    manifest_ids = {row["observation_id"] for row in package["raw_reference_manifest"]}
    observations_with_frames = {row["observation_id"] for row in observations if row["frame_count"]}
    if not observations_with_frames <= manifest_ids:
        raise ValueError("TRACEABILITY_FAILURE: Observation missing raw reference")


def freeze_package(package: dict[str, Any], path: Path) -> None:
    validate_package(package)
    path.parent.mkdir(parents=True, exist_ok=False)
    path.write_text(
        json.dumps(package, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
