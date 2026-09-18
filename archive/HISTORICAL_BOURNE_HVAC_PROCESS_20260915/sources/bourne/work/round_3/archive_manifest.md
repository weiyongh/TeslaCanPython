# 第三轮归档清单

## 正式结果

| 文件 | 内容 |
|---|---|
| `results/round_3/README.md` | 正式结论、与第二轮差异、证据理由和限制 |
| `results/round_3/VALIDATION.md` | 数据、方法和结果验收记录 |
| `results/round_3/session_quality.csv` | 五轮 CAN 覆盖与稳态窗口 |
| `results/round_3/timeline_reconstruction.json` | 每轮 ASC 墙钟偏移、覆盖范围与实际窗口 |
| `results/round_3/cross_round_bit_candidates.csv` | 52 个跨轮 raw bit 及二态复现标志、原始偏移汇总 |
| `results/round_3/candidate_session_detail.csv` | 全部共同可观测 bit 的逐轮窗口统计与单轮通过标志；用于审计被淘汰项 |
| `results/round_3/candidate_byte_context.csv` | 52 个候选所在字节的逐轮模态值、纯度和唯一值数 |
| `results/round_3/candidate_transitions.csv` | 每个候选逐轮的转换时刻、延迟和全程翻转数 |
| `results/round_3/raw_field_groups.csv` | 23个复现 raw bit 归并出的16个字节级待恢复字段组 |
| `results/round_3/prior_round_candidates_validation.csv` | 第二轮五个优先候选的定向复核 |
| `results/round_3/M_Round3_Pure_Audit.md` | M 对原第三轮报告的纯审计意见（原文保留） |
| `results/round_3/M_Round3_ReAudit.md` | M 对修订版第三轮的复审意见（原文保留） |
| `results/round_3/B_Round3_Self_Review.md` | 伯恩对审计项的独立复核与整改状态 |
| `results/round_3/B_Round3_Final_ReAudit_Evidence.md` | 伯恩提交的最终复审证据与被核验版本指纹 |
| `results/round_3/M_Round3_Final_ReAudit.md` | M 最终复审与 Round 3 关闭裁决 |

## 可复现过程

| 文件 | 内容 |
|---|---|
| `src/analyze_hvac_repeated_rounds.py` | 五轮逐会话筛选、转换扫描和结果生成脚本 |
| `work/round_3/process_session.md` | 方法选择、执行步骤、结果收敛和证据边界 |
| `work/round_3/round_2_preserved.sha256` | 第二轮产物当前校验值，用于证明后续未被覆盖 |

复现命令：`.venv/bin/python src/analyze_hvac_repeated_rounds.py`

## Gate 状态文件指纹

```text
c63837de5f1962efa77c6107beb3b930e7164595a5bd9e96b6ea5ffcd6cbb668  results/round_3/README.md
e1e0d314f0eba4da51f20f012f886e4ee364e3e153826770189497adb9881b20  results/round_3/VALIDATION.md
d9d09054c9003bc0f4e46458d19ec4fe6a67400cb6ea0522954265b6fae4fe7b  results/round_3/B_Round3_Self_Review.md
918af639739f389df4d0aa4b915ad69b8c8c66308247e8ae9d2e4d80f425c7fd  results/round_3/B_Round3_Final_ReAudit_Evidence.md
1ab91d1bcca62e1cf70bc9b0026d6e062a1bd73d319f7bb61b1f6484a75945ac  results/round_3/M_Round3_Final_ReAudit.md
8c86b47921ae5475f4d581bb4c81c8cadbf7f2c3c21cfac8cffd359a2628bf20  work/round_3/process_session.md
```

归档状态：`CLOSED`。本归档只覆盖 Round 3 现有数据复核与最终 Gate 状态，不包含下一轮 Acquisition Plan。
