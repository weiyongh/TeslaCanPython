# Challenge 001 — Py DBC 镜像应答（裁判私有）

> 保密范围：本文件包含 TeslaCanPython 既有 DBC / Signal 定义，不得提供给 TeslaCanYi。
>
> 检查边界：仅对 `input/input/challenge/challenge001_yi_hit_points.md` 的 18 个冻结点位进行镜像查询；未读取 TeslaCanYi、ASC、Yi 分析程序或中间产物，未执行新的 CAN Reverse。

| # | CAN ID | Field | Yi Claim | Py DBC Result | Private DBC Evidence |
| -: | :----- | :---- | :------- | :------------ | :------------------- |
| 1 | `0x21D` | byte 0 | 完整周期阶段相关离散状态变化 | HIT | `CP_evseStatus` 的 byte 0 明确定义 `CP_evseAccept`、`CP_evseRequest`、`CP_lineVoltageRequested`、`CP_proximity`、`CP_pilot`（不同 DBC 版本的个别起始 bit 有差异）。该字节整体就是 EVSE 请求、邻近与导引状态，位置及周期阶段功能关联明确吻合。 |
| 2 | `0x21D` | byte 2 | 完整周期阶段相关离散状态变化 | PARTIAL | byte 2 只有 bits 16–18 被定义为 `CP_cableType`，其余位未覆盖。它与连接/线缆类别明确相关，但不能完整支持“完整周期阶段状态”这一更宽 Claim。 |
| 3 | `0x21D` | byte 4 | 充电建立后变化，停止后仍保持，拔枪后恢复 | HIT | byte 4 定义为 `CP_digitalCommsAttempts`、`CP_teslaSwcanState`、`CP_digitalCommsEstablished`、`CP_evseChargeType`/`CP_evseChargeType_UI`，完整覆盖该字节；数字通信建立及 EVSE 类型与所述建立—停止保持—断开恢复关系明显吻合。 |
| 4 | `0x21D` | byte 6 | 未连接／已连接未充／充电相关分层状态变化 | PARTIAL | 现有定义存在版本差异：`tesla_model3.dbc`/ONYX 将 byte 6 定义为 `CP_gbState` 与 `CP_gbdcStopChargeReason`；`Model3CAN.dbc` 在 byte 6 还覆盖 `CP_acChargeState`（start 53, length 3），同时混有 GB DC 原因/计数字段。存在充电状态对应关系，但无法把整字节稳定判成 Claim 所述完整分层状态。 |
| 5 | `0x43D` | message-level | 小门、插枪、充电建立、停止及拔枪附近的阶段相关变化 | PARTIAL | `ID43DCP_chargeStatusLog` 定义 `CP_hvChargeStatus_log`、`CP_chargeShutdownRequest_log`、AC/DC 电流限值、绝缘/预充要求及 `CP_evseChargeType_log`。充电建立、停止和 EVSE 类型关联明确，但 DBC 未明确覆盖“小门”及 Claim 的全部阶段。 |
| 6 | `0x264` | byte 0:1，little-endian 观察 | 充电建立／退出相关连续量 | PARTIAL | `PCS_chgLineStatus` 中 `PCS_chgInputVoltage`/`ChargeLineVoltage264` 为 start 0, length 14；紧接的 `PCS_chgLineCurrent`/`ChargeLineCurrent264` 从 bit 14 开始。byte 0:1 的 16-bit 观察跨越电压字段和电流字段前 2 bit，连续量及充电关联成立，但边界不是单一完整 Signal。 |
| 7 | `0x264` | byte 2:3，little-endian 观察 | 充电建立／退出相关连续量 | PARTIAL | byte 2:3 同时覆盖 `PCS_chgLineCurrent`（start 14, length 9）的后部和 `PCS_chgInputPower`（start 24, length 8）。两者都是充电线路连续量，但 Yi 的 16-bit 位置跨两个 Signal，不能作为一个完整 field 判 HIT。 |
| 8 | `0x204` | message-level | 充电建立／退出相关多级变化 | HIT | `PCS_chgStatus` 明确定义 `PCS_chgMainState`、`PCS_chargeStatus`/`PCS_hvChargeStatus`、相线使能、可用 AC 功率、各相电流请求及 PWM/Shutdown Request；message 语义与多级充电建立/退出明确吻合。 |
| 9 | `0x212` | byte 2 | 停止过程相关阶梯衰减量 | PARTIAL | byte 2 同时覆盖 `BMS_hvState`（start 16, length 3）与 `BMS_isolationResistance`（start 19, length 10）的低位部分。停止过程与 HV 状态存在明确关系，但该字节不是一个完整“阶梯衰减量”字段，且跨离散状态和连续量。 |
| 10 | `0x212` | message-level | 充电建立／退出相关状态组合变化 | HIT | `BMS_status` 包含 `BMS_contactorState`、`BMS_uiChargeStatus`/`BMS_userChargeStatus`、`BMS_hvState`、`BMS_chargeRequest`、`BMS_state`、`BMS_chgPowerAvailable` 与 `BMS_pcsPwmEnabled`，明确属于充电建立/退出时的组合状态。 |
| 11 | `0x252` | message-level | 充电建立／退出相关阶跃及连续变化 | UNKNOWN | `BMS_powerAvailable` 定义最大回收/放电功率、驻车加热功率、功率限制状态与 HVAC 功率预算。DBC 能说明它是功率能力 message，但没有足够定义把其变化可靠归因于充电建立/退出；缺少答案不判 MISS。 |
| 12 | `0x2D2` | message-level | 充电建立／退出相关阶跃变化 | PARTIAL | `BMS_driveLimits`/`ID2D2BMSVAlimits` 包含最小/最大母线电压、`BMS_maxChargeCurrent`/`MaxChargeCurrent2D2` 和最大放电电流。最大充电电流与 Claim 有明确部分对应，但整个 message 的范围更宽，DBC 本身也不证明全部阶跃均由充电建立/退出导致。 |
| 13 | `0x24A` | byte 0 | 充电建立完成／退出附近的低频离散状态变化 | MISS | `DAS_visualDebug`/`ID24ADAS_visualDebug` 的 byte 0 已定义为 Autosteer 视觉使用字段（`DAS_autosteerVehiclesUsage`、`DAS_autosteerHPPUsage`），与充电建立/退出功能明显无关。 |
| 14 | `0x2EC` | byte 0 | 插枪后保持、拔枪后恢复的连接周期相关变化 | UNKNOWN | 查询的现有 DBC 未覆盖 `0x2EC`，无法判断该字节；DBC 无答案不等于 Yi 打错。 |
| 15 | `0x2E8` | byte 5 | 插枪后保持、拔枪后恢复的连接周期相关变化 | MISS | Model 3 定义中 `EPBR_status` 的 byte 5 覆盖 `EPBR_winchModeTimer`、`EPBR_espPowerRequest`、`EPBR_okToPark`；另两份现有 DBC 将同一 ID/byte 定义为 `UI_csaRoadCurvCounter`。虽来源间 message 定义冲突，但所有已定义语义都与插枪连接周期明显无关。 |
| 16 | `0x2A8` | byte 5 | 插枪后保持、拔枪后恢复的连接周期相关变化 | MISS | `CMPD_state` 的 byte 5 跨 `CMPD_inputHVCurrent`（start 32, length 9）和 `CMPD_inputHVVoltage`（start 41, length 11），属于压缩机驱动高压输入量，不是连接周期状态 field。 |
| 17 | `0x333` | byte 3 bit 7 | 解锁操作附近短脉冲 | MISS | ONYX/`tesla_model3.dbc` 对 bit 31 未定义；但 `Model3CAN.dbc` 将该精确位置定义为 `UI_socSnapshotExpirationTime`（start 28, length 4）的最高位。已有明确 field 定义与“解锁短脉冲”不符，因此按精确 field 判 MISS。 |
| 18 | `0x49D` | byte 6 | 充电建立后保持、拔枪附近恢复的周期相关变化 | UNKNOWN | 查询的现有 DBC 未覆盖 `0x49D`，无法判断该字节；DBC 无答案不等于 Yi 打错。 |

## 计分

- Total: 18
- HIT: 4
- PARTIAL: 7
- MISS: 4
- UNKNOWN: 3

