# TM3 Phase 3 Formal Pipeline Integration Design

**阶段：** Phase 3A（仅设计）  
**状态：** DESIGN COMPLETE / NOT IMPLEMENTED  
**目标：** 将已验证的 Discovery 与 Semantic Reasoning 以最小、可回退切片接入正式分析链；不修改本阶段任何生产代码、Evidence Plan Schema、RVM、Renderer 或 Golden Contract。

## 1. Current Pipeline Map

当前仓库不是一个统一入口，而是三类并存路径。

### 1.1 当前正式 TM3 路径

```text
实验特定 Evidence Plan Draft
        ↓
Human Review / Override
        ↓
evidence_plan_approved.csv
        ↓ 入口门
实验专用 analyze_tm3_xxx.py
        ↓ 只处理 Approved Signal 或硬编码 Signal
machine_evidence / Evidence Assessment / RVM
        ↓
实验专用 render_tm3_xxx.py
        ↓
shared report_renderer.py
        ↓
正式四件套 + Golden/结构校验
```

TM3-015 是最清楚的实例：`src/analyze_tm3_015.py` 在打开 ASC 前调用 `read_approved_csv()`，随后只遍历 `plan.signals` 解码和生成覆盖结果。TM3-007/008虽会先把原始帧装入内存或截取窗口，但语义解码、覆盖和人读证据仍以 Approved Signal 为主要准入集合。因此当前链路实际上是：

```text
Approved Signal membership
    = analysis admission
    + evidence eligibility
    + report eligibility
```

这三个职责被压在一个对象里。

### 1.2 旧实验专用路径

`src/analyze_tm3_004.py`、`src/analyze_tm3_009.py` 使用 `TARGETS`，`src/analyze_tm3_010.py` 使用 `REGISTRY`；它们直接决定读取哪些 CAN ID/Signal、计算哪些统计或进入哪些报告。这类集合同时承担已知Signal提示、分析准入和展示选择，无法代表 DBC residual 与 unknown space。

### 1.3 Phase 2.5 / 2.6 Spike 路径

```text
ASC + DBC + experiment context
        ↓
semantic_coverage_residual_discovery.run_spike
        ↓
ASC integrity / bus inventory / DBC coverage
Known Signal Summary / Residual / Unknown
Candidate Compression / raw refs
        ↓
Frozen Reasoning Input
        ↓
Semantic Reasoning Contract + validator
        ↓
Findings / ER mapping / gaps / validation proposal
```

该路径能覆盖全 bus-key，但目前明确与 Approved Plan、RVM、Renderer 和正式报告生命周期隔离。

## 2. Target Pipeline Map

```text
L3 Semantic Prior
        ↓
Analysis Charter ───────────────┐
        ↓                       │
ASC Data Admission             │
        ↓                       │
Formal Discovery Kernel        │
        ↓                       │
Observation Package            │
  ├─ Known                     │
  ├─ Residual                  │
  └─ Unknown                   │
        ↓                       │
Candidate Compression          │
        ↓                       │
Semantic Reasoning ←───────────┘
        ↓
Evidence Mapping Adapter
        ↓
Deterministic / Semantic Validation
        ↓
Human Review where required
        ↓
Approved Evidence
        ↓
Evidence Assessment + L3 Semantic Synthesis
        ↓
existing Report View Model
        ↓
existing report_renderer.py
        ↓
existing four-piece output
```

关键改变只有一个：**ASC 与全部 bus-key 先进入 Observation Space；Approval 从“数据准入门”后移为“Evidence 晋升门”。** Approved Evidence 仍是 Assessment 和正式报告引用的强门。

## 3. Constraint Bottleneck Map

| 收窄点 | 当前证据 | 影响 | Phase 3B最小处理 |
|---|---|---|---|
| Approved-before-ASC | `analyze_tm3_015.py`先读 Approved Plan，再打开ASC | 未Approved的CAN内容没有正式Observation路径 | 新入口先执行Data Admission/Discovery；旧入口保留 |
| Approved Signal循环 | TM3-015仅遍历`plan.signals`解码；TM3-007/008的覆盖同样以Approved集合为主 | DBC匹配但未Approved、Residual、Unknown被排除于机器Observation | Discovery输出独立于Approved；Approved只作用于Evidence adapter以后 |
| TARGETS / REGISTRY | TM3-004/009/010硬编码集合 | 实验知识变成全局分析边界 | 降级为Known Signal Hint/legacy adapter |
| Evidence Plan字段耦合 | Signal identity、ER、role、priority、report_position、order同表 | 研究问题、证据晋升和展示计划混合 | 概念拆分但第一切片使用adapter，不立即改CSV schema |
| Renderer Approved引用门 | `_validate()`拒绝非Approved timeline/core/coverage引用 | 若上移会压缩Observation；若保留下游则是正确安全门 | 保持不变；只接收晋升后的Approved Evidence |
| RVM构造位置不一致 | TM3-007分析器写RVM；TM3-008 renderer脚本内构造并写RVM | 分析判断与presentation assembly边界不稳定 | 第一切片只定义RVM输入契约，不迁移现有实现 |
| Follow-up重读ASC | `execute_follow_up()`重新载入DBC并遍历ASC | 不满足冻结数据、可审计盲态 | 改为对Discovery Trace Store执行固定操作 |
| Reasoning validator范围窄 | 校验引用与基本状态，但不验证完整runtime audit | 生命周期合规依赖外部人工审计 | 增加独立runtime audit validator，不扩展CoT |

## 4. Responsibility Boundary

| 阶段 | 负责 | 不负责 |
|---|---|---|
| Analysis Charter | 实验目的、用途、系统边界、主线、时间语义、允许数据源、L3 Prior引用、Evidence Requirements | Signal白名单、结论、报告布局 |
| ASC Data Admission | 文件身份/hash、格式、时间范围、通道、帧格式、只读准入、损坏行记录 | DBC语义、候选排序、Evidence判断 |
| Discovery Kernel | 全bus-key聚合、DLC、DBC Join、Known/Residual/Unknown、Signal Summary、bit/payload摘要、候选压缩、raw refs | L3映射、ER充分性、因果、Evidence批准、展示 |
| Semantic Reasoning | 基于结构化输入做语义假设、Control Tree/ER映射、替代解释、gap和最小验证请求 | 读取ASC、重算统计、批准Evidence、改L3、决定版面 |
| Evidence Mapping | 把finding/observation与ER建立可追溯关联 | 自动宣告Signal语义成立 |
| Validation | DBC/物理/时间/定量/状态机/定义冲突校验 | 把单一SUPPORTED升级为根因 |
| Human Review | 高风险语义、冲突DBC、跨边界、代理证据、model challenge的取舍 | 改写原始Observation |
| Approved Evidence | 当前实验可进入Assessment和报告的有效证据集合 | Observation全集或车型永久知识 |
| Evidence Assessment | 按ER综合有效证据，形成SUPPORTED等状态 | 重新发现Signal、决定报告结构 |
| L3 Semantic Synthesis | 事实、控制关系、基线/诊断判断、边界与建议 | 改动通用L3本体 |
| RVM | 将已完成的分析与presentation judgment组织为Renderer输入 | Evidence晋升、Signal admission、重新Assessment |
| Renderer | 忠实生成四件套并执行结构/引用/覆盖校验 | 语义推理、事件选择、DBC裁决、重要度判断 |

## 5. Evidence Plan Split

不在第一切片创建大型新框架。逻辑上将现有 Evidence Plan 拆成五个职责；物理上先用adapter读取现有CSV。

| 当前字段/对象 | 目标归属 | 决策 | 说明 |
|---|---|---|---|
| experiment_id、scope | Analysis Charter / Approval provenance | KEEP | 继续限定THIS_EXPERIMENT_ONLY |
| Evidence Requirement | Known Evidence Requirements | SPLIT | 从Signal行的字符串引用提升为Charter独立集合；旧列保留兼容 |
| signal_key、signal、message、can_id、unit | Observation identity或Evidence binding | SPLIT | Discovery产生Observation identity；Approved行保存被晋升证据引用，不再决定Observation准入 |
| suggested_role | Evidence Mapping建议 | MOVE | 来自Semantic Reasoning/adapter，不是Discovery属性 |
| suggested_priority | Evidence review | KEEP/MOVE | 仅当前实验重要度，不是Signal永久属性 |
| derivation_reason | Evidence Mapping provenance | KEEP | 应引用finding/observation/ER |
| semantic_status、confidence、uncertainty_flags | Validation/Mapping | SPLIT | Observation保留解码状态；Evidence binding保留语义成熟度与不确定性 |
| review_required / review_decision / reviewer / reviewed_at | Human Review | KEEP | 继续作为晋升门 |
| effective_role | Approved Evidence | KEEP | 仅当前实验有效 |
| effective_priority | Approved Evidence | KEEP | 不参与Observation/Candidate admission |
| effective_report_position、effective_order | Presentation Plan | MOVE | 第一切片仍由CSV adapter提供给现有Renderer；目标上与Evidence身份解耦 |
| chinese_semantic | Presentation Plan + validated semantic label | SPLIT | 语义身份来自validated mapping，中文展示措辞属于RVM |
| EvidenceAssessment | Assessment | KEEP | 只消费Approved Evidence和有效gap，不回写Observation |

兼容原则：第一切片不删除任何现有CSV列。`EvidenceMappingAdapter`把新finding映射成现有`DraftSignalEvidence`/`ReviewOverride`/`ApprovedSignalEvidence`可消费的数据，待新路径稳定后再考虑schema版本升级。

## 6. Discovery Kernel Interface

### 6.1 Formal input

建议定义不可变 `DiscoveryRequest`：

```text
pipeline_version
experiment_id
purpose
analysis_charter_ref + hash
asc_ref + hash
admitted_time_range (optional)
dbc_refs[] + hashes
bus/channel policy
deterministic limits profile
```

不得包含 Approved Signal list。Known Signal Hint可选，但只影响候选压缩的保留优先级，不能影响帧、bus-key、DBC Join或Observation生成。

### 6.2 Formal output

建议定义版本化 `DiscoveryPackage`，核心集合为：

- `asc_integrity`：hash、大小、起止时间、解析/损坏帧数；
- `bus_inventory`：`channel + frame_format + CAN ID`身份；
- `raw_variant_summaries`：DLC分布、方向、帧数、时间范围、payload/bit摘要；
- `dbc_coverage`：MATCHED/PARTIAL/UNMATCHED及定义指纹；
- `signal_summaries`：来源、单位、MUX、样本数、范围、均值/SD、SNA/越界、变化与raw refs；
- `residual_summaries`：已知Message未覆盖或冲突位段；
- `unknown_summaries`：DBC未匹配bus-key的payload/bit摘要；
- `candidates`：有界、去重、带ranking reason与raw refs；
- `trace_store`：为允许的后续固定统计保留可寻址、冻结的列式/分段数据；
- `fingerprints`：输入、算法版本、limits profile和每个集合hash。

### 6.3 Deterministic responsibility

正式Kernel可复用Spike中的 `BusKey`、ASC parser、DLC/bit/payload accumulator、DBC fingerprint、Coverage Join、SignalAccumulator、candidate compression及raw-ref设计。必须补齐：

1. 每个parsed bus-key都产生machine observation或明确parse disposition；
2. frame-format/channel不可丢失；
3. candidates被压缩不等于observations被删除；
4. capped cardinality、raw-ref上限和candidate丢弃计数进入audit；
5. 多DBC冲突不得按文件顺序静默覆盖。

### 6.4 Kernel外职责

事件物理含义、L3/Control Tree映射、ER充分性、Signal成熟度升级、因果、人工动作时间、证据批准、报告位置均留在Kernel之外。

## 7. Semantic Reasoning Interface

### 7.1 Input

`SemanticReasoningInput`只由以下冻结对象组成：

- Analysis Charter与L3 Semantic Prior引用/fingerprint；
- control mainlines、Control Tree nodes、Evidence Requirements；
- Observation、Candidate、deterministic consistency result；
- event anchors及PLANNED/OBSERVED/CAN时间类型；
- validation states；
- 允许的一次follow-up操作描述；
- package identity/hash与引用闭包。

### 7.2 Output

沿用v1合同：finding、fact binding与`OBSERVED / DERIVED / INFERRED / UNSUPPORTED`、L3/Control Tree/ER mapping、relationship hypothesis、alternatives、model interaction、gap、validation request、uncertainty、trace refs。

正式化前仅修补合同工程问题：

- 为`updated_reasoning`明确状态机：`NOT_RUN / REPLACES / DELTA`；
- 审计`audit_metadata`必填字段，而不是仅要求对象存在；
- 明确`NO_SAFE_MAPPING`与`OUTSIDE_CURRENT_SCOPE`的字段位置；
- validator校验finding ID唯一性、gap ID唯一性、claim文本与fact binding覆盖关系；
- 不保存或要求hidden chain-of-thought。

### 7.3 Runtime policy

默认一次primary reasoning、零follow-up；最多一次deterministic follow-up和一次updated result。Semantic Reasoning进程没有ASC/DBC文件权限，只能读取冻结package和follow-up result。

## 8. Evidence Promotion Boundary

Finding本身不是Approved Evidence。建议状态流：

```text
Observation
  ↓
Reasoning Finding (hypothesis/mapping)
  ↓
Evidence Binding (Observation ↔ ER ↔ proposed role)
  ↓
Validation Result
  ↓
AUTO_ELIGIBLE or HUMAN_REVIEW_REQUIRED or HOLD_UNRESOLVED
  ↓
Approved Evidence
  ↓
Evidence Assessment
```

### 8.1 可确定性自动晋升的边界

仅允许自动晋升“证据身份/技术事实”，不自动晋升高风险物理语义。例如：ASC中bus-key存在、DLC分布、帧数、同定义下解码样本数、确定性派生公式、引用闭包、文件hash。即便自动晋升，也需保留算法版本和raw refs。

### 8.2 必须人工审核

- DBC冲突、MUX/DLC/缩放/符号/枚举疑点；
- Signal承担Request/Permission/Actual/Capability等关键角色但无独立验证；
- 跨系统边界、代理证据、由上下游间接支持；
- `INFERRED`、model `EXTENDS/CHALLENGES_CURRENT_MODEL`；
- P0/P1但成熟度低；
- 结论依赖缺失人工事件或外部物理证据；
- 新Control Tree mapping建议。

### 8.3 unresolved与challenge

`NO_SAFE_MAPPING`、`OUTSIDE_CURRENT_SCOPE`和未通过验证的Candidate留在Observation/Reasoning审计层，不强制写入Approved Evidence。`CHALLENGES_CURRENT_MODEL`生成review item和L3 gap记录，但本阶段不得自动改写L3或Control Tree。

## 9. Follow-up Interface Design

现有`TARGETED_WINDOW_STATS`在`execute_follow_up()`中重新打开DBC和ASC，不满足严格冻结/盲态要求。最小替代为：

```text
TARGETED_SYNCHRONIZED_WINDOW_STATS
input:
  request_id
  finding_id
  observation_refs[bounded]
  start/end CAN time
  allowed_metrics enum
  synchronization_policy enum
  max_age_ms (only for as-of join)
output:
  input package/trace-store hash
  per-observation count/min/max/mean/SD/first/last
  synchronized row count
  same-frame derived quantities where possible
  bounded as-of statistics where explicitly requested
  transitions
  raw-reference closure
  limitations
  result hash
```

约束：

- 只访问Discovery阶段冻结的`trace_store`，不访问ASC；
- operation、metrics、ref数量、时间窗、同步策略为枚举/上限，不提供表达式语言；
- 派生仅允许登记公式，例如同帧`V×I`；
- 不允许任意Signal搜索或扩大候选空间；
- 单次Reasoning最多一个request，无自主循环；
- result进入updated reasoning前先做hash和reference validation。

第一切片可暂时禁用follow-up；若启用，必须先实现trace store。不得把现有ASC重读实现直接搬入正式盲态接口。

## 10. Audit Metadata Design

### 10.1 Runtime audit（机器执行）

最小字段：pipeline/version、stage run IDs、input/hash、L3 fingerprint、Discovery fingerprint、Reasoning package/output hash、reference closure、unknown-ref count、model/follow-up/ASC-parse计数、stage timestamps、freeze hash/time、feature flag、legacy/new path、退出状态。

### 10.2 Engineering audit（分析复现）

DBC来源/定义指纹、DLC/MUX、窗口、同步策略、derived公式、raw refs、validation结果、Evidence promotion provenance、人工审核记录、未解决冲突。

### 10.3 Report provenance（人读产物）

RVM hash、Approved Evidence/Presentation Plan hash、Renderer版本、四件套hash、结构校验结果。继续由`工程审计.md`提供简洁入口，详细字段留机器JSON。

### 10.4 Benchmark-only metadata

hidden comparison source、strict-blindness setup、benchmark scoring和历史差异只进入benchmark目录，不进入正式车辆Assessment或报告。

四类metadata不可混用：benchmark结果不能批准Evidence；Renderer结构通过不能证明Semantic Reasoning正确。

## 11. RVM / Renderer Boundary

### 11.1 保留内容

保留`ExperimentReport`、ControlRelationshipView、timeline/profile、coverage、Assessment、结论、边界、建议等presentation-facing结构，以及Renderer的标准文件名、章节顺序、Approved引用合法性、coverage完整性、浮点格式和bundle校验。

### 11.2 已观察到的上游职责泄漏

- TM3-008的`render_tm3_008.py`在构造RVM时包含实验语义选择、事件解释和Signal用途；它虽不在shared renderer中推理，但文件名“render”掩盖了RVM assembly职责。
- TM3-007分析器直接写`report_view_model.json`，随后render脚本又读取机器证据并构造`ExperimentReport`，RVM身份存在双轨。
- `effective_report_position/order`仍与Approved Evidence同表，使presentation字段看起来像Evidence语义本身。

第一切片不重构这些文件。新路径在Evidence Assessment之后增加单一`build_report_view_model()`边界，并通过adapter生成现有`ExperimentReport`。shared Renderer保持不变。

## 12. Golden / Regression Separation

| Layer | 目的 | 样本/断言 | 不得控制 |
|---|---|---|---|
| A Program/Contract | schema、hash、refs、状态机、预算 | synthetic unit tests | 分析结论 |
| B Discovery Validation | bus-key完整性、Known/Residual/Unknown、压缩与raw refs | TM3-006 static discovery + synthetic channel/extended/DLC cases | Evidence Approval、报告 |
| C Semantic Reasoning Validation | 角色边界、gap、因果克制、NO_SAFE_MAPPING | TM3-015 v2.1 benchmark；允许合理差异 | exact historical answer、Renderer |
| D Output Regression | 四件套结构、可读性、稳定展示 | TM3-009/010 Golden byte/contract regression | Observation Space、Candidate、Reasoning admission |

TM3-015是semantic-boundary benchmark，不设exact-answer Golden。TM3-009/010继续保护既有报告、窗口、关键数值和Renderer行为，但不得反向限制Discovery输入。

## 13. KEEP / MODIFY / SPLIT / RETIRE Matrix

| 对象 | 当前职责/问题 | 决策 | 目标职责 | 迁移影响 |
|---|---|---|---|---|
| AGENTS Approved-before-ASC规则 | 禁止Approved前正式读取ASC | MODIFY | 改为Charter/Data Admission允许Discovery；Approved仍门控Evidence Assessment/正式结论 | 需明确新pipeline版本例外；旧规则保留legacy |
| Evidence Plan | ER、Signal、角色、审核、展示混合 | SPLIT | Charter/ER、Evidence Mapping、Approval、Presentation Plan | 第一切片用adapter，CSV不改 |
| Draft/Review/Approved workflow | 当前实验审核与来源可追溯 | KEEP | Evidence promotion和presentation approval | 无破坏性迁移 |
| Evidence Requirement | 多附着于Signal行 | MODIFY | Charter独立需求，Evidence Map多对多引用 | 兼容保留旧列 |
| Approved Evidence | 同时近似Approved Signal list | MODIFY | 被验证并批准用于Assessment的Evidence binding | 不再控制Observation admission |
| Evidence Assessment | 汇总Approved结果 | KEEP | 继续位于promotion之后 | 输入adapter变化 |
| TARGETS / REGISTRY | Signal准入白名单 | SPLIT | Known Signal Hint + legacy experiment adapter + presentation preference | 旧分析器不动；新入口禁作全局门 |
| existing ASC analyzers | 实验特定、重复parse/decode、受白名单限制 | KEEP/MODIFY | legacy保留；新实验通过versioned formal entry | 不批量迁移 |
| Phase 2.5 Discovery Spike | 已验证但与正式链隔离 | MODIFY | 抽取稳定pure kernel；Spike保留benchmark wrapper | 不复制整文件 |
| Semantic Reasoning Contract/validator | v1引用/边界合同 | MODIFY | 正式schema、lifecycle状态和runtime audit校验 | 保持v1兼容marker |
| Control Tree / L3 Prior | Reasoning语义坐标 | KEEP | 只读、版本化、带fingerprint | 不自动修改 |
| RVM / Renderer | 展示模型与共享渲染 | KEEP | Evidence/Synthesis后的presentation | 第一切片不改Renderer |
| Golden Contract/Regression | 输出结构与已验收样本 | KEEP/SPLIT | 仅Layer D；与Discovery/Reasoning regression分开 | 现有测试继续运行 |
| Engineering Audit | 分散于实验输出 | MODIFY | 汇总stage/hash/promotion/RVM provenance | 新路径新增机器audit |
| historical four-piece output | 已完成历史产物 | KEEP | 原样保留 | 不重生成 |
| Spike-only hidden comparison | benchmark评估 | RETIRE_FROM_FORMAL | 仅benchmark工具保留 | 不进入正式pipeline |

## 14. Minimum Migration Slice

第一切片只支持显式选择的新pipeline版本，不替换任何现有实验入口。

```text
formal_pipeline.py --pipeline-version discovery-reasoning-v1
        ↓
load Analysis Charter
        ↓
admit ASC + compute identity
        ↓
formal discovery wrapper (reuse kernel logic)
        ↓
freeze observation_package.json + trace_store
        ↓
build/validate semantic_reasoning_input.json
        ↓
one Semantic Reasoning result or externally supplied result
        ↓
validate result
        ↓
EvidenceMappingAdapter
        ↓
existing Draft/Review/Approved workflow
        ↓
existing analyzer downstream adapter / Assessment / RVM / Renderer
```

最小成功定义：新入口能在没有Approved Plan时完成Discovery与冻结Reasoning package；没有Approved Evidence时必须停在`AWAITING_EVIDENCE_REVIEW`，不得生成正式Assessment/四件套。人工批准后，通过adapter进入现有下游并保持Renderer可用。

不在第一切片实现自动L3 synthesis、通用事件识别、历史迁移或任意车型框架。

## 15. Expected File-Level Change Map

以下是Phase 3B预期，不是本阶段已修改内容。

### 15.1 新增

| 建议文件 | 职责 |
|---|---|
| `src/formal_pipeline.py` | 版本化stage orchestration、feature flag、stop gate、runtime audit |
| `src/analysis_charter.py` | 最小Charter dataclass/schema loader与hash |
| `src/can_discovery.py` | 从Spike抽取的稳定Discovery Kernel接口 |
| `src/observation_package.py` | package冻结、fingerprint、reference closure、trace store manifest |
| `src/semantic_reasoning_contract.py` | 从Spike抽取input/output validator；无样本知识 |
| `src/evidence_mapping_adapter.py` | finding/observation/ER到现有Draft/Approved工作流的兼容映射 |
| `src/runtime_audit.py` | stage计数、hash、时间、freeze与promotion provenance |
| `tests/test_formal_pipeline_contract.py` | gate、rollback、无Approved时正确停止 |
| `tests/test_can_discovery.py` | TM3-006和synthetic Discovery regression |
| `tests/test_semantic_reasoning_contract.py` | TM3-015边界、引用、预算、audit验证 |

### 15.2 小幅修改

| 文件 | 预期修改 |
|---|---|
| `src/evidence_plan.py` | 增加adapter友好的Evidence binding来源字段或旁路manifest；保持现有CSV读取兼容 |
| `spikes/semantic_coverage_residual_discovery.py` | 改为调用formal kernel的benchmark wrapper，避免逻辑双份维护 |
| `spikes/dynamic_semantic_reasoning_validation.py` | 改为调用formal contract/validator；hidden compare继续仅benchmark |
| `AGENTS.md` | 将Approved-before-ASC改为pipeline-version aware规则；不得放宽正式Assessment门 |

### 15.3 首切片受保护、不得修改

- `src/report_renderer.py`
- `src/render_tm3_regression.py`
- `doc/methodology/TM3_Human-readable_Report_Golden_Contract.md`
- `doc/methodology/TM3_Golden_Regression_Samples.md`
- TM3-009/010 Golden目录及既有hash
- 既有`output/TM3-xxx/`历史四件套
- 原始ASC、DBC、L3文档
- 现有`src/analyze_tm3_007.py`、`analyze_tm3_008.py`、`analyze_tm3_015.py`及对应render脚本（首切片以新入口并行，不就地改）

## 16. Rollback Strategy

1. 新入口必须显式指定`--pipeline-version discovery-reasoning-v1`或等价feature flag；默认继续legacy。
2. 新产物进入独立子目录，如`output/TM3-xxx/pipeline_v3/`，不覆盖历史machine evidence或四件套。
3. 每阶段写immutable manifest和hash；失败只影响当前run目录。
4. Approved Review前可删除/归档整个新run，不影响legacy输出。
5. Approval后运行同输入的legacy/new downstream comparison：Evidence Assessment差异、RVM引用、四件套结构分别比较。
6. 回滚触发：bus-key遗漏、unknown空间丢失、引用不闭合、模型预算超限、Evidence越权自动晋升、Renderer/Golden回归失败、四件套无法生成。
7. 回滚动作：停用feature flag并使用原实验入口；不得自动反写旧Approved Plan或历史报告。

## 17. Phase 3B Acceptance Gates

1. 无Approved Plan时，ASC可通过Charter进入Discovery；只能停在Discovery/Reasoning/待审阶段。
2. 每个parsed bus-key都有Observation或明确disposition及raw-reference路径。
3. TARGETS/REGISTRY不会截断Observation Space。
4. DBC-unmatched与Residual均保留机器表示。
5. Semantic Reasoning只接收冻结结构化输入，进程无ASC读取权限。
6. Finding不能直接成为Approved Evidence。
7. Evidence binding、validation、human decision、Assessment全程可追溯。
8. `src/report_renderer.py`无需修改且继续通过现有测试。
9. 现有四件套仍可生成并通过统一结构校验。
10. Layer A/B/C/D可独立运行和报告失败。
11. TM3-006 Discovery regression通过，含channel/extended/DLC/Residual/Unknown断言。
12. TM3-015 v2.1 semantic-boundary regression通过，不要求exact answer。
13. legacy入口与既有输出保持可用，直到人工迁移批准。
14. 一次primary reasoning；默认零follow-up；最多一次deterministic follow-up和一次update。
15. follow-up只读冻结trace store，不打开ASC。
16. 未Approved时禁止Evidence Assessment、RVM和正式四件套。
17. TM3-009/010 Golden byte/structure regression无非预期差异。

## 18. Known Risks

| 风险 | 严重度 | 控制 |
|---|---|---|
| 全量Observation产物过大 | MEDIUM | 全量机器摘要与有界raw refs；LLM只接收压缩包；Trace Store独立 |
| Candidate压缩误伤低频语义 | MEDIUM | Observation不删；按类型配额、discard audit、Known Hint仅影响保留优先级 |
| 多DBC组合产生静默语义覆盖 | HIGH | 定义并列、指纹、冲突状态；禁止last-file-wins |
| LLM finding被误当Evidence | HIGH | 强制Evidence Mapping/Validation/Review gate |
| Human Review工作量增加 | MEDIUM | 只审高风险binding；确定性技术事实可auto-eligible |
| 新旧路径结果差异被误判为回归 | MEDIUM | 四层regression分开；semantic允许有据差异 |
| RVM assembly职责继续分散 | MEDIUM | 第一切片接受兼容债务；设单一adapter边界，后续单独迁移 |
| Follow-up冻结数据不足 | HIGH | 首切片禁用follow-up或先建trace store；禁止回退到ASC重读 |
| AGENTS规则与新入口冲突 | HIGH | 仅对显式pipeline version增加Discovery例外，Assessment/报告门不放宽 |
| 审计元数据成为新大框架 | LOW | 仅最小stage/hash/count/timestamp/provenance字段 |

## 19. Explicit Deferred Items

本设计明确延后：

- 慢充/TM3-008专项验证、加速验证和跨车型验证；
- Aion或无DBC车型专用逆向；
- SavvyCAN自动化；
- Notion同步、正式知识库、自动L3/Control Tree修改；
- 自动故障原因确认、维修车间流程；
- UI、数据库、云端和分布式处理；
- 通用CAN逆向工程框架；
- 大规模历史Evidence Plan/报告迁移；
- Renderer外观或Golden Contract重写；
- Phase 3B生产实现。

## Design Decision

当前架构不需要重写Renderer、Golden Contract或历史产物。最小可行路线是新增一个版本化正式入口，把Phase 2.5 Kernel与Phase 2.6 Contract抽成无车型知识的稳定模块，再用Evidence Mapping Adapter接回现有Draft/Review/Approved和Renderer链。总体复杂度评估为 **MEDIUM**；建议 **PROCEED_TO_PHASE_3B**，但Phase 3B第一提交必须止于并行、可回退的最小切片。
