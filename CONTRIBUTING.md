# Contributing

1. Open an issue describing the problem or need. Say who it's for.
2. For a fix: find the root cause, write a check that fails on the current build, fix it, and show the check passing. Add the defect to `build/inv/docs71.py` (it feeds docs/defects.md and the page).
3. For a new classification: write the rule with word boundaries, positive and negative tests, sample at least 15 results and record the accuracy with the view.
4. Run the build and the tests (see README). The build refuses untraced requirements and defects.
5. Write in plain English, following GOV.UK style. No personal names in public data.
