# Schema

path to academia keeps schemas small and explicit. Fields are generic by design; project
specific meaning belongs in `configs/domain.json`, not in code.

The canonical field descriptions live in `path_to_academia.schemas.FIELD_DESCRIPTIONS`, and tests require
every schema field to have one description. This page explains how to interpret the tables.

## Domain Config

File: `configs/domain.json`

Purpose: project-specific rules that should not become hardcoded schema fields.

Important keys:

- `domain`: inclusion, review, and exclusion terms.
- `constraints`: opportunity types, geography, and open-ended additional constraints.
- `evidence`: target venues, related venue families, honor sources, and accepted identity sources.
- `source_passes`: planned source-family passes with stable batch names.
- `sentinel_checks`: user-provided coverage probes such as must-include people, groups, roles,
  venues, institutions, or source families. Each sentinel must appear in outputs or receive an
  explicit audit explanation.

Keep `target_venues` user-owned and usually short. They are high-signal prioritization anchors, not
a full bibliography for the field. Put adjacent or broader lists in `related_venue_families`, and
put award, medal, fellowship, academy, invited/keynote, editorial-board, and committee sources in
`honor_sources`.

## Raw Source Records

File: `raw/source_records.csv`

Purpose: preserve extracted evidence before final merge decisions. These rows may contain
duplicates, weak candidates, adjacent candidates, or records later moved to review.

Important fields:

- `retrieved_at`: UTC retrieval timestamp.
- `source_batch`: stable source-pass name.
- `source_name`, `source_url`, `source_type`: source provenance.
- `record_type`: source record kind, such as person, group, role, or publication.
- `summary_text`, `keyword_hits`, `raw_text`: extracted evidence. Keyword hits are audit clues,
  not final proof.
- `extraction_method`: how the row was produced.
- `notes`: caveats and source limitations.

For large jobs, shard outputs may be written under `raw/shards/` before merge. Shard files should
use the same fields or a documented fixed schema and remain available as provenance.

## Final Entity Table

File: `tables/entities_final.csv`

Purpose: public fact table for included people or groups. This table should contain sourced facts
and concise relevance evidence only.

Required fields:

- `name`
- `institution`
- `country`
- `summary_text`
- `relevance_status`
- `relevance_evidence`

Evidence fields:

- `domain_tags`: semicolon-separated project tags used by the UI tag tree.
- `target_venue_exact`: `yes` when there is verified evidence in a configured target venue.
- `target_venue_family`: `yes` when there is verified evidence in a related configured venue family.
- `target_publication_evidence`: concise text naming or summarizing the verified target evidence.
- `honors`: awards or recognition relevant to prioritization.
- `metric_source`: source and retrieval context for metrics.

Identity-link fields:

- `homepage_url`: official homepage, lab page, or institutional profile.
- `scholar_url`: Google Scholar or equivalent author page when verified.
- `orcid_url`, `openalex_url`, `semantic_scholar_url`: persistent scholarly profiles when verified.

Classification fields:

- `relevance_status`: classification such as `include`, `review`, `adjacent`, `excluded`, or `stale`.
- `relevance_reason`: short machine-readable reason.
- `relevance_evidence`: human-readable evidence. This is the field that should make inclusion
  auditable without reading the whole raw source.

## Review Or Excluded Table

File: `tables/entities_review_or_excluded.csv`

Purpose: preserve candidates that were weak, ambiguous, duplicate, stale, adjacent, or outside the
project definition. Do not delete these records silently; they are audit evidence.

Per-worker review shards may be staged under `tables/shards/` before merging into this table.

## Current Positions

File: `tables/positions_current.csv`

Purpose: current role or opportunity records. These are time-sensitive and must carry retrieval
dates, source URLs, open status, deadline, constraints, and notes.

## Private Status Sidecar

File: `ui_state/outreach_status.csv`

Purpose: private workflow state. It is keyed by `person_key`, derived from normalized
`name + institution`, and may be read by the local UI. It must not be merged into public fact
tables.

Private fields:

- `status`
- `priority`
- `last_contacted`
- `next_action_date`
- `private_note`
- `updated_at`

## Field Discipline

- Prefer leaving a field blank over guessing.
- Do not treat missing enrichment as negative evidence. A blank field usually means not collected,
  not absent.
- Add source and retrieval context for time-sensitive facts.
- Add a new field only when it removes ambiguity or supports a real workflow.
- When adding a field, update `FIELD_DESCRIPTIONS` and tests in the same change.
