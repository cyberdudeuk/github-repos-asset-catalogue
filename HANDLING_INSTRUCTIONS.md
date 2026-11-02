---
classification: OFFICIAL-SENSITIVE
handling_group: RECIPIENTS ONLY
last_reviewed_on: 2026-11-02
review_in: 3 months
responsible_role: Data Management Lead, Office of the Chief Data Officer, GDS
responsible_role_contact: GDSDataManagement@dsit.gov.uk
---

This repository is private, following the GDS Way's guidance on [managing sensitive information](https://gds-way.digital.cabinet-office.gov.uk/standards/managing-sensitive-information.html). Public is the default for GDS code, and most of this repository could be public. Three things keep it closed for now.

**What is sensitive**

1. Aggregates drawn from internal collaboration tools. These are counts of links to repositories from the UK Government Digital and GDS Slack workspaces and the GDS Google Drive, and the names of public channels. They were made from one person's signed-in view. The workspace owners have not yet agreed to share them more widely.
2. Proposals for moving repositories out of the deprecated co-cddo GitHub organisation, together with the inventory and workbook behind them. Each repository's owners have not agreed these proposals, so they describe plans that haven't been announced.
3. Notes on method that describe how signed-in sessions were used to read GitHub, Slack and Drive.

None of these is a secret or a credential. The cause is consent and timing, not harm. The code, the public GitHub data and the open build (`GHRAC_AUDIENCE=public`) hold none of the three. See [docs/security/gds-way-assessment.md](docs/security/gds-way-assessment.md).

**What would change this**

- The workspace owners agree, or the Slack and Drive aggregates move out of this repository.
- The repository owners agree the co-cddo destinations, or the move workspace moves out of this repository.
- The repository moves to a GDS GitHub organisation. Its visibility can then be `internal` (HMG USE ONLY) while it is reviewed, and public once the first two points are resolved.

**Access**

The repository is shared with named recipients only. To ask for access, or for an exception, contact the responsible role at the address above.
