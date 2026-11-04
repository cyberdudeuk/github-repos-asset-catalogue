# Release readiness: what stands between this repository and a wider release

GHRAC 7.11.0, 2 November 2026. Requirement R63.

**Update, 2 November 2026.** The owner made the repository public, and the material for government and public sector users moved to a private companion repository ([ADR 0004](../adr/0004-public-and-internal-repositories.md)). That resolves B3 and B4 for the public repository: its published page is the open edition, without the Slack counts or the co-cddo move proposals. B12 now applies to the companion, which holds the handling instructions. The repository settings an owner needs to change are in [docs/repo-settings.md](../repo-settings.md). What follows is the assessment as it stood before the change.

The repository is **private** today. It could be released in two ways:

- **Government and public sector only.** This is the gov build, as it is now. It suits a GitHub organisation's "internal" visibility, or a private repository shared with named teams.
- **Fully public.** This is the open build, made with `GHRAC_AUDIENCE=public`. It leaves out everything drawn from Slack.

This page lists what blocks each one, who has to decide, and which GitHub account the repository should live under. Nothing here has been agreed by an owner yet. The recommendations are the author's assessment.

## Blockers

Status key:

- **Done**: built and checked.
- **Owner**: needs a decision or action by the owner. Automation here can't do it, and nobody else should.
- **Open**: work still to do.

| # | Blocker | Government only | Fully public | Status | What clears it |
|---|---|---|---|---|---|
| B1 | **An accountable owner.** A named team, not a person, agrees to own the catalogue, answer issues and review it every quarter. | Needed | Needed | Owner | A team (for example, the GDS team that takes over co-cddo's estate) accepts ownership. The contact form goes in the colophon; no email address is published (R69). |
| B2 | **The home account** (see below). | Needed | Needed | Owner | A transfer by an owner of the destination organisation. Redirects keep old links working. |
| B3 | **Slack aggregates.** These were made from one person's signed-in view, with their agreement only. Before they are shared beyond that person's own organisation, the workspace owners should agree. | Needed for these parts | Left out of the open build | Owner, for the gov build. Done for the open build (C-SEC-04). | The workspace administrators for UK Government Digital and GDS agree to share counts and public channel names. Otherwise, build the gov release with the collab data left out too. |
| B4 | **Proposed destinations in the co-cddo move.** These are the author's proposal, not agreed with the owners of each repository. | Fine if labelled, as it is now | Needs owner agreement or removal | Owner | Owners agree the destinations. Otherwise, publish the move view as "proposed", as it is now, or leave it out of the open build. |
| B5 | **Personal data.** No names, emails or user IDs; contributor and CODEOWNERS names removed. | Done | Done | Done (C-SAN-01, R54) | A data protection screening note from the owner's data protection officer, confirming no DPIA is needed. |
| B6 | **Security review.** Threat model, guardrails and checks. | Done | Done | Done (C-SEC-01 to C-SEC-05, P-52) | An independent review by the owner's security team before a fully public release (see the threat model's medium risks). |
| B12 | **GDS Way handling instructions** for a repository that isn't public | Needed | Not needed once public | Done (C-SEC-06) | Review by 2 February 2027, or sooner if the repository is moved or opened. |
| B7 | **Repository settings** that automation here is not allowed to change. | Needed | Needed | Owner | The settings checklist below. |
| B8 | **Accessibility statement.** The page is tested against WCAG 2.2 AA (axe, contrast, widths, keyboard). | Recommended | Needed for a public service | Draft published (3 November 2026) | The statement is in the catalogue (About, Accessibility) and in docs/accessibility-statement.md, with the tests, known issues and a way to ask for help. It stays a draft until a manual audit (roadmap item RM-04). |
| B9 | **Licences of the sources.** The code is MIT, and the content follows LICENCE-CONTENT.md. The sources are: GitHub (public data, under GitHub's terms), the X-Gov scraper, and the org mapping (MIT). | Done | Done | Done (C-LIC-01) | Checked in full on 3 November 2026. Both the X-Gov scraper and the org mapping are MIT-licensed, and the scraper states no separate licence for its data, so it can be republished with its notice. Both notices are in THIRD-PARTY-NOTICES.md. GitHub's terms allow research use of public information. Bulk crawls should use the API with a service account. |
| B10 | **Signed releases.** Tags and release notes for 7.10.0 and 7.11.0, published from one place. | Recommended | Needed | Owner | Create the releases. The values are in the 7.11.0 hand-over. |
| B11 | **Machinery of government.** GDS and CDDO teams moved to DSIT. Some names and routes in the data may lag behind. | Fine, labelled | Check | Open | A content check by the owner before public release. |

**The shortest route** is a government-only release that holds back the Slack parts. It needs B1, B2 and B7. Everything else in that column is done or only recommended.

## Which GitHub account should it live under?

| Option | For | Against |
|---|---|---|
| **gds-dtx** (recommended) | co-cddo's own deprecation notice names it as a successor ("use another GDS GitHub organisation such as uk-gov-cyber or gds-dtx"). It has a verified domain on GitHub. Most of the catalogue's subject matter, co-cddo's estate, is moving there. | It is a new organisation, so its policies and its team for maintaining the catalogue still need confirming. |
| alphagov | GDS's long-standing organisation, well known and verified. | It holds GOV.UK's production code. A cross-government catalogue that includes internal aggregates sits awkwardly beside it. |
| uk-x-gov-software-community | It is cross-government by design, and is already home to the X-Gov scraper that the catalogue draws on. | It is a community account, not a department's, so it suits only the open build. |
| uk-gov-cyber | Also named in the deprecation notice. | It is for security repositories, and this is not one. |

There are two caveats, which docs/security/gds-way-assessment.md sets out in full. The GDS Way's organisation table hasn't been updated to list gds-dtx (it was last reviewed in July 2025). And the move should wait until the machinery-of-government change has settled which GitHub Enterprise and organisations GDS will use. ADR 0003 records the proposal.

The recommendation is to move the repository to **gds-dtx**, after its owners agree. Use internal visibility for the gov build, if the organisation belongs to a GitHub Enterprise account. Otherwise keep it private and share it with teams. If an open build is agreed later, publish it from the same repository as a GitHub Pages site or a release asset.

## Repository settings checklist (for the owner)

The proxy used to build this blocks settings changes, so an owner needs to set these:

1. **Settings → General**: add the description and topics, and switch off the wiki and projects if they aren't used.
2. **Security**:
   - Switch on private vulnerability reporting, Dependabot alerts and security updates, and secret scanning with push protection.
   - On a public repository, or with Advanced Security, also switch on code scanning. The `codeql.yml` workflow is ready; on a private repository, set the variable `GHRAC_CODE_SCANNING=on` once Advanced Security is available.
3. **Rules → Rulesets for main**:
   - Require a pull request with one approval from CODEOWNERS.
   - Require the `build` check to pass.
   - Block force pushes and deletion.
   - Require signed commits.
4. **Actions → General**:
   - Allow only actions from GitHub and verified creators, pinned by SHA.
   - Give workflows read-only permissions by default.
   - Require approval for workflows from outside collaborators.
5. **Collaborators and teams**: give access to teams, not individuals. Keep at least two admins, from the owning team.
6. **Releases**: tag v7.10.0 and v7.11.0 from the commits in `docs/releases.md`, and attach `dist/index.html`.

## Trusted, accurate, complete, available, sustainable and scalable: where it stands

| Quality | How it is met | Gap |
|---|---|---|
| Trusted | Every figure has a source and date. Estimates are labelled. 283 build checks and 52 checks in the browser. Account provenance is shown. | An owner's endorsement (B1). Signed releases (B10). |
| Accurate | Reconciled against GitHub on 1 November 2026 (C-GHV-01, C-GHV-02). Labels are sampled for precision. | Labels are estimates. No owner has confirmed them yet. |
| Complete | 24,487 public repositories in 230 accounts, plus 302 found since the catalogue was built, and 1,479 marked as no longer public. | Bodies with no GitHub account, and code on GitLab or Azure DevOps, aren't covered. |
| Available | A single static file, with no server or network needed. It can be saved and used offline. | Hosting. Any static host or GitHub Pages works. Needs a decision under B2. |
| Sustainable | A weekly self-routines workflow rebuilds, checks, flags stale sources and keeps one health issue up to date. The process is documented. | A re-crawl of GitHub and Slack needs a person. A service account would let parts of it be automated safely. |
| Scalable | The page is 13.8 MB, under a 16 MB ceiling. Views use paging. The data is split by source. | Beyond about 30,000 repositories, split the page into a shell plus data files, or serve the data from the same host. |
| Resilient and robust | The page still works when a data source is missing, and says so (for example, the open build without Slack). Negative tests exist for every check. | Single maintainer until B1. |
