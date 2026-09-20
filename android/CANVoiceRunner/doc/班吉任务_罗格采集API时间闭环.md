# 班吉任务：罗格采集 API 时间闭环

## 目标

班吉（VoiceRunner）是罗格（Rogue / PiCanLog）Web API 的请求方。

本次只完成 Start / Stop API 的时间证据闭环，并保存必要记录。

---

## 先确认当前实现

开始修改前，先简短回答：

1. `script_name` 含中文时，当前 Android / HTTP 请求使用什么字符编码？
2. Rogue JSON response 当前按什么字符编码接收和解析？
3. VoiceRunner 导出的 CSV 使用什么字符编码？
4. 当前 `clock_epoch_ms` 的：
   - 数据类型
   - 单位
   - 格式
   - 示例值

不要先改变现有编码方案，先说明当前实际实现。

---

## START

发出 START 请求前立即取得班吉本地 Unix 时间：

```text
benji_start_request_epoch_ms
```

START 请求参数：

```text
script_name
session_id
benji_start_request_epoch_ms
```

Rogue START response 预期包含：

```json
{
  "ok": true,
  "script_name": "...",
  "session_id": "...",
  "log_filename": "...",
  "rogue_start_request_received_epoch_ms": 0,
  "rogue_dump_start_epoch_ms": 0
}
```

要求：

1. 完整保存 Rogue START response 原始 JSON。
2. HTTP response 到达班吉后立即取得：

```text
benji_start_response_epoch_ms
```

该时间应尽量在 JSON 解析、文件写入、UI 更新等后续处理之前取得。

---

## STOP

发出 STOP 请求前立即取得：

```text
benji_stop_request_epoch_ms
```

STOP 请求参数：

```text
script_name
session_id
benji_stop_request_epoch_ms
```

Rogue STOP response 预期包含：

```json
{
  "ok": true,
  "script_name": "...",
  "session_id": "...",
  "log_filename": "...",
  "rogue_stop_request_received_epoch_ms": 0,
  "rogue_dump_stop_epoch_ms": 0
}
```

要求：

1. 完整保存 Rogue STOP response 原始 JSON。
2. HTTP response 到达班吉后立即取得：

```text
benji_stop_response_epoch_ms
```

---

## CSV

现有 Event CSV 保持原有内容。

增加本次采集的时间证据信息，至少保留：

```text
script_name
session_id
log_filename

benji_start_request_epoch_ms
rogue_start_request_received_epoch_ms
rogue_dump_start_epoch_ms
benji_start_response_epoch_ms

benji_stop_request_epoch_ms
rogue_stop_request_received_epoch_ms
rogue_dump_stop_epoch_ms
benji_stop_response_epoch_ms
```

不要用计算后的时间覆盖任何原始时间。

---

## 必要日志

本次至少保留：

```text
Rogue START response 原始 JSON
Rogue STOP response 原始 JSON
API 请求失败 / Rogue 返回错误时的错误信息
```

两个 Rogue response JSON 必须能够与本次 `script_name + session_id` 对应。

不需要增加复杂审计日志。

---

## 边界

- 班吉保留自己的原始 Unix 时间。
- Rogue 返回的 Unix 时间原样保存。
- 不在本轮做时钟校准。
- 不修改原始 Event `clock_epoch_ms`。
- 不在本轮计算或修正 CAN 时间。
- 不扩展其他功能。

本轮目标只是把班吉 ↔ Rogue 的 Start / Stop 原始时间证据完整留下。
