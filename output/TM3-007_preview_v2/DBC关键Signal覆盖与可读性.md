# TM3-007 DBC关键Signal覆盖与可读性

## 核心Signal表

| 控制树角色 | Signal | Message | CAN ID | 单位 | 本次观测范围/状态 | 是否变化 | 解码状态 | 本次用途 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 驾驶门闩反馈 | VCLEFT_frontLatchStatus | VCLEFT_doorStatus | 0x102 | enum | CLOSED \| SNA \| OPENED | 是 | 来源：ONYX主候选；冲突项见定义对照；READABLE；STRONGLY_SUPPORTED | 驾驶门闩反馈；对应ER-02+ER-03；报告位置保持CORE_TIMELINE+CORE_SIGNAL_TABLE。 |
| 驾驶员入座反馈 | VCLEFT_frontOccupancyStatus | VCLEFT_restraintStatus | 0x30A | enum | 无有效观测 | 未观察 | 来源：ONYX主候选；冲突项见定义对照；NO_FRAME；PARTIALLY_VALIDATED | 驾驶员入座反馈；对应ER-03；报告位置保持CORE_TIMELINE+CORE_SIGNAL_TABLE。 |
| 制动条件输入 | DI_brakePedalState | DI_systemStatus | 0x118 | enum | INVALID | 否/未形成变化证据 | 来源：ONYX主候选；冲突项见定义对照；READABLE；SEMANTIC_VALIDATION_FAILED | 制动条件输入；对应ER-04；报告位置保持CORE_TIMELINE+CORE_SIGNAL_TABLE。 |
| 挡位反馈/状态门 | DI_gear | DI_systemStatus | 0x118 | enum | SNA \| P \| D | 是 | 来源：ONYX主候选；冲突项见定义对照；READABLE；STRONGLY_SUPPORTED | 挡位反馈/状态门；对应ER-07+ER-09；报告位置保持CORE_TIMELINE+CORE_SIGNAL_TABLE。 |
| 电驱状态/ENABLE候选 | DI_systemState | DI_systemStatus | 0x118 | enum | UNAVAILABLE \| STANDBY \| ENABLE | 是 | 来源：ONYX主候选；冲突项见定义对照；READABLE；STRONGLY_SUPPORTED | 电驱状态/ENABLE候选；对应ER-07+ER-09；报告位置保持CORE_TIMELINE+CONTROL_RELATIONSHIP。 |
| 仪表/用户层可驱动反馈候选 | UI_readyForDrive | UI_status | 0x353 | boolean | 0 \| 1 | 是 | 来源：ONYX主候选；冲突项见定义对照；READABLE；STRONGLY_SUPPORTED | 仪表/用户层可驱动反馈候选；对应ER-07；报告位置保持READY_CROSSCHECK_TABLE。 |
| BMS高压状态 | BMS_hvState | BMS_status | 0x212 | enum | DOWN | 否/未形成变化证据 | 来源：ONYX主候选；冲突项见定义对照；READABLE；SEMANTIC_VALIDATION_FAILED | BMS高压状态；对应ER-05+ER-06+ER-09；报告位置保持CORE_TIMELINE+HV_CHAIN_TABLE。 |
| BMS接触器总状态 | BMS_contactorState | BMS_status | 0x212 | enum | CLOSED \| OPENING \| OPEN \| CLOSING | 是 | 来源：ONYX主候选；冲突项见定义对照；READABLE；STRONGLY_SUPPORTED | BMS接触器总状态；对应ER-06+ER-09；报告位置保持CORE_TIMELINE+HV_CHAIN_TABLE。 |
| Pack端高压反馈 | BMS_packVoltage | BMS_hvBusStatus | 0x132 | V | 353.35 \| 353.25 \| 353.37 \| 353.21 \| 353.31 \| 353.44 \| 353.45 \| 353.43 \| 353.24 \| 353.36 \| 353.4 \| 353.27 | 是 | 来源：ONYX主候选；冲突项见定义对照；READABLE；STRONGLY_SUPPORTED | Pack端高压反馈；对应ER-06+ER-09；报告位置保持CORE_TIMELINE+HV_CHAIN_TABLE。 |
| PCS所见高压母线反馈 | PCS_dcdcHvBusVolt | PCS_dcdcBusStatus | 0x2B4 | V | 187.646484 \| 178.271484 \| 197.021484 \| 422.021484 \| 37.646484 \| 581.396484 \| 206.396484 \| 347.021484 \| 47.021484 \| 18.896484 \| 0.146484 \| 590.771484 | 是 | 来源：ONYX主候选；冲突项见定义对照；READABLE；SEMANTIC_VALIDATION_FAILED | PCS所见高压母线反馈；对应ER-06+ER-08；报告位置保持CORE_TIMELINE+HV_CHAIN_TABLE。 |
| HVIL安全条件 | HVP_hvilStatus | HVP_contactorState | 0x20A | enum | STATUS_OK \| UNKNOWN | 是 | 来源：ONYX主候选；冲突项见定义对照；READABLE；STRONGLY_SUPPORTED | HVIL安全条件；对应ER-05；报告位置保持SAFETY_CONDITION_TABLE+HV_CHAIN_TABLE。 |
| 绝缘安全条件背景 | BMS_isolationResistance | BMS_status | 0x212 | kOhm | 0 | 否/未形成变化证据 | 来源：ONYX主候选；冲突项见定义对照；READABLE；SEMANTIC_VALIDATION_FAILED | 绝缘安全条件背景；对应ER-05；报告位置保持SAFETY_CONDITION_TABLE。 |
| 负接触器执行反馈候选 | HVP_packContNegativeState | HVP_contactorState | 0x20A | enum | ECONOMIZED \| OPENING \| OPEN | 是 | 来源：ONYX主候选；冲突项见定义对照；READABLE；STRONGLY_SUPPORTED | 负接触器执行反馈候选；对应ER-06；报告位置保持HV_SPECIAL_TIMELINE。 |
| 正接触器/预充执行反馈候选 | HVP_packContPositiveState | HVP_contactorState | 0x20A | enum | ECONOMIZED \| OPENING \| OPEN \| PRECHARGE | 是 | 来源：ONYX主候选；冲突项见定义对照；READABLE；STRONGLY_SUPPORTED | 正接触器/预充执行反馈候选；对应ER-06；报告位置保持HV_SPECIAL_TIMELINE。 |
| DCDC状态机/执行反馈 | PCS_dcdcMainState | PCS_dcdcStatus | 0x224 | enum | STANDBY | 否/未形成变化证据 | 来源：ONYX主候选；冲突项见定义对照；READABLE；SEMANTIC_VALIDATION_FAILED | DCDC状态机/执行反馈；对应ER-08+ER-09；报告位置保持CORE_TIMELINE+DCDC_TABLE。 |
| 12V支持状态 | PCS_dcdc12VSupportStatus | PCS_dcdcStatus | 0x224 | enum | ACTIVE \| IDLE | 是 | 来源：ONYX主候选；冲突项见定义对照；READABLE；STRONGLY_SUPPORTED | 12V支持状态；对应ER-08；报告位置保持DCDC_SPECIAL_TABLE。 |
| 低压母线执行反馈 | PCS_dcdcLvBusVolt | PCS_dcdcBusStatus | 0x2B4 | V | 11.289062 \| 11.328125 \| 11.445312 \| 11.40625 \| 11.484375 \| 11.523438 \| 11.5625 \| 11.796875 \| 11.640625 \| 11.757812 \| 11.679688 \| 11.835938 | 是 | 来源：ONYX主候选；冲突项见定义对照；READABLE；STRONGLY_SUPPORTED | 低压母线执行反馈；对应ER-08+ER-09；报告位置保持CORE_TIMELINE+DCDC_TABLE。 |
| DCDC输出响应 | PCS_dcdcLvOutputCurrent | PCS_dcdcBusStatus | 0x2B4 | A | 26.9 \| 257.3 \| 334.1 \| 231.7 \| 359.7 \| 52.5 \| 282.9 \| 78.1 \| 385.3 \| 154.9 \| 206.1 \| 308.5 | 是 | 来源：ONYX主候选；冲突项见定义对照；READABLE；PARTIALLY_VALIDATED | DCDC输出响应；对应ER-08；报告位置保持DCDC_SPECIAL_TABLE。 |
| 电驱保持唤醒候选 | DI_keepAliveRequest | DI_systemStatus | 0x118 | boolean | NO_REQUEST \| KEEP_ALIVE | 是 | 来源：ONYX主候选；冲突项见定义对照；READABLE；INSUFFICIENT_EVIDENCE | 电驱保持唤醒候选；对应ER-01+ER-09；报告位置保持ENGINEERING_AUDIT+CONDITION_SUMMARY。 |
| 网关唤醒代理候选 | GTW_BMP_AWAKE_PIN | GTW_bmpDebug | 0x113 | boolean | 0 \| 1 | 是 | 来源：Model3CAN；READABLE；INSUFFICIENT_EVIDENCE | 网关唤醒代理候选；对应ER-01；报告位置保持ENGINEERING_AUDIT+NETWORK_WAKE_SUMMARY。 |
| 解/落锁请求候选 | UI_lockRequest | UI_vehicleControl | 0x273 | enum | IDLE | 否/未形成变化证据 | 来源：ONYX主候选；冲突项见定义对照；READABLE；INSUFFICIENT_EVIDENCE | 解/落锁请求候选；对应ER-02；报告位置保持ENGINEERING_AUDIT+BODY_INPUT_TABLE。 |

### 非DBC派生证据

| 控制树角色 | 派生证据 | 来源 | 本次观测 | 验证状态 | 本次用途 |
| --- | --- | --- | --- | --- | --- |
| 休眠/唤醒网络反馈 | 报文频率(派生) | ASC | 0..3086 frames/s | 来源：原始ASC统计；READABLE；PARTIALLY_VALIDATED | 休眠/唤醒网络反馈；对应ER-01；报告位置保持CORE_TIMELINE+NETWORK_WAKE_SUMMARY。 |
| 控制器分批唤醒代理 | 活跃CAN_ID数(派生) | ASC | 0..307 IDs/s | 来源：原始ASC统计；READABLE；PARTIALLY_VALIDATED | 控制器分批唤醒代理；对应ER-01；报告位置保持NETWORK_WAKE_SUMMARY。 |

## DBC异常与可读性说明

- BMS_hvState全程DOWN、BMS_isolationResistance全程0 kOhm、PCS_dcdcMainState全程STANDBY：既有结论均为SEMANTIC_VALIDATION_FAILED，不解释为车辆故障。
- 0x20A三项保留多DBC/DLC冲突边界；实验级结果见时间线专项表和machine_evidence/signal_validation_assessment.csv。
- PCS_dcdcHvBusVolt定量语义验证失败；PCS_dcdcLvBusVolt为实验候选，PCS_dcdcLvOutputCurrent仅部分验证。
