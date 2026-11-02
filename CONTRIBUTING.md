# Contributing

1. Open an issue describing the problem or need. Say who it's for.
2. For a fix: find the root cause, write a check that fails on the current build, fix it, and show the check passing. Add the defect to `build/inv/docs71.py` (it feeds docs/defects.md and the page).
3. For a new classification: write the rule with word boundaries, positive and negative tests, sample at least 15 results and record the accuracy with the view.
4. Run the build and the tests (see README). The build refuses untraced requirements and defects.
5. Write in plain English, following GOV.UK style. No personal names in public data.
6. Work the GDS Way:
   - **Branches:** work on a short-lived branch and open a pull request. Someone other than the author reviews it before it is merged into `main`.
   - **Commit messages:** start with a summary of 50 characters or fewer, then a blank line, then why the change was made, wrapped at 72 characters. See [Working with Git](https://gds-way.digital.cabinet-office.gov.uk/standards/source-code/working-with-git.html).
7. Record decisions that change the architecture as an ADR in `docs/adr/`.
8. Never commit internal-only inputs here. They live in the private companion repository (ADR 0004, `build/internal.py`), and C-SAN-01 fails if one is tracked. Rebuild `dist/index.html` with `GHRAC_INTERNAL` set, and check it with `python3 -I build/tools/verify_dist.py`.
