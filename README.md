# GitHub Repos Asset Catalogue

> [!IMPORTANT]
> This repository is OFFICIAL-SENSITIVE. Handle in line with [HANDLING_INSTRUCTIONS.md](/HANDLING_INSTRUCTIONS.md).

Every UK public sector code project on GitHub, organised for people who don't use GitHub as well as those who do: by topic, organisation, question and capability, in plain English, with the technical detail one click away.

**Status:** a working tool, not an official publication or government policy.

**Access:** this repository is private, for internal government and public sector users only, while it is reviewed. Don't share its contents outside government and the public sector until it is made public.

**Contact:** raise an issue in this repository.

## User guide

New to GitHub? Start here. The guide has three levels, each with steps, the GitHub words you'll meet and links to official guidance, learning and training:

1. [New to GitHub](docs/user-guide/beginner.md): what GitHub is, how to read a project's page, and finding code with this catalogue. No code needed.
2. [Intermediate](docs/user-guide/intermediate.md): judging whether a project is well looked after, issues and pull requests, and what good looks like in government.
3. [Advanced](docs/user-guide/advanced.md): security and automation, moving repositories between organisations, and reusing the catalogue's data.

[Guided tours and tutorials](docs/user-guide/tours.md): six tours, one for each persona, follow their journeys through the catalogue, and nine short tutorials each walk through one task.

The same guide, the tours and the tutorials are in the catalogue itself, under Home, User guide. Hover over or tab to any section button, or any dotted-underlined word, for a short explanation.

## What's in it

- **The briefing:** one page for people who don't use GitHub: what the catalogue holds, what it means for them and where to start.
- **Is it part of a live service?** Every project is labelled, in plain words: seen in live operations, likely supports a service, building block, tests and tooling, prototype or experiment, archived, or no longer public. Each label shows its evidence and how accurate the rules were on a random sample (`build/dama/life.py`). Every project also has glance tiles, a list of where to ask about it, and a checklist before reusing it.
- **What government builds on:** 196 government-made components (GOV.UK Frontend, the MOJ and NHS frontends, Notify clients and more) and the public projects that use them, read from their dependency manifests (`build/dama/reuse.py`).
- **Plain English:** view summaries average reading grade 7 (`build/dama/plainlang.py`), and the beginner guide explains GitHub in office terms.
- **User guide, tours and tooltips:** three levels, from new to GitHub to advanced, guided tours for each persona, task tutorials and tooltips throughout, with links to GitHub Docs, GitHub Skills, Microsoft Learn, GOV.UK, the GDS Way and NCSC.
- **Public services:** local public services (social care, housing, waste, planning and 12 more) with the chain of code from the person using the service through councils, central government, the NHS and the voluntary sector to shared platforms and the suppliers named in the code; a social care view; and capability, process and workflow views.
- **Strategic authorities:** England's 22 strategic authorities, established and being created, and the councils inside them that publish code.
- **Crown dependencies:** the Isle of Man Government and the Government of Jersey, found through GitHub's own list of official government accounts, with every repository verified directly against GitHub over git (`build/dama/cdot.py`). No overseas territory account was found; what was searched is listed in the catalogue.
- **Checked against GitHub:** every account in the catalogue read directly from GitHub's own pages on 1 November 2026, with GitHub's own count matched for each account and every repository added, renamed, moved or no longer listed named (`build/dama/ghverify.py`, browser collector in `build/tools/ghcrawl_browser.js`). Only public repositories are kept: the build fails if an internal or private one gets through. Which GitHub features projects switch on (Issues, Projects, Wiki, Discussions) is estimated from a reproducible random sample, with 95% intervals.
- **Beyond GitHub:** which projects are linked from the UK Government Digital and GDS Slack workspaces, in which public channels, and what about: incidents, releases, security, migrations, questions and dependencies (`build/dama/collab.py`). Aggregates only, from what one signed-in person can see: no message text, document titles, names or private channel names, and only public repositories.
- **Personal data:** names quoted from projects' own text are removed (`build/dama/pii.py`) and the build fails if one is found.
- **Department family tree by administration:** central government (with code by sponsoring department), devolved administrations, local government, crown dependencies, overseas territories and other public bodies.
- **Documentation completeness:** what each project has, a four-level bar for what good looks like, and a collector (`build/tools/collect_features.py`, run by the manual "collect GitHub feature settings" workflow) for whether Issues, Projects, Wiki and Discussions are switched on.
- **Explore repos, organised five ways:** by topic, by subject (GOV.UK's 19 top-level topics), by theme, by kind of thing and by who publishes it, with filters and eight ways to group.
- **Explore repos and Search everything:** plain-English cards, topic tiles, everyday-word search with a thesaurus, and one search across projects, organisations, accounts, topics, capabilities, tools, APIs, signals, practices, words and pages.
- **Repo profile:** three reading levels, read-aloud, who it belongs to (up to the sponsoring department), lineage and traceability for every fact, life story, care checklist and connections.
- **Department family tree:** every department and its organisations from GOV.UK's organisations list, down to the GitHub accounts and GDS units where code lives.
- **Insights:** analytics dashboard, DAMA data management wheel, data tools and suppliers, legacy and technical debt.
- **Themes:** guidance, policy and playbooks; public service journeys; devolution and the UK's nations; international work with UK alliances and partners flagged.
- **APIs and open data:** a repository-based API catalogue reconciled with the government API catalogue; open data pipelines.
- **govukOS connections:** an organisation crosswalk from GTI and ANA ids to GOV.UK slugs, feeds and a link scheme.
- **Knowledge layer:** knowledge graph, lineage and traceability from sources to defects, controlled vocabularies and taxonomies (SKOS), ontology (OWL), data dictionary and thesaurus.
- **Service design:** personas, user stories, journeys, service blueprints, processes and workflows ([docs/service-design](docs/service-design/README.md)).
- **co-cddo move:** the workspace for moving repositories out of the co-cddo GitHub organisation.

## Use it

Open [`dist/index.html`](dist/index.html) in a browser. It is one self-contained file: no server, no tracking, no calls to other sites. Links into it: `#repo=<account>/<repository>`, `#org=<GOV.UK slug>`, `#legacy=<GOV.UK slug>`, `#account=<GitHub account>`.

## Build it

```sh
pip install qrcode==8.2 python-barcode==0.16.1
cd build/inv
sh assemble71.sh                     # joins the parts into explorer71.tpl.html
GHRAC_PUBLIC=1 python3 build_v71.py  # embeds data, fonts and test results; writes explorer71_public.html
```

### Deployment settings

Nothing deployment-specific is committed. Set these when building, if needed:

- `GHRAC_URL`: the address the page is served from (used for the QR code and as the base of the JSON-LD identifiers). Defaults to this repository's address.
- `GHRAC_ISSUES_URL`: where the contact links point. Defaults to this repository's issues.
- `GHRAC_OS_LINKS`: path to a JSON file with links to the other govukOS apps, in the form `{"urls": {"gti": "", "liah": "", "ana": "", "mog": "", "measr": "", "cat": ""}, "crosswalk": {"ana": "", "liah": "", "measr": ""}}`. Without it, the govukOS connections view shows each app's name and the route to open, with no link. Keep that file out of the repository.

### What was removed before this repository was created

Personal names (contributors, CODEOWNERS entries, owners and people named in the v1 workbook's actions and evidence), email addresses, team and directorate attributions, links to private apps and design projects, descriptions of internal evidence, and the names of repositories that aren't publicly visible (shown as `unlisted-01` to `unlisted-09`). `build/scan_sensitive.py` checks for these on every build.

The build refuses to finish if a requirement or defect doesn't trace to a registered check (check C-DOC-01). The data scripts in `build/dama` regenerate the datasets from public sources (GitHub listing, git, READMEs and manifests, GOV.UK organisations API, the government API catalogue); run them with `python3 -I`. Raw clones and READMEs are not in this repository.

## Test it

The tests in `build/jt` need Node, jsdom, axe-core and Playwright:

- `t71.js`: the behaviour harness (50 tests), run with jsdom.
- `axe7x.js`: accessibility (WCAG 2.2 A and AA plus best practice) across every view.
- `ovf71.js`: no sideways scrolling at 320, 390, 768 and 1366 pixels.
- `con71.js`: rendered contrast of text on coloured blocks, light and dark.
- The page also runs 43 self-checks every time it opens (About, Method and checks).

Every defect found has a check that fails on the build that had it; see [docs/defects.md](docs/defects.md). Requirements and the checks that prove them: [docs/requirements.md](docs/requirements.md). Releases: [docs/releases.md](docs/releases.md).

## Self-* routines

Built into the page and the repository, and run on every build and every week:

| Routine | What it does | Where |
|---|---|---|
| Self-verification | Every data script writes its checks; the build refuses to finish if any fails, and registers each one with the requirement or defect it guards | `build/dama/*_checks.txt`, `build/inv/build_v71.py` |
| Self-testing | The page re-runs 50 checks in the reader's browser on every load; the harness, accessibility, width and contrast tests run before each release | `v71_js3.part`, `build/jt/` |
| Self-assessment | Checks the repository has what a well-kept GitHub repository needs | `build/tools/self_routines.py` |
| Staleness | Measures each source against its own date and flags it past its limit | `build/tools/self_routines.py` |
| Self-repair | Rebuilds the page and the docs and uploads them; a person reviews and commits | `.github/workflows/self-routines.yml` |
| Self-reporting | Writes the run summary and keeps one "Weekly health" issue up to date | `.github/workflows/self-routines.yml` |
| Self-updating | Collectors refresh the sources: GitHub features over the API (manual workflow), and the signed-in browser crawls for the check against GitHub and the Slack scan | `.github/workflows/collect-features.yml`, `build/tools/ghcrawl_browser.js` |

Automation reads, measures, rebuilds and reports. It never pushes, deletes or publishes.

## Security

Read [SECURITY.md](SECURITY.md) to report a problem. The [threat model](docs/security/threat-model.md) sets out how the catalogue could be misused and what guards against each threat. The [GDS Way assessment](docs/security/gds-way-assessment.md) checks the catalogue against the GDS Way. It also covers what going public would and wouldn't reveal, gds-dtx or alphagov as a home, and timing after GitHub Universe 2026. Decisions are recorded in [docs/adr](docs/adr). The [national security review](docs/security/national-security-review.md) checks the catalogue against government security guidance. Defence, intelligence and national security accounts are listed with what they publish, but the catalogue draws no inferences of its own about them (C-SEC-07). The [release readiness](docs/security/release-readiness.md) assessment covers what stands between this repository and a wider release, and which government account it should live under.

The page carries a Content-Security-Policy and links to no sign-in-only addresses. It shows takeover-prone links as text, and labels accounts that GitHub hasn't verified. These are checked on every build (`build/dama/security.py`, C-SEC-01 to C-SEC-05).

Build the open version with `GHRAC_AUDIENCE=public`. It leaves out the Slack data.

## Limits

- The Slack counts are lower bounds: they count links, not every mention, from what one signed-in person can see. Teams, khub.net, Basecamp and other platforms weren't reachable.
- Public GitHub only. Private and internal repositories, and work held elsewhere, aren't counted.
- Classifications come from names, descriptions, READMEs, file names and dependency names. Text-based ones were checked on samples by Claude, not confirmed by owners; each view shows its accuracy.
- Commercial tools used through their own interfaces rarely leave a trace in public code, so they're under-counted.
- Personas and journeys are proto-personas, not yet tested with users.
- Accounts from outside the government.github.com registry are shown only with a recorded check. Of 15, 11 have no verified domain on GitHub and are labelled as such.
- This public build leaves out personal names (repository contributors and owners from the co-cddo inventory).

## Licence

Code: [MIT](LICENSE). Content and data: [Open Government Licence v3.0](LICENCE-CONTENT.md), except where noted. Fonts: SIL Open Font Licence (see `build/v6/fonts`). GitHub Docs excerpts in `build/gh`: CC BY 4.0, © GitHub, Inc. (see `build/gh/NOTICE.md`).
