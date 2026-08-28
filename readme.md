# 终端环境进入
```shell
.\.venv\Scripts\Activate.ps1
```

# chatgpt：dbc和asc报文熟悉
```
明白，就是从实际asc文件中找到model3真实can数据的样子，建立一个数据观看的体感，形成经验

对，就是这个意思。现在重点已经从“找出某个神秘 ID”转向了培养对真实 CAN 数据的工程直觉。

比如今天这一轮其实已经形成了几个很具体的“体感”：0x102 是高频周期状态报文；一次现实中的“开门”，在 CAN 上不是一个瞬间，而是一串几十到几百毫秒展开的状态变化；同一条 Message 里可以同时塞进锁扣、按钮、执行器、把手、后视镜等很多 Signal；而大量周期性变化即使规律非常漂亮，也未必和你正在做的动作有关。

以后再看到 ASC，你会逐渐形成类似看示波器波形的感觉：

先看这个 ID 是周期报文还是事件报文 → 再看 Message 属于什么系统 → 再看具体 Signal → 最后把 Signal 的时间变化和真实车辆动作对应起来。

而 DBC 在这里更像一张“地图”，ASC 才是你这辆 2021 Model 3 实际跑出来的道路。DBC 告诉我们 VCLEFT_frontLatchStatus 理论上是什么，你自己的 ASC 则告诉我们它在这辆车上确实表现为 CLOSED → OPENED → CLOSED。两者一结合，知识才真正落地。

这也很符合你现在学习 CAN 的阶段：暂时不用急着做到“我能逆向所有未知报文”。先积累几十个经过实车验证的 Message/Signal，尤其是门、锁、灯、制动、档位、充电、电池、热管理这些物理意义很直观的量。积累到一定程度后，再面对一份陌生 ASC，很多东西你会自然知道先看哪里、什么值得怀疑、什么大概率只是背景周期数据。

今天从 Java 那条“收敛不了”的路绕到 DBC + ASC，其实这个弯没白绕——它让我们知道了为什么单靠统计相似性会碰壁，也知道了下一步该怎样读真实 CAN。

现在可以先围绕这份 ASC 慢慢熟悉。例如看到一个 DBC 命中的 ID，先问三个问题：它是什么 Message？里面有哪些 Signal？这些 Signal 在这几分钟真实驾驶操作过程中是怎样变化的？遇到明显的变化，再回头对照你的录音操作记录。这样不必要求录音时间精确到秒，因为很多时候我们是在认识数据特征，而不是做严格的事件因果实验。
```

# TODO 特斯拉Can数据ID范围

```
VehicleBus（车辆总线）：车辆控制、动力系统通讯，消息ID范围：0x100-0x3FF
ChassisBus（底盘总线）：底盘控制、安全系统通讯，消息ID范围：0x400-0x5FF
PartyBus（娱乐总线）：娱乐系统、显示屏通讯，消息ID范围：0x600-0x7FF
```
# TODO SavvyCan

[savvycan](https://blog.csdn.net/gitblog_00649/article/details/163753036)

[git项目](https://blog.csdn.net/gitblog_00649/article/details/163753036)

# 按采集脚本提取关键 Signal

详细文档：[extract_scripted_signals.md](doc/extract_scripted_signals.md)

已在实车采集数据中遇到的 Model 3 Message、Signal、枚举和中文解释：
[model3_dbc.md](doc/model3_dbc.md)

程序接受“标准采集脚本、ASC、DBC”三个文件名，自动识别脚本中的动作时间点，
并从 ASC 中筛选在这些时间点附近重复、稳定变化的 DBC Signal：

```powershell
python src\extract_scripted_signals.py `
    input\can_开门关门采集脚本.txt `
    input\can_20260823164405.asc `
    input\tesla_model3_ONYX.dbc
```

默认在 `output` 中生成 Markdown 报告、可用 Excel 打开的 CSV 明细，以及排名第一的
候选信号所属 CAN Message 的全 Signal 状态变化时间线。Message 追踪文件名带有
ASC 名、CAN ID 和运行时间戳，因此不会覆盖以前的结果。
可通过 `--tolerance 2` 设置动作点前后匹配秒数，通过 `--top 10` 设置候选信号数量。

使用 `--exclude-regex` 可以排除不需要分析的 Message 或 Signal，匹配时忽略大小写：

```powershell
python src\extract_scripted_signals.py `
    input\can_开门关门采集脚本.txt `
    input\can_20260823164405.asc `
    input\tesla_model3_ONYX.dbc `
    --exclude-regex "mirrorTilt"
```

正则可以组合多个排除项，例如 `--exclude-regex "mirrorTilt|temperature|counter$"`。

# Python 程序文档约定

## 事件驱动 CAN 候选 ID 遴选

详细文档：[select_can_candidates.md](doc/select_can_candidates.md)

```powershell
python src\select_can_candidates.py `
    input\can_20260824175030.asc `
    input\驾驶门物理按钮开关窗采集脚本.txt `
    --profile generic-event `
    --profile window `
    --pre-offset 0.5 `
    --post-offset 1.0 `
    --min-blind-score 60 `
    --dbc dbc\特斯拉左侧车窗_DBC_EXP.dbc
```

程序支持复合 profile 并集遴选，保留候选来源；DBC 仅用于标记已知 Message，
不参与盲评分。所有输出默认使用“ASC 文件名 + 执行时间戳”作为前缀，并生成
可直接加载 SavvyCAN 的候选事件窗口 ASC。

## 无 DBC 分析车窗通风

详细文档：[analyze_window_vent.md](doc/analyze_window_vent.md)

```powershell
python src\analyze_window_vent.py `
    input\can_车窗通风采集脚本.txt `
    input\can_20260824154441.asc
```

程序利用重复的通风/关闭动作和稳定状态区间，输出 CAN ID、Byte、Bit 候选排名，
并区分稳定状态候选与瞬时请求候选，不需要 DBC。

## 使用 DBC 提取 Window Signal

详细文档：[extract_window_signals.md](doc/extract_window_signals.md)

```powershell
python src\extract_window_signals.py `
    input\can_车窗通风采集脚本.txt `
    input\can_20260824154441.asc `
    dbc\tesla_model3_ONYX.dbc.txt
```

输出结构与 `extract_scripted_signals.py` 一致，并针对 ONYX DBC 与 ASC 的 DLC 不一致进行受控修正。

## 驾驶门物理按钮开关窗混合分析

详细文档：[analyze_driver_window_button.md](doc/analyze_driver_window_button.md)

```powershell
python src\analyze_driver_window_button.py `
    input\驾驶门物理按钮开关窗采集脚本.txt `
    input\can_20260824175030.asc `
    input\tesla_model3_ONYX.dbc `
    --verify-id 0x1FA
```

程序同时输出 DBC 已知 Window Signal、无 DBC bit 候选和指定未知 ID 的原始变化核验。

## 物理按钮与 App 通风交叉分析

详细文档：[compare_window_control_sources.md](doc/compare_window_control_sources.md)

```powershell
python src\compare_window_control_sources.py `
    input\驾驶门物理按钮开关窗采集脚本.txt `
    input\can_20260824175030.asc `
    input\can_车窗通风采集脚本.txt `
    input\can_20260824154441.asc `
    input\tesla_model3_ONYX.dbc
```

程序通过两个控制入口的共同运动响应，缩小车窗执行过程候选范围。

以后新增 Python 程序时，在 `doc` 目录创建与 Python 文件同名的 Markdown 文档：

```text
src/example.py
doc/example.md
```

同时在 `readme.md` 的相应程序章节加入该文档的链接。
