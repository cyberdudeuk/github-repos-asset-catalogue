## What this changes and why

## Checks

- [ ] The root cause is stated, for a fix
- [ ] A check fails without this change and passes with it (and has a negative test)
- [ ] The build passes: `GHRAC_PUBLIC=1 python3 -I build/inv/build_v71.py`
- [ ] `python3 -I build/scan_sensitive.py --sources` finds nothing
- [ ] `dist/index.html` and `docs/` were regenerated
- [ ] No personal names, email addresses, internal or private repository names, or message text from Slack or other private channels
