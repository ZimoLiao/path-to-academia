# Release Checklist

For a 1.0 release candidate, run the release gate from a clean checkout:

```bash
python3 -m pip install -e ".[dev]"
python3 scripts/check_release.py
```

The same gate is available through `make`:

```bash
make release-check
```

The release gate covers:

- test suite
- Python compilation
- example workspace initialization, context output, QA, and XLSX export
- root marketplace files and `plugins/path-to-academia` bundle layout
- plugin bundle sync against the root source files
- native Codex marketplace install when the local `codex` CLI is available
- plugin and skill validators when local Codex validators are available
- Claude Code plugin validator when the local `claude` CLI is available
- package build and source-distribution content checks
- wheel install smoke test in a temporary virtual environment
- i18n key consistency
- stale private-domain residue checks

Also confirm:

- `.codex-plugin/plugin.json`, `.claude-plugin/plugin.json`, the mirrored manifests in
  `plugins/path-to-academia/`, `.claude-plugin/marketplace.json` metadata, and `pyproject.toml`
  have the same release version.
- `.agents/plugins/marketplace.json` and `.claude-plugin/marketplace.json` both point to
  `./plugins/path-to-academia`.
- README quick-start commands work from a clean checkout.
- Generated caches are not committed.
- Public docs and examples are domain-configurable rather than project-specific.
- No private data is included.
- `.codex-plugin/plugin.json` has no more than three `interface.defaultPrompt` entries.
- The default schema does not imply negative evidence from blank enrichment fields.
- `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, issue templates, PR template, and
  `CITATION.cff` are present before publishing on GitHub.
- `./install.sh` and `./install-claude.sh` both smoke-test successfully from a temporary home
  directory.
