# 第二轮归档清单

## 归档主题

HVAC / 交流慢充 ASC 分段时间轴重建、双对照候选筛选，以及慢充三次独立单轮现场验证方案。

## 正式结果

正式结果根目录：`results/round_2/`

| 文件 | 角色 |
|---|---|
| `results/round_2/README.md` | 第二轮结论、优先候选、限制和下一轮实验请求 |
| `results/round_2/VALIDATION.md` | 帧数、共同候选数和语义约束验证记录 |
| `results/round_2/structured_timeline_reconstruction.json` | HVAC 与慢充 ASC 分段的统一时间轴重建数据 |
| `results/round_2/structured_bit_candidates.csv` | bit 级严格状态候选 |
| `results/round_2/structured_byte_candidates.csv` | byte 级枚举与连续变化候选 |

## 可复现分析入口

| 文件 | 角色 |
|---|---|
| `src/analyze_structured_segments.py` | 使用 ASC 文件头墙钟与 `session.start_clock` 重建时间轴并生成候选结果 |

## 过程与决策记录

| 文件 | 角色 |
|---|---|
| `work/round_2/process_session.md` | 分段重置发现、时间轴重建、双对照筛选、第一轮结论修正与后续方案决策 |
| `work/round_2/archive_manifest.md` | 本归档清单 |

## 后续采集脚本

| 文件 | 角色 |
|---|---|
| `experiment_vault/scripts/L3-Charge-Slow-MinSingRound_单人最低负担慢充单轮采集脚本.txt` | 单人最低负担慢充单轮脚本；现场独立执行三次 |

## 关键归档声明

- HVAC 与慢充 ASC 均出现分段内部时间戳从零重置，必须按文件头墙钟与 `session.start_clock` 统一到脚本时间。
- 第一轮零候选结论因时间轴未拼接而失效，已由第二轮结果修正。
- 候选采用动作前、动作中、动作后的双对照筛选，仍保持未知总线候选语义，不写成已确认 DBC 定义。
- 慢充后续方案为三次独立单轮，而不是在一个会话内连续完成三轮。
- `work/round_2/` 保存过程归档；可引用的正式结果以 `results/round_2/` 为准。
