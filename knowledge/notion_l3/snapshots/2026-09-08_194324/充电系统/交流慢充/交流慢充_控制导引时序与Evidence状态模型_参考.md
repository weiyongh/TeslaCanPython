---
title: "交流慢充_控制导引时序与Evidence状态模型_参考"
source: notion
source_url: "https://app.notion.com/p/3d2a4e43864980c9a403d879134ccac0"
source_root: "新能源汽修L3学习"
source_path: "新能源汽修L3学习/充电系统/交流慢充/交流慢充_控制导引时序与Evidence状态模型_参考"
source_page_id: "3d2a4e43864980c9a403d879134ccac0"
source_last_edited_time: "2026-09-06T11:48:12.098Z"
snapshot_time: "2026-09-08T19:43:24+08:00"
authority: official
sync_mode: faithful_snapshot
---

# 交流慢充_控制导引时序与Evidence状态模型_参考

# 交流慢充控制导引——电气原理、控制时序与 Evidence 状态模型（参考）
> 用途：作为“交流慢充”主页面下的子页面，帮助理解国标交流充电接口中 CC / CP / S2 / K1-K2 的电气关系、状态变化、控制时序，以及后续车型基线采集时应关注的 Evidence。
	边界：本页以“插枪 → Vehicle Ready（CP 约 6V）”为主线。后续“桩侧 K1/K2 闭合 → AC 建立 → OBC 取电 → 高压直流建立 → 动力电池充电”建议另设页面展开。
---
## 1. 建模目标
本页不把“电路图、状态机、控制树、车型实现”混成一张图，而是分层回答四个问题：
1. **电气原理图**：CC / CP / S2 / K1-K2 在物理上如何连接？
2. **时序图**：谁先做什么、谁观察到什么、什么时候发生状态变化？
3. **控制树**：车辆进入 Charging Ready 前，需要满足哪些条件？
4. **Evidence 状态表**：每个阶段应该观察到哪些可验证证据？
建议结构：
```plain text
国标/培训电路原理图
        ↓
Mermaid 时序图（核心讲解图）
        ↓
ASCII 控制树（条件层）
        ↓
Evidence 状态表（采集层）
        ↓
具体车型实例化（Model 3 等）
```
---
## 2. 电气原理图及阅读边界
![](https://prod-files-secure.s3.us-west-2.amazonaws.com/306c62d4-2d40-4184-a385-d164211324d2/03fae51f-3119-43ce-94de-b54bec903c67/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466UTAUENCN%2F20260908%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20260908T114431Z&X-Amz-Expires=300&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEIn%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCIHh77vquEkouxiC3upPjkgg7tcyfzgBe%2F2vizJDviLbPAiEAuDwoYgVRNMZFUrClT%2BUIKfytRMh0S3lJhG%2FqrhFOp88q%2FwMIURAAGgw2Mzc0MjMxODM4MDUiDM%2F3P%2FrtWf4oYxbl1SrcAxSFS177gufz7hwg2TDKHUwTrP4w3uUqpx9kzy8QqcI8XXxn0SA0GIcdi8pRM%2FKKQPVKdFvsUvDnHFjMwT3dHKF4i9LzKlMrs%2BS2KqhAfwLz%2F5zbRYweKoHNj7Vwimow%2BbIFHuODYId0tQImF%2FWVFHYktq7pTVMONz3WZj2gZCOj3037bhemRpp9UDaaWxL3Ds85PhHGNq7vw11116vw0Gka6jhkkt5je2eIF%2FNg67PaKpakk%2BMK7BrfA773N5QAqbV%2BvKFe%2BcrSLWHHj%2B3F36INcxRg5Dl3pRSvpQcvi9yTTgo1oC5AuI12yPzfA%2BmF5pLDpSiqGnJqn%2FJk87Zh6sTzp80yJT45p4sdZw1PAWTboYsLcy595V0aUYF7g0%2FFcFCCtspGx2G2LngdrAqrWui2nccZi%2FD3fuxJTyu3ppwNOggUZEqrj5jLKmoWvfgpUo6TVYUa3E%2F47CuI4PwqVtEQ7ZAhYI2obL0yeLtQanENH3xO8awrbdDcgD4K%2FqAL3ytATlwAP8yMADfwgokF6nAPCWhk8cRs%2FLzY4aH6z3Y0tKke%2FMts%2FJKCSNUTmxLwPterR9cG5QIZpoevAN45ThYJGOdrQB%2BpadOU1NRLb0djlGeYB3C4PanvA40JMNyL%2F9QGOqUBP0SxF%2F%2FG5cF35QDz2rHW%2Bvy%2FtStReNkqZQT5H6AvpQQROuETaj%2FGvBX%2FrwlO7tXGcOjLr2Xo924WXF%2FLzNLr513viB468ndKKXVbamHTZ%2F%2FNYKvNfe%2FK76Cj3ml%2FHww3Zec8wiYKdTrJS%2FhmYO6XAKVB3ULU4rwdKh0a1GI59GskYB4Fbrl7K6jdiYSgf6le9XiAu2IfPqE5HuvBl9r%2FXITH%2BpvI&X-Amz-Signature=1910575a045d67190f44d353e14484b0806bdb53aeab964dbd87ab05d3a1405a&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)
- 本图用于说明国标交流充电 CC/CP 控制导引的基本电气关系，不代表具体车型内部ECU拓扑和实际控制时序。CC与CP为两条独立的硬线检测/控制导引链路：
- CC主要用于车辆识别充电连接装置的连接状态及额定载流能力；
- CP用于桩识别车辆连接/Ready状态以及通过PWM向车辆传递供电能力。
- 车辆侧R3（约2.74kΩ）属于CP基础控制导引电路，不能据此推导“CC确认后车辆才接入R3”；
- 车辆明确主动控制的是S2/R2支路，使CP由约9V进入约6V的Vehicle Ready状态。
- S3属于充电连接装置机械联动部分，并非车辆控制器主动控制开关。
- 具体车型的CC检测、CP检测、硬线唤醒、电子锁、ECU唤醒及S2状态转换之间的实际时序，应通过车型资料及基线采集验证。
国标简化图通常包含以下关键元素：
```plain text
桩侧：
  +12V / PWM → R1 → CP
  S1：桩侧控制导引状态切换
  K1 / K2：交流功率输出接触器

车辆侧：
  CP → D1 → R3（约 2.74kΩ）→ PE
                  │
                  └→ S2 + R2（约 1.3kΩ）→ PE

连接确认：
  CC → Rc / S3 → PE
```
其中：
- **CC**：车辆识别充电连接状态与线缆额定载流能力。
- **CP**：桩识别车辆连接 / Ready 状态，并通过 PWM 向车辆传递供电能力。
- **R3（约 2.74kΩ）**：车辆侧 CP 基础控制导引支路。
- **S2 + R2（约 1.3kΩ）**：车辆向桩声明 Ready 的主动状态切换支路。
- **K1/K2**：桩侧交流功率输出接触器；在 Vehicle Ready 之后才进入下一阶段的闭合控制。
> 注意：原理图表示的是**标准功能模型**，不是具体车型 ECU 拓扑，也不能据此直接推断“CC → 唤醒 → CP”的固定软件时序。
---
## 3. CC / CP / 硬线唤醒时序的特殊说明
**国标规定了 CC 与 CP 各自的电气功能和控制导引状态，但不能理解为车辆内部必须严格按照“CC确认 → 硬线唤醒 → CP接入”的固定软件执行顺序。**
CC 主要用于车辆侧确认充电连接状态及识别充电线缆额定载流能力；CP 用于控制导引，供电设备通过 CP 电平识别车辆 Connected / Ready 状态，并通过 PWM 向车辆传递供电能力。
车辆内部如何利用插枪事件、CC、CP、独立硬线或其他接口完成低压唤醒，以及 BMS、OBC、充电口控制器、电子锁等模块的实际唤醒和控制先后关系，属于**具体车型实现策略**。
因此，在车型基线采集中，不应预设：
```plain text
CC一定先于CP
CC一定直接触发硬线唤醒
CC确认完成后车辆才接入2.74kΩ
```
更合适的做法是分别记录：
```plain text
CC状态变化
CP 12V → 9V
PWM建立
硬线唤醒 / CAN网络唤醒
充电口锁止
BMS上线
OBC上线
CP 9V → 6V（Vehicle Ready）
```
并通过真实时间戳与信号变化建立该车型的控制关系。
> **原则：国标定义接口行为与状态；车型基线负责证明车内实际控制时序。相关性不能直接当作因果性。**
---
## 4. 核心 Mermaid 时序图（建议作为本页主图）
> 说明：此图用于“专家讲解式”描述，从插枪开始，一直讲到 Vehicle Ready。Mermaid 的 `autonumber` 可自动编号，`Note` 用于补充课堂式解释，`par` 用于表达 CC / CP 并行关系，`alt` 用于表达 Ready 条件分支。
```mermaid
sequenceDiagram
    autonumber

    participant EVSE as 充电桩/EVSE
    participant CON as 充电枪&接口
    participant CC as CC连接确认
    participant CP as CP控制导引
    participant VC as 车辆控制器
    participant SYS as BMS/OBC等

    Note over EVSE,SYS: ST0 未连接：桩侧CP约+12V，K1/K2断开，车辆未进入充电状态

    EVSE->>CP: 输出约 +12V
    Note right of EVSE: 此时仅建立控制导引电压<br/>交流功率接触器仍断开

    CON->>CON: 充电枪开始插入
    Note over CON: PE首先建立连接<br/>随后功率触点建立<br/>CC/CP最后建立

    CON->>CC: CC回路形成
    CON->>CP: CP物理连接形成

    par CC连接确认
        CC->>VC: Rc阻值可检测
        VC->>VC: 判断连接装置已连接
        VC->>VC: 识别线缆额定载流能力
        Note right of VC: CC回答：<br/>“枪是否连接？”<br/>“线缆能力是多少？”
    and CP Vehicle Connected
        CP->>EVSE: 车辆侧R3约2.74kΩ形成负载
        EVSE->>EVSE: 检测CP正向电平约9V
        Note left of EVSE: 状态A→B<br/>EVSE确认车辆已连接
    end

    Note over VC,SYS: 具体车型内部可在此阶段发生<br/>硬线唤醒、网络唤醒、充电口锁止及控制器初始化<br/>国标不规定其固定先后顺序

    EVSE->>CP: 切换为PWM控制导引信号
    CP->>VC: PWM传递至车辆
    VC->>VC: 检测PWM有效
    VC->>VC: 根据占空比计算桩允许最大电流

    VC->>SYS: 启动充电准备检查
    SYS-->>VC: BMS/OBC/高压/温度/绝缘等状态
    VC->>VC: 汇总车辆Charging Ready条件

    alt 车辆条件未满足
        VC->>VC: 保持S2断开
        Note over EVSE,VC: CP维持约9V PWM<br/>Vehicle Connected，但尚未Ready
    else 车辆条件全部满足
        VC->>CP: 控制S2闭合
        Note right of VC: R2约1.3kΩ加入CP回路
        CP->>EVSE: CP正向电平约9V→6V
        EVSE->>EVSE: 识别Vehicle Ready
        Note over EVSE,VC: 状态B→C<br/>车已向桩声明“准备好充电”
    end

    Note over EVSE,SYS: Charging Ready 边界到此结束<br/>下一阶段：EVSE检查供电条件→K1/K2闭合→AC建立→OBC取电
```
---
## 5. 控制树：插枪到 Charging Ready
> 控制树回答的是“要进入 Charging Ready，必须满足什么条件”，不强调严格先后顺序。
```plain text
交流慢充 Charging Ready
│
├─ ① 物理连接成立
│  ├─ 充电枪已插入
│  ├─ PE连接成立
│  ├─ L/N功率触点物理连接成立
│  └─ CC/CP触点连接成立
│
├─ ② CC连接确认成立
│  ├─ 车辆检测 CC-PE 电阻 Rc
│  ├─ 确认充电连接装置已连接
│  └─ 识别充电线缆额定载流能力
│
├─ ③ 车内充电唤醒成立（车型实现）
│  ├─ 插枪事件被车辆识别
│  ├─ 相关低压控制器被唤醒
│  ├─ BMS进入充电管理状态
│  ├─ OBC进入待命 / 初始化状态
│  └─ 车辆进入外部充电连接状态
│
├─ ④ CP Vehicle Connected成立
│  ├─ 桩侧初始CP约 +12V
│  ├─ 车辆侧CP基础回路形成
│  ├─ CP正向电平约 9V
│  └─ 桩识别 Vehicle Connected
│
├─ ⑤ CP PWM控制导引成立
│  ├─ 桩开始输出PWM
│  ├─ 车辆识别PWM有效
│  └─ 车辆读取桩允许最大电流
│
├─ ⑥ 车辆内部Ready条件成立
│  ├─ CC有效
│  ├─ CP PWM有效
│  ├─ 线缆能力满足
│  ├─ 充电口锁止成功（若车型要求）
│  ├─ BMS允许充电
│  ├─ OBC状态正常
│  ├─ 高压系统允许
│  ├─ 热状态 / 绝缘状态允许
│  └─ 无禁止充电故障
│
└─ ⑦ Vehicle Ready成立
   ├─ 车辆控制S2
   ├─ R2约1.3kΩ加入CP回路
   ├─ CP约9V → 6V
   └─ 桩识别 Vehicle Ready
```
---
## 6. 状态机
> 状态机只表达“当前系统状态”和“状态迁移条件”。若页面已经有完整 sequenceDiagram，可将此图作为辅助，而不是主图。
```mermaid
stateDiagram-v2
    direction TB

    [*] --> ST0

    state "ST0 未连接" as ST0
    ST0: CP约+12V
    ST0: K1/K2断开

    ST0 --> ST1: 插枪 / 连接器建立

    state "ST1 Vehicle Connected" as ST1
    ST1: CC有效
    ST1: CP约9V
    ST1: 桩确认车辆已连接

    ST1 --> ST2: PWM建立且车辆可识别

    state "ST2 Connected + PWM" as ST2
    ST2: CP为约9V PWM
    ST2: 车辆读取桩允许电流
    ST2: 车辆执行内部Ready检查

    ST2 --> ST2: Ready条件未满足
    ST2 --> ST3: Ready条件全部满足 / S2闭合

    state "ST3 Vehicle Ready" as ST3
    ST3: CP约6V PWM
    ST3: 桩识别车辆Ready

    ST3 --> [*]
```
---
## 7. Evidence 状态表
> 此表用于把标准层模型转换为后续车型基线采集任务。
<table header-row="true">
<tr>
<td>阶段</td>
<td>物理/控制动作</td>
<td>CC Evidence</td>
<td>CP Evidence</td>
<td>车辆内部 Evidence</td>
<td>桩侧状态</td>
</tr>
<tr>
<td>ST0 未连接</td>
<td>未插枪</td>
<td>未连接</td>
<td>约 +12V</td>
<td>Sleep / Idle</td>
<td>No Vehicle</td>
</tr>
<tr>
<td>ST1 插枪建立</td>
<td>枪插入</td>
<td>Rc可检测</td>
<td>CP回路建立</td>
<td>插枪事件、唤醒候选</td>
<td>Connected建立中</td>
</tr>
<tr>
<td>ST2 Vehicle Connected</td>
<td>连接成立</td>
<td>CC有效、线缆能力可识别</td>
<td>约 9V</td>
<td>车辆控制器已能参与充电逻辑</td>
<td>Vehicle Connected</td>
</tr>
<tr>
<td>ST3 PWM建立</td>
<td>桩输出PWM</td>
<td>CC保持有效</td>
<td>约9V PWM</td>
<td>PWM有效、桩允许电流可识别</td>
<td>Connected + PWM</td>
</tr>
<tr>
<td>ST4 车辆准备</td>
<td>内部Ready判断</td>
<td>CC保持有效</td>
<td>约9V PWM</td>
<td>BMS/OBC/锁止/绝缘/热状态等</td>
<td>Waiting Ready</td>
</tr>
<tr>
<td>ST5 Vehicle Ready</td>
<td>S2闭合</td>
<td>CC保持有效</td>
<td>约6V PWM</td>
<td>Vehicle Ready</td>
<td>Ready</td>
</tr>
</table>
---
## 8. 基线采集时应重点记录的事件
后续对具体车型（如 Tesla Model 3）进行交流慢充基线采集时，建议至少记录以下关键事件与时间戳：
```plain text
T0  开始插枪
T1  CC状态变化
T2  CP由12V进入9V
T3  车辆低压系统 / CAN网络唤醒
T4  充电口锁止动作开始
T5  充电口锁止成功
T6  BMS上线 / 进入充电准备
T7  OBC上线 / 进入待命
T8  PWM建立
T9  车辆识别PWM占空比 / 桩能力
T10 车辆内部Ready条件全部满足
T11 S2状态变化
T12 CP由9V进入6V
T13 桩识别 Vehicle Ready
```
### 采集原则
1. **不要预设先后关系**，尤其是 CC、CP、硬线唤醒之间。
2. **先采时间，再建因果。**
3. 区分：
	- 触发事件（Trigger）
	- 允许条件（Enable Condition）
	- 状态（State）
	- 控制输出（Control Action）
	- 可观察证据（Evidence）
4. 若两个信号先后出现，只能先记为“时序相关”，不能直接写成因果。
---
## 9. 标准层与车型层的边界
### 标准层可以确定
```plain text
CC：连接确认 + 线缆额定载流能力识别
CP：
  约12V → 未连接
  约9V  → Vehicle Connected
  PWM   → 桩供电能力传递
  约6V  → Vehicle Ready
S2：车辆向桩声明Ready的关键控制支路
K1/K2：桩侧交流功率输出接触器
```
### 车型层需要验证
```plain text
谁检测CC？
谁检测CP？
谁生成或控制“等效S2”？
插枪事件如何触发低压唤醒？
是否存在独立硬线唤醒？
哪个ECU最先上线？
电子锁何时动作？
电子锁是否是Ready前置条件？
BMS/OBC分别何时进入充电准备？
车辆内部Ready条件有哪些？
这些条件的实际阈值是多少？
```
---
## 10. 页面边界：Charging Ready 之后另开下一阶段
本页建议截止于：
```plain text
Vehicle Ready
   ↓
S2闭合
   ↓
CP约9V → 6V
   ↓
桩识别 Vehicle Ready
```
下一阶段建议单独建立页面：
```plain text
桩侧供电允许条件成立
        ↓
K1/K2闭合
        ↓
L/N真正带电
        ↓
OBC检测AC输入
        ↓
OBC开始整流 / PFC
        ↓
HV DC输出建立
        ↓
动力电池充电建立
```
可命名为：
> **交流慢充——Vehicle Ready 到 AC/HV 充电建立控制过程**
---
## 11. 本页推荐结论
这部分学习与后续诊断可以始终保持四层分离：
```plain text
电路图：回答“物理上怎么实现”
状态机：回答“系统现在是什么状态”
时序图：回答“谁在什么时候做了什么”
控制树：回答“为什么允许进入下一状态”
Evidence：回答“我拿什么证明它真的发生了”
```
在具体车型实例化时，再把标准功能模型映射到真实 ECU、CAN Signal、硬线、电压与时间戳上。
> **核心原则：标准先定义“应该发生什么”，基线采集再证明“这辆车实际上怎么发生”。**

