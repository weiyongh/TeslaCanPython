# L3交流慢充Case

本目录保存交流慢充领域中已经审核的Case契约（Case Contract）和脚本参考（Script Reference）。它是Acquisition Plan（采集计划）工具的业务输入与回归样例目录，不属于工具实现目录，也不绑定具体Vehicle或Round。

## 当前有效业务文档

1. [FullCycle Case契约](L3-Charge-Slow-FullCycle_Case契约.md)：定义正常交流慢充完整生命周期的`L3 → Case → ER → OR`语义。
2. [FullCycle脚本Reference](L3-Charge-Slow-FullCycle_脚本Reference.md)：保存结合一组现场条件形成的预期脚本输出。
3. [CurrentControl Case契约](L3-Charge-Slow-CurrentControl_Case契约.md)：定义交流慢充电流控制实验的`L3 → Case → ER → OR`语义。
4. [CurrentControl脚本Reference](L3-Charge-Slow-CurrentControl_脚本Reference.md)：保存有效阶跃条件及对应预期脚本输出。

两份Case契约均已审核通过并采用相同五段结构；两份脚本Reference均已审核通过，但不是正式发布脚本。发生冲突时以Case契约为准，Reference不得反向定义Case、ER或OR。

## 关联文档

- [Acquisition Plan采集计划设计方案](../../tools/acquisition_plan/采集计划_设计方案.md)
- [采集身份与追溯约定](../../methodology/采集身份与追溯约定.md)
- [历史开发记录](development/)

`development/`只保存这些文档的形成过程，不再作为当前规范或Acquisition Plan生成输入。

## 当前语义边界

```text
L3 Knowledge
→ Case
→ Evidence Requirement
→ Observable Requirement
```

Acquisition Plan根据已审核Case契约和用户提供的自然语言现场条件承载Event及其映射，并生成当前所需的VoiceRunner Script。Candidate Signal Mapping和CAN侧可观测性评估属于Case契约冻结后的后续阶段，不参与Case、ER、OR或脚本实验设计。
