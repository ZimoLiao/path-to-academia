# Security Policy

path to academia is a local-first tool. It serves a local web UI, reads CSV files from a workspace,
and writes private outreach state to a local sidecar CSV.

## Supported Versions

Security fixes target the latest released version.

## Reporting A Vulnerability

Open a private security advisory on GitHub when the repository is public. If advisories are not
available, contact the repository owner through the GitHub profile listed in the plugin manifest.

Please include:

- affected version or commit
- operating system and Python version
- reproduction steps
- whether the issue can expose local files, private notes, source records, or generated exports

Do not post exploit details in a public issue until the fix is available.

## Scope

In scope:

- local web server path traversal or unsafe file access
- accidental mixing of private outreach state into public fact tables
- unsafe handling of workspace paths or generated files
- packaged artifacts that include private data
- plugin installation behavior that writes an unexpected marketplace entry or points to an
  unexpected local path
- Claude Code marketplace or skills-directory metadata that points to an unexpected local path or
  exposes unintended plugin components
- release artifacts that omit required plugin, skill, or security files

Out of scope:

- vulnerability reports about third-party websites users choose to collect from
- incorrect user-provided source data
- exposure caused by publishing a workspace that intentionally contains private notes

## Supply Chain Notes

Install from a trusted checkout. The public install path uses the agent's native marketplace
commands and points to `./plugins/path-to-academia` inside this repository. The local convenience
scripts wrap the same flow; when a CLI is unavailable, they create a personal local link to the
plugin bundle. Review `install.sh` and `install-claude.sh` before running them in managed
environments.

The release gate checks source distribution contents, wheel contents, and a wheel install smoke
test. It does not sign artifacts in 1.x.
