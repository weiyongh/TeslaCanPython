# TeslaCanPython 设计共识与工作基础（Review Draft v0.1）

> 状态：**REVIEW DRAFT / NOT YET PROJECT CONTRACT**\
> 用途：汇总截至当前已经形成的、对 TeslaCanPython
> 长期有价值的设计目的、架构原则、数据边界和 AI 协作思路。\
> 本文首先供人工 Review；Review 通过后，再决定哪些内容进入 repo 的正式
> Project Context / Methodology。\
> 本文不是新的 Phase Task，不授权 3B.2.6A 或任何后续实现。

------------------------------------------------------------------------

# 1. 项目原始目的

TeslaCanPython 最初且未改变的目的：

> **采集和分析 ASC，建立 Tesla Model 3 正常基线数据。**

进一步定义：

> 围绕 L3 控制树和采集实验，从 ASC 中建立足够可靠的通信
> Evidence，把抽象控制树实例化为 Model 3
> 的实测控制实例，并形成正常基线采集分析报告。

因此，TeslaCanPython 的主要价值不是"把 DBC
解得越来越多"，也不是"建设一个通用 CAN 逆向平台"。

更合适的长期评价方向是：

``` text
Control-Tree Instance Evidence Coverage
+
Baseline Quality
+
Evidence Reliability
```

DBC 验证是重要副产品，但不是项目终点。

------------------------------------------------------------------------

# 2. 当前阶段的核心任务

当前阶段首先服务于 Model 3：

``` text
L3 车型无关控制模型
        ↓
实验设计 / 采集脚本
        ↓
Model 3 ASC
        ↓
通信 Observation / Engineering Facts
        ↓
Semantic Reasoning
        ↓
Evidence
        ↓
Model 3 控制树实例化
        ↓
正常基线
```

正常基线未来可以支持：

``` text
Normal Baseline
      ↕
Fault Data
      ↓
DIFF
      ↓
控制树定位
      ↓
诊断树
      ↓
Fault Boundary
      ↓
Next Evidence
      ↓
Troubleshooting Procedure
```

但未来的自动诊断不是当前阶段必须一次完成的工程目标。

------------------------------------------------------------------------

# 3. 项目长期演进方向

## Stage 1 --- 当前

Model 3：

-   基线采集；
-   ASC 分析；
-   Evidence 建立；
-   控制树实例化；
-   数据质量和可追溯性建设。

## Stage 2 --- 后续

在其他车型、尤其无完整 DBC 车型上验证：

-   Observation Fingerprint；
-   Known / Residual / Unknown 方法；
-   可复用的数据处理过程。

Stage 2 不是 Stage 1 的前置条件。

## Stage 3 --- 长期

面向实际故障：

``` text
故障现象
+
故障数据
+
正常基线
+
L3 控制树 / 诊断树
+
维修资料 / 电路图
        ↓
AI 辅助诊断
        ↓
缩小故障边界
        ↓
提出下一步 Evidence
        ↓
形成诊断工作过程
```

不要为了 Stage 3 提前把所有未来需求变成 Stage 1 的当前工作量。

------------------------------------------------------------------------

# 4. 最核心的 AI 编程原则

> **我们是在建立适合 AI 分析的程序，而不是把手伸进 LLM 里。**

程序与 AI 的职责应分开。

## 4.1 程序负责

``` text
Program
├─ 保护事实
├─ 读取和解析数据
├─ 建立稳定结构
├─ Observation Space 整理
├─ 确定性统计
├─ 行为变化描述
├─ 事件和关系事实
├─ 数据压缩
├─ Provenance
├─ Hash / Audit
├─ Contract Validation
└─ 明确数据缺口和限制
```

## 4.2 AI 负责

``` text
LLM
├─ 理解语义
├─ 判断相关性
├─ 建立假设
├─ 理解控制关系
├─ 比较替代解释
├─ 挑战 DBC
├─ 选择可能的 Evidence
├─ 识别 Evidence Gap
└─ 形成自然语言分析
```

核心边界：

> **程序应该替 LLM 整理数据、保护事实、保证可追溯；但不要替 LLM
> 预先完成理解问题、选择视野和组织推理。**

------------------------------------------------------------------------

# 5. Engineering Fact 与 Semantic Claim 必须分离

程序可以确定性计算：

``` text
cardinality
transition timestamps
min / max / mean
stable intervals
step amplitude
bit activity
payload variability
change points
event-window alignment
lead / lag
co-transition
tracking error
V × I
current decay
zero-current time
```

这些属于：

> **Engineering Facts**

程序不应直接宣布：

``` text
“这是充电许可”
“这是接触器闭合命令”
“这个 ID 是 OBC 请求”
“A 导致了 B”
“这个 Signal 承担某控制角色”
```

这些属于：

> **Semantic Interpretation / Semantic Claim**

推荐关系：

``` text
Raw Observation
      ↓
Engineering Fact
      ↓
Relationship Fact
      ↓
LLM Interpretation
      ↓
Evidence Candidate / Finding
      ↓
Human Review
      ↓
Approved Evidence
```

------------------------------------------------------------------------

# 6. ASC、L3、DBC 的权威边界

一句话：

> **L3 决定要理解什么；ASC 决定实际发生了什么；DBC 帮助解释 Observation
> 可能是什么。**

------------------------------------------------------------------------

# 7. ASC 是 Observation 的事实来源

Observation Space 的入口不应由 DBC Signal List 决定。

最低要求：

``` text
Full ASC
   ↓
all bus / CAN ID / DLC census
   ↓
Full Observation Space
```

即使某个 CAN ID：

-   DBC 没有定义；
-   Signal 名称未知；
-   与当前 L3 关键词不匹配；

它仍然有资格存在于 Observation Space。

> **Visibility / Admission 与 Semantic Relevance 必须分离。**

------------------------------------------------------------------------

# 8. L3 的角色：Semantic Prior，不是 Observation Whitelist

L3 知识包括：

``` text
系统结构
状态
变量
控制主线
控制树
实现边界
诊断树
Evidence Requirement
```

以及基础控制语义：

``` text
Capability
Variable
State
Condition
Request
Action
Boundary
Evidence
```

其中 Evidence 是验证层，不是第八个控制变量。

L3 可以帮助 AI 理解：

> 当前实验应该理解哪些控制问题？

但 L3 不应该让程序规定：

> 只有名称或行为看起来符合 L3 的 Observation 才能被看见。

因此：

> **L3 Semantic Prior ≠ Observation Admission Authority**

L3 / Experiment Script 可以影响：

-   分析优先级；
-   分析深度；
-   Working Context；
-   AI 的问题方向。

但不能决定 Observation 是否存在。

------------------------------------------------------------------------

# 9. DBC 的角色重新定性

## 9.1 DBC 可以做

``` text
DBC
├─ Decode
├─ Signal Name
├─ Unit
├─ Enum
├─ ECU / Message Reference
├─ Semantic Hint
└─ Validation Target
```

DBC 也可以被实测数据反向验证。

如果 DBC 描述与物理 Observation 明显冲突，系统和 AI 应允许：

> **Challenge DBC**

而不是强迫数据服从 DBC。

## 9.2 DBC 不可以做

``` text
DBC
├─ 决定 Observation Universe       ×
├─ 决定 Candidate Admission        ×
├─ 决定 Control Tree               ×
├─ Signal Name → Evidence           ×
├─ 决定 Confirmed Control Role      ×
└─ 屏蔽 Unknown / Residual          ×
```

核心原则：

> **DBC 可以帮助人和 AI 看懂 Model 3，但不能规定 AI 只能看见什么。**

------------------------------------------------------------------------

# 10. Known / Residual / Unknown 必须共存

Observation Space 应同时容纳：

``` text
K = Known
R = Residual
U = Unknown
```

不能采用：

``` text
DBC Known
   ↓
进入分析

Unknown
   ↓
丢弃
```

K / R / U 都属于真实 ASC Observation。

这既提高 Model 3 基线的完整性，也为以后无完整 DBC 车型保留必要弹性。

------------------------------------------------------------------------

# 11. Full Observation 不等于全自动 Unknown Signal 逆向

"完整观察 CAN"不能被扩张为：

> 自动发现所有未知 Signal、位宽、Endian、Scale、物理意义并生成完整 DBC。

那会变成另一个独立工程。

当前 Unknown / Residual 可以先做有限、确定性的行为描述，例如：

``` text
Unknown CAN Payload
├─ payload cardinality
├─ byte activity
├─ bit activity
├─ transition frequency
├─ variability / entropy
├─ stable / changing regions
├─ regime changes
└─ 必要时简单 contiguous bit candidate
```

当前不要求：

-   自动命名；
-   自动赋予物理意义；
-   自动生成通用 DBC；
-   建设完整 CAN Reverse Engineering Platform。

同时必须区分：

``` text
Known DBC Signal Shape
≠
Unknown Raw Payload Behavior
```

------------------------------------------------------------------------

# 12. Full Census 与 Deep Processing 分层

完整 Observation 并不意味着对所有 CAN ID 做同等昂贵的深度分析。

推荐：

``` text
Full ASC minimum census
        ↓
Cheap Generic Behavior Fingerprint
        ↓
L3 / Script / Event guided priority
        ↓
Deeper Deterministic Features
        ↓
Candidate Compression
        ↓
Attach DBC Reference Metadata
        ↓
LLM Working Input
```

原则：

> **L3 / Script 可以指导 Priority / Depth，但不能决定 Visibility /
> Admission。**

------------------------------------------------------------------------

# 13. Candidate 是压缩，不是事实边界

必须长期保持：

``` text
Observation
≠
Candidate
```

Candidate 只是从完整 Observation Space 中压缩出的重点对象。

因此：

> Candidate 上限可以限制后续计算量，但不能删除或重新定义完整 Observation
> Space。

同理：

``` text
Observation
≠ Candidate
≠ Retrieved Observation
≠ Finding
≠ Evidence Binding Draft
≠ Approved Evidence
```

具体含义：

``` text
被程序观察到
≠
知道它是什么

成为 Candidate
≠
语义成立

被 Retrieval 选中
≠
就是所需 Evidence

被 LLM 写成 Finding
≠
人工认可

被映射到 ER
≠
Approved Evidence
```

------------------------------------------------------------------------

# 14. Relationship 的设计边界

程序可以计算确定性关系事实，例如：

``` text
A transition @ t1
B transition @ t2
Δt = 320 ms
```

或者：

``` text
Target Current ↓
Actual Current ↓
Tracking Error = ...
```

程序可以描述：

> A 的变化通常早于 B，时间差约为某个确定性统计结果。

但程序不能仅凭这个事实宣布：

> A 是 B 的控制命令。

后者仍需要结合：

-   L3；
-   实验设计；
-   DBC Reference；
-   其他 Observation；
-   物理一致性；

由 AI / 人进行语义判断。

因此当前不需要建设巨大的通用 Relationship / Causality Engine。

> **先提供 Relationship Observations，再让 AI 理解关系。**

------------------------------------------------------------------------

# 15. 时间语义必须分离

至少区分：

``` text
PLANNED_TIME
OBSERVED_EVENT_TIME
CAN_OBSERVED_TIME
```

例如实验脚本写：

> 20 秒插枪

这属于：

``` text
PLANNED_TIME
```

如果 CAN 在 20.3 秒出现变化：

``` text
CAN_OBSERVED_TIME = 20.3 s
```

不能因此自动升级为：

``` text
OBSERVED_EVENT_TIME = 20.3 s
```

除非有真实 Evidence 支撑该事件发生时间。

核心原则：

> **CAN 时间不能冒充人工事件时间；计划事件也不能冒充已观察事件。**

------------------------------------------------------------------------

# 16. Experiment Script 的角色

采集脚本告诉系统：

-   本次实验想做什么；
-   计划进行了哪些操作；
-   大致时间窗口；
-   哪些状态或控制问题值得关注。

但 Script 不提供 expected answer。

因此：

``` text
Experiment Script
      ↓
Context / Planned Event / Analysis Intent
```

而不是：

``` text
Experiment Script
      ↓
Ground Truth
```

------------------------------------------------------------------------

# 17. TM3-006 的历史经验

TM3-006 的实际结构大致是：

``` text
人确定电池问题和目标 Signal
        ↓
DBC 反查目标 CAN ID
        ↓
Python 只处理这些 ID
        ↓
DBC Decode
        ↓
确定性统计 / Window / Brick / Alert
        ↓
人 / LLM 做语义综合
        ↓
自然语言报告
```

006 的重要经验不是"旧方法错误"，而是：

> **18 个 ID 之后做得很好；18 个 ID 之前几乎没有做。**

它值得保留：

-   deterministic data 与 semantic reasoning 分离；
-   time series → engineering statistics；
-   experiment-driven window；
-   specialized physical reducer；
-   DBC decode；
-   empirical validation；
-   physical closure；
-   missing / conflict 显式表达；
-   人 / LLM 做最终语义综合。

需要演进的部分：

> **不能再由人 + DBC 在程序外提前完成 Candidate Discovery。**

一句话：

> **006 的缺口不是 LLM 不够聪明，而是候选发现由人 + DBC
> 在程序外完成了。**

------------------------------------------------------------------------

# 18. 推荐的数据链路

不再以：

``` text
ASC
→ DBC
→ Signal
→ LLM
```

作为唯一主线。

更合理的是：

``` text
Raw ASC
   ↓
Full Observation Census
   ↓
Generic Behavior Fingerprint
   ↓
Deterministic Engineering Reduction
   ↓
Change / Event / Relationship Facts
   ↓
K / R / U
   ↓
Candidate Compression
   ↓
Engineering Data Description
   ↓
Attach DBC Reference
   ↓
L3 + Experiment Context
   ↓
Frozen LLM Input
   ↓
LLM Semantic Reasoning
   ↓
Finding / Gap / Alternative / Hypothesis
   ↓
Evidence Mapping Draft
   ↓
Human Review
   ↓
Approved Evidence
   ↓
Baseline / Control Tree Instantiation
```

这张链路是当前设计讨论最重要的长期骨架之一。

------------------------------------------------------------------------

# 19. Retrieval 的当前教训

已有 Phase 3B.2.x 实践暴露出一个重要问题：

> LLM 的输入如果被程序预先筛选、预先组织得太强，表面上是 AI
> 在推理，实际上程序已经替 AI 决定了很大一部分"应该看什么"。

因此当前设计原则是：

> **大胆改 Retrieval 的结构，不要大胆调 Retrieval 的权重。**

不要优先走向：

``` text
keyword weight
semantic weight
DBC name boost
vehicle-specific score
special-case ranking
```

而应该优先检查：

``` text
Observation Space 是否完整？
Candidate Representation 是否合适？
Engineering Facts 是否足够？
Context Boundary 是否合理？
Provenance 是否完整？
AI 是否真的拥有必要的判断空间？
```

注意：

> 这并不意味着 Retrieval 一定应该被删除。

当前共识只是：

> **Retrieval 不应在无意中成为隐藏的 Semantic Decision Engine。**

其最终结构仍需要通过真实 TM3 数据验证。

------------------------------------------------------------------------

# 20. Frozen LLM Input 的目的

LLM 不应该自由访问所有历史资料然后"自己找答案"。

推理应尽量基于一个明确、可追溯的 Working Input。

最低审计原则：

``` text
Frozen Input
Final Call Envelope
Model Identity
Reasoning Effort
Call Count
Strict Blind Isolation（需要 blind validation 时）
```

目的不是控制 LLM 的思考过程，而是回答：

> **这次 AI 到底看见了什么？**

以及：

> **这个结论能否追溯到本次冻结输入？**

不需要为了这一原则建设复杂的 LLM Platform。

------------------------------------------------------------------------

# 21. Blind Validation 的边界

当任务要求 strict blind replay / blind validation 时：

-   历史正确答案不得进入输入；
-   Approved Evidence 不得泄漏；
-   expected answer 不得进入；
-   历史报告不得作为隐形提示；
-   当前有历史答案污染的会话不能冒充 blind context。

Blind 的目标是验证：

> AI 能否从允许的 Observation + L3 + Experiment Context 独立形成判断。

------------------------------------------------------------------------

# 22. Program Validation ≠ Semantic Correctness

程序可以验证：

-   schema；
-   hash；
-   reference existence；
-   package identity；
-   numeric grounding；
-   call limits；
-   approval boundary；
-   role/time/causality contract。

但：

``` text
validation = true
```

只意味着：

> **LLM 输出符合程序合同。**

它不意味着：

-   语义一定正确；
-   Signal Role 已确认；
-   Evidence 已批准；
-   报告结论已经成立。

------------------------------------------------------------------------

# 23. Human Review 的位置

现有正式流程已经存在 Human Review。

因此当前原则：

> **不要通过不断增加新的 Human Review Gate 来解决输入透明度或 AI
> 不确定性问题。**

真正需要的是：

``` text
ASC
↓
Engineering Facts
↓
Frozen / Auditable LLM Input
↓
LLM Output
↓
Deterministic Validation
↓
Evidence Mapping Draft
↓
Existing Human Review
↓
Approved Evidence
```

Human Review 应用于：

-   Evidence promotion；
-   重要语义确认；
-   冲突裁决；
-   不确定性判断。

不应该把每个中间 JSON 都变成人工审批节点。

------------------------------------------------------------------------

# 24. L3 Knowledge 的本地架构

Notion 是 L3 知识的编辑权威。

TeslaCanPython 本地：

``` text
knowledge/
└─ notion_l3/
   ├─ README.md
   ├─ snapshot_manifest.json
   ├─ current/
   └─ snapshots/
```

职责：

``` text
Notion
= Sole Editing Authority

knowledge/notion_l3/current/
= 日常本地 Knowledge Source

snapshots/
= Provenance / Historical Snapshot
```

普通 TM3 工作不应默认访问实时 Notion。

同步是：

``` text
Notion formal L3
      ↓
Manual Trigger
      ↓
Full Export
      ↓
Validate
      ↓
Snapshot
      ↓
Promote to current/
```

同步失败时：

> 保留旧 current，不提升不完整 Snapshot。

------------------------------------------------------------------------

# 25. Knowledge Source ≠ Working Context ≠ LLM Payload

必须长期保持三层区别：

``` text
① Knowledge Source
knowledge/notion_l3/current/
完整 L3 知识
        ↓
② Working Context
当前 TM3 Case 真正需要的 L3
        ↓
③ LLM Payload
当前一次 Semantic Reasoning
真正需要看到的材料
```

本地有完整 L3：

> **不等于每次把完整 L3 塞给 LLM。**

Project Context 的职责也不是复制整个 Notion L3，而是告诉 Codex：

-   知识在哪里；
-   什么是正式来源；
-   什么时候读；
-   当前任务如何使用这些知识。

------------------------------------------------------------------------

# 26. L3 文档结构本身具有语义

L3 中的 ASCII Tree 不是纯排版。

例如：

``` text
│
├─
└─
↓
```

表达：

-   父子层级；
-   兄弟关系；
-   分支关系；
-   某些情况下的先后关系。

因此处理 L3 Tree 时：

> 不得为了"格式优化"擅自改变层级、兄弟节点和竖线连续性。

Mermaid 状态图也属于语义模型，不是装饰。

需要保留：

-   State；
-   Transition；
-   Direction；
-   Condition；
-   `<br/>` 换行约定。

------------------------------------------------------------------------

# 27. Specialized Reducer 应保留

"Generic Observation Pipeline"不意味着删除所有车型/系统工程知识。

像 TM3-006 中成熟的：

-   Brick consistency；
-   voltage span；
-   power consistency；
-   current tracking；
-   specialized physical closure；

如果它们是：

-   deterministic；
-   可验证；
-   有明确物理意义；
-   不偷偷决定 Semantic Role；

就应该保留。

正确关系是：

``` text
Generic Observation Layer
        +
Specialized Deterministic Reducer
        ↓
Richer Engineering Facts
```

而不是为了"通用化"把所有工程 reducer 删除。

------------------------------------------------------------------------

# 28. 物理一致性是强 Evidence，但不是语义捷径

例如：

``` text
P ≈ V × I
Target ≈ Actual
Pack Current ≈ Charger Current
Cell / Brick consistency
```

这些可以提供很强的物理闭环。

但仍应区分：

``` text
Physical Consistency
≠
Automatically Confirmed Control Role
```

物理闭环可以显著提高语义判断可信度，但不替代必要的 Evidence Boundary。

------------------------------------------------------------------------

# 29. 缺失数据必须被允许成为结论

TeslaCanPython 不应该为了"完成报告"而填补未采集的信息。

如果当前实验没有：

-   可靠人工事件时间；
-   某个 EVSE 量；
-   某个车辆侧量；
-   某个请求量；
-   某个 Permission 直接 Evidence；

正确结果可以是：

``` text
NOT OBSERVED
UNAVAILABLE
UNRESOLVED
HOLD
EVIDENCE GAP
```

而不是通过：

-   DBC 名称；
-   相邻 Signal；
-   L3 预期；
-   历史结果；

把缺失事实补出来。

一个有效系统不仅应该：

> 找到能找到的 Evidence，

也应该：

> **正确指出不能证明什么。**

------------------------------------------------------------------------

# 30. 对旧实验应尊重数据边界

旧 TM3 实验可能没有按后来形成的方法论采集全部理想信息。

不能要求旧数据证明当时没有采集的事实。

对旧实验的公平评价是：

> 在现有数据边界内，程序有没有把能找到的东西找到？

> 有没有正确指出不能证明的东西？

> 有没有拒绝用 DBC 名称和推理去填补真实采集缺口？

------------------------------------------------------------------------

# 31. 架构不变量与实验性部分应区别管理

## 31.1 应严格保护的不变量

``` text
Raw Provenance
ASC Identity / Parse Integrity
Time Semantics
Evidence Epistemic Class
Approved Gate
Historical Leakage Boundary
Data Immutability
Assessment / Evidence Boundary
Traceability
```

## 31.2 可以快速试验的部分

``` text
Retriever Organization
Prompt
Observation Context
Candidate Recall
LLM Input Organization
Model Choice
LLM Output Form
```

因此开发方式应更接近：

``` text
Hypothesis
   ↓
Implement
   ↓
Run Real TM3
   ↓
Inspect
   ↓
Keep / Modify / Revert
```

而不是试图在实现前一次设计出最终完美架构。

------------------------------------------------------------------------

# 32. 当前工程应避免的过度建设

除非真实 TM3 工作证明有必要，否则不要为了"未来完整性"建设：

-   Multi-Agent Orchestration；
-   RAG Platform；
-   Vector DB；
-   Knowledge Graph；
-   Ontology；
-   Complex Context Compiler；
-   Complex Phase Management System；
-   Automatic Notion Sync；
-   Bidirectional Knowledge Sync；
-   Full Model 3 Semantic Signal Database；
-   Automatic Evidence Approval；
-   Automatic Control Tree Generation；
-   Automatic Diagnostic Tree Generation；
-   Generic Full CAN Reverse Engineering Engine。

判断标准：

> **这件事是否直接提高 Model 3 基线采集、分析、Evidence
> 可靠性或基线数据质量？**

如果答案不是明确的"是"：

``` text
Record
→ Minimal Elasticity
→ PARKED
```

不要立刻实施。

------------------------------------------------------------------------

# 33. "重锤原则"

TeslaCanPython
允许保留远期方向，但不允许把所有远期方向提前变成当前任务。

> **不是锤掉远见，而是锤掉把远见提前变成当前工作量的冲动。**

典型需要被锤的情况：

``` text
当前只是验证 Observation
        ↓
却顺手建设 RAG / KG / Agent / Ontology
```

或者：

``` text
当前只是发现 Unknown Behavior
        ↓
却开始自动逆向全部 DBC
```

或者：

``` text
当前只需要一个真实 TM3 验证
        ↓
却先设计十个未来 Phase
```

------------------------------------------------------------------------

# 34. 人与 Codex 的目标协作方式

TeslaCanPython 不应长期依赖：

``` text
用户
↓
ChatGPT 翻译成详细 Task
↓
用户转交
↓
Codex 执行
↓
用户搬回
↓
ChatGPT Review
```

目标方式：

``` text
用户
│
│ 正常工程语言
▼
Codex
├─ 自主读取 Project Context
├─ 自主读取 L3
├─ 检查 Current Status
├─ 提出方案
├─ 执行
├─ 测试
└─ 在正确 Stop Point 停止
```

ChatGPT 的后续主要角色：

-   架构 Review；
-   重大争议；
-   反方审查；
-   防止过度设计；
-   必要时落"大锤"。

Codex 是否完成工作移交的真正标准不是：

> 能不能独立写代码。

而是：

> **用户能否用正常工程语言直接表达目标，而不需要第三方先把它翻译成十几页执行规格。**

------------------------------------------------------------------------

# 35. 当前中间产物的认识论层级

当前 Formal Pipeline 已经形成一组有价值的中间对象。

核心区别：

``` text
Observation
≠
Candidate
≠
Retrieved Observation
≠
Finding
≠
Evidence Binding Draft
≠
Approved Evidence
```

建议把它理解成：

``` text
Observation
= 程序观察到了什么

Candidate
= 从 Observation 中压缩出的重点对象

Retrieved Observation
= 某次推理选择给 AI 看的 Observation 子集

Finding
= AI 对冻结输入形成的语义判断

Evidence Binding Draft
= Finding 与 Evidence Requirement 的待审映射

Approved Evidence
= 通过规定验证与人工审核后的正式 Evidence
```

这一层级是 TeslaCanPython 当前最有价值的认识论骨架之一，应长期保护。

------------------------------------------------------------------------

# 36. Runtime Audit 的意义

一次正式 Run 应能够回答：

``` text
用了哪个 ASC？
用了哪个 DBC？
ASC 解析了几次？
产生多少 Observation？
K / R / U 各多少？
Candidate 多少？
LLM 看到了哪个冻结输入？
调用了几次？
输出多少 Finding？
最后停在哪里？
```

Audit 的目标不是增加流程，而是保证：

> **每次分析都能知道它到底做过什么。**

------------------------------------------------------------------------

# 37. 当前设计仍未冻结的问题

以下内容仍然应该保持开放，不应因为本文汇总而误认为已经成为正式
Contract。

## 37.1 Retrieval 最终结构

尚未最终决定：

-   是否继续保留当前 Intent-driven Retrieval；
-   如何避免 DBC lexical dominance；
-   如何让 AI 获得更充分的 Observation 视野；
-   Candidate / Retrieved Observation 应如何组织；
-   Event-centered representation 应做到什么程度。

## 37.2 Engineering Data Description 的边界

仍需通过真实 TM3 数据确定：

> 程序应该把 ASC 整理到什么程度，才既足够帮助 AI，又没有替 AI
> 提前做掉语义理解？

## 37.3 3B.2.6A

当前仅作为方向性名称：

``` text
PROVISIONAL / NOT YET AUTHORIZED

DBC-independent Full Observation
→ Deterministic Engineering Description
```

详细范围、输入输出、验收标准尚未冻结。

旧的 3B.2.6 草案不得自动视为当前正式设计。

------------------------------------------------------------------------

# 38. 当前最值得保留的一组短句

这些短句可以作为以后架构 Review 的快速检查表。

> **TeslaCanPython 的原始目的，是采集和分析 ASC，建立 Model 3
> 正常基线数据。**

> **系统理解是基础，通信是路径，推理是方法，控制树是目标。**

> **我们是在建立适合 AI 分析的程序，而不是把手伸进 LLM 里。**

> **程序整理事实，AI 理解语义。**

> **L3 决定要理解什么；ASC 决定实际发生了什么；DBC 帮助解释 Observation
> 可能是什么。**

> **L3 是 Semantic Prior，不是 Observation Whitelist。**

> **DBC 是 Reference / Decode / Validation Target，不是 Observation
> Admission Authority。**

> **Visibility 不等于 Relevance。**

> **Observation 不等于 Candidate。**

> **Candidate 不等于 Evidence。**

> **Finding 不等于 Approved Evidence。**

> **Program Validation 不等于 Semantic Correctness。**

> **Correlation / Timing Relation 不等于 Causality。**

> **缺失 Evidence 本身也是有效结果。**

> **Knowledge Source ≠ Working Context ≠ LLM Payload。**

> **大胆改 Retrieval 的结构，不要大胆调 Retrieval 的权重。**

> **006 的缺口不是 LLM 不够聪明，而是候选发现由人 + DBC
> 在程序外完成了。**

> **不是锤掉远见，而是锤掉把远见提前变成当前工作量的冲动。**

------------------------------------------------------------------------

# 39. Review 时建议重点检查的六个问题

本文下一轮 Review 不建议逐字润色，先判断六个根问题。

### Q1. 项目目的是否准确？

TeslaCanPython 是否仍应明确聚焦：

> Model 3 ASC → Evidence → Control Tree Instantiation → Baseline？

### Q2. Program / LLM 边界是否准确？

哪些 Engineering Facts 应由程序计算？

哪些判断必须留给 AI / Human？

### Q3. ASC / L3 / DBC 权限是否准确？

特别检查：

``` text
ASC = Observation Fact Source
L3 = Semantic Prior
DBC = Decode / Reference / Validation Target
```

是否存在需要修正的地方。

### Q4. Observation → Evidence 的认识论层级是否准确？

``` text
Observation
→ Candidate
→ Retrieved Observation
→ Finding
→ Evidence Binding Draft
→ Approved Evidence
```

哪些是当前实现，哪些是长期概念，是否需要进一步区分。

### Q5. Retrieval 是否描述得足够中立？

当前对 Retrieval 的问题已有明确认识，但最终替代结构尚未冻结。

本文是否避免了把讨论中的方向误写成正式结论？

### Q6. 是否还有"满汉全席"？

任何不能直接帮助：

-   Model 3 基线；
-   ASC 分析；
-   Evidence 可靠性；
-   Control Tree 实例化；

的设计，是否应该从基础共识中删除或降级为 PARKED？

------------------------------------------------------------------------

# 40. Review 后的预期用途

如果 Review 通过，建议不要把本文整篇直接变成一个新的"超级 Contract"。

可以按职责拆分：

``` text
长期稳定原则
→ Project Context / AGENTS / Methodology

当前工程状态
→ PROJECT_CURRENT_STATUS.md

详细历史考古
→ Historical / Archaeology docs

具体 Phase 任务
→ 独立 Phase Spec

L3 内容
→ knowledge/notion_l3/current/
```

本文本身可以保留为：

> **Architecture Consensus / Design Rationale**

它回答的是：

> **TeslaCanPython 为什么这样设计？**

而不是：

> **Codex 下一步具体应该执行什么命令？**

------------------------------------------------------------------------

# 结语

TeslaCanPython 当前真正需要保护的不是某一版 Retrieval、某一个 JSON
Schema 或某一个 Phase 编号，而是一组更稳定的设计原则：

``` text
真实 ASC 不丢
事实与语义分离
DBC 不垄断视野
L3 提供理解框架
Unknown 不被静默删除
程序做确定性工程压缩
AI 保留真正的语义判断空间
Evidence 有明确认识论边界
所有结论可追溯
缺失可以诚实地保持缺失
真实 TM3 数据驱动架构演进
```

在这些原则稳定的前提下：

> Retriever 可以改，Prompt 可以改，Candidate 组织可以改，LLM
> 可以换，Phase 可以迭代。

但项目不会因为局部实现变化而失去方向。

# 共识一张图

```
                         TeslaCanPython
                              │
                              ▼
                           Raw ASC
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
          Full Observation             Provenance
          all bus/ID/DLC                   │
                 │                         │
                 ▼                         │
        Generic Behavior Facts             │
                 │                         │
                 ▼                         │
       Change / Event / Relation Facts     │
                 │                         │
                 ▼                         │
              K / R / U                    │
                 │                         │
                 ▼                         │
        Candidate Compression ◄────────────┘
                 │
                 ▼
      Engineering Data Description
                 │
        ┌────────┼─────────┐
        │        │         │
        ▼        ▼         ▼
       L3      Script     DBC
 Semantic Prior Experiment Reference
        │        │         │
        └────────┼─────────┘
                 ▼
          Frozen LLM Input
                 │
                 ▼
       LLM Semantic Reasoning
                 │
                 ▼
       Evidence / Alternative /
       Gap / Conflict / Hypothesis
                 │
                 ▼
          Existing Human Review
                 │
                 ▼
        Model 3 Baseline Evidence
                 │
                 ▼
       Control Tree Instantiation
```

------------------------------------------------------------------------

**Review Draft v0.1 --- END**
