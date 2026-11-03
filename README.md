# GitHub Repos Asset Catalogue

Every UK public sector code project on GitHub, organised for people who don't use GitHub as well as those who do. Find it by topic, organisation, question or capability. Everything is in plain English, with the technical detail one click away.

**Status:** a working tool, not an official publication or government policy.

**Access:** this repository and its page are public. They hold the open edition of the catalogue. There is also a government edition, built from a private companion repository for government and public sector users. It adds:

- counts of where projects are discussed in government Slack workspaces
- the workspace for the proposed co-cddo move

See [ADR 0004](docs/adr/0004-public-and-internal-repositories.md).

**Contact:** use the [contact form](https://github.com/cyberdudeuk/github-repos-asset-catalogue/issues/new?template=contact.yml). It is the only way to reach the maintainers; we don't publish an email address. For a security problem, follow [SECURITY.md](SECURITY.md) instead.

## Choose your way in

This README is written in three parts. Read the first one that fits you; each part assumes you've read the ones above it.

| You are | Start with | You'll be able to |
|---|---|---|
| **Beginner**: new to GitHub, or you don't write code | [New to GitHub](#beginner-new-to-github) | Understand what GitHub is, open the catalogue and find work related to yours |
| **Intermediate**: you use GitHub, or you need the catalogue for your work | [Using the catalogue in your work](#intermediate-using-the-catalogue-in-your-work) | Judge whether a project can be trusted and reused, compare organisations, and contribute |
| **Advanced**: you build, assure or reuse the catalogue itself | [Building, testing and trusting it](#advanced-building-testing-and-trusting-it) | Rebuild it, run the tests, read its data in open formats and check its security |

The catalogue follows the same order: **Start here**, then **Find code**, then the lenses, the insights, and finally **About**. It also has a [user guide](docs/user-guide/README.md) at all three levels.

---

## Beginner: new to GitHub

### GitHub in two minutes

Most public sector code lives on **GitHub**, a website where teams keep the files behind their digital services. Think of it as a shared drive where every change is recorded and every file keeps its history. For public projects, anyone can look.

Four words cover most of what you'll see:

- **Repository (repo):** a shared folder for one project, with every change ever made kept in its history. This catalogue calls them *code projects*.
- **Issue:** a ticket: a question, a problem report or a request, which anyone allowed can comment on.
- **Pull request:** proposed tracked changes, waiting for someone to review and accept them.
- **Fork:** your own copy of someone else's project, which you can change without affecting theirs.

Government publishes its code in the open so other teams can reuse it, rather than pay to build the same thing again. The [Service Standard](https://www.gov.uk/service-manual/service-standard/point-12-make-new-source-code-open) asks for it.

### What this catalogue does

It brings every public sector code project on GitHub into one place. You can find work related to yours, see what an organisation publishes and spot risks, without needing to use GitHub yourself.

### Open it

Open [`dist/index.html`](dist/index.html) in a browser. It's a single file that works offline, and it doesn't track you.

The page opens on **Start here**, which goes in this order:

1. **GitHub in two minutes**, the same introduction as above.
2. **What this catalogue is**, with the headline numbers.
3. **Find what already exists**: explore projects in everyday words, or search everything.
4. **What kind of work do you do?**, with questions grouped by role: policy, data, leading a department, running a service, security, engineering, and commercial.

### Three things to try first

- **Look for something before you build it:** go to *Find code*, then *Explore repos in plain English*, and type what you need in everyday words (for example "book an appointment").
- **See your organisation:** go to *Organisations*, then *Organisation profile*, and pick your department or council.
- **Read one project's story:** open any project to see what it does, whether it's still worked on, who looks after it and whether you can reuse it.

### Keep learning

- [New to GitHub](docs/user-guide/beginner.md): how to read a project's page and find code with this catalogue. No code needed.
- [Guided tours and tutorials](docs/user-guide/tours.md): tours that follow a persona's journey, and short tutorials that each walk through one task.
- In the page itself: *Start here*, then the *user guide* and the *Plain-English guide*. Hover over or tab to any dotted-underlined word for a short explanation.

---

## Intermediate: using the catalogue in your work

### Where things are

The hubs are in the order most people need them:

| Hub | Answers | Main views |
|---|---|---|
| **Start here** | What is this, and where do I begin? | Welcome, user guide, plain-English guide |
| **Find code** | Does this already exist? | Explore repos in plain English, Search everything, Search all code projects, Repo profile, API catalogue, open data pipelines, websites published from GitHub |
| **Topics and priorities** | What's being built for my policy area? | Browse by topic, what government builds on, government priorities, data and metadata management, guidance and playbooks, public service journeys, devolution, international |
| **Organisations** | What does this body publish, and who does similar work? | Organisation profile, department family tree, GDS estate explorer, all organisations, recent work, strategic authorities |
| **Public services** | Whose code runs this service? | Local public services, social care, capabilities, processes, workflows |
| **Data infrastructure** | What does the UK's public data infrastructure look like in code? | Pan-UK infrastructure, data interoperability, registers and authoritative sources |
| **Insights and analytics** | What's the big picture? | The briefing, analytics dashboard, checked against GitHub, DAMA data management wheel, data tools and suppliers, legacy and technical debt, GDS responsibilities |
| **Good practice** | Is code well looked after? | How well code is looked after, practice across disciplines |
| **Ask AI** | Can I ask in my own words? | Ask a question, how AI is used here |
| **About** | How was this made, and can I trust it? | Knowledge layer, service design, govukOS connections, design, documents, requirements, defects and releases, method and checks, accessibility |

### Judging a project before you rely on it

- **Is it part of a live service?** Every project has one of these labels, in plain words:
  - seen in live operations
  - likely supports a service
  - building block
  - tests and tooling
  - prototype or experiment
  - archived
  - no longer public

  Each label shows its evidence, and how accurate the rules were on a random sample.
- **Can I reuse it?** Glance tiles show the licence, recent activity by people (not bots), whether it has a security contact, and who to ask. A checklist covers what to confirm before you reuse it.
- **What government builds on:** 196 government-made components, such as GOV.UK Frontend, the MOJ and NHS frontends and Notify clients, and the public projects that use them.
- **Treat labels as leads.** Topics and tags come from matching words, and the samples were checked by Claude, not confirmed by owners. Each view says how it found its figures.

### Links you can share

Each view has its own address, such as `#discover` or `#orgs`. These links go straight to one item:

| Link | Also works as | Opens |
|---|---|---|
| `#repo=<account>/<repository>` | (none) | One project |
| `#org=<GOV.UK slug>` | `#org-<GOV.UK slug>` | One organisation |
| `#legacy=<GOV.UK slug>` | `#legacy-<GOV.UK slug>` | One organisation's legacy and technical debt |
| `#account=<GitHub account>` | `#account-<GitHub account>` | One GitHub account |

When the page is opened as a claude.ai artifact, only the plain forms in the middle column work, because an artifact passes only a plain `#name` to the page. Project links therefore need the file or GitHub Pages.

### Take part

- **Questions and feedback:** use the [contact form](https://github.com/cyberdudeuk/github-repos-asset-catalogue/issues/new?template=contact.yml). Messages there are public, so leave out personal or sensitive information.
- **Corrections:** use the *Correct the catalogue* form, or report a defect with the *Defect* form.
- **New GitHub features:** assess whether a GitHub feature fits government use in Discussions, using the *Feature assessment* form. It asks about fit with the GDS Way and NCSC guidance.
- **Contributing:** read [CONTRIBUTING.md](CONTRIBUTING.md). Changes come as pull requests and are checked before they're merged.
- [Intermediate guide](docs/user-guide/intermediate.md): issues and pull requests, judging whether a project is well looked after, and what good looks like in government.

---

## Advanced: building, testing and trusting it

[Advanced guide](docs/user-guide/advanced.md): security and automation, moving repositories between organisations, and reusing the catalogue's data.

### How it's made

- **One page.** The page is a single HTML file assembled from parts in `build/inv` (`v71_*.part`), with its data and fonts embedded. It makes no network calls, and its Content-Security-Policy forbids them.
- **Data scripts.** The scripts in `build/dama` regenerate the datasets from public sources: the GitHub listing, git, READMEs and manifests, the GOV.UK organisations API and the government API catalogue. Run them with `python3 -I`. Raw clones and READMEs are not in this repository.
- **Open formats.**
  - The catalogue's records download as DCAT in JSON-LD, or as CSV, from *Search all code projects*.
  - The *Knowledge layer* view holds the rest:
    - SKOS vocabularies and taxonomies
    - an OWL ontology in JSON-LD
    - the lineage graph in PROV JSON-LD
    - the data dictionary, thesaurus and knowledge graph
- **Service design.** Personas, user stories, journeys, service blueprints, processes and workflows are in [docs/service-design](docs/service-design/README.md).

### Build it

A full build needs the internal-only inputs from the private companion repository (ADR 0004). Without them, the scripts that need no internal input still run, and `build/tools/verify_dist.py` checks the published page.

```sh
pip install qrcode==8.2 python-barcode==0.16.1
export GHRAC_INTERNAL=/path/to/github-repos-asset-catalogue-internal
cd build/inv
sh assemble71.sh                                            # joins the parts into explorer71.tpl.html
GHRAC_PUBLIC=1 python3 -I build_v71.py                      # open edition: explorer71_public.html, published as dist/index.html
GHRAC_PUBLIC=1 GHRAC_AUDIENCE=gov python3 -I build_v71.py   # government edition: explorer71_gov.html, never committed here
```

The build refuses to finish in either case:

- a requirement or defect doesn't trace to a registered check (C-DOC-01)
- any of its 294 registered checks fails

#### Deployment settings

Nothing deployment-specific is committed. Set these when building, if needed:

- `GHRAC_URL`: the address the page is served from. It's used for the QR code and as the base of the JSON-LD identifiers. It defaults to this repository's address.
- `GHRAC_ISSUES_URL`: where issue links point. It defaults to this repository's issues.
- `GHRAC_CONTACT_URL`: the contact form every contact link points to. It defaults to this repository's contact issue form, whose messages are public. When the team has a private contact form (for example on GOV.UK Forms), set this to its address. The build refuses an email address or a `mailto:` link here.
- `GHRAC_OS_LINKS`: the path to a JSON file with links to the other govukOS apps, in this form:

  ```json
  {"urls": {"gti": "", "liah": "", "ana": "", "mog": "", "measr": "", "cat": ""}, "crosswalk": {"ana": "", "liah": "", "measr": ""}}
  ```

  Without it, the govukOS connections view shows each app's name and the route to open, with no link. Keep that file out of the repository.

### Test it

The tests in `build/jt` need Node, jsdom, axe-core and Playwright:

- `t71.js`: the behaviour harness (59 tests), run with jsdom against the government edition. It writes `test_results71.json`, which the build registers.
- `axe7x.js`: accessibility across every view, to WCAG 2.2 A and AA plus best practice.
- `ovf71.js`: checks there's no sideways scrolling at 320, 390, 768 and 1366 pixels.
- `con71.js`: rendered contrast of text on coloured blocks, in light and dark.
- The page also runs 54 self-checks every time it opens. They're listed under *About*, then *Method and checks*. Two of them cover the open edition:
  - P-53 checks that no link leads to a view this edition leaves out.
  - P-54 checks the order people meet things.

Every defect found has a check that fails on the build that had it; see [docs/defects.md](docs/defects.md). Requirements and the checks that prove them are in [docs/requirements.md](docs/requirements.md). Releases are in [docs/releases.md](docs/releases.md).

### Self-* routines

These are built into the page and the repository, and run on every build and every week:

| Routine | What it does | Where |
|---|---|---|
| Self-verification | Every data script writes its checks. The build refuses to finish if any fails, and registers each check with the requirement or defect it guards | `build/dama/*_checks.txt`, `build/inv/build_v71.py` |
| Self-testing | The page re-runs 54 checks in the reader's browser on every load. The harness, accessibility, width and contrast tests run before each release | `v71_js3.part`, `build/jt/` |
| Self-assessment | Checks the repository has what a well-kept GitHub repository needs, and compares its settings with the written baseline | `build/tools/self_routines.py`, `.github/settings-baseline.json` |
| Staleness | Measures each source against its own date and flags it once it's past its limit | `build/tools/self_routines.py` |
| Self-repair | Checks the published page against the code that built it. The private companion repository rebuilds both editions | `build/tools/verify_dist.py`, `.github/workflows/self-routines.yml` |
| Self-reporting | Writes the run summary and keeps one "Weekly health" issue up to date | `.github/workflows/self-routines.yml` |
| Self-updating | Collectors refresh the sources: GitHub features over the API (a manual workflow), and the signed-in browser crawl for the check against GitHub | `.github/workflows/collect-features.yml`, `build/tools/ghcrawl_browser.js` |

Automation reads, measures, rebuilds and reports. It never pushes, deletes or publishes.

### Security

- **Reporting a problem:** read [SECURITY.md](SECURITY.md).
- **Threat model:** the [threat model](docs/security/threat-model.md) sets out how the catalogue could be misused and what guards against each threat.
- **GDS Way:** the [GDS Way assessment](docs/security/gds-way-assessment.md) checks the catalogue against the GDS Way. It also covers what going public reveals, gds-dtx or alphagov as a home, and timing. Decisions are recorded in [docs/adr](docs/adr).
- **National security:** the [national security review](docs/security/national-security-review.md) covers defence, intelligence and national security accounts. They're listed with what they publish, but the catalogue draws no inferences of its own about them (C-SEC-07).
- **Release readiness:** the [release readiness](docs/security/release-readiness.md) assessment covers what stands between this repository and a wider release, and which government account it should live under.
- **Repository settings:** [docs/repo-settings.md](docs/repo-settings.md) says what each setting should be and why.
- **Guards on the page:** the page carries a Content-Security-Policy and links to no sign-in-only addresses. It shows takeover-prone links as text, and labels accounts that GitHub hasn't verified (C-SEC-01 to C-SEC-05).
- **Open edition only:** the published page leaves out the Slack counts and the co-cddo move proposals. C-SEC-04, C-DIST-02 and `build/tools/verify_dist.py` check this. `build/scan_sensitive.py` refuses internal-only files and personal data on every build.

### Limits

- Public GitHub only. Private and internal repositories, and work held elsewhere, aren't counted.
- Classifications come from names, descriptions, READMEs, file names and dependency names. The text-based ones were checked on samples by Claude, not confirmed by owners; each view shows its accuracy.
- Commercial tools used through their own interfaces rarely leave a trace in public code, so they're under-counted.
- Personas and journeys are proto-personas, not yet tested with users.
- Accounts from outside the government.github.com registry are shown only with a recorded check. 11 of those 15 accounts have no verified domain on GitHub, and they're labelled as unverified.
- Personal names (repository contributors and owners) aren't published.

## Licence

- **Code:** [MIT](LICENSE).
- **Content and data:** [Open Government Licence v3.0](LICENCE-CONTENT.md), except where noted.
- **Fonts:** SIL Open Font Licence (see `build/v6/fonts`).
- **GitHub Docs excerpts in `build/gh`:** CC BY 4.0, © GitHub, Inc. (see `build/gh/NOTICE.md`).
- **Data from other projects:** the X-Gov repo scraper and the UK Public Sector Code by Organisation mapping are both MIT-licensed. Their notices are in [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
