"""Minimal per-experiment Draft -> Review -> Approved evidence-plan workflow.

This module deliberately contains no vehicle knowledge and no signal scoring.
Codex or an experiment adapter supplies the draft.  Human overrides are scoped
to one experiment and are never promoted to a vehicle knowledge base.
"""
from __future__ import annotations

import csv
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Iterable


PRIORITIES = {"P0", "P1", "P2", "P3"}
REPORT_POSITIONS = {
    "CORE_TIMELINE", "CORE_SIGNAL_TABLE", "CONDITION_SUMMARY",
    "CAPABILITY_SUMMARY", "ANALYSIS_WINDOW", "SPECIAL_TABLE",
    "AUDIT_ONLY", "EXCLUDE", "NETWORK_WAKE_SUMMARY", "CONTROL_RELATIONSHIP",
    "READY_CROSSCHECK_TABLE", "HV_CHAIN_TABLE", "SAFETY_CONDITION_TABLE",
    "HV_SPECIAL_TIMELINE", "DCDC_TABLE", "DCDC_SPECIAL_TABLE",
    "ENGINEERING_AUDIT", "BODY_INPUT_TABLE",
}
REVIEW_DECISIONS = {"ACCEPT", "OVERRIDE", "EXCLUDE"}
UNCERTAINTY_FLAGS = {
    "NODE_BINDING_UNCERTAIN", "SEMANTIC_CANDIDATE", "DBC_VERSION_CONFLICT",
    "MULTIPLE_POSSIBLE_ROLES", "PRIORITY_AMBIGUOUS",
    "REPORT_POSITION_AMBIGUOUS", "BOUNDARY_CROSSING",
    "CROSS_MAINLINE_EVIDENCE", "PROXY_OBSERVATION",
    "PHYSICAL_MEANING_UNCONFIRMED", "STATE_APPLICABILITY_UNCERTAIN",
    "MISSING_DIRECT_SIGNAL", "SUFFICIENCY_RULE_UNCONFIRMED",
    "MUX_APPLICABILITY_UNCONFIRMED",
}
ASSESSMENT_STATUSES = {
    "SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE",
    "NOT_OBSERVED", "NOT_APPLICABLE",
}


@dataclass(frozen=True)
class EvidenceAssessment:
    requirement_id: str
    status: str
    evidence_summary: str
    limitation: str = ""

    def validate(self) -> None:
        if not self.requirement_id or self.status not in ASSESSMENT_STATUSES:
            raise ValueError("invalid evidence assessment")
        if not self.evidence_summary:
            raise ValueError("evidence assessment requires a summary")


def split_positions(value: str) -> tuple[str, ...]:
    return tuple(x.strip() for x in value.split("+") if x.strip())


def validate_positions(value: str) -> None:
    positions = split_positions(value)
    if not positions or any(x not in REPORT_POSITIONS for x in positions):
        raise ValueError(f"invalid report position: {value}")


@dataclass(frozen=True)
class DraftSignalEvidence:
    experiment_id: str
    signal_key: str
    signal: str
    message: str
    can_id: str
    unit: str
    evidence_requirement: str
    suggested_role: str
    suggested_priority: str
    suggested_report_position: str
    suggested_order: int
    derivation_reason: str
    semantic_status: str
    confidence: str
    uncertainty_flags: str = ""
    review_required: str = "NO"
    chinese_semantic: str = ""

    def validate(self) -> None:
        if not self.experiment_id or not self.signal_key or not self.signal:
            raise ValueError("experiment_id, signal_key and signal are required")
        if self.experiment_id >= "TM3-015" and not self.chinese_semantic:
            raise ValueError(f"Chinese semantic is required from TM3-015: {self.signal_key}")
        if self.suggested_priority not in PRIORITIES:
            raise ValueError(f"invalid priority: {self.suggested_priority}")
        validate_positions(self.suggested_report_position)
        if self.review_required not in {"YES", "NO"}:
            raise ValueError("review_required must be YES or NO")
        flags = {x for x in self.uncertainty_flags.split("+") if x}
        unknown = flags - UNCERTAINTY_FLAGS
        if unknown:
            raise ValueError(f"unknown uncertainty flags: {sorted(unknown)}")
        if flags and self.review_required != "YES":
            raise ValueError(f"uncertain row must require review: {self.signal_key}")


@dataclass(frozen=True)
class ReviewOverride:
    experiment_id: str
    signal_key: str
    decision: str
    override_role: str = ""
    override_priority: str = ""
    override_report_position: str = ""
    override_order: str = ""
    human_reason: str = ""
    reviewer: str = ""
    reviewed_at: str = ""

    def validate(self) -> None:
        if self.decision not in REVIEW_DECISIONS:
            raise ValueError(f"invalid review decision: {self.decision}")
        if not self.human_reason or not self.reviewer or not self.reviewed_at:
            raise ValueError(f"review provenance required: {self.signal_key}")
        if self.override_priority and self.override_priority not in PRIORITIES:
            raise ValueError(f"invalid override priority: {self.override_priority}")
        if self.override_report_position:
            validate_positions(self.override_report_position)
        if self.decision == "OVERRIDE" and not any([
            self.override_role, self.override_priority,
            self.override_report_position, self.override_order,
        ]):
            raise ValueError(f"OVERRIDE has no changed field: {self.signal_key}")


@dataclass(frozen=True)
class ApprovedSignalEvidence:
    experiment_id: str
    plan_status: str
    scope: str
    signal_key: str
    signal: str
    message: str
    can_id: str
    unit: str
    evidence_requirement: str
    suggested_role: str
    suggested_priority: str
    suggested_report_position: str
    suggested_order: int
    derivation_reason: str
    semantic_status: str
    confidence: str
    uncertainty_flags: str
    review_required: str
    review_decision: str
    effective_role: str
    effective_priority: str
    effective_report_position: str
    effective_order: int
    decision_source: str
    human_reason: str
    reviewer: str
    reviewed_at: str
    chinese_semantic: str = ""

    def validate(self) -> None:
        if self.plan_status != "APPROVED":
            raise ValueError("Renderer requires APPROVED plan rows")
        if self.experiment_id >= "TM3-015" and not self.chinese_semantic:
            raise ValueError(f"Chinese semantic is required from TM3-015: {self.signal_key}")
        if self.scope != "THIS_EXPERIMENT_ONLY":
            raise ValueError("approved plan must be experiment-scoped")
        if self.effective_priority not in PRIORITIES:
            raise ValueError(f"invalid effective priority: {self.signal_key}")
        validate_positions(self.effective_report_position)
        if self.review_required == "YES" and self.review_decision not in REVIEW_DECISIONS:
            raise ValueError(f"unreviewed uncertain row: {self.signal_key}")

    def has_position(self, position: str) -> bool:
        return position in split_positions(self.effective_report_position)


@dataclass(frozen=True)
class ApprovedEvidencePlan:
    experiment_id: str
    plan_status: str
    scope: str
    signals: tuple[ApprovedSignalEvidence, ...]

    def validate(self) -> None:
        if self.plan_status != "APPROVED" or self.scope != "THIS_EXPERIMENT_ONLY":
            raise ValueError("plan is not approved for this experiment")
        if not self.signals:
            raise ValueError("approved plan contains no signals")
        keys = set()
        for row in self.signals:
            row.validate()
            if row.experiment_id != self.experiment_id:
                raise ValueError("mixed experiment ids in approved plan")
            if row.signal_key in keys:
                raise ValueError(f"duplicate approved signal: {row.signal_key}")
            keys.add(row.signal_key)

    def by_key(self) -> dict[str, ApprovedSignalEvidence]:
        return {x.signal_key: x for x in self.signals}


def approve_plan(
    draft_rows: Iterable[DraftSignalEvidence],
    overrides: Iterable[ReviewOverride],
) -> ApprovedEvidencePlan:
    draft = list(draft_rows)
    review = list(overrides)
    if not draft:
        raise ValueError("empty draft plan")
    for row in draft:
        row.validate()
    experiment_id = draft[0].experiment_id
    if any(x.experiment_id != experiment_id for x in draft):
        raise ValueError("draft contains multiple experiments")
    review_by_key = {}
    draft_keys = {x.signal_key for x in draft}
    for item in review:
        item.validate()
        if item.experiment_id != experiment_id:
            raise ValueError("review experiment does not match draft")
        if item.signal_key not in draft_keys:
            raise ValueError(f"override references unknown signal: {item.signal_key}")
        if item.signal_key in review_by_key:
            raise ValueError(f"duplicate review override: {item.signal_key}")
        review_by_key[item.signal_key] = item
    unresolved = [x.signal_key for x in draft if x.review_required == "YES" and x.signal_key not in review_by_key]
    if unresolved:
        raise ValueError("unreviewed uncertain signals: " + ", ".join(unresolved))

    approved = []
    for row in draft:
        override = review_by_key.get(row.signal_key)
        if override and override.decision == "EXCLUDE":
            role, priority, position, order = (
                override.override_role or row.suggested_role,
                override.override_priority or row.suggested_priority,
                "EXCLUDE",
                int(override.override_order or row.suggested_order),
            )
        elif override and override.decision == "OVERRIDE":
            role, priority, position, order = (
                override.override_role or row.suggested_role,
                override.override_priority or row.suggested_priority,
                override.override_report_position or row.suggested_report_position,
                int(override.override_order or row.suggested_order),
            )
        else:
            role, priority, position, order = (
                row.suggested_role, row.suggested_priority,
                row.suggested_report_position, row.suggested_order,
            )
        approved.append(ApprovedSignalEvidence(
            experiment_id=experiment_id, plan_status="APPROVED",
            scope="THIS_EXPERIMENT_ONLY", signal_key=row.signal_key,
            signal=row.signal, message=row.message, can_id=row.can_id,
            unit=row.unit, evidence_requirement=row.evidence_requirement,
            suggested_role=row.suggested_role,
            suggested_priority=row.suggested_priority,
            suggested_report_position=row.suggested_report_position,
            suggested_order=row.suggested_order,
            derivation_reason=row.derivation_reason,
            semantic_status=row.semantic_status, confidence=row.confidence,
            uncertainty_flags=row.uncertainty_flags,
            review_required=row.review_required,
            review_decision=override.decision if override else "AUTO_ACCEPT",
            effective_role=role, effective_priority=priority,
            effective_report_position=position, effective_order=order,
            decision_source="HUMAN" if override else "CODEX",
            human_reason=override.human_reason if override else "",
            reviewer=override.reviewer if override else "",
            reviewed_at=override.reviewed_at if override else "",
            chinese_semantic=row.chinese_semantic,
        ))
    plan = ApprovedEvidencePlan(experiment_id, "APPROVED", "THIS_EXPERIMENT_ONLY", tuple(approved))
    plan.validate()
    return plan


def _write_dataclasses(path: Path, rows: Iterable[object]) -> None:
    rows = list(rows)
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    names = [x.name for x in fields(rows[0])]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=names)
        writer.writeheader()
        writer.writerows(asdict(x) for x in rows)


def write_draft_csv(path: Path, rows: Iterable[DraftSignalEvidence]) -> None:
    _write_dataclasses(path, rows)


def write_review_csv(path: Path, rows: Iterable[ReviewOverride]) -> None:
    _write_dataclasses(path, rows)


def write_approved_csv(path: Path, plan: ApprovedEvidencePlan) -> None:
    plan.validate()
    _write_dataclasses(path, plan.signals)


def read_approved_csv(path: Path) -> ApprovedEvidencePlan:
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = []
        for raw in csv.DictReader(f):
            raw["suggested_order"] = int(raw["suggested_order"])
            raw["effective_order"] = int(raw["effective_order"])
            rows.append(ApprovedSignalEvidence(**raw))
    if not rows:
        raise ValueError("empty approved plan CSV")
    plan = ApprovedEvidencePlan(rows[0].experiment_id, rows[0].plan_status, rows[0].scope, tuple(rows))
    plan.validate()
    return plan
