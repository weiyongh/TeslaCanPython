# TeslaCanPython CAN ASC Blind Reverse：Codex 引入与学习步骤

> **用途**：指导如何把 CAN ASC Blind Reverse 优化课题逐步交给
> TeslaCanPython 项目中的 Codex。\
> **当前原则**：先理解项目，先找问题，先建立
> Benchmark；外部资料按问题调用；Skill 最后沉淀。\
> **当前阶段不要求 Codex 开工实现。**

## 1. 核心顺序

``` text
Project First
    ↓
Problem First
    ↓
Benchmark First
    ↓
Reference Second
    ↓
Experiment / Improvement
    ↓
Skill Last
```

不要一开始把全部 CAN Reverse Engineering 资料交给
Codex，要求其"学习并综合实现"。

当前首先让 Codex 自己理解：

1.  TeslaCanPython 已经有什么；
2.  驾驶门 Blind Reverse 当时怎么做；
3.  Candidate 为什么这样产生和排序；
4.  当前命中率不足属于什么问题；
5.  如何建立不受 Ground Truth 污染的 V0 Benchmark。

## 2. Step 1：只审计当前项目，不学习外部资料

### 给 Codex 的第一段讨论提示

``` markdown
我们准备重新讨论 TeslaCanPython 当前的 CAN ASC blind reverse 能力。

先不要改代码，不要实现新算法，也不要立即学习全部外部 CAN RE 资料。

请先回顾项目里已有的驾驶门开关采集、采集脚本、ASC、现有 blind reverse 程序和当时产生的 Candidate 结果。

我希望我们先把 V0 讲清楚：

- 当前 blind discovery 到底怎么工作；
- 实际使用了哪些 deterministic feature；
- Candidate 怎么产生和排序；
- 当前正确目标的排名表现如何；
- 命中率不够好的主要失败模式可能是什么；
- 当前 Observation / Discovery 架构中，哪些能力已经存在，哪些只是设计上预留。

Tesla DBC 和已知 Signal 可以用于建立 Ground Truth 和后续评分，但不能用于指导 Blind Track，也不能反向污染盲猜程序。

这一轮只讨论现状和问题，不实现。讨论完停下来，我们再决定下一步。
```

期望输出：

``` text
Current Blind Reverse V0
├─ Input
├─ Existing Pipeline
├─ Existing Features
├─ Candidate Generation
├─ Candidate Ranking
├─ Current Result
├─ Known Limitations
└─ Suspected Failure Modes
```

## 3. Step 2：冻结 V0 Benchmark

任何新 CAN RE 方法进入项目前，先冻结 Baseline。

``` text
                 Same Experiment
                       │
             ┌─────────┴─────────┐
             ↓                   ↓
        Blind Track        Ground Truth Track
             │                   │
          No DBC              Tesla DBC
             │              Human Verified
             ↓                   ↓
       Candidate List       Correct Answer
             │                   │
             └─────────┬─────────┘
                       ↓
                   Evaluation
```

Benchmark 至少考虑：

-   正确 CAN ID 排名；
-   Top-1 / Top-3 / Top-5 / Top-10 是否命中；
-   Candidate 总量；
-   False Positive；
-   多次 OPEN / CLOSE 的重复一致性；
-   OPEN / CLOSE 状态反向一致性；
-   如果当前能力已达到 byte / bit 层，记录正确 byte / bit-field 排名。

此时仍不修改 blind reverse 算法，不顺便重构 Discovery Pipeline。

## 4. Ground Truth 边界

> **Ground Truth 用于评分，不用于提示。**

Blind Track 运行时不得读取：

-   Tesla DBC；
-   正确 CAN ID；
-   正确 Signal 名称；
-   正确 start bit / length；
-   endian / signedness 答案；
-   历史人工确认的正确候选；
-   当前实验的目标白名单。

允许 Ground Truth 只在 Evaluation 阶段参与：

``` text
Blind Result
    +
Ground Truth
    ↓
Benchmark Score
```

另一条原则：

> **算法优化依据失败模式，不依据答案本身。**

## 5. Step 3：让 Codex 自己判断缺什么知识

完成 V0 审计和 Benchmark 后，先问 Codex：

``` markdown
基于刚才冻结的 V0 和你识别出的失败模式：

如果要提升这个 CAN ASC blind reverse 的 Candidate Discovery / Ranking 能力，你认为需要补充哪些 CAN reverse engineering 方法知识？

这一轮只讨论“方法类别”和它们可能解决的问题，不实现。

请区分：

1. 当前项目已经具备；
2. 当前项目部分具备；
3. 当前项目明显缺失；
4. 对驾驶门 Benchmark 可能有直接信息增益；
5. 当前没有必要引入。

不要因为某个算法在论文中先进，就默认应该实现。
```

这里不是要求 Codex
必须列出固定算法菜单，而是观察它能否根据失败模式自主识别知识缺口。

## 6. Step 4：只给外部资料"地图"

完成前三步后，再给公开资料名称、链接和定位，不要求全部阅读和实现。

### 第一梯队

**CSS Electronics --- CAN Bus Reverse Engineering Skills**\
https://github.com/CSS-Electronics/can-bus-reverse-engineering-skills

重点：`survey → correlate → bitsearch → build_dbc → verify`。\
定位：CAN RE 实践工作流参考。

**READ --- Reverse Engineering of Automotive Data Frames**\
https://doi.org/10.1109/TIFS.2018.2870826

重点：bit flip、bit-level statistics、signal boundary inference、payload
segmentation。\
定位：从可疑 CAN ID 深入到 bit-field。

**CAN-D**\
https://arxiv.org/abs/2006.05993

``` text
Signal
├─ Boundary
├─ Endianness
├─ Signedness
└─ Physical Interpretation
```

定位：完整 CAN Signal Reverse Engineering 的问题地图。

**ACTT**\
https://arxiv.org/abs/1811.07897

重点：tokenization、bit grouping、field → physical meaning
translation。\
定位：Signal field reconstruction / interpretation。

**ByCAN**\
https://arxiv.org/abs/2408.09265

重点：bit-level features、byte-level features、clustering、signal
slicing。\
定位：多层特征与自动 slicing。

**SavvyCAN**\
https://github.com/collin80/SavvyCAN

重点：coherent-data scanning、graphing、filtering、实际 CAN RE
工程工具实现。\
定位：学习工程经验和算法思想，不作为 TeslaCanPython 架构模板。

## 7. Step 5：让 Codex 自己选择资料

不要说：

> 请学习以上所有资料并综合实现。

而应说：

``` markdown
这里有一组公开 CAN Reverse Engineering 资料。

它们是知识来源，不是 TeslaCanPython 的新 Contract，也不是实现清单。

请结合刚才识别出的 V0 失败模式，先判断：

- 哪一项资料最可能解决当前问题；
- 为什么；
- 哪些暂时不值得深入；
- 你希望优先阅读哪一项或哪两项。

当前不要实现。

先做资料选择和理由说明。
```

> **先让 Codex 选，再让 Codex 学。**

## 8. Step 6：问题驱动地深入学习

### A. 正确 ID 排名很差

优先考虑：

``` text
CSS workflow
event-driven filtering
SavvyCAN RE 思路
event consistency
```

问题：如何从大量同步变化 CAN ID 中，把真正与人工动作相关的 ID 推到前面？

### B. 正确 ID 已很好，但无法找到 Signal field

优先：

``` text
READ
CAN-D
ACTT
```

问题：如何从正确 payload 中自动发现真正表达目标状态的 bit-field？

### C. byte / bit segmentation 不足

考虑：

``` text
ByCAN
READ
CAN-D
```

问题：bit-level 与 byte-level feature 如何组合，提高 signal slicing？

### D. 跨车型匹配

以后再考虑 CANMatch、LibreCAN、Cross-Vehicle RE。

当前驾驶门 Benchmark 未通过前：

> **DEFER。**

## 9. Step 7：Codex 提出最小算法改进

深入阅读针对性资料后，再回到 TeslaCanPython：

``` markdown
现在回到 V0 Benchmark。

根据你刚才研究的方法，请判断：

1. V0 的具体失败模式是什么？
2. 哪个方法可能带来最大信息增益？
3. 当前 TeslaCanPython 已有能力能否复用？
4. 最小需要新增什么？
5. 哪些论文能力当前明确不需要？
6. 如何保证该改进是通用算法，而不是驾驶门专用规则？
7. 修改后如何使用完全相同的 Blind Benchmark 验证？

先给最小改进方案，等我确认后再决定是否实现。
```

## 10. Step 8：实现后重新 Blind Test

``` text
V0
↓
Study
↓
Minimal Improvement
↓
V1 Blind Test
↓
Evaluation
↓
Compare V0
```

之后再逐渐形成：

``` text
V0 → V1 → V2 → V3
```

只保留满足以下条件的改进：

-   Benchmark 明确改善；
-   没有明显破坏其他能力；
-   不依赖 Ground Truth 泄漏；
-   具有通用意义；
-   Provenance 可解释。

> **只接受 Benchmark 提升，不接受"看起来更先进"。**

## 11. Skill 什么时候建立

现在不要先造完整 CAN Reverse Engineering Skill。

正确沉淀过程：

``` text
公开资料
    ↓
Codex 按问题阅读
    ↓
真实 TM3 Benchmark
    ↓
算法验证
    ↓
证明有效
    ↓
形成稳定方法
    ↓
沉淀 CAN RE Skill
```

Skill 保存的是：

``` text
被真实 Benchmark 验证过的方法
+
成熟工作流
+
通用算法知识
+
高质量参考资料
```

而不是把所有论文和 GitHub 项目重新包装一遍。

## 12. CAN RE Skill 与项目 Contract 的边界

``` text
                    TeslaCanPython
                         │
          ┌──────────────┴──────────────┐
          │                             │
    Project Rules                Knowledge Skill
          │                             │
   Ground Truth Boundary         CAN RE Methods
   Evidence Rules                Algorithms
   Provenance                    Patterns
   Human Review                  References
          │                             │
          └──────────────┬──────────────┘
                         ↓
                       Codex
```

外部 CAN RE 知识：

> **是工具箱，不是项目法律。**

## 13. 一句话工作原则

> **先让 Codex 理解自己的项目，再让它理解自己的失败；先有 V0
> 分数，再按失败模式找老师；学到的方法先通过 Blind
> Benchmark，真正有效以后才沉淀成 Skill。**
