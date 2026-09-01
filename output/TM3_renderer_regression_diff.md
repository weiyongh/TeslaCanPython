# TM3-009 / TM3-010 公共Renderer回归摘要

## 回归基准

- TM3-009：迁移前已验收报告及`report_v1/baseline_evidence`冻结数值。
- TM3-010：迁移前已确认窗口、统计与“20 km/h有效、40 km/h仅补采”结论。
- 回归方式：诊断语义和人读结构比较，不要求Markdown逐字符一致。

## 结果

| 项目 | TM3-009 | TM3-010 |
| --- | --- | --- |
| 实验结论 | 保持 | 保持 |
| 分析窗口 | 保持27.4225～44.9230、102.0783～120.1169 s | 保持56.2764～74.9953、145～175、158.1487～161.4694 s |
| 已审核关键数值 | 保持 | 保持 |
| 时间线第一列 | 由E编号改为ASC相对时间 | ASC相对时间 |
| 主表列顺序 | 统一为输入→请求→执行→运动→能源 | 同左 |
| Pack电流/功率 | 保留；Pack功率按同帧V×I展示 | 保留；统计表增加Pack平均电压、电流 |
| 工程字段 | E编号、采样时间、Signal age、DLC留在CSV/审计 | 同左 |
| 结论与下一步建议 | 明确无需整体重采 | 明确仅补采40 km/h，不重采20 km/h |

## 有意的呈现差异

- 两个实验现在由同一Renderer生成相同四份附件骨架。
- TM3-009原先按控制链/动力/能源拆分的多张人读事件表，合并为固定十列主时间线；完整事件未删除。
- DBC核心表由Approved Evidence Plan决定纳入与排序；复杂DBC问题移到异常说明或工程审计。
- 最终报告增加结构化Evidence Assessment和固定“结论与下一步建议”。

## Regression Failure与真实数据错误

- Regression Failure：未发现。
- 真实数据错误：未发现。
- 本轮未重新检测事件、窗口或重新计算冻结统计；因此没有用新程序结果覆盖历史结论。

## 封版前Golden Regression

- 控制关系改由上游`ControlRelationshipView`提供，Renderer未从Signal列表推导。
- 无直接Signal的仲裁/决策节点仍保留，并标记“本次无直接观测”。
- 控制链、动力/物理响应、能源交叉验证独立表达。
- TM3-010保留“实验目标车速不等于ECU内部车速目标”。
- TM3-010核心Signal均恢复Signal级具体用途。
- 人读Markdown已消除典型Python浮点尾数；Evidence Assessment无双重标点。
- 全部19项unittest通过。

**Golden Regression：PASS**
