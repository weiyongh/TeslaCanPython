# TM3-017 正式控制树写入一致性检查

**检查日期：** 2026-09-15

**状态：** `PASS`

**信息边界：** `STRICT_NO_DBC_RAW_PAYLOAD_ONLY`

**正式控制树：** `knowledge/notion_l3/current/充电系统/交流慢充/交流慢充.md`

## 一致性结果

| 检查项 | Approved Gate | 正式控制树 | 结果 |
| --- | --- | --- | --- |
| 新增Node | 外部设置、外部可观察接受状态，共2个 | 写入2个 | `PASS` |
| 既有Node/State增强 | `IAC_actual`、高压充电运行态 | 均增加TM3-017 Evidence | `PASS` |
| Condition | 同一连续高压充电运行态 | 已作为Relationship适用条件写入 | `PASS` |
| 未观测区域 | 设置接受与`IAC_actual`之间必须保留 | 已显式写入且禁止拆分命名 | `PASS` |
| Node分离约束 | 设置接受状态不得与实际响应合并 | 已写入E06-P01/P02依据 | `PASS` |
| 准入Relationship | TG-R01至TG-R04 | 全部写入，强度与边界一致 | `PASS` |
| raw簇正式准入 | 0个 | 0个；仅引用Evidence附件 | `PASS` |
| 内部Target/能力/仲裁/请求/执行新增 | 0个 | 0个 | `PASS` |
| 设置到`IAC_target`/`A₂`/`AEVSE`路径 | 不准入 | 未建立 | `PASS` |
| Signal语义/scale/unit/ECU | 不准入 | 未新增 | `PASS` |
| 新采集设计 | 禁止 | 未设计 | `PASS` |
| DBC使用 | 禁止 | 未读取、未引用、未使用 | `PASS` |

## Evidence数值核对

- 输入与设置接受序列：32→16→32 A，与Evidence Assessment及Gate一致。
- 页面实际交流电流序列：32→16→32 A，与Evidence Assessment及Gate一致。
- 页面功率序列：7→4→7 kW，与Evidence Assessment及Gate一致。
- 恢复中间态：E06-P01为设置32 A、实际21 A；E06-P02后实际32 A，与Node分离依据一致。
- 稳定窗口：W1 70.000 s、W2 117.505 s、W3 102.522 s，与Evidence Assessment一致。
- 适用边界：`TESLA-M3-SOP5`、S0030、SOC约85%至86%、本次EVSE及现场条件，与Approved Gate一致。

## 结论

正式控制树写入内容与已批准Tree Gate及本轮Evidence一致；没有增加Gate未批准的Node、Relationship、Condition或Signal语义。正式增量保持在系统输入—输出层，内部处理区域继续不可辨识。
