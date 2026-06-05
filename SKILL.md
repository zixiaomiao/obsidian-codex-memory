---
name: codin
description: Read and update Codex long-term memory stored in Obsidian. Use when the user asks to read Codex memory, update session summary, record something for later ("把这个记住", "以后记住", "记录到 Codex"), continue with memory context, sync Obsidian memory, or enable Obsidian-based memory. Covers vault discovery, compact read with keyword-matched log retrieval, append with tags/source/keywords, project summary generation, and categorized memory (decisions, todos, bugs, preferences). The companion Python script handles vault discovery via environment variable, config file, or auto-scan of common paths.
---

# Codin

## Dependencies

Python 3.x with no additional packages. The script uses only the standard library.

## Script Path

The skill bundles `scripts/obsidian_memory.py`. Resolve `<skill_dir>` at runtime:

```python
import os, sys
from pathlib import Path
script = Path(os.path.dirname(os.path.dirname(__file__))) / "scripts" / "obsidian_memory.py"
```

Or reference by relative path from the skill directory:
`$CODEX_HOME/skills/codin/scripts/obsidian_memory.py`

## Vault Configuration

The vault path is resolved in this order (tiered fallback):
1. `OBSIDIAN_VAULT` environment variable
2. `~/.config/codian/config.json` — `{"vault": "/path/to/vault"}`
3. Auto-discovery: scans common paths for `.obsidian/` directories, prefers the iCloud Documents root or a vault that already has `codian/AGENTS.md` + `codian/30-Logs-日志/codex-session-summary.md`

When the vault lives inside the iCloud Obsidian container, `codian/` is created at the container's `Documents` root so it stays independent from nested vaults like `Codex/`.

## Workflow

### 1. Read Memory (user wants context)

```bash
python3 <skill_dir>/scripts/obsidian_memory.py read
```

Compact read: entry files + project summary + matching categories + startup section + matched logs.

With keyword matching (finds 1-3 relevant past session logs):

```bash
python3 <skill_dir>/scripts/obsidian_memory.py read --query "项目 插件" --logs-limit 3
```

Full dump (only when user explicitly asks "完整读取" or "全部内容"):

```bash
python3 <skill_dir>/scripts/obsidian_memory.py read --full
```

### 2. Append Memory (user asks to save)

Before writing, confirm with the user:
- What should be recorded?
- Show the exact summary text
- Only write after user approval

```bash
python3 <skill_dir>/scripts/obsidian_memory.py append \
  --summary "<concise summary of what happened>" \
  --tags "<#tag1 #tag2 ...>" \
  --source "当前 Codex 会话" \
  --keywords "<key1, key2, ...>"
```

### 3. Generate Project Summary (periodic maintenance)

```bash
python3 <skill_dir>/scripts/obsidian_memory.py project-summary --max-logs 20
```

### 4. Generate Categorized Memory (periodic maintenance)

```bash
python3 <skill_dir>/scripts/obsidian_memory.py memory-categories --max-logs 80
```

## Vault Memory Structure

The Obsidian vault uses this directory layout:

```
codian/                       # Codian memory root created in the Obsidian vault
  README.md                   # Entry point
  AGENTS.md                   # Codex behavior rules
  00-入口/                     # Quick navigation
  10-Context-上下文/            # Project summary, paths
  20-Memory-记忆/              # Categorized: decisions, todos, bugs, preferences
  30-Logs-日志/                # Session summaries (chronological)
  40-Workflows-工作流/          # Workflow configurations
  90-Archive-归档/             # Archive
```

## Trigger Keywords

Trigger memory read or write when the user says:
- "用我的 Obsidian 记忆"
- "读取记忆"
- "更新/写入/记录到 Codex 记忆"
- "把这个记住" / "以后记住"
- "更新会话总结"
- "同步 Obsidian"
- "我今天做了什么" / "我之前做过什么"

## Safety Rules

- Do NOT record API keys, passwords, tokens, or subscription raw content
- Do NOT dump full history unless user explicitly asks
- Always confirm write content and final text with user before appending

## References

- `references/` — empty by default; add domain-specific lookup tables or search patterns here as needed
