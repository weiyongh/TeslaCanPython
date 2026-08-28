# compare_window_control_sources.py

比较驾驶门物理按钮开关窗与 App 四窗通风，寻找两个控制入口共同触发的执行过程 CAN ID 和 bit。

```powershell
python src\compare_window_control_sources.py `
    input\驾驶门物理按钮开关窗采集脚本.txt `
    input\can_20260824175030.asc `
    input\can_车窗通风采集脚本.txt `
    input\can_20260824154441.asc `
    input\tesla_model3_ONYX.dbc
```

程序分别计算物理按钮和 App 运动窗口内外的 bit 翻转富集度，仅保留两份数据共有的候选，并输出 Markdown 报告和 CSV 明细。

共同候选更接近电机、编码器、速度、电流、位置或执行层校验字段；仍需进一步做字段组合和方向性验证。
