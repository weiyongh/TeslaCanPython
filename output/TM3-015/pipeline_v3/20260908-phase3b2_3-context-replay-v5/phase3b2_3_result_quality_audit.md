# Phase 3B.2.3 Interrupted Implementation Recovery & Result Quality Audit

## Outcome

Status: `AWAITING_EVIDENCE_REVIEW`.

The interrupted implementation was recovered without redesign, ASC reread, Trace Store backfill, or entry into Phase 3B.3. The final replay uses the existing frozen Observation Package and produces review-only Evidence Binding drafts.

## Recovery integrity

The recovery inspection covered the modified call chain:

- `input/TM3-015_experiment_procedure_v1.json`
- `input/TM3-015_formal_discovery_charter.json`
- `src/analysis_charter.py`
- `src/observation_context_adapter.py`
- `src/semantic_observation_retrieval.py`
- `src/semantic_reasoning_contract.py`
- `src/formal_pipeline.py`
- `src/evidence_mapping_adapter.py`
- `tests/test_semantic_observation_retrieval.py`

No incomplete `semantic/explain` token, recovery placeholder, invalid import, syntax error, or broken call signature remained. One duplicate `observation_provenance` dictionary key in the mapping adapter was removed and covered by a regression assertion.

Implemented recovery scope:

- deterministic Procedure Contract loading and source-hash validation;
- Collection Script planned-phase context in Reasoning Input;
- one generic Semantic Evidence Question per ER;
- Observation Context Adapter with explicit unavailable phase/relationship features;
- context-aware retrieval with semantic-domain coverage;
- direct/cross/global provenance contract and validation;
- review-only Evidence Mapping propagation.

No TM3-015 signal whitelist, historical timestamp, expected transition, special signal-name answer rule, or Approved Evidence path was added.

## Test result

- Python syntax/import compilation: PASS.
- Full test suite: **75/75 PASS**.
- `git diff --check`: PASS.
- `pytest` was not used because it is not installed in the project virtual environment; the repository's complete `unittest discover` suite was used.

## Final frozen replay

Run: `20260908-phase3b2_3-context-replay-v5`

- Reasoning package: `TM3-015-reasoning-f2f9203de6d5494d`
- Package hash: `1da118c87ee9299a4eb8e84a697edf652edec81741ad07dee9a82a76f5a1ad15`
- Semantic Prior fingerprint: `6d9076df47fd55ab504c8185ea92ac2b407614a72c83d3d4d11cd0e4320d4ce4`
- Control Tree fingerprint: `366634636e299d6939f0843560c1f4fd03e39f249615acf85677c62de31b5bef`
- ER fingerprint: `d48bc755071728f741b16122f7f73868336629c8b5556ffe9346bcb55821de42`
- Procedure source SHA-256: `400f83d81240611c384dc37fecb7b3e276e325c694235454b31553dbf4984a0d`
- Observation Context hash: `00684f6a3fd79ff41918206a64eeb18951a82620b7742de3cc7a8d41d097bf62`
- Semantic Evidence Questions / Intents: **14 / 14**
- Retrieval rows: **108**
- Unique retrieved Observations: **62**
- Unique source distribution: **Known 54 / Residual 3 / Unknown 5**
- Row distribution: **Known 80 / Residual 14 / Unknown 14**
- Reasoning calls: **1**
- Deterministic follow-up: **0**
- Findings: **14**
- Evidence Binding drafts: **14**
- Promotion state: **HUMAN_REVIEW_REQUIRED 9 / HOLD_UNRESOLVED 5**
- Approval state: `NOT_APPROVED`
- ASC parse count inherited from Discovery: **1**
- ASC reparses during replay: **0**


## Lineage

Every finding follows:

`L3/ER → SEQ-ER-xx → SSI-ER-xx → DIRECT_INTENT_RETRIEVAL Observation → F-3B23-xx → EB-xxxx`

All 108 retrieval rows are labelled `DIRECT_INTENT_RETRIEVAL`. The replay used no cross-intent supplement and no global-context Observation as finding evidence. Output validation passed with zero unknown references and full Observation provenance closure.

## Quality change

Relative to the first formal run:

| Metric | First formal run | Context replay v5 |
|---|---:|---:|
| Intents | 27 | 14 ER-scoped |
| Unique Observations | 25 | 62 |
| Findings | 5 | 14 |
| Explicit semantic boundaries | coarse role split | ER-specific evidence questions |
| Procedure context | absent | planned-only, hash-bound |
| Provenance | observation reference only | direct/cross/global contract |

The 27→14 change is intentional: role-fragment intents were replaced by one evidence question per ER. The larger 62-Observation recall comes from semantic domains and Observation context, not exact-signal reproduction.

Recovered semantic needs:

- interface and lock stages: partial candidates, independent physical confirmation remains GAP;
- auxiliary supply/wake: electrical context retrieved, A-contact/supply/wake separation remains GAP;
- communication: generic candidates retrieved, protocol-stage semantics remain GAP;
- EVSE Capability: not established; EVSE Actual is explicitly rejected as substitution;
- Vehicle Capability: maximum-current/power candidates are partial and require validation;
- Vehicle Request: remains `INSUFFICIENT_EVIDENCE`; Actual and Capability do not substitute;
- Permission: remains separate from contactor state and energy transfer;
- HV Path: request/status/set-state candidates provide partial state evidence;
- EVSE Actual versus Pack Actual: both boundaries are retrieved and kept separate;
- continuous relationship: incomplete because Request remains missing;
- thermal: contextual activity is retrieved without causal upgrade;
- protection/stop: stop candidates are present without inventing a fault cause;
- controlled exit: interface/HV/stop branches are present, but observed human time and full closeout remain GAP.

## DBC dominance and over-interpretation audit

DBC-labelled Known observations still dominate selection: **80/108 rows (74.1%)**. Eligibility paths are:

- `SEMANTIC_CONTEXT_COMPATIBLE`: 61
- `PROCEDURE_ALIGNED_DOMAIN_HINT`: 11
- `PHYSICAL_DIMENSION_BEHAVIOR`: 3
- `UNNAMED_BEHAVIOR_CONTEXT`: 28
- `BEHAVIOR_EXPLORATORY`: 5

Therefore DBC terminology no longer exclusively controls retrieval, but it remains the largest influence. False-positive examples remain, including unrelated latch/communication names and constant fields. These were not used as confirmed semantic roles.

Multiple semantic projection is also broad. `OBS-0005` appears in 11 intents and `OBS-0012` in 6; the leading EVSE voltage/current observations appear in 5/4 intents. Reuse across related ERs can be legitimate, but unnamed candidates repeated across unrelated domains are a **possible over-interpretation / threshold-width issue**. The reasoning result limits this risk by using only direct ER evidence, treating names as candidates, requiring Signal Validation, and emitting gaps rather than filling missing roles.

## Finding-change classification

Compared with the prior 11-finding L3 replay:

- **PRESERVED:** Request gap; Permission versus contactor boundary; EVSE Actual versus Pack Actual boundary.
- **REFINED:** interface/lock, HV path, thermal, protection/stop, and controlled-exit findings now have ER-specific direct provenance.
- **SPLIT_BY_NEW_L3:** EVSE Capability and Vehicle Capability are separate; Actual boundary and continuous control relationship are separate.
- **NEW_SEMANTIC_NEED:** auxiliary supply/wake separation and explicit communication-stage evidence.
- **DROPPED_AS_UNSUPPORTED:** no historical role or exact-signal conclusion was carried forward solely because it appeared in an earlier report.
- **RETRIEVAL_RECALL_GAP:** no validated Vehicle Request voltage/current pair, no direct Permission variable, no complete protocol-stage set.
- **POSSIBLE_OVER_INTERPRETATION:** repeated unnamed observations and a few generic DBC-label matches across multiple intents.

## Remaining issues

1. Retrieval eligibility is still permissive: eligible counts are much larger than the per-intent output, and source quota competition often selects one Residual and one Unknown candidate even when their semantic specificity is weak. They passed the current threshold, so this does not violate the quota rule, but threshold quality needs human review.
2. DBC terms remain influential and some unrelated subsystem names survive context matching.
3. Observed phase/transition and relationship features remain unavailable by contract: `PHASE_FEATURE_UNAVAILABLE` / `RELATIONSHIP_FEATURE_UNAVAILABLE`; they were not inferred and ASC was not reread.
4. Quantitative EVSE-current semantics remain unvalidated; no cross-boundary closure is claimed.
5. Strict cognitive blindness cannot be certified for this recovery session because it had historical project exposure. Artifact-level input isolation was enforced, but session-level non-exposure cannot be proven.

## Stop condition

No Approved Evidence, Evidence Assessment, Renderer input, formal four-document report, or Phase 3B.3 artifact was generated.

**AWAITING_EVIDENCE_REVIEW**
