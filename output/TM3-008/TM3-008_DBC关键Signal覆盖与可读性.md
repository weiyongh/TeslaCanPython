# TM3-008 DBC关键Signal覆盖与可读性

## 核心Signal表

| 序号 | Signal | 控制含义 | Message | CAN ID | 单位 | 本次观测范围/状态 | 是否变化 | 解码/验证状态 | 本次用途/边界 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | VCLEFT_frontOccupancyStatus | 驾驶员离座反馈候选/可见性验证目标 | VCLEFT_restraintStatus | 0x30A | enum | 无有效观测 | 未观察 | NO_FRAME；INSUFFICIENT_EVIDENCE | 用于ER-02的驾驶员离座反馈候选/可见性验证目标证据；边界：0x30A无帧。 |
| 2 | VCLEFT_frontLatchStatus | 驾驶门闩执行反馈 | VCLEFT_doorStatus | 0x102 | enum | CLOSED \| OPENED | 是 | READABLE；STRONGLY_SUPPORTED | 用于ER-02+ER-03+ER-07的驾驶门闩执行反馈证据；边界：CLOSED-OPENED-CLOSED与采集脚本动作顺序一致。 |
| 3 | VCSEC_lockRequestType | 钥匙卡/NFC锁止请求类型候选 | VCSEC_authentication | 0x339 | enum | NONE \| ACTIVE_NFC_LOCK | 是 | READABLE；STRONGLY_SUPPORTED | 用于ER-03的钥匙卡/NFC锁止请求类型候选证据；边界：ACTIVE_NFC_LOCK与两项锁状态在同一时刻转为LOCKED。 |
| 4 | VCSEC_simpleLockStatus | 整车简化锁止反馈候选 | VCSEC_authentication | 0x339 | enum | UNLOCKED \| LOCKED | 是 | READABLE；STRONGLY_SUPPORTED | 用于ER-03+ER-07的整车简化锁止反馈候选证据；边界：关门后保持UNLOCKED，NFC锁止候选出现时转LOCKED。 |
| 5 | VCSEC_vehicleLockStatus | 锁止方式/结果消费者状态候选 | VCSEC_authentication | 0x339 | enum | ACTIVE_NFC_UNLOCKED \| ACTIVE_NFC_LOCKED | 是 | READABLE；PARTIALLY_VALIDATED | 用于ER-03的锁止方式/结果消费者状态候选证据；边界：与simple状态和NFC锁止候选同向；不作为独立机械反馈。 |
| 6 | UI_lockRequest | CONSUMER_STATE_CANDIDATE | UI_vehicleControl | 0x273 | enum | IDLE | 否/未形成变化证据 | READABLE；INSUFFICIENT_EVIDENCE | 用于ER-03的CONSUMER_STATE_CANDIDATE证据；边界：有帧但全程IDLE；不代表钥匙卡落锁REQUEST，也不能独立满足ER-03。 |
| 7 | DI_gear | 挡位反馈/起始状态门 | DI_systemStatus | 0x118 | enum | 无有效观测 | 未观察 | NO_FRAME；INSUFFICIENT_EVIDENCE | 用于ER-01+ER-04的挡位反馈/起始状态门证据；边界：本片段无可解样本，P挡缺直接CAN证据。 |
| 8 | DI_systemState | 电驱执行状态/ENABLE退出候选 | DI_systemStatus | 0x118 | enum | 无有效观测 | 未观察 | NO_FRAME；INSUFFICIENT_EVIDENCE | 用于ER-01+ER-04+ER-07的电驱执行状态/ENABLE退出候选证据；边界：本片段无可解样本。 |
| 9 | UI_readyForDrive | 显示/消费者层可驱动反馈候选 | UI_status | 0x353 | boolean | 1 \| 0 | 是 | READABLE；PARTIALLY_VALIDATED | 用于ER-01+ER-04的显示/消费者层可驱动反馈候选证据；边界：起始为1并于落锁后转0；仅作消费者状态，不作为许可源。 |
| 10 | VCFRONT_vehiclePowerState | 车辆供电阶段系统结果候选 | VCFRONT_LVPowerState | 0x221 | enum | ACCESSORY \| CONDITIONING \| OFF | 是 | READABLE；PARTIALLY_VALIDATED | 用于ER-01+ER-04+ER-07的车辆供电阶段系统结果候选证据；边界：CONDITIONING到OFF先于接触器退出；仅作SYSTEM_RESULT。 |
| 11 | VCFRONT_12vStatusForDrive | 12V侧退出可驱动状态候选 | VCFRONT_vehicleStatus | 0x3A1 | enum | 无有效观测 | 否/未形成变化证据 | UNREADABLE；INSUFFICIENT_EVIDENCE | 用于ER-04+ER-06的12V侧退出可驱动状态候选证据；边界：0x3A1有帧但ONYX MUX下未解出该Signal。 |
| 12 | BMS_hvState | BMS高压系统结果/执行候选（低可信验证目标） | BMS_status | 0x212 | enum | DOWN | 否/未形成变化证据 | READABLE；SEMANTIC_VALIDATION_FAILED | 用于ER-01+ER-04+ER-05+ER-07的BMS高压系统结果/执行候选（低可信验证目标）证据；边界：接触器由CLOSED经OPENING转OPEN期间全程均为DOWN。 |
| 13 | BMS_contactorState | BMS接触器总执行状态 | BMS_status | 0x212 | enum | CLOSED \| OPENING \| OPEN | 是 | READABLE；STRONGLY_SUPPORTED | 用于ER-01+ER-05+ER-07+ER-09的BMS接触器总执行状态证据；边界：本下电窗口观察到CLOSED-OPENING-OPEN完整转换。 |
| 14 | HVP_packContPositiveState | 正接触器独立执行反馈候选 | HVP_contactorState | 0x20A | enum | ECONOMIZED \| OPENING \| OPEN | 是 | READABLE；STRONGLY_SUPPORTED | 用于ER-05+ER-07的正接触器独立执行反馈候选证据；边界：0x20A DLC6原始bit与总接触器及电压变化闭环；保留实验范围。 |
| 15 | HVP_packContNegativeState | 负接触器独立执行反馈候选 | HVP_contactorState | 0x20A | enum | ECONOMIZED \| OPENING \| OPEN | 是 | READABLE；STRONGLY_SUPPORTED | 用于ER-05+ER-07的负接触器独立执行反馈候选证据；边界：0x20A DLC6原始bit与总接触器及电压变化闭环；保留实验范围。 |
| 16 | BMS_packVoltage | Pack端高压背景反馈 | BMS_hvBusStatus | 0x132 | V | 8.540000..353.970000 | 是 | READABLE；PARTIALLY_VALIDATED | 用于ER-01+ER-05的Pack端高压背景反馈证据；边界：0.01 V缩放及高压下降/恢复动态可信；Pack端物理定位不成立或未确认。 |
| 17 | PCS_dcdcHvBusVolt | PCS所见高压母线物理响应候选 | PCS_dcdcBusStatus | 0x2B4 | V | 0.146484..590.771484 | 是 | READABLE；SEMANTIC_VALIDATION_FAILED | 用于ER-05+ER-06的PCS所见高压母线物理响应候选证据；边界：0x2B4实际DLC6而候选DLC5；值在0.15到590.77 V非物理跳变且不闭合。 |
| 18 | PCS_dcdcHvBusDischargeStatus | 高压母线主动放电执行候选 | PCS_dcdcStatus | 0x224 | enum | IDLE \| ACTIVE | 是 | READABLE；PARTIALLY_VALIDATED | 用于ER-05+ER-06+ER-07的高压母线主动放电执行候选证据；边界：IDLE-ACTIVE-IDLE与0x132电压快速下降时序一致；不证明终值。 |
| 19 | PCS_dcdcMainState | DCDC主状态机执行候选（低可信验证目标） | PCS_dcdcStatus | 0x224 | enum | STANDBY | 否/未形成变化证据 | READABLE；SEMANTIC_VALIDATION_FAILED | 用于ER-01+ER-06+ER-07的DCDC主状态机执行候选（低可信验证目标）证据；边界：12V支持ACTIVE-IDLE-ACTIVE-IDLE变化期间全程STANDBY。 |
| 20 | PCS_dcdc12VSupportStatus | 12V支持执行状态 | PCS_dcdcStatus | 0x224 | enum | ACTIVE \| IDLE | 是 | READABLE；STRONGLY_SUPPORTED | 用于ER-01+ER-06的12V支持执行状态证据；边界：最终ACTIVE-IDLE紧随vehiclePowerState OFF，且低压输出电流候选归零。 |
| 21 | PCS_dcdcLvBusVolt | PCS侧低压母线反馈候选 | PCS_dcdcBusStatus | 0x2B4 | V | 7.773438..14.062500 | 是 | READABLE；PARTIALLY_VALIDATED | 用于ER-01+ER-06的PCS侧低压母线反馈候选证据；边界：采用ETH/JSON DLC6定义后约7.77到14.06 V；动态可用但无外部12V标定。 |
| 22 | PCS_dcdcLvOutputCurrent | DCDC输出电流响应候选 | PCS_dcdcBusStatus | 0x2B4 | A | 0.000000..385.300000 | 是 | READABLE；PARTIALLY_VALIDATED | 用于ER-06的DCDC输出电流响应候选证据；边界：采用ETH/JSON DLC6 signed定义后约0到385.3 A且最终退出归零；无外部标定。 |
| 23 | BMS_nmGoingToSleep | BMS网络管理阶段系统结果候选 | BMS_vehNm | 0x2F2 | boolean | 0 | 否/未形成变化证据 | READABLE；INSUFFICIENT_EVIDENCE | 用于ER-08+ER-09的BMS网络管理阶段系统结果候选证据；边界：全程0，未观察转换。 |
| 24 | BMS_hvsBusAsleep | BMS所见总线休眠反馈候选 | BMS_vehNm | 0x2F2 | boolean | 0 \| 1 | 是 | READABLE；PARTIALLY_VALIDATED | 用于ER-08+ER-09的BMS所见总线休眠反馈候选证据；边界：0到1发生在静默前；仅BMS消费者视角。 |
| 25 | BMS_nmKeepAwakeReason | BMS保持唤醒原因候选 | BMS_vehNm | 0x2F2 | enum | CTRS_CLOSED \| NONE_SNA | 是 | READABLE；TIMING_ONLY_VALID | 用于ER-08+ER-09的BMS保持唤醒原因候选证据；边界：CTRS_CLOSED到NONE_SNA与接触器退出同步；原因枚举无独立确认。 |
| 26 | GTW_nmGoingToSleep | 网关网络管理阶段系统结果候选 | GTW_vehNm | 0x458 | boolean | 0 | 否/未形成变化证据 | READABLE；INSUFFICIENT_EVIDENCE | 用于ER-08+ER-09的网关网络管理阶段系统结果候选证据；边界：全程0，未观察转换。 |
| 27 | GTW_VEHBusAsleep | 网关所见车辆总线休眠反馈候选 | GTW_vehNm | 0x458 | boolean | 0 \| 1 | 是 | READABLE；PARTIALLY_VALIDATED | 用于ER-08+ER-09的网关所见车辆总线休眠反馈候选证据；边界：0到1发生于末段静默前；仅GTW消费者视角，不能代表整车网络。 |
| 28 | GTW_chBusAsleep | 网关所见CH总线消费者状态候选 | GTW_vehNm | 0x458 | boolean | 0 \| 1 | 是 | READABLE；PARTIALLY_VALIDATED | 用于ER-08+ER-09的网关所见CH总线消费者状态候选证据；边界：0到1发生于末段静默前；CH域边界及整车外推未确认。 |
| 29 | GTW_nmKeepAwakeReason | 网关保持唤醒原因候选 | GTW_vehNm | 0x458 | enum | NONE_SNA | 否/未形成变化证据 | READABLE；INSUFFICIENT_EVIDENCE | 用于ER-08+ER-09的网关保持唤醒原因候选证据；边界：全程NONE_SNA，不能解释退出或再唤醒。 |

### 非DBC派生证据

| 序号 | 派生证据 | 派生含义 | 来源/统计对象 | 本次观测 | 验证状态 | 本次用途/边界 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 报文频率(派生) | 采集域通信结果/静默代理 | ASC | 0..2293 frames/s | READABLE；PARTIALLY_VALIDATED | 用于ER-08+ER-09的采集域通信结果/静默代理证据；边界：采集域通信量可信；不外推整车网络。 |
| 2 | 活跃CAN_ID数(派生) | 采集域控制器活跃度代理 | ASC | 0..266 IDs/s | READABLE；PARTIALLY_VALIDATED | 用于ER-08+ER-09的采集域控制器活跃度代理证据；边界：采集域活跃ID数可信；不等同ECU数量。 |
| 3 | 逐CAN_ID最后出现时间(派生) | 分批通信退出时序代理 | ASC | 29.909000..295.838300 s | READABLE；PARTIALLY_VALIDATED | 用于ER-07+ER-08的分批通信退出时序代理证据；边界：报文最后出现时间可信；不等同ECU断电。 |

## DBC异常与可读性说明

- VCLEFT_frontOccupancyStatus、DI_gear、DI_systemState无帧；VCFRONT_12vStatusForDrive有帧但当前MUX/DBC下不可读。
- BMS_hvState、PCS_dcdcMainState、PCS_dcdcHvBusVolt均为SEMANTIC_VALIDATION_FAILED，不解释为车辆故障。
- UI_lockRequest全程IDLE，不能解释为钥匙卡落锁REQUEST，也不能独立满足ER-03。
- 0x20A正负接触器候选仅在TM3-008范围内STRONGLY_SUPPORTED，保留多DBC边界。
