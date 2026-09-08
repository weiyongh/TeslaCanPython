# TM3-006 原始分析流程考古

## 1. 审计范围与结论摘要

本报告只读审计以下原始材料：

- `src/analyze_tm3_006.py`
- `input/TM3-006_动力电池静态基线采集脚本.txt`
- `output/TM3-006/TM3-006_动力电池信号采样.csv`
- `output/TM3-006/TM3-006_动力电池静态基线分析结论.md`
- `doc/TM3-002_006采集分析汇总.md`
- 相关 Git 历史

没有读取或重新解析 ASC，没有运行 `analyze_tm3_006.py`，没有执行 Phase 3 Discovery/Reasoning，也没有发起新的 LLM 调用。

原始脚本、采集脚本和最终报告均在 commit `3ebd4d8`（2026-08-28）首次加入。当前原始脚本与报告的 SHA-256 与该 commit 中版本完全一致。当前 `output/TM3-006/discovery_spike/`、`output/TM3-006/pipeline_v3/` 和 `input/TM3-006_formal_discovery_charter.json` 是后续 Phase 3 产物，不属于 TM3-006 原始分析链。

核心结论：

> TM3-006 原始流程不是“全量 CAN Observation Discovery → 自动候选压缩”，而是“人工确定电池问题和目标 Signal 范围 → DBC 反查对应 CAN ID → Python 只解码这些报文并做结构化统计 → 人工/LLM基于统计、CSV、DBC物理含义和跨实验背景形成自然语言报告”。

它已经很好地体现了“Python 做确定性数值处理、语义层做物理解释”，但其入口仍由 DBC Signal 名单主导，缺少全量 Observation Space、Residual/Unknown 竞争、通用变化点/关系特征和正式可审计的 LLM 输入合同。

---

## 2. ① ASC 是全量 CAN ID 扫描，还是以 DBC Signal 为入口

### 结论

**原始 TM3-006 是以 DBC Signal 为入口，不是全量 CAN ID 扫描。**

代码顺序是：

1. 加载唯一 DBC：`input/tesla_model3_ONYX.dbc`。
2. 从 DBC 中选择目标 Signal：
   - 43 个 `EXPLICIT` Signal；
   - 正则 `BMS_brick\d+`；
   - 所有以 `BMS_a` 开头的字段；
   - 所有以 `HVP_w` 开头的字段。
3. 由这些 Signal 反查其 `frame_id`，生成 `wanted_by_id`。
4. 顺序读取 ASC，但遇到不在 `wanted_by_id` 的 CAN ID 就立即跳过：
   `if not frame or frame["can_id"] not in wanted_by_id: continue`。
5. 只对选中的 CAN ID 进行 DBC 解码。

按当前 DBC 静态复核，该入口选择了约 300 个 DBC Signal，分布在 18 个 CAN ID。最终 CSV 实际出现 298 个 Signal、91,867 条采样记录，时间范围约 0.0046–89.5392 s。

因此，“程序遍历了 ASC 的全部文本行”不等于“程序分析了全部 CAN ID”。它只是在流式读取时过滤，未对未命中 DBC 目标集合的报文建立统计、Residual 或 Unknown Observation。

---

## 3. ② Python 实际做了什么

## 3.1 ASC 解析与定向解码

Python 使用 `parse_asc_line()`逐行解析 ASC，然后：

- 按预选的 18 个 CAN ID 过滤；
- 对普通报文调用 cantools DBC decode；
- 使用 `decode_choices=True`保留枚举语义；
- 使用 `allow_truncated=True`容忍截断报文；
- 捕获逐 CAN ID decode exception，并只在终端输出 `FRAMES_ERRORS`；
- 对数值统一转换为 `float`；
- 保存每个 Signal 的 `(timestamp, value)`完整序列。

### 0x252 特例

`0x252`因 DBC 中 `BMS_hvacPowerBudget`与其他字段重叠，没有走通用解码器，而是按 little-endian raw bits 手工解析：

- bits 0–15：`BMS_maxRegenPower`，factor 0.01；
- bits 16–31：`BMS_maxDischargePower`，factor 0.01；
- bits 32–41：`BMS_maxStationaryHeatPower`；
- bit 48：`BMS_powerLimitsState`。

但只有属于 `wanted_by_id`的字段会写入最终 series；`BMS_maxStationaryHeatPower`不在目标选择中，因此没有进入 CSV。这一特例是“已知 DBC 冲突后的人工定向修复”，不是通用 DBC 冲突解析机制。

## 3.2 持久化输出

唯一机器持久化输出是：

`output/TM3-006/TM3-006_动力电池信号采样.csv`

字段只有：

- `signal`
- `time_s`
- `value`

CSV 保存了解码后的逐 Signal 完整采样，不保存：

- CAN ID / channel / DLC；
- DBC source / definition fingerprint；
- decode error；
- Signal 选择原因；
- raw ASC line reference；
- Known/Residual/Unknown；
- Observation/Candidate ID；
- 自动变化点或跨 Signal relationship。

这些信息部分仍能通过脚本和 DBC人工反查，但 CSV 本身不是完整 provenance artifact。

## 3.3 全局统计

脚本对 `EXPLICIT`集合逐项打印：

- 数值 Signal：`n / min / max / avg`；
- 枚举或字符串 Signal：全程出现过的唯一值；
- 未出现 Signal：`MISSING`。

注意：这只覆盖 43 个显式字段，不是对 298 个输出 Signal 的统一统计。

## 3.4 固定时间窗口

脚本硬编码三个稳定窗口：

- 10–40 s：`stable1`
- 40–70 s：`stable2`
- 70–90 s：`stable3`

窗口边界使用 `start <= t <= end`，每窗仅对 11 个指定连续量计算 `min / max / avg`：

- `BMS_packVoltage`
- `BMS_packCurrent`
- `BMS_socAvg`
- `BMS_socUI`
- `BMS_brickVoltageMax`
- `BMS_brickVoltageMin`
- `BMS_maxChargeCurrent`
- `BMS_maxDischargeCurrent`
- `HVP_packVoltage`
- `HVP_dcLinkVoltage`
- `HVP_battery12V`

这些窗口直接来自采集脚本的 10 s、40 s、70 s、90 s计划节点。代码没有独立识别实测状态边界，也没有区分 Planned Time 与 Observed Event Time。由于本实验设计为全程静止保持，这一不足没有像瞬态实验那样明显破坏报告，但仍是方法边界。

## 3.5 状态变量与连续变量

Python 没有建立通用变量类型系统，但处理方式上存在两类：

- 连续数值：全局/窗口 `min / max / avg`，例如 Pack V/I、SOC、电压、能力边界；
- 枚举/离散状态：只汇总出现过的唯一值，例如挡位、系统状态、接触器、HVIL。

它没有计算：

- 离散状态驻留时间；
- 状态转换序列；
- first/last change；
- transition count；
- 稳定区自动发现；
- 同步 lead/lag；
- tracking error；
- 关系置信度。

最终报告中的“全程不变”“打开/闭合”“约 0.5 s 交替”等表述，有些可由 CSV人工检查得到，但不是脚本标准化输出的统一 feature。

## 3.6 Brick 结构统计

这是原始 Python 最成熟的专项压缩机制：

1. 收集所有匹配 `BMS_brick\d+`的通道；
2. 计算每个 Brick 的全程均值；
3. 用 2.5–4.5 V 规则划分 valid 与 invalid/unused；
4. 找有效 Brick 均值最低/最高通道；
5. 计算有效 Brick 均值跨度；
6. 聚合所有有效 Brick 样本的全局 min/max。

CSV复核显示：

- 108 个精确 `BMS_brickN`通道；
- 另有 4 个 `BMS_brickVoltageMax/Min`及编号字段，因此以 `BMS_brick`开头共 112 个；
- 报告进一步形成 106 个有效、2 个固定 0 V占位的物理解释。

Python完成了有效范围、极值与跨度压缩；“106 串联组总和与 Pack 电压闭合，因此两个 0 V为占位”的语义和物理解释不是脚本直接输出，而是下游分析形成。

## 3.7 告警筛选

Python扫描所有匹配 `^(BMS_a|HVP_w)\d{3}_`的已选告警字段，若数值最大值不为 0，就加入 `ACTIVE_ALERTS`。

这是非常简单的候选筛选：

- 优点：快速把大量全零告警压缩成非零候选；
- 限制：不处理 SNA、翻页、counter、toggle、历史锁存、枚举语义、占空特征或 DBC 冲突。

报告对 `HVP_w001_WatchdogReset`周期翻转和 `BMS_a084`固定为 1 的谨慎解释，明显超出了 Python 的“max != 0”规则。

---

## 4. ③ DBC 在哪个阶段参与、承担什么作用

DBC 从流程最前端就参与，而且承担四种职责：

1. **Admission / 边界定义**：先按 Signal 名称选择字段，再由字段决定允许分析的 CAN ID。这是原流程最关键的 DBC 主导点。
2. **Decode**：提供 bit layout、factor、offset、unit、enum choice 和 message identity。
3. **语义命名**：CSV以 DBC Signal name 作为唯一变量身份；报告也以这些名称组织电压、电流、SOC、接触器和告警。
4. **被验证对象**：下游用物理一致性识别 DBC冲突，例如温度上下界颠倒、绝缘为 0、母线边界与实测 Pack 电压不闭合、Watchdog 位周期翻转。

因此 DBC 在 TM3-006 中既是入口、解码字典和语义提示，也是被实测反证的对象。后两种角色值得保留；第一种“用 DBC决定 Observation Space”的角色不符合当前目标。

0x252 手工解码还说明：当 DBC 整帧因重叠字段失败时，原流程能够进行局部人工纠偏，但该纠偏是车型/报文专用代码，不具备通用 conflict view、并列定义或版本审计能力。

---

## 5. ④ Python、LLM与人工提示分别完成了什么

## 5.1 可确认由 Python 完成

- ASC逐行语法解析；
- 目标 CAN ID过滤；
- DBC解码和枚举转换；
- 0x252 特定位段解码；
- 解码错误计数；
- 每个目标 Signal 的完整时序 CSV；
- 43 个显式 Signal 的全局 min/max/avg、唯一值或 missing；
- 3 个固定窗口内 11 个数值 Signal 的 min/max/avg；
- Brick均值、有效范围筛选、最低/最高/跨度和全局范围；
- 非零 BMS/HVP告警候选列表。

## 5.2 明确来自人工设计/提示

- 实验问题是“P挡、静止、关闭负载、未插枪下的动力电池静态基线”；
- 10/40/70/90 s的窗口设计；
- 要观察 SOC、Pack V/I、温度、Brick压差、充放电能力、接触器、HVIL、DC-link和12 V；
- `EXPLICIT` 43字段名单；
- `BMS_brickN`、`BMS_a*`、`HVP_w*`命名规则；
- Brick有效电压 2.5–4.5 V阈值；
- 0x252手工位段与缩放；
- 报告要围绕控制链、物理一致性与 DBC边界回答问题。

这里的“人工”包括采集脚本作者和分析代码作者。仓库没有保留当时完整对话，无法再细分哪些具体选择由用户提示、开发者判断或模型建议提出。

## 5.3 很可能由 LLM/人工分析层完成，但无法从仓库严格区分

原始代码不调用 LLM，也没有 prompt、request payload、模型配置或会话记录。最终 Markdown 与代码在同一 commit 中提交，只能证明它们属于同一工作批次，不能证明每一句由谁写成。

但从“代码未直接输出、报告却完成了”的差值，可以确认存在一个代码之外的语义分析/写作层。该层完成了：

- 将窗口统计组织成自然语言稳定性判断；
- 计算或解释窗口均值极差；
- 由约 348 V和约 1.1 A派生约 0.38 kW背景功率；
- 将 106 个 Brick均值和与 Pack 电压做物理闭环；
- 区分 SOC、能量字段及 SOH外推边界；
- 解释 Capability 与 Actual；
- 将接触器、HVIL、Pack/DC-link组合为“高压已建立”的状态判断；
- 对温度、绝缘、母线边界和告警 DBC定义做冲突判定；
- 将结果组织为“条件—决策—执行—反馈—结果”、控制树增量和下一步验证；
- 引用 TM3-004/005 已确认的 Pack电流符号背景。

这些工作符合 LLM擅长的语义综合，但也可能包含人工复核或编辑。没有历史会话证据时，不应把它们全部断言为 LLM独立完成。

---

## 6. ⑤ Python 最终给 LLM 的实际材料是什么

### 能够从仓库证明的答案

**没有正式、可重放的“Python → LLM”接口。**

`analyze_tm3_006.py`没有 LLM调用代码、prompt builder、Reasoning Input JSON或审计 trace。它产生两类材料：

1. 持久化的 `TM3-006_动力电池信号采样.csv`：
   - 298 个 Signal；
   - 91,867 个逐时刻解码样本；
   - 只有 signal/time/value。
2. 终端 stdout：
   - decode error counts；
   - EXPLICIT Signal的 range/value/missing；
   - 三个窗口统计；
   - Brick统计；
   - ACTIVE_ALERTS。

stdout没有作为独立 artifact 保存，因此今天无法证明当时 LLM看到的确切 stdout内容或完整性。

### 合理但不能升级为事实的推断

报告很可能是在分析会话中结合以下材料形成：

- 采集脚本；
- Python脚本；
- Python终端输出；
- 采样 CSV；
- DBC含义；
- TM3-004/005跨实验背景；
- 用户关于基线与控制链的分析要求。

但仓库没有保存 exact prompt、附件清单、上下文窗口或模型信息。因此不能证明“LLM实际只收到这些”，也不能恢复精确 payload。这正是新架构需要冻结 Pre-LLM Input Package 和 call provenance 的原因。

---

## 7. ⑥ 为什么 TM3-006 能形成较自然的人类可读报告

原因不是 Python自动生成了报告，而是输入问题、数值压缩和语义写作之间匹配得很好。

### 7.1 实验问题窄且静态

TM3-006没有复杂的人为瞬态动作。三个窗口都要求保持同一状态，因此简单的窗口 min/max/avg已经足以支撑“稳定或冲突”的主要判断，不必先恢复精细事件序列。

### 7.2 人工预选 Signal 与问题高度匹配

目标名单直接覆盖报告需要的主体：

- 车辆状态；
- Pack V/I；
- SOC/能量；
- Brick；
- 能力边界；
- 接触器/HVIL；
- Pack/DC-link/12 V；
- 温度、绝缘和告警。

这使下游无需从数千 Signal中发现主题，拿到的数据天然接近报告目录。自然报告的代价是较强的先验筛选和对 DBC覆盖率的依赖。

### 7.3 Python把海量样本压成可理解的数值事实

91,867行 CSV背后，窗口均值、Brick极值/跨度、非零告警等输出已经把大部分重复采样压缩为少量事实。语义层无需逐帧阅读 ASC。

### 7.4 存在多个强物理闭环

例如：

- Pack voltage ≈ DC-link voltage；
- 有效 Brick均值之和 ≈ Pack voltage；
- nominal remaining / nominal full 与 SOC量级一致；
- 温度 max/min关系和热惯性冲突；
- isolation=0 与接触器/HVIL/母线状态冲突。

这些关系很适合 LLM/人工用通用物理知识组织为“证据→判断→边界”。

### 7.5 最终报告不是模板堆字段

报告围绕一个清楚的静态电池问题组织，主动区分：

- 可用基线；
- DBC解释值；
- 物理一致性支持；
- 冲突字段；
- 不能外推的结论；
- 控制树贡献；
- 最小下一步验证。

因此读起来像分析，而不是程序 dump。其自然性主要来自下游语义综合和人工问题框架，不是原 Python具备自然语言报告能力。

---

## 8. ⑦ 对当前目标的启示

当前目标是：

> 程序负责海量 ASC 数据处理和候选压缩，LLM负责语义分析。

## 8.1 值得保留的机制

### A. 确定性数据层与语义层分工

Python负责 parse/decode/statistics，语义层负责解释、物理闭环、控制树映射和边界表达。这个基本分工是正确的。

### B. 完整时序先落盘，再做摘要

虽然 CSV provenance不足，但保存逐 Signal time/value使语义结论仍可复核。新机制应保留“摘要可追溯到原始样本”的原则，并补齐 bus key、DBC fingerprint、raw refs。

### C. 实验问题驱动的窗口与变量选择

采集脚本明确了三个稳定窗口和判读问题。新机制不应退回无目的全量统计，而应让 L3/ER/Collection Script引导候选检索，同时保持全 Observation Space可竞争。

### D. 专项物理压缩器

Brick有效性、极值、跨度、总和与 Pack闭环是高价值 domain feature。类似的确定性物理特征应作为可审计工具保留，而不是让 LLM从数万行中自行计算。

### E. DBC既用于解码，也必须接受实测验证

原报告没有把所有 DBC字段当真，能通过物理矛盾淘汰温度、绝缘、母线边界和告警解释。这一审慎边界应保留。

### F. 明确输出缺失和冲突

`MISSING`、decode errors、invalid/unused Brick、非零告警候选都属于有价值的负证据与异常入口。

## 8.2 必须由新机制补上的不足

### A. 全量 Observation Space

必须对所有实际 bus key/CAN ID/DLC建立基础 Observation，而不是先由 DBC Signal whitelist决定哪些报文值得分析。否则 DBC缺失的关键字段永远不会进入候选。

### B. Known / Residual / Unknown并行竞争

原流程没有 Residual/Unknown概念。新机制需要让：

- DBC Known Signal；
- 部分可解码或冲突定义的 Residual；
- 无 DBC语义的 Unknown behavior

在统一、可追溯的最低门槛下参与检索。

### C. 通用候选压缩而非车型专用名单

`EXPLICIT`、前缀规则和 0x252特例有效但难以迁移。新机制需要通用的稳定性、动态性、基数、变化区域、异常值、周期性和物理量特征，同时允许专项 adapter，而不是把专项逻辑变成唯一入口。

### D. 真实事件与计划窗口分离

原代码直接把脚本秒数作为统计窗。新机制必须区分：

- Planned Time；
- Observed Human Event Time；
- CAN Observed State Time。

缺少可靠 phase feature时应明确 `UNAVAILABLE`，不能以计划窗口建立瞬态因果。

### E. 状态变化点与连续变量变化特征

原脚本没有统一输出 change count、first/last change、state sequence、stable region、slope、step、edge或恢复过程。新机制应由 Python生成这些候选特征，避免 LLM人工扫描 CSV。

### F. 跨 Signal relationship feature

报告中的 Pack/DC-link闭合、Brick总和、SOC/energy比例等关系依赖额外语义分析。新机制应逐步增加可复现的同步比较、差值、tracking、lead/lag和物理闭环 feature，但必须保留“统计关系不自动等于因果”。

### G. 完整 provenance

原 CSV缺 CAN ID、channel、DLC、DBC source、definition fingerprint、raw refs和选择理由。新机制必须做到：

`ER → Intent → Observation → Context/Feature → Finding → Evidence Binding → Raw ASC`

### H. 冻结、可审计的 LLM输入

TM3-006无法回答“LLM到底收到什么”。新机制必须冻结：

- L3/ER/Procedure；
- selected observations；
- behavior/context；
- unavailable features；
- reference manifest；
- package hash；
- model/call配置；
- exact payload或明确不可恢复状态。

### I. DBC从 Admission Authority降为 Reference Metadata

DBC仍应承担解码、命名、单位、枚举和候选解释，但不能决定分析边界，也不能仅凭名称确认 Request/Actual/Capability/Permission。

### J. 输出合同与人读层分离

TM3-006自然报告依赖一次性语义写作，缺少 Finding/Evidence Mapping/RVM的稳定中间层。新机制应保留自然表达，同时让每个结论可回溯、可验证、可审核，而不是把模板变成新的推理器。

---

## 9. 原始流程与目标架构对照

| 维度 | TM3-006 原始机制 | 当前目标 |
|---|---|---|
| ASC入口 | 遍历全部行，但只接受DBC目标CAN ID | 全量bus key/CAN ID/DLC Observation |
| Signal选择 | 43个显式名称 + 3类命名规则 | L3/ER引导、Known/Residual/Unknown竞争 |
| DBC角色 | admission + decode + semantic hint + validation target | decode/reference/validation target，不控制边界 |
| Python压缩 | range/avg、3窗口、Brick、非零告警 | 通用behavior/phase/relationship + 专项物理feature |
| 变化点 | 未标准化 | 状态/连续变量变化特征可追溯 |
| 时间语义 | 计划秒数直接作为窗口 | Planned/Observed/CAN time分离 |
| 未知报文 | 完全不进入分析 | first-class候选 |
| LLM输入 | 无正式合同，可能是CSV+stdout+上下文 | 冻结package、manifest、hash、call provenance |
| LLM职责 | 物理解释、冲突判断、报告组织 | 语义映射、Evidence Gap、Validation Proposal |
| 人工职责 | 实验设计、Signal名单、阈值、特例、复核 | L3/ER与实验设计、Evidence Review、边界裁决 |
| 可追溯性 | 报告→Signal/CSV，不能直接到raw line | 完整 lineage 到 raw refs |
| 人读输出 | 自然但一次性 | 自然且由结构化上游事实约束 |

---

## 10. 最终判断

TM3-006值得保留的不是“DBC Signal白名单”或“为每个实验写一份专用脚本”，而是以下组合：

`明确实验问题 → Python确定性压缩 → 物理一致性核对 → LLM/人工语义综合 → 清楚表达证据边界`

它的成功证明了 Python不需要替代 LLM做语义裁决；只要把大规模样本压成高质量、与实验问题相关、可追溯的事实，LLM就能形成自然分析。

它的不足也同样明确：Python只处理了人和 DBC已经知道要看的东西。要实现当前目标，新机制必须在不丢失实验导向的前提下扩大到全量 Observation Space，并把 Unknown发现、变化特征、关系证据、provenance和 Pre-LLM输入冻结补齐。

换言之，正确演进不是抛弃 TM3-006，而是：

> 保留它的“专项统计与物理闭环”，替换它的“DBC决定入口”和“非正式LLM交接”。

