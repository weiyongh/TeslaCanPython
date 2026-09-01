# TM3-009 DBC关键Signal覆盖与可读性

## 核心Signal表

| 控制树角色 | Signal | Message | CAN ID | 单位 | 本次观测范围/状态 | 是否变化 | 解码状态 | 本次用途 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 驾驶输入 | DI_accelPedalPos | DI_systemStatus | 0x118 | % | 0～25.6 | 是 | 可读 | 识别真实踩下、调节及归零时刻 |
| 状态门 | DI_gear | DI_systemStatus | 0x118 | enum/raw | D / P | 是 | 可读 | 区分P/STANDBY与D/ENABLE |
| 状态门 | DI_systemState | DI_systemStatus | 0x118 | enum/raw | ENABLE / STANDBY | 是 | 可读 | 区分P/STANDBY与D/ENABLE |
| 状态门 | DI_tractionControlMode | DI_systemStatus | 0x118 | enum/raw | NORMAL | 否 | 可读 | 保留状态观测；不单凭字段名判定实际阻止驱动或介入 |
| 仲裁后请求 | DI_torqueCommand | DI_torque | 0x108 | Nm | -622～684 | 是 | 可读 | 最终电驱请求；不等同电门原始请求 |
| 执行反馈 | DI_torqueActual | DI_torque | 0x108 | Nm | -622～710 | 是 | 可读 | 与同帧请求配对，保留瞬态差值 |
| 运动反馈 | DI_axleSpeed | DI_torque | 0x108 | RPM | -1.7～279.4 | 是 | 可读 | 轴速，与扭矩同帧；非电机转子转速 |
| 物理结果 | DI_vehicleSpeed | DI_speed | 0x257 | kph | -0.16～34.72 | 是 | 可读 | 首次运动、达速、调速与停车 |
| 能源交叉验证 | DI_elecPower | DI_power | 0x266 | kW | -14～13.5 | 是 | 可读 | 电驱电功率，与Pack功率相互印证 |
| 能源交叉验证 | BMS_packVoltage | BMS_hvBusStatus | 0x132 | V | 343.85～350 | 是 | 可读 | 保存电压/电流对应关系，同帧派生Pack功率 |
| 能源交叉验证 | BMS_packCurrent | BMS_hvBusStatus | 0x132 | A | -37.6～41 | 是 | 可读 | 保存电压/电流对应关系，同帧派生Pack功率 |
| 状态条件 | BMS_socUI | BMS_socStatus | 0x292 | % | 32.2～32.5 | 是 | 可读 | 本次SOC背景，不外推整个SOC范围 |
| 能力背景 | DI_sysDrivePowerMax | DI_systemPower | 0x268 | kW | 246～247 | 是 | 可读 | 能力候选，保留数值；未验证约束阈值 |
| 能力背景 | DI_sysRegenPowerMax | DI_systemPower | 0x268 | kW | 91～92 | 是 | 可读 | 能力候选，保留数值；未验证约束阈值 |

## DBC异常与可读性说明

- 制动DBC版本差异、缺帧和不可读项保留在工程审计。
