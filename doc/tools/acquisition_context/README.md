# Acquisition Context

该工具完成原始采集包的轻量Validation、确定性Resource整理、无UI人工审核和正式JSON回写；不解析CAN Payload，不进行DBC、Signal或Evidence分析。

## 使用

```sh
python3 src/tooling/acquisition_context.py prepare <Acquisition Package目录>
```

生成`acquisition_context_toreview.json`。AI读取其中的图片、Note和录音Resource，将原始识别Value写入对应`values`。

```sh
python3 src/tooling/acquisition_context.py render-review \
  output/acquisition_context/<采集包目录>/acquisition_context_toreview.json
```

生成`recog_values_review.md`。人工保留AI识别值和位置，填写人工确认值、审核状态及备注；完成后将Round表中的`Review Status`改为`APPROVED`。

```sh
python3 src/tooling/acquisition_context.py finalize \
  output/acquisition_context/<采集包目录>/acquisition_context_toreview.json \
  output/acquisition_context/<采集包目录>/recog_values_review.md
```

只有Review为`APPROVED`、没有`PENDING`、身份和来源文件未变化时，才生成正式`acquisition_context.json`。

## 输出关系

```text
acquisition_context_toreview.json  待审处理快照
recog_values_review.md             无UI人工审核界面
acquisition_context.json           Analysis正式输入
```

审核状态：`PENDING / ACCEPTED / CORRECTED / REJECTED / HUMAN_ADDED`。不同Resource的实际值分别保留，不平均、不覆盖。
