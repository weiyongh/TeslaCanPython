# S0009 伯恩盲态自训练—DBC镜像评分

## 评分边界

- 镜像输入是已冻结的[05_frozen_blind_hit_points.md](05_frozen_blind_hit_points.md)，其SHA-256为`43905cccd9e38ac84ca3ea9b64942d06f783626c61223459f042205814b98025`。
- 镜像阶段才读取工程现有DBC；不修改冻结点位。
- `HIT`：field边界与角色明显吻合；`PARTIAL`：位置/功能有明确对应但边界或角色过宽；`MISS`：DBC有明确反证；`UNKNOWN`：DBC未覆盖或定义冲突。

## 逐项镜像

| # | CAN ID / Field | Result | DBC镜像摘要 |
| -: | :--- | :--- | :--- |
| 1 | `0x21D` byte0 bit3 | PARTIAL | 落在`CP_proximity`多bit field内，连接角色吻合，但单bit边界不完整。 |
| 2 | `0x21D` byte2 bits0:2 | PARTIAL | 与`CP_cableType`边界吻合，属连接装置属性，不足以支持“充电过程阶段”。 |
| 3 | `0x21D` byte3 bit5 | PARTIAL | 位于`CP_cableCurrentLimit` 7-bit连续/限额field内，与连接相关但非独立状态bit。 |
| 4 | `0x21D` byte4 bit7 | PARTIAL | 位于`CP_evseChargeType` 2-bit field内，充电类型相关，非独立会话bit。 |
| 5 | `0x21D` byte6 bits4:5 | UNKNOWN | 现有DBC版本在该区域存在`CP_gbState`/`CP_gbdcChargeAttempts`/`CP_acChargeState`边界差异，无法单一镜像。 |
| 6 | `0x43D` byte0 bits0:2 | HIT | 精确命中`CP_hvChargeStatus_log` 3-bit field，且充电状态机角色吻合。 |
| 7 | `0x43D` byte1 bit6 | PARTIAL | 位于`CP_acChargeCurrentLimit_log` 8-bit field内，是充电限额而非独立窗口bit。 |
| 8 | `0x43D` byte5 bits0:2 | PARTIAL | bits0:1命中`CP_evseChargeType_log`，bit2未覆盖；边界只部分吻合。 |
| 9 | `0x43D` byte5 bit5 | UNKNOWN | 现有DBC未覆盖该bit。 |
| 10 | `0x25D` byte1 bits6:7 | HIT | 精确命中`CP_chargeCableState` 2-bit field，连接离散角色吻合。 |
| 11 | `0x25D` byte3 bits3:5 | MISS | 落在`CP_apsVoltage` 8-bit测量field内，不是连接阶段离散field。 |
| 12 | `0x25D` byte5 bit0 | MISS | 位于`CP_UHF_controlState` 4-bit field内，DBC不支持充电会话角色。 |
| 13 | `0x204` byte0 bits0:2 | PARTIAL | 位于`PCS_chgMainState` 4-bit field内，状态机角色吻合但少一bit。 |
| 14 | `0x204` byte0 bit6 | MISS | 属于`PCS_gridConfig` 2-bit field，非充电会话保持状态。 |
| 15 | `0x204` byte3 bits3:5 | MISS | 属于`PCS_chgMaxAcPowerAvailable` 8-bit能力量，非会话/执行阶段field。 |
| 16 | `0x204` byte7 bit0 | HIT | 精确命中`PCS_chgPwmEnableLine`，充电执行窗口角色吻合。 |
| 17 | `0x20A` byte5 bit4 | PARTIAL | 位于`HVP_fcLinkAllowedToEnergize` 2-bit field内，高压允许角色吻合，单bit边界不完整。 |
| 18 | `0x212` byte1 bit3 | PARTIAL | 位于`BMS_uiChargeStatus` 3-bit field内，充电状态相关，但单bit与物理连接的声明过窄。 |
| 19 | `0x212` byte3 bit6 | MISS | 精确定义为`BMS_keepWarmRequest`，不是充电执行状态。 |
| 20 | `0x212` byte6 bit6 | UNKNOWN | DBC版本在该区域的能力量/计数器边界不一致，无法支持会话角色。 |
| 21 | `0x132` byte0:1 LE | HIT | 精确命中16-bit Pack电压field；能源侧慢变连续量判断成立。 |
| 22 | `0x132` byte2:3 signed LE | PARTIAL | 命中Pack电流区域和能源流向角色，但DBC对位宽、符号和offset有版本差异。 |
| 23 | `0x132` byte4:5 LE | HIT | 精确命中16-bit未滤波电流field，充电过程连续量角色成立。 |
| 24 | `0x264` byte0:1 LE | PARTIAL | 主体命中14-bit充电输入电压，但申报16 bit跨入下一电流field。 |
| 25 | `0x264` byte2:3 LE | PARTIAL | 跨越充电线电流尾部与8-bit输入功率，角色相关但非单一field。 |
| 26 | `0x264` byte4 bits5:7 | PARTIAL | 位于10-bit充电交流限流field内，与充电能力相关，非阶段field。 |
| 27 | `0x264` byte5 bit0 | PARTIAL | 同样属于10-bit充电交流限流field，非独立状态bit。 |
| 28 | `0x252` byte0:1 LE | PARTIAL | 精确命中`BMS_maxRegenPower`，是能力量；变化形态命中，但未识别出功能角色。 |
| 29 | `0x252` byte2:3 LE | PARTIAL | 精确命中`BMS_maxDischargePower`，是能力量；边界对，语义仍过宽。 |
| 30 | `0x228` byte3 bits0:1 | MISS | 位于电子驻车制动故障原因field，与插枪语义无关。 |
| 31 | `0x288` byte3 bits0:1 | MISS | 对称地位于另一侧电子驻车制动故障原因field。 |
| 32 | `0x2A8` byte5 bit7 | MISS | 位于`CMPD_inputHVVoltage` 11-bit连续量内，非连接状态。 |
| 33 | `0x2E8` byte5 bit7 | MISS | 精确定义为`EPBR_okToPark`，非充电连接状态。 |
| 34 | `0x2AA` byte0 | UNKNOWN | 当前可用DBC不足以可靠判断该field。 |
| 35 | `0x2EC` byte0 | UNKNOWN | 当前可用DBC不足以可靠判断该field。 |
| 36 | `0x232` byte0 bit6 | PARTIAL | 精确定义为`BMS_gpoHasCompleted`，与高压/接触器过程有关，但不是泛化充电执行状态。 |
| 37 | `0x232` byte1 bit1 | UNKNOWN | 当前DBC未覆盖该bit。 |
| 38 | `0x24A` byte0 bit1 | UNKNOWN | 当前DBC未覆盖该bit；不因message为ADAS即直接判MISS。 |
| 39 | `0x472` byte4 bit4 | UNKNOWN | 当前可用DBC不足以可靠判断该field。 |
| 40 | `0x49D` byte6 bit5 | UNKNOWN | 当前可用DBC不足以可靠判断该field。 |

## 最终比分

```text
S0009 Bourne Blind Self-Training — DBC Mirror Score

Total:   40
HIT:      5
PARTIAL: 17
MISS:     9
UNKNOWN:  9
```

`HIT + PARTIAL = 22 / 40`，即55%的冻结点位与DBC存在明确位置/功能对应；其中严格field边界与角色双命中为5项。

## 训练判断

1. **主战场定位成功**：盲搜较集中地命中`0x21D / 0x43D / 0x25D / 0x204 / 0x132 / 0x264`等充电或能源主报文区域。
2. **地形判断强，精确边界偏弱**：17项PARTIAL大部分来自“真实Signal内部某个bit随数值变化”，说明事件相关性能找到矿区，但尚不会稳定勾勒矿区边界。
3. **对称镜像是危险诱饵**：`0x228/0x288`等左右对称报文因同步响应被高信心选中，但DBC明确显示它们是其他系统的field。
4. **下一版算法的核心不是增加候选**：应先做字段边界推断，对同一byte中的进位、回绕、枚举联合状态和连续量相关bit进行合并，再进行语义角色判断。
