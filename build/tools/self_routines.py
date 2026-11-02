"""The self-* routines for the GitHub Repos Asset Catalogue, run weekly by .github/workflows/self-routines.yml and by hand.

  self-verification  every *_checks.txt written by the data scripts passes, and the public build matches dist/index.html
  self-assessment    the repository has what a well-kept GitHub repository needs (README sections, licences, security
                     policy, code owners, contributing guide, issue and pull request templates, Dependabot)
  settings audit     GitHub's repository settings compared with .github/settings-baseline.json; drift is reported,
                     never fixed (only an owner changes settings)
  staleness          how old each source is, measured against its own date; anything past its limit is flagged
  self-reporting     writes self_report.md (for the run summary and the weekly health issue) and self_report.json
  self-repair        the workflow rebuilds the derived files and uploads them; a person reviews and commits them.
                     Automation never pushes, deletes or publishes.

Exit code 1 only when a check fails. Stale sources are reported, not failed, because refreshing them needs a person
(the crawl of GitHub and the Slack scan run in a signed-in browser). Run with python3 -I build/tools/self_routines.py.
"""
import datetime as dt, glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = lambda *a: os.path.join(ROOT, *a)

# Each source: where its date lives, and how old it may get before it is flagged.
SOURCES = [
    ("GitHub projects (xgov inventory)", lambda: json.load(open(P("build/xgov/xgov.json")))["generated"], 45),
    ("Check against GitHub (every account)", lambda: json.load(open(P("build/dama/ghverify.json")))["read"], 35),
    ("Crown dependencies, verified over git", lambda: json.load(open(P("build/dama/cdot.json")))["verified"], 90),
    ("Account provenance (accounts outside the registry)", lambda: json.load(open(P("build/dama/provenance.json")))["read"], 90),
]
NEEDED = [("README.md", None), ("LICENSE", None), ("LICENCE-CONTENT.md", None), ("SECURITY.md", None), ("CONTRIBUTING.md", None),
          ("CODE_OF_CONDUCT.md", None), (".github/CODEOWNERS", None), (".github/PULL_REQUEST_TEMPLATE.md", None),
          (".github/ISSUE_TEMPLATE/data-correction.yml", None), (".github/ISSUE_TEMPLATE/defect.yml", None), (".github/dependabot.yml", None),
          ("README.md", r"^## User guide"), ("README.md", r"^## Build it"), ("README.md", r"^## Test it"), ("README.md", r"^## Limits"),
          ("README.md", r"^## Self-\* routines"), ("README.md", r"^## Licence"), ("docs/releases.md", None), ("docs/defects.md", None)]

def age(today, iso):
    return (today - dt.date.fromisoformat(iso[:10])).days

def staleness(today, sources=SOURCES):
    out = []
    for name, get, limit in sources:
        try: d = get(); a = age(today, d); out.append(dict(source=name, date=d[:10], days=a, limit=limit, stale=a > limit, missing=False))
        except (OSError, KeyError, ValueError): out.append(dict(source=name, date="", days=None, limit=limit, stale=True, missing=True))
    return out

def assess(root=ROOT, needed=NEEDED):
    gaps = []
    for f, rx in needed:
        p = os.path.join(root, f)
        if not os.path.isfile(p): gaps.append(f); continue
        if rx and not re.search(rx, open(p, encoding="utf-8").read(), re.M): gaps.append(f"{f}: {rx.strip('^')}")
    return gaps

def verify(root=ROOT):
    files = sorted(glob.glob(os.path.join(root, "build", "dama", "*_checks.txt")))
    fails = [f"{os.path.basename(f)}: {l.strip()[:120]}" for f in files for l in open(f, encoding="utf-8") if l.startswith("FAIL")]
    return len(files), fails

def gh_fetch(path):
    """Read one GitHub API path with the gh CLI and the workflow's token. Returns parsed JSON, or None if unreadable."""
    import subprocess
    try: return json.loads(subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=60, check=True).stdout)
    except Exception: return None

def gh_graphql(query):
    import subprocess
    try: return json.loads(subprocess.run(["gh", "api", "graphql", "-f", "query=" + query], capture_output=True, text=True, timeout=60, check=True).stdout)
    except Exception: return None

def settings_audit(repo, fetch=gh_fetch, graphql=gh_graphql, baseline=None):
    """Compare the repository's settings with the baseline. Returns rows of (setting, expected, actual, state, reason);
    state is 'ok', 'drift' or 'unreadable' (the token can't see it: an owner checks by hand)."""
    B = baseline or json.load(open(P(".github/settings-baseline.json"))); rows = []
    r = fetch(f"repos/{repo}") or {}
    for k, (want, why) in B["repo"].items():
        have = (("private" in (r.get("description") or "").lower()) if k == "description_mentions_private" else r.get(k)) if r else None
        rows.append((k, want, have, "unreadable" if have is None else "ok" if have == want else "drift", why))
    sa = r.get("security_and_analysis") if r else None
    pvr = fetch(f"repos/{repo}/private-vulnerability-reporting")
    for k, (want, why) in B["security"].items():
        if k == "private_vulnerability_reporting": have = pvr.get("enabled") if isinstance(pvr, dict) else None
        else: have = (sa.get(k, {}).get("status") == "enabled") if isinstance(sa, dict) and k in sa else None
        rows.append((k, want, have, "unreadable" if have is None else "ok" if have == want else "drift", why))
    rs = fetch(f"repos/{repo}/rules/branches/main")
    have = None if rs is None else any(x.get("type") in ("pull_request", "non_fast_forward", "deletion") for x in rs)
    rows.append(("main_protected", True, have, "unreadable" if have is None else "ok" if have else "drift", B["rulesets"]["main_protected"][1]))
    o, n = repo.split("/")
    g = graphql(f'{{repository(owner:"{o}",name:"{n}"){{discussionCategories(first:50){{nodes{{slug}}}}}}}}')
    slugs = None if not g else [x["slug"] for x in g["data"]["repository"]["discussionCategories"]["nodes"]]
    for k, (want, why) in B["discussions"].items():
        have = None if slugs is None else k.split(":", 1)[1] in slugs
        rows.append((k, want, have, "unreadable" if have is None else "ok" if have == want else "drift", why))
    labs = fetch(f"repos/{repo}/labels?per_page=100")
    names = None if labs is None else {x["name"] for x in labs}
    need, why = B["labels"]["required"]
    missing = None if names is None else [l for l in need if l not in names]
    rows.append(("labels", "all present", "unreadable" if missing is None else "missing: " + ", ".join(missing) if missing else "all present", "unreadable" if missing is None else "drift" if missing else "ok", why))
    return rows

def main():
    today = dt.date.today(); lines, fails = [], []
    n, vf = verify(); st = staleness(today); gaps = assess()
    import subprocess   # the page can't be rebuilt here without the internal inputs (ADR 0004): check it against this commit's code instead
    vd = subprocess.run([sys.executable, "-I", P("build/tools/verify_dist.py")], capture_output=True, text=True)
    same = vd.returncode == 0
    # negative tests: the routines must catch what they are for
    neg_stale = staleness(today, [("t", lambda: "2000-01-01", 30), ("u", lambda: (_ for _ in ()).throw(KeyError()), 30)])
    neg_gap = assess(ROOT, [("no-such-file.md", None), ("README.md", r"^## No such section")])
    fake = {"repos/o/r": {"has_wiki": True, "has_issues": True, "has_discussions": True, "delete_branch_on_merge": True, "web_commit_signoff_required": True, "allow_squash_merge": False, "allow_auto_merge": False, "description": "Private: x",
                          "security_and_analysis": {"secret_scanning": {"status": "disabled"}, "secret_scanning_push_protection": {"status": "enabled"}, "dependabot_security_updates": {"status": "enabled"}}},
            "repos/o/r/private-vulnerability-reporting": {"enabled": False}, "repos/o/r/rules/branches/main": [], "repos/o/r/labels?per_page=100": [{"name": "defect"}]}
    neg_rows = settings_audit("o/r", fetch=fake.get, graphql=lambda q: {"data": {"repository": {"discussionCategories": {"nodes": [{"slug": "general"}]}}}})
    neg_drift = {r[0] for r in neg_rows if r[3] == "drift"}
    neg_set = neg_drift == {"has_wiki", "description_mentions_private", "private_vulnerability_reporting", "secret_scanning", "main_protected", "category:feature-assessment", "labels"}
    neg_ok = neg_stale[0]["stale"] and neg_stale[1]["missing"] and len(neg_gap) == 2 and neg_set
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    audit = settings_audit(repo) if repo else []
    if vf: fails.append("self-verification")
    if gaps: fails.append("self-assessment")
    if same is False: fails.append("dist is this commit's open edition")
    if not neg_ok: fails.append("negative tests")
    lines += [f"# Self-routines report, {today:%-d %B %Y}", "",
              f"- **Self-verification:** {n} check files, {len(vf)} failing" + ("".join(f"\n  - {x}" for x in vf)),
              f"- **dist/index.html is this commit's code and the open edition:** {'yes' if same else 'NO: rebuild it in the companion repository and commit'}",
              f"- **Self-assessment:** {'every repository file and README section is present' if not gaps else 'missing: ' + ', '.join(gaps)}",
              f"- **Negative tests:** {'the routines catch an old date, a missing source, a missing file, a missing section and 7 kinds of settings drift' if neg_ok else 'FAILED'}", "",
              "## Staleness", "", "| Source | Date | Age (days) | Limit | State |", "|---|---|---:|---:|---|"]
    for s in st:
        lines.append(f"| {s['source']} | {dt.date.fromisoformat(s['date']).strftime('%-d %B %Y') if s['date'] else 'not present'} | {'' if s['days'] is None else s['days']} | {s['limit']} | {'missing' if s['missing'] else 'stale: refresh it' if s['stale'] else 'current'} |")
    if audit:
        lines += ["", "## Repository settings", "", f"Compared with .github/settings-baseline.json. Drift is reported here, never changed: only an owner changes settings. {sum(1 for a in audit if a[3] == 'drift')} drifted, {sum(1 for a in audit if a[3] == 'unreadable')} not readable with the workflow's token (check those by hand).", "",
                  "| Setting | Expected | On GitHub | State | Why |", "|---|---|---|---|---|"] + [f"| {a[0]} | {a[1]} | {a[2]} | {a[3]} | {a[4]} |" for a in audit]
    lines += ["", "Refreshing a stale source needs a person: the GitHub crawl runs in a signed-in browser (see README, Self-* routines). The Slack scan's freshness is checked in the private companion repository."]
    open(P("self_report.md"), "w").write("\n".join(lines) + "\n")
    json.dump(dict(date=today.isoformat(), settings=[dict(setting=a[0], expected=a[1], actual=a[2], state=a[3]) for a in audit], checks=n, failing=vf, assessment_gaps=gaps, dist_matches=same, staleness=st, negative_tests=neg_ok, fails=fails), open(P("self_report.json"), "w"), indent=1)
    print("\n".join(lines))
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
