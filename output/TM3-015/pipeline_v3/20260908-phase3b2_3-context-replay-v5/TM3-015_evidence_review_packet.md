# TM3-015 Evidence Review Packet

> Packet version: `human-evidence-review-packet-v1`  
> Status: `AWAITING_EVIDENCE_REVIEW`  
> Downstream presentation only — not analysis input, not Approved Evidence, and not a human review submission.

## Reading boundary

DBC sections are labelled **REFERENCE — NOT EVIDENCE BY ITSELF**. A DBC name is a decode/semantic hint, not proof of a role. CAN timestamps below are observed CAN-state times; planned procedure times are not human action times.

## ER-01 — Distinguish nine-terminal mechanical interface conditions from confirmed physical connection

- Control Tree: `CT-DCFC-03`
- Binding / Finding: `EB-0001` / `F-3B23-01`
- Semantic status / confidence: `VALIDATION_REQUIRED` / `MEDIUM`
- Program review state: `HUMAN_REVIEW_REQUIRED`; human disposition: **UNSET**

### L3 question

Distinguish nine-terminal mechanical interface conditions from confirmed physical connection.

Sufficiency boundary: Independent evidence is required for mechanical contact and connection confirmation.

### Direct Finding evidence

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-7BB7F570959A | KNOWN | 0x21D | CP_evseStatus | CP_proximity | CP_evseStatus / CP_proximity / enum={"0": "SNA", "1": "DISCONNECTED", "2": "UNLATCHED", "3": "LATCHED"} | stability=LOW_CARDINALITY; changes=2; first change=39.7192 s (CAN observed state time); last change=273.5338 s (CAN observed state time); sequence=SNA → DISCONNECTED → SNA | DIRECT_INTENT_RETRIEVAL |
| SO-AFC76E33264C | KNOWN | 0x25D | CP_status | CP_latchState | CP_status / CP_latchState / enum={"0": "SNA", "1": "DISENGAGED", "2": "ENGAGED", "3": "BLOCKING"} | stability=LOW_CARDINALITY; changes=2; first change=20.7178 s (CAN observed state time); last change=278.635 s (CAN observed state time); sequence=DISENGAGED → BLOCKING → DISENGAGED | DIRECT_INTENT_RETRIEVAL |

### Other retrieved candidates

These remain visible for review but were **not** used as Finding support.

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-BA9225550260 | KNOWN | 0x339 | VCSEC_authentication | VCSEC_chargePortLockStatus | VCSEC_authentication / VCSEC_chargePortLockStatus / enum={"0": "UNLOCKED", "1": "LOCKED"} | stability=LOW_CARDINALITY; changes=0; sequence=UNLOCKED | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-57834B9DC181 | KNOWN | 0x25D | CP_status | CP_latch2ControlState | CP_status / CP_latch2ControlState / enum={"0": "latchInit", "1": "latchIdle", "2": "latchDisengageRequested", "3": "latchDisengaging", "4": "latchDisengaged", "5": "latchEngaging"} | stability=LOW_CARDINALITY; changes=7; first change=21.0173 s (CAN observed state time); last change=277.2349 s (CAN observed state time); sequence=latchInit → latchDisengaged → latchDisengaging → latchDisengageRequested → latchEngaging → latchDisengaging → latchDisengaged → latchInit | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-7C154FF11732 | KNOWN | 0x25D | CP_status | CP_latchControlState | CP_status / CP_latchControlState / enum={"0": "latchInit", "1": "latchIdle", "2": "latchDisengageRequested", "3": "latchDisengaging", "4": "latchDisengaged", "5": "latchEngaging"} | stability=LOW_CARDINALITY; changes=10; first change=21.0173 s (CAN observed state time); last change=277.1347 s (CAN observed state time); sequence=latchIdle → latchDisengaging → latchDisengaged → latchEngaging → latchIdle → latchDisengaging → latchDisengaged → latchDisengaging … | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-0CCE9DD26636 | KNOWN | 0x102 | VCLEFT_doorStatus | VCLEFT_frontLatchSwitch | VCLEFT_doorStatus / VCLEFT_frontLatchSwitch | stability=CONSTANT; changes=0; range=1.0..1.0; sequence=1 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0096 | UNKNOWN | 0x2BE | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=145; bit transitions=754 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0005 | RESIDUAL | 0x108 | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=133; bit transitions=11311 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |

### DBC Semantic Reference — REFERENCE — NOT EVIDENCE BY ITSELF

- `SO-7BB7F570959A`: CP_evseStatus / CP_proximity / enum={"0": "SNA", "1": "DISCONNECTED", "2": "UNLATCHED", "3": "LATCHED"}
- `SO-AFC76E33264C`: CP_status / CP_latchState / enum={"0": "SNA", "1": "DISENGAGED", "2": "ENGAGED", "3": "BLOCKING"}
- `SO-BA9225550260`: VCSEC_authentication / VCSEC_chargePortLockStatus / enum={"0": "UNLOCKED", "1": "LOCKED"}
- `SO-57834B9DC181`: CP_status / CP_latch2ControlState / enum={"0": "latchInit", "1": "latchIdle", "2": "latchDisengageRequested", "3": "latchDisengaging", "4": "latchDisengaged", "5": "latchEngaging"}
- `SO-7C154FF11732`: CP_status / CP_latchControlState / enum={"0": "latchInit", "1": "latchIdle", "2": "latchDisengageRequested", "3": "latchDisengaging", "4": "latchDisengaged", "5": "latchEngaging"}
- `SO-0CCE9DD26636`: VCLEFT_doorStatus / VCLEFT_frontLatchSwitch

This is **REFERENCE ONLY — NOT OBSERVED CONTROL CHAIN — NOT APPROVED EVIDENCE**.

### ASC observed behavior

- `SO-7BB7F570959A`: stability=LOW_CARDINALITY; changes=2; first change=39.7192 s (CAN observed state time); last change=273.5338 s (CAN observed state time); sequence=SNA → DISCONNECTED → SNA
- `SO-AFC76E33264C`: stability=LOW_CARDINALITY; changes=2; first change=20.7178 s (CAN observed state time); last change=278.635 s (CAN observed state time); sequence=DISENGAGED → BLOCKING → DISENGAGED
- Phase Feature: **UNAVAILABLE**. Planned windows provide context only and do not establish observed human event time.
- Relationship Evidence: **CURRENTLY LIMITED**. The frozen Observation Package does not contain synchronized cross-signal relationship features required to establish this relation.

### AI interpretation

- **OBSERVED**: Interface proximity and latch observations change, but they do not independently confirm all nine-terminal mechanical contact or physical connection.

### Currently supported

- ✓ Program mapping status is `PARTIAL_SUPPORT` for the bounded statement above; Signal Validation remains required.

### Not established

- ✗ Independent physical connection confirmation and observed connection time are absent.

### Evidence gap

- Gap: `GAP-3B23-01`
- Missing evidence type: `PHYSICAL_MEASUREMENT`
- Why it matters: Independent physical connection confirmation and observed connection time are absent.

### Collection limitation

The collection predates the current Evidence architecture. Missing physical measurements or human event timestamps are not reconstructed from DBC labels or planned times.

### Audit trace

- Observation refs: `SO-7BB7F570959A, SO-AFC76E33264C`
- Candidate refs: `NONE`
- Raw ASC refs: `ASC-L35, ASC-L37, ASC-L43668, ASC-L634387, ASC-L644481, ASC-L685438, ASC-L685440, ASC-L83365`
- Reasoning package: `TM3-015-reasoning-f2f9203de6d5494d` / `1da118c87ee9299a4eb8e84a697edf652edec81741ad07dee9a82a76f5a1ad15`
- Reasoning result: `TM3-015-phase3b2_3-context-blind-replay-v5`

## ER-02 — Distinguish connection confirmation from lock request, lock execution, lock feedback, and confirmed lock

- Control Tree: `CT-DCFC-03`
- Binding / Finding: `EB-0002` / `F-3B23-02`
- Semantic status / confidence: `VALIDATION_REQUIRED` / `MEDIUM`
- Program review state: `HUMAN_REVIEW_REQUIRED`; human disposition: **UNSET**

### L3 question

Distinguish connection confirmation from lock request, lock execution, lock feedback, and confirmed lock.

Sufficiency boundary: A single state label cannot satisfy all locking stages.

### Direct Finding evidence

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-57834B9DC181 | KNOWN | 0x25D | CP_status | CP_latch2ControlState | CP_status / CP_latch2ControlState / enum={"0": "latchInit", "1": "latchIdle", "2": "latchDisengageRequested", "3": "latchDisengaging", "4": "latchDisengaged", "5": "latchEngaging"} | stability=LOW_CARDINALITY; changes=7; first change=21.0173 s (CAN observed state time); last change=277.2349 s (CAN observed state time); sequence=latchInit → latchDisengaged → latchDisengaging → latchDisengageRequested → latchEngaging → latchDisengaging → latchDisengaged → latchInit | DIRECT_INTENT_RETRIEVAL |
| SO-7C154FF11732 | KNOWN | 0x25D | CP_status | CP_latchControlState | CP_status / CP_latchControlState / enum={"0": "latchInit", "1": "latchIdle", "2": "latchDisengageRequested", "3": "latchDisengaging", "4": "latchDisengaged", "5": "latchEngaging"} | stability=LOW_CARDINALITY; changes=10; first change=21.0173 s (CAN observed state time); last change=277.1347 s (CAN observed state time); sequence=latchIdle → latchDisengaging → latchDisengaged → latchEngaging → latchIdle → latchDisengaging → latchDisengaged → latchDisengaging … | DIRECT_INTENT_RETRIEVAL |
| SO-AFC76E33264C | KNOWN | 0x25D | CP_status | CP_latchState | CP_status / CP_latchState / enum={"0": "SNA", "1": "DISENGAGED", "2": "ENGAGED", "3": "BLOCKING"} | stability=LOW_CARDINALITY; changes=2; first change=20.7178 s (CAN observed state time); last change=278.635 s (CAN observed state time); sequence=DISENGAGED → BLOCKING → DISENGAGED | DIRECT_INTENT_RETRIEVAL |

### Other retrieved candidates

These remain visible for review but were **not** used as Finding support.

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-BA9225550260 | KNOWN | 0x339 | VCSEC_authentication | VCSEC_chargePortLockStatus | VCSEC_authentication / VCSEC_chargePortLockStatus / enum={"0": "UNLOCKED", "1": "LOCKED"} | stability=LOW_CARDINALITY; changes=0; sequence=UNLOCKED | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-23B9FBB08D32 | KNOWN | 0x142 | VCLEFT_liftgateStatus | VCLEFT_liftgateLatchRequest | VCLEFT_liftgateStatus / VCLEFT_liftgateLatchRequest / enum={"0": "LATCH_REQUEST_NONE", "1": "LATCH_REQUEST_CINCH", "2": "LATCH_REQUEST_RELEASE", "3": "LATCH_REQUEST_FORCE_RELEASE", "4": "LATCH_REQUEST_RESET"} | stability=LOW_CARDINALITY; changes=0; sequence=LATCH_REQUEST_NONE | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-30E936829754 | KNOWN | 0x1F9 | VCSEC_requests | VCSEC_chargePortRequest | VCSEC_requests / VCSEC_chargePortRequest / enum={"0": "NONE", "1": "OPEN", "2": "CLOSE", "3": "SNA"} | stability=LOW_CARDINALITY; changes=2; first change=268.6751 s (CAN observed state time); last change=268.9751 s (CAN observed state time); sequence=NONE → OPEN → NONE | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0005 | RESIDUAL | 0x108 | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=133; bit transitions=11311 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0012 | UNKNOWN | 0x128 | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=5; bit transitions=9 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |

### DBC Semantic Reference — REFERENCE — NOT EVIDENCE BY ITSELF

- `SO-57834B9DC181`: CP_status / CP_latch2ControlState / enum={"0": "latchInit", "1": "latchIdle", "2": "latchDisengageRequested", "3": "latchDisengaging", "4": "latchDisengaged", "5": "latchEngaging"}
- `SO-7C154FF11732`: CP_status / CP_latchControlState / enum={"0": "latchInit", "1": "latchIdle", "2": "latchDisengageRequested", "3": "latchDisengaging", "4": "latchDisengaged", "5": "latchEngaging"}
- `SO-AFC76E33264C`: CP_status / CP_latchState / enum={"0": "SNA", "1": "DISENGAGED", "2": "ENGAGED", "3": "BLOCKING"}
- `SO-BA9225550260`: VCSEC_authentication / VCSEC_chargePortLockStatus / enum={"0": "UNLOCKED", "1": "LOCKED"}
- `SO-23B9FBB08D32`: VCLEFT_liftgateStatus / VCLEFT_liftgateLatchRequest / enum={"0": "LATCH_REQUEST_NONE", "1": "LATCH_REQUEST_CINCH", "2": "LATCH_REQUEST_RELEASE", "3": "LATCH_REQUEST_FORCE_RELEASE", "4": "LATCH_REQUEST_RESET"}
- `SO-30E936829754`: VCSEC_requests / VCSEC_chargePortRequest / enum={"0": "NONE", "1": "OPEN", "2": "CLOSE", "3": "SNA"}

This is **REFERENCE ONLY — NOT OBSERVED CONTROL CHAIN — NOT APPROVED EVIDENCE**.

### ASC observed behavior

- `SO-57834B9DC181`: stability=LOW_CARDINALITY; changes=7; first change=21.0173 s (CAN observed state time); last change=277.2349 s (CAN observed state time); sequence=latchInit → latchDisengaged → latchDisengaging → latchDisengageRequested → latchEngaging → latchDisengaging → latchDisengaged → latchInit
- `SO-7C154FF11732`: stability=LOW_CARDINALITY; changes=10; first change=21.0173 s (CAN observed state time); last change=277.1347 s (CAN observed state time); sequence=latchIdle → latchDisengaging → latchDisengaged → latchEngaging → latchIdle → latchDisengaging → latchDisengaged → latchDisengaging …
- `SO-AFC76E33264C`: stability=LOW_CARDINALITY; changes=2; first change=20.7178 s (CAN observed state time); last change=278.635 s (CAN observed state time); sequence=DISENGAGED → BLOCKING → DISENGAGED
- Phase Feature: **UNAVAILABLE**. Planned windows provide context only and do not establish observed human event time.
- Relationship Evidence: **CURRENTLY LIMITED**. The frozen Observation Package does not contain synchronized cross-signal relationship features required to establish this relation.

### AI interpretation

- **OBSERVED**: Latch control and latch feedback states are observable, but the evidence does not establish every request, execution, feedback, and confirmed-lock stage.

### Currently supported

- ✓ Program mapping status is `PARTIAL_SUPPORT` for the bounded statement above; Signal Validation remains required.

### Not established

- ✗ No independent lock confirmation or observed lock action time binds the stages.

### Evidence gap

- Gap: `GAP-3B23-02`
- Missing evidence type: `EXTERNAL_EVENT_TIME`
- Why it matters: No independent lock confirmation or observed lock action time binds the stages.

### Collection limitation

The collection predates the current Evidence architecture. Missing physical measurements or human event timestamps are not reconstructed from DBC labels or planned times.

### Audit trace

- Observation refs: `SO-57834B9DC181, SO-7C154FF11732, SO-AFC76E33264C`
- Candidate refs: `NONE`
- Raw ASC refs: `ASC-L240255, ASC-L289270, ASC-L37, ASC-L43668, ASC-L44302, ASC-L44727, ASC-L577111, ASC-L624672, ASC-L625080, ASC-L633371, ASC-L641708, ASC-L644481, ASC-L685440, ASC-L85894, ASC-L86314`
- Reasoning package: `TM3-015-reasoning-f2f9203de6d5494d` / `1da118c87ee9299a4eb8e84a697edf652edec81741ad07dee9a82a76f5a1ad15`
- Reasoning result: `TM3-015-phase3b2_3-context-blind-replay-v5`

## ER-03 — Distinguish A+ and A- contact, auxiliary supply establishment, actual controller wake, and charge-ready state

- Control Tree: `CT-DCFC-04`
- Binding / Finding: `EB-0003` / `F-3B23-03`
- Semantic status / confidence: `INSUFFICIENT_EVIDENCE` / `LOW`
- Program review state: `HOLD_UNRESOLVED`; human disposition: **UNSET**

### L3 question

Distinguish A+ and A- contact, auxiliary supply establishment, actual controller wake, and charge-ready state.

Sufficiency boundary: Downstream activity alone does not prove each upstream condition.

### Direct Finding evidence

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-1DA23ED17AA5 | KNOWN | 0x2B4 | PCS_dcdcBusStatus | PCS_dcdcLvBusVolt | PCS_dcdcBusStatus / PCS_dcdcLvBusVolt / unit=V | stability=DYNAMIC; changes=2313; range=8.2421875..13.0859375; first change=0.131 s (CAN observed state time); last change=299.6131 s (CAN observed state time); sequence=10.7421875 → 10.78125 → 10.7421875 → 10.703125 → 10.6640625 → 10.7421875 → 10.78125 → 10.5859375 … | DIRECT_INTENT_RETRIEVAL |
| SO-61297290B6D1 | KNOWN | 0x2B4 | PCS_dcdcBusStatus | PCS_dcdcLvOutputCurrent | PCS_dcdcBusStatus / PCS_dcdcLvOutputCurrent / unit=A | stability=DYNAMIC; changes=2545; range=0.0..385.40000000000003; first change=0.2306 s (CAN observed state time); last change=299.7131 s (CAN observed state time); sequence=385.3 → 282.90000000000003 → 1.3 → 231.70000000000002 → 52.5 → 26.900000000000002 → 52.5 → 206.10000000000002 … | DIRECT_INTENT_RETRIEVAL |

### Other retrieved candidates

These remain visible for review but were **not** used as Finding support.

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-3DDFDF668229 | KNOWN | 0x221 | VCFRONT_LVPowerState | VCFRONT_tunerLVRequest | VCFRONT_LVPowerState / VCFRONT_tunerLVRequest / enum={"0": "OFF", "1": "ON", "2": "GOING_DOWN", "3": "FAULT"} | stability=LOW_CARDINALITY; changes=1; first change=97.7415 s (CAN observed state time); last change=97.7415 s (CAN observed state time); sequence=GOING_DOWN → OFF | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-DC02A406ACBE | KNOWN | 0x221 | VCFRONT_LVPowerState | VCFRONT_iBoosterLVState | VCFRONT_LVPowerState / VCFRONT_iBoosterLVState / enum={"0": "OFF", "1": "ON", "2": "GOING_DOWN", "3": "FAULT"} | stability=LOW_CARDINALITY; changes=1; first change=90.6408 s (CAN observed state time); last change=90.6408 s (CAN observed state time); sequence=GOING_DOWN → OFF | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-00672B1A0092 | KNOWN | 0x221 | VCFRONT_LVPowerState | VCFRONT_uiHiCurrentLVState | VCFRONT_LVPowerState / VCFRONT_uiHiCurrentLVState / enum={"0": "OFF", "1": "ON", "2": "GOING_DOWN", "3": "FAULT"} | stability=LOW_CARDINALITY; changes=0; sequence=ON | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-02D3DB13AB41 | KNOWN | 0x221 | VCFRONT_LVPowerState | VCFRONT_LVPowerStateChecksum | VCFRONT_LVPowerState / VCFRONT_LVPowerStateChecksum | stability=DYNAMIC; changes=5993; range=2.0..254.0; first change=0.0852 s (CAN observed state time); last change=299.7038 s (CAN observed state time); sequence=79 → 158 → 111 → 190 → 143 → 222 → 175 → 254 … | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0086 | UNKNOWN | 0x2A3 | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=179; bit transitions=491 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0005 | RESIDUAL | 0x108 | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=133; bit transitions=11311 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |

### DBC Semantic Reference — REFERENCE — NOT EVIDENCE BY ITSELF

- `SO-1DA23ED17AA5`: PCS_dcdcBusStatus / PCS_dcdcLvBusVolt / unit=V
- `SO-61297290B6D1`: PCS_dcdcBusStatus / PCS_dcdcLvOutputCurrent / unit=A
- `SO-3DDFDF668229`: VCFRONT_LVPowerState / VCFRONT_tunerLVRequest / enum={"0": "OFF", "1": "ON", "2": "GOING_DOWN", "3": "FAULT"}
- `SO-DC02A406ACBE`: VCFRONT_LVPowerState / VCFRONT_iBoosterLVState / enum={"0": "OFF", "1": "ON", "2": "GOING_DOWN", "3": "FAULT"}
- `SO-00672B1A0092`: VCFRONT_LVPowerState / VCFRONT_uiHiCurrentLVState / enum={"0": "OFF", "1": "ON", "2": "GOING_DOWN", "3": "FAULT"}
- `SO-02D3DB13AB41`: VCFRONT_LVPowerState / VCFRONT_LVPowerStateChecksum

This is **REFERENCE ONLY — NOT OBSERVED CONTROL CHAIN — NOT APPROVED EVIDENCE**.

### ASC observed behavior

- `SO-1DA23ED17AA5`: stability=DYNAMIC; changes=2313; range=8.2421875..13.0859375; first change=0.131 s (CAN observed state time); last change=299.6131 s (CAN observed state time); sequence=10.7421875 → 10.78125 → 10.7421875 → 10.703125 → 10.6640625 → 10.7421875 → 10.78125 → 10.5859375 …
- `SO-61297290B6D1`: stability=DYNAMIC; changes=2545; range=0.0..385.40000000000003; first change=0.2306 s (CAN observed state time); last change=299.7131 s (CAN observed state time); sequence=385.3 → 282.90000000000003 → 1.3 → 231.70000000000002 → 52.5 → 26.900000000000002 → 52.5 → 206.10000000000002 …
- Phase Feature: **UNAVAILABLE**. Planned windows provide context only and do not establish observed human event time.
- Relationship Evidence: **CURRENTLY LIMITED**. The frozen Observation Package does not contain synchronized cross-signal relationship features required to establish this relation.

### AI interpretation

- **OBSERVED**: Low-voltage bus observations show electrical activity, but do not distinguish A-terminal contact, auxiliary supply establishment, controller wake, and charge-ready state.

### Currently supported

- No direct semantic support is accepted by the program; displayed observations remain candidates only.

### Not established

- ✗ The required upstream interface and wake boundaries are not directly observed.

### Evidence gap

- Gap: `GAP-3B23-03`
- Missing evidence type: `PHYSICAL_MEASUREMENT`
- Why it matters: The required upstream interface and wake boundaries are not directly observed.

### Collection limitation

The collection predates the current Evidence architecture. Missing physical measurements or human event timestamps are not reconstructed from DBC labels or planned times.

### Audit trace

- Observation refs: `SO-1DA23ED17AA5, SO-61297290B6D1`
- Candidate refs: `NONE`
- Raw ASC refs: `ASC-L1133, ASC-L1557, ASC-L1764, ASC-L1987, ASC-L277356, ASC-L281590, ASC-L285, ASC-L324946, ASC-L402260, ASC-L495, ASC-L685596, ASC-L709, ASC-L72, ASC-L921`
- Reasoning package: `TM3-015-reasoning-f2f9203de6d5494d` / `1da118c87ee9299a4eb8e84a697edf652edec81741ad07dee9a82a76f5a1ad15`
- Reasoning result: `TM3-015-phase3b2_3-context-blind-replay-v5`

## ER-04 — Identify communication link, handshake or initialization, version compatibility, and parameter exchange where observable

- Control Tree: `CT-DCFC-05`
- Binding / Finding: `EB-0004` / `F-3B23-04`
- Semantic status / confidence: `INSUFFICIENT_EVIDENCE` / `LOW`
- Program review state: `HOLD_UNRESOLVED`; human disposition: **UNSET**

### L3 question

Identify communication link, handshake or initialization, version compatibility, and parameter exchange where observable.

Sufficiency boundary: Generic protocol stages do not prove a fixed internal ECU sequence or unobserved protocol messages.

### Direct Finding evidence

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-11F964A63B77 | KNOWN | 0x2C1 | VCFRONT_logging10Hz | VCFRONT_compStandbyCommunication | VCFRONT_logging10Hz / VCFRONT_compStandbyCommunication | stability=LOW_CARDINALITY; changes=8; range=0.0..1.0; first change=11.3499 s (CAN observed state time); last change=20.7507 s (CAN observed state time); sequence=1 → 0 → 1 → 0 → 1 → 0 → 1 → 0 … | DIRECT_INTENT_RETRIEVAL |

### Other retrieved candidates

These remain visible for review but were **not** used as Finding support.

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-0E3BF055E63D | KNOWN | 0x38D | TAS_warningMatrix3 | TAS_w164_calibrationVersion | TAS_warningMatrix3 / TAS_w164_calibrationVersion | stability=LOW_CARDINALITY; changes=2; range=0.0..1.0; first change=173.1074 s (CAN observed state time); last change=194.1071 s (CAN observed state time); sequence=1 → 0 → 1 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0086 | UNKNOWN | 0x2A3 | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=179; bit transitions=491 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0005 | RESIDUAL | 0x108 | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=133; bit transitions=11311 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |

### DBC Semantic Reference — REFERENCE — NOT EVIDENCE BY ITSELF

- `SO-11F964A63B77`: VCFRONT_logging10Hz / VCFRONT_compStandbyCommunication
- `SO-0E3BF055E63D`: TAS_warningMatrix3 / TAS_w164_calibrationVersion

This is **REFERENCE ONLY — NOT OBSERVED CONTROL CHAIN — NOT APPROVED EVIDENCE**.

### ASC observed behavior

- `SO-11F964A63B77`: stability=LOW_CARDINALITY; changes=8; range=0.0..1.0; first change=11.3499 s (CAN observed state time); last change=20.7507 s (CAN observed state time); sequence=1 → 0 → 1 → 0 → 1 → 0 → 1 → 0 …
- Phase Feature: **UNAVAILABLE**. Planned windows provide context only and do not establish observed human event time.
- Relationship Evidence: **CURRENTLY LIMITED**. The frozen Observation Package does not contain synchronized cross-signal relationship features required to establish this relation.

### AI interpretation

- **OBSERVED**: A generic communication-related state is present, but it does not establish charging handshake, version compatibility, or parameter exchange.

### Currently supported

- No direct semantic support is accepted by the program; displayed observations remain candidates only.

### Not established

- ✗ The retrieved DBC term is not validated as the fast-charge protocol exchange.

### Evidence gap

- Gap: `GAP-3B23-04`
- Missing evidence type: `SIGNAL_VALIDATION`
- Why it matters: The retrieved DBC term is not validated as the fast-charge protocol exchange.

### Collection limitation

The collection predates the current Evidence architecture. Missing physical measurements or human event timestamps are not reconstructed from DBC labels or planned times.

### Audit trace

- Observation refs: `SO-11F964A63B77`
- Candidate refs: `NONE`
- Raw ASC refs: `ASC-L123, ASC-L24082, ASC-L25757, ASC-L27425, ASC-L29093, ASC-L38512, ASC-L40196, ASC-L42073, ASC-L685505`
- Reasoning package: `TM3-015-reasoning-f2f9203de6d5494d` / `1da118c87ee9299a4eb8e84a697edf652edec81741ad07dee9a82a76f5a1ad15`
- Reasoning result: `TM3-015-phase3b2_3-context-blind-replay-v5`

## ER-05 — Identify EVSE Capability without substituting Vehicle Capability, Vehicle Request, or Actual

- Control Tree: `CT-DCFC-07`
- Binding / Finding: `EB-0005` / `F-3B23-05`
- Semantic status / confidence: `INSUFFICIENT_EVIDENCE` / `LOW`
- Program review state: `HOLD_UNRESOLVED`; human disposition: **UNSET**

### L3 question

Identify EVSE Capability without substituting Vehicle Capability, Vehicle Request, or Actual.

Sufficiency boundary: Capability requires validated boundary variables or explicit insufficient evidence.

### Direct Finding evidence

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-C817FE195629 | KNOWN | 0x21D | CP_evseStatus | CP_cableCurrentLimit | CP_evseStatus / CP_cableCurrentLimit / unit=A | stability=CONSTANT; changes=0; range=0.0..0.0; sequence=0 | DIRECT_INTENT_RETRIEVAL |
| SO-30140211597F | KNOWN | 0x29D | CP_dcChargeStatus | CP_evseOutputDcVoltage | CP_dcChargeStatus / CP_evseOutputDcVoltage / unit=V | stability=DYNAMIC; changes=22; range=0.0..365.47857799999997; first change=140.0275 s (CAN observed state time); last change=246.2332 s (CAN observed state time); sequence=0.0 → 346.87505919999995 → 347.31451239999996 → 349.29205179999997 → 352.3682242 → 355.5176388 → 358.37408459999995 → 361.08404599999994 … | DIRECT_INTENT_RETRIEVAL |

### Other retrieved candidates

These remain visible for review but were **not** used as Finding support.

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-993932E10707 | KNOWN | 0x1D6 | DI_limits | DI_limithvDcCableTemp | DI_limits / DI_limithvDcCableTemp | stability=CONSTANT; changes=0; range=0.0..0.0; sequence=0 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-CE0335F98FD8 | KNOWN | 0x29D | CP_dcChargeStatus | CP_evseOutputDcCurrent | CP_dcChargeStatus / CP_evseOutputDcCurrent / unit=A | stability=DYNAMIC; changes=12; range=0.0..133.0892539; first change=145.0277 s (CAN observed state time); last change=246.2332 s (CAN observed state time); sequence=0.0 → 31.9355612 → 55.8872321 → 79.2529294 → 99.2492785 → 117.4144601 → 133.0892539 → 129.1339321 … | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-2CA4B2E7EDED | KNOWN | 0x29D | CP_dcChargeStatus | CP_evseOutputDcCurrentStale | CP_dcChargeStatus / CP_evseOutputDcCurrentStale | stability=LOW_CARDINALITY; changes=4; range=0.0..1.0; first change=39.7208 s (CAN observed state time); last change=273.5351 s (CAN observed state time); sequence=1 → 0 → 1 → 0 → 1 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-FEC38397A149 | KNOWN | 0x3F2 | BMS_kwhCountersMultiplexed | BMS_dcChargerKwhTotal | BMS_kwhCountersMultiplexed / BMS_dcChargerKwhTotal / unit=KWh | stability=NEAR_CONSTANT; changes=9; range=3769.587..3771.523; first change=151.8501 s (CAN observed state time); last change=247.852 s (CAN observed state time); sequence=3769.587 → 3769.667 → 3769.907 → 3770.154 → 3770.3940000000002 → 3770.631 → 3770.864 → 3771.098 … | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0060 | RESIDUAL | 0x25B | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=60; bit transitions=5558 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0047 | UNKNOWN | 0x22B | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=>=256; bit transitions=1075 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |

### DBC Semantic Reference — REFERENCE — NOT EVIDENCE BY ITSELF

- `SO-C817FE195629`: CP_evseStatus / CP_cableCurrentLimit / unit=A
- `SO-30140211597F`: CP_dcChargeStatus / CP_evseOutputDcVoltage / unit=V
- `SO-993932E10707`: DI_limits / DI_limithvDcCableTemp
- `SO-CE0335F98FD8`: CP_dcChargeStatus / CP_evseOutputDcCurrent / unit=A
- `SO-2CA4B2E7EDED`: CP_dcChargeStatus / CP_evseOutputDcCurrentStale
- `SO-FEC38397A149`: BMS_kwhCountersMultiplexed / BMS_dcChargerKwhTotal / unit=KWh

This is **REFERENCE ONLY — NOT OBSERVED CONTROL CHAIN — NOT APPROVED EVIDENCE**.

### ASC observed behavior

- `SO-C817FE195629`: stability=CONSTANT; changes=0; range=0.0..0.0; sequence=0
- `SO-30140211597F`: stability=DYNAMIC; changes=22; range=0.0..365.47857799999997; first change=140.0275 s (CAN observed state time); last change=246.2332 s (CAN observed state time); sequence=0.0 → 346.87505919999995 → 347.31451239999996 → 349.29205179999997 → 352.3682242 → 355.5176388 → 358.37408459999995 → 361.08404599999994 …
- Phase Feature: **UNAVAILABLE**. Planned windows provide context only and do not establish observed human event time.
- Relationship Evidence: **CURRENTLY LIMITED**. The frozen Observation Package does not contain synchronized cross-signal relationship features required to establish this relation.

### AI interpretation

- **OBSERVED**: The selected cable-limit field is constant and EVSE output voltage is Actual; neither is sufficient to establish EVSE Capability.

### Currently supported

- No direct semantic support is accepted by the program; displayed observations remain candidates only.

### Not established

- ✗ No validated EVSE-boundary capability voltage and current pair is present.

### Evidence gap

- Gap: `GAP-3B23-05`
- Missing evidence type: `SIGNAL_VALIDATION`
- Why it matters: No validated EVSE-boundary capability voltage and current pair is present.

### Collection limitation

The collection predates the current Evidence architecture. Missing physical measurements or human event timestamps are not reconstructed from DBC labels or planned times.

### Audit trace

- Observation refs: `SO-C817FE195629, SO-30140211597F`
- Candidate refs: `NONE`
- Raw ASC refs: `ASC-L289691, ASC-L292373, ASC-L299438, ASC-L306365, ASC-L313782, ASC-L321226, ASC-L328137, ASC-L35, ASC-L41, ASC-L431429, ASC-L685438, ASC-L685444`
- Reasoning package: `TM3-015-reasoning-f2f9203de6d5494d` / `1da118c87ee9299a4eb8e84a697edf652edec81741ad07dee9a82a76f5a1ad15`
- Reasoning result: `TM3-015-phase3b2_3-context-blind-replay-v5`

## ER-06 — Identify Vehicle Capability without substituting EVSE Capability, Vehicle Request, or Actual

- Control Tree: `CT-DCFC-08`
- Binding / Finding: `EB-0006` / `F-3B23-06`
- Semantic status / confidence: `VALIDATION_REQUIRED` / `MEDIUM`
- Program review state: `HUMAN_REVIEW_REQUIRED`; human disposition: **UNSET**

### L3 question

Identify Vehicle Capability without substituting EVSE Capability, Vehicle Request, or Actual.

Sufficiency boundary: Vehicle allowed voltage/current/power require validated vehicle-boundary evidence.

### Direct Finding evidence

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-EE1762E29E91 | KNOWN | 0x2D2 | BMS_driveLimits | BMS_maxChargeCurrent | BMS_driveLimits / BMS_maxChargeCurrent / unit=A | stability=LOW_CARDINALITY; changes=4; range=0.0..250.0; first change=115.392 s (CAN observed state time); last change=246.3935 s (CAN observed state time); sequence=0.0 → 250.0 → 0.0 → 250.0 → 0.0 | DIRECT_INTENT_RETRIEVAL |
| SO-FCA6D6091527 | KNOWN | 0x212 | BMS_status | BMS_chgPowerAvailable | BMS_status / BMS_chgPowerAvailable / unit=kW / enum={"2047": "BMS_chgPowerAvailable_SNA"} | stability=DYNAMIC; changes=189; range=21.5..255.75; first change=140.0893 s (CAN observed state time); last change=245.7928 s (CAN observed state time); sequence=255.75 → 22.0 → 21.75 → 22.0 → 21.75 → 22.0 → 21.75 → 22.0 … | DIRECT_INTENT_RETRIEVAL |

### Other retrieved candidates

These remain visible for review but were **not** used as Finding support.

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-2F68BA1F43E7 | KNOWN | 0x2D2 | BMS_driveLimits | BMS_maxBusVoltage | BMS_driveLimits / BMS_maxBusVoltage / unit=V | stability=LOW_CARDINALITY; changes=14; range=200.67000000000002..201.4; first change=124.9943 s (CAN observed state time); last change=246.0925 s (CAN observed state time); sequence=201.15 → 201.14000000000001 → 201.15 → 201.14000000000001 → 201.15 → 201.14000000000001 → 201.15 → 201.14000000000001 … | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-57FDBA89A626 | KNOWN | 0x2D2 | BMS_driveLimits | BMS_maxDischargeCurrent | BMS_driveLimits / BMS_maxDischargeCurrent / unit=A | stability=LOW_CARDINALITY; changes=4; range=0.0..53.376; first change=115.392 s (CAN observed state time); last change=246.3935 s (CAN observed state time); sequence=53.376 → 46.976 → 0.0 → 46.976 → 53.376 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-D2B7392F2DD6 | KNOWN | 0x2D2 | BMS_driveLimits | BMS_minBusVoltage | BMS_driveLimits / BMS_minBusVoltage / unit=V | stability=DYNAMIC; changes=599; range=106.11..106.75; first change=18.5903 s (CAN observed state time); last change=298.8995 s (CAN observed state time); sequence=106.36 → 106.37 → 106.36 → 106.37 → 106.36 → 106.37 → 106.36 → 106.37 … | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-30140211597F | KNOWN | 0x29D | CP_dcChargeStatus | CP_evseOutputDcVoltage | CP_dcChargeStatus / CP_evseOutputDcVoltage / unit=V | stability=DYNAMIC; changes=22; range=0.0..365.47857799999997; first change=140.0275 s (CAN observed state time); last change=246.2332 s (CAN observed state time); sequence=0.0 → 346.87505919999995 → 347.31451239999996 → 349.29205179999997 → 352.3682242 → 355.5176388 → 358.37408459999995 → 361.08404599999994 … | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0060 | RESIDUAL | 0x25B | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=60; bit transitions=5558 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0047 | UNKNOWN | 0x22B | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=>=256; bit transitions=1075 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |

### DBC Semantic Reference — REFERENCE — NOT EVIDENCE BY ITSELF

- `SO-EE1762E29E91`: BMS_driveLimits / BMS_maxChargeCurrent / unit=A
- `SO-FCA6D6091527`: BMS_status / BMS_chgPowerAvailable / unit=kW / enum={"2047": "BMS_chgPowerAvailable_SNA"}
- `SO-2F68BA1F43E7`: BMS_driveLimits / BMS_maxBusVoltage / unit=V
- `SO-57FDBA89A626`: BMS_driveLimits / BMS_maxDischargeCurrent / unit=A
- `SO-D2B7392F2DD6`: BMS_driveLimits / BMS_minBusVoltage / unit=V
- `SO-30140211597F`: CP_dcChargeStatus / CP_evseOutputDcVoltage / unit=V

This is **REFERENCE ONLY — NOT OBSERVED CONTROL CHAIN — NOT APPROVED EVIDENCE**.

### ASC observed behavior

- `SO-EE1762E29E91`: stability=LOW_CARDINALITY; changes=4; range=0.0..250.0; first change=115.392 s (CAN observed state time); last change=246.3935 s (CAN observed state time); sequence=0.0 → 250.0 → 0.0 → 250.0 → 0.0
- `SO-FCA6D6091527`: stability=DYNAMIC; changes=189; range=21.5..255.75; first change=140.0893 s (CAN observed state time); last change=245.7928 s (CAN observed state time); sequence=255.75 → 22.0 → 21.75 → 22.0 → 21.75 → 22.0 → 21.75 → 22.0 …
- Phase Feature: **UNAVAILABLE**. Planned windows provide context only and do not establish observed human event time.
- Relationship Evidence: **CURRENTLY LIMITED**. The frozen Observation Package does not contain synchronized cross-signal relationship features required to establish this relation.

### AI interpretation

- **OBSERVED**: Vehicle-boundary maximum charge current and available charging power are capability candidates, but their exact semantics and voltage counterpart remain incomplete.

### Currently supported

- ✓ Program mapping status is `PARTIAL_SUPPORT` for the bounded statement above; Signal Validation remains required.

### Not established

- ✗ DBC naming and dynamics alone do not confirm a complete Vehicle Capability set.

### Evidence gap

- Gap: `GAP-3B23-06`
- Missing evidence type: `SIGNAL_VALIDATION`
- Why it matters: DBC naming and dynamics alone do not confirm a complete Vehicle Capability set.

### Collection limitation

The collection predates the current Evidence architecture. Missing physical measurements or human event timestamps are not reconstructed from DBC labels or planned times.

### Audit trace

- Observation refs: `SO-EE1762E29E91, SO-FCA6D6091527`
- Candidate refs: `NONE`
- Raw ASC refs: `ASC-L204, ASC-L208, ASC-L240000, ASC-L276296, ASC-L282543, ASC-L289817, ASC-L292986, ASC-L293247, ASC-L293510, ASC-L293777, ASC-L294301, ASC-L294560, ASC-L295088, ASC-L578359, ASC-L685554, ASC-L685555`
- Reasoning package: `TM3-015-reasoning-f2f9203de6d5494d` / `1da118c87ee9299a4eb8e84a697edf652edec81741ad07dee9a82a76f5a1ad15`
- Reasoning result: `TM3-015-phase3b2_3-context-blind-replay-v5`

## ER-07 — Identify Vehicle Request voltage and current independently of Capability and Actual

- Control Tree: `CT-DCFC-09`
- Binding / Finding: `EB-0007` / `F-3B23-07`
- Semantic status / confidence: `INSUFFICIENT_EVIDENCE` / `LOW`
- Program review state: `HOLD_UNRESOLVED`; human disposition: **UNSET**

### L3 question

Identify Vehicle Request voltage and current independently of Capability and Actual.

Sufficiency boundary: Request power is derived from synchronized request voltage/current unless an independent request-power field is validated.

### Direct Finding evidence

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-C735BF77D6EA | KNOWN | 0x212 | BMS_status | BMS_chargeRequest | BMS_status / BMS_chargeRequest | stability=CONSTANT; changes=0; range=0.0..0.0; sequence=0 | DIRECT_INTENT_RETRIEVAL |

### Other retrieved candidates

These remain visible for review but were **not** used as Finding support.

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-E17A19938CC3 | KNOWN | 0x273 | UI_vehicleControl | UI_accessoryPowerRequest | UI_vehicleControl / UI_accessoryPowerRequest | stability=CONSTANT; changes=0; range=0.0..0.0; sequence=0 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-30140211597F | KNOWN | 0x29D | CP_dcChargeStatus | CP_evseOutputDcVoltage | CP_dcChargeStatus / CP_evseOutputDcVoltage / unit=V | stability=DYNAMIC; changes=22; range=0.0..365.47857799999997; first change=140.0275 s (CAN observed state time); last change=246.2332 s (CAN observed state time); sequence=0.0 → 346.87505919999995 → 347.31451239999996 → 349.29205179999997 → 352.3682242 → 355.5176388 → 358.37408459999995 → 361.08404599999994 … | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-CE0335F98FD8 | KNOWN | 0x29D | CP_dcChargeStatus | CP_evseOutputDcCurrent | CP_dcChargeStatus / CP_evseOutputDcCurrent / unit=A | stability=DYNAMIC; changes=12; range=0.0..133.0892539; first change=145.0277 s (CAN observed state time); last change=246.2332 s (CAN observed state time); sequence=0.0 → 31.9355612 → 55.8872321 → 79.2529294 → 99.2492785 → 117.4144601 → 133.0892539 → 129.1339321 … | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-2CA4B2E7EDED | KNOWN | 0x29D | CP_dcChargeStatus | CP_evseOutputDcCurrentStale | CP_dcChargeStatus / CP_evseOutputDcCurrentStale | stability=LOW_CARDINALITY; changes=4; range=0.0..1.0; first change=39.7208 s (CAN observed state time); last change=273.5351 s (CAN observed state time); sequence=1 → 0 → 1 → 0 → 1 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-05B359B48253 | KNOWN | 0x132 | BMS_hvBusStatus | BMS_packCurrent | BMS_hvBusStatus / BMS_packCurrent / unit=A / enum={"-16384": "SNA"} | stability=DYNAMIC; changes=17475; range=-219.60000000000002..27.8; first change=0.0421 s (CAN observed state time); last change=299.7285 s (CAN observed state time); sequence=0.8 → 0.7000000000000001 → 0.8 → 0.7000000000000001 → 0.8 → 0.7000000000000001 → 0.8 → 0.7000000000000001 … | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0005 | RESIDUAL | 0x108 | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=133; bit transitions=11311 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0012 | UNKNOWN | 0x128 | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=5; bit transitions=9 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |

### DBC Semantic Reference — REFERENCE — NOT EVIDENCE BY ITSELF

- `SO-C735BF77D6EA`: BMS_status / BMS_chargeRequest
- `SO-E17A19938CC3`: UI_vehicleControl / UI_accessoryPowerRequest
- `SO-30140211597F`: CP_dcChargeStatus / CP_evseOutputDcVoltage / unit=V
- `SO-CE0335F98FD8`: CP_dcChargeStatus / CP_evseOutputDcCurrent / unit=A
- `SO-2CA4B2E7EDED`: CP_dcChargeStatus / CP_evseOutputDcCurrentStale
- `SO-05B359B48253`: BMS_hvBusStatus / BMS_packCurrent / unit=A / enum={"-16384": "SNA"}

This is **REFERENCE ONLY — NOT OBSERVED CONTROL CHAIN — NOT APPROVED EVIDENCE**.

### ASC observed behavior

- `SO-C735BF77D6EA`: stability=CONSTANT; changes=0; range=0.0..0.0; sequence=0
- Phase Feature: **UNAVAILABLE**. Planned windows provide context only and do not establish observed human event time.
- Relationship Evidence: **CURRENTLY LIMITED**. The frozen Observation Package does not contain synchronized cross-signal relationship features required to establish this relation.

### AI interpretation

- **OBSERVED**: The retrieved charge-request field is constant and no independently validated requested voltage and current pair is available; Actual signals cannot replace Request.

### Currently supported

- No direct semantic support is accepted by the program; displayed observations remain candidates only.

### Not established

- ✗ Direct semantically validated request voltage and current are absent.

### Evidence gap

- Gap: `GAP-3B23-07`
- Missing evidence type: `DIRECT_REQUEST`
- Why it matters: Direct semantically validated request voltage and current are absent.

### Collection limitation

The collection predates the current Evidence architecture. Missing physical measurements or human event timestamps are not reconstructed from DBC labels or planned times.

### Audit trace

- Observation refs: `SO-C735BF77D6EA`
- Candidate refs: `NONE`
- Raw ASC refs: `ASC-L204, ASC-L685555`
- Reasoning package: `TM3-015-reasoning-f2f9203de6d5494d` / `1da118c87ee9299a4eb8e84a697edf652edec81741ad07dee9a82a76f5a1ad15`
- Reasoning result: `TM3-015-phase3b2_3-context-blind-replay-v5`

## ER-08 — Identify Permission and Safety Gate separately from contactor state, high-voltage path, and energy transfer

- Control Tree: `CT-DCFC-10`
- Binding / Finding: `EB-0008` / `F-3B23-08`
- Semantic status / confidence: `INSUFFICIENT_EVIDENCE` / `LOW`
- Program review state: `HOLD_UNRESOLVED`; human disposition: **UNSET**

### L3 question

Identify Permission and Safety Gate separately from contactor state, high-voltage path, and energy transfer.

Sufficiency boundary: Actual or contactor observations cannot alone prove permission.

### Direct Finding evidence

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-19CE993899A3 | KNOWN | 0x20A | HVP_contactorState | HVP_packCtrsRequestStatus | HVP_contactorState / HVP_packCtrsRequestStatus / enum={"0": "NOT_ACTIVE", "1": "ACTIVE", "2": "COMPLETED"} | stability=LOW_CARDINALITY; changes=0; sequence=NOT_ACTIVE | DIRECT_INTENT_RETRIEVAL |
| SO-464571D40359 | KNOWN | 0x20A | HVP_contactorState | HVP_hvilStatus | HVP_contactorState / HVP_hvilStatus / enum={"0": "UNKNOWN", "1": "STATUS_OK", "2": "CURRENT_SOURCE_FAULT", "3": "INTERNAL_OPEN_FAULT", "4": "VEHICLE_OPEN_FAULT", "5": "PENTHOUSE_LID_OPEN_FAULT", "6": "UNKNOWN_LOCATION_OPEN_FAULT", "7": "VEHICLE_NODE_FAULT", "8": "NO_12V_SUPPLY"} | stability=LOW_CARDINALITY; changes=2; first change=133.8453 s (CAN observed state time); last change=134.8465 s (CAN observed state time); sequence=STATUS_OK → UNKNOWN → STATUS_OK | DIRECT_INTENT_RETRIEVAL |
| SO-605D4479E286 | KNOWN | 0x20A | HVP_contactorState | HVP_fcCtrsRequestStatus | HVP_contactorState / HVP_fcCtrsRequestStatus / enum={"0": "NOT_ACTIVE", "1": "ACTIVE", "2": "COMPLETED"} | stability=LOW_CARDINALITY; changes=2; first change=133.8453 s (CAN observed state time); last change=134.8465 s (CAN observed state time); sequence=COMPLETED → NOT_ACTIVE → COMPLETED | DIRECT_INTENT_RETRIEVAL |

### Other retrieved candidates

These remain visible for review but were **not** used as Finding support.

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-B02973A15F54 | KNOWN | 0x224 | PCS_dcdcStatus | PCS_dcdcOutputIsLimited | PCS_dcdcStatus / PCS_dcdcOutputIsLimited | stability=CONSTANT; changes=0; range=0.0..0.0; sequence=0 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-00D930D51795 | KNOWN | 0x20A | HVP_contactorState | HVP_fcCtrsResetRequestRequired | HVP_contactorState / HVP_fcCtrsResetRequestRequired | stability=CONSTANT; changes=0; range=0.0..0.0; sequence=0 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-0235B54B0CCF | KNOWN | 0x20A | HVP_contactorState | HVP_packCtrsResetRequestRequired | HVP_contactorState / HVP_packCtrsResetRequestRequired | stability=CONSTANT; changes=0; range=0.0..0.0; sequence=0 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0005 | RESIDUAL | 0x108 | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=133; bit transitions=11311 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0012 | UNKNOWN | 0x128 | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=5; bit transitions=9 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |

### DBC Semantic Reference — REFERENCE — NOT EVIDENCE BY ITSELF

- `SO-19CE993899A3`: HVP_contactorState / HVP_packCtrsRequestStatus / enum={"0": "NOT_ACTIVE", "1": "ACTIVE", "2": "COMPLETED"}
- `SO-464571D40359`: HVP_contactorState / HVP_hvilStatus / enum={"0": "UNKNOWN", "1": "STATUS_OK", "2": "CURRENT_SOURCE_FAULT", "3": "INTERNAL_OPEN_FAULT", "4": "VEHICLE_OPEN_FAULT", "5": "PENTHOUSE_LID_OPEN_FAULT", "6": "UNKNOWN_LOCATION_OPEN_FAULT", "7": "VEHICLE_NODE_FAULT", "8": "NO_12V_SUPPLY"}
- `SO-605D4479E286`: HVP_contactorState / HVP_fcCtrsRequestStatus / enum={"0": "NOT_ACTIVE", "1": "ACTIVE", "2": "COMPLETED"}
- `SO-B02973A15F54`: PCS_dcdcStatus / PCS_dcdcOutputIsLimited
- `SO-00D930D51795`: HVP_contactorState / HVP_fcCtrsResetRequestRequired
- `SO-0235B54B0CCF`: HVP_contactorState / HVP_packCtrsResetRequestRequired

This is **REFERENCE ONLY — NOT OBSERVED CONTROL CHAIN — NOT APPROVED EVIDENCE**.

### ASC observed behavior

- `SO-19CE993899A3`: stability=LOW_CARDINALITY; changes=0; sequence=NOT_ACTIVE
- `SO-464571D40359`: stability=LOW_CARDINALITY; changes=2; first change=133.8453 s (CAN observed state time); last change=134.8465 s (CAN observed state time); sequence=STATUS_OK → UNKNOWN → STATUS_OK
- `SO-605D4479E286`: stability=LOW_CARDINALITY; changes=2; first change=133.8453 s (CAN observed state time); last change=134.8465 s (CAN observed state time); sequence=COMPLETED → NOT_ACTIVE → COMPLETED
- Phase Feature: **UNAVAILABLE**. Planned windows provide context only and do not establish observed human event time.
- Relationship Evidence: **CURRENTLY LIMITED**. The frozen Observation Package does not contain synchronized cross-signal relationship features required to establish this relation.

### AI interpretation

- **OBSERVED**: HVIL and contactor-request status observations describe safety and path states, but do not independently prove charging Permission.

### Currently supported

- No direct semantic support is accepted by the program; displayed observations remain candidates only.

### Not established

- ✗ No direct permission or safety-gate decision variable is validated.

### Evidence gap

- Gap: `GAP-3B23-08`
- Missing evidence type: `CONDITION_OR_PERMISSION`
- Why it matters: No direct permission or safety-gate decision variable is validated.

### Collection limitation

The collection predates the current Evidence architecture. Missing physical measurements or human event timestamps are not reconstructed from DBC labels or planned times.

### Audit trace

- Observation refs: `SO-19CE993899A3, SO-464571D40359, SO-605D4479E286`
- Candidate refs: `NONE`
- Raw ASC refs: `ASC-L1802, ASC-L277203, ASC-L279219, ASC-L683896`
- Reasoning package: `TM3-015-reasoning-f2f9203de6d5494d` / `1da118c87ee9299a4eb8e84a697edf652edec81741ad07dee9a82a76f5a1ad15`
- Reasoning result: `TM3-015-phase3b2_3-context-blind-replay-v5`

## ER-09 — Identify high-voltage path request, action, feedback, voltage matching, and establishment within observable limits

- Control Tree: `CT-DCFC-11`
- Binding / Finding: `EB-0009` / `F-3B23-09`
- Semantic status / confidence: `VALIDATION_REQUIRED` / `MEDIUM`
- Program review state: `HUMAN_REVIEW_REQUIRED`; human disposition: **UNSET**

### L3 question

Identify high-voltage path request, action, feedback, voltage matching, and establishment within observable limits.

Sufficiency boundary: Contactor state alone does not prove energy transfer.

### Direct Finding evidence

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-605D4479E286 | KNOWN | 0x20A | HVP_contactorState | HVP_fcCtrsRequestStatus | HVP_contactorState / HVP_fcCtrsRequestStatus / enum={"0": "NOT_ACTIVE", "1": "ACTIVE", "2": "COMPLETED"} | stability=LOW_CARDINALITY; changes=2; first change=133.8453 s (CAN observed state time); last change=134.8465 s (CAN observed state time); sequence=COMPLETED → NOT_ACTIVE → COMPLETED | DIRECT_INTENT_RETRIEVAL |
| SO-40123AC227A0 | KNOWN | 0x20A | HVP_contactorState | HVP_fcContactorSetState | HVP_contactorState / HVP_fcContactorSetState / enum={"0": "SNA", "1": "OPEN", "2": "CLOSING", "3": "BLOCKED", "4": "OPENING", "5": "CLOSED", "6": "PARTIAL_WELD", "7": "WELDED", "8": "POSITIVE_CLOSED", "9": "NEGATIVE_CLOSED"} | stability=LOW_CARDINALITY; changes=2; first change=134.8465 s (CAN observed state time); last change=246.8477 s (CAN observed state time); sequence=OPEN → CLOSED → OPEN | DIRECT_INTENT_RETRIEVAL |

### Other retrieved candidates

These remain visible for review but were **not** used as Finding support.

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-19CE993899A3 | KNOWN | 0x20A | HVP_contactorState | HVP_packCtrsRequestStatus | HVP_contactorState / HVP_packCtrsRequestStatus / enum={"0": "NOT_ACTIVE", "1": "ACTIVE", "2": "COMPLETED"} | stability=LOW_CARDINALITY; changes=0; sequence=NOT_ACTIVE | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-464571D40359 | KNOWN | 0x20A | HVP_contactorState | HVP_hvilStatus | HVP_contactorState / HVP_hvilStatus / enum={"0": "UNKNOWN", "1": "STATUS_OK", "2": "CURRENT_SOURCE_FAULT", "3": "INTERNAL_OPEN_FAULT", "4": "VEHICLE_OPEN_FAULT", "5": "PENTHOUSE_LID_OPEN_FAULT", "6": "UNKNOWN_LOCATION_OPEN_FAULT", "7": "VEHICLE_NODE_FAULT", "8": "NO_12V_SUPPLY"} | stability=LOW_CARDINALITY; changes=2; first change=133.8453 s (CAN observed state time); last change=134.8465 s (CAN observed state time); sequence=STATUS_OK → UNKNOWN → STATUS_OK | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-00D930D51795 | KNOWN | 0x20A | HVP_contactorState | HVP_fcCtrsResetRequestRequired | HVP_contactorState / HVP_fcCtrsResetRequestRequired | stability=CONSTANT; changes=0; range=0.0..0.0; sequence=0 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-0235B54B0CCF | KNOWN | 0x20A | HVP_contactorState | HVP_packCtrsResetRequestRequired | HVP_contactorState / HVP_packCtrsResetRequestRequired | stability=CONSTANT; changes=0; range=0.0..0.0; sequence=0 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0005 | RESIDUAL | 0x108 | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=133; bit transitions=11311 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0012 | UNKNOWN | 0x128 | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=5; bit transitions=9 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |

### DBC Semantic Reference — REFERENCE — NOT EVIDENCE BY ITSELF

- `SO-605D4479E286`: HVP_contactorState / HVP_fcCtrsRequestStatus / enum={"0": "NOT_ACTIVE", "1": "ACTIVE", "2": "COMPLETED"}
- `SO-40123AC227A0`: HVP_contactorState / HVP_fcContactorSetState / enum={"0": "SNA", "1": "OPEN", "2": "CLOSING", "3": "BLOCKED", "4": "OPENING", "5": "CLOSED", "6": "PARTIAL_WELD", "7": "WELDED", "8": "POSITIVE_CLOSED", "9": "NEGATIVE_CLOSED"}
- `SO-19CE993899A3`: HVP_contactorState / HVP_packCtrsRequestStatus / enum={"0": "NOT_ACTIVE", "1": "ACTIVE", "2": "COMPLETED"}
- `SO-464571D40359`: HVP_contactorState / HVP_hvilStatus / enum={"0": "UNKNOWN", "1": "STATUS_OK", "2": "CURRENT_SOURCE_FAULT", "3": "INTERNAL_OPEN_FAULT", "4": "VEHICLE_OPEN_FAULT", "5": "PENTHOUSE_LID_OPEN_FAULT", "6": "UNKNOWN_LOCATION_OPEN_FAULT", "7": "VEHICLE_NODE_FAULT", "8": "NO_12V_SUPPLY"}
- `SO-00D930D51795`: HVP_contactorState / HVP_fcCtrsResetRequestRequired
- `SO-0235B54B0CCF`: HVP_contactorState / HVP_packCtrsResetRequestRequired

This is **REFERENCE ONLY — NOT OBSERVED CONTROL CHAIN — NOT APPROVED EVIDENCE**.

### ASC observed behavior

- `SO-605D4479E286`: stability=LOW_CARDINALITY; changes=2; first change=133.8453 s (CAN observed state time); last change=134.8465 s (CAN observed state time); sequence=COMPLETED → NOT_ACTIVE → COMPLETED
- `SO-40123AC227A0`: stability=LOW_CARDINALITY; changes=2; first change=134.8465 s (CAN observed state time); last change=246.8477 s (CAN observed state time); sequence=OPEN → CLOSED → OPEN
- Phase Feature: **UNAVAILABLE**. Planned windows provide context only and do not establish observed human event time.
- Relationship Evidence: **CURRENTLY LIMITED**. The frozen Observation Package does not contain synchronized cross-signal relationship features required to establish this relation.

### AI interpretation

- **OBSERVED**: Fast-charge contactor request status and contactor set state support an observable HV-path state change, but do not alone prove voltage matching or energy transfer.

### Currently supported

- ✓ Program mapping status is `PARTIAL_SUPPORT` for the bounded statement above; Signal Validation remains required.

### Not established

- ✗ Voltage matching and synchronized transfer evidence are not bound to the path transition.

### Evidence gap

- Gap: `GAP-3B23-09`
- Missing evidence type: `PHYSICAL_MEASUREMENT`
- Why it matters: Voltage matching and synchronized transfer evidence are not bound to the path transition.

### Collection limitation

The collection predates the current Evidence architecture. Missing physical measurements or human event timestamps are not reconstructed from DBC labels or planned times.

### Audit trace

- Observation refs: `SO-605D4479E286, SO-40123AC227A0`
- Candidate refs: `NONE`
- Raw ASC refs: `ASC-L1802, ASC-L277203, ASC-L279219, ASC-L579549, ASC-L683896`
- Reasoning package: `TM3-015-reasoning-f2f9203de6d5494d` / `1da118c87ee9299a4eb8e84a697edf652edec81741ad07dee9a82a76f5a1ad15`
- Reasoning result: `TM3-015-phase3b2_3-context-blind-replay-v5`

## ER-10 — Distinguish EVSE Actual voltage/current/power from Pack Actual voltage/current/power at their measurement boundaries

- Control Tree: `CT-DCFC-12`
- Binding / Finding: `EB-0010` / `F-3B23-10`
- Semantic status / confidence: `VALIDATION_REQUIRED` / `MEDIUM`
- Program review state: `HUMAN_REVIEW_REQUIRED`; human disposition: **UNSET**

### L3 question

Distinguish EVSE Actual voltage/current/power from Pack Actual voltage/current/power at their measurement boundaries.

Sufficiency boundary: Cross-boundary comparison requires synchronized and semantically validated measurements.

### Direct Finding evidence

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-30140211597F | KNOWN | 0x29D | CP_dcChargeStatus | CP_evseOutputDcVoltage | CP_dcChargeStatus / CP_evseOutputDcVoltage / unit=V | stability=DYNAMIC; changes=22; range=0.0..365.47857799999997; first change=140.0275 s (CAN observed state time); last change=246.2332 s (CAN observed state time); sequence=0.0 → 346.87505919999995 → 347.31451239999996 → 349.29205179999997 → 352.3682242 → 355.5176388 → 358.37408459999995 → 361.08404599999994 … | DIRECT_INTENT_RETRIEVAL |
| SO-CE0335F98FD8 | KNOWN | 0x29D | CP_dcChargeStatus | CP_evseOutputDcCurrent | CP_dcChargeStatus / CP_evseOutputDcCurrent / unit=A | stability=DYNAMIC; changes=12; range=0.0..133.0892539; first change=145.0277 s (CAN observed state time); last change=246.2332 s (CAN observed state time); sequence=0.0 → 31.9355612 → 55.8872321 → 79.2529294 → 99.2492785 → 117.4144601 → 133.0892539 → 129.1339321 … | DIRECT_INTENT_RETRIEVAL |
| SO-05B359B48253 | KNOWN | 0x132 | BMS_hvBusStatus | BMS_packCurrent | BMS_hvBusStatus / BMS_packCurrent / unit=A / enum={"-16384": "SNA"} | stability=DYNAMIC; changes=17475; range=-219.60000000000002..27.8; first change=0.0421 s (CAN observed state time); last change=299.7285 s (CAN observed state time); sequence=0.8 → 0.7000000000000001 → 0.8 → 0.7000000000000001 → 0.8 → 0.7000000000000001 → 0.8 → 0.7000000000000001 … | DIRECT_INTENT_RETRIEVAL |
| SO-CEEC4D90BE22 | KNOWN | 0x132 | BMS_hvBusStatus | BMS_packVoltage | BMS_hvBusStatus / BMS_packVoltage / unit=V | stability=DYNAMIC; changes=28790; range=8.17..365.25; first change=0.012 s (CAN observed state time); last change=299.7285 s (CAN observed state time); sequence=347.13 → 347.06 → 347.27 → 347.11 → 347.21 → 347.2 → 347.19 → 347.12 … | DIRECT_INTENT_RETRIEVAL |

### Other retrieved candidates

These remain visible for review but were **not** used as Finding support.

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-2CA4B2E7EDED | KNOWN | 0x29D | CP_dcChargeStatus | CP_evseOutputDcCurrentStale | CP_dcChargeStatus / CP_evseOutputDcCurrentStale | stability=LOW_CARDINALITY; changes=4; range=0.0..1.0; first change=39.7208 s (CAN observed state time); last change=273.5351 s (CAN observed state time); sequence=1 → 0 → 1 → 0 → 1 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-FEC38397A149 | KNOWN | 0x3F2 | BMS_kwhCountersMultiplexed | BMS_dcChargerKwhTotal | BMS_kwhCountersMultiplexed / BMS_dcChargerKwhTotal / unit=KWh | stability=NEAR_CONSTANT; changes=9; range=3769.587..3771.523; first change=151.8501 s (CAN observed state time); last change=247.852 s (CAN observed state time); sequence=3769.587 → 3769.667 → 3769.907 → 3770.154 → 3770.3940000000002 → 3770.631 → 3770.864 → 3771.098 … | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0278 | UNKNOWN | 0x53F | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=2; bit transitions=6 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0010 | RESIDUAL | 0x123 | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=2; bit transitions=50932 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |

### DBC Semantic Reference — REFERENCE — NOT EVIDENCE BY ITSELF

- `SO-30140211597F`: CP_dcChargeStatus / CP_evseOutputDcVoltage / unit=V
- `SO-CE0335F98FD8`: CP_dcChargeStatus / CP_evseOutputDcCurrent / unit=A
- `SO-05B359B48253`: BMS_hvBusStatus / BMS_packCurrent / unit=A / enum={"-16384": "SNA"}
- `SO-CEEC4D90BE22`: BMS_hvBusStatus / BMS_packVoltage / unit=V
- `SO-2CA4B2E7EDED`: CP_dcChargeStatus / CP_evseOutputDcCurrentStale
- `SO-FEC38397A149`: BMS_kwhCountersMultiplexed / BMS_dcChargerKwhTotal / unit=KWh

This is **REFERENCE ONLY — NOT OBSERVED CONTROL CHAIN — NOT APPROVED EVIDENCE**.

### ASC observed behavior

- `SO-30140211597F`: stability=DYNAMIC; changes=22; range=0.0..365.47857799999997; first change=140.0275 s (CAN observed state time); last change=246.2332 s (CAN observed state time); sequence=0.0 → 346.87505919999995 → 347.31451239999996 → 349.29205179999997 → 352.3682242 → 355.5176388 → 358.37408459999995 → 361.08404599999994 …
- `SO-CE0335F98FD8`: stability=DYNAMIC; changes=12; range=0.0..133.0892539; first change=145.0277 s (CAN observed state time); last change=246.2332 s (CAN observed state time); sequence=0.0 → 31.9355612 → 55.8872321 → 79.2529294 → 99.2492785 → 117.4144601 → 133.0892539 → 129.1339321 …
- `SO-05B359B48253`: stability=DYNAMIC; changes=17475; range=-219.60000000000002..27.8; first change=0.0421 s (CAN observed state time); last change=299.7285 s (CAN observed state time); sequence=0.8 → 0.7000000000000001 → 0.8 → 0.7000000000000001 → 0.8 → 0.7000000000000001 → 0.8 → 0.7000000000000001 …
- `SO-CEEC4D90BE22`: stability=DYNAMIC; changes=28790; range=8.17..365.25; first change=0.012 s (CAN observed state time); last change=299.7285 s (CAN observed state time); sequence=347.13 → 347.06 → 347.27 → 347.11 → 347.21 → 347.2 → 347.19 → 347.12 …
- Phase Feature: **UNAVAILABLE**. Planned windows provide context only and do not establish observed human event time.
- Relationship Evidence: **CURRENTLY LIMITED**. The frozen Observation Package does not contain synchronized cross-signal relationship features required to establish this relation.

### AI interpretation

- **OBSERVED**: Distinct EVSE-side voltage and current and Pack-side voltage and current observations are present, preserving two measurement boundaries, but quantitative cross-boundary closure is not established.

### Currently supported

- ✓ Program mapping status is `PARTIAL_SUPPORT` for the bounded statement above; Signal Validation remains required.

### Not established

- ✗ EVSE current quantitative semantics and synchronized cross-boundary comparison remain unvalidated.

### Evidence gap

- Gap: `GAP-3B23-10`
- Missing evidence type: `SIGNAL_VALIDATION`
- Why it matters: EVSE current quantitative semantics and synchronized cross-boundary comparison remain unvalidated.

### Collection limitation

The collection predates the current Evidence architecture. Missing physical measurements or human event timestamps are not reconstructed from DBC labels or planned times.

### Audit trace

- Observation refs: `SO-30140211597F, SO-CE0335F98FD8, SO-05B359B48253, SO-CEEC4D90BE22`
- Candidate refs: `NONE`
- Raw ASC refs: `ASC-L109, ASC-L11, ASC-L131, ASC-L150, ASC-L169, ASC-L193, ASC-L25, ASC-L279095, ASC-L289691, ASC-L292373, ASC-L299438, ASC-L302096, ASC-L306365, ASC-L308731, ASC-L313782, ASC-L314, ASC-L316171, ASC-L321226, ASC-L323355, ASC-L328137, ASC-L330534, ASC-L332, ASC-L337698, ASC-L338601, ASC-L344876, ASC-L355, ASC-L41, ASC-L431429, ASC-L502893, ASC-L55, ASC-L576808, ASC-L685444, ASC-L685615, ASC-L79`
- Reasoning package: `TM3-015-reasoning-f2f9203de6d5494d` / `1da118c87ee9299a4eb8e84a697edf652edec81741ad07dee9a82a76f5a1ad15`
- Reasoning result: `TM3-015-phase3b2_3-context-blind-replay-v5`

## ER-11 — Assess the continuous Capability, Request, EVSE Actual, and Pack Actual relationship without collapsing roles or assuming causality from proximity

- Control Tree: `CT-DCFC-13`
- Binding / Finding: `EB-0011` / `F-3B23-11`
- Semantic status / confidence: `VALIDATION_REQUIRED` / `LOW`
- Program review state: `HUMAN_REVIEW_REQUIRED`; human disposition: **UNSET**

### L3 question

Assess the continuous Capability, Request, EVSE Actual, and Pack Actual relationship without collapsing roles or assuming causality from proximity.

Sufficiency boundary: Missing roles remain explicit gaps.

### Direct Finding evidence

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-EE1762E29E91 | KNOWN | 0x2D2 | BMS_driveLimits | BMS_maxChargeCurrent | BMS_driveLimits / BMS_maxChargeCurrent / unit=A | stability=LOW_CARDINALITY; changes=4; range=0.0..250.0; first change=115.392 s (CAN observed state time); last change=246.3935 s (CAN observed state time); sequence=0.0 → 250.0 → 0.0 → 250.0 → 0.0 | DIRECT_INTENT_RETRIEVAL |
| SO-30140211597F | KNOWN | 0x29D | CP_dcChargeStatus | CP_evseOutputDcVoltage | CP_dcChargeStatus / CP_evseOutputDcVoltage / unit=V | stability=DYNAMIC; changes=22; range=0.0..365.47857799999997; first change=140.0275 s (CAN observed state time); last change=246.2332 s (CAN observed state time); sequence=0.0 → 346.87505919999995 → 347.31451239999996 → 349.29205179999997 → 352.3682242 → 355.5176388 → 358.37408459999995 → 361.08404599999994 … | DIRECT_INTENT_RETRIEVAL |
| SO-CE0335F98FD8 | KNOWN | 0x29D | CP_dcChargeStatus | CP_evseOutputDcCurrent | CP_dcChargeStatus / CP_evseOutputDcCurrent / unit=A | stability=DYNAMIC; changes=12; range=0.0..133.0892539; first change=145.0277 s (CAN observed state time); last change=246.2332 s (CAN observed state time); sequence=0.0 → 31.9355612 → 55.8872321 → 79.2529294 → 99.2492785 → 117.4144601 → 133.0892539 → 129.1339321 … | DIRECT_INTENT_RETRIEVAL |

### Other retrieved candidates

These remain visible for review but were **not** used as Finding support.

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-2CA4B2E7EDED | KNOWN | 0x29D | CP_dcChargeStatus | CP_evseOutputDcCurrentStale | CP_dcChargeStatus / CP_evseOutputDcCurrentStale | stability=LOW_CARDINALITY; changes=4; range=0.0..1.0; first change=39.7208 s (CAN observed state time); last change=273.5351 s (CAN observed state time); sequence=1 → 0 → 1 → 0 → 1 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-C817FE195629 | KNOWN | 0x21D | CP_evseStatus | CP_cableCurrentLimit | CP_evseStatus / CP_cableCurrentLimit / unit=A | stability=CONSTANT; changes=0; range=0.0..0.0; sequence=0 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-CDB81064C219 | KNOWN | 0x21D | CP_evseStatus | CP_lineVoltageRequested | CP_evseStatus / CP_lineVoltageRequested | stability=LOW_CARDINALITY; changes=4; range=0.0..1.0; first change=39.7192 s (CAN observed state time); last change=273.5338 s (CAN observed state time); sequence=1 → 0 → 1 → 0 → 1 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0278 | UNKNOWN | 0x53F | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=2; bit transitions=6 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0005 | RESIDUAL | 0x108 | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=133; bit transitions=11311 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |

### DBC Semantic Reference — REFERENCE — NOT EVIDENCE BY ITSELF

- `SO-EE1762E29E91`: BMS_driveLimits / BMS_maxChargeCurrent / unit=A
- `SO-30140211597F`: CP_dcChargeStatus / CP_evseOutputDcVoltage / unit=V
- `SO-CE0335F98FD8`: CP_dcChargeStatus / CP_evseOutputDcCurrent / unit=A
- `SO-2CA4B2E7EDED`: CP_dcChargeStatus / CP_evseOutputDcCurrentStale
- `SO-C817FE195629`: CP_evseStatus / CP_cableCurrentLimit / unit=A
- `SO-CDB81064C219`: CP_evseStatus / CP_lineVoltageRequested

This is **REFERENCE ONLY — NOT OBSERVED CONTROL CHAIN — NOT APPROVED EVIDENCE**.

### ASC observed behavior

- `SO-EE1762E29E91`: stability=LOW_CARDINALITY; changes=4; range=0.0..250.0; first change=115.392 s (CAN observed state time); last change=246.3935 s (CAN observed state time); sequence=0.0 → 250.0 → 0.0 → 250.0 → 0.0
- `SO-30140211597F`: stability=DYNAMIC; changes=22; range=0.0..365.47857799999997; first change=140.0275 s (CAN observed state time); last change=246.2332 s (CAN observed state time); sequence=0.0 → 346.87505919999995 → 347.31451239999996 → 349.29205179999997 → 352.3682242 → 355.5176388 → 358.37408459999995 → 361.08404599999994 …
- `SO-CE0335F98FD8`: stability=DYNAMIC; changes=12; range=0.0..133.0892539; first change=145.0277 s (CAN observed state time); last change=246.2332 s (CAN observed state time); sequence=0.0 → 31.9355612 → 55.8872321 → 79.2529294 → 99.2492785 → 117.4144601 → 133.0892539 → 129.1339321 …
- Phase Feature: **UNAVAILABLE**. Planned windows provide context only and do not establish observed human event time.
- Relationship Evidence: **CURRENTLY LIMITED**. The frozen Observation Package does not contain synchronized cross-signal relationship features required to establish this relation.

### AI interpretation

- **OBSERVED**: A vehicle capability candidate and EVSE Actual candidates coexist, but direct Vehicle Request and a complete Pack Actual pair are absent from this question's direct evidence.

### Currently supported

- ✓ Program mapping status is `PARTIAL_SUPPORT` for the bounded statement above; Signal Validation remains required.

### Not established

- ✗ The continuous relationship cannot be completed without validated Request and all boundary roles.

### Evidence gap

- Gap: `GAP-3B23-11`
- Missing evidence type: `DIRECT_REQUEST`
- Why it matters: The continuous relationship cannot be completed without validated Request and all boundary roles.

### Collection limitation

The collection predates the current Evidence architecture. Missing physical measurements or human event timestamps are not reconstructed from DBC labels or planned times.

### Audit trace

- Observation refs: `SO-EE1762E29E91, SO-30140211597F, SO-CE0335F98FD8`
- Candidate refs: `NONE`
- Raw ASC refs: `ASC-L208, ASC-L240000, ASC-L276296, ASC-L282543, ASC-L289691, ASC-L292373, ASC-L299438, ASC-L302096, ASC-L306365, ASC-L308731, ASC-L313782, ASC-L316171, ASC-L321226, ASC-L323355, ASC-L328137, ASC-L330534, ASC-L337698, ASC-L344876, ASC-L41, ASC-L431429, ASC-L578359, ASC-L685444, ASC-L685554`
- Reasoning package: `TM3-015-reasoning-f2f9203de6d5494d` / `1da118c87ee9299a4eb8e84a697edf652edec81741ad07dee9a82a76f5a1ad15`
- Reasoning result: `TM3-015-phase3b2_3-context-blind-replay-v5`

## ER-12 — Identify thermal state, thermal demand, execution, and effects on capability or request where supported

- Control Tree: `CT-DCFC-14`
- Binding / Finding: `EB-0012` / `F-3B23-12`
- Semantic status / confidence: `VALIDATION_REQUIRED` / `MEDIUM`
- Program review state: `HUMAN_REVIEW_REQUIRED`; human disposition: **UNSET**

### L3 question

Identify thermal state, thermal demand, execution, and effects on capability or request where supported.

Sufficiency boundary: Thermal correlation requires validation and an alternative-condition check for causal attribution.

### Direct Finding evidence

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-7717801FE8E8 | KNOWN | 0x2E1 | VCFRONT_status | VCFRONT_isActiveHeatingBattery | VCFRONT_status / VCFRONT_isActiveHeatingBattery | stability=LOW_CARDINALITY; changes=2; range=0.0..1.0; first change=141.2739 s (CAN observed state time); last change=248.3204 s (CAN observed state time); sequence=0 → 1 → 0 | DIRECT_INTENT_RETRIEVAL |
| SO-BC7D879CB5FA | KNOWN | 0x241 | VCFRONT_coolant | VCFRONT_wasteHeatRequestType | VCFRONT_coolant / VCFRONT_wasteHeatRequestType / enum={"0": "NONE", "1": "PARTIAL", "2": "FULL"} | stability=LOW_CARDINALITY; changes=4; first change=141.3329 s (CAN observed state time); last change=255.3398 s (CAN observed state time); sequence=PARTIAL → FULL → PARTIAL → NONE → PARTIAL | DIRECT_INTENT_RETRIEVAL |

### Other retrieved candidates

These remain visible for review but were **not** used as Finding support.

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-2BAA1DECBE96 | KNOWN | 0x312 | BMS_thermalStatus | BMS_inletActiveHeatTargetT | BMS_thermalStatus / BMS_inletActiveHeatTargetT / unit=DegC | stability=DYNAMIC; changes=598; range=-14.0..80.5; first change=0.9913 s (CAN observed state time); last change=299.4974 s (CAN observed state time); sequence=79.75 → -13.75 → 79.75 → -13.75 → 79.75 → -13.75 → 79.75 → -13.75 … | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-C8661259C0DA | KNOWN | 0x312 | BMS_thermalStatus | BMS_inletActiveCoolTargetT | BMS_thermalStatus / BMS_inletActiveCoolTargetT / unit=DegC | stability=DYNAMIC; changes=598; range=-12.25..92.25; first change=0.9913 s (CAN observed state time); last change=299.4974 s (CAN observed state time); sequence=-0.25 → -12.25 → -0.25 → -12.25 → -0.25 → -12.25 → -0.25 → -12.25 … | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-364390148393 | KNOWN | 0x82 | UI_tripPlanning | UI_requestActiveBatteryHeating | UI_tripPlanning / UI_requestActiveBatteryHeating | stability=CONSTANT; changes=0; range=0.0..0.0; sequence=0 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-4A197BB1EE53 | KNOWN | 0x381 | VCFRONT_logging1Hz | VCFRONT_passiveCoolingState | VCFRONT_logging1Hz / VCFRONT_passiveCoolingState | stability=CONSTANT; changes=0; range=0.0..0.0; sequence=0 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0005 | RESIDUAL | 0x108 | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=133; bit transitions=11311 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0012 | UNKNOWN | 0x128 | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=5; bit transitions=9 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |

### DBC Semantic Reference — REFERENCE — NOT EVIDENCE BY ITSELF

- `SO-7717801FE8E8`: VCFRONT_status / VCFRONT_isActiveHeatingBattery
- `SO-BC7D879CB5FA`: VCFRONT_coolant / VCFRONT_wasteHeatRequestType / enum={"0": "NONE", "1": "PARTIAL", "2": "FULL"}
- `SO-2BAA1DECBE96`: BMS_thermalStatus / BMS_inletActiveHeatTargetT / unit=DegC
- `SO-C8661259C0DA`: BMS_thermalStatus / BMS_inletActiveCoolTargetT / unit=DegC
- `SO-364390148393`: UI_tripPlanning / UI_requestActiveBatteryHeating
- `SO-4A197BB1EE53`: VCFRONT_logging1Hz / VCFRONT_passiveCoolingState

This is **REFERENCE ONLY — NOT OBSERVED CONTROL CHAIN — NOT APPROVED EVIDENCE**.

### ASC observed behavior

- `SO-7717801FE8E8`: stability=LOW_CARDINALITY; changes=2; range=0.0..1.0; first change=141.2739 s (CAN observed state time); last change=248.3204 s (CAN observed state time); sequence=0 → 1 → 0
- `SO-BC7D879CB5FA`: stability=LOW_CARDINALITY; changes=4; first change=141.3329 s (CAN observed state time); last change=255.3398 s (CAN observed state time); sequence=PARTIAL → FULL → PARTIAL → NONE → PARTIAL
- Phase Feature: **UNAVAILABLE**. Planned windows provide context only and do not establish observed human event time.
- Relationship Evidence: **CURRENTLY LIMITED**. The frozen Observation Package does not contain synchronized cross-signal relationship features required to establish this relation.

### AI interpretation

- **OBSERVED**: Battery-heating activity and waste-heat request state changes support a thermal-control context, but no causal effect on capability or request is established.

### Currently supported

- ✓ Program mapping status is `PARTIAL_SUPPORT` for the bounded statement above; Signal Validation remains required.

### Not established

- ✗ No alternative-condition comparison separates thermal influence from other controls.

### Evidence gap

- Gap: `GAP-3B23-12`
- Missing evidence type: `ALTERNATIVE_CONDITION`
- Why it matters: No alternative-condition comparison separates thermal influence from other controls.

### Collection limitation

The collection predates the current Evidence architecture. Missing physical measurements or human event timestamps are not reconstructed from DBC labels or planned times.

### Audit trace

- Observation refs: `SO-7717801FE8E8, SO-BC7D879CB5FA`
- Candidate refs: `NONE`
- Raw ASC refs: `ASC-L122, ASC-L292266, ASC-L292390, ASC-L578215, ASC-L583363, ASC-L585461, ASC-L597592, ASC-L61, ASC-L685458, ASC-L685532`
- Reasoning package: `TM3-015-reasoning-f2f9203de6d5494d` / `1da118c87ee9299a4eb8e84a697edf652edec81741ad07dee9a82a76f5a1ad15`
- Reasoning result: `TM3-015-phase3b2_3-context-blind-replay-v5`

## ER-13 — Identify protection monitoring, limiting action, stop request, and safe shutdown without inventing fault causes

- Control Tree: `CT-DCFC-14`
- Binding / Finding: `EB-0013` / `F-3B23-13`
- Semantic status / confidence: `VALIDATION_REQUIRED` / `MEDIUM`
- Program review state: `HUMAN_REVIEW_REQUIRED`; human disposition: **UNSET**

### L3 question

Identify protection monitoring, limiting action, stop request, and safe shutdown without inventing fault causes.

Sufficiency boundary: Protection interpretation requires applicable safety and fault-state evidence.

### Direct Finding evidence

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-39C18ABF3E3C | KNOWN | 0x21D | CP_evseStatus | CP_stopChargeRequest | CP_evseStatus / CP_stopChargeRequest | stability=LOW_CARDINALITY; changes=12; range=0.0..1.0; first change=39.7192 s (CAN observed state time); last change=273.5338 s (CAN observed state time); sequence=0 → 1 → 0 → 1 → 0 → 1 → 0 → 1 … | DIRECT_INTENT_RETRIEVAL |
| SO-31D612FA2BA9 | KNOWN | 0x25D | CP_status | CP_vehicleUnlockRequest | CP_status / CP_vehicleUnlockRequest | stability=LOW_CARDINALITY; changes=12; range=0.0..1.0; first change=41.0186 s (CAN observed state time); last change=278.435 s (CAN observed state time); sequence=1 → 0 → 1 → 0 → 1 → 0 → 1 → 0 … | DIRECT_INTENT_RETRIEVAL |
| SO-4AA492D64A9C | KNOWN | 0x214 | FC_status | FC_voltageLimitAchieved | FC_status / FC_voltageLimitAchieved | stability=CONSTANT; changes=0; range=0.0..0.0; sequence=0 | DIRECT_INTENT_RETRIEVAL |
| SO-5772080DA750 | KNOWN | 0x214 | FC_status | FC_powerLimitAchieved | FC_status / FC_powerLimitAchieved | stability=CONSTANT; changes=0; range=0.0..0.0; sequence=0 | DIRECT_INTENT_RETRIEVAL |
| SO-61CF5F025B68 | KNOWN | 0x214 | FC_status | FC_currentLimitAchieved | FC_status / FC_currentLimitAchieved | stability=CONSTANT; changes=0; range=0.0..0.0; sequence=0 | DIRECT_INTENT_RETRIEVAL |

### Other retrieved candidates

These remain visible for review but were **not** used as Finding support.

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-6A427DF5AFB4 | KNOWN | 0x333 | UI_chargeRequest | UI_acChargeCurrentLimit | UI_chargeRequest / UI_acChargeCurrentLimit / unit=A / enum={"127": "SNA"} | stability=CONSTANT; changes=0; range=16.0..16.0; sequence=16 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0278 | UNKNOWN | 0x53F | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=2; bit transitions=6 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0005 | RESIDUAL | 0x108 | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=133; bit transitions=11311 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |

### DBC Semantic Reference — REFERENCE — NOT EVIDENCE BY ITSELF

- `SO-39C18ABF3E3C`: CP_evseStatus / CP_stopChargeRequest
- `SO-31D612FA2BA9`: CP_status / CP_vehicleUnlockRequest
- `SO-4AA492D64A9C`: FC_status / FC_voltageLimitAchieved
- `SO-5772080DA750`: FC_status / FC_powerLimitAchieved
- `SO-61CF5F025B68`: FC_status / FC_currentLimitAchieved
- `SO-6A427DF5AFB4`: UI_chargeRequest / UI_acChargeCurrentLimit / unit=A / enum={"127": "SNA"}

This is **REFERENCE ONLY — NOT OBSERVED CONTROL CHAIN — NOT APPROVED EVIDENCE**.

### ASC observed behavior

- `SO-39C18ABF3E3C`: stability=LOW_CARDINALITY; changes=12; range=0.0..1.0; first change=39.7192 s (CAN observed state time); last change=273.5338 s (CAN observed state time); sequence=0 → 1 → 0 → 1 → 0 → 1 → 0 → 1 …
- `SO-31D612FA2BA9`: stability=LOW_CARDINALITY; changes=12; range=0.0..1.0; first change=41.0186 s (CAN observed state time); last change=278.435 s (CAN observed state time); sequence=1 → 0 → 1 → 0 → 1 → 0 → 1 → 0 …
- `SO-4AA492D64A9C`: stability=CONSTANT; changes=0; range=0.0..0.0; sequence=0
- `SO-5772080DA750`: stability=CONSTANT; changes=0; range=0.0..0.0; sequence=0
- `SO-61CF5F025B68`: stability=CONSTANT; changes=0; range=0.0..0.0; sequence=0
- Phase Feature: **UNAVAILABLE**. Planned windows provide context only and do not establish observed human event time.
- Relationship Evidence: **CURRENTLY LIMITED**. The frozen Observation Package does not contain synchronized cross-signal relationship features required to establish this relation.

### AI interpretation

- **OBSERVED**: Stop and unlock request observations are present while selected limit-achieved states remain inactive; this supports stop observability but not a protection cause or safe-shutdown completion.

### Currently supported

- ✓ Program mapping status is `PARTIAL_SUPPORT` for the bounded statement above; Signal Validation remains required.

### Not established

- ✗ Applicable fault and protection decision evidence and independent safe-state confirmation are absent.

### Evidence gap

- Gap: `GAP-3B23-13`
- Missing evidence type: `CONDITION_OR_PERMISSION`
- Why it matters: Applicable fault and protection decision evidence and independent safe-state confirmation are absent.

### Collection limitation

The collection predates the current Evidence architecture. Missing physical measurements or human event timestamps are not reconstructed from DBC labels or planned times.

### Audit trace

- Observation refs: `SO-39C18ABF3E3C, SO-31D612FA2BA9, SO-4AA492D64A9C, SO-5772080DA750, SO-61CF5F025B68`
- Candidate refs: `NONE`
- Raw ASC refs: `ASC-L239851, ASC-L240253, ASC-L273533, ASC-L274543, ASC-L275550, ASC-L282612, ASC-L35, ASC-L37, ASC-L624868, ASC-L625080, ASC-L633371, ASC-L633571, ASC-L634196, ASC-L642692, ASC-L685438, ASC-L685440, ASC-L83365, ASC-L83378, ASC-L86107, ASC-L86314`
- Reasoning package: `TM3-015-reasoning-f2f9203de6d5494d` / `1da118c87ee9299a4eb8e84a697edf652edec81741ad07dee9a82a76f5a1ad15`
- Reasoning result: `TM3-015-phase3b2_3-context-blind-replay-v5`

## ER-14 — Describe controlled stop across Request, EVSE Actual, Pack Actual, high-voltage path, communication closeout, and safe unlock

- Control Tree: `CT-DCFC-15`
- Binding / Finding: `EB-0014` / `F-3B23-14`
- Semantic status / confidence: `VALIDATION_REQUIRED` / `LOW`
- Program review state: `HUMAN_REVIEW_REQUIRED`; human disposition: **UNSET**

### L3 question

Describe controlled stop across Request, EVSE Actual, Pack Actual, high-voltage path, communication closeout, and safe unlock.

Sufficiency boundary: CAN state time is not human action time, and a missing initiator remains an evidence gap.

### Direct Finding evidence

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-31D612FA2BA9 | KNOWN | 0x25D | CP_status | CP_vehicleUnlockRequest | CP_status / CP_vehicleUnlockRequest | stability=LOW_CARDINALITY; changes=12; range=0.0..1.0; first change=41.0186 s (CAN observed state time); last change=278.435 s (CAN observed state time); sequence=1 → 0 → 1 → 0 → 1 → 0 → 1 → 0 … | DIRECT_INTENT_RETRIEVAL |
| SO-7BB7F570959A | KNOWN | 0x21D | CP_evseStatus | CP_proximity | CP_evseStatus / CP_proximity / enum={"0": "SNA", "1": "DISCONNECTED", "2": "UNLATCHED", "3": "LATCHED"} | stability=LOW_CARDINALITY; changes=2; first change=39.7192 s (CAN observed state time); last change=273.5338 s (CAN observed state time); sequence=SNA → DISCONNECTED → SNA | DIRECT_INTENT_RETRIEVAL |
| SO-DCF64D235226 | KNOWN | 0x7AA | HVP_debugMessage | HVP_gpioCpLatchEnable | HVP_debugMessage / HVP_gpioCpLatchEnable | stability=LOW_CARDINALITY; changes=2; range=0.0..1.0; first change=135.1584 s (CAN observed state time); last change=247.1598 s (CAN observed state time); sequence=0 → 1 → 0 | DIRECT_INTENT_RETRIEVAL |

### Other retrieved candidates

These remain visible for review but were **not** used as Finding support.

| Observation | Space | CAN / Bus | Message | Signal | DBC semantic | Frozen behavior | Provenance |
|---|---|---|---|---|---|---|---|
| SO-C6316DC7735B | KNOWN | 0x359 | VCSEC_BLEDeviceStatus | VCSEC_mobileAppVersion | VCSEC_BLEDeviceStatus / VCSEC_mobileAppVersion | stability=DYNAMIC; changes=2192; range=0.0..246.0; first change=0.1073 s (CAN observed state time); last change=299.7283 s (CAN observed state time); sequence=0 → 60 → 0 → 93 → 141 → 234 → 0 → 238 … | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-30E936829754 | KNOWN | 0x1F9 | VCSEC_requests | VCSEC_chargePortRequest | VCSEC_requests / VCSEC_chargePortRequest / enum={"0": "NONE", "1": "OPEN", "2": "CLOSE", "3": "SNA"} | stability=LOW_CARDINALITY; changes=2; first change=268.6751 s (CAN observed state time); last change=268.9751 s (CAN observed state time); sequence=NONE → OPEN → NONE | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| SO-330F3936C51C | KNOWN | 0x2E1 | VCFRONT_status | VCFRONT_reverseBatteryFault | VCFRONT_status / VCFRONT_reverseBatteryFault | stability=LOW_CARDINALITY; changes=16; range=0.0..1.0; first change=142.298 s (CAN observed state time); last change=157.3709 s (CAN observed state time); sequence=0 → 1 → 0 → 1 → 0 → 1 → 0 → 1 … | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0005 | RESIDUAL | 0x108 | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=133; bit transitions=11311 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |
| OBS-0012 | UNKNOWN | 0x128 | — | UNNAMED OBSERVATION | NONE / UNKNOWN / NOT DEFINED | raw payload cardinality=5; bit transitions=9 | RETRIEVED CANDIDATE — NOT FINDING EVIDENCE |

### DBC Semantic Reference — REFERENCE — NOT EVIDENCE BY ITSELF

- `SO-31D612FA2BA9`: CP_status / CP_vehicleUnlockRequest
- `SO-7BB7F570959A`: CP_evseStatus / CP_proximity / enum={"0": "SNA", "1": "DISCONNECTED", "2": "UNLATCHED", "3": "LATCHED"}
- `SO-DCF64D235226`: HVP_debugMessage / HVP_gpioCpLatchEnable
- `SO-C6316DC7735B`: VCSEC_BLEDeviceStatus / VCSEC_mobileAppVersion
- `SO-30E936829754`: VCSEC_requests / VCSEC_chargePortRequest / enum={"0": "NONE", "1": "OPEN", "2": "CLOSE", "3": "SNA"}
- `SO-330F3936C51C`: VCFRONT_status / VCFRONT_reverseBatteryFault

This is **REFERENCE ONLY — NOT OBSERVED CONTROL CHAIN — NOT APPROVED EVIDENCE**.

### ASC observed behavior

- `SO-31D612FA2BA9`: stability=LOW_CARDINALITY; changes=12; range=0.0..1.0; first change=41.0186 s (CAN observed state time); last change=278.435 s (CAN observed state time); sequence=1 → 0 → 1 → 0 → 1 → 0 → 1 → 0 …
- `SO-7BB7F570959A`: stability=LOW_CARDINALITY; changes=2; first change=39.7192 s (CAN observed state time); last change=273.5338 s (CAN observed state time); sequence=SNA → DISCONNECTED → SNA
- `SO-DCF64D235226`: stability=LOW_CARDINALITY; changes=2; range=0.0..1.0; first change=135.1584 s (CAN observed state time); last change=247.1598 s (CAN observed state time); sequence=0 → 1 → 0
- Phase Feature: **UNAVAILABLE**. Planned windows provide context only and do not establish observed human event time.
- Relationship Evidence: **CURRENTLY LIMITED**. The frozen Observation Package does not contain synchronized cross-signal relationship features required to establish this relation.

### AI interpretation

- **OBSERVED**: Unlock request, proximity, and charge-port latch-enable observations provide partial controlled-exit coverage, but the initiator, communication closeout, energy decay, and human action time are not established.

### Currently supported

- ✓ Program mapping status is `PARTIAL_SUPPORT` for the bounded statement above; Signal Validation remains required.

### Not established

- ✗ Planned time cannot substitute for observed stop or unplug time and several exit stages lack direct evidence.

### Evidence gap

- Gap: `GAP-3B23-14`
- Missing evidence type: `EXTERNAL_EVENT_TIME`
- Why it matters: Planned time cannot substitute for observed stop or unplug time and several exit stages lack direct evidence.

### Collection limitation

The collection predates the current Evidence architecture. Missing physical measurements or human event timestamps are not reconstructed from DBC labels or planned times.

### Audit trace

- Observation refs: `SO-31D612FA2BA9, SO-7BB7F570959A, SO-DCF64D235226`
- Candidate refs: `NONE`
- Raw ASC refs: `ASC-L279854, ASC-L341, ASC-L35, ASC-L37, ASC-L580365, ASC-L624868, ASC-L625080, ASC-L633371, ASC-L633571, ASC-L634387, ASC-L642692, ASC-L684524, ASC-L685438, ASC-L685440, ASC-L83365, ASC-L86107, ASC-L86314`
- Reasoning package: `TM3-015-reasoning-f2f9203de6d5494d` / `1da118c87ee9299a4eb8e84a697edf652edec81741ad07dee9a82a76f5a1ad15`
- Reasoning result: `TM3-015-phase3b2_3-context-blind-replay-v5`
