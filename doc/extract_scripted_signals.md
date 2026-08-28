# ASC + DBC 自动分析项目会话记录

## 1. 本次工作的目标与成果

本次工作从一份规范的开关门采集实验开始，建立了以下完整分析链路：

```text
标准采集脚本
→ ASC 原始 CAN 数据
→ DBC 自动解码
→ 关键动作时间匹配
→ Signal 变化筛选和排名
→ Message 全状态变化时间线
→ 人工解释和实车验证
→ 中文知识文档沉淀
```

本次使用的三个输入文件是：

```text
input/can_开门关门采集脚本.txt
input/can_20260823164405.asc
input/tesla_model3_ONYX.dbc
```

由此新增了自动分析程序：

```text
src/extract_scripted_signals.py
```

程序已经能够：

- 解析标准采集脚本中的绝对偏移时间和操作步骤。
- 加载 DBC 并解码 ASC 中能够匹配的 CAN Message。
- 自动寻找动作时间附近发生变化的 Signal。
- 根据重复动作命中数、时间接近程度、一致性和背景变化量进行排名。
- 输出 Markdown 分析报告和 CSV 明细。
- 自动选择排名第一的候选 Message，输出全 Signal 状态变化时间线。
- 使用排除正则过滤无关 Signal。
- 为 Message 追踪文件添加时间戳，避免覆盖历史结果。

第一次有效采集共处理：

```text
ASC 数据帧：225,776
DBC 成功解码：101,399
关键动作：4 个
```

## 2. 程序运行方式

在项目根目录运行：

```powershell
python src\extract_scripted_signals.py `
    input\can_开门关门采集脚本.txt `
    input\can_20260823164405.asc `
    input\tesla_model3_ONYX.dbc `
    --exclude-regex "mirrorTilt"
```

主要参数：

| 参数 | 作用 | 默认值 |
|---|---|---:|
| `--tolerance` | 动作点前后的 Signal 匹配容差，单位为秒 | `2` |
| `--top` | 输出的候选 Signal 数量 | `10` |
| `--output-dir` | 输出目录 | `output` |
| `--exclude-regex` | 排除 Message/Signal 名称的正则表达式 | 无 |

排除规则同时匹配：

- Message 名称
- Signal 名称
- `Message.Signal` 完整名称

例如：

```powershell
--exclude-regex "mirrorTilt|temperature|counter$"
```

## 3. 输出文件

程序生成三类结果：

```text
output/<ASC名称>_关键步骤信号报告.md
output/<ASC名称>_关键步骤信号明细.csv
output/asc_dbc_message_trace_<ASC名称>_<CAN ID>_<时间戳>.txt
```

其中：

- Markdown 报告用于阅读采集步骤、候选排名和动作对应变化。
- CSV 用于 Excel 分析、筛选和二次统计。
- Message 追踪文件用于观察一个 CAN Message 中所有有效 Signal 的完整变化顺序。

本次生成的 Message 追踪文件选择了排名第一的：

```text
CAN ID：0x102
Message：VCLEFT_doorStatus
```

使用 `mirrorTilt` 排除规则后，后视镜位置的细微波动不会进入初始状态和变化事件。

## 4. Message、Signal 和 8 字节载荷

本次分析确认了以下基本概念：

> 一条 CAN Message 使用有效载荷承载多个 Signal；不是一个 Signal 独占整条 8 字节载荷。

经典 CAN 的 8 字节载荷共有 64 bit：

```text
Byte 0  Byte 1  Byte 2  Byte 3  Byte 4  Byte 5  Byte 6  Byte 7
 8 bit   8 bit   8 bit   8 bit   8 bit   8 bit   8 bit   8 bit
```

DBC 指定每个 Signal 在这 64 bit 中的：

- 起始位
- 位长度
- 字节序
- 有无符号
- 比例因子
- 偏移量
- 物理范围
- 单位
- 枚举名称

基本解码过程：

```text
8 字节载荷
→ 根据 DBC 的起始位和位宽定位
→ 使用位移和掩码提取原始整数
→ 按字节序和符号解释
→ physical = raw × scale + offset
→ 使用 VAL_ 将数值转换为枚举名称
```

## 5. DBC 的 Message 定义

本次核心 Message 定义为：

```dbc
BO_ 258 VCLEFT_doorStatus: 8 VEH
```

含义：

| 字段 | 解释 |
|---|---|
| `258` | 十进制 CAN ID |
| `0x102` | 对应十六进制 CAN ID |
| `VCLEFT_doorStatus` | Message 名称 |
| `8` | 有效载荷长度为 8 字节 |
| `VEH` | DBC 声明的发送节点 |

DBC 还定义了：

```text
GenMsgCycleTime = 100 ms
```

因此 `0x102` 是约 10 Hz 的周期状态报文。即使车门没有动作，控制器也会持续广播当前状态。

## 6. DBC 的 Signal 定义

驾驶门锁扣状态：

```dbc
SG_ VCLEFT_frontLatchStatus : 0|4@1+ (1,0) [0|0] "" X
```

解释：

| 字段 | 含义 |
|---|---|
| `0` | 起始位是 bit 0 |
| `4` | 长度为 4 bit |
| `@1` | Intel/Little Endian |
| `+` | 无符号整数 |
| `(1,0)` | scale 为 1，offset 为 0 |
| `[0\|0]` | DBC 声明范围；本文件部分范围明显不完整 |
| `""` | 无单位 |
| `X` | 接收节点 |

计算公式：

```text
physical = raw × 1 + 0
```

所以物理数值等于提取出的原始整数。

## 7. DBC 的枚举定义

Signal 位定义和枚举定义在 DBC 中分开放置，通过 `Message ID + Signal名称` 关联。

```dbc
VAL_ 258 VCLEFT_frontLatchStatus
    0 "SNA"
    1 "OPENED"
    2 "CLOSED"
    3 "CLOSING"
    4 "OPENING"
    5 "AJAR"
    6 "TIMEOUT"
    7 "DEFAULT"
    8 "FAULT";
```

枚举含义：

| 原始值 | 名称 | 中文解释 |
|---:|---|---|
| 0 | `SNA` | 状态不可用 |
| 1 | `OPENED` | 已打开 |
| 2 | `CLOSED` | 已关闭 |
| 3 | `CLOSING` | 正在关闭 |
| 4 | `OPENING` | 正在打开 |
| 5 | `AJAR` | 未完全关闭 |
| 6 | `TIMEOUT` | 超时 |
| 7 | `DEFAULT` | 默认状态 |
| 8 | `FAULT` | 故障 |

## 8. 手工解码一次开门

第一次开门前后的两帧为：

```text
变化前：22 B3 48 84 8C 0C 21 08
变化后：21 33 49 84 8C 0C 21 08
```

`frontLatchStatus` 位于 Byte 0 的低 4 bit：

```text
0x22 & 0x0F = 2 = CLOSED
0x21 & 0x0F = 1 = OPENED
```

因此得到：

```text
VCLEFT_frontLatchStatus：CLOSED → OPENED
```

Byte 0 的高 4 bit 都是 `2`，表示左后门一直保持 `CLOSED`。

`frontLatchSwitch` 位于 Byte 1 的 bit 0：

```python
front_latch_switch = byte1 & 0x01
```

本次实车观察：

```text
关闭位置：1
门打开后：0
```

`frontIntSwitchPressed` 起始位为 31，即 Byte 3 的 bit 7：

```python
front_int_switch_pressed = (byte3 >> 7) & 0x01
```

```text
0x04 = 0000 0100 → 0
0x84 = 1000 0100 → 1
```

Byte 3 的低 7 bit 同时属于 `rearHandlePWM`：

```python
rear_handle_pwm = byte3 & 0x7F
```

这说明同一个字节可以同时承载多个不同 Signal。

## 9. 第一次开门的完整时序

第一次打开驾驶门并不是一个 bit 的瞬间变化，而是一组按顺序发生的事件：

| 时间 | Signal 变化 | 可能对应过程 |
|---:|---|---|
| 25.138300s | `frontHandlePWM 8 → 72` | 把手相关控制量升高 |
| 25.138300s | `frontIntSwitchPressed 0 → 1` | VCLEFT 检测到内部开门按钮 |
| 25.148400s | `frontLatchStatus CLOSED → OPENED` | 锁扣状态机进入打开状态 |
| 25.184300s | `frontRelActuatorSwitch 1 → 0` | 释放执行器反馈变化 |
| 25.328300s | `frontLatchSwitch 1 → 0` | 锁扣物理位置反馈确认释放 |
| 25.328300s | `frontIntSwitchPressed 1 → 0` | 内部开门开关恢复 |
| 25.758300s | `frontRelActuatorSwitch 0 → 1` | 执行器反馈恢复 |
| 25.788400s | `frontHandlePWM 73 → 72` | PWM 回落 |

第一次关闭驾驶门时：

```text
frontLatchStatus：OPENED → CLOSED
frontLatchSwitch：0 → 1
```

第二次关门中，两者相差约 4.1 ms，说明物理反馈和控制器状态更新不一定发生在同一帧。

## 10. VCLEFT 的含义

`VCLEFT` 可以理解为管理车辆左侧相关设备的实体电子控制器，而不只是一段软件。

它通常包含：

```text
微控制器
+ 输入采集电路
+ 功率驱动电路
+ CAN 接口
+ 嵌入式控制软件
```

它参与管理：

- 左前门和左后门锁扣
- 内外门把手及开关
- 锁扣释放执行器
- 左侧后视镜调节、折叠和加热
- 左侧车窗相关功能

开门过程可抽象为：

```text
驾驶员按下物理按钮
→ VCLEFT 输入电路检测电信号
→ VCLEFT 软件判断是否允许执行
→ VCLEFT 驱动锁扣释放执行器
→ 执行器和锁扣发生机械动作
→ 位置开关/传感器反馈变化
→ VCLEFT 通过 0x102 广播整个过程
```

通常不是执行器自己直接发送 CAN，而是 VCLEFT 采集执行器和传感器反馈后统一广播。

## 11. 状态报文与请求报文

CAN 本身没有程序变量意义上的“只读/可写”属性。控制器发送 Message，其他控制器监听。

`0x102 / VCLEFT_doorStatus` 主要属于状态反馈：

- `Status`：控制器综合状态
- `Switch`：物理开关反馈
- `Pressed/Pulled`：输入检测
- `PWM`：驱动或测量状态
- `State`：内部状态机结果

它不是“动作完成后只发一次”，而是持续周期广播；动作只会改变其中部分 bit。

真正的控制请求常出现以下命名：

```text
Request / Req
Command / Cmd
Control
Target
Enable
```

## 12. 当前 DBC 中确认的请求 Signal

### 12.1 车辆锁车/解锁请求

```text
CAN ID：0x273（十进制 627）
Message：UI_vehicleControl
Signal：UI_lockRequest
```

枚举：

| 值 | 名称 | 中文解释 |
|---:|---|---|
| 0 | `IDLE` | 无请求 |
| 1 | `LOCK` | 锁车请求 |
| 2 | `UNLOCK` | 解锁请求 |
| 3 | `REMOTE_UNLOCK` | 远程解锁 |
| 4 | `REMOTE_LOCK` | 远程锁车 |
| 7 | `SNA` | 状态不可用 |

### 12.2 锁车/解锁请求来源

```text
CAN ID：0x339（十进制 825）
Message：VCSEC_authentication
Signal：VCSEC_lockRequestType
```

它区分多种来源，包括：

- P 挡被动解锁
- 内部门把手解锁
- 驶离自动锁车
- BLE 靠近解锁
- UI 按钮锁车/解锁
- 远程锁车/解锁
- NFC 锁车/解锁
- 碰撞解锁

### 12.3 后视镜请求

`0x273 / UI_vehicleControl` 还包含：

```text
UI_mirrorFoldRequest
UI_mirrorHeatRequest
```

后视镜折叠请求枚举：

| 值 | 名称 | 中文解释 |
|---:|---|---|
| 0 | `IDLE` | 无请求 |
| 1 | `RETRACT` | 请求折叠 |
| 2 | `PRESENT` | 请求展开 |
| 3 | `SNA` | 状态不可用 |

这可以与 `0x102` 中的 `mirrorFoldState` 形成请求—执行—反馈链。

## 13. Tesla App 车窗通风请求

当前 ONYX DBC 定义：

```text
CAN ID：0x3B3（十进制 947）
Message：UI_vehicleControl2
Signal：UI_windowRequest
起始位：20
位宽：3 bit
声明范围：0–4
```

当前 ONYX DBC 缺少它的 `VAL_`，但项目中的 `dbc/Model3CAN.dbc` 给出了枚举：

| 值 | 名称 | 中文解释 |
|---:|---|---|
| 0 | `WINDOW_REQUEST_IDLE` | 无请求 |
| 1 | `WINDOW_REQUEST_GOTO_PERCENT` | 移动到指定百分比 |
| 2 | `WINDOW_REQUEST_GOTO_VENT` | 打开到通风间隙 |
| 3 | `WINDOW_REQUEST_GOTO_CLOSED` | 完全关闭 |
| 4 | `WINDOW_REQUEST_GOTO_OPEN` | 完全打开 |

另一份 DBC 还定义了更接近执行层的：

```text
CAN ID：0x119（十进制 281）
Message：VCSEC_windowRequests
```

其中包括：

- 左前、左后、右前、右后四个车窗选择位
- `VCSEC_windowRequestType`
- `VCSEC_windowRequestPercent`

请求类型：

| 值 | 名称 | 中文解释 |
|---:|---|---|
| 0 | `WINDOW_REQUEST_IDLE` | 无请求 |
| 1 | `WINDOW_REQUEST_GOTO_PERCENT` | 移动到指定百分比 |
| 2 | `WINDOW_REQUEST_GOTO_CRACKED` | 打开一条小缝 |
| 3 | `WINDOW_REQUEST_GOTO_CLOSED` | 完全关闭 |

可能的控制链为：

```text
App 点击“通风”
→ UI_windowRequest = GOTO_VENT
→ VCSEC 完成权限和安全条件判断
→ 选择四个车窗并生成 GOTO_CRACKED 请求
→ VCLEFT/VCRIGHT 驱动车窗电机
→ 位置和状态反馈
```

该完整链路目前是基于两份 DBC 的工程推断，需要下一次实车采集验证。

本次开关门 ASC 中：

```text
0x3B3 的 UI_windowRequest = 0（IDLE）
0x119 的相关请求位也为 0
```

符合本次没有操作车窗的实际情况。

需要注意当前 DBC 的质量问题：ONYX 将 `0x3B3` 长度写为 2 字节，但 Signal 起始位 20 已位于第 3 字节，实际 ASC 的 DLC 为 8。说明 DBC 可能不完整，或者与当前车型软件版本并不完全匹配。

## 14. 新增的车窗通风采集脚本

已经生成：

```text
input/can_车窗通风采集脚本.txt
```

实验总时长 105 秒，包含：

```text
车窗全关稳定
→ App 第一次通风
→ 通风稳定
→ App 第一次关闭
→ 全关稳定
→ App 第二次通风
→ 通风稳定
→ App 第二次关闭
→ 全关稳定
```

程序解析器已经确认能够识别 4 个动作：

```text
25s  打开车窗通风
45s  关闭全部车窗
65s  再次打开车窗通风
85s  再次关闭全部车窗
```

## 15. 门把手故障的通用诊断模型

门把手案例可以抽象为新能源汽车大量机电系统共同的结构：

```text
人的操作或外部条件
→ 机械输入部件
→ 传感器/开关
→ 信号线、供电、接地、接插件
→ 控制器输入电路
→ 控制器软件与状态机
→ 控制请求/功率驱动
→ 执行器
→ 机械执行机构
→ 位置、电流、速度等反馈
→ CAN 状态广播
```

正常数据与故障数据对比的核心是：

> 找到两个样本中最早出现分歧的位置。

| 观察结果 | 优先怀疑的功能层 |
|---|---|
| 有物理操作，但输入 Signal 不变 | 机械触发、传感器、输入线束 |
| 输入正常，但请求不成立 | 联锁条件、控制逻辑、安全策略 |
| 请求正常，但没有驱动 | 控制器输出、供电、功率驱动 |
| 驱动存在，但执行器不动作 | 执行器、功率线束、机械卡滞 |
| 执行器动作，但反馈不变 | 位置开关、编码器、反馈线路 |
| 实物已经恢复，但 Signal 不恢复 | 内部触发件、传感器、线路、控制器输入或状态机 |
| CAN 状态正常，但实物异常 | 纯机械故障、DBC 解释错误或遗漏变量 |

CAN 能够帮助定位“异常功能层”，但从功能层继续落到具体弹簧、微动开关、插头或导线，还需要：

- 机械结构图
- 电气原理图
- 接插件针脚定义
- 正常件和故障件对比
- 电压、电阻、电流测量
- 拆检验证

最有效的维修组合是：

```text
实物现象
+ CAN/诊断数据
+ 电气测量
+ 机械检查
```

## 16. 没有 DBC 的车型如何继续

未来扩展到其他国产新能源车型时，不应放弃原始通信采集，也不应要求必须先获得完整 DBC。

建议同时建立两类基线：

### 维修基线

使用商用诊断仪记录：

- DTC 和冻结帧
- 数据流
- 执行器测试
- ECU 信息和软件版本
- 厂家服务程序

### 通信基线

使用 CAN/CAN FD/DoIP 等采集：

- 原始报文
- 动作时序
- 请求与反馈
- 正常与故障差异
- 瞬时异常

诊断仪适合快速维修，但不能完全替代原始通信，因为它可能刷新慢、开放数据有限，并隐藏控制器之间的中间时序。

没有 DBC 时可以：

```text
规范采集
→ 找动作附近变化的 CAN ID
→ 找变化的 Byte 和 bit
→ 验证重复动作一致性
→ 使用临时名称记录未知字段
→ 与诊断仪数据同步对照
→ 建立局部自定义 DBC
```

例如：

```text
UNKNOWN_102_B0_LOW_NIBBLE
关闭时 = 2
打开时 = 1
```

再通过实车、诊断仪或后续资料将其命名。

建议为结论设置证据等级：

| 等级 | 含义 |
|---|---|
| A | 厂家资料或可靠 DBC 明确定义 |
| B | 诊断仪与原始报文同步验证 |
| C | 多次实车操作验证 |
| D | 统计相关，尚未完全确认 |
| E | 暂时推测 |

最终目标是准确定位故障，不是完整逆向整辆车协议。

## 17. 无 DBC 的盲测方法

下一次实验可以先完全不加载 DBC：

```text
标准脚本
→ 动作时间附近的 CAN ID 变化
→ 字节级差分
→ bit 级差分
→ 重复动作一致性
→ 暂定物理含义
```

第一阶段记录：

```text
哪个 ID
哪个字节
哪些 bit
何时变化
变化方向
是否重复
```

第二阶段再加载 DBC，对照：

```text
UNKNOWN 字段
→ 官方或社区 Signal 名称
→ 枚举和物理单位
```

这样可以评价：

- 无 DBC 时能否找到正确 CAN ID。
- 能否定位到正确字节和 bit。
- 能否区分请求、过程和稳定状态。
- DBC 为分析增加了哪些信息。
- 自己的物理含义推断是否正确。

### 下一次车窗通风采集的收敛策略

下一次车窗通风数据采集将刻意采用**无 DBC 辅助分析**。程序不能只按动作时间附近是否发生变化来排名，否则容易把车辆唤醒、电源轨、电压、计数器和校验和等伴随变化误认为车窗直接信号。

分析采用三级收敛：

```text
报文级粗筛
→ 候选 CAN ID 的字节/bit 级差分
→ 多次动作和负对照实验进行语义收敛
```

报文级粗筛应考虑：

- 操作窗口内是否发生变化；
- 多次相同操作是否重复变化；
- 通风与关闭时变化方向是否相反；
- 变化时间是否接近动作时间；
- 非操作区间是否稳定；
- 报文周期和 DLC 是否稳定；
- 是否具有计数器、校验和或持续高频变化特征。

候选 CAN ID 进入精细分析后，应执行：

- payload 的 XOR 差分；
- 单字节和单 bit 翻转统计；
- bit 变化率与熵统计；
- 相邻 bit 联动分析和候选字段宽度推断；
- 大小端、无符号数和有符号数假设测试；
- 请求、执行过程与稳定位置三类时序特征区分。

候选评分不只计算“动作命中次数”，而应综合：

```text
候选得分
= 重复一致性
+ 通风/关闭方向可逆性
+ 与动作时间的接近程度
+ 非操作区间稳定性
+ 动作专属性
- 背景变化频率
- 无关动作命中率
- 计数器/校验和特征
```

其中，**动作专属性**用于区分车窗直接信号与伴随状态。例如，一个字段虽然每次车窗通风时都变化，但如果车辆解锁、开门或单纯唤醒时也变化，就应降低其作为车窗信号的优先级。

需要尽可能设置负对照：

- 仅解锁或唤醒车辆，不操作车窗；
- 打开、关闭车门但不操作车窗；
- 只操作单个车窗；
- 全部车窗通风；
- 全部车窗关闭；
- 操作完成后保留足够长的稳定观察区间。

无 DBC 时，程序的阶段性输出不强求正式 Signal 名称，而应可靠记录：

```text
CAN ID
+ Byte/Bit 位置或候选字段
+ 变化方向
+ 动作时序
+ 重复一致性
+ 动作专属性
+ 暂定含义和证据等级
```

对于大体量 ASC，采用流式和分层处理，避免一次性对全部帧执行最细粒度分析：

```text
流式读取 ASC
→ 按 CAN ID 汇总周期、DLC 和变化率
→ 提取动作窗口及稳定对照窗口
→ 筛选候选 CAN ID
→ 仅对候选 ID 进行字节/bit 级分析
→ 输出未知字段候选及证据
```

本次开关门实验中的 `VCFRONT_railBState`、`EPBR_12VFilt` 和 `EPBL_12VFilt` 作为典型反例保留：它们与开关门高度同步，但更可能表示车辆唤醒和低压供电变化，说明**时间相关不等于直接因果**。

## 18. 项目的长期方向

该项目不需要一次性成为完整的整车协议百科。更适合坚持：

> 一个行为、一次采集、一条控制链、一个可验证结论。

优先积累：

- 四门开关、锁车和解锁
- 内外门把手
- 车窗升降、通风和关闭
- 后视镜折叠、展开、调节和加热
- 前备箱、后备箱和充电口
- 制动、驻车和挡位
- 灯光、雨刷和转向灯
- 充电开始、停止和高压上电

每次保留：

```text
标准操作脚本
+ 原始 ASC
+ DBC 版本
+ 车辆软硬件版本
+ 环境和前置条件
+ 自动分析结果
+ 人工确认结论
```

长期将形成三类资产：

```text
自动化分析工具
+ 标准车辆行为基线
+ 面向维修的通信知识库
```

## 19. 项目文档约定

Python 程序和文档采用同名规则：

```text
src/example.py
doc/example.md
```

新增程序时，需要：

1. 在 `doc` 中创建同名 Markdown 文档。
2. 在 `readme.md` 相应章节加入链接。
3. 记录输入、输出、参数、验证数据和已知限制。

实车确认过的 Model 3 Signal、枚举和中文解释持续写入：

```text
doc/model3_dbc.md
```

## 20. 本轮结论

第一次规范采集与分析已经形成闭环，可以结束并准备下一次实验。

本轮最重要的认识是：

```text
实物现象告诉我们发生了什么
报文告诉我们控制器认为发生了什么
电气测量告诉我们线路实际发生了什么
机械检查告诉我们部件为什么不能完成动作
```

报文是新能源车控制器之间的语言，也是维修人员理解车辆内部逻辑的重要入口。它不能独自替代机械结构和电气测量，但能够把海量、复杂的控制过程变成可观察、可比较和可验证的数据证据。
