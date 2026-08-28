# 事件驱动 CAN 候选 ID 遴选

`select_can_candidates.py` 使用采集脚本中的时间点，从原始 ASC 中盲选候选
CAN ID、Byte 和 Bit。DBC 是可选输入，只标记已知 Message，不参与盲分数。

## 单一 profile

```powershell
python src\select_can_candidates.py `
    input\can_20260824175030.asc `
    input\驾驶门物理按钮开关窗采集脚本.txt `
    --profile window `
    --pre-offset 0.5 `
    --post-offset 1.0 `
    --min-blind-score 60 `
    --dbc dbc\特斯拉左侧车窗_DBC_EXP.dbc
```

## 复合 profile

`--profile` 可以重复使用，也可以使用逗号分隔。各 profile 独立评分，最终按
CAN ID 取并集；报告和 CSV 会保留每条候选的来源。

```powershell
python src\select_can_candidates.py `
    input\can_20260824175030.asc `
    input\驾驶门物理按钮开关窗采集脚本.txt `
    --profile generic-event `
    --profile window `
    --pre-offset 0.5 `
    --post-offset 1.0 `
    --dbc dbc\特斯拉左侧车窗_DBC_EXP.dbc
```

当前 profile：

- `generic-event`：寻找多个事件时间附近重复变化、背景变化较少的 bit。
- `window`：增加车窗稳定状态、瞬时请求和运动过程特征。

`window` 不以全部脚本时间点作为统一分母，而是分别评分：

- “记录”生成的全关、部分开启、全开稳定窗口；
- 按方向、手动/自动、触发/松开划分的按钮事件子组；
- 从动作开始到下一稳定记录的完整运动窗口。

按钮事件采用角色内0～100分，由事件覆盖率、时间接近度、窗口内外活动富集和
背景纯净度组成。例如“上升按钮 bit”只以上升事件为分母，不会因为没有响应下降
事件而被扣分。

## 输出命名

ASC 是所有工作的根。默认输出前缀为：

```text
<ASC文件名>_<执行时间戳>
```

例如：

```text
can_20260824175030_20260826_143015_候选分析报告.md
can_20260824175030_20260826_143015_候选ID汇总.csv
can_20260824175030_20260826_143015_候选ByteBit明细.csv
can_20260824175030_20260826_143015_事件矩阵.csv
can_20260824175030_20260826_143015_SavvyCAN事件窗口.asc
```

事件窗口 ASC 保留原始时间戳，只包含排名靠前的候选 ID 及事件前后窗口，便于
直接加载 SavvyCAN 做 Frame Data Analysis 和 Flow View 人工复核。
事件矩阵中的单元格使用“变化 bit 数/总翻转次数”，既显示变化覆盖范围，也避免
把一个高频变化字段误读成多个独立 Signal。

## 主要参数

| 参数 | 含义 | 默认值 |
|---|---|---:|
| `--profile` | 可重复或逗号分隔的分析 profile | `generic-event` |
| `--pre-offset` | 事件前窗口，秒 | `0.5` |
| `--post-offset` | 事件后窗口，秒 | `1.0` |
| `--dbc` | 可选 DBC，只辅助标记 | 无 |
| `--top` | 汇总及 SavvyCAN 切片保留的 ID 数 | `30` |
| `--min-blind-score` | 候选综合盲分下限，低于该值不输出 | `60` |
| `--output-dir` | 输出目录 | `output` |

盲分阈值统一作用于报告、候选 ID/Byte.Bit CSV、事件矩阵和 SavvyCAN 事件窗口
ASC。需要观察较弱候选时可以显式降低，例如 `--min-blind-score 40`。

复合 profile 的汇总以各来源最高盲分为主体，只对命中多个 profile 的证据广度
给小幅奖励，避免把不同量纲的评分直接相加。
