---
artefact:id: P08-TOC-001
artefact:version: 1.0.0
artefact:as-of: 2026-11-20
artefact:review-date: 2027-02-20
project: P08 GitHub Repos Asset Catalogue
grade: G3
profile: public sector > central > work
---

# Theory of change: GitHub Repos Asset Catalogue

> **How to read this.** Facts marked V were read from this repository on 20 November 2026. Assumptions, measures and risks are proposals written for this kit, not findings. U means unconfirmed. Where another document in this repository already covers a topic, this one links to it rather than repeating it.

## Problem
Public bodies rebuild what already exists because they cannot easily find UK public sector code on GitHub or judge whether to reuse it.

## Long-term outcome
Teams find and reuse existing public sector code before building.

## Chain

| Inputs | Activities | Outputs | Short-term outcomes | Medium-term outcomes |
|---|---|---|---|---|
| GitHub organisations of UK public bodies; publiccode.yml files; a home-organisation register; the private companion edition's extra signals | Crawl and classify repositories; explain them in plain English; group by hub (find code, topics, organisations, services, data infrastructure); build one self-contained page | dist/index.html (open edition); a government edition from the private repository; research bundle; requirements R1 onward | Users answer 'does this already exist?' in minutes | Documented reuse decisions; fewer duplicate builds |

## Assumptions (proposed; each one testable)

| # | Assumption | How to test it | Evidence today |
|---|---|---|---|
| A1 | Plain-English summaries are accurate enough to decide reuse | Spot-check sample against repositories | Not tested |
| A2 | Two editions serve two audiences without confusion (ADR 0002, 0004) | Research round 1 | Not tested |

## Measures (proposed)
- Every requirement traced (docs/requirements.md)
- Self-routines pass weekly
- Reuse decisions recorded through the form (count only)

No target is set before a baseline exists.

## What would prove this wrong
If users rely on GitHub search alone with the same success, reduce the catalogue to a curated list.

## Status
A working tool, not an official publication (V: README). Live site: https://cyberdudeuk.github.io/github-repos-asset-catalogue/
