# Round 1 Truth / Map Review

## 1. 审阅边界

- 被评测对象仅为伯恩已冻结 `results/` 中明确提出的主要候选和解释。
- 本审阅没有替伯恩增加候选、补全遗漏 Signal，也没有重做 CAN Reverse。
- HVAC 与交流慢充只记录原结论：**伯恩未发现严格二态候选**；未使用精确地图寻找正确答案。
- 伯恩 Workspace 未被修改；本文件位于总部项目输出域。

判定标记：`HIT`=命中，`PARTIAL`=只命中一部分或仅在本实验条件成立，`MISS`=真值冲突，`UNRESOLVED`=现有真值不足以裁决。`False Positive` 只评价伯恩所声称的功能解释，不否认原始位变化确实存在。

## 2. 总裁决：端回来的咖啡有多少是真的

按伯恩在 README 中明确提出的 **19 个主要 bit 候选**计数：

| 裁决层级 | 数量 | 含义 |
|---|---:|---|
| 在伯恩声明的有限语义深度上成立 | **9/19** | 6 个 D/R 离散判别位、2 个车速字段内部位、1 个车窗汇总状态位 |
| 命中相关系统字段，但把共变条件当成目标状态 | **2/19** | `0x126 B3.b2`、`0x2E8 B0.b0` |
| 观察真实，但总部现有地图仍不能确认其功能语义 | **5/19** | `0x25B` 两位、`0x348`、`0x324`、`0x52F` |
| 可由精确地图判定为功能性误报 | **3/19** | `0x23A B0.b4`、`0x32A B0.b3`、`0x32A B4.b3` |

若只统计用户指定的四组重点（D/R、正向运动、回收、车窗，共 16 位），结果为：**9 个成立、2 个部分命中、4 个未决、1 个明确误报**。

这个 9/19 不是“恢复了 9 个完整 Signal”。其深度分布是：

- **完整字段边界 + 正确语义 + 正确角色：1 个**：`0x1FA B0.b5`。
- **找到官方字段位置，但只取到枚举字段内部 code bit：2 个**：`0x118 B2.b7/B2.b6`。
- **找到可靠的 D/R 派生编码，但字段边界和来源角色未恢复：4 个**：`0x108` 与 `0x1E5` 的四个位。
- **找到连续车速量内部的两个量化 bit；能标识本次速度带，但不是独立状态：2 个**：`0x257 B2.b4/B2.b5`。

因此最准确的结论是：伯恩**很强地找到了 D/R 的多个离散投影和一个真正的车窗汇总状态位**；同时也暴露了盲态单 bit 筛选的典型上限——它容易把枚举/连续量内部 bit、相关控制条件和无关复用字段端成“二态状态”。

## 3. 逐候选真值表

### 3.1 D/R 挡重点候选

| 候选 | Observation Hit | Boundary Hit | Semantic Hit | Role Hit | Diagnostic Value | False Positive | 真值裁决 |
|---|---|---|---|---|---|---|---|
| `0x108 B7.b5`（D） | HIT | MISS | HIT（D 判别） | PARTIAL | MEDIUM | NO（作为本采集 D 指纹）；YES（若当独立 D Signal） | 原始 byte 7 在 P/D/R 稳态分别稳定呈现不同编码，且实验明确全程不踩加速踏板；现有 DBC 将 byte 7 标作连续踏板量，与实测物理条件冲突。伯恩发现的是可靠 D 派生编码位，但没有恢复字段边界或权威角色。它不是 checksum：同帧 checksum 在 byte 0，counter 在 byte 1。 |
| `0x108 B7.b4`（R） | HIT | MISS | HIT（R 判别） | PARTIAL | MEDIUM | NO（作为本采集 R 指纹）；YES（若当独立 R Signal） | 同上；命中了同一未知编码字段中的 R code bit。 |
| `0x118 B2.b7`（D） | HIT | PARTIAL | HIT | HIT | HIGH | NO（作为 D code bit）；YES（若当独立字段） | 位于 `DI_gear` 的 3-bit 枚举字段（start 21, length 3）内部。D 枚举值为 4，因此该 bit 被置位。正确位置、语义和反馈角色均命中，但边界只恢复了 1/3。 |
| `0x118 B2.b6`（R） | HIT | PARTIAL | HIT | HIT | HIGH | NO（作为 R code bit）；YES（若当独立字段） | 同一 `DI_gear` 枚举字段内部；R 枚举值为 2。不是独立 R 状态字段。 |
| `0x1E5 B0.b3`（D） | HIT | UNRESOLVED | HIT（D 判别） | UNRESOLVED | MEDIUM | NO（作为本采集 D 指纹） | 该 ID 未被当前总部 DBC 命名，但 payload byte 0 对 P/D/R 呈稳定 one-hot 式编码，重复换挡闭合。可确认是 D 的稳定派生投影；不能确认它是源、网关还是消费者状态，也不能确认完整字段宽度。 |
| `0x1E5 B0.b2`（R） | HIT | UNRESOLVED | HIT（R 判别） | UNRESOLVED | MEDIUM | NO（作为本采集 R 指纹） | 同上，是 R 的稳定派生投影，角色与边界未恢复。 |

**D/R 总结：** 6/6 都不是“奶茶”。但只有 `0x118` 两位进入了官方实际挡位反馈字段；`0x108`、`0x1E5` 是真实、可重复的 D/R 编码投影，不能据此宣称三条独立 Request/Command/Feedback 链。伯恩关于“多通道一致即可检测来源/网关/消费者不一致”的建议超出了已恢复角色：在未确认通道独立性和来源前，诊断价值只能评为中等。

### 3.2 低速正向运动重点候选

| 候选 | Observation Hit | Boundary Hit | Semantic Hit | Role Hit | Diagnostic Value | False Positive | 真值裁决 |
|---|---|---|---|---|---|---|---|
| `0x126 B3.b2=1` | HIT | MISS | PARTIAL | PARTIAL | LOW | YES（若当离散运动状态） | 该位落在 `DIR_dcCableCurrentEst` 16-bit 连续电流字段内部；当前 ONYX 还存在 message DLC 3 与实测 DLC 5 的适配冲突。它随驱动电流/工况变化是合理共变，但不是独立“正向运动”位。 |
| `0x257 B2.b4=0` | HIT | MISS | HIT（仅本速度带） | PARTIAL | LOW–MEDIUM | YES（若当稳定二态 Signal） | 位于 12-bit 连续量 `DI_vehicleSpeed` 内部。伯恩命中了真实车速位置和本实验低速带的量化模式，但不是字段边界；换速度带后该 bit 模式可改变。 |
| `0x257 B2.b5=1` | HIT | MISS | HIT（仅本速度带） | PARTIAL | LOW–MEDIUM | YES（若当稳定二态 Signal） | 同上，是同一连续车速值内部的另一个 bit，不构成第二条独立 Evidence。 |
| `0x2E8 B0.b0=1` | HIT | MISS | PARTIAL | MISS（对“运动反馈”） | LOW | YES（若当运动状态） | 位于 4-bit 枚举 `EPBR_systemStatus` 内部。它反映电子驻车制动系统状态编码，在本实验中随驻车释放/行驶条件共变；不是速度、加速请求或驱动执行反馈。 |

**正向运动总结：** 伯恩没有恢复一个独立的“低速正向运动字段”。他命中了连续车速本体中的两个 bit，并触及了相关电流与 EPB 状态字段。作为本次窗口分类器有效，作为可外推控制指纹不稳健。

### 3.3 松电门回收重点候选

| 候选 | Observation Hit | Boundary Hit | Semantic Hit | Role Hit | Diagnostic Value | False Positive | 真值裁决 |
|---|---|---|---|---|---|---|---|
| `0x25B B1.b6=0` | HIT | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNPROVEN | UNRESOLVED / HIGH RISK | 当前车型地图把 `0x25B` 定义为 1-byte `APP_environment`；候选位位于 byte 1，超出该定义边界，而实测帧存在更长 payload，说明存在版本/总线定义冲突。Golden 回收证据链不能把该位确认成松踏板、负扭矩或回收功率。 |
| `0x25B B7.b2=0` | HIT | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNPROVEN | UNRESOLVED / HIGH RISK | 同一 ID 的 byte 7，亦超出当前定义。4 次边界同步只能证明本实验共变，不能通过真值机升级为回收语义。 |

**回收总结：** 0/2 得到语义真值确认；也不能武断判成确定奶茶。总部只能确认“杯子里有东西”，尚不能证明是咖啡。

### 3.4 车窗重点候选

| 候选 | Observation Hit | Boundary Hit | Semantic Hit | Role Hit | Diagnostic Value | False Positive | 真值裁决 |
|---|---|---|---|---|---|---|---|
| `0x23A B0.b4=1` | HIT | MISS | MISS | MISS | NONE（对车窗） | YES | 位于 `VCSEC_TPMSStatusIndex` 5-bit multiplexer/index 字段内部，属于 TPMS 状态页索引，不是车窗状态。三次实验的完美同步是实验条件或消息页共变造成的误报。 |
| `0x348 B4.b4=1` | HIT | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNPROVEN | UNRESOLVED | 当前地图对 `0x348` 的已知定义不足以覆盖 byte 4；跨三次车窗实验的观察值得保留，但没有真值依据确认“任一车窗非全关”。 |
| `0x1FA B0.b5=1` | HIT | HIT | HIT | HIT | HIGH | NO | HQ 已确认的 1-bit `EXP_anyWindowNotFullyClosedCandidate`：右前、右后、左后三组开/关状态严格可逆，无操作基线零翻转。伯恩准确恢复了位置、1-bit 边界、汇总语义和状态反馈角色。 |
| `0x324 B1.b6=0` | HIT | UNRESOLVED | UNRESOLVED | UNRESOLVED | LOW | UNRESOLVED / HIGH RISK | 地图未给出可验证的对应字段，且伯恩自己的跨窗纯度已下降。不能确认单窗/区域语义。 |

**车窗总结：** 1 个是真咖啡且认到了完整字段深度；1 个可确定是奶茶；另外 2 个仍是未决样品。

### 3.5 驾驶门候选

| 候选 | Observation Hit | Boundary Hit | Semantic Hit | Role Hit | Diagnostic Value | False Positive | 真值裁决 |
|---|---|---|---|---|---|---|---|
| `0x52F B4.b2=0` | HIT | UNRESOLVED | UNRESOLVED | UNRESOLVED | LOW | UNRESOLVED / HIGH RISK | 仅一次开门，且当前地图无对应定义。伯恩把它降为 C 级是合理边界；不能确认门状态。 |
| `0x32A B0.b3` | HIT | HIT | MISS | MISS | NONE（对车门） | YES | 精确字段为 `DAS_w004_accDisabled`，属于告警矩阵，不是门状态。 |
| `0x32A B4.b3` | HIT | HIT | MISS | MISS | NONE（对车门） | YES | 精确字段为 `DAS_w036_bdyMia`，属于告警矩阵，不是门状态。 |

## 4. HVAC 与交流慢充

- HVAC：**伯恩未发现严格二态候选。**
- 交流慢充：**伯恩未发现严格二态候选。**

本阶段不利用地图为这两类实验寻找或提示正确字段，因此不计 Hit，也不计 Miss。

## 5. 方法层面的真值结论（不回传伯恩）

1. **Observation Hit 很强。** 伯恩的窗口纯度和边界翻转筛选确实找到了与实验段同步的真实变化；D/R 和车窗尤其突出。
2. **Boundary Recovery 明显弱于位置发现。** 19 个主要 bit 中，只有 `0x1FA B0.b5` 恢复了完整且正确的 1-bit 字段；大量候选只是多 bit 枚举或连续量中的某一位。
3. **Semantic Hit 取决于伯恩声明的深度。** 他把 `0x257` 称作“正向运动复合指纹”而非车速 Signal，这使其在本速度带成立；若把它提升为通用二态运动状态，则是误报。
4. **Role Hit 是最薄弱环节。** `0x118/DI_gear` 和 `0x1FA` 可确认反馈角色；其余冗余编码不能仅凭同步性分配为 Source、Gateway、Consumer、Request、Command 或 Feedback。
5. **诊断价值不能按候选数量相加。** 同一枚举字段的多个 code bit、同一连续量的多个量化 bit，以及可能同源的多个镜像，只构成一条相关证据，不是多条独立证据。

## 6. 总部真值依据

- `input/tesla_model3_ONYX.dbc`
- `dbc/Model3CAN.dbc`
- `dbc/Model3_ETH_json_reference_optional.dbc`
- `dbc/tesla_model3.dbc`
- `output/TM3-003/TM3-003_静止挂挡分析结论.md`
- `output/TM3-004/TM3-004_低速加速分析结论.md`
- `output/TM3-005/TM3-005_低速松电门回收分析结论.md`
- `output/四车窗候选ID综合验证报告.md`
- 对原始 ASC 中上述候选 payload 的只读抽查

这些真值与对照信息仅保存在总部侧本报告中，不进入伯恩 Workspace。
