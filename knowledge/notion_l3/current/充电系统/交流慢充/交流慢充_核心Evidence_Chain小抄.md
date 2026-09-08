---
title: "交流慢充_核心Evidence_Chain小抄"
source: notion
source_url: "https://app.notion.com/p/3d3a4e4386498091bc0ae1b6b8a21766"
source_root: "新能源汽修L3学习"
source_path: "新能源汽修L3学习/充电系统/交流慢充/交流慢充_核心Evidence_Chain小抄"
source_page_id: "3d3a4e4386498091bc0ae1b6b8a21766"
source_last_edited_time: "2026-09-06T15:57:05.459Z"
snapshot_time: "2026-09-08T19:43:24+08:00"
authority: official
sync_mode: faithful_snapshot
---

# 交流慢充_核心Evidence_Chain小抄

# 交流慢充核心 Evidence Chain 小抄
> **用途：**从完整慢充控制树中蒸馏出的现场诊断索引。
	不替代控制树、诊断树和车型实例化，只回答一个问题：
	**慢充从”连接成立”到”功率真正进入 Pack”，关键 Evidence<br>应该怎样逐级成立？**
## 1. 慢充核心 Evidence Chain
```plain text
CC
↓
CP
↓
Ready
↓
EVSE输出
↓
AEVSE
↓
A₂
↓
IAC_target
↓
高压路径
↓
OBC功率转换
↓
IAC_actual
↓
Pack
```
## 2. 三段理解
```plain text
CC → CP → Ready → EVSE输出
        资格 / 状态建立

AEVSE → A₂ → IAC_target
        能力边界 / 控制目标

高压路径 → OBC功率转换 → IAC_actual → Pack
        功率执行 / 实际结果
```
第一段回答：**为什么现在允许开始充电？**
第二段回答：**外部允许多少、车辆允许多少、最终要求 OBC 取多少？**
第三段回答：**目标形成以后，功率是否真正建立并进入动力电池？**
关键变量：
```plain text
A₁         = 线缆允许电流
Amax       = 桩自身最大输出能力
AEVSE      = 桩发布的允许电流上限
A₂         = 车辆自身允许交流输入电流
IAC_target = min(AEVSE, A₂)
IAC_actual = OBC实际交流输入电流
```
## 3. 把控制链反过来，就是诊断索引
```plain text
Pack没有正常充电
↑
IAC_actual正常吗？
↑
OBC功率转换正常吗？
↑
高压路径建立了吗？
↑
IAC_target形成了吗？
↑
A₂允许吗？
↑
AEVSE有效吗？
↑
EVSE输出建立了吗？
↑
Ready成立了吗？
↑
CP正常吗？
↑
CC正常吗？
```
> **寻找”最后一个已经成立的状态”和”第一个没有成立的 Evidence”。**
第一个断点附近，就是优先收敛的故障边界。
## 4. 每个节点现场问什么
```plain text
CC
↓
连接确认成立了吗？
线缆能力 A₁ 被正确识别了吗？

CP
↓
CP状态正确吗？
PWM有效吗？
EVSE允许能力信息能被车辆正确识别吗？

Ready
↓
车辆内部充电条件成立了吗？
S2 / CP Ready状态正确建立了吗？

EVSE输出
↓
车辆Ready以后，交流输入真的建立了吗？

AEVSE
↓
桩当前允许车辆最多取多少交流电流？

A₂
↓
车辆当前自身最多允许多少交流输入电流？

IAC_target
↓
OBC最终被要求取多少交流电流？

高压路径
↓
预充 / HV Bus / 主接触器 / 高压充电路径是否建立？

OBC功率转换
↓
OBC是否真正进入AC→DC功率转换状态？

IAC_actual
↓
OBC实际交流输入电流是多少？
是否正确跟随IAC_target？

Pack
↓
功率是否真正进入动力电池？
Pack实际电压 / 电流 / 功率是否与前级Evidence一致？
```
## 5. 最关键的诊断分叉
### 5.1 IAC_target = 0
```plain text
IAC_target = 0
```
首先不要问”OBC为什么没有输出”，而应向上游查：
```plain text
AEVSE有效吗？
↓
A₂是否为0 / 被限制？
↓
充电许可是否成立？
↓
目标为什么没有形成？
```
**没有目标，就不能用”没有实际电流”证明 OBC 执行失败。**
### 5.2 IAC_target \> 0，但 IAC_actual ≈ 0
在充电许可、高压路径和合理响应时间均已满足的前提下：
```plain text
IAC_target > 0
高压路径 = Established
↓
IAC_actual ≈ 0
```
说明：**目标已经形成，但没有转化为实际交流输入电流。**
重点进入：
```plain text
OBC执行状态
AC实际输入
DC实际输出
OBC Ready / Fault / Derate
高压侧运行条件
IAC_actual反馈可信度
```
这能把边界推向 OBC 执行链，但**不能单独判定 OBC 总成损坏**。
### 5.3 IAC_target下降，IAC_actual正常跟随
```plain text
IAC_target ↓
↓
IAC_actual ↓
```
OBC可能只是在正确执行新的目标。
继续向上追：
```plain text
AEVSE下降？
还是
A₂下降？
```
AEVSE下降：重点看 EVSE / CP 能力链。
A₂下降：继续看 BMS允许能力、OBC允许能力/降额、热管理约束、整车约束。
### 5.4 IAC_target稳定，IAC_actual异常下降 / 波动
```plain text
IAC_target ───── 稳定
IAC_actual  ↓ ↑ ↓ ↑  异常
```
这是高价值异常特征。优先观察：
```plain text
AC输入 V / I / P
↓
OBC Ready / Derate / Temperature / Fault
↓
DC输出 V / I / P
↓
Pack实际充电功率
```
如果 Target 稳定，而 AC/DC 实际功率同步异常，故障边界会明显向 OBC<br>功率执行链或相关功率条件收敛。
### 5.5 IAC_target正常，IAC_actual正常，但 Pack异常
```plain text
IAC_target 正常
↓
IAC_actual 正常
↓
OBC AC输入正常
↓
？
↓
Pack充电异常
```
不要继续死盯交流输入电流，应检查：
```plain text
OBC DC输出
↓
HV Bus / 高压路径
↓
Pack实际 V / I / P
↓
BMS充电状态 / 电池边界
```
若 OBC AC/DC 两侧均正常，故障边界继续向 Pack / BMS 移动。
## 6. “谁先变化”比单个异常值更重要
把关键变量放到同一时间轴：
```plain text
CC
CP
Ready
AEVSE
A₂
IAC_target
IAC_actual
OBC Ready / Derate / Fault
AC V/I/P
DC V/I/P
HV Bus / Contactor
Pack V/I/P
```
重点问：**第一个异常变化是谁？**
```plain text
AEVSE ↓
→ IAC_target ↓
→ IAC_actual ↓
```
优先看外部能力链。
```plain text
OBC Temperature ↑
→ OBC Capability ↓
→ A₂ ↓
→ IAC_target ↓
→ IAC_actual ↓
```
更像 OBC 自身受控降额。
```plain text
IAC_target稳定
→ IAC_actual先异常
→ AC/DC功率异常
→ OBC Fault随后出现
```
更支持 OBC 功率执行链异常。
```plain text
HV Bus / Contactor先异常
→ DC功率消失
→ IAC_actual下降
→ OBC退出
```
OBC退出可能只是结果，不能把后出现的 OBC Fault 当成第一原因。
## 7. Evidence 还有第三层：物理实测
```plain text
Target
控制系统想做什么
↓
IAC_target

Actual Feedback
控制器认为自己做到了什么
↓
IAC_actual / AC/DC状态

Physical Reality
物理世界真正发生了什么
↓
独立电压 / 电流 / 波形 / 功率测量
```
> **IAC_actual 是 Evidence，但 Evidence 本身也可能失效。**
当 ECU 数据与故障现象矛盾时，应使用独立物理测量核实。
## 8. 一眼判读
```plain text
AEVSE低
→ 外部允许能力边界

A₂低
→ 车辆自身能力 / 约束边界

IAC_target低
→ 先解释目标为什么低

IAC_target正常 + IAC_actual低
→ 查目标→执行链

IAC_target稳定 + IAC_actual波动
→ 高价值OBC执行异常特征

IAC_actual正常 + DC输出异常
→ 查OBC功率转换 / 高压侧

AC/DC输出均正常 + Pack异常
→ 边界继续向Pack / BMS移动
```
## 9. 现场心法
```plain text
              Pack异常
                 ↑
            IAC_actual
                 ↑
           OBC功率转换
                 ↑
              高压路径
                 ↑
            IAC_target
                 ↑
          ┌──────┴──────┐
        AEVSE            A₂
          ↑              ↑
      EVSE / CP      车辆能力约束
          ↑              │
          └──── Ready ───┘
                 ↑
                CP
                 ↑
                CC
```
不要先问：
> “哪个总成坏了？”
先问：
> **哪一个本来应该成立的 Evidence，第一次没有成立？**
## 10. 最终记忆句
> **CC / CP / Ready 决定能不能进入充电；AEVSE / A₂ / IAC_target<br>决定应该充多少；高压路径 / OBC / IAC_actual / Pack<br>证明实际上充成了什么。**
> **Limit → Target → Actual。谁先变，谁没跟，哪里第一次失去<br>Evidence，故障边界就优先向哪里收敛。**

