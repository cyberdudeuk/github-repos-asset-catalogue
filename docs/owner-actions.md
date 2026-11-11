# What only the owner can do

Prepared on 11 November 2026 from the roadmap (docs/roadmap.md). Each item is something automation here can't or shouldn't do, because it changes settings, publishes, deletes or needs a decision. Everything it needs is ready.

## Publish

**RM-18: release 7.16.0.** On GitHub, open Releases, then Draft a new release. Create the tag `v7.16.0` on commit `b9d21a8`, title it "7.16.0 (5 November 2026)", and paste the text from [docs/release-notes/7.16.0.md](release-notes/7.16.0.md). Do the same for 7.17.0 and 7.18.0 after their pull requests are merged.

## Delete (only with your confirmation)

**RM-20: four stale branches.** `gds-way-assessment` and `test-results-7.11.1` hold code from before the public and internal split and fail the build. `readme-assessment` and `roadmap-github` were merged. On the Branches page, delete each. GitHub keeps a deleted branch restorable for a while from the closed pull request.

## Settings

**RM-14: security settings**, under Settings, Code security:
- private vulnerability reporting
- secret scanning, with push protection
- a ruleset for `main` that requires a pull request and the build to pass
- Actions limited to GitHub's own and verified actions
- approval before outside contributors' workflows run

**RM-24: approval for each deployment.** Settings, Environments, `github-pages`: add yourself as a required reviewer. Do the same in the companion repository.

**RM-16 and RM-25: two Discussions categories.** Settings, Discussions categories: create "Feature assessment" with the slug `feature-assessment`, and "Q&A" with the slug `q-a` and the question and answer format. The forms for both are already in .github/DISCUSSION_TEMPLATE.

**RM-26: the roadmap as a project board.** Projects, New project, Board. Add the issues the roadmap-item form opens, with Status, Owner and Date fields.

## Ask

**RM-19: GitHub Support.** At support.github.com, choose the repository and ask:

> The history of cyberdudeuk/github-repos-asset-catalogue was rewritten on 3 November 2026 to remove material that should not be public. Commits from before the rewrite can still be reached by their IDs through pull request references and cached views. Please run garbage collection and remove cached views of unreachable commits for this repository.

## Decide

- **RM-21: security.txt.** A proposed decision is in [ADR 0005](adr/0005-security-txt.md): do it when the repository moves, because a project site can't serve the root address.
- **RM-12 and RM-13: ownership and home.** A named team accepts ownership, then the repository moves to the agreed organisation (ADR 0003 proposes gds-dtx, after the machinery-of-government change settles).
- **RM-22: before a wider release.** A data protection screening note, an independent security review and a machinery-of-government content check (docs/security/release-readiness.md, blockers B5, B6 and B11).

## Done on your behalf on 11 November 2026

- **RM-23:** the seven labels the forms apply were created and read back from GitHub.
- **RM-02, RM-07 (data.gov.uk) and RM-08:** in the 7.18.0 pull request.
