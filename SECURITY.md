# Security

## Reporting a problem

Please report security problems privately; please don't open an issue. You can:

- use the contact form
- use GitHub's private vulnerability reporting for this repository (Security tab, then "Report a vulnerability")
- report through the Cabinet Office's [vulnerability disclosure programme](https://www.gov.uk/help/report-vulnerability), which the GDS Way asks GDS services to take part in

We'll acknowledge reports within five working days and agree a fix and disclosure date with you.

Please report anything that could:

- let the page run code it shouldn't
- reveal internal or personal information
- list an impersonating account as government
- send readers to a link that someone has taken over
- change the build without review

## How the catalogue is protected

The full model is in [docs/security/threat-model.md](docs/security/threat-model.md). In short:

- **The page.** It is a single static file. It makes no network requests and keeps no data about visitors. A Content-Security-Policy blocks network requests, frames, forms that submit elsewhere, and external scripts, styles and fonts (C-SEC-02).
- **Repository text.** All of it is treated as untrusted. It is escaped before display, and the tests include hostile-input cases (T-XSS-01, T-XSS-02, T-RX-03, T-SRCH-01).
- **Links.**
  - Links to sign-in-only or private addresses are removed: SharePoint, Atlassian, Google Docs, Slack, Teams, localhost and private networks (C-SEC-01).
  - Links on shared hosting, where anyone could take over an abandoned address, are shown as text, not links. So are plain http links.
- **Accounts.** Every account needs provenance. Accounts that GitHub hasn't verified are labelled as such (C-SEC-03).
- **Audiences.**
  - The default build is for government and public sector users.
  - The open build (`GHRAC_AUDIENCE=public`) leaves out the Slack aggregates, and the labels drawn from them (C-SEC-04).
- **Automation.**
  - Workflows run with read-only tokens unless a write is explained.
  - Every action is pinned to a commit SHA, and the token isn't kept after checkout.
  - There is no `pull_request_target`, and no event text is put into scripts (C-SEC-05).
  - CodeQL runs where code scanning is available.
- **Data.** The repository must not hold personal data, credentials, tokens, email addresses or links to private services. `build/scan_sensitive.py` checks for all of these on every build (C-SAN-01).

This repository is private, for internal government and public sector users. Before it is shared more widely, read [docs/security/release-readiness.md](docs/security/release-readiness.md).
