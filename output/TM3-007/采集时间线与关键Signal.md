# TM3-007 采集时间线与关键Signal

## 实际时间线

| 阶段 | CAN时间/窗口 | 实际变化 | Signal / CAN ID | Signal值/变化 | 工程意义 | 局部限制 |
| --- | --- | --- | --- | --- | --- | --- |
| 低通信候选与通信恢复 | 103.1571 | 采集域进入长时间无帧窗口。 | `报文频率(派生)` / `derived` | 网络帧率降为0 | 形成后续通信恢复的采集域内前置状态。 | — |
| 低通信候选与通信恢复 | 470.1237 | 长时间无帧后，CAN通信恢复。 | `报文频率(派生)` / `derived`；`活跃CAN_ID数(派生)` / `derived` | 网络帧率由0恢复；活跃CAN ID重新出现 | 标志本采集域内部上电状态链开始。 | 没有独立Observed Event Time，不确认具体人工解锁时刻。 |
| 高压建立序列 | 472.6697 | BMS总接触器进入闭合过程。 | `BMS_contactorState` / `0x212`；`BMS_packVoltage` / `0x132` | BMS接触器总状态进入CLOSING；Pack电压开始建立 | 高压建立执行序列开始。 | — |
| 高压建立序列 | 473.3233 | 高压互锁候选转为正常，正接触器进入预充。 | `HVP_hvilStatus` / `0x20A`；`HVP_packContPositiveState` / `0x20A`；`BMS_packVoltage` / `0x132` | HVIL由UNKNOWN转为STATUS_OK；正接触器由OPEN转为PRECHARGE | 安全条件候选满足后进入预充阶段，Pack电压同期上升。 | 0x20A语义仅在本实验既有Signal Validation边界内成立。 |
| 高压建立序列 | 474.2713 | BMS总接触器闭合，Pack电压建立至约354 V。 | `BMS_contactorState` / `0x212`；`BMS_packVoltage` / `0x132` | 接触器总状态由CLOSING转为CLOSED；Pack电压升至353.51 V | 总接触器状态与Pack侧物理电压响应形成实验级闭环。 | — |
| 高压建立序列 | 474.3233 | 正负接触器候选进入保持状态，DCDC低压支持激活。 | `HVP_packContPositiveState` / `0x20A`；`HVP_packContNegativeState` / `0x20A`；`PCS_dcdc12VSupportStatus` / `0x224` | 正接触器由PRECHARGE转为ECONOMIZED；负接触器由OPEN转为ECONOMIZED；12V支持由IDLE转为ACTIVE | 高压接触器序列完成，并进入DCDC低压支持阶段。 | 0x20A接触器语义不自动升级为车型级正式定义。 |
| Ready/车身反馈 | 477.0302 | 用户界面可驱动候选由0变为1。 | `UI_readyForDrive` / `0x353` | UI ready候选由0转为1 | 提供高压建立后的显示/消费者层交叉反馈。 | 该Signal是显示层候选，不作为驱动许可源头。 |
| Ready/车身反馈 | 500.7386 | 驾驶门闩反馈进入OPENED。 | `VCLEFT_frontLatchStatus` / `0x102` | 驾驶门闩由CLOSED转为OPENED | 确认门闩反馈能够区分开门状态。 | 该CAN边沿不是独立人工开门时刻。 |
| Ready/车身反馈 | 525.7703 | 驾驶门闩反馈回到CLOSED。 | `VCLEFT_frontLatchStatus` / `0x102` | 驾驶门闩由OPENED转为CLOSED | 形成CLOSED→OPENED→CLOSED门闩状态序列。 | 该CAN边沿不是独立人工关门时刻。 |
| D/ENABLE进入与返回P | 540.4155 | 电驱状态报文出现并稳定为P/STANDBY。 | `DI_gear` / `0x118`；`DI_systemState` / `0x118`；`DI_brakePedalState` / `0x118` | 挡位反馈可读为P；电驱状态可读为STANDBY；制动字段仍为INVALID | 建立挂D前的电驱内部参考状态。 | 制动输入不能由本事件确认。 |
| D/ENABLE进入与返回P | 545.267 | 挡位进入D，电驱状态同步进入ENABLE。 | `DI_gear` / `0x118`；`DI_systemState` / `0x118` | 挡位由P转为D；电驱状态由STANDBY转为ENABLE | 形成CAN内部可驱动状态建立节点。 | — |
| D/ENABLE进入与返回P | 555.4262 | 挡位回到P，电驱状态同步回到STANDBY。 | `DI_gear` / `0x118`；`DI_systemState` / `0x118` | 挡位由D转为P；电驱状态由ENABLE转为STANDBY | 形成可驱动状态退出节点。 | — |
| 结束稳定窗口 | 599.9996 | P挡上电状态保持至采集结束。 | `DI_gear` / `0x118`；`DI_systemState` / `0x118`；`BMS_contactorState` / `0x212`；`PCS_dcdc12VSupportStatus` / `0x224` | P/STANDBY保持；接触器CLOSED保持；12V支持ACTIVE保持 | 稳定窗口：形成约44.6秒P挡上电稳定窗口。 | — |

## 0x20A既有Signal Validation迁移

| Signal | 既有结果 | 时序 | 方向 | 枚举 | 既有证据与边界 |
| --- | --- | --- | --- | --- | --- |
| HVP_hvilStatus | STRONGLY_SUPPORTED | SUPPORTED | NOT_APPLICABLE | SUPPORTED_THIS_EXPERIMENT | 下电段UNKNOWN；上电预充开始473.3233秒转STATUS_OK；独立ETH/JSON候选0x682同步为OK；无外部HVIL测量；0x20A在旧tesla_can中另定义为BrakeMessage；只在本实验范围强支持 |
| HVP_packContNegativeState | STRONGLY_SUPPORTED | SUPPORTED | SUPPORTED | SUPPORTED_THIS_EXPERIMENT | OPENING→OPEN后经历静默；上电474.3233秒进入ECONOMIZED，与BMS总接触器CLOSED及Pack电压建立闭环；未直接观察PULLED_IN瞬态；不自动升级车型级正式语义 |
| HVP_packContPositiveState | STRONGLY_SUPPORTED | SUPPORTED | SUPPORTED | SUPPORTED_THIS_EXPERIMENT | OPENING→OPEN；上电473.3233秒PRECHARGE→474.3233秒ECONOMIZED；Pack电压同期由约5V升至约354V；单次实验级闭环；不写回车型DBC |

> Event ID、raw sample time、Signal age、DLC与per-frame decode status仅保留在机器证据或工程审计中。
