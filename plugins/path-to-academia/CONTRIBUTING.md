# Contributing

path to academia is a small, standard-library-first project. Keep changes focused on the generic
academic-opportunity workflow rather than one user's domain.

## Development Setup

```bash
python3 -m pip install -e ".[dev]"
python3 scripts/check_release.py
```

## Design Rules

- Keep public schemas generic and explicit.
- Put project-specific directions, journal/conference lists, keywords, and evidence rules in `configs/domain.json`.
- Do not treat missing enrichment as negative evidence. Blank means unknown or not collected unless
  a source proves absence.
- Keep private outreach state in `ui_state/outreach_status.csv`; never merge it into public fact
  tables.
- Prefer auditable CSV/XLSX artifacts and source URLs over opaque summaries.
- Add tests for stable product contracts, not for user-customizable field choices.
- Keep `path-to-academia context <workspace>` useful for fresh agent sessions.

## Before Opening A Pull Request

Run:

```bash
python3 scripts/check_release.py
```

For fast inner-loop development, run narrower checks first:

```bash
python3 -m pytest
python3 -m py_compile $(find src scripts -name '*.py')
```

Use the GitHub issue templates for bug reports, feature requests, and research workflow gaps. Pull
requests should keep the template checklist intact and explain any skipped release gate.
