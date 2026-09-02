# TM3-015 Approved Evidence Plan

- 状态：`APPROVED`
- 范围：`THIS_EXPERIMENT_ONLY`
- 正式机器可读计划：`evidence_plan_approved.csv`
- 总行数：58；其中3项有效报告位置为`EXCLUDE`，仅允许DBC版本适配/工程审计。
- 主计划及热管理候选均保留“中文语义”、原语义状态、置信度、不确定性、人工决定和审核来源。
- 进入Approved不代表候选Signal升级为车型已确认语义；实际不可读、复用页不成立或方向不符时，Assessment使用`INSUFFICIENT_EVIDENCE / SEMANTIC_VALIDATION_FAILED`。

## 车辆内部可观测主链

`连接检测/锁止 → 可见通信/协商 → 整车状态 + 电池状态 + 安全条件 → 车辆充电条件判断/许可 → 高压直流充电状态 → 直流电流建立`

外部扫码、付款、平台接受、停止入口和拔枪只作为外部事件轴，与车辆可观测响应进行时间对应，不视为车辆内部控制节点。

## 独立副线

- 能源：CP侧电压/电流/派生功率 ↔ Pack电压/电流/同帧派生功率。
- 热管理：Pack热状态 → 充电能力条件 → BMS请求/目标 → 执行器候选反馈 → 温度响应。
- 充电接口热状态：`CP_pinTemperature1/2/3`独立于Pack热管理副线。

## 人读符号

正文统一“充入Pack为正”。原始ASC/DBC值、原始符号和转换过程保留工程审计，原始文件不修改。
