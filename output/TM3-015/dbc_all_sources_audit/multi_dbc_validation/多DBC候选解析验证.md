# TM3-015 多DBC候选解析验证

本输出仅扩大候选命中与语义验证范围，不修改既有Approved Evidence Plan。

- 扫描DBC：10份。
- 相关定义解析结果：911条。
- ONYX无同名Signal的定义：77条。
- 聚焦高价值候选：210条；其中动态103条，关键事件±2秒存在转换71条。

## 有事件近邻转换的聚焦候选

| Signal | CAN ID | DBC | ONYX同名 | 事件近邻转换 |
| --- | --- | --- | --- | --- |
| `HVP_fcContPositiveAuxOpen` | 0x20A | `dbc/Model3CAN.dbc` | NO | stop:246.848=1;current_zero:246.848=1;ui_exit:246.848=1 |
| `HVP_fcContNegativeAuxOpen` | 0x20A | `dbc/Model3CAN.dbc` | NO | stop:246.848=1;current_zero:246.848=1;ui_exit:246.848=1 |
| `HVP_fcContNegativeState` | 0x20A | `dbc/Model3CAN.dbc` | YES | stop:246.848=1;current_zero:246.848=1;ui_exit:246.848=1 |
| `HVP_fcContPositiveState` | 0x20A | `dbc/Model3CAN.dbc` | YES | stop:246.848=1;current_zero:246.848=1;ui_exit:246.848=1 |
| `HVP_fcContactorSetState` | 0x20A | `dbc/Model3CAN.dbc` | YES | stop:246.848=1;current_zero:246.848=1;ui_exit:246.848=1 |
| `HVP_fcCtrsClosingAllowed` | 0x20A | `dbc/Model3CAN.dbc` | YES | stop:246.848=0;current_zero:246.848=0;ui_exit:246.848=0 |
| `HVP_fcLinkAllowedToEnergize` | 0x20A | `dbc/Model3CAN.dbc` | NO | ui_charge:115.845=2;stop:246.848=0;current_zero:246.848=0;ui_exit:246.848=0 |
| `BMS_fcContactorRequest` | 0x232 | `dbc/Model3CAN.dbc` | NO | stop:246.518=2;current_zero:246.518=2;ui_exit:246.518=2 |
| `CP_chargeDoorOpenUI` | 0x25D | `dbc/Model3CAN.dbc` | YES | ui_charge:115.423=1;dc_voltage:140.125=1;dc_current:145.126=0;stop:245.933=0;current_zero:246.232=0;ui_exit:246.432=0 |
| `CP_evseOutputDcCurrentStale` | 0x29D | `dbc/Model3CAN.dbc` | YES | dc_voltage:140.028=0 |
| `VCFRONT_bmsHvChargeEnable` | 0x3A1 | `dbc/Model3CAN.dbc` | YES | ui_charge:115.410=0;dc_voltage:140.011=0;dc_current:145.011=0;stop:245.717=0;current_zero:246.217=0;ui_exit:246.417=0 |
| `BMS_isolationResistance` | 0x212 | `dbc/Model3CAN.dbc` | YES | dc_current:145.089=90;stop:245.893=380;current_zero:246.191=250;ui_exit:246.393=190 |
| `CP_hvChargeStatus_log` | 0x43D | `dbc/Model3CAN.dbc` | NO | ui_charge:115.328=2;dc_voltage:139.525=5;stop:246.233=1;current_zero:246.233=1;ui_exit:246.233=1 |
| `UI_chargeEnableRequest` | 0x333 | `dbc/Model3CAN.dbc` | YES | stop:245.656=0;current_zero:245.656=0;ui_exit:245.656=0 |
| `TotalChargeKWh3D2` | 0x3D2 | `dbc/Model3CAN.dbc` | NO | dc_current:144.851=14620.364;stop:245.851=14622.296;current_zero:245.851=14622.296;ui_exit:245.851=14622.296 |
| `BMS_kwhDcChargeTotalModule3` | 0x3F2 | `dbc/Model3CAN.dbc` | NO | stop:243.851=993.335 |
| `BMS_kwhDcChargeTotalModule2` | 0x3F2 | `dbc/Model3CAN.dbc` | NO | dc_current:145.851=992.527 |
| `BMS_kwhDcChargeTotalModule4` | 0x3F2 | `dbc/Model3CAN.dbc` | NO | stop:245.852=885.965;current_zero:245.852=885.965;ui_exit:245.852=885.965 |
| `BMS_kwhDcChargeTotalModule1` | 0x3F2 | `dbc/Model3CAN.dbc` | NO | dc_current:143.851=885.7470000000001 |
| `FC_statusCode` | 0x214 | `dbc/Model3CAN.dbc` | YES | ui_charge:115.328=6;stop:245.836=0;current_zero:245.836=0;ui_exit:245.836=0 |
| `FC_dcCurrent` | 0x214 | `dbc/Model3CAN.dbc` | YES | dc_current:145.030=54.492196799999995;stop:246.236=0.0;current_zero:246.236=0.0;ui_exit:246.236=0.0 |
| `FC_dcVoltage` | 0x214 | `dbc/Model3CAN.dbc` | YES | dc_voltage:140.030=346.87505919999995;dc_current:144.030=349.29205179999997;stop:246.236=0.0;current_zero:246.236=0.0;ui_exit:246.236=0.0 |
| `BMS_maxChargeCurrent` | 0x2D2 | `dbc/tesla_model3.dbc` | YES | ui_charge:115.392=250.0;stop:246.393=0.0;current_zero:246.393=0.0;ui_exit:246.393=0.0 |
| `BMS_isolationResistance` | 0x212 | `dbc/tesla_model3.dbc` | YES | dc_current:145.089=90;stop:245.893=380;current_zero:246.191=250;ui_exit:246.393=190 |
| `CP_pilot` | 0x21D | `dbc/tesla_model3.dbc` | YES | ui_charge:115.323=4 |
| `CP_vehiclePrechargeRequired` | 0x21D | `dbc/tesla_model3.dbc` | YES | stop:245.734=1;current_zero:245.734=1;ui_exit:245.734=1 |
| `FC_powerLimit` | 0x244 | `dbc/tesla_model3.dbc` | YES | dc_voltage:139.428=10.4589912;dc_current:145.029=31.5637413;stop:245.634=98.73785740000001;current_zero:246.134=95.6250624;ui_exit:246.334=0.0 |
| `FC_currentLimit` | 0x244 | `dbc/tesla_model3.dbc` | YES | dc_current:145.029=89.9414216;stop:246.234=270.62992899999995;current_zero:246.234=270.62992899999995;ui_exit:246.334=0.0 |
| `FC_maxPowerLimit` | 0x541 | `dbc/tesla_model3.dbc` | YES | stop:246.234=0.0;current_zero:246.234=0.0;ui_exit:246.234=0.0 |
| `FC_maxCurrentLimit` | 0x541 | `dbc/tesla_model3.dbc` | YES | stop:246.234=0.0;current_zero:246.234=0.0;ui_exit:246.234=0.0 |
| `FC_statusCode` | 0x214 | `dbc/tesla_model3.dbc` | YES | ui_charge:115.328=6;stop:245.836=0;current_zero:245.836=0;ui_exit:245.836=0 |
| `FC_dcCurrent` | 0x214 | `dbc/tesla_model3.dbc` | YES | dc_current:145.030=54.492196799999995;stop:246.236=0.0;current_zero:246.236=0.0;ui_exit:246.236=0.0 |
| `FC_dcVoltage` | 0x214 | `dbc/tesla_model3.dbc` | YES | dc_voltage:140.030=346.87505919999995;dc_current:144.030=349.29205179999997;stop:246.236=0.0;current_zero:246.236=0.0;ui_exit:246.236=0.0 |
| `HVP_fcContNegativeState` | 0x20A | `dbc/tesla_model3.dbc` | YES | stop:246.848=1;current_zero:246.848=1;ui_exit:246.848=1 |
| `HVP_fcContPositiveState` | 0x20A | `dbc/tesla_model3.dbc` | YES | stop:246.848=1;current_zero:246.848=1;ui_exit:246.848=1 |
| `HVP_fcContactorSetState` | 0x20A | `dbc/tesla_model3.dbc` | YES | stop:246.848=1;current_zero:246.848=1;ui_exit:246.848=1 |
| `HVP_fcCtrsClosingAllowed` | 0x20A | `dbc/tesla_model3.dbc` | YES | stop:246.848=0;current_zero:246.848=0;ui_exit:246.848=0 |
| `HVP_packContVoltage` | 0x7AA | `dbc/tesla_model3.dbc` | YES | dc_voltage:140.307=12.600000000000001;dc_current:145.307=13.0;stop:244.309=13.100000000000001;current_zero:247.309=13.200000000000001;ui_exit:247.309=13.200000000000001 |
| `HVP_fcContCoilCurrent` | 0x7AA | `dbc/tesla_model3.dbc` | YES | dc_voltage:140.467=0.6000000000000001;dc_current:143.468=0.4;stop:246.470=0.0;current_zero:246.470=0.0;ui_exit:246.470=0.0 |
| `HVP_fcContVoltage` | 0x7AA | `dbc/tesla_model3.dbc` | YES | dc_voltage:139.468=12.4;dc_current:146.468=12.9;stop:246.470=13.100000000000001;current_zero:246.470=13.100000000000001;ui_exit:246.470=13.100000000000001 |
| `HVP_packContCoilCurrent` | 0x7AA | `dbc/tesla_model3.dbc` | YES | dc_voltage:138.537=1.3;dc_current:146.537=1.2000000000000002 |
| `HVP_fcLinkVoltage` | 0x7AA | `dbc/tesla_model3.dbc` | YES | ui_charge:116.236=0.0;dc_voltage:140.237=347.90000000000003;dc_current:145.237=351.1;stop:245.242=364.90000000000003;current_zero:246.242=353.5;ui_exit:246.242=353.5 |
| `HVP_fcLinkNegativeV` | 0x7AA | `dbc/tesla_model3.dbc` | YES | ui_charge:116.387=0.5;dc_voltage:140.388=-173.0;dc_current:145.391=-175.0;stop:245.390=-174.70000000000002;current_zero:246.390=1.1;ui_exit:246.390=1.1 |
| `UI_chargeEnableRequest` | 0x333 | `dbc/tesla_model3.dbc` | YES | stop:245.656=0;current_zero:245.656=0;ui_exit:245.656=0 |
| `VCFRONT_bmsHvChargeEnable` | 0x3A1 | `dbc/tesla_model3.dbc` | YES | ui_charge:115.410=0;dc_voltage:140.011=0;dc_current:145.011=0;stop:245.717=0;current_zero:246.217=0;ui_exit:246.417=0 |
| `BMS_maxChargeCurrent` | 0x2D2 | `input/tesla_model3_ONYX.dbc` | YES | ui_charge:115.392=250.0;stop:246.393=0.0;current_zero:246.393=0.0;ui_exit:246.393=0.0 |
| `BMS_isolationResistance` | 0x212 | `input/tesla_model3_ONYX.dbc` | YES | dc_current:145.089=90;stop:245.893=380;current_zero:246.191=250;ui_exit:246.393=190 |
| `BMS_packTMin` | 0x312 | `input/tesla_model3_ONYX.dbc` | YES | ui_charge:115.493=-23.0;dc_voltage:139.991=67.25;dc_current:144.991=67.25;stop:245.494=-16.75;current_zero:245.993=68.5;ui_exit:246.494=-23.0 |
| `BMS_packTMax` | 0x312 | `input/tesla_model3_ONYX.dbc` | YES | ui_charge:115.994=15.0;dc_voltage:139.991=15.0;dc_current:144.991=15.0;stop:245.494=-20.75;current_zero:245.993=15.0;ui_exit:246.494=-25.0 |
| `CP_pilot` | 0x21D | `input/tesla_model3_ONYX.dbc` | YES | ui_charge:115.323=4 |
| `CP_vehiclePrechargeRequired` | 0x21D | `input/tesla_model3_ONYX.dbc` | YES | stop:245.734=1;current_zero:245.734=1;ui_exit:245.734=1 |
| `CP_chargeDoorOpenUI` | 0x25D | `input/tesla_model3_ONYX.dbc` | YES | ui_charge:115.423=1;dc_voltage:140.125=1;dc_current:145.126=0;stop:245.933=0;current_zero:246.232=0;ui_exit:246.432=0 |
| `CP_evseOutputDcCurrentStale` | 0x29D | `input/tesla_model3_ONYX.dbc` | YES | dc_voltage:140.028=0 |
| `FC_powerLimit` | 0x244 | `input/tesla_model3_ONYX.dbc` | YES | dc_voltage:139.428=10.4589912;dc_current:145.029=31.5637413;stop:245.634=98.73785740000001;current_zero:246.134=95.6250624;ui_exit:246.334=0.0 |
| `FC_currentLimit` | 0x244 | `input/tesla_model3_ONYX.dbc` | YES | dc_current:145.029=89.9414216;stop:246.234=270.62992899999995;current_zero:246.234=270.62992899999995;ui_exit:246.334=0.0 |
| `FC_maxPowerLimit` | 0x541 | `input/tesla_model3_ONYX.dbc` | YES | stop:246.234=0.0;current_zero:246.234=0.0;ui_exit:246.234=0.0 |
| `FC_maxCurrentLimit` | 0x541 | `input/tesla_model3_ONYX.dbc` | YES | stop:246.234=0.0;current_zero:246.234=0.0;ui_exit:246.234=0.0 |
| `FC_statusCode` | 0x214 | `input/tesla_model3_ONYX.dbc` | YES | ui_charge:115.328=6;stop:245.836=0;current_zero:245.836=0;ui_exit:245.836=0 |
| `FC_dcCurrent` | 0x214 | `input/tesla_model3_ONYX.dbc` | YES | dc_current:145.030=54.492196799999995;stop:246.236=0.0;current_zero:246.236=0.0;ui_exit:246.236=0.0 |
| `FC_dcVoltage` | 0x214 | `input/tesla_model3_ONYX.dbc` | YES | dc_voltage:140.030=346.87505919999995;dc_current:144.030=349.29205179999997;stop:246.236=0.0;current_zero:246.236=0.0;ui_exit:246.236=0.0 |
| `HVP_fcContNegativeState` | 0x20A | `input/tesla_model3_ONYX.dbc` | YES | stop:246.848=1;current_zero:246.848=1;ui_exit:246.848=1 |
| `HVP_fcContPositiveState` | 0x20A | `input/tesla_model3_ONYX.dbc` | YES | stop:246.848=1;current_zero:246.848=1;ui_exit:246.848=1 |
| `HVP_fcContactorSetState` | 0x20A | `input/tesla_model3_ONYX.dbc` | YES | stop:246.848=1;current_zero:246.848=1;ui_exit:246.848=1 |
| `HVP_fcCtrsClosingAllowed` | 0x20A | `input/tesla_model3_ONYX.dbc` | YES | stop:246.848=0;current_zero:246.848=0;ui_exit:246.848=0 |
| `HVP_fcContCoilCurrent` | 0x7AA | `input/tesla_model3_ONYX.dbc` | YES | dc_voltage:140.467=0.6000000000000001;dc_current:143.468=0.4;stop:246.470=0.0;current_zero:246.470=0.0;ui_exit:246.470=0.0 |
| `HVP_packContVoltage` | 0x7AA | `input/tesla_model3_ONYX.dbc` | YES | dc_voltage:140.307=12.600000000000001;dc_current:145.307=13.0;stop:244.309=13.100000000000001;current_zero:247.309=13.200000000000001;ui_exit:247.309=13.200000000000001 |
| `HVP_fcContVoltage` | 0x7AA | `input/tesla_model3_ONYX.dbc` | YES | dc_voltage:139.468=12.4;dc_current:146.468=12.9;stop:246.470=13.100000000000001;current_zero:246.470=13.100000000000001;ui_exit:246.470=13.100000000000001 |
| `HVP_packContCoilCurrent` | 0x7AA | `input/tesla_model3_ONYX.dbc` | YES | dc_voltage:138.537=1.3;dc_current:146.537=1.2000000000000002 |
| `HVP_fcLinkNegativeV` | 0x7AA | `input/tesla_model3_ONYX.dbc` | YES | ui_charge:116.387=0.5;dc_voltage:140.388=-173.0;dc_current:145.391=-175.0;stop:245.390=-174.70000000000002;current_zero:246.390=1.1;ui_exit:246.390=1.1 |
| `HVP_fcLinkVoltage` | 0x7AA | `input/tesla_model3_ONYX.dbc` | YES | ui_charge:116.236=0.0;dc_voltage:140.237=347.90000000000003;dc_current:145.237=351.1;stop:245.242=364.90000000000003;current_zero:246.242=353.5;ui_exit:246.242=353.5 |
| `UI_chargeEnableRequest` | 0x333 | `input/tesla_model3_ONYX.dbc` | YES | stop:245.656=0;current_zero:245.656=0;ui_exit:245.656=0 |

事件近邻只用于筛选，不单独证明控制语义；需要结合状态方向、相邻节点及定义冲突人工评估。
