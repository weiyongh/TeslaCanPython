# Acquisition Plan / 采集计划

Acquisition Plan是连接已审核L3 Case语义与现场执行输出的公共中间体。AI根据Case契约和用户提供的自然语言现场条件草拟Event与OR映射；确定性代码负责最小结构承载、校验和当前唯一的VoiceRunner文本渲染。

## 当前范围

- 面向不同L3系统的Case，不归属于慢充系统。
- 核心模型为`acquisition-plan-v1`。
- 当前唯一Renderer和输出目标是VoiceRunner Script。
- 当前使用FullCycle和CurrentControl两组慢充Case契约与脚本Reference作为首批验证输入。
- 尚未通过其他L3系统Case验证跨系统复用。
- 不包含Candidate Signal、DBC、ASC、Evidence Mapping或分析报告生成。
- 不建设Renderer插件机制、通用工作流、数据库或未来输出抽象。

## 长期生成原则

- 先保证L3验证充分，再以真实人员位置、移动、设备切换、取证和倒计时前就位时间安排Event。
- 多个现场方案都能满足Case时，选择对持续采集干扰更小、时间锚点更清楚、操作更稳定的方案。
- 跨来源Evidence需要联合判断时，在同一短时窗口连续取证；需要证明持续状态时，在后续窗口重复同类联合观察。
- 只强制采集当前Case必要且现场自然可得的信息，不为页面字段齐全增加操作负担。
- Script使用功能动作语言；未经本次现场条件明确提供且无必要的设备、软件或车型实现细节不得注入。
- 相邻但独立的人工动作保留各自Event和时间锚点，不以合并步骤换取表面简短。

## 文档

- [采集计划设计方案](采集计划_设计方案.md)：当前已审核设计基线。
- [2026-09采集计划共享实现任务书](development/2026-09_采集计划共享实现_任务书.md)：本轮开发过程、交互、审核、状态和结果的统一记录。

## 代码与测试位置

```text
src/tooling/acquisition_plan.py
tests/tooling/test_acquisition_plan.py
```

第一版保持单文件实现，不拆成`core.py / validator.py / renderer.py`目录包。

## 使用方式

先准备符合`acquisition-plan-v1`的Acquisition Plan JSON，其中`contract_ref`使用工作区相对路径。然后在项目根目录执行：

```sh
python3 src/tooling/acquisition_plan.py \
  --plan <acquisition-plan.json> \
  --output L3-<System>-<Module>-<AcquisitionBriefName>_<中文名>采集.txt
```

程序读取冻结Case契约，校验Case ID、字段、Event时间、OR引用和完整覆盖，再生成UTF-8、LF换行的VoiceRunner TXT。成功时输出Event数量；失败时返回包含字段路径和原因的错误。程序不生成Event语义，也不补造现场条件。

Script文件名采用英文Case语义前缀和中文业务后缀。中文名由Module中文名与Acquisition Brief Name中文名组成，例如`L3-Charge-Slow-FullCycle_慢充全过程采集.txt`。CLI会校验文件名以当前`case_id`和下划线开头，并以非空中文业务名及`采集.txt`结尾；中文名是否准确仍由AI生成和人工审核。Acquisition Plan JSON继续使用`_acquisition_plan.json`标识中间模型，不与现场Script混淆。

## 首批业务输入与Reference

- [FullCycle Case契约](../../L3采集Case/交流慢充/L3-Charge-Slow-FullCycle_Case契约.md)
- [FullCycle脚本Reference](../../L3采集Case/交流慢充/L3-Charge-Slow-FullCycle_脚本Reference.md)
- [CurrentControl Case契约](../../L3采集Case/交流慢充/L3-Charge-Slow-CurrentControl_Case契约.md)
- [CurrentControl脚本Reference](../../L3采集Case/交流慢充/L3-Charge-Slow-CurrentControl_脚本Reference.md)

## 当前状态

- 定位与设计：已审核通过。
- 文档目录：已按独立工具域建立。
- 实现与测试：第一版已完成并通过FullCycle Human Review。
