# Quality Gates

Use these checks before publishing a table, handing off a workspace, or claiming a collection pass
is complete.

## Required Checks

- `tables/entities_final.csv` exists and has the expected header.
- Required fields are not blank: `name`, `institution`, `country`, `summary_text`,
  `relevance_status`, and `relevance_evidence`.
- Duplicate normalized `name + institution` keys are reviewed.
- `raw/source_records.csv` preserves source URLs and retrieval dates.
- Source-batch counts are reported in `audit/`, including seed-roster share versus independent
  source-family rows.
- Review and excluded rows are preserved in `tables/entities_review_or_excluded.csv`.
- Private outreach state is only in `ui_state/outreach_status.csv`.
- Current facts have current retrieval dates and sources.
- `configs/domain.json` sentinel checks either appear in the outputs or have explicit audit notes.
- `configs/domain.json` records target journals/conferences, related journal/conference families,
  honor sources, and open-ended additional constraints as separate user-owned lists. A target
  journal/conference list should not be auto-filled into a broad field bibliography without user
  confirmation.
- Wrapped XLSX output opens with a frozen header, filters, and wrapped text.
- Blank enrichment fields are treated as unknown or not collected, not as evidence that a person,
  group, or role lacks that attribute.
- QA reports enrichment coverage for important optional fields such as `homepage_url`, `scholar_url`,
  `orcid_url`, `openalex_url`, `semantic_scholar_url`, `honors`, and
  `target_publication_evidence`.
- Source passes cover constraint-derived paths such as journals, conferences, awards, institutions,
  funders, job boards, and bridge sources when those constraints are in scope.
- Substantial passes leave reusable operational memory in `audit/`, including false positives,
  source limits, failed queries, manual decisions, and next source passes.
- Collection writes raw, candidate, review, position, or shard rows incrementally instead of keeping
  evidence only in chat context until the end.
- Shard outputs validate before merge: fixed header, expected row count or explained omissions,
  source URLs, verification notes, and manual-check flags for uncertainty.

## Commands

```bash
python3 scripts/qa_workspace.py ./workspace
python3 scripts/export_wrapped_xlsx.py ./workspace/tables/entities_final.csv ./workspace/tables/entities_final_wrapped.xlsx
python3 -m pytest
```

## Private/Public Boundary

The public fact table may contain sourced facts and audit notes. It must not contain private
outreach fields such as:

- personal priority
- contacted state
- application state
- private notes
- last contact date
- next action date

Those fields belong in `ui_state/outreach_status.csv`, keyed by `person_key`.

## Red Flags

Stop and repair the workflow when:

- a source pass silently drops weak or adjacent records without review output
- a source pass has no source-batch accounting or hides that most rows came from a seed roster
- a sentinel check is absent or downgraded without an audit explanation
- the agent chooses target journals/conferences, related journal/conference families, honor sources, or other constraints
  without asking the user or clearly marking the list as provisional
- `scholar_url` or other requested identity-link fields are blank across the final table without an
  audit note explaining that they were not collected
- metrics are assigned from a name-only search
- missing enrichment is used as a negative filter without an explicit source proving absence
- current roles or deadlines are stated without current sources
- a final table cannot explain why each included row is relevant
- duplicate handling loses source provenance
- the UI writes private state into the fact table
- a workspace relies only on a seed roster, spreadsheet, single query, or single database without
  independent source-family passes
- a substantial pass ends without depositing lessons, gaps, and next actions in `audit/`
- an agent browses many pages before writing rows, risking context compaction before merge or QA
- a resumed session reruns or overwrites completed shards without checking existing files, offsets,
  logs, and running processes
