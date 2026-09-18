我要迁移到windows工作，有哪些值得注意的事项，我已经整个目录提交到了github。首次在windows codex打开怎么说

8:34

用时 1分钟 23秒

可以迁移，而且仓库当前已经具备较完整的 Windows 复现说明。建议在 Windows 上使用“重新 `git clone`”，不要直接复制 Mac 工作目录。

你当前的迁移基线状态：

- 分支：`main`
- 当前提交：`1690c29`
- 本地与 `origin/main` 一致
- 工作区无未提交修改
- Git 跟踪文件约 1.12 GiB
- 当前没有发现 Windows 大小写冲突、非法文件名或符号链接
- `.venv`、Gradle 缓存、构建目录不会提交，需要在 Windows 重建
- `.downloads` 有约 6.4 GiB，但已被忽略，不会随 GitHub 迁移

## Windows 上建议这样做

在 PowerShell 中：

```
git clone https://github.com/weiyongh/TeslaCanPython.git
Set-Location TeslaCanPython

git rev-parse HEAD
git status --short
```

应看到提交 `1690c29` 或更新提交，并且 `git status --short` 没有输出。

然后建立 Python 环境：

```
py -3.12 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

python --version
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m unittest discover -s tests -p "test_*.py" -v
```

仓库已经有专门的 Windows 验证说明：[Windows_Reproducibility_Check.md](/Users/hwy/codex_work/TeslaCanPython/doc/Windows_Reproducibility_Check.md)。

## 值得特别注意

1. 不要复制 Mac 的 `.venv`

Windows 应重新创建 `.venv`。Windows 的 Python 路径是：

```
.\.venv\Scripts\python.exe
```

不是项目文档里常见的：

```
.venv/bin/python
```

以后新增复现命令，最好统一写成：

```
python src/xxx.py
```

前提是已经激活虚拟环境。

1. 不要批量转换换行符

仓库的 [.gitattributes](/Users/hwy/codex_work/TeslaCanPython/.gitattributes) 已经规定：

- Python、Markdown、JSON、普通 CSV 使用 LF；
- ASC、ZIP、图片按二进制处理；
- 部分冻结机器证据保留原始字节；
- `.bat` 使用 CRLF。

不要运行“统一全仓库 CRLF”之类的工具，否则可能破坏黄金回归样本（Golden Regression Samples）的哈希。

1. 中文路径不需要改名

仓库没有发现 Windows 非法文件名。建议：

- Windows、Git、PowerShell 使用 UTF-8；
- 不要给中文文件另建英文副本；
- 尽量克隆到较短路径，例如：

```
D:\work\TeslaCanPython
```

不要放在层级很深的 OneDrive 目录下，避免 Windows 路径长度和同步锁定问题。

1. GitHub 并不等于“整台 Mac 的目录都迁移了”

以下本机内容没有提交：

- `.venv/`
- `.downloads/`
- Android `.gradle/`
- Android `build/`
- `local.properties`
- Codex 本机配置和旧会话
- 未纳入仓库的账号授权、密钥、插件连接

尤其是 Codex 旧聊天上下文不会因为 GitHub 自动迁移；真正可迁移的长期上下文是 `AGENTS.md`、项目状态文档及仓库产物。

1. 当前管线不要误继续

当前正式状态是：

- TM3-015 当前运行位于
  `output/TM3-015/pipeline_v3/20260908-phase3b2_3-context-replay-v5/`
- 状态为 `AWAITING_EVIDENCE_REVIEW`
- 不得自动生成批准证据、Evidence Assessment、RVM 或正式四件套
- Phase 3B.2.6A 尚未获得授权

所以首次打开时应先让 Codex 做只读接管审计，不要直接让它“继续项目”。

1. 注意 GitHub 隐私

仓库包含 ASC、照片、音频和车辆实验材料。请确认仓库可见性符合你的预期。若敏感文件曾经提交，即使后来删除，也可能仍存在于 Git 历史中。

1. Android 子项目

Windows 上用 Android Studio 打开：

```
android\CANVoiceRunner
```

不要打开仓库根目录作为 Android 工程。然后：

```
Set-Location android\CANVoiceRunner
.\gradlew.bat testDebugUnitTest assembleDebug
```

需要重新生成 `local.properties`，不要提交它。

## 首次在 Windows Codex 打开后这样说

建议直接复制下面这段：

```
这是 TeslaCanPython 项目从 macOS 迁移到 Windows 后的首次接管。本次只做环境与项目状态核对，不修改源码、文档、冻结产物或Git历史，也不要启动新的ASC分析。

请先完整阅读并遵守根目录 AGENTS.md，然后依次阅读：
1. doc/PROJECT_CURRENT_STATUS.md
2. L3新能源实车数据诊断分析规范_v1.1.md
3. doc/Windows_Reproducibility_Check.md
4. 根据上述文件明确要求，再读取当前任务必需的方法文档；不要遍历全部ASC和全部历史输出。

请执行只读检查并向我汇报：
1. 当前Windows路径、Git分支、HEAD提交和git status；
2. input、output、src、dbc、doc、knowledge/notion_l3/current、android/CANVoiceRunner是否完整；
3. Python版本、虚拟环境状态和requirements.txt依赖是否可用；
4. 是否存在macOS绝对路径、.venv/bin/python、/tmp、AppleScript或其他Windows不兼容入口；
5. 当前正式Pipeline入口、权威运行目录、当前状态门和禁止越过的人工审核门；
6. TM3-009、TM3-010、TM3-015的Golden保护边界；
7. Windows下建议使用的等价PowerShell命令；
8. 完整测试和TM3-007冻结复现是否能够执行。

当前已知基线：main分支，迁移时提交为1690c29；如实际HEAD更新，请以git结果为准并报告差异。TM3-015当前应处于AWAITING_EVIDENCE_REVIEW，不得自动批准Evidence Mapping，不得生成Evidence Assessment、RVM或正式报告。

先完成检查并给我一份“Windows接管报告”。发现问题只提出最小修改建议，未经我明确同意不要修改。
```

这段提示词最适合第一次接管：它会让 Windows Codex 先建立准确上下文，同时防止它误读 ASC、重写冻结输出或越过 TM3-015 的人工审核门。

8:36