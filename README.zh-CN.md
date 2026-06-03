# Obsidian Codex Memory

[English](README.md)

把 Obsidian vault 作为 Codex 的长期记忆。

这是一个 **Codex 插件**，不是 Obsidian 社区插件。它可以让 Codex 读取一份精简记忆笔记、追加会话总结，并且在 Obsidian vault 是 Git 仓库时，选择性把记忆文件同步到 GitHub。

## 功能

- 从你的 Obsidian vault 读取 `Codex/Codex 会话总结.md`。
- 追加简洁的 Codex 会话总结。
- 支持通过 `OBSIDIAN_VAULT` 或本地配置指定任意 vault 路径。
- 可以只同步记忆文件到 GitHub，同时让其他 vault 差异以 GitHub 为准。
- 默认不记录 API key、密码、token 等敏感信息；但在同步敏感工作前，仍建议你检查总结内容。

## 一行安装

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

也就是 vault 里的这个文件：

```text
<your-vault>/Codex/Codex 会话总结.md
```

初始化时可以改成其他路径：

```bash
python3 ~/plugins/obsidian-codex-memory/scripts/obsidian_memory.py init --vault "/path/to/vault" --memory-rel "Codex/My Memory.md"
```

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
- `Codex/MACOS_CODEX_OBSIDIAN_MEMORY.md`

其他本地 vault 差异会在同步时恢复为 GitHub 版本。你的 vault 必须已经是 Git 仓库，并且配置好了 `origin`。

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
