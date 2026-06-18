#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MARKETPLACE="${HOME}/.agents/plugins/marketplace.json"
PLUGIN_NAME="path-to-academia"
PLUGIN_DIR="${HOME}/plugins/${PLUGIN_NAME}"
PLUGIN_SOURCE="${ROOT}/plugins/${PLUGIN_NAME}"

if [ ! -f "${PLUGIN_SOURCE}/.codex-plugin/plugin.json" ]; then
  echo "Missing Codex plugin bundle at ${PLUGIN_SOURCE}" >&2
  echo "Run from a complete checkout of path-to-academia." >&2
  exit 1
fi

if command -v codex >/dev/null 2>&1; then
  codex plugin marketplace add "${ROOT}"
  codex plugin add "${PLUGIN_NAME}@${PLUGIN_NAME}"
  echo "Codex plugin installed."
  echo "Start a new Codex session, or open /plugins and confirm ${PLUGIN_NAME} is enabled."
  exit 0
fi

mkdir -p "$(dirname "${MARKETPLACE}")"
mkdir -p "$(dirname "${PLUGIN_DIR}")"

if [ -e "${PLUGIN_DIR}" ] || [ -L "${PLUGIN_DIR}" ]; then
  if [ "$(realpath "${PLUGIN_DIR}")" != "${PLUGIN_SOURCE}" ]; then
    echo "${PLUGIN_DIR} already exists and does not point to this checkout." >&2
    echo "Move it aside or install from that checkout instead." >&2
    exit 1
  fi
else
  ln -s "${PLUGIN_SOURCE}" "${PLUGIN_DIR}"
fi

python3 - "${MARKETPLACE}" "${PLUGIN_NAME}" <<'PY'
import json
import sys
from pathlib import Path

marketplace = Path(sys.argv[1]).expanduser()
plugin_name = sys.argv[2]

if marketplace.exists():
    data = json.loads(marketplace.read_text(encoding="utf-8"))
else:
    data = {"name": "personal", "interface": {"displayName": "Personal"}, "plugins": []}

data.setdefault("name", "personal")
data.setdefault("interface", {}).setdefault("displayName", "Personal")
plugins = data.setdefault("plugins", [])

entry = {
    "name": plugin_name,
    "source": {"source": "local", "path": f"./plugins/{plugin_name}"},
    "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
    "category": "Productivity",
}

for index, existing in enumerate(plugins):
    if existing.get("name") == plugin_name:
        plugins[index] = entry
        break
else:
    plugins.append(entry)

marketplace.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(marketplace)
PY

echo "Codex CLI not found; personal marketplace entry written."
echo "Install later with: codex plugin add ${PLUGIN_NAME}@personal"
