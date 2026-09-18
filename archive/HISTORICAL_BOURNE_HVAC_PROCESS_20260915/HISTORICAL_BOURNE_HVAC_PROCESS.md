# 伯恩 HVAC 工作历史过程记录

## 一、记录范围与编写原则

本文整理本会话中能够追溯和确认的伯恩 HVAC 工作过程，起点为 Round 2 修正既有 HVAC 判断并形成后续采集方案，终点为 `Bourne每轮工作建议_20260914.md` 形成。

本文只记录当时实际出现的提交、审核意见、整改、裁决和状态变化：

- 不重新分析采集数据；
- 不重新评价伯恩的工作；
- 不以本会话之外的信息补齐过程；
- 不用后来的结果改写较早阶段的判断；
- 对后来被撤销、收窄或纠正的判断，保留原判断及其后续变化；
- Director-only 内部活动只记录其发生、职责边界和当时形成的结论，不将其转化为伯恩可见要求。

---

## 二、Round 2 后续采集方案：制定、现场约束修订与人工审核

### 1. Round 2 结果形成后续实验请求

**提交内容**

Round 2 重建了 HVAC 与交流慢充分段 ASC 的统一时间轴，并撤回 Round 1 对这两类数据作出的“没有严格二态候选”判断。Round 2 正式结果保留了两个需要通过新采集继续验证的方向：

- HVAC 候选需要跨独立 Session 重复，并继续区分 HVAC 总体状态、送风和制冷相关响应；
- 交流慢充候选需要跨独立 Session 重复，并保留未连接、已连接未启动、充电、停止但仍插枪、解锁和拔枪等状态层次。

**审核内容**

这一阶段没有形成独立的正式 `M Audit` 文件。后续方案是在伯恩任务会话中逐项提出、讨论和修改，并由用户进行人工审核。

**修改内容**

伯恩开始把 Round 2 的 Evidence Gap 转化为两项独立的现场方案和 VoiceRunner 脚本：交流慢充重复验证方案与 HVAC 重复验证方案。

**后续状态**

两项方案进入草拟和人工校对阶段，尚未开始采集。

### 2. 交流慢充重复验证方案及人工审核

**提交内容**

伯恩形成交流慢充单轮采集方案和脚本，计划每轮独立经历：

`未连接 → 插枪但不启动 → 提交启动 → 充电稳定 → 正常停止但保持插枪 → 解锁 → 拔枪`

方案最终确定为 3 次独立单轮采集，每轮分别开始、结束和保存。现场脚本包含 9 个时间节点，并安排 2 张照片。

**审核内容**

用户在会话中逐项校对执行方式和 VoiceRunner 适配性。可以确认的审核意见包括：

- 脚本不应写入额外手工打点要求；
- `00s` 需要明确同时启动 VoiceRunner 和 CAN 数据记录；
- `30s` 插枪后暂不扫码，保持“已连接未启动”状态至 `60s`；
- 需要在脚本旁另设执行次数说明，因为 VoiceRunner 脚本本身不适合承载重复次数；
- 慢充是 3 次独立单轮采集，不是 5 次。

**修改内容**

伯恩据此：

- 删除脚本中的打点文字；
- 补齐 CAN 记录启动动作；
- 明确插枪后保持未启动的时间段；
- 保留 9 个时间节点和 2 张照片规则；
- 新增 `L3-Charge-Slow-MinSingRound_执行次数说明.txt`，明确独立执行 3 次且每轮单独保存。

**后续状态**

用户随后对慢充与 HVAC 两套脚本统一回复“审核通过”。这里的身份是方案和现场脚本的人工审核通过，不是正式 `M Audit`，也不是分析结果 Audit。

### 3. HVAC 最低负担重复验证方案的初稿

**提交内容**

伯恩首先提出 HVAC 单轮采集草案，原设计为：

`全关 → 仅送风 → 送风 + A/C → 关闭 A/C 但保持送风 → 全关`

草案计划独立执行 5 次，每轮单独开始、结束和保存，并希望保持温度、风量、风向和循环模式一致。

**审核内容**

用户先指出，“独立完成 5 次”和“五轮使用相同设置”等执行说明不应直接写入 VoiceRunner 脚本，需要等待逐项确认后统一调整。

随后现场预演又发现一项实际约束：车辆开启 HVAC 后会直接进入制冷状态，现场无法确认能够方便、稳定地获得“仅送风、不制冷”的独立状态。用户要求重新判断“仅送风”是否不可替代，并要求在不改变主要目的、不增加现场负担的前提下重新设计，不能假设通过复杂操作制造该状态。

**修改内容**

伯恩重新判断后认为，“仅送风”不是当前主要实验目的不可替代的条件。删除该状态的代价是：本轮不再分离风机与制冷语义，只验证 HVAC `OFF → ON → OFF` 候选能否重复，并把候选保留为 HVAC 综合状态候选。

修订后的单轮流程为：

`开始采集 → HVAC 关闭稳态 → 开启 HVAC 并允许正常进入制冷 → 运行确认及拍照 → 关闭 HVAC → 关闭确认及拍照 → 结束采集`

### 4. HVAC 脚本定型与人工审核通过

**提交内容**

伯恩根据上述现场约束生成：

- `L3-HVAC-Cooling-MinSingRound_单人最低负担空调制冷单轮采集脚本.txt`；
- `L3-HVAC-Cooling-MinSingRound_执行次数说明.txt`。

脚本保留 7 个时间节点和 2 张照片；执行次数说明明确独立完成 5 次单轮采集，每次单独保存。

**审核内容**

用户确认脚本可以生成，并要求将重复次数放在脚本旁的独立说明文件中。伯恩完成文件和结构核验后，用户对慢充与 HVAC 采集脚本及执行次数说明统一回复：

“审核通过”。

**修改内容**

两项脚本及执行次数说明定型；Round 2 过程归档同时记录了 ASC 分段问题、时间轴重建、双对照筛选、第一轮结论修正以及后续现场方案决策。

**后续状态**

- 交流慢充：3 次独立单轮采集方案及脚本人工审核通过；
- HVAC：5 次独立 `OFF → ON → OFF` 单轮采集方案及脚本人工审核通过；
- 两者均属于采集方案/脚本的制定与人工审核，不追记为正式 `M Audit`；
- 用户当时表示将在完成现场采集并提供数据包后继续，当前会话在该任务中暂时停止。

---

## 三、Round 3：既有 HVAC 分析提交、返工与关闭

### 1. Round 3 正式分析提交进入审核

**提交内容**

伯恩提交了 Round 3 HVAC 分析及相关机器产物。会话中可确认的主要内容包括：

- 5 个 Session 的重复实验；
- 对既有候选 raw bit 的跨 Session 检查；
- 52 个稳定 raw bit；
- 其中 23 个 raw bit 通过两次转换检查；
- 5 个优先 raw bit 在 5 个 Session 中重复出现；
- 对事件附近变化、较晚变化、照片可见 UI 事实和时间关系的整理；
- `README.md`、`VALIDATION.md`、Session 质量、时间轴、候选明细和转换记录等提交物。

**审核内容：`M_Round3_Pure_Audit.md`**

当时审核确认了以下工作价值：

- 伯恩做了逐 Session 的 5/5 重复验证；
- 使用了实际 Event 窗口；
- 检查了全程两次转换；
- 对语义判断较为克制；
- 照片只用于 UI 可见事实边界。

同时提出以下问题：

1. “23 个强候选”容易被理解为 23 个独立 Signal；当时要求改为“23 个跨五个 Session 可重复的二值 raw bit”。
2. 分析仍需从单 bit 推进到完整字节或候选字段结构，识别同字节、同步变化或可能属于同一结构的 bit。
3. 两次转换只能加强重复性，不能直接证明语义。
4. 在约 ±1 秒对齐精度下，不能据此给出 0.2 秒级响应先后；只能区分“事件附近”和“数秒后”等粗粒度关系。
5. 需要显式保存并核对每个候选的 `before → after` 变化方向。
6. 5 个 Session 是同条件重复，不应表述为 5 个独立条件。
7. 当时使用的 `C+ / B` 等级没有定义，应定义或删除。

**修改内容**

伯恩随后完成了本轮返工：

- 修正“23 个候选”的命名和含义；
- 新增 `raw_field_groups.csv`，将 23 个 raw bit 整理为 16 个 byte-level hypothesis，其中 7 个为多成员组、9 个为单成员组；
- 增加方向核验，形成 115 条（23 × 5）方向记录，并报告全部匹配；
- 同时整理 260 条（52 × 5）候选转换记录；
- 收窄时间先后表述；
- 明确 5 个 Session 是相同采集条件下的重复；
- 删除未定义等级；
- 分开记录事实、解释、未知项和 Evidence Gap。

**后续状态**

Round 3 尚未关闭，进入 Re-Audit。

### 2. Round 3 Re-Audit

**提交内容**

伯恩提交上述整改后的 Round 3 文档和机器产物。

**审核内容：`M_Round3_ReAudit.md`**

复审认定大部分整改已经满足，但发现一项残留问题：

- `work/round_3/process_session.md` 中仍写有“只有在 blower/A/C 解耦和 physical execution evidence 之后……”一类具体未来验证路径。

当时的判断是，这段内容超出了本轮审核停止点，把具体后续验证方向写入了当前 Round 的过程材料。

**修改内容**

复审只要求删除或抽象这句话：

- 不新增采集；
- 不制定下一轮计划；
- 不改变已形成的机器结果；
- 只将具体未来路径改为当前 Evidence limitation、竞争解释或 Evidence Gap。

**后续状态**

状态保持 `REWORK_REQUIRED`，等待最终复审。

### 3. Round 3 最终返工 Evidence 与 Final Re-Audit

**提交内容：`B_Round3_Final_ReAudit_Evidence.md`**

伯恩报告已将具体未来验证路径替换为当前证据限制、竞争解释和 Evidence Gap，并检查 5 份相关文档，记录：

`POSITIVE_FUTURE_PATH_RESIDUE_COUNT=0`

同时明确等待最终审核，没有创建 Round 4 计划。

**审核内容：`M_Round3_Final_ReAudit.md`**

最终复审核验了：

- 指定语句已经移除；
- 没有残留新的具体未来路径；
- 文件指纹和状态一致；
- 没有借整改启动下一阶段。

**修改内容**

最终复审没有再要求分析返工。随后进行了独立的 Gate 状态落地：更新 Round 3 正式状态文件及相应指纹，并增加最终审核记录。

**后续状态**

Round 3 Gate 变为：

`ROUND_3_CLOSED`

Round 3 关闭后，才进入 Round 4 Acquisition Plan 的形成和审核。

---

## 四、Round 4 Acquisition Plan：形成、发现、审核与授权边界

### 1. Round 4 Acquisition Plan 形成

**提交内容**

伯恩基于 Round 3 已关闭的正式 Evidence 和未决问题形成 Round 4 Acquisition Plan。会话中可确认的计划要点包括：

- 起点为 Round 3 的 52 个稳定 raw bit、23 个重复且通过两次转换检查的 raw bit、16 个 byte-level group；
- 未决问题包括 bit、枚举或连续结构，HVAC 总开关、风量、A/C 的区分，source/copy/derived 关系，以及 UI、请求、许可、执行和物理制冷之间的证据层级；
- 设计 6 个稳态：
  - `S0`：OFF；
  - `S1`：ON、A/C OFF、fan 2；
  - `S2`：fan 6；
  - `S3`：A/C ON、fan 6；
  - `S4`：A/C OFF、fan 6，回到对照状态；
  - `S5`：OFF；
- 计划 5 个 Session；
- 每个 Session 使用 `E01–E13`，计划约 330 秒；
- 包含 UI 照片，并将温度或音频视为可选证据；
- 仍属于同条件重复，不把 5 个 Session 表述为 5 个独立条件；
- 以实际 Event 为时间锚，稳态窗口设置 5 秒保护区；
- 预注册 overall on/off、fan、A/C reversible、dynamic/non-reversible 等分类逻辑；
- 在 bit 判断前先检查完整字节和相邻结构；
- 时间只做粗粒度判断；
- 计划输出状态表、16 个 group 的轨迹、raw-field 分类、纯度、方向、粗时间关系、UI 与物理 Evidence 区分、竞争解释和 Evidence Gap。

### 2. 正式入口未发现计划

**审核内容**

最初从 `results/` 正式入口检查时，没有找到 Round 4 Acquisition Plan。因此当时没有跨目录寻找，而是给出：

`NOT_REVIEWED / PLAN_NOT_AVAILABLE`

**修改内容**

用户随后明确授权查看 `work/round_4` 中的计划及关联脚本。

**后续状态**

审核材料范围得到明确后，才继续计划审核。

### 3. Acquisition Plan Audit

**提交内容**

审核对象包括 Round 4 Acquisition Plan、review 材料及两份关联脚本。

**审核内容：`M_Round4_Acquisition_Plan_Audit.md`**

审核检查了计划与脚本之间的状态、Event、时长、证据和停止点一致性，并接受计划。

**修改内容**

计划本身未因本次审核继续扩展。后续仅进行了状态和文件指纹的 Gate 落地。

**后续状态**

计划状态为：

`ACQUISITION_PLAN_APPROVED / DATA_NOT_YET_COLLECTED`

当时明确：计划审核通过不等于已经授权执行采集。用户随后单独批准 Gate 落地；仍未自动开始采集。

---

## 五、Round 4 数据采集与分析提交

### 1. 采集材料出现

**提交内容**

用户后来提供了 5 个 Round 4 HVAC 采集目录，目录名称对应 `L3-HVAC-ModeFanAC-FieldDisambiguation...` 实验。会话同时记录了一个现场意外：

- 其中一轮因屏幕滑动发生补拍；
- 该轮共出现 7 张照片；
- 后来补充了 1 张照片。

**审核内容**

最初只要求伯恩检查材料，不立即分析；随后伯恩完成 Round 4 分析并提交正式结果。

**修改内容**

这一阶段没有由 M 代替伯恩修改分析。伯恩独立形成 Round 4 数据、方法、Evidence 和结论产物。

**后续状态**

Round 4 从采集材料检查进入分析提交和预审阶段。

### 2. 初始分析问题与 field-level 问题暂缓

**提交内容**

伯恩报告 Round 4 HVAC 分析已完成。

**审核内容**

最初的审核任务限定为：

- 从 `results/` 正式入口开始；
- 只评价伯恩自己的数据、方法、Evidence 和结论；
- 先确认 Round 4 提交物和状态；
- 不修改文件。

会话随后提出了一个问题：多状态实验是否真正推进到 field-level hypothesis，还是仍停留在 raw-bit stimulus classification。

**修改内容**

在伯恩对初步意见作出修正后，用户明确要求暂不审计 field-level 问题。因此后续预审先处理提交合规、Evidence、方法定型、状态和边界，不提前裁决该问题。

**后续状态**

field-level 问题被暂缓到正式 Audit，不作为当时预审整改文本的题面。

---

## 六、Round 4 预审机制与整改文本边界的形成

### 1. 第一版预审整改稿及多次边界纠正

**提交内容**

M 起草了针对 Round 4 的预审整改意见。

**审核内容**

用户连续指出预审文本本身的边界问题：

1. M 不能查看伯恩的分析程序和分析过程；只能审核伯恩正式输出物。
2. 文本需要明确哪些属于伯恩应提交的审计资料，哪些不属于。
3. 文本不能出现 M 的总部信息或向伯恩暴露其未知身份背景。
4. 不能出现内部审核规范中的原话，例如要求审核者若无法独立核验便到特定目录补充脱敏 Evidence 的内部规则。
5. 预审意见只能给出提交要求、Evidence 要求、状态要求和整改目标，不能反向泄露 M 的内部审核规则、观察视角、访问边界、检查路径或判卷机制。
6. 防止泄露审核机制不能削弱伯恩应承担的 Evidence provenance、方法定型、结果可追溯和自审责任。

**修改内容**

用户提供了一份净化后的《HVAC Round 4 预审整改意见》，并要求完整采用，不再改写。该版本限定正式提交物、各提交物责任、必须整改问题、当前范围及停止点，同时不暴露内部审核方法。

**后续状态**

形成了后续 Round 4 预审文件的内容基础。

### 2. 预审文件命名与固定 Gate

**提交内容**

双方讨论预审文件名。

**审核内容**

最终采用：

`results/round_4/PREAUDIT_01.md`

选择理由是 Round 信息已经由目录表达，`PREAUDIT_01` 能清楚表示第 1 次预审，后续自然递增为 `PREAUDIT_02.md`、`PREAUDIT_03.md` 等，并与伯恩提交物及最终 Audit Record 区分。

**修改内容**

用户进一步规定：以后伯恩审计必须先经过预审，并持续整改到预审通过，之后才能进入正式 Audit。

**后续状态**

Round 4 进入强制 Pre-Audit Gate。

---

## 七、Round 4 Pre-Audit 01 至 06 的完整演变

### 1. `PREAUDIT_01.md`

**提交内容**

初始正式包被要求至少包括：

- `README.md`
- `VALIDATION.md`
- `METHOD.md`
- `input_evidence_manifest.csv`
- `photo_evidence_index.csv`
- `session_quality.csv`
- `timeline_reconstruction.json`
- `round3_group_state_detail.csv`
- `round3_group_summary.csv`
- `round3_bit_disambiguation.csv`
- `round3_group_transitions.csv`
- `all_bus_repeatable_bit_hypotheses.csv`
- `SELF_REVIEW.md`
- `REWORK_RESPONSE.md`
- `archive_manifest.md`

正式包只包含定型结论、方法合同、Evidence 索引、机器产物、自审和整改记录，不纳入分析程序、工作过程、探索草稿、临时产物或下一阶段计划。

**审核内容**

`PREAUDIT_01` 的主要整改要求包括：

- 撤销伯恩自行写入、但未经正式复审确认的“审核通过”和 `CLOSED`；
- 当前状态统一为 `OPEN / REWORK_REQUIRED`；
- 删除自行生成的通过性审核记录；
- 补充输入 Evidence manifest 和照片 Evidence index；
- 将方法整理为确定性的 `METHOD.md`；
- 核对 Session、Event、照片、帧数、候选组、raw bit、分类和转换记录数量；
- 核对人读报告与机器产物的数字和术语；
- 确认结论不超过 Evidence 覆盖范围；
- 完成自审、整改响应、archive manifest 和文件指纹。

**修改内容**

伯恩根据 `PREAUDIT_01` 完成第一轮修改，补齐或修订正式提交结构、状态、方法和 Evidence 索引。

**后续状态**

进入严格复核，预审尚未通过。

### 2. `PREAUDIT_02.md`

**提交内容**

伯恩提交了预审 1 的整改版本。

**审核内容**

严格复核当时发现：

1. `S0/S5` 的照片索引只记录“面板未展开、底栏 20°C”，不足以直接证明 HVAC 已关闭，但 `README.md` 和 `VALIDATION.md` 将其写成“全关状态有可见证据”。
2. 65 个 Event 和窗口边界还没有逐事件的正式索引。
3. 方法合同缺少若干影响复现的确定性规则。

随后用户说明，`S0/S5` 问题与现场发生屏幕滑动、7 张照片及后来补拍有关，并明确同意放行这一项。因此该项没有继续作为阻断整改要求。

**修改内容**

`PREAUDIT_02.md` 主要要求：

- 增加逐事件正式索引；
- 明确时间基准和窗口边界；
- 补充可复现所需的确定性方法规则；
- 移除对分析程序的引用，保持只审核正式输出物。

**后续状态**

预审仍未通过，等待伯恩继续整改。

### 3. `PREAUDIT_02.md` 的边界修订

**提交内容**

`PREAUDIT_02.md` 已形成，但用户对该预审文件本身进行边界审查。

**审核内容**

用户指出第五节越界：

- 将内部已经决定暂缓的“更高层级候选建模”写入给伯恩的整改文本，会提前透露后续审核题目；
- “等待第 3 次预审”和“预审通过 0 轮”也不是伯恩完成本轮整改所必需的信息，会暴露后续审核安排和内部状态机。

**修改内容**

M 只修订上述位置，其余内容不借机扩改：

- 删除暂缓审计题目；
- 删除下一次预审编号安排；
- 删除内部预审通过计数；
- 只保留本次任务边界、证明责任、状态和停止点。

**后续状态**

修订后的 `PREAUDIT_02.md` 继续作为伯恩整改依据。

### 4. `PREAUDIT_03.md`

**提交内容**

伯恩对预审 2 要求完成修改。

**审核内容**

新一轮预审继续检查正式提交范围、方法合同、Event Evidence、状态和停止点，同时进一步清理不必要的内部流程信息。

**修改内容**

`PREAUDIT_03.md`：

- 去除残留的预审次数、下一文件安排和内部状态描述；
- 收窄 `METHOD.md` 与 `VALIDATION.md` 中超出正式复现责任的内容；
- 保持整改目标，不提供分析实现提示。

伯恩随后继续修改。

**后续状态**

预审未结束，进入下一轮复核。

### 5. `PREAUDIT_04.md`

**提交内容**

伯恩提交了再次修改后的正式包。

**审核内容**

复核发现 `REWORK_RESPONSE.md` 中仍残留“0 轮通过”一类内部预审计数。

**修改内容**

`PREAUDIT_04.md` 只要求去除这一残留，不扩展其他整改范围。

伯恩随后完成修改。

**后续状态**

内部预审状态机信息不再作为伯恩可见提交内容，继续进行结论合法性复核。

### 6. `PREAUDIT_05.md`：结论与 Evidence 支持范围

**提交内容**

伯恩提交了预审 4 后的版本。

**审核内容**

本轮从“报告结论是否超过 Evidence”这一维度发现 6 项问题：

1. 不同 bit 响应不同，不能直接证明它们“不属于单一 field”；只能说现有 grouping 受到挑战，需要重新评估。
2. “与 cooling chain 相关”超过照片和 UI Evidence；应收窄为与 A/C UI toggle 的观察关系。
3. 解析失败数量不能等同于“没有丢帧”。
4. 首末时间端点不能单独证明整个区间连续覆盖。
5. 毫秒级对齐估计不能被写成因果响应延迟。
6. “相同条件”只能指相同采集设计和 UI 操作序列，不能扩展为所有环境、车辆和物理条件完全相同。

**修改内容**

伯恩根据上述问题收窄表述：

- 将结构性结论改为竞争解释或重新评估需要；
- 将语义关系限制在直接观察到的 UI toggle；
- 分开解析有效性、帧连续性和时间覆盖；
- 保留粗粒度时间边界；
- 限定“同条件重复”的具体含义。

**后续状态**

这一层整改完成后，继续检查另一维度：伯恩报告中的概念、未知项和参照系是否合法来自其获准知识与任务材料。

### 7. 概念来源、未知项与角色观察位置审查

**提交内容**

伯恩的 `README.md` 和其他正式提交物中包含 `cooling_enable`、盲扫、盲态边界、DBC、盲猜等表达。

**审核内容与判断演变**

这一阶段的判断经历了多次核查和修正，按发生顺序如下：

1. 首先检查的不是结论对错，而是概念能否从伯恩获准材料和任务中自然产生，以及某个“未知项”是否暗含外部标准答案、真实命名、真实映射或 Ground Truth。
2. 对 `cooling_enable` 的核查确认：该词出现在伯恩获准的 L3/HVAC Knowledge Snapshot 中，因此其概念来源合法，不能仅凭该词认定越界。
3. 一度对“盲扫”和“盲态边界”提出越界疑虑。
4. 用户提醒，伯恩获准的 Knowledge Snapshot 可能本身含有相关表述，不能只依据 `mission.md` 推断其全部合法认知。
5. 重新核查后发现正式入口的根 `results/README.md` 已包含“结果是盲分析候选……”之类表述，因此相关概念已经被合法授予；此前针对“盲扫/盲态边界”的越界判断被撤销。
6. 对“新能源工程师”字样的核查显示：精确短语没有出现，但获准材料中有“从驾驶者转变成一个诊断工程师”这句话。
7. 用户确认该句也存在于电驱系统知识中，并已在 Notion 笔记删除；要求本地删除原话，本次不进行 Notion 同步。
8. M 先从伯恩快照移除该句，随后发现正式本地 `current/` 来源仍保留该句，于是也从正式本地来源删除，并用完整本地电驱文档同步伯恩 L3 快照；同步后文件哈希一致。本次没有访问或同步 Notion。
9. 用户进一步说明：伯恩材料中的 DBC 和“盲猜”等字样，是因为当天 M 的审计原话中出现了这些信息，伯恩随后复制了相关内容。
10. M 接受这一事实，并撤销将这些用词作为伯恩主动越界 Evidence 的判断：由审核方文本造成的信息污染，不能反过来归责于伯恩。

**修改内容**

- 伯恩按预审意见继续修订正式提交物；
- 本地获准电驱知识中删除了“从驾驶者转变成一个诊断工程师”的原话；
- 本地电驱 Markdown 同步给伯恩的 L3 快照；
- 对 `cooling_enable`、盲扫/盲态边界、DBC/盲猜的越界定性按核查结果撤销或不再作为阻断项。

**后续状态**

上述概念来源和信息污染问题处理后，预审进入最终裁决。

### 8. `PREAUDIT_06.md`：预审通过

**提交内容**

伯恩完成此前预审整改，正式包进入最终预审检查。

**审核内容**

最终预审核对了提交完整性、状态、Evidence provenance、方法合同、数字闭合、结论边界以及前述概念来源问题的处理结果。

**修改内容**

没有再提出新的预审整改。`PREAUDIT_06.md` 作为预审通过记录，要求冻结提交并等待正式 Audit。

**后续状态**

状态变为：

`PREAUDIT_PASSED`

用户确认本次预审通过。Round 4 随后才能进入 Formal Audit。

---

## 八、Round 4 Formal Audit、返工与正式关闭

### 1. `AUDIT_01.md`

**提交内容**

Round 4 正式提交包在预审通过后进入 Formal Audit。M 只审核伯恩的正式提交物，不修改伯恩文件，也不进入下一阶段。

**审核内容**

`AUDIT_01.md` 首先确认了核心数量、索引和文件指纹闭合，包括：

- 5 个 Session；
- 65 个 Event；
- 31 张照片；
- 3,711,471 帧；
- 80 条 group-state detail；
- 16 个 group；
- 23 个 raw bit；
- 400 条 transition；
- 93 条 all-bus observation。

随后发现 4 项正式问题：

1. 多状态实验仍主要停留在 raw-bit stimulus classification，尚未形成可审核的 field-level hypothesis set。
2. Group 使用单一分类标签，不能表达 `G02`、`G07` 这样的 composite group；相应的 `classification_accepted=True` 以及 5/5/5 计数具有误导性。
3. 照片 collection digest 无法按声明的 `filename  file_sha256\n` 规则独立重算。
4. 状态不一致：`SELF_REVIEW.md` 仍写 `REVISED / PENDING_RE-AUDIT`，部分正式文件已经写成 `PREAUDIT_PASSED`，根 `results/README.md` 也已过时。

**修改要求**

正式 Audit 要求伯恩独立完成：

- 增加 field-level hypothesis 的正式表达；
- 对 group 类型作互斥且不误导的处理；
- 修正照片 collection digest provenance；
- 统一正式状态和根入口；
- 重新生成相关指纹。

用户特别规定：M 只能把 `AUDIT_01` 当前整改要求发给伯恩，不得补充实现方法、算法提示、字段划分方法或预期答案；field-level hypothesis 如何由现有 Evidence 形成，由伯恩自行解决。

**后续状态**

正式裁决为：

`OPEN / REWORK_REQUIRED`

不进入下一阶段，不新增采集计划。

### 2. 伯恩对 `AUDIT_01` 的独立返工

**提交内容**

伯恩完成正式返工，主要变化为：

- 新增 `field_level_hypotheses.csv`；
- 对 16 个 group 形成 18 个 candidate partition；
- `G02`、`G07` 被拆分表达；
- `G03` 暂停接受；
- 其他 group 保留相应竞争解释；
- group 汇总变为 13 个 single-response accepted，其中 HVAC 5 个、fan 4 个、A/C 4 个，另有 2 个 composite、1 个 constant；
- 增加照片哈希验证机制 `PHC1`；
- 状态同步为 `OPEN / REWORK_REQUIRED`；
- 更新根入口和 manifest。

**审核内容**

M 准备对上述返工执行独立 Re-Audit，没有把伯恩的自述直接视为通过。

**修改内容**

此阶段记录的是伯恩的返工结果，本身尚未形成新的通过裁决。

**后续状态**

进入 `AUDIT_02.md`。

### 3. `AUDIT_02.md`

**提交内容**

伯恩提交 `AUDIT_01` 整改后的正式包。

**审核内容**

复审确认以下项目通过：

- field-level hypothesis 已形成正式机器产物；
- group type 和分类表达得到修正；
- 数量关系闭合；
- 状态同步；
- 正式文件指纹一致。

但独立核验发现照片哈希仍存在实质问题：

- `photo_collection_hash_verification.csv` 中的校验表复制了原登记值并标为 `match=True`；
- 按正式 `photo_evidence_index.csv` 和当时声明的 `PHC1` 规则独立计算时，5 个 Session 全部不匹配。

**修改要求**

只要求修复照片 collection digest provenance 和独立复算闭环，不重开已经通过的其他分析整改，也不提供具体 field 形成方法。

**后续状态**

裁决继续为：

`OPEN / REWORK_REQUIRED`

### 4. 伯恩对 `AUDIT_02` 的返工

**提交内容**

伯恩废止 `PHC1`，改为 `PHC2`：

- 按 ASCII 顺序排序 `photo_id`；
- 将每张照片的 SHA-256 十六进制值解码为 32 字节；
- 串接这些字节；
- 对串接结果再次计算 SHA-256。

伯恩据此更新 5 个 Session 的 collection digest 和验证表。

**审核内容**

M 独立复算确认 5 个 Session 的 `PHC2` 结果一致。会话中记录的结果为：

- `S0019`：192 bytes，`57e9...1e29`；
- `S0020`：`737f...d3cd`；
- `S0021`：`71ed...1882`；
- `S0022`：`2fd8...4733`；
- `S0023`：224 bytes，`0c46...ab2f`。

**修改内容**

照片 Evidence collection provenance 得到可独立重算的定型规则和一致结果。

**后续状态**

进入最终 Formal Re-Audit。

### 5. `AUDIT_03.md` 与 Gate 状态落地

**提交内容**

伯恩提交 `PHC2` 修复后的 Round 4 正式包。

**审核内容**

`AUDIT_03.md` 确认：

- `PHC2` 独立复算通过；
- `AUDIT_01` 和 `AUDIT_02` 的全部整改闭合；
- 17 个非自指纹文件的哈希通过；
- 正式 Evidence、状态和 manifest 一致。

当时的最终分析边界表述为：Round 4 已经形成 field-level hypothesis，但不等同于已经确认真实 field semantics。

**修改内容**

正式分析内容不再修改。随后只执行 Gate 状态落地：

- 将 7 处正式状态同步为 `CLOSED`；
- 更新相关文件指纹；
- 12 个机器 Evidence 产物保持不变；
- 既有 Audit 文件保持不变。

**后续状态**

Round 4 Formal Audit 最终裁决：

`CLOSED`

用户接受正式裁决。Round 4 不重开，不进入下一阶段。

---

## 九、Round 4 关闭后的 Director-only Internal Truth Review

### 1. 首次内部最终报告

**提交内容**

在 Round 4 Formal Audit 已经 `CLOSED` 后，用户新增并授权 M 执行 `M → Director Internal Truth Review`。

**审核内容**

该内部收尾与 Formal Audit 严格分离：

- 只有 Formal Audit `CLOSED` 后才允许使用内部 Truth、DBC、既有 Signal 结论和其他对伯恩隔离的信息；
- 报告只属于 M → Director；
- 不进入伯恩 `results/`、Knowledge Snapshot 或其他伯恩可见输入；
- 不回流为后续 Audit、整改、采集条件、计划题面或预期答案；
- 不追溯修改已经 `CLOSED` 的正式裁决；
- 不自动触发下一 Round。

本轮形成：

`doc/internal/bourne_truth_reviews/ROUND_04_INTERNAL_TRUTH_REVIEW.md`

当时报告使用的内部评价包括：

- raw bit：`HIT`；
- field boundary：`PARTIAL`；
- semantic role：`PARTIAL`；
- diagnostic usefulness：`HIT / PARTIAL`；
- False Positive control：`MISS / NEEDS TRAINING`。

这些结论只记录为当时 Director-only 内部报告内容，没有进入伯恩后续输入。

**修改内容**

同时在既有《伯恩档案》生命周期中固化：以后每个分析 Round 在 Formal Audit `CLOSED` 后，由 M 自动执行 Director-only Internal Truth Review。

**后续状态**

用户接受 Round 4 Formal Audit 和 Internal Truth Review，Round 4 保持 `CLOSED`。`ROUND_04_INTERNAL_TRUTH_REVIEW.md` 被确认为本轮唯一已经完成的内部最终报告，不重复生成。

### 2. 固定生命周期规则的重复核验

**提交内容**

用户随后两次要求核验这一职责是否已经真正写入《伯恩档案》，而不是只完成了 Round 4 单次实例。

**审核内容**

核验确认现有规范已经明确规定：

- `CLOSED` 是打开内部 Truth 的前置 Gate；
- Internal Truth Review 自动发生；
- 报告只进入 Director 通道；
- 不回流伯恩；
- 不改变已关闭裁决；
- 不直接启动下一 Round。

**修改内容**

因为规则已经完整存在，后续核验没有重复修改规范，也没有重复生成 Round 4 内部报告。

**后续状态**

内部收尾职责保持为固定生命周期步骤；Round 4 仍为 `CLOSED`。

---

## 十、跨 Round Evidence Diff / Hypothesis Evolution 规则

### 1. 规则提出与固化

**提交内容**

用户要求：从存在前序 Round 的分析开始，伯恩的正式提交必须说明相对于上一轮正式 Evidence，本轮新增 Evidence 使既有 Observation / Hypothesis 发生了什么变化。

需要覆盖的变化类型包括：

- 强化；
- 细化；
- 拆分；
- 削弱；
- 否定；
- 保持未决；
- 本轮新增。

**审核内容**

M 的 Formal Audit 相应增加跨轮 continuity Gate，审核：

- 变化是否真实存在；
- 能否由前后两轮正式 Evidence 独立复核；
- 结论演变是否有 Evidence 支撑。

用户同时限定：

- 只规定职责、输出目标和审核责任；
- 不向伯恩规定 Diff 的实现方法、算法、数据结构、字段重建方法或预期结果；
- Internal Truth Review 仍位于 `CLOSED` 后；
- Truth/DBC 对照、真实 field 结构、MISS、False Positive 和内部训练建议不得回流到跨轮 Diff、后续 Audit 或任务题面。

**修改内容**

M 将该规则最小补充到现有《伯恩档案》的伯恩提交职责和 M Audit Gate 中，没有建立新的制度层级。

**后续状态**

用户核验并接受该规则。之后再次检查时确认规则已经存在，因此没有重复修改，也没有启动下一 Round。

---

## 十一、CLOSED 后脱敏赛后反馈环节的流程核验

### 1. 对 Round 3 历史做法与现行规范的比较

**提交内容**

用户指出，Round 3 结束后曾出现过一种做法：M 基于正式 Audit 和已关闭 Evidence 向伯恩形成脱敏赛后审核反馈，随后由伯恩基于自身合法 Evidence 和该反馈，自主提出下一轮 Acquisition Plan。

用户要求核验：

- 《伯恩档案》是否已经把这一环节规定为正式生命周期；
- Round 4 在 `CLOSED` 后是否尚未执行；
- 如果制度已存在，则按现有规则执行；
- 如果制度缺失，只向 Director 报告缺口，不自行扩展流程。

**审核内容**

核验当时确认：

- 现有规范允许伯恩收到 M 的脱敏审核意见；
- 现有规范允许 Round `CLOSED` 后由伯恩提出下一轮计划；
- 现有规范也规定 M 审核 Acquisition Plan；
- 但没有明确规定一个固定的“`CLOSED` → 脱敏赛后反馈 → 伯恩自主提出计划”生命周期步骤，也没有规定对应的必需产物；
- Round 3 的历史流程可以看到伯恩基于已关闭 Evidence 和 Gap 形成 Round 4 计划，但不足以证明该环节已经被制度化；
- Round 4 当时尚未形成独立的 post-close 脱敏反馈产物。

同时重申：任何伯恩可见反馈只能来自 Formal Audit、Re-Audit 和伯恩自身合法 Evidence，不得使用或转写 `ROUND_04_INTERNAL_TRUTH_REVIEW.md` 的内容，也不能告诉伯恩下一轮应采什么、找什么 field 或使用什么算法。

**修改内容**

依照用户指令，M 只报告制度缺口，没有自行增加新的生命周期步骤，没有触发伯恩，也没有启动下一 Round。

**后续状态**

该事项停留在“已核验、待 Director 决定是否制度化”的状态。

---

## 十二、`Bourne每轮工作建议_20260914.md` 的形成

### 1. 是否需要向伯恩提供脱敏工作协议

**提交内容**

用户询问是否需要将工作协议脱敏后提供给伯恩，并引用：

`/Users/hwy/Downloads/bourne/results/round_3/Bourne每轮工作协议.md`

**审核内容**

检查时未找到该文件。随后形成的判断是：伯恩确实需要一份可见的、脱敏的长期工作建议，但不宜放入已经关闭的 Round 3 目录，也不能包含 M 的内部审核视角、Truth Review、判卷机制或内部状态机。

**修改内容**

用户随后明确授权只读：

`/Users/hwy/Downloads/bourne/doc/Bourne每轮工作建议.md`

并要求：

- 不修改原文件；
- 生成 `Bourne每轮工作建议_20260914.md`；
- 先交由用户核对。

**后续状态**

进入工作建议副本的编制阶段。

### 2. 原始工作建议内容

**提交内容**

原文件当时包含的主要职责为：

- 开始工作前读取问题和获准材料，确认上一 Round 已关闭，定义不确定性；
- 分析时保证 provenance 和 reproducibility，区分事实与解释，结论受 Evidence 限制，区分证据层级；
- 提交时给出数据、检查、结果、支持与反证、未决问题、Gap 和复现信息；
- 保持报告、Validation、机器表和 manifest 一致；
- Audit 只处理当前 Round，返工后更新哈希并等待复审；
- `CLOSED` 后才可自主提出 Acquisition Plan；
- Acquisition Plan 审核通过不等于已经授权采集。

原文件保持不变。会话中记录其 SHA-256 为：

`5256ba...508`

### 3. 新版本形成

**审核内容**

新版本的编制吸收了本会话已经明确且可向伯恩公开的职责，同时继续排除 M 的内部信息。新增或强化的内容包括：

- 获准输入及其 provenance 责任；
- Evidence 层级、事实与解释分离，以及不得用聚合统计遮蔽差异；
- 从存在前序 Round 开始，记录 Evidence Diff / Hypothesis Evolution；
- 正式提交完整性、状态一致性、自审和文件指纹责任；
- Formal Audit 前必须经过 Pre-Audit，并按整改持续到 Pre-Audit 通过；
- Formal Audit / Re-Audit 的返工和等待规则；
- `CLOSED` 后冻结本轮正式结果；
- 如果收到脱敏赛后反馈，只能用来理解哪些能力已有正式 Evidence 支持、哪些问题仍 unresolved、哪些 Evidence Gap 仍存在；该反馈不替伯恩选择答案，也不直接构成下一轮计划；
- `CLOSED` 后由伯恩自主提出下一轮 Acquisition Plan；计划通过后仍等待明确采集授权。

**修改内容**

创建：

`/Users/hwy/Downloads/bourne/doc/Bourne每轮工作建议_20260914.md`

没有修改原始 `Bourne每轮工作建议.md`。边界检查未发现 Truth、Director-only 内部评价等级、总部信息、内部判卷机制等不应进入伯恩可见建议的内容。

会话中记录新文件 SHA-256 为：

`5d69f6...d061`

**后续状态**

新版本已经形成，等待用户核对；当时没有将其发送给伯恩，没有启动下一 Round，也没有执行新的采集或分析。

---

## 十三、截至历史记录终点的状态汇总

- Round 3：Formal Audit 已完成，状态 `ROUND_3_CLOSED`。
- Round 2 后续交流慢充方案：3 次独立单轮采集方案及脚本已经人工审核通过；不是正式 `M Audit`。
- Round 2 后续 HVAC 方案：5 次独立 `OFF → ON → OFF` 单轮采集方案及脚本已经人工审核通过；不是正式 `M Audit`。
- Round 4 Acquisition Plan：曾获审核通过；该批准本身当时不等于采集授权。
- Round 4 采集与分析：已经完成。
- Round 4 Pre-Audit：经过 `PREAUDIT_01.md` 至 `PREAUDIT_06.md`，最终 `PREAUDIT_PASSED`。
- Round 4 Formal Audit：经过 `AUDIT_01.md`、`AUDIT_02.md` 和 `AUDIT_03.md`，最终 `CLOSED`。
- Round 4 Internal Truth Review：已在 Formal Audit `CLOSED` 后完成，报告为 `ROUND_04_INTERNAL_TRUTH_REVIEW.md`，仅供 Director。
- Internal Truth Review：已经固化为每个 Round 在 Formal Audit `CLOSED` 后自动执行的内部生命周期职责。
- Round-to-Round Evidence Diff / Hypothesis Evolution：已经固化到伯恩提交职责和 M 的 Formal Audit continuity Gate。
- CLOSED 后固定脱敏赛后反馈步骤：本会话核验时尚未被明确制度化；依指令只报告了缺口，没有自行增加流程。
- `Bourne每轮工作建议_20260914.md`：已经生成，原文件未修改，新文件等待用户核对，尚未发送给伯恩。
- 下一 Round：截至本记录终点没有启动。
