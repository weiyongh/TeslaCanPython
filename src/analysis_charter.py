"""Minimal, hashable analysis boundary for the discovery-v1 pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Any


CHARTER_VERSION = "analysis-charter-v1"


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


@dataclass(frozen=True)
class AnalysisCharter:
    experiment_id: str
    purpose: str
    system_scope: str
    analysis_scope: str
    allowed_data_sources: tuple[str, ...]
    asc_ref: str
    dbc_refs: tuple[str, ...]
    time_policy: dict[str, Any]
    l3_prior_refs: tuple[str, ...] = ()
    evidence_requirements: tuple[str, ...] = ()
    known_signal_hints: tuple[str, ...] = ()
    semantic_context_ref: str | None = None
    experiment_procedure_ref: str | None = None
    charter_version: str = CHARTER_VERSION
    source_ref: str | None = field(default=None, compare=False)

    @classmethod
    def load(cls, path: Path) -> "AnalysisCharter":
        raw = json.loads(path.read_text(encoding="utf-8"))
        if raw.get("charter_version") != CHARTER_VERSION:
            raise ValueError(f"unsupported charter_version: {raw.get('charter_version')!r}")
        required = (
            "experiment_id", "purpose", "system_scope", "analysis_scope",
            "allowed_data_sources", "asc_ref", "dbc_refs", "time_policy",
        )
        missing = [name for name in required if name not in raw]
        if missing:
            raise ValueError(f"missing charter fields: {', '.join(missing)}")
        if not raw["experiment_id"] or not raw["asc_ref"] or not raw["dbc_refs"]:
            raise ValueError("experiment_id, asc_ref, and dbc_refs must be non-empty")
        return cls(
            charter_version=raw["charter_version"],
            experiment_id=str(raw["experiment_id"]),
            purpose=str(raw["purpose"]),
            system_scope=str(raw["system_scope"]),
            analysis_scope=str(raw["analysis_scope"]),
            l3_prior_refs=tuple(map(str, raw.get("l3_prior_refs", ()))),
            evidence_requirements=tuple(map(str, raw.get("evidence_requirements", ()))),
            allowed_data_sources=tuple(map(str, raw["allowed_data_sources"])),
            asc_ref=str(raw["asc_ref"]),
            dbc_refs=tuple(map(str, raw["dbc_refs"])),
            time_policy=dict(raw["time_policy"]),
            known_signal_hints=tuple(map(str, raw.get("known_signal_hints", ()))),
            semantic_context_ref=(str(raw["semantic_context_ref"]) if raw.get("semantic_context_ref") else None),
            experiment_procedure_ref=(str(raw["experiment_procedure_ref"]) if raw.get("experiment_procedure_ref") else None),
            source_ref=str(path),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "charter_version": self.charter_version,
            "experiment_id": self.experiment_id,
            "purpose": self.purpose,
            "system_scope": self.system_scope,
            "analysis_scope": self.analysis_scope,
            "l3_prior_refs": list(self.l3_prior_refs),
            "evidence_requirements": list(self.evidence_requirements),
            "allowed_data_sources": list(self.allowed_data_sources),
            "asc_ref": self.asc_ref,
            "dbc_refs": list(self.dbc_refs),
            "time_policy": self.time_policy,
            "known_signal_hints": list(self.known_signal_hints),
            "semantic_context_ref": self.semantic_context_ref,
            "experiment_procedure_ref": self.experiment_procedure_ref,
        }

    @property
    def fingerprint(self) -> str:
        return hashlib.sha256(canonical_json(self.as_dict())).hexdigest()


def resolve_repo_path(repo_root: Path, reference: str) -> Path:
    path = Path(reference)
    resolved = (path if path.is_absolute() else repo_root / path).resolve()
    root = repo_root.resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"data reference escapes repository: {reference}")
    return resolved
