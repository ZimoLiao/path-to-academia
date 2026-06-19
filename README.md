# path to academia

path to academia is a plugin for Claude Code, Codex, and compatible coding agents that helps you
find potential PhD or postdoc supervisors, labs, and open academic positions.

Tell the agent your research direction and constraints; it asks the right questions, searches
current sources, saves a traceable candidate table, and opens a Web UI for review.

The screenshot below uses the built-in real demo: 60 OpenAlex-derived spatial transcriptomics and
single-cell biology candidates, with source links and caveats preserved.

![path to academia biology demo Web UI](docs/assets/path-to-academia-biology-demo.png)

## Getting Started

After installing the plugin, start a new agent session and ask it to use `path-to-academia`.

```text
Use path-to-academia to find postdoc supervisors in computational biology.
Ask me the intake questions first, then create a workspace and collect auditable candidates.
```

The agent should first ask about your field, degree or role type, geography, deadlines, evidence
filters, honor sources, age policy, Google Scholar links, and any extra constraints.
Do not start source collection until the basic brief is clear.

## Quick Example

Try the built-in real biology demo:

```bash
git clone https://github.com/ZimoLiao/path-to-academia.git
cd path-to-academia
python3 -m pip install -e .
path-to-academia init ./workspace --example ml-bio
path-to-academia qa ./workspace
path-to-academia serve ./workspace --port 8765
```

Then open `http://127.0.0.1:8765/`.

The demo is source-limited by design. It is useful for testing the plugin and Web UI, but a real
supervisor search should still verify official profiles, current roles, Google Scholar profiles,
honors, age, and open positions before outreach.

For a real project, start with an empty configurable workspace:

```bash
path-to-academia init ./workspace --example empty
```

## Install

### Claude Code

```text
/plugin marketplace add ZimoLiao/path-to-academia
/plugin install path-to-academia@path-to-academia
/reload-plugins
```

Invoke the skill with:

```text
/path-to-academia:path-to-academia
```

### Codex

```bash
codex plugin marketplace add ZimoLiao/path-to-academia
codex plugin add path-to-academia@path-to-academia
```

If your Codex build installs plugins through the TUI, run `codex`, open `/plugins`, choose the
**path to academia** marketplace, and install **path-to-academia**.

### Local Checkout

```bash
codex plugin marketplace add "$PWD"
codex plugin add path-to-academia@path-to-academia
```

```text
/plugin marketplace add /absolute/path/to/path-to-academia
/plugin install path-to-academia@path-to-academia
/reload-plugins
```

The convenience scripts `./install.sh` and `./install-claude.sh` wrap the same local marketplace
flow for smoke testing.

## What It Creates

`path-to-academia` creates a local workspace with:

| Path | Purpose |
|------|---------|
| `configs/domain.json` | Research direction, constraints, evidence filters, source plan |
| `raw/source_records.csv` | Source-level evidence collected from profiles, lists, papers, and job boards |
| `tables/entities_final.csv` | Candidate supervisors, labs, or groups ready for review |
| `tables/entities_review_or_excluded.csv` | Weak, duplicate, stale, or off-scope candidates kept for audit |
| `tables/positions_current.csv` | Current PhD, postdoc, fellowship, or academic role listings |
| `ui_state/outreach_status.csv` | Private outreach status and notes, kept separate from public facts |
| `audit/` | QA reports, source-pass notes, merge decisions, and coverage gaps |

The local Web UI reads the workspace, lets you filter candidates, and edits only the private status
sidecar.

## Workflow

1. Guided Intake: ask for the research direction, opportunity type, constraints, and output format.
2. Source collection: search official pages, scholarly profiles, named evidence filters, honors,
   conferences, job boards, and user-provided sources.
3. Identity verification: prefer official profiles, Google Scholar, ORCID, OpenAlex, Semantic
   Scholar, lab pages, and persistent source URLs.
4. Evidence fields: write concrete labels such as journal names, conference names, medals, and
   fellowships into `evidence_items`.
5. Age fields: collect `birth_year`, `age`, `age_as_of`, and `age_evidence` only when the source is
   public or the estimate is transparent.
6. QA and export: run quality checks, export wrapped XLSX files, and review candidates in the Web
   UI.

The skill also tells agents to parallelize source passes when possible and to write rows
incrementally instead of browsing many pages before saving data.

## CLI

```bash
path-to-academia init ./workspace --example empty
path-to-academia context ./workspace
path-to-academia qa ./workspace
path-to-academia export-xlsx ./workspace/tables/entities_final.csv ./workspace/tables/entities_final_wrapped.xlsx
path-to-academia serve ./workspace --port 8765
```

You can run the same commands without installing the package:

```bash
python3 scripts/init_workspace.py ./workspace --example ml-bio
python3 scripts/workspace_context.py ./workspace
python3 scripts/qa_workspace.py ./workspace
python3 scripts/export_wrapped_xlsx.py ./workspace/tables/entities_final.csv ./workspace/tables/entities_final_wrapped.xlsx
python3 scripts/serve_web.py ./workspace --port 8765
```

## Documentation

- [Workflow](docs/workflow.md)
- [Collection playbook](docs/collection-playbook.md)
- [Schema](docs/schema.md)
- [Plugin install](docs/plugin-install.md)
- [Quality gates](docs/quality-gates.md)
- [Privacy](docs/privacy.md)
- [Release checklist](docs/release-checklist.md)

## Development

```bash
python3 -m pip install -e ".[dev]"
python3 scripts/check_release.py
```

For faster inner-loop checks:

```bash
python3 -m pytest
python3 -m py_compile $(find src scripts -name '*.py')
```

## Version

Current release: `1.0.6`.

## License

MIT.
