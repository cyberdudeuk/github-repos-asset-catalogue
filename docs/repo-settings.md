# Repository settings review

GHRAC 7.12.0. Requirement R66. Settings were read on 2 November 2026 at about 13:30, after the repository was made public and GitHub Pages and Discussions were switched on. They were read from GitHub's API and from the settings pages in the owner's browser. Nothing was changed.

The settings this project expects, and the reason for each, are written down in [.github/settings-baseline.json](../.github/settings-baseline.json). The weekly self-routines compare GitHub against that file and report any drift in the "Weekly health" issue (C-SET-01). They never change a setting.

Three pages need the owner to confirm their password again, so they weren't read: Collaborators and teams, Moderation, and Notifications. Check those by hand.

## Do first

| # | Setting | Now | Should be | Why |
|---|---|---|---|---|
| 1 | **Repository content** | The internal-only material (Slack counts, the co-cddo move proposals, the v1 workbook layer, handling instructions) was public on main | Moved to the private companion by the 7.12.0 pull request. The published page is the open edition. | Agreed in option 2; see ADR 0004 |
| 2 | **History** | Earlier commits held that material, and the old document-store counts | Rewritten on 3 November 2026 at the owner's decision: every branch's history no longer holds the internal-only files, earlier published pages or the document-store wording. A second rewrite the same day, after 7.13.1, took out the team's email address, the email in commit messages and the showcase plan (R69, R70) | Done, checked commit by commit with C-SAN-01. Still to do (owner): ask GitHub Support to remove cached views and unreferenced commits. GitHub may still serve the old commits by their IDs, through pull request references and cached views, until GitHub Support removes them; anyone who cloned or forked before 3 November 2026 keeps the old history. |
| 3 | **Private vulnerability reporting** (Settings → Advanced Security) | Off | On | SECURITY.md offers it. The GDS Way expects a private route for reports. |
| 4 | **Secret Protection: secret scanning and push protection** | Off | Both on | Free on public repositories. Stops a leaked token reaching GitHub. |
| 5 | **A ruleset for main** (Settings → Rules → Rulesets) | None | Require a pull request; require the `build` check to pass; block force pushes and deletion. Add the owner to the bypass list until there is a second maintainer, because GitHub doesn't let authors approve their own pull requests. | The GDS Way: protect the main branch |
| 6 | **Allowed actions** (Settings → Actions → General) | Allow all actions | Allow actions created by GitHub only. Tick "Require actions to be pinned to a full-length commit SHA". | Every workflow here uses only `actions/*` and `github/codeql-action`. C-SEC-05 already checks the pinning, and this enforces it on GitHub too. |
| 7 | **Allow GitHub Actions to create and approve pull requests** | On | Off | Nothing here needs it. Leaving it on lets a compromised workflow approve its own changes. |
| 8 | **Fork pull request workflows** | Require approval for first-time contributors | Require approval for all external contributors | A public government repository gets drive-by pull requests |
| 9 | **Installed GitHub Apps with access to this repository** | 12: Atlassian, ChatGPT Codex Connector, Claude, Claude Design Import, Codecov, Figma, Linear, lovable.dev, Repography, Supabase, Vercel, whitehall-connect | Only the apps this repository uses. On each app's settings, choose "Only select repositories". | Least privilege. Each app with write access can change the code. |
| 10 | **Description** | Says "Private: internal government and public sector users only" | "UK public sector code on GitHub, organised for everyone. Open edition; a government edition is built from a private companion." | It must match the visibility (checked weekly) |

## Then

| # | Setting | Now | Should be | Why |
|---|---|---|---|---|
| 11 | **GitHub Pages** | Source is GitHub Actions. HTTPS is enforced. The environment allows main only. Nothing has been deployed. | `.github/workflows/pages.yml` (in the 7.12.0 pull request) deploys `dist/index.html` after checking it is this commit's code and the open edition | Publishes only what the checks allow |
| 12 | **Homepage** (the About panel) | Empty | The Pages address, once deployed | People find the page from the repository |
| 13 | **Code scanning** | Default setup off; the `codeql` workflow runs now the repository is public | Keep the workflow (advanced setup). Don't also switch on default setup, which would conflict. | CodeQL covers JavaScript, Python and the workflows |
| 14 | **Dependabot** | Security updates on; version updates from dependabot.yml | Also turn on Dependabot alerts and malware alerts if they're off | Alerts for known vulnerabilities and malicious packages |
| 15 | **Merging** | Merge commits, squash and rebase all allowed; auto-merge on | Turn off auto-merge. Keep merge commits. Turning off squash is optional. | The GDS Way: commits that tell a story. Nothing should merge without a person while there is one maintainer. |
| 16 | **Code review limits** | Off | Limit approvals to users with explicit access | Stops reviews from strangers counting as approvals |
| 17 | **Discussions categories** | GitHub's six defaults | Add "Feature assessment" (slug `feature-assessment`). Consider removing Polls and Show and tell. Keep Announcements for maintainers only. | The feature-assessment form only appears in a category with that slug |
| 18 | **Labels** | GitHub's defaults | Add: data correction, defect, feature assessment, health, security | The issue and discussion forms apply these. GitHub silently skips a label that doesn't exist. |
| 19 | **Releases** | None. Release immutability is on, which is good. | Tag v7.12.0 when this is merged, with the notes from docs/releases.md | The GDS Way: version numbers and release notes |
| 20 | **Projects** | On, unused | Keep on, for one board: the roadmap (RM-26). Each roadmap item is an issue from the roadmap-item form | A status, an owner and a date for every open item, on GitHub (changed 4 November 2026; it said Off before) |
| 21 | **CODEOWNERS** | One owner | Add the owning team when there is one (blocker B1) | Reviews by someone other than the author |

## Already right

These need no action:

- **Visibility and features:** visibility is public, the wiki is off, issues and Discussions are on, and Sponsorships are off.
- **Commits:** web commits need a sign-off, and branches are deleted after merging.
- **Archiving and releases:** "Preserve this repository" is on, and so is release immutability.
- **Workflow permissions:** the default is read-only.
- **Credentials:** there are no repository secrets, deploy keys or webhooks.
- **Pages:** the github-pages environment allows main only.
- **Community profile:** the README, licence, code of conduct, contributing guide, security policy and issue templates are all present (100%).

## The private companion

The companion, cyberdudeuk/github-repos-asset-catalogue-internal, needs settings of its own:

- Keep it private.
- Share it with named people or a team only.
- Turn on secret scanning, if available, and Dependabot alerts.
- Set Actions to read-only, with only GitHub's actions allowed and SHA pinning required.
- Add a ruleset on main: block force pushes and deletion.
- Leave GitHub Pages off.
- Review HANDLING_INSTRUCTIONS.md by 2 February 2027.
