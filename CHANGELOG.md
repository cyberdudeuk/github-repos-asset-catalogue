# Changelog

All notable changes to this repository are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/) where the repository publishes versions.

Changes before this file was started are recorded in the git history.

## Unreleased

### Added (7.22.0, 20 November 2026)

- The API view shows which government API catalogue entries relate to data exchanges between public bodies, and each entry links to its exchanges (R88). Figures from the Digital Economy Act register are given with their limits. The exchanges come from a pinned copy of the NDL PubSec MCP feed (`build/dama/sources/`), checked by SHA-256 and joined by `build/dama/exchanges.py` (checks C-XCH-01 to C-XCH-05).

### Found

- V722-1: the merged API catalogue records providers as ids in one file and names in the other. The exchanges join handles both; normalising the providers waits for the next refresh.

### Added (repository standards for the move to gds-dtx, 17 November 2026)

- This changelog.
- An exceptions register in `docs/compliance/exceptions.yaml`.
- Pre-commit hooks: detect-secrets against a new `.secrets.baseline`, YAML and JSON checks, whitespace fixes, and gitlint for GDS Way commit messages (`.gitlint`).
- `.secrets.baseline` with every candidate audited, and the audit recorded in `docs/compliance/secrets-audit.md`.

### Changed

- The cleaner expands the old team acronym to Government Data Directorate.
