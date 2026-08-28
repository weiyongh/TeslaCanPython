# 特斯拉 DBC 名词解释

## 文档用途

本文档记录 Tesla Model 3 CAN 数据分析中已经遇到、能够借助 DBC 解释的 CAN ID、Message 和 Signal。它是持续更新的通用名词表，不等同于特斯拉官方 CAN/DBC 文档，也不表示其中所有定义均已在实车上完成语义验证。

当前内容来源于：

- 实验：`TM3-002 踩制动进入 READY 相关状态`
- 实验：`TM3-003 静止挂挡`
- 实验：`TM3-004 低速加速`
- 实验：`TM3-005 低速松电门回收`
- 实验：`TM3-006 动力电池静态基线`
- ASC：`input/can_20260827135113_TM3-002_进入READY采集.asc`
- ASC：`input/can_20260827140254_TM3-003_静止挂挡采集.asc`
- ASC：`input/can_20260827135814_TM3-004_低速加速采集.asc`
- ASC：`input/can_20260827140713_TM3-005_低速松电门回收采集.asc`
- ASC：`input/can_20260827141104_TM3-006_动力电池静态基线采集.asc`
- 主用 DBC：`input/tesla_model3_ONYX.dbc`
- 分析日期：2026-08-27

证据等级说明：

- **已确认**：信号变化与动作、时序和系统状态相符，可用于本采集域内的判断。
- **DBC可解释**：DBC给出了名称和值表，但本次只观察到静态值或缺少独立验证。
- **定义待验证**：虽然能够解码，但结果存在物理冲突、版本不匹配或SNA解释问题，不能写入正常基线。
- **当前不可见**：DBC中有定义，但本次没有成功解码到该信号。

## 常见控制器与缩写

| 缩写 | 英文/角色 | 中文理解 |
|---|---|---|
| `BMS` | Battery Management System | 动力电池管理系统，负责电池状态估算、能力边界和安全控制 |
| `HVP` | High Voltage Power / Pack controller | 高压电源或电池包高压控制相关模块，负责接触器、HVIL及高压状态 |
| `DI` | Drive Inverter | 驱动逆变器/后电驱相关控制与状态 |
| `DIS` | Drive Inverter Slave / secondary drive | 第二电驱或前电驱相关状态；具体前后轴对应关系需结合车型验证 |
| `PCS` | Power Conversion System | 功率转换系统，通常涉及OBC、DC/DC及相关预充状态 |
| `VCLEFT` | Vehicle Controller Left | 左侧车身控制器，包含车门、制动开关等输入状态 |
| `VCFRONT` | Vehicle Controller Front | 前车身控制器，包含低压供电、热管理和部分整车状态 |
| `SCCM` | Steering Column Control Module | 转向柱控制模块，包含换挡拨杆等输入 |
| `UI` | User Interface | 中控/用户界面相关请求、显示和告警 |
| `GTW` | Gateway | 整车网关及配置相关信息 |
| `CP` | Charge Port | 充电口、充电连接和充电接口相关状态 |
| `PMS` | Power/Propulsion Management System | 动力或功率管理相关告警；具体模块角色需结合车型验证 |
| `CMPD` | Compressor Drive | 电动压缩机驱动，不是整车驱动READY |

## 0x3C2：制动开关与车身开关状态

- Message：`VCLEFT_switchStatus`
- 主要角色：驾驶员制动输入、车身开关状态
- 本次证据：**已确认**

| Signal | 中文含义 | 本次观察与诊断意义 |
|---|---|---|
| `VCLEFT_brakeSwitchPressed` | 制动踏板开关是否按下 | `0→1`表示踩下制动，`1→0`表示松开；是本次进入电驱待命链的输入证据 |

本次制动开关约在39.518秒由0变为1。松开制动时出现约70 ms的快速翻转，可能是机械触点抖动、去抖过程或采样状态切换，最终稳定为0。

## 0x118：电驱系统状态

- Message：`DI_systemStatus`
- 主要角色：电驱状态、挡位、踏板及驱动许可
- 本次证据：`DI_systemState`、`DI_gear` **已确认**；部分字段定义待验证

| Signal | 中文含义 | 常见值/状态 | 本次观察与诊断意义 |
|---|---|---|---|
| `DI_systemState` | 电驱系统运行状态 | `UNAVAILABLE`不可用、`IDLE`空闲、`STANDBY`待命、`FAULT`故障、`ABORT`中止、`ENABLE`使能 | TM3-002踩制动后进入`STANDBY`；TM3-003四次挂D/R均进入`ENABLE`，回P均同步回到`STANDBY` |
| `DI_gear` | 电驱识别的实际挡位 | `P/R/N/D`等 | TM3-003两次D、两次R及四次回P均与驾驶请求方向和时序一致 |
| `DI_accelPedalPos` | 加速踏板位置 | `%` | 本次没有踩加速踏板；后续用于扭矩请求链分析 |
| `DI_brakePedalState` | 电驱侧制动踏板状态 | `OFF/ON/INVALID` | 本次解码为`INVALID`，与0x3C2的有效制动开关冲突，暂不使用该字段判断制动动作 |
| `DI_driveBlocked` | 驱动是否被阻止 | 状态枚举 | 用于判断有扭矩请求但车辆不允许驱动的边界条件 |
| `DI_immobilizerState` | 防启动/防盗许可状态 | 状态枚举 | 可能参与驱动允许判断，本次未形成独立结论 |
| `DI_keepAliveRequest` | 电驱保持唤醒请求 | 0/1 | 表示电驱是否请求保持系统唤醒 |
| `DI_proximity` | 钥匙或接近状态 | 0/1 | 可能参与车辆唤醒与驾驶授权，具体语义待验证 |

`DI_systemState=STANDBY`表示电驱处于待命状态。TM3-003已经确认挂入D/R后进入`ENABLE`，回P后恢复`STANDBY`。这些是电驱状态机语义，仍不应脱离挡位、扭矩、轴速和整车UI，单独等同于所有语境下的整车READY。

## 0x108：电驱扭矩请求与执行反馈

- Message：`DI_torque`
- 主要角色：扭矩请求、实际扭矩和轴速反馈
- 当前证据：TM3-002/003确认静止零输出；TM3-004确认低速正扭矩建立与执行跟随

| Signal | 中文含义 | 单位 | 本次观察与诊断意义 |
|---|---|---:|---|
| `DI_torqueCommand` | 电驱扭矩指令/请求扭矩 | Nm | TM3-004加速时转正；TM3-005松电门越过零扭矩点后转负 |
| `DI_torqueActual` | 电驱实际输出扭矩 | Nm | 正驱动和回收工况均与请求同方向、同帧跟随；绝对缩放和机械参考点仍需更多工况验证 |
| `DI_axleSpeed` | 电驱轴转速 | RPM | 正扭矩时随车速上升，负扭矩回收时随车速下降 |

基本诊断链为：

```text
扭矩指令 DI_torqueCommand
        ↓
实际扭矩 DI_torqueActual
        ↓
轴转速 DI_axleSpeed
```

## 0x257：电驱侧车速

- Message：`DI_speed`
- 主要角色：电驱使用的车辆速度及UI速度
- 本次证据：**已确认变化方向与目标速度**

| Signal | 中文含义 | 单位 | TM3-004观察 |
|---|---|---:|---|
| `DI_vehicleSpeed` | 电驱使用的车辆速度 | km/h | 两次低速加速峰值约11.84、11.44 km/h |
| `DI_uiSpeed` | 面向UI的整数车速 | 当前DBC未标单位 | 本次最高12，与 `DI_vehicleSpeed`一致 |

## 0x266：电驱实际电功率

- Message：`DI_power`
- 主要角色：电驱电功率与热损耗估算

| Signal | 中文含义 | 单位 | TM3-004观察 |
|---|---|---:|---|
| `DI_elecPower` | 电驱电功率 | kW | TM3-004正加速最高约2.0 kW；TM3-005松电门回收最低约-3.5至-4.0 kW。当前采集域已确认正值为驱动用电、负值为回收发电方向 |

## 0x132：动力电池高压母线状态

- Message：`BMS_hvBusStatus`
- 主要角色：Pack实际电压、电流
- 注意：实车报文为6字节，主用DBC声明为8字节；目标字段位于前6字节，可截断解码，但保留版本差异标记。

| Signal | 中文含义 | 单位 | TM3-004观察 |
|---|---|---:|---|
| `BMS_packVoltage` | 动力电池包实际电压 | V | 静止约347.9 V，加速窗口最低约347.3 V |
| `BMS_packCurrent` | 动力电池包实际电流 | A | TM3-004正加速升至约6.4、7.9 A；TM3-005回收降至约-9.2、-9.5 A。当前采集域已确认正值放电、负值充电/回收 |
| `BMS_currentUnfiltered` | 未滤波或较少滤波的Pack电流 | A | 与Pack电流方向和量级接近，具体滤波语义待验证 |

## 0x2D2：动力电池驱动能力边界

- Message：`BMS_driveLimits`
- 主要角色：BMS向整车/电驱提供充放电能力限制
- 本次证据：两个电流边界的**变化方向与时序已确认**，绝对值仍需跨样本验证

| Signal | 中文含义 | 单位 | 本次观察与诊断意义 |
|---|---|---:|---|
| `BMS_maxDischargeCurrent` | 动力电池最大允许放电电流 | A | 踩制动后约140 ms由53.376跃升至682.624，表示驱动放电能力边界显著放宽 |
| `BMS_maxChargeCurrent` | 动力电池最大允许充电电流 | A | 同时由0跃升至250，表示充电/能量回收接收能力边界被释放 |
| `BMS_minBusVoltage` | BMS允许或计算使用的最小母线电压边界 | V | 本次稳定；具体是不是实时限制值需继续验证 |
| `BMS_maxBusVoltage` | BMS允许或计算使用的最大母线电压边界 | V | 本次稳定；具体是不是实时限制值需继续验证 |

这里的`max`不是实际电流，而是BMS计算出的能力上限：

```text
电池状态与安全边界
        ↓
BMS计算允许充/放电电流
        ↓
VCU/电驱在边界内生成扭矩
```

## 0x212：BMS总体状态

- Message：`BMS_status`
- 主要角色：接触器、绝缘及电池包状态

| Signal | 中文含义 | 本次证据与注意事项 |
|---|---|---|
| `BMS_contactorState` | BMS判断的动力电池主接触器状态 | 从采集开始即为`CLOSED`，说明本次没有捕获接触器闭合沿；**已确认** |
| `BMS_isolationResistance` | 动力电池高压系统绝缘电阻 | 本次解码为0，但与HVIL正常、接触器闭合且无绝缘告警等证据冲突；**定义待验证，不能解释为真实零绝缘电阻** |
| `BMS_minPackTemperature` | 电池包最低温度 | 本次结果与0x312温度信号冲突；**定义待验证** |

## 0x20A：高压接触器与HVIL状态

- Message：`HVP_contactorState`
- 主要角色：高压回路实际设定状态与互锁状态
- 本次证据：**已确认静态状态**

| Signal | 中文含义 | 本次观察与诊断意义 |
|---|---|---|
| `HVP_packContactorSetState` | 动力电池包接触器设定状态 | 从采集开始即为`CLOSED`，与BMS接触器状态相互印证 |
| `HVP_fcContactorSetState` | 快充接触器设定状态 | 本次为`OPEN`，符合未进行直流快充 |
| `HVP_hvilStatus` | 高压互锁回路状态 | 本次为`STATUS_OK`，表示该DBC定义下HVIL状态正常 |

`SetState`更接近控制器设定/命令状态，不一定等于物理接触器的独立辅助触点反馈。诊断粘连或无法闭合时，还需对比接触器反馈、母线电压和电流。

## 0x7AA：高压控制调试信息

- Message：`HVP_debugMessage`
- 主要角色：高压包电压、HVIL电气量及调试状态

| Signal | 中文含义 | 单位 | 本次证据与注意事项 |
|---|---|---:|---|
| `HVP_packVoltage` | 高压电池包电压 | V | 本次约348.3 V，踩制动前后基本稳定；**已确认趋势** |
| `HVP_dcLinkVoltage` | DC-link直流母线实际电压 | V | 本次约348.1–348.5 V，与Pack电压基本一致；**已确认** |
| `HVP_gpioHvilEnable` | HVIL检测/相关GPIO使能状态 | 0/1 | 本次为1；DBC可解释 |
| `HVP_hvilInVoltage` | HVIL输入侧检测电压 | V | 本次约1.2 V；绝对正常范围待建立 |
| `HVP_hvilOutVoltage` | HVIL输出侧检测电压 | V | 本次约2.6 V；绝对正常范围待建立 |
| `HVP_packCurrentMia` | Pack电流信号丢失/不可用标志 | 0/1 | 本次为1，但与系统正常工作背景需交叉验证，不能单独定性通信故障 |
| `HVP_gpioShuntDataReady` | 分流器电流数据就绪标志 | 0/1 | 本次为0；具体有效逻辑待验证 |

`MIA`通常是`Missing In Action`的缩写，在CAN语境中表示某个报文或信号缺失、超时或不可用。

`HVP_packVoltage`与`HVP_dcLinkVoltage`的区别是：前者表示动力电池包侧电压，后者表示接触器之后、整车高压负载侧的直流母线电压。接触器闭合且母线稳定时二者应当接近；预充阶段则可以通过二者的压差和收敛过程判断母线是否成功建立。

## 0x292：动力电池SOC状态

- Message：`BMS_socStatus`
- 主要角色：BMS内部、显示及单体分布相关SOC
- 本次证据：**DBC可解释，数值内部一致性较好**

| Signal | 中文含义 | 本次值 |
|---|---|---:|
| `BMS_socMin` | BMS估算的最低SOC | 约45.8% |
| `BMS_socUI` | 面向UI/驾驶员显示使用的SOC | 约46.7% |
| `BMS_socMax` | BMS估算的最高SOC | 约48.4–48.5% |
| `BMS_socAvg` | BMS估算的平均SOC | 约46.0% |

TM3-006静态基线中，`socMin/socAvg/socUI/socMax`分别约45.5%、45.7%、46.5%、48.1～48.2%，90秒内稳定。该报文还包含 `BMS_initialFullPackEnergy`，但本次解码为0.1 kWh，与其他能量字段明显冲突，不能用于容量或SOH判断。

`socMin/socMax`可能反映电池内部估算分布或不同边界，并不一定等于“最低/最高单体电压对应的SOC”，具体算法属于BMS内部实现。

## 0x332：单体电压极值

- Message：`BMS_bmbMinMax`
- 主要角色：单体电压最高值、最低值及对应编号
- 本次证据：电压极值与压差趋势**可解释**；编号会随采样波动

| Signal | 中文含义 | 本次观察与诊断意义 |
|---|---|---|
| `BMS_brickVoltageMax` | 最高单体/Brick电压 | 踩制动前约3.286 V，之后约3.284 V |
| `BMS_brickVoltageMin` | 最低单体/Brick电压 | 踩制动前约3.284 V，之后约3.282 V |
| `BMS_brickNumVoltageMax` | 当前最高电压Brick编号 | 微小电压变化会造成编号切换，不能把一次编号变化当作电芯故障 |

`Brick`在特斯拉电池DBC中通常表示BMS采样和管理的串联电芯组/电压采样单元，不应未经车型结构确认就直接翻译成单颗物理电芯。

本次最高与最低电压差约2 mV量级：

```text
单体压差 = BMS_brickVoltageMax - BMS_brickVoltageMin
```

TM3-006进一步确认：106个有效Brick的均值范围约3.2838～3.2857 V，另有两个固定0 V的未使用占位通道。有效Brick平均电压之和约348.2 V，与Pack电压约348.08 V一致；诊断程序必须排除占位通道，不能把0 V误报为单体严重欠压。

## 0x252：BMS充放电功率能力

- Message：`BMS_powerAvailable`
- 主要角色：BMS根据SOC、温度、电压和安全条件计算的当前功率边界
- 注意：主用DBC存在字段重叠，通用解析器会拒绝整帧；以下两个信号位于互不重叠的前4字节，可按DBC位定义独立提取。

| Signal | 中文含义 | TM3-006结果 | 使用边界 |
|---|---|---:|---|
| `BMS_maxDischargePower` | BMS最大允许放电功率 | 约190.91～190.93 kW | 能力上限，不是实际功率 |
| `BMS_maxRegenPower` | BMS最大允许回收/充电功率 | 约90.31 kW | 能力上限，不是实际回收功率 |
| `BMS_powerLimitsState` | BMS功率边界状态位 | 1 | 枚举语义待验证 |

## 0x352：BMS能量状态

- Message：`BMS_energyStatus`
- 主要角色：标称满包能量、剩余能量和能量缓冲

| Signal | 中文含义 | TM3-006结果 |
|---|---|---:|
| `BMS_nominalFullPackEnergy` | 当前标称满包能量 | 51.12 kWh |
| `BMS_nominalEnergyRemaining` | 标称剩余能量 | 23.00 kWh |
| `BMS_idealEnergyRemaining` | 理想剩余能量 | 23.00 kWh |
| `BMS_expectedEnergyRemaining` | 期望剩余能量 | 23.00 kWh |
| `BMS_energyBuffer` | 能量缓冲区 | 2.23 kWh |
| `BMS_energyToChargeComplete` | 充满所需能量 | 26.50 kWh |

这些是BMS估算量。51.12 kWh与23.00 kWh的比例和SOC量级一致，但仍需能量积分或可信服务数据验证后，才能用于SOH趋势。

## 0x401：各Brick电压

- Message：`BMS_brickVoltages`
- 主要角色：逐个Brick电压
- 本次证据：**DBC可解释**

| Signal示例 | 中文含义 |
|---|---|
| `BMS_brick2` | 编号2的Brick电压 |
| `BMS_brick5` | 编号5的Brick电压 |
| `BMS_brick102` | 编号102的Brick电压 |

本报文中的各Brick电压会随负载、采样噪声和温度产生0.1–1 mV量级的持续变化。它们在自动事件排名中容易因为“频繁变化”得到高分，但不能仅凭靠近动作时间就判断某一个Brick与制动动作存在独立因果关系。诊断时应优先看整体极值、压差和重复负载响应。

## 0x312：动力电池热状态

- Message：`BMS_thermalStatus`
- 主要角色：电池包温度极值及热管理状态

| Signal | 中文含义 | 本次证据与注意事项 |
|---|---|---|
| `BMS_packTMin` | 电池包最低温度 | 本次解码约20.125°C |
| `BMS_packTMax` | 电池包最高温度 | 本次解码出现-25°C至-5°C，与最低温度关系不成立；**定义待验证** |

温度必须满足：

```text
最高温度 ≥ 最低温度
```

本次不满足这一基本物理约束，因此0x312相关温度暂不能写入正常基线。

## 0x320：BMS告警矩阵

- Message：`BMS_alertMatrix`
- 主要角色：BMS安全、绝缘、HVIL和接触器故障状态
- 本次证据：相关位均为0；**表示没有广播对应告警，不等于完成部件级健康验证**

| Signal | 中文含义 |
|---|---|
| `BMS_a034_SW_Passive_Isolation` | 被动绝缘监测相关软件告警 |
| `BMS_a035_SW_Isolation` | 绝缘监测相关软件告警 |
| `BMS_a036_SW_HvpHvilFault` | 高压包HVIL故障告警 |
| `BMS_a123_SW_Internal_Isolation` | 电池包内部绝缘异常告警 |
| `BMS_a151_SW_external_isolation` | 电池包外部/整车高压侧绝缘异常告警 |
| `BMS_a163_SW_Contactor_Mismatch` | 接触器命令与反馈不一致告警 |

名称中的`a`通常表示Alert（告警），数字是告警编号，`SW`表示软件判定逻辑。

## 0x3AA：HVP高压告警矩阵

- Message：`HVP_alertMatrix1`
- 主要角色：HVIL、接触器意外断开或强制断开告警

| Signal | 中文含义 |
|---|---|
| `HVP_w026_HvilFault` | HVIL故障警告 |
| `HVP_w039_PackContactorFellOpen` | 动力电池包接触器意外掉开 |
| `HVP_w040_FcContactorFellOpen` | 快充接触器意外掉开 |
| `HVP_w043_packContactorForceOpen` | 动力电池包接触器被强制断开 |
| `HVP_w044_fcContactorForceOpen` | 快充接触器被强制断开 |

本次这些告警位均为0，仅说明没有观察到相应告警。

## 0x3B5与0x3C5：第二电驱告警矩阵

- Message：`DIS_alertMatrix2`、`DIS_alertMatrix3`
- 主要角色：电驱转速、HVIL、母线及旋变异常

| CAN ID | Signal | 中文含义 | 本次证据 |
|---:|---|---|---|
| `0x3B5` | `DIS_a073_motorSpeed` | 电机转速相关异常 | 0，未广播该告警 |
| `0x3B5` | `DIS_a075_motorSpeedMismatch` | 电机转速信号不一致 | 0，未广播该告警 |
| `0x3B5` | `DIS_a114_noMotorSpeed` | 无有效电机转速信号 | 0，未广播该告警 |
| `0x3B5` | `DIS_a086_hvilNotPresent` | 电驱侧未检测到HVIL | 0，未广播该告警 |
| `0x3C5` | `DIS_a160_busVoltageAnomaly` | 直流母线电压异常 | 0，未广播该告警 |
| `0x3C5` | `DIS_a154_resolver` | 旋变/转子位置传感器相关异常 | 0，只能说明没有旋变告警，不能证明实时角度正确 |

## 0x384：动力管理告警矩阵

- Message：`PMS_alertMatrix1`
- 主要角色：电驱挡位一致性和旋变相关告警

| Signal | 中文含义 | 本次证据 |
|---|---|---|
| `PMS_w006_inconsistentDIGear` | 电驱挡位状态不一致警告 | 本次为0 |
| `PMS_w055_resolver` | 旋变相关警告 | 本次为0 |

旋变告警位为0只覆盖异常诊断结果，不提供旋变实时角度、角度有效性、载波或锁相状态。

## 0x7D5：电驱调试与内部边界变量

- Message：`DI_debug`
- 主要角色：电驱内部状态、扭矩边界、旋变和控制算法调试量
- 注意：这是多路复用调试报文，不同`DI_debugIndex`对应不同信号页；必须确认对应页实际出现后才能读取信号。

| Signal | 中文含义 | 本次状态 |
|---|---|---|
| `DI_gateDriveState` | 功率器件栅极驱动状态 | 本次可见`INIT`，具体状态机语义待验证 |
| `DI_sysPedalMinTorque` | 系统踏板链允许的最小扭矩边界 | 本次解码约-25.5 Nm，绝对值待跨样本验证 |
| `DI_sysPedalMaxTorque` | 系统踏板链允许的最大扭矩边界 | 本次为0，符合未请求驱动扭矩 |
| `DI_sysPostPedalMinTorque` | 踏板处理后最小扭矩边界 | 本次值落在DBC下限，可能是无效/饱和值，定义待验证 |
| `DI_sysPostPedalMaxTorque` | 踏板处理后最大扭矩边界 | 本次为0 |
| `DI_rotorMaxMagnetTemp` | 转子永磁体最高估算温度 | 本次约36°C；是否为有效估算需后续行驶样本验证 |
| `DI_resolverReady` | 旋变信号是否就绪 | DBC有定义，本次未解码到对应多路复用页 |
| `DI_resolverNoCarrier` | 旋变激励载波缺失 | DBC有定义，本次不可见 |
| `DI_resolverNoPhaseLock` | 旋变相位未锁定 | DBC有定义，本次不可见 |
| `DI_resolverClaMIA` | 旋变相关CLA/内部计算单元通信或数据缺失 | DBC有定义，本次不可见 |
| `DI_resolverOffsetCos` | 旋变余弦通道偏置 | DBC有定义，本次不可见 |
| `DI_resolverOffsetSin` | 旋变正弦通道偏置 | DBC有定义，本次不可见 |
| `DI_resolverPhaseOffset` | 旋变相位偏置 | DBC有定义，本次不可见 |
| `DI_loadAngle` | 电机负载角 | DBC有定义，本次不可见 |
| `DI_internalAngleFilt` | 电驱内部滤波角度 | DBC有定义，本次不可见 |
| `DI_rotorFlux` | 转子磁链估算值 | DBC有定义，本次不可见 |

旋变相关控制链可理解为：

```text
旋变正弦/余弦反馈
        ↓
位置角计算与有效性判断
        ↓
转子位置/转速
        ↓
FOC电流矢量控制
        ↓
电机实际扭矩
```

## 0x224：PCS DC/DC预充状态

- Message：`PCS_dcdcStatus`
- 主要角色：DC/DC预充状态机和重试计数

| Signal | 中文含义 | 本次状态 |
|---|---|---|
| `PCS_dcdcPrechargeStatus` | DC/DC内部预充状态 | `IDLE` |
| `PCS_dcdcPrechargeRtyCnt` | DC/DC预充重试次数 | 0 |
| `PCS_dcdcPrechargeRestartCnt` | DC/DC预充重新启动次数 | 0 |
| `PCS_dcdcInitialPrechargeSubState` | DC/DC初始预充子状态 | `STANDBY` |

这里是PCS/DC/DC内部预充，不应与动力电池主接触器的整车高压预充直接混为同一状态机。

## 0x3A4：PCS预充告警

- Message：`PCS_alertMatrix`
- 主要角色：充电和DC/DC母线预充失败告警

| Signal | 中文含义 |
|---|---|
| `PCS_a006_chgPrechargeFailedScr` | 充电侧SCR相关预充失败 |
| `PCS_a013_chgPrechargeFailedBoost` | 充电升压环节预充失败 |
| `PCS_a043_hvBusPrechargeFailure` | PCS高压母线预充失败 |

本次相关位均为0。

## 0x21D：充电设备接口状态

- Message：`CP_evseStatus`
- 主要角色：车辆与充电设备之间的接口状态

| Signal | 中文含义 | 本次状态 |
|---|---|---|
| `CP_vehiclePrechargeRequired` | 车辆是否要求充电设备执行预充 | 0；本次未处于充电工况 |

`EVSE`是`Electric Vehicle Supply Equipment`，即电动汽车供电设备/交流充电设备。

## 0x229：换挡拨杆状态

- Message：`SCCM_rightStalk`
- 主要角色：右侧转向柱拨杆及换挡输入

| Signal | 中文含义 | 已观察状态与诊断意义 |
|---|---|---|
| `SCCM_gearStalkStatus` | 换挡拨杆操作状态 | TM3-003中`DOWN_2`两次对应D请求，`UP_2`两次对应R请求，松开后回`IDLE`；`UP_1`可作为拨杆机械行程的中间状态 |
| `SCCM_parkButtonStatus` | P挡按钮状态 | TM3-003中四次`1ST_DETENT`均对应回P请求，随后回`NOT_PRESSED` |

TM3-003中拨杆请求到 `DI_gear=D/R`约14.5～21.6 ms，实际挡位反馈后约9.2～9.5 ms，`DI_systemState`进入`ENABLE`。P按钮请求到实际回P约273.8～279.9 ms，回P与系统状态恢复`STANDBY`同一时间戳发生。

## 0x54F：换挡拨杆告警

- Message：`SCCM_alertMatrix`
- 主要角色：换挡拨杆信号电气与合理性故障

| Signal | 中文含义 |
|---|---|
| `SCCM_a021_gearStalkSignalInvalid` | 换挡拨杆信号无效 |
| `SCCM_a022_gearStalkOpenCircuit` | 换挡拨杆开路 |
| `SCCM_a023_gearStalkShortCircuit` | 换挡拨杆短路 |
| `SCCM_a024_gearStalkGenErr` | 换挡拨杆综合/一般错误 |

本次相关位均为0。

## 其他本次遇到的可解释ID

| CAN ID | Message / Signal | 中文含义 | 本次使用边界 |
|---:|---|---|---|
| `0x360` | `VCLEFT_a136_brakeSwitchMismatch` | 制动开关多路信号不一致告警 | 本次为0，仅作制动输入一致性旁证 |
| `0x7FF` | `GTW_numberHVILNodes` | 网关配置的HVIL节点数量 | 本次为4，属于配置量，不是实时HVIL健康度 |
| `0x123` | `UI_a019_ParkBrakeFault` | 驻车制动故障告警 | 本次为0 |
| `0x293` | `UI_parkBrakeRequest` | UI发出的驻车制动请求 | 本次为`IDLE` |
| `0x273` | `UI_driveStateRequest` | UI相关驱动状态请求 | 本次为`IDLE`，具体控制角色待验证 |
| `0x2C1` | `VCFRONT_pumpBatteryPowerOn` | 电池冷却液泵供电/开启状态 | 本次为1；不等于泵一定达到目标转速 |
| `0x2C1` | `VCFRONT_compStandbyHVNotReady` | 压缩机因高压未就绪而待命 | 本次为0；对象是空调压缩机，不是整车READY |
| `0x2C1` | `VCFRONT_compStandbySelfNotReady` | 压缩机自身未就绪而待命 | 本次为1 |
| `0x2A8` | `CMPD_ready` | 电动空调压缩机驱动就绪状态 | 不能解释为整车READY |
| `0x2B3` | `VCRIGHT_ptcHeaterHvacActNotReady` | PTC/HVAC执行未就绪状态 | 本次为0 |
| `0x31E` | `CP_a025_ledsOC` | 充电口LED开路/过流类告警，具体OC含义需结合注释验证 | 本次为0，与READY链无直接关系 |

## 本次存在冲突、不能直接采信的定义

| CAN ID | Signal | 冲突现象 | 当前处理 |
|---:|---|---|---|
| `0x212` | `BMS_isolationResistance` | 解码为0，但高压已建立、HVIL正常且无绝缘告警 | 不作为绝缘电阻实值 |
| `0x212` | `BMS_minPackTemperature` | 与0x312温度结果不一致 | 不写入温度基线 |
| `0x312` | `BMS_packTMin/BMS_packTMax` | 最高温度低于最低温度，违反物理约束 | DBC版本或位定义待验证 |
| `0x33A` | `UI_actualSOC/UI_usableSOC` | 3%与69%均和BMS SOC约46%冲突 | 0x33A相关定义暂不采信 |
| `0x118` | `DI_brakePedalState` | 解码为`INVALID`，但0x3C2清楚捕获制动按下 | 制动判断采用0x3C2 |
| `0x7AA` | `HVP_packCurrentMia` | 解码为1，但缺少与真实电流有效性/故障状态的一致证据 | 保留为待验证状态位 |

## 本次建立的控制关系

```text
0x3C2 制动开关按下
        │
        ├── 0x2D2 BMS充/放电能力边界释放
        │
        └── 0x118 电驱状态报文启动
                 │
                 └── DI_systemState进入STANDBY
                         │
                         ├── 0x108 扭矩指令 = 0
                         ├── 0x108 实际扭矩 = 0
                         └── 0x108 轴速 = 0
```

高压条件旁证：

```text
0x212 BMS接触器 = CLOSED
0x20A HVP接触器 = CLOSED
0x20A HVIL = STATUS_OK
0x7AA Pack电压 ≈ 348.3 V
0x7AA DC-link实际母线电压 ≈ 348.1–348.5 V
```

因此，本次样本描述的是“高压已经建立后，踩制动触发能力释放并使电驱进入待命”，不是完整的“预充—接触器闭合—READY”过程。

## 使用原则

- CAN ID和Signal名称来自第三方DBC，中文解释优先作为诊断语言映射，不视为官方定义。
- 枚举状态和值表需要同时满足动作一致性、系统一致性和物理合理性后，才能进入正常基线。
- 告警位为0只表示没有广播对应告警，不能替代对传感器、执行器和反馈链的验证。
- 调试报文和多路复用报文必须确认正确的多路复用页，不能把未出现的页解码成有效值。
- 后续每次实验继续在本文档中追加新ID；跨采集域或不同DBC来源的含义冲突应并列保留，并注明日期、采集域与证据等级。
