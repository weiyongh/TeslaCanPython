# TM3-015 Semantic Prior Diff — v1 → v2

## 范围与来源

- 变更范围仅为 `reasoning_input.json` 中的 L3 Semantic Prior、关联 Control Mainline / Control Tree / Evidence Requirement 及推理边界规则。
- 新版 L3 来源：[直流快充](https://app.notion.com/p/3d0a4e4386498073a723f95a15d1c301)，最后编辑时间 `2026-09-07T14:24:38.661Z`。
- L3 source SHA-256：`11f0739849e68516982ca5a9536724b63f1dc6a89644fd90ca7130f0d32920e9`。哈希对象为完整 Notion fetch `text` 字段的 UTF-8 字节，共 37,129 bytes；fetch 未截断。
- Phase 2.5 Discovery payload 未变化；未重新解析 ASC，未运行 Discovery Kernel、DBC Coverage Join、Signal Summary 或 Candidate Discovery。

## 新增

### Semantic Prior

新增五条与 TM3-015 实验目的直接相关的通用语义：

1. `Capability → Request → EVSE Actual → Pack Actual` 是四个不可互相替代的控制/响应层。
2. 请求充电电压和请求充电电流是车辆当前向 EVSE 提出的控制目标，不等于能力上限或实际输出。
3. `P_request`、`P_EVSE_actual`、`P_pack_actual` 优先分别由同一边界、同一时刻的电压和电流派生；不预设独立功率 Signal。
4. 只有 Actual 不能证明 Request 存在或正确；Request 缺少可验证 Observation 时必须保留 `INSUFFICIENT_EVIDENCE / Evidence Gap`。
5. L3 是 Semantic Prior，不是 Signal Whitelist；`DBC Signal Name ≠ Confirmed Semantic Role`。

### Control Tree Node

新增四个通用功能节点，补足旧 Prior 将能力、请求和两侧实际量压缩在“电压/电流建立、能源交叉验证”中的语义缺口：

| Node | 新增语义 | 对 Semantic Reasoning 的影响 |
|---|---|---|
| `CT-DCFC-12 充电能力边界` | 分开桩侧可提供能力与车辆当前允许能力 | Capability 只能作为范围/上限，不能映射为 Request 或 Actual |
| `CT-DCFC-13 车辆充电请求` | 请求电压、请求电流及派生请求功率 | 没有经验证 Request Observation 时保留 Evidence Gap |
| `CT-DCFC-14 桩侧实际输出` | EVSE 实际输出电压、电流及派生功率 | 与车辆 Request 建立请求—响应关系，但不代替 Pack Actual |
| `CT-DCFC-15 Pack实际响应` | Pack 侧最终实际电压、电流及派生功率 | 与 EVSE Actual 保持测量边界区分，并用于物理建立核对 |

### Control Mainline

- `CML-DCFC-START` 在短时稳定运行前加入 `CT-DCFC-12～15`。
- `CML-DCFC-ENERGY` 从单一 `CT-ENERGY-01` 展开为 `CT-DCFC-12 → CT-DCFC-13 → CT-DCFC-14 → CT-DCFC-15 → CT-ENERGY-01`。
- 这两项会影响 Semantic Reasoning 和 Signal Role Classification：候选证据必须先区分 Capability、Request、EVSE Actual、Pack Actual，再进入能源交叉验证。

## 删除

无 Semantic Prior、Control Mainline、Control Tree Node 或 Evidence Requirement 被删除。

## 修改

### Evidence Requirement

| ER | 原 ER | 新 ER | 修改原因与新版 L3 依据 | 分类 | 影响 |
|---|---|---|---|---|---|
| `ER-04` | “实际直流电流建立并与CP及Pack能源响应对应。”充分性为方向、量级和时序相容。 | “车辆Request、EVSE Actual与Pack Actual形成可区分的请求—响应—物理建立关系。”分别验证请求电压/电流、桩侧实际输出和Pack实际响应；Request缺失时判证据不足，禁止替代。 | 新版 L3 明确车辆请求是控制目标、桩侧实际输出是请求响应、Pack Actual是最终物理响应。 | **真正 Requirement Change** | 直接影响 ER Mapping 与四层 Signal Role；旧 Actual-only 证据不再足以覆盖完整 ER。 |
| `ER-05` | “形成可描述的短时充电窗口。” | 在短稳态窗口内按可观测范围区分 Capability、Request、EVSE Actual、Pack Actual；缺失层保留 Evidence Gap。 | 新版 L3 将稳态充电描述为能力评估、请求更新、桩输出调整、Pack状态变化的循环。 | **Semantic Clarification** | 不改变 20～30 s 窗口门槛；改变窗口内的语义分层和 Signal Role Classification。 |
| `ER-06` | “停止请求后输出电流和充电状态退出。” | 停止入口后分别观察车辆请求、EVSE输出、Pack响应和充电状态退出；缺少Request Observation不得由Actual反推。 | 新版结束主线明确“降低充电电流请求 → 桩停止输出 → DC电流退出 → 状态收尾”。 | **真正 Requirement Change** | 影响 ER Mapping；Request 缺失时只能形成部分支持或证据缺口。 |
| `ER-08` | “记录条件、能力和告警边界。” | 明确记录桩侧/车辆侧 Capability，并与 Request、Actual 严格区分；DBC名称须先 Signal Validation。 | 新版 L3 明确能力只表示可行边界，请求表示当前目标，Actual表示实际结果。 | **Semantic Clarification** | 主要影响 Signal Role Classification；不新增“必须存在同名 Signal”的要求。 |

`ER-01`、`ER-02`、`ER-03`、`ER-07`、`ER-09`、`ER-10` 未修改。它们分别覆盖连接/协商、许可与高压状态、安全释放、整车状态门和热管理副线；新版 L3 未产生必须改变这些 Requirement 的新增实验命题。

## 仅文字变化

- `ER-05` 与 `ER-08` 的修改属于语义澄清：原证据目标和完成门槛不变，但明确了角色边界与证据不足的表达方式。
- 新增推理规则将既有原则显式化：不得把 Capability、Actual 或名称相似的 DBC Signal 当作 Request；不得跨边界或跨时刻派生功率。

## 会影响 Semantic Reasoning

- 必须显式区分四层链路，不能再把 CP/Pack 电压电流的一致变化直接概括为完整“请求—响应”闭环。
- 请求电压、请求电流没有可验证 Observation 时，结论必须停在 `INSUFFICIENT_EVIDENCE / Evidence Gap`。
- 功率角色必须带边界：Request power、EVSE actual power、Pack actual power；默认是派生量。

## 会影响 ER Mapping

- `ER-04` 和 `ER-06` 为真正 Requirement Change。
- `ER-05` 和 `ER-08` 为 Semantic Clarification。
- 其他 ER 不受影响。

## 会影响 Signal Role Classification

- Capability、Request、EVSE Actual、Pack Actual 由一个宽泛能源角色拆成独立角色。
- Signal 名称、可解码、动态变化或与 Actual 同步，均不能单独确认 Request 角色。
- Signal Validation 是所有具体车型角色映射的前提；新版 Prior 不构成 Signal 白名单。
