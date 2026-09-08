# TM3-015 LLM 前分析输入审计

> 这是 LLM 前输入可见性产物，不是 Human Evidence Review，不是 Approved Evidence。

## 总览

- Experiment / Run ID：`TM3-015` / `20260908-phase3b2_3-context-replay-v5`
- Reasoning Package ID：`TM3-015-reasoning-f2f9203de6d5494d`
- Package Hash：`1da118c87ee9299a4eb8e84a697edf652edec81741ad07dee9a82a76f5a1ad15`
- Evidence Requirement / Semantic Question：14 / 14
- Retrieval 总行数：108
- Unique Observation：62
- Model Provider：冻结运行中未记录
- Model Name：冻结运行中未记录
- Model Identity：codex-recovery-session
- Reasoning / Effort：冻结运行中未记录
- 冻结运行 LLM Call：1
- 冻结运行 Follow-up Call：0
- 本次审计新增 LLM Call：0

### Source Artifact 与 Hash

- `semantic_reasoning_input.json`：`4c8b747fa35ddc1401cc0e986b7c7c5491b233e002fd00594283438979d29af7`
- `semantic_reasoning_output.json`：`ff72bfa0b4a146425ecf70c73889f8c8191b09d27ef58ce35a2c74d0cc23364b`
- `evidence_mapping_draft.json`：`7464e8364f6179e02fadefcd89d84d07078e26ec7972e103c2b4dcea3edbe22e`
- `runtime_audit.json`：`706698043cae895a893c386e07a5a0f2c17e069eefe368586aae60d632f2f072`
- `experiment_procedure.json`：`1d3bd2a725c985df8c27099815a7d3d0681365956b1f6343f5f44efae5759eaa`
- `semantic_evidence_questions.json`：`f498acd955f00a235a346673f73c9f177fa68d764beb57d155e38f8683345b02`
- `semantic_search_intents.json`：`b8e1b659b96b9d572f2ef3a0892e51a6e7ce9fdcc6dfb544a71a46a87d358127`
- `semantic_retrieval_results.json`：`2668fca5ca4c7746d86b78ba327f3460fbaacf910b5ac7181e4f7b58aa2887e2`
- `observation_contexts.json`：`1a9f4867c8bfebdae44fa7d1f17794486d3c9efd831d1c9d02e3fc3ba7df8cb8`

## 实际 LLM Payload 可见性

冻结运行未保留可证明的最终 LLM Call Payload。

冻结运行没有保存可核验的 System / Developer Instruction、Provider、真实 Model Name、Effort 或最终请求 envelope；当前代码也没有可证明与当时调用完全相同的确定性 Call Builder。因此本产物不声称重建 Exact Payload。

最接近调用边界、可验证的权威 Pre-call Object 是：

- `semantic_reasoning_input.json` 根对象：JSON Pointer `/`
- Package ID / Hash：`TM3-015-reasoning-f2f9203de6d5494d` / `1da118c87ee9299a4eb8e84a697edf652edec81741ad07dee9a82a76f5a1ad15`
- Canonical request envelope：不可证明，未生成近似 envelope。

## ER-01 — Distinguish nine-terminal mechanical interface conditions from confirmed physical connection

### A. 语义目标

- ER：`ER-01`
- Control Tree Reference：`CT-DCFC-01, CT-DCFC-03, CT-DCFC-10, CT-DCFC-14, CT-DCFC-15`
- Semantic Evidence Question：Distinguish nine-terminal mechanical interface conditions from confirmed physical connection.
- Sufficiency / Semantic Boundary：Independent evidence is required for mechanical contact and connection confirmation.
- Candidate Role（未确认）：`STATE`
- Forbidden Substitution：`ACTUAL, CAPABILITY, PERMISSION, REQUEST`
- Collection Script / Planned Procedure Context：`PP-PORT-OPEN`（open charge port without connecting；20–40 s；PLANNED_TIME）; `PP-CONNECT`（connect charging interface and record recognition and locking when independently observed；40–60 s；PLANNED_TIME）
- 时间边界：`PLANNED_TIME_IS_NOT_OBSERVED_EVENT_TIME`

### B. 实际送入 LLM 的 Observation

| Observation | Space | CAN ID / Bus | Message / Signal | DBC 参考 | ASC 实际行为 | Retrieval Provenance |
|---|---|---|---|---|---|---|
| SO-BA9225550260 | KNOWN | 0x339 | VCSEC_authentication / VCSEC_chargePortLockStatus | VCSEC_authentication / VCSEC_chargePortLockStatus / enum={"0": "UNLOCKED", "1": "LOCKED"} | 稳定性=LOW_CARDINALITY；变化次数=0；序列=UNLOCKED | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-57834B9DC181 | KNOWN | 0x25D | CP_status / CP_latch2ControlState | CP_status / CP_latch2ControlState / enum={"0": "latchInit", "1": "latchIdle", "2": "latchDisengageRequested", "3": "latchDisengaging", "4": "latchDisengaged", "5": "latchEngaging"} | 稳定性=LOW_CARDINALITY；变化次数=7；首次变化=21.0173 s（CAN Observed Time）；末次变化=277.2349 s（CAN Observed Time）；序列=latchInit → latchDisengaged → latchDisengaging → latchDisengageRequested → latchEngaging → latchDisengaging → latchDisengaged → latchInit | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-7C154FF11732 | KNOWN | 0x25D | CP_status / CP_latchControlState | CP_status / CP_latchControlState / enum={"0": "latchInit", "1": "latchIdle", "2": "latchDisengageRequested", "3": "latchDisengaging", "4": "latchDisengaged", "5": "latchEngaging"} | 稳定性=LOW_CARDINALITY；变化次数=10；首次变化=21.0173 s（CAN Observed Time）；末次变化=277.1347 s（CAN Observed Time）；序列=latchIdle → latchDisengaging → latchDisengaged → latchEngaging → latchIdle → latchDisengaging → latchDisengaged → latchDisengaging … | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-AFC76E33264C | KNOWN | 0x25D | CP_status / CP_latchState | CP_status / CP_latchState / enum={"0": "SNA", "1": "DISENGAGED", "2": "ENGAGED", "3": "BLOCKING"} | 稳定性=LOW_CARDINALITY；变化次数=2；首次变化=20.7178 s（CAN Observed Time）；末次变化=278.635 s（CAN Observed Time）；序列=DISENGAGED → BLOCKING → DISENGAGED | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-7BB7F570959A | KNOWN | 0x21D | CP_evseStatus / CP_proximity | CP_evseStatus / CP_proximity / enum={"0": "SNA", "1": "DISCONNECTED", "2": "UNLATCHED", "3": "LATCHED"} | 稳定性=LOW_CARDINALITY；变化次数=2；首次变化=39.7192 s（CAN Observed Time）；末次变化=273.5338 s（CAN Observed Time）；序列=SNA → DISCONNECTED → SNA | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-0CCE9DD26636 | KNOWN | 0x102 | VCLEFT_doorStatus / VCLEFT_frontLatchSwitch | VCLEFT_doorStatus / VCLEFT_frontLatchSwitch | 稳定性=CONSTANT；变化次数=0；最小值=1.0；最大值=1.0；序列=1 | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| OBS-0096 | UNKNOWN | 0x2BE | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=754 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |
| OBS-0005 | RESIDUAL | 0x108 | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=11311 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |

### C. 为什么进入输入（DBC REFERENCE METADATA — 仅供参考，不是 Evidence）

- `SO-BA9225550260`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": [], "domain_concepts": ["INTERFACE"], "domain_terms": ["lock", "port"], "planned_phase_refs": [], "role_terms": ["status"]}`。不据此确认 Semantic Role。
- `SO-57834B9DC181`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["INTERFACE"], "domain_terms": ["latch"], "planned_phase_refs": ["PP-PORT-OPEN"], "role_terms": ["state", "status"]}`。不据此确认 Semantic Role。
- `SO-7C154FF11732`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["INTERFACE"], "domain_terms": ["latch"], "planned_phase_refs": ["PP-PORT-OPEN"], "role_terms": ["state", "status"]}`。不据此确认 Semantic Role。
- `SO-AFC76E33264C`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["INTERFACE"], "domain_terms": ["latch"], "planned_phase_refs": ["PP-PORT-OPEN"], "role_terms": ["state", "status"]}`。不据此确认 Semantic Role。
- `SO-7BB7F570959A`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["INTERFACE"], "domain_terms": ["proximity"], "planned_phase_refs": ["PP-PORT-OPEN"], "role_terms": ["status"]}`。不据此确认 Semantic Role。
- `SO-0CCE9DD26636`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": [], "domain_concepts": ["INTERFACE"], "domain_terms": ["latch"], "planned_phase_refs": [], "role_terms": ["status"]}`。不据此确认 Semantic Role。
- `OBS-0096`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": ["PP-PORT-OPEN"], "role_terms": []}`。不据此确认 Semantic Role。
- `OBS-0005`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": [], "role_terms": []}`。不据此确认 Semantic Role。

### D. LLM 获得的 Structured Context

- `SO-BA9225550260` identity_hint：`{"bus_key": "ch1:0x339", "dbc_name_hint": "VCSEC_chargePortLockStatus", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "VCSEC_authentication", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-BA9225550260` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 1, "change_count": 0, "first_change_time_s": null, "last_change_time_s": null, "stability_class": "LOW_CARDINALITY", "tags": []}`
- `SO-BA9225550260` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-BA9225550260` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-BA9225550260` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-57834B9DC181` identity_hint：`{"bus_key": "ch1:0x25D", "dbc_name_hint": "CP_latch2ControlState", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_status", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-57834B9DC181` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 5, "change_count": 7, "first_change_time_s": 21.0173, "last_change_time_s": 277.2349, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-57834B9DC181` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-PORT-OPEN", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-57834B9DC181` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-57834B9DC181` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-7C154FF11732` identity_hint：`{"bus_key": "ch1:0x25D", "dbc_name_hint": "CP_latchControlState", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_status", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-7C154FF11732` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 4, "change_count": 10, "first_change_time_s": 21.0173, "last_change_time_s": 277.1347, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-7C154FF11732` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-PORT-OPEN", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-7C154FF11732` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-7C154FF11732` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-AFC76E33264C` identity_hint：`{"bus_key": "ch1:0x25D", "dbc_name_hint": "CP_latchState", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_status", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-AFC76E33264C` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 2, "first_change_time_s": 20.7178, "last_change_time_s": 278.635, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-AFC76E33264C` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-PORT-OPEN", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-AFC76E33264C` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-AFC76E33264C` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-7BB7F570959A` identity_hint：`{"bus_key": "ch1:0x21D", "dbc_name_hint": "CP_proximity", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_evseStatus", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-7BB7F570959A` behavior：`{"anomaly_flags": ["SNA_PRESENT"], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 2, "first_change_time_s": 39.7192, "last_change_time_s": 273.5338, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-7BB7F570959A` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-PORT-OPEN", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-7BB7F570959A` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-7BB7F570959A` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-0CCE9DD26636` identity_hint：`{"bus_key": "ch1:0x102", "dbc_name_hint": "VCLEFT_frontLatchSwitch", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "VCLEFT_doorStatus", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-0CCE9DD26636` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 1, "change_count": 0, "first_change_time_s": null, "last_change_time_s": null, "stability_class": "CONSTANT", "tags": []}`
- `SO-0CCE9DD26636` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-0CCE9DD26636` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-0CCE9DD26636` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0096` identity_hint：`{"bus_key": "ch1:0x2BE", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0096` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 145, "change_count": 754, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "UNNAMED_ACTIVITY"]}`
- `OBS-0096` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-PORT-OPEN", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0096` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0096` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0005` identity_hint：`{"bus_key": "ch1:0x108", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0005` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 133, "change_count": 11311, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "UNNAMED_ACTIVITY"]}`
- `OBS-0005` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0005` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0005` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`

### E. 精确输入追溯

- Question：`/semantic_evidence_questions/0`
- Per-question evidence：`/per_question_evidence/0`
- Intent：`/semantic_search_intents/0` (`SSI-ER-01`)
- Retrieval result：`/retrieval_results/0`
- Observation objects：`/observations/0` → `SO-BA9225550260`, `/observations/1` → `SO-57834B9DC181`, `/observations/2` → `SO-7C154FF11732`, `/observations/3` → `SO-AFC76E33264C`, `/observations/4` → `SO-7BB7F570959A`, `/observations/5` → `SO-0CCE9DD26636`, `/observations/6` → `OBS-0096`, `/observations/7` → `OBS-0005`
- Observation contexts：`/observation_contexts/51` → `SO-BA9225550260`, `/observation_contexts/15` → `SO-57834B9DC181`, `/observation_contexts/16` → `SO-7C154FF11732`, `/observation_contexts/17` → `SO-AFC76E33264C`, `/observation_contexts/19` → `SO-7BB7F570959A`, `/observation_contexts/49` → `SO-0CCE9DD26636`, `/observation_contexts/60` → `OBS-0096`, `/observation_contexts/54` → `OBS-0005`

## ER-02 — Distinguish connection confirmation from lock request, lock execution, lock feedback, and confirmed lock

### A. 语义目标

- ER：`ER-02`
- Control Tree Reference：`CT-DCFC-01, CT-DCFC-03, CT-DCFC-10, CT-DCFC-14, CT-DCFC-15`
- Semantic Evidence Question：Distinguish connection confirmation from lock request, lock execution, lock feedback, and confirmed lock.
- Sufficiency / Semantic Boundary：A single state label cannot satisfy all locking stages.
- Candidate Role（未确认）：`REQUEST, STATE`
- Forbidden Substitution：`ACTUAL, CAPABILITY, PERMISSION`
- Collection Script / Planned Procedure Context：`PP-PORT-OPEN`（open charge port without connecting；20–40 s；PLANNED_TIME）; `PP-CONNECT`（connect charging interface and record recognition and locking when independently observed；40–60 s；PLANNED_TIME）; `PP-CHARGE-OBSERVE`（observe EVSE and Pack voltage current power capability state and thermal context；150–210 s；PLANNED_TIME）; `PP-STEADY-HOLD`（observe a conditional short stable interval if naturally available；210–240 s；PLANNED_TIME）; `PP-STOP`（request one normal stop if charging has not already ended；240–270 s；PLANNED_TIME）
- 时间边界：`PLANNED_TIME_IS_NOT_OBSERVED_EVENT_TIME`

### B. 实际送入 LLM 的 Observation

| Observation | Space | CAN ID / Bus | Message / Signal | DBC 参考 | ASC 实际行为 | Retrieval Provenance |
|---|---|---|---|---|---|---|
| SO-BA9225550260 | KNOWN | 0x339 | VCSEC_authentication / VCSEC_chargePortLockStatus | VCSEC_authentication / VCSEC_chargePortLockStatus / enum={"0": "UNLOCKED", "1": "LOCKED"} | 稳定性=LOW_CARDINALITY；变化次数=0；序列=UNLOCKED | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-57834B9DC181 | KNOWN | 0x25D | CP_status / CP_latch2ControlState | CP_status / CP_latch2ControlState / enum={"0": "latchInit", "1": "latchIdle", "2": "latchDisengageRequested", "3": "latchDisengaging", "4": "latchDisengaged", "5": "latchEngaging"} | 稳定性=LOW_CARDINALITY；变化次数=7；首次变化=21.0173 s（CAN Observed Time）；末次变化=277.2349 s（CAN Observed Time）；序列=latchInit → latchDisengaged → latchDisengaging → latchDisengageRequested → latchEngaging → latchDisengaging → latchDisengaged → latchInit | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-7C154FF11732 | KNOWN | 0x25D | CP_status / CP_latchControlState | CP_status / CP_latchControlState / enum={"0": "latchInit", "1": "latchIdle", "2": "latchDisengageRequested", "3": "latchDisengaging", "4": "latchDisengaged", "5": "latchEngaging"} | 稳定性=LOW_CARDINALITY；变化次数=10；首次变化=21.0173 s（CAN Observed Time）；末次变化=277.1347 s（CAN Observed Time）；序列=latchIdle → latchDisengaging → latchDisengaged → latchEngaging → latchIdle → latchDisengaging → latchDisengaged → latchDisengaging … | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-AFC76E33264C | KNOWN | 0x25D | CP_status / CP_latchState | CP_status / CP_latchState / enum={"0": "SNA", "1": "DISENGAGED", "2": "ENGAGED", "3": "BLOCKING"} | 稳定性=LOW_CARDINALITY；变化次数=2；首次变化=20.7178 s（CAN Observed Time）；末次变化=278.635 s（CAN Observed Time）；序列=DISENGAGED → BLOCKING → DISENGAGED | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-23B9FBB08D32 | KNOWN | 0x142 | VCLEFT_liftgateStatus / VCLEFT_liftgateLatchRequest | VCLEFT_liftgateStatus / VCLEFT_liftgateLatchRequest / enum={"0": "LATCH_REQUEST_NONE", "1": "LATCH_REQUEST_CINCH", "2": "LATCH_REQUEST_RELEASE", "3": "LATCH_REQUEST_FORCE_RELEASE", "4": "LATCH_REQUEST_RESET"} | 稳定性=LOW_CARDINALITY；变化次数=0；序列=LATCH_REQUEST_NONE | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-30E936829754 | KNOWN | 0x1F9 | VCSEC_requests / VCSEC_chargePortRequest | VCSEC_requests / VCSEC_chargePortRequest / enum={"0": "NONE", "1": "OPEN", "2": "CLOSE", "3": "SNA"} | 稳定性=LOW_CARDINALITY；变化次数=2；首次变化=268.6751 s（CAN Observed Time）；末次变化=268.9751 s（CAN Observed Time）；序列=NONE → OPEN → NONE | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| OBS-0005 | RESIDUAL | 0x108 | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=11311 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |
| OBS-0012 | UNKNOWN | 0x128 | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=9 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |

### C. 为什么进入输入（DBC REFERENCE METADATA — 仅供参考，不是 Evidence）

- `SO-BA9225550260`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": [], "domain_concepts": ["INTERFACE"], "domain_terms": ["lock", "port"], "planned_phase_refs": [], "role_terms": ["status"]}`。不据此确认 Semantic Role。
- `SO-57834B9DC181`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["INTERFACE"], "domain_terms": ["latch"], "planned_phase_refs": ["PP-PORT-OPEN"], "role_terms": ["state", "status"]}`。不据此确认 Semantic Role。
- `SO-7C154FF11732`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["INTERFACE"], "domain_terms": ["latch"], "planned_phase_refs": ["PP-PORT-OPEN"], "role_terms": ["state", "status"]}`。不据此确认 Semantic Role。
- `SO-AFC76E33264C`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["INTERFACE"], "domain_terms": ["latch"], "planned_phase_refs": ["PP-PORT-OPEN"], "role_terms": ["state", "status"]}`。不据此确认 Semantic Role。
- `SO-23B9FBB08D32`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": [], "domain_concepts": ["INTERFACE"], "domain_terms": ["latch"], "planned_phase_refs": [], "role_terms": ["request", "status"]}`。不据此确认 Semantic Role。
- `SO-30E936829754`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["INTERFACE"], "domain_terms": ["port"], "planned_phase_refs": ["PP-STOP"], "role_terms": ["request"]}`。不据此确认 Semantic Role。
- `OBS-0005`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": ["PP-STOP"], "role_terms": []}`。不据此确认 Semantic Role。
- `OBS-0012`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": ["PP-STOP"], "role_terms": []}`。不据此确认 Semantic Role。

### D. LLM 获得的 Structured Context

- `SO-BA9225550260` identity_hint：`{"bus_key": "ch1:0x339", "dbc_name_hint": "VCSEC_chargePortLockStatus", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "VCSEC_authentication", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-BA9225550260` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 1, "change_count": 0, "first_change_time_s": null, "last_change_time_s": null, "stability_class": "LOW_CARDINALITY", "tags": []}`
- `SO-BA9225550260` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-BA9225550260` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-BA9225550260` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-57834B9DC181` identity_hint：`{"bus_key": "ch1:0x25D", "dbc_name_hint": "CP_latch2ControlState", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_status", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-57834B9DC181` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 5, "change_count": 7, "first_change_time_s": 21.0173, "last_change_time_s": 277.2349, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-57834B9DC181` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-PORT-OPEN", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-57834B9DC181` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-57834B9DC181` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-7C154FF11732` identity_hint：`{"bus_key": "ch1:0x25D", "dbc_name_hint": "CP_latchControlState", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_status", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-7C154FF11732` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 4, "change_count": 10, "first_change_time_s": 21.0173, "last_change_time_s": 277.1347, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-7C154FF11732` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-PORT-OPEN", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-7C154FF11732` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-7C154FF11732` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-AFC76E33264C` identity_hint：`{"bus_key": "ch1:0x25D", "dbc_name_hint": "CP_latchState", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_status", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-AFC76E33264C` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 2, "first_change_time_s": 20.7178, "last_change_time_s": 278.635, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-AFC76E33264C` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-PORT-OPEN", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-AFC76E33264C` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-AFC76E33264C` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-23B9FBB08D32` identity_hint：`{"bus_key": "ch1:0x142", "dbc_name_hint": "VCLEFT_liftgateLatchRequest", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "VCLEFT_liftgateStatus", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-23B9FBB08D32` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 1, "change_count": 0, "first_change_time_s": null, "last_change_time_s": null, "stability_class": "LOW_CARDINALITY", "tags": []}`
- `SO-23B9FBB08D32` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-23B9FBB08D32` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-23B9FBB08D32` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-30E936829754` identity_hint：`{"bus_key": "ch1:0x1F9", "dbc_name_hint": "VCSEC_chargePortRequest", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "VCSEC_requests", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-30E936829754` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 2, "first_change_time_s": 268.6751, "last_change_time_s": 268.9751, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-30E936829754` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-30E936829754` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-30E936829754` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0005` identity_hint：`{"bus_key": "ch1:0x108", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0005` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 133, "change_count": 11311, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "UNNAMED_ACTIVITY"]}`
- `OBS-0005` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0005` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0005` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0012` identity_hint：`{"bus_key": "ch1:0x128", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0012` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 5, "change_count": 9, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "LOW_CARDINALITY", "UNNAMED_ACTIVITY"]}`
- `OBS-0012` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0012` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0012` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`

### E. 精确输入追溯

- Question：`/semantic_evidence_questions/1`
- Per-question evidence：`/per_question_evidence/1`
- Intent：`/semantic_search_intents/1` (`SSI-ER-02`)
- Retrieval result：`/retrieval_results/1`
- Observation objects：`/observations/0` → `SO-BA9225550260`, `/observations/1` → `SO-57834B9DC181`, `/observations/2` → `SO-7C154FF11732`, `/observations/3` → `SO-AFC76E33264C`, `/observations/8` → `SO-23B9FBB08D32`, `/observations/9` → `SO-30E936829754`, `/observations/7` → `OBS-0005`, `/observations/10` → `OBS-0012`
- Observation contexts：`/observation_contexts/51` → `SO-BA9225550260`, `/observation_contexts/15` → `SO-57834B9DC181`, `/observation_contexts/16` → `SO-7C154FF11732`, `/observation_contexts/17` → `SO-AFC76E33264C`, `/observation_contexts/50` → `SO-23B9FBB08D32`, `/observation_contexts/52` → `SO-30E936829754`, `/observation_contexts/54` → `OBS-0005`, `/observation_contexts/56` → `OBS-0012`

## ER-03 — Distinguish A+ and A- contact, auxiliary supply establishment, actual controller wake, and charge-ready state

### A. 语义目标

- ER：`ER-03`
- Control Tree Reference：`CT-DCFC-01, CT-DCFC-02, CT-DCFC-04, CT-DCFC-06, CT-DCFC-07, CT-DCFC-08, CT-DCFC-09, CT-DCFC-10, CT-DCFC-11, CT-DCFC-12, CT-DCFC-13, CT-DCFC-14, CT-DCFC-15`
- Semantic Evidence Question：Distinguish A+ and A- contact, auxiliary supply establishment, actual controller wake, and charge-ready state.
- Sufficiency / Semantic Boundary：Downstream activity alone does not prove each upstream condition.
- Candidate Role（未确认）：`STATE`
- Forbidden Substitution：`ACTUAL, CAPABILITY, PERMISSION, REQUEST`
- Collection Script / Planned Procedure Context：`PP-CONNECT`（connect charging interface and record recognition and locking when independently observed；40–60 s；PLANNED_TIME）; `PP-AUTH-START`（perform authorization and request charging start; actual timing may vary；60–120 s；PLANNED_TIME）
- 时间边界：`PLANNED_TIME_IS_NOT_OBSERVED_EVENT_TIME`

### B. 实际送入 LLM 的 Observation

| Observation | Space | CAN ID / Bus | Message / Signal | DBC 参考 | ASC 实际行为 | Retrieval Provenance |
|---|---|---|---|---|---|---|
| SO-3DDFDF668229 | KNOWN | 0x221 | VCFRONT_LVPowerState / VCFRONT_tunerLVRequest | VCFRONT_LVPowerState / VCFRONT_tunerLVRequest / enum={"0": "OFF", "1": "ON", "2": "GOING_DOWN", "3": "FAULT"} | 稳定性=LOW_CARDINALITY；变化次数=1；首次变化=97.7415 s（CAN Observed Time）；末次变化=97.7415 s（CAN Observed Time）；序列=GOING_DOWN → OFF | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-1DA23ED17AA5 | KNOWN | 0x2B4 | PCS_dcdcBusStatus / PCS_dcdcLvBusVolt | PCS_dcdcBusStatus / PCS_dcdcLvBusVolt / unit=V | 稳定性=DYNAMIC；变化次数=2313；最小值=8.2421875；最大值=13.0859375；首次变化=0.131 s（CAN Observed Time）；末次变化=299.6131 s（CAN Observed Time）；序列=10.7421875 → 10.78125 → 10.7421875 → 10.703125 → 10.6640625 → 10.7421875 → 10.78125 → 10.5859375 … | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-DC02A406ACBE | KNOWN | 0x221 | VCFRONT_LVPowerState / VCFRONT_iBoosterLVState | VCFRONT_LVPowerState / VCFRONT_iBoosterLVState / enum={"0": "OFF", "1": "ON", "2": "GOING_DOWN", "3": "FAULT"} | 稳定性=LOW_CARDINALITY；变化次数=1；首次变化=90.6408 s（CAN Observed Time）；末次变化=90.6408 s（CAN Observed Time）；序列=GOING_DOWN → OFF | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-61297290B6D1 | KNOWN | 0x2B4 | PCS_dcdcBusStatus / PCS_dcdcLvOutputCurrent | PCS_dcdcBusStatus / PCS_dcdcLvOutputCurrent / unit=A | 稳定性=DYNAMIC；变化次数=2545；最小值=0.0；最大值=385.40000000000003；首次变化=0.2306 s（CAN Observed Time）；末次变化=299.7131 s（CAN Observed Time）；序列=385.3 → 282.90000000000003 → 1.3 → 231.70000000000002 → 52.5 → 26.900000000000002 → 52.5 → 206.10000000000002 … | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-00672B1A0092 | KNOWN | 0x221 | VCFRONT_LVPowerState / VCFRONT_uiHiCurrentLVState | VCFRONT_LVPowerState / VCFRONT_uiHiCurrentLVState / enum={"0": "OFF", "1": "ON", "2": "GOING_DOWN", "3": "FAULT"} | 稳定性=LOW_CARDINALITY；变化次数=0；序列=ON | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-02D3DB13AB41 | KNOWN | 0x221 | VCFRONT_LVPowerState / VCFRONT_LVPowerStateChecksum | VCFRONT_LVPowerState / VCFRONT_LVPowerStateChecksum | 稳定性=DYNAMIC；变化次数=5993；最小值=2.0；最大值=254.0；首次变化=0.0852 s（CAN Observed Time）；末次变化=299.7038 s（CAN Observed Time）；序列=79 → 158 → 111 → 190 → 143 → 222 → 175 → 254 … | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| OBS-0086 | UNKNOWN | 0x2A3 | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=491 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |
| OBS-0005 | RESIDUAL | 0x108 | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=11311 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |

### C. 为什么进入输入（DBC REFERENCE METADATA — 仅供参考，不是 Evidence）

- `SO-3DDFDF668229`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["AUX_WAKE"], "domain_terms": ["lv"], "planned_phase_refs": ["PP-AUTH-START"], "role_terms": ["state"]}`。不据此确认 Semantic Role。
- `SO-1DA23ED17AA5`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC"], "domain_concepts": ["AUX_WAKE", "ELECTRICAL"], "domain_terms": ["dc", "lv"], "planned_phase_refs": [], "role_terms": ["status"]}`。不据此确认 Semantic Role。
- `SO-DC02A406ACBE`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["AUX_WAKE"], "domain_terms": ["lv"], "planned_phase_refs": ["PP-AUTH-START"], "role_terms": ["state"]}`。不据此确认 Semantic Role。
- `SO-61297290B6D1`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC"], "domain_concepts": ["AUX_WAKE", "ELECTRICAL"], "domain_terms": ["current", "dc", "lv"], "planned_phase_refs": [], "role_terms": ["status"]}`。不据此确认 Semantic Role。
- `SO-00672B1A0092`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": [], "domain_concepts": ["AUX_WAKE", "ELECTRICAL"], "domain_terms": ["current", "lv"], "planned_phase_refs": [], "role_terms": ["state"]}`。不据此确认 Semantic Role。
- `SO-02D3DB13AB41`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC"], "domain_concepts": ["AUX_WAKE"], "domain_terms": ["lv"], "planned_phase_refs": [], "role_terms": ["state"]}`。不据此确认 Semantic Role。
- `OBS-0086`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": ["PP-AUTH-START"], "role_terms": []}`。不据此确认 Semantic Role。
- `OBS-0005`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": [], "role_terms": []}`。不据此确认 Semantic Role。

### D. LLM 获得的 Structured Context

- `SO-3DDFDF668229` identity_hint：`{"bus_key": "ch1:0x221", "dbc_name_hint": "VCFRONT_tunerLVRequest", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "VCFRONT_LVPowerState", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-3DDFDF668229` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 1, "first_change_time_s": 97.7415, "last_change_time_s": 97.7415, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-3DDFDF668229` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-AUTH-START", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-3DDFDF668229` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-3DDFDF668229` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-1DA23ED17AA5` identity_hint：`{"bus_key": "ch1:0x2B4", "dbc_name_hint": "PCS_dcdcLvBusVolt", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "PCS_dcdcBusStatus", "semantic_validation_state": "UNVALIDATED", "unit": "V"}`
- `SO-1DA23ED17AA5` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 93, "change_count": 2313, "first_change_time_s": 0.131, "last_change_time_s": 299.6131, "stability_class": "DYNAMIC", "tags": ["DYNAMIC"]}`
- `SO-1DA23ED17AA5` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-1DA23ED17AA5` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-1DA23ED17AA5` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-DC02A406ACBE` identity_hint：`{"bus_key": "ch1:0x221", "dbc_name_hint": "VCFRONT_iBoosterLVState", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "VCFRONT_LVPowerState", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-DC02A406ACBE` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 1, "first_change_time_s": 90.6408, "last_change_time_s": 90.6408, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-DC02A406ACBE` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-AUTH-START", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-DC02A406ACBE` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-DC02A406ACBE` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-61297290B6D1` identity_hint：`{"bus_key": "ch1:0x2B4", "dbc_name_hint": "PCS_dcdcLvOutputCurrent", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "PCS_dcdcBusStatus", "semantic_validation_state": "UNVALIDATED", "unit": "A"}`
- `SO-61297290B6D1` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 38, "change_count": 2545, "first_change_time_s": 0.2306, "last_change_time_s": 299.7131, "stability_class": "DYNAMIC", "tags": ["DYNAMIC"]}`
- `SO-61297290B6D1` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-61297290B6D1` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-61297290B6D1` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-00672B1A0092` identity_hint：`{"bus_key": "ch1:0x221", "dbc_name_hint": "VCFRONT_uiHiCurrentLVState", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "VCFRONT_LVPowerState", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-00672B1A0092` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 1, "change_count": 0, "first_change_time_s": null, "last_change_time_s": null, "stability_class": "LOW_CARDINALITY", "tags": []}`
- `SO-00672B1A0092` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-00672B1A0092` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-00672B1A0092` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-02D3DB13AB41` identity_hint：`{"bus_key": "ch1:0x221", "dbc_name_hint": "VCFRONT_LVPowerStateChecksum", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "VCFRONT_LVPowerState", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-02D3DB13AB41` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 50, "change_count": 5993, "first_change_time_s": 0.0852, "last_change_time_s": 299.7038, "stability_class": "DYNAMIC", "tags": ["DYNAMIC"]}`
- `SO-02D3DB13AB41` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-02D3DB13AB41` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-02D3DB13AB41` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0086` identity_hint：`{"bus_key": "ch1:0x2A3", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0086` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 179, "change_count": 491, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "UNNAMED_ACTIVITY"]}`
- `OBS-0086` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-AUTH-START", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0086` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0086` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0005` identity_hint：`{"bus_key": "ch1:0x108", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0005` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 133, "change_count": 11311, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "UNNAMED_ACTIVITY"]}`
- `OBS-0005` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0005` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0005` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`

### E. 精确输入追溯

- Question：`/semantic_evidence_questions/2`
- Per-question evidence：`/per_question_evidence/2`
- Intent：`/semantic_search_intents/2` (`SSI-ER-03`)
- Retrieval result：`/retrieval_results/2`
- Observation objects：`/observations/11` → `SO-3DDFDF668229`, `/observations/12` → `SO-1DA23ED17AA5`, `/observations/13` → `SO-DC02A406ACBE`, `/observations/14` → `SO-61297290B6D1`, `/observations/15` → `SO-00672B1A0092`, `/observations/16` → `SO-02D3DB13AB41`, `/observations/17` → `OBS-0086`, `/observations/7` → `OBS-0005`
- Observation contexts：`/observation_contexts/46` → `SO-3DDFDF668229`, `/observation_contexts/33` → `SO-1DA23ED17AA5`, `/observation_contexts/42` → `SO-DC02A406ACBE`, `/observation_contexts/34` → `SO-61297290B6D1`, `/observation_contexts/47` → `SO-00672B1A0092`, `/observation_contexts/40` → `SO-02D3DB13AB41`, `/observation_contexts/59` → `OBS-0086`, `/observation_contexts/54` → `OBS-0005`

## ER-04 — Identify communication link, handshake or initialization, version compatibility, and parameter exchange where observable

### A. 语义目标

- ER：`ER-04`
- Control Tree Reference：`CT-DCFC-05, CT-DCFC-06, CT-DCFC-10, CT-DCFC-14, CT-DCFC-15`
- Semantic Evidence Question：Identify communication link, handshake or initialization, version compatibility, and parameter exchange where observable.
- Sufficiency / Semantic Boundary：Generic protocol stages do not prove a fixed internal ECU sequence or unobserved protocol messages.
- Candidate Role（未确认）：`TIMING_ONLY`
- Forbidden Substitution：`ACTUAL, CAPABILITY, PERMISSION, REQUEST`
- Collection Script / Planned Procedure Context：`PP-AUTH-START`（perform authorization and request charging start; actual timing may vary；60–120 s；PLANNED_TIME）
- 时间边界：`PLANNED_TIME_IS_NOT_OBSERVED_EVENT_TIME`

### B. 实际送入 LLM 的 Observation

| Observation | Space | CAN ID / Bus | Message / Signal | DBC 参考 | ASC 实际行为 | Retrieval Provenance |
|---|---|---|---|---|---|---|
| SO-0E3BF055E63D | KNOWN | 0x38D | TAS_warningMatrix3 / TAS_w164_calibrationVersion | TAS_warningMatrix3 / TAS_w164_calibrationVersion | 稳定性=LOW_CARDINALITY；变化次数=2；最小值=0.0；最大值=1.0；首次变化=173.1074 s（CAN Observed Time）；末次变化=194.1071 s（CAN Observed Time）；序列=1 → 0 → 1 | DIRECT_INTENT_RETRIEVAL; BEHAVIOR_EXPLORATORY |
| OBS-0086 | UNKNOWN | 0x2A3 | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=491 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |
| SO-11F964A63B77 | KNOWN | 0x2C1 | VCFRONT_logging10Hz / VCFRONT_compStandbyCommunication | VCFRONT_logging10Hz / VCFRONT_compStandbyCommunication | 稳定性=LOW_CARDINALITY；变化次数=8；最小值=0.0；最大值=1.0；首次变化=11.3499 s（CAN Observed Time）；末次变化=20.7507 s（CAN Observed Time）；序列=1 → 0 → 1 → 0 → 1 → 0 → 1 → 0 … | DIRECT_INTENT_RETRIEVAL; BEHAVIOR_EXPLORATORY |
| OBS-0005 | RESIDUAL | 0x108 | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=11311 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |

### C. 为什么进入输入（DBC REFERENCE METADATA — 仅供参考，不是 Evidence）

- `SO-0E3BF055E63D`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`BEHAVIOR_EXPLORATORY`；retrieval_reasons=`BEHAVIOR_EXPLORATORY`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["COMMUNICATION"], "domain_terms": ["version"], "planned_phase_refs": [], "role_terms": []}`。不据此确认 Semantic Role。
- `OBS-0086`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": ["PP-AUTH-START"], "role_terms": []}`。不据此确认 Semantic Role。
- `SO-11F964A63B77`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`BEHAVIOR_EXPLORATORY`；retrieval_reasons=`BEHAVIOR_EXPLORATORY`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["COMMUNICATION"], "domain_terms": ["communication"], "planned_phase_refs": [], "role_terms": []}`。不据此确认 Semantic Role。
- `OBS-0005`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": [], "role_terms": []}`。不据此确认 Semantic Role。

### D. LLM 获得的 Structured Context

- `SO-0E3BF055E63D` identity_hint：`{"bus_key": "ch1:0x38D", "dbc_name_hint": "TAS_w164_calibrationVersion", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "TAS_warningMatrix3", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-0E3BF055E63D` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 2, "first_change_time_s": 173.1074, "last_change_time_s": 194.1071, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-0E3BF055E63D` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-CHARGE-OBSERVE", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-0E3BF055E63D` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-0E3BF055E63D` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0086` identity_hint：`{"bus_key": "ch1:0x2A3", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0086` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 179, "change_count": 491, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "UNNAMED_ACTIVITY"]}`
- `OBS-0086` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-AUTH-START", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0086` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0086` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-11F964A63B77` identity_hint：`{"bus_key": "ch1:0x2C1", "dbc_name_hint": "VCFRONT_compStandbyCommunication", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "VCFRONT_logging10Hz", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-11F964A63B77` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 8, "first_change_time_s": 11.3499, "last_change_time_s": 20.7507, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-11F964A63B77` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-PORT-OPEN", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-11F964A63B77` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-11F964A63B77` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0005` identity_hint：`{"bus_key": "ch1:0x108", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0005` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 133, "change_count": 11311, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "UNNAMED_ACTIVITY"]}`
- `OBS-0005` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0005` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0005` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`

### E. 精确输入追溯

- Question：`/semantic_evidence_questions/3`
- Per-question evidence：`/per_question_evidence/3`
- Intent：`/semantic_search_intents/3` (`SSI-ER-04`)
- Retrieval result：`/retrieval_results/3`
- Observation objects：`/observations/18` → `SO-0E3BF055E63D`, `/observations/17` → `OBS-0086`, `/observations/19` → `SO-11F964A63B77`, `/observations/7` → `OBS-0005`
- Observation contexts：`/observation_contexts/36` → `SO-0E3BF055E63D`, `/observation_contexts/59` → `OBS-0086`, `/observation_contexts/41` → `SO-11F964A63B77`, `/observation_contexts/54` → `OBS-0005`

## ER-05 — Identify EVSE Capability without substituting Vehicle Capability, Vehicle Request, or Actual

### A. 语义目标

- ER：`ER-05`
- Control Tree Reference：`CT-DCFC-01, CT-DCFC-02, CT-DCFC-04, CT-DCFC-06, CT-DCFC-07, CT-DCFC-08, CT-DCFC-09, CT-DCFC-10, CT-DCFC-11, CT-DCFC-12, CT-DCFC-13, CT-DCFC-14, CT-DCFC-15`
- Semantic Evidence Question：Identify EVSE Capability without substituting Vehicle Capability, Vehicle Request, or Actual.
- Sufficiency / Semantic Boundary：Capability requires validated boundary variables or explicit insufficient evidence.
- Candidate Role（未确认）：`CAPABILITY`
- Forbidden Substitution：`ACTUAL, PERMISSION, REQUEST`
- Collection Script / Planned Procedure Context：`PP-CHARGE-OBSERVE`（observe EVSE and Pack voltage current power capability state and thermal context；150–210 s；PLANNED_TIME）; `PP-STEADY-HOLD`（observe a conditional short stable interval if naturally available；210–240 s；PLANNED_TIME）
- 时间边界：`PLANNED_TIME_IS_NOT_OBSERVED_EVENT_TIME`

### B. 实际送入 LLM 的 Observation

| Observation | Space | CAN ID / Bus | Message / Signal | DBC 参考 | ASC 实际行为 | Retrieval Provenance |
|---|---|---|---|---|---|---|
| SO-C817FE195629 | KNOWN | 0x21D | CP_evseStatus / CP_cableCurrentLimit | CP_evseStatus / CP_cableCurrentLimit / unit=A | 稳定性=CONSTANT；变化次数=0；最小值=0.0；最大值=0.0；序列=0 | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-993932E10707 | KNOWN | 0x1D6 | DI_limits / DI_limithvDcCableTemp | DI_limits / DI_limithvDcCableTemp | 稳定性=CONSTANT；变化次数=0；最小值=0.0；最大值=0.0；序列=0 | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-30140211597F | KNOWN | 0x29D | CP_dcChargeStatus / CP_evseOutputDcVoltage | CP_dcChargeStatus / CP_evseOutputDcVoltage / unit=V | 稳定性=DYNAMIC；变化次数=22；最小值=0.0；最大值=365.47857799999997；首次变化=140.0275 s（CAN Observed Time）；末次变化=246.2332 s（CAN Observed Time）；序列=0.0 → 346.87505919999995 → 347.31451239999996 → 349.29205179999997 → 352.3682242 → 355.5176388 → 358.37408459999995 → 361.08404599999994 … | DIRECT_INTENT_RETRIEVAL; PROCEDURE_ALIGNED_DOMAIN_HINT |
| SO-CE0335F98FD8 | KNOWN | 0x29D | CP_dcChargeStatus / CP_evseOutputDcCurrent | CP_dcChargeStatus / CP_evseOutputDcCurrent / unit=A | 稳定性=DYNAMIC；变化次数=12；最小值=0.0；最大值=133.0892539；首次变化=145.0277 s（CAN Observed Time）；末次变化=246.2332 s（CAN Observed Time）；序列=0.0 → 31.9355612 → 55.8872321 → 79.2529294 → 99.2492785 → 117.4144601 → 133.0892539 → 129.1339321 … | DIRECT_INTENT_RETRIEVAL; PROCEDURE_ALIGNED_DOMAIN_HINT |
| SO-2CA4B2E7EDED | KNOWN | 0x29D | CP_dcChargeStatus / CP_evseOutputDcCurrentStale | CP_dcChargeStatus / CP_evseOutputDcCurrentStale | 稳定性=LOW_CARDINALITY；变化次数=4；最小值=0.0；最大值=1.0；首次变化=39.7208 s（CAN Observed Time）；末次变化=273.5351 s（CAN Observed Time）；序列=1 → 0 → 1 → 0 → 1 | DIRECT_INTENT_RETRIEVAL; PROCEDURE_ALIGNED_DOMAIN_HINT |
| SO-FEC38397A149 | KNOWN | 0x3F2 | BMS_kwhCountersMultiplexed / BMS_dcChargerKwhTotal | BMS_kwhCountersMultiplexed / BMS_dcChargerKwhTotal / unit=KWh | 稳定性=NEAR_CONSTANT；变化次数=9；最小值=3769.587；最大值=3771.523；首次变化=151.8501 s（CAN Observed Time）；末次变化=247.852 s（CAN Observed Time）；序列=3769.587 → 3769.667 → 3769.907 → 3770.154 → 3770.3940000000002 → 3770.631 → 3770.864 → 3771.098 … | DIRECT_INTENT_RETRIEVAL; PROCEDURE_ALIGNED_DOMAIN_HINT |
| OBS-0060 | RESIDUAL | 0x25B | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=5558 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |
| OBS-0047 | UNKNOWN | 0x22B | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=1075 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |

### C. 为什么进入输入（DBC REFERENCE METADATA — 仅供参考，不是 Evidence）

- `SO-C817FE195629`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": [], "domain_concepts": ["ELECTRICAL", "EVSE_BOUNDARY"], "domain_terms": ["cable", "current", "evse"], "planned_phase_refs": [], "role_terms": ["limit"]}`。不据此确认 Semantic Role。
- `SO-993932E10707`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": [], "domain_concepts": ["ELECTRICAL", "EVSE_BOUNDARY"], "domain_terms": ["cable", "dc"], "planned_phase_refs": [], "role_terms": ["limit"]}`。不据此确认 Semantic Role。
- `SO-30140211597F`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`PROCEDURE_ALIGNED_DOMAIN_HINT`；retrieval_reasons=`PROCEDURE_ALIGNED_DOMAIN_HINT`；context_matches=`{"behavior_tags": ["DYNAMIC"], "domain_concepts": ["ELECTRICAL", "EVSE_BOUNDARY"], "domain_terms": ["charge", "dc", "evse", "voltage"], "planned_phase_refs": [], "role_terms": []}`。不据此确认 Semantic Role。
- `SO-CE0335F98FD8`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`PROCEDURE_ALIGNED_DOMAIN_HINT`；retrieval_reasons=`PROCEDURE_ALIGNED_DOMAIN_HINT`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["ELECTRICAL", "EVSE_BOUNDARY"], "domain_terms": ["charge", "current", "dc", "evse"], "planned_phase_refs": [], "role_terms": []}`。不据此确认 Semantic Role。
- `SO-2CA4B2E7EDED`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`PROCEDURE_ALIGNED_DOMAIN_HINT`；retrieval_reasons=`PROCEDURE_ALIGNED_DOMAIN_HINT`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["ELECTRICAL", "EVSE_BOUNDARY"], "domain_terms": ["charge", "current", "dc", "evse"], "planned_phase_refs": [], "role_terms": []}`。不据此确认 Semantic Role。
- `SO-FEC38397A149`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`PROCEDURE_ALIGNED_DOMAIN_HINT`；retrieval_reasons=`PROCEDURE_ALIGNED_DOMAIN_HINT`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["ELECTRICAL", "EVSE_BOUNDARY"], "domain_terms": ["charge", "charger", "dc"], "planned_phase_refs": ["PP-CHARGE-OBSERVE"], "role_terms": []}`。不据此确认 Semantic Role。
- `OBS-0060`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": ["PP-STEADY-HOLD"], "role_terms": []}`。不据此确认 Semantic Role。
- `OBS-0047`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": ["PP-STEADY-HOLD"], "role_terms": []}`。不据此确认 Semantic Role。

### D. LLM 获得的 Structured Context

- `SO-C817FE195629` identity_hint：`{"bus_key": "ch1:0x21D", "dbc_name_hint": "CP_cableCurrentLimit", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_evseStatus", "semantic_validation_state": "UNVALIDATED", "unit": "A"}`
- `SO-C817FE195629` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 1, "change_count": 0, "first_change_time_s": null, "last_change_time_s": null, "stability_class": "CONSTANT", "tags": []}`
- `SO-C817FE195629` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-C817FE195629` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-C817FE195629` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-993932E10707` identity_hint：`{"bus_key": "ch1:0x1D6", "dbc_name_hint": "DI_limithvDcCableTemp", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "DI_limits", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-993932E10707` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 1, "change_count": 0, "first_change_time_s": null, "last_change_time_s": null, "stability_class": "CONSTANT", "tags": []}`
- `SO-993932E10707` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-993932E10707` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-993932E10707` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-30140211597F` identity_hint：`{"bus_key": "ch1:0x29D", "dbc_name_hint": "CP_evseOutputDcVoltage", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_dcChargeStatus", "semantic_validation_state": "UNVALIDATED", "unit": "V"}`
- `SO-30140211597F` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 19, "change_count": 22, "first_change_time_s": 140.0275, "last_change_time_s": 246.2332, "stability_class": "DYNAMIC", "tags": ["DYNAMIC"]}`
- `SO-30140211597F` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-30140211597F` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-30140211597F` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-CE0335F98FD8` identity_hint：`{"bus_key": "ch1:0x29D", "dbc_name_hint": "CP_evseOutputDcCurrent", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_dcChargeStatus", "semantic_validation_state": "UNVALIDATED", "unit": "A"}`
- `SO-CE0335F98FD8` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 11, "change_count": 12, "first_change_time_s": 145.0277, "last_change_time_s": 246.2332, "stability_class": "DYNAMIC", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-CE0335F98FD8` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-CE0335F98FD8` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-CE0335F98FD8` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-2CA4B2E7EDED` identity_hint：`{"bus_key": "ch1:0x29D", "dbc_name_hint": "CP_evseOutputDcCurrentStale", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_dcChargeStatus", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-2CA4B2E7EDED` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 4, "first_change_time_s": 39.7208, "last_change_time_s": 273.5351, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-2CA4B2E7EDED` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-PORT-OPEN", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-2CA4B2E7EDED` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-2CA4B2E7EDED` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-FEC38397A149` identity_hint：`{"bus_key": "ch1:0x3F2", "dbc_name_hint": "BMS_dcChargerKwhTotal", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "BMS_kwhCountersMultiplexed", "semantic_validation_state": "UNVALIDATED", "unit": "KWh"}`
- `SO-FEC38397A149` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 10, "change_count": 9, "first_change_time_s": 151.8501, "last_change_time_s": 247.852, "stability_class": "NEAR_CONSTANT", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-FEC38397A149` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-CHARGE-OBSERVE", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-FEC38397A149` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-FEC38397A149` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0060` identity_hint：`{"bus_key": "ch1:0x25B", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0060` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 60, "change_count": 5558, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "UNNAMED_ACTIVITY"]}`
- `OBS-0060` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STEADY-HOLD", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0060` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0060` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0047` identity_hint：`{"bus_key": "ch1:0x22B", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0047` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": ">=256", "change_count": 1075, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "UNNAMED_ACTIVITY"]}`
- `OBS-0047` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STEADY-HOLD", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0047` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0047` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`

### E. 精确输入追溯

- Question：`/semantic_evidence_questions/4`
- Per-question evidence：`/per_question_evidence/4`
- Intent：`/semantic_search_intents/4` (`SSI-ER-05`)
- Retrieval result：`/retrieval_results/4`
- Observation objects：`/observations/20` → `SO-C817FE195629`, `/observations/21` → `SO-993932E10707`, `/observations/22` → `SO-30140211597F`, `/observations/23` → `SO-CE0335F98FD8`, `/observations/24` → `SO-2CA4B2E7EDED`, `/observations/25` → `SO-FEC38397A149`, `/observations/26` → `OBS-0060`, `/observations/27` → `OBS-0047`
- Observation contexts：`/observation_contexts/11` → `SO-C817FE195629`, `/observation_contexts/22` → `SO-993932E10707`, `/observation_contexts/14` → `SO-30140211597F`, `/observation_contexts/12` → `SO-CE0335F98FD8`, `/observation_contexts/13` → `SO-2CA4B2E7EDED`, `/observation_contexts/2` → `SO-FEC38397A149`, `/observation_contexts/58` → `OBS-0060`, `/observation_contexts/57` → `OBS-0047`

## ER-06 — Identify Vehicle Capability without substituting EVSE Capability, Vehicle Request, or Actual

### A. 语义目标

- ER：`ER-06`
- Control Tree Reference：`CT-DCFC-01, CT-DCFC-02, CT-DCFC-04, CT-DCFC-05, CT-DCFC-06, CT-DCFC-07, CT-DCFC-08, CT-DCFC-09, CT-DCFC-10, CT-DCFC-11, CT-DCFC-12, CT-DCFC-13, CT-DCFC-14, CT-DCFC-15`
- Semantic Evidence Question：Identify Vehicle Capability without substituting EVSE Capability, Vehicle Request, or Actual.
- Sufficiency / Semantic Boundary：Vehicle allowed voltage/current/power require validated vehicle-boundary evidence.
- Candidate Role（未确认）：`CAPABILITY`
- Forbidden Substitution：`ACTUAL, PERMISSION, REQUEST`
- Collection Script / Planned Procedure Context：`PP-CHARGE-OBSERVE`（observe EVSE and Pack voltage current power capability state and thermal context；150–210 s；PLANNED_TIME）; `PP-STEADY-HOLD`（observe a conditional short stable interval if naturally available；210–240 s；PLANNED_TIME）
- 时间边界：`PLANNED_TIME_IS_NOT_OBSERVED_EVENT_TIME`

### B. 实际送入 LLM 的 Observation

| Observation | Space | CAN ID / Bus | Message / Signal | DBC 参考 | ASC 实际行为 | Retrieval Provenance |
|---|---|---|---|---|---|---|
| SO-EE1762E29E91 | KNOWN | 0x2D2 | BMS_driveLimits / BMS_maxChargeCurrent | BMS_driveLimits / BMS_maxChargeCurrent / unit=A | 稳定性=LOW_CARDINALITY；变化次数=4；最小值=0.0；最大值=250.0；首次变化=115.392 s（CAN Observed Time）；末次变化=246.3935 s（CAN Observed Time）；序列=0.0 → 250.0 → 0.0 → 250.0 → 0.0 | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-2F68BA1F43E7 | KNOWN | 0x2D2 | BMS_driveLimits / BMS_maxBusVoltage | BMS_driveLimits / BMS_maxBusVoltage / unit=V | 稳定性=LOW_CARDINALITY；变化次数=14；最小值=200.67000000000002；最大值=201.4；首次变化=124.9943 s（CAN Observed Time）；末次变化=246.0925 s（CAN Observed Time）；序列=201.15 → 201.14000000000001 → 201.15 → 201.14000000000001 → 201.15 → 201.14000000000001 → 201.15 → 201.14000000000001 … | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-57FDBA89A626 | KNOWN | 0x2D2 | BMS_driveLimits / BMS_maxDischargeCurrent | BMS_driveLimits / BMS_maxDischargeCurrent / unit=A | 稳定性=LOW_CARDINALITY；变化次数=4；最小值=0.0；最大值=53.376；首次变化=115.392 s（CAN Observed Time）；末次变化=246.3935 s（CAN Observed Time）；序列=53.376 → 46.976 → 0.0 → 46.976 → 53.376 | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-D2B7392F2DD6 | KNOWN | 0x2D2 | BMS_driveLimits / BMS_minBusVoltage | BMS_driveLimits / BMS_minBusVoltage / unit=V | 稳定性=DYNAMIC；变化次数=599；最小值=106.11；最大值=106.75；首次变化=18.5903 s（CAN Observed Time）；末次变化=298.8995 s（CAN Observed Time）；序列=106.36 → 106.37 → 106.36 → 106.37 → 106.36 → 106.37 → 106.36 → 106.37 … | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-FCA6D6091527 | KNOWN | 0x212 | BMS_status / BMS_chgPowerAvailable | BMS_status / BMS_chgPowerAvailable / unit=kW / enum={"2047": "BMS_chgPowerAvailable_SNA"} | 稳定性=DYNAMIC；变化次数=189；最小值=21.5；最大值=255.75；首次变化=140.0893 s（CAN Observed Time）；末次变化=245.7928 s（CAN Observed Time）；序列=255.75 → 22.0 → 21.75 → 22.0 → 21.75 → 22.0 → 21.75 → 22.0 … | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-30140211597F | KNOWN | 0x29D | CP_dcChargeStatus / CP_evseOutputDcVoltage | CP_dcChargeStatus / CP_evseOutputDcVoltage / unit=V | 稳定性=DYNAMIC；变化次数=22；最小值=0.0；最大值=365.47857799999997；首次变化=140.0275 s（CAN Observed Time）；末次变化=246.2332 s（CAN Observed Time）；序列=0.0 → 346.87505919999995 → 347.31451239999996 → 349.29205179999997 → 352.3682242 → 355.5176388 → 358.37408459999995 → 361.08404599999994 … | DIRECT_INTENT_RETRIEVAL; PROCEDURE_ALIGNED_DOMAIN_HINT |
| OBS-0060 | RESIDUAL | 0x25B | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=5558 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |
| OBS-0047 | UNKNOWN | 0x22B | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=1075 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |

### C. 为什么进入输入（DBC REFERENCE METADATA — 仅供参考，不是 Evidence）

- `SO-EE1762E29E91`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["ELECTRICAL", "VEHICLE_BOUNDARY"], "domain_terms": ["bms", "charge", "current"], "planned_phase_refs": [], "role_terms": ["limit"]}`。不据此确认 Semantic Role。
- `SO-2F68BA1F43E7`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["ELECTRICAL", "VEHICLE_BOUNDARY"], "domain_terms": ["bms", "voltage"], "planned_phase_refs": [], "role_terms": ["limit"]}`。不据此确认 Semantic Role。
- `SO-57FDBA89A626`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["ELECTRICAL", "VEHICLE_BOUNDARY"], "domain_terms": ["bms", "current"], "planned_phase_refs": [], "role_terms": ["limit"]}`。不据此确认 Semantic Role。
- `SO-D2B7392F2DD6`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC"], "domain_concepts": ["ELECTRICAL", "VEHICLE_BOUNDARY"], "domain_terms": ["bms", "voltage"], "planned_phase_refs": [], "role_terms": ["limit"]}`。不据此确认 Semantic Role。
- `SO-FCA6D6091527`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC"], "domain_concepts": ["ELECTRICAL", "VEHICLE_BOUNDARY"], "domain_terms": ["bms", "power"], "planned_phase_refs": [], "role_terms": ["available"]}`。不据此确认 Semantic Role。
- `SO-30140211597F`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`PROCEDURE_ALIGNED_DOMAIN_HINT`；retrieval_reasons=`PROCEDURE_ALIGNED_DOMAIN_HINT`；context_matches=`{"behavior_tags": ["DYNAMIC"], "domain_concepts": ["ELECTRICAL"], "domain_terms": ["charge", "dc", "evse", "voltage"], "planned_phase_refs": [], "role_terms": []}`。不据此确认 Semantic Role。
- `OBS-0060`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": ["PP-STEADY-HOLD"], "role_terms": []}`。不据此确认 Semantic Role。
- `OBS-0047`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": ["PP-STEADY-HOLD"], "role_terms": []}`。不据此确认 Semantic Role。

### D. LLM 获得的 Structured Context

- `SO-EE1762E29E91` identity_hint：`{"bus_key": "ch1:0x2D2", "dbc_name_hint": "BMS_maxChargeCurrent", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "BMS_driveLimits", "semantic_validation_state": "UNVALIDATED", "unit": "A"}`
- `SO-EE1762E29E91` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 4, "first_change_time_s": 115.392, "last_change_time_s": 246.3935, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-EE1762E29E91` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-AUTH-START", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-EE1762E29E91` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-EE1762E29E91` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-2F68BA1F43E7` identity_hint：`{"bus_key": "ch1:0x2D2", "dbc_name_hint": "BMS_maxBusVoltage", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "BMS_driveLimits", "semantic_validation_state": "UNVALIDATED", "unit": "V"}`
- `SO-2F68BA1F43E7` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 7, "change_count": 14, "first_change_time_s": 124.9943, "last_change_time_s": 246.0925, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-2F68BA1F43E7` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-2F68BA1F43E7` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-2F68BA1F43E7` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-57FDBA89A626` identity_hint：`{"bus_key": "ch1:0x2D2", "dbc_name_hint": "BMS_maxDischargeCurrent", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "BMS_driveLimits", "semantic_validation_state": "UNVALIDATED", "unit": "A"}`
- `SO-57FDBA89A626` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 3, "change_count": 4, "first_change_time_s": 115.392, "last_change_time_s": 246.3935, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-57FDBA89A626` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-AUTH-START", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-57FDBA89A626` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-57FDBA89A626` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-D2B7392F2DD6` identity_hint：`{"bus_key": "ch1:0x2D2", "dbc_name_hint": "BMS_minBusVoltage", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "BMS_driveLimits", "semantic_validation_state": "UNVALIDATED", "unit": "V"}`
- `SO-D2B7392F2DD6` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 45, "change_count": 599, "first_change_time_s": 18.5903, "last_change_time_s": 298.8995, "stability_class": "DYNAMIC", "tags": ["DYNAMIC"]}`
- `SO-D2B7392F2DD6` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-D2B7392F2DD6` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-D2B7392F2DD6` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-FCA6D6091527` identity_hint：`{"bus_key": "ch1:0x212", "dbc_name_hint": "BMS_chgPowerAvailable", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "BMS_status", "semantic_validation_state": "UNVALIDATED", "unit": "kW"}`
- `SO-FCA6D6091527` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 54, "change_count": 189, "first_change_time_s": 140.0893, "last_change_time_s": 245.7928, "stability_class": "DYNAMIC", "tags": ["DYNAMIC"]}`
- `SO-FCA6D6091527` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-FCA6D6091527` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-FCA6D6091527` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-30140211597F` identity_hint：`{"bus_key": "ch1:0x29D", "dbc_name_hint": "CP_evseOutputDcVoltage", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_dcChargeStatus", "semantic_validation_state": "UNVALIDATED", "unit": "V"}`
- `SO-30140211597F` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 19, "change_count": 22, "first_change_time_s": 140.0275, "last_change_time_s": 246.2332, "stability_class": "DYNAMIC", "tags": ["DYNAMIC"]}`
- `SO-30140211597F` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-30140211597F` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-30140211597F` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0060` identity_hint：`{"bus_key": "ch1:0x25B", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0060` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 60, "change_count": 5558, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "UNNAMED_ACTIVITY"]}`
- `OBS-0060` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STEADY-HOLD", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0060` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0060` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0047` identity_hint：`{"bus_key": "ch1:0x22B", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0047` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": ">=256", "change_count": 1075, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "UNNAMED_ACTIVITY"]}`
- `OBS-0047` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STEADY-HOLD", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0047` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0047` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`

### E. 精确输入追溯

- Question：`/semantic_evidence_questions/5`
- Per-question evidence：`/per_question_evidence/5`
- Intent：`/semantic_search_intents/5` (`SSI-ER-06`)
- Retrieval result：`/retrieval_results/5`
- Observation objects：`/observations/28` → `SO-EE1762E29E91`, `/observations/29` → `SO-2F68BA1F43E7`, `/observations/30` → `SO-57FDBA89A626`, `/observations/31` → `SO-D2B7392F2DD6`, `/observations/32` → `SO-FCA6D6091527`, `/observations/22` → `SO-30140211597F`, `/observations/26` → `OBS-0060`, `/observations/27` → `OBS-0047`
- Observation contexts：`/observation_contexts/6` → `SO-EE1762E29E91`, `/observation_contexts/5` → `SO-2F68BA1F43E7`, `/observation_contexts/7` → `SO-57FDBA89A626`, `/observation_contexts/8` → `SO-D2B7392F2DD6`, `/observation_contexts/1` → `SO-FCA6D6091527`, `/observation_contexts/14` → `SO-30140211597F`, `/observation_contexts/58` → `OBS-0060`, `/observation_contexts/57` → `OBS-0047`

## ER-07 — Identify Vehicle Request voltage and current independently of Capability and Actual

### A. 语义目标

- ER：`ER-07`
- Control Tree Reference：`CT-DCFC-01, CT-DCFC-02, CT-DCFC-04, CT-DCFC-05, CT-DCFC-06, CT-DCFC-07, CT-DCFC-08, CT-DCFC-09, CT-DCFC-10, CT-DCFC-11, CT-DCFC-12, CT-DCFC-13, CT-DCFC-14, CT-DCFC-15`
- Semantic Evidence Question：Identify Vehicle Request voltage and current independently of Capability and Actual.
- Sufficiency / Semantic Boundary：Request power is derived from synchronized request voltage/current unless an independent request-power field is validated.
- Candidate Role（未确认）：`REQUEST`
- Forbidden Substitution：`ACTUAL, CAPABILITY, PERMISSION`
- Collection Script / Planned Procedure Context：`PP-CHARGE-OBSERVE`（observe EVSE and Pack voltage current power capability state and thermal context；150–210 s；PLANNED_TIME）; `PP-STEADY-HOLD`（observe a conditional short stable interval if naturally available；210–240 s；PLANNED_TIME）; `PP-STOP`（request one normal stop if charging has not already ended；240–270 s；PLANNED_TIME）
- 时间边界：`PLANNED_TIME_IS_NOT_OBSERVED_EVENT_TIME`

### B. 实际送入 LLM 的 Observation

| Observation | Space | CAN ID / Bus | Message / Signal | DBC 参考 | ASC 实际行为 | Retrieval Provenance |
|---|---|---|---|---|---|---|
| SO-C735BF77D6EA | KNOWN | 0x212 | BMS_status / BMS_chargeRequest | BMS_status / BMS_chargeRequest | 稳定性=CONSTANT；变化次数=0；最小值=0.0；最大值=0.0；序列=0 | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-E17A19938CC3 | KNOWN | 0x273 | UI_vehicleControl / UI_accessoryPowerRequest | UI_vehicleControl / UI_accessoryPowerRequest | 稳定性=CONSTANT；变化次数=0；最小值=0.0；最大值=0.0；序列=0 | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-30140211597F | KNOWN | 0x29D | CP_dcChargeStatus / CP_evseOutputDcVoltage | CP_dcChargeStatus / CP_evseOutputDcVoltage / unit=V | 稳定性=DYNAMIC；变化次数=22；最小值=0.0；最大值=365.47857799999997；首次变化=140.0275 s（CAN Observed Time）；末次变化=246.2332 s（CAN Observed Time）；序列=0.0 → 346.87505919999995 → 347.31451239999996 → 349.29205179999997 → 352.3682242 → 355.5176388 → 358.37408459999995 → 361.08404599999994 … | DIRECT_INTENT_RETRIEVAL; PROCEDURE_ALIGNED_DOMAIN_HINT |
| SO-CE0335F98FD8 | KNOWN | 0x29D | CP_dcChargeStatus / CP_evseOutputDcCurrent | CP_dcChargeStatus / CP_evseOutputDcCurrent / unit=A | 稳定性=DYNAMIC；变化次数=12；最小值=0.0；最大值=133.0892539；首次变化=145.0277 s（CAN Observed Time）；末次变化=246.2332 s（CAN Observed Time）；序列=0.0 → 31.9355612 → 55.8872321 → 79.2529294 → 99.2492785 → 117.4144601 → 133.0892539 → 129.1339321 … | DIRECT_INTENT_RETRIEVAL; PROCEDURE_ALIGNED_DOMAIN_HINT |
| SO-2CA4B2E7EDED | KNOWN | 0x29D | CP_dcChargeStatus / CP_evseOutputDcCurrentStale | CP_dcChargeStatus / CP_evseOutputDcCurrentStale | 稳定性=LOW_CARDINALITY；变化次数=4；最小值=0.0；最大值=1.0；首次变化=39.7208 s（CAN Observed Time）；末次变化=273.5351 s（CAN Observed Time）；序列=1 → 0 → 1 → 0 → 1 | DIRECT_INTENT_RETRIEVAL; PROCEDURE_ALIGNED_DOMAIN_HINT |
| SO-05B359B48253 | KNOWN | 0x132 | BMS_hvBusStatus / BMS_packCurrent | BMS_hvBusStatus / BMS_packCurrent / unit=A / enum={"-16384": "SNA"} | 稳定性=DYNAMIC；变化次数=17475；最小值=-219.60000000000002；最大值=27.8；首次变化=0.0421 s（CAN Observed Time）；末次变化=299.7285 s（CAN Observed Time）；序列=0.8 → 0.7000000000000001 → 0.8 → 0.7000000000000001 → 0.8 → 0.7000000000000001 → 0.8 → 0.7000000000000001 … | DIRECT_INTENT_RETRIEVAL; PHYSICAL_DIMENSION_BEHAVIOR |
| OBS-0005 | RESIDUAL | 0x108 | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=11311 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |
| OBS-0012 | UNKNOWN | 0x128 | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=9 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |

### C. 为什么进入输入（DBC REFERENCE METADATA — 仅供参考，不是 Evidence）

- `SO-C735BF77D6EA`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": [], "domain_concepts": ["ELECTRICAL", "VEHICLE_BOUNDARY"], "domain_terms": ["bms", "charge"], "planned_phase_refs": [], "role_terms": ["request"]}`。不据此确认 Semantic Role。
- `SO-E17A19938CC3`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": [], "domain_concepts": ["ELECTRICAL", "VEHICLE_BOUNDARY"], "domain_terms": ["power", "vehicle"], "planned_phase_refs": [], "role_terms": ["request"]}`。不据此确认 Semantic Role。
- `SO-30140211597F`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`PROCEDURE_ALIGNED_DOMAIN_HINT`；retrieval_reasons=`PROCEDURE_ALIGNED_DOMAIN_HINT`；context_matches=`{"behavior_tags": ["DYNAMIC"], "domain_concepts": ["ELECTRICAL"], "domain_terms": ["charge", "dc", "evse", "voltage"], "planned_phase_refs": ["PP-STOP"], "role_terms": []}`。不据此确认 Semantic Role。
- `SO-CE0335F98FD8`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`PROCEDURE_ALIGNED_DOMAIN_HINT`；retrieval_reasons=`PROCEDURE_ALIGNED_DOMAIN_HINT`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["ELECTRICAL"], "domain_terms": ["charge", "current", "dc", "evse"], "planned_phase_refs": ["PP-STOP"], "role_terms": []}`。不据此确认 Semantic Role。
- `SO-2CA4B2E7EDED`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`PROCEDURE_ALIGNED_DOMAIN_HINT`；retrieval_reasons=`PROCEDURE_ALIGNED_DOMAIN_HINT`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["ELECTRICAL"], "domain_terms": ["charge", "current", "dc", "evse"], "planned_phase_refs": [], "role_terms": []}`。不据此确认 Semantic Role。
- `SO-05B359B48253`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`PHYSICAL_DIMENSION_BEHAVIOR`；retrieval_reasons=`PHYSICAL_DIMENSION_BEHAVIOR`；context_matches=`{"behavior_tags": ["DYNAMIC"], "domain_concepts": ["ELECTRICAL", "VEHICLE_BOUNDARY"], "domain_terms": ["bms", "current", "pack"], "planned_phase_refs": [], "role_terms": []}`。不据此确认 Semantic Role。
- `OBS-0005`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": ["PP-STOP"], "role_terms": []}`。不据此确认 Semantic Role。
- `OBS-0012`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": ["PP-STOP"], "role_terms": []}`。不据此确认 Semantic Role。

### D. LLM 获得的 Structured Context

- `SO-C735BF77D6EA` identity_hint：`{"bus_key": "ch1:0x212", "dbc_name_hint": "BMS_chargeRequest", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "BMS_status", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-C735BF77D6EA` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 1, "change_count": 0, "first_change_time_s": null, "last_change_time_s": null, "stability_class": "CONSTANT", "tags": []}`
- `SO-C735BF77D6EA` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-C735BF77D6EA` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-C735BF77D6EA` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-E17A19938CC3` identity_hint：`{"bus_key": "ch1:0x273", "dbc_name_hint": "UI_accessoryPowerRequest", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "UI_vehicleControl", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-E17A19938CC3` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 1, "change_count": 0, "first_change_time_s": null, "last_change_time_s": null, "stability_class": "CONSTANT", "tags": []}`
- `SO-E17A19938CC3` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-E17A19938CC3` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-E17A19938CC3` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-30140211597F` identity_hint：`{"bus_key": "ch1:0x29D", "dbc_name_hint": "CP_evseOutputDcVoltage", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_dcChargeStatus", "semantic_validation_state": "UNVALIDATED", "unit": "V"}`
- `SO-30140211597F` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 19, "change_count": 22, "first_change_time_s": 140.0275, "last_change_time_s": 246.2332, "stability_class": "DYNAMIC", "tags": ["DYNAMIC"]}`
- `SO-30140211597F` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-30140211597F` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-30140211597F` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-CE0335F98FD8` identity_hint：`{"bus_key": "ch1:0x29D", "dbc_name_hint": "CP_evseOutputDcCurrent", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_dcChargeStatus", "semantic_validation_state": "UNVALIDATED", "unit": "A"}`
- `SO-CE0335F98FD8` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 11, "change_count": 12, "first_change_time_s": 145.0277, "last_change_time_s": 246.2332, "stability_class": "DYNAMIC", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-CE0335F98FD8` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-CE0335F98FD8` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-CE0335F98FD8` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-2CA4B2E7EDED` identity_hint：`{"bus_key": "ch1:0x29D", "dbc_name_hint": "CP_evseOutputDcCurrentStale", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_dcChargeStatus", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-2CA4B2E7EDED` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 4, "first_change_time_s": 39.7208, "last_change_time_s": 273.5351, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-2CA4B2E7EDED` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-PORT-OPEN", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-2CA4B2E7EDED` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-2CA4B2E7EDED` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-05B359B48253` identity_hint：`{"bus_key": "ch1:0x132", "dbc_name_hint": "BMS_packCurrent", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "BMS_hvBusStatus", "semantic_validation_state": "UNVALIDATED", "unit": "A"}`
- `SO-05B359B48253` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": ">=256", "change_count": 17475, "first_change_time_s": 0.0421, "last_change_time_s": 299.7285, "stability_class": "DYNAMIC", "tags": ["DYNAMIC"]}`
- `SO-05B359B48253` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-05B359B48253` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-05B359B48253` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0005` identity_hint：`{"bus_key": "ch1:0x108", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0005` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 133, "change_count": 11311, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "UNNAMED_ACTIVITY"]}`
- `OBS-0005` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0005` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0005` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0012` identity_hint：`{"bus_key": "ch1:0x128", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0012` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 5, "change_count": 9, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "LOW_CARDINALITY", "UNNAMED_ACTIVITY"]}`
- `OBS-0012` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0012` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0012` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`

### E. 精确输入追溯

- Question：`/semantic_evidence_questions/6`
- Per-question evidence：`/per_question_evidence/6`
- Intent：`/semantic_search_intents/6` (`SSI-ER-07`)
- Retrieval result：`/retrieval_results/6`
- Observation objects：`/observations/33` → `SO-C735BF77D6EA`, `/observations/34` → `SO-E17A19938CC3`, `/observations/22` → `SO-30140211597F`, `/observations/23` → `SO-CE0335F98FD8`, `/observations/24` → `SO-2CA4B2E7EDED`, `/observations/35` → `SO-05B359B48253`, `/observations/7` → `OBS-0005`, `/observations/10` → `OBS-0012`
- Observation contexts：`/observation_contexts/0` → `SO-C735BF77D6EA`, `/observation_contexts/38` → `SO-E17A19938CC3`, `/observation_contexts/14` → `SO-30140211597F`, `/observation_contexts/12` → `SO-CE0335F98FD8`, `/observation_contexts/13` → `SO-2CA4B2E7EDED`, `/observation_contexts/9` → `SO-05B359B48253`, `/observation_contexts/54` → `OBS-0005`, `/observation_contexts/56` → `OBS-0012`

## ER-08 — Identify Permission and Safety Gate separately from contactor state, high-voltage path, and energy transfer

### A. 语义目标

- ER：`ER-08`
- Control Tree Reference：`CT-DCFC-01, CT-DCFC-02, CT-DCFC-04, CT-DCFC-06, CT-DCFC-07, CT-DCFC-08, CT-DCFC-09, CT-DCFC-10, CT-DCFC-11, CT-DCFC-12, CT-DCFC-13, CT-DCFC-14, CT-DCFC-15`
- Semantic Evidence Question：Identify Permission and Safety Gate separately from contactor state, high-voltage path, and energy transfer.
- Sufficiency / Semantic Boundary：Actual or contactor observations cannot alone prove permission.
- Candidate Role（未确认）：`REQUEST, ACTUAL, STATE`
- Forbidden Substitution：`CAPABILITY, PERMISSION`
- Collection Script / Planned Procedure Context：`PP-ESTABLISH`（check whether charging actually established using independent vehicle and EVSE evidence；120–150 s；PLANNED_TIME）; `PP-CHARGE-OBSERVE`（observe EVSE and Pack voltage current power capability state and thermal context；150–210 s；PLANNED_TIME）; `PP-STEADY-HOLD`（observe a conditional short stable interval if naturally available；210–240 s；PLANNED_TIME）; `PP-STOP`（request one normal stop if charging has not already ended；240–270 s；PLANNED_TIME）; `PP-SAFE-EXIT`（confirm output stopped and lock released before disconnecting；270–300 s；PLANNED_TIME）
- 时间边界：`PLANNED_TIME_IS_NOT_OBSERVED_EVENT_TIME`

### B. 实际送入 LLM 的 Observation

| Observation | Space | CAN ID / Bus | Message / Signal | DBC 参考 | ASC 实际行为 | Retrieval Provenance |
|---|---|---|---|---|---|---|
| SO-19CE993899A3 | KNOWN | 0x20A | HVP_contactorState / HVP_packCtrsRequestStatus | HVP_contactorState / HVP_packCtrsRequestStatus / enum={"0": "NOT_ACTIVE", "1": "ACTIVE", "2": "COMPLETED"} | 稳定性=LOW_CARDINALITY；变化次数=0；序列=NOT_ACTIVE | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-464571D40359 | KNOWN | 0x20A | HVP_contactorState / HVP_hvilStatus | HVP_contactorState / HVP_hvilStatus / enum={"0": "UNKNOWN", "1": "STATUS_OK", "2": "CURRENT_SOURCE_FAULT", "3": "INTERNAL_OPEN_FAULT", "4": "VEHICLE_OPEN_FAULT", "5": "PENTHOUSE_LID_OPEN_FAULT", "6": "UNKNOWN_LOCATION_OPEN_FAULT", "7": "VEHICLE_NODE_FAULT", "8": "NO_12V_SUPPLY"} | 稳定性=LOW_CARDINALITY；变化次数=2；首次变化=133.8453 s（CAN Observed Time）；末次变化=134.8465 s（CAN Observed Time）；序列=STATUS_OK → UNKNOWN → STATUS_OK | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-B02973A15F54 | KNOWN | 0x224 | PCS_dcdcStatus / PCS_dcdcOutputIsLimited | PCS_dcdcStatus / PCS_dcdcOutputIsLimited | 稳定性=CONSTANT；变化次数=0；最小值=0.0；最大值=0.0；序列=0 | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-605D4479E286 | KNOWN | 0x20A | HVP_contactorState / HVP_fcCtrsRequestStatus | HVP_contactorState / HVP_fcCtrsRequestStatus / enum={"0": "NOT_ACTIVE", "1": "ACTIVE", "2": "COMPLETED"} | 稳定性=LOW_CARDINALITY；变化次数=2；首次变化=133.8453 s（CAN Observed Time）；末次变化=134.8465 s（CAN Observed Time）；序列=COMPLETED → NOT_ACTIVE → COMPLETED | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-00D930D51795 | KNOWN | 0x20A | HVP_contactorState / HVP_fcCtrsResetRequestRequired | HVP_contactorState / HVP_fcCtrsResetRequestRequired | 稳定性=CONSTANT；变化次数=0；最小值=0.0；最大值=0.0；序列=0 | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-0235B54B0CCF | KNOWN | 0x20A | HVP_contactorState / HVP_packCtrsResetRequestRequired | HVP_contactorState / HVP_packCtrsResetRequestRequired | 稳定性=CONSTANT；变化次数=0；最小值=0.0；最大值=0.0；序列=0 | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| OBS-0005 | RESIDUAL | 0x108 | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=11311 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |
| OBS-0012 | UNKNOWN | 0x128 | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=9 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |

### C. 为什么进入输入（DBC REFERENCE METADATA — 仅供参考，不是 Evidence）

- `SO-19CE993899A3`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": [], "domain_concepts": ["ELECTRICAL", "HV_PATH"], "domain_terms": ["contactor", "hv", "pack"], "planned_phase_refs": ["PP-SAFE-EXIT"], "role_terms": ["request", "state", "status"]}`。不据此确认 Semantic Role。
- `SO-464571D40359`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["HV_PATH"], "domain_terms": ["contactor", "hv", "hvil"], "planned_phase_refs": ["PP-ESTABLISH"], "role_terms": ["state", "status"]}`。不据此确认 Semantic Role。
- `SO-B02973A15F54`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": [], "domain_concepts": ["ELECTRICAL", "PROTECTION"], "domain_terms": ["dc", "limit"], "planned_phase_refs": ["PP-SAFE-EXIT"], "role_terms": ["output", "status"]}`。不据此确认 Semantic Role。
- `SO-605D4479E286`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["HV_PATH"], "domain_terms": ["contactor", "hv"], "planned_phase_refs": ["PP-ESTABLISH"], "role_terms": ["request", "state", "status"]}`。不据此确认 Semantic Role。
- `SO-00D930D51795`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": [], "domain_concepts": ["HV_PATH"], "domain_terms": ["contactor", "hv"], "planned_phase_refs": ["PP-SAFE-EXIT"], "role_terms": ["request", "state"]}`。不据此确认 Semantic Role。
- `SO-0235B54B0CCF`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": [], "domain_concepts": ["ELECTRICAL", "HV_PATH"], "domain_terms": ["contactor", "hv", "pack"], "planned_phase_refs": ["PP-SAFE-EXIT"], "role_terms": ["request", "state"]}`。不据此确认 Semantic Role。
- `OBS-0005`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": ["PP-ESTABLISH", "PP-STOP"], "role_terms": []}`。不据此确认 Semantic Role。
- `OBS-0012`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": ["PP-ESTABLISH", "PP-STOP"], "role_terms": []}`。不据此确认 Semantic Role。

### D. LLM 获得的 Structured Context

- `SO-19CE993899A3` identity_hint：`{"bus_key": "ch1:0x20A", "dbc_name_hint": "HVP_packCtrsRequestStatus", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "HVP_contactorState", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-19CE993899A3` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 1, "change_count": 0, "first_change_time_s": null, "last_change_time_s": null, "stability_class": "LOW_CARDINALITY", "tags": []}`
- `SO-19CE993899A3` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-19CE993899A3` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-19CE993899A3` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-464571D40359` identity_hint：`{"bus_key": "ch1:0x20A", "dbc_name_hint": "HVP_hvilStatus", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "HVP_contactorState", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-464571D40359` behavior：`{"anomaly_flags": ["SNA_PRESENT"], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 2, "first_change_time_s": 133.8453, "last_change_time_s": 134.8465, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-464571D40359` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-464571D40359` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-464571D40359` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-B02973A15F54` identity_hint：`{"bus_key": "ch1:0x224", "dbc_name_hint": "PCS_dcdcOutputIsLimited", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "PCS_dcdcStatus", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-B02973A15F54` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 1, "change_count": 0, "first_change_time_s": null, "last_change_time_s": null, "stability_class": "CONSTANT", "tags": []}`
- `SO-B02973A15F54` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-B02973A15F54` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-B02973A15F54` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-605D4479E286` identity_hint：`{"bus_key": "ch1:0x20A", "dbc_name_hint": "HVP_fcCtrsRequestStatus", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "HVP_contactorState", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-605D4479E286` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 2, "first_change_time_s": 133.8453, "last_change_time_s": 134.8465, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-605D4479E286` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-605D4479E286` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-605D4479E286` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-00D930D51795` identity_hint：`{"bus_key": "ch1:0x20A", "dbc_name_hint": "HVP_fcCtrsResetRequestRequired", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "HVP_contactorState", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-00D930D51795` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 1, "change_count": 0, "first_change_time_s": null, "last_change_time_s": null, "stability_class": "CONSTANT", "tags": []}`
- `SO-00D930D51795` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-00D930D51795` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-00D930D51795` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-0235B54B0CCF` identity_hint：`{"bus_key": "ch1:0x20A", "dbc_name_hint": "HVP_packCtrsResetRequestRequired", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "HVP_contactorState", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-0235B54B0CCF` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 1, "change_count": 0, "first_change_time_s": null, "last_change_time_s": null, "stability_class": "CONSTANT", "tags": []}`
- `SO-0235B54B0CCF` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-0235B54B0CCF` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-0235B54B0CCF` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0005` identity_hint：`{"bus_key": "ch1:0x108", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0005` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 133, "change_count": 11311, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "UNNAMED_ACTIVITY"]}`
- `OBS-0005` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0005` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0005` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0012` identity_hint：`{"bus_key": "ch1:0x128", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0012` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 5, "change_count": 9, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "LOW_CARDINALITY", "UNNAMED_ACTIVITY"]}`
- `OBS-0012` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0012` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0012` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`

### E. 精确输入追溯

- Question：`/semantic_evidence_questions/7`
- Per-question evidence：`/per_question_evidence/7`
- Intent：`/semantic_search_intents/7` (`SSI-ER-08`)
- Retrieval result：`/retrieval_results/7`
- Observation objects：`/observations/36` → `SO-19CE993899A3`, `/observations/37` → `SO-464571D40359`, `/observations/38` → `SO-B02973A15F54`, `/observations/39` → `SO-605D4479E286`, `/observations/40` → `SO-00D930D51795`, `/observations/41` → `SO-0235B54B0CCF`, `/observations/7` → `OBS-0005`, `/observations/10` → `OBS-0012`
- Observation contexts：`/observation_contexts/31` → `SO-19CE993899A3`, `/observation_contexts/30` → `SO-464571D40359`, `/observation_contexts/35` → `SO-B02973A15F54`, `/observation_contexts/27` → `SO-605D4479E286`, `/observation_contexts/28` → `SO-00D930D51795`, `/observation_contexts/32` → `SO-0235B54B0CCF`, `/observation_contexts/54` → `OBS-0005`, `/observation_contexts/56` → `OBS-0012`

## ER-09 — Identify high-voltage path request, action, feedback, voltage matching, and establishment within observable limits

### A. 语义目标

- ER：`ER-09`
- Control Tree Reference：`CT-DCFC-01, CT-DCFC-02, CT-DCFC-04, CT-DCFC-06, CT-DCFC-07, CT-DCFC-08, CT-DCFC-09, CT-DCFC-10, CT-DCFC-11, CT-DCFC-12, CT-DCFC-13, CT-DCFC-14, CT-DCFC-15`
- Semantic Evidence Question：Identify high-voltage path request, action, feedback, voltage matching, and establishment within observable limits.
- Sufficiency / Semantic Boundary：Contactor state alone does not prove energy transfer.
- Candidate Role（未确认）：`REQUEST, ACTUAL, STATE`
- Forbidden Substitution：`CAPABILITY, PERMISSION`
- Collection Script / Planned Procedure Context：`PP-ESTABLISH`（check whether charging actually established using independent vehicle and EVSE evidence；120–150 s；PLANNED_TIME）; `PP-CHARGE-OBSERVE`（observe EVSE and Pack voltage current power capability state and thermal context；150–210 s；PLANNED_TIME）; `PP-STEADY-HOLD`（observe a conditional short stable interval if naturally available；210–240 s；PLANNED_TIME）; `PP-STOP`（request one normal stop if charging has not already ended；240–270 s；PLANNED_TIME）; `PP-SAFE-EXIT`（confirm output stopped and lock released before disconnecting；270–300 s；PLANNED_TIME）
- 时间边界：`PLANNED_TIME_IS_NOT_OBSERVED_EVENT_TIME`

### B. 实际送入 LLM 的 Observation

| Observation | Space | CAN ID / Bus | Message / Signal | DBC 参考 | ASC 实际行为 | Retrieval Provenance |
|---|---|---|---|---|---|---|
| SO-19CE993899A3 | KNOWN | 0x20A | HVP_contactorState / HVP_packCtrsRequestStatus | HVP_contactorState / HVP_packCtrsRequestStatus / enum={"0": "NOT_ACTIVE", "1": "ACTIVE", "2": "COMPLETED"} | 稳定性=LOW_CARDINALITY；变化次数=0；序列=NOT_ACTIVE | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-464571D40359 | KNOWN | 0x20A | HVP_contactorState / HVP_hvilStatus | HVP_contactorState / HVP_hvilStatus / enum={"0": "UNKNOWN", "1": "STATUS_OK", "2": "CURRENT_SOURCE_FAULT", "3": "INTERNAL_OPEN_FAULT", "4": "VEHICLE_OPEN_FAULT", "5": "PENTHOUSE_LID_OPEN_FAULT", "6": "UNKNOWN_LOCATION_OPEN_FAULT", "7": "VEHICLE_NODE_FAULT", "8": "NO_12V_SUPPLY"} | 稳定性=LOW_CARDINALITY；变化次数=2；首次变化=133.8453 s（CAN Observed Time）；末次变化=134.8465 s（CAN Observed Time）；序列=STATUS_OK → UNKNOWN → STATUS_OK | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-605D4479E286 | KNOWN | 0x20A | HVP_contactorState / HVP_fcCtrsRequestStatus | HVP_contactorState / HVP_fcCtrsRequestStatus / enum={"0": "NOT_ACTIVE", "1": "ACTIVE", "2": "COMPLETED"} | 稳定性=LOW_CARDINALITY；变化次数=2；首次变化=133.8453 s（CAN Observed Time）；末次变化=134.8465 s（CAN Observed Time）；序列=COMPLETED → NOT_ACTIVE → COMPLETED | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-00D930D51795 | KNOWN | 0x20A | HVP_contactorState / HVP_fcCtrsResetRequestRequired | HVP_contactorState / HVP_fcCtrsResetRequestRequired | 稳定性=CONSTANT；变化次数=0；最小值=0.0；最大值=0.0；序列=0 | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-0235B54B0CCF | KNOWN | 0x20A | HVP_contactorState / HVP_packCtrsResetRequestRequired | HVP_contactorState / HVP_packCtrsResetRequestRequired | 稳定性=CONSTANT；变化次数=0；最小值=0.0；最大值=0.0；序列=0 | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-40123AC227A0 | KNOWN | 0x20A | HVP_contactorState / HVP_fcContactorSetState | HVP_contactorState / HVP_fcContactorSetState / enum={"0": "SNA", "1": "OPEN", "2": "CLOSING", "3": "BLOCKED", "4": "OPENING", "5": "CLOSED", "6": "PARTIAL_WELD", "7": "WELDED", "8": "POSITIVE_CLOSED", "9": "NEGATIVE_CLOSED"} | 稳定性=LOW_CARDINALITY；变化次数=2；首次变化=134.8465 s（CAN Observed Time）；末次变化=246.8477 s（CAN Observed Time）；序列=OPEN → CLOSED → OPEN | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| OBS-0005 | RESIDUAL | 0x108 | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=11311 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |
| OBS-0012 | UNKNOWN | 0x128 | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=9 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |

### C. 为什么进入输入（DBC REFERENCE METADATA — 仅供参考，不是 Evidence）

- `SO-19CE993899A3`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": [], "domain_concepts": ["ELECTRICAL", "HV_PATH"], "domain_terms": ["contactor", "hv", "pack"], "planned_phase_refs": ["PP-SAFE-EXIT"], "role_terms": ["request", "state", "status"]}`。不据此确认 Semantic Role。
- `SO-464571D40359`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["HV_PATH"], "domain_terms": ["contactor", "hv", "hvil"], "planned_phase_refs": ["PP-ESTABLISH"], "role_terms": ["state", "status"]}`。不据此确认 Semantic Role。
- `SO-605D4479E286`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["HV_PATH"], "domain_terms": ["contactor", "hv"], "planned_phase_refs": ["PP-ESTABLISH"], "role_terms": ["request", "state", "status"]}`。不据此确认 Semantic Role。
- `SO-00D930D51795`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": [], "domain_concepts": ["HV_PATH"], "domain_terms": ["contactor", "hv"], "planned_phase_refs": ["PP-SAFE-EXIT"], "role_terms": ["request", "state"]}`。不据此确认 Semantic Role。
- `SO-0235B54B0CCF`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": [], "domain_concepts": ["ELECTRICAL", "HV_PATH"], "domain_terms": ["contactor", "hv", "pack"], "planned_phase_refs": ["PP-SAFE-EXIT"], "role_terms": ["request", "state"]}`。不据此确认 Semantic Role。
- `SO-40123AC227A0`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["HV_PATH"], "domain_terms": ["contactor", "hv"], "planned_phase_refs": ["PP-ESTABLISH", "PP-STOP"], "role_terms": ["state"]}`。不据此确认 Semantic Role。
- `OBS-0005`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": ["PP-ESTABLISH", "PP-STOP"], "role_terms": []}`。不据此确认 Semantic Role。
- `OBS-0012`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": ["PP-ESTABLISH", "PP-STOP"], "role_terms": []}`。不据此确认 Semantic Role。

### D. LLM 获得的 Structured Context

- `SO-19CE993899A3` identity_hint：`{"bus_key": "ch1:0x20A", "dbc_name_hint": "HVP_packCtrsRequestStatus", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "HVP_contactorState", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-19CE993899A3` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 1, "change_count": 0, "first_change_time_s": null, "last_change_time_s": null, "stability_class": "LOW_CARDINALITY", "tags": []}`
- `SO-19CE993899A3` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-19CE993899A3` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-19CE993899A3` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-464571D40359` identity_hint：`{"bus_key": "ch1:0x20A", "dbc_name_hint": "HVP_hvilStatus", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "HVP_contactorState", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-464571D40359` behavior：`{"anomaly_flags": ["SNA_PRESENT"], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 2, "first_change_time_s": 133.8453, "last_change_time_s": 134.8465, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-464571D40359` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-464571D40359` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-464571D40359` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-605D4479E286` identity_hint：`{"bus_key": "ch1:0x20A", "dbc_name_hint": "HVP_fcCtrsRequestStatus", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "HVP_contactorState", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-605D4479E286` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 2, "first_change_time_s": 133.8453, "last_change_time_s": 134.8465, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-605D4479E286` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-605D4479E286` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-605D4479E286` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-00D930D51795` identity_hint：`{"bus_key": "ch1:0x20A", "dbc_name_hint": "HVP_fcCtrsResetRequestRequired", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "HVP_contactorState", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-00D930D51795` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 1, "change_count": 0, "first_change_time_s": null, "last_change_time_s": null, "stability_class": "CONSTANT", "tags": []}`
- `SO-00D930D51795` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-00D930D51795` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-00D930D51795` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-0235B54B0CCF` identity_hint：`{"bus_key": "ch1:0x20A", "dbc_name_hint": "HVP_packCtrsResetRequestRequired", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "HVP_contactorState", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-0235B54B0CCF` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 1, "change_count": 0, "first_change_time_s": null, "last_change_time_s": null, "stability_class": "CONSTANT", "tags": []}`
- `SO-0235B54B0CCF` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-0235B54B0CCF` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-0235B54B0CCF` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-40123AC227A0` identity_hint：`{"bus_key": "ch1:0x20A", "dbc_name_hint": "HVP_fcContactorSetState", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "HVP_contactorState", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-40123AC227A0` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 2, "first_change_time_s": 134.8465, "last_change_time_s": 246.8477, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-40123AC227A0` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-40123AC227A0` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-40123AC227A0` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0005` identity_hint：`{"bus_key": "ch1:0x108", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0005` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 133, "change_count": 11311, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "UNNAMED_ACTIVITY"]}`
- `OBS-0005` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0005` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0005` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0012` identity_hint：`{"bus_key": "ch1:0x128", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0012` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 5, "change_count": 9, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "LOW_CARDINALITY", "UNNAMED_ACTIVITY"]}`
- `OBS-0012` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0012` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0012` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`

### E. 精确输入追溯

- Question：`/semantic_evidence_questions/8`
- Per-question evidence：`/per_question_evidence/8`
- Intent：`/semantic_search_intents/8` (`SSI-ER-09`)
- Retrieval result：`/retrieval_results/8`
- Observation objects：`/observations/36` → `SO-19CE993899A3`, `/observations/37` → `SO-464571D40359`, `/observations/39` → `SO-605D4479E286`, `/observations/40` → `SO-00D930D51795`, `/observations/41` → `SO-0235B54B0CCF`, `/observations/42` → `SO-40123AC227A0`, `/observations/7` → `OBS-0005`, `/observations/10` → `OBS-0012`
- Observation contexts：`/observation_contexts/31` → `SO-19CE993899A3`, `/observation_contexts/30` → `SO-464571D40359`, `/observation_contexts/27` → `SO-605D4479E286`, `/observation_contexts/28` → `SO-00D930D51795`, `/observation_contexts/32` → `SO-0235B54B0CCF`, `/observation_contexts/26` → `SO-40123AC227A0`, `/observation_contexts/54` → `OBS-0005`, `/observation_contexts/56` → `OBS-0012`

## ER-10 — Distinguish EVSE Actual voltage/current/power from Pack Actual voltage/current/power at their measurement boundaries

### A. 语义目标

- ER：`ER-10`
- Control Tree Reference：`CT-DCFC-01, CT-DCFC-02, CT-DCFC-04, CT-DCFC-05, CT-DCFC-06, CT-DCFC-07, CT-DCFC-08, CT-DCFC-09, CT-DCFC-10, CT-DCFC-11, CT-DCFC-12, CT-DCFC-13, CT-DCFC-14, CT-DCFC-15`
- Semantic Evidence Question：Distinguish EVSE Actual voltage/current/power from Pack Actual voltage/current/power at their measurement boundaries.
- Sufficiency / Semantic Boundary：Cross-boundary comparison requires synchronized and semantically validated measurements.
- Candidate Role（未确认）：`ACTUAL`
- Forbidden Substitution：`CAPABILITY, PERMISSION, REQUEST`
- Collection Script / Planned Procedure Context：`PP-CHARGE-OBSERVE`（observe EVSE and Pack voltage current power capability state and thermal context；150–210 s；PLANNED_TIME）; `PP-STEADY-HOLD`（observe a conditional short stable interval if naturally available；210–240 s；PLANNED_TIME）; `PP-SAFE-EXIT`（confirm output stopped and lock released before disconnecting；270–300 s；PLANNED_TIME）
- 时间边界：`PLANNED_TIME_IS_NOT_OBSERVED_EVENT_TIME`

### B. 实际送入 LLM 的 Observation

| Observation | Space | CAN ID / Bus | Message / Signal | DBC 参考 | ASC 实际行为 | Retrieval Provenance |
|---|---|---|---|---|---|---|
| SO-2CA4B2E7EDED | KNOWN | 0x29D | CP_dcChargeStatus / CP_evseOutputDcCurrentStale | CP_dcChargeStatus / CP_evseOutputDcCurrentStale | 稳定性=LOW_CARDINALITY；变化次数=4；最小值=0.0；最大值=1.0；首次变化=39.7208 s（CAN Observed Time）；末次变化=273.5351 s（CAN Observed Time）；序列=1 → 0 → 1 → 0 → 1 | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-30140211597F | KNOWN | 0x29D | CP_dcChargeStatus / CP_evseOutputDcVoltage | CP_dcChargeStatus / CP_evseOutputDcVoltage / unit=V | 稳定性=DYNAMIC；变化次数=22；最小值=0.0；最大值=365.47857799999997；首次变化=140.0275 s（CAN Observed Time）；末次变化=246.2332 s（CAN Observed Time）；序列=0.0 → 346.87505919999995 → 347.31451239999996 → 349.29205179999997 → 352.3682242 → 355.5176388 → 358.37408459999995 → 361.08404599999994 … | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-05B359B48253 | KNOWN | 0x132 | BMS_hvBusStatus / BMS_packCurrent | BMS_hvBusStatus / BMS_packCurrent / unit=A / enum={"-16384": "SNA"} | 稳定性=DYNAMIC；变化次数=17475；最小值=-219.60000000000002；最大值=27.8；首次变化=0.0421 s（CAN Observed Time）；末次变化=299.7285 s（CAN Observed Time）；序列=0.8 → 0.7000000000000001 → 0.8 → 0.7000000000000001 → 0.8 → 0.7000000000000001 → 0.8 → 0.7000000000000001 … | DIRECT_INTENT_RETRIEVAL; PHYSICAL_DIMENSION_BEHAVIOR |
| SO-CE0335F98FD8 | KNOWN | 0x29D | CP_dcChargeStatus / CP_evseOutputDcCurrent | CP_dcChargeStatus / CP_evseOutputDcCurrent / unit=A | 稳定性=DYNAMIC；变化次数=12；最小值=0.0；最大值=133.0892539；首次变化=145.0277 s（CAN Observed Time）；末次变化=246.2332 s（CAN Observed Time）；序列=0.0 → 31.9355612 → 55.8872321 → 79.2529294 → 99.2492785 → 117.4144601 → 133.0892539 → 129.1339321 … | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-CEEC4D90BE22 | KNOWN | 0x132 | BMS_hvBusStatus / BMS_packVoltage | BMS_hvBusStatus / BMS_packVoltage / unit=V | 稳定性=DYNAMIC；变化次数=28790；最小值=8.17；最大值=365.25；首次变化=0.012 s（CAN Observed Time）；末次变化=299.7285 s（CAN Observed Time）；序列=347.13 → 347.06 → 347.27 → 347.11 → 347.21 → 347.2 → 347.19 → 347.12 … | DIRECT_INTENT_RETRIEVAL; PHYSICAL_DIMENSION_BEHAVIOR |
| SO-FEC38397A149 | KNOWN | 0x3F2 | BMS_kwhCountersMultiplexed / BMS_dcChargerKwhTotal | BMS_kwhCountersMultiplexed / BMS_dcChargerKwhTotal / unit=KWh | 稳定性=NEAR_CONSTANT；变化次数=9；最小值=3769.587；最大值=3771.523；首次变化=151.8501 s（CAN Observed Time）；末次变化=247.852 s（CAN Observed Time）；序列=3769.587 → 3769.667 → 3769.907 → 3770.154 → 3770.3940000000002 → 3770.631 → 3770.864 → 3771.098 … | DIRECT_INTENT_RETRIEVAL; PROCEDURE_ALIGNED_DOMAIN_HINT |
| OBS-0278 | UNKNOWN | 0x53F | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=6 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |
| OBS-0010 | RESIDUAL | 0x123 | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=50932 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |

### C. 为什么进入输入（DBC REFERENCE METADATA — 仅供参考，不是 Evidence）

- `SO-2CA4B2E7EDED`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["ELECTRICAL", "EVSE_BOUNDARY"], "domain_terms": ["charge", "current", "dc", "evse"], "planned_phase_refs": ["PP-SAFE-EXIT"], "role_terms": ["output"]}`。不据此确认 Semantic Role。
- `SO-30140211597F`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC"], "domain_concepts": ["ELECTRICAL", "EVSE_BOUNDARY"], "domain_terms": ["charge", "dc", "evse", "voltage"], "planned_phase_refs": [], "role_terms": ["output"]}`。不据此确认 Semantic Role。
- `SO-05B359B48253`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`PHYSICAL_DIMENSION_BEHAVIOR`；retrieval_reasons=`PHYSICAL_DIMENSION_BEHAVIOR`；context_matches=`{"behavior_tags": ["DYNAMIC"], "domain_concepts": ["ELECTRICAL", "VEHICLE_BOUNDARY"], "domain_terms": ["bms", "current", "pack"], "planned_phase_refs": ["PP-SAFE-EXIT"], "role_terms": []}`。不据此确认 Semantic Role。
- `SO-CE0335F98FD8`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["ELECTRICAL", "EVSE_BOUNDARY"], "domain_terms": ["charge", "current", "dc", "evse"], "planned_phase_refs": [], "role_terms": ["output"]}`。不据此确认 Semantic Role。
- `SO-CEEC4D90BE22`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`PHYSICAL_DIMENSION_BEHAVIOR`；retrieval_reasons=`PHYSICAL_DIMENSION_BEHAVIOR`；context_matches=`{"behavior_tags": ["DYNAMIC"], "domain_concepts": ["ELECTRICAL", "VEHICLE_BOUNDARY"], "domain_terms": ["bms", "pack", "voltage"], "planned_phase_refs": ["PP-SAFE-EXIT"], "role_terms": []}`。不据此确认 Semantic Role。
- `SO-FEC38397A149`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`PROCEDURE_ALIGNED_DOMAIN_HINT`；retrieval_reasons=`PROCEDURE_ALIGNED_DOMAIN_HINT`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["ELECTRICAL", "EVSE_BOUNDARY", "VEHICLE_BOUNDARY"], "domain_terms": ["bms", "charge", "charger", "dc"], "planned_phase_refs": ["PP-CHARGE-OBSERVE"], "role_terms": []}`。不据此确认 Semantic Role。
- `OBS-0278`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": ["PP-CHARGE-OBSERVE", "PP-SAFE-EXIT"], "role_terms": []}`。不据此确认 Semantic Role。
- `OBS-0010`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": ["PP-SAFE-EXIT"], "role_terms": []}`。不据此确认 Semantic Role。

### D. LLM 获得的 Structured Context

- `SO-2CA4B2E7EDED` identity_hint：`{"bus_key": "ch1:0x29D", "dbc_name_hint": "CP_evseOutputDcCurrentStale", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_dcChargeStatus", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-2CA4B2E7EDED` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 4, "first_change_time_s": 39.7208, "last_change_time_s": 273.5351, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-2CA4B2E7EDED` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-PORT-OPEN", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-2CA4B2E7EDED` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-2CA4B2E7EDED` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-30140211597F` identity_hint：`{"bus_key": "ch1:0x29D", "dbc_name_hint": "CP_evseOutputDcVoltage", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_dcChargeStatus", "semantic_validation_state": "UNVALIDATED", "unit": "V"}`
- `SO-30140211597F` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 19, "change_count": 22, "first_change_time_s": 140.0275, "last_change_time_s": 246.2332, "stability_class": "DYNAMIC", "tags": ["DYNAMIC"]}`
- `SO-30140211597F` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-30140211597F` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-30140211597F` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-05B359B48253` identity_hint：`{"bus_key": "ch1:0x132", "dbc_name_hint": "BMS_packCurrent", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "BMS_hvBusStatus", "semantic_validation_state": "UNVALIDATED", "unit": "A"}`
- `SO-05B359B48253` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": ">=256", "change_count": 17475, "first_change_time_s": 0.0421, "last_change_time_s": 299.7285, "stability_class": "DYNAMIC", "tags": ["DYNAMIC"]}`
- `SO-05B359B48253` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-05B359B48253` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-05B359B48253` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-CE0335F98FD8` identity_hint：`{"bus_key": "ch1:0x29D", "dbc_name_hint": "CP_evseOutputDcCurrent", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_dcChargeStatus", "semantic_validation_state": "UNVALIDATED", "unit": "A"}`
- `SO-CE0335F98FD8` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 11, "change_count": 12, "first_change_time_s": 145.0277, "last_change_time_s": 246.2332, "stability_class": "DYNAMIC", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-CE0335F98FD8` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-CE0335F98FD8` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-CE0335F98FD8` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-CEEC4D90BE22` identity_hint：`{"bus_key": "ch1:0x132", "dbc_name_hint": "BMS_packVoltage", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "BMS_hvBusStatus", "semantic_validation_state": "UNVALIDATED", "unit": "V"}`
- `SO-CEEC4D90BE22` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": ">=256", "change_count": 28790, "first_change_time_s": 0.012, "last_change_time_s": 299.7285, "stability_class": "DYNAMIC", "tags": ["DYNAMIC"]}`
- `SO-CEEC4D90BE22` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-CEEC4D90BE22` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-CEEC4D90BE22` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-FEC38397A149` identity_hint：`{"bus_key": "ch1:0x3F2", "dbc_name_hint": "BMS_dcChargerKwhTotal", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "BMS_kwhCountersMultiplexed", "semantic_validation_state": "UNVALIDATED", "unit": "KWh"}`
- `SO-FEC38397A149` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 10, "change_count": 9, "first_change_time_s": 151.8501, "last_change_time_s": 247.852, "stability_class": "NEAR_CONSTANT", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-FEC38397A149` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-CHARGE-OBSERVE", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-FEC38397A149` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-FEC38397A149` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0278` identity_hint：`{"bus_key": "ch1:0x53F", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0278` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 6, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "LOW_CARDINALITY", "UNNAMED_ACTIVITY"]}`
- `OBS-0278` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-CHARGE-OBSERVE", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0278` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0278` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0010` identity_hint：`{"bus_key": "ch1:0x123", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0010` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 50932, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "LOW_CARDINALITY", "UNNAMED_ACTIVITY"]}`
- `OBS-0010` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0010` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0010` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`

### E. 精确输入追溯

- Question：`/semantic_evidence_questions/9`
- Per-question evidence：`/per_question_evidence/9`
- Intent：`/semantic_search_intents/9` (`SSI-ER-10`)
- Retrieval result：`/retrieval_results/9`
- Observation objects：`/observations/24` → `SO-2CA4B2E7EDED`, `/observations/22` → `SO-30140211597F`, `/observations/35` → `SO-05B359B48253`, `/observations/23` → `SO-CE0335F98FD8`, `/observations/43` → `SO-CEEC4D90BE22`, `/observations/25` → `SO-FEC38397A149`, `/observations/44` → `OBS-0278`, `/observations/45` → `OBS-0010`
- Observation contexts：`/observation_contexts/13` → `SO-2CA4B2E7EDED`, `/observation_contexts/14` → `SO-30140211597F`, `/observation_contexts/9` → `SO-05B359B48253`, `/observation_contexts/12` → `SO-CE0335F98FD8`, `/observation_contexts/10` → `SO-CEEC4D90BE22`, `/observation_contexts/2` → `SO-FEC38397A149`, `/observation_contexts/61` → `OBS-0278`, `/observation_contexts/55` → `OBS-0010`

## ER-11 — Assess the continuous Capability, Request, EVSE Actual, and Pack Actual relationship without collapsing roles or assuming causality from proximity

### A. 语义目标

- ER：`ER-11`
- Control Tree Reference：`CT-DCFC-01, CT-DCFC-02, CT-DCFC-04, CT-DCFC-05, CT-DCFC-06, CT-DCFC-07, CT-DCFC-08, CT-DCFC-09, CT-DCFC-10, CT-DCFC-11, CT-DCFC-12, CT-DCFC-13, CT-DCFC-14, CT-DCFC-15`
- Semantic Evidence Question：Assess the continuous Capability, Request, EVSE Actual, and Pack Actual relationship without collapsing roles or assuming causality from proximity.
- Sufficiency / Semantic Boundary：Missing roles remain explicit gaps.
- Candidate Role（未确认）：`CAPABILITY, REQUEST, ACTUAL`
- Forbidden Substitution：`PERMISSION`
- Collection Script / Planned Procedure Context：`PP-CHARGE-OBSERVE`（observe EVSE and Pack voltage current power capability state and thermal context；150–210 s；PLANNED_TIME）; `PP-STEADY-HOLD`（observe a conditional short stable interval if naturally available；210–240 s；PLANNED_TIME）; `PP-STOP`（request one normal stop if charging has not already ended；240–270 s；PLANNED_TIME）; `PP-SAFE-EXIT`（confirm output stopped and lock released before disconnecting；270–300 s；PLANNED_TIME）
- 时间边界：`PLANNED_TIME_IS_NOT_OBSERVED_EVENT_TIME`

### B. 实际送入 LLM 的 Observation

| Observation | Space | CAN ID / Bus | Message / Signal | DBC 参考 | ASC 实际行为 | Retrieval Provenance |
|---|---|---|---|---|---|---|
| SO-30140211597F | KNOWN | 0x29D | CP_dcChargeStatus / CP_evseOutputDcVoltage | CP_dcChargeStatus / CP_evseOutputDcVoltage / unit=V | 稳定性=DYNAMIC；变化次数=22；最小值=0.0；最大值=365.47857799999997；首次变化=140.0275 s（CAN Observed Time）；末次变化=246.2332 s（CAN Observed Time）；序列=0.0 → 346.87505919999995 → 347.31451239999996 → 349.29205179999997 → 352.3682242 → 355.5176388 → 358.37408459999995 → 361.08404599999994 … | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-CE0335F98FD8 | KNOWN | 0x29D | CP_dcChargeStatus / CP_evseOutputDcCurrent | CP_dcChargeStatus / CP_evseOutputDcCurrent / unit=A | 稳定性=DYNAMIC；变化次数=12；最小值=0.0；最大值=133.0892539；首次变化=145.0277 s（CAN Observed Time）；末次变化=246.2332 s（CAN Observed Time）；序列=0.0 → 31.9355612 → 55.8872321 → 79.2529294 → 99.2492785 → 117.4144601 → 133.0892539 → 129.1339321 … | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-EE1762E29E91 | KNOWN | 0x2D2 | BMS_driveLimits / BMS_maxChargeCurrent | BMS_driveLimits / BMS_maxChargeCurrent / unit=A | 稳定性=LOW_CARDINALITY；变化次数=4；最小值=0.0；最大值=250.0；首次变化=115.392 s（CAN Observed Time）；末次变化=246.3935 s（CAN Observed Time）；序列=0.0 → 250.0 → 0.0 → 250.0 → 0.0 | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-2CA4B2E7EDED | KNOWN | 0x29D | CP_dcChargeStatus / CP_evseOutputDcCurrentStale | CP_dcChargeStatus / CP_evseOutputDcCurrentStale | 稳定性=LOW_CARDINALITY；变化次数=4；最小值=0.0；最大值=1.0；首次变化=39.7208 s（CAN Observed Time）；末次变化=273.5351 s（CAN Observed Time）；序列=1 → 0 → 1 → 0 → 1 | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-C817FE195629 | KNOWN | 0x21D | CP_evseStatus / CP_cableCurrentLimit | CP_evseStatus / CP_cableCurrentLimit / unit=A | 稳定性=CONSTANT；变化次数=0；最小值=0.0；最大值=0.0；序列=0 | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-CDB81064C219 | KNOWN | 0x21D | CP_evseStatus / CP_lineVoltageRequested | CP_evseStatus / CP_lineVoltageRequested | 稳定性=LOW_CARDINALITY；变化次数=4；最小值=0.0；最大值=1.0；首次变化=39.7192 s（CAN Observed Time）；末次变化=273.5338 s（CAN Observed Time）；序列=1 → 0 → 1 → 0 → 1 | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| OBS-0278 | UNKNOWN | 0x53F | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=6 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |
| OBS-0005 | RESIDUAL | 0x108 | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=11311 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |

### C. 为什么进入输入（DBC REFERENCE METADATA — 仅供参考，不是 Evidence）

- `SO-30140211597F`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC"], "domain_concepts": ["ELECTRICAL", "EVSE_BOUNDARY"], "domain_terms": ["charge", "dc", "evse", "voltage"], "planned_phase_refs": ["PP-STOP"], "role_terms": ["output"]}`。不据此确认 Semantic Role。
- `SO-CE0335F98FD8`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["ELECTRICAL", "EVSE_BOUNDARY"], "domain_terms": ["charge", "current", "dc", "evse"], "planned_phase_refs": ["PP-STOP"], "role_terms": ["output"]}`。不据此确认 Semantic Role。
- `SO-EE1762E29E91`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["ELECTRICAL", "VEHICLE_BOUNDARY"], "domain_terms": ["bms", "charge", "current"], "planned_phase_refs": ["PP-STOP"], "role_terms": ["limit"]}`。不据此确认 Semantic Role。
- `SO-2CA4B2E7EDED`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["ELECTRICAL", "EVSE_BOUNDARY"], "domain_terms": ["charge", "current", "dc", "evse"], "planned_phase_refs": ["PP-SAFE-EXIT"], "role_terms": ["output"]}`。不据此确认 Semantic Role。
- `SO-C817FE195629`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": [], "domain_concepts": ["ELECTRICAL", "EVSE_BOUNDARY"], "domain_terms": ["cable", "current", "evse"], "planned_phase_refs": ["PP-SAFE-EXIT"], "role_terms": ["limit"]}`。不据此确认 Semantic Role。
- `SO-CDB81064C219`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["ELECTRICAL", "EVSE_BOUNDARY"], "domain_terms": ["evse", "voltage"], "planned_phase_refs": ["PP-SAFE-EXIT"], "role_terms": ["request"]}`。不据此确认 Semantic Role。
- `OBS-0278`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": ["PP-CHARGE-OBSERVE", "PP-SAFE-EXIT"], "role_terms": []}`。不据此确认 Semantic Role。
- `OBS-0005`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": ["PP-STOP"], "role_terms": []}`。不据此确认 Semantic Role。

### D. LLM 获得的 Structured Context

- `SO-30140211597F` identity_hint：`{"bus_key": "ch1:0x29D", "dbc_name_hint": "CP_evseOutputDcVoltage", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_dcChargeStatus", "semantic_validation_state": "UNVALIDATED", "unit": "V"}`
- `SO-30140211597F` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 19, "change_count": 22, "first_change_time_s": 140.0275, "last_change_time_s": 246.2332, "stability_class": "DYNAMIC", "tags": ["DYNAMIC"]}`
- `SO-30140211597F` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-30140211597F` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-30140211597F` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-CE0335F98FD8` identity_hint：`{"bus_key": "ch1:0x29D", "dbc_name_hint": "CP_evseOutputDcCurrent", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_dcChargeStatus", "semantic_validation_state": "UNVALIDATED", "unit": "A"}`
- `SO-CE0335F98FD8` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 11, "change_count": 12, "first_change_time_s": 145.0277, "last_change_time_s": 246.2332, "stability_class": "DYNAMIC", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-CE0335F98FD8` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-CE0335F98FD8` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-CE0335F98FD8` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-EE1762E29E91` identity_hint：`{"bus_key": "ch1:0x2D2", "dbc_name_hint": "BMS_maxChargeCurrent", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "BMS_driveLimits", "semantic_validation_state": "UNVALIDATED", "unit": "A"}`
- `SO-EE1762E29E91` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 4, "first_change_time_s": 115.392, "last_change_time_s": 246.3935, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-EE1762E29E91` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-AUTH-START", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-EE1762E29E91` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-EE1762E29E91` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-2CA4B2E7EDED` identity_hint：`{"bus_key": "ch1:0x29D", "dbc_name_hint": "CP_evseOutputDcCurrentStale", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_dcChargeStatus", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-2CA4B2E7EDED` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 4, "first_change_time_s": 39.7208, "last_change_time_s": 273.5351, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-2CA4B2E7EDED` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-PORT-OPEN", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-2CA4B2E7EDED` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-2CA4B2E7EDED` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-C817FE195629` identity_hint：`{"bus_key": "ch1:0x21D", "dbc_name_hint": "CP_cableCurrentLimit", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_evseStatus", "semantic_validation_state": "UNVALIDATED", "unit": "A"}`
- `SO-C817FE195629` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 1, "change_count": 0, "first_change_time_s": null, "last_change_time_s": null, "stability_class": "CONSTANT", "tags": []}`
- `SO-C817FE195629` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-C817FE195629` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-C817FE195629` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-CDB81064C219` identity_hint：`{"bus_key": "ch1:0x21D", "dbc_name_hint": "CP_lineVoltageRequested", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_evseStatus", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-CDB81064C219` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 4, "first_change_time_s": 39.7192, "last_change_time_s": 273.5338, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-CDB81064C219` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-PORT-OPEN", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-CDB81064C219` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-CDB81064C219` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0278` identity_hint：`{"bus_key": "ch1:0x53F", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0278` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 6, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "LOW_CARDINALITY", "UNNAMED_ACTIVITY"]}`
- `OBS-0278` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-CHARGE-OBSERVE", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0278` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0278` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0005` identity_hint：`{"bus_key": "ch1:0x108", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0005` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 133, "change_count": 11311, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "UNNAMED_ACTIVITY"]}`
- `OBS-0005` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0005` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0005` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`

### E. 精确输入追溯

- Question：`/semantic_evidence_questions/10`
- Per-question evidence：`/per_question_evidence/10`
- Intent：`/semantic_search_intents/10` (`SSI-ER-11`)
- Retrieval result：`/retrieval_results/10`
- Observation objects：`/observations/22` → `SO-30140211597F`, `/observations/23` → `SO-CE0335F98FD8`, `/observations/28` → `SO-EE1762E29E91`, `/observations/24` → `SO-2CA4B2E7EDED`, `/observations/20` → `SO-C817FE195629`, `/observations/46` → `SO-CDB81064C219`, `/observations/44` → `OBS-0278`, `/observations/7` → `OBS-0005`
- Observation contexts：`/observation_contexts/14` → `SO-30140211597F`, `/observation_contexts/12` → `SO-CE0335F98FD8`, `/observation_contexts/6` → `SO-EE1762E29E91`, `/observation_contexts/13` → `SO-2CA4B2E7EDED`, `/observation_contexts/11` → `SO-C817FE195629`, `/observation_contexts/18` → `SO-CDB81064C219`, `/observation_contexts/61` → `OBS-0278`, `/observation_contexts/54` → `OBS-0005`

## ER-12 — Identify thermal state, thermal demand, execution, and effects on capability or request where supported

### A. 语义目标

- ER：`ER-12`
- Control Tree Reference：`CT-DCFC-08, CT-DCFC-14`
- Semantic Evidence Question：Identify thermal state, thermal demand, execution, and effects on capability or request where supported.
- Sufficiency / Semantic Boundary：Thermal correlation requires validation and an alternative-condition check for causal attribution.
- Candidate Role（未确认）：`CAPABILITY, REQUEST, STATE`
- Forbidden Substitution：`ACTUAL, PERMISSION`
- Collection Script / Planned Procedure Context：`PP-CHARGE-OBSERVE`（observe EVSE and Pack voltage current power capability state and thermal context；150–210 s；PLANNED_TIME）; `PP-STEADY-HOLD`（observe a conditional short stable interval if naturally available；210–240 s；PLANNED_TIME）; `PP-STOP`（request one normal stop if charging has not already ended；240–270 s；PLANNED_TIME）
- 时间边界：`PLANNED_TIME_IS_NOT_OBSERVED_EVENT_TIME`

### B. 实际送入 LLM 的 Observation

| Observation | Space | CAN ID / Bus | Message / Signal | DBC 参考 | ASC 实际行为 | Retrieval Provenance |
|---|---|---|---|---|---|---|
| SO-2BAA1DECBE96 | KNOWN | 0x312 | BMS_thermalStatus / BMS_inletActiveHeatTargetT | BMS_thermalStatus / BMS_inletActiveHeatTargetT / unit=DegC | 稳定性=DYNAMIC；变化次数=598；最小值=-14.0；最大值=80.5；首次变化=0.9913 s（CAN Observed Time）；末次变化=299.4974 s（CAN Observed Time）；序列=79.75 → -13.75 → 79.75 → -13.75 → 79.75 → -13.75 → 79.75 → -13.75 … | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-C8661259C0DA | KNOWN | 0x312 | BMS_thermalStatus / BMS_inletActiveCoolTargetT | BMS_thermalStatus / BMS_inletActiveCoolTargetT / unit=DegC | 稳定性=DYNAMIC；变化次数=598；最小值=-12.25；最大值=92.25；首次变化=0.9913 s（CAN Observed Time）；末次变化=299.4974 s（CAN Observed Time）；序列=-0.25 → -12.25 → -0.25 → -12.25 → -0.25 → -12.25 → -0.25 → -12.25 … | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-7717801FE8E8 | KNOWN | 0x2E1 | VCFRONT_status / VCFRONT_isActiveHeatingBattery | VCFRONT_status / VCFRONT_isActiveHeatingBattery | 稳定性=LOW_CARDINALITY；变化次数=2；最小值=0.0；最大值=1.0；首次变化=141.2739 s（CAN Observed Time）；末次变化=248.3204 s（CAN Observed Time）；序列=0 → 1 → 0 | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-BC7D879CB5FA | KNOWN | 0x241 | VCFRONT_coolant / VCFRONT_wasteHeatRequestType | VCFRONT_coolant / VCFRONT_wasteHeatRequestType / enum={"0": "NONE", "1": "PARTIAL", "2": "FULL"} | 稳定性=LOW_CARDINALITY；变化次数=4；首次变化=141.3329 s（CAN Observed Time）；末次变化=255.3398 s（CAN Observed Time）；序列=PARTIAL → FULL → PARTIAL → NONE → PARTIAL | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-364390148393 | KNOWN | 0x82 | UI_tripPlanning / UI_requestActiveBatteryHeating | UI_tripPlanning / UI_requestActiveBatteryHeating | 稳定性=CONSTANT；变化次数=0；最小值=0.0；最大值=0.0；序列=0 | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-4A197BB1EE53 | KNOWN | 0x381 | VCFRONT_logging1Hz / VCFRONT_passiveCoolingState | VCFRONT_logging1Hz / VCFRONT_passiveCoolingState | 稳定性=CONSTANT；变化次数=0；最小值=0.0；最大值=0.0；序列=0 | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| OBS-0005 | RESIDUAL | 0x108 | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=11311 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |
| OBS-0012 | UNKNOWN | 0x128 | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=9 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |

### C. 为什么进入输入（DBC REFERENCE METADATA — 仅供参考，不是 Evidence）

- `SO-2BAA1DECBE96`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["THERMAL"], "domain_terms": ["heat", "thermal"], "planned_phase_refs": [], "role_terms": ["status", "target"]}`。不据此确认 Semantic Role。
- `SO-C8661259C0DA`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["THERMAL"], "domain_terms": ["cool", "thermal"], "planned_phase_refs": [], "role_terms": ["status", "target"]}`。不据此确认 Semantic Role。
- `SO-7717801FE8E8`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["THERMAL"], "domain_terms": ["heat", "heating"], "planned_phase_refs": ["PP-STOP"], "role_terms": ["status"]}`。不据此确认 Semantic Role。
- `SO-BC7D879CB5FA`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["THERMAL"], "domain_terms": ["cool", "heat"], "planned_phase_refs": ["PP-STOP"], "role_terms": ["request"]}`。不据此确认 Semantic Role。
- `SO-364390148393`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": [], "domain_concepts": ["THERMAL"], "domain_terms": ["heat", "heating"], "planned_phase_refs": [], "role_terms": ["request"]}`。不据此确认 Semantic Role。
- `SO-4A197BB1EE53`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": [], "domain_concepts": ["THERMAL"], "domain_terms": ["cool", "cooling"], "planned_phase_refs": [], "role_terms": ["state"]}`。不据此确认 Semantic Role。
- `OBS-0005`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": ["PP-STOP"], "role_terms": []}`。不据此确认 Semantic Role。
- `OBS-0012`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": ["PP-STOP"], "role_terms": []}`。不据此确认 Semantic Role。

### D. LLM 获得的 Structured Context

- `SO-2BAA1DECBE96` identity_hint：`{"bus_key": "ch1:0x312", "dbc_name_hint": "BMS_inletActiveHeatTargetT", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "BMS_thermalStatus", "semantic_validation_state": "UNVALIDATED", "unit": "DegC"}`
- `SO-2BAA1DECBE96` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 9, "change_count": 598, "first_change_time_s": 0.9913, "last_change_time_s": 299.4974, "stability_class": "DYNAMIC", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-2BAA1DECBE96` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-2BAA1DECBE96` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-2BAA1DECBE96` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-C8661259C0DA` identity_hint：`{"bus_key": "ch1:0x312", "dbc_name_hint": "BMS_inletActiveCoolTargetT", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "BMS_thermalStatus", "semantic_validation_state": "UNVALIDATED", "unit": "DegC"}`
- `SO-C8661259C0DA` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 12, "change_count": 598, "first_change_time_s": 0.9913, "last_change_time_s": 299.4974, "stability_class": "DYNAMIC", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-C8661259C0DA` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-C8661259C0DA` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-C8661259C0DA` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-7717801FE8E8` identity_hint：`{"bus_key": "ch1:0x2E1", "dbc_name_hint": "VCFRONT_isActiveHeatingBattery", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "VCFRONT_status", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-7717801FE8E8` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 2, "first_change_time_s": 141.2739, "last_change_time_s": 248.3204, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-7717801FE8E8` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-7717801FE8E8` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-7717801FE8E8` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-BC7D879CB5FA` identity_hint：`{"bus_key": "ch1:0x241", "dbc_name_hint": "VCFRONT_wasteHeatRequestType", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "VCFRONT_coolant", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-BC7D879CB5FA` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 3, "change_count": 4, "first_change_time_s": 141.3329, "last_change_time_s": 255.3398, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-BC7D879CB5FA` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-BC7D879CB5FA` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-BC7D879CB5FA` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-364390148393` identity_hint：`{"bus_key": "ch1:0x82", "dbc_name_hint": "UI_requestActiveBatteryHeating", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "UI_tripPlanning", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-364390148393` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 1, "change_count": 0, "first_change_time_s": null, "last_change_time_s": null, "stability_class": "CONSTANT", "tags": []}`
- `SO-364390148393` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-364390148393` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-364390148393` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-4A197BB1EE53` identity_hint：`{"bus_key": "ch1:0x381", "dbc_name_hint": "VCFRONT_passiveCoolingState", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "VCFRONT_logging1Hz", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-4A197BB1EE53` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 1, "change_count": 0, "first_change_time_s": null, "last_change_time_s": null, "stability_class": "CONSTANT", "tags": []}`
- `SO-4A197BB1EE53` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-4A197BB1EE53` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-4A197BB1EE53` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0005` identity_hint：`{"bus_key": "ch1:0x108", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0005` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 133, "change_count": 11311, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "UNNAMED_ACTIVITY"]}`
- `OBS-0005` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0005` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0005` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0012` identity_hint：`{"bus_key": "ch1:0x128", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0012` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 5, "change_count": 9, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "LOW_CARDINALITY", "UNNAMED_ACTIVITY"]}`
- `OBS-0012` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0012` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0012` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`

### E. 精确输入追溯

- Question：`/semantic_evidence_questions/11`
- Per-question evidence：`/per_question_evidence/11`
- Intent：`/semantic_search_intents/11` (`SSI-ER-12`)
- Retrieval result：`/retrieval_results/11`
- Observation objects：`/observations/47` → `SO-2BAA1DECBE96`, `/observations/48` → `SO-C8661259C0DA`, `/observations/49` → `SO-7717801FE8E8`, `/observations/50` → `SO-BC7D879CB5FA`, `/observations/51` → `SO-364390148393`, `/observations/52` → `SO-4A197BB1EE53`, `/observations/7` → `OBS-0005`, `/observations/10` → `OBS-0012`
- Observation contexts：`/observation_contexts/4` → `SO-2BAA1DECBE96`, `/observation_contexts/3` → `SO-C8661259C0DA`, `/observation_contexts/43` → `SO-7717801FE8E8`, `/observation_contexts/48` → `SO-BC7D879CB5FA`, `/observation_contexts/39` → `SO-364390148393`, `/observation_contexts/44` → `SO-4A197BB1EE53`, `/observation_contexts/54` → `OBS-0005`, `/observation_contexts/56` → `OBS-0012`

## ER-13 — Identify protection monitoring, limiting action, stop request, and safe shutdown without inventing fault causes

### A. 语义目标

- ER：`ER-13`
- Control Tree Reference：`CT-DCFC-08, CT-DCFC-10, CT-DCFC-14, CT-DCFC-15`
- Semantic Evidence Question：Identify protection monitoring, limiting action, stop request, and safe shutdown without inventing fault causes.
- Sufficiency / Semantic Boundary：Protection interpretation requires applicable safety and fault-state evidence.
- Candidate Role（未确认）：`CAPABILITY, REQUEST, STATE`
- Forbidden Substitution：`ACTUAL, PERMISSION`
- Collection Script / Planned Procedure Context：`PP-CHARGE-OBSERVE`（observe EVSE and Pack voltage current power capability state and thermal context；150–210 s；PLANNED_TIME）; `PP-STEADY-HOLD`（observe a conditional short stable interval if naturally available；210–240 s；PLANNED_TIME）; `PP-STOP`（request one normal stop if charging has not already ended；240–270 s；PLANNED_TIME）; `PP-SAFE-EXIT`（confirm output stopped and lock released before disconnecting；270–300 s；PLANNED_TIME）
- 时间边界：`PLANNED_TIME_IS_NOT_OBSERVED_EVENT_TIME`

### B. 实际送入 LLM 的 Observation

| Observation | Space | CAN ID / Bus | Message / Signal | DBC 参考 | ASC 实际行为 | Retrieval Provenance |
|---|---|---|---|---|---|---|
| SO-4AA492D64A9C | KNOWN | 0x214 | FC_status / FC_voltageLimitAchieved | FC_status / FC_voltageLimitAchieved | 稳定性=CONSTANT；变化次数=0；最小值=0.0；最大值=0.0；序列=0 | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-31D612FA2BA9 | KNOWN | 0x25D | CP_status / CP_vehicleUnlockRequest | CP_status / CP_vehicleUnlockRequest | 稳定性=LOW_CARDINALITY；变化次数=12；最小值=0.0；最大值=1.0；首次变化=41.0186 s（CAN Observed Time）；末次变化=278.435 s（CAN Observed Time）；序列=1 → 0 → 1 → 0 → 1 → 0 → 1 → 0 … | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-39C18ABF3E3C | KNOWN | 0x21D | CP_evseStatus / CP_stopChargeRequest | CP_evseStatus / CP_stopChargeRequest | 稳定性=LOW_CARDINALITY；变化次数=12；最小值=0.0；最大值=1.0；首次变化=39.7192 s（CAN Observed Time）；末次变化=273.5338 s（CAN Observed Time）；序列=0 → 1 → 0 → 1 → 0 → 1 → 0 → 1 … | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-5772080DA750 | KNOWN | 0x214 | FC_status / FC_powerLimitAchieved | FC_status / FC_powerLimitAchieved | 稳定性=CONSTANT；变化次数=0；最小值=0.0；最大值=0.0；序列=0 | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-61CF5F025B68 | KNOWN | 0x214 | FC_status / FC_currentLimitAchieved | FC_status / FC_currentLimitAchieved | 稳定性=CONSTANT；变化次数=0；最小值=0.0；最大值=0.0；序列=0 | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-6A427DF5AFB4 | KNOWN | 0x333 | UI_chargeRequest / UI_acChargeCurrentLimit | UI_chargeRequest / UI_acChargeCurrentLimit / unit=A / enum={"127": "SNA"} | 稳定性=CONSTANT；变化次数=0；最小值=16.0；最大值=16.0；序列=16 | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| OBS-0278 | UNKNOWN | 0x53F | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=6 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |
| OBS-0005 | RESIDUAL | 0x108 | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=11311 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |

### C. 为什么进入输入（DBC REFERENCE METADATA — 仅供参考，不是 Evidence）

- `SO-4AA492D64A9C`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": [], "domain_concepts": ["PROTECTION"], "domain_terms": ["limit"], "planned_phase_refs": ["PP-SAFE-EXIT"], "role_terms": ["limit", "status"]}`。不据此确认 Semantic Role。
- `SO-31D612FA2BA9`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["STOP"], "domain_terms": ["unlock"], "planned_phase_refs": ["PP-SAFE-EXIT"], "role_terms": ["request", "status"]}`。不据此确认 Semantic Role。
- `SO-39C18ABF3E3C`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["STOP"], "domain_terms": ["stop"], "planned_phase_refs": ["PP-SAFE-EXIT"], "role_terms": ["request", "status"]}`。不据此确认 Semantic Role。
- `SO-5772080DA750`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": [], "domain_concepts": ["PROTECTION"], "domain_terms": ["limit"], "planned_phase_refs": ["PP-SAFE-EXIT"], "role_terms": ["limit", "status"]}`。不据此确认 Semantic Role。
- `SO-61CF5F025B68`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": [], "domain_concepts": ["PROTECTION"], "domain_terms": ["limit"], "planned_phase_refs": ["PP-SAFE-EXIT"], "role_terms": ["limit", "status"]}`。不据此确认 Semantic Role。
- `SO-6A427DF5AFB4`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": [], "domain_concepts": ["PROTECTION"], "domain_terms": ["limit"], "planned_phase_refs": ["PP-SAFE-EXIT"], "role_terms": ["limit", "request"]}`。不据此确认 Semantic Role。
- `OBS-0278`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": ["PP-CHARGE-OBSERVE", "PP-SAFE-EXIT"], "role_terms": []}`。不据此确认 Semantic Role。
- `OBS-0005`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": ["PP-STOP"], "role_terms": []}`。不据此确认 Semantic Role。

### D. LLM 获得的 Structured Context

- `SO-4AA492D64A9C` identity_hint：`{"bus_key": "ch1:0x214", "dbc_name_hint": "FC_voltageLimitAchieved", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "FC_status", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-4AA492D64A9C` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 1, "change_count": 0, "first_change_time_s": null, "last_change_time_s": null, "stability_class": "CONSTANT", "tags": []}`
- `SO-4AA492D64A9C` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-PORT-OPEN", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-4AA492D64A9C` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-4AA492D64A9C` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-31D612FA2BA9` identity_hint：`{"bus_key": "ch1:0x25D", "dbc_name_hint": "CP_vehicleUnlockRequest", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_status", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-31D612FA2BA9` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 12, "first_change_time_s": 41.0186, "last_change_time_s": 278.435, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-31D612FA2BA9` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-CONNECT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-31D612FA2BA9` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-31D612FA2BA9` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-39C18ABF3E3C` identity_hint：`{"bus_key": "ch1:0x21D", "dbc_name_hint": "CP_stopChargeRequest", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_evseStatus", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-39C18ABF3E3C` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 12, "first_change_time_s": 39.7192, "last_change_time_s": 273.5338, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-39C18ABF3E3C` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-PORT-OPEN", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-39C18ABF3E3C` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-39C18ABF3E3C` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-5772080DA750` identity_hint：`{"bus_key": "ch1:0x214", "dbc_name_hint": "FC_powerLimitAchieved", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "FC_status", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-5772080DA750` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 1, "change_count": 0, "first_change_time_s": null, "last_change_time_s": null, "stability_class": "CONSTANT", "tags": []}`
- `SO-5772080DA750` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-PORT-OPEN", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-5772080DA750` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-5772080DA750` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-61CF5F025B68` identity_hint：`{"bus_key": "ch1:0x214", "dbc_name_hint": "FC_currentLimitAchieved", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "FC_status", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-61CF5F025B68` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 1, "change_count": 0, "first_change_time_s": null, "last_change_time_s": null, "stability_class": "CONSTANT", "tags": []}`
- `SO-61CF5F025B68` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-PORT-OPEN", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-61CF5F025B68` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-61CF5F025B68` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-6A427DF5AFB4` identity_hint：`{"bus_key": "ch1:0x333", "dbc_name_hint": "UI_acChargeCurrentLimit", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "UI_chargeRequest", "semantic_validation_state": "UNVALIDATED", "unit": "A"}`
- `SO-6A427DF5AFB4` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 1, "change_count": 0, "first_change_time_s": null, "last_change_time_s": null, "stability_class": "CONSTANT", "tags": []}`
- `SO-6A427DF5AFB4` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-6A427DF5AFB4` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-6A427DF5AFB4` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0278` identity_hint：`{"bus_key": "ch1:0x53F", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0278` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 6, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "LOW_CARDINALITY", "UNNAMED_ACTIVITY"]}`
- `OBS-0278` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-CHARGE-OBSERVE", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0278` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0278` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0005` identity_hint：`{"bus_key": "ch1:0x108", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0005` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 133, "change_count": 11311, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "UNNAMED_ACTIVITY"]}`
- `OBS-0005` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0005` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0005` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`

### E. 精确输入追溯

- Question：`/semantic_evidence_questions/12`
- Per-question evidence：`/per_question_evidence/12`
- Intent：`/semantic_search_intents/12` (`SSI-ER-13`)
- Retrieval result：`/retrieval_results/12`
- Observation objects：`/observations/53` → `SO-4AA492D64A9C`, `/observations/54` → `SO-31D612FA2BA9`, `/observations/55` → `SO-39C18ABF3E3C`, `/observations/56` → `SO-5772080DA750`, `/observations/57` → `SO-61CF5F025B68`, `/observations/58` → `SO-6A427DF5AFB4`, `/observations/44` → `OBS-0278`, `/observations/7` → `OBS-0005`
- Observation contexts：`/observation_contexts/25` → `SO-4AA492D64A9C`, `/observation_contexts/21` → `SO-31D612FA2BA9`, `/observation_contexts/20` → `SO-39C18ABF3E3C`, `/observation_contexts/24` → `SO-5772080DA750`, `/observation_contexts/23` → `SO-61CF5F025B68`, `/observation_contexts/37` → `SO-6A427DF5AFB4`, `/observation_contexts/61` → `OBS-0278`, `/observation_contexts/54` → `OBS-0005`

## ER-14 — Describe controlled stop across Request, EVSE Actual, Pack Actual, high-voltage path, communication closeout, and safe unlock

### A. 语义目标

- ER：`ER-14`
- Control Tree Reference：`CT-DCFC-01, CT-DCFC-02, CT-DCFC-03, CT-DCFC-04, CT-DCFC-05, CT-DCFC-06, CT-DCFC-07, CT-DCFC-08, CT-DCFC-09, CT-DCFC-10, CT-DCFC-11, CT-DCFC-12, CT-DCFC-13, CT-DCFC-14, CT-DCFC-15`
- Semantic Evidence Question：Describe controlled stop across Request, EVSE Actual, Pack Actual, high-voltage path, communication closeout, and safe unlock.
- Sufficiency / Semantic Boundary：CAN state time is not human action time, and a missing initiator remains an evidence gap.
- Candidate Role（未确认）：`REQUEST, ACTUAL, STATE`
- Forbidden Substitution：`CAPABILITY, PERMISSION`
- Collection Script / Planned Procedure Context：`PP-PORT-OPEN`（open charge port without connecting；20–40 s；PLANNED_TIME）; `PP-CONNECT`（connect charging interface and record recognition and locking when independently observed；40–60 s；PLANNED_TIME）; `PP-AUTH-START`（perform authorization and request charging start; actual timing may vary；60–120 s；PLANNED_TIME）; `PP-ESTABLISH`（check whether charging actually established using independent vehicle and EVSE evidence；120–150 s；PLANNED_TIME）; `PP-CHARGE-OBSERVE`（observe EVSE and Pack voltage current power capability state and thermal context；150–210 s；PLANNED_TIME）; `PP-STEADY-HOLD`（observe a conditional short stable interval if naturally available；210–240 s；PLANNED_TIME）; `PP-STOP`（request one normal stop if charging has not already ended；240–270 s；PLANNED_TIME）; `PP-SAFE-EXIT`（confirm output stopped and lock released before disconnecting；270–300 s；PLANNED_TIME）
- 时间边界：`PLANNED_TIME_IS_NOT_OBSERVED_EVENT_TIME`

### B. 实际送入 LLM 的 Observation

| Observation | Space | CAN ID / Bus | Message / Signal | DBC 参考 | ASC 实际行为 | Retrieval Provenance |
|---|---|---|---|---|---|---|
| SO-7BB7F570959A | KNOWN | 0x21D | CP_evseStatus / CP_proximity | CP_evseStatus / CP_proximity / enum={"0": "SNA", "1": "DISCONNECTED", "2": "UNLATCHED", "3": "LATCHED"} | 稳定性=LOW_CARDINALITY；变化次数=2；首次变化=39.7192 s（CAN Observed Time）；末次变化=273.5338 s（CAN Observed Time）；序列=SNA → DISCONNECTED → SNA | DIRECT_INTENT_RETRIEVAL; SEMANTIC_CONTEXT_COMPATIBLE |
| SO-C6316DC7735B | KNOWN | 0x359 | VCSEC_BLEDeviceStatus / VCSEC_mobileAppVersion | VCSEC_BLEDeviceStatus / VCSEC_mobileAppVersion | 稳定性=DYNAMIC；变化次数=2192；最小值=0.0；最大值=246.0；首次变化=0.1073 s（CAN Observed Time）；末次变化=299.7283 s（CAN Observed Time）；序列=0 → 60 → 0 → 93 → 141 → 234 → 0 → 238 … | DIRECT_INTENT_RETRIEVAL; BEHAVIOR_EXPLORATORY |
| SO-30E936829754 | KNOWN | 0x1F9 | VCSEC_requests / VCSEC_chargePortRequest | VCSEC_requests / VCSEC_chargePortRequest / enum={"0": "NONE", "1": "OPEN", "2": "CLOSE", "3": "SNA"} | 稳定性=LOW_CARDINALITY；变化次数=2；首次变化=268.6751 s（CAN Observed Time）；末次变化=268.9751 s（CAN Observed Time）；序列=NONE → OPEN → NONE | DIRECT_INTENT_RETRIEVAL; PROCEDURE_ALIGNED_DOMAIN_HINT |
| SO-DCF64D235226 | KNOWN | 0x7AA | HVP_debugMessage / HVP_gpioCpLatchEnable | HVP_debugMessage / HVP_gpioCpLatchEnable | 稳定性=LOW_CARDINALITY；变化次数=2；最小值=0.0；最大值=1.0；首次变化=135.1584 s（CAN Observed Time）；末次变化=247.1598 s（CAN Observed Time）；序列=0 → 1 → 0 | DIRECT_INTENT_RETRIEVAL; PROCEDURE_ALIGNED_DOMAIN_HINT |
| SO-330F3936C51C | KNOWN | 0x2E1 | VCFRONT_status / VCFRONT_reverseBatteryFault | VCFRONT_status / VCFRONT_reverseBatteryFault | 稳定性=LOW_CARDINALITY；变化次数=16；最小值=0.0；最大值=1.0；首次变化=142.298 s（CAN Observed Time）；末次变化=157.3709 s（CAN Observed Time）；序列=0 → 1 → 0 → 1 → 0 → 1 → 0 → 1 … | DIRECT_INTENT_RETRIEVAL; BEHAVIOR_EXPLORATORY |
| SO-31D612FA2BA9 | KNOWN | 0x25D | CP_status / CP_vehicleUnlockRequest | CP_status / CP_vehicleUnlockRequest | 稳定性=LOW_CARDINALITY；变化次数=12；最小值=0.0；最大值=1.0；首次变化=41.0186 s（CAN Observed Time）；末次变化=278.435 s（CAN Observed Time）；序列=1 → 0 → 1 → 0 → 1 → 0 → 1 → 0 … | DIRECT_INTENT_RETRIEVAL; BEHAVIOR_EXPLORATORY |
| OBS-0005 | RESIDUAL | 0x108 | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=11311 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |
| OBS-0012 | UNKNOWN | 0x128 | — / UNNAMED | NONE / UNKNOWN / NOT DEFINED | 变化次数=9 | DIRECT_INTENT_RETRIEVAL; UNNAMED_BEHAVIOR_CONTEXT |

### C. 为什么进入输入（DBC REFERENCE METADATA — 仅供参考，不是 Evidence）

- `SO-7BB7F570959A`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`SEMANTIC_CONTEXT_COMPATIBLE`；retrieval_reasons=`SEMANTIC_CONTEXT_COMPATIBLE`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["ELECTRICAL", "EVSE_BOUNDARY", "INTERFACE"], "domain_terms": ["evse", "proximity"], "planned_phase_refs": ["PP-PORT-OPEN", "PP-SAFE-EXIT"], "role_terms": ["status"]}`。不据此确认 Semantic Role。
- `SO-C6316DC7735B`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`BEHAVIOR_EXPLORATORY`；retrieval_reasons=`BEHAVIOR_EXPLORATORY`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["COMMUNICATION"], "domain_terms": ["version"], "planned_phase_refs": ["PP-SAFE-EXIT"], "role_terms": ["status"]}`。不据此确认 Semantic Role。
- `SO-30E936829754`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`PROCEDURE_ALIGNED_DOMAIN_HINT`；retrieval_reasons=`PROCEDURE_ALIGNED_DOMAIN_HINT`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["ELECTRICAL", "INTERFACE"], "domain_terms": ["charge", "port"], "planned_phase_refs": ["PP-STOP"], "role_terms": ["request"]}`。不据此确认 Semantic Role。
- `SO-DCF64D235226`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`PROCEDURE_ALIGNED_DOMAIN_HINT`；retrieval_reasons=`PROCEDURE_ALIGNED_DOMAIN_HINT`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["HV_PATH", "INTERFACE"], "domain_terms": ["hv", "latch"], "planned_phase_refs": ["PP-ESTABLISH", "PP-STOP"], "role_terms": []}`。不据此确认 Semantic Role。
- `SO-330F3936C51C`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`BEHAVIOR_EXPLORATORY`；retrieval_reasons=`BEHAVIOR_EXPLORATORY`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["ELECTRICAL", "PROTECTION", "VEHICLE_BOUNDARY"], "domain_terms": ["battery", "fault"], "planned_phase_refs": ["PP-CHARGE-OBSERVE", "PP-ESTABLISH"], "role_terms": ["status"]}`。不据此确认 Semantic Role。
- `SO-31D612FA2BA9`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`BEHAVIOR_EXPLORATORY`；retrieval_reasons=`BEHAVIOR_EXPLORATORY`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY"], "domain_concepts": ["INTERFACE", "STOP", "VEHICLE_BOUNDARY"], "domain_terms": ["unlock", "vehicle"], "planned_phase_refs": ["PP-CONNECT", "PP-SAFE-EXIT"], "role_terms": ["request", "status"]}`。不据此确认 Semantic Role。
- `OBS-0005`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": ["PP-ESTABLISH", "PP-STOP"], "role_terms": []}`。不据此确认 Semantic Role。
- `OBS-0012`：provenance=`DIRECT_INTENT_RETRIEVAL`；eligibility_path=`UNNAMED_BEHAVIOR_CONTEXT`；retrieval_reasons=`UNNAMED_BEHAVIOR_CONTEXT`；context_matches=`{"behavior_tags": ["DYNAMIC", "LOW_CARDINALITY", "UNNAMED_ACTIVITY"], "domain_concepts": [], "domain_terms": [], "planned_phase_refs": ["PP-ESTABLISH", "PP-STOP"], "role_terms": []}`。不据此确认 Semantic Role。

### D. LLM 获得的 Structured Context

- `SO-7BB7F570959A` identity_hint：`{"bus_key": "ch1:0x21D", "dbc_name_hint": "CP_proximity", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_evseStatus", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-7BB7F570959A` behavior：`{"anomaly_flags": ["SNA_PRESENT"], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 2, "first_change_time_s": 39.7192, "last_change_time_s": 273.5338, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-7BB7F570959A` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-PORT-OPEN", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-7BB7F570959A` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-7BB7F570959A` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-C6316DC7735B` identity_hint：`{"bus_key": "ch1:0x359", "dbc_name_hint": "VCSEC_mobileAppVersion", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "VCSEC_BLEDeviceStatus", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-C6316DC7735B` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 12, "change_count": 2192, "first_change_time_s": 0.1073, "last_change_time_s": 299.7283, "stability_class": "DYNAMIC", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-C6316DC7735B` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-INITIAL", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-C6316DC7735B` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-C6316DC7735B` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-30E936829754` identity_hint：`{"bus_key": "ch1:0x1F9", "dbc_name_hint": "VCSEC_chargePortRequest", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "VCSEC_requests", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-30E936829754` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 2, "first_change_time_s": 268.6751, "last_change_time_s": 268.9751, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-30E936829754` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-30E936829754` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-30E936829754` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-DCF64D235226` identity_hint：`{"bus_key": "ch1:0x7AA", "dbc_name_hint": "HVP_gpioCpLatchEnable", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "HVP_debugMessage", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-DCF64D235226` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 2, "first_change_time_s": 135.1584, "last_change_time_s": 247.1598, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-DCF64D235226` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-DCF64D235226` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-DCF64D235226` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-330F3936C51C` identity_hint：`{"bus_key": "ch1:0x2E1", "dbc_name_hint": "VCFRONT_reverseBatteryFault", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "VCFRONT_status", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-330F3936C51C` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 16, "first_change_time_s": 142.298, "last_change_time_s": 157.3709, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-330F3936C51C` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-CHARGE-OBSERVE", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-330F3936C51C` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-330F3936C51C` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `SO-31D612FA2BA9` identity_hint：`{"bus_key": "ch1:0x25D", "dbc_name_hint": "CP_vehicleUnlockRequest", "dbc_source": "/Users/hwy/codex_work/TeslaCanPython/input/tesla_model3_ONYX.dbc", "message_name_hint": "CP_status", "semantic_validation_state": "UNVALIDATED", "unit": ""}`
- `SO-31D612FA2BA9` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 2, "change_count": 12, "first_change_time_s": 41.0186, "last_change_time_s": 278.435, "stability_class": "LOW_CARDINALITY", "tags": ["DYNAMIC", "LOW_CARDINALITY"]}`
- `SO-31D612FA2BA9` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-CONNECT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-SAFE-EXIT", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `SO-31D612FA2BA9` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `SO-31D612FA2BA9` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0005` identity_hint：`{"bus_key": "ch1:0x108", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0005` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 133, "change_count": 11311, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "UNNAMED_ACTIVITY"]}`
- `OBS-0005` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0005` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0005` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`
- `OBS-0012` identity_hint：`{"bus_key": "ch1:0x128", "dbc_name_hint": null, "dbc_source": null, "message_name_hint": null, "semantic_validation_state": "UNVALIDATED", "unit": null}`
- `OBS-0012` behavior：`{"anomaly_flags": [], "availability": "FROZEN_AGGREGATE_ONLY", "cardinality": 5, "change_count": 9, "first_change_time_s": null, "last_change_time_s": null, "stability_class": null, "tags": ["DYNAMIC", "LOW_CARDINALITY", "UNNAMED_ACTIVITY"]}`
- `OBS-0012` planned phase alignment：`[{"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-ESTABLISH", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}, {"basis": "CHANGE_ENDPOINT_IN_PLANNED_WINDOW", "planned_phase_ref": "PP-STOP", "time_type": "PLANNED_TIME_CONTEXT_ONLY"}]`
- `OBS-0012` Phase Feature：`OBSERVED_EVENT_PHASE_UNAVAILABLE`
- `OBS-0012` Relationship Feature：`TRACE_STORE_UNAVAILABLE, RELATIONSHIP_FEATURE_UNAVAILABLE`

### E. 精确输入追溯

- Question：`/semantic_evidence_questions/13`
- Per-question evidence：`/per_question_evidence/13`
- Intent：`/semantic_search_intents/13` (`SSI-ER-14`)
- Retrieval result：`/retrieval_results/13`
- Observation objects：`/observations/4` → `SO-7BB7F570959A`, `/observations/59` → `SO-C6316DC7735B`, `/observations/9` → `SO-30E936829754`, `/observations/60` → `SO-DCF64D235226`, `/observations/61` → `SO-330F3936C51C`, `/observations/54` → `SO-31D612FA2BA9`, `/observations/7` → `OBS-0005`, `/observations/10` → `OBS-0012`
- Observation contexts：`/observation_contexts/19` → `SO-7BB7F570959A`, `/observation_contexts/53` → `SO-C6316DC7735B`, `/observation_contexts/52` → `SO-30E936829754`, `/observation_contexts/29` → `SO-DCF64D235226`, `/observation_contexts/45` → `SO-330F3936C51C`, `/observation_contexts/21` → `SO-31D612FA2BA9`, `/observation_contexts/54` → `OBS-0005`, `/observation_contexts/56` → `OBS-0012`

## LLM 没有收到什么

以下边界可由冻结输入直接证明：

- 完整 synchronized cross-signal Relationship Feature：未提供；冻结输入标记为 `RELATIONSHIP_FEATURE_UNAVAILABLE`。
- Observed Human Event Timestamp：未提供；只有 planned procedure context，且明确为 `PLANNED_TIME_IS_NOT_OBSERVED_EVENT_TIME`。
- Frozen Trace Store / CAN region detail：未提供；相关 context 标记为 `TRACE_STORE_UNAVAILABLE` / `CAN_REGION_DETAIL_UNAVAILABLE`。
- 原采集没有独立记录的车外物理量或人工操作事实：未由 DBC 名称、planned time 或历史报告补造。
- External Golden Review Decision：不在 `semantic_reasoning_input.json` 中。
- Approved Evidence、Assessment、Final Report Conclusion：不在该 Pre-call Object 中。
- Phase 3B.2.4 Review Packet：是后生成的下游展示产物，不在冻结 Reasoning Input 中。

## 审计边界

本产物只呈现冻结输入，不新增 ranking、Signal whitelist、Semantic Role、relationship、Finding 或 review decision。所有 DBC 内容均为 Reference Metadata。
