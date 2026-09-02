# TM3-007 Evidence Plan Context

- 状态：`ANALYZED / EVIDENCE_ASSESSED / COMPLETE_WITH_GAPS`。
- 用途：正常基线数据采集；不以车辆故障排查或健康判定为本次目标。
- 车辆：Tesla Model 3，上海产2021款，2021年5月出厂，标准续航，55 kWh，后驱。
- 实验目的：在车辆从已休眠/低通信状态开始的条件下，建立“解锁—开门—入座—关门—制动—挂D—回P”与网络唤醒、高压条件/建立、READY/ENABLE及DCDC/低压反馈的本车映射。
- 系统边界：整车唤醒与高压上电协同；边界内包括车身输入反馈、电驱状态、BMS/HVP高压控制与PCS DCDC响应。人工动作、仪表显示和12 V外部实测属边界外证据。
- 主验证线：外部解锁/开门/入座/制动/挂挡输入 → 网络与控制器唤醒 → 安全条件与高压决策 → 预充/接触器/高压建立 → 可驱动状态。
- 能源/低压交叉验证：高压可用 ↔ DCDC状态与低压母线电压/输出电流。
- 状态机（待实测修正）：`SLEEP/LOW_COMMS → WAKE → INITIALIZE/CHECK → HV_COMING_UP → HV_UP → DRIVE_ENABLE → P_POWERED_STABLE`。这是实验分析模型，不是Tesla官方状态机。
- 时间边界：脚本时间仅用于定位；正式分析必须区分 `Planned Time / Observed Event Time / CAN Observed Time`。目前未发现现场记录或App实际触发CSV，在获得独立事件锚点前不用CAN反推人工动作时刻。
- DBC边界：主候选来自`input/tesla_model3_ONYX.dbc`；同时审计`dbc/`。`HVP_contactorState (0x20A)`存在跨DBC位段冲突，必须并列解析。`Model3_ETH_json_reference_optional.dbc`中多个定义标注为ETH/JSON参考，不自动假定本次CAN域可见。
- 审核范围：人工审核仅对TM3-007有效，范围为`THIS_EXPERIMENT_ONLY`，不自动写回车型级知识或正式DBC。2026-09-01人工Review接受全部23个Draft候选，保持原P等级、角色、报告位置和顺序；`ACCEPT`仅表示允许进入本实验Approved Plan与后续证据分析范围，不代表Signal语义已经验证成立。
- `0x20A/HVP_contactorState`审核边界：三个候选保持P1，按多DBC并列解析并必须执行Signal Validation；不预选冲突定义，不因Approved升级成熟度或车型级语义；只有完整状态序列、其他高压状态Signal及母线物理响应形成闭环后，才能评价具体语义。
- 事件时间审核边界：接受缺少独立Observed Event Time的事实。Planned Time只用于粗定位，不替代Observed Event Time，不由CAN反推人工动作并循环证明，不形成精确“人工动作→CAN响应”延迟；起始状态只称“本采集域低通信候选”，主要评价CAN内部状态转换、先后关系和条件化状态链；完成状态留待Evidence Assessment决定。

## Evidence Requirements

| ID | 需要证明的事项 | 充分性要求 | 缺口时评定 |
| --- | --- | --- | --- |
| ER-01 | 起始为休眠/低通信候选窗口 | 起始窗口报文频率、活跃ID与后续唤醒后明显不同，且有现场“已静置/无干预”记录 | 无独立现场记录时最多称“低通信候选” |
| ER-02 | 解锁、驾驶门开启与车身反馈可区分 | 独立动作锚点+门闩/门状态+网络唤醒趋势 | 只有CAN时不确认刷卡的精确物理时刻 |
| ER-03 | 入座和关门后的状态变化可区分 | 占座反馈、门闩关闭反馈与控制器/高压状态时序 | 占座Signal不可见时保留为无直接观测节点 |
| ER-04 | 制动条件输入与其后状态变化 | 制动Signal边沿与独立动作锚点一致；不把单独制动等同READY | 无独立锚点时只评估CAN内部时序 |
| ER-05 | 高压安全条件在上电过程中的观测性 | HVIL、绝缘或允许状态至少一项直接可读，其余节点明确直接/代理/无观测 | 不用上下游正常结果反推所有安全检查均已直接观测 |
| ER-06 | 预充、接触器与高压建立的顺序 | 至少有BMS/HVP状态转换+高压电压反馈；冲突DBC必须并列验证 | 未捕获瞬态不等于未执行预充 |
| ER-07 | 挂D成功且可驱动状态建立 | 挡位反馈+电驱ENABLE/READY类状态，或挡位+独立仪表可驱动反馈 | 不以制动或高压UP单项代替Drive Enable |
| ER-08 | DCDC启动与低压能源响应 | DCDC状态+低压母线电压/输出电流；若有外部12 V读数则交叉验证 | 仅有DCDC Signal时不宣称外部电池端电压已实测 |
| ER-09 | 回P后保持上电的稳定结果 | P挡、高压/DCDC状态和稳定窗口同时满足 | 仅作本次条件化基线，不外推到全部软件/温度/SOC条件 |
