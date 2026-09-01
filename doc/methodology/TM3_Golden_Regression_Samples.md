# TM3 Golden Regression Samples

**状态：** ACTIVE  
**登记日期：** 2026-09-01

## Golden样本

### TM3-009 中等负载加速

- 产物目录：`output/TM3-009/report_v1/`
- 保护窗口：27.4225～44.9230 s、102.0783～120.1169 s。
- 保护统计：请求/实际MAE 2.34/2.58 Nm；两轮已核实输入、请求/实际扭矩、电驱功率和Pack电流峰值。
- 保护结论：两组加速可作为动态基线；低速补踩制动为独立控制工况，缺少轮端摩擦制动力，不确认制动力分配策略。
- 保护边界：控制链、动力/物理响应和能源交叉验证独立表达。

### TM3-010 稳定匀速

- 产物目录：`output/TM3-010/`
- 保护窗口：20 km/h带56.2764～74.9953 s；40 km/h计划段145～175 s；40 km/h带最长连续段158.1487～161.4694 s。
- 保护统计：20 km/h连续18.72 s、均值20.60 km/h、SD 0.45 km/h、扭矩MAE 0.30 Nm、电驱平均1.70 kW、Pack平均2.25 kW；40 km/h相关冻结统计见最终报告和窗口CSV。
- 保护结论：20 km/h短时条件化基线有效；40 km/h稳态基线未建立；仅补采40 km/h，不重复20 km/h。
- 保护边界：20/40 km/h是驾驶员实验目标，不是电驱控制器内部车速目标。

## 共同保护内容

- 已验收诊断/基线结论、窗口、关键数值和Signal物理语义；
- 控制树定义关系、Signal提供证据的表达边界；
- 人读时间线固定列顺序和工程字段隔离；
- Draft、Review Override、Approved实验级审核机制；
- Renderer只消费Approved/effective结果和上游Report View Model；
- Signal级“本次用途”、人读数值精度和模板标点质量。

## 修改规则

除非原始数据或算法真实错误得到可复现证明，任何重构不得静默修改Golden结果。差异必须先标记`Regression Failure`，说明影响范围，并经人工审核后才能更新Golden样本。

当前回归入口：

```sh
PYTHONPYCACHEPREFIX=/tmp/tm3_pycache python3 src/render_tm3_regression.py
PYTHONPYCACHEPREFIX=/tmp/tm3_pycache python3 -m unittest discover -s tests -v
```
