# Phase 3B.2.2 — Semantic Reasoning Input & Observation Context Gap Design

**Status:** `PHASE_3B_2_2_DESIGN_COMPLETE`  
**Review gate:** `AWAITING_DESIGN_REVIEW`  
**用途：** TM3-015 正常基线/Signal Validation 方法设计；不形成新的实验结论  
**执行边界：** 仅审计现有文件并设计；未重读 ASC、未运行 Retrieval/Reasoning、未调用 LLM、未修改程序。

## 1. Executive Verdict

当前 LLM 完整获得了 Generic Fast-Charge L3 Prior，却没有真正获得 TM3-015 Collection Script / Procedure。`analysis_charter → experiment_context` 只传入 purpose、scope 和 time-policy；正式采集脚本的初始条件、计划动作、先后顺序、弹性规则、保持阶段、人工停止入口和收尾观察均未进入 Reasoning Input。

Frozen Observation Package 保留了可审计的全局统计、有限状态序列、首末变化时刻、稀疏 raw refs、DBC 来源和 Known/Residual/Unknown 来源空间；但没有保存足以重建完整行为片段的逐样本 trace。因此：

- 当前可确定性恢复基础 activity / quality context；
- 可以把正式采集脚本加入为 `PLANNED_PHASE`，但不能把它升级为 observed event；
- 不能从当前 frozen package 可靠生成完整 stable regions、major transitions、lead/lag、tracking、V×I 或累计能量闭合；
- `event_anchors` 实际只是每个 Signal 的首次 CAN 值变化，不是实验事件锚点；
- DBC lexical feature 因缺少 procedure、phase 和 relationship context 而事实上垄断 Known retrieval；
- global Observation union 允许 Finding 跨 Intent 取数，但未显式记录 direct/cross/global provenance。

推荐最小架构是：

1. **现在采用 Option B：Deterministic Observation Context Adapter**，只消费已冻结 package、正式 Collection Script 和 L3；
2. **从未来新 Discovery run 起采用窄版 Option C：Frozen Trace Store**，ASC 仍只 parse once；
3. 不为 TM3-015 回读 ASC，不把 Option A 作为当前主方案，不以调权重代替上下文恢复。

## 2. Current Pipeline Input Lineage

### 2.1 当前真实链路

```text
Generic L3 JSON ───────────────────────────────┐
                                              ├─ Analysis Charter
Charter purpose/scope/time policy ────────────┘
                                                     ↓
Frozen Observation Package + DBC summaries → SemanticSearchIntent
                                                     ↓
                                       DBC-term-heavy Retrieval
                                                     ↓
                          Global union of 26 selected Observations
                                                     ↓
                                     Semantic Reasoning Input
                                                     ↓
                               Finding → Evidence Mapping Draft

TM3-015 Collection Script ─────── X (not referenced or transported)
Observed external event record ── X (not available in this formal path)
```

### 2.2 Audited sources

- Charter: `input/TM3-015_formal_discovery_charter.json`
- Formal procedure source: `input/TM3-015_直流快充采集脚本.txt`
- Generic prior: `input/generic_dc_fast_charge_semantic_context_v2.json`
- Frozen run: `output/TM3-015/pipeline_v3/20260908-l3v2-blind-replay/`
- Audited frozen artifacts: Observation Package, Search Intents, Retrieval Results/Audit, Reasoning Input/Output, Evidence Mapping Draft, Result Quality Audit

The similarly named files under `doc/examples/` are regression examples, not the procedure referenced by the current Charter. Historical final reports were not used as input.

### 2.3 Where information is lost

| Information | Source | First loss / transformation |
|---|---|---|
| Complete Generic L3 | L3 JSON | Not lost; copied into Reasoning Input |
| Procedure source identity | Collection script | Absent from Analysis Charter |
| Planned action sequence | Collection script | Absent from Analysis Charter / Experiment Context |
| Planned windows and flexible timing | Collection script | Absent from Reasoning Input |
| Actual operator actions | Field evidence | No formal source supplied; legitimately unavailable |
| Full decoded/raw time series | ASC parse | Compressed before Observation Package freeze |
| Stable/ramp/active regions | Full trace | Not materialized in frozen package |
| Cross-observation temporal/numeric relations | Full trace | Not materialized; current “consistency” entries are candidate summaries, not general relations |
| Direct ER provenance | Retrieval Results | Weakened when Reasoning Input exposes a global union |

## 3. Fast-Charge L3 Preservation Audit

Statuses describe preservation into the formal chain, not whether evidence was found.

| L3 semantic need | Semantic context | ER / Intent | Result | Note |
|---|---|---|---|---|
| Nine-terminal physical interface | CT-01 | ER-01 / STATE | `PRESENT` | Explicit terminal set and physical/electrical boundary retained |
| Connection confirmation | CT-02 | ER-01/02 | `PRESENT` | Kept separate from contact and locking |
| Lock | CT-03 | ER-02 / REQUEST+STATE | `PRESENT` | Request/execution/feedback/confirmed state retained |
| Auxiliary LV / wake | CT-04 | ER-03 / ACTUAL+STATE | `PRESENT` | A-contact, supply, wake and ready separated |
| Digital communication / negotiation | CT-05/06 | ER-04 / TIMING_ONLY | `PARTIAL` | Prior is complete; one broad Timing-only Intent weakens link/handshake/version/parameter distinctions |
| EVSE Capability | CT-07 | ER-05 / three roles | `PRESENT` | Non-substitution rule retained |
| Vehicle / Battery State | CT-08/13/14 | distributed across ER-06/11/12 | `TRANSFORMED` | Present as constraints/context, but no dedicated Evidence Question |
| Vehicle Capability | CT-08 | ER-06 / four roles | `PRESENT` | Boundary retained |
| Vehicle Request | CT-09 | ER-07 / three roles | `PRESENT` | Voltage/current and derived-power rule retained |
| Permission / Safety Gate | CT-10 | ER-08 / three roles | `PRESENT` | Explicitly not contactor or transfer |
| HV Path | CT-11 | ER-09 / four roles | `PRESENT` | Request/action/feedback/matching/establishment retained |
| EVSE Actual | CT-12 | ER-10 / ACTUAL | `PRESENT` | Combined question, boundary still explicit |
| Pack Actual | CT-12 | ER-10 / ACTUAL | `PRESENT` | Combined question, boundary still explicit |
| Continuous Capability/Request/Actual relation | CT-13 | ER-11 / three roles | `PRESENT` | Missing roles must remain GAP |
| Thermal | CT-14 | ER-12 / three roles | `PRESENT` | Causal alternative-condition boundary retained |
| Protection / supervision | CT-14 | ER-13 / three roles | `PRESENT` | No invented fault cause |
| Controlled exit | CT-15 | ER-14 / three roles | `PRESENT` | Initiator may remain unknown |

The four mandatory constraints remain verbatim or semantically equivalent in the Reasoning Input:

```text
A± contact ≠ auxiliary supply ≠ vehicle awake
Capability ≠ Request ≠ Actual
Permission ≠ Contactor State ≠ Energy Transfer
EVSE Actual ≠ Pack Actual
```

The main L3 loss is not content deletion. It is **question-shape compression**: rich nodes and sufficiency rules become role-labelled Intents with large lexical term bags, while procedure context and executable evidence questions are absent.

## 4. Collection Script Preservation Audit

### 4.1 Formal planned procedure

The formal script describes this planned sequence:

| Planned region | Script content | Preservation |
|---|---|---|
| Initial background | 00–20 s: awake, P, unplugged, no operation; not a sleep-start experiment | `AVAILABLE_UPSTREAM_BUT_DROPPED` |
| Port-open window | 20–40 s: open charge door, do not plug | `AVAILABLE_UPSTREAM_BUT_DROPPED` |
| Connect window | 40–60 s: insert plug; record recognition and lock; real charger rules may change order | `AVAILABLE_UPSTREAM_BUT_DROPPED` |
| Authorization/start | 60–120 s: scan/authorize/pay/start; record each actual event; do not delay an early start | `AVAILABLE_UPSTREAM_BUT_DROPPED` |
| Establishment check | 120–150 s: verify actual charging using vehicle/EVSE status and current, not scan success | `AVAILABLE_UPSTREAM_BUT_DROPPED` |
| Charge observation | 150–210 s: record EVSE and Pack V/I/P, capability, SOC, temperature, LV, warnings | `AVAILABLE_UPSTREAM_BUT_DROPPED` |
| Planned steady hold | 210–240 s: 20–30 s stability if naturally available; do not prolong for the test | `AVAILABLE_UPSTREAM_BUT_DROPPED` |
| Planned stop | 240–270 s: one normal stop request; may stop earlier; record actual time and entry | `AVAILABLE_UPSTREAM_BUT_DROPPED` |
| Safe exit | 270–300 s: confirm stop/current zero/unlock before unplug; Pack current cannot prove EVSE stop | `AVAILABLE_UPSTREAM_BUT_DROPPED` |
| Tail | after unplug: recommend 30 s additional recording | `AVAILABLE_UPSTREAM_BUT_DROPPED` |

Only a generic purpose and safety time-policy survive in `experiment_context`. This is `PRESENT_BUT_WEAKENED`; the actual Procedure is not a first-class input.

### 4.2 Time semantics

- Script times are `PLANNED_TIME` only.
- No formal observed-event source is referenced by the Charter; therefore `OBSERVED_EVENT_TIME_UNAVAILABLE` and `OBSERVED_EVENT_PHASE_UNAVAILABLE` are required.
- Reasoning Input `event_anchors` are per-Signal first-change timestamps. They are `CAN_OBSERVED_TIME`, not connect/start/stop/unlock events.
- A CAN first-change anchor must not be aligned back to a planned action and then used to prove that action.

### 4.3 Consequence

Without the script, the model cannot know why the data was collected, which planned stimulus separates door-open from plug-in, why authorization can float inside a one-minute window, why “steady” is conditional, or why the stop/unplug sequence has safety prerequisites. This is an explicit:

```text
EXPERIMENT_CONTEXT_GAP
```

## 5. Observation Behavior Data-Loss Audit

| Feature | Current status | Comment |
|---|---|---|
| Sample/frame count | `AVAILABLE` | Signal and bus-variant summaries |
| Min/max/mean/std | `AVAILABLE` for numeric Known | Not applicable to enum/raw observations |
| Cardinality/dominant ratio | `AVAILABLE` for Known | Raw has payload/byte cardinality |
| Change/transition count | `AVAILABLE` for Known; bit transition counts for raw | Change count is aggregate, not a transition table |
| First/last change | `AVAILABLE` for Known | Not a phase or human-event anchor |
| Discrete state order | `PARTIAL_AVAILABLE` | `sequence` is capped; timestamps per state are absent |
| Full transition list | `REQUIRES_TRACE_STORE` | Cannot reconstruct from sparse refs |
| Stable regions | `REQUIRES_TRACE_STORE` | Global stability class is not region segmentation |
| Major step changes | `PARTIAL / REQUIRES_TRACE_STORE` | Some candidate time scopes exist; no uniform representation |
| Active/inactive regions | `REQUIRES_TRACE_STORE` | Threshold and time series needed |
| Ramp/monotonic behavior | `REQUIRES_TRACE_STORE` | Global min/max is insufficient |
| SNA/invalid/out-of-range | `AVAILABLE` for Known | Signal summary contains counts and DBC bounds |
| Raw byte/bit behavior | `AVAILABLE` as aggregates | changing bits, ones, transitions, sparse raw refs |
| Full raw/decoded samples | `REQUIRES_TRACE_STORE` | Existing refs are capped evidence samples |
| DBC source/name/unit/mux/fingerprint | `AVAILABLE` | Semantic hint only |
| Known/Residual/Unknown | `AVAILABLE` | Preserved into selected Reasoning observations |
| Unnamed/raw activity | `AVAILABLE` as aggregates | Insufficient for phase/relationship semantics |

No listed missing feature requires rereading ASC **if it had been stored during the original parse**. For this already-frozen TM3-015 package, full-region and relationship recovery would require ASC reread, which is forbidden and not justified for this phase.

## 6. Phase Context Design

Use three non-interchangeable phase types:

```text
PLANNED_PHASE
  source: frozen collection-procedure artifact
  meaning: intended stimulus/window only

OBSERVED_EVENT_PHASE
  source: field record, voice mark, independent event marker, external measurement
  current TM3-015 formal path: UNAVAILABLE

CAN_DERIVED_REGION
  source: deterministic segmentation of a frozen trace store
  neutral names only: HIGH_ACTIVITY, TRANSITION_CLUSTER, STABLE, RETURN_TOWARD_BASELINE
```

For the current frozen package, the Adapter may materialize `PLANNED_PHASE` and attach `CAN_FIRST_CHANGE` summaries, but must set:

```text
OBSERVED_EVENT_PHASE_UNAVAILABLE
CAN_REGION_DETAIL_UNAVAILABLE
```

It must not emit `HUMAN_STOP`, `REQUEST_ACCEPTED`, `PERMISSION_PHASE`, or `CHARGING_STARTED`.

## 7. Relationship Context Design

### 7.1 Availability audit

| Relationship | Frozen package now | Future trace store |
|---|---|---|
| Same bus/raw source | `DERIVABLE_FROM_FROZEN_PACKAGE` via bus key/raw refs | yes |
| DBC definition source/conflict hint | `PARTIAL` | preserve complete definition refs |
| Raw field overlap | `NOT GENERALLY AVAILABLE` | derive from frozen definition map |
| Co-transition / same-window activation | `REQUIRES_TRACE_STORE` | derive deterministically |
| Lead/lag | `REQUIRES_TRACE_STORE` | derive with explicit window/tolerance |
| Same/inverse direction tracking | `REQUIRES_TRACE_STORE` | derive with neutral metric |
| Stable ratio | `REQUIRES_TRACE_STORE` | derive with validity mask |
| Shared state boundary | `REQUIRES_TRACE_STORE` | derive from transition tables |
| V×I compatibility | `REQUIRES_TRACE_STORE` | derive only on synchronized validated units |
| Cumulative energy closure | `REQUIRES_TRACE_STORE` | derive with sampling/integration audit |
| Duplicate/independent agreement | `REQUIRES_TRACE_STORE` plus boundary metadata | no semantic confirmation |
| Source-boundary distinction | `NOT DETERMINISTICALLY INFERABLE` | L3 hypothesis + validation/human review |

Current `consistency_results` are candidate-specific anomaly/context summaries. They do not implement a general observation relationship layer and sometimes group same-message fields by DBC locality rather than physical relationship.

### 7.2 Allowed output vocabulary

The deterministic layer may output `CO_TRANSITION`, `LEADS_BY_DT`, `FOLLOWS_BY_DT`, `SAME_DIRECTION_TRACKING`, `INVERSE_TRACKING`, `VALUE_RATIO_STABLE`, `NUMERICALLY_COMPATIBLE`, `V_TIMES_I_CLOSURE`, `CUMULATIVE_DELTA_CLOSURE`, `STATE_OVERLAP`, `RAW_FIELD_OVERLAP`, and `DBC_DEFINITION_CONFLICT`.

It must never output semantic predicates such as `CAUSES`, `PERMITS`, `REQUESTS`, `ENABLES`, `IS_REQUEST`, `IS_PERMISSION`, `IS_CAPABILITY`, or `IS_ACTUAL`.

## 8. Minimal Observation Context Schema

This is a logical design, not a new committed JSON Schema:

```json
{
  "observation_ref": "...",
  "source_space": "KNOWN|RESIDUAL|UNKNOWN",
  "identity_hint": {
    "bus_key": "...",
    "raw_refs": ["..."],
    "dbc_source": "...",
    "dbc_name_hint": "...",
    "unit": "...",
    "semantic_validation_state": "UNVALIDATED"
  },
  "behavior": {
    "activity_summary": {},
    "discrete_state_summary": {},
    "major_transitions": [],
    "stable_regions": [],
    "anomaly_flags": [],
    "availability": []
  },
  "phase_alignment": {
    "planned_phase_refs": [],
    "observed_event_phase_refs": [],
    "can_region_refs": [],
    "activity_by_region": [],
    "evidence_quality": "..."
  },
  "relationships": [],
  "provenance": {
    "frozen_package_ref": "...",
    "derivation_method": "...",
    "unavailable_reasons": []
  }
}
```

Fields with no information remain empty with an explicit unavailable reason. Do not add final semantic role, priority, assessment, or expected answer.

## 9. Structured Reasoning Input Design

The next input contract should be organized per Evidence Question rather than as one global candidate pool:

```text
experiment_context
  purpose / system boundary
  procedure_source + source hash
  planned action sequence
  observed-event sources or explicit absence
  time-semantics policy

evidence_questions[]
  L3 node + ER
  generic evidence question
  role boundaries / forbidden substitutions
  relevant PLANNED_PHASE refs
  direct_candidates[]
  cross_intent_supplements[]
  global_context_refs[]
  explicit context/retrieval/evidence gaps
```

Example question shape:

```text
Need: Vehicle charging request
Procedure context: the experiment planned establishment, observation, and later stop.
Question: Is there behavior or a relationship that may represent a vehicle-side
requested voltage/current target?
Do not substitute: Capability, Permission, EVSE Actual, Pack Actual.
Limitation: planned action time is not observed event time.
```

The question is deterministically composed from Generic L3 + formal Procedure. It must not contain a known TM3-015 Signal, expected time, expected transition, or historical answer.

## 10. Direct / Cross-Intent Provenance

Every candidate presented under an ER receives one of:

- `DIRECT_INTENT_RETRIEVAL`: selected by the current Evidence Question;
- `CROSS_INTENT_SUPPLEMENT`: selected elsewhere and admitted with original Intent, current ER, supplementary reason, and relation to direct evidence;
- `GLOBAL_CONTEXT_ONLY`: visible for experiment-wide context, not a candidate for this ER.

A Finding must preserve this class per Observation. Cross-intent use without `supplementary_reason` is invalid. A global-context observation cannot appear in the Finding's support refs unless explicitly promoted to a reviewed cross-intent supplement. Evidence Mapping carries the same provenance rather than flattening it.

This design directly addresses the audited case where seven Findings consumed observations outside their mapped ER's retrieval path.

## 11. Signal-Name-Hidden Thought Experiment

No model was run. “Effect” means the expected retrieval-quality direction, not an expected semantic answer.

| Observation used to expose failure mode | Current name-hidden sufficiency | Missing context | Derivable now without ASC reread? | Expected effect / cost |
|---|---|---|---|---|
| `CP_lineVoltageRequested` | Weak: binary, four changes, first/last only | planned phases; transition table; relation to V/I actual | Script yes; full behavior/relation no | Restore candidacy if behavior aligns; low Adapter cost, trace needed |
| `UI_chargeEnableRequest` | Weak: binary, two changes | operator-source boundary; phase alignment | Script only | May downgrade UI intent or retain as alternative; low/medium |
| `CP_stopChargeRequest` | Weak: binary, repeated changes | planned stop context; actual event source; full transitions | Script yes; observed event no | Can search stop-window behavior without claiming human stop |
| `HVP_fcCtrsRequestStatus` | Weak: two-state short change interval | relation to contactor feedback/HV path | No | Could support an HV-path question as a candidate, not Permission |
| `CP_evseOutputDcCurrent` | Moderate: numeric dynamic with unit and bounded sequence | stable regions; alignment with voltage/Pack current | No | Behavior/relationship could rescue Actual candidacy; medium trace cost |
| `BMS_packCurrent` | Poor: dynamic throughout whole capture | neutral regions; synchronized Pack voltage; energy closure | No | Phase/relationship distinguishes experiment response from background load |
| `HVP_packVoltage` | Poor/moderate: bounded dynamic voltage | synchronized current and EVSE voltage; regions | No | Preserves Pack Actual boundary if compatible; medium |
| `CP_proximity` | Moderate: two changes | planned door/connect/unplug windows; observed physical record | Script only | Raises connection candidate, still not physical proof |
| `CP_latchState` | Moderate: two changes | planned connect/exit; lock request/feedback relation | Script only for coarse window | Raises lock candidate without collapsing stages |
| `BMS_contactorState` | Poor: four-state change cluster | direct ER relation, voltage matching, transfer evidence | No | Should be limited to HV-path context; not 35 of 36 Intents |
| `DAS_highLowBeamDecision` | Poor: generic state change | no plausible procedure or physical relationship | Script is sufficient negative context | Strongly downgrade as experiment-irrelevant; low |
| `VCFRONT_indicatorLeftRequest` | Poor: early rapid activity | procedure mismatch and absence of relation | Script is sufficient negative context | Strongly downgrade despite “Request” token; low |
| Residual `OBS-0005` | Weak: active only in a bounded broad interval, many changing bits | neutral regions; relation to direct candidates | Partial aggregates only | Preserve Unknown path; trace needed for discrimination |
| Unknown `OBS-0009` | Poor: near-continuous alternating pattern | heartbeat/counter discrimination; relations | Aggregate strongly suggests periodicity; full proof needs trace | Downgrade broad projection while keeping unresolved audit path |

These examples must remain design fixtures only—never a whitelist, special-case ranking table, or expected answer set.

## 12. Collection-Script Ablation Thought Experiment

### Case A — L3 + Observation + DBC

- The system knows semantic roles but not why the recording contains door-open, connect, authorization, establishment, hold, stop and exit stimuli.
- Any dynamic low-cardinality field looks broadly relevant.
- Generic lexical matches such as “Request” dominate.
- A missing candidate is indistinguishable from a retrieval-context gap.
- Planned stop and actual human stop are both unavailable, but the reason is not explicit.

### Case B — L3 + Collection Script + Observation + DBC

- The system knows which experiment stages were planned and which were conditional or movable.
- It can ask phase-aware search questions without claiming that actions occurred.
- Early indicator activity can be recognized as inconsistent with the planned charging stimulus context.
- Connection/lock/request/actual candidates have a legal behavior/context path even with a weak name.
- It can distinguish `EXPERIMENT_CONTEXT_GAP`, `RETRIEVAL_RECALL_GAP`, and true `EVIDENCE_GAP` more accurately.

The script improves interpretation of why changes might matter; it does not establish observed events or semantic roles.

## 13. Architecture Options

| Criterion | A: enrich Observation Package | B: Context Adapter | C: Frozen Trace Store |
|---|---|---|---|
| Current TM3-015 without ASC reread | Limited | Best available | Cannot retroactively populate |
| Procedure preservation | Possible but mixes Discovery concerns | Strong / explicit | Needs Adapter anyway |
| L3 independence | Good if kept separate | Strong | Strong |
| ASC parse count | One on future runs | Zero additional | One total on future runs |
| Behavior detail | Medium | Limited by frozen input | High |
| Phase/relationship detail | Medium if Discovery expands greatly | Planned phase now; trace-limited otherwise | High neutral context |
| Runtime/memory/disk | Larger Discovery package | Low | Highest disk, bounded query runtime |
| Determinism/auditability | Good | Best | Good with versioned derivations |
| Complexity | Risks Discovery expansion | Smallest change | Moderate |
| No-DBC usefulness | Moderate | Moderate now | Strong |
| Overengineering risk | High | Low | Medium if narrowly scoped |

## 14. Recommended Minimal Architecture

### Immediate: Option B

Add a deterministic Adapter between frozen artifacts and Retrieval/Reasoning Input. Its responsibilities:

1. Load a versioned Procedure artifact explicitly referenced by the Charter.
2. Preserve planned actions and flexible windows as `PLANNED_PHASE` only.
3. Wrap existing Observation aggregates in minimal `ObservationContext`.
4. Generate generic Evidence Questions from L3 + Procedure.
5. Preserve direct/cross/global provenance.
6. Emit explicit unavailable markers instead of guessing phase or relations.

### Forward-only: narrow Option C

On the next legitimate Discovery parse, freeze a bounded trace store containing timestamped decoded values, validity masks, selected raw fields, transition tables, and provenance needed for neutral window/relationship queries. Do not reparse TM3-015 solely to backfill it.

### Not recommended now

- Do not expand `observation_package-v1` into a large semantic object as the main fix.
- Do not tune `dbc_term` weights before procedure and context paths exist.
- Do not implement semantic classification in Python.

## 15. Required Architecture Decisions

1. **Complete Fast-Charge L3?** Yes, content is complete in Reasoning Input; communication and Vehicle/Battery State question shapes are partially compressed.
2. **Complete Procedure?** No.
3. **Where lost?** It is absent from the Analysis Charter and therefore never reaches experiment context, Retrieval, or Reasoning Input.
4. **Behavior retained?** Counts, ranges, cardinality, aggregate transitions, first/last change, capped state sequence, quality flags, sparse raw refs, source provenance.
5. **Behavior compressed away?** Full transitions, regional stability/activity, ramps, synchronized samples and general relations.
6. **Phase sources?** Procedure for planned phase; independent field evidence for observed-event phase; frozen trace for neutral CAN regions.
7. **Relationship layer?** Deterministic Context Adapter querying a frozen trace store, before Retrieval/Reasoning.
8. **Derivable now?** Procedure phases, global activity/quality summaries, same-bus/source facts, explicit availability gaps.
9. **Needs trace store?** Region behavior, co-transition, lead/lag, tracking, ratios, V×I and energy closure.
10. **Must reread ASC now?** No. Missing detail cannot be recovered now, but reread is not worth violating the frozen-run constraint.
11. **Retriever sees?** Evidence Question, planned context, neutral behavior/phase/relation features, DBC hint and provenance.
12. **LLM sees?** Procedure, time boundaries, per-question direct candidates, controlled supplements, Observation Context and explicit gaps.
13. **Human-only?** Semantic confirmation, role promotion, causal claims, source-boundary ownership, adequacy of external evidence, Approved Evidence decisions.
14. **Recommended option?** B now + narrow forward-only C.
15. **Smallest next slice?** Procedure contract/reference, Adapter, Evidence Question object, minimal Context object, provenance classes, synthetic tests; no ASC parser or Retrieval ranking change in the first slice.

## 16. Future Implementation Slice

Subject to design approval, the next slice should be limited to:

- a small versioned `experiment_procedure` input contract and TM3-015 procedure representation derived only from the formal script;
- Charter reference + hash validation for that procedure;
- deterministic `observation_context_adapter` consuming frozen package + L3 + procedure;
- per-ER `SemanticEvidenceQuestion` generation;
- explicit availability enums and time-type enforcement;
- `DIRECT_INTENT_RETRIEVAL / CROSS_INTENT_SUPPLEMENT / GLOBAL_CONTEXT_ONLY` provenance through Reasoning Input and Mapping;
- synthetic fixtures and contract tests.

First implementation slice should **not** change retrieval scoring, reread ASC, generate a trace store retroactively, run a blind replay, change Reasoning Output, or enter Phase 3B.3.

## 17. Future Acceptance Tests

1. Changing Generic L3 changes Evidence Questions without Signal hard-coding.
2. Changing Procedure changes planned context but not raw Observation facts.
3. Planned stop never becomes observed human stop.
4. A Signal containing “Request” is insufficient for Request/Capability/Actual candidacy.
5. Behavior has a legal path to rescue a weak-name candidate.
6. Unknown/Residual can enter through behavior/phase/relation without a DBC name.
7. Valuable request-like behavior remains retrievable under lexical competition.
8. Pack voltage/current-like behavior remains eligible through physical/relationship context.
9. Cross-intent use must preserve origin and supplementary reason.
10. Context output cannot contain semantic promotion predicates.
11. ASC parse count remains one on future trace-enabled Discovery and zero for downstream replay.
12. Historical answers are inaccessible to context generation and ranking.
13. Missing observed-event evidence emits `OBSERVED_EVENT_PHASE_UNAVAILABLE`.
14. Sparse current packages emit `CAN_REGION_DETAIL_UNAVAILABLE`, not guessed regions.
15. Name-hidden unrelated activity is downgraded by procedure mismatch without becoming deterministically `IRRELEVANT` semantic truth.

## 18. Risks and Non-goals

Risks:

- Planned phases may be misread as actual phases unless type enforcement is structural.
- A Context Adapter can become a hidden semantic classifier if its vocabulary is not restricted.
- Cross-intent supplements can recreate the current global-pool problem if admission reasons are optional.
- A trace store can become unbounded; retention and query scopes must be explicit.
- Procedure-aware filtering may suppress unexpected but valuable evidence; global context and Unknown paths must remain available.

Non-goals:

- no TM3-015 Signal whitelist or special case;
- no retrieval-weight tuning;
- no semantic role decision in Python;
- no ASC reread or retroactive trace reconstruction;
- no model call or replay;
- no Approved Evidence, Assessment, Renderer, Golden Contract, Phase 3B.3, knowledge base, cross-vehicle fingerprint, or general no-DBC reverse engineering.

## 19. Stop State

```text
PHASE_3B_2_2_DESIGN_COMPLETE
AWAITING_DESIGN_REVIEW
```

Implementation requires explicit design approval.
