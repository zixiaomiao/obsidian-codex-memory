# Codian

> 旧项目名称 / Former project name: **obsidian-codex-memory**

[English](README.en.md)

把 Obsidian vault 作为 Codex 的长期记忆。

这是一个 **Codex 插件**，不是 Obsidian 社区插件。它按新的 Codex 记忆仓库规则读写 Obsidian：入口、上下文、记忆、日志、工作流分层保存，让 Codex 读得到、找得到、记得住。

后续优化规划见 [ROADMAP.md](ROADMAP.md).

## 当前规则

默认 Codex 记忆仓库结构：

```text
README.md
AGENTS.md
00-入口/
10-Context-上下文/
  project-summary.md
  fixed-path-index.md
20-Memory-记忆/
  project.md
  decisions.md
  todos.md
  bugs-and-fixes.md
  user-preferences.md
  lessons.md
30-Logs-日志/
  codex-session-summary.md
40-Workflows-工作流/
  codex-memory-workflow.md
90-Archive-归档/
```

插件只使用上述新结构。

## 功能

- 先读取 `README.md` 和 `AGENTS.md`，再读取 `10-Context-上下文/project-summary.md`。
- 读取 `30-Logs-日志/codex-session-summary.md` 作为完整会话日志。
- 生成 `20-Memory-记忆/` 下的分类记忆文件。
- 初始化时自动创建新规则目录、`README.md`、`AGENTS.md` 和工作流文件。
- 默认优先读取入口规则和项目摘要；带关键词时读取匹配分类，再读取启动规则和少量命中日志。
- 支持按关键词检索 1-3 条相关历史日志，避免每次展开完整历史。
- 追加简洁的 Codex session summary。
- 支持通过 `OBSIDIAN_VAULT` 或本地配置指定任意 vault 路径。
- 默认不记录 API key、密码、token 等敏感信息。

## 一行安装

### 从 Release 下载后双击安装

- macOS：下载 [`install-macos.command`](https://raw.githubusercontent.com/zixiaomiao/codian/main/release-assets/install-macos.command)，双击运行
- Windows：下载 [`install-windows.cmd`](https://raw.githubusercontent.com/zixiaomiao/codian/main/release-assets/install-windows.cmd)，双击运行

安装器会自动下载插件并注册到 Codex 的个人插件市场。

也可以从 [Releases](https://github.com/zixiaomiao/codian/releases) 下载版本附件。

### 复制命令安装

macOS 或 Linux：

```bash
curl -fsSL https://raw.githubusercontent.com/zixiaomiao/codian/main/install.sh | bash
```

Windows PowerShell：

```powershell
irm https://raw.githubusercontent.com/zixiaomiao/codian/main/install.ps1 | iex
```

安装后配置你的 Obsidian vault：

```bash
python3 ~/plugins/codian/scripts/obsidian_memory.py init --vault "/path/to/your/Obsidian vault"
```

Windows：

```powershell
python "$env:USERPROFILE\plugins\codian\scripts\obsidian_memory.py" init --vault "D:\path\to\your\Obsidian vault"
```

你也可以不写入本地配置，直接在 shell 环境里设置 `OBSIDIAN_VAULT`。

## 使用方法

读取精简记忆：

```bash
python3 ~/plugins/codian/scripts/obsidian_memory.py read
```

生成或刷新项目摘要：

```bash
python3 ~/plugins/codian/scripts/obsidian_memory.py project-summary
```

生成或刷新分类记忆：

```bash
python3 ~/plugins/codian/scripts/obsidian_memory.py memory-categories
```

按关键词读取相关历史，默认最多 3 条：

```bash
python3 ~/plugins/codian/scripts/obsidian_memory.py read --query "obsidian memory plugin"
```

读取完整记忆日志：

```bash
python3 ~/plugins/codian/scripts/obsidian_memory.py read --full
```

追加一条总结：

```bash
python3 ~/plugins/codian/scripts/obsidian_memory.py append --summary "5-8 行长期有用的 session summary"
```

## Token 节省策略

插件默认遵循这套读取逻辑：

- 普通任务：优先读取 `README.md`、`AGENTS.md`、`10-Context-上下文/project-summary.md`，再读"启动必读"和用户当前消息。
- 分类任务：按关键词读取 `20-Memory-记忆/` 中的匹配分类。
- Obsidian/记忆任务：再检索 `obsidian`、`vault-structure`、`codian` 等关键词。
- 插件/记忆任务：再检索 `codex/plugin`、`codex/memory`、`codian` 等关键词。
- 旧问题复盘：只读取命中的 1-3 个历史日志块。
- 除非明确要求完整读取，否则不展开整篇会话总结。

## Token 与缓存收益估算

使用本插件后，默认启动读取通常只需要约 1k-2k token；如果再按关键词带出 1-3 条相关历史，通常约 2k-4k token。

新结构让稳定内容更容易缓存：

- 项目摘要：`10-Context-上下文/project-summary.md`
- 分类记忆：`20-Memory-记忆/*.md`
- 长日志：`30-Logs-日志/codex-session-summary.md`

简单说：它不是为了和"完全不读记忆"比较，而是把长期记忆成本从上万 token 压到一两千 token，同时保留必要上下文。

## 安装脚本做了什么

安装脚本会：

- 把这个仓库克隆或更新到 `~/plugins/codian`
- 把 `skills/codian` 同步安装到 `~/.codex/skills/codian`
- 创建或更新 `~/.agents/plugins/marketplace.json`
- 把插件注册到 Codex 的个人插件市场

安装后，Codex 可以直接读取独立 skill；也可以打开 Codex，在个人插件市场里启用 **Codian** 插件。

## 环境要求

- Codex 桌面版，或支持插件的 Codex 环境
- Python 3
- 本地磁盘上的 Obsidian vault

## 许可证

MIT
