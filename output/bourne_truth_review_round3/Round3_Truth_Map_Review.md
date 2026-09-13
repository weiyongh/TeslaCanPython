# Round 3 Truth / Map Review

## 1. 审阅边界

- 被评测对象为伯恩 `results/round_3/` 中的第三轮 HVAC 五次独立单轮复现分析，以及对应机器结果和分析脚本。
- 本审阅核对了 S0014～S0018 的会话元数据、事件时间、候选统计、转换统计及项目当前可用 DBC。
- 本审阅没有重写伯恩的分析结果，没有向伯恩 Workspace 写入文件，也没有把总部 DBC 或真值反馈给伯恩。
- 本轮用途应定义为：**HVAC 候选发现与跨轮复现验证**。它不是车辆故障诊断，也尚未形成可批准的车型正常基线。
- 本报告位于总部项目输出域。当前状态：`HQ REVIEW / NOT DELIVERED TO BOURNE`。

## 2. 总裁决

### 2.1 一句话结论

伯恩第三轮成功证明了若干 raw bit 在五个相同脚本会话中重复跟随 HVAC UI 总体启停，核心统计结果基本可信；但它没有利用已有 DBC 恢复字段边界和候选语义，也没有满足 Vehicle、Evidence Plan、Signal Validation 和正式报告门禁，因此只能作为 **Discovery/候选验证产物**，不能作为完成态 L3 分析报告。

### 2.2 分项裁决

| 审计项目 | 裁决 | 说明 |
|---|---|---|
| ASC与会话完整性 | `PASS` | 5个会话均为`COMPLETED`；共2,592,668帧；单会话时间轴单调，覆盖完整脚本周期。 |
| 稳态窗口设计 | `PASS` | 使用实际Event时间并设置保护区，适合判断OFF→ON→OFF稳态复现。 |
| 五轮逐轮验证 | `PASS` | 先在每轮内部判定，再求五轮交集，避免总体多数掩盖单轮失败。 |
| 两次翻转过滤 | `PASS_WITH_LIMITS` | 能排除大量过程内反复变化项，但不能证明候选是独立布尔Signal。 |
| 52/23/5统计结论 | `PASS_AS_RAW_OBSERVATION` | 可作为raw bit层观察保存；不能等同于52或23个独立语义Signal。 |
| 时延结论 | `PARTIAL` | 可区分近事件组与约数秒后的晚变化组；不足以比较0.2 s级先后顺序。 |
| DBC与字段边界审计 | `FAIL` | 多个候选已有直接DBC字段映射；连续量、枚举和MUX字段被拆成独立bit候选。 |
| Signal成熟度 | `FAIL` | 使用未定义的`B/C+`等级，没有映射到项目当前成熟度体系。 |
| Vehicle身份与追溯 | `FAIL` | 五个输入目录未发现Vehicle Marker，分析程序也没有读取Vehicle ID。 |
| 正式L3流程门禁 | `FAIL` | 未见Approved Evidence Plan、Evidence Assessment、RVM或标准正式四件套。 |
| 作为下一轮实验输入 | `PASS` | 可用于设计送风/A/C解耦实验及定向Signal验证。 |

## 3. 伯恩结论中成立的部分

### 3.1 五轮复现目标确实完成

伯恩把 S0014～S0018 当作五个单独会话，要求候选在每轮内部满足：

```text
OFF前 = OFF后 ≠ ON
+ 三个窗口最低纯度 ≥ 95%
+ 五轮变化方向一致
```

该方法比合并全部样本后计算总体多数更严格。第二轮五个优先候选均达到5/5、最低窗口纯度100%，且每轮全程只有两次翻转。因此以下事实成立：

> 第二轮五个优先raw bit在本次相同脚本、相近现场条件下得到五次重复支持。

这证明的是**同条件重复性**，不是跨温度、风量、SOC、车辆或软件版本的普适性。

### 3.2 两级筛选逻辑合理

第一层稳态筛选负责确认三个状态窗口的可分性；第二层全程翻转筛选排除稳态窗口恰好一致、但过程内频繁波动的字段。作为无DBC候选压缩方法，这一逻辑是有效的。

### 3.3 证据边界总体克制

伯恩正确指出：

- 多个同步bit不等于多个独立Signal；
- UI照片只证明显示与用户操作状态，不证明压缩机实际运行；
- 早、晚响应组不能直接命名为Request和Feedback；
- 下一步需要拆分“仅送风”和“A/C制冷”。

这些限制符合当前项目“位段可解不等于语义确认”的原则。

## 4. DBC Truth / Map审计

## 4.1 `0x20C`：已有HVAC请求与使能定义

项目当前 DBC 对 `0x20C` 给出如下字段：

| 伯恩候选 | DBC字段边界 | 当前审计解释 | 裁决 |
|---|---|---|---|
| `B1.b3` | bit 11，`VCRIGHT_hvacEvapEnabled` | 蒸发器/HVAC制冷使能候选 | `BOUNDARY_HIT / SEMANTIC_CANDIDATE` |
| `B1.b4` | bit 12，`VCRIGHT_conditioningRequest` | HVAC调节请求候选 | `BOUNDARY_HIT / SEMANTIC_CANDIDATE` |
| `B4.b1` | `VCRIGHT_hvacBlowerSpeedRPMReq`内部bit | 鼓风机转速请求连续量的一部分 | `OBSERVATION_HIT / BOUNDARY_MISS` |
| `B5.b0` | `VCRIGHT_hvacBlowerSpeedRPMReq`内部bit | 同一连续量的另一个量化bit | `OBSERVATION_HIT / BOUNDARY_MISS` |
| `B7.b3` | ONYX未覆盖；Model3CAN只定义到bit56附近的部分状态 | 实测DLC 8下可读，但字段语义未知 | `UNRESOLVED / DLC_CONFLICT` |

关键问题：伯恩将 `0x20C B1.b3` 继续统一称为“未知CAN字段”，低估了现有DBC证据。正确表达应为：

> `VCRIGHT_hvacEvapEnabled`第三方DBC定义与五轮启停事件时序一致，字段边界命中；具体控制角色及车型适配仍需解耦实验与独立执行证据验证。

`0x20C`还存在DBC版本冲突：ONYX定义DLC 7，`Model3CAN.dbc`定义DLC 8，而本次实测帧为DLC 8。该冲突必须进入Signal Validation记录，不能静默选用其中一份定义。

## 4.2 `0x282`：鼓风机反馈报文被拆成多个bit

`0x282 / VCLEFT_hvacBlowerFeedback`是复用报文。伯恩列出的五个强候选实际落在以下字段中：

| 伯恩候选 | DBC字段 | 字段性质 | 裁决 |
|---|---|---|---|
| `B0.b2` | `VCLEFT_hvacBlowerEnabled m0` | 独立1-bit使能 | `BOUNDARY_HIT` |
| `B0.b6` | `VCLEFT_hvacBlowerOutputDuty m0` | 多位连续量内部bit | `BOUNDARY_MISS` |
| `B1.b2` | `VCLEFT_hvacBlowerRPMTarget m0` | 多位目标转速内部bit | `BOUNDARY_MISS` |
| `B2.b1` | `VCLEFT_hvacBlowerRPMTarget m0` | 同一目标转速字段内部bit | `BOUNDARY_MISS` |
| `B3.b3` | `VCLEFT_hvacBlowerRPMActual m0` | 多位实际转速内部bit | `BOUNDARY_MISS` |

其中只有 `B0.b2` 可以作为独立布尔候选。其余bit证明对应多位物理量跨越了某些二进制量化边界，不能作为四条独立状态证据。

正式复核必须：

1. 先验证 `VCLEFT_blowerIndex == 0`；
2. 完整解码 `BlowerEnabled / OutputDuty / RPMTarget / RPMActual`；
3. 分别比较建立、稳定、退出及Target—Actual关系；
4. 检查 ONYX 与 `Model3CAN.dbc` 在Torque、FET温度等字段宽度和缩放上的版本冲突。

## 4.3 `0x2F3`：命中用户电源状态枚举内部bit

`0x2F3 B3.b2`对应bit 26，是三位字段 `UI_hvacReqUserPowerState` 的最低位，不是独立布尔Signal。

其相对人工事件近零时延变化，与“UI用户电源请求状态”候选角色相符，但应完整解码三位枚举值，验证OFF→ON→OFF状态码，而不能保留为 `B3.b2` 独立强候选。

## 4.4 其他已知或冲突定义

| CAN ID | 当前DBC情况 | 审计结论 |
|---|---|---|
| `0x1FA` | 项目实验DBC中用于车窗汇总候选；与本次HVAC同步的`B0.b3/b4`没有已确认HVAC定义 | 保留相关性观察，可能是共享状态编码、网关投影或未恢复字段；不可命名。 |
| `0x253` | 当前可见DBC对该报文存在长度/覆盖不足风险，而候选位于Byte 7 | 回到实测DLC与全部DBC定义审计后再判断。 |
| `0x2A1` | 当前总部DBC未发现可靠HVAC定义 | `TIMING_ONLY`候选；晚变化不足以证明压缩机反馈。 |
| `0x2A7` | ONYX将其定义为`UI_csaRoadCurvature` | 与本次HVAC同步提示DBC域/版本不适配或条件共变，禁止按道路曲率解释。 |
| `0x2BF` | `tesla_powertrain.dbc`将其定义为`DAS_control` | 与HVAC事件同步可能来自总线/版本冲突或连续字段量化，禁止直接套用DAS语义。 |
| `0x323` | 当前总部DBC未发现稳定适配定义 | 保留未知状态组合观察。 |
| `0x361` | 当前总部DBC未发现稳定适配定义 | 保留未知状态组合观察。 |

`0x2A7`和`0x2BF`尤其说明：相同CAN ID的第三方名称不能跨总线、车型版本或采集域直接移植。应先核对实测DLC、报文周期、完整payload结构和事件闭环。

## 5. 方法与程序审计

### 5.1 正确之处

- 使用实际Event触发时间，不以名义脚本时间直接作为事实；
- 三个稳态窗口都有明确保护区；
- 每轮单独计算mode和purity；
- 对全会话翻转次数做二次筛选；
- 保存逐会话详情、字节上下文和全部转换，具备基本复查能力；
- 第二轮结果单独定向复核，没有被新一轮排序冲淡。

### 5.2 `strict_two_transition_pass`的真实含义有限

程序把“事件附近找到一次转换且全程转换总数等于2”定义为强候选。这个条件能证明bit级OFF/ON/OFF二态闭合，但不能排除：

- 枚举字段内部code bit；
- 连续量跨过量化阈值；
- 多个bit属于同一字段；
- 其他系统条件与HVAC操作共同变化；
- 网关或显示层复制状态。

因此 `strict_two_transition_pass=True`应解释为：

> `RAW_BIT_TWO_EDGE_REPRODUCED`

不应解释为“已发现强语义Signal”。

### 5.3 转换匹配没有显式验证方向

程序在人工事件前5秒至后10秒范围内选择距离事件最近的转换，但没有在匹配时显式要求转换方向等于候选的OFF→ON或ON→OFF方向。对于全程恰好两次翻转且稳态闭合的候选，通常不会改变最终判断，但审计字段应保存 `from_value / to_value`，并由程序明确校验方向，避免以后复杂会话误配。

### 5.4 时延只能用于粗粒度分组

ASC文件头只有整秒精度，程序以文件头墙钟减 `session.start_clock` 计算偏移。结果中已经出现负时延，说明人工事件与CAN时间轴的亚秒对齐不可用于ECU级延迟。

因此：

- `0.204 s`与`0.246 s`不可比较先后；
- “开启后约0.2～0.25 s建立”应改为“与人工操作在约±1 s对齐范围内近同时变化”；
- `0x2A1/0x2BF`约1.4～5.0 s的晚变化与近事件组存在可保留的粗粒度分离；
- 任何负时延不能写成车辆预知操作，应归入时间对齐不确定度。

### 5.5 会话独立性的措辞需要收窄

五轮是五个独立记录会话，但连续发生在同一车辆、相近环境和相同操作配置下。它们提供重复测量支持，但不是跨环境、跨车辆或统计意义上的完全独立样本。

建议用语：

> “五个单独采集会话中的同条件重复复现。”

## 6. 车辆身份与证据追溯审计

当前五个输入目录未发现单一无后缀Vehicle Marker，分析程序也没有读取Vehicle ID。按项目当前《采集身份与追溯约定》，不能从目录名、历史背景或DBC猜测车型。

因此本轮结论的当前适用范围只能写为：

> S0014～S0018五个指定采集会话；Vehicle ID未通过当前合同验证。

在补齐来源可审计的Vehicle Marker前，不得升级为 `TESLA-M3-SOP5` 车型基线。若原始导入包确有Vehicle Marker、只是伯恩归档时遗漏，应恢复其来源与校验记录，而不是依据已知车辆档案反向伪造。

此外，当前结果没有保存输入ASC哈希、DBC来源哈希和分析运行标识。若要作为正式可追溯证据，应补充这些机器审计字段。

## 7. Signal成熟度裁决

伯恩使用 `C+ → B` 表达跨轮提升，但没有提供等级定义。该等级不能替代项目当前Signal成熟度。

建议按当前证据暂定：

| 候选 | 建议成熟度 | 理由 |
|---|---|---|
| `0x20C / VCRIGHT_hvacEvapEnabled` | `PARTIALLY_VALIDATED` | 字段边界已知，五轮启停时序一致；仍缺仅送风/A/C解耦和压缩机物理证据。 |
| `0x20C / VCRIGHT_conditioningRequest` | `PARTIALLY_VALIDATED` | DBC字段边界与五轮事件对应；具体Request层级仍需验证。 |
| `0x282 / VCLEFT_hvacBlowerEnabled m0` | `PARTIALLY_VALIDATED` | 五轮二态闭合；须确认MUX及与RPM反馈关系。 |
| `0x282 / BlowerOutputDuty/RPMTarget/RPMActual` | `QUANTITATIVE_SEMANTICS_UNVALIDATED` | 当前只验证了内部bit变化，尚未完成完整数值解码与物理合理性检查。 |
| `0x2F3 / UI_hvacReqUserPowerState` | `PARTIALLY_VALIDATED` | 命中完整枚举字段位置，但当前只分析了其中一个code bit。 |
| `0x2A1 B5.b0` | `TIMING_ONLY_VALID` | 五轮晚变化复现，无可靠字段语义和独立物理证据。 |
| `0x2BF B5.b3` | `TIMING_ONLY_VALID` | 五轮晚变化复现，但存在第三方DBC域/语义冲突。 |
| 其余raw bit | `INSUFFICIENT_EVIDENCE` | 可保存观察，暂不足以单独赋予Signal语义。 |

这些成熟度只适用于本次审计范围，不自动写回车型级知识或正式DBC。

## 8. 控制关系重构

基于当前DBC映射与实测观察，本轮最多支持以下部分可观测链：

```text
人工操作 / HVAC UI状态
        ↓
UI用户电源状态候选
0x2F3 / UI_hvacReqUserPowerState
        ↓
调节请求与蒸发器使能候选
0x20C / VCRIGHT_conditioningRequest
0x20C / VCRIGHT_hvacEvapEnabled
        ↓
鼓风机使能、目标与实际响应候选
0x282 / VCLEFT_hvacBlowerEnabled
0x282 / OutputDuty / RPMTarget / RPMActual
        ↓
车内实际送风、压缩机运行、出风温度和舱温结果
本轮无直接充分证据
```

该链并不证明每一级之间的因果先后，也没有直接确认压缩机实际运行。`0x2A1/0x2BF`可以作为晚响应候选继续观察，但当前不能插入为压缩机执行反馈。

## 9. 对伯恩第三轮报告的修订要求

若只把第三轮定位为候选发现报告，最小修订如下：

1. 把“23个强候选”改为“23个跨五轮复现的二态raw bit”，避免Signal语义暗示。
2. 增加完整字段归并表，至少恢复 `0x20C`、`0x282`、`0x2F3` 的DBC边界。
3. 对MUX字段强制记录实际MUX值。
4. 增加实测DLC和各DBC定义DLC的对照表。
5. 将`0.2～0.25 s建立`改为“约±1 s范围内近事件变化”。
6. 明确`B/C+`只是伯恩内部候选等级，或直接改用项目统一成熟度。
7. 把“独立实验”收窄为“独立记录会话中的同条件重复”。
8. 写明Vehicle ID未通过当前合同验证。
9. 保存ASC、DBC、脚本和输出文件哈希。

若要升级为正式L3实验分析，还必须满足：

- 明确用途、Case、ER和OR；
- 存在冻结且人工批准的Evidence Plan；
- 完成Signal Validation和Evidence Assessment；
- 形成Report View Model；
- 通过共享Renderer生成标准人读四件套；
- 明确完成状态、基线有效性、最小补采及是否进入诊断树。

## 10. 最小下一步实验

伯恩建议的解耦顺序总体正确：

```text
全关
→ 仅送风
→ 保持送风并开启A/C
→ 仅关闭A/C、保持送风
→ 全关
```

下一轮应重点验证：

1. `UI_hvacReqUserPowerState`是否只跟随总电源；
2. `VCRIGHT_conditioningRequest`与`VCRIGHT_hvacEvapEnabled`能否被“仅送风”和“A/C开启”分离；
3. `VCLEFT_hvacBlowerEnabled/RPMTarget/RPMActual`是否只跟随送风；
4. `0x2A1/0x2BF`是否只在A/C制冷执行时建立；
5. 是否能增加压缩机实际运行、出风温度或其他车外/独立物理证据；
6. 所有目标Signal是否完成DBC来源、DLC、MUX、位段、缩放和完整状态转换核验。

## 11. 最终裁决

### 可以保留

- 5/5同条件重复复现事实；
- 52个第一层raw bit候选；
- 23个全程两边沿raw bit候选；
- 第二轮五个优先候选全部通过第三轮复核；
- 近事件组与数秒晚变化组的粗粒度区别；
- 下一轮送风/A/C解耦方向。

### 必须降级或改写

- “23个强候选”不能等同23个独立Signal；
- 第二轮五个候选不能全部继续称为无DBC未知字段；
- `0x282`和`0x2F3`内部bit必须归并回完整字段；
- 0.2 s级延迟不能用于ECU先后排序；
- `B/C+`不能替代正式Signal成熟度；
- 未验证Vehicle ID前不能形成车型基线。

### 当前状态

```text
ROUND_3_RAW_REPRODUCTION: PASSED
DBC_FIELD_RECOVERY: FAILED / REWORK_REQUIRED
SIGNAL_VALIDATION: INCOMPLETE
VEHICLE_IDENTITY: NOT_VALIDATED
FORMAL_L3_ANALYSIS: NOT_ADMISSIBLE
NEXT_EXPERIMENT_INPUT: USABLE
DELIVERY_TO_BOURNE: HOLD
```
