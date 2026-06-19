# Changelog

## 1.0.6 - 2026-06-19

- Added `evidence_items` and `evidence_summary` as the preferred entity fields for concrete,
  filterable evidence labels such as exact journals, conferences, medals, fellowships, academies,
  invited lists, and named programs.
- Added `birth_year`, `age`, `age_as_of`, and `age_evidence` to support public sourced or
  transparently estimated PI age collection, with Web UI age-range filtering.
- Replaced fixed Web UI publication-priority toggles with dynamic evidence-item facets.
- Updated Guided Intake, workflow docs, quality gates, and default prompts so agents ask for named
  evidence filters and age policy before collecting data.

## 1.0.5 - 2026-06-19

- Replaced ambiguous publication-place wording with explicit journal/conference wording across
  Guided Intake, docs, schema descriptions, default prompts, examples, and Web UI labels.
- Kept released compatibility keys such as `target_venues` and `target_venue_exact`, while
  documenting them as compatibility fields.
- Added regression tests so public guidance and UI labels do not drift back to unclear publication
  terminology.

## 1.0.4 - 2026-06-18

- Split Guided Intake evidence setup into separate required questions for exact publication
  priorities, adjacent evidence groups, honor sources, identity-link sources, and open-ended
  additional constraints.
- Clarified that publication-priority lists are user-owned high-signal anchors, not an
  agent-generated full field bibliography.
- Added `related_venue_families`, `honor_sources`, and `constraints.additional_constraints` to
  workspace config and context output.
- Added quality-report enrichment coverage for profile links, Google Scholar links, honors, and
  target-publication evidence.

## 1.0.3 - 2026-06-18

- Added direct profile/source links to result cards so homepage, scholar, ORCID, OpenAlex,
  Semantic Scholar, and primary source URLs are one click away when present.
- Made evidence badges actionable: honors and journal/conference badges now jump to the
  corresponding profile section and briefly highlight the evidence.
- Linkified URLs inside dossier text and rendered source provenance as clickable source links.
- Updated synthetic examples to use more specific honors such as fellowships and medals.

## 1.0.2 - 2026-06-18

- Added the large-collection playbook for source-batch accounting, sentinel checks, staged source
  passes, reverse discovery, shard validation, resumable enrichment, publication-evidence safety,
  current-position capture, QA, and handoff.
- Updated Guided Intake to collect sentinel checks and added `sentinel_checks` to workspace
  configuration.
- Added default `raw/shards/` and `tables/shards/` directories for incremental subagent outputs.
- Strengthened sharding and quality-gate docs so workers persist rows before continuing, validate
  fixed schemas before merge, and do not rely on chat context surviving compaction.

## 1.0.1 - 2026-06-18

- Updated the `path-to-academia` skill to parallelize source collection by default after Guided
  Intake, using the maximum practical subagent capacity available in the current agent harness.
- Documented the default shard contract for parallel workers and the sequential fallback when
  subagents are unavailable.

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
