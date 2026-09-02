# TM3-015 JSON候选Signal人工复核

## 可直接参考的高价值候选

| Signal | CAN ID / 位段 | 中文语义（候选边界） | TM3-015表现 | 判断 |
| --- | --- | --- | --- | --- |
| `BMS_userChargeStatus` | `0x212`, bit 11, 3位 | BMS面向用户的充电阶段状态候选 | 0 DISCONNECTED → 5 STOPPED（插枪）→ 2 ABOUT_TO_CHARGE（115.392s）→ 3 CHARGING（139.589s）→ 5 STOPPED（245.793s）→ 0 DISCONNECTED（273.596s） | `SUPPORTED_AS_EXPERIMENT_CANDIDATE`；ONYX无同名定义，阶段与实测高度一致 |
| `BMS_isolationResistance` | `0x212` | Pack高压绝缘电阻候选 | 电流建立附近由0逐步升至约490，稳定段约430–450，停止后回0 | JSON与现有DBC定义一致；可作为高压安全条件/响应候选，单位和算法滤波仍需确认 |
| `BMS_hvilCoverVSense` | `0x232`, bit 32, 16位，0.001 V | BMS盖板HVIL检测电压候选 | 全程约1.246–1.249 V，未出现离散异常 | `SUPPORTED_AS_STABLE_BACKGROUND`；不能由无变化证明完整HVIL健康规则 |
| `BMS_internalHvilSenseV` | `0x232`, bit 16, 16位，0.001 V | BMS内部HVIL检测电压候选 | 全程约2.52–2.53 V | 与`Model3CAN.dbc`定义一致；仅作为稳定安全背景 |
| `HVP_fcContactorHwFault` | `0x682` | 快充接触器硬件故障标志候选 | 全程0 | 本次未观察到故障置位；不能单独用于“系统正常”判定 |
| `HVP_packContactorHwFault` | `0x682` | Pack接触器硬件故障标志候选 | 全程0 | 同上 |

## 能解释ONYX失效，但当前枚举仍不可信

`CP_gbState`是JSON最重要的DBC冲突线索：

- JSON 3.1.2和`Model3CAN.dbc`：`0x21D` bit 42、4位；
- ONYX和`tesla_model3.dbc`：`0x21D` bit 48、5位。

ONYX定义在本次数据中恒为0；JSON定义则得到0→1（132.024s）→2（139.524s）→6（245.734s）→0（273.534s），明显命中准备、运行、停止和断开边沿。但是，按JSON枚举文本，稳定充电阶段的值2表示`GBDC_COMMS_RECEIVED`，停止时的值6表示`GBDC_VEH_PACK_PRECHARGE`，状态名称与实际阶段顺序不合理。因此该定义可以说明正确位段可能在bit 42，但当前枚举/版本语义仍标记`SEMANTIC_VALIDATION_FAILED`，不得恢复为P0或用于正式协议状态结论。

## 暂不采用的候选

- `DIR_hvilCmVoltage`、`DIR_hvilCurrent`、`DIR_hvilStatus (0x279)`只在约141.5s后出现报文，数值基本稳定；可说明相关控制器在高压阶段上线，但不足以确认具体HVIL控制层级。
- `VCFRONT_tempCoolantBatInlet (0x321)`虽与JSON及部分DBC定义一致，但本次由约35°C持续升至59.6°C，随后十余秒降至约26°C再回升，物理变化速率异常；继续标记`SEMANTIC_VALIDATION_FAILED / POSSIBLE_VERSION_OR_TRANSPORT_MAPPING_MISMATCH`。
- 多个带`Index`或日志选择字段的“事件近邻变化”来自轮询/复用页切换，不是充电状态变化，不进入Evidence Plan。
- `HVP_hvilDiag`及多个HVIL状态位全程不变，只能作为覆盖或背景，不能承担事件主链。

## JSON来源边界

文件元数据为Model3版本3.1.2、`eth/caneth`总线。其`message_id`与TM3-015 ASC存在51个报文交集，说明ID具有实际参考价值；但该文件是否对应本车当前网关、软件版本和总线转发表尚未确认。采用JSON定义时必须保留`JSON_SOURCE`、版本、位段和与DBC的冲突状态。
