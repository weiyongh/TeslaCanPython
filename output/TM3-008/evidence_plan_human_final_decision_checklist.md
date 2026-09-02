# TM3-008 Evidence Plan 最终人工决策清单

状态：`SUPERSEDED_BY_HUMAN_DECISION / APPROVED / ASC_NOT_ANALYZED`。

> 最新人工修订（2026-09-02）：`UI_lockRequest`不再EXCLUDE，改为`P1 / CONSUMER_STATE_CANDIDATE`进入ASC验证；验证前禁止解释为“钥匙卡落锁REQUEST”，且不得作为ER-03独立充分证据。本修订优先于下文原始决策准备建议。

本清单基于已接受的Human Review Preparation整理。23项`ACCEPT`建议默认接受，但其中涉及P0关键链且存在语义边界的项目仍列在第二部分供人工确认。本文件不修改Draft，不是Review Override，也不产生Approved Plan。

## 一、必须逐项决定的10项

### 6项 NEEDS_CLARIFICATION

| Signal / ER / Role | Codex建议 | 关键理由 | 接受该建议的影响 | 不接受的风险 |
| --- | --- | --- | --- | --- |
| `VCLEFT_frontOccupancyStatus` / ER-02 / `FEEDBACK` | 保留为P0“离座反馈候选/可见性验证目标” | 与离座物理节点直接对应，但TM3-007无帧，且存在DBC/DLC适配不确定性 | 保留离座节点的直接候选；无帧或不适配时按GAP处理 | 排除后ER-02离座节点只能由门闩和外部记录间接支持 |
| `VCSEC_lockRequestType` / ER-03 / `REQUEST` | 保留，但由P0收窄为P1请求候选 | 枚举可能区分NFC锁止，但请求主体、发布层及保持方式未验证 | 可检查钥匙卡落锁请求类型，同时避免把名称当作事实 | 保持P0易夸大语义；完全排除则失去区分锁止来源的最佳DBC候选 |
| `VCFRONT_vehiclePowerState` / ER-01/04/07 / `SYSTEM_RESULT` | 保留，但由P0降为P1系统状态候选 | 可能表达车辆供电阶段，但不能证明是整车下电请求或命令 | 保留整车状态层交叉证据，不侵占REQUEST/COMMAND角色 | 保持P0或赋予请求角色会过度解释；排除则状态层只剩电驱/BMS代理 |
| `BMS_nmGoingToSleep` / ER-08/09 / 网络管理`SYSTEM_RESULT` | 保留为P1状态候选，不标为REQUEST或COMMAND | 仅凭名称无法判断是请求、命令还是内部状态 | 可与通信派生结果交叉验证BMS视角的网络阶段 | 赋予请求角色会虚构控制方向；排除则失去BMS网络管理视角 |
| `GTW_nmGoingToSleep` / ER-08/09 / 网络管理`SYSTEM_RESULT` | 保留为P1状态候选，不标为REQUEST或COMMAND | 字段名不足以确认其在网络管理中的控制层级 | 可与帧率、活跃ID和总线状态交叉 | 赋予命令角色会过度解释；排除则缺少网关侧阶段候选 |
| `GTW_chBusAsleep` / ER-08/09 / `CONSUMER_STATE` | 保持P2，仅在CH总线/采集域适配确认后使用 | 具备分域退出价值，但当前采集域是否覆盖CH总线未知 | 保留分域审计能力，不影响核心静默结论 | 无条件接受会把不可见域写成事实；排除则无法检查CH域候选状态 |

### 2项 REJECT

| Signal / ER / Role | Codex建议 | 关键理由 | 接受该建议的影响 | 不接受的风险 |
| --- | --- | --- | --- | --- |
| `BMS_hvState` / ER-01/04/05/07 / `SYSTEM_RESULT`或`EXECUTION_CANDIDATE` | 拒绝当前Draft行按现状批准；先纠正成熟度为低可信/语义验证失败边界，再决定保留或排除 | Draft写为`STRONGLY_SUPPORTED/HIGH`，但TM3-007正式结果为全程DOWN且`SEMANTIC_VALIDATION_FAILED` | 阻止把TM3-007早期候选成熟度迁移为TM3-008事实；仍可在纠正后作为验证目标 | 按现状接受会污染高压需求/状态链，并可能制造错误时序结论 |
| `PCS_dcdcMainState` / ER-01/06/07 / `EXECUTION_CANDIDATE` | 拒绝当前Draft行按现状批准；先纠正成熟度，再作为低可信候选或排除 | Draft写为`PARTIALLY_VALIDATED/MEDIUM`，但TM3-007正式结果为全程STANDBY且`SEMANTIC_VALIDATION_FAILED` | 避免将未经验证的枚举作为DCDC主执行证据 | 按现状接受可能把固定/错误枚举解释为DCDC退出过程 |

> 当前Review Override结构不能修改`semantic_status`、`confidence`或`evidence_requirement`。因此这两项不能通过仅覆盖Role/Priority来消除问题；人工应选择“先修订Draft后再Review”或“从本次Approved范围排除”。

### 1项最终EXCLUDE与1项后续人工变更

| Signal / ER / Role | Codex建议 | 关键理由 | 接受该建议的影响 | 不接受的风险 |
| --- | --- | --- | --- | --- |
| `UI_lockRequest` / ER-03 / `CONSUMER_STATE_CANDIDATE` | OVERRIDE为P1并进入ASC验证 | 最新人工决定保留该消费者状态候选，但禁止解释为钥匙卡落锁REQUEST | 增加UI层候选观察；不得作为ER-03独立充分证据 | 若忽略边界，可能误判请求主体并重复计算锁止证据 |
| `VCFRONT_vehicleStatusDBG` / ER-04/07/09 / 调试`SYSTEM_RESULT`候选 | EXCLUDE | MUX适用性未确认，与`VCFRONT_vehiclePowerState`及网络派生证据重叠，调试枚举易过度解释 | 简化状态链，避免未经验证的调试字段进入主时间线 | 保留会增加错误阶段标签和虚假状态机解释的风险 |

## 二、默认ACCEPT但需确认语义边界的P0关键候选

下列项目维持默认`ACCEPT`，但接受的对象是“受限角色下的验证候选”，不是Signal语义或TM3-008事实。

| Signal / ER / Role | Codex建议 | 关键理由 | 接受该建议的影响 | 不接受的风险 |
| --- | --- | --- | --- | --- |
| `CanIdLastSeenTime_derived` / ER-07/08 / `SYSTEM_RESULT` | ACCEPT，仅描述逐ID最后出现时间 | 是分批通信退出的关键P0派生证据，但ID停止出现不等于ECU断电 | 可建立当前采集域退出时间结构 | 排除后ER-08主要只剩总帧率和活跃ID，分批顺序能力明显下降 |
| `VCLEFT_frontLatchStatus` / ER-02/03/07 / `FEEDBACK` | ACCEPT，保留跨DBC位段验证和动作锚点边界 | 能反馈门闩状态，但不能证明人工动作时间、物理关严或车辆已锁 | 保留开门/关门状态链的P0反馈 | 排除后门状态缺少直接CAN候选；放宽边界则会形成循环时间证据 |
| `DI_systemState` / ER-01/04/07 / `EXECUTION` | ACCEPT，仅作为电驱系统执行状态 | 可观察ENABLE/STANDBY类变化，但不是整车READY、许可源或下电请求 | 保留电驱层P0执行状态 | 排除会丢失电驱退出层；角色扩大则会把局部系统状态当成整车决策 |
| `BMS_contactorState` / ER-01/05/07/09 / `EXECUTION` | ACCEPT，仅作为BMS接触器总状态 | 是高压执行链核心，但不能替代正负接触器细分或下游母线反馈 | 可判断总接触器状态序列 | 排除会削弱ER-05执行证据；过度使用会错误宣称下游已去电 |
| `PCS_dcdcHvBusVolt` / ER-05/06 / `PHYSICAL_RESPONSE_CANDIDATE` | ACCEPT为P0 Signal Validation目标，继续保持`SEMANTIC_VALIDATION_FAILED` | 是现有唯一直接PCS侧下游高压电压候选，但既有定量语义失败 | 保留验证ER-05物理闭环的机会；验证失败时ER-05继续保留GAP | 排除后当前没有下游电压Candidate；提升可信度则会制造错误高压物理结论 |
| `PCS_dcdc12VSupportStatus` / ER-01/06 / `EXECUTION` | ACCEPT，必须与低压物理反馈交叉 | 可表达12V支持状态，但不能单独证明DCDC物理输出 | 保留DCDC执行层P0候选 | 排除会削弱ER-06状态证据；单独使用会把枚举当成物理结果 |
| `PCS_dcdcLvBusVolt` / ER-01/06 / `PHYSICAL_RESPONSE_CANDIDATE` | ACCEPT，限定为PCS侧低压母线候选 | 跨DBC存在DLC/位段/缩放差异，且不是外部12V电池端实测 | 保留ER-06低压响应候选，同时维持外部测量GAP | 排除后低压物理响应只剩电流弱候选；放宽边界会虚构外部12V实测 |

## 三、无需再次逐项确认的默认ACCEPT项

除第二部分已单列者外，下列16项按Human Review Preparation建议默认接受，所有项目仍需Approved之后由ASC验证：

- `NetworkFrameRate_derived`、`ActiveCanIdCount_derived`
- `VCSEC_simpleLockStatus`、`VCSEC_vehicleLockStatus`
- `DI_gear`、`UI_readyForDrive`、`VCFRONT_12vStatusForDrive`
- `HVP_packContPositiveState`、`HVP_packContNegativeState`
- `BMS_packVoltage`、`PCS_dcdcHvBusDischargeStatus`、`PCS_dcdcLvOutputCurrent`
- `BMS_hvsBusAsleep`、`BMS_nmKeepAwakeReason`
- `GTW_VEHBusAsleep`、`GTW_nmKeepAwakeReason`

默认接受边界继续有效：0x20A保持多DBC/实验验证限制；Pack电压不是下游母线证据；网络状态只代表发布者/采集域视角；keep-awake原因只作`DIAGNOSTIC_CONTEXT`。

## 四、ER-10固定决定

ER-10继续保持外部证据GAP，不接受任何CAN Candidate替代：

- 不由CAN反推开门、关门、刷卡落锁或离车Observed Event；
- 不由锁止Signal替代后视镜、灯光或声音等物理反馈；
- 不由末段低通信替代“人员/钥匙远离且未操作App”的现场记录；
- 不形成精确“人工动作→CAN响应”延迟。

该决定不阻止后续分析CAN内部状态顺序，但会限制动作归因、自然休眠充分性和精确响应时延。

## 五、人工最终确认格式

人工可直接确认：

1. 是否接受23项默认ACCEPT及第二部分的语义边界；
2. 对6项`NEEDS_CLARIFICATION`逐项选择接受Codex收窄建议、另行Override或Exclude；
3. 对2项`REJECT`选择先修订Draft再Review，或Exclude；
4. `VCFRONT_vehicleStatusDBG`保持`EXCLUDE`；`UI_lockRequest`已由最新人工决定改为P1消费者状态候选；
5. 是否确认ER-10继续保持不可由CAN替代的GAP。

收到人工最终决定前，不创建`evidence_plan_review_overrides.csv`或`evidence_plan_approved.csv`，不读取ASC。
