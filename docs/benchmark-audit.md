# Benchmark Audit

Date: 2026-06-17

This audit compares path to academia against mature public plugin, extension, and agent-tool
ecosystem repositories. It is not a feature parity target; it is a release-readiness checklist.

## Reference Projects

- Oh My Zsh: large plugin framework with per-plugin documentation, community health files, and
  install/update conventions.
- Raycast Extensions: extension registry with README, contributing guide, security policy,
  developer documentation, examples, and store-oriented submission boundaries.
- Home Assistant Core: modular integration ecosystem with public architecture references,
  privacy-first positioning, code of conduct, contributing, security policy, and frequent releases.
- Model Context Protocol servers: agent-tool reference implementations with explicit warnings
  about production readiness, contributor docs, code of conduct, security policy, and registry
  guidance.
- Visual Studio Code: extension ecosystem with public community health files, release cadence,
  security guidance, and extension-risk documentation.

## Gap Review

| Area | Mature project pattern | path to academia status |
|---|---|---|
| Quick start | One obvious install and first-run path | Present in README with native Codex and Claude Code marketplace commands |
| Agent onboarding | Suggested prompts or explicit workflow entry | Present through Guided Intake |
| Community health | Code of conduct, contributing, security, issue and PR templates | Added for 1.0.0 |
| Release gate | Single reproducible command for tests, build, and package smoke | Added as `scripts/check_release.py` |
| Architecture | Public architecture or developer docs | Added in `docs/architecture.md` |
| Privacy and security | Clear local data and reporting boundaries | Added in `docs/privacy.md` and `SECURITY.md` |
| Packaging integrity | Manifest coverage and install smoke tests | Covered by release checker, including the `plugins/path-to-academia` bundle |
| Examples | Synthetic example data that does not leak private state | Present in `examples/ml-bio` |
| Extension discovery | Manifest metadata and default prompts | Present in root marketplace files and mirrored plugin manifests |
| Citation metadata | Machine-readable citation for academic users | Added as `CITATION.cff` |
| Agent context | Standard way for a fresh coding agent to load workspace state | Added as `path-to-academia context` |

The agent-native scorecard is maintained separately in [agent-native-audit.md](agent-native-audit.md).

## Intentional Non-Goals For 1.0.0

- Hosted documentation site.
- Signed release artifacts or SBOM generation.
- Screenshot or video demo assets.
- Multi-agent runtime service or hosted database.
- Hardcoded discipline-specific rankings.

These are reasonable follow-ups after the repository is public and real users validate the core
workflow.
