---
name: path-to-academia
description: Use when building or maintaining an auditable academic opportunity workspace for people, groups, labs, roles, source evidence, quality checks, Excel exports, private outreach state, or the local web UI.
---

# path to academia

## Overview

This skill turns an academic search problem into a source-driven, agent-maintainable workspace:
raw source records, final fact tables, review tables, private outreach state, quality reports,
Excel exports, and a local browsing UI.

Use it for academic people or position discovery across any domain. Do not hardcode a discipline
into schemas, filenames, or public documentation. Put domain-specific inclusion terms, venues, and
source passes in `configs/domain.json`.

## Guided Intake First

For a new workspace, actively ask the user for the research brief before collecting data. Do not
start source collection until the answers are specific enough to configure `configs/domain.json`,
unless the user explicitly asks to use the default example.

Minimum intake:

1. research direction: domain, subdomains, methods, applications, and boundary cases.
2. opportunity type: people, groups, labs, open postdoc roles, fellowships, calls, or a mixed workspace.
3. constraints: geography, institution types, career stage, funding, visa, deadlines, language, and
   must-include or must-exclude rules.
4. geographic scope: countries, regions, institutions, and source languages to include or avoid.
5. evidence signals: target venues, related venue families, awards, metrics, official profiles,
   publication evidence, and freshness requirements.
6. output format: CSV, wrapped XLSX, local UI, audit report, private outreach state, or a publishable
   repository.

After intake, write the assumptions into `configs/domain.json` and keep unclear or disputed rules in
`audit/` so future agents can inspect the decision trail.

Use `--example empty` for real projects after intake. Use `--example ml-bio` only for demos, tests,
or when the user explicitly asks for a starter example.

## Default Parallel Collection

After Guided Intake, plan source passes as independent shards and parallelize by default. Do not
wait for the user to ask for parallelism. Use the maximum number of subagents the current harness
can practically support, bounded by available tooling, source rate limits, and the need for clean
mergeable outputs.

If subagents are available, assign each worker a distinct source pass, direction shard, geography,
venue/award pass, open-position board, or enrichment task. The main agent owns coordination,
deduplication, QA, final exports, and user-facing synthesis. If subagents are unavailable, execute
the same shard plan sequentially and note that limitation in `audit/`.

Load `../../docs/sharding.md` before dispatching workers. Every shard must return source rows,
candidate rows, review/excluded rows, retrieval dates, source URLs, identity evidence, unresolved
questions, and an audit note. Never let parallel workers write private outreach state.

## Quick Start

From the plugin root:

```bash
python3 scripts/init_workspace.py ./my-workspace --example ml-bio
python3 scripts/qa_workspace.py ./my-workspace
python3 scripts/export_wrapped_xlsx.py ./my-workspace/tables/entities_final.csv ./my-workspace/tables/entities_final_wrapped.xlsx
python3 scripts/serve_web.py ./my-workspace --port 8765
```

If the package is installed, the equivalent CLI is:

```bash
path-to-academia init ./my-workspace --example ml-bio
path-to-academia context ./my-workspace
path-to-academia qa ./my-workspace
path-to-academia export-xlsx ./my-workspace/tables/entities_final.csv ./my-workspace/tables/entities_final_wrapped.xlsx
path-to-academia serve ./my-workspace --port 8765
```

## Workflow

1. Load `../../docs/workflow.md` before doing a substantial collection, merge, or rebuild.
2. Load `../../docs/quality-gates.md` before editing canonical CSVs or claiming a workspace is ready.
3. Load `../../docs/sharding.md` when splitting discovery or profiling work across several agents.
4. Use `../../docs/schema.md` from the plugin root when deciding whether a field belongs in the public
   fact table, review table, position table, or private status sidecar.
5. Use `../../docs/localization.md` before changing UI language behavior. Localize static UI labels only;
   do not translate sourced data, CSV headers, or stored status values.

The invariant is: collect broadly, preserve source evidence, verify identity, classify explicitly,
deduplicate conservatively, and rank only after coverage and auditability are acceptable.

At the start of a new agent session on an existing workspace, run:

```bash
path-to-academia context ./my-workspace
```

Use the context output to load the project brief, file locations, quality counts, and private-state
boundary before changing tables.

## Workspace Contract

- `configs/domain.json`: project-specific terms, venues, source-pass plan, and identity sources.
- `raw/source_records.csv`: extracted source evidence and intermediate records.
- `tables/entities_final.csv`: canonical public fact table for people/groups.
- `tables/entities_review_or_excluded.csv`: weak, adjacent, duplicate, outdated, or off-scope records.
- `tables/positions_current.csv`: current opportunity records with retrieval dates.
- `audit/`: quality reports, source-pass notes, merge decisions, false-positive patterns.
- `ui_state/outreach_status.csv`: private status sidecar keyed by normalized `name + institution`.

Never write private status fields into `tables/entities_final.csv`. Status fields include priority,
contact state, contact dates, next action date, and private notes.

## Quality Bar

Before finishing, run at least:

```bash
python3 -m pytest
python3 scripts/qa_workspace.py ./my-workspace
```

For a published or user-facing table, also export a wrapped XLSX and inspect the QA report:

```bash
python3 scripts/export_wrapped_xlsx.py ./my-workspace/tables/entities_final.csv ./my-workspace/tables/entities_final_wrapped.xlsx
cat ./my-workspace/audit/quality_report.json
```

When facts are time-sensitive, browse or use a current API and record `retrieved_at`, source URL,
and metric source. Do not infer current roles, deadlines, metrics, or publication evidence from
memory.
