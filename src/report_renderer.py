"""Deliberately dumb Markdown renderer for approved experiment evidence."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Iterable

from evidence_plan import ApprovedEvidencePlan, EvidenceAssessment


@dataclass(frozen=True)
class TimelineEvent:
    time_s: float
    action: str
    driver_input: str = "—"
    request: str = "—"
    actual: str = "—"
    motion: str = "—"
    elec_power: str = "—"
    pack_current: str = "—"
    pack_power: str = "—"
    note: str = ""


@dataclass(frozen=True)
class CoreSignal:
    signal_key: str
    observed: str
    changed: str
    decode_status: str
    purpose: str


@dataclass(frozen=True)
class ControlNodeView:
    name: str
    observability: str


@dataclass(frozen=True)
class ControlRelationshipView:
    """Upstream-authored L3 relationship; the renderer never derives it from signals."""
    control_chain: tuple[ControlNodeView, ...]
    physical_response: str
    energy_cross_validation: str
    boundaries: tuple[str, ...] = field(default_factory=tuple)

    def validate(self) -> None:
        if not self.control_chain or not self.physical_response or not self.energy_cross_validation:
            raise ValueError("control relationship view must contain three independent lines")
        allowed = {"直接观测", "部分可观测", "本次无直接观测", "由上下游证据间接支持"}
        for node in self.control_chain:
            if not node.name or node.observability not in allowed:
                raise ValueError("invalid control-node view")


@dataclass(frozen=True)
class Table:
    title: str
    headers: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class ExperimentReport:
    experiment_id: str
    title: str
    metadata_lines: tuple[str, ...]
    facts: tuple[str, ...]
    control_relationship: ControlRelationshipView
    diagnostic_conclusion: tuple[str, ...]
    evidence_boundaries: tuple[str, ...]
    recommendations: tuple[str, ...]
    timeline_signal_keys: tuple[str, ...]
    timeline: tuple[TimelineEvent, ...]
    analysis_tables: tuple[Table, ...]
    core_signals: tuple[CoreSignal, ...]
    readability_issues: tuple[str, ...]
    audit_lines: tuple[str, ...]
    special_tables: tuple[Table, ...] = field(default_factory=tuple)
    assessments: tuple[EvidenceAssessment, ...] = field(default_factory=tuple)


_FLOAT_TAIL = re.compile(r"(?<![\w.])-?\d+\.\d{8,}(?![\w.])")


def _humanize_float_tails(text: str) -> str:
    """Remove binary-float tails while leaving intentional short precision intact."""
    def replace(match: re.Match[str]) -> str:
        return f"{float(match.group(0)):.6f}".rstrip("0").rstrip(".")
    return _FLOAT_TAIL.sub(replace, text)


def _escape(value: object) -> str:
    return _humanize_float_tails(str(value)).replace("|", "\\|").replace("\n", "<br>")


def _table(headers: Iterable[str], rows: Iterable[Iterable[object]]) -> str:
    headers = tuple(headers)
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines.extend("| " + " | ".join(_escape(value) for value in row) + " |" for row in rows)
    return "\n".join(lines)


def _bullets(items: Iterable[str]) -> str:
    return "\n".join(f"- {item}" for item in items) or "- 无"


def _validate(plan: ApprovedEvidencePlan, report: ExperimentReport) -> None:
    plan.validate()
    if plan.experiment_id != report.experiment_id:
        raise ValueError("report experiment does not match approved plan")
    report.control_relationship.validate()
    allowed = plan.by_key()
    for signal_key in report.timeline_signal_keys:
        if signal_key not in allowed or not allowed[signal_key].has_position("CORE_TIMELINE"):
            raise ValueError(f"signal not approved for core timeline: {signal_key}")
    for signal in report.core_signals:
        if signal.signal_key not in allowed or not allowed[signal.signal_key].has_position("CORE_SIGNAL_TABLE"):
            raise ValueError(f"signal not approved for core table: {signal.signal_key}")
    for assessment in report.assessments:
        assessment.validate()


def render_final_report(plan: ApprovedEvidencePlan, report: ExperimentReport) -> str:
    _validate(plan, report)
    relationship = report.control_relationship
    chain = " → ".join(f"{x.name}（{x.observability}）" for x in relationship.control_chain)
    relationship_text = "\n".join((
        f"- 控制链：{chain}",
        f"- 动力/物理响应：{relationship.physical_response}",
        f"- 能源交叉验证：{relationship.energy_cross_validation}",
        *[f"- 边界：{x}" for x in relationship.boundaries],
    ))
    assessment_text = "\n".join(
        f"- `{x.requirement_id}`：`{x.status}` — {x.evidence_summary.rstrip('。；; ')}" +
        (f"；边界：{x.limitation.rstrip('。；; ')}。" if x.limitation else "。")
        for x in report.assessments
    ) or "- 无结构化Assessment"
    return f"""# {report.title}

## 实验信息与适用范围

{_bullets(report.metadata_lines)}

## 事实与关键证据

{_bullets(report.facts)}

## 控制关系

{relationship_text}

## 诊断判断

{_bullets(report.diagnostic_conclusion)}

### Evidence Assessment

{assessment_text}

## 证据边界

{_bullets(report.evidence_boundaries)}

## 结论与下一步建议

{_bullets(report.recommendations)}
"""


def render_timeline(plan: ApprovedEvidencePlan, report: ExperimentReport) -> str:
    _validate(plan, report)
    headers = ("时间(s)", "状态/动作", "电门(%)", "请求扭矩(Nm)", "实际扭矩(Nm)",
               "车速(km/h)", "电驱功率(kW)", "Pack电流(A)", "Pack功率(kW)", "备注")
    rows = ((f"{x.time_s:.3f}".rstrip("0").rstrip("."), x.action, x.driver_input, x.request,
             x.actual, x.motion, x.elec_power, x.pack_current, x.pack_power, x.note) for x in report.timeline)
    sections = [f"# {report.experiment_id} 采集时间线与关键Signal", "## 人读主时间线", _table(headers, rows)]
    for table in report.analysis_tables + report.special_tables:
        sections.extend([f"## {table.title}", _table(table.headers, table.rows)])
    sections.append("> 事件编号、原始采样时间、Signal age 与 DLC 仅保留在 CSV/工程审计中。")
    return "\n\n".join(sections) + "\n"


def render_signal_coverage(plan: ApprovedEvidencePlan, report: ExperimentReport) -> str:
    _validate(plan, report)
    by_key = plan.by_key()
    signals = sorted(report.core_signals, key=lambda x: by_key[x.signal_key].effective_order)
    rows = []
    for item in signals:
        approved = by_key[item.signal_key]
        rows.append((approved.effective_role, approved.signal, approved.message, approved.can_id,
                     approved.unit, item.observed, item.changed, item.decode_status, item.purpose))
    body = _table(("控制树角色", "Signal", "Message", "CAN ID", "单位", "本次观测范围/状态",
                   "是否变化", "解码状态", "本次用途"), rows)
    issues = _bullets(report.readability_issues)
    return f"# {report.experiment_id} DBC关键Signal覆盖与可读性\n\n## 核心Signal表\n\n{body}\n\n## DBC异常与可读性说明\n\n{issues}\n"


def render_audit(plan: ApprovedEvidencePlan, report: ExperimentReport) -> str:
    _validate(plan, report)
    reviewed = sum(row.decision_source == "HUMAN" for row in plan.signals)
    return (f"# {report.experiment_id} 工程审计\n\n## Evidence Plan状态\n\n"
            f"- 状态：`{plan.plan_status}`\n- 范围：`{plan.scope}`\n- Approved Signal：{len(plan.signals)}\n"
            f"- 含人工审核记录：{reviewed}\n- Renderer未执行Signal重要度判断。\n\n"
            f"## 数据与复现\n\n{_bullets(report.audit_lines)}\n\n"
            "## 工程字段边界\n\n- E事件编号、原始采样时间、Signal age、DLC与逐帧解码状态保留在CSV/审计文件，不进入人读主时间线。\n")


def render_report_bundle(plan: ApprovedEvidencePlan, report: ExperimentReport, output_dir: Path) -> dict[str, Path]:
    _validate(plan, report)
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "final": output_dir / f"{report.experiment_id}_最终报告.md",
        "timeline": output_dir / "采集时间线与关键Signal.md",
        "coverage": output_dir / "DBC关键Signal覆盖与可读性.md",
        "audit": output_dir / "工程审计.md",
    }
    content = {
        "final": render_final_report(plan, report), "timeline": render_timeline(plan, report),
        "coverage": render_signal_coverage(plan, report), "audit": render_audit(plan, report),
    }
    for key, path in outputs.items():
        path.write_text(content[key], encoding="utf-8")
    return outputs
