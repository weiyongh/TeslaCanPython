# TeslaCanPython 三阶段演进与人-AI协同开发原则备忘录

**状态：ARCHITECTURE MEMO / FUTURE VISION**  
**用途：保存方向，避免反复思考；不是当前 Roadmap，也不自动转化为 Codex 任务。**

---

## 1. 当前主目标不能漂移

TeslaCanPython 建立的初衷没有变化：

> **采集和分析 ASC，建立 Model 3 正常基线数据，为后续特斯拉故障诊断建立可参考、可比较、可复用的诊断数据库基础。**

当前工作的核心产出是：

```text
ASC 采集
   ↓
基线分析
   ↓
Reliable Communication Evidence
   ↓
Model 3 L3 控制树实例化
   ↓
正常基线数据 + 基线分析报告
```

DBC 核实只是分析过程中自然产生的副产品，而不是常态目标。

正确关系：

```text
为了理解 ASC
    ↓
使用 DBC 解释 Signal
    ↓
通过实测行为、时序、数值和关系验证
    ↓
发现 DBC 正确 / 部分正确 / 可疑 / 错误
```

而不是：

```text
为了验证 DBC
    ↓
组织整个 TeslaCanPython
```

如果主目标开始漂移到后者，应立即“挨锤”。

---

## 2. 程序的定位：建立适合 AI 分析的基础设施

核心开发原则：

> **我是在建立适合 AI 分析的程序，而不是把手伸进 LLM 里。**

程序负责：

```text
事实保存
结构化
Observation 压缩
Behavior / Phase / Relationship 提取
Provenance
L3 与 Collection Script 上下文
确定性计算
硬边界验证
计算规模控制
```

LLM 负责：

```text
语义理解
相关性判断
Signal Hypothesis
控制关系推理
替代解释
DBC 质疑
Evidence Candidate 形成
```

应警惕把人工语义判断写成大量关键词、车型特判、魔法权重和 scoring function。

例如：

```text
request +40
state +20
phase +25
...
```

如果这些权重实际上在决定“这个 Observation 是什么语义角色”，就等于在 Python 中重新实现一个简陋的 Semantic Reasoner。

更合理的原则是：

> **确定性的程序负责告诉 AI“发生了什么”；AI 负责判断“这意味着什么”。**

Retrieval 可以大胆实验，但重点应是结构、上下文组织和多路召回，而不是不断人工调语义权重。

---

## 3. 人与 AI 的开发协同方式需要优化

用户具备软件架构与程序员背景，因此不需要采用“需求方 → AI 架构委员会 → Codex 机械执行”的模式。

更合适的是：

```text
用户
├─ 目标
├─ 领域知识
├─ 软件架构直觉
├─ 工程经验
└─ 最终取舍
        ↕
ChatGPT
├─ 帮助拆解问题
├─ 补充 AI / 数据分析视角
├─ 发现架构漏洞
├─ 守关键边界
└─ 在真正高风险处提高严谨度
        ↕
Codex
├─ 阅读真实代码
├─ 快速实现
├─ 跑真实数据
├─ 自动测试
└─ 输出结果供共同审查
```

AI 的高严谨度是长处，但不能让这种严谨度成为开发负担。

人类优秀软件开发大量依赖：

```text
方向判断
→ 快速实现
→ 跑起来
→ 看真实结果
→ 形成直觉
→ 修正
→ 再运行
```

TeslaCanPython 是探索型工程，不应把每一个可逆的小设计都升级成 Contract / Gate / Phase / Formal Review。

---

## 4. 用“可逆性”决定严谨程度

### Hard Invariants —— 继续严格

错误会污染整个证据链的部分，应保持高强度约束：

```text
Raw provenance
ASC identity / parse integrity
Time semantics
Observed / Inferred 边界
Evidence epistemic class
Approved Evidence gate
历史答案泄漏防护
原始数据不可篡改
Evidence → Assessment 边界
Traceability
```

这些地方 AI 的“超人类严谨度”是优势，应充分利用。

### Experimental Layer —— 快速迭代

容易修改、容易验证、失败成本低的部分，应采用：

> **大胆尝试，小心求证。**

例如：

```text
Retrieval 结构
Prompt
Observation Context
Candidate Recall
LLM 输入组织
模型选择
报告表达
```

典型循环：

```text
Hypothesis
   ↓
Implement
   ↓
Run Real TM3 Data
   ↓
Inspect Result
   ↓
Keep / Modify / Revert
```

不要为了证明“绝对不会错”而花掉比试错本身更多的成本。

---

## 5. 未来想法的状态管理

未来设想不等于当前需求。

建议长期使用三种状态：

```text
CURRENT
当前问题直接需要，实施。

ARCHITECTURE CONSIDERATION
当前不实施，但当前设计不要轻易封死未来路径。

PARKED / FUTURE VISION
记录想法；未来条件成熟时重新论证，可能采用、修改，也可能放弃。
```

架构原则：

> **对未来保持架构弹性，但不为未来支付当前实现成本。**

备忘录的意义是让未来想法有地方存放，从而可以安心回到当前任务，而不是把备忘录自动变成 Roadmap。

---

# 6. 三阶段长期演进

## Stage 1 — Model 3 正常基线

**状态：CURRENT**

这是当前唯一需要真正投入开发资源的阶段。

目标：

```text
Model 3
│
├─ 统一 Collection Script
├─ ASC 数据采集
├─ L3 Semantic Prior
├─ DBC 辅助车型通信解释
├─ Behavior / Phase / Relationship
├─ Signal Validation
├─ Reliable Communication Evidence
├─ Control Tree Instance
└─ Normal Baseline + Analysis Report
```

主要资产：

```text
正常控制过程
正常状态
正常时序
正常数值
正常 Signal Relationship
正常物理关系
正常 Evidence Pattern
```

这些数据为后续特斯拉实际诊断建立“正常世界”。

未来面对故障车时，只有知道正常是什么样，才能判断哪里开始异常。

---

## Stage 2 — 一两个无 DBC 车型的指纹性质基线

**状态：PARKED / FUTURE EXPERIMENT**

未来可以选择一两个缺少可用 DBC 的车型，验证 Stage 1 积累的方法是否具有迁移价值。

可能复用：

```text
L3 Semantic Prior
Collection Script 方法
ASC Parser / Observation Model
Behavior Feature
Phase Model
Relationship Extraction
Evidence Model
LLM Reasoning Contract
Validation 思路
```

目标不是强行复制 Tesla Signal，而是研究：

```text
L3 Semantic Role
        ↓
相同 / 相近实验刺激
        ↓
Raw CAN Behavior
        ↓
Timing / Transition / Relationship Fingerprint
        ↓
Signal Role Hypothesis
```

这项工作未来不一定继续放在 TeslaCanPython 中。

可以：

- 复用部分程序；
- 抽取通用模块；
- 或另建实验工程。

现在不决定。

当前只需要保持必要的软件弹性，不要把所有能力硬编码为 Model 3 专用即可。

---

## Stage 3 — AI 辅助故障诊断

**状态：LONG-TERM GOAL**

这是 L3 能力最终真正落地并产生实际回报的方向。

输入可能包括：

```text
Fault Case
│
├─ 故障现象描述
├─ Vehicle Configuration
├─ L3 System Knowledge
├─ Control Tree
├─ Diagnostic Tree
├─ Normal Baseline
├─ Fault ASC / Diagnostic Data
├─ Wiring Diagram
├─ Service Manual
└─ Previous Cases
```

AI Reasoning：

```text
正常基线
    ↕
故障车辆数据
    ↓
DIFF
    ↓
异常首先出现在哪个控制阶段？
    ↓
Control Tree Location
    ↓
Diagnostic Tree
    ↓
Evidence 缺失 / 矛盾
    ↓
Fault Boundary
    ↓
下一步最有价值的验证
```

最终输出：

> **可执行的排故方案。**

例如：

```text
故障现象：无法直流快充
        ↓
正常基线对比
        ↓
Connection      ✓
Wake            ✓
Communication   ✓
Capability      ✓
Request         ✓
Permission      ?
HV Establishment ✗
        ↓
故障边界：Request 后 / HV Establishment 前
        ↓
结合诊断树 + 电路图 + 维修手册
        ↓
生成下一步 Evidence 获取方案
        ↓
根据测量结果继续收窄
```

这里的“排故方案”才是长期 L3 学习、控制树、诊断树、基线、通信 Evidence 等资产最终转化为现实价值的输出。

---

# 7. 三阶段之间真正的关系

```text
Stage 1
建立“正常是什么”
        ↓
Normal Baseline / Control Tree Instance
        ↓
Stage 2（可选）
验证无 DBC 情况下的方法迁移能力
        ↓
更通用的 Observation / Fingerprint 能力
        ↓
Stage 3
故障数据 vs 正常基线
        ↓
Control Tree 定位
        ↓
Diagnostic Tree 展开
        ↓
Evidence 获取
        ↓
缩小故障边界
        ↓
Troubleshooting Procedure
```

Stage 2 不是 Stage 3 的绝对前置条件。

即使未来不做通用无 DBC 平台，Stage 1 的 Model 3 正常基线也可以直接服务于 Model 3 / Tesla 的 Stage 3 故障诊断。

---

# 8. “重锤”的新定义

用户具有较高自我要求，思路跳跃快，也能够较早看到长期方向。

这不是需要消灭的缺点。

未来设想往往有架构价值，可以帮助今天避免走入死路。

真正需要监督的是：

> **不要把未来可能有价值的想法，提前变成今天必须完成的工作。**

因此“重锤”不再是：

> 不要想那么远。

而是：

> **可以尽情想远，可以记录，可以留下架构弹性；但回到 Codex 前必须判断它属于 CURRENT、ARCHITECTURE CONSIDERATION 还是 PARKED。**

当前 Codex 工作只有一个最高优先判断：

> **这件事是否直接提高 Model 3 基线采集、分析、Evidence 可靠性或基线数据质量？**

如果不是：

```text
记录
↓
保留必要架构弹性
↓
PARKED
↓
不实现
```

---

# 9. 当前阶段一句话目标

> **先把 Model 3 的正常世界建立好。**

即：

> **Model 3 ASC → Reliable Evidence → L3 Control Tree Instance → Normal Baseline → Baseline Analysis Report。**

DBC Validation 是副产品。

无 DBC Fingerprint 是未来实验。

AI Troubleshooting 是长期落地目标。

现在不开席。

---

# 10. 协同开发原则一句话总结

> **让 AI 补足人类软件开发容易缺失的严谨性，但不要让 AI 的严谨性取代软件架构师的方向感、工程直觉、快速试错和取舍能力。**

以及：

> **程序负责把事实、数据、上下文和证据准备好；不要在程序中替 LLM 思考。**

最后：

> **远见可以放心存进备忘录，当前只做 Stage 1。**
