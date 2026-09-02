# TM3-015 多DBC回归时间线

以下为既有时间线的补充视图，不以外部扫码/支付事件替代车辆内部节点。

| 事件 | 时间(s) | 候选状态/动作 | 数据判据 |
| --- | ---: | --- | --- |
| R00 | 115.3280 | 快充状态准备候选 | FC_statusCode 0→6 |
| R01 | 115.8453 | DC链路允许上电候选 | HVP_fcLinkAllowedToEnergize NONE→DC |
| R02 | 133.0273 | EVSE测试通过候选 | CP_hvChargeStatus_log TEST_PASSED |
| R03 | 134.5149 | 快充接触器闭合请求 | BMS_fcContactorRequest OPEN→CLOSE |
| R04 | 134.8465 | 快充接触器辅助反馈闭合 | 正/负AuxOpen 1→0 |
| R05 | 139.5253 | 高压充电使能阶段 | CP_hvChargeStatus_log → ENABLED |
| R06 | 140.0299 | FC直流电压建立 | FC_dcVoltage 0→346.88 V |
| R07 | 145.0303 | FC直流电流建立 | FC_dcCurrent 0→54.49 A并继续爬升 |
| R08 | 245.8359 | 快充状态退出 | FC_statusCode → 0 |
| R09 | 246.2327 | 高压充电阶段退出 | CP_hvChargeStatus_log ENABLED→CONNECTED |
| R10 | 246.2355 | FC电压电流归零 | FC_dcVoltage/current → 0 |
| R11 | 246.5176 | 快充接触器打开请求 | BMS_fcContactorRequest CLOSE→OPEN |
| R12 | 246.8477 | 快充接触器辅助反馈打开 | 正/负AuxOpen 0→1；DC允许回NONE |

主链补充解释：`DC链路允许上电候选 → 快充接触器闭合请求 → 辅助触点闭合反馈 → 高压充电ENABLED候选 → 直流电压建立 → 直流电流建立`。
停止侧顺序为：`状态退出/电流归零 → 接触器打开请求 → 辅助触点打开反馈`。该顺序只对TM3-015成立。
