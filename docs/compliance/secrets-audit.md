# Secrets scan audit

Scanned on 17 November 2026 with detect-secrets 1.5.0 over every tracked file (excluding `node_modules`,
`vendor` and lock files). The results are recorded in [`.secrets.baseline`](../../.secrets.baseline).

- Candidates found: 223
- Audited as real secrets: 0

Each candidate was read in context and judged not to be a secret:

Repository full names (`owner/repo`) and declared content hashes in the built catalogue data; placeholder credentials (`test-user`, `PASSWORD`) quoted from other projects' public READMEs in `build/dama/tooling.json`; public GitHub GraphQL node IDs in `build/gh/gei_migrate.md`.

New commits are checked by the detect-secrets pre-commit hook against this baseline. If the hook flags a
new string, read it, and either remove it or audit it into the baseline with `detect-secrets audit .secrets.baseline`.
Never audit a real credential as a false positive: remove it and rotate it.
