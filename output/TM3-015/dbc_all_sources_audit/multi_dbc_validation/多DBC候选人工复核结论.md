# TM3-015 多DBC候选人工复核结论

## 范围与边界

- 本次使用`dbc/`及`input/`下10份DBC对TM3-015 ASC重新解码。
- 结果是既有Approved Evidence Plan之外的补充工程审计，不自动改变P0/P1/P2、既有Assessment或车型级Signal语义。
- “可解释”要求至少同时满足：本ASC有对应报文、位段可解、变化方向合理、关键转换能与实测充电阶段对应。单纯名称相关或数值变化不构成语义确认。

## 可补充解释的强候选

| Signal | 中文语义（候选边界） | DBC / CAN ID | 本次实测对应 | 当前判断 |
| --- | --- | --- | --- | --- |
| `HVP_fcLinkAllowedToEnergize` | 快充链路允许上电类型候选 | `Model3CAN.dbc` / `0x20A` | 115.845 s由NONE(0)变DC(2)，246.848 s回NONE；覆盖直流充电准备至退出 | `SUPPORTED_AS_EXPERIMENT_CANDIDATE` |
| `BMS_fcContactorRequest` | BMS快充接触器开闭请求候选 | `Model3CAN.dbc` / `0x232` | 134.515 s由OPEN(2)变CLOSE(1)，246.518 s回OPEN；位于直流电压建立前及电流退出后 | `SUPPORTED_AS_EXPERIMENT_CANDIDATE` |
| `HVP_fcContPositiveAuxOpen` / `HVP_fcContNegativeAuxOpen` | 快充正/负接触器辅助触点开路反馈候选 | `Model3CAN.dbc` / `0x20A` | 134.847 s由1变0，246.848 s回1；与请求及直流链路退出顺序一致 | `SUPPORTED_AS_EXPERIMENT_CANDIDATE` |
| `CP_hvChargeStatus_log` | 高压充电阶段日志状态候选 | `Model3CAN.dbc` / `0x43D` | CONNECTED→STANDBY→EVSE_TEST_ACTIVE→TEST_PASSED→ENABLED；139.525 s进入ENABLED，246.233 s退回CONNECTED | `SUPPORTED_AS_EXPERIMENT_CANDIDATE` |
| `FC_statusCode` | 快充设备/适配器状态码候选 | `Model3CAN.dbc` / `0x214` | 115.328 s 0→6，133.029 s 6→1，245.836 s回0；与准备、接触器请求及停止相邻 | `SUPPORTED_TIMING_SEMANTICS_PENDING_ENUM` |
| `TotalChargeKWh3D2` | 车辆累计充入电量计数候选 | `Model3CAN.dbc` / `0x3D2` | 电流建立后由14620.356增加至14622.296 kWh，停止后不再增加 | `SUPPORTED_AS_ENERGY_CROSS_CHECK` |
| `BMS_kwhDcChargeTotalModule*` | 模组直流充电累计量候选 | `Model3CAN.dbc` / `0x3F2` | 各模组计数在直流电流建立后持续增加，停止后收敛 | `SUPPORTED_AS_ENGINEERING_AUDIT` |

这些Signal在ONYX中没有同名定义，能够扩大当前实验的有效命中范围。其中接触器请求、辅助触点和高压充电阶段日志共同补充了原主链中“车辆充电条件判断/许可 → 高压直流充电状态”之间的部分可观测证据；仍不能据此反推出OEM完整许可算法。

## 可读且时序合理，但定量定义仍冲突

| Signal | 观察 | 边界 |
| --- | --- | --- |
| `FC_dcVoltage (0x214)` | 140.030 s由0变346.88 V，稳定段约365.48 V，246.236 s回0 | 建立/退出时序与既有直流电压一致；数值定义需与Pack电压及`CP_*`版本继续交叉验证 |
| `FC_dcCurrent (0x214)` | 145.030 s开始建立，稳定段约218.55 A，246.236 s回0 | 时序高度一致，但幅值与`BMS_packCurrent`及现有`CP_evseOutputDcCurrent`不闭合；只支持电流建立/退出，不支持定量功率结论 |
| `CP_evseMaxDcCurrentLimit`等`0x27D/0x2BD`限值 | 能随充电阶段出现并在停止时归零 | 部分数值关系不合理，且此前人工审核已限定为DBC版本适配/工程审计；维持EXCLUDE |

## 解析成功但语义验证失败或证据不足

- `CP_dcPinTemperature`、`CP_acPinTemperature`及部分`BMS_packTMin/TMax`替代定义出现约-55～149 °C跳变或复用页混杂，标记`SEMANTIC_VALIDATION_FAILED`。
- `BMS_packContactorRequest`本次基本保持CLOSE，仅在133.515～135.515 s短暂OPEN；无法单独建立其与快充主链接触器的层级关系，标记`INSUFFICIENT_EVIDENCE`。
- `BMS_internalHvilSenseV`虽可读但仅有毫伏级细小波动，没有离散安全事件，当前只作为稳定背景。
- AC充电器、宽泛热管理执行器、告警矩阵及仅按名称命中的字段未进入上述候选结论。

## 对既有结论的影响

多DBC解析显著增强了直流快充阶段状态和高压接触器链的可观测性，并证明部分ONYX缺失Signal在TM3-015数据上具有合理解释可能。它没有解决不同电流定义间的定量冲突，也没有补齐OEM内部完整充电许可逻辑。因此既有“直流电流建立、稳定和停止退出可形成条件化基线；定量功率链与完整许可链证据不足”的结论保持不变。
