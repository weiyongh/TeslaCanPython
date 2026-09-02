"""Build the human-approved TM3-015 experiment-scoped Evidence Plan.

This script only combines reviewed planning artifacts. It does not read ASC data.
"""
from __future__ import annotations

import csv
from pathlib import Path

from evidence_plan import (
    DraftSignalEvidence,
    ReviewOverride,
    approve_plan,
    write_approved_csv,
    write_draft_csv,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "TM3-015"


def read_main_draft() -> list[DraftSignalEvidence]:
    rows = []
    with (OUT / "evidence_plan_draft.csv").open(encoding="utf-8-sig", newline="") as f:
        for raw in csv.DictReader(f):
            raw["suggested_order"] = int(raw["suggested_order"])
            rows.append(DraftSignalEvidence(**raw))
    return rows


def read_thermal_draft(existing: set[str]) -> list[DraftSignalEvidence]:
    rows = []
    with (OUT / "thermal_signal_candidates_draft.csv").open(encoding="utf-8-sig", newline="") as f:
        for index, raw in enumerate(csv.DictReader(f), start=1):
            key = raw["signal"]
            if key in existing:
                continue
            priority = raw["suggested_priority"]
            role = raw["control_role"]
            if key.startswith("CP_pinTemperature"):
                position = "SPECIAL_TABLE"
            elif priority == "P1":
                position = "CONDITION_SUMMARY+SPECIAL_TABLE"
            else:
                position = "SPECIAL_TABLE"
            rows.append(DraftSignalEvidence(
                experiment_id="TM3-015",
                signal_key=key,
                signal=key,
                message=raw["message"],
                can_id=raw["can_id"],
                unit=raw["unit"],
                evidence_requirement="ER-10 Pack热状态—充电能力条件—热管理请求/目标—执行反馈—温度响应",
                suggested_role=role,
                suggested_priority=priority,
                suggested_report_position=position,
                suggested_order=400 + index * 10,
                derivation_reason=f"人工审核的热管理副线候选；DBC来源={raw['dbc_source']}；mux={raw['mux']}",
                semantic_status=raw["semantic_status"],
                confidence=raw["confidence"],
                uncertainty_flags=raw["uncertainty_flags"],
                review_required="YES",
                chinese_semantic=raw["chinese_semantic"],
            ))
    return rows


def read_reviews(path: Path) -> list[ReviewOverride]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return [ReviewOverride(**raw) for raw in csv.DictReader(f)]


def main() -> None:
    draft = read_main_draft()
    keys = {row.signal_key for row in draft}
    draft.extend(read_thermal_draft(keys))
    reviews = read_reviews(OUT / "evidence_plan_review_overrides.csv")
    thermal_reviews = read_reviews(OUT / "thermal_signal_review_overrides.csv")
    reviews.extend(row for row in thermal_reviews if row.signal_key not in keys)
    write_draft_csv(OUT / "evidence_plan_draft_combined.csv", draft)
    plan = approve_plan(draft, reviews)
    write_approved_csv(OUT / "evidence_plan_approved.csv", plan)
    print(f"approved_rows={len(plan.signals)}")
    print(f"excluded_rows={sum(x.effective_report_position == 'EXCLUDE' for x in plan.signals)}")
    print(f"scope={plan.scope}")


if __name__ == "__main__":
    main()
