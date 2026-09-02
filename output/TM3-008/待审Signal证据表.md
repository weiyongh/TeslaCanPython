# TM3-008 待审Signal证据表

状态：`DRAFT / NOT_APPROVED / ASC_NOT_ANALYZED`。本表先由TM3-008实验问题、物理/控制过程和Evidence Requirements建立证据需求，再从DBC寻找候选；尚未读取本次ASC。DBC字段名不构成本实验事实。

## 1. 实验要回答的问题

车辆从READY、P挡稳定状态开始，驾驶员离座并开门、关门未锁、随后钥匙卡落锁后，可驱动/高压需求、高压接触器与下游母线、DCDC/低压支持及当前采集域通信按什么顺序退出；末段是否形成无再唤醒的通信静默候选。

判断只限`THIS_EXPERIMENT_ONLY`条件化基线，不评价车辆整体健康，不把“仍有报文”直接判为故障，也不把当前采集域静默外推为整车完全休眠。

## 2. Requirement与Candidate摘要

| Requirement | 证据目标 | 主要Candidate及Evidence Role | 当前覆盖判断 |
| --- | --- | --- | --- |
| ER-01 | 起始READY/P挡及高压、DCDC稳定 | `DI_gear`状态门；`DI_systemState`执行状态；`UI_readyForDrive`消费者反馈；`BMS_hvState`/`BMS_contactorState`高压执行；PCS DCDC状态与低压反馈 | CAN候选较完整；缺外部READY/现场记录 |
| ER-02 | 离座、开门和关门反馈 | `VCLEFT_frontOccupancyStatus`离座反馈候选；`VCLEFT_frontLatchStatus`门闩执行反馈 | 候选存在；独立动作时间GAP |
| ER-03 | 关门未锁与钥匙卡落锁区分 | `VCSEC_lockRequestType`请求类型；`VCSEC_simpleLockStatus`/`VCSEC_vehicleLockStatus`反馈/消费者状态；`UI_lockRequest`弱请求候选 | 候选存在但语义与来源均需ASC验证；外部落锁反馈GAP |
| ER-04 | 可驱动/驱动及高压需求撤销 | `DI_systemState`电驱执行；`VCFRONT_vehiclePowerState`整车供电状态候选；`VCFRONT_vehicleStatusDBG`阶段候选；`UI_readyForDrive`消费者反馈；`BMS_hvState`高压状态 | 没有已确认的整车下电请求直接Signal，保留请求/仲裁层GAP |
| ER-05 | 接触器退出与下游高压响应 | `BMS_contactorState`总执行；HVP正负接触器候选；`PCS_dcdcHvBusDischargeStatus`放电执行候选；`PCS_dcdcHvBusVolt`物理反馈候选；`BMS_packVoltage`仅作Pack端背景 | 接触器候选存在；下游高压定量反馈可信度低，可能形成GAP |
| ER-06 | DCDC/低压退出或保持 | `PCS_dcdcMainState`状态机；`PCS_dcdc12VSupportStatus`执行状态；PCS低压电压/电流反馈；`VCFRONT_12vStatusForDrive`消费者/状态交叉验证 | CAN候选存在；外部12 V实测GAP |
| ER-07 | 分层退出先后关系 | ER-02至ER-08的多层事件共同提供 | 无单一Signal可证明；必须在Assessment阶段逐层组合且不从先后关系自动推断因果 |
| ER-08 | 网络分批停止通信 | 帧率、活跃ID、逐ID最后出现时间三项派生证据；BMS/GTW网络管理候选 | 当前采集域候选充分；整车全网络覆盖不成立 |
| ER-09 | 末段持续静默且无再唤醒 | 派生网络证据；BMS/GTW asleep和keep-awake候选 | CAN结果候选存在；不少于10分钟无干预的外部证明GAP |
| ER-10 | Planned/Observed/CAN时间分离及无外部干扰 | 无合适CAN/DBC Candidate；只能由现场记录或App触发CSV提供 | **明确GAP** |

## 3. Candidate审核分组

### 建议P0核心候选

- 网络结果：`NetworkFrameRate_derived`、`CanIdLastSeenTime_derived`。
- 车身输入/反馈：`VCLEFT_frontOccupancyStatus`、`VCLEFT_frontLatchStatus`、`VCSEC_lockRequestType`、`VCSEC_simpleLockStatus`。
- 起始及需求/状态退出：`DI_gear`、`DI_systemState`、`VCFRONT_vehiclePowerState`。
- 高压执行/反馈：`BMS_hvState`、`BMS_contactorState`、`PCS_dcdcHvBusVolt`。
- DCDC/低压：`PCS_dcdcMainState`、`PCS_dcdc12VSupportStatus`、`PCS_dcdcLvBusVolt`。

其中`PCS_dcdcHvBusVolt`虽然承担P0 Requirement，但其既有定量语义验证失败；P0只表示该证据缺口对本实验重要，不提升Signal成熟度。若本次仍不能形成物理闭环，ER-05必须保留GAP。

### 建议P1交叉或专项候选

- `ActiveCanIdCount_derived`、`VCSEC_vehicleLockStatus`、`UI_readyForDrive`、`VCFRONT_vehicleStatusDBG`、`VCFRONT_12vStatusForDrive`。
- `HVP_packContPositiveState`、`HVP_packContNegativeState`、`BMS_packVoltage`、`PCS_dcdcHvBusDischargeStatus`、`PCS_dcdcLvOutputCurrent`。
- `BMS_nmGoingToSleep`、`BMS_hvsBusAsleep`、`GTW_nmGoingToSleep`、`GTW_VEHBusAsleep`。

### 建议P2工程审计/替代解释候选

- `UI_lockRequest`：UI发布者与B柱钥匙卡动作的绑定不明，不作为落锁请求主证据。
- `BMS_nmKeepAwakeReason`、`GTW_nmKeepAwakeReason`：只用于解释持续通信候选，不因枚举名称直接确认保持唤醒原因。
- `GTW_chBusAsleep`：用于分域退出线索，当前采集域适配范围待验证。

## 4. Candidate来源与当前可信度

- ONYX与`dbc/tesla_model3.dbc`同位段支持：BMS状态、BMS网络管理、DI状态、GTW网络管理、PCS DCDC状态、VCFRONT状态、VCSEC锁止状态等。跨文件一致只能提高候选定义可信度，仍不证明TM3-008中存在或语义成立。
- TM3-007已有实验级支持：`DI_gear`、`DI_systemState`、`BMS_contactorState`、`BMS_packVoltage`及部分DCDC状态。该结果只用于说明它们值得进入TM3-008候选，不把TM3-007的Assessment迁移为TM3-008事实。
- `0x20A`正负接触器候选：TM3-007内曾形成实验级支持，但存在跨DBC/DLC冲突；TM3-008仍须并列Signal Validation，不自动沿用结论。
- `0x2B4`：多个DBC在DLC、位段、缩放和符号上存在差异。`PCS_dcdcHvBusVolt`已有语义验证失败记录，低压电流仍属定量未验证；必须在本实验独立复核。
- `VCLEFT_frontLatchStatus`存在ETH参考版本位段冲突；`VCLEFT_frontOccupancyStatus`存在DLC/采集域适配问题。
- VCSEC、VCFRONT下电阶段及BMS/GTW网络管理字段目前主要是DBC命名候选，未获得TM3-008实测支持。

## 5. 全部Candidate均需ASC验证

Approved之后至少核对：CAN ID是否出现、实测DLC、位段/字节序/缩放/枚举适配、MUX条件、SNA/越界状态、完整状态转换、与其他层事件的时序、物理合理性及替代解释。派生证据还需验证ASC时间范围、无帧区间、逐ID末次出现时间及末段是否发生通信恢复。

ER-10没有Signal Candidate，不能通过扩大DBC搜索来补齐。ER-03的钥匙卡物理动作/反馈、ER-06的外部12 V以及ER-09的无干预条件也保留外部证据GAP。

## 6. 本轮需要人工Review

1. 是否接受上述10项Evidence Requirements及充分性边界。
2. 是否接受全部33项候选进入`THIS_EXPERIMENT_ONLY` Approved分析范围，或对任一项给出`ACCEPT / OVERRIDE / EXCLUDE`。
3. 是否接受三个P0但低成熟度候选：`VCSEC_lockRequestType`、`VCFRONT_vehiclePowerState`、`PCS_dcdcHvBusVolt`；其P0仅表示Requirement重要度，不代表语义可信。
4. 是否允许`0x20A`按多DBC并列Signal Validation候选进入分析，但不得自动升级车型级定义。
5. 是否接受缺少Observed Event Time和无干预现场记录的边界：脚本时间只用于粗定位，不形成精确人工动作响应延迟。
6. 是否接受ER-10保持明确GAP，而不以CAN事件替代现场记录。

本轮未创建`evidence_plan_review_overrides.csv`或`evidence_plan_approved.csv`。完成Review前禁止读取ASC和生成Evidence Assessment。
