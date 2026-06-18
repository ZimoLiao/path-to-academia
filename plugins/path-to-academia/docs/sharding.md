# Sharded Agent Work

path to academia supports multi-agent collection by treating each pass as a shard with a
clear input, output, and audit note. Shards should be mergeable without relying on hidden chat
context.

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
