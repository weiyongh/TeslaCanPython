# TeslaCanYi：用“纯净环境 Challenge”盲打 TeslaCanPython

## 1. 这招是干什么的

`TeslaCanYi` 不是 TeslaCanPython 的分支，也不是拿 TeslaCanPython 的中间结果继续分析。

它是一个独立考场：

- **TeslaCanPython（Py）**：已经形成正式工程、方法、流程和历史经验。
- **TeslaCanYi（Yi / 叶问）**：在纯净环境下，只拿原始题面和原始 Evidence，自行分析。
- **Challenge 的目标**：不仅比较“谁找到的 Signal 更多”，还比较双方如何理解问题、如何建立分析流程、如何产生中间产物、如何失败和自我修正。

核心思想：

> 同一张考卷，Py 和 Yi 各自作答。  
> Py 的草稿纸不能给 Yi。

---

## 2. 为什么不能给 Yi 看 Py 的中间文件

如果输入变成：

```text
原始数据
↓
Py 的 Observation / Retrieval / 过滤 / Candidate
↓
Yi 继续推理
```

这不是“Yi 打 Py”，而是：

> **Yi 接着 Py 打。**

真正的 Challenge 应该是：

```text
                 同一张考卷

              原始实验题面
              原始采集数据
              原始现场 Evidence
                    │
             ┌──────┴──────┐
             ↓             ↓
      TeslaCanPython    TeslaCanYi
             ↓             ↓
         Py 的方法链      Yi 的方法链
             ↓             ↓
          Py 的结果       Yi 的结果
             └──────┬──────┘
                    ↓
                 最后对比
```

因此，Py 的中间产物属于**答案袋**，不能进入 Yi 的**试卷袋**。

---

## 3. “纯净环境”不是“什么都不给”

一个很重要的边界：

> **不给答案 ≠ 不给实验条件。**

Yi 应该知道：

- 实验目的是什么；
- 实验如何设计；
- 实际进行了哪些操作；
- 什么时间发生了什么；
- 原始 CAN 数据是什么；
- 现场观察到了什么；
- 采集条件和数据质量怎样。

Yi 不应该知道：

- 已有 DBC；
- 已知 Signal 定义；
- 已确认 CAN ID / byte / bit；
- TeslaCanPython 的历史分析结果；
- Observation / Retrieval；
- Signal Candidate；
- Evidence Mapping；
- Approved Evidence；
- RVM；
- 最终四件套；
- Notion L3 知识；
- 已有 reverse 程序和过滤算法；
- Golden Answer。

一句话判断：

> **这个文件是在告诉 Yi“题目是什么”，还是在告诉 Yi“答案是什么”？**

前者可以给，后者不能给。

---

## 4. 当前 Slow Charge FullCycle Challenge 输入

当前 Py 给出的题面：

```text
TeslaCanYi/input/
├── case/
│   ├── L3-Charge-Slow-FullCycle_Case契约.md
│   ├── L3-Charge-Slow-FullCycle_acquisition_plan.json
│   └── L3-Charge-Slow-FullCycle_慢充全过程采集.txt
├── contracts/
│   └── voicerunner_v1/
│       ├── 任务7_结构化导出_schema_v1_说明.md
│       ├── 任务7_结构化导出_schema_v1.json
│       └── event_timeline_csv_v1_接口合同.md
└── acquisition/
    └── L3-Charge-Slow-FullCycle_慢充全过程采集__20260911_133727_858__S0009/
        ├── TESLA-M3-SOP5
        ├── session.json
        ├── event_timeline.csv
        ├── can/
        │   ├── can_20260911133648.asc
        │   └── can_20260911133648_2.asc
        └── photos/
            ├── E03-P01_插枪_20260911_133907_626.jpg
            ├── E05-P01_扫码启动_20260911_134042_388.jpg
            ├── E05-P02_扫码启动_20260911_134050_424.jpg
            ├── E05-P03_扫码启动_20260911_134127_933.jpg
            ├── E06-P01_记录充电数据1_20260911_134133_171.jpg
            ├── E06-P02_记录充电数据1_20260911_134249_787.jpg
            ├── E07-P01_记录充电数据2_20260911_134255_656.jpg
            ├── E08-P01_停止充电_20260911_134356_019.jpg
            └── E08-P02_停止充电_20260911_134401_541.jpg
```

这里的原则是：

- Case Contract：题目边界。
- Acquisition Plan：实验 Should。
- VoiceRunner Script：实验设计和动作计划。
- Schema / Interface Contract：让 Yi 正确理解原始结构化数据，不属于答案。
- `session.json` / `event_timeline.csv`：实际发生的 Session / Event Evidence。
- ASC：核心原始证据。
- Photos：现场原始 Evidence。
- `TESLA-M3-SOP5`：需确认其内容；如果只是采集/车辆/SOP 元数据可以给，如果包含已知 Signal、DBC、CAN ID 或分析结论则删除。

当前阶段不要继续为了“完整”往 input 里塞文件。

---

## 5. 为什么照片、时间线、现场备注可以给

Challenge 不是把 Yi 蒙住眼睛。

例如：

```text
48.76 s：
用户把鼓风机从 1 档调到 5 档，
现场观察出风明显增加。
```

这是实验 Ground Truth，不是 CAN 答案。

真正需要 Yi 自己完成的是：

```text
现场事件
↓
CAN 时间对齐
↓
变化发现
↓
ID / byte / bit Candidate
↓
重复性 / 相关性验证
↓
Evidence
↓
语义推断
```

所以原始现场 Evidence 可以充分提供。

---

## 6. 第一轮为什么不规定算法

第一次 Challenge 最有价值的问题不是：

> Yi 能不能把我们已经知道的方法重新执行一遍？

而是：

> 面对 ASC + Timeline + Photos + Contract，Codex 自己会发明什么 reverse workflow？

因此第一轮不要提前教：

- entropy；
- bit flip；
- correlation；
- clustering；
- change point；
- event-window score；
- differential analysis；
- rolling statistics；
- mutual information；
- known-signal transfer；
- Py 已经实现过的算法。

甚至不要告诉 Yi：

> “你应该先解析 ASC，再切 Event Window。”

让它自己决定木人桩摆在哪里。

---

## 7. 第一轮 Challenge Prompt

```markdown
# TeslaCanYi Challenge 001

这是一次纯净环境 CAN Reverse Challenge。

## 目标

仅使用 `input/` 中提供的材料，独立分析本次慢充 Full Cycle 采集。

你的任务不是复现任何已有答案，而是从原始实验数据和现场 Evidence 出发，自行发现：

1. 本次实验过程中 CAN 数据发生了什么。
2. 哪些 CAN ID / byte / bit / value pattern 与实验事件存在可信关联。
3. 能否从这些变化中识别出具有诊断价值的 Signal Candidate。
4. 能否建立操作事件、车辆状态变化与 CAN Evidence 之间的关系。

## 规则

- 只能使用 `input/`。
- 不得读取本项目之外的任何文件。
- 不得使用外部 DBC、Tesla 已知 Signal 定义、历史分析结果或互联网答案。
- 不得假设 Signal 的语义。
- 猜测必须明确标记为猜测。
- 结论必须能够回指原始 Evidence。
- 允许自行编写程序、建立中间数据结构并设计分析方法。
- 不限制分析路线。

## 第一轮要求

先独立完成一次探索。

不要向我询问应该使用什么算法。
不要询问已有答案。
不要为了获得答案而搜索外部资料。

如果第一轮无法得到满意结果，也请保留结果，并说明：

- 你发现了什么；
- 你没有发现什么；
- 当前方法的主要限制；
- 下一轮你准备如何改进。

现在开始。
```

第一轮甚至可以**不规定输出文件名和 CSV Schema**。

因为“Yi 自己决定产生什么中间产物”本身就是考试内容。

---

## 8. Challenge 的真正观察指标

### 8.1 第一眼怎么看题

观察 Yi 是：

- 先理解 Case 和实验设计；
- 先建立事件模型；
- 先看 Timeline；
- 直接扑进 ASC；
- 还是先检查照片和 Session。

这能反映它如何建立问题模型。

### 8.2 自己会产生什么中间产物

这是最重要的观察之一。

例如 Yi 是否自然形成：

```text
ASC
↓
解析
↓
时间对齐
↓
事件窗口
↓
ID 变化筛选
↓
byte / bit 分析
↓
模式识别
↓
Candidate
↓
Evidence
↓
语义推断
```

如果 Yi 在完全不知道 Py 方法的情况下，也自然长出了类似：

```text
Observation
↓
Retrieval
↓
Candidate
↓
Evidence
```

这说明 Py 的某些架构可能不是人为规则，而是问题本身具有的自然结构。

反过来，如果 Yi 发明了一条完全不同、效果更好的路线，那更有价值。

### 8.3 打不过以后怎么办

第一轮失败不能立即喂答案。

推荐节奏：

```text
第一轮：裸奔
↓
结果不足
↓
Yi 自己复盘
↓
Yi 自己提出下一轮方法
↓
第二轮继续撞墙
↓
仍然不足
↓
只给方向性提示
↓
再运行
↓
最后才考虑提供算法知识
```

这可以观察 Codex 是否具有：

- 方法反思能力；
- 失败归因能力；
- 新策略生成能力；
- 自我迭代能力。

---

## 9. 最后怎么“Yi 打 Py”

最终不应该只比较 Signal 命中率。

至少比较：

### 结果层

- 找到多少有效 Candidate；
- 命中多少已知 Signal；
- False Positive 数量；
- 置信度是否校准；
- 是否把猜测写成事实。

### Evidence 层

- 是否能回指原始 ASC；
- 是否正确利用 Event Timeline；
- 是否利用重复事件；
- 是否利用照片和现场状态；
- Evidence 是否真正支持结论。

### 方法层

- 时间窗口如何建立；
- 噪声如何过滤；
- CAN ID 如何初筛；
- byte / bit 如何定位；
- 连续量、状态量如何区别；
- counter / checksum 如何识别或排除；
- 是否发现 Py 没发现的模式。

### 工程层

- 自己写了什么工具；
- 产生了什么中间文件；
- 工作流是否可重复；
- 下一次 Challenge 能否复用；
- 是否形成了值得反哺 TeslaCanPython 的新算法或新结构。

真正有价值的结果甚至可能不是：

> Yi 打赢 Py。

而是：

> **Yi 走了一条 Py 没想到的路，其中某些方法值得吸收到 TeslaCanPython。**

---

## 10. 权限边界

如果人不在电脑旁，可以提前让 Yi 说明预计需要的授权并一次性授权必要操作。

但权限仍应遵循：

> **能运行，不等于能越界。**

最好只允许完成 Challenge 所需要的：

- 在 `TeslaCanYi` 内读写；
- 运行本地分析程序；
- 创建临时文件和中间产物；
- 执行必要命令。

不要为了减少授权弹窗而开放：

- TeslaCanPython；
- Notion；
- 本地 DBC；
- 历史报告；
- 其他答案目录。

操作系统权限边界和 Challenge 逻辑边界最好一致。

---

## 11. 可长期复用的 Challenge Protocol

以后可以固定成：

```text
Py：出题
↓
列出合法输入文件
↓
人工审核：题面还是答案？
↓
复制到 TeslaCanYi/input
↓
Yi：第一轮裸奔
↓
保存 Yi 全部中间产物和结果
↓
Yi：自我复盘
↓
必要时第二轮自主改进
↓
仍不足时才逐级给提示
↓
最后打开 Py 的“答案袋”
↓
Yi vs Py 对比
↓
提炼值得反哺 Py 的方法
```

可以进一步给 Challenge 编号：

```text
CH-001 SlowCharge FullCycle
CH-002 HVAC Blower
CH-003 Door Open/Close
CH-004 HVAC Recirculation
...
```

每次 Challenge 都保存：

```text
题面
原始 Evidence
Yi 第一轮结果
Yi 自我复盘
Yi 第二轮结果
提示记录
Py 原结果
最终对比
方法改进结论
```

久而久之，这本身会成为一个很有价值的 **CAN Reverse Benchmark / Challenge Corpus**。

---

## 12. 一句话原则

> **Py 给 Yi 出考卷，不给草稿纸；Yi 自己找木人桩、自己造拳法，打完以后再开答案袋。**

这就是 `TeslaCanYi` 的存在意义。
