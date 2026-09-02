# TM3-015 热管理待审 Signal 候选表

状态：`PENDING_HUMAN_REVIEW`。以下候选来自对 `input/tesla_model3_ONYX.dbc` 的定义扫描，未读取 ASC、未检查报文覆盖、未验证复用页，也未根据名称直接升级为车型语义。

Evidence Requirement：`Pack热状态 → 充电能力条件 → BMS热管理请求/目标 → 热管理执行反馈 → 快充过程温度响应`。这是一条独立条件/响应副线，不属于直流充电许可主控制链。

| 分组 | Signal | 中文语义 | CAN ID/复用 | 角色 | 建议级别 | 置信度 | 主要边界 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pack热状态 | `BMS_modelTMax` / `BMS_modelTMin` | Pack模型最高/最低温度候选 | `0x332 m0` | Pack热状态 | P1 | MEDIUM | “model”是否对应实测温度范围待验证 |
| Pack热状态 | `BMS_minPackTemperature` | Pack最低温度候选 | `0x212` | Pack热状态 | P2 | MEDIUM | 不能代表完整温度范围；DBC冲突 |
| 接口热状态 | `CP_pinTemperature1/2/3` | 三个充电接口针脚温度候选 | `0x75D m1` | 接口热状态 | P2 | LOW | 针脚对应关系及复用覆盖待验证 |
| BMS条件/请求 | `BMS_activeHeatingWorthwhile` | BMS主动加热价值判断候选 | `0x212` | 条件/决策 | P2 | LOW | 不是执行反馈 |
| BMS请求 | `BMS_hvacPowerRequest` | BMS热管理功率请求候选 | `0x212` | 请求 | P2 | LOW | 请求内容和接收方待验证 |
| BMS请求 | `BMS_flowRequest` | 电池回路流量请求候选 | `0x312` | 请求 | P1 | MEDIUM | 物理边界待验证 |
| BMS目标 | `BMS_inletActiveCoolTargetT` / `BMS_inletActiveHeatTargetT` | 电池入口主动冷却/加热目标温度候选 | `0x312` | 目标 | P1 | MEDIUM | 不直接等同实际温度 |
| 温度反馈 | `VCFRONT_tempCoolantBatInlet` | 电池回路冷却液入口温度候选 | `0x321` | 反馈 | P1 | MEDIUM | 传感器位置含义待验证 |
| 流量目标/反馈 | `VCFRONT_coolantFlowBatTarget/Actual` | 电池回路目标/实际流量候选 | `0x241` | 目标/反馈 | P1 | MEDIUM | 需验证两者是否同一控制边界 |
| 泵目标/反馈 | `VCFRONT_pumpBatteryRPMTarget/Actual` | 电池冷却液泵目标/实际转速候选 | `0x2C1 m0` / `0x201 m0` | 目标/反馈 | P2 | LOW | 两个复用报文的可见性及对时待验证 |
| Chiller | `VCFRONT_chillerDemandActive` | Chiller需求激活候选 | `0x2E1 m3` | 决策/请求 | P2 | LOW | 复用及角色边界待验证 |
| Chiller阀 | `VCFRONT_chillerExvFlowTarget/Flow` | Chiller膨胀阀目标/实际开度候选 | `0x201 m5/m3` | 目标/反馈 | P2 | LOW | 位于不同复用页，不能假定同帧对应 |
| 压缩机 | `VCFRONT_compressorTargetDuty/Enable` | 压缩机目标占空比/使能候选 | `0x281` | 目标 | P2 | MEDIUM | 目标不等于执行 |
| 压缩机 | `VCFRONT_compressorState` | 压缩机运行状态候选 | `0x201 m2` | 反馈 | P2 | LOW | 复用覆盖和枚举待验证 |
| 冷却液阀 | `VCFRONT_coolantValveAngleTarget/Actual` | 多通阀目标/实际角度候选 | `0x2C1 m2` | 目标/反馈 | P2 | LOW | 模式与机械位置语义待验证 |
| 热管理模式 | `VCFRONT_hpMode` / `VCFRONT_hpBatteryCool` | 热泵总模式/电池冷却模式候选 | `0x381 m16/m17` | 模式 | P2 | LOW | 不同复用页且枚举语义待验证 |
| 加热反馈 | `VCFRONT_isActiveHeatingBattery` | 电池主动加热执行状态候选 | `0x2E1 m0` | 反馈 | P2 | LOW | 状态主体和复用覆盖待验证 |

建议审核顺序：先决定P1的Pack温度范围、BMS流量/温度目标、冷却液入口温度及流量目标/反馈是否进入热管理副线；P2执行器和模式字段可整体批准为专项候选，或仅保留DBC覆盖审计。
