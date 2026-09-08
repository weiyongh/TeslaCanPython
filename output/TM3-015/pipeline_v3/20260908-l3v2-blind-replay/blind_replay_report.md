# TM3-015 Fast-Charge L3 Prior Blind Replay

Status: `AWAITING_EVIDENCE_REVIEW`

## Frozen inputs and fingerprints

- Replay source: `output/TM3-015/pipeline_v3/20260907T235633-dd8ac28b/observation_package.json`
- ASC reparse for replay: `0`
- Recorded ASC parse count: `1` (inherited from frozen Discovery trace)
- L3 source SHA-256: `59ab6c5fa499b896196fb715acf1d10fea77b93cea4e51679cdcb10fe5f33c6f`
- L3 semantic prior fingerprint: `6d9076df47fd55ab504c8185ea92ac2b407614a72c83d3d4d11cd0e4320d4ce4`
- Control Tree fingerprint: `366634636e299d6939f0843560c1f4fd03e39f249615acf85677c62de31b5bef`
- Evidence Requirement fingerprint: `d48bc755071728f741b16122f7f73868336629c8b5556ffe9346bcb55821de42`
- Reasoning package: `TM3-015-reasoning-da477196fb3331c3`
- Reasoning package hash: `59182d91f76e2d4a3d3e262158241fd4d313c85bf68c11deafb2addb6ebd27dc`
- Retrieval algorithm: `semantic-observation-retrieval-v1`; implementation SHA-256: `27fbe2ef3d1f3c9665fbd8fba61dbb4f86f90884cd358ce9293e0b7576eddd72`

## Retrieval trace

- SemanticSearchIntent: `36`
- Intent role categories: Request `9`, Actual `9`, State `8`, Capability `7`, Permission `2`, Timing-only `1`
- Unique retrieved observations: `26`
- Source spaces: Known `23`, Residual `2`, Unknown `1`
- Below-threshold observations were not quota-promoted. Every intent had at least one eligible retrieval candidate, so `no_suitable_observation=true` count is `0`.
- The frozen package has no reliable phase or relationship feature. Reasoning records `PHASE_FEATURE_UNAVAILABLE` and `RELATIONSHIP_FEATURE_UNAVAILABLE` rather than reconstructing them.

## Semantic need disposition

| Need | Retrieval candidate | Reasoning disposition |
|---|---:|---|
| ER-01 nine-terminal interface / connection | yes | GAP — independent physical and connection-confirmation evidence absent |
| ER-02 locking stages | yes | PARTIAL — latch/unlock candidates; stages remain unseparated |
| ER-03 auxiliary supply / wake | yes | GAP — contact, supply, wake, and ready cannot be separated |
| ER-04 communication stages | yes | GAP — handshake/version/parameter stages unvalidated |
| ER-05 EVSE Capability | yes | GAP — no validated capability boundary |
| ER-06 Vehicle Capability | yes | GAP — no validated vehicle boundary |
| ER-07 Vehicle Request | yes | GAP — no validated request voltage/current pair |
| ER-08 Permission / Safety Gate | yes | GAP — permission not independently observed |
| ER-09 HV Path | yes | PARTIAL — contactor/HVIL candidates; path and transfer unproven |
| ER-10 EVSE Actual / Pack Actual | yes | PARTIAL — EVSE-voltage candidate only; Pack boundary missing |
| ER-11 continuous control relation | yes | GAP — missing roles and relationship feature |
| ER-12 Thermal | yes | GAP — charge-specific thermal chain unvalidated |
| ER-13 Protection | yes | GAP — limiting/stop/fault causality unvalidated |
| ER-14 controlled exit | yes | GAP — phase, initiator, and synchronized exit stages absent |

## Reasoning, validation, and mapping

- Primary reasoning calls: `1`
- Targeted deterministic follow-up: `1` (removed two prohibited numeric-statistic restatements; semantic decisions unchanged)
- Findings: `11`
- Proposed roles: State `5`, Unresolved `2`, Timing-only `1`, Capability `1`, Request `1`, Actual `1`
- Semantic states: `VALIDATION_REQUIRED 3`, `INSUFFICIENT_EVIDENCE 5`, `UNVALIDATED 3`
- Reference validation: `PASS`; unknown references: `0`
- Evidence Mapping Draft bindings: `11`
- Promotion states: `HUMAN_REVIEW_REQUIRED 3`, `HOLD_UNRESOLVED 8`

The semantic boundaries remain explicit: mechanical A-terminal contact is not auxiliary supply or wake; Capability, Request, Permission, contactor state, Actual, and energy transfer are not substituted for one another; EVSE Actual and Pack Actual remain separate measurement boundaries. The generic communication flow is not treated as a fixed vehicle-ECU software sequence.

## Regression

- Full suite: `75/75 PASS` using `python -m unittest discover`.
- No Approved Evidence, Assessment, Renderer, formal report set, or Phase 3B.3 artifact was produced.
