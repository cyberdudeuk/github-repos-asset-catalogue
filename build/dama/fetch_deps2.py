"""Second pass (31 Oct 2026): package manifests for every remaining git-checked repository with JavaScript, Ruby or JVM code, so links to GDS
components (govuk-frontend, Notify and Pay clients, One Login libraries) can be found. Same safety rules as fetch_deps.py: parse only, never execute."""
import os, re, gzip, sys, concurrent.futures as cf, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_deps as F
RX2 = {"js": r"(?:^|/)package\.json$", "rb": r"(?:^|/)Gemfile$", "jvm": r"(?:^|/)(?:pom\.xml|build\.gradle(?:\.kts)?|build\.sbt)$", "py": F.RX["py"]}
jobs = []
for d in sorted(os.listdir(F.E)):
    if os.path.exists(f"{F.OUT}/{d}.json"): continue
    try: t = gzip.open(f"{F.E}/{d}/tree.gz", "rt", errors="replace").read().splitlines()
    except Exception: continue
    t = [p for p in t if "node_modules/" not in p and "/vendor/" not in p and "/test" not in p.lower()]
    files = [p for k, r in RX2.items() for p in [x for x in t if re.search(r, x)][:2]]
    if files: jobs.append((d, files))
print("repositories", len(jobs), "files", sum(len(f) for _, f in jobs), flush=True)
res = collections.Counter(); n = 0
with cf.ThreadPoolExecutor(32) as ex:
    for d, s in ex.map(F.job, jobs):
        res[s.split(" ")[0]] += 1; n += 1
        if n % 250 == 0: print(n, dict(res), flush=True)
print("done", dict(res), flush=True)
