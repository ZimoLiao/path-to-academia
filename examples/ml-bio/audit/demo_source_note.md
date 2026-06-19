# Demo Source Note

Retrieved: 2026-06-19

This demo uses OpenAlex API results for topic `T11289` (`Single-cell and spatial transcriptomics`), filtered to articles from 2021 onward and sorted by OpenAlex citation count. Rows are real people discovered as last-named authors on title-relevant works with OpenAlex author IDs. The title filter required terms such as `single-cell`, `spatial transcriptomics`, `multiomics`, `cell atlas`, `scRNA`, `scATAC`, or related phrases.

Caveats:

- OpenAlex author disambiguation, authorship institution, ORCID, h-index, and citation counts can be incomplete or stale.
- A last-named author is a useful PI-discovery heuristic, not proof of current supervisory role.
- `scholar_url` values are Google Scholar search URLs so the Web UI has a useful one-click entry point; they are not verified author-profile URLs unless a later pass replaces them.
- Age, honors, current openings, and lab homepage fields are intentionally blank unless this demo source pass collected them from reliable public sources.
- Real user workspaces should run official-profile, Google Scholar verification, honors reverse-discovery, and open-position passes after this source layer.
