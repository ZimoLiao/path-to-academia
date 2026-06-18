# Localization

path to academia localizes static UI text only. This keeps the product useful across
languages without changing facts, identifiers, or stored workflow values.

## Localized

- panel titles
- filter labels
- sort labels
- button text
- status labels shown in the UI
- priority labels shown in the UI
- empty states and save messages
- dossier section headings
- link labels

## Not Localized

- person names
- institution names
- country values from source data
- `domain_tags` values
- research summaries
- notes
- source names and URLs
- CSV headers
- status values stored in `ui_state/outreach_status.csv`
- priority values stored in `ui_state/outreach_status.csv`

For example, the UI may display `waiting reply` as Chinese, Japanese, French, or another language,
but the saved CSV value remains `waiting_reply`. The same rule applies to priority: the UI label may
be localized, while the stored value remains `high`, `medium`, `low`, or blank.

## Adding A Language

Edit `src/path_to_academia/webui/static/i18n.json`.

Every language must contain the same keys as English. Tests enforce this:

```bash
python3 -m pytest tests/test_web.py::test_static_ui_has_complete_localization_boundary
```

Keep translations concise because dashboard labels must fit in narrow panels.
