# TeslaCanPython CAN 盲猜逆向能力优化：思路、实现路径、原则与学习资料

> 状态：阶段方法论 / 算法优化路线\
> 目标：以已有真实 TM3 动态采集为训练与 Benchmark，优先验证并提升
> **No-DBC + Event-driven CAN Reverse Engineering** 能力。\
> 核心判断：如果无法在不使用 DBC 答案的条件下，将原始 CAN
> 数据稳定压缩为少量高质量 Signal Candidate，则 TeslaCanPython
> 的跨车型自主 Discovery
> 目标需要重新评估；因此该能力属于当前项目的地基能力之一。

------------------------------------------------------------------------

## 1. 为什么现在优先做 CAN 盲猜逆向

TeslaCanPython 已经建立了较完整的 Discovery / Observation / Semantic
Reasoning / Evidence Mapping
架构，但当前更关键的问题不是继续增加上层合同，而是验证底层 Candidate
Discovery 是否足够强。

如果底层只能产生大量低质量 Candidate，那么：

``` text
低质量 Candidate
    ↓
Semantic Reasoning
    ↓
Evidence Mapping
    ↓
Human Review
```

上层越规范，只会把低质量候选管理得更规范，并不会提高真正的发现能力。

因此当前优先问题应收敛为：

> **在完全屏蔽 DBC 答案的情况下，TeslaCanPython 能否仅依赖
> ASC、实验脚本和事件时间轴，将真实目标 Signal 稳定排入 Top-N
> Candidate？**

第一阶段不追求完整 DBC 自动生成，不追求所有 CAN RE
算法一次实现，不追求跨车型泛化证明。

先把一颗钉子钉穿。

------------------------------------------------------------------------

## 2. 第一训练样本：驾驶门开关

优先使用之前已经完成的一版 Model 3 驾驶门开关动态采集。

选择它的原因：

-   二值状态清楚；
-   OPEN / CLOSE 可逆；
-   人工动作时间明确；
-   可以多次重复；
-   已有采集脚本；
-   已有 ASC；
-   已有基于 Tesla DBC 的明猜结果；
-   可以形成可靠 Ground Truth；
-   之前已有一版盲拆程序和候选 ID，可直接形成 V0 Baseline；
-   当前盲猜虽然能够推荐若干 ID 范围，但命中率 /
    排名质量还不够好，正适合作为算法优化样本。

第一阶段只做：

> **Driver Door Open / Close**

暂不同时扩展四门、挡位、制动、加速、慢充等题型。

------------------------------------------------------------------------

## 3. 两条通道必须严格隔离

### 3.1 Blind Track

``` text
ASC
  +
采集脚本
  +
人工事件时间轴
  ↓
Blind CAN Observation
  ↓
Frame / Byte / Bit Analysis
  ↓
Candidate Generation
  ↓
Candidate Ranking
  ↓
Blind Result
```

Blind Track 运行时不得读取：

-   Tesla DBC；
-   已知 Signal 名称；
-   Ground Truth CAN ID；
-   Ground Truth start bit / length；
-   Ground Truth endian / signedness；
-   历史人工结论；
-   历史报告中的正确答案；
-   为该实验专门编写的目标 ID 白名单。

------------------------------------------------------------------------

### 3.2 Ground Truth Track

``` text
同一份 ASC
  +
Tesla DBC
  +
采集脚本 / 时间轴
  +
人工核验
  ↓
Known Signal Decode
  ↓
Ground Truth
```

Ground Truth 可以包含：

-   正确 CAN ID；
-   正确 Signal；
-   start bit；
-   length；
-   endian；
-   signed / unsigned；
-   OPEN / CLOSE 对应 raw / physical value；
-   事件响应时间；
-   重复动作一致性；
-   必要的人工确认说明。

------------------------------------------------------------------------

### 3.3 两条通道唯一汇合点：Evaluation

``` text
Blind Result ─────┐
                  ├─→ Evaluation
Ground Truth ─────┘
```

核心原则：

> **Ground Truth 用于评分，不用于提示。**

> **DBC 在开发期当老师，在运行期退出考场。**

------------------------------------------------------------------------

## 4. 防止 Ground Truth 污染

算法学习允许研究 Ground Truth 失败案例，但必须避免"看答案改题"。

允许：

-   分析为什么正确 Candidate 排名过低；
-   分析现有 feature 对某类事件不敏感；
-   研究通用 CAN RE 方法；
-   引入对所有实验都成立的通用 feature；
-   用多个训练样本验证改进；
-   比较算法版本前后的 Benchmark 分数。

禁止：

-   因为知道正确 ID 而加入该 ID 的优先规则；
-   因为知道正确 bit 而人为设计只适合该 bit 的权重；
-   把 DBC Signal 名称传入 Blind Track；
-   把历史正确候选作为白名单；
-   把 Ground Truth 的物理值用于运行时筛选；
-   为单个 TM3 样本建立隐性车型专用规则。

原则：

> **算法优化依据失败模式，不依据答案本身。**

------------------------------------------------------------------------

## 5. 第一阶段 Benchmark 指标

不要再用"发现了一些有意义 Candidate"作为成功标准。

每个版本至少记录：

``` text
Top-1 命中？
Top-3 命中？
Top-5 命中？
Top-10 命中？

正确 CAN ID 排名
正确 byte / bit-field 排名
OPEN / CLOSE 方向一致性
重复事件命中一致性
事件响应延迟稳定性
False Positive 数量
Candidate 总量
```

后续进入 Field Inference 后增加：

``` text
start_bit 是否正确
length 是否正确
endianness 是否正确
signedness 是否正确
raw state mapping 是否正确
```

最终希望看到的是可量化的版本演进，例如：

``` text
V0  正确 ID Rank = 17
 ↓
V1  Rank = 8
 ↓
V2  Rank = 3
 ↓
V3  ID Rank = 1 / bit-field Rank = 2
```

只有 Benchmark 提升才算算法进步。

------------------------------------------------------------------------

## 6. CAN RE 能力分层

不要把"盲猜 Signal"看成一个动作，应拆成几个层次。

### Layer 1：Frame Discovery

回答：

> 哪些 CAN ID 与目标事件最相关？

可能使用：

-   周期 / jitter；
-   DLC；
-   event-window change；
-   pre/post distribution；
-   change count；
-   transition timing；
-   event repetition consistency；
-   OPEN / CLOSE reversibility。

------------------------------------------------------------------------

### Layer 2：Byte / Bit Discovery

回答：

> 这个 CAN ID 中究竟哪些 byte / bit 在表达事件？

可能使用：

-   byte entropy；
-   bit flip rate；
-   bit transition；
-   state count；
-   change localization；
-   bit-level event correlation；
-   repeated-event consistency。

------------------------------------------------------------------------

### Layer 3：Signal Boundary / Field Inference

回答：

> 哪些连续 bit 应当组成一个 Signal？

目标逐渐推断：

``` text
start_bit
length
endianness
signed / unsigned
```

这里重点参考 READ、CAN-D、ACTT、ByCAN 等研究。

------------------------------------------------------------------------

### Layer 4：Behavior Classification

判断 Candidate 更像：

``` text
boolean
enum
continuous
counter
checksum
bitfield
step
ramp
pulse
noise / unrelated
```

------------------------------------------------------------------------

### Layer 5：Semantic Hypothesis

到这里才进入：

``` text
Experiment Context
+
L3 Semantic Prior
+
Candidate Behavior
+
Control Tree
+
Known Baseline（若运行模式允许）
↓
LLM Semantic Reasoning
```

LLM 不负责从百万帧中直接搜索模式。

------------------------------------------------------------------------

## 7. Python 与 LLM / Codex 的职责边界

### Python / deterministic program 负责

-   ASC parsing；
-   CAN ID / BusKey aggregation；
-   DLC statistics；
-   frame timing；
-   byte / bit transition；
-   entropy；
-   event-window statistics；
-   pre/post comparison；
-   repeated-event consistency；
-   correlation；
-   lag；
-   candidate scoring；
-   signal-boundary feature；
-   raw frame alignment；
-   provenance；
-   Benchmark evaluation。

### Codex / LLM 负责

-   阅读 CAN RE 资料；
-   分析当前算法失败模式；
-   自主选择适合当前实验的通用算法；
-   设计和实现改进；
-   对 Candidate 做工程语义解释；
-   提出 Validation Proposal；
-   解释算法为何改善或退化；
-   判断哪些算法值得保留。

原则：

> **Python 做确定性计算；Codex 负责工程选择与语义推理。**

------------------------------------------------------------------------

## 8. 不提前固定一张"算法菜单"

以下 feature 是候选工具，不是新的 HARD CONTRACT：

``` text
CAN_ID
├─ 周期 / jitter
├─ DLC
├─ byte entropy
├─ bit flip rate
├─ change count
├─ transition time
├─ event-window delta
├─ pre/post action distribution
├─ monotonicity
├─ counter likelihood
├─ checksum likelihood
├─ cross-ID correlation
├─ lag correlation
└─ known-signal similarity
```

对于可能的 bit field：

``` text
Candidate Signal
├─ start_bit
├─ length
├─ little/big endian
├─ signed/unsigned
├─ raw time series
├─ entropy
├─ state count
├─ action correlation
├─ reference correlation
├─ temporal alignment score
└─ confidence / evidence
```

这些是专业知识空间，不要求第一轮全部实现。

应让 Codex根据：

``` text
当前 Benchmark 失败模式
        ↓
研究成熟方法
        ↓
判断缺少什么信息
        ↓
只增加有明显信息增益的通用算法
```

而不是提前把几十项 feature 全部写成强制要求。

------------------------------------------------------------------------

## 9. Codex 的逐步学习路线

推荐采用：

``` text
Baseline V0
现有盲拆算法
    ↓
冻结成绩

Study 1
CSS Electronics + READ
    ↓
Codex 自主提出最小算法改进
    ↓

V1 Blind Test
    ↓
Benchmark

Study 2
CAN-D + ACTT
    ↓
V2 Blind Test
    ↓
Benchmark

Study 3
ByCAN + SavvyCAN
    ↓
V3 Blind Test
    ↓
Benchmark
```

每轮要求：

1.  先记录旧版本成绩；
2.  明确失败模式；
3.  阅读针对性资料；
4.  Codex 自主提出改进；
5.  只实现必要算法；
6.  Blind Track 重新运行；
7.  Ground Truth 仅在 Evaluation 阶段打开；
8.  比较成绩；
9.  提升则保留；
10. 无提升或产生明显副作用则回退 / 调整。

原则：

> **只接受 Benchmark 提升，不接受"看起来更先进"。**

------------------------------------------------------------------------

## 10. 学习资料优先级

### 第一梯队：直接用于当前算法学习

#### 10.1 CSS Electronics --- CAN Bus Reverse Engineering Skills

GitHub：

https://github.com/CSS-Electronics/can-bus-reverse-engineering-skills

重点：

``` text
survey
↓
correlate
↓
bitsearch
↓
build_dbc
↓
verify
```

学习价值：

-   AI + Python CAN RE 工作流；
-   continuous / discrete signal；
-   bit search；
-   counter；
-   checksum-like；
-   sub-byte / non-byte-aligned signal；
-   DBC reconstruction；
-   verification。

定位：

> 实践老师 / CAN RE Skill 原型。

------------------------------------------------------------------------

#### 10.2 READ --- Reverse Engineering of Automotive Data Frames

论文：

https://doi.org/10.1109/TIFS.2018.2870826

重点学习：

-   bit flip rate；
-   bit-level statistics；
-   signal boundary inference；
-   payload segmentation；
-   使用真实车辆规范作为 Ground Truth 的评估思想。

与当前项目高度相关：

> 从"哪个 ID 可疑"继续深入到"这个 ID 中哪个 bit-field 才是真正 Signal"。

------------------------------------------------------------------------

#### 10.3 CAN-D --- A Modular Four-Step Pipeline for Comprehensively Decoding CAN Data

论文：

https://arxiv.org/abs/2006.05993

重点：

``` text
Signal
├─ Boundary
├─ Endianness
├─ Signedness
└─ Physical interpretation
```

价值：

> 为完整 CAN Signal Reverse Engineering 提供问题分解地图。

------------------------------------------------------------------------

#### 10.4 ACTT --- Automotive CAN Tokenization and Translation

论文：

https://arxiv.org/abs/1811.07897

重点：

-   CAN payload tokenization；
-   自动 bit grouping；
-   reference / diagnostic information 与 CAN field 的映射；
-   从 bit pattern 到 physical meaning 的桥梁。

与 TeslaCanPython 的关系：

> Ground Truth 可以作为开发教师，但不能进入 Blind Track。

------------------------------------------------------------------------

#### 10.5 ByCAN

论文：

https://arxiv.org/abs/2408.09265

重点：

-   bit-level feature；
-   byte-level feature；
-   clustering；
-   template matching；
-   signal slicing。

价值：

> 防止只依赖单一 bit-flip 思路，学习多层特征融合。

------------------------------------------------------------------------

### 第二梯队：工程实现与未来扩展参考

#### 10.6 SavvyCAN

官网：

https://www.savvycan.com/

GitHub：

https://github.com/collin80/SavvyCAN

重点研究：

-   coherent data scanning；
-   graphing；
-   frame filtering；
-   RE tools；
-   实际工程筛选策略。

原则：

> 学习算法思想，不复制 SavvyCAN 架构。

------------------------------------------------------------------------

#### 10.7 LibreCAN

项目：

https://github.com/mdp93/LibreCAN_CCS

重点：

-   automated CAN message translation；
-   降低人工逆向工作量；
-   跨车型自动解释思路。

当前：

> 阅读思想即可，不作为第一阶段实现依赖。

------------------------------------------------------------------------

#### 10.8 CANMatch

资料：

https://orbilu.uni.lu/handle/10993/48502

重点：

-   跨车型 CAN frame matching；
-   利用不同车型间 CAN 数据结构相似性；
-   未来 Tesla baseline → unknown vehicle 的辅助匹配。

当前：

> DEFER。驾驶门 Benchmark 尚未成功前，不做跨车型算法。

------------------------------------------------------------------------

## 11. CAN Reverse Engineering Skill 的定位

未来可以把筛选后的资料整理为：

``` text
can-reverse-engineering/
│
├─ SKILL.md
├─ methodology.md
├─ signal-encoding.md
├─ algorithms.md
├─ patterns.md
├─ tool-reference.md
└─ references.md
```

但 Skill 的性质必须明确：

``` text
Skill
= 专业工具箱
+ 方法论
+ 参考资料
+ 算法知识
```

不是：

``` text
Skill
= TeslaCanPython 新 Contract
```

TeslaCanPython 仍然控制：

-   项目边界；
-   Evidence 原则；
-   Provenance；
-   Ground Truth 隔离；
-   Human Review；
-   正式输出。

CAN RE Skill 只负责扩大 Codex 的专业视野。

------------------------------------------------------------------------

## 12. 与现有 TeslaCanPython 架构的关系

现有方向可以保留：

``` text
Raw ASC
   ↓
Full Observation
   ↓
Known / Residual / Unknown
   ↓
Candidate
   ↓
Semantic Reasoning
   ↓
Evidence Mapping
   ↓
Human Review
```

本阶段重点增强的是中间这一段：

``` text
Raw ASC
   ↓
Full Observation
   ↓
Event-driven Feature Extraction
   ↓
Frame Candidate
   ↓
Byte / Bit Candidate
   ↓
Field Candidate
   ↓
Candidate Ranking
```

也就是说：

> **不是推翻 Phase 3，而是验证并增强 Phase 3 地基里的 Candidate
> Discovery Quality。**

在这项能力没有得到充分验证前，不应因为上层 Pipeline
已经存在，就继续用更多 Contract 掩盖 Discovery 质量问题。

------------------------------------------------------------------------

## 13. 样本逐步扩展路线

只有驾驶门通过 Benchmark 后才扩展。

建议顺序：

``` text
Stage 1
驾驶门 OPEN / CLOSE
↓
Stage 2
其他车门
↓
Stage 3
挡位
↓
Stage 4
制动 / 加速
↓
Stage 5
车辆唤醒
↓
Stage 6
慢充插枪 / 连接建立
↓
Stage 7
其他 Model 3 动态实验
↓
Stage 8
No-DBC Cross-Vehicle Test
```

每增加一个样本，都在问：

> 当前算法学到的是通用 CAN 行为，还是只背熟了上一道题？

------------------------------------------------------------------------

## 14. 最终能力验证

真正有意义的最终测试不是 Model 3。

而是：

``` text
未知车型
+
无可用 DBC
+
标准化实验脚本
+
准确事件时间轴
+
原始 ASC
↓
TeslaCanPython Blind Discovery
↓
Top-N Candidate
↓
bit-field inference
↓
semantic hypothesis
↓
validation proposal
```

如果这条链路能够在多个不同事件中稳定工作，则可以认为：

> TeslaCanPython 已具备 Cross-Vehicle + No-DBC + Event-driven CAN
> Reverse Engineering 的基础能力。

如果无法达到，则需要重新评估自主 Discovery 的能力边界，而不是通过增加
Semantic Reasoning 或报告复杂度掩盖问题。

------------------------------------------------------------------------

## 15. 本阶段最重要的几条原则

### 原则 1

> **Ground Truth 用于评分，不用于提示。**

### 原则 2

> **DBC 在开发期当老师，在运行期退出考场。**

### 原则 3

> **算法优化依据失败模式，不依据答案本身。**

### 原则 4

> **只接受 Benchmark 提升，不接受"看起来更先进"。**

### 原则 5

> **Python 负责确定性计算；Codex 负责工程选择与语义推理。**

### 原则 6

> **程序负责压缩数据量，但不能过度压缩语义可能性。**

### 原则 7

> **先解决 Candidate Discovery，再讨论上层推理有多漂亮。**

### 原则 8

> **专业资料是 Codex 的工具箱，不是 TeslaCanPython 的新枷锁。**

### 原则 9

> **先把驾驶门这一颗钉子钉穿，再增加题型。**

------------------------------------------------------------------------

## 16. 一句话阶段目标

> **利用已有 Model 3 动态实验和 DBC Ground Truth
> 建立可重复、可评分、无答案污染的 CAN RE Benchmark，让 Codex 通过公开
> CAN Reverse Engineering
> 研究与工具逐步优化通用盲拆算法，首先证明"事件时间轴 + 原始 ASC →
> 少量高质量 Signal Candidate"这条最关键链路能够走通。**

这一步走通以后，Semantic Reasoning、Evidence Mapping、L3 Control Tree
和跨车型诊断才真正有可靠的数据地基。
