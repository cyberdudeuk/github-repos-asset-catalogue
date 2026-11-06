# GitHub Repos Asset Catalogue

**Before you build it, look for it.** This catalogue gathers every UK public sector code project on GitHub in one place, explained in plain English. Use it to find work that already exists, see what any public body publishes, and decide whether you can reuse it. You don't need to know GitHub to use it.

### [Open the catalogue →](https://cyberdudeuk.github.io/github-repos-asset-catalogue/)

It opens in any browser, works on a phone, and doesn't track you. You can also download [`dist/index.html`](dist/index.html) and open it offline.

| | |
|---|---|
| **Status** | A working tool, not an official publication or government policy |
| **Edition** | This is the open edition, for everyone. A government edition, for government and public sector users only, is built from a private companion repository ([ADR 0004](docs/adr/0004-public-and-internal-repositories.md)). It adds counts of where projects are discussed in government Slack workspaces, and the workspace for the proposed co-cddo move. People with access to the companion repository download it from its Actions runs, and record decisions on the move through its issue form |
| **What you need** | A web browser. The catalogue needs no account, licence or sign-in, uses no AI service and makes no network requests once it has loaded. Anything that changes something, such as a correction, a question or a decision, is a GitHub form |
| **Contact** | The [contact form](https://github.com/cyberdudeuk/github-repos-asset-catalogue/issues/new?template=contact.yml) is the only way to reach the maintainers; no email address is published. Messages there are public. For a security problem, follow [SECURITY.md](SECURITY.md) |

## Choose your way in

### 1. How well do you know GitHub?

Pick the row that sounds like you. Each part of this README builds on the one before.

| If you… | You're | Start in the catalogue | Then read |
|---|---|---|---|
| have never used GitHub, or don't write code | **Beginner** | *Start here*, then *Welcome*: "GitHub in two minutes" | [New to GitHub](#beginner-new-to-github) below, and the [beginner guide](docs/user-guide/beginner.md) |
| use GitHub sometimes, or need the catalogue for your work | **Intermediate** | *Find code*, then *Explore repos in plain English* | [Using the catalogue in your work](#intermediate-using-the-catalogue-in-your-work), and the [intermediate guide](docs/user-guide/intermediate.md) |
| work in GitHub every day, or want to build, assure or reuse the catalogue itself | **Advanced** | *About*, then *Method and checks* | [Building, testing and trusting it](#advanced-building-testing-and-trusting-it), and the [advanced guide](docs/user-guide/advanced.md) |

### 2. What kind of work do you do?

The catalogue's home page asks the same question and takes you straight to answers. Each role below has a guided tour in the catalogue: open *Start here*, then the *user guide*, and choose *Guided tours by persona*.

| You are | Your question | Usually | Guided tour, in the catalogue's own words | Where it takes you |
|---|---|---|---|---|
| **Policy lead**: a policy or strategy colleague | Who in government already works on my policy area, before I commission anything? | Beginner | From a policy question to the right team | Start here → Explore repos in plain English → Repo profile → Department family tree |
| **Service owner**: building a public service | What can I reuse (components, APIs, journeys, patterns) before I build? | Beginner to intermediate | Reuse before build | Search everything → API catalogue → Repo profile → Guidance, policy and playbooks |
| **Data leader**: a Chief Data Officer or data governance lead | What does my organisation's data estate look like in code, and where are the legacy and debt? | Intermediate | From estate question to remediation plan | Analytics dashboard → Data management wheel → Legacy and technical debt → Department family tree |
| **Engineering and security lead**: head of engineering, architect or security lead | How well is our code looked after, and where are the risks? | Advanced | Raise the standard of public code | Practice across disciplines → Legacy and technical debt |
| **Cross-government architect**: working across GDS and the govukOS apps | How do I join this catalogue to the shared registers on one key? | Advanced | Join the catalogue to govukOS | govukOS connections → Knowledge layer |

A sixth role, the **repository owner moving from co-cddo**, has its tour in the government edition only, with the move workspace it uses. In this edition, the engineering tour leaves out its GDS Way checks step for the same reason.

The home page's role cards add two more ways in: **leading a department or arm's-length body** (your organisation's estate on a page, compared with peers), and **commercial, finance and spend** (check for existing work before funding a build).

### 3. How the catalogue is laid out

The hubs are in the order most people need them: **Start here**, **Find code**, then the lenses (**Topics and priorities**, **Organisations**, **Public services**, **Data infrastructure**), then **Insights and analytics**, **Good practice** and **Ask**, with **About** last. The [intermediate section](#where-things-are) lists what each hub answers.

---

## Beginner: new to GitHub

### GitHub in two minutes

This is the same introduction the catalogue opens with.

Most public sector code lives on **GitHub**, a website where teams keep the files behind their digital services. Think of it as a shared drive where every change is recorded and every file keeps its history. For public projects, anyone can look.

Four words cover most of what you'll see:

- **Repository (repo):** a shared folder for one project, with every change ever made kept in its history. This catalogue calls them *code projects*.
- **Issue:** a ticket: a question, a problem report or a request, which anyone allowed can comment on.
- **Pull request:** proposed tracked changes, waiting for someone to review and accept them.
- **Fork:** your own copy of someone else's project, which you can change without affecting theirs.

Government publishes its code in the open so other teams can reuse it, rather than pay to build the same thing again. The [Service Standard](https://www.gov.uk/service-manual/service-standard/point-12-make-new-source-code-open) asks for it.

### What the catalogue's home page walks you through

1. **GitHub in two minutes**: the introduction above.
2. **What this catalogue is**: what it holds, with the headline numbers.
3. **Find what already exists**: explore projects in everyday words, search everything, or browse a department's family tree.
4. **What kind of work do you do?**: questions grouped by role, each one a shortcut to its answer.

After that come headlines from the data, the estate at a glance, and a spotlight on recent work.

### Three things to try first

- **Look for something before you build it:** go to *Find code*, then *Explore repos in plain English*, and type what you need in everyday words (for example "book an appointment").
- **See your organisation:** go to *Organisations*, then *Organisation profile*, and pick your department or council.
- **Read one project's story:** open any project to see what it does, whether it's still worked on, who looks after it and whether you can reuse it.

### Keep learning

- [New to GitHub](docs/user-guide/beginner.md): how to read a project's page and find code with this catalogue. No code needed.
- [Guided tours and tutorials](docs/user-guide/tours.md): the persona tours above, and short tutorials that each walk through one task.
- In the catalogue: *Start here*, then the *user guide* and the *Plain-English guide*. Hover over or tab to any dotted-underlined word for a short explanation.

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
| **Ask** | Can I ask in my own words? | Ask a question (answered from the catalogue's data, with no AI), how AI is used here |
| **About** | What is still open, how was this made, and can I trust it? | Roadmap and open items, Knowledge layer, service design, govukOS connections, design, documents, requirements, defects and releases, method and checks, accessibility |

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

Some hosts pass only a plain `#name` to the page; there only the forms in the middle column work, and project links need the file or GitHub Pages.

### Take part

- **Questions and feedback:** use the [contact form](https://github.com/cyberdudeuk/github-repos-asset-catalogue/issues/new?template=contact.yml). Messages there are public, so leave out personal or sensitive information.
- **Corrections:** every project page and organisation profile has *Suggest a correction*, which opens the correction form with the project or organisation filled in. Every view has *Report a problem with this page*.
- **Help measure accuracy:** every project page has *Check a label*, and every organisation profile has *Check this profile*. Answers become the labelled samples that measure how accurate the catalogue's labels are.
- **What's still open:** the [roadmap](docs/roadmap.md) lists every open item, who must act and where it is tracked on GitHub. The same list is in the catalogue, under *About*, then *Roadmap and open items*, with how each part of the catalogue connects to GitHub.
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
- any of its registered checks fails (the build prints how many it ran)

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

- `t71.js`: the behaviour harness, run with jsdom against the government edition. It writes `test_results71.json`, which the build registers.
- `axe7x.js`: accessibility across every view, to WCAG 2.2 A and AA plus best practice.
- `ovf71.js`: checks there's no sideways scrolling at 320, 390, 768 and 1366 pixels.
- `con71.js`: rendered contrast of text on coloured blocks, in light and dark.
- `build/inv/contrast71.py`: contrast of every colour token pair, in light and dark (T-CON-01).
- `build/tools/collect_decisions.py --self-test`: the collector that turns decision issues into the government edition's data (C-DEC-01).
- The page also runs its own checks every time it opens. They're listed, with their current count, under *About*, then *Method and checks*. Some of them guard the open edition and the contact rules:
  - P-53: no link leads to a view this edition leaves out.
  - P-54: hubs and the home page follow the order people meet things.
  - P-13: no AI service or network address is called from the page's code; Ask and the drafts work from the page's own data.
  - P-55: organisation, legacy and account links also work on hosts that pass only a plain `#name`.
  - P-56: contact is through the contact form only, with no email address anywhere.

To check that a copy of the page is the one this repository published, download it and run `gh attestation verify index.html --repo cyberdudeuk/github-repos-asset-catalogue`. The pages workflow records where each published page was built (build provenance). Every pull request also gets a dependency review.

Every defect found has a check that fails on the build that had it; see [docs/defects.md](docs/defects.md). Requirements and the checks that prove them are in [docs/requirements.md](docs/requirements.md). Releases are in [docs/releases.md](docs/releases.md).

### Self-* routines

These are built into the page and the repository, and run on every build and every week:

| Routine | What it does | Where |
|---|---|---|
| Self-verification | Every data script writes its checks. The build refuses to finish if any fails, and registers each check with the requirement or defect it guards | `build/dama/*_checks.txt`, `build/inv/build_v71.py` |
| Self-testing | The page re-runs its checks in the reader's browser on every load. The harness, accessibility, width and contrast tests run before each release | `v71_js3.part`, `build/jt/` |
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

## Help shape the catalogue

We're running user research from November 2026, and the backlog is decided in the open. In the catalogue, open About, then [Help shape the catalogue](https://cyberdudeuk.github.io/github-repos-asset-catalogue/#shape). There you can:

- **Take part in research:** a 45-minute conversation, a session trying the catalogue, an accessibility session, or a journey across the three related portals. [Ask to take part](https://github.com/cyberdudeuk/github-repos-asset-catalogue/issues/new?template=research-signup.yml); the form asks for no personal details.
- **Suggest an idea, or vote for one** with a thumbs-up: [the ideas with the most votes](https://github.com/cyberdudeuk/github-repos-asset-catalogue/issues?q=is%3Aissue+is%3Aopen+label%3Aidea+sort%3Areactions-%2B1-desc).
- **Take the five-minute survey.** Only totals are published, and counts under 5 are hidden.
- **See how we decide:** each idea is scored for value, reach, fit with government strategy and feasibility, in labels on its issue, and capacity decides when. The backlog is checked against the six themes of the roadmap for modern digital government and the DAM Policy, and will be checked against the Strategic Data Roadmap once it is published.

The research bundle is in [docs/research](docs/research/README.md). To make the version for sending by email (Word and PDF files, and the invitation ready to paste), run `python3 -I build/tools/research_bundle.py <folder>`; it needs pandoc and LibreOffice. The invitation contains no address of ours: people reply to whoever sent it.

## Related portals

Two other open projects sit next to this one. Each has its own owner, purpose, audience, licence terms and status, so they are linked, not merged:

| Portal | What it is | Status | When to go there |
|---|---|---|---|
| [DAM capability playbooks](https://cyberdudeuk.github.io/dam-capability-playbooks/) | How to put the government's Data Asset Management (DAM) Policy into practice: requirements, methods, roles, capabilities and change | Prototype guidance, centrally owned; the policy is mandatory for some organisations | To find what the policy asks of an organisation whose estate you are looking at here |
| [Public Sector Data Quality Commons](https://cyberdudeuk.github.io/dq-commons/) | Check, score and improve data quality, with a toolkit, frameworks and community guidance | Community project, open to contributions, voluntary | To act on data quality, or compare catalogue and data quality tools before buying |

The page links back (RM-27): a **Related elsewhere** panel on the Data management wheel, Data tools and suppliers, Data catalogues and standards, and Legacy and technical debt views, and **Related open projects** in the footer, each naming the portal and its status. Links only: the page still makes no network requests.

It uses the sister portals' own keys, so a link from either opens the same thing here:

| Link | Opens | Key from |
|---|---|---|
| `#dama=DM-GOV` (or `#dama-dm-gov`) | The data management wheel on one knowledge area, DM-GOV to DM-DQ | The DAM playbooks and the Commons |
| `#standard=dcat3` (or `#standard-dcat3`) | The standard's row in Data catalogues and standards | The Commons standards catalogue (14 of the 16 standards here; Croissant and LinkML are linked by name) |
| `#org=hm-revenue-customs` | An organisation's family tree | GOV.UK organisation slugs |

The catalogue publishes its keys, organisations and views in [`data/xref.json`](https://cyberdudeuk.github.io/github-repos-asset-catalogue/data/xref.json), in the same shape as the others' manifests. Every week `build/tools/check_sisters.py` reads their manifests and every page linked from here, and reports anything that has moved in the health issue.

The portals share keys so each can link to the same thing in the others: the DAM playbooks publish theirs (DAMA knowledge areas, capabilities, tool categories, roles) in [`data/xref.json`](https://cyberdudeuk.github.io/dam-capability-playbooks/data/xref.json) and the Commons in [`api/xref.json`](https://cyberdudeuk.github.io/dq-commons/api/xref.json). The Commons page [Three portals, one journey](https://cyberdudeuk.github.io/dq-commons/ecosystem.html) compares the three, maps the lineage between them and traces a knowledge area, role or standard through all three. The Commons' [standards catalogue](https://cyberdudeuk.github.io/dq-commons/interop.html#catalogue) links each standard to this catalogue's standards view. Signposts on the remaining views (data tools, legacy) are still on the [roadmap](docs/roadmap.md).

Not sure which of the three you need, or in what order? The [estate compass](https://cyberdudeuk.github.io/dam-capability-playbooks/compass/) is a neutral guide that suggests where to start from your situation and role, and why each step matters.

## Licence

- **Code:** [MIT](LICENSE).
- **Content and data:** [Open Government Licence v3.0](LICENCE-CONTENT.md), except where noted.
- **Fonts:** SIL Open Font Licence (see `build/v6/fonts`).
- **GitHub Docs excerpts in `build/gh`:** CC BY 4.0, © GitHub, Inc. (see `build/gh/NOTICE.md`).
- **Data from other projects:** the X-Gov repo scraper and the UK Public Sector Code by Organisation mapping are both MIT-licensed. Their notices are in [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
