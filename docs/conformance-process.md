# Checking a repository is ready for gds-dtx

This page sets out how to show, with evidence anyone can check, that a repository meets the GDS Way before it moves into the gds-dtx organisation. It is how this catalogue's own repositories were checked on 27 November 2026, and any team can repeat it on theirs.

## What is checked

`tools/conformance.py` runs 25 checks. Each one names the GDS Way page and section it comes from, the strength the page uses and the date the page was last reviewed. The GDS Way was read at alphagov/gds-way commit 7bc40fb (25 November 2026).

| Area | GDS Way page | What it asks |
| --- | --- | --- |
| Publishing code (SC-01 to SC-07) | [How to store source code](https://gds-way.digital.cabinet-office.gov.uk/standards/source-code/#publish-open-source-code) | MUST: README, informative commit messages, MIT and OGL licence files, an email address for security reports, and a changelog, release notes, known issues and semantic versioning if third parties are affected. SHOULD: contributing guidelines and tests in public CI. |
| Git (GT-01, GT-02) | [Working with Git](https://gds-way.digital.cabinet-office.gov.uk/standards/source-code/working-with-git.html) | SHOULD: default branch `main`, commit summaries of 50 characters or fewer |
| GitHub (UG-01) | [Use GitHub](https://gds-way.digital.cabinet-office.gov.uk/standards/source-code/use-github.html#configuring-github-repositories) | Consider protecting the main branch |
| GitHub Actions (GA-01 to GA-07) | [Using GitHub Actions](https://gds-way.digital.cabinet-office.gov.uk/standards/source-code/using-github-actions.html) | MUST: pin third-party actions to a commit SHA, set least-privilege permissions, avoid risky triggers unless security-reviewed, avoid script injection, use no personal access tokens, use OIDC for AWS. Consider: CODEOWNERS over workflows. |
| Dependencies (TD-01 to TD-03) | [Tracking dependencies](https://gds-way.digital.cabinet-office.gov.uk/standards/tracking-dependencies.html) | SHOULD: automated updates, a cooldown, an open pull request limit of 10 or more |
| Sensitive information (MS-01) | [Managing sensitive information](https://gds-way.digital.cabinet-office.gov.uk/standards/managing-sensitive-information.html) | MUST: internal or private repositories have `HANDLING_INSTRUCTIONS.md` |
| Vulnerability disclosure (VD-01) | [Vulnerability disclosure](https://gds-way.digital.cabinet-office.gov.uk/standards/vulnerability-disclosure.html) | SHOULD: published sites point `security.txt` at the Cabinet Office programme |
| Decisions (AD-01) | [Architecture decisions](https://gds-way.digital.cabinet-office.gov.uk/standards/architecture-decisions.html) | SHOULD: decisions recorded in version control |
| gds-dtx practice (DX-01, DX-02) | What gds-dtx does in [its own repositories](https://github.com/gds-dtx/gds-dtx-github-users-tf) | Pre-commit with detect-secrets; the third-party actions to add to the gds-dtx Actions allowlist. Good practice, not GDS Way rules, so they never decide the verdict. |

## How to read the result

- **Ready**: every MUST check passes.
- **Ready with exceptions**: every MUST check passes or departs by a recorded decision. A decision counts only with a reason, a review date and a reference in `docs/compliance/exceptions.yaml`.
- **Not ready**: a MUST check fails with no recorded decision.
- **Incomplete**: a MUST check needs a person or a repository setting to confirm it. The checker never counts a missing setting as a pass.

## Do it for your repository

1. Run `python3 -I tools/conformance.py --self-test` to prove the checker still catches each problem it is meant to.
2. Run `sh tools/conformance_meta.sh OWNER/REPO > meta.json` (needs the GitHub CLI, signed in). It only reads settings.
3. Run `python3 -I tools/conformance.py PATH/TO/REPO --meta meta.json --write`.
4. Fix each FAIL, or record the decision behind it.
5. Commit `docs/conformance/` and add the badge to the README:
   `[![gds-dtx readiness](docs/conformance/badge.svg)](docs/conformance/report.md)`
6. Rerun it whenever the repository or the GDS Way changes. The report is dated, so readers can see how fresh it is.

## Results for this catalogue's repositories, 27 November 2026

| Repository | Verdict | MUST met | SHOULD met | Recorded exceptions |
| --- | --- | --- | --- | --- |
| [dam-capability-playbooks](https://github.com/cyberdudeuk/dam-capability-playbooks/blob/main/docs/conformance/report.md) | Ready with exceptions | 10 of 10 | 7 of 11 | SC-04 |
| [dam-policy-explorer](https://github.com/cyberdudeuk/dam-policy-explorer/blob/main/docs/conformance/report.md) | Ready with exceptions | 10 of 10 | 3 of 11 | SC-04 |
| [dcat-ap-uk](https://github.com/cyberdudeuk/dcat-ap-uk/blob/main/docs/conformance/report.md) | Ready with exceptions | 10 of 10 | 9 of 11 | SC-04 |
| [dq-commons](https://github.com/cyberdudeuk/dq-commons/blob/main/docs/conformance/report.md) | Ready with exceptions | 11 of 11 | 5 of 11 | SC-03, SC-04, GA-03 |
| [github-repos-asset-catalogue](https://github.com/cyberdudeuk/github-repos-asset-catalogue/blob/main/docs/conformance/report.md) | Ready with exceptions | 10 of 10 | 8 of 11 | SC-04 |
| [ndl-pubsec-mcp](https://github.com/cyberdudeuk/ndl-pubsec-mcp/blob/main/docs/conformance/report.md) | Ready with exceptions | 10 of 10 | 7 of 11 | SC-03, SC-04 |
| [ai-capability-governance](https://github.com/cyberdudeuk/ai-capability-governance/blob/main/docs/conformance/report.md) | Ready with exceptions | 10 of 10 | 7 of 11 | SC-03, SC-04 |
| [pubsec-tech-hub](https://github.com/cyberdudeuk/pubsec-tech-hub/blob/main/docs/conformance/report.md) | Ready with exceptions | 10 of 10 | 5 of 11 | SC-03, SC-04, GA-03 |
| [legacy-technology-observatory](https://github.com/cyberdudeuk/legacy-technology-observatory/blob/main/docs/conformance/report.md) | Ready with exceptions | 10 of 10 | 4 of 11 | SC-03, SC-04 |

The owner's 4 private repositories were checked the same way. 1 is ready with exceptions. 3 need `HANDLING_INSTRUCTIONS.md`, which only the owner can write. They are not named here because they are private.

The exceptions recorded are the owner's decisions:

- **SC-04**: no email address is published anywhere. Security reports go through GitHub private vulnerability reporting or the Cabinet Office vulnerability disclosure programme.
- **SC-03** in five repositories: content is CC BY 4.0, not OGL, because it is not Crown copyright. The OGL v3.0 says complying with CC BY 4.0 meets its conditions.
- **GA-03** in two repositories: `issues` and `workflow_run` triggers kept after a written security review.

## What this does not cover

- Organisation settings that only gds-dtx owners can see, such as the Actions allowlist, rulesets and secret scanning.
- Whether the code is correct. The repositories' own tests cover that.
- The GDS Way's people rules: accounts connected to a work email with two-factor authentication, and review of changes by someone other than the author. A single maintainer can't meet the review rule alone.

## Defects found while building the checker

Each defect is now caught by `--self-test` (see `DEFECTS` in the code):

- **D-CONF-02**: risky triggers written as a mapping were missed.
- **D-CONF-03**: user text passed safely through `env:` was flagged as script injection.
- **D-CONF-04**: rules for publishing open source code were applied to private repositories.
- **D-CONF-05**: an OGL file under `docs/` was missed.
- **D-CONF-06**: the "no email" exception was accepted with no working private route.
- **D-CONF-07**: the GOV.UK page for the Cabinet Office programme was not recognised as a route.
- **D-CONF-08**: the amber "incomplete" badge failed WCAG AA contrast with white text. This was found by looking at the rendered badge.
