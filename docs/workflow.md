# Workflow

path to academia is built around a conservative rule: coverage and evidence come before
ranking. Agents should collect broadly from planned sources, keep review and exclusion trails, and
avoid turning a search into an untraceable shortlist.

## 1. Configure The Domain

Start from `configs/domain.json` and define:

- inclusion terms that make a person, group, or role relevant
- review terms that require manual inspection
- exclusion terms that indicate expired, off-topic, duplicate, or unverified records
- target or impact venues that matter for prioritization
- identity sources accepted for verification
- source passes to run

These terms are project data. Do not bake them into code or schema names.

## 2. Extract Source Records

Write source-level rows into `raw/source_records.csv`. A source row should preserve:

- retrieval timestamp
- source batch name
- source name and URL
- source type
- raw or summarized source text
- extracted name, institution, role, location, and links when available
- extraction method and notes

Good source passes include official group pages, award lists, conference programs, publication
venue sweeps, job boards, funder project databases, institute rosters, and curated directories.

## 3. Verify Identity

Do not merge or enrich by name alone. Prefer at least one credible identity anchor:

- official profile page
- ORCID or other persistent identifier
- institutional profile
- scholarly index author page
- personal or lab website
- publication corpus with matching affiliation history

For common names, require stronger evidence before assigning metrics or publication evidence.

## 4. Classify Explicitly

Every included row in `tables/entities_final.csv` needs:

- `relevance_status`
- `relevance_reason`
- `relevance_evidence`

Rows that are weak, adjacent, ambiguous, duplicated, stale, or off-topic belong in
`tables/entities_review_or_excluded.csv`, not in an untracked scratch file.

## 5. Merge Conservatively

Normalize obvious variants, but avoid aggressive merging when identity evidence is weak. When
merging duplicates:

- preserve all source URLs in `all_source_urls`
- preserve all source names in `all_source_names`
- keep the strongest identity links
- keep audit notes for manual decisions

## 6. Enrich With Current Evidence

Current positions, deadlines, affiliations, metrics, and publication evidence are time-sensitive.
Refresh them from live sources and record `retrieved_at`, source URL, and metric source. If a value
cannot be verified, leave it blank and explain why in `notes` or an audit file.

Do not use a blank enrichment value as negative evidence. Blank means unknown or not collected
unless a source explicitly proves absence.

## 7. QA And Export

Run:

```bash
python3 scripts/qa_workspace.py ./workspace
python3 scripts/export_wrapped_xlsx.py ./workspace/tables/entities_final.csv ./workspace/tables/entities_final_wrapped.xlsx
```

Review `audit/quality_report.json` for row count, blank required fields, duplicate person keys, and
unmatched private status rows.

## 8. Preserve Operational Memory

After a substantial pass, write down:

- source-specific limitations
- false-positive patterns
- identity aliases
- API limits or rate limits
- manual merge decisions
- known gaps and next source passes

Use `audit/` for project-specific notes and update public docs only when the lesson is generally
reusable.
