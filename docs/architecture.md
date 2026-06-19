# Architecture

path to academia is a local-first workflow for coding agents. The product has five layers:

1. **Marketplace metadata** in `.agents/plugins/marketplace.json` and
   `.claude-plugin/marketplace.json`.
2. **Installable plugin bundle** in `plugins/path-to-academia/`.
3. **Agent skill instructions** in `skills/path-to-academia/SKILL.md`, mirrored into the bundle.
4. **Python package and CLI** in `src/path_to_academia/`, with script wrappers in `scripts/`.
5. **User workspace data** created by `path-to-academia init`.

The package has no runtime dependencies outside the Python standard library.

## Agent Flow

The skill starts with Guided Intake. The agent asks for the research direction, opportunity type,
constraints, geographic scope, evidence signals, and output shape before collecting data. Those
answers become `configs/domain.json`, audit notes, and source-pass plans.

The core loop is:

1. Configure the domain.
2. Collect raw source rows.
3. Verify identities and evidence.
4. Merge conservatively.
5. Run QA and write audit notes.
6. Export CSV/XLSX artifacts.
7. Track private outreach state in the sidecar.

For existing workspaces, `path-to-academia context <workspace>` prints the agent-ready context:
project brief, domain terms, evidence settings, source passes, quality counts, workspace file
locations, and privacy boundary. This is the standard context-injection primitive for fresh Codex,
Claude Code, or other coding-agent sessions.

## Data Boundaries

Public facts live in `tables/entities_final.csv`, `tables/entities_review_or_excluded.csv`, and
`tables/positions_current.csv`. Private outreach state lives in `ui_state/outreach_status.csv`.

The boundary is intentional:

- Agents may read both public facts and private status when serving the local UI.
- Agents must not write private fields into public fact tables.
- Blank enrichment fields mean unknown or not collected, not negative evidence.
- Unmatched sidecar rows are preserved and reported rather than deleted.

## Web UI

`path-to-academia serve` starts a local `ThreadingHTTPServer` bound to `127.0.0.1` by default. It
serves static assets and exposes three local JSON endpoints:

- `GET /api/health`
- `GET /api/entities`
- `GET /api/status`
- `POST /api/status`

The UI reads fact rows, joins private status rows by `person_key`, and writes only to the status
sidecar. It does not edit source evidence.

## Packaging

The wheel includes the Python package and static UI assets. The source distribution also includes
root marketplace files, the self-contained `plugins/path-to-academia` bundle, docs, examples,
scripts, tests, CI, and community files so a cloned or downloaded release remains self-contained.

## Quality Gates

The release gate is `python3 scripts/check_release.py`. It verifies tests, Python compilation,
workspace initialization, QA, XLSX export, native marketplace layout, plugin bundle sync, plugin
and skill metadata when local validators are available, context output, package contents, wheel
installation, i18n consistency, and stale private-domain residue.
