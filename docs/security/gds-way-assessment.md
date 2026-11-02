# Assessment against the GDS Way, disclosure review, home organisation and timing

GHRAC 7.11.0, 2 November 2026. Requirement R64.

This page answers four questions:

1. How well does the catalogue follow the GDS Way?
2. Would going public reveal inner workings that matter only to government and public sector users?
3. Is gds-dtx really a better home than alphagov?
4. Is now the right time, or should we wait until after GitHub Universe?

Every GDS Way finding was checked against the [GDS Way source](https://github.com/alphagov/gds-way) as it stood at commit ff39661 (30 October 2026). Each page's own review date is shown. The facts about organisations were read on GitHub, signed in, on 2 November 2026. Only public facts and counts are recorded here.

## 1. Against the GDS Way

Status key:

- **Meets**: already in place.
- **Fixed today**: fixed in this change.
- **Gap**: still to do, with who owns it.

| GDS Way page (last reviewed) | What it asks | Status | Evidence or action |
|---|---|---|---|
| [How to store source code](https://gds-way.digital.cabinet-office.gov.uk/standards/source-code/) (19 Mar 2026) | A README, informative commit messages, MIT and OGL licence files | Meets | README, LICENSE, LICENCE-CONTENT.md |
| | An email address for security bug reports | **Fixed today** | SECURITY.md now gives the team inbox and the Cabinet Office vulnerability disclosure programme, as well as GitHub's private reporting. |
| | For changes that affect third parties: a changelog, release notes, a public list of known issues, and Semantic Versioning | Meets | docs/releases.md, docs/defects.md, versions 7.x.y. Releases need tagging (an owner action). |
| | Should: a contributing file, and tests in public CI | Meets | CONTRIBUTING.md; the `build` workflow on GitHub Actions |
| [Use GitHub](https://gds-way.digital.cabinet-office.gov.uk/standards/source-code/use-github.html) (19 Jul 2025, review overdue) | Code lives in a GDS organisation under the GDS GitHub Enterprise. Accounts are connected to a GDS or DSIT email, with two-factor authentication. | **Gap (owner)** | The repository is in a personal account. Moving it is ADR 0003. |
| | Consider protecting the main branch | **Gap (owner)** | A settings change, listed in the release-readiness checklist |
| | Archive retired repositories, and explain why in the README | Meets | The catalogue checks this for others. Nothing here is retired. |
| [Using GitHub Actions](https://gds-way.digital.cabinet-office.gov.uk/standards/source-code/using-github-actions.html) (4 Aug 2025) | Pin third-party actions to a full commit SHA; least-privilege permissions; guard against script injection; don't use classic personal access tokens | Meets | C-SEC-05 checks all four on every build. Only GITHUB_TOKEN is used. |
| [Working with Git](https://gds-way.digital.cabinet-office.gov.uk/standards/source-code/working-with-git.html) (18 Feb 2025) | Default branch `main` | Meets | |
| | Short-lived feature branches; commit summaries of 50 characters or fewer | **Gap, rule added today** | All 4 commits so far went straight to `main`, and their summaries run to 69–102 characters. CONTRIBUTING.md now sets the rule. From now on, changes go through branches and pull requests where the session can push them. |
| [Pull requests](https://gds-way.digital.cabinet-office.gov.uk/standards/pull-requests.html) (20 Aug 2026) | Changes are reviewed by someone other than the author | **Gap (owner)** | The catalogue has one maintainer, so it needs an owning team (blocker B1) |
| [Managing sensitive information](https://gds-way.digital.cabinet-office.gov.uk/standards/managing-sensitive-information.html) (1 Oct 2025) | "Public is the default for GDS code." Internal or private repositories must have HANDLING_INSTRUCTIONS.md, plus a banner in the README. | **Fixed today** | HANDLING_INSTRUCTIONS.md (RECIPIENTS ONLY, review in 3 months) and the README banner. The scanner allows the marking only in those two places, and its self-test checks this. |
| [Tracking dependencies](https://gds-way.digital.cabinet-office.gov.uk/standards/tracking-dependencies.html) (22 Sep 2026) | A cooldown period, and an open pull request limit of 10 or more | **Fixed today** | dependabot.yml now has a 7-day cooldown and a limit of 10 |
| [Threat modelling](https://gds-way.digital.cabinet-office.gov.uk/standards/threat-modelling.html) (20 Aug 2026) | A threat model, reviewed each year or on change | Meets, partly | docs/security/threat-model.md. The GDS Way also asks for a team session that scores how hard each attack would be, from 0 to 5. That needs the owning team. |
| [Vulnerability disclosure](https://gds-way.digital.cabinet-office.gov.uk/standards/vulnerability-disclosure.html) (18 Feb 2025, review overdue) | Services publish a `security.txt` that points to the Cabinet Office policy | **Gap, once hosted** | When the page has a host, serve `/.well-known/security.txt` from the central file at vdp.cabinetoffice.gov.uk. |
| [Architecture decisions](https://gds-way.digital.cabinet-office.gov.uk/standards/architecture-decisions.html) | Record decisions in version control | **Fixed today** | docs/adr: 0001 one self-contained page, 0002 two audience builds, 0003 home organisation (proposed) |
| [Naming software products](https://gds-way.digital.cabinet-office.gov.uk/standards/naming-software-products.html) (5 Mar 2026) | A name that describes what the product does | Meets | "GitHub Repos Asset Catalogue" |
| [Programming languages](https://gds-way.digital.cabinet-office.gov.uk/standards/programming-languages.html) (13 May 2026) | Supported languages; Python 3 | Meets | Python 3.12 and JavaScript |
| Service Standard point 12 (make new source code open) | Open by default | **Gap, by decision** | HANDLING_INSTRUCTIONS.md records the reasons it is closed. The open build is ready. |

**Score:** 13 of the 19 rows are met, fully or in part, including 4 fixed today. Of the 6 gaps, 4 need an owner (the organisation, branch protection, a second reviewer, the decision to open). 1 waits for a host (security.txt). The last is a habit to start now: branches and short commit summaries. The scored threat-modelling session, which needs the owning team, is the unmet part of the threat modelling row.

**Two GDS Way pages are out of date.**

- The *Use GitHub* page was due for review in January 2026. It still lists co-cddo, and it doesn't list gds-dtx.
- The *Vulnerability disclosure* page was due for review in February 2026.

A pull request to the GDS Way from the new owning team would bring the organisation table up to date.

## 2. Would going public reveal too much?

Mostly, no. Working in the open is what the GDS Way expects, and most of what looks like inner workings is the kind of material GDS publishes routinely: the check registry, the defect log, the requirements, the threat model and the build scripts. Three layers are different, though. They matter only to government and public sector users, or their owners haven't agreed to them being shared.

| Material | Where | Why it matters only to the target audiences, or isn't agreed | Recommendation |
|---|---|---|---|
| Slack aggregates: link counts, public channel names, topics such as incidents, and the "Seen in live operations" label | `build/dama/collab*.json`, the Beyond GitHub view, the life labels | It shows where internal work happens and which repositories live services lean on. That is useful to colleagues and a target list to an attacker. The workspace owners haven't agreed. | Keep internal. The open build already leaves it out (C-SEC-04). Move it to an internal companion repository. |
| The co-cddo move workspace: proposed destinations, the inventory, the v1 workbook layer, risks and the move plan | `build/v1/`, the co-cddo views | These are plans that haven't been announced or agreed with each repository's owners. That is one of the GDS reasons for keeping code closed. | Keep internal until the owners agree. Then publish the agreed outcome, not the working. |
| How signed-in sessions were used | requirements R57 to R59, the defect V79-2, README "Self-* routines", `build/tools/ghcrawl_browser.js` | It describes one person's sessions being used to read GitHub, Slack. That is accurate and safe as written. But the collector is dual-use: a member could point it at an organisation they belong to. It keeps public rows only (C-GHV-03), and that filter is the safeguard. | Publish the collector with its public-only filter and the negative test. In the open edition, reword the method notes to describe a service account with read-only scopes, once one is used. |
| Practice signals for each repository (security policy, Dependabot, unpinned actions, workflow permissions) | the practice and analytics views | These are public on GitHub, but collecting them in one place makes them easier to use as a target list | An accepted risk (threat model T5). Showing them prompts owners to fix them. |
| Who built it, and how | the colophon, the disclosures | Transparency about AI help is expected | Keep |

**What the open edition looks like:**

- the code, the public GitHub data and the open build
- the user guide, the briefing, the reuse map and the life labels (generalised where they draw on Slack)
- the threat model and this assessment

It holds no internal collaboration data and no unagreed plans. That edition can go public as soon as an owner agrees. The cleanest way to get there is to split the repository (ADR 0002): a public repository, and an internal companion repository for the two closed layers.

## 3. Which organisation: gds-dtx or alphagov?

| | gds-dtx | alphagov |
|---|---|---|
| Who it's for | "the Digital Transformation group within the Government Digital Service at DSIT" (its profile). Its stated purpose includes "improving reuse across services and departments" and "developing shared patterns, guidance and tooling". | "Used by most teams in GDS Digital Products, including GOV.UK and the Products and Services directorate" (the GDS Way) |
| Size | 30 public repositories (GitHub's description). A member sees more, because most of its repositories are internal. | 1,461 public repositories |
| Verified domain | Yes: GitHub shows the verified badge | The check found no badge on its page; confirm this with GitHub |
| In the GDS Way's list | No (the list was last reviewed July 2025) | Yes. It is also covered by the Cabinet Office's GitHub enterprise support agreement. |
| Internal visibility, for an HMG-only release | Already in use | Available under the GDS GitHub Enterprise |
| Named in co-cddo's deprecation notice | Yes | No |
| How easy it is to find | Low. A new, small organisation. | High. The best-known government organisation on GitHub. |
| Fit with the catalogue | Strong. The catalogue is cross-government reuse tooling. | Weaker. The catalogue isn't a GOV.UK product, and sits oddly beside production code. |

**Verdict: gds-dtx is still the better home, on two conditions.**

1. The owning team accepts the catalogue, and the gds-dtx owners agree to hold it.
2. The move waits until the machinery-of-government change has settled which GitHub Enterprise and organisations GDS will use, so the repository moves once.

alphagov wins if the owning team sits in GDS Digital Products, or if being easy to find matters more than fit. Being easy to find can be fixed separately: list the catalogue in the GDS Way, in the x-gov software community, and from GOV.UK's guidance on open source.

## 4. Now, or after GitHub Universe?

GitHub Universe 2026 has already happened: 28 to 29 October 2026, in San Francisco. So there is no event to wait for. What's left is to fold in what was announced.

GitHub's own post lists the Copilot app, Copilot Fusion, Copilot projects, automations and code review Max. A third-party summary lists the security and Actions items. Its statuses still need confirming against GitHub's changelog before anything is adopted.

| Announcement | Reported status | Relevance to the catalogue and to government | Suggested stance |
|---|---|---|---|
| Workflow lockfiles (`actions.lock`), with a "Require lockfile" policy | GA (third-party summary) | Pins the actions that other actions pull in, which closes a gap SHA pinning leaves open | Adopt once confirmed. Extend C-SEC-05 to check it. |
| GitHub Agentic Workflows: Markdown that compiles to Actions, read-only by default, with a threat-detection job | GA (third-party summary) | Could run the weekly self-routines with a plain-English definition | Trial with safeguards, after AI assurance |
| Issue artifacts: Markdown or HTML attached to issues | Public preview | Catalogue views could be attached to the issues where people discuss them | Watch |
| Public monitoring for enterprises: secret leaks anywhere on public GitHub | GA (third-party summary) | Enterprise-wide protection for every government account | Recommend to the GDS enterprise owners |
| AI secret detection in push protection; code scanning for AI applications; Dependabot reachability | Public preview | Useful as government builds more agent code | Watch. Discuss in the Discussions board. |
| Copilot app, Fusion, projects, automations, code review Max; Copilot included with GitHub Enterprise | Announced 28 October; GitHub's post gives no statuses | Big questions about cost, assurance and data handling for every department | Discuss in the Discussions board, not in the catalogue |

**Recommendation: don't wait.** Universe has passed, and none of its announcements changes the catalogue's design.

- **Now:** release internally to HMG, once the owner, home and settings blockers are cleared (B1, B2, B7).
- **Next:** switch on Discussions with a "Feature assessment" category. The form is already in `.github/DISCUSSION_TEMPLATE/feature-assessment.yml`; the owner creates the category. Seed it with one thread for each row above, so departments can assess what Universe means for government.
- **Then:** time the showcase (the deck and the film) to land a week or two after the internal release, with a short "What's new from Universe 2026" segment.
- **The open edition:** follows the agreement steps in section 2. The calendar doesn't drive it.

## Sources

- [The GDS Way](https://gds-way.digital.cabinet-office.gov.uk/) and its [source](https://github.com/alphagov/gds-way), at commit ff39661, 30 October 2026
- [GitHub Universe 2026 schedule](https://github.blog/news-insights/company-news/your-guide-to-github-universe-2026-is-here-the-schedule-just-launched/) (GitHub)
- [GitHub Universe 2026: Evolving every layer of the stack](https://github.blog/news-insights/company-news/github-universe-2026-evolving-every-layer-of-the-stack/) (GitHub)
- [GitHub Universe 2026: what DevOps engineers need to know](https://dev.to/pwd9000/github-universe-2026-what-devops-engineers-need-to-know-1ap9) (a third-party summary; confirm statuses against GitHub's changelog)
- Organisation profiles for gds-dtx, alphagov and co-cddo on GitHub, read on 2 November 2026
