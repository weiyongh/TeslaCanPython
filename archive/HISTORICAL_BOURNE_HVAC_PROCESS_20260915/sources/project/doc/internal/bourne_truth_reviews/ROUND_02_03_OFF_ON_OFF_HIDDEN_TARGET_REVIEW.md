# Round 2/3 `OFF→ON→OFF` 控制树隐藏标靶复盘

**密级与流向：** M → 导演内部使用  
**状态：** `COMPLETE / DIRECTOR_ONLY`  
**日期：** 2026-09-14  
**适用范围：** Round 2/3 `OFF→ON→OFF` 样板实验  

> 本报告不进入伯恩的 `results`、`work`、`knowledge_snapshot` 或其他输入环境，不构成对伯恩的任务、提示或审核反馈，也不改变 Round 2/3 已有正式裁决。

## 一、复盘口径

本次复盘回答三个问题：Truth 侧理论可实例化范围、伯恩实际命中情况，以及本次实验对控制树实例化产生的净增量。

### 1. 状态定义

- `HIT`：伯恩发现的 raw candidate 精确覆盖 Truth 字段边界，且跨轮重复证据足以把相应控制树节点投射到该字段；此为总部回看结论，不表示伯恩盲态报告已经获得该语义。
- `PARTIAL`：伯恩命中了 Truth 字段中的部分 bit、相邻字段组或节点的一部分证据，但没有恢复完整字段、层级或节点关系。
- `MISS`：字段在本次数据中具有足够、可复核的区分信息，按现有 Evidence 理论上能够发现或恢复，但伯恩正式产物未命中。
- `NOT_OBSERVABLE`：关键报文未采到、字段未被该 Diff 激活，或 DBC 与实测存在不可接受冲突；不计作伯恩遗漏。

### 2. Evidence 层级边界

本 Diff 同时改变了整套 HVAC 电源状态，因此能够证明多个节点与 `OFF→ON→OFF` 同步，却不能仅凭同步关系区分它们的因果先后，也不能把请求、使能、目标、实际运行和物理结果跨层等同。

### 3. 核验材料

- Round 2 正式结果及候选表；
- Round 3 正式结果、52-bit 跨轮候选表及五次重复结果；
- Round 2 S0010 两段 ASC 与实际 Event 时间；
- `input/tesla_model3_ONYX.dbc` 及既有多 DBC 冲突审计；
- 既有总部 `Round3_Truth_Map_Review.md`。

本次重新解码 S0010 使用的比较窗为：`OFF1=10–55 s`、`ON early=70–115 s`、`ON steady=130–470 s`、`OFF2=545–650 s`。数值仅用于判断本次 Diff 是否激活字段，不提升 DBC 的车型级成熟度。

## 二、问题一：Truth 侧理论标靶

### A. 本次已经达到可观测、可辨识或部分可辨识的节点

| 控制树层级 | Truth 节点与已知字段 | 本次实测变化 | Truth 侧可辨识度 |
|---|---|---|---|
| 外部操作 / 设置 | HVAC 用户电源状态（`0x2F3 / UI_hvacReqUserPowerState`） | `0 → 1 → 0` | 字段可观测；与操作关联可辨识；其完整枚举语义仅部分可辨识 |
| 请求 | 空调综合请求（`0x20C / VCRIGHT_conditioningRequest`） | `0 → 1 → 0`，各稳定窗纯度 100% | 二值字段及与本 Diff 的关系可辨识；具体因果层级仍受共线限制 |
| 许可 / 使能 | 蒸发器 HVAC 使能（`0x20C / VCRIGHT_hvacEvapEnabled`） | `0 → 1 → 0`，各稳定窗纯度 100% | 二值字段可辨识；不能单凭本 Diff证明等同于压缩机许可或实际运行 |
| 系统计算需求 | 蒸发器功率需求（`0x20C / VCRIGHT_wattsDemandEvap`） | `0 → 约 3.1–3.4 kW → 0` | 字段变化与需求角色可观测；本 Diff 下可部分实例化 |
| 执行目标 / Command | 鼓风机转速请求（`0x20C / VCRIGHT_hvacBlowerSpeedRPMReq`） | `0 → 955–1850 rpm → 0` | 完整数值字段可观测；目标角色可辨识 |
| 执行目标 / Command | 鼓风机使能与输出占空比（`0x282 / VCLEFT_hvacBlowerEnabled`、`...OutputDuty`） | 使能 `0→1→0`；Duty `0→9–19%→0` | 使能可辨识；输出命令可部分辨识 |
| 执行目标 / Command | 鼓风机 RPM Target（`0x282 / VCLEFT_hvacBlowerRPMTarget`） | `0 → 960–1850 rpm → 0` | 字段与目标角色可辨识 |
| 执行器实际运行 | 鼓风机 RPM Actual（`0x282 / VCLEFT_hvacBlowerRPMActual`） | `0 → 950–1860 rpm → 0` | 字段与实际反馈角色可辨识 |
| 状态反馈 | HVAC 状态（`0x243 / VCRIGHT_hvacACRunning`、`...hvacPowerState` 等 multiplexed fields） | ON 窗与 OFF 窗分布不同 | 状态族可观测；因复用页与状态共线，只能部分辨识 |
| 物理结果 | 蒸发器温度（`0x20C / VCRIGHT_tempEvaporator`） | OFF1 中位 `18.3°C`，ON steady 中位 `5.8°C`，OFF2 中位 `12.9°C` | 冷却动态结果可观测；热惯性使其不是严格 `0→1→0` 型标靶 |
| 物理结果 | 左/右风道温度（`0x243 / VCRIGHT_tempDuctLeft/Right`） | 约 `26.5/27°C → 9.5/10°C → 22/22°C` | 冷风结果可观测；只证明风道温度响应，不独立证明中间执行链 |

### B. 本次不能作为 MISS 统计的关键节点

| 控制树节点 | 已知字段 / 原因 | 裁定 |
|---|---|---|
| 压缩机运行请求 / 使能 / 目标 | `0x281 / VCFRONT_compressorRequest` 在 S0010 各窗均无报文 | `NOT_OBSERVABLE` |
| 压缩机实际运行 | `0x20D / TAS_compressorRun` 在 S0010 各窗均无报文 | `NOT_OBSERVABLE` |
| HVAC 能源请求 | `0x212 / BMS_hvacPowerRequest` 全程为 0，未被 Diff 激活 | `NOT_OBSERVABLE` |
| HVAC 能源预算 / 限制 | `0x252 / BMS_hvacPowerBudget` 基本稳定，不能据此辨识许可变化 | `NOT_OBSERVABLE` |
| 前热管理压缩机状态与制冷剂诊断字段 | `0x201/0x381` 的当前 DBC 解码出现状态恒 0、估算转速在 OFF/ON 均恒定等内部矛盾 | `NOT_OBSERVABLE`（DBC 适配不足） |

因此，本实验可覆盖“用户状态 → HVAC 请求/使能 → 蒸发器需求 → 鼓风机请求/目标/实际 → 温度结果”的一段控制链，但不能直接覆盖压缩机命令与独立实际运行节点。

## 三、问题二：伯恩实际实例化情况

### 1. 节点级对照

| Truth 节点 | 伯恩实际发现 | 裁决 | 依据 |
|---|---|---|---|
| 空调综合请求 | `0x20C B1.b4` | `HIT` | 精确等于单 bit 字段 `VCRIGHT_conditioningRequest`，Round 3 为 5/5 重复 |
| 蒸发器 HVAC 使能 | `0x20C B1.b3` | `HIT` | 精确等于单 bit 字段 `VCRIGHT_hvacEvapEnabled`，Round 2/3 均命中 |
| 鼓风机使能 | `0x282 B0.b2` | `HIT` | 精确等于单 bit 字段 `VCLEFT_hvacBlowerEnabled`，Round 2/3 均命中 |
| HVAC 用户电源状态 | `0x2F3 B3.b2` | `PARTIAL` | 命中 `UI_hvacReqUserPowerState` 的最低 bit，但未恢复 3-bit 字段边界、枚举或设置层节点 |
| 蒸发器功率需求 | 无 `0x20C B0` 对应候选 | `MISS` | `VCRIGHT_wattsDemandEvap` 在数据中呈稳定 OFF/ON 分离且回零，现有数据足够识别为动态数值字段 |
| 蒸发器温度目标 | 无完整字段恢复 | `MISS` | `VCRIGHT_tempEvaporatorTarget` 在窗间明显变化；严格二值 bit 筛选与按 byte 分组未恢复该字段 |
| 鼓风机转速请求 | `0x20C B4.b1/b2/b3、B5.b0` 等 bit | `PARTIAL` | 命中 10-bit `VCRIGHT_hvacBlowerSpeedRPMReq` 的多个 bit-plane，但未恢复字段边界与数值轨迹 |
| 鼓风机输出占空比 | `0x282 B0.b5/b6、B1` 相邻 bit | `PARTIAL` | 命中 `VCLEFT_hvacBlowerOutputDuty` 的部分 bit-plane，未重建完整 7-bit 字段 |
| 鼓风机 RPM Target | `0x282 B1.b2/b3/b4、B2` 相邻 bit | `PARTIAL` | 命中字段内部变化，但未恢复 10-bit Target 字段及物理值 |
| 鼓风机 RPM Actual | `0x282 B2.b4/b5/b6、B3.b3` 等 bit | `PARTIAL` | 命中字段内部变化，但未恢复 10-bit Actual 字段及 Target↔Actual 收敛关系 |
| HVAC 状态反馈族 | 未命中 `0x243` 字段族 | `MISS` | 该报文存在可观测状态分布变化；需要复用页感知与多值字段分析，现有 raw-bit 严格模板未覆盖 |
| 蒸发器 / 风道温度结果 | 未恢复 `0x20C tempEvaporator` 或 `0x243 tempDuct*` | `MISS` | 温度在 ON 窗显著下降，属于本次已有数据中的动态结果证据；其非二值及热惯性使严格两边沿算法漏检 |

### 2. 汇总

- `HIT`：3 个节点投射——空调综合请求、蒸发器使能、鼓风机使能；
- `PARTIAL`：5 个节点投射——用户电源状态、鼓风机转速请求、鼓风机输出占空比、鼓风机 RPM Target、鼓风机 RPM Actual；
- `MISS`：4 类节点投射——蒸发器功率需求、蒸发器温度目标、HVAC 状态反馈族、蒸发器/风道温度结果；
- `NOT_OBSERVABLE`：压缩机请求/使能/目标、压缩机独立运行反馈、未激活的能源请求/预算，以及 DBC 适配不成立的前热管理诊断字段。

这里的 `HIT` 是总部以 Truth 回看后确认“raw observation 精确落在该节点字段上”；伯恩的盲态正式结论仍停留在 raw candidate，并未自行完成这些语义命名。换言之，伯恩找到了三处完整的一位字段投射，但尚未在其报告中把它们正式实例化为控制树节点。

## 四、问题三：本次实验对控制树的最终增量

### 1. 新增的可追溯节点

总部可由 Round 2/3 现有 Evidence 建立以下实验级投射：

1. HVAC 用户电源状态节点 ↔ `0x2F3 / UI_hvacReqUserPowerState`（字段边界与枚举仍为部分成立）；
2. 空调综合请求节点 ↔ `0x20C / VCRIGHT_conditioningRequest`；
3. 蒸发器使能节点 ↔ `0x20C / VCRIGHT_hvacEvapEnabled`；
4. 蒸发器功率需求节点 ↔ `0x20C / VCRIGHT_wattsDemandEvap`；
5. 鼓风机转速请求节点 ↔ `0x20C / VCRIGHT_hvacBlowerSpeedRPMReq`；
6. 鼓风机使能、输出占空比、RPM Target、RPM Actual 节点 ↔ `0x282` 对应字段；
7. 蒸发器温度与风道温度结果节点 ↔ `0x20C / VCRIGHT_tempEvaporator`、`0x243 / VCRIGHT_tempDuctLeft/Right`。

### 2. 得到强化、但尚未完全建立的控制关系

现有数据强化了以下“同一实验链上的有序层级关系”：

```text
HVAC 用户电源状态
→ 空调综合请求 / 蒸发器使能
→ 蒸发器功率需求 + 鼓风机转速请求
→ 鼓风机使能 / 输出目标
→ 鼓风机实际转速
→ 蒸发器与风道温度响应
```

但本次只有一个总状态 Diff，上述节点高度共线；除鼓风机 Target 与 Actual 的数值接近和动态响应外，不能仅凭本次数据把所有箭头升级为已证明的直接因果关系。当前最扎实的链内关系是：

- `BlowerRPMTarget` 与 `BlowerRPMActual` 同时从 0 建立，并在 ON steady 中分别覆盖约 `960–1850 rpm` 与 `950–1860 rpm`，支持“目标—实际反馈”关系；
- 蒸发器和风道温度在 ON 后持续下降，支持“HVAC 执行后出现冷却物理结果”，但不单独识别是哪一个中间节点造成该结果。

### 3. 仍未建立的关键节点与关系

- 压缩机运行请求、许可、目标与独立实际运行节点未建立，因为相应报文在本次采集域不可见，替代 DBC 字段又存在适配矛盾；
- 空调综合请求、蒸发器使能与压缩机执行之间的层级关系未建立；
- HVAC 状态反馈族的完整字段边界、复用页语义及其相对请求/执行层级未建立；
- 蒸发器功率需求、温度目标、鼓风机请求/目标/实际虽在 Truth 侧可由现有数据恢复，但伯恩未完成其字段级重建，因此这些仍是伯恩侧未实例化的 Tree Gap；
- 本次 Diff 无法单独区分“整机电源状态”“制冷功能”“送风功能”各自的独立贡献，因此不能把共变字段进一步唯一归属为更细的功能角色。

## 五、导演结论

Round 2/3 并非只得到一组泛化候选：其现有数据实际已经让一段 HVAC 控制链达到字段级可见。伯恩完整命中了 3 个一位节点字段，部分命中了 5 个多位命令/反馈字段，但漏掉了 4 类现有数据本可恢复的动态数值或复用状态节点。

本次实验对控制树的真实增量，是把“用户状态—请求/使能—鼓风机目标/实际—温度结果”这段链从完全未知推进到多个可追溯字段投射；尚未越过的核心断点是压缩机命令/运行链不可观测，以及单一总状态 Diff 无法消除各同步节点之间的竞争解释。

本报告到此结束，不产生下一轮 Acquisition Plan，不向伯恩发送任何任务。

## 附录：输入指纹

| 文件 | SHA-256 |
|---|---|
| Round 2 `README.md` | `ac07ff6319f6655ad03c56b8d492bd5287779a964d8e46599c12ae883cc641cf` |
| Round 2 `structured_bit_candidates.csv` | `6bb5ee04aa221b1de50e840de3e3bdf0d47b58d31da8e9f7391489245890e333` |
| Round 3 `README.md` | `c63837de5f1962efa77c6107beb3b930e7164595a5bd9e96b6ea5ffcd6cbb668` |
| Round 3 `cross_round_bit_candidates.csv` | `a234c6189db5fb3bb6c68ff5b3465c22716a99f3da6de0ea4c47165242a0cab5` |
| 既有总部 Truth Review | `0d2da40ca5788346e40a1a49903e05d1885d8cd9faad3da746a9e4e74bcda041` |
| `input/tesla_model3_ONYX.dbc` | `3554e37a3a8371bc9c1b76445061d30f2c5bbaa35a055fe1f01f7ee75030e86c` |
