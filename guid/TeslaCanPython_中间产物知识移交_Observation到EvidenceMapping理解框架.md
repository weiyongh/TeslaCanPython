# TeslaCanPython 中间产物知识移交：从 Observation 到 Evidence Mapping 的理解框架

> **用途**：项目移交 / 知识移交学习笔记\
> **背景**：在继续修改 TeslaCanPython 架构之前，先通过 Codex
> 对当前程序中间产物的"自我描述"，理解现有正式管线到底生成了什么、每个对象处在哪个认识层级，以及当前架构中最值得继续审查的地方。\
> **性质**：理解现状，不代表认可当前所有设计；尤其 Retrieval 与 LLM
> 输入边界仍需继续 Review。

------------------------------------------------------------------------

## 1. 为什么先熟悉中间产物

这是一次很有价值的项目移交方式。

与其直接阅读大量 Python 代码，不如先从一次真实 Run 的产物入手：

``` text
输入是什么
    ↓
程序生成了什么
    ↓
每个文件回答什么问题
    ↓
哪些是事实
    ↓
哪些是筛选结果
    ↓
哪些是 AI 判断
    ↓
哪些已经进入 Evidence
```

这样能够先建立系统的"认识论地图"，再去看代码为什么这样实现。

对于 TeslaCanPython，尤其需要避免把不同层级的对象混为一谈。

最重要的一条关系是：

``` text
Observation
≠ Candidate
≠ Retrieved Observation
≠ Finding
≠ Evidence Binding Draft
≠ Approved Evidence
```

这些对象虽然都可能引用同一条 CAN 数据，但它们代表完全不同的认识层级。

------------------------------------------------------------------------

# 2. 当前正式管线的中间产物链

Codex 对当前 Run 的自我描述可以整理为：

``` text
ASC + DBC + Analysis Charter
            ↓
    observation_package.json
            ↓
 semantic_search_intents.json
            ↓
semantic_retrieval_results.json
            │
            ├── semantic_retrieval_audit.json
            ↓
 semantic_reasoning_input.json
            ↓
      LLM Semantic Reasoning
            ↓
 semantic_reasoning_output.json
            ↓
semantic_reasoning_validation.json
            ↓
 evidence_mapping_draft.json

runtime_audit.json
贯穿整个 Run
```

从人的理解角度，可以进一步压缩成五层：

``` text
① 看到了什么？
      Observation

② 准备让 AI 看什么？
      Retrieval

③ AI 实际看到了什么、判断了什么？
      Reasoning

④ AI 是否违反事实和契约？
      Validation

⑤ AI 的判断如何准备进入 Evidence？
      Evidence Mapping
```

另外：

``` text
runtime_audit.json
```

相当于整次程序运行的"黑匣子记录"。

------------------------------------------------------------------------

# 3. 第一层：Observation ------ 程序到底观察到了什么

核心文件：

``` text
observation_package.json
```

它不是 AI 的分析结论。

它更接近：

> **Python 对 ASC 做确定性分析以后形成的冻结工程观察世界。**

它包含的主要内容包括：

``` text
Full CAN Observation
DBC Coverage
Known Signal Summary
Residual Observation
Unknown Observation
Candidate
Raw Reference / Provenance
```

例如当前 TM3-015 Run 中大致形成：

``` text
344 Observation
4280 Known Signal Summary
56 Residual
174 Unknown
120 Candidate
```

这里最重要的是：

> **Candidate 不等于 Observation。**

完整 Observation 世界仍然存在。

Candidate 只是程序根据某些确定性规则，从大量数据中形成的重点关注对象。

因此：

``` text
Full Observation
        ↓
Candidate Compression
```

不能理解成：

``` text
Candidate = 全部数据
```

------------------------------------------------------------------------

# 4. Observation 的认识论地位

Observation 应尽可能属于：

``` text
Engineering Fact
```

例如：

``` text
CAN ID = 0x123
DLC = 8
frame_count = 300
bit 17 changed 6 times
first change = 35.82 s
payload cardinality = 4
```

这些是程序能够确定性计算的事实。

Observation 不应该直接变成：

``` text
这是充电许可
这是接触器请求
这是 BMS 充电能力
```

这些已经属于 Semantic Claim。

所以：

``` text
Observation
       ↓
提供事实
       ↓
但不决定语义
```

这是整个 TeslaCanPython 架构中非常重要的边界。

------------------------------------------------------------------------

# 5. 第二层：Semantic Search Intent ------ AI 要寻找什么

文件：

``` text
semantic_search_intents.json
```

它回答：

> **根据 L3、Evidence Requirement 和实验目标，我们希望从 Observation
> 世界中寻找什么类型的工程现象？**

当前 Run 中形成了多个 Semantic Intent。

这些 Intent 的来源应该是：

``` text
L3 Semantic Prior
Control Tree
Evidence Requirement
Experiment Context
```

而不能来自：

``` text
历史正确答案
已经确认的 TM3-015 Signal
旧报告结论
预先写好的答案脚本
```

否则就会发生：

``` text
先知道答案
↓
再设计搜索问题
↓
最后“成功发现答案”
```

这种结果没有 Blind Discovery 的价值。

------------------------------------------------------------------------

# 6. 第三层：Semantic Retrieval ------ 程序准备让 AI 看什么

核心文件：

``` text
semantic_retrieval_results.json
```

以及：

``` text
semantic_retrieval_audit.json
```

这是目前架构中非常值得重点审查的一层。

它做的事情本质上是：

``` text
完整 Observation 世界
        ↓
根据 Semantic Intent
        ↓
选择一部分 Observation
        ↓
送入 LLM
```

例如：

``` text
344 Observations
+ 4280 Known Signal Summaries
+ 56 Residual
+ 174 Unknown
        ↓
      Retrieval
        ↓
25 unique Observations
```

这里立刻产生一个重要问题：

> **是谁决定 AI 只能看到这 25 个 Observation？**

------------------------------------------------------------------------

# 7. Retrieval 为什么是当前最值得警惕的一层

Retrieval 本身不是错误。

因为不可能把所有原始 ASC 和几千个 Signal Summary 无脑塞给 LLM。

问题在于：

> **Retrieval 到底是在压缩数据量，还是已经偷偷开始压缩语义可能性？**

理想情况：

``` text
大量工程数据
       ↓
压缩冗余
       ↓
保留关键行为
       ↓
LLM 自己做语义判断
```

危险情况：

``` text
大量工程数据
       ↓
程序认为“这些像 Request”
程序认为“那些不像”
程序认为“DBC 名字更相关”
       ↓
只给 AI 看程序认为正确的对象
       ↓
LLM 在预筛选世界中“自由推理”
```

后一种情况下，LLM 再强也无法发现被 Retrieval 提前删除的可能性。

因此当前最重要的架构问题不是：

> "LLM 推理能力够不够？"

而是：

> **"LLM 实际获得了多大的观察视野？"**

------------------------------------------------------------------------

# 8. semantic_retrieval_audit.json 的作用

Retrieval Audit 记录：

``` text
算法版本
输入 Hash
阈值
每个 Intent 上限
全局 Candidate 上限
Known / Residual / Unknown quota
最终选中数量
```

它主要回答：

> **Retrieval 是否按照既定规则执行？**

但必须注意：

``` text
Retrieval Audit PASS
≠
Retrieval 语义有效
```

它只能证明：

> 程序忠实执行了 Retrieval Algorithm。

不能证明：

> Retrieval Algorithm 本身没有漏掉重要 Observation。

因此未来判断 Retrieval，需要额外的人类可审核摘要和真实 Replay。

------------------------------------------------------------------------

# 9. 第四层：Semantic Reasoning Input ------ LLM 真正看到了什么

文件：

``` text
semantic_reasoning_input.json
```

这个文件非常重要。

它不是：

``` text
完整 Observation Package
```

而是：

> **本次 LLM 调用实际冻结下来的输入世界。**

里面可能包括：

``` text
Retrieved Observations
Candidate References
L3 Context
Experiment Context
Semantic Intents
Event Anchors
Validation Context
Reference Manifest
Observation Package ID / Hash
```

因此：

``` text
observation_package.json
```

回答：

> 程序知道什么？

而：

``` text
semantic_reasoning_input.json
```

回答：

> **AI 实际被允许知道什么？**

这是两个完全不同的问题。

------------------------------------------------------------------------

# 10. JSON 会不会限制 LLM 推理能力

不会。

JSON 本身并不是问题。

结构化数据反而有很多优势：

``` text
对象关系稳定
字段含义明确
数值不容易混淆
Reference ID 可引用
容易进行自动 Validation
容易建立 Provenance
```

例如：

``` json
{
  "observation_id": "OBS-087",
  "change_count": 3,
  "first_change_time_s": 35.82,
  "states": [0, 1]
}
```

LLM 完全能够理解这种数据。

真正影响推理能力的是：

> **JSON 形成之前，程序已经替 LLM 做了多少语义判断。**

因此真正需要 Review 的不是：

``` text
为什么给 LLM JSON？
```

而是：

``` text
为什么 JSON 里只有这些东西？
```

------------------------------------------------------------------------

# 11. Data Compression 与 Semantic Compression

这是理解当前架构非常重要的一组概念。

## Data Compression

例如：

``` text
685,617 CAN Frames
        ↓
OBS-087
frame_count = 18,421
state = {0,1}
change at 35.82 s
```

这是好的压缩。

因为没有必要让 LLM 阅读十八万、几十万行 Raw Frame。

------------------------------------------------------------------------

## Semantic Compression

如果变成：

``` text
685,617 Frames
       ↓
程序认为只有 25 个 Observation
与“充电控制”有关
       ↓
其余全部不给 LLM
```

那么程序可能已经开始替 AI 决定：

> 什么值得理解。

这就是需要警惕的地方。

因此 TeslaCanPython 更合理的原则应该是：

> **程序尽可能压缩数据量，但尽可能少压缩语义可能性。**

------------------------------------------------------------------------

# 12. 第五层：Semantic Reasoning Output ------ AI 的判断

文件：

``` text
semantic_reasoning_output.json
```

其中的 Finding 已经不是 Observation Fact。

它属于：

``` text
Semantic Judgment
```

例如：

``` text
这个 Observation 可能承担某种 L3 Role
它与某个 Evidence Requirement 有关系
存在这些支持事实
还有这些 Alternative Explanation
仍缺少这些 Evidence
```

因此：

``` text
Finding
≠
Fact
```

更不能直接变成：

``` text
Finding
=
Approved Evidence
```

------------------------------------------------------------------------

# 13. 为什么必须区分 Request / Capability / Actual

当前 Semantic Reasoning Contract 中一个很重要的认识边界是：

``` text
Capability
≠
Request
≠
Actual
```

例如：

``` text
EVSE Maximum Current
```

可能表示 Capability。

``` text
Vehicle Requested Current
```

可能表示 Request。

``` text
Measured Charge Current
```

可能表示 Actual。

即使三个数值接近，也不能因为：

``` text
A ≈ B ≈ C
```

就把它们当成同一个语义角色。

同样：

``` text
DBC Name
≠
Confirmed Semantic Role
```

这些约束是合理的，因为它们保护了 Evidence 的认识边界。

------------------------------------------------------------------------

# 14. 第六层：Semantic Reasoning Validation

文件：

``` text
semantic_reasoning_validation.json
```

它主要检查：

``` text
引用是否合法
Observation 是否存在
数值是否来自冻结输入
是否虚构时间
是否越过 epistemic boundary
是否违反 Reasoning Contract
是否出现非法 Approval
```

如果：

``` text
valid = true
```

正确理解是：

> **这次 LLM 输出符合 Reasoning Contract。**

不能理解成：

> **LLM 的语义判断一定正确。**

因此：

``` text
Validation PASS
≠
Semantic Truth
```

------------------------------------------------------------------------

# 15. 第七层：Evidence Mapping Draft

文件：

``` text
evidence_mapping_draft.json
```

它负责把：

``` text
Evidence Requirement
        ↕
Finding
        ↕
Observation / Candidate
        ↕
Suggested Evidence Role
        ↕
Validation
```

组织起来。

但这里仍然只是：

``` text
Draft
```

不是：

``` text
Approved Evidence
```

所以：

``` text
Evidence Mapping Draft
       ↓
Human Review
       ↓
Approved Evidence
```

这条边界不能被程序或 LLM 自动跨越。

------------------------------------------------------------------------

# 16. runtime_audit.json ------ 整个 Run 的黑匣子

`runtime_audit.json` 不回答某条 CAN 数据是什么。

它回答：

> **这一次程序到底做了什么？**

典型内容包括：

``` text
Run ID
Pipeline Version
ASC Hash
DBC Hash
Frame Count
Observation Count
K/R/U Count
Candidate Count
ASC Parse Count
Retrieval Hash
Reasoning Package Hash
L3 Fingerprint
Control Tree Fingerprint
ER Fingerprint
LLM Call Count
Follow-up Count
Finding Count
Binding Count
Timing
Exit State
```

因此需要区分：

``` text
Provenance
=
这条数据 / 事实从哪里来？

Runtime Audit
=
这次程序运行做了什么？
```

二者共同构成系统的可追溯性。

------------------------------------------------------------------------

# 17. Provenance 不是另一个 Observation 来源

Provenance 中文更接近：

``` text
数据溯源
来源追踪
```

例如：

``` text
Candidate C-021
      ↓
Observation OBS-087
      ↓
CAN ID / DLC / Channel
      ↓
Raw Reference
      ↓
ASC Line
      ↓
Original Payload
```

它不是：

``` text
Raw ASC
├── Observation
└── Provenance Observation
```

而应该理解成：

``` text
Raw ASC
   ↓
Observation
   ↓
Behavior Fact
   ↓
Change / Event Fact
   ↓
Candidate
   ↓
Engineering Data Description

与此同时：

Provenance 贯穿所有派生层
```

所以 Provenance 是一个 **Cross-Cutting
Property**，不是另一条数据分析分支。

------------------------------------------------------------------------

# 18. 当前中间产物最重要的认识阶梯

整个体系可以压缩成：

``` text
Raw ASC
   ↓
Observation
   ↓
Candidate
   ↓
Retrieved Observation
   ↓
Finding
   ↓
Evidence Binding Draft
   ↓
Human Review
   ↓
Approved Evidence
```

每下降一层，认识程度都会发生变化。

------------------------------------------------------------------------

## Observation

> 数据客观发生了什么？

------------------------------------------------------------------------

## Candidate

> 哪些客观行为值得进一步关注？

------------------------------------------------------------------------

## Retrieved Observation

> 对当前 Semantic Question，程序选择让 AI 看哪些 Observation？

------------------------------------------------------------------------

## Finding

> AI 如何解释这些 Observation？

------------------------------------------------------------------------

## Evidence Binding Draft

> AI 的解释可能如何映射到 Evidence Requirement？

------------------------------------------------------------------------

## Approved Evidence

> 人最终认可哪些内容可以进入正式诊断 Evidence？

------------------------------------------------------------------------

# 19. 当前架构中最值得继续 Review 的地方

从这次知识移交看，Observation Package 本身已经形成比较清楚的事实边界。

真正值得重点审查的是：

``` text
Observation
     ↓
Retrieval
     ↓
Frozen LLM Input
```

核心问题不是：

> "JSON 做得漂亮不漂亮？"

而是：

> **"为什么 AI 只看到了这些？"**

以后看到 `semantic_reasoning_input.json`，应该形成条件反射：

``` text
完整 Observation 世界有多大？
        ↓
Retrieval 选了多少？
        ↓
漏掉了什么？
        ↓
为什么漏？
        ↓
DBC 名称是否影响过强？
        ↓
Unknown / Residual 有没有公平进入？
        ↓
程序有没有提前替 LLM 做语义判断？
```

------------------------------------------------------------------------

# 20. Retrieval 应该如何被人验证

人不应该靠逐条阅读大量 JSON 来判断 Retrieval 是否有效。

更合理的是生成一个轻量的人类可审核摘要：

``` text
Retrieval Human Review Summary
│
├─ Observation Universe
│
├─ Intent Coverage
│
├─ Top Observation per Intent
│   ├─ Observation ID
│   ├─ K / R / U
│   ├─ behavior
│   ├─ score
│   └─ selection reason
│
├─ Source Distribution
│   ├─ Known
│   ├─ Residual
│   └─ Unknown
│
├─ Strong but not retrieved
│
├─ Known-answer blind replay
│   ├─ Recall@10
│   ├─ Recall@25
│   └─ Recall@50
│
└─ DBC-name bias / ablation
```

真正需要回答的是：

``` text
该看的东西看到了吗？       Recall
不该看的东西是不是太多？   Precision
有没有来源偏置？           Bias
为什么选它？               Explainability
```

------------------------------------------------------------------------

# 21. 最有价值的 Retrieval 验证方法：Blind Replay

对于已经完成、事后知道部分关键 Signal / Evidence 的 TM3 实验，可以：

``` text
不把历史答案给 Retrieval
        ↓
运行完整 Observation → Retrieval
        ↓
事后检查已知关键对象是否被重新发现
```

例如：

``` text
已知关键对象 = 10

Recall@10 = 6/10
Recall@25 = 8/10
Recall@50 = 9/10
```

它回答的是：

> **如果不提前告诉程序答案，它还能不能把真正重要的对象捞出来？**

这比单纯看 Retrieval Score 更有意义。

------------------------------------------------------------------------

# 22. DBC Name Ablation Test

还可以对同一组 Observation 做：

``` text
A. 保留 DBC Signal / Message Name

B. 隐藏语义名称
   只保留行为事实
```

比较 Retrieval 排名。

例如：

``` text
保留 DBC Name：
OBS-087 Rank = 2

隐藏 DBC Name：
OBS-087 Rank = 78
```

说明 Retrieval 很可能主要依赖名称。

如果：

``` text
Rank 2
↓
Rank 7
```

则说明行为事实本身也具有足够支撑。

这个测试可以直接回答：

> **DBC 到底是 Reference，还是实际上已经变成 Semantic Admission
> Authority？**

------------------------------------------------------------------------

# 23. Strong-but-not-retrieved 检查

从 Full Observation 中寻找客观行为很强但没有进入 Retrieval
的对象，例如：

``` text
明显 Step
低离散状态切换
关键时间附近变化
Unknown regime change
Residual bit activity
```

如果：

``` text
OBS-U143
t = 35.8 s
bit2: 0 → 1
之后长期保持
```

却完全没有进入 Retrieval，那么它就是非常值得调查的 False Negative。

因此：

> **Retrieval 的失败不只体现在"选错"，更重要的是"漏掉"。**

------------------------------------------------------------------------

# 24. 这次知识移交带来的架构认识

通过这些中间产物，可以看到 TeslaCanPython 已经不只是：

``` text
ASC
↓
Python
↓
Report
```

而是形成了一个明确的认识链：

``` text
Raw Data
   ↓
Engineering Observation
   ↓
Candidate
   ↓
Semantic Visibility Selection
   ↓
LLM Reasoning
   ↓
Contract Validation
   ↓
Evidence Draft
   ↓
Human Approval
```

真正需要长期保护的是：

``` text
事实不能被语义覆盖
Observation 不能被 Candidate 取代
Retrieval 不能偷偷成为答案生成器
Finding 不能自动升级成 Evidence
Validation 不能被误解成语义正确
Approved Evidence 必须有明确边界
```

------------------------------------------------------------------------

# 25. 对后续项目移交方式的意义

以后与 Codex 的协作，不必再由人逐文件告诉它：

``` text
打开哪个 Python
修改哪个函数
生成哪个 JSON
```

更合理的是：

``` text
用户
  ↓
正常工程目标
  ↓
Codex
  ├─ 读取 Project Context
  ├─ 读取本地 L3
  ├─ 判断当前状态
  ├─ 找正式入口
  ├─ 执行
  ├─ 测试
  └─ 正确停止
```

而 ChatGPT 更适合承担：

``` text
架构 Review
边界 Review
反向质疑
防止过度设计
发现语义越权
必要时落锤
```

这也是这次"先理解中间产物"的真正价值：

> **项目移交的不是文件名，而是系统为什么这样分层、每一层能证明什么、不能证明什么。**

------------------------------------------------------------------------

# 26. 最终应记住的几个问题

以后面对任何新的 TeslaCanPython Run，可以依次问：

``` text
1. Raw ASC 完整进入 Observation 了吗？

2. Observation 中哪些是确定性事实？

3. Candidate 为什么被选出来？

4. Retrieval 为什么让 AI 看到这些，而不是另外一些？

5. Frozen LLM Input 是否保留了足够的语义可能性？

6. Finding 是事实还是推理？

7. Validation 到底证明了什么？

8. Evidence Binding 是否仍然只是 Draft？

9. Approved Evidence 的边界在哪里？

10. 每条结果能否沿 Provenance 回到 Raw ASC？
```

如果这十个问题都能清楚回答，才算真正理解了这条分析管线。

------------------------------------------------------------------------

## 一句话总结

> **理解 TeslaCanPython 中间产物，不是为了学会读一堆
> JSON，而是为了知道：从 Raw ASC 到 Approved Evidence
> 的每一步，系统究竟增加了什么认识，又凭什么增加这种认识。**

而在当前架构中，最值得继续追问的一句话是：

> **"为什么 AI 只看到了这些？"**
