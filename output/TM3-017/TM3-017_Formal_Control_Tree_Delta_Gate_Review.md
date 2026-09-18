# TM3-017 正式控制树增量 Gate Review

**Experiment：** `TM3-017`

**Round：** `S0030`

**Vehicle：** `TESLA-M3-SOP5`

**用途：** 正常基线的正式控制树增量审核

**状态：** `APPROVED`

**审核日期：** 2026-09-15

**信息边界：** `STRICT_NO_DBC_RAW_PAYLOAD_ONLY`

**正式控制树：** 已按本Gate最小增量写入

## 1. Tree Gate结论

本轮Evidence达到正式控制树准入标准的最小增量，不是新增一条已识别的内部控制链，而是补入两个外部可观察Node、确认一条带未观测区域的系统级控制Relationship，并给既有实际交流输入与高压充电运行态增加本车实验级Evidence。

拟议正式增量为：

```text
[新增] 操作者充电电流设置（外部输入）
       ↓  TG-R01：SUPPORTED
[新增] 车辆接受并保持的充电电流设置（外部可观察状态）
       ↓
       [边界注释：车辆内部处理区域未观测，不拆分、不命名]
       ↓  TG-R02：SUPPORTED_SYSTEM_LEVEL_CONTROL_RELATIONSHIP
[既有] OBC交流输入端实际电流 IAC_actual
       ↓  TG-R03：SUPPORTED_CONDITIONED_STATE_TRANSITION
[既有] 高压充电运行态在新水平持续稳定

Condition：全过程保持同一连续高压充电运行态。
Structural constraint：设置接受状态与实际响应状态不得合并。
```

这个增量不改变既有通用慢充树中`AEVSE`、`A₂`、`IAC_target`、OBC功率级或保护分支的定义，也不声称TM3-017已经把这些通用Node投射到本车可识别变量。

## 2. Gate准入原则

本次使用以下最小准入标准：

1. Node必须由已审核现场Evidence直接观察，或是既有正式Node得到新的车型实验支持；仅由逻辑需要推定的内部环节不作为新正式Node。
2. Relationship必须在本轮相反动作中表现方向一致、可逆，并具有稳定结果；时序相关而因果方向不唯一的关系不得准入。
3. Condition必须是本轮实际成立且决定Relationship适用范围的车辆状态；实验记录条件与未施加工况不伪装成控制条件。
4. 匿名raw行为只可作为Evidence附件。数字相似、先后顺序或跨Round共变均不足以赋予控制Role。
5. 既有通用控制树中的理论Node不能因为“结构上合理”而自动获得本车Evidence身份。

## 3. Node Gate

| Gate | 决定 | 拟议内容 | Evidence依据 | 正式边界 |
| --- | --- | --- | --- | --- |
| TG-N01 | `ADMIT / NEW_NODE` | 操作者充电电流设置（外部输入） | E03与E06形成32→16→32 A相反输入 | 不是`AEVSE`、`A₂`、`IAC_target`或内部Signal |
| TG-N02 | `ADMIT / NEW_NODE` | 车辆接受并保持的充电电流设置（外部可观察状态） | E03-P01、E04-P01/P03及E06-P01/P02显示新设置被接受并保持 | 不证明内部写入位置、Target或裁决结果 |
| TG-N03 | `RETAIN_UNOBSERVED` | 设置接受与实际响应之间的车辆内部处理区域 | E06-P01中设置已为32 A、实际仍为21 A；raw存在不同动态类别 | 仅作观察缺口，不拆成正式Target、能力、仲裁、请求或执行Node |
| TG-N04/05/06 | `RETAIN_CANDIDATE` | 早期、中间、较晚匿名raw行为簇 | S0030双向阶跃及S0009跨Round复现 | 全部留在Evidence附件，零个raw簇准入正式树 |
| TG-N07 | `ADMIT / ANNOTATE_EXISTING_NODE` | 既有`IAC_actual`获得本车方向性、可逆响应支持 | 页面实际电流32→16→32 A，功率7→4→7 kW | 不绑定raw，不确认内部采样Signal，也不形成scale/unit映射 |
| TG-N08 | `ADMIT / ANNOTATE_EXISTING_STATE` | 既有高压充电运行态可在新设置下进入短时稳定水平 | W1 70.000 s、W2 117.505 s、W3 102.522 s | 不是新增控制器Node；只适用于本Round短时基线 |
| TG-N09 | `ADMIT / CONDITION_ON_EXISTING_STATE` | 连续高压充电运行态 | 全程无已记录停充、重启或重连，页面持续显示正在充电 | 不拆分连接、锁止、许可、Ready或接触器子状态 |

## 4. Relationship Gate

### 4.1 准入Relationship

| Gate | 正式Relationship | 强度 | Evidence | 边界 |
| --- | --- | --- | --- | --- |
| TG-R01 | 操作者设置→车辆接受并保持设置 | `SUPPORTED_DIRECT_RELATIONSHIP` | E03/E06相反操作及之后多张设置保持照片 | Event Clock不是触控完成时刻，不能给接受延迟 |
| TG-R02 | 已接受设置变化→实际交流取电方向一致且可逆变化 | `SUPPORTED_SYSTEM_LEVEL_CONTROL_RELATIONSHIP` | 设置与实际均呈32→16→32 A，功率呈7→4→7 kW，三窗口成立 | 中间必须保留未观测区域；不能写成已知内部直连、1:1传递函数或具体算法 |
| TG-R03 | 实际响应→新水平持续充电稳定结果 | `SUPPORTED_CONDITIONED_STATE_TRANSITION` | W1/W2/W3及车辆、应用阶段性读数 | 只确认阶段顺序与短时稳定，不确认精确收敛时间 |
| TG-R04 | 设置接受状态与实际响应状态相互独立、不可合并 | `SUPPORTED_NODE_SEPARATION` | E06-P01设置32 A、实际21 A；E06-P02后实际32 A | 可确认前者能先完成；不能推定固定延迟或内部节点数量 |

TG-R02是系统输入—输出层的实验关系。它不是从TG-N02跨过未知区域直接指认某个内部实现；正式图示必须把该未知区域画出或明确标注。

### 4.2 不准入Relationship

- TG-N02连接到既有`IAC_target`、`A₂`或`AEVSE`的具体路径：`DO_NOT_ADMIT`。当前无法区分设置作用于目标、能力、上限、仲裁还是其他内部量。
- 早期raw簇驱动中间或较晚raw簇：`DO_NOT_ADMIT`。串行结构和共同潜变量并行结构仍不可区分。
- 任一raw簇连接到`IAC_actual`、功率反馈或具体ECU：`DO_NOT_ADMIT`。目前只有行为共变。
- 设置与实际之间的定量1:1闭环、精确传递函数或控制延迟：`DO_NOT_ADMIT`。页面刷新与实际触控时间均不够精确。
- raw候选之间的复制、网关转发、计算派生或固定多byte字段关系：`DO_NOT_ADMIT`。

## 5. Condition Gate

| Condition | 决定 | 用法 | 边界 |
| --- | --- | --- | --- |
| 同一连续高压充电运行态保持 | `ADMIT` | TG-R02和TG-R03的正式适用条件 | 不证明连接、锁止、Ready、许可或接触器各子状态 |
| 页面可见可用上限未低于设置 | `RETAIN_AS_EXPERIMENT_SCOPE` | 记录本轮是在页面上限32 A、设置16/32 A范围内成立 | 字段来源及内部语义未确认，不命名为`AEVSE`或`A₂` |
| 无其他已记录人工动作或现场异常 | `RETAIN_AS_EVIDENCE_VALIDITY` | 支撑本轮系统级因果解释 | 属实验有效性条件，不是车辆控制树Condition |
| SOC约85%至86%、本次EVSE和现场条件 | `RETAIN_AS_APPLICABILITY_BOUNDARY` | 限制车型基线外推 | 不构造SOC、温度或EVSE阈值 |
| 热限制、SOC限制、桩侧限流及异常保护 | `DO_NOT_ADMIT / NOT_OBSERVED` | 本轮不进入 | 未施加或未独立观测，不能为结构完整而补入车型投射 |

## 6. 与现有正式控制树的合并方式

若本Gate获批，推荐采用“最小拓扑增量＋既有节点Evidence增强”，而不是复制一棵TM3专用平行树：

1. 在既有⑭“高压充电运行态 / 充电目标持续更新”附近增加TG-N01与TG-N02，明确它们是外部设置及其外部可观察接受状态。
2. TG-N02到既有`IAC_actual`之间保留显式未观测区域。既有`AEVSE`、`A₂`和`IAC_target`仍是通用L3节点，但本轮不选择其中任何一个作为设置的车型级落点。
3. 给既有`IAC_actual`增加TM3-017/S0030的方向性、可逆性Evidence引用；给既有⑭增加三个短时稳定窗口引用。
4. 把“连续高压充电运行态”标为上述Relationship的条件，而不是新建一套连接、Ready或许可分支。
5. 匿名raw分组继续留在TM3-017 Evidence附件，不写入正式控制树正文，也不建立Signal映射。

## 7. 可接受的正式结论强度

若本增量通过，正式控制树最多可表达：

> 在`TESLA-M3-SOP5`的S0030条件下，车辆处于同一连续交流充电过程时，操作者充电电流设置被车辆界面接受并保持；设置的相反变化对应实际交流取电方向一致、可逆的变化，并在新水平形成短时稳定状态。设置接受与实际响应是可分离的观察节点，两者之间的车辆内部处理结构尚未识别。

不得升级为：

- 已确认用户设置直接写入`IAC_target`或改变`A₂`；
- 已确认`AEVSE`、车辆能力与用户设置的仲裁公式；
- 已确认某个匿名raw候选是设置、请求、能力、目标、执行或实际Signal；
- 已确认内部Node顺序、ECU归属、编码、scale、unit或精确响应延迟；
- 已确认关系适用于其他SOC、温度、EVSE、车辆或限制工况。

## 8. Gate汇总与停止点

本轮拟议准入结果：

- 新增正式Node：2个（外部设置、外部可观察接受状态）；
- 增强既有Node/State：2处（`IAC_actual`、高压充电运行态稳定结果）；
- 正式Condition：1项（同一连续高压充电运行态）；
- 正式Relationship/结构约束：4项；
- raw行为簇准入：0个；
- 内部Target、能力、仲裁、请求、执行Node准入：0个。

这已经是当前批准Evidence能够承受的最大正式增量。继续扩展会把通用L3结构、匿名raw相关性或逻辑必需环节误当成本车实证。

本文件仅提交Tree Gate待审结果；未修改正式控制树，不设计新采集。审核后停止在正式树写入授权之前。
