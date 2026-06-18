# Agent Guidance For The Plugin Bundle

This directory is the installable `path-to-academia` plugin bundle. It must remain self-contained:
agent manifests, skill instructions, docs, runtime scripts, Python package code, and examples should
work after an agent marketplace installs only this directory.

Before publishing changes from the repository root, run:

```bash
python3 scripts/check_release.py
```

Do not add generated files, caches, `.egg-info`, `__pycache__`, private workspaces, or
project-specific research data to this bundle.
