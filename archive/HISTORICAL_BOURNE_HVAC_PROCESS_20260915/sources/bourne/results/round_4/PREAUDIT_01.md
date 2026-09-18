# HVAC Round 4 预审整改意见

## 一、当前任务

请修订 HVAC Round 4 正式提交物。

当前状态：

`OPEN / REWORK_REQUIRED`

此前仅完成预审，不构成正式审核通过。未经正式复审，不得将状态记录为 `CLOSED`，也不得自行创建“审核通过”记录。

本次仅整理、核对和完善现有 Round 4 数据及正式产物，不进行新采集，不开展下一阶段工作。

## 二、正式提交物

本次正式提交包括：

1. `README.md`
2. `VALIDATION.md`
3. `METHOD.md`
4. `input_evidence_manifest.csv`
5. `photo_evidence_index.csv`
6. `session_quality.csv`
7. `timeline_reconstruction.json`
8. `round3_group_state_detail.csv`
9. `round3_group_summary.csv`
10. `round3_bit_disambiguation.csv`
11. `round3_group_transitions.csv`
12. `all_bus_repeatable_bit_hypotheses.csv`
13. `SELF_REVIEW.md`
14. `REWORK_RESPONSE.md`
15. `archive_manifest.md`

正式提交包仅包含定型结论、方法合同、Evidence索引、机器产物、自审与整改记录；不纳入工作过程、探索草稿、临时产物和下一阶段计划。

## 三、各提交物要求

### 1. `README.md`

记录：

- 本轮数据范围；
- 已确认的事实；
- 主要分析结果；
- Evidence支持的结论；
- 尚不能确定的事项；
- 当前状态。

关键数字应注明其对应的数据来源或机器产物。

结论不得超过现有Evidence覆盖范围。

### 2. `VALIDATION.md`

记录：

- Session数量及标识；
- 各Session完成状态；
- Event数量和完整性；
- 数据段数量；
- 各Session帧数与总帧数；
- 首末时间；
- 无效记录数量；
- 时间戳倒退情况；
- 六个稳态窗口覆盖；
- 照片数量与核验状态；
- 分类门槛；
- 已知限制。

### 3. `METHOD.md`

只记录本轮已经采用的确定性分析方法：

- 输入数据类型；
- 时间轴换算规则；
- 六个稳态窗口定义；
- 操作保护区；
- 模态值和纯度计算口径；
- 五轮一致性要求；
- 各分类的明确判定条件；
- 转换方向匹配规则；
- 时间精度边界；
- 各正式输出表之间的对应关系。

不记录程序实现、探索过程、调试经历、尝试顺序或失败路径。

### 4. `input_evidence_manifest.csv`

逐项登记本轮实际采用的输入Evidence。

至少包含：

session\_id
evidence\_type
source\_record\_id
source\_file\_name
sha256
record\_count
first\_time
last\_time
coverage\_summary
included\_in\_analysis
notes

要求：

- 分别登记五个Session的数据记录、Event记录和照片集合；
- 给出各项输入SHA-256；
- 记录各Session帧数及时间覆盖；
- 标明分段、遗漏、重复、替换或时间空洞；
- 输入数量与 `VALIDATION.md`、`session_quality.csv` 保持一致。

### 5. `photo_evidence_index.csv`

逐张登记照片Evidence。

至少包含：

session\_id
photo\_id
source\_file\_name
sha256
event\_id
claimed\_state
visible\_ui\_facts
recognition\_status
duplicate\_or\_retake
disposition
notes

要求：

- 每张照片单独一行；
- 只记录画面直接可见事实；
- 区分原拍、补拍和重复照片；
- 明确额外照片对应的Session、Event和状态；
- 记录补拍照片是否改变状态识别或分析窗口；
- 不根据画面推断无法直接观察的系统执行状态。

### 6. `session_quality.csv`

每个Session一行，至少记录：

- Session状态；
- Event数量；
- 照片数量；
- 音频状态；
- 数据段数量；
- 帧数；
- 首末时间；
- 预期结束时间；
- 无效记录数；
- 时间戳倒退数；
- 六个稳态窗口。

### 7. `timeline_reconstruction.json`

记录正式分析采用的时间轴：

- Session ID；
- 数据段标识；
- 时间偏移；
- 首末时间；
- 帧数；
- 六个稳态窗口。

### 8. `round3_group_state_detail.csv`

记录既有候选组在五轮六状态中的：

- 完整字节值；
- 掩码值；
- 样本数；
- 模态纯度；
- 唯一值数量；
- 状态轨迹；
- 逐轮分类结果。

### 9. `round3_group_summary.csv`

记录每个既有候选组的：

- 五轮一致性；
- 通过轮数；
- 最低窗口纯度；
- 重复轨迹；
- 分类；
- 分类是否接受；
- Evidence边界。

### 10. `round3_bit_disambiguation.csv`

记录既有raw bit的：

- 六状态轨迹；
- 五轮一致性；
- 最低窗口纯度；
- 分类；
- 分类是否接受；
- Evidence边界。

### 11. `round3_group_transitions.csv`

记录：

- Session；
- 候选组；
- Event；
- 预期变化方向；
- Event时刻；
- 观测变化时刻；
- 时间偏移；
- 方向是否匹配；
- 全程转换次数。

### 12. `all_bus_repeatable_bit_hypotheses.csv`

记录全总线补充观察，包括：

- 观测位置；
- 六状态轨迹；
- 分类；
- 五轮通过情况；
- 最低窗口纯度；
- Evidence边界。

必须明确每行的计数单位。

多个同步变化的raw bit不得自动视为多条独立Evidence。

### 13. `SELF_REVIEW.md`

记录本次提交前自审：

- 文件是否齐全；
- 状态是否一致；
- 输入与输出数量是否闭合；
- 文件指纹是否匹配；
- 报告与机器Evidence是否一致；
- 是否存在超过Evidence的表述；
- 哪些问题仍无法由现有数据确定。

自审不得代替正式复审，不得记录“审核通过”。

### 14. `REWORK_RESPONSE.md`

逐项记录：

- 预审问题；
- 整改位置；
- 受影响文件；
- 是否改变机器结果；
- 文件指纹变化说明。

### 15. `archive_manifest.md`

记录：

- 全部正式提交文件；
- 每个文件用途；
- 当前状态；
- 除清单自身外各提交文件SHA-256；
- 清单自身标记为 `SELF / NOT HASHED`。

## 四、必须整改的问题

1. 撤销所有未经正式复审确认的“审核通过”和 `CLOSED`。
2. 当前状态统一为 `OPEN / REWORK_REQUIRED`。
3. 删除现有自行生成的通过性审核记录。
4. 补充 `input_evidence_manifest.csv`。
5. 补充 `photo_evidence_index.csv`。
6. 将现有方法说明整理为 `METHOD.md`，仅保留确定性方法合同。
7. 核对Session、Event、照片、各Session帧数、总帧数、候选组、raw bit、分类及转换记录数量。
8. 核对 `README.md`、`VALIDATION.md` 与正式机器产物中的关键数字和术语。
9. 核对所有结论是否处于现有Evidence覆盖范围。
10. 如发现原结果有误，应修正并在 `REWORK_RESPONSE.md` 中说明影响。
11. 重新生成 `archive_manifest.md` 和相应文件指纹。

## 五、本次暂不处理

本次整改不裁决分析是否已经推进到更高层级的候选建模，也不开展下一阶段实验设计。

## 六、提交状态与停止点

完成整改后，状态统一设为：

`REVISED / PENDING_RE-AUDIT`

提交后停止，等待复审。

不得自行写入“审核通过”、`CLOSED`或下一阶段状态；不得执行新的采集。
