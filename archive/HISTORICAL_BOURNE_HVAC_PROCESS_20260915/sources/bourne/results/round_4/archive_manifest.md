# Round 4 正式提交归档清单

当前状态：`CLOSED`。

已完成 `PREAUDIT_01.md` 至 `PREAUDIT_05.md` 的整改，第 6 次预审通过；`AUDIT_01.md` 与 `AUDIT_02.md` 整改完成，`AUDIT_03.md` 最终裁决为 `CLOSED`。六份预审文件与三份正式审核意见原件保留在同目录，但不属于下列 18 项正式提交物，也不由本 Manifest 冻结。

| # | 文件 | 作用 |
|---:|---|---|
| 1 | `README.md` | 正式结论、Evidence 边界与状态 |
| 2 | `VALIDATION.md` | 输入完整性、数量闭合、门槛和限制 |
| 3 | `METHOD.md` | 确定性方法合同与输出对应关系 |
| 4 | `input_evidence_manifest.csv` | 五轮 CAN、Event 与照片集合输入索引 |
| 5 | `photo_evidence_index.csv` | 31 张照片逐张事实、指纹及补拍处置 |
| 6 | `event_evidence_index.csv` | 65 个 Event 的时间、窗口角色、照片关联和源指纹 |
| 7 | `session_quality.csv` | 五轮覆盖与完整性 |
| 8 | `timeline_reconstruction.json` | ASC 墙钟到脚本时间重建 |
| 9 | `round3_group_state_detail.csv` | 16 组 × 5 轮的完整字节/掩码六状态轨迹 |
| 10 | `round3_group_summary.csv` | 16 个旧组的五轮分类汇总 |
| 11 | `round3_bit_disambiguation.csv` | Round 3 的 23 个 raw bit 六状态拆分 |
| 12 | `field_level_hypotheses.csv` | 16 个继承组的 18 个字段候选分区与存废裁决 |
| 13 | `round3_group_transitions.csv` | 16 组 × 5 轮 × 5 事件的方向和时刻明细 |
| 14 | `all_bus_repeatable_bit_hypotheses.csv` | 全总线 93 个重复稳态 raw bit observations |
| 15 | `photo_collection_hash_verification.csv` | PHC2 合同下五个照片集合指纹复算 |
| 16 | `SELF_REVIEW.md` | 提交完整性、内部一致性与 Evidence 边界自审 |
| 17 | `REWORK_RESPONSE.md` | 五轮预审、两轮正式审核整改及最终关闭记录 |
| 18 | `archive_manifest.md` | 本归档索引；自身不设自引用 SHA-256 |

## 冻结 SHA-256

以下指纹冻结除本清单自身之外的全部 17 项正式提交物。清单自身因自引用不可能获得有限稳定哈希，标记为 `SELF / NOT HASHED`。

```text
ac37a2660d0e45a75708e5a99cd9f40b0dc54924df0bdf501de566532fb30a91  README.md
3be154e4387c11587389c315aae0984c257ddeba956b369889c4412d8d56bfd7  VALIDATION.md
73565dbc295afddc0b15a639e495a7484608dd1b6fe95c0fc382e222e8c0c9f2  METHOD.md
759cc41159f854f2a7ba818fb68961dcfc27376739600fd4eed8a2f71b1c7c57  input_evidence_manifest.csv
6e312b01abfbe6e127cba78d08d3930de10e699251cdb2a12f6613f853fd3f8b  photo_evidence_index.csv
5568b7c126dd2c9da028dd857385cdca5a415d44cd72d34c6233f05eb4dd8194  event_evidence_index.csv
2c35d5d49d0193aafd537323d17a5a62e4da75a326699eb6de222738a07de6df  session_quality.csv
a04c5b1cff85019c9ef4b07c683b043b1fb922078fa7520b4239e28ee09f38a6  timeline_reconstruction.json
f75ed744252ae57b80c20b856bd513665f076f5264f3b58af60ba7c3d6e1315b  round3_group_state_detail.csv
3df75d40ded52e99955fc90625e7387c0dc9fd6a76c485d6381de2710a1e7312  round3_group_summary.csv
2645ef951c052d9a29754224dc39600e76d415082ceb75296a1f0886de625ace  round3_bit_disambiguation.csv
bde261f0860084f50c442f0a141fd9c32401f587d6e57805d32e9f65be3b1b5e  field_level_hypotheses.csv
da57dfdb4a469ac1821b765f6a2975d4685b2f77b53b207c99c1f1d9b2c215e3  round3_group_transitions.csv
63857fe3b7dd8d57e5bd48b5ca7f0c7a77f8b689b591bb956d38dbe3be73630d  all_bus_repeatable_bit_hypotheses.csv
53a7f0bed33d111c4a210a198f3dbf8794e74a0463a5929f45a82bf65aecd19b  photo_collection_hash_verification.csv
7f2877d6072147645b8d929c4427f3e7f637f63bf154519a9358a8842a826967  SELF_REVIEW.md
26bb608b34365eddda2986dc931c16d7fd1e14ab95dc8c39e4a8fb023e9b8bc1  REWORK_RESPONSE.md
SELF / NOT HASHED                                                        archive_manifest.md
```

正式入口 `../README.md` 位于 Round 4 包外，其当前 SHA-256 为：

```text
80da98a2e25e86b4ca8671ae0274eca34dbbb5e874c8fcecf37e49130c59834b  ../README.md
```
