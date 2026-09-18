# Round 4 可复核方法与盲态边界

正式状态：`CLOSED`。

## 输入边界

本轮分析采用 S0019–S0023 的 Session 记录、Event 记录、总线记录和照片，以及 Round 3 正式提交的 16 个既有候选组。

## 时间轴重建

每个 ASC 文件首行的墙钟时间减去 `session.start_clock` 得到文件相对脚本起点的偏移；每帧 ASC 相对时间加该偏移，得到脚本时间。逐文件检查解析失败和时间戳倒退。本批每轮只有一个 ASC 段。该检查不包含可证明丢帧为零的序号连续性证据，也未设帧间隔连续性判据。

## 预注册稳态窗口

全部边界使用每轮实际事件触发时间：

| 状态 | 窗口 |
|---|---|
| S0 | E02+5 s 至 E03−5 s |
| S1 | E04 至 E05−5 s |
| S2 | E06 至 E07−5 s |
| S3 | E08 至 E09−5 s |
| S4 | E10 至 E11−5 s |
| S5 | E12 至 E13−5 s |

转换区不混入稳态统计。

## 稳态统计与五轮门槛

对每个 CAN ID、字节和 bit，在每个状态窗口统计取值频次、模态值、样本数和模态纯度。候选必须同时满足：六个窗口均有样本；每个窗口纯度至少 95%；五轮的六状态模式完全相同。任何总体多数不能替代单轮失败。

确定性细则：

- 字节编号从 payload 首字节 `B0` 开始；bit 编号为 Intel 式字节内最低有效位 `b0` 至最高有效位 `b7`。本轮不据此声明跨字节信号字节序。
- 模态纯度＝模态计数/该窗口有效样本总数。完整字节模态并列时选择数值较小者；单 bit 的 0/1 计数并列时选择 0。
- 任一目标窗口没有该 CAN ID/字节的有效样本时，该候选不进入五轮交集，也不输出为通过项。
- “无效记录”定义为首个非空白字符是数字、因而形似 ASC 数据行，但不能由正式 ASC 解析规则得到时间戳、CAN ID、DLC 和完整 payload 的行。文件头、注释和空行不计无效记录。
- DLC 不同时，只统计实际 payload 中存在的字节；短帧中不存在的字节不补零。若这造成某窗口无样本，按上一条淘汰。
- bit 候选去重单位是 `(CAN ID, payload字节索引, 字节内bit索引)`；Round 3 组单位是既有 `group_id + CAN ID + byte + mask`，不同位置不因轨迹相同而合并。

Round 3 组先按完整字节保存上下文，再按旧候选掩码统计掩码模态值与纯度，最后拆分组内 bit。下列分类名是实验刺激标签，不是字段或系统语义命名；raw-bit 分类规则为：

- HVAC/送风开启相关：S0=S5，且 S1=S2=S3=S4，与关闭侧不同。
- 风量敏感：S1≠S2 且 S2=S4；本批通过者同时满足 S2=S3=S4。
- A/C UI 切换可逆相关：S2=S4 且 S3 与二者不同。
- S2≠S4 的观察保留为非可逆/动态候选，不强行分类；本批严格五轮结果中没有形成该类正式 bit 清单。

全总线补充筛选使用相同逐轮门槛。其计数单位是 raw bit observation，不是 Signal 或独立 Evidence。

## 组级接受与字段假设合同

组级状态按下列互斥顺序确定：

1. 若组内所有成员六状态常值，记为 `constant`，不接受刺激分类。
2. 若组内成员出现两个或更多 raw-bit 刺激类别，记为 `composite_response`，原组必须拆分，不接受单一组标签。
3. 若全部成员属于同一刺激类别且每个成员满足五轮门槛，记为 `single_response`，接受该实验刺激标签。
4. 其他情况记为 `insufficient_evidence`，不接受分类。本批没有该类。

字段候选分区先按继承组边界建立，再将复合响应组按 raw-bit 刺激类别拆分。每个分区保存六状态取值、成员响应一致性、存废状态、竞争解释、支持或否定依据和 Evidence Boundary。单 bit 分区只是最小候选边界；同步或互补的多 bit 分区只保留为未决边界。轨迹一致不是自动合并条件，现有状态不能区分时必须并列保留“一个多 bit 字段”“多个同步/互补 flag”“复制或派生值”等解释。

## 照片集合指纹合同 PHC2

每个 Session 只使用 `photo_evidence_index.csv` 中该 Session 的行。`photo_id` 必须为 ASCII，按其原始 ASCII 字节升序排列；将每行的 64 位 `sha256` 十六进制文本解码为恰好 32 个原始字节，按排序顺序直接连接，不加入文件名、分隔符、换行、表头、BOM 或其他字节；最后对长度严格为 `photo_count × 32` 的 payload 计算 SHA-256。`photo_collection_hash_verification.csv` 保存照片数、payload 字节数、独立计算值、输入清单登记值与匹配结果。该合同不依赖 Unicode 文件名或 CSV 文本序列化。

输出排序固定为：Session 按 ID 升序；CAN ID 按数值升序；byte、bit 按索引升序；Round 3 组按 `group_id` 升序；Event 按 E03、E05、E07、E09、E11 顺序。分类不参与改变机器表的基础位置排序。

## 转换匹配

对 Round 3 掩码组扫描完整会话内的掩码变化。E03、E05、E07、E09、E11 分别使用相邻稳态模态作为预期 before→after 方向，只在事件前 5 s 至后 15 s 内寻找方向一致的变化，并选择距事件最近者。保存原始事件时刻、变化时刻、偏移、方向是否匹配和全程变化数。

- 若两个方向匹配变化与 Event 的绝对距离完全相同，选择脚本时间较早者。
- 若相邻稳态的 before 与 after 相等，则不存在预期状态变化：仍输出该组×Session×Event 记录，但 `transition_s` 和 `delay_s` 留空、`direction_match=False`，不把无变化伪装成转换。
- `full_session_masked_transitions` 是在完整重建会话内，按时间顺序观察同一 CAN ID 时，候选字节与掩码相与后的值相对上一个可用同 ID payload 发生改变的次数。缺少该字节的短帧被忽略，且不会清空上一个可用值；跨 ASC 段时延续上一个值。本批每轮只有一段。

ASC 文件头为整秒精度，偏移仅支持“对齐精度内”与“数秒后”层级，不支持亚秒因果排序。`delay_s` 是重建时间轴上的对齐偏移估计，不是控制响应延迟；负值只表示落在对齐不确定范围内，不解释为事件前响应，也不用于确定请求、许可、执行或反馈顺序。

## Evidence 边界

照片只确认 UI 设置。当前数据没有固定出风温度、压缩机、电功率、压力或音频 Evidence。因此分类只表达与本轮实验刺激的相关性，不确认 DBC 名称、字段真实边界、发送 ECU、请求/许可/执行层或实际制冷建立。五轮采用相同采集设计和 UI 状态序列；未完整记录的车辆与环境条件不默认为一致。

## 正式输出对应关系

| 输出 | 方法阶段 |
|---|---|
| `input_evidence_manifest.csv` | 输入文件、集合指纹、数量与覆盖登记 |
| `photo_evidence_index.csv` | 逐张 UI Evidence 核验与补拍处置 |
| `event_evidence_index.csv` | 65 个 Event 的状态、实际时间、窗口角色和照片关联 |
| `session_quality.csv` | 会话、帧、时间轴与窗口完整性 |
| `timeline_reconstruction.json` | ASC 分段偏移和正式窗口 |
| `round3_group_state_detail.csv` | 16 个组的逐轮完整字节/掩码统计 |
| `round3_group_summary.csv` | 组级五轮一致性与分类 |
| `round3_bit_disambiguation.csv` | 23 个旧 bit 的六状态拆分 |
| `field_level_hypotheses.csv` | 16 个继承组的 18 个字段候选分区与存废裁决 |
| `round3_group_transitions.csv` | 组级方向匹配和时间偏移 |
| `all_bus_repeatable_bit_hypotheses.csv` | 相同门槛下的全总线补充观察 |
| `photo_collection_hash_verification.csv` | PHC2 照片集合指纹独立复算结果 |
