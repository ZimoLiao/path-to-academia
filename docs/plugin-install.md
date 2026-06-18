# Plugin Install

This repository uses the same marketplace layout as mature agent plugin repos:

```text
.agents/plugins/marketplace.json
.claude-plugin/marketplace.json
plugins/path-to-academia/
  .codex-plugin/plugin.json
  .claude-plugin/plugin.json
  skills/path-to-academia/SKILL.md
```

The root files register the marketplace. The installable plugin bundle lives under
`plugins/path-to-academia` and contains the workflow skill, docs, runtime scripts, examples, and
Python package code needed by the plugin after installation.

## Codex

After the repository is public:

```bash
codex plugin marketplace add ZimoLiao/path-to-academia
codex plugin add path-to-academia@path-to-academia
```

For local development from a clone:

```bash
codex plugin marketplace add "$PWD"
codex plugin add path-to-academia@path-to-academia
```

If your Codex build exposes plugin activation only through the TUI, launch `codex`, run `/plugins`,
select the **path to academia** marketplace, and install **path-to-academia**.

## Claude Code

After the repository is public:

```text
/plugin marketplace add ZimoLiao/path-to-academia
/plugin install path-to-academia@path-to-academia
```

For local development from a clone:

```text
/plugin marketplace add /absolute/path/to/path-to-academia
/plugin install path-to-academia@path-to-academia
/reload-plugins
```

Claude Code plugin skills are namespaced by plugin name, so invoke:

```text
/path-to-academia:path-to-academia
```

If using the non-interactive CLI instead of slash commands:

```bash
claude plugin marketplace add /absolute/path/to/path-to-academia
claude plugin install path-to-academia@path-to-academia
```

## Local Convenience Scripts

The scripts below wrap the same local marketplace flow. Use them for smoke tests or personal local
setup, but document the native marketplace commands as the public install path.

```bash
./install.sh
./install-claude.sh
```

When the Codex CLI is unavailable, `install.sh` writes a personal marketplace entry and links the
plugin bundle at:

```text
~/plugins/path-to-academia
```

When the Claude Code CLI is unavailable, `install-claude.sh` falls back to linking the plugin bundle
at:

```text
~/.claude/skills/path-to-academia
```
