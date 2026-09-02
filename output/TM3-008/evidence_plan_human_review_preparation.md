# TM3-008 Evidence Plan Human Review Preparation

状态：`REVIEW_PREPARATION / NOT_APPROVED / ASC_NOT_ANALYZED`。

本文件是对`evidence_plan_draft.csv`的逐项审核建议，不是人工Review Override，也不产生Approved Plan。建议状态含义：

- `ACCEPT`：候选与Requirement有实际对应关系，可按本文限定角色进入人工审核；不代表已在TM3-008中得到事实支持。
- `REJECT`：当前Draft中的成熟度、Requirement绑定或证据能力存在实质错误，不应按现状批准；需人工决定修订或排除。
- `NEEDS_CLARIFICATION`：候选可能有价值，但角色、适配范围或成熟度在批准前必须收窄。
- `EXCLUDE`：重复、弱相关或不能提供独立证据，建议不进入Approved Plan。

P0/P1/P2只表示TM3-008中的重要程度；不表示Signal语义可信度。

## 逐项Review表

| # | Candidate | ER | 建议 | 建议Evidence Role | Review理由与批准边界 |
| ---: | --- | --- | --- | --- | --- |
| 1 | `NetworkFrameRate_derived` | ER-08/09 | ACCEPT | `SYSTEM_RESULT` | 直接回答当前采集域通信量是否下降/静默；只能描述采集域，不能推出整车休眠、ECU断电或高压下电。 |
| 2 | `ActiveCanIdCount_derived` | ER-08/09 | ACCEPT | `SYSTEM_RESULT` | 可与帧率区分“少数ID仍活跃”和整体高通信；属于采集域代理，不是控制器数量或整车网络覆盖。 |
| 3 | `CanIdLastSeenTime_derived` | ER-07/08 | ACCEPT | `SYSTEM_RESULT` | 对分批停止通信有独立价值；它表示报文最后出现时间，不等同ECU关机时间，也不直接证明控制因果。 |
| 4 | `VCLEFT_frontOccupancyStatus` | ER-02 | NEEDS_CLARIFICATION | `FEEDBACK` | 与离座节点直接相关，但TM3-007中该报文无帧，且DBC间存在DLC/适配差异。批准时应标为“占座反馈候选/可见性验证目标”，不能预设本域可见。 |
| 5 | `VCLEFT_frontLatchStatus` | ER-02/03/07 | ACCEPT | `FEEDBACK` | 能承担门闩开/关状态反馈；不能作为独立人工动作时间，也不能单独证明车门物理完全关严或车辆已锁。跨DBC位段冲突必须验证。 |
| 6 | `VCSEC_lockRequestType` | ER-03 | NEEDS_CLARIFICATION | `REQUEST` | 字段枚举包含NFC锁止候选，与钥匙卡动作具有针对性；但请求主体、发布层和事件保持方式尚未验证。建议保留但由P0收窄为P1请求候选，不能单独证明实际刷卡。 |
| 7 | `VCSEC_simpleLockStatus` | ER-03/07 | ACCEPT | `FEEDBACK` | 可承担安全控制器发布的聚合锁止反馈；不能替代门锁机械执行或后视镜/灯光/声音等外部反馈。 |
| 8 | `VCSEC_vehicleLockStatus` | ER-03 | ACCEPT | `CONSUMER_STATE` | 枚举可能保留锁止方式和结果信息，适合作为请求类型/简化锁状态的交叉状态；不应与`simpleLockStatus`一起被计为两份独立物理锁止证据。 |
| 9 | `UI_lockRequest` | ER-03 | EXCLUDE | `CONSUMER_STATE`（若仅审计） | UI发布者与B柱钥匙卡请求绑定不明，且已有VCSEC请求/反馈候选；无法承担独立落锁请求证据，重复且弱相关。必要时只在非Approved探索中观察。 |
| 10 | `DI_gear` | ER-01/04 | ACCEPT | `FEEDBACK` | 可确认起始及过程中的P挡反馈，是ER-01状态门；它不能证明ER-04的下电请求或需求撤销。批准理由必须明确其对ER-04仅为背景约束。 |
| 11 | `DI_systemState` | ER-01/04/07 | ACCEPT | `EXECUTION` | 可观察电驱系统ENABLE/STANDBY等执行状态变化；不是整车READY、下电请求、许可源头或高压需求本身。 |
| 12 | `UI_readyForDrive` | ER-01/04 | ACCEPT | `CONSUMER_STATE` | 可作为显示/消费层READY交叉反馈；不得提升为`PERMISSION`、`COMMAND`或高压控制源。0x353/0x00C定义冲突需按实测适配。 |
| 13 | `VCFRONT_vehiclePowerState` | ER-01/04/07 | NEEDS_CLARIFICATION | `SYSTEM_RESULT` | 与车辆供电阶段相关，但DBC名称不足以证明其为整车下电控制请求。建议由P0降为P1系统状态候选，先验证状态序列和发布范围。 |
| 14 | `VCFRONT_vehicleStatusDBG` | ER-04/07/09 | EXCLUDE | `SYSTEM_RESULT`（调试候选） | MUX适用性未确认，与`VCFRONT_vehiclePowerState`及网络派生结果高度重叠，且调试状态名称容易诱发过度解释，无法承担独立证据作用。 |
| 15 | `VCFRONT_12vStatusForDrive` | ER-04/06 | ACCEPT | `CONSUMER_STATE` | 可作为12V侧可驱动/退出状态交叉反馈；不是DCDC执行状态或低压物理响应，不得单独满足ER-06。 |
| 16 | `BMS_hvState` | ER-01/04/05/07 | REJECT | `SYSTEM_RESULT` / `EXECUTION_CANDIDATE` | 当前Draft标为`STRONGLY_SUPPORTED/HIGH`不成立：TM3-007正式覆盖结果为全程DOWN且`SEMANTIC_VALIDATION_FAILED`。不得迁移TM3-007早期Draft成熟度。只有先纠正成熟度/边界后才可作为低可信验证候选，不能按现状批准。 |
| 17 | `BMS_contactorState` | ER-01/05/07/09 | ACCEPT | `EXECUTION` | 能承担BMS接触器总执行状态；TM3-007只提供候选成熟度参考，TM3-008仍须验证完整退出序列。总状态不能代替正负接触器独立状态或下游母线物理响应。 |
| 18 | `HVP_packContPositiveState` | ER-05/07 | ACCEPT | `EXECUTION_CANDIDATE` | 对正接触器退出顺序有价值；批准必须保留0x20A多DBC/DLC冲突和`THIS_EXPERIMENT_ONLY` Signal Validation边界，不写成已确认执行反馈。 |
| 19 | `HVP_packContNegativeState` | ER-05/07 | ACCEPT | `EXECUTION_CANDIDATE` | 对负接触器退出顺序有价值；与正接触器同样保持多DBC、完整枚举序列和物理闭环要求，不自动继承TM3-007结论。 |
| 20 | `BMS_packVoltage` | ER-01/05 | ACCEPT | `PHYSICAL_RESPONSE`（Pack侧背景） | 定量Pack端电压已有较强参考价值，但接触器断开后Pack端仍可保持高压。只用于起始Pack状态和两侧边界对照，不能证明下游母线退出。 |
| 21 | `PCS_dcdcHvBusVolt` | ER-05/06 | ACCEPT | `PHYSICAL_RESPONSE_CANDIDATE` | ER-05确实需要下游母线反馈，因此保留为P0验证目标；但既有`SEMANTIC_VALIDATION_FAILED`必须原样保留。除非本实验完成原始位段、多DBC、物理范围和接触器/放电时序闭环，否则不得用于支持ER-05。 |
| 22 | `PCS_dcdcHvBusDischargeStatus` | ER-05/06/07 | ACCEPT | `EXECUTION_CANDIDATE` | 名称指向母线放电状态而非命令源，暂按执行状态候选；不能由枚举名称推断实际放电电流或母线已经去电，须与下游电压闭环。 |
| 23 | `PCS_dcdcMainState` | ER-01/06/07 | REJECT | `EXECUTION_CANDIDATE` | 当前Draft的`PARTIALLY_VALIDATED/MEDIUM`高于现有正式依据：TM3-007中全程STANDBY且`SEMANTIC_VALIDATION_FAILED`。需先纠正成熟度后方可作为低可信状态机验证目标，不能按现状批准为P0核心证据。 |
| 24 | `PCS_dcdc12VSupportStatus` | ER-01/06 | ACCEPT | `EXECUTION` | 可承担DCDC 12V支持执行状态；TM3-007结果仅提高候选价值，TM3-008仍须验证退出/保持序列，并与低压物理反馈交叉。 |
| 25 | `PCS_dcdcLvBusVolt` | ER-01/06 | ACCEPT | `PHYSICAL_RESPONSE_CANDIDATE` | 能提供PCS侧低压母线反馈，但跨DBC存在DLC/位段/缩放差异；不是外部12V电池端实测，不能替代ER-10或外部测量GAP。 |
| 26 | `PCS_dcdcLvOutputCurrent` | ER-06 | ACCEPT | `PHYSICAL_RESPONSE_CANDIDATE` | 可用于DCDC输出响应方向与量级验证；符号、位宽和缩放存在冲突，定量语义未验证，不能单独证明DCDC退出。 |
| 27 | `BMS_nmGoingToSleep` | ER-08/09 | NEEDS_CLARIFICATION | `SYSTEM_RESULT`（网络管理状态） | 字段名不能确定它是请求、命令还是内部状态。不得标为REQUEST；可保留为网络管理状态候选，与派生通信结果交叉验证。 |
| 28 | `BMS_hvsBusAsleep` | ER-08/09 | ACCEPT | `CONSUMER_STATE` | 表示BMS所见总线状态候选，而不是整车全部网络事实；需要与当前采集域帧率、活跃ID及报文适配共同验证。 |
| 29 | `BMS_nmKeepAwakeReason` | ER-08/09 | ACCEPT | `CONSUMER_STATE` / `DIAGNOSTIC_CONTEXT` | 只用于末段仍通信时提供替代解释；不能单独证明保持唤醒原因、下电失败或休眠完成。建议保持P2审计位置。 |
| 30 | `GTW_nmGoingToSleep` | ER-08/09 | NEEDS_CLARIFICATION | `SYSTEM_RESULT`（网络管理状态） | 同样无法仅凭名称区分REQUEST/COMMAND/STATE。可作为网关网络管理状态候选，不得赋予整车下电命令角色。 |
| 31 | `GTW_VEHBusAsleep` | ER-08/09 | ACCEPT | `CONSUMER_STATE` | 可作为网关所见VEH总线休眠反馈；不能证明底盘、以太网、低压电源或所有ECU均已下电。 |
| 32 | `GTW_chBusAsleep` | ER-08/09 | NEEDS_CLARIFICATION | `CONSUMER_STATE` | 有分域退出价值，但当前采集域是否覆盖CH总线尚不清楚；建议保持P2，仅在报文和采集域适配确认后使用。 |
| 33 | `GTW_nmKeepAwakeReason` | ER-08/09 | ACCEPT | `CONSUMER_STATE` / `DIAGNOSTIC_CONTEXT` | 仅作为持续通信的候选解释和工程审计；枚举名称不能替代外部无干预记录，也不能形成故障结论。 |

## Review建议统计

| 建议 | 数量 | Candidate |
| --- | ---: | --- |
| ACCEPT | 23 | 1、2、3、5、7、8、10、11、12、15、17、18、19、20、21、22、24、25、26、28、29、31、33 |
| NEEDS_CLARIFICATION | 6 | 4、6、13、27、30、32 |
| REJECT | 2 | 16、23 |
| EXCLUDE | 2 | 9、14 |

`REJECT`不是说对应物理节点不重要，而是当前Draft行的成熟度与正式既有结果冲突，不能以现状进入Approved Plan。当前Review Override结构不能修改`semantic_status/confidence/evidence_requirement`，因此人工决定前需要明确：修订Draft内容后再Review，或将该候选排除；不能用角色/优先级Override掩盖成熟度错误。

## ER-05：下游高压母线证据专项

### 可以承担的部分

- `BMS_contactorState`：接触器总执行状态，不能代表下游母线电压。
- `HVP_packContPositiveState`、`HVP_packContNegativeState`：正负接触器执行候选，保持0x20A多DBC和实验验证边界。
- `PCS_dcdcHvBusDischargeStatus`：主动放电执行状态候选，不能证明放电实际完成。
- `BMS_packVoltage`：Pack侧电压背景，用于明确“电池包仍有高压”与“下游母线是否退出”是两个问题。

### 当前唯一直接下游电压候选

`PCS_dcdcHvBusVolt`仍是ER-05唯一直接的PCS侧下游高压电压Candidate，但其边界必须保持：

- 既有状态为`SEMANTIC_VALIDATION_FAILED`；
- P0只表示ER-05需要这种证据，不表示该Signal可信；
- 必须核对原始位段、DLC、多DBC定义、物理范围、接触器和主动放电时序；
- 未形成闭环时，ER-05只能支持“接触器状态退出”，不能支持“下游高压母线已定量下降/去电”。

因此ER-05目前存在实质性的`PHYSICAL_RESPONSE GAP`，不能由Pack端电压补齐。

## ER-08/09：网络退出与静默专项

主证据应是三个采集域派生结果：

1. `NetworkFrameRate_derived`：通信总量；
2. `ActiveCanIdCount_derived`：同时活跃的ID数量；
3. `CanIdLastSeenTime_derived`：各报文分批停止出现的时间结构。

BMS/GTW网络管理字段只提供控制器视角的交叉状态或替代解释，不应替代实际通信统计。所有结论必须使用“本采集域通信下降、低通信或静默候选”措辞，不得写成：

- 整车全部ECU已经下电；
- 整车所有CAN/以太网均已休眠；
- 低压电源已经关闭；
- 某ID停止出现即对应ECU已经断电。

若600秒仍有报文，应先描述哪些ID仍活跃、帧率是否稳定、是否发生再唤醒，并检查keep-awake候选；不能直接评为故障。

## ER-10：外部证据GAP

ER-10保持无Signal Candidate。以下内容只能由现场记录、App实际触发CSV或独立物理记录提供：

- 实际开门、离座、关门和刷卡落锁时刻；
- 落锁的后视镜、灯光或声音反馈；
- 人员和全部钥匙离车距离及时间；
- 等待期间是否打开Tesla App、靠近车辆或发生其他唤醒；
- 采集停止前状态和停止方式是否污染末段。

门闩、锁止状态、网络变化或其他CAN边沿均不得反推为Observed Event后再用于证明同一动作。该GAP会限制精确动作响应时延和“自然休眠”充分性，但不阻止分析CAN内部状态转换。

## 角色超过实际证据能力的项目

存在，需在人工决定时收窄：

| Candidate | 当前可能的过度角色 | 允许的最大角色 |
| --- | --- | --- |
| `DI_gear` | 驱动/高压需求撤销 | P挡`FEEDBACK`与ER-01状态门 |
| `UI_readyForDrive` | READY许可或高压控制源 | `CONSUMER_STATE` |
| `VCFRONT_vehiclePowerState` | 整车下电请求/命令 | 待验证的`SYSTEM_RESULT` |
| `VCFRONT_12vStatusForDrive` | DCDC执行或低压物理响应 | `CONSUMER_STATE` |
| `BMS_hvState` | 已确认高压需求/执行状态 | 纠正成熟度后的低可信状态候选 |
| `BMS_packVoltage` | 接触器下游母线物理响应 | Pack侧`PHYSICAL_RESPONSE`背景 |
| `PCS_dcdcHvBusDischargeStatus` | 下电命令或母线已去电证明 | `EXECUTION_CANDIDATE` |
| `BMS/GTW_nmGoingToSleep` | 网络休眠REQUEST/COMMAND | 未定性的网络管理`SYSTEM_RESULT`候选 |
| `BMS/GTW_*BusAsleep` | 整车休眠结果 | 单一控制器视角的`CONSUMER_STATE` |
| `*KeepAwakeReason` | 已确认唤醒根因 | `DIAGNOSTIC_CONTEXT` |

当前33项中没有足够定义可直接赋予确定的`PERMISSION`或`COMMAND`角色；也没有Signal可以替代ER-10外部证据。人工Review不应为了填满REQUEST—PERMISSION—COMMAND—EXECUTION链路而提升候选角色。

## 人工决定入口

人工可基于本表逐项决定：

- 对`ACCEPT`项确认是否接受建议角色和边界；
- 对`NEEDS_CLARIFICATION`项决定收窄角色/优先级后接受，或排除；
- 对`REJECT`项决定先修订Draft成熟度再审核，或排除；
- 对`EXCLUDE`项确认排除，或说明保留的独立证据价值。

在人工决定落地前，不创建`evidence_plan_review_overrides.csv`或`evidence_plan_approved.csv`，不读取ASC，不生成Evidence Assessment。
