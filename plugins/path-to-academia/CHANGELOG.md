# Changelog

## 1.0.0 - 2026-06-17

- Added the initial path to academia package and Codex/Claude Code plugin.
- Added the public `path-to-academia` CLI and `path_to_academia` Python package namespace.
- Added generic workspace scaffolding with ML and biology synthetic example data.
- Added an empty workspace template for real projects after Guided Intake.
- Added source records, final entity tables, review tables, current position tables, audit reports,
  and private outreach sidecar layout.
- Added QA checks for required fields, duplicate person keys, and unmatched private status rows.
- Added wrapped XLSX export without runtime dependencies.
- Added local web UI for browsing records and editing private status sidecars.
- Added static UI localization with a language switcher and a documented boundary that leaves sourced data unchanged.
- Removed default representative-work and citation-rank fields; missing enrichment is treated as
  unknown or not collected, not negative evidence.
- Added native Codex and Claude Code marketplace metadata with a self-contained
  `plugins/path-to-academia` bundle.
- Added one-command local convenience installers for Codex and Claude Code.
- Added public docs, examples, release checklist, contribution guide, security policy, tests, and CI.
