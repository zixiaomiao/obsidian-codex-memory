#!/usr/bin/env python3
"""Read, append, and sync Codex memory stored in an Obsidian vault."""

import argparse
import json
import os
import platform
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional


APP_NAME = "obsidian-codex-memory"
DEFAULT_MEMORY_REL = Path("Codex/Codex 会话总结.md")
DEFAULT_EXTRA_MEMORY_REL = Path("Codex/MACOS_CODEX_OBSIDIAN_MEMORY.md")
STARTUP_HEADING = "## 启动必读"
LOGS_HEADING = "## 会话日志"
ALLOWED_OVERWRITE = {
    DEFAULT_MEMORY_REL.as_posix(),
    DEFAULT_EXTRA_MEMORY_REL.as_posix(),
}


def config_path() -> Path:
    explicit = os.environ.get("OBSIDIAN_CODEX_MEMORY_CONFIG")
    if explicit:
        return Path(explicit).expanduser()
    if platform.system() == "Windows":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        return base / APP_NAME / "config.json"
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / APP_NAME / "config.json"


def load_config() -> dict:
    path = config_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid config file: {path}\n{exc}") from exc


def save_config(config: dict) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def candidate_vaults() -> List[Path]:
    home = Path.home()
    candidates = [
        home / "Library/Mobile Documents/iCloud~md~obsidian/Documents",
        home / "Documents",
        home / "Obsidian",
        home / "obsidian-vault",
        Path("D:/AI/obsidian-vault"),
        Path("D:/Obsidian"),
    ]
    return candidates


def looks_like_vault(path: Path) -> bool:
    return path.exists() and (path / ".obsidian").exists()


def discover_vault() -> Optional[Path]:
    vaults = []
    for root in candidate_vaults():
        if looks_like_vault(root):
            vaults.append(root)
        if root.exists() and root.is_dir():
            for child in sorted(root.iterdir()):
                if looks_like_vault(child):
                    vaults.append(child)

    for vault in vaults:
        if (vault / DEFAULT_MEMORY_REL).exists():
            return vault
    return vaults[0] if vaults else None


def vault_path() -> Path:
    if os.environ.get("OBSIDIAN_VAULT"):
        return Path(os.environ["OBSIDIAN_VAULT"]).expanduser()

    config = load_config()
    configured = config.get("vault")
    if configured:
        return Path(configured).expanduser()

    discovered = discover_vault()
    if discovered:
        return discovered

    raise SystemExit(
        "Obsidian vault not configured.\n"
        "Run one of these:\n"
        f"  python3 {Path(__file__).resolve()} init --vault /path/to/your/vault\n"
        "  export OBSIDIAN_VAULT=/path/to/your/vault"
    )


def memory_rel() -> Path:
    configured = os.environ.get("OBSIDIAN_CODEX_MEMORY_REL") or load_config().get("memory_rel")
    return Path(configured) if configured else DEFAULT_MEMORY_REL


def memory_path() -> Path:
    return vault_path() / memory_rel()


def run(cmd: list, cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise SystemExit(result.stderr.strip() or result.stdout.strip())
    return result


def git_changed_paths(vault: Path) -> List[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain", "-z"],
        cwd=vault,
        text=False,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(result.stderr.decode("utf-8", errors="replace").strip())

    paths = []
    entries = [entry for entry in result.stdout.split(b"\0") if entry]
    i = 0
    while i < len(entries):
        entry = entries[i].decode("utf-8", errors="replace")
        status = entry[:2]
        path = entry[3:]
        paths.append(path)
        i += 1
        if status.startswith("R") or status.startswith("C"):
            i += 1
    return paths


def now_iso() -> str:
    return datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()


def current_system_name() -> str:
    system = platform.system()
    if system == "Darwin":
        return "macOS"
    return system or "unknown"


def default_memory_template(vault: Path, rel: Path) -> str:
    return f"""# Codex 会话总结

## 启动必读

- 启动时先判断当前系统；读取当前系统对应的 Obsidian vault。
- 当前系统：`{current_system_name()}`
- 当前 Obsidian vault：`{vault}`
- 主会话总结相对路径：`{rel.as_posix()}`
- GitHub 仓库：未配置；如果 vault 是 Git 仓库，使用 `git remote -v` 确认远程和分支。
- 用户偏好：先完成任务，再写 Obsidian 总结；回答尽量直接、少废话。
- 记忆读取策略：默认只读本节和用户当前消息；按任务关键词检索相关条目；不要默认展开全部历史。
- 同步策略：只同步 Codex 记忆文件；不要把插件当作完整 Obsidian vault 管理工具。
- 安全规则：不记录 API key、密码、token、订阅原文等敏感信息。
- Codex 主要插件：`obsidian-codex-memory`。

## 读取策略

- 普通任务：只读“启动必读”和用户当前消息。
- Obsidian/GitHub/同步任务：再检索 `obsidian`、`sync`、`git/github`、`github-sync`、`vault-structure`。
- 插件/记忆任务：再检索 `codex/plugin`、`codex/memory`、`obsidian-codex-memory`。
- 旧问题复盘：只读取命中的 1-3 个历史日志块。
- 除非用户要求“完整读取记忆”，否则不要读取整篇会话总结。

## 任务检索索引

### Obsidian 与同步

关键词：`obsidian`、`vault-structure`、`git/github`、`sync`、`github-sync`、`iCloud`、`obsidian-git`、`dataview`

用途：Codex 记忆文件路径、GitHub 同步、iCloud 多端同步、Obsidian 社区插件状态。

### Codex 记忆与插件

关键词：`codex/memory`、`codex/plugin`、`obsidian-codex-memory`、`token-saving`、`optimization`、`self-learning`

用途：长期记忆读取规则、会话总结写入、插件脚本、token 节省策略。

## 固定路径索引

- 当前 Obsidian vault：`{vault}`
- 当前主会话总结：`{vault / rel}`
- 当前 Codex 记忆插件：自动安装到用户本机插件目录，通常是 `~/plugins/obsidian-codex-memory`。

## 历史归档说明

- 下面日志只作为可检索历史，默认不完整读取。
- 新增总结控制在 5 行以内，只记录会影响后续任务的路径、偏好、结论、坑点和验证结果。
- 稳定信息沉淀到“启动必读”或“固定路径索引”，不要在每条日志里重复展开。

## 会话日志
"""


def ensure_memory_note() -> None:
    path = memory_path()
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(default_memory_template(vault_path(), memory_rel()), encoding="utf-8")
    print(f"Created memory note: {path}")


def section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start == -1:
        return ""
    next_start = text.find("\n## ", start + 1)
    return text[start : next_start if next_start != -1 else len(text)].strip()


def split_logs(text: str) -> List[str]:
    logs = section(text, LOGS_HEADING)
    if not logs:
        return []
    parts = logs.split("\n### ")
    if len(parts) <= 1:
        return []
    return ["### " + part.strip() for part in parts[1:] if part.strip()]


def matched_logs(text: str, query: str, limit: int) -> List[str]:
    terms = [term.strip().lower() for term in query.replace(",", " ").split() if term.strip()]
    if not terms:
        return []
    matches = []
    for block in reversed(split_logs(text)):
        lower = block.lower()
        if any(term in lower for term in terms):
            matches.append(block)
        if len(matches) >= limit:
            break
    return list(reversed(matches))


def init(vault: str, memory: Optional[str], create: bool) -> None:
    vault_dir = Path(vault).expanduser().resolve()
    if not vault_dir.exists():
        raise SystemExit(f"Vault path does not exist: {vault_dir}")

    config = load_config()
    config["vault"] = str(vault_dir)
    if memory:
        config["memory_rel"] = memory
    save_config(config)
    if create:
        ensure_memory_note()
    print(f"Saved config: {config_path()}")
    print(f"Vault: {vault_dir}")
    print(f"Memory note: {memory_path()}")


def read_memory(full: bool = False, query: str = "", logs_limit: int = 3) -> None:
    path = memory_path()
    if not path.exists():
        raise SystemExit(f"Memory note not found: {path}")
    text = path.read_text(encoding="utf-8")
    if full:
        print(text)
        return

    sections = []
    for heading in [STARTUP_HEADING, "## 读取策略", "## 任务检索索引", "## 固定路径索引"]:
        found = section(text, heading)
        if found:
            sections.append(found)

    matches = matched_logs(text, query, logs_limit)
    if matches:
        sections.append(LOGS_HEADING + "\n\n" + "\n\n".join(matches))

    print("\n\n".join(s for s in sections if s))


def append_summary(summary: str, tags: str, source: str, keywords: str) -> None:
    path = memory_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else "# Codex 会话总结\n\n## 会话日志\n"
    summary = summary.replace("\\n", "\n")
    ts = now_iso()
    block = (
        f"\n\n### {ts}\n\n"
        f"标签：{tags}\n\n"
        f"来源：{source}\n\n"
        f"关键词：{keywords}\n\n"
        "摘要：\n\n"
        f"{summary.strip()}\n"
    )
    if "## 会话日志" not in existing:
        existing += "\n\n## 会话日志\n"
    updated = existing.rstrip() + block + "\n"
    if updated.startswith("---"):
        end = updated.find("\n---", 3)
        if end != -1:
            front = updated[:end]
            body = updated[end:]
            lines = []
            wrote = False
            for line in front.splitlines():
                if line.startswith("updated:"):
                    lines.append(f"updated: {ts}")
                    wrote = True
                else:
                    lines.append(line)
            if not wrote:
                lines.append(f"updated: {ts}")
            updated = "\n".join(lines) + body
    path.write_text(updated, encoding="utf-8")
    print(f"Appended memory summary to {path}")


def sync_github(dry_run: bool = False, branch: str = "main") -> None:
    vault = vault_path()
    if not (vault / ".git").exists():
        raise SystemExit(f"Not a Git vault: {vault}")

    allowed = set(ALLOWED_OVERWRITE)
    allowed.add(memory_rel().as_posix())

    run(["git", "fetch", "origin", branch], cwd=vault)
    changed = git_changed_paths(vault)
    disallowed = [p for p in changed if p not in allowed]

    print("Changed files:")
    for p in changed:
        print(f"- {p}")
    if dry_run:
        print("Dry run only.")
        return

    if disallowed:
        print("Leaving non-memory local differences unchanged:")
        for p in disallowed:
            print(f"- {p}")

    run(["git", "pull", "--ff-only", "origin", branch], cwd=vault)
    remaining = run(["git", "status", "--porcelain"], cwd=vault).stdout.strip()
    if not remaining:
        print("Nothing to sync.")
        return

    run(["git", "add", *sorted(allowed)], cwd=vault, check=False)
    if run(["git", "diff", "--cached", "--quiet"], cwd=vault, check=False).returncode != 0:
        run(["git", "commit", "-m", "Sync Codex memory files"], cwd=vault)
        run(["git", "push", "origin", branch], cwd=vault)
        print("Memory files synced to GitHub.")
    else:
        print("No allowed memory changes to commit.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    init_p = sub.add_parser("init", help="Save the Obsidian vault path for this computer.")
    init_p.add_argument("--vault", required=True)
    init_p.add_argument("--memory-rel", default=None)
    init_p.add_argument("--no-create", action="store_true", help="Do not create the default memory note if it is missing.")

    read_p = sub.add_parser("read", help="Read compact Codex memory.")
    read_p.add_argument("--full", action="store_true")
    read_p.add_argument("--query", default="", help="Optional keywords for retrieving 1-3 matching history blocks.")
    read_p.add_argument("--logs-limit", type=int, default=3, help="Maximum matched history blocks to include.")

    append_p = sub.add_parser("append", help="Append a compact memory summary.")
    append_p.add_argument("--summary", required=True)
    append_p.add_argument("--tags", default="#codex/memory #obsidian")
    append_p.add_argument("--source", default="当前 Codex 会话")
    append_p.add_argument("--keywords", default="Codex, Obsidian, memory")

    sync_p = sub.add_parser("sync-github", help="Selectively sync memory files in a Git-backed vault.")
    sync_p.add_argument("--dry-run", action="store_true")
    sync_p.add_argument("--branch", default="main")

    args = parser.parse_args()

    if args.cmd == "init":
        init(args.vault, args.memory_rel, not args.no_create)
    elif args.cmd == "read":
        read_memory(args.full, args.query, args.logs_limit)
    elif args.cmd == "append":
        append_summary(args.summary, args.tags, args.source, args.keywords)
    elif args.cmd == "sync-github":
        sync_github(args.dry_run, args.branch)


if __name__ == "__main__":
    main()
