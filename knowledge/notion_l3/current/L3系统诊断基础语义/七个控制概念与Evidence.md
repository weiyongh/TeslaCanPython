---
title: "七个控制概念与Evidence"
source: notion
source_url: "https://app.notion.com/p/3d1a4e43864980879991e843589536a6"
source_root: "新能源汽修L3学习"
source_path: "新能源汽修L3学习/L3系统诊断基础语义/七个控制概念与Evidence"
source_page_id: "3d1a4e43864980879991e843589536a6"
source_last_edited_time: "2026-09-04T15:03:20.377Z"
snapshot_time: "2026-09-08T19:43:24+08:00"
authority: official
sync_mode: faithful_snapshot
---

# 七个控制概念与Evidence

```javascript
                    Capability
                        │
                        ▼
Target ───────→ Request
                  │
          State + Variable
                  │
             Condition
                  │
                  ▼
               Command
                  │
                  ▼
               Action
                  │
                  ▼
             物理世界
                  │
                  ▼
              Feedback
                  │
                  ├────→ Variable
                  │
                  └────→ State
                           │
                           └────→ 下一轮 Condition

══════════════ Boundary ══════════════
       不同控制主体在这里交互

◎ Evidence
       诊断者从外部验证整条因果链
```
输入 → 变量/状态 → 条件表达式 → 状态机/控制决策 → Command → Action → Feedback → 新的变量/状态。
# L3 系统诊断基础语义：七个控制概念与 Evidence
> **定位**：本页用于统一新能源 L3 系统学习、控制树、车型实现、通信分析与故障诊断中的基础语言。
	目标不是增加术语，而是避免在分析控制过程时把“能力、变量、状态、条件、请求、执行、边界”混为一谈。
---
## 1. 为什么需要统一这七个概念
一个系统的正常控制过程，本质上不断回答下面的问题：
- **Capability｜能力**：能不能做？能做到什么范围？
- **Variable｜变量**：现在这个量是多少？
- **State｜状态**：现在是什么状态、处在哪一步？
- **Condition｜条件**：满足什么才允许继续？
- **Request｜请求**：控制主体希望对方做什么？
- **Action｜执行**：控制系统或执行机构实际上做了什么？
- **Boundary｜边界**：系统在哪里交互？各自责任到哪里？
而诊断者还要额外追问：
> **Evidence｜证据：我凭什么证明上述判断是真的？**
因此，七个概念描述的是**系统控制世界**；Evidence 描述的是**诊断者如何认识和验证这个世界**。
---
## 2. 七个核心概念
<table header-row="true">
<tr>
<td>概念</td>
<td>定义</td>
<td>核心问题</td>
<td>典型示例</td>
</tr>
<tr>
<td>**能力 Capability**</td>
<td>系统、控制器或部件能够提供、承受或完成的功能及范围</td>
<td>**能做什么？范围多大？**</td>
<td>充电桩最大输出电压/电流；动力电池最大允许充电电流</td>
</tr>
<tr>
<td>**变量 Variable**</td>
<td>描述系统当前物理量或逻辑量的可变化数据</td>
<td>**现在是多少？**</td>
<td>电池电压、电流、SOC、温度</td>
</tr>
<tr>
<td>**状态 State**</td>
<td>系统、部件或控制过程当前所处的离散状态</td>
<td>**现在是什么？处在哪一步？**</td>
<td>已连接、Locked、Charging、Fault</td>
</tr>
<tr>
<td>**条件 Condition**</td>
<td>某个动作或状态迁移被允许发生前必须满足的判据</td>
<td>**满足什么才能继续？**</td>
<td>绝缘正常、锁止完成、电压条件满足</td>
</tr>
<tr>
<td>**请求 Request**</td>
<td>一个控制主体向另一个主体提出的动作要求、目标或期望值</td>
<td>**希望它做什么？**</td>
<td>请求充电 80 A；请求闭合接触器</td>
</tr>
<tr>
<td>**执行 Action**</td>
<td>控制主体根据请求和条件实施的控制动作，以及执行机构实际产生的物理动作</td>
<td>**实际上做了什么？**</td>
<td>输出线圈驱动；接触器机械闭合；功率模块调节输出</td>
</tr>
<tr>
<td>**边界 Boundary**</td>
<td>两个系统之间进行能量、信息、控制或物理作用交换的接口与责任分界</td>
<td>**在哪里交互？责任到哪里？**</td>
<td>车辆快充口；控制器与执行器接口</td>
</tr>
<tr>
<td>命令Command</td>
<td>决策后向受控对象发出的明确指令</td>
<td>**命令它做什么？**</td>
<td>\*</td>
</tr>
<tr>
<td>目标Target </td>
<td>控制希望最终达到的量值或状态</td>
<td>要达到什么？</td>
<td>\*</td>
</tr>
<tr>
<td>Feedback 反馈</td>
<td>Action 后返回给控制系统、用于确认结果的信息</td>
<td>做完以后结果怎样？</td>
<td>\*</td>
</tr>
</table>
---
## 3. Capability｜能力
**能力描述系统“具备什么能力以及能力边界”，而不是系统此刻正在做什么。**
例如直流快充：
```plain text
充电桩能力
├─ 最大输出电压
├─ 最大输出电流
└─ 最大输出功率

车辆能力
├─ 允许充电电压范围
├─ 最大允许充电电流
└─ 电池当前可接受充电能力
```
### 能力 ≠ 请求
```plain text
桩能力：最多可输出 250 A
车辆能力：最多允许 180 A
                  ↓
车辆当前请求：80 A
```
> **能力描述“能做到哪里”；请求描述“现在想要什么”。**
能力决定控制空间和上限，请求则可以随控制过程持续变化。
---
## 4. Variable｜变量
变量用于描述系统中**连续变化或可变化的量值/逻辑数据**。
例如：
```plain text
电池电压 = 352.6 V
充电电流 = 79.6 A
SOC = 63 %
枪口温度 = 41 ℃
```
### 变量 ≠ 状态
```plain text
电池电压 = 352.6 V       ← Variable
SOC = 63 %               ← Variable

充电状态 = Charging      ← State
锁止状态 = Locked        ← State
```
工程实现中，状态本身也可能由布尔量或枚举变量编码。因此这里的区别不是编程数据类型，而是**控制语义**：
> **Variable 更强调“量值是什么”；State 更强调“系统现在是什么/处在哪一步”。**
---
## 5. State｜状态
状态描述系统、控制器、部件或控制流程在某一时刻**已经处于什么阶段或结果**。
例如：
```plain text
未连接
  ↓
已连接
  ↓
通信建立
  ↓
充电准备
  ↓
高压回路建立
  ↓
Charging
```
状态是控制过程的重要锚点。
### 状态 ≠ 条件
```plain text
当前 State：
车辆已连接
      │
      ▼
进入下一阶段所需 Conditions：
├─ 连接确认成立
├─ 通信建立
├─ 参数协商完成
└─ 安全检查通过
      │
      ▼
下一 State：
高压充电准备 / 高压回路建立
```
> **状态回答“现在在哪里”；条件回答“凭什么允许往下走”。**
---
## 6. Condition｜条件
条件是控制逻辑中的**门槛和判据**。
它通常来自：
- 一个或多个 Variable 的范围判断；
- 一个或多个 State 的成立；
- Capability 是否满足需求；
- 安全检查结果；
- 边界输入是否有效；
- 其他控制器的许可或互锁结果。
例如：
```plain text
允许建立高压充电回路
│
├─ 连接确认成立
├─ 通信状态正常
├─ 车辆允许充电
├─ 绝缘条件满足
├─ 温度条件满足
└─ 相关高压安全条件满足
```
因此 Condition 往往是控制树与诊断树连接最紧密的位置：
> **某个 Action 没发生，不要首先怀疑执行器；先问它的 Condition 是否成立。**
---
## 7. Request｜请求
Request 是**控制意图**。
它可以是：
```plain text
请求闭合接触器
请求进入充电状态
请求充电电流 = 80 A
请求充电电压 = XXX V
请求冷却
请求加热
```
请求并不等于执行，更不等于物理结果。
典型链路：
```plain text
Request
   ↓
Condition 判断
   ↓
Action
   ↓
Physical Result
   ↓
State / Variable 改变
```
因此：
> **“有请求”不能证明“动作已经发生”。**
---
## 8. Action｜执行
Action 是把控制意图转变成现实的环节。
建议在诊断中区分两层 Action：
```plain text
控制 Action
    ↓
执行机构 / 功率器件
    ↓
物理 Action
```
以接触器为例：
```plain text
闭合接触器请求
      │
      ▼
 Request
      │
      ▼
闭合条件满足
      │
      ▼
 Condition
      │
      ▼
控制器输出驱动
      │
      ▼
 Control Action
      │
      ▼
接触器机械闭合
      │
      ▼
 Physical Action
      │
      ▼
辅助触点 = Closed
母线电压建立
      │
      ▼
 State / Variable
```
这一区分对诊断非常重要。
```plain text
没有 Request
      ↓
为什么控制逻辑没有提出请求？

有 Request，无 Control Action
      ↓
Condition 未满足？
控制器没有输出？
保护逻辑介入？

有 Control Action，无 Physical Action
      ↓
驱动线路？
线圈？
执行机构？
机械故障？

有 Physical Action，结果仍异常
      ↓
反馈？
采样？
功率路径？
负载侧？
```
这使“执行器不动作”从一个模糊现象变成可以分段验证的因果链。
---
## 9. Boundary｜边界
边界不是单纯的“一个地方”，而是**系统责任、能量、信息和控制发生交换的位置**。
例如车—桩快充边界：
```plain text
             充电桩
                │
        桩侧责任 / 控制域
                │
                ▼
══════════ 车桩 Boundary ══════════
                ▲
                │
        车辆责任 / 控制域
                │
               车辆
```
在这个边界上可能同时存在：
```plain text
能量交换
├─ DC+
└─ DC-

通信交换
├─ S+
└─ S-

连接 / 控制相关
├─ CC1
├─ CC2
├─ A+
├─ A-
└─ PE
```
Boundary 对诊断的核心意义是：
> **把“到底是谁的问题”转换成“边界两侧分别发生了什么”的可验证问题。**
因此边界也是高价值的 **Measurement Access / Evidence Access** 位置。
---
## 10. 七个概念如何组成控制语言
可以把一个典型控制过程抽象成：
```plain text
Capability
系统有没有能力完成目标？
        │
        ▼
Variable / State
系统现在的量值和状态是什么？
        │
        ▼
Condition
是否满足进入下一步的条件？
        │
        ▼
Request
控制主体希望发生什么？
        │
        ▼
Action
控制器和执行机构实际上做了什么？
        │
        ▼
Variable / State
物理世界是否产生预期变化？
        │
        └──────────────→ 下一控制循环

Boundary
贯穿整个过程：
定义不同控制主体在哪里交换能量、信息、请求和状态。
```
注意：这不是要求所有系统都严格按照一个固定线性顺序运行，而是一套用于**描述和拆解控制逻辑的语义工具**。
---
## 11. 快充案例：七个概念放到同一条控制链
```plain text
【Capability】
车辆能接受多少？
充电桩能提供多少？
        │
        ▼
【Boundary】
车桩通过标准接口建立物理与通信连接
        │
        ▼
【Variable】
Ubat / SOC / 温度 / 电流……
        │
        ▼
【State】
连接状态 / 通信状态 / 充电阶段……
        │
        ▼
【Condition】
允许充电？
绝缘条件满足？
高压安全条件满足？
        │
        ▼
【Request】
车辆提出当前充电需求
        │
        ▼
【Action】
桩调节功率输出
车辆 / 桩执行相应控制动作
        │
        ▼
【Variable / State】
实际电压、电流、SOC、温度和充电状态发生变化
        │
        └──────────────→ 下一轮控制
```
---
## 12. Evidence 不与七个概念并列
Evidence 是诊断者对上述七个概念进行验证的方法。
```plain text
Capability
    └─ Evidence：能力声明 / 配置 / 参数 / 实测能力

Variable
    └─ Evidence：CAN Signal / 万用表 / 示波器 / 传感器测量

State
    └─ Evidence：状态报文 / 反馈信号 / 物理现象

Condition
    └─ Evidence：构成该条件的变量、状态和判据是否成立

Request
    └─ Evidence：控制请求报文 / 内部状态 / 输出命令

Action
    └─ Evidence：驱动电压 / 电流 / 波形 / 执行机构物理动作

Boundary
    └─ Evidence：边界两侧的电气、通信和物理测量
```
因此诊断者真正需要不断问的是：
> **我要证明什么？**
	**这个 Evidence 能不能证明它？**
	**Evidence 从哪里取得？**
	**它证明的是 Request、Action，还是最终 State？**
---
## 13. 从控制树到诊断树
七个概念最大的价值不是给节点贴标签，而是帮助故障定位。
例如“接触器没有闭合”：
```plain text
🔴 接触器未闭合
│
├─ Capability
│  └─ 系统是否具备执行能力？
│
├─ State
│  └─ 当前控制阶段是否已经到达闭合阶段？
│
├─ Condition
│  └─ 闭合条件是否全部满足？
│
├─ Request
│  └─ 是否产生闭合请求？
│
├─ Action
│  ├─ 控制器是否输出驱动？
│  └─ 接触器是否产生机械动作？
│
├─ Variable / State
│  ├─ 辅助触点状态是否改变？
│  └─ 高压母线电压是否按预期建立？
│
└─ Boundary
   └─ 控制器—线束—接触器之间在哪一段失去控制传递？
```
这样，诊断树就不是凭经验罗列“可能坏的零件”，而是沿着**控制因果链**逐段寻找断点。
---
## 14. 与 L3 知识结构的关系
建议统一使用以下图例：
```plain text
🟢 控制树
🔵 实现
🔴 诊断树
⇄ 通信
```
七个概念贯穿这些层级：
```plain text
🟢 控制树
   └─ 用 Capability / Variable / State / Condition /
      Request / Action / Boundary 描述“系统应该怎样运行”

🔵 车型实现
   └─ 回答这些概念在具体车型上由什么控制器、
      线路、执行器、传感器、报文和 Signal 实现

⇄ 通信
   └─ 承载能力、变量、状态、请求等信息在控制主体之间交换

🔴 诊断树
   └─ 沿控制因果链寻找：
      能力是否存在？
      变量是否合理？
      状态是否到达？
      条件是否满足？
      请求是否产生？
      执行是否发生？
      边界是否正常？
```
最终再由 Evidence 对每一个判断进行证明。
---
## 15. 一页记忆版
```plain text
Capability｜能力
→ 我能做什么？

Variable｜变量
→ 现在是多少？

State｜状态
→ 现在是什么 / 在哪一步？

Condition｜条件
→ 满足什么才能继续？

Request｜请求
→ 我希望你做什么？

Action｜执行
→ 实际上做了什么？

Boundary｜边界
→ 在哪里交互？责任到哪里？

Evidence｜证据
→ 我凭什么证明以上判断是真的？
```
### 核心关系
```plain text
Capability
     ↓
Variable + State
     ↓
Condition
     ↓
Request
     ↓
Action
     ↓
新的 Variable + State
     ↺

Boundary：定义控制主体之间的交互界面

Evidence：从诊断者视角验证整条控制链
```
---
## 16. 核心原则
> **控制树不是部件树，而是因果链。**
> **Request 是意图，Action 是执行，State / Variable 是结果；三者不能互相代替。**
> **Condition 决定 Action 是否被允许发生，因此“没有动作”首先不等于“执行器坏了”。**
> **Boundary 把系统间责任分界变成可测量、可验证的位置。**
> **Evidence 不属于控制对象本身，而属于诊断者对控制世界的证明过程。**
最终形成 L3 诊断的基本思维：
```plain text
理解系统控制逻辑
        ↓
找到控制链当前位置
        ↓
识别 Capability / Variable / State /
Condition / Request / Action / Boundary
        ↓
提出 Evidence Requirement
        ↓
从合适 Measurement Access 获取 Evidence
        ↓
比较“控制系统认为发生了什么”
与“物理世界实际上发生了什么”
        ↓
定位控制因果链断点
```

