# HVAC Round 4 第 2 次预审整改意见

## 一、预审结论

第1次预审整改已完成状态回退、正式提交物补充、数量闭合和归档指纹重建，但当前提交仍存在事件追溯、时间基准和方法定型问题。

本次预审结论：

`PREAUDIT_REWORK_REQUIRED`

Round 4状态继续保持：

`REVISED / PENDING_RE-AUDIT`

本结论不构成正式审核通过，不得进入正式审计或下一阶段工作。

## 二、已确认完成或本轮放行的事项

1. 已撤销未经正式复审确认的“审核通过”和 `CLOSED`。
2. 正式状态已统一为 `REVISED / PENDING_RE-AUDIT`。
3. 自行生成的通过性审核记录已删除。
4. 已提交 `input_evidence_manifest.csv` 和 `photo_evidence_index.csv`。
5. Session、帧数、候选组、raw bit、分类、转换记录和全总线观察数量在现有正式产物之间闭合。
6. Manifest所列正式文件的当前SHA-256与 `archive_manifest.md` 一致。
7. 五个照片集合指纹均可由 `photo_evidence_index.csv` 中逐张照片的文件名和SHA-256重建。
8. 接受S0023第七张照片为现场意外情况下的补拍；该照片与原照片记录同一状态，不改变Event或分析窗口。本轮不再要求就照片数量、补拍处置及S0/S5照片表述返工，相关事项不作为预审阻塞项。

## 三、必须整改的问题

### 1. 缺少逐Event正式Evidence索引

当前 `input_evidence_manifest.csv` 只为每个Session登记一条 `E01-E13` 集合记录，尚未逐Event记录：

- Event ID；
- Event状态；
- 实际触发时间；
- 是否参与窗口构造；
- 对应窗口边界角色；
- 关联照片数量。

整改要求：新增 `event_evidence_index.csv`，每个Session的E01至E13各一行，共65行。

至少包含：

```text
session_id
event_id
event_status
event_time_s
used_for_window
window_role
linked_photo_count
source_file_name
source_file_sha256
notes
```

要求：

- 65行唯一对应 `5 Session × 13 Events`；
- Event状态与 `VALIDATION.md` 一致；
- Event时间能够按 `METHOD.md` 的规则重建六个稳态窗口；
- 照片数量与 `photo_evidence_index.csv` 一致；
- S0023补拍绑定实际Event，并保持原有分析窗口不变；
- 文件指纹与 `input_evidence_manifest.csv` 中对应Event文件一致。

### 2. 输入清单未明确区分时间基准

`input_evidence_manifest.csv` 的 `first_time`、`last_time` 同时使用相对脚本时间的数字秒和带时区的墙钟时间，但没有标明时间基准。

整改要求：增加：

```text
time_basis
timezone
```

并使用明确取值区分：

```text
SCRIPT_RELATIVE_SECONDS
WALL_CLOCK_ISO8601
```

不适用的时区字段留空，不使用默认时区隐式解释。

### 3. `METHOD.md` 尚未完整定型确定性规则

现有方法已记录主要窗口、纯度门槛和分类条件，但以下规则仍需明确：

- 字节内bit编号方向；
- 模态值并列时的处理；
- 某窗口无样本时的处理；
- 无效记录的精确定义；
- 不同数据长度的处理；
- 候选去重单位；
- 输出排序规则；
- 转换搜索中距离相同候选的选择规则；
- before与after相等时的转换记录规则；
- `full_session_masked_transitions` 的精确定义。

这些内容属于确定性方法合同，不是程序实现说明。

整改要求：在 `METHOD.md` 中明确上述规则，使相同输入和相同方法合同得到唯一结果。

### 4. `VALIDATION.md` 仍包含分析程序位置

`VALIDATION.md` 的“可复算命令”章节没有提供实际命令，却写入分析程序位置及相关说明。

整改要求：

- 删除分析程序位置及相关说明；
- 将章节改为“可复现摘要”或其他准确名称；
- 只保留正式方法合同、输入Evidence与预期结果摘要之间的关系；
- 不提交或引用分析程序。

## 四、正式提交物调整

第2次整改后，正式提交物增加：

`event_evidence_index.csv`

`archive_manifest.md` 应同步更新正式提交物数量、文件用途和SHA-256。

`PREAUDIT_01.md` 与 `PREAUDIT_02.md` 继续作为预审意见原件保留，不计入正式提交物冻结清单。

## 五、整改答复与停止点

完成整改后：

1. 更新 `REWORK_RESPONSE.md`，分别回应 `PREAUDIT_01.md` 和 `PREAUDIT_02.md`；
2. 更新 `SELF_REVIEW.md`；
3. 更新 `archive_manifest.md` 和正式提交物SHA-256；
4. 状态继续保持：

`REVISED / PENDING_RE-AUDIT`

提交后停止，等待复审。

不得自行记录预审通过、正式审核通过、`CLOSED`或任何下一阶段状态；不得执行新的采集。
