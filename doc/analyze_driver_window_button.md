# analyze_driver_window_button.py

该程序用于分析驾驶门物理按钮开关窗采集，同时保留两条证据链：

1. 使用 DBC 解码名称含 `window` 的已知 Signal，验证物理按钮输入。
2. 无 DBC 分析所有 CAN ID 的稳定状态和动作响应，并额外完整核验指定未知 ID。

## 使用

```powershell
python src\analyze_driver_window_button.py `
    input\驾驶门物理按钮开关窗采集脚本.txt `
    input\can_20260824175030.asc `
    input\tesla_model3_ONYX.dbc `
    --verify-id 0x1FA
```

默认输出：

- `*_驾驶窗按钮混合分析报告.md`
- `*_驾驶窗DBC信号明细.csv`
- `*_驾驶窗未知bit候选.csv`
- `*_驾驶窗执行过程候选.csv`：按下按钮后，活动显著集中在玻璃运动窗口的 ID/bit
- `*_0x1FA_原始变化追踪.txt`
- 存在 DBC 候选时，排名第一 Message 的完整变化追踪

## 判读

DBC 候选用于确认按钮请求属于哪个 Signal。未知 bit 候选用于寻找车窗位置、运动状态或汇总状态。指定 ID 无论是否存在 DBC 定义都会被输出，脚本状态与实测 Payload 不一致时也会保留原始证据。

执行过程分析从每次按钮按下延伸到下一稳定状态记录，比较窗口内外的 bit 翻转率，并降低等周期字段权重。高富集候选可能来自电机、编码器、速度、电流或相关校验字段，仍需后续字段宽度和方向性验证。
