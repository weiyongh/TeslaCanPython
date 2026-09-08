# TeslaCanPython --- Notion L3 本地同步规范 v0.2

> **文档性质**：长期同步规范 / Knowledge Snapshot Contract\
> **版本**：v0.2\
> **适用工程**：TeslaCanPython\
> **固定本地根目录**：`/Users/hwy/codex_work/TeslaCanPython/knowledge/notion_l3/`\
> **工程相对路径**：`knowledge/notion_l3/`\
> **权威编辑源**：Notion `新能源汽修L3学习` 正式分支\
> **日常工作知识源**：`knowledge/notion_l3/current/`

------------------------------------------------------------------------

# 1. 目标

将 Notion 中已经稳定的 L3 正式知识，以 Markdown 为主格式忠实镜像到
TeslaCanPython 本地工程，使 Codex 在日常 TM3
工作中优先读取本地知识，不必频繁访问 Notion。

本规范同时提供：

-   固定本地存放位置；
-   `current` 日常工作副本；
-   按同步时间保存的历史 Snapshot；
-   正式 Notion 来源判定规则；
-   Markdown / ASCII Tree / Mermaid 保真规则；
-   Knowledge Maturity 边界；
-   最小 manifest 和同步报告；
-   后续重复更新的统一执行流程。

本任务不是知识重写、知识库重构或同步平台建设任务。

------------------------------------------------------------------------

# 2. 核心架构

``` text
Notion
新能源汽修L3学习
= 唯一人工维护的权威 L3 编辑源
          │
          │ 用户明确要求更新时
          ▼
Codex 只读同步
          │
          ▼
knowledge/notion_l3/
│
├─ current/
│  └─ 最近一次成功同步的正式 L3
│
├─ snapshots/
│  └─ YYYY-MM-DD_HHMMSS/
│     └─ 当时的完整正式 L3
│
├─ snapshot_manifest.json
└─ README.md
```

日常 TeslaCanPython 工作：

``` text
Project Context
      ↓
knowledge/notion_l3/current/
      ↓
按当前 case 获取必要 L3 Working Context
      ↓
ASC / DBC / Script / Evidence / Analysis
```

普通 TM3 case 不应因此再次访问实时 Notion。

------------------------------------------------------------------------

# 3. 固定本地存放目录

## MUST

所有 Notion L3 本地镜像必须存放于：

``` text
/Users/hwy/codex_work/TeslaCanPython/knowledge/notion_l3/
```

工程内统一使用相对路径：

``` text
knowledge/notion_l3/
```

除非用户以后明确修改该约定，Codex 不得自行选择其他知识目录。

不得把 L3 镜像散落到：

-   `input/`
-   `output/`
-   `doc/`
-   TM3 case 目录
-   临时目录
-   用户 Home 下其他目录

------------------------------------------------------------------------

# 4. 固定目录结构

``` text
TeslaCanPython/
└─ knowledge/
   └─ notion_l3/
      │
      ├─ README.md
      ├─ snapshot_manifest.json
      │
      ├─ current/
      │  ├─ L3学习库说明.md
      │  ├─ L3学习主框架.md
      │  │
      │  ├─ 电驱动系统/
      │  │  └─ 电驱动系统.md
      │  │
      │  ├─ 动力电池系统/
      │  │  ├─ 动力电池系统.md
      │  │  └─ 动力电池状态变量表.md
      │  │
      │  ├─ 充电系统/
      │  │  ├─ 充电系统.md
      │  │  ├─ 直流快充/
      │  │  │  ├─ 直流快充.md
      │  │  │  └─ 直流快充通信控制器、BMS 与车桩通信关系.md
      │  │  └─ 交流慢充/
      │  │     └─ 交流慢充.md
      │  │
      │  └─ L3系统诊断基础语义/
      │     └─ 七个控制概念与Evidence.md
      │
      └─ snapshots/
         ├─ YYYY-MM-DD_HHMMSS/
         │  └─ <与当时正式 Notion ancestor tree 对应的完整 Markdown 树>
         └─ ...
```

这里展示的是当前结构基线。

如果以后正式 Notion ancestor tree 新增、删除或移动页面：

> **以实时正式 Notion
> 结构为准更新本地镜像，不以本文件中的旧目录示例强行覆盖实时结构。**

------------------------------------------------------------------------

# 5. Notion 正式来源

正式根：

``` text
新能源汽修L3学习
```

当前已经核实的正式结构：

``` text
新能源汽修L3学习
├─ L3学习库说明
├─ L3学习主框架
├─ 电驱动系统
├─ 动力电池系统
│  └─ 动力电池状态变量表
├─ 充电系统
│  ├─ 直流快充
│  │  └─ 直流快充通信控制器、BMS 与车桩通信关系
│  └─ 交流慢充
└─ L3系统诊断基础语义
   └─ 七个控制概念与Evidence
```

------------------------------------------------------------------------

# 6. Authority Resolution Rule

Notion 页面是否属于正式 L3，不以标题相似度判断。

优先级：

``` text
正式 ancestor path
>
页面标题相似度
>
全局搜索排名
```

正式来源：

``` text
新能源汽修L3学习 / …
```

非正式 / 历史来源：

``` text
备份库 / …
备份库 / 复制备份 / …
```

即使全局搜索返回：

``` text
动力电池系统
动力电池系统 (1)
交流慢充
交流慢充 (1)
```

也必须根据 ancestor path 判断，而不是根据标题选择。

## MUST NOT

-   不得将备份库同步进 `current/`；
-   不得用搜索排名最高的副本替代正式页面；
-   不得因为标题完全一致就忽略 ancestor path；
-   不得把历史副本与正式内容合并。

------------------------------------------------------------------------

# 7. Notion 是唯一人工维护权威源

``` text
Notion 正式 L3
= Authoritative Knowledge Source

Local Markdown
= Read-only Working Snapshot
```

Codex 不得在：

``` text
knowledge/notion_l3/current/
```

或：

``` text
knowledge/notion_l3/snapshots/
```

独立修改 L3 技术知识并形成第二套版本。

如果日常工作发现 L3：

-   有错误；
-   需要修订；
-   缺少内容；
-   TODO 已经可以解决；
-   待审核内容需要转正；

应向用户报告。

正式修改应先发生在 Notion，然后执行一次新的同步。

------------------------------------------------------------------------

# 8. Markdown 是正文主格式

原则：

> **一个正式 Notion 页面原则上对应一个 `.md` 文件。**

目录结构应镜像 Notion ancestor path。

Markdown 应尽可能忠实保存：

-   页面标题；
-   heading 层级；
-   正文；
-   列表；
-   表格；
-   Code Block；
-   ASCII Tree；
-   Mermaid；
-   TODO；
-   待审核；
-   问题；
-   FAQ；
-   来源备注；
-   车型待验证内容；
-   其他具有知识意义的纯文本。

不得为了 AI 使用将正文整体转换为：

-   JSON；
-   YAML；
-   数据库记录；
-   自动 Ontology；
-   Knowledge Graph。

JSON 只用于 manifest 等机器元数据。

------------------------------------------------------------------------

# 9. Faithful Snapshot 原则

同步必须执行：

``` text
Notion
↓
忠实读取
↓
格式保真
↓
Markdown Snapshot
```

不得执行：

``` text
Notion
↓
Codex理解
↓
Codex总结
↓
Codex润色
↓
“AI友好版 L3”
```

## MUST NOT

同步过程中不得：

-   总结正文；
-   改写技术表述；
-   润色；
-   自动纠错；
-   合并重复观点；
-   删除看似不重要内容；
-   使用 Codex 自己的知识补写缺失部分；
-   将待确认内容改成确定结论。

------------------------------------------------------------------------

# 10. ASCII Tree 是语义结构

L3 中大量使用 ASCII Tree。

例如：

``` text
A
│
├─ B
│  ├─ B1
│  └─ B2
│
└─ C
```

这些字符不是装饰：

``` text
│
├─
└─
↓
```

它们可能表达：

-   父子层级；
-   兄弟关系；
-   分支归属；
-   顺序；
-   控制推进；
-   前置条件；
-   诊断展开；
-   能量路径；
-   时间关系。

同步时必须保持：

-   原始节点顺序；
-   父子层级；
-   兄弟节点；
-   竖线连续性；
-   `├─ / └─`；
-   `↓`；
-   原始文本内容。

优先使用：

```` markdown
```text
<原始 ASCII Tree>
```
````

不得让 formatter 自动破坏树结构。

------------------------------------------------------------------------

# 11. Mermaid 是状态模型

Mermaid 代码必须尽可能原样保存：

```` markdown
```mermaid
<原始 Mermaid>
```
````

不得只提取 State 名称而丢失：

-   Transition；
-   Direction；
-   Transition Condition；
-   Branch；
-   Normal Path；
-   Recovery；
-   Termination Path。

Notion L3 Mermaid 的换行约定：

``` text
<br/>
```

必须保留。

不得擅自替换为：

``` text
\n
```

------------------------------------------------------------------------

# 12. Knowledge Maturity Rule

**正式页面 ≠ 页面内每句话都是成熟知识。**

正式 L3 页面内部可能包含：

``` text
TODO
待审核
问题
FAQ
chatgpt:
来源备注
待车型验证
实践记录
```

这些成熟度标记必须保留。

必须区分：

``` text
Source Authority
        ≠
Knowledge Maturity
```

因此：

``` text
新能源汽修L3学习/充电系统/交流慢充
```

可以是正式 Knowledge Source；

但其中一个：

``` text
TODO
```

仍然只是 TODO。

Codex 不得因为页面来源正式，就把 TODO 自动当成 Approved L3 Fact。

------------------------------------------------------------------------

# 13. Front Matter

每个 `.md` 可增加最小 front matter。

建议：

``` yaml
---
source: notion
source_root: 新能源汽修L3学习
source_path: 新能源汽修L3学习/充电系统/交流慢充
snapshot_time: 2026-09-08T19:30:00+08:00
authority: official
sync_mode: faithful_snapshot
---
```

如果 Notion 能可靠提供，可增加：

``` yaml
source_page_id: ...
source_last_edited_time: ...
```

Front matter 只记录 provenance，不得替代正文。

------------------------------------------------------------------------

# 14. README.md

固定位置：

``` text
knowledge/notion_l3/README.md
```

README 说明整个本地镜像机制，而不是某个 Snapshot。

至少说明：

``` text
1. Notion 是唯一权威编辑源
2. current/ 是日常只读工作镜像
3. snapshots/ 是历史版本
4. snapshot_manifest.json 描述当前同步状态
5. 正式 ancestor path 规则
6. Knowledge Maturity 规则
7. ASCII Tree / Mermaid 结构不可破坏
8. 更新必须遵循本规范
```

README 不复制 Domain 正文。

------------------------------------------------------------------------

# 15. Snapshot

历史版本目录：

``` text
knowledge/notion_l3/snapshots/YYYY-MM-DD_HHMMSS/
```

命名使用实际同步时间，例如：

``` text
2026-09-08_193000
```

含义：

> 在该时间点，从 Notion 正式 L3 ancestor tree
> 成功读取并保存的完整知识快照。

Snapshot 必须是完整版本，而不是仅保存变化文件。

------------------------------------------------------------------------

# 16. current

固定位置：

``` text
knowledge/notion_l3/current/
```

定义：

> 最近一次成功完成并通过完整性检查的正式 L3 Snapshot。

Codex 日常工作默认只使用：

``` text
current/
```

而不是：

``` text
snapshots/
```

历史 Snapshot 只有在以下任务才读取：

-   历史版本比较；
-   旧 TM3 case 回放；
-   Knowledge provenance；
-   用户明确要求查看旧版。

不得让多个 Snapshot 同时进入普通 LLM Working Context。

------------------------------------------------------------------------

# 17. Snapshot 更新事务边界

更新流程：

``` text
读取实时正式 Notion
        ↓
核实 ancestor tree
        ↓
创建新的 timestamp Snapshot
        ↓
逐页导出 Markdown
        ↓
结构与完整性检查
        ↓
生成 manifest
        ↓
PASS ?
├─ NO → 保留旧 current，报告 PARTIAL / FAILED
└─ YES
    ↓
更新 current
    ↓
Completion Report
    ↓
STOP
```

## MUST

在新 Snapshot 完整性验证成功前：

> 不得删除、清空或破坏现有 `current/`。

同步失败必须保持旧 current 可继续使用。

------------------------------------------------------------------------

# 18. snapshot_manifest.json

固定位置：

``` text
knowledge/notion_l3/snapshot_manifest.json
```

至少记录：

``` json
{
  "snapshot_time": "...",
  "snapshot_path": "knowledge/notion_l3/snapshots/...",
  "source_root": "新能源汽修L3学习",
  "authority_rule": "official_ancestor_path_only",
  "sync_mode": "faithful_snapshot",
  "status": "complete",
  "documents": []
}
```

每个 document 至少记录：

``` text
title
source_path
local_path
authority
```

如果成本很低，可增加：

``` text
source_page_id
source_last_edited_time
sha256
```

这些增强字段不是建立复杂同步框架的理由。

------------------------------------------------------------------------

# 19. 更新差异

第二次及以后同步应提供简单变化摘要：

``` text
新增页面
删除页面
ancestor path 变化
内容变化页面
未变化页面
```

优先使用：

-   Git diff；
-   SHA256；
-   文件比较；

等确定性方式。

不要自动对差异做大规模语义解释，除非用户要求。

------------------------------------------------------------------------

# 20. 普通 TM3 工作如何读取 L3

同步机制的目的不是把整个 L3 塞给每次分析。

例如直流快充：

``` text
Project Context
+
L3学习主框架
+
七个控制概念与Evidence
+
充电系统
+
直流快充
+
必要正式子页
+
必要邻接 Domain
```

交流慢充类似。

原则：

> **Knowledge Source ≠ Working Context ≠ LLM Payload。**

`current/` 是本地 Knowledge Source。

具体 case 只读取完成任务所需的 Working Context。

最终 LLM Payload 仍应根据当前分析任务形成可审计的必要输入。

------------------------------------------------------------------------

# 21. Notion 访问策略

完成首次本地同步后：

## 默认不访问 Notion

普通 TM3：

-   数据采集；
-   ASC 分析；
-   DBC 分析；
-   Evidence Mapping；
-   报告；
-   Control Tree 实例化；

优先使用 `current/`。

## 只有以下情况访问 Notion

-   用户明确要求"更新本地 L3"；
-   用户说明 Notion 已发生重要修改；
-   current 缺少当前必需知识；
-   用户明确要求核实实时 Notion；
-   发现本地版本可能已经过期且影响当前判断。

不得为了"保险"在每个任务开始时重复读取 Notion。

------------------------------------------------------------------------

# 22. v0.2 明确不建设的内容

本规范不要求：

-   自动定时同步；
-   后台监控 Notion；
-   双向同步；
-   自动写回 Notion；
-   复杂增量同步；
-   Knowledge Graph；
-   RAG Framework；
-   Vector DB；
-   Notion 数据库镜像；
-   Ontology compiler；
-   L3 parser framework；
-   自动知识审核系统。

当前目标只是：

``` text
稳定 Notion
→ 低频人工触发
→ 忠实 Markdown Snapshot
→ Codex 本地高频读取
```

------------------------------------------------------------------------

# 23. 首次同步验收

第一次执行至少确认：

``` text
[ ] 固定目录 knowledge/notion_l3/ 已建立
[ ] README.md 已建立
[ ] 正式根目录已实时核实
[ ] 未混入备份库
[ ] 正式页面全部有对应 Markdown
[ ] 本地目录正确反映 ancestor path
[ ] ASCII Tree 抽查未变形
[ ] Mermaid 抽查未变形
[ ] <br/> 未被改成 \n
[ ] TODO / 待审核 / 问题等成熟度仍保留
[ ] timestamp Snapshot 完整
[ ] snapshot_manifest.json 完整
[ ] current 与成功 Snapshot 一致
[ ] 普通任务可脱离 Notion 读取 L3
```

如果某种 Notion Block 无法可靠转换为 Markdown：

> 不得静默丢弃。

Completion Report 必须说明：

``` text
页面
Block 类型
转换问题
潜在信息损失
采用的保真方式
```

------------------------------------------------------------------------

# 24. 后续更新验收

第二次及以后执行：

``` text
[ ] 实时正式 ancestor tree 已重新核实
[ ] 新 Snapshot 使用新的同步时间
[ ] 新 Snapshot 完整
[ ] 备份库未混入
[ ] 变化页面已识别
[ ] 新增/删除/移动页面已识别
[ ] ASCII / Mermaid 保真
[ ] manifest 已更新
[ ] PASS 后才更新 current
[ ] 旧 Snapshot 保留
[ ] Completion Report 已生成
```

------------------------------------------------------------------------

# 25. Completion Report

每次同步结束后，用中文报告：

``` text
Notion L3 Sync Completion Report

同步时间：
正式根：
本地根：
新 Snapshot：
current：
同步页面数：

结构变化：
- 新增：
- 删除：
- 移动：

内容变化：
- 变化：
- 未变化：

Authority：
- 正式页面：
- 跳过备份/副本：

保真检查：
- ASCII Tree：
- Mermaid：
- Knowledge Maturity：
- 转换异常：

Manifest：
总体状态：
```

总体状态只能是：

``` text
SUCCESS
PARTIAL
FAILED
```

`PARTIAL` / `FAILED` 时不得将不完整 Snapshot 更新为 current。

------------------------------------------------------------------------

# 26. STOP CONDITION

完成：

``` text
正式结构核实
→ Snapshot
→ Markdown
→ 保真/完整性检查
→ manifest
→ PASS 后 current
→ Completion Report
```

立即停止。

不得继续：

-   修改 Notion；
-   修改 L3 技术知识；
-   设计新知识架构；
-   自动启动 TM3；
-   自动继续其他 Phase；
-   因同步过程中发现有趣问题而扩大任务。

------------------------------------------------------------------------

# 27. 以后用户的简化触发语

当用户以后说：

> **按 Notion L3 本地同步规范更新一次 L3。**

应理解为：

1.  使用本文件作为执行规范；
2.  访问实时 Notion 正式 `新能源汽修L3学习`；
3.  核实正式 ancestor tree；
4.  创建新 timestamp Snapshot；
5.  忠实转换为 Markdown；
6.  做保真和完整性检查；
7.  更新 manifest；
8.  成功后更新 current；
9.  输出 Completion Report；
10. STOP。

无需再次询问本地存放位置。

------------------------------------------------------------------------

# 28. 一句话规则

> **Notion 是 L3 唯一权威编辑源；`knowledge/notion_l3/current/` 是 Codex
> 日常只读知识源；`snapshots/时间戳/` 提供历史可追溯性。只有 L3
> 真正需要更新时才访问 Notion，并将正式 ancestor path 忠实镜像为
> Markdown；不得在同步过程中重写知识。**
