# TM3-015 Model3_ETH JSON字典审计

- JSON产品/版本：`Model3` / `3.1.2`；总线：`eth`。
- JSON消息：148；Signal：375。
- 与本ASC报文ID有交集：51个消息、192个Signal定义。
- 充电/高压/热管理相关且ASC有报文：22个定义。
- 其中ONYX无同名Signal：12个；动态：7个；关键事件±2秒有转换：6个。

## ONYX缺失且有事件近邻转换的候选

| Signal | CAN ID | JSON消息 | 阶段中值 PRE/PREP/RAMP/STEADY/STOP/POST | 事件近邻 |
| --- | --- | --- | --- | --- |
| `BMS_hvilCoverVSense` | 0x232 | `BMS_contactorRequest` | 1.248 / 1.248 / 1.247 / 1.247 / 1.247 / 1.247 | ui_charge:115.515=1.247;contactor_request:134.515=1.246;dc_voltage:140.516=1.247;dc_current:145.516=1.248;stop:246.518=1.248;current_zero:246.518=1.248;contactor_open:246.518=1.248 |
| `BMS_internalHvilSenseV` | 0x232 | `BMS_contactorRequest` | 2.526 / 2.525 / 2.5275 / 2.526 / 2.527 / 2.525 | ui_charge:114.515=2.528;contactor_request:134.515=2.528;dc_voltage:140.516=2.528;dc_current:145.516=2.527;stop:245.518=2.527;current_zero:246.518=2.525;contactor_open:246.518=2.525 |
| `BMS_userChargeStatus` | 0x212 | `BMS_status` | 5 / 2 / 3 / 3 / 5 / 5 | ui_charge:115.392=2.0;dc_voltage:139.589=3.0;stop:245.793=5.0;current_zero:245.793=5.0;contactor_open:245.793=5.0 |
| `DIR_hvilCmVoltage` | 0x279 | `DIR_lvStatus` |  /  / 1.28 / 1.28 / 1.28 / 1.28 | dc_voltage:141.546=1.28 |
| `DIR_hvilCurrent` | 0x279 | `DIR_lvStatus` |  /  / 20.8 / 20.8 / 20.8 / 20.8 | dc_voltage:141.546=20.8;dc_current:145.446=20.700000000000003;stop:245.639=20.8;current_zero:245.639=20.8;contactor_open:245.639=20.8 |
| `HVP_hvilDiag` | 0x20A | `HVP_contactorState` | 1 / 1 / 1 / 1 / 1 / 1 | contactor_request:134.846=1.0 |

JSON位段可解只表示候选可读。该文件标记为ETH/caneth字典，是否与本车当前网关版本完全一致仍须由DLC、事件方向和物理闭环验证。
