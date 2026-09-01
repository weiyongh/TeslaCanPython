# TM3-010 待审Signal证据表

| Signal | 本实验角色 | 建议优先级 | 建议报告位置 | 推导理由 | 语义状态 | 判断置信度 | 人工审核 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DI_accelPedalPos | 驾驶输入 | P0 | CORE_TIMELINE+CORE_SIGNAL_TABLE | 由本次稳定匀速命题、车辆电驱边界、控制链和能源交叉验证线推导 | 已确认 | HIGH | 无需 |
| DI_gear | 状态门 | P2 | CONDITION_SUMMARY+CORE_SIGNAL_TABLE | 由本次稳定匀速命题、车辆电驱边界、控制链和能源交叉验证线推导 | 已确认 | HIGH | 无需 |
| DI_systemState | 状态门 | P2 | CONDITION_SUMMARY+CORE_SIGNAL_TABLE | 由本次稳定匀速命题、车辆电驱边界、控制链和能源交叉验证线推导 | 已确认 | HIGH | 无需 |
| DI_tractionControlMode | 状态门 | P2 | CONDITION_SUMMARY+CORE_SIGNAL_TABLE | 由本次稳定匀速命题、车辆电驱边界、控制链和能源交叉验证线推导 | 强候选 | MEDIUM | 需要：STATE_APPLICABILITY_UNCERTAIN |
| DI_torqueCommand | 仲裁后请求 | P0 | CORE_TIMELINE+CORE_SIGNAL_TABLE | 由本次稳定匀速命题、车辆电驱边界、控制链和能源交叉验证线推导 | 已确认 | HIGH | 无需 |
| DI_torqueActual | 执行反馈 | P0 | CORE_TIMELINE+CORE_SIGNAL_TABLE | 由本次稳定匀速命题、车辆电驱边界、控制链和能源交叉验证线推导 | 已确认 | HIGH | 无需 |
| DI_axleSpeed | 运动反馈 | P0 | CORE_TIMELINE+CORE_SIGNAL_TABLE | 由本次稳定匀速命题、车辆电驱边界、控制链和能源交叉验证线推导 | 已确认 | MEDIUM | 需要：REPORT_POSITION_AMBIGUOUS |
| DI_vehicleSpeed | 物理结果 | P0 | CORE_TIMELINE+CORE_SIGNAL_TABLE | 由本次稳定匀速命题、车辆电驱边界、控制链和能源交叉验证线推导 | 已确认 | HIGH | 无需 |
| DI_elecPower | 能源交叉验证 | P1 | CORE_TIMELINE+CORE_SIGNAL_TABLE | 由本次稳定匀速命题、车辆电驱边界、控制链和能源交叉验证线推导 | 强候选 | MEDIUM | 需要：DBC_VERSION_CONFLICT+CROSS_MAINLINE_EVIDENCE |
| BMS_packVoltage | 能源交叉验证 | P1 | CORE_TIMELINE+CORE_SIGNAL_TABLE | 由本次稳定匀速命题、车辆电驱边界、控制链和能源交叉验证线推导 | 已确认 | MEDIUM | 需要：REPORT_POSITION_AMBIGUOUS |
| BMS_packCurrent | 能源交叉验证 | P1 | CORE_TIMELINE+CORE_SIGNAL_TABLE | 由本次稳定匀速命题、车辆电驱边界、控制链和能源交叉验证线推导 | 已确认 | HIGH | 需要：CROSS_MAINLINE_EVIDENCE |
| BMS_socUI | 状态条件 | P2 | CONDITION_SUMMARY+CORE_SIGNAL_TABLE | 由本次稳定匀速命题、车辆电驱边界、控制链和能源交叉验证线推导 | 已确认 | HIGH | 无需 |
| DI_sysDrivePowerMax | 能力背景 | P2 | CAPABILITY_SUMMARY+CORE_SIGNAL_TABLE | 由本次稳定匀速命题、车辆电驱边界、控制链和能源交叉验证线推导 | 强候选 | MEDIUM | 需要：PROXY_OBSERVATION |
| DI_sysRegenPowerMax | 能力背景 | P2 | CAPABILITY_SUMMARY+CORE_SIGNAL_TABLE | 由本次稳定匀速命题、车辆电驱边界、控制链和能源交叉验证线推导 | 强候选 | MEDIUM | 需要：PROXY_OBSERVATION |
| Pack功率(同帧V×I派生) | 能源交叉验证 | P1 | CORE_TIMELINE+ANALYSIS_WINDOW | 由同一0x132帧的电压和电流计算，不是DBC原生Signal | 已确认 | HIGH | 无需 |
