# TM3-015 DBC关键Signal覆盖与可读性

- ASC：`input/can_20260831102614_TM3-015_直流快充采集.asc`；SHA-256 `622bfb8e8db203f0a5ba09b4ab91bff42415a28728a078a7c4f7f771e880665d`。
- 主DBC：`input/tesla_model3_ONYX.dbc`；Approved范围：`THIS_EXPERIMENT_ONLY`。
- 技术可解码不等于语义成立；完整逐Signal数据见`dbc_coverage_gate.csv`。

## 覆盖门失败项

| Signal | CAN ID | 结果 | Assessment |
| --- | --- | --- | --- |
| CP_hvChargeStatus | 0x13D | NO_FRAME | INSUFFICIENT_EVIDENCE / SEMANTIC_VALIDATION_FAILED |
| CP_chargeShutdownRequest | 0x13D | NO_FRAME | INSUFFICIENT_EVIDENCE / SEMANTIC_VALIDATION_FAILED |
| VCFRONT_chillerExvFlowTarget | 0x201 | MUX_NOT_OBSERVED_OR_UNREADABLE | INSUFFICIENT_EVIDENCE / SEMANTIC_VALIDATION_FAILED |
| VCFRONT_compressorTargetDuty | 0x281 | NO_FRAME | INSUFFICIENT_EVIDENCE / SEMANTIC_VALIDATION_FAILED |
| VCFRONT_compressorEnable | 0x281 | NO_FRAME | INSUFFICIENT_EVIDENCE / SEMANTIC_VALIDATION_FAILED |

## 关键语义验证结果

| Signal组 | 结果 | 边界 |
| --- | --- | --- |
| CP_chargeCablePresent / Secured / DoorOpen | 未通过名称语义验证 | 开口/插枪边沿方向与名称不一致 |
| CP_digitalCommsEstablished / evseRequest / evseAccept / gbState | 未观察到变化 | 不能证明内部协商顺序 |
| BMS_hvState | 未通过当前DBC适配 | 出现不合理快速枚举轮转 |
| CP_evseOutputDcCurrent / Voltage | Voltage定量较强；Current仅时序可信 | Current 128.108 A不作为桩端Actual；不确认CP功率 |
| BMS_packCurrent / Voltage | Pack侧实验级定量成立 | 平滑/未滤波电流、V×I和累计量在约70.7 kW闭合 |
| BMS_chgPowerAvailable | bit40部分验证 | 约72.98 kW能力上限候选；非Request/Actual；ONYX bit38失败 |
| BMS_modelTMax | 候选可用 | 33.5→35.0°C；仍保持候选 |
| BMS_modelTMin / minPackTemperature / CP针脚温度 | 未通过 | SNA/不合理范围，不进入温度结论 |
| 热管理泵/阀/Chiller/压缩机/模式 | 部分技术可读 | 不据名称形成请求—执行结论 |

## Approved关键Signal逐项覆盖

| 角色 | Signal | 中文语义 | CAN ID | DBC/需要/ASC DLC | 解码/帧 | 可读性 |
| --- | --- | --- | --- | --- | --- | --- |
| 外部动作反馈 | CP_chargeDoorOpen | 充电口盖开启状态（DBC定义候选，待本车验证） | 0x25D | 8/2/8 | 2997/2997 | READABLE |
| 连接状态 | CP_chargeCablePresent | 充电线缆存在状态（待验证，不替代实际插拔记录） | 0x25D | 8/1/8 | 2997/2997 | READABLE |
| 安全状态门 | CP_chargeCableSecured | 充电线缆已固定状态（具体锁止含义待验证） | 0x25D | 8/1/8 | 2997/2997 | READABLE |
| 安全状态门 | CP_latchState | 充电枪锁止机构状态（待验证，不单独作为安全拔枪依据） | 0x25D | 8/1/8 | 2997/2997 | READABLE |
| 连接类型状态 | CP_evseChargeType | 车辆侧可见的EVSE充电类型候选（直流/交流枚举待验证） | 0x21D | 8/5/8 | 2997/2997 | READABLE |
| 协商状态 | CP_digitalCommsEstablished | 车辆侧数字通信已建立候选状态（不代表完整协议握手） | 0x21D | 8/5/8 | 2997/2997 | READABLE |
| 请求候选 | CP_evseRequest | EVSE请求候选状态（请求主体及控制层级待验证） | 0x21D | 8/1/8 | 2997/2997 | READABLE |
| 许可反馈候选 | CP_evseAccept | EVSE接受候选状态（不等同扫码或支付平台接受） | 0x21D | 8/1/8 | 2997/2997 | READABLE |
| 专项状态机候选 | CP_gbState | 国标直流充电状态机候选（位段/位宽冲突未解决） | 0x21D | 8/7/8 | 2997/2997 | READABLE |
| 充电许可/状态 | CP_hvChargeStatus | 车辆侧高压充电状态候选（连接/测试/使能等枚举待验证） | 0x13D | 6/1/- | 0/0 | NO_FRAME |
| 专项停止请求候选 | CP_chargeShutdownRequest | 充电关断请求候选（正常/紧急及请求主体待验证） | 0x13D | 6/1/- | 0/0 | NO_FRAME |
| 专项停止请求候选 | CP_stopChargeRequest | 停止充电请求候选（与关断请求的层级关系待验证） | 0x21D | 8/6/8 | 2997/2997 | READABLE |
| 车辆充电请求 | BMS_chargeRequest | BMS充电请求状态（车型语义仍需本次验证） | 0x212 | 8/4/8 | 2997/2997 | READABLE |
| 车辆状态反馈 | BMS_uiChargeStatus | BMS面向车辆显示的充电状态（本地DBC位段冲突待复核） | 0x212 | 8/5/8 | 2997/2997 | READABLE |
| 高压状态门 | BMS_hvState | BMS高压系统状态（含直流充电状态枚举，待本次验证） | 0x212 | 8/3/8 | 2997/2997 | READABLE |
| 安全状态门 | BMS_contactorState | Pack主接触器状态（仅作为高压建立的部分证据） | 0x212 | 8/2/8 | 2997/2997 | READABLE |
| 执行反馈 | CP_evseOutputDcCurrent | 车辆侧可见的EVSE直流输出电流候选（待与桩端和Pack交叉验证） | 0x29D | 4/2/5 | 2997/2997 | READABLE |
| 能源交叉验证 | CP_evseOutputDcVoltage | 车辆侧可见的EVSE直流输出电压候选（不能单独定义充电开始） | 0x29D | 4/4/5 | 2997/2997 | READABLE |
| 能源交叉验证 | CP直流输出功率(同帧V×I派生) | 由CP侧同帧电压与电流计算的直流输出功率候选 | 0x29D | -/-/5 | 0/2997 | DERIVED_AFTER_INPUT_VALIDATION |
| 能源交叉验证 | BMS_packVoltage | Pack端电压（用于能源交叉验证和功率计算） | 0x132 | 8/2/6 | 29973/29973 | READABLE |
| 能源响应 | BMS_packCurrent | Pack净电流（实际充电建立核心证据，符号/偏置待审计） | 0x132 | 8/4/6 | 29973/29973 | READABLE |
| 能源交叉验证 | Pack功率(同帧V×I派生) | 由Pack同帧电压与电流计算的净功率（展示符号待明确） | 0x132 | -/-/6 | 0/29973 | DERIVED_AFTER_INPUT_VALIDATION |
| 能力背景 | BMS_chgPowerAvailable | BMS可用充电功率候选（Available不等于Request或Actual） | 0x212 | 8/7/8 | 2997/2997 | READABLE |
| 状态条件 | BMS_socUI | 车辆显示SOC（仅限定本次充电条件，不用于容量或SOH判断） | 0x292 | 8/3/8 | 2997/2997 | READABLE |
| 状态条件 | BMS_minPackTemperature | Pack最低温度候选（不能代表完整温度范围） | 0x212 | 8/8/8 | 2997/2997 | READABLE |
| 状态条件 | PCS_dcdcLvBusVolt | DCDC低压母线电压候选（充电期间低压供电背景） | 0x2B4 | 5/2/6 | 2998/2998 | READABLE |
| 异常分支筛查 | CP_numAlertsSet | 充电口控制器告警数量候选（计数本身不构成故障语义） | 0x25D | 8/8/8 | 2997/2997 | READABLE |
| 整车状态条件 | DI_gear | 挡位状态（充电许可条件背景，不代表OEM完整许可规则） | 0x118 | 8/3/8 | 10683/10683 | READABLE |
| 整车系统状态条件 | DI_systemState | 电驱系统状态（是否参与充电许可待验证） | 0x118 | 8/3/8 | 10683/10683 | READABLE |
| Pack热状态 | BMS_modelTMax | Pack模型最高温度候选（是否代表实测单体/模组最高温度待验证） | 0x332 | 6/5/6 | 149/299 | READABLE_ON_MUX_PAGE |
| Pack热状态 | BMS_modelTMin | Pack模型最低温度候选（是否代表实测单体/模组最低温度待验证） | 0x332 | 6/6/6 | 149/299 | READABLE_ON_MUX_PAGE |
| 接口热状态 | CP_pinTemperature1 | 充电接口针脚温度1候选（具体针脚对应关系待验证） | 0x75D | 8/2/8 | 214/1499 | READABLE_ON_MUX_PAGE |
| 接口热状态 | CP_pinTemperature2 | 充电接口针脚温度2候选（具体针脚对应关系待验证） | 0x75D | 8/3/8 | 214/1499 | READABLE_ON_MUX_PAGE |
| 接口热状态 | CP_pinTemperature3 | 充电接口针脚温度3候选（具体针脚对应关系待验证） | 0x75D | 8/4/8 | 214/1499 | READABLE_ON_MUX_PAGE |
| 热管理条件/决策 | BMS_activeHeatingWorthwhile | BMS判断主动加热是否值得的候选状态（不是加热执行反馈） | 0x212 | 8/1/8 | 2997/2997 | READABLE |
| 热管理请求 | BMS_hvacPowerRequest | BMS向热管理系统提出功率请求的候选状态（具体请求内容待验证） | 0x212 | 8/1/8 | 2997/2997 | READABLE |
| 热管理请求 | BMS_flowRequest | BMS电池回路冷却液流量请求候选 | 0x312 | 8/3/8 | 599/599 | READABLE |
| 热管理目标 | BMS_inletActiveCoolTargetT | BMS电池入口主动冷却目标温度候选 | 0x312 | 8/4/8 | 599/599 | READABLE |
| 热管理目标 | BMS_inletActiveHeatTargetT | BMS电池入口主动加热目标温度候选 | 0x312 | 8/6/8 | 599/599 | READABLE |
| 热管理反馈 | VCFRONT_tempCoolantBatInlet | 电池回路冷却液入口温度候选 | 0x321 | 8/2/8 | 299/299 | READABLE |
| 执行目标 | VCFRONT_coolantFlowBatTarget | 电池回路冷却液目标流量候选 | 0x241 | 7/3/7 | 2997/2997 | READABLE |
| 执行反馈 | VCFRONT_coolantFlowBatActual | 电池回路冷却液实际流量候选 | 0x241 | 7/2/7 | 2997/2997 | READABLE |
| 执行目标 | VCFRONT_pumpBatteryRPMTarget | 电池冷却液泵目标转速候选 | 0x2C1 | 8/2/8 | 2997/14986 | READABLE_ON_MUX_PAGE |
| 执行反馈 | VCFRONT_pumpBatteryRPMActual | 电池冷却液泵实际转速候选 | 0x201 | 8/2/8 | 2997/11988 | READABLE_ON_MUX_PAGE |
| 热管理决策/请求 | VCFRONT_chillerDemandActive | Chiller制冷需求激活候选状态 | 0x2E1 | 8/4/8 | 3123/18735 | READABLE_ON_MUX_PAGE |
| 执行目标 | VCFRONT_chillerExvFlowTarget | Chiller电子膨胀阀目标开度候选 | 0x201 | 8/2/8 | 0/11988 | MUX_NOT_OBSERVED_OR_UNREADABLE |
| 执行反馈 | VCFRONT_chillerExvFlow | Chiller电子膨胀阀实际开度候选 | 0x201 | 8/2/8 | 2997/11988 | READABLE_ON_MUX_PAGE |
| 执行目标 | VCFRONT_compressorTargetDuty | 压缩机目标占空比候选 | 0x281 | 8/2/- | 0/0 | NO_FRAME |
| 执行目标 | VCFRONT_compressorEnable | 压缩机使能请求候选 | 0x281 | 8/6/- | 0/0 | NO_FRAME |
| 执行反馈 | VCFRONT_compressorState | 压缩机运行状态候选 | 0x201 | 8/4/8 | 2997/11988 | READABLE_ON_MUX_PAGE |
| 执行目标 | VCFRONT_coolantValveAngleTarget | 冷却液多通阀目标角度候选 | 0x2C1 | 8/4/8 | 2997/14986 | READABLE_ON_MUX_PAGE |
| 执行反馈 | VCFRONT_coolantValveAngleActual | 冷却液多通阀实际角度候选 | 0x2C1 | 8/3/8 | 2997/14986 | READABLE_ON_MUX_PAGE |
| 热管理模式 | VCFRONT_hpMode | 热泵系统运行模式候选 | 0x381 | 8/2/8 | 308/8326 | READABLE_ON_MUX_PAGE |
| 热管理模式 | VCFRONT_hpBatteryCool | 热泵电池冷却模式候选 | 0x381 | 8/3/8 | 308/8326 | READABLE_ON_MUX_PAGE |
| 执行反馈 | VCFRONT_isActiveHeatingBattery | 电池主动加热执行状态候选 | 0x2E1 | 8/8/8 | 3122/18735 | READABLE_ON_MUX_PAGE |

## DBC冲突排除

`0x27D`在ONYX中为`APS_eacMonitor`，替代DBC中却是`CP_dcChargeLimits`；`0x2BD`仅替代DBC定义。三项能力字段继续仅作版本适配审计，不进入结论。
