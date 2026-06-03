# Obsidian Codex Memory

[English](README.en.md)

把 Obsidian vault 作为 Codex 的长期记忆。

这是一个 **Codex 插件**，不是 Obsidian 社区插件。它可以让 Codex 读取一份精简记忆笔记、追加会话总结，并且在 Obsidian vault 是 Git 仓库时，选择性把记忆文件同步到 GitHub。

后续优化规划见 [ROADMAP.md](ROADMAP.md)。

## 功能

- 从你的 Obsidian vault 读取 `Codex/Codex 会话总结.md`。
- 从会话总结生成 `Codex/project-summary.md` 项目摘要。
- 初始化时可自动创建一份通用“启动必读”记忆模板。
- 默认优先读取项目摘要，再读取启动规则、读取策略、检索索引和固定路径，避免每次展开完整历史。
- 支持按关键词检索 1-3 条相关历史日志，适合节省 token。
- 追加简洁的 Codex 会话总结。
- 支持通过 `OBSIDIAN_VAULT` 或本地配置指定任意 vault 路径。
- 可以只同步 Codex 记忆文件到 GitHub。
- 默认不记录 API key、密码、token 等敏感信息；但在同步敏感工作前，仍建议你检查总结内容。

## 一行安装

### 从 Release 下载后双击安装

如果你不想复制命令，可以下载对应系统的安装文件：

- macOS：下载 [`install-macos.command`](https://raw.githubusercontent.com/zixiaomiao/obsidian-codex-memory/main/release-assets/install-macos.command)，双击运行
- Windows：下载 [`install-windows.cmd`](https://raw.githubusercontent.com/zixiaomiao/obsidian-codex-memory/main/release-assets/install-windows.cmd)，双击运行

安装器会自动下载插件并注册到 Codex 的个人插件市场。

也可以从 [Releases](https://github.com/zixiaomiao/obsidian-codex-memory/releases) 下载版本附件。

### 复制命令安装

macOS 或 Linux：

```bash
curl -fsSL https://raw.githubusercontent.com/zixiaomiao/obsidian-codex-memory/main/install.sh | bash
```

Windows PowerShell：

```powershell
irm https://raw.githubusercontent.com/zixiaomiao/obsidian-codex-memory/main/install.ps1 | iex
```

安装后配置你的 Obsidian vault：

```bash
python3 ~/plugins/obsidian-codex-memory/scripts/obsidian_memory.py init --vault "/path/to/your/Obsidian vault"
```

Windows：

```powershell
python "$env:USERPROFILE\plugins\obsidian-codex-memory\scripts\obsidian_memory.py" init --vault "D:\path\to\your\Obsidian vault"
```

你也可以不写入本地配置，直接在 shell 环境里设置 `OBSIDIAN_VAULT`。

## 使用方法

读取精简记忆：

```bash
python3 ~/plugins/obsidian-codex-memory/scripts/obsidian_memory.py read
```

生成或刷新项目摘要：

```bash
python3 ~/plugins/obsidian-codex-memory/scripts/obsidian_memory.py project-summary
```

按关键词读取相关历史，默认最多 3 条：

```bash
python3 ~/plugins/obsidian-codex-memory/scripts/obsidian_memory.py read --query "obsidian sync git/github"
```

读取完整记忆笔记：

```bash
python3 ~/plugins/obsidian-codex-memory/scripts/obsidian_memory.py read --full
```

追加一条总结：

```bash
python3 ~/plugins/obsidian-codex-memory/scripts/obsidian_memory.py append --summary "5-8 行长期有用的会话总结"
```

预览 GitHub 同步：

```bash
python3 ~/plugins/obsidian-codex-memory/scripts/obsidian_memory.py sync-github --dry-run
```

执行 GitHub 同步：

```bash
python3 ~/plugins/obsidian-codex-memory/scripts/obsidian_memory.py sync-github
```

## 默认 Obsidian 笔记

默认记忆笔记是：

```text
Codex/Codex 会话总结.md
```

默认项目摘要是：

```text
Codex/project-summary.md
```

也就是 vault 里的这个文件：

```text
<your-vault>/Codex/Codex 会话总结.md
```

初始化时可以改成其他路径：

```bash
python3 ~/plugins/obsidian-codex-memory/scripts/obsidian_memory.py init --vault "/path/to/vault" --memory-rel "Codex/My Memory.md"
```

如果这个笔记不存在，`init` 会创建一份通用模板，包含：

- 启动必读
- 读取策略
- 任务检索索引
- 固定路径索引
- 历史归档说明
- 会话日志

这份模板不会写入你的个人路径以外的固定信息；vault 路径会按当前电脑自动写入。

## Token 节省策略

插件默认遵循这套读取逻辑：

- 普通任务：优先读取 `Codex/project-summary.md`，再读“启动必读”和用户当前消息。
- Obsidian/GitHub/同步任务：再检索 `obsidian`、`sync`、`git/github`、`github-sync` 等关键词。
- 插件/记忆任务：再检索 `codex/plugin`、`codex/memory`、`obsidian-codex-memory` 等关键词。
- 旧问题复盘：只读取命中的 1-3 个历史日志块。
- 除非明确要求完整读取，否则不展开整篇会话总结。

## Token 与缓存收益估算

以一份约 18,000 字符的会话总结为例，完整读取通常可能消耗约 9k-16k token。使用本插件后，默认启动读取通常只需要约 1k-2k token；如果再按关键词带出 1-3 条相关历史，通常约 2k-4k token。

| 场景 | 读取内容 | 估算 token | 相比完整读取 |
| --- | --- | --- | --- |
| 不读记忆 | 无长期记忆 | 0 | 最省，但没有记忆收益 |
| 插件默认读取 | 启动必读、读取策略、索引、固定路径 | 约 1k-2k | 约省 80%-90% |
| 插件 + 关键词检索 | 默认读取 + 1-3 条相关历史 | 约 2k-4k | 约省 65%-85% |
| 完整读取会话总结 | 整篇记忆文件 | 约 9k-16k | 基准 |

缓存命中方面，默认读取的内容比较稳定，通常更容易复用缓存；关键词检索会随任务变化，缓存命中率会中等一些；完整读取虽然也有稳定部分，但日志不断追加，体量和顺序变化更容易降低实际收益。

简单说：它不是为了和“完全不读记忆”比较，而是把长期记忆成本从上万 token 压到一两千 token，同时保留必要上下文。

## 安装脚本做了什么

安装脚本会：

- 把这个仓库克隆或更新到 `~/plugins/obsidian-codex-memory`
- 创建或更新 `~/.agents/plugins/marketplace.json`
- 把插件注册到 Codex 的个人插件市场

安装后，打开 Codex，在个人插件市场里启用 **Obsidian Codex Memory**。

## GitHub 同步规则

`sync-github` 是保守同步，只允许少数记忆文件用本地版本覆盖远端。

允许本地覆盖远端的文件：

- `Codex/Codex 会话总结.md`
- `Codex/project-summary.md`
- `Codex/MACOS_CODEX_OBSIDIAN_MEMORY.md`

插件只面向 Codex 记忆文件，不负责管理整个 Obsidian vault。你的 vault 必须已经是 Git 仓库，并且配置好了 `origin`。

在新的 vault 上第一次同步前，建议先运行：

```bash
python3 ~/plugins/obsidian-codex-memory/scripts/obsidian_memory.py sync-github --dry-run
```

## 环境要求

- Codex 桌面版，或支持插件的 Codex 环境
- Python 3
- Git，一行安装和 GitHub 同步需要它
- 本地磁盘上的 Obsidian vault

## 许可证

MIT
