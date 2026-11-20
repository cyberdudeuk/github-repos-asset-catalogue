---
artefact:id: P08-SAD-001
artefact:version: 1.0.0
artefact:as-of: 2026-11-20
artefact:review-date: 2027-02-20
project: P08 GitHub Repos Asset Catalogue
grade: G3
profile: public sector > central > work
---

# Solution architecture (SAD): GitHub Repos Asset Catalogue

> **How to read this.** Facts marked V were read from this repository on 20 November 2026. Assumptions, measures and risks are proposals written for this kit, not findings. U means unconfirmed. Where another document in this repository already covers a topic, this one links to it rather than repeating it.

## Context
Public bodies rebuild what already exists because they cannot easily find UK public sector code on GitHub or judge whether to reuse it.

The solution is described in [03-prd.md](03-prd.md). It connects with: GitHub API; Private companion repository; gds-dtx organisation.

## Architecturally significant decisions
These are the decisions already recorded in this repository (V):

- [0001-one-self-contained-page.md](../adr/0001-one-self-contained-page.md)
- [0002-two-audiences.md](../adr/0002-two-audiences.md)
- [0003-home-organisation.md](../adr/0003-home-organisation.md)
- [0004-public-and-internal-repositories.md](../adr/0004-public-and-internal-repositories.md)
- [0005-security-txt.md](../adr/0005-security-txt.md)

## Quality attributes

| Attribute | How it is met |
|---|---|
| No network requests after load | No network requests after load; no tracking (V: README) |
| Accessibility statement | Accessibility statement (docs/accessibility-statement.md) |
| CodeQL, dependency review, Scorecard | CodeQL, dependency review, Scorecard |
| Contact | By form only; no email address anywhere (estate rule) |
| Documentation | This kit, checked in CI by `tools/artefact_check.py` |

## Constraints
- A working tool, not an official publication (V: README).
- No personal data unless a DPIA has been done first.
- Contact by form only.

## Risks (proposed ratings)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Crawl misses or misclassifies projects | Medium | Medium | Correction form; spot checks |
| Organisation move changes URLs | Medium | Low | Redirect plan |
