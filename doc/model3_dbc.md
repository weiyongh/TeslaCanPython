# Tesla Model 3 DBC 实车 Signal 笔记

本文档记录已经在实车 ASC 采集数据中遇到并通过 DBC 解码的 Message 和 Signal。内容会随着新的采集实验持续补充。

> 说明：表格中的“DBC 定义”来自 `input/tesla_model3_ONYX.dbc`；“实车解释”来自 Signal 名称、DBC 枚举和本项目采集结果。DBC 没有给出枚举的 `0/1` Signal，会明确标注为实车观察或合理推断，不将其当作官方协议定义。

## 0x102：VCLEFT_doorStatus

### Message 基本信息

| 项目 | 内容 | 说明 |
|---|---|---|
| 十进制 CAN ID | `258` | DBC 的 `BO_ 258` |
| 十六进制 CAN ID | `0x102` | ASC 中显示为 `102` |
| Message 名称 | `VCLEFT_doorStatus` | 左侧车身控制器的车门/后视镜状态 |
| 载荷长度 | 8 字节 | 共 64 bit |
| 发送节点 | `VEH` | DBC 定义 |
| 发送类型 | `0` | `GenMsgSendType`，DBC 未附带文字枚举 |
| 发送周期 | `100 ms` | `GenMsgCycleTime = 100`，约 10 Hz |
| 字节序 | Intel，小端 | 本 Message 的 Signal 均为 `@1` |

### 本次遇到的状态

以下是本次 ASC 中观察窗口开始时解码出的状态：

```text
VCLEFT_frontLatchStatus           = CLOSED
VCLEFT_rearLatchStatus            = CLOSED
VCLEFT_frontLatchSwitch           = 1
VCLEFT_rearLatchSwitch            = 1
VCLEFT_frontHandlePulled          = 0
VCLEFT_rearHandlePulled           = 0
VCLEFT_frontRelActuatorSwitch     = 1
VCLEFT_rearRelActuatorSwitch      = 1
VCLEFT_frontHandlePWM             = 8
VCLEFT_rearHandlePWM              = 4
VCLEFT_frontIntSwitchPressed      = 0
VCLEFT_rearIntSwitchPressed       = 0
VCLEFT_mirrorState                = IDLE
VCLEFT_mirrorFoldState            = UNFOLDED
VCLEFT_mirrorRecallState          = INIT
VCLEFT_mirrorHeatState            = OFF
VCLEFT_mirrorDipped               = 0
VCLEFT_frontHandlePulledPersist   = 0
```

### Signal 定义总表

所有 Signal 都是无符号数（DBC 中的 `+`），比例因子为 `1`、偏移量为 `0`。因此除枚举名称外，物理数值等于从载荷中提取的原始整数。

| Signal | 中文解释 | 起始位 | 位宽 | 载荷位置 | 编码可表示范围 | DBC 单位 | 本次值 | 本次值的含义 |
|---|---|---:|---:|---|---:|---|---:|---|
| `VCLEFT_frontLatchStatus` | 左前门锁扣状态 | 0 | 4 | Byte 0 bit 0–3 | 0–15；枚举定义 0–8 | 无 | `CLOSED`（2） | 左前门锁扣关闭 |
| `VCLEFT_rearLatchStatus` | 左后门锁扣状态 | 4 | 4 | Byte 0 bit 4–7 | 0–15；枚举定义 0–8 | 无 | `CLOSED`（2） | 左后门锁扣关闭 |
| `VCLEFT_frontLatchSwitch` | 左前门锁扣位置开关 | 8 | 1 | Byte 1 bit 0 | 0–1 | 无 | `1` | 实车观察：1 为闭合位置；开门后变为 0 |
| `VCLEFT_rearLatchSwitch` | 左后门锁扣位置开关 | 9 | 1 | Byte 1 bit 1 | 0–1 | 无 | `1` | 推断：左后门锁扣位于闭合位置 |
| `VCLEFT_frontHandlePulled` | 左前门把手拉动状态 | 10 | 1 | Byte 1 bit 2 | 0–1 | 无 | `0` | 推断：把手未被拉动 |
| `VCLEFT_rearHandlePulled` | 左后门把手拉动状态 | 11 | 1 | Byte 1 bit 3 | 0–1 | 无 | `0` | 推断：把手未被拉动 |
| `VCLEFT_frontRelActuatorSwitch` | 左前门释放执行器开关反馈 | 12 | 1 | Byte 1 bit 4 | 0–1 | 无 | `1` | 静止值为 1；开门过程中短暂变为 0 后恢复 |
| `VCLEFT_rearRelActuatorSwitch` | 左后门释放执行器开关反馈 | 13 | 1 | Byte 1 bit 5 | 0–1 | 无 | `1` | 本次未操作左后门，保持为 1 |
| `VCLEFT_frontHandlePWM` | 左前门把手 PWM 数值 | 16 | 7 | Byte 2 bit 0–6 | 编码 0–127 | `%` | `8` | 静止基准值；开门时观察到 72–73 |
| `VCLEFT_rearHandlePWM` | 左后门把手 PWM 数值 | 24 | 7 | Byte 3 bit 0–6 | 编码 0–127 | `%` | `4` | 本次左后门未操作，保持基准值 4 |
| `VCLEFT_frontIntSwitchPressed` | 左前门内部开门开关 | 31 | 1 | Byte 3 bit 7 | 0–1 | 无 | `0` | 未按下；开门起始阶段变为 1 |
| `VCLEFT_rearIntSwitchPressed` | 左后门内部开门开关 | 32 | 1 | Byte 4 bit 0 | 0–1 | 无 | `0` | 推断：未按下 |
| `VCLEFT_mirrorState` | 左后视镜当前动作状态 | 49 | 3 | Byte 6 bit 1–3 | 0–7；枚举定义 0–4 | 无 | `IDLE`（0） | 后视镜没有执行动作 |
| `VCLEFT_mirrorFoldState` | 左后视镜折叠状态 | 52 | 3 | Byte 6 bit 4–6 | 0–7；枚举定义 0–4 | 无 | `UNFOLDED`（2） | 后视镜已展开 |
| `VCLEFT_mirrorRecallState` | 左后视镜位置恢复状态 | 55 | 3 | Byte 6 bit 7 + Byte 7 bit 0–1 | 0–7；枚举定义 0–5 | 无 | `INIT`（0） | 位置恢复状态机处于初始状态 |
| `VCLEFT_mirrorHeatState` | 左后视镜加热状态 | 58 | 3 | Byte 7 bit 2–4 | 0–7；枚举定义 0–4 | 无 | `OFF`（2） | 后视镜加热关闭 |
| `VCLEFT_mirrorDipped` | 左后视镜是否下倾 | 61 | 1 | Byte 7 bit 5 | 0–1 | 无 | `0` | 推断：未下倾 |
| `VCLEFT_frontHandlePulledPersist` | 左前门把手拉动保持标志 | 62 | 1 | Byte 7 bit 6 | 0–1 | 无 | `0` | 推断：没有保持的把手拉动状态 |

### 关于范围 `[0|0]` 的注意事项

这份 DBC 为上述 Signal 写出的物理范围都是 `[0|0]`，但这与实际位宽和枚举明显矛盾，例如：

```dbc
SG_ VCLEFT_frontLatchStatus : 0|4@1+ (1,0) [0|0] "" X
```

锁扣状态实际已经定义了 `0–8` 的枚举，因此不能把 `[0|0]` 理解为“只能取 0”。本文档的范围采用以下原则：

1. “编码可表示范围”由无符号位宽计算，例如 4 bit 为 `0–15`、7 bit 为 `0–127`。
2. 有 `VAL_` 时，另行注明 DBC 实际定义了哪些枚举值。
3. PWM 虽然 7 bit 可编码 `0–127`，单位为 `%`，但合理物理范围通常应为 `0–100%`；当前 DBC 没有可靠声明，`101–127` 是否有效需要实车验证。

### 锁扣状态枚举

`VCLEFT_frontLatchStatus` 和 `VCLEFT_rearLatchStatus` 使用相同枚举：

| 原始值 | DBC 名称 | 中文解释 |
|---:|---|---|
| 0 | `SNA` | 状态不可用或未提供 |
| 1 | `OPENED` | 已打开 |
| 2 | `CLOSED` | 已关闭 |
| 3 | `CLOSING` | 正在关闭 |
| 4 | `OPENING` | 正在打开 |
| 5 | `AJAR` | 未完全关闭、半开 |
| 6 | `TIMEOUT` | 动作或状态确认超时 |
| 7 | `DEFAULT` | 默认状态 |
| 8 | `FAULT` | 故障状态 |
| 9–15 | 未定义 | 位宽能够表示，但 DBC 没有赋予含义 |

### 后视镜动作状态枚举

`VCLEFT_mirrorState`：

| 原始值 | DBC 名称 | 中文解释 |
|---:|---|---|
| 0 | `IDLE` | 空闲，没有进行动作 |
| 1 | `TILT_X` | 正在调节 X 轴位置 |
| 2 | `TILT_Y` | 正在调节 Y 轴位置 |
| 3 | `FOLD_UNFOLD` | 正在折叠或展开 |
| 4 | `RECALL` | 正在恢复已保存的位置 |
| 5–7 | 未定义 | DBC 没有赋予含义 |

### 后视镜折叠状态枚举

`VCLEFT_mirrorFoldState`：

| 原始值 | DBC 名称 | 中文解释 |
|---:|---|---|
| 0 | `UNKNOWN` | 状态未知 |
| 1 | `FOLDED` | 已折叠 |
| 2 | `UNFOLDED` | 已展开 |
| 3 | `FOLDING` | 正在折叠 |
| 4 | `UNFOLDING` | 正在展开 |
| 5–7 | 未定义 | DBC 没有赋予含义 |

### 后视镜位置恢复状态枚举

`VCLEFT_mirrorRecallState`：

| 原始值 | DBC 名称 | 中文解释 |
|---:|---|---|
| 0 | `INIT` | 初始状态 |
| 1 | `RECALLING_AXIS_1` | 正在恢复第一个轴的位置 |
| 2 | `RECALLING_AXIS_2` | 正在恢复第二个轴的位置 |
| 3 | `RECALLING_COMPLETE` | 位置恢复完成 |
| 4 | `RECALLING_FAILED` | 位置恢复失败 |
| 5 | `RECALLING_STOPPED` | 位置恢复被停止 |
| 6–7 | 未定义 | DBC 没有赋予含义 |

### 后视镜加热状态枚举

`VCLEFT_mirrorHeatState`：

| 原始值 | DBC 名称 | 中文解释 |
|---:|---|---|
| 0 | `SNA` | 状态不可用或未提供 |
| 1 | `ON` | 加热开启 |
| 2 | `OFF` | 加热关闭 |
| 3 | `OFF_UNAVAILABLE` | 加热关闭且当前不可用 |
| 4 | `FAULT` | 加热系统故障 |
| 5–7 | 未定义 | DBC 没有赋予含义 |

### 8 字节位布局

```text
Byte 0  [rearLatchStatus:4] [frontLatchStatus:4]
Byte 1  [未使用:2] [rearRelActuator:1] [frontRelActuator:1]
        [rearHandlePulled:1] [frontHandlePulled:1]
        [rearLatchSwitch:1] [frontLatchSwitch:1]
Byte 2  [未使用:1] [frontHandlePWM:7]
Byte 3  [frontIntSwitch:1] [rearHandlePWM:7]
Byte 4  [mirrorTiltX 的低7位] [rearIntSwitch:1]
Byte 5  [mirrorTiltY 的低7位] [mirrorTiltX 的最高位]
Byte 6  [mirrorRecall 的最低位] [mirrorFoldState:3]
        [mirrorState:3] [mirrorTiltY 的最高位]
Byte 7  [未使用:1] [frontHandlePulledPersist:1] [mirrorDipped:1]
        [mirrorHeatState:3] [mirrorRecall 的高2位]
```

表中每个字节左侧是高位 bit 7，右侧是低位 bit 0。后视镜位置 Signal 虽未列入本次状态清单，但它们占据的位仍需保留，否则无法正确理解 Byte 4–6 的布局。

### 实车开门变化规律

第一次打开驾驶门时观察到：

| 相对时间 | Signal 变化 | 中文解释 |
|---:|---|---|
| 25.138300s | `frontHandlePWM 8 → 72` | 前门把手相关 PWM 明显升高 |
| 25.138300s | `frontIntSwitchPressed 0 → 1` | 内部开门开关被触发 |
| 25.148400s | `frontLatchStatus CLOSED → OPENED` | 控制器报告锁扣已经打开 |
| 25.184300s | `frontRelActuatorSwitch 1 → 0` | 释放执行器反馈发生变化 |
| 25.328300s | `frontLatchSwitch 1 → 0` | 锁扣位置开关确认脱离闭合位置 |
| 25.328300s | `frontIntSwitchPressed 1 → 0` | 内部开门开关恢复 |
| 25.758300s | `frontRelActuatorSwitch 0 → 1` | 释放执行器反馈恢复 |
| 25.788400s | `frontHandlePWM 73 → 72` | PWM 小幅回落 |

第一次关闭驾驶门时，两个最关键的状态在同一帧变化：

```text
VCLEFT_frontLatchStatus：OPENED → CLOSED
VCLEFT_frontLatchSwitch：0 → 1
```

目前实车数据支持以下判断：

- `frontLatchStatus` 是控制器解释后的多状态锁扣状态。
- `frontLatchSwitch` 是更接近物理位置开关的二值反馈。
- 两者结合可以更可靠地判断左前门是否真正关闭。

## 后续记录格式

每次在新采集中确认一个 Message/Signal，建议补充：

1. Message 的十进制和十六进制 ID、名称、长度和周期。
2. Signal 的起始位、位宽、字节序、符号、比例、偏移和单位。
3. 位宽编码范围以及 DBC 枚举范围，两者不要混为一谈。
4. 已观察到的原始值、枚举名称和中文解释。
5. 触发该变化的实车操作、时间点和重复验证次数。
6. 明确区分“DBC 已定义”“实车已验证”和“尚待验证的推断”。
