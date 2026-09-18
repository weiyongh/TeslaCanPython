# Round 4 — M → Director Internal Truth Review

状态：`INTERNAL / DIRECTOR ONLY / COMPLETE`

正式 Audit 状态：`CLOSED`（保持不变）

## 一、内部边界

本报告生成于 Round 4 正式 Audit 完成 `CLOSED` 之后。此处允许使用总部掌握的 DBC、既有 Signal 定义和其他对伯恩隔离的信息，仅用于评价伯恩的独立分析表现。

本报告不属于伯恩提交物，不进入伯恩的 `results/` 或 `knowledge_snapshot/`，不得回流为后续 Audit、整改任务、分析提示、采集条件或预期答案，也不追溯修改 Round 4 的正式裁决。

内部对照主要使用：

- `input/tesla_model3_ONYX.dbc`
- `dbc/tesla_model3.dbc`
- `dbc/Model3CAN.dbc`
- `dbc/tesla_powertrain.dbc`
- 项目内既有 Signal 定义和 Round 4 已关闭产物

不同 DBC 存在版本、DLC 和总线域差异。只有位置与定义稳定相合的项目才按 HIT/PARTIAL 评价；未收录项目记为 UNKNOWN，不以缺失定义判定 MISS。

## 二、伯恩本轮独立发现

伯恩在五个独立 Session、六个 UI 稳态中，将 Round 3 的 23 个二态 raw bit 分化为：

- 9 个 HVAC/送风开启相关；
- 5 个风量 2→6 敏感；
- 8 个 A/C UI 切换可逆相关；
- 1 个本轮保持常值。

它进一步：

- 识别出 G02 与 G07 的组内成员响应分裂，否定两组作为单一响应整体；
- 将 16 个继承组定型为 18 个 field-level candidate partitions；
- 对同步、互补 bit 保留“多 bit 字段、多个 flag、复制或派生值”等竞争解释；
- 将 93 个全总线补充结果限制为 raw bit observations，没有虚报为字段数或独立 Evidence 数；
- 保持 UI、请求/许可/执行/反馈和物理结果的层级边界。

## 三、Truth/DBC 对照总评

| 评价层级 | 裁定 | 内部结论 |
|---|---|---|
| raw bit discovery | `HIT` | 23 个候选中至少 10 个落在已知 HVAC 请求、使能、风机目标或实际反馈字段内；核心 HVAC ID 被有效捕获。 |
| field boundary | `PARTIAL` | G02、G07 的拆分方向正确，但多数连续字段只命中其中若干 bit；跨原组、跨字节的真实连续字段没有恢复。 |
| semantic role | `PARTIAL` | 刺激分类大体命中制冷相关、风机相关和用户电源请求相关区域，但未区分请求、使能、目标与实际反馈。 |
| diagnostic usefulness | `HIT / PARTIAL` | 已找到能覆盖 UI 请求、HVAC 请求、风机 enable/target/actual 的诊断链候选，但 False Positive 与字段碎片化使其尚不能直接成为可靠诊断判据。 |

## 四、关键命中明细

### 1. `0x20C / VCRIGHT_hvacRequest`

| 伯恩位置 | DBC 对照 | 裁定 | 命中层级 |
|---|---|---|---|
| `B1.b3` | `VCRIGHT_hvacEvapEnabled`，start bit 11、长度 1 | `HIT` | raw bit + exact field boundary + semantic family |
| `B1.b4` | `VCRIGHT_conditioningRequest`，start bit 12、长度 1 | `HIT` | raw bit + exact field boundary + request role |
| `B4.b1` | 位于 `VCRIGHT_hvacBlowerSpeedRPMReq`（start 32、length 10）内部 | `PARTIAL` | true field component；本轮常值停止判断合理 |
| `B5.b0` | 位于同一 10-bit blower RPM request 内部 | `PARTIAL` | raw bit + fan sensitivity；field boundary 未恢复 |
| `B7.b3` | 现有版本定义不稳定或未覆盖该位置，且消息 DLC 存在版本差异 | `UNKNOWN` | 不以 DBC 缺失判错 |

G02 拆成 `B1.b3` 与 `B1.b4` 是本轮最强 field-boundary HIT：它不仅拆对了响应类别，也恰好对应两个相邻的一位字段。伯恩没有知道名称和层级，仍通过多状态刺激独立拆开，属于真实能力提升。

### 2. `0x282 / VCLEFT_hvacBlowerFeedback`

| 伯恩位置 | DBC 对照 | 裁定 | 命中层级 |
|---|---|---|---|
| `B0.b2` | `VCLEFT_hvacBlowerEnabled`，start bit 2、长度 1 | `HIT` | raw bit + exact boundary + enable/feedback family |
| `B0.b6` | 位于 `VCLEFT_hvacBlowerOutputDuty`（start 3、length 7）内部 | `PARTIAL` | fan-sensitive bit plane；不是独立一位字段 |
| `B1.b2` | `VCLEFT_hvacBlowerRPMTarget` 的起始位（start 10、length 10） | `PARTIAL` | target field component |
| `B2.b1` | 位于同一 10-bit RPM target 内部 | `PARTIAL` | target field component |
| `B3.b3` | 位于 `VCLEFT_hvacBlowerRPMActual`（start 20、length 10）内部 | `PARTIAL` | actual feedback component |

G07 将 `B0.b2` 与 `B0.b6` 拆开是正确的边界方向：前者是真实一位 enable，后者属于较宽 output-duty 字段。但伯恩仍把 `B0.b6` 保留为 single-bit hypothesis，只把“更宽编码”列为竞争解释，因此 field boundary 仅为 PARTIAL。

更重要的 MISS 是：G08 与 G09 分属原有不同字节组，但 Truth 中两者属于同一个跨字节 10-bit RPM target；G10 则属于另一个 10-bit RPM actual。伯恩没有突破 Round 3 的同字节分组框架重建这些连续字段。

### 3. `0x2F3 / UI_hvacRequest`

`B3.b2` 对应绝对 bit 26，落在 `UI_hvacReqUserPowerState`（start 26、length 3）内。

- raw bit 与 HVAC 开关刺激关联：`HIT`；
- 用户电源请求语义族：`PARTIAL/HIT`；
- 把该位置保留为单 bit 候选边界：`PARTIAL`，真实定义为 3-bit 字段。

该项说明伯恩已碰到 UI request 层，但正式报告谨慎地没有把它命名为执行反馈，这个停止边界正确。

## 五、MISS、UNKNOWN 与 False Positive

### 明确或较强 False Positive

1. `0x2A7 B7.b0 / B7.b2`：现有主 DBC 将整个 Byte 7 定义为 `UI_csaRoadCurvChecksum`。伯恩观察到的互补 A/C 模式位于 checksum 内，不是 A/C 字段。该组属于 `MISS`，也是典型“payload 随状态变化导致 checksum bit 可重复相关”的 False Positive。
2. `0x2BF B5.b3 / B5.b4`：现有 powertrain DBC 将 `0x2BF` 定义为 `DAS_control`；两个位置分别落在纵向加速度约束字段边缘，不属于 HVAC。若总线域和版本适配成立，则该组为 `MISS`。由于该定义来自不同 DBC 域，内部置信度低于 checksum 案例，保留版本/总线域条件。

### `UNKNOWN`

`0x1FA B0.b3/b4`、`0x253 B7.b4`、`0x2A1 B5.b0`、`0x323 B4.b1/b2`、`0x361 B3.b1/b2` 在当前总部参考中缺少足够稳定、适配本车与本总线域的定义。它们不能因未被 DBC 收录而判为 False Positive，统一记为 `UNKNOWN`。

其中 `0x1FA` 在项目实验 DBC 中另有车窗汇总候选，但只确认了其他 bit；这不足以否定 `B0.b3/b4` 的 HVAC 相关性，也提示同一报文可能承载多个不同系统或派生状态。

### False Positive 结构性统计

- 强 False Positive：2 个 raw bit（`0x2A7` checksum 位）。
- 条件性 False Positive：2 个 raw bit（`0x2BF`，取决于 DBC 总线域/版本适配）。
- 其余无法对照者：9 个 raw bit，记为 `UNKNOWN`，不计入 False Positive。

93 个全总线补充 bit 未逐项做字段恢复，预期仍含连续量 bit plane、counter/checksum 和跨系统共变造成的更多 False Positive；伯恩将其限制在 raw observation 层，因此没有形成正式语义误判。

## 六、未命中 Truth 但当时仍合理的竞争假设

下列假设虽不等于当前 DBC 定义，但在伯恩当时 Evidence 下仍属合理：

- 对同步或互补 bit 并列保留“一个多 bit 枚举”与“多个同步 flag”；六个离散状态不足以唯一证伪任一解释。
- 对风量敏感单 bit 保留“更宽风量编码的一部分”；只有风量 2 和 6，无法恢复完整位宽和编码。
- 对不同 ID 的同步响应保留源、复制、消费者派生或共因响应；被动观察无法确认报文来源关系。
- 对 A/C UI 相关项拒绝直接命名为请求、许可、执行或物理制冷；缺少执行器和热力学 Evidence 时，这是正确停止条件。
- 对 DBC 未覆盖位置保持 unresolved，而不是把缺失定义当作不存在。

因此，Formal Audit `CLOSED` 合理：正式审计评价的是伯恩的 Evidence 推理是否合法，而不是是否完全命中总部 Truth。

## 七、能力提升、停止条件与推理短板

### 能力提升

- 从单一 OFF/ON 二态相关推进到六状态、五轮重复的刺激分化。
- 能用组内成员响应差异否定继承分组，而非维护旧结论。
- 开始形成 field-level hypothesis，并显式保存竞争解释和存废状态。
- 对时间精度、UI 与执行层级、同步 bit 非独立 Evidence 的边界控制明显增强。
- 在 provenance 复审后能够纠正不可复算的照片集合摘要，并形成真正可独立复算的合同。

### 正确停止条件

- 不把 field hypothesis 写成字段确认。
- 不用刺激标签命名系统语义或控制层级。
- 不由 UI 状态推断压缩机、风机实际运行或物理制冷建立。
- 不把 93 个同步 raw bit 计为 93 个独立 Signal。

### 推理短板

- 仍以 raw-bit 分类为主，field recovery 受 Round 3“同 CAN ID、同字节”分组强烈约束。
- 没有主动搜索跨字节连续字段，因而把一个 10-bit RPM target 切成多个独立候选。
- 对连续量只抓取发生翻转的 bit plane，没有重建完整原始值随刺激的单调性、比例结构和目标/实际关系。
- 缺少 counter/checksum 排除机制；五轮可重复相关仍可稳定地产生 checksum False Positive。
- 组内拆分能力已出现，但跨组重新聚合能力不足。
- 对 request、enable、target、actual 的层级区分仍主要停留在“不能确定”，尚未从多变量时序与数值关系中形成更强竞争裁决。

## 八、下一轮内部训练价值与建议

下一轮训练价值不在增加更多 raw-bit 命中数，而在验证伯恩能否从 bit-plane observation 转向完整 field reconstruction：

1. 训练其打破继承分组，主动检查同一报文内相邻及跨字节 bit 是否组成连续字段。
2. 要求从完整原始值、状态阶梯、单调性和目标—实际关系建立字段候选，而非仅按单 bit 模式聚类。
3. 增加 counter/checksum/rolling code 的独立排除责任，避免“高度重复相关”被误当成功能字段。
4. 训练 request、enable、target、actual feedback 的分层竞争解释，但不得将本报告中的真实名称或位置回流给伯恩。
5. 继续保留外部执行 Evidence 要求，使字段语义升级与控制层级升级分开进行。

这些建议只用于 Director 决定未来训练目标。若进入下一轮，题面必须由伯恩基于已关闭 Evidence 自主提出，并继续经过独立审核；不得把本报告的 Truth 命中、未命中位置或字段结构转写为提示。

## 九、内部结论

Round 4 是一次显著的能力进步：伯恩已从纯二态 raw-bit 重复性验证，推进到多状态刺激分类和初步 field-level hypothesis，并独立命中了若干真实 HVAC 请求、使能、风机目标与实际反馈字段的关键 bit。

总体评级：

`RAW BIT: HIT`  
`FIELD BOUNDARY: PARTIAL`  
`SEMANTIC ROLE: PARTIAL`  
`DIAGNOSTIC USEFULNESS: HIT / PARTIAL`  
`FALSE POSITIVE CONTROL: MISS / NEEDS TRAINING`

正式 Audit 的 `CLOSED` 裁决保持不变。本内部收尾完成后停止，不触发伯恩，不进入下一阶段。
