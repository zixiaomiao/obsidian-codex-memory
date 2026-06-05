# Codian

> Former project name / 旧项目名称: **obsidian-codex-memory**

[中文](README.md)

Use an Obsidian vault as Codex long-term memory.

This is a **Codex plugin**, not an Obsidian community plugin. It reads and writes the new structured Codex memory vault layout: entry files, context, memory, logs, workflows, and archive.

See [ROADMAP.md](ROADMAP.md) for planned improvements.

## Current Layout

Default Codex memory vault layout:

```text
codian/
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

If the vault lives inside the iCloud Obsidian container, first init creates `codian/` at the container's `Documents` root. All later Codian memory files are written under that independent directory, not inside a nested vault.

## Features

- Reads `codian/README.md` and `codian/AGENTS.md` first, then `codian/10-Context-上下文/project-summary.md`.
- Reads `codian/30-Logs-日志/codex-session-summary.md` as the full session log.
- Generates categorized memory files under `codian/20-Memory-记忆/`.
- Creates the `codian/` directory, the new subdirectory layout, `README.md`, `AGENTS.md`, and workflow files during init.
- Compact reads prioritize the project summary, then matching categories, startup rules, and a few matched history entries.
- Supports keyword lookup for 1-3 relevant historical log blocks.
- Appends compact Codex session summaries.
- Supports any local Obsidian vault through `OBSIDIAN_VAULT` or local config.
- Avoids recording API keys, passwords, tokens, and other secrets by default.

## Install

Copy the command below into Codex or your terminal. No double-click installer is required.

macOS or Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/zixiaomiao/codian/main/install.sh | bash
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/zixiaomiao/codian/main/install.ps1 | iex
```

On first use, the script asks for your Obsidian vault path. You can also run this manually:

```bash
python3 ~/.codex/skills/Codian/scripts/obsidian_memory.py init --vault "/path/to/your/Obsidian vault"
```

Windows:

```powershell
python "$env:USERPROFILE\.codex\skills\Codian\scripts\obsidian_memory.py" init --vault "D:\path\to\your\Obsidian vault"
```

You may also set `OBSIDIAN_VAULT` instead of writing local config.

## Usage

Read compact memory:

```bash
python3 ~/.codex/skills/Codian/scripts/obsidian_memory.py read
```

Generate or refresh the project summary:

```bash
python3 ~/.codex/skills/Codian/scripts/obsidian_memory.py project-summary
```

Generate or refresh categorized memory:

```bash
python3 ~/.codex/skills/Codian/scripts/obsidian_memory.py memory-categories
```

Read matched history, up to 3 blocks by default:

```bash
python3 ~/.codex/skills/Codian/scripts/obsidian_memory.py read --query "obsidian memory plugin"
```

Read the full memory log:

```bash
python3 ~/.codex/skills/Codian/scripts/obsidian_memory.py read --full
```

Append a summary:

```bash
python3 ~/.codex/skills/Codian/scripts/obsidian_memory.py append --summary "5-8 lines of durable session memory"
```

## Token Saving Strategy

- Ordinary tasks: read `codian/README.md`, `codian/AGENTS.md`, and `codian/10-Context-上下文/project-summary.md` first, then startup rules and the current user message.
- Category tasks: read matching files under `codian/20-Memory-记忆/` by keyword.
- Obsidian/memory tasks: search for `obsidian`, `vault-structure`, `codian`.
- Plugin/memory tasks: search for `codex/plugin`, `codex/memory`, `codian`.
- Historical review: include only 1-3 matched log blocks.
- Do not expand the full session log unless explicitly requested.

## Requirements

- Codex desktop app, or another Codex environment with plugin support
- Python 3
- A local Obsidian vault

## What the install command does

- Syncs the full repository into `~/.codex/skills/Codian GitHub`.
- Syncs the required runtime files into `~/.codex/skills/Codian`.
- Registers Codian in the Codex personal marketplace.

After installation, Codex reads the plugin directly from `~/.codex/skills/Codian`, and the root-level `SKILL.md` is the skill definition. The `~/.codex/skills/Codian GitHub` folder keeps the repository and release assets.

## License

MIT
