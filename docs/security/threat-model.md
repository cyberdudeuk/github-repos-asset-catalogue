# Threat model

GitHub Repos Asset Catalogue (GHRAC), version 7.11.0, 2 November 2026. Requirement R63.

This is an adversarial review. It asks how the catalogue could be misused to cause harm, and records what guards against each threat and what risk is left. It follows the shape of the NCSC's threat modelling guidance and uses STRIDE as a checklist. Each guard has a check that runs on every build, and each check has a negative test that shows it catches the problem it exists for.

## What the catalogue is

- One self-contained HTML page, built from data files in this repository.
- It makes no network requests and keeps nothing about the people who use it.
- It reads only public repositories. Anything private or internal that was seen while signed in is never stored (C-GHV-03).
- The only parts not drawn from public GitHub data are aggregates from Slack (R59), made from what one signed-in person could see.
- It has two audiences:
  - **gov**, the default: internal government and public sector users. It includes the Slack aggregates.
  - **public**, set with `GHRAC_AUDIENCE=public`: an open build. The Slack aggregates, and every label that relies on them, are left out.

## What is worth protecting

| Asset | Why it matters |
|---|---|
| Trust that what the catalogue says is accurate | People decide what to reuse and depend on from it. A wrong "safe to depend on" claim is a harm. |
| Readers' devices and sessions | The page runs in their browser, usually on a government device. |
| Internal context | Slack channel names, which services lean on which repositories, and the proposed destinations in the co-cddo move. |
| The repository and its automation | Anyone who can change the build can change what thousands of readers see. |
| People | Contributors, maintainers and the people named in repository text. |

## Threats, guards and remaining risk

| # | Threat (STRIDE) | How it could happen | Guard | Check | Risk left |
|---|---|---|---|---|---|
| T1 | Information disclosure | Repository text quoted on the page links to SharePoint, Atlassian, Google Docs, Slack, Teams, localhost or private network addresses. These map internal tenants, sites and document IDs. | Before the page is built, every such address is replaced with a note, in both audiences. The 7.11 build replaced 59. | C-SEC-01; negative tests in C-SEC-01n | Low. Names of public bodies' tenants can still appear in plain text that isn't a link. |
| T2 | Spoofing, tampering | A repository links to an app on shared hosting (Heroku, Azure Web Apps, Netlify and similar). Once the app is deleted, anyone can register the same name and serve content behind a government-looking link. Plain http links can also be altered in transit. | These addresses are shown as text with an explanation, never as links. The page and the build share one list (`DATA.sec.risky`). | C-SEC-01n; P-52 (in the browser) | Low. A reader can still copy the address by hand. |
| T3 | Spoofing (impersonation) | Someone creates a GitHub account named after a public body. If the catalogue lists it as government, the catalogue lends it credibility. | Every account must come from the government.github.com registry, or have a recorded check on GitHub. Only GitHub's verified-domain badge counts as proof. 11 of the 15 accounts from outside the registry have no verified domain. They are labelled "Account not verified by GitHub" on every one of their projects. | C-SEC-03; P-52 | Medium. The registry itself is curated by people outside this team, and listing in it is not domain verification. |
| T4 | Tampering, elevation of privilege | Hostile text in a repository's name, description, topics or README is designed to run as code on the page (cross-site scripting), or to send data elsewhere. | All repository text is escaped before display (T-XSS-01, T-XSS-02, T-RX-03, T-SRCH-01). A Content-Security-Policy allows no network requests, frames, plug-ins, external scripts, styles or fonts, and no form submission. The code uses no eval or new Function. Every new-tab link has `rel="noopener"`. | C-SEC-02; P-52; the harness's T-XSS tests | Low. Inline scripts are allowed because the page is one file. Escaping is the main defence, and the policy is the backstop. |
| T5 | Information disclosure (reconnaissance) | The catalogue joins public facts into something new: which repositories underpin live services, where incidents are discussed, and which projects lack a security policy. This becomes a prioritised target list. | The open build leaves out the Slack aggregates, channel names and the "Seen in live operations" label, which is drawn from Slack. The gov build is for government and public sector users only. | C-SEC-04; C-CLB-01; P-51 | Medium, as an accepted risk. Practice signals for each repository stay in both builds: README, licence, SECURITY.md, Dependabot, unpinned actions and workflow permissions. Anyone can read these from GitHub, and showing them is how owners find out what to fix. In the open build, the "likely supports a service" label is still inferred from public text. |
| T6 | Tampering (data poisoning) | An account changes its descriptions or topics to steer the catalogue's labels, for example to look "safe to depend on" or "used across government". | Labels are rule-based and show their evidence. Precision is measured on random samples (life labels 13–14 of 15). The reuse map counts dependencies, not claims. A label never reads as an endorsement: "Is it safe to depend on?" lists the signals behind it. | C-LIF-01, C-REU-01, C-FEAT-02 | Medium. A determined account can still game text-based rules. The labels say they are estimates. |
| T7 | Tampering (supply chain) | A compromised third-party GitHub Action, or a workflow that runs untrusted text, changes the build. | Every action is pinned to a full commit SHA. The token is read-only unless a write is explained. Checkout doesn't keep the token. There is no `pull_request_target`, and no event text in shell scripts. Dependencies are pinned to exact versions. CodeQL runs where code scanning is available. | C-SEC-05; negative tests in C-SEC-01n; `codeql.yml` | Low. CodeQL needs GitHub Advanced Security while the repository is private. |
| T8 | Information disclosure (secrets) | A token or key is committed by mistake, or quoted from a repository's text. | `scan_sensitive.py` refuses the build if it finds a GitHub, Slack, AWS or Google token, a private key or a Slack webhook. It also refuses email addresses, protective markings and links to private Claude apps. Its self-test plants 11 examples. | C-SAN-01 | Low. GitHub secret scanning and push protection should also be switched on in the repository's settings. |
| T9 | Information disclosure (personal data) | Contributor names, CODEOWNERS entries or names in README text identify people. Combined with the reuse and security views, this could support phishing aimed at maintainers. | Names are removed from the build (R54, C-SAN-01, pii.py). CODEOWNERS entries are summarised. The Slack aggregates hold no names, user IDs or message text. | C-SAN-01; C-CLB-01 | Low |
| T10 | Repudiation, tampering (integrity of the published page) | Someone republishes a changed copy and passes it off as the catalogue. | Every release has a document ID, a barcode and a QR code. The page carries its own check registry and runs 52 checks in the browser. Releases should be tagged and signed (see release readiness). | P-01 to P-52 | Medium, until releases are signed and published from one place. |
| T11 | Denial of service, availability | The host goes down, or the page gets too big to load on a phone. | The page is a single static file, about 13.8 MB, under a 16 MB ceiling. It works offline once saved and needs no server. Any static host can serve it. | Build size limit; the overflow and width tests | Low |
| T12 | Elevation of privilege (misuse of the signed-in crawl) | The browser crawls used a person's signed-in GitHub, Slack and Google sessions. Code or instructions in fetched pages could try to act with those sessions. | Crawls were read-only. Fetched content was treated as data. Tokens were never read or stored. Nothing internal or private was kept. No crawl runs in automation. | C-GHV-03; C-CLB-01; process (README, "Limits") | Low. Future crawls need the same rules, and should move to a service account with read-only scopes. |
| T13 | Information disclosure (aggregation about national security accounts) | The catalogue combines public facts about defence, intelligence and national security accounts: which projects run live services, which lack a security policy, and where they are discussed. The Government Security Classifications Policy warns that aggregated OFFICIAL data "may warrant additional controls". | For the 10 accounts in `SENSITIVE_COMMUNITIES`, the catalogue lists what they publish but draws no inferences: no life labels, no practice or security signals, no chat links, no naming as reuse consumers. This applies to both audiences. | C-SEC-07; P-52; negative tests in C-SEC-01n | Low. The source data files still hold the raw signals; strip them before an open edition (national-security-review.md). |

## What the catalogue cannot be used for

- **It cannot be used to reach private code.** It holds no private or internal repositories, tokens or credentials.
- **It cannot change anything on GitHub or Slack.** The page has no network access, and the automation is read-only apart from one health issue.
- **It doesn't show vulnerabilities.** It reads whether projects have a security policy and dependency monitoring. It does not read security alerts, advisories or code scanning results.

## Review

Review this model at every minor release, when a new data source is added, and before any change of audience or visibility.

Owner: the catalogue's maintainers, through the repository's issues. Report security problems privately, as set out in [SECURITY.md](../../SECURITY.md).
