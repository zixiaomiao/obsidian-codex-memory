# Obsidian Codex Memory

[中文说明](README.zh-CN.md)

Use an Obsidian vault as long-term memory for Codex.

This is a **Codex plugin**, not an Obsidian community plugin. It lets Codex read a compact memory note, append session summaries, and optionally sync the memory note through a Git-backed Obsidian vault.

## What it does

- Reads `Codex/Codex 会话总结.md` from your Obsidian vault.
- Appends compact Codex session summaries.
- Supports any vault path through `OBSIDIAN_VAULT` or a saved local config.
- Can selectively sync memory files to GitHub while keeping other vault differences aligned with GitHub.
- Avoids recording credentials or secrets by design; you should still review summaries before syncing sensitive work.

## One-line install

macOS or Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/zixiaomiao/obsidian-codex-memory/main/install.sh | bash
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/zixiaomiao/obsidian-codex-memory/main/install.ps1 | iex
```

Then configure your vault:

```bash
python3 ~/plugins/obsidian-codex-memory/scripts/obsidian_memory.py init --vault "/path/to/your/Obsidian vault"
```

On Windows:

```powershell
python "$env:USERPROFILE\plugins\obsidian-codex-memory\scripts\obsidian_memory.py" init --vault "D:\path\to\your\Obsidian vault"
```

You can also skip local config and set `OBSIDIAN_VAULT` in your shell environment.

## Usage

Read compact memory:

```bash
python3 ~/plugins/obsidian-codex-memory/scripts/obsidian_memory.py read
```

Read the full memory note:

```bash
python3 ~/plugins/obsidian-codex-memory/scripts/obsidian_memory.py read --full
```

Append a summary:

```bash
python3 ~/plugins/obsidian-codex-memory/scripts/obsidian_memory.py append --summary "5-8 lines of durable session memory"
```

Preview GitHub sync:

```bash
python3 ~/plugins/obsidian-codex-memory/scripts/obsidian_memory.py sync-github --dry-run
```

Run GitHub sync:

```bash
python3 ~/plugins/obsidian-codex-memory/scripts/obsidian_memory.py sync-github
```

## Expected Obsidian note

The default memory note is:

```text
Codex/Codex 会话总结.md
```

Inside the vault, this means:

```text
<your-vault>/Codex/Codex 会话总结.md
```

You can change it when initializing:

```bash
python3 ~/plugins/obsidian-codex-memory/scripts/obsidian_memory.py init --vault "/path/to/vault" --memory-rel "Codex/My Memory.md"
```

## How installation works

The install scripts:

- clone or update this repository into `~/plugins/obsidian-codex-memory`
- create or update `~/.agents/plugins/marketplace.json`
- register the plugin as available in Codex

After installation, open Codex and enable **Obsidian Codex Memory** from the personal marketplace.

## GitHub sync behavior

`sync-github` is intentionally conservative.

- Allowed local-over-remote memory files:
  - `Codex/Codex 会话总结.md`
  - `Codex/MACOS_CODEX_OBSIDIAN_MEMORY.md`
- Other local vault differences are restored from GitHub during sync.
- The vault must already be a Git repository with `origin` configured.

Always run `sync-github --dry-run` before real sync when using a new vault.

## Requirements

- Codex desktop or Codex environment with plugin support
- Python 3
- Git, if using one-line install or GitHub sync
- Obsidian vault on local disk

## License

MIT
