# Review against government security guidance, with care for national security, defence and intelligence

GHRAC 7.11.1, 2 November 2026. Requirement R65.

## In short

- **No protective markings.** None were found in the descriptions or the README text quoted from any public repository in the catalogue.
- **Ten accounts get extra care.** They belong to the defence, intelligence and national security communities. Between them they publish 1,668 public repositories.
- **What the catalogue does with them.** It lists what these accounts publish themselves, but it no longer draws any conclusions of its own about them. That means no "part of a live service" labels, no security or practice signals for each repository, no links to internal chat, and they aren't named as users of other projects. This applies to both audiences. C-SEC-07 checks it, and P-52 checks it again in the browser.
- **One of the collaboration-platform scans is gone.** It and everything drawn from it were removed at the owner's request. The removed material is still in the repository's history and in earlier versions of the artifact (see "What's left to do").

## The guidance applied

| Guidance | What it says that matters here | How the catalogue meets it |
|---|---|---|
| [Government Security Classifications Policy](https://www.gov.uk/government/publications/government-security-classifications/government-security-classifications-policy-html), version 2.0, August 2024 | "Aggregated data sets of OFFICIAL information may warrant additional controls." The -SENSITIVE marking is for OFFICIAL information "not intended for public release" and "of at least some interest to threat actors". Information is shared on "a genuine need-to-know, balanced with the need-to-share". Public information "requires no additional assurance". | The repositories themselves are public information, so they are listed. The catalogue's own combinations, for these ten accounts, are withheld (C-SEC-07). The Slack aggregates, which aren't for public release, stay in the government build (HANDLING_INSTRUCTIONS.md, C-SEC-04). |
| [When code should be open or closed](https://www.gov.uk/government/publications/open-source-guidance/when-code-should-be-open-or-closed), GOV.UK | Keep keys, credentials, fraud detection algorithms and unannounced policy closed. Open everything else, including code that enforces security. | The catalogue holds no keys (C-SAN-01 scans for 6 kinds of credential). The unannounced co-cddo move plans stay closed (HANDLING_INSTRUCTIONS.md). Its security guardrails are open code. |
| [The GDS Way: managing sensitive information](https://gds-way.digital.cabinet-office.gov.uk/standards/managing-sensitive-information.html) | Public by default. A repository that isn't public explains why in HANDLING_INSTRUCTIONS.md. | Done (C-SEC-06) |
| [The GDS Way: threat modelling](https://gds-way.digital.cabinet-office.gov.uk/standards/threat-modelling.html) | Model threats, and review the model each year or when things change | The threat model gains T13 (aggregation about national security accounts). A scored team session still needs the owning team. |
| [Software Security Code of Practice](https://www.gov.uk/government/publications/software-security-code-of-practice) (DSIT and NCSC, 2025, updated January 2026) | 14 principles that software vendors are expected to meet. They cover secure development, build environments, secure deployment and maintenance, and communication with customers. | The catalogue isn't a vendor product, but it follows the same practice. Builds are reproducible (V711-5). Actions are pinned and tokens are least-privilege (C-SEC-05). There is a vulnerability reporting route (SECURITY.md), and a release history and known-issues list (docs/releases.md, docs/defects.md). |

## The ten accounts

The list is in `build/dama/security.py` (`SENSITIVE_COMMUNITIES`), with the reason for each account. Changing it is a security decision and needs review.

| Community | Accounts | What they are |
|---|---|---|
| Intelligence and cyber security | GCHQ, ukncsc | GCHQ, and the National Cyber Security Centre, which is part of GCHQ |
| Defence | defencedigital, dstl, UKHO | Defence Digital, the Defence Science and Technology Laboratory and the UK Hydrographic Office, all part of the Ministry of Defence |
| National security and law enforcement | NationalCrimeAgency, UKHomeOffice, UKHomeOffice-attic, UKHomeOfficeForms, HO-CTO | The National Crime Agency, and the Home Office's accounts (policing, borders and counter-terrorism) |

**What the build withholds for these accounts (counts from the 7.11.1 build):**

- 227 life labels
- 257 sets of practice and security signals
- 11 projects' links to internal chat
- 9 mentions as users of other projects in the reuse map

**What stays:** what each account publishes itself. That means the repository's name, description, licence, language and activity, and a link to GitHub. A notice on each of these projects explains why there is less detail.

## Scans for anything that shouldn't be public

Both scans covered 12,251 repositories with enriched records, reading their name, description, README summary and topics.

- **Protective markings.** The scan looked for every classification and caveat marking in the Government Security Classifications Policy, as well as NATO markings. It found **none**. A looser pattern found 18 matches, and all were ordinary words: secret management, restricted words, restricted patients.
- **Defence, intelligence and national security terms outside the ten accounts.** 13 repositories matched. None is defence or intelligence work:
  - legal defence (Crown Court Defence, a "defence" context in court software)
  - flood defences
  - disease surveillance (public health and animal health)
  - the electronic monitoring of offenders, which is criminal justice
  - military service records at The National Archives

  So no other accounts were added to the list. The electronic monitoring projects are worth a second look by their owners: they are the closest to security work.

None of this was reported to the accounts. The repositories are public, and nothing was found that needs reporting. If a future scan finds a marking, report it to the account's owners privately, and never put it on the page.

## What's left to do

1. **Earlier artifact versions, and GitHub's copies of old commits.** The repository's history was rewritten on 3 November 2026, at the owner's decision, so no commit holds the removed scan's aggregates or its wording. GitHub may still serve the old commits by their IDs, through pull request references and cached views, until GitHub Support removes them; anyone who cloned or forked before 3 November 2026 keeps the old history. Earlier versions of the artifact still hold them, and can only be removed by deleting the whole artifact.
2. **The source data files.** The data files in `build/` still hold the raw practice signals for the ten accounts. The page leaves them out, but the files don't. Before an open edition, strip them at source too.
3. **A security review by the owning team,** including someone from a defence or national security security function. It should confirm the list of accounts and that withholding inferences is the right level of care.
4. **Other public repositories that mention the same service.** Three or four repositories have their own names or descriptions that mention that document-sharing service, for example a National Archives research project and a link converter. These are what those organisations publish, not this catalogue's data, so they were left as they are.
