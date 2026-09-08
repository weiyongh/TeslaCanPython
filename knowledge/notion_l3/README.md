# Notion L3 本地镜像

本目录是 TeslaCanPython 对 Notion 正式 L3 学习库的只读工作镜像。

- Notion `新能源汽修L3学习` 正式分支是唯一人工维护的权威编辑源。
- `current/` 是最近一次成功同步并通过完整性检查的日常只读工作镜像。
- `snapshots/` 保存按同步时间冻结的完整历史版本。
- `snapshot_manifest.json` 记录当前成功同步的来源、路径、哈希与完整性状态。
- 页面权威性只按正式 ancestor path 判断：`新能源汽修L3学习/…` 为正式来源；`备份库/…`、`备份库/复制备份/…` 和历史 `(1)` 副本不得同步。
- Source Authority 不等于 Knowledge Maturity。正文中的 TODO、待审核、问题、FAQ、来源备注、待车型验证和实践记录必须保留，并继续按其原成熟度理解。
- ASCII Tree 的父子层级、兄弟关系、竖线、箭头和顺序不可破坏。
- Mermaid 必须保留状态、迁移、条件与分支；其中 `<br/>` 不得替换成 `\\n`。
- 本地 Markdown 不得独立修订 L3 技术知识。发现问题时应先报告并在 Notion 正式源修改，再按同步规范生成新 Snapshot。
- 更新流程遵循 [TeslaCanPython_Notion_L3_本地同步规范_v0.2.md](../../doc/methodology/TeslaCanPython_Notion_L3_本地同步规范_v0.2.md)。

普通 TM3 工作默认只读取 `current/` 中与当前任务有关的必要页面，不同时加载多个历史 Snapshot。

