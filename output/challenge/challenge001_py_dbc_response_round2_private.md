# Challenge 001 — Round 2 Py DBC 最终镜像应答（裁判私有）

> 保密范围：本文件包含 TeslaCanPython 既有 DBC / Signal 定义，不得提供给 TeslaCanYi。
>
> 检查边界：仅对 `input/input/challenge/challenge001_yi_hit_points_round2.md` 的冻结点位执行 DBC / Signal 镜像查询；未读取 TeslaCanYi、ASC、照片、Timeline、Session Evidence、Yi 分析程序或中间产物，未执行新的 CAN Reverse。

原表约定：byte 从 0 开始编号；bit 0 为该 byte 的最低位。所有 Yi Claim 均表示关联，不表示已确认语义。

| # | CAN ID | Field | Yi Claim | Py DBC Result | Private DBC Evidence |
| -: | :----- | :---- | :------- | :------------ | :------------------- |
| 1 | `0x21D` | byte 3 bit 5 | 插枪后保持、拔枪后恢复的连接周期相关状态 | MISS | 全局 bit 29 位于 `CP_cableCurrentLimit`（start 24, length 7, A）内，是线缆电流限值的数值位，不是连接周期状态。 |
| 2 | `0x21D` | byte 4 bit 7 | 充电建立后保持、拔枪后恢复的会话相关状态 | PARTIAL | 全局 bit 39 位于 `CP_evseChargeType`/`CP_evseChargeType_UI`（start 38, length 2）内。位置与 EVSE 充电类型字段重合且和会话相关，但 Yi 仅取该多 bit Signal 的一个 bit，DBC 也不能完整证明所述保持/恢复行为。 |
| 3 | `0x21D` | byte 6 bits 4:6 | 未连接／连接／充电／停止瞬态相关阶段状态 | UNKNOWN | 现有 DBC 在 bits 52–54 定义无法统一：ONYX/`tesla_model3.dbc` 为 `CP_gbState` 与 `CP_gbdcStopChargeReason` 的交界；`Model3CAN.dbc` 则由 `CP_gbdcChargeAttempts` 和 `CP_acChargeState` 交叠覆盖。精确 field 含义和边界存在无法消解的版本冲突。 |
| 4 | `0x43D` | byte 0 bit 0 | 插枪后保持、拔枪后恢复的连接周期相关状态 | PARTIAL | bit 0 位于 `CP_hvChargeStatus_log`（start 0, length 3）内。充电状态关系明确，但单 bit 不是完整 Signal，且 Claim 扩展到整个插枪连接周期。 |
| 5 | `0x43D` | byte 0 bit 2 | 充电建立／停止相关状态变化 | PARTIAL | bit 2 位于 `CP_hvChargeStatus_log`（start 0, length 3）内，功能关联明确；但只命中多 bit 状态字段的一位，不能按完整 field 判 HIT。 |
| 6 | `0x43D` | byte 1 bit 6 | 充电建立／停止相关窗口状态 | MISS | 全局 bit 14 位于 `CP_acChargeCurrentLimit_log`（start 8, length 8, scale 0.5 A）内，是 AC 电流限值的数值位，不是窗口状态。 |
| 7 | `0x43D` | byte 5 bit 5 | 充电小门打开周期相关状态 | UNKNOWN | 全局 bit 45 在现有 `ID43DCP_chargeStatusLog` 定义中未覆盖；不能因同一 message 与充电有关就补成小门状态。 |
| 8 | `0x43D` | byte 5 bits 0:2 | 充电建立／停止仍连接相关阶段子状态 | PARTIAL | bits 40–41 定义为 `CP_evseChargeType_log`（start 40, length 2），bit 42 未覆盖。与 EVSE/充电阶段存在明确关系，但 Yi field 多出未定义 bit，Claim 也比“充电类型”更宽。 |
| 9 | `0x132` | byte 0:1，little-endian 观察 | 充电保持期间缓慢变化、停止后回落的连续量 | HIT | byte 0:1 精确对应 `BMS_packVoltage`/`BattVoltage132`（start 0, length 16, 0.01 V），位置、完整字段和充电过程连续量关联明确吻合。 |
| 10 | `0x132` | byte 2:3，signed little-endian 观察 | 充电建立后跨零增长、停止时回零的连续量 | PARTIAL | 该位置对应 `BMS_packCurrent`/`SmoothBattCurrent132`，功能关联明确；但现有定义在 length 15/16、offset 与负 scale 编码上存在版本差异，不能完整支持 Yi 声明的“signed 16-bit”边界与编码。 |
| 11 | `0x132` | byte 4:5，little-endian 观察 | 充电过程相关连续量 | HIT | byte 4:5 精确对应 `BMS_currentUnfiltered`/`RawBattCurrent132`（start 32, length 16），是 Pack 原始/未滤波电流连续量，位置和功能关联明确吻合。 |
| 12 | `0x264` | byte 0 + byte 1 bits 0:6，little-endian 观察 | 充电建立／退出相关 15-bit 连续量 | PARTIAL | `PCS_chgInputVoltage`/`ChargeLineVoltage264` 仅为 bits 0–13（length 14）；bit 14 已是 `PCS_chgLineCurrent` 的起始位。Yi 的 15-bit 观察跨两个 Signal，虽为充电线路连续量但边界不完整吻合。 |
| 13 | `0x264` | byte 2:3，little-endian 观察 | 充电建立／退出相关连续量 | PARTIAL | bits 16–22 是 `PCS_chgLineCurrent` 后部，bits 24–31 是 `PCS_chgInputPower`，中间还含未归入同一数值的边界；16-bit 观察跨多个 Signal，关联成立但不能判完整 HIT。 |
| 14 | `0x264` | byte 4 bits 5:7 | 未建立／充电／停止仍连接相关阶段状态 | MISS | 全局 bits 37–39 位于 `PCS_chgAcCurrentLimit`/`ChargeLineCurrentLimit264`（start 32, length 10, A）内，是电流限值数值位，不是阶段状态。 |
| 15 | `0x264` | byte 5 bit 0 | 稳态充电窗口相关状态 | MISS | 全局 bit 40 同样位于 `PCS_chgAcCurrentLimit`/`ChargeLineCurrentLimit264` 数值字段内，不是稳态窗口状态。 |
| 16 | `0x252` | byte 0:1，little-endian 观察 | 充电建立时进入、停止时归零的连续量 | MISS | byte 0:1 精确对应 `BMS_maxRegenPower`（start 0, length 16, kW），定义为最大回收功率能力，不是充电建立/停止连续量。 |
| 17 | `0x252` | byte 2:3，little-endian 观察 | 充电建立／退出期间反向变化的连续量 | MISS | byte 2:3 精确对应 `BMS_maxDischargePower`（start 16, length 16, kW），定义为最大放电功率能力，不是充电建立/退出连续量。 |
| 18 | `0x204` | byte 7 bit 0 | 充电建立／停止相关窗口状态 | HIT | 全局 bit 56 精确对应单 bit `PCS_chgPwmEnableLine`，是充电 PWM 使能线路状态；位置、粒度和充电建立/停止窗口关联明确吻合。 |
| 19 | `0x212` | byte 2 | 充电建立后增长、停止时阶梯衰减的连续量 | PARTIAL | byte 2 同时覆盖 `BMS_hvState`（start 16, length 3）和 `BMS_isolationResistance`（start 19, length 10）的低位。存在 HV/绝缘连续量对应，但整 byte 跨离散状态与连续 Signal，不能作为单一衰减量。 |
| 20 | `0x212` | byte 3 bit 6 | 充电建立／停止相关窗口状态 | MISS | 全局 bit 30 精确对应 `BMS_keepWarmRequest`，是保温请求，不是充电建立/停止窗口状态。 |
| 21 | `0x20A` | byte 5 bit 4 | 充电窗口相关状态 | UNKNOWN | `Model3CAN.dbc` 将该位放在 `HVP_fcLinkAllowedToEnergize`（start 44, length 2）中，ONYX/`tesla_model3.dbc` 对该位未覆盖，另有现有 DBC 将 `0x20A` 定义成不同 message。当前定义冲突/不足，无法可靠裁决 Claim。 |
| 22 | `0x24A` | byte 0 bit 1 | 充电建立／停止相关低频状态变化 | UNKNOWN | 虽然 `0x24A` message 被定义为 `DAS_visualDebug`，但精确 bit 1 在现有 Model 3 DBC 中未覆盖；按规则不能仅凭 message 功能将未定义 field 判 MISS。 |
| 23 | `0x232` | byte 0 bit 6 | 充电建立／停止相关状态变化 | UNKNOWN | `Model3CAN.dbc` 将 bit 6 定义为 `BMS_gpoHasCompleted`；ONYX/`tesla_model3.dbc` 同位置未覆盖。名称不足以可靠确认或排除其与充电接触器过程的关系，因此不补充语义、不判 MISS。 |
| 24 | `0x232` | byte 1 bit 1 | 充电建立／停止相关状态变化 | UNKNOWN | 全局 bit 9 在现有 `BMS_contactorRequest` 定义中未覆盖。 |
| 25 | `0x472` | byte 4 bit 4 | 充电建立完成／停止相关窗口状态 | UNKNOWN | 查询的现有 DBC 未覆盖 `0x472`，无法判断该 field。 |
| 26 | `0x32A` | byte 3 bits 0:3 | 充电保持／退出相关离散值变化 | MISS | bits 24–27 在 `DAS_warningMatrix0` 中分别定义为转向接管、ECU 时序、ECU reset 与 SPI 接收错误告警位，和充电保持/退出明显无关。 |
| 27 | `0x2EC` | byte 0 | 插枪后保持、拔枪后恢复的连接周期相关值 | UNKNOWN | 查询的现有 DBC 未覆盖 `0x2EC`。 |
| 28 | `0x2AA` | byte 0 | 插枪后保持、拔枪后恢复的连接周期相关值 | UNKNOWN | 查询的现有 DBC 未覆盖 `0x2AA`。 |
| 29 | `0x2E8` | byte 5 bit 7 | 插枪后保持、拔枪后恢复的连接周期相关状态 | UNKNOWN | 同一 ID/field 的现有定义冲突：Model 3 DBC 为 `EPBR_okToPark`，另两份 DBC 为 `UI_csaRoadCurvCounter`。两者均不支持 Claim，但因 Ground Truth 镜像自身在精确位置存在无法解决的功能冲突，按本轮规则判 UNKNOWN。 |
| 30 | `0x2A8` | byte 5 bit 7 | 插枪后保持、拔枪后恢复的连接周期相关状态 | MISS | 全局 bit 47 位于 `CMPD_inputHVVoltage`（start 41, length 11, V）内，是压缩机驱动 HV 输入电压数值位，不是连接周期状态。 |
| 31 | `0x228` | byte 3 bits 0:1 | 插枪／拔枪相关离散值变化 | MISS | bits 24–25 位于 `EPBR_csmFaultReason`（start 21, length 5）内，属于右侧电子驻车制动故障原因，不是插枪/拔枪状态。 |
| 32 | `0x228` | byte 5 bit 7 | 插枪／拔枪相关状态变化 | MISS | 全局 bit 47 位于 `EPBR_12VFilt`（start 37, length 12, V）内，是右侧电子驻车制动 12 V 滤波电压的数值位。 |
| 33 | `0x288` | byte 3 bits 0:1 | 插枪／拔枪相关离散值变化 | MISS | bits 24–25 位于 `EPBL_csmFaultReason`（start 21, length 5）内，属于左侧电子驻车制动故障原因。 |
| 34 | `0x288` | byte 5 bit 7 | 插枪／拔枪相关状态变化 | MISS | 全局 bit 47 位于 `EPBL_12VFilt`（start 37, length 12, V）内，是左侧电子驻车制动 12 V 滤波电压的数值位。 |
| 35 | `0x25D` | byte 1 bit 7 | 插枪后保持、拔枪后恢复的连接周期相关状态 | PARTIAL | 全局 bit 15 位于 `CP_chargeCableState`（start 14, length 2）内，位置和连接周期功能明确对应；但 Yi 只提交完整 2-bit Signal 的一个 bit，故判 PARTIAL。另有第三方 DBC 将同 ID 定义为不同 DAS message，不用于提高结论。 |
| 36 | `0x25D` | byte 5 bit 0 | 充电建立后保持、拔枪后恢复的会话相关状态 | MISS | 全局 bit 40 位于 `CP_UHF_controlState`（start 38, length 4）内，是 UHF 控制状态，不是充电会话状态。 |
| 37 | `0x333` | byte 1 | 充电、停止仍连接及拔枪过渡相关低频阶段值 | PARTIAL | byte 1 的 bits 8–14 对应 `UI_acChargeCurrentLimit`（start 8, length 7, A），bit 15 未覆盖。它与充电明确相关，但 Yi 的整 byte 边界更宽，且电流限值不是完整阶段状态。 |
| 38 | `0x333` | byte 3 bit 7 | 解锁操作附近短脉冲 | MISS | ONYX/`tesla_model3.dbc` 未覆盖该位；`Model3CAN.dbc` 将精确 bit 31 定义在 `UI_socSnapshotExpirationTime`（start 28, length 4, weeks）内。已有 field 定义与解锁脉冲明显不符。 |
| 39 | `0x49D` | byte 6 bit 5 | 充电建立后保持、拔枪后恢复的会话相关状态 | UNKNOWN | 查询的现有 DBC 未覆盖 `0x49D`，无法判断该 field。 |

原表统计：总点位数 39；field-level 点位数 39；message-level 点位数 0。

## 最终计分

- Total: 39
- HIT: 3
- PARTIAL: 10
- MISS: 15
- UNKNOWN: 11

