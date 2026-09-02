# TM3 Human-readable Report Golden Contract

## 1. 适用范围与权威样本

本契约适用于按当前生命周期完成正式分析的所有TM3实验，固定标准人读四件套的职责、结构和唯一生成路径。TM3-009与TM3-010是冻结Golden Regression Samples；除非证明原始数据或算法存在真实错误，不得改变其既有内容、结构或关键结论。

标准四件套精确文件名为：

- `TM3-xxx_最终报告.md`
- `采集时间线与关键Signal.md`
- `DBC关键Signal覆盖与可读性.md`
- `工程审计.md`

四件套必须由共享`Report View Model → report_renderer.py`路径生成。实验分析器只负责分析、机器证据和Report View Model，不得自行拼接正式四件套Markdown。结构差异属于`Regression Failure`。

## 2. 固定报告骨架

### 2.1 最终报告

一级标题后，以下七个核心职责槽位必须存在，并保持以下相对顺序：

1. `## 实验信息与适用范围`：用途、车辆、采集身份和适用范围。
2. `## 事实与关键证据`：支撑本实验判断的关键事实、数值和状态。
3. `## 控制关系`：分别表达控制链、动力/物理响应、能源交叉验证及边界。
4. 判断章节：基线实验使用`## 基线结论`，故障诊断使用`## 诊断判断`；冻结Golden保留已验收标题。
5. `### Evidence Assessment`：位于判断章节内，逐项对应Approved Evidence Requirements。
6. `## 证据边界`：集中表达DBC适配、缺失变量、阈值和外推边界。
7. `## 结论与下一步建议`：完成状态含义、是否补采、最小下一步及是否进入诊断树。

上述核心职责槽位不得删除、合并、改名或换位，`Evidence Assessment`必须位于判断章节之后、证据边界之前。完整标题序列不要求与上述列表完全相等；在不破坏核心职责相对顺序的前提下，允许加入实验专项内容。事实、控制关系、判断、边界和建议的具体条目允许实验特化；实验脚本明确要求逐题回答时，可在适当位置增加专项内容。

### 2.2 采集时间线与关键Signal

一级标题后固定包含：

1. 人读时间线职责槽位；连续过程实验可使用`## 实际时间线`，冻结Drive Golden保留`## 人读主时间线`；
2. 与实验类型匹配的关键事件或状态变化表达；
3. 零个或多个实验特定分析表或专项内容；
4. 人读层与工程审计层的字段边界说明。

Event ID/事件ID、raw sample time/原始采样时间、Signal age、DLC及per-frame decode status不得成为人读主时间线的常规展示字段，这些字段保留在机器证据或工程审计中。Signal Name和CAN ID是证据追溯身份，不属于上述机器审计噪声，不得因人读简化而弱化关键事件的证据定位能力。

当前注册Profile：

- `DRIVE`：固定表头、字段顺序和既有Golden行为继续作为Hard Contract：`时间(s) | 状态/动作 | 电门(%) | 请求扭矩(Nm) | 实际扭矩(Nm) | 车速(km/h) | 电驱功率(kW) | Pack电流(A) | Pack功率(kW) | 备注`。
- `WAKE_HV`：采用变化优先的连续离散事件时间线，并允许上游按实验语义提供可选工程阶段和`event / stable_window`事件类型，不再以固定十列完整状态快照作为Hard Contract。进入人读时间线的关键事件必须能够表达CAN时间或窗口、关键变化、实际Signal值变化、支撑该变化的Approved Signal及对应CAN ID、该变化在本实验状态链中的工程意义，以及存在时的事件局部证据限制。阶段可以作为连续时间线中的分组字段，不要求拆成多张表。Contract规定必须表达的信息，不规定阶段名称、阶段数量、固定列数或固定字面表头。

离散事件时间线应优先呈现事件变化。持续背景状态原则上不在每个事件节点机械重复；实验级全局证据边界原则上集中进入`证据边界`等适当位置；Signal Validation和DBC冲突根据用途进入专项内容或DBC覆盖报告，不因Profile而逐行展开。

中文工程概念用于帮助读者理解，Signal Name和CAN ID用于追溯证据。关键证据首次出现或需要消除歧义时应自然提供完整定位，后续可根据上下文简写；具体组合方式属于Soft Guidance，不要求每次机械采用`中文名（Signal Name, CAN ID）`格式。

### 2.3 DBC关键Signal覆盖与可读性

一级标题后，章节及顺序固定为：

1. `## 核心Signal表`
2. `## DBC异常与可读性说明`

冻结Drive Golden继续保留既有九列及顺序：

`控制树角色 | Signal | Message | CAN ID | 单位 | 本次观测范围/状态 | 是否变化 | 解码状态 | 本次用途`

`core_signals`与`coverage_signals`是不同集合：前者表示最终报告等人读主线主动选择的核心Signal，不决定DBC覆盖范围；后者负责说明本实验全部Approved证据Signal的去向。DBC Signal覆盖表必须保留九项工程职责：Signal、控制含义、Message、CAN ID、单位、观测范围/状态、变化情况、解码/验证状态及用途/边界；允许增加连续序号作为引用辅助。Signal应作为主要阅读对象，“控制含义”说明其在本实验过程中的含义，不要求强行定义为严格控制树角色。

`coverage_signals`成员资格仍由Approved Plan确定；展示顺序属于RVM的Presentation Judgment，可按实际状态推进或首次有效观测组织，不改变Approved `effective_order`本身。无可靠时间、无帧或语义验证失败的Signal不得制造时间事实，可放在对应阶段之后或其他合理位置。

非DBC派生指标进入独立的“非DBC派生证据”小节，不得伪装成DBC Signal或人为生成不存在的Message；应说明来源/统计对象与派生含义。无帧、不可读、语义验证失败及存在多DBC冲突的Approved Signal仍须保留。不得以未经Approved的Signal扩展覆盖视图，也不得为了扩大覆盖而修改既有Approved placement。

覆盖表成员不得被`CORE_SIGNAL_TABLE`意外截断。具体措辞和机械布局不作为跨Profile Hard Contract；证据身份、覆盖完整性和上述工程职责属于Hard Contract。

### 2.4 工程审计

一级标题后，章节及顺序固定为：

1. `## Evidence Plan状态`：Approved状态、范围、Signal数量、人工审核记录及Renderer裁决边界。
2. `## 数据与复现`：原始输入身份、哈希、分析入口、窗口及机器证据路径。
3. `## 工程字段边界`：说明Event ID、原始采样时间、Signal age、DLC及逐帧解码状态的机器证据归属。

上述章节不得删除、合并、改名或换位。具体复现条目允许实验特化。

## 3. 固定、实验特化与条件触发内容

### A. 固定报告骨架

- 四件套精确文件名、核心职责槽位和相对顺序；
- Evidence Assessment的位置；
- DBC覆盖表的全部Approved证据去向、证据身份、工程职责及Approved准入；
- 工程审计三章节；
- `DRIVE` Profile的固定字段和顺序；`WAKE_HV` Profile必须表达的事件语义与证据追溯信息；
- 工程字段不得进入人读主时间线。

### B. 实验特定内容

- 标题、元数据、事实、控制关系内容、判断、Evidence Assessment条目；
- 证据边界、建议、时间线行值；
- 分析专项表、Signal观测范围、用途和DBC异常说明；
- 数据哈希、命令、机器证据路径和复现说明。

### C. 条件触发专项章节

实验可在不破坏核心职责槽位相对顺序的位置增加专项分析表或章节，例如稳定窗口统计、多DBC对照、Signal Validation、能量闭环或故障专项。专项内容不得取代、拆散或改名核心职责槽位，不得改变`DRIVE`冻结结构，也不得把分析裁决下放给Renderer。

## 4. Report View Model与Renderer边界

Report View Model是Renderer唯一输入接口，并应承载分析层已经完成的Presentation Judgment，包括实验特定的信息选择、组织和自然语言表达。上游必须提供已批准Signal引用、Control Relationship View、Evidence Assessment及必要展示数据，但不得在RVM阶段重新进行Evidence Assessment或改变机器证据。离散状态实验允许把`control_mainline`、`mainline_verification`、实验特定的控制关系表达与`global_evidence_boundaries`分层表达：控制关系可分别组织状态推进、控制执行、物理响应、能源交叉验证和结果反馈，不要求把不同性质内容压成一条因果链；验证覆盖保存Approved Signal引用、验证程度和局部限制；全局边界集中保存实验级限制。不得把“部分可观测”“无直接观测”“候选”“缺失”等验证标签机械拼入主线节点名称。

Renderer负责标准文件名、必要章节、基本相对顺序、Approved Signal引用合法性、coverage完整性、Evidence Assessment完整性、基本格式、人读层与工程审计层的字段边界及Bundle结构校验。Renderer保证不丢失合同要求的信息、不越过证据边界且输出结构可验证；语义正确性仍由分析层、Human Review和RVM形成过程负责。

Renderer不得选择关键事件、决定某事件最重要的Signal、自动拼装领域状态快照、自动决定中文工程名称、根据P等级或Signal名称生成控制主线、根据时间先后推断因果、选择冲突DBC定义、改变Signal maturity、从Signal值重新推导控制关系、重写Evidence Assessment或重写实验结论。

所有完成态TM3在发布前必须通过统一结构校验。历史完成态尚未迁移到共享Renderer时保留原状；只有收到明确迁移或重渲染任务后才纳入，不得为满足扫描测试而自动改写历史产物。
