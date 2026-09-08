截图展示的是 TM3-015 的一次早期正式管线运行：
output/TM3-015/pipeline_v3/20260907T235633-dd8ac28b/
这一目录可以理解为一次独立的运行快照（Run Snapshot）。里面的 JSON 不是重复文件，而是把“全量数据观察 → 语义检索 → LLM推理 → 程序验证 → 证据映射”各阶段分别冻结，便于追溯和审核。
整体流向如下：
```
ASC + DBC + Analysis Charter
        ↓
observation_package.json
        ↓
semantic_search_intents.json
        ↓
semantic_retrieval_results.json
        ├── semantic_retrieval_audit.json
        ↓
semantic_reasoning_input.json
        ↓
LLM Semantic Reasoning
        ↓
semantic_reasoning_output.json
        ↓
semantic_reasoning_validation.json
        ↓
evidence_mapping_draft.json


runtime_audit.json
```
贯穿并记录整个运行过程
# 1. observation_package.json
中文名：冻结观察包（Frozen Observation Package）
这是整个运行中最大、最基础的机器产物，约13 MB。它是程序读取ASC、结合DBC完成正式发现（Formal Discovery）后形成的完整观察空间。
本次包含：
- 344个总线观察（Observation）
- 344条DBC覆盖记录
- 4,280个已知Signal摘要（Signal Summary）
- 56个残差观察（Residual Observation）
- 174个未知观察（Unknown Observation）
- 120个压缩候选（Candidate）
- 665条处理去向（Disposition）
- 2,166个原始ASC引用（Raw Reference）
主要作用：
- 保存ASC中所有已解析CAN总线键（bus-key）的观察；
- 区分已知区（Known）、残差区（Residual）和未知区（Unknown）；
- 保存帧数、DLC、时间范围、Payload变化、Bit变化和Signal统计；
- 保存DBC覆盖结果，但不让DBC决定哪些CAN ID可以进入观察空间；
- 为后续检索和语义推理提供唯一的底层冻结数据来源。
重要边界：
observation_package.json 是完整观察，不是LLM结论，也不是已批准证据（Approved Evidence）。

其中120个Candidate只是从完整观察中压缩出的重点候选，并不表示其余Observation被删除。
# 2. semantic_search_intents.json
中文名：语义检索意图（Semantic Search Intents）
它描述程序准备“寻找什么类型的观察”。
本次包含27个Intent。
Intent一般来自：
- L3语义先验（L3 Semantic Prior）
- 控制树（Control Tree）
- 证据需求（Evidence Requirement，ER）
- 实验上下文（Experiment Context）
例如，它可能要求寻找：
- Capability相关观察；
- Request相关观察；
- Actual相关观察；
- Permission或HV Path相关观察；
- Thermal、Protection或Stop相关观察。
主要作用：
把抽象的L3/ER问题转化为结构化的检索问题，但不能写入预期答案。

它不应该包含：
- 已知正确Signal；
- 历史正确时间点；
- expected answer；
- 针对TM3-015编写的答案脚本。
# 3. semantic_retrieval_results.json
中文名：语义检索结果（Semantic Retrieval Results）
这是把每个检索意图与实际Observation匹配后的结果。
本次结果：
- 27个Intent对应27组检索结果；
- 最终选择25个不重复的Observation。
它通常记录：
- 每个Intent检索到了哪些Observation；
- Observation属于Known、Residual还是Unknown；
- 匹配分数；
- 为什么匹配；
- 哪些Observation最终进入Reasoning Input；
- 某个Intent是否没有合适观察。
主要作用：
从13 MB的完整Observation Package中，为LLM选择一个较小但仍可追溯的语义相关子集。

重要边界：
- 25个Retrieved Observation不是完整CAN观察；
- 被检索到不等于语义角色已经成立；
- DBC名称只能是检索特征，不能直接证明Signal角色；
- 一个Observation可以被多个Intent检索，但这不自动证明它承担多个语义角色。
# 4. semantic_retrieval_audit.json
中文名：语义检索审计（Semantic Retrieval Audit）
它不保存主要业务结论，而是记录Retrieval过程是否按规则执行。
本次记录了：
- 检索算法版本；
- 检索输入哈希；
- 检索输出哈希；
- 最低分数：20；
- 每个Intent最多8条；
- 全局最多120条；
- Known最多6条；
- Residual最多1条；
- Unknown最多1条；
- 最终选择25个Observation。
主要作用：
- 证明检索输入和输出没有被静默修改；
- 记录阈值和数量限制；
- 说明某个Intent为何没有候选；
- 检查source-space quota有没有把低于阈值的观察强制送入推理；
- 支持重复运行时比较结果。
可以把它理解为：
semantic_retrieval_results.json回答“检索到了什么”，
semantic_retrieval_audit.json回答“检索过程是否合规”。

# 5. semantic_reasoning_input.json
中文名：冻结语义推理输入（Frozen Semantic Reasoning Input）
这是实际交给LLM做语义分析的结构化输入包。
它不是完整的13 MB Observation Package，而是经过Retrieval压缩后的推理材料。
本次包含：
- 25个Retrieved Observation；
- 7个相关Candidate；
- L3语义上下文；
- 实验上下文；
- 检索意图和检索结果；
- 一致性检查结果；
- 事件锚点；
- Validation状态；
- 允许执行的确定性补充查询；
- 所有可引用对象的Reference Manifest；
- 来源Observation Package的ID和Hash。
主要作用：
明确LLM允许看到什么、允许引用什么，以及不能从哪里补充事实。

重要边界：
- LLM不能直接读取ASC；
- LLM不能自己重新计算统计；
- LLM只能引用这个Package内存在的Observation、Candidate和其他冻结对象；
- 历史报告、Approved Evidence和expected answer不应进入该输入；
- Package ID和Hash用于保证输入冻结性。
# 6. semantic_reasoning_output.json
中文名：语义推理输出（Semantic Reasoning Output）
这是LLM基于冻结输入形成的结构化推理结果。
本次产生：
- 5个语义发现（Finding）
- 0次确定性补充查询（Follow-up）
Finding通常表达：
- 某个Observation可能对应什么语义角色；
- 支持程度；
- 引用了哪些事实；
- 对应哪个L3概念、控制树节点或ER；
- 是否存在替代解释；
- 缺少什么证据；
- 需要什么Signal Validation。
主要作用：
把程序产生的统计Observation解释为候选语义、控制关系、Evidence Gap和下一步验证建议。

重要边界：
- Finding是LLM判断，不是已批准事实；
- OBSERVED、DERIVED、INFERRED和UNSUPPORTED必须区分；
- Request不能由Capability或Actual替代；
- DBC Signal Name不能直接成为Confirmed Semantic Role；
- Finding必须引用冻结输入中的有效对象。
# 7. semantic_reasoning_validation.json
中文名：语义推理结果验证（Semantic Reasoning Validation）
这是程序对LLM输出进行的确定性合同检查。
本次结果：
valid = true
errors = []
unknown_reference_count = 0
主要检查：
- 输出结构是否符合语义推理契约（Semantic Reasoning Contract）；
- Package ID和Hash是否匹配；
- 引用的Observation和Candidate是否真实存在；
- 是否虚构输入中没有的数值；
- Finding ID是否有效；
- 调用次数是否超限；
- 是否违反角色、时间、因果或Approval边界。
主要作用：
防止LLM输出格式正确但引用了不存在的证据，或者越过已规定的推理边界。

重要边界：
valid=true只表示：
输出符合程序合同。

它不代表：
- LLM语义判断已经被人工认可；
- Signal语义已经确认；
- Evidence已经Approved；
- 分析结论一定正确。
# 8. evidence_mapping_draft.json
中文名：证据映射草案（Evidence Mapping Draft）
这是把LLM Finding进一步映射到Evidence Requirement的程序产物。
本次包含：
- 5条Evidence Binding；
- 2条HUMAN_REVIEW_REQUIRED；
- 3条HOLD_UNRESOLVED；
- approval_state = NOT_APPROVED。
每条Binding一般连接：
Evidence Requirement
↕
Finding
↕
Observation / Candidate
↕
建议的Evidence Role
↕
Validation状态
主要作用：
为人工审核准备“哪条Observation可能支撑哪个ER、承担什么Evidence角色”的待审记录。

重要边界：
- 文件名明确是draft；
- NOT_APPROVED表示尚未批准；
- 它不能直接进入Evidence Assessment；
- 它不能直接用于生成正式报告；
- 人工审核不能被程序自动绕过。
# 9. runtime_audit.json
中文名：运行审计记录（Runtime Audit）
这是整个Run的“工程流水账”和状态凭证。
本次记录：
- Run ID；
- Pipeline版本；
- ASC和DBC Hash；
- 解析帧数；
- Observation、Known、Residual、Unknown和Candidate数量；
- ASC parse count；
- Retrieval输入/输出Hash；
- Reasoning Input ID和Hash；
- L3、Control Tree、ER fingerprint；
- LLM调用次数；
- Follow-up次数；
- Finding数量；
- Evidence Binding数量；
- 各阶段运行时间；
- 最终停止状态。
本次关键状态：
asc_parse_count = 1
reasoning_call_count = 1
follow_up_count = 0
finding_count = 5
evidence_binding_draft_count = 5
exit_status = AWAITING_EVIDENCE_REVIEW
主要作用：
证明这次运行究竟做了什么、调用了几次、使用了哪些冻结输入，以及停在了哪里。

它也是判断能不能继续下一阶段的重要依据。
按用途分类
文件	中文作用	类型
observation_package.json	完整冻结观察空间	底层事实与统计
semantic_search_intents.json	定义要寻找的语义证据	检索输入
semantic_retrieval_results.json	保存检索匹配结果	检索输出
semantic_retrieval_audit.json	检查检索过程与限制	检索审计
semantic_reasoning_input.json	实际交给LLM的冻结材料	LLM输入
semantic_reasoning_output.json	LLM产生的结构化Finding	LLM输出
semantic_reasoning_validation.json	程序验证LLM输出是否合法	合同验证
evidence_mapping_draft.json	Finding到ER的待审映射	证据草案
runtime_audit.json	记录整个Run的过程和状态	全局审计


最重要的区分是：
Observation
≠ Candidate
≠ Retrieved Observation
≠ Finding
≠ Evidence Binding Draft
≠ Approved Evidence
也就是说：
- 被程序观察到，不等于知道它是什么；
- 被选为Candidate，不等于语义成立；
- 被Retrieval选中，不等于它就是所需证据；
- 被LLM写成Finding，不等于人工认可；
- 被映射到ER，不等于Approved；
- 只有通过验证和人工审核后，才可能成为已批准证据（Approved Evidence）。
截图中的这次运行最终停在等待证据审核（AWAITING_EVIDENCE_REVIEW），并没有进入已批准证据、证据评估或正式报告阶段。