# path to academia

path to academia is an agent-native workspace and Codex/Claude Code plugin for building audited
academic opportunity databases. It helps agents collect source records, verify identity, merge
people and groups, track current roles, export Excel-friendly tables, and browse records locally
without mixing private outreach notes into public facts.

The default example is intentionally generic: machine learning and biology. The workflow is
configured through `configs/domain.json`, so a new project can define its own inclusion terms,
venues, source passes, and evidence rules without changing the schema.

## Guided Intake For Agents

When a coding agent uses this plugin for a new project, it should start by asking the user for the
basic research brief instead of immediately collecting sources. Do not start source collection until
the answers are clear enough to write or update `configs/domain.json`.

Ask for:

- research direction: field, subfield, methods, application area, and boundary cases.
- opportunity type: people, groups, labs, open postdoc roles, fellowships, calls, or all of these.
- constraints: career stage, institution type, seniority, funding, visa, remote/on-site, deadlines,
  language, or collaboration requirements.
- geographic scope: countries, regions, institutions, and explicit exclusions.
- evidence signals: target venues, related venue families, awards, metrics, official profile types,
  publication evidence, and recency requirements.
- sentinel checks: must-include people, groups, roles, venues, institutions, or source families that
  must appear or receive an explicit audit explanation.
- output format: local UI, CSV, wrapped XLSX, audit notes, private outreach state, or a publishable
  repository.

If the user wants a fast default, initialize the machine-learning-and-biology example and write the
assumptions into `audit/`.

For a real project after Guided Intake, prefer starting from an empty configurable workspace:

```bash
path-to-academia init ./workspace --example empty
```

## What It Gives You

- A reproducible workspace layout for raw evidence, final tables, review tables, audit reports,
  private outreach state, and local UI state.
- A Python CLI with no runtime dependencies beyond the standard library.
- An agent plugin skill that teaches Codex, Claude Code, and compatible tools the collection and QA process.
- CSV and wrapped XLSX exports for human review.
- A local web UI for filtering records and editing private status sidecars.
- Static UI localization for English, Chinese, Japanese, Korean, French, German, Spanish, and Brazilian Portuguese.
- Tests that guard the public package against private-domain residue.

## Quick Start

```bash
git clone https://github.com/ZimoLiao/path-to-academia.git
cd path-to-academia
python3 -m pip install -e .
path-to-academia init ./workspace --example ml-bio
path-to-academia context ./workspace
path-to-academia qa ./workspace
path-to-academia export-xlsx ./workspace/tables/entities_final.csv ./workspace/tables/entities_final_wrapped.xlsx
path-to-academia serve ./workspace --port 8765
```

Then open `http://127.0.0.1:8765/`.

Without installing the package:

```bash
python3 scripts/init_workspace.py ./workspace --example ml-bio
python3 scripts/workspace_context.py ./workspace
python3 scripts/qa_workspace.py ./workspace
python3 scripts/export_wrapped_xlsx.py ./workspace/tables/entities_final.csv ./workspace/tables/entities_final_wrapped.xlsx
python3 scripts/serve_web.py ./workspace --port 8765
```

## Install

### Codex

After the repository is public:

```bash
codex plugin marketplace add ZimoLiao/path-to-academia
codex plugin add path-to-academia@path-to-academia
```

For local development from this checkout:

```bash
codex plugin marketplace add "$PWD"
codex plugin add path-to-academia@path-to-academia
```

After installing, start a new Codex thread and ask it to use `path-to-academia`, or invoke the skill
directly if your Codex UI exposes skill selection. If your Codex build only exposes plugin
installation through the TUI, run `codex`, open `/plugins`, select the **path to academia**
marketplace, and install **path-to-academia**.

### Claude Code

After the repository is public:

```text
/plugin marketplace add ZimoLiao/path-to-academia
/plugin install path-to-academia@path-to-academia
```

For local development from this checkout:

```text
/plugin marketplace add /absolute/path/to/path-to-academia
/plugin install path-to-academia@path-to-academia
/reload-plugins
```

Start Claude Code, or run `/reload-plugins` in an existing Claude Code session, then invoke:

```text
/path-to-academia:path-to-academia
```

### Local Convenience Scripts

The scripts below wrap the same marketplace flow for a local checkout. They are useful for smoke
testing, but they are not the primary public install path.

```bash
./install.sh
./install-claude.sh
```

This repository follows the marketplace layout used by mature agent plugin repos:

```text
.agents/plugins/marketplace.json
.claude-plugin/marketplace.json
plugins/path-to-academia/
  .codex-plugin/plugin.json
  .claude-plugin/plugin.json
  skills/path-to-academia/SKILL.md
```

## Workspace Layout

```text
workspace/
  configs/domain.json
  raw/source_records.csv
  tables/entities_final.csv
  tables/entities_review_or_excluded.csv
  tables/positions_current.csv
  audit/quality_report.json
  ui_state/outreach_status.csv
```

The fact table and private status sidecar are intentionally separate. Agents may read both for the
local UI, but status fields must never be written back into `tables/entities_final.csv`.

For agent handoff or a fresh coding session, print the current workspace context:

```bash
path-to-academia context ./workspace
```

## Core Workflow

1. Define the domain in `configs/domain.json`.
2. Extract source records into `raw/source_records.csv`.
3. Verify identities with official pages, persistent identifiers, scholarly indexes, or credible
   publication profiles.
4. Classify each row as included, review, or excluded with explicit evidence.
5. Merge conservatively and preserve all source URLs and source names.
6. Run QA, regenerate wrapped XLSX files, and write audit notes.
7. Use the UI state sidecar for private outreach progress.

More detail is in [docs/workflow.md](docs/workflow.md).
Field semantics are defined in [docs/schema.md](docs/schema.md).
Localization boundaries are defined in [docs/localization.md](docs/localization.md).
The system architecture is summarized in [docs/architecture.md](docs/architecture.md), and local
data/privacy boundaries are in [docs/privacy.md](docs/privacy.md).

## Repository Quality

- Release checks are listed in [docs/release-checklist.md](docs/release-checklist.md).
- The benchmark against mature plugin and extension repositories is in
  [docs/benchmark-audit.md](docs/benchmark-audit.md).
- The agent-native architecture audit is in [docs/agent-native-audit.md](docs/agent-native-audit.md).
- Contribution rules are in [CONTRIBUTING.md](CONTRIBUTING.md).
- Project conduct rules are in [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
- Security reporting and local-server scope are in [SECURITY.md](SECURITY.md).
- Citation metadata for academic use is in [CITATION.cff](CITATION.cff).
- Changes should preserve the rule that blank enrichment means unknown or not collected, not
  negative evidence.

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

Current release: `1.0.2`.

## License

MIT.
