# TM3-015 待审 Signal 证据表（第二轮）

状态：`DRAFT_REVISED / PARTIALLY_REVIEWED / NOT_APPROVED`。未读取或分析ASC。

## 1. 第一轮已审核结果

前述30项已形成Review Override：20项接受、7项覆盖、3项排除。候选Signal进入拟Approved不代表车型语义升级；正式分析仍必须验证DBC适配、可读性、状态方向和时序对应。

| Signal | 中文语义 | Draft | 审核后有效值 | 决定 |
| --- | --- | --- | --- | --- |
| `CP_evseRequest` | EVSE请求候选状态（主体/层级待验证） | 请求/P0 | 请求候选/P1/专项表 | OVERRIDE |
| `CP_evseAccept` | EVSE接受候选状态（不等同平台接受） | 许可反馈/P0 | 许可反馈候选/P1/专项表 | OVERRIDE |
| `CP_gbState` | 国标直流状态机候选（DBC冲突未解决） | 状态机/P0 | 专项状态机候选/P1 | OVERRIDE |
| `CP_chargeShutdownRequest` | 充电关断请求候选 | 停止请求/P0 | 专项停止请求候选/P1 | OVERRIDE |
| `CP_stopChargeRequest` | 停止充电请求候选 | 停止请求/P0 | 专项停止请求候选/P1 | OVERRIDE |
| `CP_evseOutputDcVoltage` | EVSE直流输出电压候选 | 执行反馈/P0 | 能源交叉验证/P1 | OVERRIDE |
| `BMS_packVoltage` | Pack端电压 | 能源交叉验证/P0 | 能源交叉验证/P1 | OVERRIDE |
| `CP_evseInstantDcCurrentLimit` | EVSE瞬时直流电流能力候选 | 能力背景/P2 | EXCLUDE；仅DBC/工程审计 | EXCLUDE |
| `CP_evseMaxDcCurrentLimit` | EVSE最大直流电流能力候选 | 能力背景/P2 | EXCLUDE；仅DBC/工程审计 | EXCLUDE |
| `CP_evseInstantDcPowerLimit` | EVSE瞬时直流功率能力候选 | 能力背景/P2 | EXCLUDE；仅DBC/工程审计 | EXCLUDE |

其余20项按Draft建议接受。其中：`CP_evseOutputDcCurrent`与`BMS_packCurrent`保持P0；两侧派生功率保持P1；`BMS_chgPowerAvailable`保持P1并明确Available不等于Request或Actual。

## 2. 新增整车状态门——待审

| Signal | 中文语义 | CAN ID | 角色 | 建议 | 置信度 | 不确定性 | 审核 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `DI_gear` | 挡位状态（充电许可条件背景，不代表OEM完整许可规则） | `0x118` | 整车状态条件 | P2，条件摘要/核心Signal表 | HIGH | 本次适用性及许可关系不可由单次P挡充电反推 | PENDING |
| `DI_systemState` | 电驱系统状态（是否参与充电许可待验证） | `0x118` | 整车系统状态条件 | P2，条件摘要/核心Signal表 | HIGH | 它是电驱系统状态，不自动等同整车充电许可状态 | PENDING |

建议：两项均批准为P2条件背景。若批准，正式报告只能陈述本次状态与充电过程共存，不能写成OEM充电许可充分条件。

## 3. 新增热管理副线——待审

完整候选及DBC来源见[热管理待审Signal候选表](/Users/hwy/codex_work/TeslaCanPython/output/TM3-015/热管理待审Signal候选表.md)。共27项，全部为 `PENDING_HUMAN_REVIEW`，当前不进入拟Approved核心计划。

建议优先批准为P1副线候选：

- `BMS_modelTMax`、`BMS_modelTMin`：Pack温度范围候选；
- `BMS_flowRequest`：BMS流量请求候选；
- `BMS_inletActiveCoolTargetT`、`BMS_inletActiveHeatTargetT`：入口温度目标候选；
- `VCFRONT_tempCoolantBatInlet`：电池回路冷却液入口温度候选；
- `VCFRONT_coolantFlowBatTarget`、`VCFRONT_coolantFlowBatActual`：流量目标/反馈候选。

其余泵、阀、Chiller、压缩机和热泵模式建议作为P2专项候选整体审核；它们不得仅凭名称进入控制结论。

## 4. 本轮需人工决定

1. `DI_gear`、`DI_systemState`：接受、覆盖或排除。
2. 热管理P1建议组：逐项或整体接受、覆盖或排除。
3. 热管理P2执行器/模式组：批准为专项候选、仅审计，或排除。
4. Pack功率人读符号：建议正文统一展示“充入Pack为正”，同时工程明细保留原始DBC值和换算过程；请确认。

