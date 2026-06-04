#!/usr/bin/env python3
"""Read and update Codex memory stored in an Obsidian vault."""

import argparse
import json
import os
import platform
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional


APP_NAME = "codian"
MEMORY_ROOT_REL = Path("codian")
DEFAULT_MEMORY_REL = MEMORY_ROOT_REL / "30-Logs-日志/codex-session-summary.md"
DEFAULT_PROJECT_SUMMARY_REL = MEMORY_ROOT_REL / "10-Context-上下文/project-summary.md"
DEFAULT_ENTRY_RELS = [MEMORY_ROOT_REL / "README.md", MEMORY_ROOT_REL / "AGENTS.md"]
MEMORY_CATEGORY_RELS = {
    "Project": MEMORY_ROOT_REL / "20-Memory-记忆/project.md",
    "Decision": MEMORY_ROOT_REL / "20-Memory-记忆/decisions.md",
    "Todo": MEMORY_ROOT_REL / "20-Memory-记忆/todos.md",
    "Bug": MEMORY_ROOT_REL / "20-Memory-记忆/bugs-and-fixes.md",
    "User Preference": MEMORY_ROOT_REL / "20-Memory-记忆/user-preferences.md",
}
DEFAULT_EXTRA_MEMORY_REL = MEMORY_ROOT_REL / "40-Workflows-工作流/codex-memory-workflow.md"
STARTUP_HEADING = "## 启动必读"
LOGS_HEADING = "## 会话日志"


def config_path() -> Path:
    explicit = os.environ.get("CODIA_CONFIG")
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
        if (vault / MEMORY_ROOT_REL / "AGENTS.md").exists() and (vault / DEFAULT_MEMORY_REL).exists():
            return vault
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
    configured = os.environ.get("CODIA_MEMORY_REL") or load_config().get("memory_rel")
    return Path(configured) if configured else DEFAULT_MEMORY_REL


def memory_path() -> Path:
    return vault_path() / memory_rel()


def project_summary_rel() -> Path:
    configured = os.environ.get("CODIA_PROJECT_SUMMARY_REL") or load_config().get("project_summary_rel")
    return Path(configured) if configured else DEFAULT_PROJECT_SUMMARY_REL


def project_summary_path() -> Path:
    return vault_path() / project_summary_rel()


def entry_paths() -> List[Path]:
    vault = vault_path()
    return [vault / rel for rel in DEFAULT_ENTRY_RELS]


def memory_category_rels() -> dict:
    configured = load_config().get("memory_category_rels", {})
    rels = dict(MEMORY_CATEGORY_RELS)
    if isinstance(configured, dict):
        for name, rel in configured.items():
            rels[name] = Path(rel)
    return rels


def category_paths() -> dict:
    vault = vault_path()
    return {name: vault / rel for name, rel in memory_category_rels().items()}


def now_iso() -> str:
    return datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()


def current_system_name() -> str:
    system = platform.system()
    if system == "Darwin":
        return "macOS"
    return system or "unknown"


def default_memory_template(vault: Path, rel: Path) -> str:
    return f"""# Codex Session Summary

## 启动必读

- 当前系统：`{current_system_name()}`
- 当前 Obsidian vault：`{vault}`
- Codian 记忆根目录：`{MEMORY_ROOT_REL.as_posix()}/`
- 项目摘要相对路径：`{DEFAULT_PROJECT_SUMMARY_REL.as_posix()}`
- 记忆分类目录：`{(MEMORY_ROOT_REL / "20-Memory-记忆").as_posix()}/`
- 主会话总结相对路径：`{rel.as_posix()}`
- 用户偏好：回答尽量直接，中文为主，少废话；只有用户触发记忆写入关键词时，才进入 Codex 记忆写回流程；写入前需确认记录内容和最终写入文本。
- 记忆读取策略：进入仓库时先读取 `codian/README.md`、`codian/AGENTS.md` 和项目摘要；再读本节和用户当前消息；按任务关键词检索相关条目；不要默认展开全部历史。
- 同步策略：当前插件不负责 Git 同步，只负责记忆读取、摘要、分类和追加。
- 安全规则：不记录 API key、密码、token、订阅原文等敏感信息。
- Codex 主要插件：`codian`。

## 读取策略

- 普通任务：优先读取 `codian/README.md`、`codian/AGENTS.md` 和 `codian/10-Context-上下文/project-summary.md`。
- 项目任务：优先读取 `codian/10-Context-上下文/project-summary.md`。
- 分类读取：按任务类型读取 `codian/20-Memory-记忆/project.md`、`decisions.md`、`todos.md`、`bugs-and-fixes.md`、`user-preferences.md`。
- 工作流任务：读取 `codian/40-Workflows-工作流/codex-memory-workflow.md`。
- Obsidian/记忆任务：再检索 `obsidian`、`vault-structure`、`codex/memory`、`codian`。
- 插件/记忆任务：再检索 `codex/plugin`、`codex/memory`、`codian`。
- 旧问题复盘：只读取命中的 1-3 个历史日志块。
- 除非用户要求“完整读取记忆”，否则不要读取整篇会话总结。

## 任务检索索引

### Obsidian 与记忆

关键词：`obsidian`、`vault-structure`、`iCloud`、`obsidian-git`、`dataview`

用途：Codex 记忆文件路径、iCloud 多端同步、Obsidian 社区插件状态。

### Codex 记忆与插件

关键词：`codex/memory`、`codex/plugin`、`codian`、`token-saving`、`optimization`、`self-learning`

用途：长期记忆读取规则、session summary 写入、插件脚本、token 节省策略。

## 固定路径索引

- 当前 Obsidian vault：`{vault}`
- 当前项目摘要：`{vault / DEFAULT_PROJECT_SUMMARY_REL}`
- 当前记忆分类目录：`{vault / MEMORY_ROOT_REL / "20-Memory-记忆"}`
- 当前主会话总结：`{vault / rel}`
- 当前 Codex 记忆插件：自动安装到用户本机插件目录，通常是 `~/plugins/codian`。

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
    write_default_vault_structure(vault_path())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(default_memory_template(vault_path(), memory_rel()), encoding="utf-8")
    print(f"Created memory note: {path}")


def write_if_missing(path: Path, content: str) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def write_default_vault_structure(vault: Path) -> None:
    root = vault / MEMORY_ROOT_REL
    write_if_missing(
        root / "README.md",
        """# Codex

## 仓库用途

这个目录是 Codex/Codian 的本地长期记忆目录，用来保存项目上下文、用户偏好、技术决策、待办、修复经验和会话日志。

## 必读顺序

1. `README.md`
2. `AGENTS.md`
3. `10-Context-上下文/project-summary.md`
4. 按任务需要读取 `20-Memory-记忆/`、`40-Workflows-工作流/`
5. 需要历史细节时，再读取 `30-Logs-日志/codex-session-summary.md`
""",
    )
    write_if_missing(
        root / "AGENTS.md",
        """# Codex 工作规则

## 启动必读

进入本仓库后，先读取：

1. `README.md`
2. `AGENTS.md`
3. `10-Context-上下文/project-summary.md`
4. 按任务需要读取 `20-Memory-记忆/`、`40-Workflows-工作流/`
5. 需要历史细节时，再读取 `30-Logs-日志/codex-session-summary.md`

## 工作原则

- 回答尽量直接，中文为主，少废话。
- 不记录 API key、密码、token、订阅原文等敏感信息。
- 不默认读取全部历史日志；只在需要复盘时读取命中的 1-3 条。
- 只有用户触发记忆写入关键词时，才进入 Codex 记忆写回流程。
- 写入记忆前，先向用户确认需要记录哪些内容。
- 整理出最终写入文本后，必须再次给用户确认；用户确认后才能写入 Codex 记忆。

## 记忆写入触发词

- 更新 Codex 记忆
- 写入 Codex 记忆
- 记录到 Codex
- 更新 Codex 会话总结
- 同步 Obsidian 记忆
- 把这个记住
- 以后记住
- 用我的 Obsidian 记忆继续
""",
    )
    for rel, title, purpose in [
        ("00-入口/README.md", "00-入口", "仓库索引、命名规则、快速导航。"),
        ("10-Context-上下文/README.md", "10-Context-上下文", "当前项目状态、固定路径、环境信息。"),
        ("20-Memory-记忆/README.md", "20-Memory-记忆", "长期记忆，包括偏好、决策、待办、问题和经验。"),
        ("30-Logs-日志/README.md", "30-Logs-日志", "完整或较长的会话日志，默认不全量读取。"),
        ("40-Workflows-工作流/README.md", "40-Workflows-工作流", "Codex 执行任务、读写记忆、同步仓库的流程。"),
        ("90-Archive-归档/README.md", "90-Archive-归档", "旧结构说明和低频历史归档。"),
    ]:
        write_if_missing(root / rel, f"# {title}\n\n## 用途\n\n{purpose}\n")
    write_if_missing(
        vault / DEFAULT_EXTRA_MEMORY_REL,
        """# Codex 记忆工作流

## 读取

1. 先读 `codian/README.md` 和 `codian/AGENTS.md`。
2. 再读 `codian/10-Context-上下文/project-summary.md`。
3. 根据任务关键词读取 `codian/20-Memory-记忆/` 下的相关文件。
4. 只有需要历史细节时，才读 `codian/30-Logs-日志/codex-session-summary.md`。

## 写回

- 当前状态写入 `codian/10-Context-上下文/project-summary.md`。
- 偏好写入 `codian/20-Memory-记忆/user-preferences.md`。
- 决策写入 `codian/20-Memory-记忆/decisions.md`。
- 待办写入 `codian/20-Memory-记忆/todos.md`。
- 坑点和修复写入 `codian/20-Memory-记忆/bugs-and-fixes.md`。
- 长日志写入 `codian/30-Logs-日志/codex-session-summary.md`。
""",
    )


def section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start == -1:
        return ""
    next_start = text.find("\n## ", start + 1)
    return text[start : next_start if next_start != -1 else len(text)].strip()


def split_logs(text: str) -> List[str]:
    start = text.find(LOGS_HEADING)
    if start == -1:
        return []
    logs = text[start:].strip()
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


def clean_summary_lines(block: str) -> List[str]:
    lines = []
    capture = False
    for raw in block.splitlines():
        line = raw.strip()
        if line == "摘要：":
            capture = True
            continue
        if line.startswith(("标签：", "来源：", "关键词：")):
            continue
        if capture and line:
            lines.append(line.replace("\\n", " "))
    return lines


def log_timestamp(block: str) -> str:
    first = block.splitlines()[0].strip() if block.splitlines() else ""
    return first.replace("###", "").strip()


def log_keywords(block: str) -> str:
    for raw in block.splitlines():
        line = raw.strip()
        if line.startswith("关键词："):
            return line.replace("关键词：", "", 1).strip()
    return ""


def compact_line(value: str, limit: int = 140) -> str:
    compact = " ".join(value.replace("\\n", " ").split())
    return compact[: limit - 1] + "…" if len(compact) > limit else compact


def infer_project_name(text: str, fallback: str) -> str:
    candidates = [
        "codian",
        "Codian",
        "Codex Memory",
    ]
    for candidate in candidates:
        if candidate.lower() in text.lower():
            return "Codian"
    return fallback


def detect_terms(text: str, mapping: dict) -> List[str]:
    found = []
    lower = text.lower()
    for label, terms in mapping.items():
        if any(term.lower() in lower for term in terms):
            found.append(label)
    return found


def classify_log(block: str) -> List[str]:
    payload = (log_keywords(block) + "\n" + " ".join(clean_summary_lines(block))).lower()
    categories = []
    if any(term in payload for term in ["bug", "fix", "修复", "错误", "失败", "报错", "兼容", "验证"]):
        categories.append("Bug")
    if any(term in payload for term in ["decision", "决定", "选择", "策略", "规则", "默认", "不再", "改为", "优先", "只同步"]):
        categories.append("Decision")
    if any(term in payload for term in ["todo", "待办", "roadmap", "规划", "下一阶段", "后续推进"]):
        categories.append("Todo")
    if any(term in payload for term in ["preference", "偏好", "用户偏好", "先完成任务", "少废话", "不要"]):
        categories.append("User Preference")
    if any(term in payload for term in ["project", "项目", "release", "readme", "插件", "仓库", "安装", "发布", "summary"]):
        categories.append("Project")
    return categories or ["Project"]


def generate_memory_categories(max_logs: int = 80) -> List[Path]:
    source_path = memory_path()
    if not source_path.exists():
        raise SystemExit(f"Memory note not found: {source_path}")

    text = source_path.read_text(encoding="utf-8")
    logs = split_logs(text)
    selected_logs = logs[-max_logs:] if max_logs > 0 else logs
    buckets = {name: [] for name in memory_category_rels()}

    for block in selected_logs:
        ts = log_timestamp(block)
        keywords = log_keywords(block)
        summary_lines = clean_summary_lines(block)
        summary = compact_line(" ".join(summary_lines), 220) if summary_lines else ""
        if not summary:
            continue
        entry = f"- {ts}：{summary}"
        if keywords:
            entry += f"\n  - 关键词：{keywords}"
        for category in classify_log(block):
            buckets.setdefault(category, []).append(entry)

    written = []
    now = now_iso()
    for name, path in category_paths().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        items = buckets.get(name, [])
        body = f"""# {name}

updated: {now}
source: `{source_path.relative_to(vault_path())}`

## 用途

{category_purpose(name)}

## 条目

{chr(10).join(items[-30:]) if items else "- 暂无条目。"}
"""
        path.write_text(body, encoding="utf-8")
        written.append(path)
        print(f"Wrote {name} memory to {path}")
    return written


def category_purpose(name: str) -> str:
    return {
        "Project": "项目概况、发布记录、安装流程、当前状态和近期变更。",
        "Decision": "长期有效的技术决策、同步策略、读取策略和范围边界。",
        "Todo": "后续规划、待办事项和路线图。",
        "Bug": "错误、失败原因、修复记录、兼容性问题和验证结果。",
        "User Preference": "用户偏好、固定路径、操作习惯、安全规则和回答风格。",
    }.get(name, "分类记忆。")


def categories_for_query(query: str) -> List[str]:
    lower = query.lower()
    matched = []
    mapping = {
        "Project": ["project", "项目", "summary", "release", "readme", "发布", "安装"],
        "Decision": ["decision", "决策", "为什么", "策略", "规则", "选择"],
        "Todo": ["todo", "待办", "roadmap", "规划", "下一步"],
        "Bug": ["bug", "修复", "错误", "失败", "报错", "兼容"],
        "User Preference": ["preference", "偏好", "路径", "安全", "少废话", "用户"],
    }
    for name, terms in mapping.items():
        if any(term in lower for term in terms):
            matched.append(name)
    return matched


def generate_project_summary(project_name: str = "", output_rel: Optional[str] = None, max_logs: int = 12) -> Path:
    source_path = memory_path()
    if not source_path.exists():
        raise SystemExit(f"Memory note not found: {source_path}")

    text = source_path.read_text(encoding="utf-8")
    logs = split_logs(text)
    recent_logs = logs[-max_logs:] if max_logs > 0 else logs
    combined = "\n\n".join(recent_logs) or text
    name = project_name or infer_project_name(combined, vault_path().name)

    tech_stack = detect_terms(
        combined,
        {
            "Codex plugin": ["codex plugin", "codex 插件", ".codex-plugin", "plugin.json"],
            "Python": ["python", "obsidian_memory.py", "py_compile"],
            "Markdown": ["markdown", "README", "ROADMAP", ".md"],
            "Shell": ["install.sh", ".command", "bash", "shell"],
            "PowerShell/Windows CMD": ["powershell", ".cmd", "windows"],
            "Chrome automation": ["chrome", "release 页面", "浏览器"],
            "Obsidian": ["obsidian", "vault", "会话总结"],
        },
    )

    completed = []
    decisions = []
    todos = []
    for block in recent_logs:
        ts = log_timestamp(block)
        keywords = log_keywords(block)
        summary_lines = clean_summary_lines(block)
        joined = " ".join(summary_lines)
        if summary_lines:
            completed.append(f"- {ts}：{compact_line(summary_lines[0])}")
        if any(word in joined for word in ["决定", "选择", "策略", "规则", "优先", "默认", "只", "不再", "改为"]):
            decisions.append(f"- {ts}：{compact_line(joined, 180)}")
        if any(word.lower() in joined.lower() for word in ["todo", "待办", "规划", "roadmap"]):
            todos.append(f"- {ts}：{compact_line(joined, 180)}")
        elif any(word.lower() in keywords.lower() for word in ["roadmap", "todo"]):
            todos.append(f"- {ts}：{compact_line(joined, 180)}")

    if not todos:
        todos = [
            "- 实现更稳定的项目摘要提炼逻辑。",
            "- 后续推进 Memory 分类、Decision Log、自动归档和 Generate Context。",
        ]

    project_goal = (
        "把 Obsidian vault 作为 Codex 的长期记忆，用项目摘要和按需检索减少 token 消耗，"
        "让 AI 更快理解项目状态、决策和待办。"
    )
    current_progress = completed[-1].split("：", 1)[1] if completed else "已建立基础记忆读取、追加、摘要和分类流程。"
    tech_stack_text = "\n".join(f"- {item}" for item in tech_stack) if tech_stack else (
        "- Markdown-first memory workflow\n"
        "- Python utility script"
    )
    completed_text = "\n".join(completed[-8:]) if completed else "- 已创建基础 Codex session summary。"
    todos_text = "\n".join(todos[-6:])
    decisions_text = "\n".join(decisions[-8:]) if decisions else (
        "- Markdown 优先，不引入数据库作为默认依赖。\n"
        "- 默认读取项目摘要和启动必读，不默认展开完整历史。\n"
        "- 当前插件不负责 Git 同步；同步能力后续拆分为独立插件。"
    )

    now = now_iso()
    out_rel = Path(output_rel) if output_rel else project_summary_rel()
    out_path = vault_path() / out_rel
    out_path.parent.mkdir(parents=True, exist_ok=True)
    body = f"""# Project Summary

updated: {now}
source: `{source_path.relative_to(vault_path())}`

## 项目名称

{name}

## 项目目标

{project_goal}

## 技术栈

{tech_stack_text}

## 当前进度

{current_progress}

## 已完成任务

{completed_text}

## 待办事项

{todos_text}

## 重要技术决策

{decisions_text}

## 读取建议

- 进入仓库时先读取 `codian/README.md` 和 `codian/AGENTS.md`，再读取本文件。
- 需要偏好、决策、待办、修复记录或工作流时，按任务读取 `codian/20-Memory-记忆/`、`codian/40-Workflows-工作流/`。
- 需要细节时再读取 `codian/30-Logs-日志/codex-session-summary.md` 的启动必读和关键词命中的 1-3 条日志。
- 除非用户明确要求，不要完整读取全部历史。
"""
    out_path.write_text(body, encoding="utf-8")
    print(f"Wrote project summary to {out_path}")
    return out_path


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


def read_memory(
    full: bool = False,
    query: str = "",
    logs_limit: int = 3,
    include_project_summary: bool = True,
    include_categories: bool = True,
) -> None:
    path = memory_path()
    if not path.exists():
        raise SystemExit(f"Memory note not found: {path}")
    text = path.read_text(encoding="utf-8")
    if full:
        print(text)
        return

    sections = []
    for entry_path in entry_paths():
        if entry_path.exists():
            sections.append(entry_path.read_text(encoding="utf-8").strip())

    summary_path = project_summary_path()
    if include_project_summary and summary_path.exists():
        sections.append(summary_path.read_text(encoding="utf-8").strip())

    if include_categories and query:
        for category in categories_for_query(query):
            category_path = category_paths().get(category)
            if category_path and category_path.exists():
                sections.append(category_path.read_text(encoding="utf-8").strip())

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
    if not path.exists():
        ensure_memory_note()
    existing = path.read_text(encoding="utf-8") if path.exists() else "# Codex Session Summary\n\n## 会话日志\n"
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
    read_p.add_argument("--no-project-summary", action="store_true", help="Do not include codian/10-Context-上下文/project-summary.md in compact reads.")
    read_p.add_argument("--no-categories", action="store_true", help="Do not include matching codian/20-Memory-记忆 category files.")

    append_p = sub.add_parser("append", help="Append a compact memory summary.")
    append_p.add_argument("--summary", required=True)
    append_p.add_argument("--tags", default="#codex/memory #obsidian")
    append_p.add_argument("--source", default="当前 Codex 会话")
    append_p.add_argument("--keywords", default="Codex, Obsidian, memory")

    summary_p = sub.add_parser("project-summary", help="Generate codian/10-Context-上下文/project-summary.md from the memory note.")
    summary_p.add_argument("--project-name", default="")
    summary_p.add_argument("--output-rel", default=None)
    summary_p.add_argument("--max-logs", type=int, default=12)

    categories_p = sub.add_parser("memory-categories", help="Generate categorized memory files under codian/20-Memory-记忆/.")
    categories_p.add_argument("--max-logs", type=int, default=80)

    args = parser.parse_args()

    if args.cmd == "init":
        init(args.vault, args.memory_rel, not args.no_create)
    elif args.cmd == "read":
        read_memory(args.full, args.query, args.logs_limit, not args.no_project_summary, not args.no_categories)
    elif args.cmd == "append":
        append_summary(args.summary, args.tags, args.source, args.keywords)
    elif args.cmd == "project-summary":
        generate_project_summary(args.project_name, args.output_rel, args.max_logs)
    elif args.cmd == "memory-categories":
        generate_memory_categories(args.max_logs)


if __name__ == "__main__":
    main()
