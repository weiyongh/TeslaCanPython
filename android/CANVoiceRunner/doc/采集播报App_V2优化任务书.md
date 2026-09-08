# 采集播报 App V2 优化任务书

> 目标：针对现有 CAN / ASC 基线数据采集过程中已经暴露出的真实问题，对采集播报 App 做一次**有限、收敛、可验证的优化**。  
> 本轮不是重做 App，也不是扩展成完整的数据采集平台。只解决已经在实际采集中证明有价值的问题。

---

## 1. 背景

现有采集播报 App 的基本作用是：

- 按预设采集脚本进行计时；
- 在指定时间播报操作提示；
- 辅助驾驶员/采集人员按照统一流程完成车辆操作；
- 为后续 ASC 数据分析提供大致的操作时间参考。

经过 Model 3 多轮基线采集和 TM3 数据分析后，现有方案暴露出一个核心问题：

> **Planned Time（计划时间）适合作为现场操作指导，但不能被当成真实事件发生时间。**

例如：

```text
00:30  插枪
00:45  开始充电
01:00  观察状态
```

这是实验脚本的计划时间。

但实际操作过程中会受到以下因素影响：

- 人工操作速度；
- 充电枪插入过程；
- 车辆响应；
- EVSE 响应；
- UI 操作；
- 拍照；
- 临时观察；
- 其他不可控延迟。

因此：

```text
Planned Time ≠ Observed Event Time
```

后续 ASC 分析真正需要的时间锚点，应当是：

```text
Observed Event Time
```

而不是简单根据 Planned Time 建立固定分析窗口。

本轮优化的核心，就是让采集播报 App 从：

> **“定时语音提醒器”**

向：

> **“实验执行辅助 + 现场事件时间锚定工具”**

前进一步。

但必须严格控制范围，不能演化成新的大型采集平台。

---

# 2. 本轮目标

本轮只实现以下五类优化：

1. 后台持续计时与语音播报；
2. Planned Time 与 Observed Event Time 分离；
3. Event 支持多张照片及照片实际时间；
4. Event / Photo 支持可选备注；
5. 形成可供后续 ASC 分析程序使用的 Event Timeline 导出。

除此之外，不主动增加新功能。

---

# 3. 核心设计原则

## 3.1 Planned Time 只是执行指导

采集脚本中的计划时间继续保留。

例如：

```text
Event E03
Planned Time: 00:30
Action: 插入充电枪
```

App 应当在接近 `00:30` 时进行语音提示。

但是：

```text
00:30
```

不能直接被视为“充电枪实际插入时间”。

---

## 3.2 Observed Event Time 是分析锚点

用户完成动作后，通过最简单的现场操作记录真实事件时间。

例如：

```text
00:30.000  App 播报：请插入充电枪

00:34.827  用户点击：
            [完成 / 记录事件]
```

则：

```text
Planned Time       = 00:30.000
Observed Event Time = 00:34.827
```

后续 ASC 分析程序应优先使用：

```text
Observed Event Time
```

生成分析窗口。

---

## 3.3 Raw ASC 永远保持原始

App 不负责：

- 修改 ASC；
- 切割 ASC；
- 重新编码 ASC；
- 根据 Event 自动生成新的 ASC。

原始采集文件必须保持：

```text
Raw ASC = Immutable
```

Event Timeline 只是 ASC 的外部时间索引。

后续分析程序可以根据 Event Timeline 动态选择：

```text
Observed Event Time - Pre Window
                ↓
            Event
                ↓
Observed Event Time + Post Window
```

---

## 3.4 一个 ASC 可以包含多个 Session

不要假设：

```text
1 ASC = 1 Session
```

实际采集中可能出现：

```text
ASC
│
├─ Session 01
│  ├─ Event 01
│  ├─ Event 02
│  └─ Event 03
│
└─ Session 02
   ├─ Event 01
   ├─ Event 02
   └─ Event 03
```

特别是在：

- 路测；
- 重复验证；
- 充电测试；
- 多次开关车辆状态；

场景下，多 Session 是正常情况。

数据结构必须允许这种情况。

---

# 4. 功能需求

## 4.1 后台计时与语音播报

### 当前问题

当用户切换到其他 App 时，采集播报 App 的：

- 计时；
- 语音提示；

可能停止或失效。

实际采集过程中用户可能需要切换：

- CAN 采集软件；
- 相机；
- 车辆 App；
- 其他辅助软件。

因此播报 App 不能依赖始终处于前台。

### 要求

采集开始后：

```text
Start Session
     ↓
后台计时持续
     ↓
到达 Planned Time
     ↓
正常语音播报
```

即使 App 不在前台，也应尽可能维持实验计时和播报。

### 验收

启动一个测试脚本：

```text
00:10 播报 A
00:20 播报 B
00:30 播报 C
```

启动后立即切换到其他 App。

要求：

- 三次播报均正常发生；
- 时间误差处于系统合理范围；
- 返回 App 后当前 Session 状态正确；
- Event 状态不能因为切换前后台而丢失。

---

# 5. Event 时间模型

每个 Event 至少包含：

```text
event_id
session_id
planned_time
observed_time
action
status
notes
```

建议语义：

```text
planned_time
    计划执行时间

observed_time
    用户确认该事件真实发生的时间

action
    操作说明

status
    pending / completed / skipped

notes
    可选人工备注
```

---

## 5.1 Event 操作

每个 Event 应提供尽可能简单的现场操作。

至少：

```text
[完成 / 记录事件]
[跳过]
```

点击：

```text
完成 / 记录事件
```

立即记录：

```text
observed_time
```

不要要求用户再输入时间。

---

## 5.2 不允许自动用 Planned Time 填充 Observed Time

如果用户没有确认：

```text
observed_time = null
```

不能：

```text
observed_time = planned_time
```

否则会重新制造“计划时间冒充真实时间”的问题。

---

# 6. Event 照片

一个 Event 应允许：

```text
0...N Photos
```

而不是：

```text
1 Event = 1 Photo
```

例如：

```text
E05 充电开始

├─ Photo 01  仪表状态
├─ Photo 02  充电口状态
└─ Photo 03  EVSE 屏幕
```

---

## 6.1 Photo 数据

每张照片至少保存：

```text
photo_id
event_id
captured_time
file_path / file_reference
notes
```

其中：

```text
captured_time
```

必须是真实拍摄时间。

不能使用 Event Planned Time 代替。

---

## 6.2 Photo 与 Event 的关系

照片属于 Event：

```text
Session
   ↓
Event
   ↓
Photo[]
```

但：

```text
Photo captured_time
```

和：

```text
Event observed_time
```

是两个不同时间。

例如：

```text
Event observed_time = 10:32:15.200

Photo 01 = 10:32:17.800
Photo 02 = 10:32:22.100
```

必须分别保留。

---

# 7. Notes

## 7.1 Event Notes

Event 可以增加可选备注。

例如：

```text
充电枪已插入，充电口蓝灯持续约 3 秒后变化。
```

---

## 7.2 Photo Notes

每张照片也可以单独备注。

例如：

```text
仪表显示“正在准备充电”
```

---

## 7.3 Notes 必须是可选项

现场采集的第一优先级仍然是：

```text
动作
→
时间
→
数据
```

不能因为 Notes 功能导致现场操作复杂化。

因此：

```text
notes = optional
```

不能阻塞 Event 完成。

---

# 8. Event Timeline

App 应当能够形成完整的实际事件时间轴。

逻辑结构：

```text
Collection
│
├─ ASC / Recording Reference
│
├─ Session 01
│  │
│  ├─ Event E01
│  │  ├─ Planned Time
│  │  ├─ Observed Time
│  │  ├─ Action
│  │  ├─ Notes
│  │  └─ Photos[]
│  │
│  ├─ Event E02
│  └─ Event E03
│
└─ Session 02
   ├─ Event E01
   └─ Event E02
```

---

# 9. 导出

本轮重点不是设计复杂的报告，而是提供机器可读的 Event Timeline。

至少提供一种结构化导出。

优先考虑：

```text
JSON
```

如果现有工程已经使用其他结构化格式，可以沿用，但不要为了本轮任务额外建立复杂 Schema 系统。

建议结构示意：

```json
{
  "collection_id": "TM3-XXX",
  "sessions": [
    {
      "session_id": "S01",
      "events": [
        {
          "event_id": "E01",
          "planned_time": "00:00:30.000",
          "observed_time": "00:00:34.827",
          "action": "插入充电枪",
          "status": "completed",
          "notes": "",
          "photos": [
            {
              "photo_id": "P01",
              "captured_time": "00:00:37.211",
              "file": "...",
              "notes": ""
            }
          ]
        }
      ]
    }
  ]
}
```

注意：

> 上述只是语义示例，不要求机械照搬字段命名。Codex 应首先检查现有 App 的数据模型，并进行最小兼容修改。

---

# 10. 与 ASC 分析程序的边界

本轮 App 只负责生成：

```text
Experiment Plan
       ↓
现场执行
       ↓
Observed Event Timeline
```

ASC 分析属于后续处理：

```text
Raw ASC
   +
Observed Event Timeline
   ↓
Analysis Window Generator
   ↓
Signal Analysis
```

因此本轮：

## SHOULD

- 输出真实 Event 时间；
- 输出 Session；
- 输出照片时间；
- 输出备注；
- 保持稳定机器可读结构。

## SHOULD NOT

- 解析 ASC；
- 分析 CAN Signal；
- 自动判断车辆状态；
- 自动识别 Event；
- 自动切割 ASC；
- 生成诊断报告。

---

# 11. UI 原则

这是现场工具，不是桌面管理系统。

优先级：

```text
少点击
>
大按钮
>
一眼看懂
>
允许单手操作
>
信息完整
>
界面美观
```

Event 主界面应优先显示：

```text
当前 Event

计划时间
动作提示
当前计时

[完成 / 记录事件]

[拍照]

[备注]

[跳过]
```

不要把低频信息堆到主界面。

---

# 12. 数据可靠性

以下数据一旦记录，不应因为：

- App 切后台；
- 页面切换；
- 临时退出当前页面；

而丢失：

```text
Session
Event status
Observed Event Time
Photo
Photo Time
Notes
```

如果现有 App 已经有本地持久化机制，应复用。

不要为了本轮任务引入大型数据库或新的基础设施，除非现有实现确实无法满足最低可靠性要求。

---

# 13. 时间精度

Event 时间和照片时间至少应达到：

```text
毫秒级存储
```

UI 不一定必须显示全部毫秒。

内部数据不要只保存：

```text
HH:MM:SS
```

建议保存足够精度的时间信息，以便后续与 ASC 时间轴对齐。

如果 ASC 和 App 使用不同时间基准，应明确：

```text
absolute timestamp
relative session time
```

之间的关系。

不要在本轮擅自设计复杂时间同步协议。

---

# 14. 向后兼容

Codex 修改前必须先检查：

- 当前采集脚本格式；
- 当前 Event 数据结构；
- 当前 Session 机制；
- 当前语音播报实现；
- 当前照片机制；
- 当前导出格式；
- 当前持久化方式。

原则：

> 能扩展现有结构，就不要重写。

旧采集脚本如果可以合理兼容，应继续可用。

---

# 15. 明确禁止的范围扩张

本轮不要增加：

- CAN 数据采集功能；
- DBC 解析；
- Signal Viewer；
- 波形显示；
- 自动 CAN 分析；
- AI 分析；
- 自动 Evidence 判断；
- GPS 轨迹系统；
- 云同步；
- Notion 同步；
- Google Drive 同步；
- 完整实验管理平台；
- 用户账户系统；
- 新的大型数据库架构；
- 复杂照片管理系统；
- 自动报告生成。

这些即使未来可能有价值，也不是本轮问题。

---

# 16. Codex 执行方式

不要一次完成所有修改。

建议分阶段执行。

## Phase 1 — Audit

只检查现有工程。

输出：

```text
1. 当前 App 架构
2. 当前计时 / 播报机制
3. Event 数据模型
4. Session 数据模型
5. Photo 实现
6. Export 实现
7. Persistence 实现
8. 实现五项需求预计需要修改的文件
9. 是否存在平台限制
10. 建议的最小修改方案
```

### STOP

Phase 1 完成后停止。

**不要修改代码。**

等待人工审核。

---

## Phase 2 — Event Time Model

人工批准 Phase 1 后：

实现：

```text
Planned Time
+
Observed Event Time
+
Event Status
```

以及必要的数据持久化。

增加对应测试。

### STOP

完成后等待验证。

---

## Phase 3 — Background Timing

实现：

```text
后台计时
+
后台语音播报
```

重点验证：

```text
App 前台
App 后台
前后台切换
锁屏/系统限制（如适用）
```

如果操作系统存在不可绕过限制，必须明确说明，不允许用看似可用但实际不可靠的方式掩盖。

### STOP

等待验证。

---

## Phase 4 — Photo & Notes

实现：

```text
Event → Photos[]
Event Notes
Photo Notes
Photo captured_time
```

保持现场 UI 简洁。

### STOP

等待验证。

---

## Phase 5 — Timeline Export

完成结构化：

```text
Session
→
Event
→
Observed Time
→
Photos
→
Notes
```

导出。

确保后续 Python ASC 分析程序可以稳定读取。

### STOP

等待最终验收。

---

# 17. 测试要求

至少覆盖：

## Event

```text
Planned Time 正常读取
Observed Time 正确记录
Observed Time 未确认时保持 null
Skip 状态正确
```

## Session

```text
单 Session
多 Session
Session 间 Event 不串联
```

## Background

```text
前台播报
后台播报
前后台切换后计时连续
```

## Photo

```text
单 Event 0 张照片
单 Event 1 张照片
单 Event 多张照片
每张照片时间独立
```

## Notes

```text
无备注
Event 备注
Photo 备注
```

## Export

```text
Planned Time 保留
Observed Time 保留
Photo Time 保留
Session ID 保留
Event ID 保留
空字段语义稳定
```

---

# 18. 最终验收场景

使用一个模拟采集脚本：

```text
S01

E01 00:10 开门
E02 00:20 关闭车门
E03 00:30 锁车
```

实际执行：

```text
00:10 播报“开门”
00:12 用户完成 → 点击记录

00:20 播报“关闭车门”
00:23 用户完成 → 点击记录
      拍 Photo 01
      拍 Photo 02

00:30 播报“锁车”
用户跳过
```

最终数据必须能明确表达：

```text
E01
Planned  = 00:10
Observed = 00:12
Status   = completed

E02
Planned  = 00:20
Observed = 00:23
Status   = completed
Photos   = 2
每张 Photo 有独立 captured_time

E03
Planned  = 00:30
Observed = null
Status   = skipped
```

随后创建：

```text
S02
```

重复一轮操作。

最终导出必须能明确区分：

```text
S01
S02
```

---

# 19. 完成定义

只有以下条件全部满足，本轮 V2 优化才算完成：

- [ ] 后台计时/播报达到平台允许范围内的可靠状态；
- [ ] Planned Time 与 Observed Event Time 明确分离；
- [ ] Observed Time 由真实操作记录；
- [ ] 未确认 Event 不伪造 Observed Time；
- [ ] 一个 Event 支持多照片；
- [ ] 每张照片保存独立实际时间；
- [ ] Event Notes 可选；
- [ ] Photo Notes 可选；
- [ ] 支持多个 Session；
- [ ] Event Timeline 可结构化导出；
- [ ] 后续 Python 程序可以读取 Timeline；
- [ ] Raw ASC 不受 App 修改；
- [ ] 旧功能没有明显回归；
- [ ] 自动化测试通过；
- [ ] 没有引入本任务之外的大规模架构重构。

---

# 20. 本轮设计边界

本轮真正要建立的是这一条关系：

```text
Experiment Script
      │
      ├─ Planned Time
      │
      ↓
现场操作提示
      │
      ↓
真实动作发生
      │
      ├─ Observed Event Time
      ├─ Photos
      └─ Notes
      │
      ↓
Event Timeline
      │
      ├──────────────┐
      ↓              ↓
   人工复核       ASC Analysis
                     │
                     ↓
              Dynamic Window
                     │
                     ↓
              Signal Evidence
```

App 到：

```text
Event Timeline
```

为止。

后面的：

```text
ASC Analysis
→ Signal Evidence
→ Evidence Mapping
→ Assessment
→ Report
```

属于 TeslaCanPython 分析流水线。

**不要把这些职责重新塞回采集 App。**

---

# 21. 给 Codex 的首轮指令

请先执行 **Phase 1 — Audit**。

要求：

1. 阅读现有采集播报 App 工程；
2. 不修改任何代码；
3. 对照本任务书五项需求检查现有实现；
4. 尽量复用当前架构，不主动提出重写；
5. 给出最小修改方案；
6. 列出预计修改文件；
7. 指出 Android / iOS 或当前目标平台对于后台计时、语音、拍照等能力存在的系统限制；
8. 评估旧采集脚本兼容性；
9. 评估当前数据模型能否自然加入 `Observed Event Time` 和 `Photos[]`；
10. 给出 Phase 2 的建议实施边界。

完成后输出：

```text
AWAITING_APP_V2_AUDIT_REVIEW
```

然后停止。

**不要进入 Phase 2，不要修改代码。**
