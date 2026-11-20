---
artefact:id: P08-PRD-001
artefact:version: 1.0.0
artefact:as-of: 2026-11-20
artefact:review-date: 2027-02-20
project: P08 GitHub Repos Asset Catalogue
grade: G3
profile: public sector > central > work
---

# Product requirements (PRD): GitHub Repos Asset Catalogue

> **How to read this.** Facts marked V were read from this repository on 20 November 2026. Assumptions, measures and risks are proposals written for this kit, not findings. U means unconfirmed. Where another document in this repository already covers a topic, this one links to it rather than repeating it.

## Problem and outcome
Public bodies rebuild what already exists because they cannot easily find UK public sector code on GitHub or judge whether to reuse it.

Outcome sought: Teams find and reuse existing public sector code before building. See [01-theory-of-change.md](01-theory-of-change.md).

## Users
- People new to GitHub who need to know what exists
- Teams deciding whether to reuse a project
- Policy and service owners looking for the code behind a service

User evidence: [docs/research/README.md](../../docs/research/README.md).

## Scope
**In:**
- Open edition page
- Hubs and filters
- Correction, question and decision forms
- Research bundle

**Out:**
- Tracking users
- Any AI service at runtime
- Slack counts (government edition only)

## Requirements
Derived from what this repository says it does (V: README and ADRs). The last column is the check that proves each one, where one exists. U means no check was found that clearly covers it; that is a gap to close, not a pass.

| ID | Requirement | Priority | Verified by |
|---|---|---|---|
| P08-R01 | One self-contained page, offline-capable (ADR 0001) | Must | build/tools/verify_dist.py |
| P08-R02 | Two audiences: open and government editions (ADR 0002, 0004) | Must | build/tools/check_sisters.py |
| P08-R03 | Home organisation for each repository (ADR 0003) | Must | build/dama/test_rules.py |
| P08-R04 | security.txt (ADR 0005) | Must | build/tools/verify_dist.py (U) |
| P08-R05 | publiccode.yml checked | Should | build/tools/check_publiccode.py |
| P08-R06 | Changes only through GitHub forms | Must | build/tools/check_workflows.py (U) |

## Non-functional requirements
- No network requests after load; no tracking (V: README)
- Accessibility statement (docs/accessibility-statement.md)
- CodeQL, dependency review, Scorecard

## Status
A working tool, not an official publication (V: README)
