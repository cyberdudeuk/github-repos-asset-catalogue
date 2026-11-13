"""Public bodies on GitHub that the X-Gov source list misses (R82).

  python3 -I build/refresh/supplement.py            check each sample repository with git, then write supplement.json
  python3 -I build/refresh/supplement.py --offline  write from the last stored git results

The catalogue's repositories come from the X-Gov scraper's list of accounts. Looking for devolved and strategic authority code on
11 November 2026 found accounts that list doesn't include. Each is recorded here with:
  - the public body it belongs to, and the evidence: the account's own GitHub organisation page, the body's own website or
    GitHub Pages site, or the body's own records in a data catalogue
  - how many public repositories GitHub showed on that date
  - one repository confirmed public with git
Only organisations are listed, never a person's account. An account whose page GitHub refused to show is listed as not read,
not as found. These accounts are shown beside the catalogue, not mixed into its counts, until the source list adds them: the
right fix is upstream, in the scraper's list.
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import long_date

H = os.path.dirname(os.path.abspath(__file__))
READ = "2026-11-11"
ACCOUNTS = [  # account, body, nation, devolution role, repos shown on GitHub, sample repository, evidence, confidence
    ("dof-dss", "Department of Finance (Northern Ireland): Digital Shared Services", "Northern Ireland", "devolved", 113, "nidirect-drupal",
     "GitHub organisation page: 'Digital Shared Services - Department of Finance - NICS'; it builds nidirect and the departments' sites", "organisation page"),
    ("GIGCymru", "NHS Wales (GIG Cymru): shared code across NHS Wales, with Digital Health and Care Wales", "Wales", "devolved", 13, "architecture",
     "GitHub organisation page with the verified domain nhs.wales", "verified domain"),
    ("wgdsu", "Welsh Government: Data Science Unit", "Wales", "devolved", 8, "KASStylesR",
     "GitHub organisation page: 'Welsh Government Data Science Unit / Uned Gwyddor Data Llywodraeth Cymru'", "organisation page"),
    ("SeneddCymru", "Senedd Cymru (Welsh Parliament)", "Wales", "devolved", 2, "e-petitions",
     "the organisation's name and its e-petitions repository only; the Senedd's own pages weren't found to link it", "name only"),
    ("greater-london-authority", "Greater London Authority", "England", "strategic authority (gla)", 47, "nowcast-birth-estimates",
     "the GLA's own dataset records on data.gov.uk name its repositories; GitHub organisation page", "body's own records"),
    ("west-midlands-combined-authority", "West Midlands Combined Authority", "England", "strategic authority (wmca)", 1, "west-midlands-combined-authority.github.io",
     "GitHub organisation page links wmca.org.uk, and its GitHub Pages site is titled 'WMCA (West Midlands Combined Authority) on GitHub'", "organisation page and own site"),
]
NOT_READ = [
    ("datasciencescotland", "Scotland", "named by a Scottish Government dataset on data.gov.scot (Covid-19: Scottish Contact Survey); GitHub refused to show its page, so whether it is an organisation is unknown"),
    ("wmcadigital", "England", "found in search results as 'WMCA Digital and Data'; GitHub refused to show its page"),
]


def git_public(full):
    try:
        return subprocess.run(["git", "ls-remote", f"https://github.com/{full}.git", "HEAD"], capture_output=True, timeout=60,
                              env=dict(os.environ, GIT_TERMINAL_PROMPT="0")).returncode == 0
    except Exception:
        return None


def main():
    path = os.path.join(H, "supplement.json")
    old = json.load(open(path)) if os.path.exists(path) else {}
    rows = []
    for acc, body, nation, role, n, sample, evidence, conf in ACCOUNTS:
        full = f"{acc}/{sample}"
        ok = (old.get("git", {}) or {}).get(full) if "--offline" in sys.argv else git_public(full)
        rows.append(dict(account=acc, body=body, nation=nation, role=role, repos_shown=n, sample=sample, sample_public=ok, evidence=evidence, confidence=conf))
        if "--offline" not in sys.argv: time.sleep(1)
    src = json.loads(subprocess.run([sys.executable, "-I", "-c", "import gzip,json,sys;print(json.dumps(sorted({r['owner'].lower() for r in json.load(gzip.open(sys.argv[1])) if isinstance(r, dict) and r.get('owner')})))",
                                     os.path.join(H, "sources", "repos.json.gz")], capture_output=True, text=True).stdout)
    out = dict(read=READ, git_checked=old.get("git_checked") if "--offline" in sys.argv else time.strftime("%Y-%m-%d"), accounts=rows,
               not_read=[dict(account=a, nation=n, note=t) for a, n, t in NOT_READ], git={f"{r['account']}/{r['sample']}": r["sample_public"] for r in rows})
    checks = []
    def check(ok, cid, msg, guards): checks.append(("PASS " if ok else "FAIL ") + f"{cid} {msg}   [guards: {guards}]")
    already = [r["account"] for r in rows if r["account"].lower() in src]
    neg = [r["account"] for r in rows if r["account"].lower() in set(src) | {"dof-dss"}]   # negative test: a listed account is caught
    check(not already and neg == ["dof-dss"], "C-ACC-01", f"{len(rows)} accounts found outside the X-Gov source list, none already in it (in it: {already}); negative test: an account already listed is caught", "R82")
    check(all(r["sample_public"] for r in rows), "C-ACC-02", f"each account has a repository git confirms is public (checked {long_date(out['git_checked'])}); failing: {[r['account'] for r in rows if not r['sample_public']]}", "R82, V717-2")
    check(all(r["evidence"] and r["confidence"] for r in rows) and not set(a for a, *_ in NOT_READ) & {r["account"] for r in rows}, "C-ACC-03",
          f"every account names its public body and the evidence for it, and the {len(NOT_READ)} accounts GitHub wouldn't show are listed as not read, never as found", "R82, R54")
    json.dump(out, open(path, "w"), indent=1, ensure_ascii=False)
    open(os.path.join(H, "supplement_checks.txt"), "w").write("\n".join(checks) + "\n")
    print("\n".join(checks))
    return 0 if all(c.startswith("PASS") for c in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
