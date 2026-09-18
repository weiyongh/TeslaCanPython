# Bourne Round 4 — M Final Re-Audit

## 一、复审边界

本次只复核 `AUDIT_02.md` 所列照片集合 provenance 整改及正式提交一致性，不使用当前提交之外的既有答案，不检查分析程序或过程材料。

`AUDIT_01.md` 与 `AUDIT_02.md` 保持原样。

## 二、核验结果

1. PHC2 合同已明确定型：按 ASCII `photo_id` 排序，将每张照片的 64 位 SHA-256 十六进制文本解码为 32 个原始字节，依序连接后计算集合 SHA-256。
2. 使用 `photo_evidence_index.csv` 独立复算，S0019–S0022 的 payload 均为 192 bytes，S0023 为 224 bytes。
3. 五个 Session 的独立计算值均与 `photo_collection_hash_verification.csv` 的 `computed_sha256` 以及 `input_evidence_manifest.csv` 的登记值一致；五行 `match=True` 成立。
4. VALIDATION、SELF_REVIEW 和 REWORK_RESPONSE 对该整改的记录与机器 Evidence 一致。
5. `archive_manifest.md` 所列 17 个非自引用正式文件的 SHA-256 均与当前文件一致。
6. `AUDIT_01.md` 的其他整改在上一轮复审中已通过，本轮未发现其机器结果、字段假设或 Evidence 边界发生未说明变化。

## 三、最终结论边界

Round 4 已证明 23 个既有 raw bit 在五次相同采集设计和 UI 状态序列下的可重复多状态刺激响应，并将继承组定型为可审核的字段级候选分区、存废裁决和竞争解释。

这些结果属于 field-level hypothesis，不等同于字段边界、系统语义、发送来源、控制层级或物理执行已经确认。93 个全总线补充结果仍只按 raw bit observation 计数。

## 四、状态裁决

`CLOSED`

本裁决只关闭 Round 4 正式分析。伯恩应仅将 `results/README.md`、Round 4 正式状态文件、自审、整改答复和归档清单同步为 `CLOSED`，重新计算受影响文件指纹；不得修改本轮分析结论或机器 Evidence。

完成状态归档后停止。不得提交下一阶段计划，不得开展新的采集或下一阶段工作。
