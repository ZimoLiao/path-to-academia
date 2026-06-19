# Agent Guidance For This Repository

This repository is a public, domain-configurable agent plugin. Keep it generic. Do not reintroduce
private application data, legacy discipline-specific fields, old project names, or hardcoded
discipline rankings.

## Product Boundary

- Root marketplace metadata lives in `.agents/plugins/marketplace.json` and
  `.claude-plugin/marketplace.json`.
- The installable plugin bundle lives in `plugins/path-to-academia/`.
- The root package and plugin bundle are both expected to work. When changing runtime code, docs,
  scripts, manifests, examples, or skills, keep the bundle in sync.
- The public CLI package lives in `src/path_to_academia/`.
- The agent workflow lives in `skills/path-to-academia/SKILL.md`.

## Release Gate

Before claiming the repo is publishable, run:

```bash
python3 scripts/check_release.py
```

This gate validates tests, compilation, workspace QA, wrapped XLSX export, root and bundle plugin
metadata, Codex and Claude Code installation flows when local CLIs are available, bundle runtime
smoke, package build, wheel install, i18n consistency, and stale private-domain residue.

## Editing Rules

- Preserve the separation between public fact tables and private outreach state.
- Treat blank enrichment as unknown or not collected, not negative evidence.
- Keep examples generic in product meaning. Demo rows may be real, but their source scope and
  verification limits must be explicit, and the default biology demo must not imply that biology is
  the product's only supported domain.
- Do not add generated files, build artifacts, caches, `.egg-info`, `__pycache__`, or local
  workspaces to the repository.
- Do not add tests that lock in user-customizable domain content. Tests should guard generic
  behavior, schemas, packaging, UI mechanics, and privacy boundaries.
- If UI copy changes, update `src/path_to_academia/webui/static/i18n.json` consistently across all
  supported languages and keep sourced record data untranslated.

## Installation Contract

The public install path is native marketplace registration, not shell scripts:

```bash
codex plugin marketplace add ZimoLiao/path-to-academia
codex plugin add path-to-academia@path-to-academia
```

Claude Code:

```text
/plugin marketplace add ZimoLiao/path-to-academia
/plugin install path-to-academia@path-to-academia
```

`install.sh` and `install-claude.sh` are local convenience wrappers only.
