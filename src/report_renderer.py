"""Deliberately dumb Markdown renderer for approved experiment evidence."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Iterable

from evidence_plan import ApprovedEvidencePlan, EvidenceAssessment


STANDARD_REPORT_FILENAMES = (
    "{experiment_id}_最终报告.md",
    "采集时间线与关键Signal.md",
    "DBC关键Signal覆盖与可读性.md",
    "工程审计.md",
)
DRIVE_TIMELINE_HEADERS = (
    "时间(s)", "状态/动作", "电门(%)", "请求扭矩(Nm)", "实际扭矩(Nm)",
    "车速(km/h)", "电驱功率(kW)", "Pack电流(A)", "Pack功率(kW)", "备注",
)
TIMELINE_PROFILES = {
    "DRIVE": DRIVE_TIMELINE_HEADERS,
    # WAKE_HV is semantic and change-first.  Unlike DRIVE it intentionally has
    # no contract-level fixed-width header.
    "WAKE_HV": (),
}
COVERAGE_HEADERS = (
    "控制树角色", "Signal", "Message", "CAN ID", "单位", "本次观测范围/状态",
    "是否变化", "解码状态", "本次用途",
)
APPROVED_COVERAGE_HEADERS = (
    "序号", "Signal", "控制含义", "Message", "CAN ID", "单位", "本次观测范围/状态",
    "是否变化", "解码/验证状态", "本次用途/边界",
)
FINAL_FIXED_HEADINGS = (
    "## 实验信息与适用范围", "## 事实与关键证据", "## 控制关系",
    "### Evidence Assessment", "## 证据边界", "## 结论与下一步建议",
)
AUDIT_HEADINGS = ("## Evidence Plan状态", "## 数据与复现", "## 工程字段边界")
FORBIDDEN_TIMELINE_FIELDS = (
    "Event ID", "事件ID", "raw sample time", "原始采样时间",
    "Signal age", "DLC", "per-frame decode status",
)


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
class ProfileTimelineRow:
    """Legacy fixed-width profile row retained for backward compatibility."""
    values: tuple[str, ...]


@dataclass(frozen=True)
class SemanticTimelineEvent:
    """Upstream-authored presentation view for one discrete CAN event."""
    time: str
    natural_summary: str
    changes: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    engineering_significance: str
    local_limitation: str = ""
    phase: str = ""
    event_type: str = "event"

    def validate(self) -> None:
        if not self.time or not self.natural_summary:
            raise ValueError("semantic timeline event requires time and natural summary")
        if not self.changes or not all(self.changes):
            raise ValueError("semantic timeline event requires at least one change")
        if not self.evidence_refs or not all(self.evidence_refs):
            raise ValueError("semantic timeline event requires approved evidence references")
        if not self.engineering_significance:
            raise ValueError("semantic timeline event requires engineering significance")
        if self.event_type not in {"event", "stable_window"}:
            raise ValueError("semantic timeline event type must be event or stable_window")


@dataclass(frozen=True)
class CoreSignal:
    signal_key: str
    observed: str
    changed: str
    decode_status: str
    purpose: str


@dataclass(frozen=True)
class CoverageSignal:
    """Approved signal disposition for the DBC/readability report."""
    signal_key: str
    observed: str
    changed: str
    decode_status: str
    purpose: str
    evidence_kind: str = "DBC"
    control_meaning: str = ""
    source: str = ""
    boundary: str = ""
    presentation_order: int = 0

    def validate(self) -> None:
        if self.evidence_kind not in {"DBC", "DERIVED"}:
            raise ValueError("coverage evidence kind must be DBC or DERIVED")


@dataclass(frozen=True)
class MainlineVerification:
    node: str
    signal_refs: tuple[str, ...]
    validation: str
    limitation: str = ""

    def validate(self) -> None:
        if not self.node or not self.signal_refs or not self.validation:
            raise ValueError("mainline verification requires node, signals and validation")


@dataclass(frozen=True)
class ControlRelationshipLine:
    """One upstream-authored relationship line; the renderer does not infer it."""
    label: str
    expression: str
    signal_refs: tuple[str, ...] = field(default_factory=tuple)
    note: str = ""

    def validate(self) -> None:
        if not self.label or not self.expression:
            raise ValueError("control relationship line requires label and expression")


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
    timeline_profile: str = "DRIVE"
    profile_timeline_rows: tuple[ProfileTimelineRow, ...] = field(default_factory=tuple)
    judgment_heading: str = "诊断判断"
    semantic_timeline_events: tuple[SemanticTimelineEvent, ...] = field(default_factory=tuple)
    control_mainline: tuple[str, ...] = field(default_factory=tuple)
    mainline_verification: tuple[MainlineVerification, ...] = field(default_factory=tuple)
    global_evidence_boundaries: tuple[str, ...] = field(default_factory=tuple)
    coverage_signals: tuple[CoverageSignal, ...] = field(default_factory=tuple)
    control_relationship_lines: tuple[ControlRelationshipLine, ...] = field(default_factory=tuple)


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


def _purpose_and_boundary(item: CoverageSignal) -> str:
    if item.boundary:
        return f"{item.purpose.rstrip('。；; ')}；边界：{item.boundary.rstrip('。；; ')}。"
    return item.purpose


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
    if bool(report.control_mainline) != bool(report.mainline_verification):
        raise ValueError("control mainline and mainline verification must be provided together")
    if report.control_mainline:
        if len(set(report.control_mainline)) != len(report.control_mainline):
            raise ValueError("control mainline node names must be unique")
        nodes = set(report.control_mainline)
        for item in report.mainline_verification:
            item.validate()
            if item.node not in nodes:
                raise ValueError(f"verification references unknown mainline node: {item.node}")
            for signal_key in item.signal_refs:
                if signal_key not in allowed or allowed[signal_key].has_position("EXCLUDE"):
                    raise ValueError(f"mainline verification references non-approved signal: {signal_key}")
    for line in report.control_relationship_lines:
        line.validate()
        for signal_key in line.signal_refs:
            if signal_key not in allowed or allowed[signal_key].has_position("EXCLUDE"):
                raise ValueError(f"control relationship references non-approved signal: {signal_key}")
    if report.coverage_signals:
        coverage_keys = [item.signal_key for item in report.coverage_signals]
        approved_keys = [row.signal_key for row in sorted(plan.signals, key=lambda row: row.effective_order)
                         if not row.has_position("EXCLUDE")]
        if len(coverage_keys) != len(set(coverage_keys)):
            raise ValueError("coverage signals must not contain duplicates")
        if set(coverage_keys) != set(approved_keys):
            missing = sorted(set(approved_keys) - set(coverage_keys))
            extra = sorted(set(coverage_keys) - set(approved_keys))
            raise ValueError(f"coverage signals must account for every Approved signal; missing={missing}, extra={extra}")
        for item in report.coverage_signals:
            item.validate()
            if item.signal_key not in allowed:
                raise ValueError(f"coverage contains non-approved signal: {item.signal_key}")
        if any(item.presentation_order < 0 for item in report.coverage_signals):
            raise ValueError("coverage presentation order must be non-negative")
    for assessment in report.assessments:
        assessment.validate()
    if report.timeline_profile not in TIMELINE_PROFILES:
        raise ValueError(f"unknown timeline profile: {report.timeline_profile}")
    if report.timeline_profile == "DRIVE" and report.profile_timeline_rows:
        raise ValueError("DRIVE profile must use TimelineEvent rows")
    if report.timeline_profile == "DRIVE" and report.semantic_timeline_events:
        raise ValueError("DRIVE profile does not consume semantic timeline events")
    if report.timeline_profile != "DRIVE" and report.timeline:
        raise ValueError(f"{report.timeline_profile} profile must use ProfileTimelineRow rows")
    if report.semantic_timeline_events and report.profile_timeline_rows:
        raise ValueError("semantic and legacy profile timeline rows cannot be mixed")
    width = len(TIMELINE_PROFILES[report.timeline_profile])
    for row in report.profile_timeline_rows:
        if report.timeline_profile == "WAKE_HV":
            raise ValueError("WAKE_HV no longer accepts fixed-width profile rows")
        if len(row.values) != width:
            raise ValueError(f"{report.timeline_profile} timeline row must contain {width} values")
    for event in report.semantic_timeline_events:
        event.validate()
        for signal_key in event.evidence_refs:
            if signal_key not in allowed or allowed[signal_key].has_position("EXCLUDE"):
                raise ValueError(f"semantic event references non-approved signal: {signal_key}")
    if report.judgment_heading not in {"基线结论", "诊断判断"}:
        raise ValueError("judgment heading must be 基线结论 or 诊断判断")


def render_final_report(plan: ApprovedEvidencePlan, report: ExperimentReport) -> str:
    _validate(plan, report)
    relationship = report.control_relationship
    if report.control_mainline:
        approved = plan.by_key()
        chain = " → ".join(report.control_mainline)
        verification_rows = []
        for item in report.mainline_verification:
            refs = "；".join(f"`{approved[key].signal}`（`{approved[key].can_id}`）"
                            for key in item.signal_refs)
            verification_rows.append((item.node, refs, item.validation, item.limitation or "—"))
        if report.control_relationship_lines:
            lines = []
            for line in report.control_relationship_lines:
                refs = "；".join(f"`{approved[key].signal}`（`{approved[key].can_id}`）"
                                for key in line.signal_refs)
                suffix = f"  \n  证据：{refs}" if refs else ""
                note = f"  \n  {line.note}" if line.note else ""
                lines.append(f"- **{line.label}**：{line.expression}{suffix}{note}")
            relationship_intro = "\n".join(lines)
        else:
            relationship_intro = f"- 系统状态推进主线：{chain}"
        relationship_text = "\n\n".join((
            relationship_intro,
            "### 主线核验摘要\n\n" + _table(
                ("主线节点", "Approved Signal", "当前验证程度", "局部限制"), verification_rows),
        ))
    else:
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

## {report.judgment_heading}

{_bullets(report.diagnostic_conclusion)}

### Evidence Assessment

{assessment_text}

## 证据边界

{_bullets(report.global_evidence_boundaries or report.evidence_boundaries)}

## 结论与下一步建议

{_bullets(report.recommendations)}
"""


def render_timeline(plan: ApprovedEvidencePlan, report: ExperimentReport) -> str:
    _validate(plan, report)
    if report.timeline_profile == "WAKE_HV" and report.semantic_timeline_events:
        approved = plan.by_key()
        sections = [f"# {report.experiment_id} 采集时间线与关键Signal", "## 实际时间线"]
        rows = []
        for event in report.semantic_timeline_events:
            evidence = "；".join(
                f"`{approved[key].signal}` / `{approved[key].can_id}`"
                for key in event.evidence_refs
            )
            significance = event.engineering_significance
            if event.event_type == "stable_window":
                significance = f"稳定窗口：{significance}"
            rows.append((event.phase or "关键事件", event.time, event.natural_summary,
                         evidence, "；".join(event.changes), significance,
                         event.local_limitation or "—"))
        sections.append(_table(
            ("阶段", "CAN时间/窗口", "实际变化", "Signal / CAN ID", "Signal值/变化",
             "工程意义", "局部限制"), rows))
        for table in report.analysis_tables + report.special_tables:
            sections.extend([f"## {table.title}", _table(table.headers, table.rows)])
        sections.append("> Event ID、raw sample time、Signal age、DLC与per-frame decode status仅保留在机器证据或工程审计中。")
        return "\n\n".join(sections) + "\n"
    headers = TIMELINE_PROFILES[report.timeline_profile]
    if report.timeline_profile == "DRIVE":
        rows = ((f"{x.time_s:.3f}".rstrip("0").rstrip("."), x.action, x.driver_input, x.request,
                 x.actual, x.motion, x.elec_power, x.pack_current, x.pack_power, x.note) for x in report.timeline)
    else:
        rows = (x.values for x in report.profile_timeline_rows)
    sections = [f"# {report.experiment_id} 采集时间线与关键Signal", "## 人读主时间线", _table(headers, rows)]
    for table in report.analysis_tables + report.special_tables:
        sections.extend([f"## {table.title}", _table(table.headers, table.rows)])
    sections.append("> 事件编号、原始采样时间、Signal age 与 DLC 仅保留在 CSV/工程审计中。")
    return "\n\n".join(sections) + "\n"


def render_signal_coverage(plan: ApprovedEvidencePlan, report: ExperimentReport) -> str:
    _validate(plan, report)
    by_key = plan.by_key()
    signals = report.coverage_signals or report.core_signals
    if report.coverage_signals:
        signals = sorted(signals, key=lambda x: (
            x.presentation_order or 10**9, by_key[x.signal_key].effective_order))
    else:
        signals = sorted(signals, key=lambda x: by_key[x.signal_key].effective_order)
    rows = []
    derived_rows = []
    for item in signals:
        approved = by_key[item.signal_key]
        if isinstance(item, CoverageSignal) and item.evidence_kind == "DERIVED":
            derived_rows.append((len(derived_rows) + 1, approved.signal,
                                 item.control_meaning or approved.effective_role,
                                 item.source or approved.message, item.observed,
                                 item.decode_status, _purpose_and_boundary(item)))
        else:
            if isinstance(item, CoverageSignal):
                rows.append((len(rows) + 1, approved.signal,
                             item.control_meaning or approved.effective_role,
                             approved.message, approved.can_id, approved.unit, item.observed,
                             item.changed, item.decode_status, _purpose_and_boundary(item)))
            else:
                rows.append((approved.effective_role, approved.signal, approved.message, approved.can_id,
                             approved.unit, item.observed, item.changed, item.decode_status, item.purpose))
    body = _table(APPROVED_COVERAGE_HEADERS if report.coverage_signals else COVERAGE_HEADERS, rows)
    issues = _bullets(report.readability_issues)
    derived = ""
    if derived_rows:
        derived = "\n\n### 非DBC派生证据\n\n" + _table(
            ("序号", "派生证据", "派生含义", "来源/统计对象", "本次观测", "验证状态",
             "本次用途/边界"), derived_rows)
    return f"# {report.experiment_id} DBC关键Signal覆盖与可读性\n\n## 核心Signal表\n\n{body}{derived}\n\n## DBC异常与可读性说明\n\n{issues}\n"


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
        # Keep rendered reports byte-stable across POSIX and Windows.  The
        # Golden hashes protect the UTF-8/LF representation, so relying on the
        # host's default newline would turn every LF into CRLF on Windows.
        path.write_text(content[key], encoding="utf-8", newline="\n")
    validate_report_bundle(report.experiment_id, output_dir, report.timeline_profile)
    return outputs


def _ordered_headings(text: str) -> tuple[str, ...]:
    return tuple(line for line in text.splitlines() if line.startswith("## ") or line.startswith("### "))


def validate_report_bundle(experiment_id: str, output_dir: Path, timeline_profile: str) -> None:
    """Validate one completed shared-renderer bundle against the human report contract."""
    if timeline_profile not in TIMELINE_PROFILES:
        raise ValueError(f"unknown timeline profile: {timeline_profile}")
    paths = tuple(output_dir / name.format(experiment_id=experiment_id) for name in STANDARD_REPORT_FILENAMES)
    missing = [path.name for path in paths if not path.is_file()]
    if missing:
        raise ValueError(f"missing standard report files: {missing}")
    final_text, timeline_text, coverage_text, audit_text = (path.read_text(encoding="utf-8") for path in paths)
    final_headings = _ordered_headings(final_text)
    judgment = tuple(x for x in final_headings if x in {"## 基线结论", "## 诊断判断"})
    if len(judgment) != 1:
        raise ValueError("final report must contain exactly one judgment heading")
    expected_final = FINAL_FIXED_HEADINGS[:3] + (judgment[0],) + FINAL_FIXED_HEADINGS[3:]
    duplicated = [heading for heading in expected_final if final_headings.count(heading) != 1]
    if duplicated:
        raise ValueError(f"final report core headings must appear exactly once: {duplicated}")
    try:
        positions = [final_headings.index(heading) for heading in expected_final]
    except ValueError as error:
        raise ValueError(f"final report is missing a Golden Contract heading: {final_headings}") from error
    if positions != sorted(positions):
        raise ValueError(f"final report headings do not satisfy Golden Contract: {final_headings}")
    timeline_lines = timeline_text.splitlines()
    if timeline_profile == "DRIVE":
        if "## 人读主时间线" not in timeline_lines:
            raise ValueError("DRIVE timeline is missing the human main timeline section")
        expected_header = "| " + " | ".join(DRIVE_TIMELINE_HEADERS) + " |"
        if expected_header not in timeline_lines:
            raise ValueError("DRIVE timeline does not use its frozen Golden header")
    elif "## 实际时间线" not in timeline_lines:
        raise ValueError("WAKE_HV timeline is missing the actual timeline section")
    for header in (line for line in timeline_lines if line.startswith("| ")):
        for field_name in FORBIDDEN_TIMELINE_FIELDS:
            if field_name in header:
                raise ValueError(f"engineering field is forbidden in human timeline: {field_name}")
    coverage_headings = tuple(line for line in coverage_text.splitlines() if line.startswith("## "))
    if coverage_headings != ("## 核心Signal表", "## DBC异常与可读性说明"):
        raise ValueError(f"coverage headings do not satisfy Golden Contract: {coverage_headings}")
    coverage_lines = coverage_text.splitlines()
    legacy_coverage = "| " + " | ".join(COVERAGE_HEADERS) + " |"
    approved_coverage = "| " + " | ".join(APPROVED_COVERAGE_HEADERS) + " |"
    if legacy_coverage not in coverage_lines and approved_coverage not in coverage_lines:
        raise ValueError("coverage report is missing its evidence-identity fields")
    if _ordered_headings(audit_text) != AUDIT_HEADINGS:
        raise ValueError("audit headings do not satisfy Golden Contract")
