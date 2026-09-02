# TM3-008 Evidence Plan Context

- 状态：`ANALYZED / EVIDENCE_ASSESSED / PARTIAL`。
- 用途：正常基线数据采集；目标是建立本车关门、落锁后的条件化下电过程映射，不进行车辆故障判断。
- 车辆：Tesla Model 3，上海产2021款，2021年5月出厂，标准续航，55 kWh，后驱。
- 实验问题：车辆从READY、P挡稳定状态开始，驾驶员离座并开门、关门但暂不落锁、随后用钥匙卡落锁后，可驱动/高压需求、高压接触器与母线、DCDC/低压支持以及当前采集域通信按什么顺序退出；在本次观察期内能否形成无再唤醒的通信静默候选。
- Scope：`THIS_EXPERIMENT_ONLY`；当前仅建立待人工审核的证据合同。DBC定义只用于提出候选，不是本次实验事实；所有候选均须在Approved之后由ASC验证。
- 系统边界：整车下电协同。边界内包括驾驶门/占座/锁止反馈、车辆/电驱状态、高压需求与接触器执行、PCS DCDC响应、网络管理及采集域通信结果；人工动作、钥匙距离、App操作、后视镜/灯光/声音、外部12 V读数和采集器是否干扰休眠属于边界外证据。
- 主验证线：离座/开门/关门/落锁外部动作与车身反馈 → 可驱动或高压需求撤销候选 → 高压接触器退出及下游母线响应 → DCDC/低压支持状态变化 → 控制器/网络分批停止通信 → 本采集域静默候选。
- 重要非对称边界：TM3-008不是TM3-007上电序列的时间反演。落锁、高压退出、DCDC变化和网络休眠可以由不同策略和延时决定；Pack端电压在接触器断开后仍可存在，不能当作下游高压母线退出的单独证据。
- 时间边界：脚本中的30/40/60/70/120/300/600秒均为Planned Time。当前没有现场记录或App实际触发时间CSV；不得用CAN变化反推人工动作时刻并循环证明动作响应，也不得形成精确“人工动作→CAN响应”延迟。
- 完成判据边界：脚本/指导要求起始READY稳定、开门/离座/关门/落锁有实际时间标记、落锁后不少于10分钟无干预，并记录高压/DCDC退出及通信下降。缺少实际时间和无干预记录时，相关Requirement必须降为`INSUFFICIENT_EVIDENCE`或保留GAP，不能由ASC存在替代。
- 审核边界：33项Draft Candidate已于2026-09-02完成人工Review；经最新人工修订，32项进入有效Approved范围，1项标记`EXCLUDE`。Approved范围固定为`THIS_EXPERIMENT_ONLY`，不提升Signal成熟度或写回车型级知识。ASC已在Approved门后分析，Evidence Assessment已形成；正式四件套尚未生成。

## Human Review结果

- 23项默认`ACCEPT`。
- 6项原`NEEDS_CLARIFICATION`按收窄方案批准，其中`VCSEC_lockRequestType`与`VCFRONT_vehiclePowerState`降为P1；BMS/GTW going-to-sleep字段只作为网络管理状态候选，不作为REQUEST或COMMAND。
- `BMS_hvState`修正为`SEMANTIC_VALIDATION_FAILED / LOW`，重新Review后以P1低可信高压专项/审计候选保留。
- `PCS_dcdcMainState`修正为`SEMANTIC_VALIDATION_FAILED / LOW`，重新Review后以P1低可信DCDC专项/审计候选保留。
- `UI_lockRequest`按最新人工决定以`P1 / CONSUMER_STATE_CANDIDATE`进入ASC验证，位置为`BODY_INPUT_TABLE+ENGINEERING_AUDIT`；验证前禁止解释为“钥匙卡落锁REQUEST”，且不得作为ER-03独立充分证据。
- `VCFRONT_vehicleStatusDBG`标记`EXCLUDE`。
- ER-10继续保持不可由CAN Candidate替代的外部证据GAP。

## ASC Analysis结果入口

- 输入身份：依据原始文件起始时间、用户确认的12:34左右落锁/12:44:00结束及600秒脚本，TM3-008确定为组合源`input/can_20260831113240开关门采集.asc`的0～660秒。已生成标准独立输入`input/can_20260831113240_TM3-008_关门落锁完整下电采集.asc`，时间戳保持从0开始；源660秒之后的TM3-007段未纳入分析。
- 完整性：标准片段解析592949帧、284个CAN ID、损坏帧0；首帧0秒，最后一帧295.8383秒，295.8383～660秒为采集域末段无帧窗口，并非文件截断。
- 完成状态：`PARTIAL`。开门、关门、NFC落锁/锁止反馈、Ready消费者状态退出、高压/DCDC退出、网络分层退出与末段静默均已捕获；P挡、离座占座反馈、直接请求/许可层、ER-05可靠下游母线定量证据及外部现场证据仍有缺口。
- Evidence Assessment：ER-03、ER-06、ER-08为`SUPPORTED`；ER-01、ER-02、ER-04、ER-05、ER-07、ER-10为`INSUFFICIENT_EVIDENCE`；ER-09为`NOT_OBSERVED`。
- 机器证据入口：`output/TM3-008/machine_evidence/analysis_summary.json`、`evidence_assessment.csv`、`key_events.csv`、`signal_validation_assessment.csv`、`network_activity_1s.csv`及关联逐帧证据。

## Evidence Requirements

| ID | 需要证明的事项 | 充分性要求 | 当前候选覆盖 | 缺口时评定 |
| --- | --- | --- | --- | --- |
| ER-01 | 起始为READY、P挡且高压/DCDC支持稳定的参考窗口 | 独立现场状态记录；CAN内至少有P挡、可驱动/电驱状态、高压接触器状态和DCDC支持的相互一致稳定窗口 | 有多层DBC候选；缺独立现场记录 | 仅有CAN时最多建立“CAN内部上电稳定候选”，不确认外部READY事实 |
| ER-02 | 驾驶员离座与驾驶门打开/关闭反馈可观察 | 独立动作锚点，加占座和门闩完整状态转换；两者缺一时明确部分可观测 | 门闩与占座DBC候选存在 | 无独立锚点时不计算人工动作响应；占座不可读时保留离座节点GAP |
| ER-03 | 关门未锁状态与钥匙卡落锁后的锁止结果可区分 | 关门反馈、落锁Observed Event、锁止请求类型/锁状态反馈及外部落锁反馈至少形成请求—反馈交叉验证 | VCSEC请求/状态及UI请求候选存在 | DBC名称或锁状态单项不能证明B柱钥匙卡请求；无外部反馈时为部分证据 |
| ER-04 | 可驱动/驱动与高压需求在离座、关门、落锁后如何撤销 | 起始与后续车辆/电驱/高压状态转换相互一致；区分控制请求、执行状态和消费者显示 | 电驱、VCFRONT、UI、BMS状态候选存在 | 当前没有已确认的“整车下电请求”直接Signal；不得由P挡或显示层单项反推内部决策 |
| ER-05 | 高压接触器退出及下游高压母线响应 | BMS总接触器或正负接触器状态序列，加接触器下游电压/放电响应；冲突定义须并列验证 | 接触器、PCS高压母线和主动放电候选存在 | `BMS_packVoltage`仅是Pack端背景，不能代替下游母线；若PCS定量语义不成立则保留物理响应GAP |
| ER-06 | DCDC与低压支持的退出或保持过程 | DCDC状态/支持状态与PCS侧低压电压、电流方向和时序相互一致；最好有外部12 V实测 | PCS状态、电压、电流候选存在 | 无外部12 V测量时只评价PCS侧反馈；枚举或缩放不闭合时执行Signal Validation |
| ER-07 | 车身反馈、需求撤销、高压、DCDC和通信退出的先后关系 | 各层至少一个经验证的事件；按CAN内部时序描述，不把时间先后自动升级为控制因果 | 由ER-02至ER-08候选共同覆盖，无单一Signal可证明 | 任一层不可观测时保留节点并标记直接/部分/无观测，不补造完整链路 |
| ER-08 | 控制器/网络是否分批停止通信 | 全局帧率、活跃ID、逐ID最后出现时间和至少一个网络管理候选相互支持 | 三项派生指标及BMS/GTW网络管理候选存在 | 只证明当前采集域通信变化，不外推整车全部网络或ECU断电 |
| ER-09 | 末段是否形成持续、无再唤醒的通信静默候选 | 落锁后不少于10分钟无干预；末段帧率/活跃ID稳定低位或为零；无后续恢复，并记录停止采集前状态 | 派生指标与总线睡眠候选存在 | 无独立无干预记录时只称“本采集域末段低通信/静默候选”；600秒仍有报文不等于故障 |
| ER-10 | Planned、Observed与CAN Event时间可分离，且确认无外部唤醒干扰 | App触发CSV或现场记录，包含实际开门、关门、落锁、离车、接近/停止及App/钥匙干扰 | **GAP：无DBC/CAN Signal可替代** | 保持`INSUFFICIENT_EVIDENCE`；禁止从CAN反推Observed Event后循环证明 |

## 当前不能证明的事项

- 不能仅凭本采集域静默证明整车全部网络、全部ECU或低压系统已经完全休眠。
- 不能仅凭落锁相关Signal名称证明实际使用了B柱钥匙卡，也不能补出实际人工动作时间。
- 不能把P挡、`UI_readyForDrive`变化或某个电驱状态单独解释为整车内部下电请求或高压需求源头。
- 不能用Pack端电压证明接触器下游母线已经去电。
- 不能在没有外部12 V测量时声明低压电池端电压或DCDC物理输出已经独立实测。
- 不能把“600秒仍有报文”直接解释为下电失败或车辆故障。
- Approved Plan只定义分析边界；Signal的实际命中、变化和成熟度以当前`machine_evidence`中的Signal Validation与Evidence Assessment为准。

## 相比TM3-007暴露的结构观察

现有Evidence Plan的Signal级Draft、Review Override、Approved和Evidence Assessment状态足以承载TM3-008，不需要修改共享结构。TM3-008更依赖两类非单Signal证据：一是逐CAN ID最后出现时间/帧率等派生网络证据，二是外部无干预与实际动作记录。它们可分别作为`derived`候选和Requirement级GAP表达。

当前结构的限制是Draft CSV只能登记候选Signal/派生量，不能把“外部证据来源但当前缺失”作为独立行，也不能单独表达一个Requirement由多层Signal共同满足的充分性逻辑。本轮通过`evidence_plan_context.md`固定ER充分性和GAP，不修改`evidence_plan.py`、Renderer、Golden Contract或方法论。
