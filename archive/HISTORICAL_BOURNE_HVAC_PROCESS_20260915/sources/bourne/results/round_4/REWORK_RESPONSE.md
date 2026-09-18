# Round 4 审查整改答复

当前状态：`CLOSED`。

已完成 `PREAUDIT_01.md` 至 `PREAUDIT_05.md` 的整改。

## PREAUDIT_01

| # | 预审问题 | 整改位置 | 受影响文件 | 是否改变机器结果 | 指纹影响 |
|---:|---|---|---|---|---|
| 1 | 撤销未经正式复审的“审核通过”和 `CLOSED` | 全部正式状态回退 | 顶层及 Round 4 README/VALIDATION/METHOD/Manifest | 否 | 文档 SHA 更新 |
| 2 | 状态统一为 `OPEN / REWORK_REQUIRED`，整改后提交为指定状态 | 整改期间按 OPEN 执行，提交点统一为 `REVISED / PENDING_RE-AUDIT` | 全部状态入口 | 否 | 文档 SHA 更新 |
| 3 | 删除自行生成的通过记录 | 删除 `AUDIT_RECORD.md` | 文件集合 | 否 | 从 Manifest 移除 |
| 4 | 缺少输入 Evidence 清单 | 新增 15 行输入索引，逐 Session 登记 CAN/Event/照片集合和 SHA-256 | `input_evidence_manifest.csv` | 否 | 新文件 |
| 5 | 缺少逐张照片索引 | 新增 31 行照片索引，明确 S0023 E08 补拍处置 | `photo_evidence_index.csv` | 否 | 新文件 |
| 6 | METHOD 需限制为确定性方法合同 | 删除实现依赖表述，补足输出对应关系 | `METHOD.md` | 否 | 文档 SHA 更新 |
| 7 | 核对所有数量 | 补充逐 Session 表和数量闭合段 | `VALIDATION.md`, `SELF_REVIEW.md` | 否 | 文档 SHA 更新 |
| 8 | 核对报告关键数字与术语 | 给关键数字添加机器产物来源；统一 raw observation 术语 | `README.md`, `VALIDATION.md` | 否 | 文档 SHA 更新 |
| 9 | 核对 Evidence 边界 | 保留 UI/raw 相关性边界，明确无执行与物理制冷结论 | `README.md`, `METHOD.md`, `SELF_REVIEW.md` | 否 | 文档 SHA 更新 |
| 10 | 如结果有误需修正 | 第 1 轮复算未发现分类结果错误 | 全部机器结果 | 否 | 第 1 轮时两个新增索引外既有机器结果 SHA 不变；第 2 轮确定性并列规则使组明细重生成并另行记录 |
| 11 | 重建 Manifest 与指纹 | 纳入规定 15 项正式文件，排除预审意见文件，重算 SHA-256 | `archive_manifest.md` | 否 | 全包重新冻结 |

## 机器结果复核摘要

- 5 个 Session、65 个 triggered Events、5 个 ASC 段、3,711,471 帧。
- 16 个 Round 3 组、80 行逐轮组明细；按预审阶段旧组级口径为 15 组接受分类（该口径已由 `AUDIT_01` 整改替换）。
- 23 个旧 raw bit：9 个 HVAC/送风、5 个风量、8 个 A/C、1 个未分类。
- 400 条组×Session×Event 转换记录。
- 93 个全总线重复 raw bit observations。

整改没有改变既有分析算法、窗口、候选分类或机器结论。

## PREAUDIT_02

| # | 预审问题 | 整改位置 | 受影响文件 | 是否改变机器结果 | 指纹影响 |
|---:|---|---|---|---|---|
| 1 | 缺少逐 Event 正式索引 | 新增 65 行、键唯一的逐 Event 表，记录实际时间、窗口角色、照片数和源文件 SHA | `event_evidence_index.csv`, `VALIDATION.md`, `METHOD.md` | 否 | 新文件；文档 SHA 更新 |
| 2 | 输入清单混用时间基准 | 新增 `time_basis` 与 `timezone`；脚本秒和 ISO8601 墙钟明确区分 | `input_evidence_manifest.csv` | 否 | 该 CSV SHA 更新 |
| 3 | METHOD 确定性规则不完整 | 补充 bit 方向、并列、空窗、无效行、DLC、去重、排序、等距、无变化和全程转换定义 | `METHOD.md`, `round3_group_state_detail.csv` | 分类结论不变；完整字节并列模态现固定选择较小值 | 文档及组明细 SHA 更新 |
| 4 | VALIDATION 引用程序位置 | 改为“可复现摘要”，删除程序位置和命令引用 | `VALIDATION.md` | 否 | 文档 SHA 更新 |
| 5 | 正式提交物增加与状态文件更新 | 正式包增至 16 项；同步更新 README/VALIDATION/SELF_REVIEW/Manifest 状态记录 | README/VALIDATION/SELF_REVIEW/Manifest | 否 | 文档及 Manifest 重冻 |

### 第 2 轮闭合核对

- `event_evidence_index.csv`：65 行，`(session_id,event_id)` 65 个唯一键，状态全部 `triggered`。
- Event 索引关联照片合计 31，与 `photo_evidence_index.csv` 行数一致；S0023 E08 绑定 1 张补拍，注明不改变窗口。
- 每个 Session 的 Event 源 SHA 与 `input_evidence_manifest.csv` 对应 Event 集合 SHA 一致。
- 新增确定性规则后重跑，当时核心摘要仍为 5 Session、3,711,471 帧、16 组、旧口径 15 组接受分类、93 个全总线 raw bit observations；当前组级口径见 `AUDIT_01` 整改段。

第 2 轮整改没有改变稳态窗口、既有候选分类或核心结论。为消除完整字节模态并列的不确定性，`round3_group_state_detail.csv` 已按“并列取较小值”规则重生成，因此该明细文件指纹发生变化；组汇总、bit 拆分、转换和全总线分类结果不变。

## PREAUDIT_03

| # | 预审问题 | 整改位置 | 受影响文件 | 是否改变机器结果 | 指纹影响 |
|---:|---|---|---|---|---|
| 1 | 正式文件包含不必要的预审通过次数与后续安排 | 删除通过次数、下一文件编号和后续安排，仅保留已完成整改与当前状态 | README/VALIDATION/SELF_REVIEW/REWORK_RESPONSE/Manifest | 否 | 文档 SHA 更新 |
| 2 | METHOD 输入边界含否定性范围说明 | 收窄为实际采用输入的正面事实陈述 | `METHOD.md` | 否 | 文档 SHA 更新 |
| 3 | VALIDATION 可复现摘要含复核材料和实现范围说明 | 改为方法合同、冻结输入索引与关键数量的直接对应说明 | `VALIDATION.md` | 否 | 文档 SHA 更新 |
| 4 | 同步自审、答复和指纹 | 更新本节、自审和 Manifest | `SELF_REVIEW.md`, `REWORK_RESPONSE.md`, `archive_manifest.md` | 否 | 文档及 Manifest 重冻 |

第 3 轮只进行了预审指定的定点文本删除与收窄。机器统计、稳态窗口、候选分类、数量摘要、Evidence 结论边界和照片处置均未修改。

## PREAUDIT_04

| # | 预审问题 | 整改位置 | 受影响文件 | 是否改变机器结果 | 指纹影响 |
|---:|---|---|---|---|---|
| 1 | 答复中保留“通过 0 轮”等不必要计数 | 删除通过次数，只记录正式提交物增加和实际更新的状态文件 | `REWORK_RESPONSE.md` | 否 | 答复及 Manifest SHA 更新 |

第 4 轮未修改其他正式文件或机器结果。

## PREAUDIT_05

| # | 预审问题 | 整改位置 | 受影响文件 | 是否改变机器结果 | 指纹影响 |
|---:|---|---|---|---|---|
| 1 | 组内响应分化被过度解释为非单一字段 | 改为挑战原分组假设、需要重新评估，明确未确定真实字段边界；同步收窄标题 | `README.md`, `SELF_REVIEW.md` | 否 | 文档 SHA 更新 |
| 2 | “制冷链相关”超过 Evidence 层级 | 改为与本轮 A/C UI 切换相关，并明确分类名是实验刺激标签 | `README.md`, `METHOD.md`, `SELF_REVIEW.md` | 否 | 文档 SHA 更新 |
| 3 | 无解析失败被写成无帧缺损 | 改为未发现无法解析的数据样式行和时间戳倒退，明确不证明零丢帧 | `README.md`, `VALIDATION.md`, `METHOD.md`, `SELF_REVIEW.md` | 否 | 文档 SHA 更新 |
| 4 | 首末覆盖被过度解释为连续覆盖 | 改为首末时间覆盖六个稳态窗口，明确不单独证明段内连续 | `VALIDATION.md`, `METHOD.md`, `SELF_REVIEW.md` | 否 | 文档 SHA 更新 |
| 5 | 人读偏移精度和因果措辞超过时间基准 | 改为整秒级对齐偏移估计；负值归入对齐不确定范围；不作控制延迟和层级排序 | `README.md`, `METHOD.md`, `SELF_REVIEW.md` | 否 | 文档 SHA 更新 |
| 6 | “五轮同条件重复”范围过宽 | 改为相同采集设计和 UI 状态序列下重复，不假定未记录条件一致 | `README.md`, `VALIDATION.md`, `METHOD.md`, `SELF_REVIEW.md` | 否 | 文档 SHA 更新 |

第 5 轮仅收窄人读表述和审查记录。机器统计、稳态窗口、机器明细精度、候选分类结果、数量摘要和照片处置均未修改。

## AUDIT_01

| # | 正式审核问题 | 整改位置 | 受影响文件 | 机器结果或计数变化 |
|---:|---|---|---|---|
| 1 | 缺少 field-level hypothesis | 新增逐组存废与分区表，记录六状态值、成员响应、竞争解释、依据和边界 | `field_level_hypotheses.csv`, `METHOD.md`, `README.md`, `VALIDATION.md`, `SELF_REVIEW.md` | 新增 18 个候选分区；不改变 23 个 raw bit 值 |
| 2 | 组级单标签不能表达复合响应 | 组级接受改为互斥的单一响应、复合响应、常值、证据不足；G02/G07 标为复合并拆分 | `round3_group_summary.csv`, `round3_group_state_detail.csv`, `METHOD.md`, `README.md`, `VALIDATION.md` | 接受组由 15 改为 13；组级分类由 5/5/5 改为 5/4/4，另有复合 2、常值 1 |
| 3 | 照片集合指纹合同不可独立复算 | 当时定型 PHC1 文本合同并新增五集合复算表；该整改随后被 `AUDIT_02` 否定并由 PHC2 替换 | `input_evidence_manifest.csv`, `photo_collection_hash_verification.csv`, `METHOD.md`, `VALIDATION.md` | PHC1 登记值已废止；当前值见 `AUDIT_02` 整改段 |
| 4 | 正式状态自审与顶层入口矛盾 | 当前状态统一为正式审核裁决 | `results/README.md` 及 Round 4 六个状态入口 | 状态统一为 `OPEN / REWORK_REQUIRED` |
| 5 | 更新归档与说明机器变化 | 正式包增至 18 项并重算所有受影响文件 SHA-256 | `archive_manifest.md`, `REWORK_RESPONSE.md` | raw-bit 9/5/8/1、400 条转换、93 条全总线观察均不变 |

本轮没有修改 `AUDIT_01.md`，没有引入新数据或外部答案。改变的是组级接受语义和相应计数；raw bit 的六状态值、窗口、帧数、转换明细和全总线观察不变。

## AUDIT_02

| # | 正式复审问题 | 整改位置 | 受影响文件 | 机器结果或计数变化 |
|---:|---|---|---|---|
| 1 | PHC1 合同、计算值和登记值未获独立复审核验 | 废止基于 Unicode 文件名和文本换行的 PHC1；定型 PHC2：按 ASCII `photo_id` 排序，将逐张 SHA-256 解码为 32-byte binary digest 后直接连接并哈希 | `METHOD.md`, `photo_collection_hash_verification.csv` | 集合摘要算法改变 |
| 2 | 五个集合登记值与复算 Evidence 不闭合 | 使用 Python CSV/二进制实现和 shell `awk/sort/xxd/shasum` 两条独立路径复算；六图 payload 192 bytes、七图 payload 224 bytes | `input_evidence_manifest.csv`, `photo_collection_hash_verification.csv`, `VALIDATION.md`, `SELF_REVIEW.md` | 五个照片集合登记 SHA-256 全部更新；照片数量与逐张 SHA-256 不变 |
| 3 | 同步报告、状态与指纹 | 更新审核轮次说明、整改答复、正式入口和所有受影响文件指纹 | `README.md`, `results/README.md`, `REWORK_RESPONSE.md`, `archive_manifest.md` | 状态保持 `OPEN / REWORK_REQUIRED`；其他分析机器结果不变 |

PHC2 独立复算结果：S0019 `57e9dde3…1e29`，S0020 `737f03a2…d3cd`，S0021 `71ede58b…1882`，S0022 `2fd898b7…4733`，S0023 `0c466c0e…ab2f`；完整 64 位值见两份正式机器表。本轮未修改 `AUDIT_01.md` 或 `AUDIT_02.md`，未改变照片逐张指纹、分析窗口、raw-bit/组级/字段假设、转换或全总线结果。

## AUDIT_03 状态归档

`AUDIT_03.md` 最终复审裁决为 `CLOSED`。本次仅同步正式状态入口、自审、整改答复和归档指纹；分析结论与机器 Evidence 未修改。
