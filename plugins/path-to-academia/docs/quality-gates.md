# Quality Gates

Use these checks before publishing a table, handing off a workspace, or claiming a collection pass
is complete.

## Required Checks

- `tables/entities_final.csv` exists and has the expected header.
- Required fields are not blank: `name`, `institution`, `country`, `summary_text`,
  `relevance_status`, and `relevance_evidence`.
- Duplicate normalized `name + institution` keys are reviewed.
- `raw/source_records.csv` preserves source URLs and retrieval dates.
- Review and excluded rows are preserved in `tables/entities_review_or_excluded.csv`.
- Private outreach state is only in `ui_state/outreach_status.csv`.
- Current facts have current retrieval dates and sources.
- Wrapped XLSX output opens with a frozen header, filters, and wrapped text.
- Blank enrichment fields are treated as unknown or not collected, not as evidence that a person,
  group, or role lacks that attribute.

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
- metrics are assigned from a name-only search
- missing enrichment is used as a negative filter without an explicit source proving absence
- current roles or deadlines are stated without current sources
- a final table cannot explain why each included row is relevant
- duplicate handling loses source provenance
- the UI writes private state into the fact table
