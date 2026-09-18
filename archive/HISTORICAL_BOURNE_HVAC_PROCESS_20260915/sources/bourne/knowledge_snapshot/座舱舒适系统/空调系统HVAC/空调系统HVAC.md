---
title: "空调系统HVAC"
source: notion
source_url: "https://app.notion.com/p/3d6a4e4386498053a16ef09f594b3893"
source_root: "新能源汽修L3学习"
source_path: "新能源汽修L3学习/座舱舒适系统/空调系统HVAC"
source_page_id: "3d6a4e4386498053a16ef09f594b3893"
source_last_edited_time: "2026-09-14T00:14:09.170Z"
snapshot_time: "2026-09-14T08:20:39+08:00"
authority: official
sync_mode: faithful_snapshot
---

# 空调系统HVAC

#  一、系统结构
```plain text
空调系统 HVAC
│
├─ 制冷系统
├─ 制热系统
└─ 通风与空气分配系统
```
# 二、状态和变量
## 1、性质分类
### 1.1 空调请求、设置与目标状态
**请求状态**
- HVAC开启/关闭请求 `HVAC_request`
- 制冷请求状态 `Cooling_request`
- 制热请求状态 `Heating_request`
- 通风请求状态 `Ventilation_request`
- 自动空调请求状态 `Auto_request`
- 除霜/除雾请求状态 `Defog_request`
- 内/外循环请求状态 `Recirc_request`
**HVAC Profile / 设置状态**
- HVAC开启/关闭状态 `HVAC_state`
- 模式设置 `HVAC_mode`
- 自动空调状态 `Auto_state`
- A/C状态 `AC_state`
- 设定温度 `Tcabin_set`
- 风量设置 `Blower_set`
- 配风设置 `AirDist_set`
- 内/外循环状态 `Recirc_state`
**环境与目标状态**
- 环境温度 `Tamb`
- 座舱温度 `Tcabin`
- 阳光负荷 `Solar_load`
- 座舱湿度 `RHcabin`
- 座舱温度目标 `Tcabin_target`
- 空气调节目标 `AirCond_target`
**计算需求状态**
- 制冷需求 `Cooling_demand`
- 制热需求 `Heating_demand`
- 通风需求 `Ventilation_demand`
- 除湿/除雾需求 `Defog_demand`
---
### 1.2 HVAC运行、许可与功率状态
- HVAC运行许可状态 `HVAC_enable`
- HVAC可用状态 `HVAC_available`
- 高压供电可用状态 `HV_available`
- 低压供电可用状态 `LV_available`
- HVAC功率可用状态 `PHVAC_available`
- HVAC功率限制/降额状态 `HVAC_derate`
- HVAC目标功率 `PHVAC_target`
- HVAC实际功率 `PHVAC_actual`
- HVAC故障状态 `HVAC_fault`
---
### 1.3 制冷系统状态和变量
- 制冷允许状态 `Cooling_enable`
- 制冷运行状态 `Cooling_active`
- 制冷限制/降额状态 `Cooling_derate`
- 制冷目标能力 `Cooling_target`
- 制冷实际能力 `Cooling_actual`
- 压缩机请求状态 `Comp_request`
- 压缩机运行状态 `Comp_active`
- 压缩机目标转速 `Ncomp_target`
- 压缩机实际转速 `Ncomp_actual`
- 压缩机温度 `Tcomp`
- 压缩机高压输入电压 `Vcomp_HV`
- 压缩机高压输入电流 `Icomp_HV`
- 压缩机输入功率 `Pcomp`
- 高压侧压力 `Pref_high`
- 低压侧压力 `Pref_low`
- 制冷剂温度 `Tref`
- 电子膨胀阀目标开度 `EEV_target`
- 电子膨胀阀实际开度 `EEV_actual`
- 蒸发器温度 `Tevap`
- 冷凝器温度 `Tcond`
- 制冷系统故障状态 `Cooling_fault`
---
### 1.4 制热系统状态和变量
- 制热允许状态 `Heating_enable`
- 制热运行状态 `Heating_active`
- 制热限制/降额状态 `Heating_derate`
- 制热目标能力 `Heating_target`
- 制热实际能力 `Heating_actual`
- PTC请求状态 `PTC_request`
- PTC运行状态 `PTC_active`
- PTC目标功率 `PPTC_target`
- PTC实际功率 `PPTC_actual`
- PTC电压 `VPTC`
- PTC电流 `IPTC`
- PTC温度 `TPTC`
- 制热系统故障状态 `Heating_fault`
> 对热泵车型，后续实例化时再增加压缩机、阀门、换热器及冷却液回路相关变量，不必现在把 Model 3 热泵结构塞进通用空调笔记。
---
### 1.5 通风与空气分配状态和变量
- 通风允许状态 `Ventilation_enable`
- 通风运行状态 `Ventilation_active`
- 鼓风机请求状态 `Blower_request`
- 鼓风机运行状态 `Blower_active`
- 鼓风机目标转速 `Nblower_target`
- 鼓风机实际转速 `Nblower_actual`
- 风量等级 `Blower_level`
- 出风量 `Airflow_actual`
- 内/外循环目标状态 `Recirc_target`
- 内/外循环实际状态 `Recirc_actual`
- 混合风门目标位置 `BlendDoor_target`
- 混合风门实际位置 `BlendDoor_actual`
- 模式风门目标位置 `ModeDoor_target`
- 模式风门实际位置 `ModeDoor_actual`
- 出风模式 `AirDist_mode`
- 出风口温度 `Toutlet`
---
### 1.6 冷却液相关状态和变量
- 冷却液入口温度 `Tcoolant_in`
- 冷却液出口温度 `Tcoolant_out`
- 冷却液泵请求状态 `CoolantPump_request`
- 冷却液泵运行状态 `CoolantPump_active`
- 冷却液泵目标转速 `Npump_target`
- 冷却液泵实际转速 `Npump_actual`
- 冷却液流量 `CoolantFlow`
- 冷却液阀目标位置/状态 `CoolantValve_target`
- 冷却液阀实际位置/状态 `CoolantValve_actual`
> 本节属于实现/车型相关变量。通用空调系统仅保留必要接口，不在此展开整车热管理冷却液网络。
---
### 1.7 保护与故障状态
- 压缩机过温状态 `Comp_overtemp`
- 压缩机过流状态 `Comp_overcurrent`
- 压缩机高压保护状态 `Comp_highPressureProtect`
- 压缩机低压保护状态 `Comp_lowPressureProtect`
- 制冷剂压力异常状态 `RefPressure_fault`
- 蒸发器防结冰状态 `Evap_freezeProtect`
- PTC过温状态 `PTC_overtemp`
- 高压供电异常状态 `HV_fault`
- 传感器异常状态 `Sensor_fault`
- HVAC功率限制状态 `HVAC_derate`
- HVAC故障状态 `HVAC_fault`
---
### 1.8 热搬运相关控制状态
- 热搬运需求 `HeatTransfer_demand`
- 热搬运方向 `HeatTransfer_direction`
- 热搬运方式 `HeatTransfer_mode`
- 热搬运能力 `HeatTransfer_capacity`
- 热搬运路径/回路状态 `HeatTransfer_path`
- 热搬运限制状态 `HeatTransfer_limit`
> 本节仅在控制树需要时引用，属于控制逻辑层的抽象状态，不要求存在同名 CAN Signal。具体 Evidence 可由制冷、制热、通风及执行反馈变量组合证明；完整热搬运建模归入整车热管理系统。
## 2、来源分类
### 2.1 直接测量
环境温度、
座舱温度、
蒸发器温度、
冷凝器温度、
出风口温度、
制冷剂压力、
制冷剂温度、
压缩机温度、
压缩机电压、
压缩机电流、
PTC温度、
PTC电压、
PTC电流、
冷却液温度。
### 2.2 外部输入
空调开启/关闭请求、
设定温度、
制冷请求、
制热请求、
AUTO请求、
除霜/除雾请求、
风量设定、
出风模式设定、
内/外循环请求。
### 2.3 车辆计算 / 控制量
制冷允许状态、
制热允许状态、
压缩机目标转速、
压缩机功率请求、
电子膨胀阀目标开度、
PTC目标功率、
鼓风机目标转速、
风门目标位置、
热负荷需求、
功率限制/降额状态、
保护状态。
# 三、主线
## 1、控制主线
### 1）制冷  
```plain text
用户舒适需求
↓
座舱制冷需求
↓
制冷能力目标
↓
制冷许可 / 能力限制
↓
压缩机等执行目标
↓
制冷循环建立
↓
蒸发器吸热能力建立
↓
冷风输出
↓
通风系统输送与分配
↓
座舱温度变化
↓
反馈调节
```
### 2）制热
 
```plain text
用户舒适需求
↓
座舱制热需求
↓
制热能力目标
↓
制热许可 / 能力限制
↓
水泵驱动
↓
水循环建立
↓
PTC加热
↓
冷却液升温
↓
暖风水箱换热
↓
热风输出
↓
通风系统输送与分配
↓
座舱温度变化
↓
反馈调节

说明：Should → Execute → Physical Result → Final Result → Feedback
```
### 3）通风
```plain text
用户空气舒适需求
↓
通风需求
↓
风量 / 风向 / 内外循环目标
↓
通风能力限制
↓
风机 / 风门控制
↓
空气流动与分配
↓
座舱空气状态变化
↓
反馈调节
```
### 4）前挡除雾/除霜
```plain text
前挡除雾 / 除霜需求
↓
HVAC除雾策略
↓
空气处理目标（除湿，加热，风量提升）
↓
除霜风门 / 风量控制
↓
空气定向输送至前挡
↓
玻璃表面温湿状态改变
↓
雾 / 霜消除
```
## 2、能量主线
### 1）制冷
```plain text
   座舱空气热量
   ↓
   蒸发器换热
   ↓
   冷媒吸热
   ↓
   冷媒携热循环
   ↓
   冷凝器换热
   ↓
   环境吸收热量
```
### 2）制热
```plain text
电能 
↓
PTC产生热量
↓
PTC与冷却液换热
↓
冷却液吸热升温
↓
冷却液携热循环
↓
暖风水箱换热
↓
空气吸热升温
↓
热空气进入座舱
↓
座舱获得热量
```
<empty-block/>
## 3、动力主线
压缩机、水泵、风机都属于流体系统的动力执行器，分别驱动冷媒、冷却液和空气；只是压缩机同时参与热力学状态改变。
### 1）制冷
```plain text
高压电能
↓
压缩机电机驱动
↓
压缩机做功
↓
冷媒压缩
↓
建立高低压差
↓
冷媒循环建立
```
### 2）制热
```plain text
低压电能
↓
水泵电机驱动
↓
水泵做功
↓
建立压差 / 流量
↓
冷却液循环建立
```
### 3）通风
```plain text
低压电能
↓
风机电机驱动
↓
风机做功
↓
建立空气压差 / 流量
↓
空气流动建立
↓
风门改变流路
↓
目标风道空气流动建立
```
## 4、安全主线
```plain text
HVAC运行
↓
压力 / 温度 / 电气 / 执行状态监测
↓
异常识别
↓
能力限制
↓
保护降级
↓
必要时停止相关执行
↓
关键功能保留 / 故障恢复

前挡除雾 / 除霜
↓
驾驶视野保障
```
# 四、控制树
原理层：热怎么搬。<br>控制层：决定热往哪搬、走哪条路、搬多少，以及怎样送进座舱。<br>实现层：冷媒、冷却液、空气，以及压缩机/泵/阀/风机实际完成它。
```plain text
空调系统
│
├─ 请求
│  ├─ 请求来源
│  │  ├─ 车机输入
│  │  ├─ TBox远程请求
│  │  └─ 车辆自动请求
│  └─ 功能请求
│     ├─ HVAC开关请求
│     ├─ 目标温度请求
│     ├─ AUTO模式请求
│     ├─ 风量请求
│     ├─ 配风请求
│     ├─ 内外循环请求
│     ├─ A/C请求
│     ├─ 除雾 / 除霜请求
│     └─ 座舱过热保护请求
│
├─ 整车控制协调
│  ├─ HVAC运行许可
│  │  ├─ 整车状态许可
│  │  └─ 系统可用状态确认
│  ├─ 安全许可
│  │  ├─ 高压安全许可
│  │  ├─ 绝缘安全许可
│  │  └─ 故障状态许可
│  └─ 功率 / 能量协调
│     ├─ 高压功率可用
│     ├─ 低压供电可用
│     ├─ 电池能量状态
│     └─ HVAC功率限制
│
├─ 状态与目标识别
│  ├─ HVAC设置状态
│  │  ├─ HVAC开关状态
│  │  ├─ 模式设置
│  │  ├─ AUTO状态
│  │  ├─ A/C状态
│  │  ├─ 温度设置
│  │  ├─ 风量设置
│  │  ├─ 配风设置
│  │  └─ 内外循环设置
│  │
│  ├─ 座舱环境状态
│  │  ├─ 座舱温度
│  │  ├─ 座舱湿度
│  │  └─ 空气质量
│  │
│  ├─ 外部环境状态
│  │  ├─ 环境温度
│  │  ├─ 环境湿度
│  │  └─ 阳光负荷
│  │
│  ├─ 目标状态
│  │  ├─ 目标温度
│  │  ├─ 目标空气状态
│  │  └─ 特殊功能目标
│  │
│  └─ 环境调节需求
│     ├─ 温度调节需求
│     ├─ 湿度 / 除湿需求
│     ├─ 空气质量调节需求
│     └─ 送风 / 配风需求
│
├─ 热搬运控制
│  ├─ 热搬运需求确定
│  │  ├─ 座舱降温需求确认
│  │  ├─ 座舱升温需求确认
│  │  └─ 无主动热搬运需求确认
│  │
│  ├─ 热搬运方向确定
│  │  ├─ 座舱排热
│  │  ├─ 座舱供热
│  │  └─ 无主动热搬运
│  │
│  ├─ 热搬运方式选择
│  │  ├─ 制冷
│  │  ├─ 制热
│  │  └─ 制冷 / 制热协同
│  │
│  └─ 热搬运能力确定
│     ├─ 制冷能力需求
│     ├─ 制热能力需求
│     └─ 能力限制 / 降额
│
├─ 制冷控制
│  │
│  ├─ 制冷启动控制
│  │  ├─ 制冷启动条件
│  │  │  ├─ 制冷需求 Cooling_demand
│  │  │  ├─ 制冷允许 Cooling_enable
│  │  │  └─ 制冷系统可用状态
│  │  ├─ 制冷启动决策
│  │  ├─ 制冷启动执行
│  │  │  ├─ 压缩机启动控制
│  │  │  └─ 制冷剂调节控制
│  │  └─ 制冷启动反馈
│  │
│  ├─ 压缩机控制
│  │  ├─ 压缩机运行条件确认
│  │  ├─ 压缩机目标转速 Ncomp_target
│  │  ├─ 压缩机驱动执行
│  │  ├─ 压缩机运行反馈
│  │  │  ├─ 压缩机实际转速 Ncomp_actual
│  │  │  ├─ 压缩机输入功率 Pcomp
│  │  │  └─ 压缩机温度 Tcomp
│  │  └─ 压缩机运行调节
│  │
│  ├─ 制冷剂调节控制
│  │  ├─ 制冷剂状态识别
│  │  │  ├─ 高压侧压力 Pref_high
│  │  │  ├─ 低压侧压力 Pref_low
│  │  │  └─ 制冷剂温度 Tref
│  │  ├─ 制冷剂调节目标确定
│  │  ├─ 电子膨胀阀目标开度 EEV_target
│  │  ├─ 电子膨胀阀执行
│  │  ├─ 制冷剂状态反馈
│  │  │  ├─ 电子膨胀阀实际开度 EEV_actual
│  │  │  ├─ 高压侧压力 Pref_high
│  │  │  └─ 低压侧压力 Pref_low
│  │  └─ 电子膨胀阀再调节
│  │
│  ├─ 空气侧协同控制
│  │  ├─ 空气侧状态确认
│  │  │  ├─ 座舱温度 Tcabin
│  │  │  ├─ 环境温度 Tamb
│  │  │  └─ 蒸发器温度 Tevap
│  │  ├─ 风量目标确定
│  │  ├─ 内 / 外循环目标确定
│  │  ├─ 配风 / 风向目标确定
│  │  ├─ 通风执行请求
│  │  └─ 空气侧反馈
│  │     ├─ 鼓风机运行状态 Blower_active
│  │     ├─ 出风量 Airflow_actual
│  │     ├─ 内 / 外循环实际状态 Recirc_actual
│  │     ├─ 配风实际状态
│  │     └─ 出风口温度 Toutlet
│  │
│  └─ 制冷效果控制
│     ├─ 制冷效果状态识别
│     │  ├─ 座舱温度 Tcabin
│     │  ├─ 蒸发器温度 Tevap
│     │  ├─ 出风口温度 Toutlet
│     │  └─ 出风量 Airflow_actual
│     ├─ 制冷效果判断
│     ├─ 制冷能力调整请求
│     ├─ 冷媒侧 / 空气侧协同调节
│     └─ 制冷效果再反馈
│
├─ 制热控制
│
├─ 通风控制
│  ├─ 风量控制
│  ├─ 内 / 外循环控制
│  └─ 配风控制
│
├─ 特殊功能控制
│  ├─ 前挡除雾 / 除霜
│  └─ 座舱过热保护
│
└─ 状态反馈与保护
   ├─ 系统状态反馈
   ├─ 执行状态反馈
   └─ 异常保五、实现
```
# 五、实现  
```plain text
空调系统
│
├─ 制冷
│  ├─ 电动压缩机
│  ├─ 冷凝器
│  ├─ 蒸发箱
│  ├─ 膨胀阀
│  └─ 冷媒循环管路
│
├─ 制热
│  ├─ PTC电加热器
│  ├─ 水泵
│  ├─ 暖风水箱
│  └─ 水循环管路
│
├─ 通风
│  ├─ 鼓风机
│  ├─ 内外循环风门
│  ├─ 模式 / 配风风门
│  ├─ 风道
│  ├─ 出风口
│  └─ 空调滤芯
│
├─ 前挡除雾/除霜
│
└─ 传感器
   ├─ 温度传感器
   │  ├─ 座舱温度
   │  ├─ 环境温度
   │  ├─ 出风温度
   │  └─ 蒸发器温度
   ├─ 压力传感器
   │  └─ 冷媒压力
   ├─ 空气质量传感器
   └─ 阳光传感器
         
```
# 六、诊断树
<empty-block/>
# 七、状态
<empty-block/>
# 八、边界
```plain text
空调系统 HVAC
│
├─ 人机 / 远程边界
│  └─ 功能请求 / 目标设定
│
├─ 整车控制边界
│  └─ 运行许可 / 安全许可 / 功率与能量约束
│
├─ 能源边界
│  └─ 高压 / 低压供电
│
├─ 热管理边界
│  └─ 热源 / 热汇 / 热搬运资源与状态
│
└─ 座舱环境边界
   └─ 环境状态 / 座舱状态 / 空气调节结果
```
# FAQ 
## 1、L3四条主线在HVAC中的表现
```plain text
控制主线：为什么动、要做到什么程度？
需求 → 目标 → 许可/限制 → 控制 → 执行 → 结果 → 反馈

动力主线：什么东西被驱动、流动如何建立？
压缩机 → 冷媒循环
水泵   → 冷却液循环
风机   → 空气流动

能量主线：能量从哪里来、到哪里去？
制热：电能 → 热量 → 冷却液 → 空气 → 座舱
制冷：座舱热量 → 冷媒搬运 → 环境

安全主线：什么条件不成立就必须限制或停止？
高压安全 / 温压边界 / 部件保护 / 系统故障
→ 限功率 / 禁止执行 / 退出
```
这其实说明四主线不是“四张固定流程图”，而是**四种观察系统的坐标轴**：
> **控制看意图，动力看运动，能量看传递，安全看边界。**
## 2、HVAC系统原理抽象   
HVAC原理要点就是热的搬运。<br>其原理更适合成为一张非常薄的物理底图：
```plain text
热量是对象
冷媒/冷却液/空气是载体
压缩、膨胀、相变、换热是机制
压缩机/泵/阀/风机是操纵手段
温度、压力、流量等是状态与 Evidence
```
然后再问：<br>控制系统究竟能够操纵什么，使热按照需要搬？<br>这句话可能就是从“热怎么搬”的系统原理跨到“控制什么”的控制树之间缺失的那座桥。
<empty-block/>
<empty-block/>
<empty-block/>
<empty-block/>
<empty-block/>
<empty-block/>
<empty-block/>
<empty-block/>
<empty-block/>
<empty-block/>
<empty-block/>
<empty-block/>
<empty-block/>
<empty-block/>
<empty-block/>
<empty-block/>
<empty-block/>
<empty-block/>
<empty-block/>

