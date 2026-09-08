# TeslaCanPython Observation 算法核心：新能源车 CAN 数据行为覆盖与验证原则

> 状态：学习理解文档\
> 目的：理解 `Observation` 层为什么这样分析 CAN
> 数据、目前覆盖了哪些数学/行为类型、还存在哪些边界，以及后续应该怎样通过真实
> TM3 实验验证，而不是提前堆叠算法。

------------------------------------------------------------------------

## 1. Observation 层到底在做什么

TeslaCanPython 的 Observation 层首先不是在回答：

> "这个 CAN Signal 是什么？"

而是在回答：

> "这份 ASC 中客观存在什么数据，它们以什么数学和时间行为变化？"

因此它位于语义解释之前：

``` text
Raw ASC
   ↓
Full Observation
   ↓
Deterministic Engineering Facts
   ↓
Candidate / Engineering Data Description
   ↓
L3 + Experiment + DBC Reference
   ↓
LLM Semantic Reasoning
```

Observation 层的核心职责是：

1.  尽可能完整地观察 ASC；
2.  把大量原始 CAN Frame 压缩成确定性的工程事实；
3.  不提前决定 Signal 的控制语义；
4.  保留 Provenance，使派生事实可以追溯到原始 ASC；
5.  为后续 Retrieval 和 LLM 提供足够丰富、但不过度语义化的数据表达。

核心原则：

> **程序负责压缩数据量，不应过度压缩语义可能性。**

------------------------------------------------------------------------

## 2. 为什么要从"数学行为类型"理解新能源车 CAN

新能源车虽然包含电池、电驱、充电、热管理、车身等不同系统，但从 CAN
数据本身来看，大量 Signal 可以归纳为有限的行为形态。

例如：

-   SOC 是连续缓变量；
-   电流、转速是连续动态变量；
-   接触器状态是二值状态；
-   Charge State 是枚举状态；
-   Rolling Counter 是周期计数；
-   Fault Word 是 Bitfield；
-   充电请求建立可能表现为 Step；
-   电流建立可能表现为 Ramp；
-   保护动作可能表现为 Pulse。

因此 Observation 不必先知道：

> "这是 BMS 还是 OBC。"

它首先可以知道：

> "这是一个稳定量、连续量、状态量、周期量、突变量还是某种关系型数据。"

这就是 DBC-independent Observation 的数学基础。

------------------------------------------------------------------------

## 3. 当前主要 CAN 行为类型及覆盖情况

  -------------------------------------------------------------------------------------------
  数学 / 行为类型         新能源车典型例子              当前 Observation 能力
  ----------------------- ----------------------------- -------------------------------------
  连续缓变量              SOC、温度、电压               已基本覆盖

  连续快变量              电流、扭矩、转速、功率        已基本覆盖

  二值状态                接触器、许可、Ready           已基本覆盖

  多状态枚举              Gear、Charge State、Mode      已基本覆盖

  Counter                 Rolling Counter               基本可识别周期变化

  Heartbeat               Alive、周期状态               基本可见

  Bitfield                Fault / Status Word           已有 Bit activity / transition

  固定常量                Capability、Config、Version   已覆盖稳定性/cardinality

  Step / Edge             请求建立、接触器动作          基本覆盖 change / transition

  Ramp                    电流建立、扭矩爬升            部分覆盖，形态表达仍可验证

  Oscillation             闭环波动、周期控制            基础统计可见，形态表达有限

  Pulse / Transient       短时请求、保护动作            部分覆盖

  累计量                  能量计数、里程                基础变化可见，单调性/增量特征可验证

  Target / Actual         请求电流 vs 实际电流          单变量层可见，generic relationship
  Tracking                                              尚需验证

  物理关系                P≈V×I                         适合 Specialized Reducer

  Multiplex / Conditional 同 ID 多页/多模式数据         Known DBC 可辅助，Unknown 是潜在盲区
  Payload                                               

  Unknown Packed Field    无 DBC 的未知位段             可做行为 fingerprint，不等于自动
                                                        Signal Discovery
  -------------------------------------------------------------------------------------------

因此当前更准确的判断是：

> **Observation 已覆盖新能源 CAN
> 的主要基础行为类型，足够进入真实实验验证；但尚不能宣称数学行为完备。**

------------------------------------------------------------------------

# 4. 四类特别值得关注的行为盲区

## 4.1 "发生变化"与"怎样变化"不是一回事

下面四种 Signal 都可能拥有相同的最小值和最大值：

``` text
A. Step

0 ─────────┐
           └──────── 16


B. Ramp

0 ───────╱╱╱╱╱────── 16


C. Oscillation

0 ─────╱\/\/\/╲────── 16


D. Pulse

0 ─────────▲────────── 0
```

仅有：

``` text
min
max
mean
change_count
```

并不足以完全区分它们。

未来如果真实实验表明现有表达不足，可以考虑增加：

``` text
slope / derivative
monotonicity
ramp duration
pulse width
oscillation / periodicity
```

但是这些不是现在必须全部实现的功能。

正确顺序应是：

``` text
现有算法
   ↓
真实 TM3 数据验证
   ↓
发现明确 Blind Spot
   ↓
补充最小必要特征
```

而不是先建立一套"CAN 数学特征全集"。

------------------------------------------------------------------------

## 4.2 Counter / Heartbeat 是典型的"高变化假目标"

Rolling Counter：

``` text
0 → 1 → 2 → 3 → 4 → 5 → ...
```

通常具有：

``` text
change_count = 很高
cardinality = 很高
bit activity = 很高
```

但它未必具有我们关心的控制语义。

相反，一个真正重要的控制状态可能只是：

``` text
Charge Request

0 0 0 0 0 1 1 1 1 1
```

它只变化一次。

因此：

> **变化强度不能直接等于语义重要度。**

在 TM3-015 Observation / Retrieval 验证中，应特别检查：

-   Counter 是否大量占据 Candidate；
-   Heartbeat 是否因为周期变化获得过高排名；
-   Checksum / rolling field 是否形成假"强变化"；
-   真正低频但关键的状态变化是否被压低。

------------------------------------------------------------------------

## 4.3 Multiplex / Conditional Payload 是 Unknown 数据的重要风险

典型结构：

``` text
CAN ID 0x123
│
├─ Mode = 0
│   └─ Byte1~4 = A 类数据
│
├─ Mode = 1
│   └─ Byte1~4 = B 类数据
│
└─ Mode = 2
    └─ Byte1~4 = C 类数据
```

如果不知道 Mode / MUX：

``` text
Byte1
  ↓
大量跳变
  ↓
高 Cardinality
  ↓
高 Entropy
```

程序可能错误地把它理解成：

> "一个变化非常复杂的字段。"

实际上它可能是：

> "多个不同语义字段共享同一 Payload 区域。"

对于 Known Message，DBC 的 MUX 定义可以帮助解释。

对于 Unknown Message，则应该至少意识到：

> 某些复杂 Payload 可能存在 Conditional Regime / Multiplex Behavior。

但这里必须控制边界。

当前阶段不应该因此立即建设：

-   通用 MUX Reverse Engineering；
-   自动未知 Signal 切片；
-   自动 DBC 生成；
-   自动 Signal 命名。

这会迅速把 Model 3 基线项目变成通用 CAN 逆向工程平台。

------------------------------------------------------------------------

## 4.4 新能源控制大量依赖"关系"，而不只是单 Signal

### Request / Actual

``` text
Request Current ──────┐
                      ├── Tracking
Actual Current  ──────┘
```

### 物理关系

``` text
Pack Voltage
      ×
Pack Current
      ↓
Pack Power
```

### 时序关系

``` text
Permission
    ↓  Δt1
Contactor
    ↓  Δt2
Current Establishment
```

单独看三个 Signal：

``` text
Signal A changed
Signal B changed
Signal C changed
```

信息有限。

更有价值的是确定性关系事实：

``` text
A 与 B 相差 320 ms
B 与 C 相差 180 ms
A/B 在多个事件中共同变化
Actual 跟踪 Request
P 与 V×I 在误差范围内一致
```

这里的架构边界非常重要：

> **程序可以计算 Relationship Facts，但不应该直接宣布 Relationship
> Semantics。**

例如程序可以说：

``` text
OBS-A 0→1 后 320 ms，OBS-B 0→1
```

但不能仅凭这一事实直接宣布：

``` text
A 是充电许可
A 导致接触器闭合
```

后者属于 L3 + 实验上下文 + LLM / 人工推理。

------------------------------------------------------------------------

# 5. Specialized Reducer 为什么仍然重要

Generic Observation 不应该取代所有领域工程分析。

例如：

``` text
Pack Voltage × Pack Current ≈ Pack Power
```

或者：

``` text
Brick Voltage Max
Brick Voltage Min
Brick Voltage Span
```

这些属于具有明确物理意义的工程关系。

因此合理架构不是：

``` text
Generic Observation
→ 取代全部专用分析
```

而是：

``` text
                  Full Observation
                        │
          ┌─────────────┴─────────────┐
          ↓                           ↓
 Generic Behavior Facts      Specialized Reducers
          │                           │
          └─────────────┬─────────────┘
                        ↓
           Engineering Data Description
```

TM3-006 已经证明 Specialized Engineering Compression 很有价值。

需要修正的是它过去"先由人 + DBC 决定观察哪些 CAN
ID"的入口，而不是抛弃其成熟的工程 reducer。

------------------------------------------------------------------------

# 6. Observation 不等于 Signal Reverse Engineering

这一点必须严格区分。

``` text
Full CAN Observation
≠
Full Unknown Signal Discovery
```

对 Unknown CAN，目前合理目标是：

``` text
CAN ID / DLC
Frame Count
Payload Cardinality
Byte Cardinality
Changing Bits
Bit Transition
Bit Activity
Time Distribution
Stable / Dynamic Behavior
Possible Periodic Behavior
Raw Provenance
```

这些形成：

> **Unknown Behavior Fingerprint**

而不是直接形成：

``` text
Byte2 bit3~5 = Charge Permission
```

后者已经进入 Signal Reverse Engineering 和 Semantic Claim。

因此 Observation 层的价值不是"自动破解所有 CAN"，而是：

> **即使不知道 Signal 名称，也不让这部分真实数据从 AI 的视野中消失。**

------------------------------------------------------------------------

# 7. Observation 的真正目标不是数学完备

不存在一个现实可行的：

> "新能源车 CAN 所有可能数学行为全集。"

CAN 中还可能出现：

-   编码计数；
-   校验字段；
-   非线性映射；
-   Lookup-table 状态；
-   多帧协议；
-   压缩字段；
-   Proprietary Encoding；
-   Rolling Key；
-   Gateway Transform；
-   多层 MUX；
-   Event-dependent Sampling。

如果把"覆盖所有可能 CAN 编码"作为 Observation
的完成条件，项目会无限扩张。

TeslaCanPython 当前真正需要的是：

> **对于 Model 3 基线实验中具有诊断价值的 CAN 行为，Observation
> 是否提供了足够的事实表达，使后续 AI 能够发现和解释它们。**

因此评价标准应该从：

``` text
算法覆盖了多少数学方法？
```

转变成：

``` text
重要的真实行为有没有因为 Observation 表达不足而消失？
```

------------------------------------------------------------------------

# 8. TM3-015 应如何验证 Observation

下一次 TM3-015 Observation + Retrieval 验证，可以重点检查以下五类问题。

## ① 基础行为是否充分

检查：

``` text
Stable
Continuous
Discrete
Enum
Bitfield
Step
```

是否能够从 Observation 中明显看出来。

------------------------------------------------------------------------

## ② Step / Ramp / Pulse 是否可以区分

选择几个真实动态 Signal，观察现有 Summary 是否足以让人或 AI 区分：

``` text
突变
缓慢建立
短暂脉冲
周期波动
```

如果不能，再决定是否增加 slope / duration 等特征。

------------------------------------------------------------------------

## ③ Counter / Heartbeat 是否制造假强候选

检查：

``` text
Counter
Heartbeat
Checksum-like field
Paging
```

是否因为高 change_count / bit activity 被 Candidate 或 Retrieval
过度放大。

------------------------------------------------------------------------

## ④ Unknown / Residual 是否存在 Conditional / MUX 盲区

重点观察：

``` text
高 cardinality
复杂 bit activity
明显存在多个数据 regime
```

但现有统计无法合理描述的 Unknown。

这里首先记录 Blind Spot，不立即开发通用 MUX Reverse Engineering。

------------------------------------------------------------------------

## ⑤ 跨 Observation 关系是否足够

检查真实实验中重要的：

``` text
A → B
Request ↔ Actual
V × I ≈ P
状态变化时间差
共同变化
```

现有数据是否足够支持后续 LLM 做语义推理。

如果不够，应优先考虑增加确定性的 Relationship Facts，而不是继续堆大量单
Signal 指标。

------------------------------------------------------------------------

# 9. Observation 算法发展的正确路线

推荐路线：

``` text
Raw ASC
   ↓
Full CAN Census
   ↓
Generic Behavior Fingerprint
   ↓
Change / Event Facts
   ↓
K / R / U
   ↓
Candidate Compression
   ↓
Relationship Facts
   ↓
Specialized Engineering Reducers
   ↓
Engineering Data Description
   ↓
LLM Semantic Reasoning
```

其中 Provenance 应贯穿所有派生对象：

``` text
Raw ASC
   │
   ├── Observation
   │      ↓
   ├── Behavior Fact
   │      ↓
   ├── Change / Event Fact
   │      ↓
   ├── Candidate
   │      ↓
   └── Engineering Data Description

Provenance:
每一层均可追溯回原始 ASC
```

Provenance 不是另一个 Observation 来源，而是整个派生链的可追溯属性。

------------------------------------------------------------------------

# 10. Program 与 LLM 的边界

Observation 层尤其需要守住这个边界。

## Program 应该做

``` text
统计
变化检测
时间点
Cardinality
Bit Activity
Transition
稳定区间
数值关系
时间关系
物理公式计算
Provenance
```

这些属于：

> **Engineering Facts**

## Program 不应该越权做

``` text
“这是充电许可”
“这是接触器命令”
“这是 BMS 请求”
“这个 Signal 导致了那个动作”
“这个 Unknown Bit 就是 S2”
```

这些属于：

> **Semantic Claims**

应该由：

``` text
Engineering Facts
+ L3 Semantic Prior
+ Experiment Context
+ DBC Reference
        ↓
       LLM
```

进行解释。

------------------------------------------------------------------------

# 11. 当前阶段结论

目前 Observation 层可以做出三个判断。

### 判断一：基础能力已经足够进入验证

当前已经覆盖新能源车 CAN 中最常见的：

``` text
连续量
状态量
枚举量
Bitfield
稳定量
变化量
周期行为
Unknown Bit Activity
DBC Residual
```

因此没有理由因为"理论上还可能缺算法"而停止真实 TM3 验证。

### 判断二：仍存在需要真实数据验证的边界

重点包括：

``` text
Ramp / Pulse / Oscillation 的形态表达
Counter / Heartbeat 的假强变化
Unknown Multiplex / Conditional Regime
跨 Signal / Observation Relationship
```

### 判断三：现在不应该提前补齐这些能力

正确方法：

``` text
现有 Observation
        ↓
TM3-015 实际验证
        ↓
发现真实 Blind Spot
        ↓
形成明确失败案例
        ↓
只增加最小必要算法
        ↓
再次 Replay
```

这符合 TeslaCanPython 当前的开发原则：

> **Hypothesis → Implement → Run TM3 → Inspect → Keep / Modify /
> Revert**

------------------------------------------------------------------------

# 12. 最重要的理解

Observation 算法的目标不是：

> **把 CAN 数据"理解完"。**

而是：

> **在不提前替 AI 做语义判断的前提下，把海量 Raw CAN
> 压缩成足够丰富、准确、可追溯的工程事实。**

因此它追求的不是：

``` text
Mathematical Completeness
```

而是：

``` text
Semantic Opportunity Preservation
+
Engineering Fact Quality
+
Traceability
```

最终判断 Observation 是否优秀，不应该问：

> "我们实现了多少种统计方法？"

而应该问：

> **"真实实验里有诊断价值的行为，有没有因为程序的观察和压缩方式而从 AI
> 的视野中消失？"**

如果没有，它就是有效的 Observation。

如果有，就用那个真实 Blind Spot 驱动下一次最小改进。

------------------------------------------------------------------------

## 一句话总结

> **Observation 的核心不是替 AI 看懂 CAN，而是保证 AI 有机会看懂 CAN。**
