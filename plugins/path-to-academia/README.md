# path to academia plugin

path to academia is a plugin for Claude Code, Codex, and compatible coding agents that helps you
find potential PhD or postdoc supervisors, labs, and open academic positions.

This directory is the installable plugin bundle. The repository root registers it through:

```text
.agents/plugins/marketplace.json
.claude-plugin/marketplace.json
```

The bundle contains:

- `.codex-plugin/plugin.json` for Codex metadata.
- `.claude-plugin/plugin.json` for Claude Code metadata.
- `skills/path-to-academia/SKILL.md` for the agent workflow.
- `docs/` for schema, workflow, privacy, localization, and release notes.
- `scripts/` and `src/` for the local CLI, QA, XLSX export, and web UI.

After installation, invoke the skill as `path-to-academia` in Codex or as
`/path-to-academia:path-to-academia` in Claude Code. Tell it what you want to study and where you
want to apply; it will ask the missing questions before collecting sources.

The Python CLI can also be used directly from this bundle:

```bash
python3 -m pip install -e .
path-to-academia init ./workspace --example ml-bio
path-to-academia context ./workspace
path-to-academia qa ./workspace
path-to-academia export-xlsx ./workspace/tables/entities_final.csv ./workspace/tables/entities_final_wrapped.xlsx
path-to-academia serve ./workspace --port 8765
```

Core documentation:

- `skills/path-to-academia/SKILL.md`
- `docs/workflow.md`
- `docs/collection-playbook.md`
- `docs/schema.md`
- `docs/quality-gates.md`
- `docs/sharding.md`
- `docs/privacy.md`
