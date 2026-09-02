# TM3-008 采集时间线与关键Signal

## 实际时间线

| 阶段 | CAN时间/窗口 | 实际变化 | Signal / CAN ID | Signal值/变化 | 工程意义 | 局部限制 |
| --- | --- | --- | --- | --- | --- | --- |
| 起始状态 | 0 | 分析区间开始 | `UI_readyForDrive` / `0x353`；`VCLEFT_frontLatchStatus` / `0x102`；`VCSEC_simpleLockStatus` / `0x339`；`BMS_contactorState` / `0x212`；`PCS_dcdc12VSupportStatus` / `0x224` | Ready候选为1、门闩CLOSED、车辆UNLOCKED、接触器CLOSED、DCDC支持ACTIVE | 建立CAN内部起始参考状态。 | DI_gear无可解样本，P挡仍缺直接CAN证据 |
| 开关门与落锁 | 7.9845 | 驾驶门打开 | `VCLEFT_frontLatchStatus` / `0x102` | CLOSED→OPENED | 驾驶门闩反馈进入打开状态。 | 无占座Signal，不能单独证明人员已经离座 |
| 开关门与落锁 | 29.6561 | 驾驶门关闭 | `VCLEFT_frontLatchStatus` / `0x102` | OPENED→CLOSED | 驾驶门闩反馈回到关闭状态。 | 门闩反馈，不等于落锁 |
| 开关门与落锁 | 33.3626 | NFC锁止请求候选及锁止反馈 | `VCSEC_lockRequestType` / `0x339`；`VCSEC_simpleLockStatus` / `0x339`；`VCSEC_vehicleLockStatus` / `0x339` | ACTIVE_NFC_LOCK；UNLOCKED→LOCKED；ACTIVE_NFC_UNLOCKED→ACTIVE_NFC_LOCKED | 形成CAN域内NFC落锁候选与锁止反馈。 | CAN内部时序支持；ER-10外部刷卡/灯光/声音记录仍缺失 |
| 需求/消费者状态退出 | 122.8397 | Ready消费者状态候选退出 | `UI_readyForDrive` / `0x353` | 1→0 | Ready消费者状态候选退出。 | CONSUMER_STATE，不作为许可或控制命令 |
| 最终下电执行 | 282.1605 | 车辆供电阶段候选进入OFF | `VCFRONT_vehiclePowerState` / `0x221` | CONDITIONING→OFF | 车辆供电系统结果候选进入OFF。 | SYSTEM_RESULT候选，不是下电REQUEST或COMMAND |
| 最终下电执行 | 282.2451 | BMS总接触器开始打开 | `BMS_contactorState` / `0x212` | CLOSED→OPENING | 高压总接触器开始打开。 | BMS总状态 |
| 最终下电执行 | 282.2645 | 12V支持状态退出 | `PCS_dcdc12VSupportStatus` / `0x224` | ACTIVE→IDLE | DCDC低压支持最终退出。 | PCS内部状态；外部12V未测 |
| 最终下电执行 | 282.3549 | 正负接触器候选进入OPENING | `HVP_packContPositiveState` / `0x20A`；`HVP_packContNegativeState` / `0x20A` | ECONOMIZED→OPENING | 正负接触器候选进入打开过程。 | 0x20A实验级多DBC验证 |
| 高压物理响应候选 | 282.4645 | PCS母线放电状态候选激活 | `PCS_dcdcHvBusDischargeStatus` / `0x224` | IDLE→ACTIVE | PCS放电执行状态候选激活。 | 执行状态候选，不证明母线已去电 |
| 最终下电执行 | 282.5436 | BMS总接触器打开 | `BMS_contactorState` / `0x212` | OPENING→OPEN | BMS总接触器进入OPEN。 | BMS总状态 |
| 高压物理响应候选 | 282.5503 | 0x132电压字段快速下降 | `BMS_packVoltage` / `0x132` | 由约353.5 V降至60 V以下并继续下降 | 0x132电压字段快速下降。 | 缩放/动态可信；Pack端物理定位与实测矛盾，不能沿用名称 |
| 高压物理响应候选 | 282.7644 | PCS母线放电状态候选返回IDLE | `PCS_dcdcHvBusDischargeStatus` / `0x224` | ACTIVE→IDLE | PCS放电执行状态候选结束。 | PCS_dcdcHvBusVolt定义失败，不能据此确认下游母线终值 |
| 最终下电执行 | 283.3549 | 正负接触器候选进入OPEN | `HVP_packContPositiveState` / `0x20A`；`HVP_packContNegativeState` / `0x20A` | OPENING→OPEN | 正负接触器候选进入OPEN。 | 0x20A实验级多DBC验证 |
| 网络分层退出 | 295.0436 | BMS发布总线休眠候选 | `BMS_hvsBusAsleep` / `0x2F2` | 0→1 | BMS消费者视角的总线休眠候选出现。 | BMS消费者视角，不代表整车全部网络 |
| 末段通信静默 | 295.8383 | 本采集域最后一帧/进入末段静默 | `报文频率(派生)` / `derived`；`逐CAN_ID最后出现时间(派生)` / `derived` | 最后一帧后通信为0 | 当前采集域进入末段无帧窗口。 | 当前采集域静默候选 |
| 末段通信静默 | 660 | 计划采集窗口结束 | `报文频率(派生)` / `derived` | 末段未见通信恢复 | 稳定窗口：声明的TM3-008采集窗口结束。 | 结束时刻来自用户确认和拆分合同，不是CAN事件 |

> Event ID、raw sample time、Signal age、DLC与per-frame decode status仅保留在机器证据或工程审计中。
