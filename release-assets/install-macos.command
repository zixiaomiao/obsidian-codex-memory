#!/bin/bash
set -e

REPO_URL="https://github.com/zixiaomiao/codian.git"
PLUGIN_NAME="codian"
PLUGIN_DIR="$HOME/plugins/$PLUGIN_NAME"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SKILL_DIR="$CODEX_HOME/skills/$PLUGIN_NAME"
MARKETPLACE_PATH="$HOME/.agents/plugins/marketplace.json"

cd "$HOME"

if ! command -v git >/dev/null 2>&1; then
  echo "Git is required. Install Xcode Command Line Tools, then run this installer again."
  xcode-select --install 2>/dev/null || true
  read -r -p "Press Enter to close..."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required. Install Python 3, then run this installer again."
  read -r -p "Press Enter to close..."
  exit 1
fi

mkdir -p "$(dirname "$PLUGIN_DIR")"

if [ -d "$PLUGIN_DIR/.git" ]; then
  echo "Updating existing plugin..."
  git -C "$PLUGIN_DIR" pull --ff-only
elif [ -d "$PLUGIN_DIR" ]; then
  echo "Plugin directory already exists but is not a Git repository:"
  echo "$PLUGIN_DIR"
  echo "Move that folder aside, then run this installer again."
  read -r -p "Press Enter to close..."
  exit 1
else
  echo "Downloading plugin..."
  git clone "$REPO_URL" "$PLUGIN_DIR"
fi

rm -rf "$SKILL_DIR"
mkdir -p "$(dirname "$SKILL_DIR")"
cp -R "$PLUGIN_DIR/skills/$PLUGIN_NAME" "$SKILL_DIR"

mkdir -p "$(dirname "$MARKETPLACE_PATH")"

python3 - "$MARKETPLACE_PATH" "$PLUGIN_NAME" "./plugins/$PLUGIN_NAME" <<'PY'
import json
import sys
from pathlib import Path

marketplace_path = Path(sys.argv[1]).expanduser()
plugin_name = sys.argv[2]
source_path = sys.argv[3]

if marketplace_path.exists():
    data = json.loads(marketplace_path.read_text(encoding="utf-8"))
else:
    data = {
        "name": "personal",
        "interface": {"displayName": "Personal"},
        "plugins": [],
    }

data.setdefault("name", "personal")
data.setdefault("interface", {}).setdefault("displayName", "Personal")
plugins = data.setdefault("plugins", [])

entry = {
    "name": plugin_name,
    "source": {
        "source": "local",
        "path": source_path,
    },
    "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL",
    },
    "category": "Productivity",
}

for index, item in enumerate(plugins):
    if item.get("name") == plugin_name:
        plugins[index] = entry
        break
else:
    plugins.append(entry)

marketplace_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Registered {plugin_name} in {marketplace_path}")
PY

echo
echo "Installed Codian."
echo "Plugin path: $PLUGIN_DIR"
echo "Skill path: $SKILL_DIR"
echo
echo "Next step:"
echo "  Open Codex, enable Codian, then configure your Obsidian vault if needed."
echo
echo "Optional vault config command:"
echo "  python3 \"$PLUGIN_DIR/scripts/obsidian_memory.py\" init --vault \"/path/to/your/Obsidian vault\""
echo
read -r -p "Press Enter to close..."
