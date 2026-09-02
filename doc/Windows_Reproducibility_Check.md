# Windows 跨平台复现检查

本文用于在一台未参与开发的 Windows 机器上，从 GitHub 仓库重新建立 TeslaCanPython 环境并复现 TM3-007 冻结输出。Windows 验证必须从 `git clone` 开始，不能复制 macOS 工作目录。

## 1. 基础环境

- 安装 Git for Windows。
- 安装 64 位 Python 3.12；本项目当前开发环境验证版本为 Python 3.12.2。
- clone 时保持 Git 默认配置即可；仓库 `.gitattributes` 已固定报告、普通文本fixture、JSON和源码为 LF，冻结输出CSV/machine evidence保留仓库原始字节，并将 ASC、ZIP 等证据输入按二进制处理。

在 PowerShell 中执行：

```powershell
git clone https://github.com/weiyongh/TeslaCanPython.git
Set-Location TeslaCanPython
git rev-parse HEAD
git status --short
```

预期：能够输出本次冻结提交 SHA，`git status --short` 无输出。

## 2. 创建隔离 Python 环境

```powershell
py -3.12 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python --version
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

预期：Python 显示 3.12.x，`cantools` 及其运行依赖安装成功。项目只声明直接依赖，不使用开发机环境的整包冻结文件。

## 3. 完整测试

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

预期：测试全部通过，包括 Renderer、Golden Contract、TM3-007 freeze/migration 和 TM3-009/010 Golden 回归。

## 4. 仅从既有证据复现 TM3-007

TM3-007 已冻结。本步骤只能运行共享 Renderer 入口，不得运行 `src/analyze_tm3_007.py`，也不得重新读取 ASC：

```powershell
python src/render_tm3_007.py
python -m unittest tests.test_tm3_007_report_migration tests.test_tm3_regression_outputs -v
git status --short
```

预期：

- `output/TM3-007/` 下四件套成功生成；
- Approved Signal 数量仍为 23；
- Evidence Assessment、Signal maturity 和 0x20A Validation 保持不变；
- 专项测试通过；
- 若 checkout 与冻结提交一致，重新渲染后 `git status --short` 仍无输出。

正式四件套为：

- `output/TM3-007/TM3-007_最终报告.md`
- `output/TM3-007/采集时间线与关键Signal.md`
- `output/TM3-007/DBC关键Signal覆盖与可读性.md`
- `output/TM3-007/工程审计.md`

确认 Approved 数量：

```powershell
(Import-Csv -Encoding UTF8 "output/TM3-007/evidence_plan_approved.csv").Count
```

预期输出：`23`。

## 5. SHA 与跨平台判定

```powershell
Get-FileHash -Algorithm SHA256 "output/TM3-007/TM3-007_最终报告.md"
Get-FileHash -Algorithm SHA256 "output/TM3-007/采集时间线与关键Signal.md"
Get-FileHash -Algorithm SHA256 "output/TM3-007/DBC关键Signal覆盖与可读性.md"
Get-FileHash -Algorithm SHA256 "output/TM3-007/工程审计.md"
```

四件套、TM3-009/010 Golden、Approved Plan及冻结测试明确保护的机器证据要求字节级一致。PowerShell显示格式、测试耗时、pip日志和本机临时路径只要求行为与语义一致，不纳入字节级比较。

TM3-007当前四件套冻结 SHA-256：

| 文件 | SHA-256 |
|---|---|
| `TM3-007_最终报告.md` | `f9d7b041e96c10b58c614cbb7b02e4c180b4658436aeec67275aa4c8a6b08f53` |
| `采集时间线与关键Signal.md` | `07a8220aa17157028cc2c2eb49fe4877d63a33c55c8290977e9cb661a1dc4145` |
| `DBC关键Signal覆盖与可读性.md` | `19724017e1dfaf1f50156ff8da285edbf93ab1e9b88365727ba556833d437569` |
| `工程审计.md` | `54506040e4c1d81723d47a7435620e9871c91d5dd7e8dbb0c4c586545bd64d98` |

## 6. Windows 验收结论

只有实际 Windows clone 满足以下全部条件，才可标记跨平台验证通过：clone和依赖安装成功、完整测试通过、Renderer入口不读ASC即可复现四件套、23项Approved和Assessment等冻结边界不变、字节级文件SHA一致、无Windows专属临时补丁。任何失败请保留完整PowerShell命令、错误输出、Python版本、`git rev-parse HEAD`和`git status --short`，返回开发侧分析。

## 7. macOS 提交前 clean verification

本节必须在 macOS 开发机执行；Windows 或应用内置 Python 的结果不能代替它：

```bash
git status --short --branch
git rev-parse HEAD
python3 --version
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 src/render_tm3_007.py
python3 -m unittest tests.test_tm3_007_report_migration tests.test_tm3_regression_outputs -v
git status --short
```

预期：Python 为3.12.x；所有测试通过；Renderer不读取ASC；重新生成后只有本轮有意修改的源码/文档出现在状态中，四件套不产生内容差异。提交后记录并推送 `git rev-parse HEAD` 的结果，Windows必须clone并验证同一提交。

## 8. 文件名、编码与故障日志

- 仓库包含中文文件名；Git for Windows、PowerShell和Python均按UTF-8路径处理，不要手工改成英文副本。
- 不要设置会覆盖仓库 `.gitattributes` 的换行规则。正式Markdown使用UTF-8/LF；冻结machine evidence CSV保留仓库中的原始字节。
- 若 `python` 打开Microsoft Store或不可执行，说明Python安装/launcher尚未完成。安装Python 3.12后关闭并重新打开PowerShell，再执行 `py -3.12 --version`；不要修改项目代码绕过环境问题。
- 失败回传至少包含：`git rev-parse HEAD`、`git status --short`、`py -3.12 --version`、失败命令完整输出，以及四件套的 `Get-FileHash` 结果。
