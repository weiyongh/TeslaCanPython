# TM3-007 DBC关键Signal覆盖与可读性

## 核心Signal表

| 序号 | Signal | 控制含义 | Message | CAN ID | 单位 | 本次观测范围/状态 | 是否变化 | 解码/验证状态 | 本次用途/边界 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | GTW_BMP_AWAKE_PIN | 网关唤醒代理候选 | GTW_bmpDebug | 0x113 | boolean | 0 \| 1 | 是 | READABLE；INSUFFICIENT_EVIDENCE | 用于ER-01的网关唤醒代理候选证据；边界：NON_ONYX_DEFINITION+PROXY_OBSERVATION。 |
| 2 | DI_keepAliveRequest | 电驱保持唤醒候选 | DI_systemStatus | 0x118 | boolean | NO_REQUEST \| KEEP_ALIVE | 是 | READABLE；INSUFFICIENT_EVIDENCE | 用于ER-01+ER-09的电驱保持唤醒候选证据；边界：PROXY_OBSERVATION+SCOPE_UNCERTAIN。 |
| 3 | UI_lockRequest | 解/落锁请求候选 | UI_vehicleControl | 0x273 | enum | IDLE | 否/未形成变化证据 | READABLE；INSUFFICIENT_EVIDENCE | 用于ER-02的解/落锁请求候选证据；边界：NON_ONYX_DEFINITION+REQUEST_SOURCE_UNCERTAIN。 |
| 4 | HVP_hvilStatus | HVIL安全条件 | HVP_contactorState | 0x20A | enum | STATUS_OK \| UNKNOWN | 是 | READABLE；STRONGLY_SUPPORTED | 用于ER-05的HVIL安全条件证据；边界：DBC_VERSION_CONFLICT+DLC_CONFLICT。 |
| 5 | BMS_isolationResistance | 绝缘安全条件背景 | BMS_status | 0x212 | kOhm | 0 | 否/未形成变化证据 | READABLE；SEMANTIC_VALIDATION_FAILED | 用于ER-05的绝缘安全条件背景证据；边界：OEM_THRESHOLD_UNKNOWN+SNA_CHECK_REQUIRED。 |
| 6 | BMS_contactorState | BMS接触器总状态 | BMS_status | 0x212 | enum | CLOSED \| OPENING \| OPEN \| CLOSING | 是 | READABLE；STRONGLY_SUPPORTED | 用于ER-06+ER-09的BMS接触器总状态证据；边界：AGGREGATE_STATE。 |
| 7 | HVP_packContPositiveState | 正接触器/预充执行反馈候选 | HVP_contactorState | 0x20A | enum | ECONOMIZED \| OPENING \| OPEN \| PRECHARGE | 是 | READABLE；STRONGLY_SUPPORTED | 用于ER-06的正接触器/预充执行反馈候选证据；边界：DBC_VERSION_CONFLICT+DLC_CONFLICT。 |
| 8 | HVP_packContNegativeState | 负接触器执行反馈候选 | HVP_contactorState | 0x20A | enum | ECONOMIZED \| OPENING \| OPEN | 是 | READABLE；STRONGLY_SUPPORTED | 用于ER-06的负接触器执行反馈候选证据；边界：DBC_VERSION_CONFLICT+DLC_CONFLICT。 |
| 9 | BMS_packVoltage | Pack端高压反馈 | BMS_hvBusStatus | 0x132 | V | 353.35 \| 353.25 \| 353.37 \| 353.21 \| 353.31 \| 353.44 \| 353.45 \| 353.43 \| 353.24 \| 353.36 \| 353.4 \| 353.27 | 是 | READABLE；STRONGLY_SUPPORTED | 用于ER-06+ER-09的Pack端高压反馈证据；边界：PACK_SIDE_NOT_EXTERNAL_BUS。 |
| 10 | PCS_dcdcHvBusVolt | PCS所见高压母线反馈 | PCS_dcdcBusStatus | 0x2B4 | V | 187.646484 \| 178.271484 \| 197.021484 \| 422.021484 \| 37.646484 \| 581.396484 \| 206.396484 \| 347.021484 \| 47.021484 \| 18.896484 \| 0.146484 \| 590.771484 | 是 | READABLE；SEMANTIC_VALIDATION_FAILED | 用于ER-06+ER-08的PCS所见高压母线反馈证据；边界：PHYSICAL_CLOSURE_REQUIRED。 |
| 11 | BMS_hvState | BMS高压状态 | BMS_status | 0x212 | enum | DOWN | 否/未形成变化证据 | READABLE；SEMANTIC_VALIDATION_FAILED | 用于ER-05+ER-06+ER-09的BMS高压状态证据；边界：ENUM_SEQUENCE_REQUIRES_VALIDATION。 |
| 12 | PCS_dcdc12VSupportStatus | 12V支持状态 | PCS_dcdcStatus | 0x224 | enum | ACTIVE \| IDLE | 是 | READABLE；STRONGLY_SUPPORTED | 用于ER-08的12V支持状态证据；边界：ROLE_OVERLAP_UNCERTAIN。 |
| 13 | PCS_dcdcMainState | DCDC状态机/执行反馈 | PCS_dcdcStatus | 0x224 | enum | STANDBY | 否/未形成变化证据 | READABLE；SEMANTIC_VALIDATION_FAILED | 用于ER-08+ER-09的DCDC状态机/执行反馈证据；边界：ENUM_REQUIRES_PHYSICAL_FEEDBACK。 |
| 14 | PCS_dcdcLvBusVolt | 低压母线执行反馈 | PCS_dcdcBusStatus | 0x2B4 | V | 11.289062 \| 11.328125 \| 11.445312 \| 11.40625 \| 11.484375 \| 11.523438 \| 11.5625 \| 11.796875 \| 11.640625 \| 11.757812 \| 11.679688 \| 11.835938 | 是 | READABLE；STRONGLY_SUPPORTED | 用于ER-08+ER-09的低压母线执行反馈证据；边界：PCS_SIDE_NOT_EXTERNAL_METER。 |
| 15 | PCS_dcdcLvOutputCurrent | DCDC输出响应 | PCS_dcdcBusStatus | 0x2B4 | A | 26.9 \| 257.3 \| 334.1 \| 231.7 \| 359.7 \| 52.5 \| 282.9 \| 78.1 \| 385.3 \| 154.9 \| 206.1 \| 308.5 | 是 | READABLE；PARTIALLY_VALIDATED | 用于ER-08的DCDC输出响应证据；边界：DBC_VERSION_CONFLICT+SIGN_CONFLICT。 |
| 16 | UI_readyForDrive | 仪表/用户层可驱动反馈候选 | UI_status | 0x353 | boolean | 0 \| 1 | 是 | READABLE；STRONGLY_SUPPORTED | 用于ER-07的仪表/用户层可驱动反馈候选证据；边界：DBC_VERSION_CONFLICT+CONSUMER_SIGNAL。 |
| 17 | VCLEFT_frontLatchStatus | 驾驶门闩反馈 | VCLEFT_doorStatus | 0x102 | enum | CLOSED \| SNA \| OPENED | 是 | READABLE；STRONGLY_SUPPORTED | 用于ER-02+ER-03的驾驶门闩反馈证据；边界：DBC_VERSION_CONFLICT+EVENT_ANCHOR_MISSING。 |
| 18 | VCLEFT_frontOccupancyStatus | 驾驶员入座反馈 | VCLEFT_restraintStatus | 0x30A | enum | 无有效观测 | 未观察 | NO_FRAME；PARTIALLY_VALIDATED | 用于ER-03的驾驶员入座反馈证据；边界：DBC_APPLICABILITY_UNVERIFIED+EVENT_ANCHOR_MISSING。 |
| 19 | DI_brakePedalState | 制动条件输入 | DI_systemStatus | 0x118 | enum | INVALID | 否/未形成变化证据 | READABLE；SEMANTIC_VALIDATION_FAILED | 用于ER-04的制动条件输入证据；边界：EVENT_ANCHOR_MISSING。 |
| 20 | DI_gear | 挡位反馈/状态门 | DI_systemStatus | 0x118 | enum | SNA \| P \| D | 是 | READABLE；STRONGLY_SUPPORTED | 用于ER-07+ER-09的挡位反馈/状态门证据；边界：FEEDBACK_NOT_RAW_REQUEST。 |
| 21 | DI_systemState | 电驱状态/ENABLE候选 | DI_systemStatus | 0x118 | enum | UNAVAILABLE \| STANDBY \| ENABLE | 是 | READABLE；STRONGLY_SUPPORTED | 用于ER-07+ER-09的电驱状态/ENABLE候选证据；边界：NOT_WHOLE_VEHICLE_READY。 |

### 非DBC派生证据

| 序号 | 派生证据 | 派生含义 | 来源/统计对象 | 本次观测 | 验证状态 | 本次用途/边界 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 报文频率(派生) | 休眠/唤醒网络反馈 | 原始ASC统计 | 0..3086 frames/s | READABLE；PARTIALLY_VALIDATED | 用于ER-01的休眠/唤醒网络反馈证据；边界：DOMAIN_SLEEP_PROXY。 |
| 2 | 活跃CAN_ID数(派生) | 控制器分批唤醒代理 | 原始ASC统计 | 0..307 IDs/s | READABLE；PARTIALLY_VALIDATED | 用于ER-01的控制器分批唤醒代理证据；边界：DOMAIN_OBSERVATION_ONLY。 |

## DBC异常与可读性说明

- BMS_hvState全程DOWN、BMS_isolationResistance全程0 kOhm、PCS_dcdcMainState全程STANDBY：既有结论均为SEMANTIC_VALIDATION_FAILED，不解释为车辆故障。
- 0x20A三项保留多DBC/DLC冲突边界；实验级结果见时间线专项表和machine_evidence/signal_validation_assessment.csv。
- PCS_dcdcHvBusVolt定量语义验证失败；PCS_dcdcLvBusVolt为实验候选，PCS_dcdcLvOutputCurrent仅部分验证。
