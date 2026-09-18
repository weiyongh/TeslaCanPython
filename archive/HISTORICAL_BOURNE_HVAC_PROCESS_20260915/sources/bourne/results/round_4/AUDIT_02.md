# Bourne Round 4 — M Re-Audit

## 一、复审边界

本次只复核 `AUDIT_01.md` 所列整改是否由 Round 4 修订后的正式提交物实际完成，不使用当前提交之外的既有答案，不检查分析程序或过程材料。

`AUDIT_01.md` 保持原样。

## 二、已通过的整改

1. `field_level_hypotheses.csv` 已覆盖 16 个继承组，形成 18 个候选分区，并记录六状态值、存废状态、竞争解释、支持或否定依据及 Evidence Boundary。
2. 字段级结论保持在 hypothesis 层级。同步或互补 raw bit 没有被写成已确认字段，无法由现有状态区分的解释被并列保留。
3. 组级机器产物已将 13 个单一响应组、2 个复合响应组和 1 个常值组互斥区分；5/4/4 的接受分类计数与 README、VALIDATION 和 SELF_REVIEW 一致。
4. 23 个 raw bit 的 9/5/8/1 结果、400 条转换记录、93 条全总线补充观察以及原有窗口和帧数均未发生未说明的变化。
5. `results/README.md` 与 Round 4 正式状态文件现均为 `OPEN / REWORK_REQUIRED`；自审中的状态依据与实际文件一致。
6. `archive_manifest.md` 所列正式文件指纹与当前文件一致。

## 三、未通过的整改

### 照片集合指纹复算仍不成立

`METHOD.md` 新增的 PHC1 合同规定：按 `source_file_name` 的 Unicode code-point 升序排列，将每项拼为“文件名原文、两个 ASCII 空格、小写 SHA-256、LF”，以 UTF-8 无 BOM 连接后计算 SHA-256。

严格使用 `photo_evidence_index.csv` 的正式逐张记录按该合同复算，S0019–S0023 五个 Session 的结果均不等于 `input_evidence_manifest.csv` 的登记值，也不等于 `photo_collection_hash_verification.csv` 的 `computed_sha256`。

因此，`photo_collection_hash_verification.csv` 中五行 `match=True`、VALIDATION 中“5/5 一致”以及 SELF_REVIEW 中对应 PASS 均与可复算结果矛盾。PHC1 合同、计算值和登记值三者仍未闭合。

## 四、当前最准确的结论边界

本轮已从 raw-bit stimulus classification 推进到可审核的 field-level hypothesis：它对继承组完成了保留、拆分或暂停裁决，并明确保留边界竞争解释。这不等同于字段边界或系统语义已经确认。

数据、窗口、raw-bit 分类、组级重分类和字段假设之间已基本闭合；但照片集合 provenance 的新增机器 Evidence 不真实可复算，因此正式 Evidence 包仍不能通过。

## 五、当前 Round 整改要求

1. 按正式声明的唯一合同重新独立计算五个照片集合指纹，修正计算值、登记值或书面合同，使三者真实一致。
2. 同步修正 `photo_collection_hash_verification.csv`、`input_evidence_manifest.csv`、VALIDATION、SELF_REVIEW、REWORK_RESPONSE 及受影响的归档指纹。
3. 整改后自行从正式逐张索引重新复算，不得以“计算值等于登记值”的抄录代替实际计算。

## 六、状态裁决

`OPEN / REWORK_REQUIRED`

本次只整改现有照片集合 provenance。不得修改 `AUDIT_01.md` 或 `AUDIT_02.md`，不得新采集，不提交下一阶段计划。整改完成后停止并等待复审。
