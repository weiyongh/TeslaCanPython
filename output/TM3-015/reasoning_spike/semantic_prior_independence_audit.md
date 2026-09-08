# Semantic Prior Independence Audit

## L3 原文内容（保留）

- `Capability → Request → EVSE Actual → Pack Actual`：来自最新版《直流快充》的“充电参数关键变量”及核心控制关系。
- 请求电压/电流属于车辆控制目标；Capability 是能力边界；EVSE Actual 与 Pack Actual 是不同边界的实际量。
- `P_request`、`P_EVSE_actual`、`P_pack_actual` 的电压×电流派生公式，以及“不预设独立功率 Signal”。
- L3 是 Semantic Prior 而非 Signal Whitelist；DBC 名称不能独立确认具体车型 Semantic Role。

## 人为抽象总结（已删除）

- 五条 semantic principle 中的 `reasoning_impact`，包括强制逐层映射、预设 Evidence Gap、规定 Request 角色判法等输出指示。
- 人为整理的 `L3-DCFC-REQUEST-RESPONSE` Evidence 路径条目；其 L3 原文关系已由控制链条目完整保留。
- v2 新增的三条 expected reasoning rules，包括直接要求返回 `INSUFFICIENT_EVIDENCE / Evidence Gap` 的规则。

## 结论

`reasoning_input_v2.1.json` 保留 L3 的变量定义、性质、数学约束和原文控制关系，不再预设 TM3-015 的 Request 是否可见、应得到何种 Evidence 状态或 Signal Role。未发现 reasoning-answer leakage。

Discovery、Observation、Candidate、Control Tree 和 ER 与 v2 对象级一致。
