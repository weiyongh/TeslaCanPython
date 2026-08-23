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

以后新增 Python 程序时，在 `doc` 目录创建与 Python 文件同名的 Markdown 文档：

```text
src/example.py
doc/example.md
```

同时在 `readme.md` 的相应程序章节加入该文档的链接。
