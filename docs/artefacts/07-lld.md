---
artefact:id: P08-LLD-001
artefact:version: 1.0.0
artefact:as-of: 2026-11-20
artefact:review-date: 2027-02-20
project: P08 GitHub Repos Asset Catalogue
grade: G3
profile: public sector > central > work
---

# Low-level design (LLD): GitHub Repos Asset Catalogue

> **How to read this.** Facts marked V were read from this repository on 20 November 2026. Assumptions, measures and risks are proposals written for this kit, not findings. U means unconfirmed. Where another document in this repository already covers a topic, this one links to it rather than repeating it.

## Build and check commands (V: README)
```
python3 -I build/tools/verify_dist.py
python3 -I build/tools/self_routines.py
```

## Scripts (V: file tree)
- `build/tools/check_conflicts.py`
- `build/tools/check_publiccode.py`
- `build/tools/check_sisters.py`
- `build/tools/check_workflows.py`
- `build/tools/collect_decisions.py`
- `build/tools/collect_features.py`
- `build/tools/collect_ideas.py`
- `build/tools/ghcrawl_browser.js`
- `build/tools/js_names.py`
- `build/tools/research_bundle.py`
- `build/tools/self_routines.py`
- `build/tools/test_collect.py`
- `build/tools/verify_dist.py`

## Tests (V: file tree)
- No test files found. Adding tests is an open item.

## Workflows (V: .github/workflows)
- `build.yml`
- `codeql.yml`
- `collect-features.yml`
- `dependency-review.yml`
- `pages.yml`
- `scorecard.yml`
- `self-routines.yml`

## Repository size
392 files tracked on 20 November 2026.

## Documentation kit
- `docs/artefacts/manifest.yaml` lists every core document, where it is, and its review date.
- `tools/artefact_check.py` checks the kit (rules AC-01 to AC-08, each with a negative test). Run `python3 tools/artefact_check.py --self-test` then `python3 tools/artefact_check.py .`.

## Handover
Someone new can rebuild and verify with the commands above, then read [03-prd.md](03-prd.md) and [05-sad.md](05-sad.md).
