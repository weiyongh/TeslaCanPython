# 特斯拉左前车窗实验 DBC 说明

对应文件：`dbc/特斯拉左前车窗_DBC_EXP.dbc`

该文件把现有 DBC 定义与多份实车 ASC 推导结果整理为一个局部实验 DBC，用于正常车辆与故障车辆的轨迹对比。它不是 Tesla 官方协议，不应用于报文发送或车辆控制。

## 数据来源

| 数据 | 用途 |
|---|---|
| `can_20260824175030.asc` | 驾驶门物理按钮手动/自动升降 |
| `can_20260824154441.asc` | App 四窗通风与关闭 |
| `can_20260823164405.asc` | 驾驶门开关负对照及无框车窗自动小降 |
| `tesla_model3_ONYX.dbc` | `0x3C2` 按钮输入的已知定义 |

## 证据等级

| 标记 | 含义 |
|---|---|
| DBC-defined | 来自已有 DBC，并得到实车动作验证 |
| EXP-C+ | 多种控制入口和负对照支持，正式语义仍未知 |
| EXP-C | 多次实车相关性成立，具体字段仍需验证 |

## 控制链临时模型

```text
0x3C2  物理按钮输入
  ↓
0x545  车窗运动过程反馈候选
  ↓
0x2C2  主动开关窗执行/到位状态候选

0x1FA  App通风或多窗汇总状态候选
```

## 0x3C2 / 962 / VCLEFT_switchStatus_EXP

证据性质：DBC-defined，并由物理按钮采集验证。

| Signal | 位置 | 含义 |
|---|---:|---|
| `VCLEFT_switchStatusIndex` | bit 0–1 | 多路复用索引 |
| `VCLEFT_btnWindowSwPackUpLF` | bit 32 | 左前窗手动上升输入 |
| `VCLEFT_btnWindowSwPackAutoUpLF` | bit 33 | 左前窗自动上升档输入 |
| `VCLEFT_btnWindowSwPackDownLF` | bit 34 | 左前窗手动下降输入 |
| `VCLEFT_btnWindowSwPackAutoDownLF` | bit 35 | 左前窗自动下降档输入 |

这些按钮 Signal 仅在 multiplexer 等于 0 时有效。实车数据确认了手动下降、手动上升和自动上升；自动下降的独立证据尚不完整。

## 0x545 / 1349 / EXP_windowMotionFeedback

证据等级：EXP-C。

临时 Message 含义：车窗运动过程反馈候选。

主要证据：

- 物理按钮升降时活动显著增加；
- App 通风/关闭四个运动窗口全部响应；
- 开门时无框玻璃自动下降一小段，Byte 1 bit 1在两次开门后分别活动约0.33秒和0.23秒；
- Byte 1 bit 1在开门之外的背景翻转为0，表现出明显的下降方向专属性；
- Byte 6和Byte 7持续滚动，可能混有计数器或校验和，不能作为绝对位置解释。

临时字段：

| Signal | 位置 | 暂定含义 | 语义置信度 |
|---|---:|---|---:|
| `EXP_windowDownMotionActivityCandidate` | B1.b1 | 下降运动活动候选 | 约70% |
| `EXP_windowMotionActivityCandidate2` | B1.b2 | 次级运动活动候选 | 约50% |
| `EXP_windowMotionData_B2` | Byte 2 | 原始运动相关数据 | 未定 |
| `EXP_windowRollingData_B6` | Byte 6 | 滚动/复合数据 | 未定 |
| `EXP_windowChecksumOrMotionData_B7` | Byte 7 | 校验或复合运动数据 | 未定 |

Message 与车窗运动直接相关的工程置信度约92%；“车窗运动过程反馈”名称的置信度约80%。

## 0x2C2 / 706 / EXP_windowExecutionStatus

证据等级：EXP-C+。

临时 Message 含义：主动开关窗执行/到位状态候选。

重点分析 `B0=0x20、B1=0x40` 的 Payload 家族。App 数据形成重复指纹：

```text
关闭：20 40 C0 4B 01 00 80 CB
通风：20 40 00 59 01 00 xx D9
```

两次通风和两次关闭方向可逆。物理自动上升与 App 关闭均出现：

```text
BB 4B → C0 4B
```

变化时延与玻璃行程相符：短距离通风约0.4–0.8秒，自动全降约3秒，自动全升约5.9秒。

开关门负对照中，同一 Payload 家族在四个动作窗口始终保持：

```text
20 40 80 20 01 00 00 FE
```

此前筛出的 B1.b2、B2.b2、B2.b4均为0次翻转，因此没有把单纯车门开关或车辆唤醒误判为主动开关窗到位轨迹。

临时字段：

| Signal | 位置 | 暂定含义 |
|---|---:|---|
| `EXP_messageFamily_B0_B1` | Byte 0–1 | Payload家族原始值；`20 40`按小端为`0x4020` |
| `EXP_windowStateOrPosition_B2` | Byte 2 | 执行、到位或位置状态组合 |
| `EXP_windowPositionOrTarget_B3` | Byte 3 | 端点/目标编码候选；尚非线性位置 |
| `EXP_windowSelectionOrFlags_B6` | Byte 6 | 选择位、状态位或滚动字段 |
| `EXP_windowStateOrChecksum_B7` | Byte 7 | 状态或校验候选 |

Message 与主动开关窗执行相关的工程置信度约95%；“执行/到位状态”名称的置信度约85%；具体字段解释约45%–55%。

## 0x1FA / 506 / EXP_multiWindowVentSummaryStatus

证据等级：EXP-C。

该 Message 长度为3字节，当前只确认 Byte 0 bit 5：

```text
App全关：02 C0 01，bit 5 = 0
App通风：22 C0 01，bit 5 = 1
```

它完整跟随App的两次通风和两次关闭，但在物理单窗采集中只变化两次，在开关门和无框玻璃自动小降采集中保持不变。因此更像App通风、多窗汇总或特定位置阈值状态，而不是单窗位置。

Message 与App通风/多窗状态相关的置信度较高，但正式范围尚未确认。不得将枚举文字理解为厂家定义。

## 使用限制

1. 所有 `EXP_` 名称都是实验临时名称。
2. DBC 只适合解码和正常/故障轨迹比较，不适合构造控制报文。
3. `0x2C2` 同一 ID 中存在多个 Payload 家族，分析时必须先检查 `EXP_messageFamily_B0_B1`。
4. 原始 Byte 定义用于保留数据，不能单独当作正式 Signal。
5. 后续完成右前、右后、左后车窗独立采集后，应更新字段、置信度和证据等级。

## 面向故障诊断的用法

正常基线可按以下顺序观察：

```text
按钮输入是否出现（0x3C2）
→ 运动活动是否出现（0x545）
→ 执行/到位指纹是否收敛（0x2C2）
→ 多窗或App汇总状态是否正确（0x1FA）
```

故障车辆与正常基线最早出现分歧的位置，可用于区分输入开关、控制逻辑、电机/线束、机械卡滞、编码器/位置反馈和到位状态异常。
