# TM3-007 DBC关键Signal覆盖与可读性

## 核心Signal表

| 控制树角色 | Signal | Message | CAN ID | 单位 | 本次观测范围/状态 | 是否变化 | 解码状态 | 本次用途 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 驾驶门闩反馈 | VCLEFT_frontLatchStatus | VCLEFT_doorStatus | 0x102 | enum | CLOSED \| SNA \| OPENED | 是 | READABLE；STRONGLY_SUPPORTED | 记录门闩CLOSED→OPENED→CLOSED反馈；不作为人工动作时刻。 |
| 驾驶员入座反馈 | VCLEFT_frontOccupancyStatus | VCLEFT_restraintStatus | 0x30A | enum | 无有效观测 | 未观察 | NO_FRAME；PARTIALLY_VALIDATED | 检查入座条件节点覆盖；本次无帧，仅保留证据缺口。 |
| 制动条件输入 | DI_brakePedalState | DI_systemStatus | 0x118 | enum | INVALID | 否（全程INVALID） | READABLE；SEMANTIC_VALIDATION_FAILED | 检查制动条件输入；全程INVALID，不用于证明制动动作。 |
| 挡位反馈/状态门 | DI_gear | DI_systemStatus | 0x118 | enum | SNA \| P \| D | 是 | READABLE；STRONGLY_SUPPORTED | 记录P→D→P挡位反馈，并与电驱状态链交叉验证。 |

## DBC异常与可读性说明

- BMS_hvState全程DOWN、BMS_isolationResistance全程0 kOhm、PCS_dcdcMainState全程STANDBY：既有结论均为SEMANTIC_VALIDATION_FAILED，不解释为车辆故障。
- 0x20A三项保留多DBC/DLC冲突边界；实验级结果见时间线专项表和machine_evidence/signal_validation_assessment.csv。
- PCS_dcdcHvBusVolt定量语义验证失败；PCS_dcdcLvBusVolt为实验候选，PCS_dcdcLvOutputCurrent仅部分验证。
