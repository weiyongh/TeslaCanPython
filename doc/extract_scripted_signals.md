# extract_scripted_signals.py 使用与原理说明

## 程序用途

[`extract_scripted_signals.py`](../src/extract_scripted_signals.py) 使用以下三个输入文件分析车辆操作与 CAN Signal 的对应关系：

1. 标准采集脚本：记录操作步骤及相对于采集起点的时间。
2. ASC 文件：保存实际采集的原始 CAN 报文。
3. DBC 文件：定义 CAN Message 中各 Signal 的位位置、长度、换算方式和枚举含义。

程序自动识别采集脚本中的关键动作时间点，在 ASC 数据中寻找动作附近发生变化、并在重复动作中表现一致的 Signal。

## 运行方式

在项目根目录执行：

```powershell
python src\extract_scripted_signals.py `
    input\can_开门关门采集脚本.txt `
    input\can_20260823164405.asc `
    input\tesla_model3_ONYX.dbc `
    --exclude-regex "mirrorTilt"
```

常用参数：

| 参数 | 含义 | 默认值 |
|---|---|---:|
| `--tolerance` | 关键动作前后的匹配时间范围，单位为秒 | `2` |
| `--top` | 输出排名靠前的候选 Signal 数量 | `10` |
| `--output-dir` | 结果目录 | `output` |
| `--exclude-regex` | 排除 Message/Signal 名称的正则表达式 | 不排除 |

排除多个类别时可以使用：

```powershell
--exclude-regex "mirrorTilt|temperature|counter$"
```

匹配不区分大小写，同时检查 Message 名、Signal 名以及 `Message.Signal` 完整名称。

## 输出文件

程序在 `output` 目录生成：

- `*_关键步骤信号报告.md`：采集步骤、候选 Signal 排名和动作点变化详情。
- `*_关键步骤信号明细.csv`：便于使用 Excel 查看和进一步统计的明细。
- `asc_dbc_message_trace_<ASC名称>_<CAN ID>_<时间戳>.txt`：排名第一的候选 Signal 所属 Message 的完整状态变化时间线。

Message 追踪文件带运行时间戳，因此不会覆盖以前的结果。`--exclude-regex` 同样作用于该文件，不需要的 Signal 不会出现在初始状态和变化事件中。

## ASC、Message 和 Signal 的关系

本次数据中重要的 Message 是：

```text
十进制 ID：258
十六进制 ID：0x102
Message：VCLEFT_doorStatus
载荷长度：8 字节（64 bit）
```

一条 Message 使用 8 字节承载多个 Signal。每个 Signal 只占其中一个或多个 bit；多个 Signal 可以共用一个字节，Signal 也可以跨字节。

DBC 相当于载荷的结构说明书，ASC 则保存实际采集到的时间戳、CAN ID 和载荷字节。

## DBC Signal 定义

驾驶门锁扣状态的定义为：

```dbc
SG_ VCLEFT_frontLatchStatus : 0|4@1+ (1,0) [0|0] "" X
```

字段解释：

| 内容 | 含义 |
|---|---|
| `0` | 起始位是 bit 0 |
| `4` | Signal 长度为 4 bit |
| `@1` | Intel/Little Endian 位序 |
| `+` | 无符号整数 |
| `(1,0)` | 比例因子为 1，偏移量为 0 |
| `[0\|0]` | DBC 声明的范围；本 DBC 的部分范围信息并不完整 |
| `""` | 没有物理单位 |
| `X` | DBC 中的接收节点 |

一般换算公式：

```text
物理值 = 原始整数 × 比例因子 + 偏移量
```

## DBC 枚举定义

Message ID 258 的驾驶门锁扣枚举定义为：

```dbc
VAL_ 258 VCLEFT_frontLatchStatus
    0 "SNA"
    1 "OPENED"
    2 "CLOSED"
    3 "CLOSING"
    4 "OPENING"
    5 "AJAR"
    6 "TIMEOUT"
    7 "DEFAULT"
    8 "FAULT";
```

Signal 位定义和枚举定义通过 `Message ID + Signal 名称` 关联：

```text
258 + VCLEFT_frontLatchStatus
```

因此，从载荷中提取到原始值 `1` 后显示为 `OPENED`，原始值 `2` 显示为 `CLOSED`。

## 0x102 的主要字节布局

| 字节 | bit | Signal | 含义 |
|---|---|---|---|
| Byte 0 | 0–3 | `VCLEFT_frontLatchStatus` | 左前门锁扣状态 |
| Byte 0 | 4–7 | `VCLEFT_rearLatchStatus` | 左后门锁扣状态 |
| Byte 1 | 0 | `VCLEFT_frontLatchSwitch` | 左前门锁扣开关 |
| Byte 1 | 1 | `VCLEFT_rearLatchSwitch` | 左后门锁扣开关 |
| Byte 1 | 2 | `VCLEFT_frontHandlePulled` | 左前门把手拉动状态 |
| Byte 1 | 3 | `VCLEFT_rearHandlePulled` | 左后门把手拉动状态 |
| Byte 1 | 4 | `VCLEFT_frontRelActuatorSwitch` | 左前门释放执行器开关 |
| Byte 1 | 5 | `VCLEFT_rearRelActuatorSwitch` | 左后门释放执行器开关 |
| Byte 2 | 0–6 | `VCLEFT_frontHandlePWM` | 左前门把手 PWM |
| Byte 3 | 0–6 | `VCLEFT_rearHandlePWM` | 左后门把手 PWM |
| Byte 3 | 7 | `VCLEFT_frontIntSwitchPressed` | 左前门内部开关 |
| Byte 4 | 0 | `VCLEFT_rearIntSwitchPressed` | 左后门内部开关 |
| Byte 4–7 | 多个字段 | 后视镜相关 Signal | 位置、折叠、恢复和加热状态等 |

## 手工解码开门状态

第一次开门附近的两帧为：

```text
变化前：22 B3 48 84 8C 0C 21 08
变化后：21 33 49 84 8C 0C 21 08
```

驾驶门锁扣状态位于 Byte 0 的低 4 bit：

```text
0x22 & 0x0F = 2 = CLOSED
0x21 & 0x0F = 1 = OPENED
```

所以解码结果是：

```text
VCLEFT_frontLatchStatus：CLOSED -> OPENED
```

Byte 0 的高 4 bit 在两帧中都是 `2`，说明同一 Message 中的左后门锁扣状态一直是 `CLOSED`。

## 手工解码单 bit 开关

`VCLEFT_frontLatchSwitch` 的定义是 `8|1@1+`，也就是 Byte 1 的 bit 0：

```python
front_latch_switch = byte1 & 0x01
```

例如：

```text
0xB3 & 0x01 = 1
0x22 & 0x01 = 0
```

本次实车数据表现为：

- `1`：锁扣处于闭合位置。
- `0`：锁扣已经释放。

该 Signal 没有 `VAL_` 枚举，所以程序显示数字 `0/1`。

## 手工解码共享字节

`VCLEFT_frontIntSwitchPressed` 起始位是 31，位于 Byte 3 的 bit 7：

```python
front_int_switch_pressed = (byte3 >> 7) & 0x01
```

```text
Byte 3 = 0x04 = 0000 0100，开关值为 0
Byte 3 = 0x84 = 1000 0100，开关值为 1
```

Byte 3 的低 7 bit 同时属于 `VCLEFT_rearHandlePWM`：

```python
rear_handle_pwm = byte3 & 0x7F
```

所以 `0x04 -> 0x84` 只是最高位变化，低 7 bit 都是 `4`。同一个字节可以同时承载两个不同 Signal。

## 第一次开门的事件顺序

追踪结果显示，一次物理开门并不是单个 bit 的一次变化，而是一组有先后顺序的事件：

| 时间 | Signal 变化 | 含义 |
|---:|---|---|
| 25.138300s | `frontHandlePWM 8 -> 72`；`frontIntSwitchPressed 0 -> 1` | 检测到内部开关动作 |
| 25.148400s | `frontLatchStatus CLOSED -> OPENED` | 控制器认为锁扣已经打开 |
| 25.184300s | `frontRelActuatorSwitch 1 -> 0` | 释放执行器开关变化 |
| 25.328300s | `frontLatchSwitch 1 -> 0`；内部开关恢复 | 锁扣物理反馈确认释放 |
| 25.758300s | `frontRelActuatorSwitch 0 -> 1` | 释放执行器恢复 |
| 25.788400s | `frontHandlePWM 73 -> 72` | 把手 PWM 回落 |

第一次关门时：

```text
VCLEFT_frontLatchStatus：OPENED -> CLOSED
VCLEFT_frontLatchSwitch：0 -> 1
```

这说明控制器状态和锁扣开关都确认车门重新关闭。

## 程序解码流程

```text
读取 ASC 中的 CAN 帧
    → 根据 CAN ID 找到 DBC Message
    → 根据 start bit 和 length 提取 Signal 原始整数
    → 按字节序和有无符号解释原始整数
    → 使用 raw × scale + offset 得到物理值
    → 使用 VAL_ 将数字映射为枚举名称
    → 与上一帧解码结果比较
    → 输出发生变化的 Signal
```

## VS Code 跳转到 DBC 指定行

打开 DBC 后按 `Ctrl + G`，输入行号，例如：

```text
11268
```

也可以按 `Ctrl + P`，输入：

```text
input/tesla_model3_ONYX.dbc:11268
```

即可打开文件并跳转到枚举定义位置。
