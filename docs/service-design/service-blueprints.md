# Service blueprints

> **Status:** Proto-personas and assumed journeys, written from the requests that shaped the catalogue. Not yet tested with users: research is the first thing to do next.

## B1: Answering 'who already does this?'

| Layer | Ask | Search | Understand | Connect |
|---|---|---|---|---|
| **User actions** | Has a question | Searches or picks a topic | Reads a profile | Raises an issue or contacts the publisher |
| **Front stage (the page)** | Start here, masthead search | Grouped results, thesaurus | Profile: summary, ladder, care, lineage | Links to GitHub, GOV.UK, the repository's issues |
| **Back stage (in the page)** | Search index built in the browser | Ranking, highlighting | Signals joined per repository | Link scheme |
| **Support processes** | Nightly listing (X-Gov scraper) | git checks, README and file reads | Classifiers with precision samples | GOV.UK organisations API |
| **Evidence and checks** | P-41 | T-SRCH-01 | T-RX-02 | T-OS-01 |

## B2: Publishing a new release of the catalogue

| Layer | Gather | Classify | Build | Verify | Publish |
|---|---|---|---|---|---|
| **Maintainer actions** | Runs the data scripts | Reviews precision samples | Runs the build | Runs tests and scans | Publishes the page |
| **Systems** | git clones, manifests, GOV.UK API | Rules with negative tests | build_v71.py assembles the page | jsdom harness, axe-core, Playwright | Artifact and this repository |
| **Checks** | C- checks per dataset | C-TH, C-LEG, C-HIER | C-DOC-01 refuses untraced work | T- tests, T-AXE-01, T-WID-01, T-CON-02 | File hash matches the tested file |
| **Records** | Source dates in the page | Precision tables | Registry of every check | Defect register | Release notes |

## B3: Joining govukOS apps on one organisation key

| Layer | Read | Match | Resolve | Share |
|---|---|---|---|---|
| **Architect actions** | Reads each app's ids | Runs the crosswalk | Reviews unresolved ids | Shares feeds |
| **Front stage** | govukOS connections page | Crosswalk table and search | Reasons for every gap | Downloads and link scheme |
| **Back stage** | GTI and ANA tables copied verbatim | Exact and abbreviation matches only | Hand resolutions with reasons | window.GHRAC_API |
| **Owners needed** | App owners | Organisations register (R3) | R3 owner confirms 105 ANA bodies | Studio issues the identifier (R7) |
