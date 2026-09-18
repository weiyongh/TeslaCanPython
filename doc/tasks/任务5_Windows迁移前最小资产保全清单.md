# 任务5：Windows迁移前最小资产保全清单

**状态：** `BACKLOG / APPROVED / 未启动`  
**记录日期：** 2026-09-14  
**服务目标：** Mac暂时不可用后，当前有效工作仍能在Windows继续。  
**原则：** 只保护“不可重建且当前需要”的资产；不开展全局工程治理、统一Git状态或完整Mac环境复制。

## 一、必须Git固化

### TeslaCanPython

- 今天更新的HVAC正式Knowledge Snapshot及Manifest；
- 当前总部任务视图和班吉迁移待办；
- 伯恩持续困境与叶问异常激活建议机制；
- 在`AGENTS.md`补入“采集目的不决定最终资产身份”的最小长期规则；
- 修订叶问现有方法文档，将其明确为第二条独立Signal Reverse路线；
- 形成可恢复检查点并推送到有效远端。

不因迁移完整文档化今天全部对话。无法确认用途、能够从其他项目重建的重复文件不自动纳入。

### 伯恩

- Round 4采集脚本、执行次数说明和当前`work/round_4/`有效状态；
- 最新HVAC Knowledge Snapshot；
- Round 3已关闭结果继续可读；
- 形成Round 4启动前检查点。

伯恩当前远端跟踪分支已失效；实施时须恢复有效私有远端并推送，或创建完整Git Bundle随迁移介质保存。

### 叶问

- 当前Challenge题面、获准输入边界、分析程序、报告和Hit Points；
- 形成首个Clean Room检查点；
- 不引入总部答案、伯恩候选或DBC Truth。

叶问当前尚无Commit且远端跟踪分支已失效；实施时须恢复有效私有远端并推送，或创建完整Git Bundle。

### 罗格

- 固化远端`0.1.4`之后已经验证的有效成果，包括App状态接口、`vcan0`、Web开发模式、共享CGI逻辑、README、开发记录和项目共识；
- 只形成可恢复检查点，不借机重构或整理成完整发布版；
- 推送到有效远端。

## 二、必须单独复制

- 今天新采集的伯恩HVAC Round 4完整原始包：Vehicle Marker、ASC、`session.json`、`event_timeline.csv`、照片、Note、录音、实际脚本和偏差记录；
- 伯恩Round 4实际引用但未进入Git的必要历史HVAC实验数据，不横向复制整个`experiment_vault`；
- 叶问当前Challenge实际依赖、未进入Git的大体积Clean Room输入；
- 罗格一份已经验证可用的最小Golden Replay及哈希；
- 近期确实可能分析的总部采集包，不复制全部历史ASC；
- GitHub、Codex和树莓派等访问材料通过安全方式迁移，密码、Token和私钥不得进入项目文件。

单独复制的数据保留原目录结构，并生成文件清单和SHA-256。

## 三、可以不迁移

- `.venv/`、`__pycache__/`和其他Python缓存；
- Android SDK、Gradle缓存、`build/`和可重新生成的APK；
- 编辑器、LSP、下载缓存和`.DS_Store`；
- 临时日志及可由源码重新生成的Preview或分析输出；
- Windows、Android和USB设备驱动安装缓存；
- 整个Mac用户目录；
- 与近期任务无关的全部历史ASC；
- 今天对话的逐字备份。

班吉当前源码由TeslaCanPython Git历史承载，实施时不复制整个Android构建目录。

## 四、Windows端最小验收

### 工作区恢复

- TeslaCanPython、伯恩、叶问和罗格均能从有效远端或Git Bundle恢复；
- 检查点Commit SHA与Mac记录一致；
- 没有意外缺失当前工作文件，叶问Clean Room边界未被污染。

### TeslaCanPython

- 能读取当前总部任务视图和最新HVAC Knowledge Snapshot；
- 新建Windows Python环境并安装当前实际需要的依赖；
- 运行一组Acquisition Plan、Validation/Recognition或基础ASC解析相关测试；
- 能读取一份ASC、DBC、JSON、CSV和图片。

### 伯恩

- 能恢复Round 4状态并读取新Acquisition Package；
- 当前Reverse分析入口能够运行并生成测试输出；
- 原始数据与结果目录关系没有断裂。

### 叶问

- 能从Clean Room工作区启动并读取获准Challenge输入；
- 分析脚本至少完成输入解析；
- 伯恩结果和总部Truth对其保持不可见。

### 罗格

- Windows能查看和编辑罗格仓库；
- 能通过SSH连接树莓派并访问罗格Web页面；
- 能使用最小回放样本完成一次`vcan0`验证，或读取树莓派已生成日志；
- 不要求Linux采集核心在原生Windows运行。

### 数据完整性

- 单独复制文件的数量和SHA-256与清单一致；
- Round 4的ASC、JSON、CSV、照片和录音可打开；
- 至少一个采集包能够被总部工具识别。

## 五、完成判据

```text
四个工作区存在可恢复检查点
+ 近期不可重建数据有独立副本和哈希
+ Windows能够恢复并打开这些资产
+ 总部、伯恩、叶问、罗格各通过一次最小工作验证
```

未收到导演明确启动指令前，不执行本清单。
