# Sharded Agent Work

path to academia supports multi-agent collection by treating each pass as a shard with a
clear input, output, and audit note. Shards should be mergeable without relying on hidden chat
context.

## Default Parallelism

Parallel sharding is the default after Guided Intake. The agent should quietly use the maximum
available subagent capacity the current environment supports, rather than making the user request
parallel work explicitly.

Apply these rules:

- Split source collection and enrichment into independent shards before dispatch.
- Use as many subagents as the harness can practically run, bounded by source rate limits, tool
  availability, and clean merge boundaries.
- Keep one main agent responsible for coordination, merge, deduplication, QA, exports, and final
  reporting.
- If subagents are unavailable, run the same shard plan sequentially and record the limitation in
  `audit/`.
- Do not let workers edit `ui_state/` or private outreach fields.
- Prefer source-derived queues with a fixed schema over vague "find good candidates" worker tasks.

## Incremental Persistence

Workers must not browse a large result set and keep findings only in chat context. Each worker
should collect one source or small batch, write rows, record unresolved questions, and only then
move to the next source. This protects the project from context compaction and makes partial work
recoverable.

Preferred shard artifacts:

- `raw/shards/<batch>_source_records.csv`
- `tables/shards/<batch>_entities_candidates.csv`
- `tables/shards/<batch>_review_or_excluded.csv`
- `tables/shards/<batch>_positions_current.csv`
- `audit/<batch>_notes.md`

If a worker cannot write files, it should return compact machine-readable rows for the batch and
stop before opening more sources. The main agent should persist those rows before dispatching a
continuation.

Before resuming a shard after context compaction, inspect existing shard files, offset logs, and
running processes. Continue from the latest durable artifact; do not rerun or overwrite completed
work blindly.

## Shard Contract

Each worker should produce:

- a source batch name
- raw source rows
- candidate entity rows
- review or excluded rows
- source URLs and retrieval timestamps
- identity evidence used
- unresolved questions
- an audit note describing method, coverage, and limits

Worker output must validate before merge:

- CSV header matches the assigned schema exactly
- row count matches the input shard or missing rows are explained
- every included row has source URLs and verification notes
- uncertain identity, metrics, publication evidence, or relevance is marked for review
- source-list text embedded in a name field is moved to an evidence or notes field

## Suggested Shards

- source directory crawl
- award or keynote reverse-discovery pass
- publication venue author pass
- open position board pass
- metric enrichment pass
- identity resolution pass
- deduplication and merge pass
- final QA and export pass

## Merge Rules

- Merge by verified identity, not by name alone.
- Keep separate rows when identity is ambiguous.
- Preserve all source URLs and source names.
- Move weak candidates into review output instead of deleting them.
- Record manual decisions in `audit/`.

## Worker Prompt Template

```text
You are working on path to academia shard: <batch-name>.
Use configs/domain.json for relevance rules.
Write raw evidence rows, candidate rows, review rows, and an audit note.
Do not edit private outreach state.
Do not drop ambiguous records silently.
Do not assign current facts without a current source and retrieval date.
Persist rows after each source or small batch; do not rely on chat context surviving compaction.
```
