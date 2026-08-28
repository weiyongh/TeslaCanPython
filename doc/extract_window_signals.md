# extract_window_signals.py

该程序根据标准采集脚本，从 ASC 中提取 DBC 已命名的 Window Signal，并将变化与通风、关闭动作对应。

## 使用

```powershell
python src\extract_window_signals.py `
    input\can_车窗通风采集脚本.txt `
    input\can_20260824154441.asc `
    dbc\tesla_model3_ONYX.dbc.txt
```

输入顺序与 `extract_scripted_signals.py` 相同：采集脚本、ASC、DBC。

## 输出

默认在 `output` 生成：

- `*_Window关键步骤信号报告.md`
- `*_Window关键步骤信号明细.csv`
- 存在候选时，生成排名第一 Message 的 Window Signal 状态追踪文件

报告和 CSV 的候选排名、关键步骤数据表与 `extract_scripted_signals.py` 一致，并额外列出 Window Message 的 DBC/ASC DLC、覆盖情况和静态 Signal。

## DLC 修正

当前 ONYX DBC 的部分 Message 存在长度矛盾。例如 `UI_vehicleControl2` 声明为 2 字节，但 `UI_windowRequest` 位于 bit 20，且实车 ASC 的 DLC 为 8。

程序仅在 ASC 实际 DLC 足够时，将解码长度扩大到实际 DLC。该处理只修正解码边界，不改变 Signal 的起始位、长度、字节序、比例和偏移。

## 限制

- 只处理 Signal 名称包含 `window` 的字段。
- DBC 未收录的 ID 不会被命名或加入 DBC 候选排名。
- Signal 未变化不代表它无关，也可能是请求未经过当前采集总线。
- DBC 与车型或软件版本不匹配时，名称仍需实车验证。
