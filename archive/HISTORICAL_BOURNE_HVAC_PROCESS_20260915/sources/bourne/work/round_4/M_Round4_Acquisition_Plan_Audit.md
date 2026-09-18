# 伯恩 Round 4 Acquisition Plan — M Audit

## 审核范围

本次只审核 `work/round_4/acquisition_plan.md`、其知识对照 Review，以及归档清单明确引用的两份现场脚本之间的一致性；不修改 Acquisition Plan 内容，不授权或执行数据采集。

## 核验结果

- 计划针对 Round 3 剩余不确定性提出了可区分、可回归的状态设计。
- 计划、E01–E13 事件、S0–S5 状态、330 秒脚本和五会话执行要求一致。
- 合格、无效和停止条件明确。
- UI 设置 Evidence、执行 Evidence 与物理结果 Evidence 的边界已明确。
- 输出被限制为实验相关 raw 字段假设，不支持提前赋予最终语义。

## Gate 裁决

`ACQUISITION_PLAN_APPROVED / DATA_NOT_YET_COLLECTED`

批准范围仅为当前 Acquisition Plan。该状态不等于已经获得现场采集授权。
