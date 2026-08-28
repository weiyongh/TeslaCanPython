# MacBook 项目迁移交接

## 1. 文档用途

本文是 TeslaCanPython 从 Windows 工作环境迁移到 MacBook ChatGPT/Codex 桌面工作环境的统一接管入口。

新环境首次打开本仓库时，应先阅读本文，再按本文给出的顺序加载项目背景、实验结论和可复现证据。不要仅依赖旧电脑上的本地聊天记录恢复项目上下文。

本仓库包含两个相互关联的工作部分：

1. Tesla Model 3 CAN 正常基线采集与分析；
2. `android/CANVoiceRunner`离线 Android 采集脚本播报器。

二者都需要迁移到 MacBook 的同一个 ChatGPT/Codex 项目工作区中。

## 2. 项目目标与工作边界

本项目服务于“新能源诊断 L3 能力与正常基线数据库”的建设。Tesla Model 3 是首个基准车型，不以完整逆向特斯拉私有 CAN/DBC 为目标。

统一原则：

> 系统理解是基础，通信信号是路径，逻辑推理是方法，控制树是目标。

工作边界：

- 每次采集先提出诊断问题，再规划动作、稳定窗口、事件窗口和观察量；
- 优先建立“请求—条件—决策—执行—反馈—结果—异常分支”；
- DBC 用于解释与验证，不视为官方定义；
- 无 DBC 时只保留候选 ID、Byte/Bit、角色猜测和置信度；
- 不跨采集域自动迁移信号语义或候选分数；
- Notion 保存长期知识与决策，本地仓库保存原始证据和可复现分析。

## 3. 新环境首次阅读顺序

MacBook 上克隆仓库并将其添加为 ChatGPT/Codex 项目后，按以下顺序阅读：

1. `AGENTS.md`：工作区长期约定和证据原则；
2. `doc/MacBook_项目迁移交接.md`：本迁移与接管说明；
3. `doc/notion_workspace_context.md`：Notion知识入口；
4. `doc/TM3-002_006采集分析汇总.md`：本批次总体复盘；
5. `doc/特斯拉_DBC_名词解释.md`：已遇到 Signal 的中文解释和使用边界；
6. 根据任务读取对应的 `output/TM3-00x/*分析结论.md`；
7. 需要复算时再读取对应 `input/*.asc`、采集脚本、DBC和 `src/`程序。

不要在一开始遍历全部 ASC 内容。先根据实验结论确定目标 CAN ID、时间窗口和验证问题，再读取原始数据。

## 4. GitHub 与分支状态

- GitHub：`https://github.com/weiyongh/TeslaCanPython.git`
- 主分支：`main`
- Windows环境迁移基线提交：`3ebd4d8`
- 基线提交说明：`docs: add Tesla CAN baseline collection and analysis`

该提交已经包含：

- `input/`全部原始采集、采集脚本和主用DBC；
- `output/`全部分析过程与结果文件；
- `src/`分析程序；
- `dbc/`不同来源和实验性DBC；
- `doc/`项目说明、名词解释和分析汇总；
- `android/CANVoiceRunner`完整Android源项目；
- 根目录工作区配置和说明文件。

## 5. 本批次实验进展

### TM3-001

OBD-II接口验证。当前接法数据不足，已经作为更换采集方案的决策依据保存到Notion。

### TM3-002：进入READY相关状态

已确认：

- 制动开关动作可由 `0x3C2 / VCLEFT_brakeSwitchPressed`捕获；
- 踩制动后BMS充放电能力边界释放；
- 电驱状态报文出现并进入 `STANDBY`；
- 本次没有进入 `ENABLE`，也没有捕获完整高压上电过程。

### TM3-003：静止挂挡

已确认：

- D/R拨杆请求与实际挡位反馈对应；
- 挂入D/R后 `DI_systemState`由 `STANDBY`进入 `ENABLE`；
- 回P后状态恢复 `STANDBY`；
- 四次换挡闭环具有较好的重复性。

### TM3-004：低速加速

已确认：

- `D + ENABLE + 制动释放 + 加速踏板`建立正扭矩请求；
- 实际扭矩与请求同方向跟随；
- 轴速、车速和Pack放电电流上升；
- Pack电压出现轻微负载压降。

### TM3-005：低速松电门回收

已确认：

- 踏板释放越过零扭矩点后，请求和实际扭矩转负；
- 电驱功率与Pack电流转负；
- Pack/DC-link电压轻微抬升；
- 轴速和车速下降；
- 当前采集域中Pack电流正值表示放电，负值表示充电/回收。

### TM3-006：动力电池静态基线

已确认或获得强物理一致性支持：

- P挡、高压接触器闭合、HVIL正常、DC-link已建立；
- Pack电压约348 V，静态放电电流约1.1 A；
- 106个有效Brick，另有两个固定0 V的未使用占位通道；
- 有效Brick约3.284～3.286 V，极差约2 mV；
- SOC平均约45.7%，UI相关SOC约46.5%；
- Pack/DC-link电压接近，12 V母线约13.0～13.1 V。

## 6. 重要DBC边界

### 可支持控制链分析

- 制动开关；
- 换挡拨杆请求与实际挡位；
- `DI_systemState`；
- 加速踏板位置；
- 请求扭矩、实际扭矩、轴速；
- 电驱侧车速和实际电功率；
- Pack电压和电流；
- 接触器、HVIL和Pack/DC-link电压；
- 106个有效Brick电压；
- BMS SOC主体字段。

### 角色基本成立，但绝对值待验证

- `DI_torqueCommand/DI_torqueActual`的绝对Nm缩放和机械参考点；
- BMS最大充放电电流；
- BMS最大放电/回收功率；
- DI最大驱动/回收功率；
- 标称满包能量及相关剩余能量。

### 当前不能进入正常基线

- BMS最高/最低温度；
- `BMS_isolationResistance`；
- `BMS_minBusVoltage/BMS_maxBusVoltage`；
- `UI_actualSOC/UI_usableSOC`；
- `BMS_initialFullPackEnergy`；
- 与车辆物理状态冲突的部分MIA和告警位。

### 当前采集域不可见

- 旋变实时角度、载波、锁相和直接有效性状态；
- U/V/W三相电流和电压；
- 缺相直接诊断量；
- 电流环、转矩环和FOC内部状态；
- 完整的高压预充和接触器闭合过程。

详细冲突和处理原则见 `doc/TM3-002_006采集分析汇总.md`。

## 7. Notion 与本地仓库分工

Notion负责：

- 项目目标和学习框架；
- 控制树、功能诊断树和长期结论；
- 实验计划、决策和下一步；
- 跨车型正常基线数据库。

本地Git仓库负责：

- 原始ASC；
- 采集脚本和时间标记；
- DBC；
- 分析程序；
- 中间CSV、候选报告和事件窗口；
- 可复现的实验分析结论。

迁移到MacBook后，需要使用同一Notion账号重新授权连接。`doc/notion_workspace_context.md`只是Notion页面索引，不是完整离线副本。

## 8. MacBook上的基础接管步骤

### 8.1 克隆仓库

```bash
git clone https://github.com/weiyongh/TeslaCanPython.git
cd TeslaCanPython
git status
git log -1 --oneline
```

期望至少能看到迁移基线提交 `3ebd4d8`或其后续提交。

### 8.2 验证迁移内容

确认以下目录存在：

```text
input/
output/
src/
dbc/
doc/
android/CANVoiceRunner/
```

随机验证：

- 能打开中文文件名；
- 能打开一份大型 `input/*.asc`；
- `input/tesla_model3_ONYX.dbc`存在；
- TM3-002～006分析结论存在；
- `android/CANVoiceRunner/gradlew`存在。

### 8.3 Python环境

`.venv/`和本机缓存没有提交，需要在MacBook重新建立。优先检查项目实际导入，再安装所需依赖。当前分析通常会使用：

- Python 3；
- `python-can`；
- `cantools`；
- 以及Python标准库。

不要复制Windows虚拟环境到macOS。建立新虚拟环境后，先选择一个小型分析命令验证，再运行大型ASC分析。

### 8.4 路径与换行

- macOS路径使用 `/`，不能复用 `C:\...`绝对路径；
- 项目程序应优先使用仓库相对路径；
- Git会处理文本换行差异，不要为了统一换行批量改写原始ASC；
- 原始ASC中的行尾空格属于采集文件格式特征，不应在迁移时机械清理。

## 9. Android项目迁移

### 9.1 项目位置和用途

Android子项目位于：

`android/CANVoiceRunner`

它是面向车辆CAN实验的离线采集脚本执行器，读取 `00s  动作`格式的UTF-8脚本，在计划动作前进行中文语音播报和倒计时，并记录实际触发时间。

### 9.2 已经提交的内容

Git中已经包含：

- Android应用源码；
- `AndroidManifest.xml`和资源；
- Gradle Kotlin DSL配置；
- Gradle Wrapper及其JAR；
- `gradlew`和 `gradlew.bat`；
- 示例采集脚本；
- Android项目README。

当前配置：

- `compileSdk = 36`；
- `targetSdk = 36`；
- `minSdk = 26`；
- application ID：`com.teslacan.voicerunner`。

### 9.3 不应迁移的Windows本机文件

以下文件或目录已被忽略，应在MacBook重新生成：

- `.gradle/`；
- `.idea/`；
- `build/`；
- `app/build/`；
- `local.properties`；
- Android SDK绝对路径；
- 未明确纳入版本管理的签名文件和密钥。

### 9.4 MacBook Android环境恢复

1. 安装并启动Mac版Android Studio；
2. 使用Android Studio打开 `android/CANVoiceRunner`目录，而不是仓库根目录；
3. 安装项目要求的Android SDK 36及相应Build Tools；
4. 使用Android Studio自带JDK或与当前Android Gradle Plugin兼容的JDK；
5. 等待Gradle同步并让Android Studio生成新的 `local.properties`；
6. 在终端确保Wrapper可执行：

```bash
chmod +x android/CANVoiceRunner/gradlew
```

7. 在Android项目目录执行基础构建验证：

```bash
cd android/CANVoiceRunner
./gradlew assembleDebug
```

8. 在模拟器或真机验证脚本导入、中文离线TTS、开始/暂停、倒计时和CSV导出。

首次Gradle同步和构建需要联网下载依赖。不要把Mac新生成的 `local.properties`、缓存或构建产物提交到Git。

### 9.5 Android与CAN分析主线的关系

Android项目不是CAN解析器，它用于提高实车采集动作的一致性和时间可追溯性。后续应重点考虑：

- 将正式采集脚本方便地导入App；
- 将实际执行时间导出CSV；
- 分析程序读取执行记录，将动作时间与ASC自动对齐；
- 保持离线工作，避免实车采集时依赖网络；
- 将脚本版本、ASC文件和执行记录关联到同一实验编号。

## 10. 当前下一步建议

### 分析项目

1. 完成本批次TM3-002～006的Notion总复盘；
2. 规划维护模式正常数据采集，重点观察旋变页、三相电流页和电驱告警矩阵；
3. 使用可信诊断数据校正电池温度与绝缘字段；
4. 单独采集完整预充、接触器闭合和下电母线下降过程；
5. 对未知ID继续采用单变量和重复实验验证，不追求穷举私有DBC。

### Android项目

1. 在MacBook完成首次Gradle同步和Debug构建；
2. 使用现有TM3采集脚本验证解析兼容性；
3. 验证中文离线TTS和倒计时在目标Android设备上的实际效果；
4. 将实际动作时间CSV纳入后续CAN分析输入。

## 11. 交给MacBook ChatGPT/Codex的启动提示词

在MacBook上首次打开该仓库后，可将以下内容作为新任务的第一条消息：

```text
这是“新能源诊断L3能力与正常基线数据库”的Tesla Model 3基准车型项目，同时包含android/CANVoiceRunner采集脚本播报器。

请先完整阅读根目录AGENTS.md，然后依次阅读：
1. doc/MacBook_项目迁移交接.md
2. doc/notion_workspace_context.md
3. doc/TM3-002_006采集分析汇总.md
4. doc/特斯拉_DBC_名词解释.md

阅读后检查Git状态、input/output/src/dbc/doc目录和android/CANVoiceRunner项目是否完整。先向我汇报：项目目标、已完成实验、已确认结论、DBC冲突、当前不可见信号、Android项目状态及Mac环境还缺少什么。未经我说“开始分析”，不要启动新的CAN数据分析。

请遵守以下边界：第三方DBC不是官方定义；未知ID只给候选和置信度；不跨采集域自动迁移语义；原始ASC和既有分析结果不得被覆盖；分析结论必须形成请求—条件—决策—执行—反馈—结果—异常分支，并说明对控制树/诊断树的增量。
```

## 12. Windows旧环境退出条件

满足以下条件后，Windows上的旧工作副本才可以停止作为主环境：

1. MacBook成功克隆并读取全部目录；
2. 中文文件名和大型ASC文件正常；
3. Python分析环境至少完成一次可复现验证；
4. Android项目完成Gradle同步和 `assembleDebug`；
5. GitHub可以正常拉取和推送；
6. Notion连接恢复；
7. MacBook上的ChatGPT/Codex已经按照本文完成知识对齐。

在上述检查完成前，不建议删除Windows本地副本。
