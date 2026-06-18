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
```
