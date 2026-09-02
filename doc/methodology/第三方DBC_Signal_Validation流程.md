# 第三方DBC Signal Validation流程

**状态：** 项目当前有效  
**生效日期：** 2026-09-01  
**首个Golden Case：** TM3-015直流快充能源链DBC适配专项

## 1. 原则与触发条件

第三方DBC是Signal发现和验证的起点，不是车型真值表。成功解码不等于语义成立；语义成立不等于定量定义成立。能解释最多独立实车证据、且不制造新矛盾的定义，才能逐步升级为车型可信Signal。

任何关键Signal出现以下情况之一时，自动进入Signal Validation，不直接解释为车辆行为或进入故障诊断树：

- 数值明显违反物理常识；
- 与同一控制链其他Signal矛盾；
- 与实际车辆动作/状态不一致；
- Request / Available / Actual关系不合理；
- 同一物理量在不同来源DBC中定义冲突；
- DLC、MUX、start bit、length、factor、offset、signed/unsigned存在版本差异；
- Signal全程不变、SNA、越界或异常枚举轮转；
- 与独立测量、累计量或物理守恒不能闭合。

## 2. 强制验证顺序

### 2.1 区分车辆异常与测量/解释链异常

不得因为Signal异常就默认车辆异常。先核查报文是否存在、实测DLC是否覆盖字段、MUX页是否实际出现、原始bit是否稳定可读。完成测量链核查前，不进入车辆故障诊断树。

### 2.2 回到原始CAN bit

每个目标Signal至少记录：

`CAN ID / 实测DLC / raw frame / start bit / length / endian / signed / factor / offset / mux / DBC来源与版本`

比较项目全部可用DBC、JSON参考字典和实验级候选解析视图，明确冲突发生在报文覆盖、位段、数据类型、缩放、枚举还是控制语义层。不得只比较最终物理值。

### 2.3 查找独立或冗余字段

优先寻找同一Message或其他Message中的raw / smooth / filtered / redundant / target / actual等独立字段。不同位段、不同缩放得到相近物理量时，可显著提高定量可信度；同名字段不天然属于独立证据。

### 2.4 验证完整状态转换

验证`未激活 → 建立 → 稳定 → 退出`。枚举、SNA、零值、边沿和恢复状态均须与实际车辆状态对应。单一稳态数值看似合理不足以确认语义；只有边沿吻合但量级冲突时，只能确认时序。

### 2.5 验证控制关系

按当前实验控制树检查：

`条件/状态 → Request/Target → Actual/Feedback → 物理结果`

核对方向、顺序和量级。不要求每个内部节点均有Signal，但不得用缺失Signal反向删除控制节点，也不得将Available、Request和Actual互相替代。

### 2.6 物理一致性与守恒

尽可能使用独立关系，例如：

- `P = V × I`；
- 累计能量差分 / 时间 → 平均功率；
- 速度、轴速、扭矩和功率关系；
- 温度变化率与热管理请求/执行状态；
- 同一路径输入、输出及合理损耗方向。

明显违反能量守恒、运动学或基本物理关系的DBC定义必须降级。

### 2.7 累计量积分校验

瞬时Signal存在累计电量、里程或计数器时，应做相同实测窗口的积分/差分核验。累计量是重要独立证据，但其DBC语义、分辨率、回绕和更新周期也必须保留候选边界。

### 2.8 外部物理证据标定

优先使用桩屏、仪表、SMT、万用表、示波器、实际机械动作、视频时间点等与CAN不同来源的证据。外部证据用于校验，不得为了使DBC闭合而反向修改实测值。

### 2.9 禁止单次实验反推并写回factor

允许计算“若要闭合所需factor/offset”作为诊断线索，必须标记`INFERRED_FOR_DIAGNOSTIC_CLUE_ONLY`。没有独立字典来源、外部标定或第二次实车验证前，不得写回正式车型DBC。实验级候选DBC必须保留来源、推算理由和非权威标记。

### 2.10 输出成熟度判断

每个异常Signal至少给出以下车型语义状态之一：

- `CONFIRMED`
- `STRONGLY_SUPPORTED`
- `PARTIALLY_VALIDATED`
- `TIMING_ONLY_VALID`
- `QUANTITATIVE_SEMANTICS_UNVALIDATED`
- `SEMANTIC_VALIDATION_FAILED`
- `INSUFFICIENT_EVIDENCE`

并分别记录：时序可信度、方向可信度、定量可信度、枚举可信度、当前适用车型/实验范围、仍缺少的独立证据。

## 3. P等级与成熟度独立

P0/P1/P2/P3回答“这个Signal对当前实验有多重要”；Signal成熟度回答“我们对Signal定义有多大把握”。两者必须作为独立字段保存，允许`P0 + QUANTITATIVE_SEMANTICS_UNVALIDATED`或`P2 + CONFIRMED`，不得因P0自动提高车型语义可信度。

Evidence Assessment状态也不替代Signal成熟度：Requirement可以由多个候选Signal共同`SUPPORTED`，其中单个Signal仍可能只是`TIMING_ONLY_VALID`。

## 4. 最小审计输出

Signal Validation至少保存：

1. 定义对照表：所有DBC/JSON来源、定义指纹和冲突层；
2. 原始帧或逐帧bit解码附件；
3. 状态转换和事件窗口；
4. 冗余字段、控制关系、物理守恒和累计量核验；
5. 外部证据及时间对应；
6. 成熟度、当前有效定义、失败定义、适用范围和最小下一步证据。

## 5. Golden Case：TM3-015能源链

专项报告：`output/TM3-015/energy_dbc_adaptation/TM3-015_能源链DBC适配专项结论.md`。

| Signal | 触发矛盾 | 验证路径 | 成熟度结论 |
| --- | --- | --- | --- |
| `0x132 / BMS_packCurrent` | 与CP电流量级冲突，DBC有15/16位及符号差异 | 平滑电流 ↔ 同帧独立未滤波电流 ↔ Pack V×I ↔ 累计充电量差分 ↔ SOC数量级旁证 | `STRONGLY_SUPPORTED`；TM3-015 Pack侧实验级可信定量Signal |
| `0x29D / CP_evseOutputDcCurrent` | 128.108 A对应46.8 kW，与Pack及累计量不闭合 | 原始bit、DLC、位宽、符号、factor候选、建立/稳定/归零时序及能量守恒 | `TIMING_ONLY_VALID`；定量语义未验证 |
| `BMS_chgPowerAvailable` | ONYX bit38得到35.9 kW，Available小于Actual | bit38/bit40定义比较、非充电raw 2047=SNA、爬升、稳定值及Actual小于Available关系 | `PARTIALLY_VALIDATED`；bit40实验级能力上限候选，非Request/Actual |

该Golden Case保护的是验证方法、原始窗口、关键数值、定义冲突和成熟度边界。未来工具重构不得静默把`0x29D`升级为定量Signal、把Available写成Actual，或撤销`0x132`多路闭合结论。
