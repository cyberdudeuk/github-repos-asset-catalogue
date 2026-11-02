# ADR 0002: Two audience builds from one source

Status: accepted, 2 November 2026

## Context

Some layers of the catalogue suit government and public sector users but shouldn't be published openly yet. These are the Slack and Drive aggregates, and the labels drawn from them. HANDLING_INSTRUCTIONS.md gives the reasons. The GDS Way makes public the default for code.

## Decision

One source produces two builds:

- **gov** (the default): for government and public sector users.
- **public** (`GHRAC_AUDIENCE=public`): the open build. It leaves out everything drawn from Slack and Drive.

`build/dama/security.py` applies the audience. C-SEC-04 proves the result.

## Consequences

- The open build can be published as soon as an owner agrees, without having to fork the code.
- Each new data source must declare which audience it belongs to.
- **Next step:** move the gov-only data out of this repository. The repository and the open build can then be public, as the GDS Way expects. The internal data would live in an internal companion repository.
