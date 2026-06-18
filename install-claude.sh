#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_NAME="path-to-academia"
PLUGIN_DIR="${HOME}/.claude/skills/${PLUGIN_NAME}"
PLUGIN_SOURCE="${ROOT}/plugins/${PLUGIN_NAME}"

if [ ! -f "${PLUGIN_SOURCE}/.claude-plugin/plugin.json" ]; then
  echo "Missing Claude Code plugin bundle at ${PLUGIN_SOURCE}" >&2
  echo "Run from a complete checkout of path-to-academia." >&2
  exit 1
fi

if command -v claude >/dev/null 2>&1; then
  claude plugin marketplace add "${ROOT}"
  claude plugin install "${PLUGIN_NAME}@${PLUGIN_NAME}"
  echo "Claude Code plugin installed."
  echo "Run /reload-plugins in an existing session, or start a new Claude Code session."
  echo "Invoke with: /${PLUGIN_NAME}:${PLUGIN_NAME}"
  exit 0
fi

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

echo "${PLUGIN_DIR}"
echo "Claude Code CLI not found; registered as a skills-dir plugin."
echo "Install Claude Code later, then start it or run /reload-plugins in an existing session."
echo "Invoke with: /path-to-academia:path-to-academia"
