# TM3-007 待审Signal证据表

状态：`DRAFT / NOT_APPROVED / ASC_NOT_ANALYZED`。本表只由实验目的、控制树片段、脚本与DBC定义推导，尚未读取本次ASC。

## 1. Draft Evidence Plan

| 顺序 | Signal/派生量 | CAN ID | 控制树节点/本实验角色 | 建议 | 建议报告位置 | DBC来源 | 当前语义状态 | 不确定性/审核理由 |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | `NetworkFrameRate_derived` | 派生 | 休眠/唤醒网络反馈 | P0 | 核心时间线+网络唤醒摘要 | 原始ASC统计 | `PARTIALLY_VALIDATED` | 低报文率只支持本采集域低通信候选，不等于整车休眠 |
| 20 | `ActiveCanIdCount_derived` | 派生 | 控制器分批唤醒代理 | P1 | 网络唤醒摘要 | 原始ASC统计 | `PARTIALLY_VALIDATED` | 只表示当前采集域活跃ID数 |
| 30 | `VCLEFT_frontLatchStatus` | `0x102` | 驾驶门闩反馈；区分开门/关门 | P0 | 核心时间线+核心Signal表 | ONYX；Model3CAN有同ID不同位段版本 | `PARTIALLY_VALIDATED` | 跨DBC位段冲突；需以完整OPENED/CLOSED转换审计 |
| 40 | `VCLEFT_frontOccupancyStatus` | `0x30A` | 驾驶员入座反馈 | P0 | 核心时间线+核心Signal表 | ONYX | `PARTIALLY_VALIDATED` | 必须确认本采集域可见且枚举方向与事件一致 |
| 50 | `DI_brakePedalState` | `0x118` | 制动条件输入 | P0 | 核心时间线+核心Signal表 | ONYX；多DBC同位段支持 | `STRONGLY_SUPPORTED` | 只表示制动状态，不自动等同制动为READY请求 |
| 60 | `DI_gear` | `0x118` | 挡位反馈/可驱动状态门 | P0 | 核心时间线+核心Signal表 | ONYX；多DBC同位段支持 | `STRONGLY_SUPPORTED` | 是挡位反馈，不代表原始换挡手柄请求 |
| 70 | `DI_systemState` | `0x118` | 电驱状态；ENABLE候选 | P0 | 核心时间线+控制关系 | ONYX；多DBC支持 | `STRONGLY_SUPPORTED` | ENABLE是电驱系统状态，不单独等同整车READY |
| 80 | `UI_readyForDrive` | `0x353` | 仪表/用户界面可驱动反馈候选 | P1 | READY交叉验证表 | ONYX；Model3CAN同时定义`0x00C`/位段版本 | `PARTIALLY_VALIDATED` | 消费者/显示层反馈，非高压或驱动许可源头；DBC版本冲突 |
| 90 | `BMS_hvState` | `0x212` | BMS高压状态；COMING_UP/UP_FOR_DRIVE | P0 | 核心时间线+高压链 | ONYX；ETH参考定义同位段 | `STRONGLY_SUPPORTED` | 需验证枚举转换顺序，不只看终值 |
| 100 | `BMS_contactorState` | `0x212` | BMS接触器总状态 | P0 | 核心时间线+高压链 | ONYX；ETH参考定义同位段 | `STRONGLY_SUPPORTED` | 总状态不能代替正/负接触器独立反馈 |
| 110 | `BMS_packVoltage` | `0x132` | Pack端高压反馈 | P0 | 核心时间线+高压链 | ONYX；已有TM3-015 Golden Case实验级支持 | `STRONGLY_SUPPORTED` | Pack端电压可在主接触器断开时仍存在；不单独证明外部母线已上电 |
| 120 | `PCS_dcdcHvBusVolt` | `0x2B4` | PCS所见高压母线反馈 | P0 | 核心时间线+高压链 | ONYX | `QUANTITATIVE_SEMANTICS_UNVALIDATED` | 需与BMS/HVP状态及物理范围闭环；定量缩放尚待本实验验证 |
| 130 | `HVP_hvilStatus` | `0x20A` | HVIL安全条件 | P1 | 安全条件表+高压链 | ONYX；Model3CAN/ETH参考定义冲突 | `QUANTITATIVE_SEMANTICS_UNVALIDATED` | `0x20A`跨DBC位段/DLC版本必须并列解析；不得默认一版 |
| 140 | `BMS_isolationResistance` | `0x212` | 绝缘安全条件背景 | P1 | 安全条件表 | ONYX；ETH参考定义同位段 | `PARTIALLY_VALIDATED` | 可见数值不自动等同厂家上电许可阈值；SNA需排除 |
| 150 | `HVP_packContNegativeState` | `0x20A` | 负接触器执行反馈候选 | P1 | 高压专项时间线 | ONYX；Model3CAN/ETH参考版本冲突 | `QUANTITATIVE_SEMANTICS_UNVALIDATED` | 需执行第三方DBC Signal Validation；未验证前不进入确认结论 |
| 160 | `HVP_packContPositiveState` | `0x20A` | 正接触器/预充执行反馈候选 | P1 | 高压专项时间线 | ONYX；Model3CAN/ETH参考版本冲突 | `QUANTITATIVE_SEMANTICS_UNVALIDATED` | 需验证OPEN/PRECHARGE/CLOSED类序列与母线电压对应 |
| 170 | `PCS_dcdcMainState` | `0x224` | DCDC状态机/执行反馈 | P0 | 核心时间线+DCDC表 | ONYX | `PARTIALLY_VALIDATED` | 需与电压/电流反馈同时验证，不仅凭枚举名称 |
| 180 | `PCS_dcdc12VSupportStatus` | `0x224` | 12 V支持状态 | P1 | DCDC专项表 | ONYX | `PARTIALLY_VALIDATED` | 可能与主DCDC状态角色重叠，需本次时序区分 |
| 190 | `PCS_dcdcLvBusVolt` | `0x2B4` | 低压母线执行反馈 | P0 | 核心时间线+DCDC表 | ONYX | `PARTIALLY_VALIDATED` | 是PCS侧低压母线值，不等同外部仪表实测12 V电压 |
| 200 | `PCS_dcdcLvOutputCurrent` | `0x2B4` | DCDC输出响应 | P1 | DCDC专项表 | ONYX；ETH参考定义在符号/位宽上不同 | `QUANTITATIVE_SEMANTICS_UNVALIDATED` | 跨DBC定义冲突；先做方向和物理范围验证 |
| 210 | `DI_keepAliveRequest` | `0x118` | 电驱保持唤醒/保持请求候选 | P2 | 工程审计+状态条件 | ONYX | `INSUFFICIENT_EVIDENCE` | 名称不足以确认其为整车唤醒请求；建议仅审计 |
| 220 | `GTW_BMP_AWAKE_PIN` | `0x113` | 网关唤醒代理候选 | P2 | 工程审计+网络唤醒摘要 | Model3CAN，ONYX未覆盖 | `INSUFFICIENT_EVIDENCE` | 非ONYX主定义；需确认报文/DLC适配且不等同整车唤醒 |
| 230 | `UI_lockRequest` | `0x273` | 解/落锁请求候选 | P2 | 工程审计+车身输入表 | Model3CAN，ONYX未覆盖 | `INSUFFICIENT_EVIDENCE` | UI来源/请求主体不明，不能自动等同B柱钥匙卡解锁 |

## 2. 本轮需要人工审核

1. 建议批准为P0核心：`NetworkFrameRate_derived`、`VCLEFT_frontLatchStatus`、`VCLEFT_frontOccupancyStatus`、`DI_brakePedalState`、`DI_gear`、`DI_systemState`、`BMS_hvState`、`BMS_contactorState`、`BMS_packVoltage`、`PCS_dcdcHvBusVolt`、`PCS_dcdcMainState`、`PCS_dcdcLvBusVolt`。
2. 建议批准为P1交叉/专项：`ActiveCanIdCount_derived`、`UI_readyForDrive`、`HVP_hvilStatus`、`BMS_isolationResistance`、`HVP_packContNegativeState`、`HVP_packContPositiveState`、`PCS_dcdc12VSupportStatus`、`PCS_dcdcLvOutputCurrent`。
3. 建议仅工程审计：`DI_keepAliveRequest`、`GTW_BMP_AWAKE_PIN`、`UI_lockRequest`；未经覆盖不进入主控制结论。
4. 请确认`0x20A/HVP_contactorState`三项是否允许按“多DBC并列Signal Validation候选”进入正式分析，但不允许在本实验内自动升级为车型级定义。
5. 本次未发现现场记录/触发CSV。请确认是否接受“脚本时间只用于定位，最终动作时刻不作独立Observed Event”的证据边界。

审核时可直接按“全部接受”，或对任一Signal给出 `ACCEPT / OVERRIDE / EXCLUDE`及有效角色、优先级、报告位置。

