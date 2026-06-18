# Large Collection Playbook

Use this playbook when a workspace needs hundreds of academic people, groups, or opportunities.
It generalizes lessons from prior large agent-run collection projects.

## Operating Principle

Build an auditable extraction system before building a ranking system. The first useful deliverable
is not a shortlist; it is a set of durable source records, review queues, merge rules, and QA
counts that can survive context compaction and future agent handoff.

## Collection Layers

Keep these layers separate:

- `raw/source_records.csv`: one row per source observation.
- shard files under `raw/shards/` or `tables/shards/`: per-worker or per-source-batch outputs.
- `tables/entities_review_or_excluded.csv`: ambiguous, adjacent, weak, stale, duplicate, or
  manually rejected records.
- `tables/entities_final.csv`: deduped public fact table after identity and relevance checks.
- `tables/positions_current.csv`: current opportunity records with retrieval dates and deadlines.
- `audit/`: source limitations, false positives, merge choices, QA reports, and next passes.

Do not collapse these layers into a single spreadsheet. A single table hides provenance and makes
later repair expensive.

## Source Expansion Pattern

Treat any seed roster, spreadsheet, or user-provided list as one provenance source, not as a
coverage boundary.

Before source expansion, confirm high-signal prioritization inputs with the user as separate
questions:

- exact target venues, usually a short list rather than a full field bibliography
- related venue families that count as adjacent evidence
- honor sources for reverse discovery, such as awards, medals, fellowships, academies, invited or
  keynote lists, editorial boards, and committees
- identity-link sources to collect, including Google Scholar author pages when the user cares about
  them
- any other constraints or things to emphasize, avoid, or handle carefully

Do not auto-fill broad target-venue or honor-source lists from field assumptions. If defaults are
needed, propose a compact provisional list and record that it was not user-confirmed.

Keep source-batch accounting from the first pass. Every source family should have a batch name,
row count, retrieval date, access method, and caveat in `audit/`. If a table is mostly seed data,
say so explicitly and continue expanding independent sources.

Run independent source-family passes:

- official department, institute, center, lab, and program directories
- journal, venue-family, proceedings, special-issue, and editorial-board passes
- conference, workshop, keynote, program-committee, and society passes
- award, medal, fellowship, academy, and invited-lecture reverse-discovery passes
- funder project databases, grant rosters, fellowship calls, and hiring pages
- job boards and university HR pages for current roles
- local application folders or user notes as additional provenance, never as the only source

When the user supplies must-include examples, use them as sentinel coverage checks. If a sentinel is
missing, expand the source strategy instead of defending the partial pass.

Record sentinel checks in `configs/domain.json`. A sentinel can be a known person, group, role,
venue, institution, or source family that the final database must include or explicitly explain.
Fail the pass when a sentinel is absent, misclassified, or downgraded without an audit note.

## Incremental Persistence

Write data before browsing more. A good loop is:

1. Open or query one source family, source page, or small batch.
2. Extract source rows and candidate rows.
3. Put weak or unclear records into review output.
4. Write an audit note with URLs, retrieval date, method, limits, and unresolved questions.
5. Continue to the next batch.

Do not hold many pages in chat context waiting for final synthesis. Long sessions can compact; open
tabs and memory are not durable artifacts.

## Sharding Pattern

For large reverse-discovery or profiling passes:

- split candidates into stable input shards with a fixed schema
- divide candidates into `profile_now` and `review` queues instead of forcing one confidence bucket
- give each worker one source-derived queue, one input shard, and one output schema
- require each worker to write the shard CSV and list records needing main-agent review
- merge only after schema validation, row-count checks, duplicate checks, and spot review
- keep the unmerged shard outputs as provenance

Workers should not be asked to "find good people" from scratch when a source-derived queue already
exists. Give them bounded rows to profile, not vague discovery authority. Workers should not make
final inclusion decisions silently. The main agent owns merge, deduplication, quality gates, and
user-facing synthesis.

Useful worker validation rules:

- output CSV is readable with Python `csv`
- output header exactly matches the provided schema
- output row count matches input row count or explains every missing row
- each row has source URLs and verification notes
- scraped list names are normalized to person or group names only
- original award, citation, role, or source-list text is preserved in evidence fields
- unknown metrics or publication evidence remain blank with notes
- ambiguous publication or identity matches are marked for manual review

## Identity And Metrics

Do not enrich by name alone. Use official profiles, persistent IDs, author pages, affiliation
history, lab pages, and publication corpora to verify identity.

For metrics:

- record the metric source and retrieval date
- use conservative matching by name, institution, field, and citation scale
- leave blanks when a reliable match is unavailable
- write rate limits and failed API passes into `audit/`
- design enrichment scripts with offsets, limits, shards, and rerun-safe outputs

High-throughput APIs are useful, but aggressive concurrency can reduce coverage if it triggers rate
limits. Prefer small bounded concurrency, caching, resume points, and source-specific fallbacks.

## Publication Evidence

Publication signals are prioritization evidence, not proof that someone lacks impact.

Use author-identity-backed sources when possible. Name-only publication search is especially risky
for common names and cross-field surnames. Keep unverified hits in a review table rather than
turning them into final flags.

Good publication passes produce:

- raw paper rows
- per-entity summaries
- exact target-venue flags
- related venue-family flags
- a manual-check table for ambiguous matches
- notes explaining API limits and false-positive patterns

Do not infer a negative publication signal from missing enrichment.

Rejected or unsafe evidence paths should stay documented. For example, if a source creates
name-only false positives, keep its output as review/provenance or discard it with an audit note;
do not silently reuse it for final flags.

## Current Positions

Open roles are time-sensitive. For each current opportunity, record:

- source URL
- retrieval date
- open/closed/unknown status
- deadline and timezone if stated
- host group or PI when available
- eligibility, location, visa, funding, duration, and language constraints
- how the source was accessed: direct HTML/API, rendered page, search result, or blocked source

If a site is Cloudflare-protected or JavaScript-heavy, record that limitation and use search/open
verification or other official mirrors. Do not claim a full scrape when only snippets or pages were
available.

## Quality And Handoff

Before calling a large pass ready, check:

- row counts by source batch
- blank required fields
- duplicate normalized identities
- enrichment coverage for identity links and evidence fields, especially requested fields such as
  `scholar_url`, `homepage_url`, `honors`, and `target_publication_evidence`
- unmatched private status rows
- review/excluded counts
- metric coverage and missing-metric exceptions
- current-position retrieval dates and deadlines
- publication evidence manual-check counts
- wrapped XLSX readability if the user will inspect in Excel

Before resuming or rerunning after compaction, check existing shard files, offsets, logs, and running
processes. Do not overwrite a completed shard just because the chat forgot it.

Finish by writing what future agents need to know: what worked, what failed, what was rate-limited,
what sources were blocked, which aliases or duplicates were manually resolved, and what source
families remain.
