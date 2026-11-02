"""The self-* routines for the GitHub Repos Asset Catalogue, run weekly by .github/workflows/self-routines.yml and by hand.

  self-verification  every *_checks.txt written by the data scripts passes, and the public build matches dist/index.html
  self-assessment    the repository has what a well-kept GitHub repository needs (README sections, licences, security
                     policy, code owners, contributing guide, issue and pull request templates, Dependabot)
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
    ("Slack and collaboration scan", lambda: json.load(open(P("build/dama/collab.json")))["read"], 35),
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

def main():
    today = dt.date.today(); lines, fails = [], []
    n, vf = verify(); st = staleness(today); gaps = assess()
    built = P("build/inv/explorer71_public.html"); dist = P("dist/index.html")
    same = None
    if os.path.exists(built) and os.path.exists(dist):
        same = open(dist, encoding="utf-8").read().split("\n", 3)[3] == open(built, encoding="utf-8").read()
    # negative tests: the routines must catch what they are for
    neg_stale = staleness(today, [("t", lambda: "2000-01-01", 30), ("u", lambda: (_ for _ in ()).throw(KeyError()), 30)])
    neg_gap = assess(ROOT, [("no-such-file.md", None), ("README.md", r"^## No such section")])
    neg_ok = neg_stale[0]["stale"] and neg_stale[1]["missing"] and len(neg_gap) == 2
    if vf: fails.append("self-verification")
    if gaps: fails.append("self-assessment")
    if same is False: fails.append("dist matches the build")
    if not neg_ok: fails.append("negative tests")
    lines += [f"# Self-routines report, {today:%-d %B %Y}", "",
              f"- **Self-verification:** {n} check files, {len(vf)} failing" + ("".join(f"\n  - {x}" for x in vf)),
              f"- **dist/index.html matches the public build:** {'yes' if same else 'not built in this run' if same is None else 'NO: rebuild and commit'}",
              f"- **Self-assessment:** {'every repository file and README section is present' if not gaps else 'missing: ' + ', '.join(gaps)}",
              f"- **Negative tests:** {'the routines catch an old date, a missing source, a missing file and a missing section' if neg_ok else 'FAILED'}", "",
              "## Staleness", "", "| Source | Date | Age (days) | Limit | State |", "|---|---|---:|---:|---|"]
    for s in st:
        lines.append(f"| {s['source']} | {dt.date.fromisoformat(s['date']).strftime('%-d %B %Y') if s['date'] else 'not present'} | {'' if s['days'] is None else s['days']} | {s['limit']} | {'missing' if s['missing'] else 'stale: refresh it' if s['stale'] else 'current'} |")
    lines += ["", "Refreshing a stale source needs a person: the GitHub crawl and the Slack scan run in a signed-in browser (see README, Self-* routines)."]
    open(P("self_report.md"), "w").write("\n".join(lines) + "\n")
    json.dump(dict(date=today.isoformat(), checks=n, failing=vf, assessment_gaps=gaps, dist_matches=same, staleness=st, negative_tests=neg_ok, fails=fails), open(P("self_report.json"), "w"), indent=1)
    print("\n".join(lines))
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
