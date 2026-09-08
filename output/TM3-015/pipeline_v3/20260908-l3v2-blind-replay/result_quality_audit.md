# Phase 3B.2.1 Result Quality Audit

## 1. Audit scope and verdict

This audit reads only the two frozen traces:

- Baseline: `20260907T235633-dd8ac28b` (`27 Intent / 25 Observation / 5 Finding`)
- Updated L3 replay: `20260908-l3v2-blind-replay` (`36 Intent / 26 Observation / 11 Finding`)

No ASC was read, and Retrieval, Reasoning, or any model call was not rerun.

**Verdict: the semantic result is conservative enough to remain at `AWAITING_EVIDENCE_REVIEW`, but retrieval quality is not suitable for promotion.** The expanded L3 correctly creates finer evidence gaps and prevents role collapse. However, retrieval remains strongly DBC-term-driven, the net `+1` Observation masks severe set churn, and seven Findings use at least one Observation that was admitted by an Intent outside the Finding's mapped ER. There is no confirmed answer leakage or confirmed role overstatement, but there are material retrieval-recall gaps and several possible over-interpretation paths at the draft-binding layer.

## 2. Why 27 Intent became 36

The prior changed from 10 broad ERs to 14 boundary-specific ERs. Intent IDs cannot be compared only by number because ER-02 through ER-10 were semantically reassigned.

- Exact Intent-ID delta: `22 added`, `13 removed`, net `+9`.
- Role-count delta:
  - Request: `5 → 9` (`+4`)
  - Capability: `3 → 7` (`+4`)
  - Actual: `6 → 9` (`+3`)
  - State: `7 → 8` (`+1`)
  - Permission: `3 → 2` (`-1`)
  - Timing-only: `3 → 1` (`-2`)

The increase is attributable to explicit new separation of EVSE Capability, Vehicle Capability, Vehicle Request, Permission/HV Path, cross-boundary Actual, continuous control, thermal/protection, and controlled exit. It is not caused by new experiment data.

Added Intent IDs:

`ER-02-REQUEST`; `ER-06-CAPABILITY/PERMISSION`; `ER-07-REQUEST/CAPABILITY/ACTUAL`; `ER-08-STATE`; `ER-09-REQUEST/CAPABILITY/ACTUAL`; `ER-11-REQUEST/CAPABILITY/ACTUAL`; `ER-12-REQUEST/CAPABILITY/STATE`; `ER-13-REQUEST/CAPABILITY/STATE`; `ER-14-REQUEST/ACTUAL/STATE`.

Removed Intent IDs:

`ER-03-PERMISSION/TIMING_ONLY`; `ER-04-REQUEST/CAPABILITY/ACTUAL`; `ER-06-STATE/TIMING_ONLY`; `ER-07-STATE`; `ER-08-REQUEST/CAPABILITY`; `ER-09-PERMISSION`; `ER-10-REQUEST/STATE`.

## 3. Why 25 Observation became 26

This is **not** one incremental Observation. The frozen selection changed by `16 added / 15 dropped`, leaving only 10 retained observations.

Added Known observations are mostly generic state/control-name matches: controller voltage, standby communication, status indices, contactor-set state, HVIL, unlock request, HVAC fields, a discharge-controller output, and unrelated-looking `highLowBeamDecision` / `indicatorLeftRequest` fields.

Dropped observations include materially relevant prior candidates:

- Request-labelled: `CP_lineVoltageRequested`, `UI_chargeEnableRequest`, `CP_stopChargeRequest`, `HVP_fcCtrsRequestStatus`
- Actual boundary: `CP_evseOutputDcCurrent`, `BMS_packCurrent`, `HVP_packVoltage`
- Interface/lock: `CP_proximity`, `CP_latchControlState`, `CP_latchState`, `CP_latch2ControlState`
- Exit/contact: `HVP_packCtrsOpenNowRequested`

Therefore the updated replay has a **retrieval recall regression** for Request, EVSE current, Pack Actual, and detailed connection/lock evidence. The resulting explicit gaps are epistemically safe, but some are retrieval-induced rather than evidence-absence findings.

## 4. Complete ER lineage

The Observation column is the per-ER union returned by that ER's Intent(s). `RAW-R`, `RAW-U` mean Residual and Unknown.

| L3 / ER | Intent(s) | Observation union | Finding | Binding |
|---|---|---|---|---|
| ER-01 nine-terminal / connection | STATE | contactorState; FC_status; iBoosterState; controllerVoltage; statusIndex; latch2State; RAW-R; RAW-U | `F-INTERFACE-LOCK-BOUNDARY` | `EB-0001` |
| ER-02 lock stages | REQUEST, STATE | contactorState; FC_status; statusIndex; EVSE-current-stale; packContactorSetState; vehicleUnlockRequest; iBoosterState; controllerVoltage; HVAC-power; RAW-R/U | `F-INTERFACE-LOCK-BOUNDARY` | `EB-0001` |
| ER-03 A± / auxiliary / wake | ACTUAL, STATE | LVPower checksum; highLowBeamDecision; indicatorLeftRequest; contactorState; discharge output; blower duty; FC_status; retry exceeded; initial energy; RAW-R/U | `F-AUX-WAKE-GAP` | `EB-0002` |
| ER-04 communication | TIMING_ONLY | statusIndex; UHF control; standby communication; security info index; HVAC transition reason; HVIL; RAW-R/U | `F-COMMUNICATION-STAGES-GAP` | `EB-0003` |
| ER-05 EVSE Capability | REQUEST, CAPABILITY, ACTUAL | highLowBeamDecision; indicatorLeftRequest; contactorState; FC_status; iBoosterState; controllerVoltage; LVPower checksum; discharge output; blower duty; RAW-R/U | `F-CAPABILITY-GAP` | `EB-0004` |
| ER-06 Vehicle Capability | REQUEST, CAPABILITY, ACTUAL, PERMISSION | same generic request/capability pool as ER-05 | `F-CAPABILITY-GAP` | `EB-0004` |
| ER-07 Vehicle Request | REQUEST, CAPABILITY, ACTUAL | same generic request/capability pool as ER-05 | `F-VEHICLE-REQUEST-GAP` | `EB-0005` |
| ER-08 Permission / gate | ACTUAL, PERMISSION, STATE | generic actual/request/state pool; FC status; retry; initial energy; RAW-R/U | `F-PERMISSION-HV-PATH-BOUNDARY` | `EB-0006` |
| ER-09 HV Path | REQUEST, CAPABILITY, ACTUAL, STATE | generic request/capability/state pool; retry; initial energy; RAW-R/U | `F-PERMISSION-HV-PATH-BOUNDARY` | `EB-0006` |
| ER-10 Actual boundaries | ACTUAL | LVPower checksum; highLowBeamDecision; indicatorLeftRequest; contactorState; discharge output; blower duty; RAW-R/U | `F-ACTUAL-BOUNDARY-PARTIAL` | `EB-0007` |
| ER-11 continuous relation | REQUEST, CAPABILITY, ACTUAL | same generic request/capability pool as ER-05 | `F-CONTINUOUS-CONTROL-GAP` | `EB-0008` |
| ER-12 Thermal | REQUEST, CAPABILITY, STATE | contactorState; FC/statusIndex; EVSE-current-stale; packContactorSetState; unlockRequest; EVSE voltage; iBooster/controller voltage; HVAC power; RAW-R/U | `F-THERMAL-PROTECTION-GAP` | `EB-0009` |
| ER-13 Protection | REQUEST, CAPABILITY, STATE | same pool as ER-12 | `F-THERMAL-PROTECTION-GAP` | `EB-0009` |
| ER-14 controlled exit | REQUEST, ACTUAL, STATE | generic request/actual/state pool; retry; initial energy; RAW-R/U | `F-CONTROLLED-EXIT-GAP` | `EB-0010` |
| No safe L3 mapping | source-space competition | `OBS-0010`, `OBS-0005`, `OBS-0009` | `F-RAW-UNRESOLVED` | `EB-0011` |

Important lineage caveat: the Reasoning Input exposes the global union of retrieved Observations. Consequently, a Finding can consume an Observation retrieved by another ER. The following Findings contain such cross-Intent references:

- `F-AUX-WAKE-GAP`: both referenced observations came from other ER retrieval paths.
- `F-COMMUNICATION-STAGES-GAP`: `FC_statusCode` came from other ER paths.
- `F-PERMISSION-HV-PATH-BOUNDARY`: HVIL came from ER-04; contactor-set state came from ER-02/12/13.
- `F-ACTUAL-BOUNDARY-PARTIAL`: both EVSE observations came from ER-12/13, not ER-10-ACTUAL.
- `F-CONTINUOUS-CONTROL-GAP`: EVSE voltage came from ER-12/13.
- `F-THERMAL-PROTECTION-GAP`: blower, HVIL, and retry observations came from other ER paths.
- `F-CONTROLLED-EXIT-GAP`: unlock request and EVSE voltage came from other ER paths.

This does not create an invalid reference—the observations are in the frozen global manifest—but it weakens direct `ER → Intent → Observation → Finding` provenance. A future quality gate should distinguish `DIRECT_INTENT_RETRIEVAL` from `CROSS_INTENT_GLOBAL_POOL` before promotion.

## 5. Finding change classification

| Updated Finding | Classification | Explanation |
|---|---|---|
| `F-INTERFACE-LOCK-BOUNDARY` | `REFINED`, `SPLIT_BY_NEW_L3`, `RETRIEVAL_RECALL_GAP` | Preserves the former connection/lock caution and separates ER-01/02, but loses four prior proximity/latch observations. |
| `F-AUX-WAKE-GAP` | `NEW_SEMANTIC_NEED`, `POSSIBLE_OVER_INTERPRETATION` | New A±/auxiliary/wake boundary. Its two observations were imported cross-Intent and do not directly retrieve for ER-03; the Finding remains cautious. |
| `F-COMMUNICATION-STAGES-GAP` | `NEW_SEMANTIC_NEED`, `POSSIBLE_OVER_INTERPRETATION` | New handshake/version/parameter requirement. Labels only support a gap, not protocol stages; one observation is cross-Intent. |
| `F-CAPABILITY-GAP` | `PRESERVED`, `REFINED` | Former Capability gap is retained and split into EVSE and Vehicle Capability. No role substitution occurs. |
| `F-VEHICLE-REQUEST-GAP` | `DROPPED_AS_UNSUPPORTED`, `RETRIEVAL_RECALL_GAP` | The former Request candidate finding is replaced by an explicit gap. This is safe, but request-labelled observations disappeared from retrieval. |
| `F-PERMISSION-HV-PATH-BOUNDARY` | `NEW_SEMANTIC_NEED`, `SPLIT_BY_NEW_L3`, `POSSIBLE_OVER_INTERPRETATION` | Correctly separates Permission, contactor, path, and transfer; two of three observations came through unrelated Intent paths. |
| `F-ACTUAL-BOUNDARY-PARTIAL` | `REFINED`, `RETRIEVAL_RECALL_GAP` | Preserves Actual semantics and strengthens boundary separation, but loses EVSE-current magnitude and both Pack Actual observations. The staleness flag is correctly not treated as current. |
| `F-CONTINUOUS-CONTROL-GAP` | `NEW_SEMANTIC_NEED`, `SPLIT_BY_NEW_L3`, `RETRIEVAL_RECALL_GAP` | New continuous-relation ER. Correctly reports missing roles; its sole observation was retrieved elsewhere. |
| `F-THERMAL-PROTECTION-GAP` | `SPLIT_BY_NEW_L3`, `POSSIBLE_OVER_INTERPRETATION` | Expands the former thermal ER into thermal plus protection. Cabin-HVAC and AC-retry labels are weak DC-charge evidence; alternatives and gaps prevent assertion, but the combined binding may visually imply relevance. |
| `F-CONTROLLED-EXIT-GAP` | `SPLIT_BY_NEW_L3`, `RETRIEVAL_RECALL_GAP`, `POSSIBLE_OVER_INTERPRETATION` | Refines the former stop/exit need. Stop-request and Pack/EVSE-current observations were dropped; two references are cross-Intent and phase is unavailable. |
| `F-RAW-UNRESOLVED` | `PRESERVED` | Same Residual/Unknown set remains explicitly unmapped with phase and relationship gaps. |

No updated Finding warrants a confirmed semantic role. The three `HUMAN_REVIEW_REQUIRED` bindings are appropriately not promoted; the remaining eight are `HOLD_UNRESOLVED`.

## 6. Is DBC term still dominating retrieval?

**Yes—decisively.**

- Updated trace contains 288 Intent–Observation placements (`36 × 8`).
- Known placements: `216/288` (75%).
- Every Known placement (`216/216`) has a non-zero `dbc_term` component.
- DBC term contributes `40` points, compared with `15` for dynamic behavior and `10` for low-cardinality state in the common 65-point pattern.
- Phase and relationship contribute `0` everywhere because those features are unavailable.
- Residual/Unknown slots are repeatedly filled by activity scoring, not semantic relationship evidence.

The strongest symptom is projection breadth:

- `BMS_contactorState`: 35 of 36 Intents
- `DAS_highLowBeamDecision`: 26 Intents
- `VCFRONT_indicatorLeftRequest`: 26 Intents
- `FC_statusCode`: 21 Intents
- Unknown `OBS-0009`: all 36 Intents

The presence of `highLowBeamDecision` and `indicatorLeftRequest` across Capability, Actual, Request, Permission, and State intents shows that broad shared DBC terms—especially generic words such as request/state/actual/control—are dominating semantic specificity. The result is high recall in the mechanical sense of filling every Intent (`no_suitable_observation=0`) but low precision for the requested semantic need.

## 7. Multi-semantic projection and over-interpretation audit

Retrieval-level multi-projection is extensive and cannot be read as multi-role evidence. The same Observation being ranked for many roles is primarily a consequence of broad DBC-term overlap and absent phase/relationship features.

Finding-level reuse is narrower:

- EVSE-voltage candidate: 3 Findings (`Actual`, continuous-control gap, controlled-exit gap)
- contactor state: 2 Findings (HV-path boundary, controlled-exit gap)
- standby communication: 2 Findings (aux/wake gap, communication gap)
- unlock request: 2 Findings (lock boundary, controlled-exit gap)
- HVIL: 2 Findings (permission/HV path, thermal/protection)

No Finding claims that one observation simultaneously proves these roles. Wording consistently uses “candidate”, “does not prove”, or an explicit gap, so **confirmed semantic over-interpretation is not present**. Nevertheless, `POSSIBLE_OVER_INTERPRETATION` applies where cross-Intent observations are packaged into an ER binding, particularly auxiliary/wake, communication, thermal/protection, and controlled exit. A reviewer could mistake binding membership or raw-reference closure for positive relevance.

## 8. Final quality decision

- Semantic boundary discipline: **PASS**
- Frozen-reference validity: **PASS**
- Explicit evidence-gap behavior: **PASS**
- DBC-name independence: **FAIL / material weakness**
- Per-ER retrieval precision: **FAIL / material weakness**
- Request and Pack Actual recall versus baseline: **FAIL / regression**
- Finding epistemic restraint: **PASS**
- Direct ER-to-Observation lineage: **PARTIAL** because cross-Intent global-pool consumption is not distinguished
- Promotion readiness: **NO**

The correct terminal state remains `AWAITING_EVIDENCE_REVIEW`. Do not interpret the increase from 5 to 11 Findings as more evidence: it mainly reflects decomposition of new L3 semantic needs into explicit gaps. Do not enter Phase 3B.3 from this result without a separate decision on retrieval precision, per-Intent provenance, and recall of the dropped Request/Actual/interface candidates.
