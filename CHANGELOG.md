# Changelog

All notable changes to this repository are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/) where the repository publishes versions.

Changes before this file was started are recorded in the git history.

## Unreleased

### Added (repository standards for the move to gds-dtx, 17 November 2026)

- This changelog.
- An exceptions register in `docs/compliance/exceptions.yaml`.
- Pre-commit hooks: detect-secrets against a new `.secrets.baseline`, YAML and JSON checks, whitespace fixes, and gitlint for GDS Way commit messages (`.gitlint`).
- `.secrets.baseline` with every candidate audited, and the audit recorded in `docs/compliance/secrets-audit.md`.

### Changed

- The cleaner expands the old team acronym to Government Data Directorate.
