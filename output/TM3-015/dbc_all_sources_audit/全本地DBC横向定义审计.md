# TM3-015 全本地DBC横向定义审计

- 扫描DBC：10份；成功加载10份；失败0份。
- Approved原生Signal：56个；找到精确定义147条。
- 存在两个及以上不同定义指纹的Approved Signal：24个。
- 在本ASC确有报文、名称与充电/热管理相关但未进入Approved的额外Signal：434个（822条跨DBC定义）。

## 各DBC命中Approved Signal

| DBC | 定义条数 |
| --- | ---: |
| `dbc/Model3CAN.dbc` | 43 |
| `dbc/tesla_can (1).dbc` | 2 |
| `dbc/tesla_can.dbc` | 2 |
| `dbc/tesla_model3.dbc` | 40 |
| `dbc/tesla_model3_party.dbc` | 2 |
| `dbc/tesla_model3_vehicle.dbc` | 2 |
| `dbc/tesla_powertrain.dbc` | 2 |
| `input/tesla_model3_ONYX.dbc` | 54 |

## 定义冲突

| Signal | 定义变体 | 来源定义数 |
| --- | ---: | ---: |
| `BMS_chgPowerAvailable` | 2 | 3 |
| `BMS_inletActiveCoolTargetT` | 2 | 2 |
| `BMS_inletActiveHeatTargetT` | 2 | 2 |
| `BMS_packCurrent` | 2 | 2 |
| `BMS_uiChargeStatus` | 2 | 3 |
| `CP_chargeCablePresent` | 2 | 3 |
| `CP_chargeCableSecured` | 2 | 3 |
| `CP_chargeDoorOpen` | 2 | 3 |
| `CP_chargeShutdownRequest` | 2 | 3 |
| `CP_evseChargeType` | 2 | 4 |
| `CP_gbState` | 2 | 3 |
| `CP_hvChargeStatus` | 2 | 3 |
| `CP_latchState` | 2 | 3 |
| `CP_numAlertsSet` | 2 | 3 |
| `CP_pinTemperature1` | 2 | 3 |
| `CP_pinTemperature2` | 2 | 3 |
| `CP_pinTemperature3` | 2 | 3 |
| `DI_gear` | 3 | 8 |
| `DI_systemState` | 3 | 8 |
| `PCS_dcdcLvBusVolt` | 2 | 3 |
| `VCFRONT_compressorState` | 2 | 3 |
| `VCFRONT_pumpBatteryRPMActual` | 2 | 3 |
| `VCFRONT_pumpBatteryRPMTarget` | 2 | 2 |
| `VCFRONT_tempCoolantBatInlet` | 2 | 3 |

完整位段、缩放、偏置、符号、单位及复用定义见`approved_signal_definition_comparison.csv`。冲突只说明字典版本不一致，不自动说明车辆异常。

## 额外候选边界

额外候选只因名称相关且本ASC中存在对应CAN ID而列出，未经过控制树角色审核，不进入TM3-015既有Assessment或结论。完整列表见`additional_relevant_candidates_with_asc_frames.csv`。
