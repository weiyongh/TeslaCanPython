# TeslaCanPython 当前工程状态与操作入口

> 性质：新会话的当前状态入口。  
> 更新日期：2026-09-08  
> 本文件只说明当前有效实现、状态门和继续入口；具体方法与字段合同仍以 `AGENTS.md`、`doc/methodology/`、源码、测试和冻结产物为准。

## 1. 项目当前在哪里

TeslaCanPython 同时支持正常基线采集和故障诊断，当前正式方向是：程序负责ASC全量处理、观察（Observation）生成和候选压缩；大语言模型（LLM）负责受冻结输入约束的语义分析；证据（Evidence）经验证与人工审核后才能进入证据评估（Evidence Assessment）和正式报告。

Phase 3A设计已经有对应实现。当前有效的新管线已完成：

- Phase 3B.1：正式发现（Formal Discovery）与冻结观察包（Frozen Observation Package）；
- Phase 3B.2：语义推理契约（Semantic Reasoning Contract）与证据映射（Evidence Mapping）边界；
- Phase 3B.2.1～3B.2.3：由L3/证据需求（ER）驱动的检索意图（Intent）、语义证据问题（Semantic Evidence Question）、观察上下文（Observation Context）、语义检索（Retrieval），以及直接/跨意图/全局来源追踪（direct/cross/global provenance）；
- Phase 3B.2.4：人类可读证据审核包（Evidence Review Packet）；
- Phase 3B.2.5：LLM前分析输入审计（Pre-LLM Analysis Input Audit）。

`doc/methodology/TM3_Phase3_Formal_Pipeline_Integration_Design.md`是当时的Phase 3A设计记录，其中“NOT IMPLEMENTED”描述的是设计完成时状态，不代表当前仓库仍未实现。根目录 `readme.md`主要记录早期程序入口，不作为当前Phase状态依据。

## 2. 当前有效管线（Pipeline）

正式版本化入口是 `src/formal_pipeline.py`：

```text
分析章程（Analysis Charter）
→ ASC数据准入（ASC Data Admission）
→ 正式发现（discovery-v1）
→ 完整观察包（Complete Observation Package）
→ 发现完成（DISCOVERY_COMPLETE）
→ 人工审核（Human Review）/ 明确授权继续
→ 语义证据问题 + 观察上下文 + 语义检索
  （Semantic Evidence Question + Observation Context + Retrieval）
→ 冻结推理输入（Frozen Reasoning Input）
→ 推理输入已冻结（REASONING_INPUT_FROZEN）
→ 1次有界语义推理（bounded Semantic Reasoning）
→ 结果验证（Validation）
→ 证据映射草案（Evidence Mapping Draft）
→ 等待证据审核（AWAITING_EVIDENCE_REVIEW）
→ 人工审核（Human Review）
→ 已批准证据（Approved Evidence）
→ 证据评估（Evidence Assessment）
→ 报告视图模型（Report View Model，RVM）
→ 共享报告渲染器（shared report_renderer.py）
→ 正式四件套
```

正式发现（Discovery）入口示例：

```sh
PYTHONPYCACHEPREFIX=/tmp/tm3_pycache .venv/bin/python src/formal_pipeline.py \
  --pipeline-version discovery-v1 \
  --charter input/TM3-xxx_formal_discovery_charter.json
```

默认 `legacy` 是兼容性空操作（no-op），不代表已执行正式发现。是否读取ASC、复用冻结观察，必须由用户目标和当前状态决定：要求新采集或重新执行发现时才解析ASC；只要求语义检索、语义推理、人工审核或冻结产物审计时，优先复用指定的冻结观察包（Frozen Observation Package），不得无理由重读ASC。

## 3. 主要对象与停止点

- **分析章程（Analysis Charter）**：定义实验目的、范围、允许数据源、时间策略、L3/证据需求（ER）引用；不是Signal白名单或预期答案。
- **观察包（Observation Package）**：ASC全部已解析总线键（bus-key）的冻结观察空间，包含已知区（Known）、残差区（Residual）、未知区（Unknown）、Signal摘要（Signal Summary）、原始引用（raw references）和处理去向（disposition）。DBC只参与解释、解码与覆盖连接（Coverage Join），不决定CAN观察准入。
- **候选（Candidate）**：从完整观察空间（Observation Space）压缩出的有界候选；候选上限不得删除观察。候选集合不等于完整CAN观察。
- **检索所得观察（Retrieved Observation）**：根据L3、证据需求（ER）、实验流程（Procedure）和上下文（Context）为语义推理选择的子集；不等于完整观察，也不是证据。
- **语义发现（Finding）**：LLM在冻结输入内形成的、受引用约束的语义判断或证据缺口（Evidence Gap）；不是已批准证据。
- **证据绑定草案（Evidence Binding Draft）**：观察、语义发现与证据需求（ER）之间的待审映射，只能作为人工审核候选。
- **已批准证据（Approved Evidence）**：经有效验证和人工审核后，当前实验可用于证据评估和正式报告的证据；不自动成为车型永久知识。

停止点：

- `DISCOVERY_COMPLETE`（发现完成）：已形成完整观察包；如果用户要求先审核观察，立即停止，不进入语义推理。
- `REASONING_INPUT_FROZEN`（推理输入已冻结）：语义推理输入已经冻结，但尚未产生正式推理结果。
- `AWAITING_EVIDENCE_REVIEW`（等待证据审核）：语义推理、结果验证和证据映射草案已经完成；不得自动生成已批准证据、证据评估、报告视图模型（RVM）、渲染器输入或正式四件套。
- 正式四件套只能在已批准证据和证据评估完成后，由共享的“报告视图模型 → 渲染器”（RVM → Renderer）路径生成。

## 4. 当前TM3 / Phase状态

TM3-009和TM3-010是黄金回归样本（Golden Regression Samples）；TM3-015能源链DBC适配是Signal验证黄金案例（Signal Validation Golden Case），保护边界见 `AGENTS.md`和`doc/methodology/TM3_Golden_Regression_Samples.md`。

当前Phase 3B工作实例为TM3-015：

- 当前冻结运行（run）：`output/TM3-015/pipeline_v3/20260908-phase3b2_3-context-replay-v5/`；
- 当前状态：等待证据审核（`AWAITING_EVIDENCE_REVIEW`）；
- 推理输入（Reasoning Input）、推理输出（Reasoning Output）、结果验证（Validation）、证据映射草案（Evidence Mapping Draft）、审核包（Review Packet）和LLM前输入审计（Pre-LLM Input Audit）均已存在；
- 当前证据映射（Evidence Mapping）仍为待审，不是已批准证据（Approved Evidence）；
- 未进入Phase 3B.3；
- 不得从同目录之外的历史报告或黄金答案（Golden答案）回流污染冻结推理输入。

Phase 3B.2.6A当前只能记录为：

```text
暂定 / 尚未授权（PROVISIONAL / NOT YET AUTHORIZED）

目标方向：
不依赖DBC的完整观察（DBC-independent Full Observation）
→ 确定性工程描述（Deterministic Engineering Description）
```

详细范围和验收标准尚未冻结。不得将历史会话、旧3B.2.6草案或推断升级为正式Phase规格；用户明确批准前不得执行。

## 5. L3知识源（L3 Knowledge Source）

普通工程任务使用 `knowledge/notion_l3/current/`，并按当前案例（case）只选择必要页面。Notion `新能源汽修L3学习`正式祖先路径（ancestor path）分支是唯一人工维护的权威编辑源，但不作为普通任务的默认实时读取入口。只有同步、实时核实或本地知识确实缺失时访问Notion。

## 6. 最小LLM调用审计规则

凡是需要可审计语义推理（Semantic Reasoning）的运行，至少必须保存并相互绑定：

1. **冻结输入（Frozen input）**：实际送入语义推理的完整冻结对象、包标识（package ID）、SHA-256及引用闭包。
2. **最终调用信封（Final call envelope）**：最终调用边界内的系统指令（System）、开发者指令（Developer）、用户请求（User/request），以及实际引用或内嵌的冻结输入；不能只保存调用前的近似对象并声称它是精确调用载荷（Exact Payload）。
3. **模型身份与推理强度（Model identity / effort）**：模型提供方（provider，可得时）、模型名称/身份（model name/identity）、推理强度（reasoning effort）及影响行为的调用参数；不可得字段必须明确记录为不可得。
4. **调用次数（Call count）**：首次推理（primary reasoning）、确定性补充查询（deterministic follow-up）和更新后结果（updated result）分别计数，并遵循当前契约（Contract）上限。
5. **严格盲态隔离（Strict blind isolation）**：要求严格盲态（Strict Blind）认证时，执行LLM上下文在推理前不得读取历史语义发现（Finding）、历史推理输出（Reasoning Output）、隐藏比较（Hidden Comparison）、已批准证据（Approved Evidence）、最终报告结论或预期答案（expected answer）；仅限制输出引用范围不能证明认知盲态。无法证明隔离时必须标记限制，不得宣称“严格认知盲态通过”（Strict Cognitive Blindness PASS）。

本规则不授权建设LLM调用构建器（Call Builder）、调用平台或新的智能体/上下文（Agent/Context）基础设施。

## 7. 新会话从哪里继续

1. 先读取 `AGENTS.md`和本文件。
2. 根据任务用途读取必要方法契约（Contract）和 `knowledge/notion_l3/current/`中的必要L3页面。
3. 核实用户指定TM3的输入、冻结运行（run）、运行审计（runtime audit）和当前停止状态，不按目录时间戳猜测权威运行。
4. 将用户目标映射到最窄阶段：观察（Observation）目标停在“发现完成”（`DISCOVERY_COMPLETE`）；语义（Semantic）目标必须有冻结输入（Frozen input）；证据审核（Evidence Review）目标使用待审包；没有明确授权不得越过人工审核门。
5. 用户新指令和最新实验事实优先；若与本文件状态冲突，先核实并更新状态记录，保留冲突，不静默选择历史结论。
