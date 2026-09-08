# TeslaCanPython 跨车型语义指纹与 Raw Evidence 演进备忘录

> **定位：Future Vision / 暂不进入当前 Phase 3B 实现范围**
>
> 这是一份"满汉全席"备忘录：记录 TeslaCanPython 在完成 Model 3
> 基线实例化之后，未来向无 DBC 车型 Signal
> 逆向工程、正常/故障差分诊断和跨车型语义行为指纹演进的可能方向。\
> 当前阶段只要求架构**不要堵死这条路**，不要求现在实现。

------------------------------------------------------------------------

## 1. 出发点

当前 TeslaCanPython 以 Tesla Model 3 为第一辆基线车型：

-   有 ASC 原始 CAN 数据；
-   有第三方 DBC，可提供高价值 Signal 语义候选；
-   有 L3 系统语义、控制树、状态变量和 Evidence Requirement；
-   有统一采集脚本与动作/事件锚点；
-   可以通过 Signal 间时序、数值、状态变化和物理关系进行交叉验证；
-   可以发现 DBC 定义与真实数据之间的冲突，并对 DBC Signal
    语义或定量定义降级。

Model 3 的长期价值不应只是得到一套"已知 DBC Signal 报告"，而应逐步形成：

> **经过 L3 语义解释和 Evidence 验证的车型控制行为实例。**

它未来可以成为其他无 DBC 车型分析时的高可信参考样板。

------------------------------------------------------------------------

## 2. 核心原则：箭头必须从语义指向数据

目标不是：

``` text
DBC Signal
    ↓
根据 Signal 名称猜语义
    ↓
往 L3 控制树中拼装
```

而是：

``` text
L3语义 + 控制树 + 采集脚本
              ↓
      本次实验在做什么
              ↓
      应观察哪些控制关系
              ↓
       需要哪些 Evidence
              ↓
        Observation Space
       ↙       ↓        ↘
 Known DBC  Residual   Unknown
       ↘       ↓        ↙
          AI关系发现
              ↓
 Signal角色 / Signal关系
              ↓
 ASC行为与物理一致性验证
              ↓
 DBC定义可信度反向检查
              ↓
 Evidence / Gap / Confidence
```

DBC 不是被抛弃。

DBC 应作为：

-   Semantic Dictionary
-   Candidate Generator
-   Decode Tool
-   Cross-DBC Comparison Source
-   Signal Hypothesis 的高价值先验

但不能成为问题定义器，也不能成为 Observation 的准入白名单。

一句话：

> **L3 定义"要理解什么"，采集脚本定义"这次做了什么"，ASC
> 告诉我们"实际发生了什么"，DBC
> 提供"它可能是什么"，推理负责判断"它到底有多可信、彼此是什么关系"。**

------------------------------------------------------------------------

## 3. 三层长期数据结构

未来车型知识不应只保存 Signal Definition，而应至少保留三层。

``` text
L3 Semantic Layer
        ↓
Vehicle Instance Layer
        ↓
Raw Signal / Evidence Layer
```

### 3.1 L3 Semantic Layer

描述跨车型相对稳定的问题域语义：

-   控制节点；
-   状态；
-   Capability；
-   Request；
-   Permission；
-   Command；
-   Feedback；
-   Actual；
-   Limit / Constraint；
-   Fault / Inhibit；
-   控制关系；
-   Evidence Requirement；
-   可观测 / 间接支持 / 未观测边界。

这一层不绑定 Tesla CAN ID，也不依赖某份 DBC。

### 3.2 Vehicle Instance Layer

描述某辆/某车型如何实例化 L3 控制语义。

例如 Model 3 快充可能观察到：

``` text
DC链路允许上电候选
    ↓
快充接触器闭合请求
    ↓
辅助触点闭合反馈
    ↓
高压充电阶段候选
    ↓
DC Voltage Actual
    ↓
DC Current Actual
```

其他车型的 ECU、CAN ID、bit 位置、Signal
名称完全可以不同，但仍可实例化同一 L3 控制关系。

### 3.3 Raw Signal / Evidence Layer

这是未来跨车型逆向工程和复杂故障 Diff 的关键资产。

应尽可能保存：

``` text
Experiment Context
Collection Script
Event Anchor

Raw Observation
├─ CAN ID / Channel / DLC / Raw Location
├─ 出现位置
├─ 状态迁移
├─ 数值范围
├─ 变化方向
├─ 变化速率
├─ 周期 / 频率
├─ 稳态特征
└─ 原始数据引用

Relationship
├─ 谁先谁后
├─ 时间间隔
├─ 同步 / 反向变化
├─ 数值约束
├─ 状态条件
├─ 重复性
└─ 物理一致性

Semantic Mapping
├─ 已确认角色
├─ 候选角色
├─ Alternatives
└─ Unknown

Validation
├─ DBC
├─ 多 DBC 横向定义
├─ 诊断仪
├─ 物理测量
├─ 跨 Signal 闭合
├─ 重复实验
└─ 正常 / 故障对照

Confidence / Provenance
```

------------------------------------------------------------------------

## 4. 为什么 Raw Evidence 本身就有诊断价值

未知 Signal 不必全部完成 DBC 级逆向定义后才能参与诊断。

对于正常车和故障车，只要执行：

-   相同车型或可比较车型；
-   相同采集脚本；
-   相同或可控制工况；
-   可靠动作/Event Anchor；

就可以比较控制行为。

例如：

``` text
正常车：
A ──→ B ──→ C ──→ D
     0.3s   4.8s   5.1s

故障车：
A ──→ B ──X
```

即使 A/B/C 尚不知道正式 Signal 名称，也已经得到重要事实：

> 故障差异发生在 B 之后、C 应出现而没有出现的控制阶段附近。

结合 L3 控制树、已知 Signal、诊断仪数据和其他
Evidence，可以进一步缩小故障边界。

因此未来存在两条相互独立、又相互增强的能力：

``` text
① Signal Reverse Engineering

Raw行为
  ↓
角色假设
  ↓
Signal关系
  ↓
DBC定义候选
  ↓
验证
```

``` text
② Fault Differential Diagnosis

正常Raw行为模板
        ↕ DIFF
故障Raw行为
        ↓
异常出现位置
        ↓
映射L3控制阶段
        ↓
故障边界
```

关键结论：

> **② 不要求 ① 已经完成。**

因此不能形成"必须先逆向完整 DBC，才能诊断"的新前置条件。

------------------------------------------------------------------------

## 5. 从 Signal Fingerprint 升级为 Control-Semantic Fingerprint

单个 Signal 的数值变化通常辨识力有限。

例如：

``` text
0 → 1
```

它可能代表：

-   Permission
-   Request
-   Enable
-   State
-   Contactor Command
-   Relay Feedback
-   Wake State

真正高价值的是**关系指纹**。

例如：

``` text
A变化
  ↓ 350 ms
B变化
  ↓ 4.7 s
DC Voltage建立
  ↓ 5.0 s
DC Current建立
```

再结合条件：

``` text
A只在连接成立后出现
B只在A成立后出现
稳态期间保持
主动停止时按一定顺序退出
```

这种：

-   时序关系；
-   状态关系；
-   数值关系；
-   条件关系；
-   物理关系；

组成的模式，比 CAN ID、bit 位置乃至 Signal
名称更可能具有跨车型迁移价值。

因此未来更准确的概念不是单纯：

> Signal Fingerprint Library

而是：

> **Normal Control Behavior Baseline / Control-Semantic Fingerprint
> Library**

------------------------------------------------------------------------

## 6. 相同采集脚本是跨车型比较的重要前提

采集脚本不是附属信息，而是实验设计的一部分。

例如快充实验：

``` text
未充电
  ↓
连接 / 启动快充
  ↓
通信 / 高压建立
  ↓
电流爬升
  ↓
稳定充电
  ↓
人工主动停止
  ↓
电流下降
  ↓
高压退出
```

相同实验刺激使 AI 可以比较不同车型：

-   哪些 Observation 在相同阶段出现；
-   哪些状态迁移具有相似先后关系；
-   哪些连续量具有相似建立/退出行为；
-   哪些未知字段只在特定控制条件下变化；
-   哪些关系在正常车稳定存在；
-   故障车在哪个阶段首次偏离正常模板。

因此未来跨车型逆向工程的核心不是：

``` text
Tesla Signal
    ↓
寻找国产车相似 Signal
```

而应该是：

``` text
            L3 Semantic Pattern
             ↙       ↓       ↘
        Model 3    车型A     车型B
           ↓         ↓         ↓
      Vehicle     Vehicle    Vehicle
      Instance    Instance   Instance
```

比较的是：

> **Semantic Role ↔ Behavior Pattern**

而不是：

> Tesla CAN Signal ↔ 国产 CAN Signal

------------------------------------------------------------------------

## 7. 无 DBC 车型的未来推理方式

面对无 DBC 车型，AI 可能只看到：

``` text
0x3A2 byte2-3
0x417 bit5
0x2D1 bytes4-5
...
```

但通过统一采集脚本，可以计算和观察：

-   时间指纹；
-   状态迁移指纹；
-   数值形态；
-   出现阶段；
-   与其他未知量的先后关系；
-   同步 / 反向变化；
-   物理约束；
-   与已实例化车型 Semantic Pattern 的相似性。

由此提出：

``` text
Raw Candidate
      ↓
Candidate Semantic Role
      ↓
Relationship Hypothesis
      ↓
Alternative Explanations
      ↓
Cross-Signal Validation
      ↓
External Corroboration
      ↓
Confidence
```

重要边界：

> **AI 不应直接"猜 Signal"，而应提出并验证 Signal Hypothesis。**

例如某未知 bit：

``` text
建立前 = 0
建立后 = 1
稳态 = 1
停止后 = 0
```

正确输出不是：

> 这是 Charge Permission。

而应类似：

``` text
Observed Behavior
      ↓
与某些L3控制角色相容
      ↓
Candidate:
Permission / Enable / State
      ↓
检查上下游时序关系
      ↓
寻找重复实验和反例
      ↓
检查其他DBC/诊断仪/物理Evidence
      ↓
仍无法区分
      ↓
保留Alternatives并提出下一步验证
```

即使最终仍是
`Unknown Candidate U052`，只要它已经被定位到某个控制阶段并建立了关系假设，就已经产生工程价值。

------------------------------------------------------------------------

## 8. SavvyCAN + 诊断仪 + Raw CAN 的未来组合

对于无 DBC 车型，成熟诊断仪可以成为重要外部 Evidence。

例如：

``` text
诊断仪：
快充接触器请求 = ON

同时Raw CAN：
0xXYZ bit3 = 0 → 1
```

如果在多个相同实验中稳定重复：

``` text
诊断仪状态
     +
Raw Candidate变化
     +
L3控制阶段
     +
上下游时序关系
        ↓
Candidate Role Confidence ↑
```

未来可形成：

``` text
统一采集脚本
      +
SavvyCAN / Raw CAN
      +
诊断仪实时数据
      +
人工动作时间锚点
      +
必要的物理测量
      ↓
弱监督式 Signal Reverse Engineering
```

诊断仪不是"DBC替代品"，而是独立 Evidence Source。

------------------------------------------------------------------------

## 9. Model 3 的真正长期资产

TM3-006、TM3-015 等正常车实验的长期价值，不应只理解为最终四件套报告。

真正值得长期保存的是报告下面那一层：

> **Vehicle Control Behavior Baseline**

它应能够支持未来：

``` text
车型实例化
    ↓
Semantic Behavior Pattern
    ↓
无DBC Signal Discovery
    ↓
正常 / 故障 Diff
    ↓
L3故障边界定位
    ↓
Signal Hypothesis Validation
```

因此：

> **报告是给人看的；结构化的行为基线才是未来给 AI 推理的粮食。**

------------------------------------------------------------------------

## 10. 可能的长期演进路线

``` text
阶段1
Model 3 + DBC
→ 建立可信车型实例
→ 当前主要工作
```

``` text
阶段2
车型实例
→ 提炼 Semantic Behavior Pattern
→ Normal Control Behavior Baseline
```

``` text
阶段3
无DBC车型 + 相同采集脚本
→ Raw Observation Discovery
→ Unknown Signal / Role Hypothesis
```

``` text
阶段4
SavvyCAN + 诊断仪 + 重复实验 + 必要物理Evidence
→ Signal Hypothesis Validation
→ 车型控制树实例化
```

``` text
阶段5
多车型实例
→ Cross-Vehicle Control-Semantic Fingerprint Library
→ 更强的无DBC逆向工程与故障Diff
```

随着有标签车型实例增加，系统应逐渐降低对单一 DBC 的依赖，但始终允许 DBC
作为高价值语义先验参与推理。

------------------------------------------------------------------------

## 11. 对当前 TeslaCanPython 的 Future-Proof 要求

这份备忘录**不要求当前 Phase 3B 实现跨车型系统**。

当前只应确保架构不会丢掉未来需要的基础资产。

尤其避免在最终报告生成后丢弃：

-   Raw Observation reference；
-   Experiment Phase；
-   Event Anchor；
-   状态迁移；
-   数值范围；
-   时间关系；
-   Signal 间关系；
-   物理一致性结果；
-   Semantic Role；
-   Candidate Role；
-   Alternatives；
-   Validation Basis；
-   Confidence；
-   Provenance；
-   Known DBC / Residual / Unknown 身份。

当前版本不需要建立：

-   跨车型模型；
-   Fingerprint 数据库；
-   自动无 DBC 逆向系统；
-   SavvyCAN 自动控制；
-   诊断仪自动同步；
-   AI 训练流水线。

原则是：

> **现在不摆这桌菜，但厨房的地基不要盖在未来灶台的位置上。**

------------------------------------------------------------------------

## 12. 与当前 L3 / Semantic Discovery 重构的关系

当前正在解决的问题仍然是：

``` text
L3 Semantic Need
        ↓
Experiment Intent
        ↓
Evidence Need
        ↓
完整 Observation Space
        ↓
Known DBC + Residual + Unknown
        ↓
Semantic-directed Discovery
        ↓
Signal / Relationship Hypothesis
        ↓
Validation
        ↓
Evidence
```

这条链如果在 Model 3 上建立正确，未来才能自然扩展到无 DBC 车型。

因此当前最重要的不是提前实现跨车型功能，而是确保：

> **今天的 Model 3 实例化结果，可以在未来作为跨车型 Semantic
> Fingerprinting 的训练/参考样本，而不是只生成一份车型报告。**

------------------------------------------------------------------------

## 13. 最终备忘

未来 TeslaCanPython 可能不只是：

> "根据 DBC 分析 CAN 数据的报告工具。"

它有机会演进成：

> **以 L3 控制语义为坐标，以标准化实验为刺激，以 Raw CAN 为
> Observation，以 DBC/诊断仪/物理测量为多源
> Evidence，通过时序、状态、数值和控制关系建立车型实例，并利用正常行为基线进行无
> DBC Signal 逆向与复杂故障差分定位的 AI 辅助诊断系统。**

但当前阶段保持克制：

> **先把 Model 3 这一辆车、一个实验、一个 Semantic Discovery
> 闭环做正确。**

等基础真正稳定，再回来开这桌"满汉全席"。

------------------------------------------------------------------------

**状态：PARKED / FUTURE VISION**\
**当前不进入 Phase 3B Scope。**
