# TM3-010 DBC关键Signal覆盖与可读性

## 核心Signal表

| 控制树角色 | Signal | Message | CAN ID | 单位 | 本次观测范围/状态 | 是否变化 | 解码状态 | 本次用途 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 驾驶输入 | DI_accelPedalPos | DI_systemStatus | 0x118 | % | 0.0～25.6 | True | 可读 | 识别驾驶输入及匀速调节。 |
| 状态门 | DI_gear | DI_systemStatus | 0x118 | enum | — | True | 可读 | 确认实验处于D挡驱动状态。 |
| 状态门 | DI_systemState | DI_systemStatus | 0x118 | enum | — | True | 可读 | 确认驱动系统处于实验适用状态。 |
| 状态门 | DI_tractionControlMode | DI_systemStatus | 0x118 | enum | — | False | 可读 | 观察牵引控制状态，避免把特殊介入误作正常稳态。 |
| 仲裁后请求 | DI_torqueCommand | DI_torque | 0x108 | Nm | -622.0～794.0 | True | 可读 | 观察仲裁后的电驱扭矩请求。 |
| 执行反馈 | DI_torqueActual | DI_torque | 0x108 | Nm | -622.0～838.0 | True | 可读 | 与同帧请求比较，验证执行跟随。 |
| 运动反馈 | DI_axleSpeed | DI_torque | 0x108 | RPM | -1.3～349.1 | True | 可读 | 提供动力侧运动反馈，并与扭矩同帧对应。 |
| 物理结果 | DI_vehicleSpeed | DI_speed | 0x257 | km/h | -0.16～43.44 | True | 可读 | 识别目标速度带、连续稳定窗口及速度波动。 |
| 能源交叉验证 | DI_elecPower | DI_power | 0x266 | kW | -14.0～14.5 | True | 可读 | 提供电驱能源侧响应。 |
| 能源交叉验证 | BMS_packVoltage | BMS_hvBusStatus | 0x132 | V | 343.81～350.07 | True | 可读 | 记录高压背景，并与Pack电流同帧派生Pack功率。 |
| 能源交叉验证 | BMS_packCurrent | BMS_hvBusStatus | 0x132 | A | -38.3～45.5 | True | 可读 | 观察Pack充放电方向和幅度，并参与同帧Pack功率计算。 |
| 状态条件 | BMS_socUI | BMS_socStatus | 0x292 | % | 32.5～32.7 | True | 可读 | 记录当前实验SOC适用条件。 |
| 能力背景 | DI_sysDrivePowerMax | DI_systemPower | 0x268 | kW | 246.0～247.0 | True | 可读 | 作为驱动能力背景观察，不直接解释为本次实际限制阈值。 |
| 能力背景 | DI_sysRegenPowerMax | DI_systemPower | 0x268 | kW | 91.0～92.0 | True | 可读 | 作为回收能力背景观察，不直接解释为本次实际限制阈值。 |

## DBC异常与可读性说明

- DBC版本差异、INVALID与字段长度细节见baseline_evidence CSV。
