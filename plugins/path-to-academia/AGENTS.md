# Agent Guidance For The Plugin Bundle

This directory is the installable `path-to-academia` plugin bundle. It must remain self-contained:
agent manifests, skill instructions, docs, runtime scripts, Python package code, and examples should
work after an agent marketplace installs only this directory.

Do not add generated files, caches, `.egg-info`, `__pycache__`, private workspaces, or
project-specific research data to this bundle.

## Bundle Smoke Checks

From this directory, useful checks are:

```bash
python3 scripts/init_workspace.py /tmp/path-to-academia-bundle-smoke --example ml-bio --force
python3 scripts/qa_workspace.py /tmp/path-to-academia-bundle-smoke
python3 scripts/workspace_context.py /tmp/path-to-academia-bundle-smoke
```

The full repository release gate lives in the repository root as `scripts/check_release.py`; it is
not part of the installed bundle.
