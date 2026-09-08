# Phase 3B.2.5 完成报告

## 修改文件

- `src/pre_llm_input_audit.py`：新增只读、确定性的 LLM 前分析输入审计生成器。
- `tests/test_pre_llm_input_audit.py`：新增冻结性、输入闭包、来源空间、不可用特征与禁止回流测试。
- `output/TM3-015/pipeline_v3/20260908-phase3b2_3-context-replay-v5/TM3-015_pre_llm_analysis_input_audit.md`：主要中文审计产物。
- `output/TM3-015/pipeline_v3/20260908-phase3b2_3-context-replay-v5/TM3-015_pre_llm_analysis_input_audit.json`：机器伴随元数据。
- `output/TM3-015/pipeline_v3/20260908-phase3b2_3-context-replay-v5/Phase3B.2.5_completion_report.md`：本报告。

未修改 Retrieval、Semantic Evidence Question、Observation Context Adapter、Reasoning、Finding、Evidence Mapping 或 Phase 3B.2.4 产物。

## 使用的冻结基线

- Frozen Run：`20260908-phase3b2_3-context-replay-v5`
- Reasoning Package：`TM3-015-reasoning-f2f9203de6d5494d`
- Package Hash：`1da118c87ee9299a4eb8e84a697edf652edec81741ad07dee9a82a76f5a1ad15`
- ER / Semantic Question：14 / 14
- Retrieval 行：108
- Unique Observation：62
- Known / Residual / Unknown：54 / 3 / 5

## Source Hash 前后校验

以下九个只读源产物在生成前后 SHA-256 完全相同：

| Source Artifact | SHA-256（前后相同） |
|---|---|
| `semantic_reasoning_input.json` | `4c8b747fa35ddc1401cc0e986b7c7c5491b233e002fd00594283438979d29af7` |
| `semantic_reasoning_output.json` | `ff72bfa0b4a146425ecf70c73889f8c8191b09d27ef58ce35a2c74d0cc23364b` |
| `evidence_mapping_draft.json` | `7464e8364f6179e02fadefcd89d84d07078e26ec7972e103c2b4dcea3edbe22e` |
| `runtime_audit.json` | `706698043cae895a893c386e07a5a0f2c17e069eefe368586aae60d632f2f072` |
| `experiment_procedure.json` | `1d3bd2a725c985df8c27099815a7d3d0681365956b1f6343f5f44efae5759eaa` |
| `semantic_evidence_questions.json` | `f498acd955f00a235a346673f73c9f177fa68d764beb57d155e38f8683345b02` |
| `semantic_search_intents.json` | `b8e1b659b96b9d572f2ef3a0892e51a6e7ce9fdcc6dfb544a71a46a87d358127` |
| `semantic_retrieval_results.json` | `2668fca5ca4c7746d86b78ba327f3460fbaacf910b5ac7181e4f7b58aa2887e2` |
| `observation_contexts.json` | `1a9f4867c8bfebdae44fa7d1f17794486d3c9efd831d1c9d02e3fc3ba7df8cb8` |

完整的 before/after 哈希也保存在机器伴随 JSON 中。

## Pre-LLM 输入可见性结果

主审计产物逐 ER 展示了：

- 冻结 Semantic Evidence Question、Sufficiency Boundary、Control Tree refs；
- 实际关联的 planned procedure phase 及其 `action`；
- 实际送入该 ER 的 direct/cross/global Observation 引用；
- Known、Residual、Unknown；
- 冻结 ASC aggregate behavior；
- DBC Reference Metadata，并明确其不是 Evidence；
- eligibility path、retrieval reason、context match；
- `OBSERVED_EVENT_PHASE_UNAVAILABLE`、`TRACE_STORE_UNAVAILABLE`、`RELATIONSHIP_FEATURE_UNAVAILABLE`；
- 到 `semantic_reasoning_input.json` 的精确 JSON Pointer。

External Golden Review Decision、Approved Evidence、Assessment、最终报告结论与 Phase 3B.2.4 Review Packet 均未进入冻结 Reasoning Input。

## Exact Final LLM Payload 与模型配置

无法恢复或证明 Exact Final LLM Payload。

冻结运行未保存可核验的 System / Developer Instruction、最终 request envelope，也没有可证明与当时调用完全相同的确定性 Call Builder。因此只把 `semantic_reasoning_input.json` 根对象作为最接近调用边界的权威 Pre-call Object，没有生成或冒充 Exact Payload。

- Model Provider：冻结运行中未记录
- Model Name：冻结运行中未记录
- Model Identity：`codex-recovery-session`
- Reasoning / Effort：冻结运行中未记录
- 冻结运行 Reasoning Call：1
- 冻结运行 Follow-up Call：0
- 本次审计 LLM Call：0

## 测试

执行：

- `PYTHONPYCACHEPREFIX=/tmp/tm3_prellm_pyc .venv/bin/python -m py_compile src/pre_llm_input_audit.py`
- `.venv/bin/python -m unittest tests.test_pre_llm_input_audit`
- `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'`
- `git diff --check`

结果：聚焦测试 2/2 PASS；全量测试 79/79 PASS；`git diff --check` PASS。

聚焦测试覆盖附件要求的 16 项边界，包括所有 ER 呈现、逐 ER Observation 完全一致、三类 source space、Source/Finding/Mapping 哈希不变、不可用特征不被补算、Golden Decision 不进入输入、Exact Payload 声称受限，以及无 Approved/下游产物生成。

## 运行与停止边界

- ASC reread = NO
- ASC parse delta = 0
- Retrieval rerun = NO
- Reasoning rerun = NO
- LLM call = 0
- Finding changed = NO
- Evidence Mapping changed = NO
- Approved Evidence = NOT GENERATED
- Assessment = NOT GENERATED
- RVM = NOT RUN
- Renderer = NOT RUN
- Four documents = NOT GENERATED
- 新 Human Review Workflow = NOT CREATED

最终状态保持：`AWAITING_EVIDENCE_REVIEW`。
