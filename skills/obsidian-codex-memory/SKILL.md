---
name: obsidian-codex-memory
description: Use when the user asks to enable Obsidian memory, read Codex memory, sync Obsidian memory, update Codex session summary, or continue with their Obsidian memory. Reads and updates the user's Codex memory note in Obsidian.
---

# Obsidian Codex Memory

Use this skill when the user says any of:

- 启用 Obsidian 记忆
- 先读我的 Obsidian
- 同步 Obsidian 记忆
- 更新 Codex 会话总结
- 用我的 Obsidian 记忆继续
- read Obsidian memory
- update Codex memory

## Vault and configuration

The memory script supports any computer. It resolves the vault in this order:

- `OBSIDIAN_VAULT` environment variable
- saved config from `obsidian_memory.py init --vault <path>`
- common Obsidian vault locations

If no vault can be found, ask the user for their Obsidian vault path and run:

```bash
python3 ~/plugins/obsidian-codex-memory/scripts/obsidian_memory.py init --vault "<path-to-vault>"
```

## Workflow

1. At the start of any task, read token-saving memory before doing substantial work. Default reading should only load startup rules, reading strategy, indexes, fixed paths, and any history blocks explicitly matched by query keywords:

```bash
python3 ~/plugins/obsidian-codex-memory/scripts/obsidian_memory.py read
```

For Obsidian, GitHub, sync, plugin, memory, or retrospective tasks, pass task keywords and read only 1-3 matching history blocks:

```bash
python3 ~/plugins/obsidian-codex-memory/scripts/obsidian_memory.py read --query "obsidian sync git/github"
python3 ~/plugins/obsidian-codex-memory/scripts/obsidian_memory.py read --query "codex/plugin obsidian-codex-memory"
```

Use the installed plugin root if it is not installed in `~/plugins/obsidian-codex-memory`.

2. Finish the user's actual task.

3. After the task is complete, append a compact summary only if the user asks to update memory, or the work creates a durable preference, path, fix, or operating rule:

```bash
python3 ~/plugins/obsidian-codex-memory/scripts/obsidian_memory.py append --summary "<5 lines max>"
```

Keep summaries short. Record only durable paths, preferences, conclusions, pitfalls, and verified fixes.

4. For selective GitHub sync of memory files:

```bash
python3 ~/plugins/obsidian-codex-memory/scripts/obsidian_memory.py sync-github --dry-run
python3 ~/plugins/obsidian-codex-memory/scripts/obsidian_memory.py sync-github
```

## Rules

- Do not record API keys, passwords, tokens, or private credentials.
- Do not dump the entire memory note unless the user asks for full memory.
- For ordinary tasks, use startup memory only. For specialized tasks, query matching history blocks by keywords.
- Complete the user's task before writing a memory summary.
- Keep new summaries within 5 lines when possible.
- Prefer UTF-8 direct file writes. Avoid shell pipelines that can corrupt Chinese text.
- For GitHub sync, only Codex memory files should be staged and committed. Do not treat this plugin as a full Obsidian vault manager.
