# Workflow

path to academia is built around a conservative rule: coverage and evidence come before
ranking. Agents should collect broadly from planned sources, keep review and exclusion trails, and
avoid turning a search into an untraceable shortlist.

For large workspaces that may reach hundreds of records, also use
`docs/collection-playbook.md`. It captures the source-record, sharding, enrichment, publication,
current-position, QA, and handoff patterns needed for long-running collection.

## 1. Configure The Domain

Start from `configs/domain.json` and define:

- inclusion terms that make a person, group, or role relevant
- review terms that require manual inspection
- exclusion terms that indicate expired, off-topic, duplicate, or unverified records
- target or impact venues that matter for prioritization
- identity sources accepted for verification
- source passes to run

These terms are project data. Do not bake them into code or schema names.

## 2. Plan Constraint-Driven Source Passes

Convert constraints into source paths before collecting names. This prevents a workspace from
collapsing into a small keyword-search shortlist.

- Publication constraints: search target journals, venue families, proceedings, special issues,
  editorial boards, and recurring authors.
- Conference or prestige constraints: reverse-scan societies, awards, medals, invited talks,
  keynote lists, program committees, and academy or fellowship rosters.
- Geography or institution constraints: use official department, institute, center, lab, and
  graduate-program directories, including local-language source terms when relevant.
- Current-opening constraints: use job boards, funder project databases, fellowship calls, lab
  hiring pages, university HR pages, and program-specific calls.
- Interdisciplinary constraints: search bridge sources such as centers, review papers, shared
  grants, summer schools, and cross-field workshops.

Keep the pass plan in `configs/domain.json`. Record source-specific gaps in `audit/`; do not let a
missing result from one source become proof that no relevant person, group, or role exists.

## 3. Extract Source Records

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

Persist incrementally. Do not open or read a large collection of pages and wait until the end to
write data. After each source or small batch, write raw rows, candidate/review rows, and an audit
note before continuing. If the work is sharded, each subagent should write or return durable shard
rows before collecting more pages.

Do not treat a seed roster, one spreadsheet, one query, or one database as a coverage guarantee.
Treat it as provenance for one source pass and expand coverage through independent source families.

## 4. Verify Identity

Do not merge or enrich by name alone. Prefer at least one credible identity anchor:

- official profile page
- ORCID or other persistent identifier
- institutional profile
- scholarly index author page
- personal or lab website
- publication corpus with matching affiliation history

For common names, require stronger evidence before assigning metrics or publication evidence.

## 5. Classify Explicitly

Every included row in `tables/entities_final.csv` needs:

- `relevance_status`
- `relevance_reason`
- `relevance_evidence`

Rows that are weak, adjacent, ambiguous, duplicated, stale, or off-topic belong in
`tables/entities_review_or_excluded.csv`, not in an untracked scratch file.

Missing enrichment is not evidence of absence. A blank publication signal, metric, representative
work, or current-opening field means unknown or not collected unless a source explicitly proves the
negative.

## 6. Merge Conservatively

Normalize obvious variants, but avoid aggressive merging when identity evidence is weak. When
merging duplicates:

- preserve all source URLs in `all_source_urls`
- preserve all source names in `all_source_names`
- keep the strongest identity links
- keep audit notes for manual decisions

## 7. Enrich With Current Evidence

Current positions, deadlines, affiliations, metrics, and publication evidence are time-sensitive.
Refresh them from live sources and record `retrieved_at`, source URL, and metric source. If a value
cannot be verified, leave it blank and explain why in `notes` or an audit file.

Do not use a blank enrichment value as negative evidence. Blank means unknown or not collected
unless a source explicitly proves absence.

## 8. QA And Export

Run:

```bash
python3 scripts/qa_workspace.py ./workspace
python3 scripts/export_wrapped_xlsx.py ./workspace/tables/entities_final.csv ./workspace/tables/entities_final_wrapped.xlsx
```

Review `audit/quality_report.json` for row count, blank required fields, duplicate person keys, and
unmatched private status rows.

## 9. Preserve Operational Memory

After a substantial pass, write down:

- source passes completed, skipped, or still needed
- source-specific limitations
- good sources worth reusing and bad sources that caused false positives
- false-positive patterns
- identity aliases
- API limits or rate limits
- query patterns that worked or failed
- manual merge decisions
- known gaps and next source passes

Use `audit/` for project-specific notes and update public docs only when the lesson is generally
reusable.
