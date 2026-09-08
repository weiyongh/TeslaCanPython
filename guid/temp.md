observation_package.json这个文件，你的json存储结构说明一下，生成这个文件主要用了哪些can报文分析方法。可以通过回顾py程序进行说明。







21:24






用时 1分钟 2秒



observation_package.json可以理解为：
Python 对整份ASC进行一次全量、静态、DBC非准入式扫描后形成的“冻结CAN观察数据库”（Frozen CAN Observation Package）。

它既保存全量CAN报文层观察，也保存DBC解码统计、未解释Bit、未知报文和重点候选，但不包含LLM语义结论。
实际调用链是：
TM3-015_formal_discovery_charter.json
        ↓
formal_pipeline.py
        ↓
can_discovery.py
        ↓
semantic_coverage_residual_discovery.py
        ↓
observation_package.py
        ↓
observation_package.json
相关实现：
- [formal_pipeline.py](/Users/hwy/codex_work/TeslaCanPython/src/formal_pipeline.py)
- [can_discovery.py](/Users/hwy/codex_work/TeslaCanPython/src/can_discovery.py)
- [semantic_coverage_residual_discovery.py](/Users/hwy/codex_work/TeslaCanPython/spikes/semantic_coverage_residual_discovery.py)
- [observation_package.py](/Users/hwy/codex_work/TeslaCanPython/src/observation_package.py)
- [TM3-015冻结观察包](/Users/hwy/codex_work/TeslaCanPython/output/TM3-015/pipeline_v3/20260907T235633-dd8ac28b/observation_package.json)
一、顶层JSON结构
可以把整个文件分为七组：
observation_package.json
│
├── 1. Package身份与来源
├── 2. ASC准入与完整性
├── 3. 全量原始CAN观察
├── 4. DBC覆盖与Signal统计
├── 5. Known / Residual / Unknown分区
├── 6. Candidate候选压缩
└── 7. 完整性、引用和Hash
1. Package身份与来源
主要字段：
{
  "package_version": "observation-package-v1",
  "experiment_id": "TM3-015",
  "package_id": "...",
  "package_hash": "...",
  "analysis_charter": {},
  "discovery_algorithm_version": "...",
  "limits_profile": {}
}
作用：
- package_version：观察包契约版本；
- experiment_id：对应哪个TM3实验；
- package_id：本次观察包的唯一身份；
- package_hash：整个Package内容的SHA-256指纹；
- analysis_charter：记录分析章程（Analysis Charter）路径和Hash；
- discovery_algorithm_version：记录使用的Discovery算法版本；
- limits_profile：记录统计和候选压缩上限。
TM3-015使用的限制包括：
{
  "unique_values_per_observation": 256,
  "raw_refs_per_observation": 8,
  "candidates_per_type": 25,
  "candidates_total": 120
}
这些限制主要控制文件体积，不得用于删除完整Observation。
2. asc_integrity
中文名：ASC完整性与数据准入（ASC Integrity and Admission）
实际内容包括：
{
  "asc_identity": "...TM3-015_直流快充采集.asc",
  "sha256": "...",
  "file_size": 31815365,
  "parsed_frame_count": 685617,
  "abnormal_line_count": 0,
  "first_timestamp": 0.0,
  "last_timestamp": 299.7339,
  "channels": ["1"],
  "frame_formats": ["STANDARD"],
  "admission_status": "ADMITTED"
}
作用：
- 确认读取的是哪份ASC；
- 保存文件SHA-256；
- 统计解析帧数；
- 统计异常或无法解析的候选行；
- 记录时间范围；
- 记录CAN通道；
- 区分标准帧（STANDARD）和扩展帧（EXTENDED）；
- 给出ASC是否通过准入。
这一步完全发生在语义分析之前。
二、全量CAN观察结构
3. bus_inventory
中文名：总线清单（Bus Inventory）
这是按CAN身份和DLC汇总的原始观察。
实际聚合主键是：
Channel
+ Frame Format
+ CAN ID
+ Observed DLC
例如：
Channel 1
+ STANDARD
+ 0x4F
+ DLC 8
对应的单条结构大致为：
{
  "bus_key": "ch1:0x4F",
  "channel": "1",
  "frame_format": "STANDARD",
  "can_id": "0x4F",
  "dlc": 8,
  "frame_count": 300,
  "first_time_s": 0.0219,
  "last_time_s": 298.901,
  "directions": {
    "RX": 300
  },
  "payload_cardinality": 4,
  "byte_cardinality": [],
  "changing_bits": [],
  "bit_ones": [],
  "bit_transitions": [],
  "raw_refs": []
}
字段含义：
- frame_count：该报文变体出现多少帧；
- first_time_s / last_time_s：第一次和最后一次出现时间；
- directions：RX/TX方向分布；
- payload_cardinality：观察到多少种不同Payload；
- byte_cardinality：每个Byte位置出现多少种不同值；
- changing_bits：哪些Bit在整个采集中发生过变化；
- bit_ones：每个Bit为1的帧数；
- bit_transitions：每个Bit发生0↔1切换的次数；
- raw_refs：代表性ASC原始帧引用。
这里不需要DBC，即使CAN ID在DBC中完全不存在，也会生成这类统计。
为什么338个bus-key却有344个Observation？
因为同一个CAN ID可能以不同DLC出现。
例如：
ch1:0x123 / DLC 6
ch1:0x123 / DLC 8
在字符串上都属于同一个bus_key，但在观察层会形成两个不同的总线变体（Bus Variant）。
4. observations
中文名：正式观察集合（Formal Observations）
observations以bus_inventory为基础，为每个CAN报文变体增加正式身份和DBC覆盖信息：
{
  "observation_id": "OBS-0001",
  "observation_kind": "BUS_VARIANT",
  "bus_key": "ch1:0x4F",
  "dlc": 8,
  "frame_count": 300,
  "payload_cardinality": 4,
  "changing_bits": [57, 58],
  "coverage_state": "MATCHED",
  "coverage_reasons": [],
  "definition_sources": [],
  "residual_changing_bits": []
}
与bus_inventory相比，它增加：
- observation_id：后续Retrieval和Reasoning引用的稳定ID；
- observation_kind：当前为BUS_VARIANT；
- coverage_state：DBC覆盖分类；
- definition_sources：哪些DBC定义参与解释；
- residual_changing_bits：报文发生变化、但没有被DBC Signal覆盖的Bit。
可以理解为：
bus_inventory
= 原始统计视图

observations
= 加入正式ID和DBC覆盖后的可引用视图
本次共344个Observation。
三、DBC参与形成的结构
5. coverage
中文名：DBC覆盖审计（DBC Coverage Audit）
程序首先对所有ASC报文完成原始统计，然后再把DBC定义连接进来。
因此逻辑是：
全部ASC Bus Variant
        ↓
DBC Coverage Join
        ↓
MATCHED / PARTIAL / INVALID / CONFLICTED / UNMATCHED
覆盖状态含义：
- MATCHED：DBC定义能够解码，DLC匹配，没有动态Residual Bit；
- PARTIAL：可以部分解码，但存在DLC差异、解码失败或未覆盖动态Bit；
- INVALID：有DBC定义，但在实际DLC上没有成功解码；
- CONFLICTED：多个DBC存在不兼容Message定义；
- UNMATCHED：没有任何DBC Message匹配该CAN报文。
TM3-015本次分布：
覆盖状态	数量
MATCHED	65
PARTIAL	97
INVALID	8
UNMATCHED	174


每条Coverage还记录：
{
  "definition_sources": [
    {
      "dbc_source": "...",
      "message_name": "...",
      "message_dlc": 8,
      "definition_fingerprint": "...",
      "attempted": 300,
      "succeeded": 300,
      "failed": 0,
      "covered_bits_observed": []
    }
  ]
}
这可以回答：
- DBC来自哪个文件；
- Message叫什么；
- DBC规定的DLC是多少；
- 尝试解码多少次；
- 成功/失败多少次；
- DBC Signal实际覆盖了哪些Bit；
- 哪些动态Bit仍然没有解释。
重要边界：
DBC是在全量ASC扫描之后参与解释，不是ASC Observation准入入口。

6. signal_summaries
中文名：DBC Signal统计摘要（DBC Signal Summaries）
当报文能够通过DBC解码后，程序使用SignalAccumulator为每个Signal累计统计。
Signal身份由以下内容组成：
DBC source
+ bus-key
+ Signal name
每条Signal Summary主要包括：
{
  "signal_key": "...",
  "signal_name": "APP_buildType",
  "message_name": "APP_info",
  "bus_key": "ch1:0x549",
  "dbc_source": "...",
  "definition_fingerprint": "...",
  "unit": "",
  "enum_definition": {},
  "mux_context": "APP_infoIndex=0",

  "sample_count": 30,
  "numeric_count": 0,
  "first_time_s": 0.6712,
  "last_time_s": 290.6881,

  "minimum": null,
  "maximum": null,
  "mean": null,
  "standard_deviation": null,

  "cardinality": 1,
  "dominant_value_ratio": 1.0,
  "change_count": 0,
  "first_change_time_s": null,
  "last_change_time_s": null,
  "current_value": "SIGNED",
  "sequence": ["SIGNED"],
  "stability_class": "LOW_CARDINALITY",

  "sna_count": 0,
  "out_of_dbc_range_count": 0,
  "dbc_minimum": null,
  "dbc_maximum": null,
  "raw_refs": []
}
本次共生成4,280个Signal Summary。
它执行的统计包括：
- 样本数量；
- 数值样本数量；
- 最小值和最大值；
- 平均值；
- 标准差；
- 不同值数量；
- 主导值比例；
- 变化次数；
- 第一次和最后一次变化时间；
- 去除连续重复后的状态序列；
- 当前/末尾值；
- 枚举定义；
- MUX上下文；
- SNA、INVALID、UNKNOWN等值计数；
- 超出DBC最小/最大范围的次数；
- 最小值、最大值、变化点对应的ASC原始引用。
稳定性分类（Stability Class）包括：
- CONSTANT：只有一个数值；
- LOW_CARDINALITY：不超过8个不同值；
- NEAR_CONSTANT：变化范围不超过平均量级的约0.1%；
- DYNAMIC：连续或明显变化；
- NON_NUMERIC：非数值型。
注意：
这里的stability_class只是数据行为分类，不是语义确认。

四、Known / Residual / Unknown分区
7. residual_summaries
中文名：残差观察（Residual Observations）
Residual表示：
这个CAN报文存在DBC定义
但某些实际发生变化的Bit没有被DBC Signal覆盖
判断方法是：
报文全部changing_bits
-
DBC定义覆盖的bit
=
residual_changing_bits
本次有56个Residual Observation。
它们的价值是发现：
- DBC定义不完整；
- DBC只覆盖了部分位段；
- DLC不匹配导致尾部数据没有解释；
- MUX或版本差异；
- 同一Message中存在尚未定义的动态字段。
Residual不能直接被解释成新Signal，只能作为进一步分析候选。
8. unknown_summaries
中文名：未知报文观察（Unknown Observations）
Unknown表示：
ASC中实际存在该CAN报文
但当前DBC没有匹配Message
本次有174个Unknown Observation。
即使没有DBC名称，程序仍保留：
- CAN ID；
- Channel；
- Standard/Extended；
- DLC；
- 帧数；
- 起止时间；
- Payload不同值数量；
- 每个Byte的不同值数量；
- 每个Bit为1的次数；
- 每个Bit变化次数；
- 原始帧引用。
这正是“不让DBC限制观察范围”的核心实现。
五、候选发现使用的分析方法
9. candidates
中文名：压缩候选（Compressed Candidates）
Python不会把4,280个Signal和344个Observation全部直接送给LLM，而是通过若干确定性规则产生Candidate。
当前实现包括以下方法。
1. 异常值和DBC范围检查
候选类型：
INVALID_OR_OUT_OF_RANGE
检查：
- Signal是否出现SNA；
- 是否出现INVALID、UNKNOWN、NOT_AVAILABLE；
- 解码值是否超出DBC定义的最小/最大范围。
用途：发现DBC适配错误、无效状态或Signal语义问题。
2. 固定边界值检测
候选类型：
FIXED_BOUNDARY_VALUE
FIXED_PHYSICAL_BOUNDARY_CONTEXT
检查数值Signal是否：
- 全程固定；
- 固定在0；
- 固定在DBC最小值；
- 固定在DBC最大值。
同时寻找同一Message内的低离散度Signal作为上下文。
用途：区分：
- 真实稳定状态；
- 占ร้อม值；
- SNA/未初始化；
- DBC缩放错误；
- MUX页不成立；
- 实际物理边界。
3. 低离散度周期变化检测
候选类型：
PERIODIC_LOW_CARDINALITY
PERIODIC_ALERT_LIKE
程序取得Signal变化时间，计算：
- 相邻变化间隔；
- 中位变化周期（median interval）；
- 间隔变异系数（interval CV）。
条件：
- 至少有足够变化点；
- Signal不同值数量不超过8；
- 周期间隔变异系数不超过约0.12。
如果Signal名称含：
watchdog
fault
error
warning
alarm
alert
invalid
failure
则额外标记为PERIODIC_ALERT_LIKE。
目的不是确认它是故障，而是发现：
名称看起来像告警，但行为可能更像分页计数器、心跳或周期轮询。

4. 同帧最小值—最大值关系检查
候选类型：
MIN_MAX_ORDER_VIOLATION
程序自动寻找名称上成对的Minimum/Maximum Signal，并在同一帧内检查：
Maximum >= Minimum
如果出现：
Maximum < Minimum
就产生高优先级候选。
例如冻结包中的：
BMS_brickNumVoltageMax
<
BMS_brickNumVoltageMin
本次150次同帧比较中发现66次违反顺序。
这不直接证明车辆异常，更可能提示：
- DBC位段错误；
- 缩放错误；
- MUX错误；
- 字段名称语义不可靠；
- 数据解释链冲突。
5. Signal族离群分析
候选类型：
SIGNAL_FAMILY_OUTLIER
程序识别名称末尾带编号的Signal族，例如：
xxx1
xxx2
xxx3
xxx4
然后使用：
- Signal均值；
- 族中位数（Median）；
- 中位绝对偏差（Median Absolute Deviation，MAD）
寻找明显偏离同族成员的Signal。
用途：发现某个通道可能是：
- 无效占位；
- 缩放异常；
- 传感器离群；
- DBC映射错误。
6. Signal族求和与总量比较
候选类型：
SIGNAL_FAMILY_SUM_VS_TOTAL
对于同单位的编号Signal族，程序计算成员均值之和，并寻找可能的Pack/Total Signal进行比较。
用途：寻找潜在结构关系，例如：
若干分量之和
≈
某个总量
但这里只是结构候选，需要后续语义审核，不能直接确认物理关系。
7. Residual Bit活动检测
候选类型：
RESIDUAL_BIT_ACTIVITY
对DBC没有覆盖但实际发生变化的Bit，记录：
- Residual Bit位置；
- 变化Bit数量；
- 报文帧数；
- 代表性原始帧。
用途：从DBC已知Message内部发现未解释动态区域。
8. Unknown低离散度Payload检测
候选类型：
UNKNOWN_LOW_CARDINALITY_PAYLOAD
如果一个DBC未匹配报文只有少量不同Payload，例如不超过8种，就作为潜在状态型报文候选。
它可能是：
- 开关状态；
- 状态枚举；
- 模式字段；
- 心跳；
- 固定背景报文。
但程序不会自行给出语义名称。
9. Unknown Bit周期性检测
候选类型：
UNKNOWN_PERIODIC_BIT
对Unknown报文中的每个Bit计算变化周期。
如果Bit近似固定周期切换，就生成候选，并标记：
COUNTER_HEARTBEAT_OR_PAGING_CANDIDATE
这意味着它可能是：
- Counter；
- Heartbeat；
- 分页选择；
- 周期状态；
- 其他规律Bit。
同样不直接确认语义。
六、候选压缩方法
所有Candidate生成后会经过：
去重
→ 每个Candidate Type最多25条
→ 按ranking_score排序
→ 各Candidate Type平衡选择
→ 全局最多120条
本次：
- 保留Candidate：120
- 因限制丢弃：1,129
- 完整Observation仍然保留：344
也就是说：
Candidate被压缩
≠
Observation被删除
candidate_compression会明确记录每种候选丢弃了多少，避免压缩过程不可见。
七、追溯与完整性字段
10. raw_reference_manifest
中文名：原始ASC引用清单（Raw ASC Reference Manifest）
每条引用包括：
{
  "raw_reference_id": "OBS-0001-R01",
  "observation_id": "OBS-0001",
  "asc_sha256": "...",
  "line_number": 54,
  "time_s": 0.0219,
  "bus_key": "ch1:0x4F",
  "dlc": 8,
  "raw_hex": "45 a3 5c 81 b4 63 67 12"
}
它让任何Observation都可以追溯到：
- 哪份ASC；
- 第几行；
- 什么时间；
- 哪个CAN ID；
- DLC是多少；
- 原始Payload是什么。
11. dispositions
中文名：处理去向（Disposition）
用于记录没有进入正常Signal Summary的内容及原因，例如：
MESSAGE_DECODE_FAILED_FOR_OBSERVED_DLC
SIGNAL_NOT_PRESENT_IN_OBSERVED_MUX_OR_TRUNCATED_DECODE
MALFORMED_OR_UNSUPPORTED_RECORD
它解决的是：
某个DBC Signal为什么没有统计结果？

而不是静默忽略解码失败。
12. collection_fingerprints
中文名：集合指纹（Collection Fingerprints）
分别为以下集合计算SHA-256：
- Bus Inventory；
- Observations；
- Coverage；
- Signal Summaries；
- Residual Summaries；
- Unknown Summaries；
- Candidates。
作用是检测后续文件是否被修改，以及不同Run之间哪些集合发生变化。
13. closure
中文名：观察闭包（Observation Closure）
TM3-015结果：
{
  "parsed_bus_key_count": 338,
  "observed_bus_key_count": 338,
  "disposed_bus_key_count": 0,
  "missing_bus_keys": [],
  "closed": true
}
它验证：
ASC中解析出来的每个bus-key，是否都进入了Observation，或者获得明确的Disposition。

closed=true表示没有CAN bus-key在处理中静默丢失。
八、当前分析的能力边界
这个Package执行的是静态全采集统计（Static Full-Capture Statistics）。
在can_discovery.py中，调用底层Kernel时传入的是：
conditions=[]
windows=[]
因此当前Package主要知道：
- 报文是否存在；
- 出现频率和时间范围；
- Payload/Byte/Bit怎样变化；
- DBC能否解码；
- Signal取值范围、均值和标准差；
- 状态变化次数和变化序列；
- 未知Bit和周期模式；
- 候选一致性问题。
但它没有可靠建立：
- 人工动作实际发生时间；
- 插枪、握手、请求、充电、停止等Observed Phase；
- 某个变化是否由具体动作触发；
- 多个Signal之间的同步关系；
- 请求—响应延迟；
- 跨Signal定量闭环；
- 因果因果因果
- 因果关系；
- Signal的最终L3语义角色。
所以它更准确的定位是：
完整、可追溯的CAN工程观察层，不是最终语义分析层。

后续的语义检索（Semantic Retrieval）和语义推理（Semantic Reasoning）只能在这个冻结观察层上解释数据，不能反过来改写其中的统计事实。