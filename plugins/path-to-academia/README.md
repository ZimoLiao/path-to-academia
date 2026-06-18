# path to academia plugin

This is the installable plugin bundle for `path-to-academia`. The repository root registers this
bundle through:

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
`/path-to-academia:path-to-academia` in Claude Code. The skill starts with Guided Intake: it asks
for the research direction, opportunity type, constraints, geographic scope, evidence signals,
sentinel checks, and desired outputs before collecting sources.

The Python CLI can also be used directly from this bundle:

```bash
python3 -m pip install -e .
path-to-academia init ./workspace --example ml-bio
path-to-academia context ./workspace
path-to-academia qa ./workspace
path-to-academia serve ./workspace --port 8765
```

Core documentation:

- [Workflow](docs/workflow.md)
- [Schema](docs/schema.md)
- [Quality gates](docs/quality-gates.md)
- [Privacy](docs/privacy.md)
