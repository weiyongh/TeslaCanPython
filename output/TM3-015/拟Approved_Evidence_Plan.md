# TM3-015 拟 Approved Evidence Plan

状态：`PROPOSED_APPROVED / BLOCKED_BY_NEW_PENDING_REVIEW`。本文件用于预览，不是正式Approved Plan；不存在 `evidence_plan_approved.csv`，不得启动ASC分析。

## Control Relationship View

边界外事件轴：

`人工开充电口 → 人工插枪 → 扫码/付款/平台处理 → 桩端接受启动 → 人工/平台停止 → 桩端确认停止 → 人工拔枪`

车辆内部可观测主链：

`连接检测/锁止 → 可见通信/协商 → 整车状态 + 电池状态 + 安全条件 → 车辆充电条件判断/许可 → 高压直流充电状态 → 直流电流建立`

时间对应规则：只建立“外部实际事件 → 车辆可观测响应”的对应关系，不把扫码、付款或平台接受写成车辆内部控制节点。

停止观察链：

`外部实际停止时刻 → 两个车辆侧停止/关断候选状态 → 充电状态退出 → 直流输出电流退出 → 锁止释放`

热管理副线（待审，尚未进入本拟Approved）：

`Pack热状态 → 充电能力条件 → BMS热管理请求/目标 → 执行器反馈 → 温度响应`

## 第一轮审核后拟纳入项

| 顺序 | Signal | 中文语义 | 有效角色 | 有效优先级 | 有效报告位置 | 审核来源 |
| ---: | --- | --- | --- | --- | --- | --- |
| 10 | `CP_chargeDoorOpen` | 充电口盖开启状态候选 | 外部动作反馈 | P1 | 核心时间线/Signal表 | ACCEPT |
| 20 | `CP_chargeCablePresent` | 充电线缆存在状态候选 | 连接状态 | P0 | 核心时间线/Signal表 | ACCEPT |
| 30 | `CP_chargeCableSecured` | 线缆固定状态候选 | 安全状态门 | P0 | 核心时间线/Signal表 | ACCEPT |
| 40 | `CP_latchState` | 枪锁机构状态候选 | 安全状态门 | P0 | 核心时间线/Signal表 | ACCEPT |
| 50 | `CP_evseChargeType` | EVSE充电类型候选 | 连接类型状态 | P0 | 核心时间线/Signal表 | ACCEPT |
| 60 | `CP_digitalCommsEstablished` | 数字通信建立候选 | 协商状态 | P0 | 核心时间线/Signal表 | ACCEPT |
| 70 | `CP_evseRequest` | EVSE请求候选（主体待验证） | 请求候选 | P1 | 核心时间线/专项表 | OVERRIDE |
| 80 | `CP_evseAccept` | EVSE接受候选（不等同平台接受） | 许可反馈候选 | P1 | 核心时间线/专项表 | OVERRIDE |
| 90 | `CP_gbState` | 国标直流状态机候选 | 专项状态机候选 | P1 | 时间线/专项表/事件窗 | OVERRIDE |
| 100 | `CP_hvChargeStatus` | 车辆侧高压充电状态候选 | 充电许可/状态 | P0 | 核心时间线/Signal表 | ACCEPT |
| 110 | `CP_chargeShutdownRequest` | 充电关断请求候选 | 专项停止请求候选 | P1 | 专项表/事件窗 | OVERRIDE |
| 120 | `CP_stopChargeRequest` | 停止充电请求候选 | 专项停止请求候选 | P1 | 专项表/事件窗 | OVERRIDE |
| 130 | `BMS_chargeRequest` | BMS充电请求状态候选 | 车辆充电请求 | P0 | 核心时间线/Signal表 | ACCEPT |
| 140 | `BMS_uiChargeStatus` | BMS显示充电状态候选 | 车辆状态反馈 | P0 | 核心时间线/Signal表 | ACCEPT |
| 150 | `BMS_hvState` | BMS高压系统状态候选 | 高压状态门 | P0 | 核心时间线/Signal表 | ACCEPT |
| 160 | `BMS_contactorState` | Pack主接触器状态候选 | 安全状态门 | P1 | 核心时间线/Signal表 | ACCEPT |
| 170 | `CP_evseOutputDcCurrent` | EVSE直流输出电流候选 | 执行反馈 | P0 | 时间线/Signal表/事件窗 | ACCEPT |
| 180 | `CP_evseOutputDcVoltage` | EVSE直流输出电压候选 | 能源交叉验证 | P1 | 时间线/Signal表/事件窗 | OVERRIDE |
| 190 | CP侧同帧功率 | CP电压×电流派生功率 | 能源交叉验证 | P1 | 时间线/事件窗 | ACCEPT |
| 200 | `BMS_packVoltage` | Pack端电压 | 能源交叉验证 | P1 | 时间线/Signal表/事件窗 | OVERRIDE |
| 210 | `BMS_packCurrent` | Pack净电流 | 能源响应 | P0 | 时间线/Signal表/事件窗 | ACCEPT |
| 220 | Pack同帧功率 | Pack电压×电流派生功率 | 能源交叉验证 | P1 | 时间线/事件窗 | ACCEPT |
| 230 | `BMS_chgPowerAvailable` | BMS可用充电功率候选（非请求/实际） | 能力背景 | P1 | 能力摘要/Signal表 | ACCEPT |
| 240 | `BMS_socUI` | 车辆显示SOC | 状态条件 | P2 | 条件摘要/Signal表 | ACCEPT |
| 250 | `BMS_minPackTemperature` | Pack最低温度候选 | 状态条件 | P2 | 条件摘要/Signal表 | ACCEPT |
| 260 | `PCS_dcdcLvBusVolt` | DCDC低压母线电压候选 | 状态条件 | P2 | 条件摘要/Signal表 | ACCEPT |
| 270 | `CP_numAlertsSet` | CP告警数量候选 | 异常分支筛查 | P3 | 专项表/审计 | ACCEPT |

## 已排除项

`CP_evseInstantDcCurrentLimit`、`CP_evseMaxDcCurrentLimit`、`CP_evseInstantDcPowerLimit`：从Approved核心证据排除，仅允许进入DBC版本适配/工程审计，不得进入诊断结论。

## 尚未进入拟Approved的新增项

- 整车状态门：`DI_gear`、`DI_systemState`；
- 热管理候选：27项，详见热管理待审表。

待上述新增项完成第二轮审核后，才能生成正式 `evidence_plan_approved.csv`，范围固定为 `THIS_EXPERIMENT_ONLY`。
