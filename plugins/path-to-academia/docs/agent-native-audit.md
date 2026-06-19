# Agent-Native Audit

Date: 2026-06-17

This audit applies the compound-engineering agent workflow principles to path to academia 1.x.

## Score Summary

| Principle | Score | Status | Notes |
|---|---:|---|---|
| Action parity | 5/6 | Excellent | Agents can initialize, inspect context, run QA, export, serve, and update private status. Client-only filter state is not persisted. |
| Tools as primitives | 6/7 | Excellent | CLI commands expose small capabilities. `check_release.py` is intentionally a workflow gate. |
| Context injection | 5/6 | Excellent | `path-to-academia context` provides project, domain, quality, file, and privacy context. Runtime auto-injection depends on the host agent. |
| Shared workspace | 5/5 | Excellent | Agent and user operate on the same CSV workspace and sidecar files. |
| CRUD completeness | 9/12 | Partial | Fact tables are file-editable. Status sidecar has create/read/update, but no dedicated delete command in 1.x. |
| UI integration | 3/4 | Partial | UI writes status sidecar immediately. External agent edits require refresh; there is no file watcher or live reload. |
| Capability discovery | 6/7 | Excellent | README, skill metadata, default prompts, CLI help, docs, issue templates, and context output describe capabilities. No in-app command palette. |
| Prompt-native features | 5/6 | Excellent | Guided Intake and workflow rules live in the skill/docs; stable file and schema contracts remain code-defined. |

Overall score: 44/53, or 83%.

## Public Release Readiness

The project is ready for public agent workflows because it has:

- a single Guided Intake entrypoint for new workspaces
- a context command for fresh agent sessions
- shared local files instead of hidden service state
- a hard public/private data boundary
- CLI and script access to the same core operations
- release checks that validate plugin, skill, package, and workspace behavior

## Follow-Up Candidates

- Add `status-delete` if users need explicit removal instead of status updates.
- Add a UI refresh button or file polling if long-running agents update workspaces while the UI is open.
- Add a hosted demo site or short video walkthrough after public usage clarifies the best examples.
- Add artifact signing or SBOM generation if releases move beyond source distribution and local installs.
