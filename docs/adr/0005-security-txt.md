# ADR 0005: How the catalogue offers a security.txt

Status: **proposed**. This needs a decision by the repository owner (roadmap item RM-21).

## Context

The GDS Way asks every service to publish `/.well-known/security.txt` that points to the Cabinet Office vulnerability disclosure programme. The catalogue is a GitHub Pages project site, served under `cyberdudeuk.github.io/github-repos-asset-catalogue/`. A project site can only serve files under its own path, so `/.well-known/security.txt` at the root of `cyberdudeuk.github.io` is not ours to publish.

What already points people to the right place:

- SECURITY.md in the repository names the Cabinet Office programme and GitHub's private vulnerability reporting (once RM-14 switches it on).
- The page footer links to the security policy.

## Options

1. **Wait for the move (RM-13).** A GDS organisation's own Pages site, or a custom domain, can serve `/.well-known/security.txt` at its root. One change, done once, when the repository has its permanent home.
2. **A custom domain now.** Needs a domain the owning team controls, DNS changes and a CNAME, and would change again after the move.
3. **A copy under the project path** (`/github-repos-asset-catalogue/.well-known/security.txt`). Scanners and researchers don't look there, so it adds little.

## Proposed decision

Option 1: do it as part of the move to the agreed organisation (ADR 0003). Until then SECURITY.md and the footer carry the route, and the release readiness assessment keeps this as an open item rather than calling it met.

## Consequences

- No new hosting or DNS to look after now.
- The GDS Way point stays open until the move. The roadmap says so.
