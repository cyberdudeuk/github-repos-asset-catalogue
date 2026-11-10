"""Step 2 of the refresh (R75, defect V717-2): make sure the new scraper file has not silently lost repositories.

  python3 -I build/refresh/reconcile.py [--workers 12]

The scraper's file can be incomplete: on 10 November 2026 it listed 240 ONSdigital repositories where GitHub shows 1,475.
So every repository that was in the previous catalogue but is missing from the new file is checked with
`git ls-remote` (public read, no credentials):
  - it answers: the repository still exists and is public, so its previous row is carried forward, marked as such
  - it does not: it was deleted, renamed away or made private, so it is recorded as removed, with the date checked
It also records which repositories in the new file were not in the previous snapshot (added), and every account's list in
the previous snapshot, so checks made against GitHub between the two snapshots are reconciled with the snapshot they were
made against.
Writes sources/reconcile.json.gz and prints a summary per account.
"""
import collections
import concurrent.futures as cf
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ASOF, BUILD, H, git, read_json, write_json_gz

LIC_BACK = {"M": "MIT", "O": "OGL-UK-3.0", "A": "Apache-2.0", "G": "GPL-3.0", "P": "MPL-2.0", "U": "Unlicense", "B": "BSD-3-Clause", "C": "CC0-1.0", "X": "NOASSERTION"}


def previous_rows(cat_path=None, xg_path=None):
    """The previous snapshot's repositories, in the scraper's own shape. Run before the catalogue is rebuilt (run.sh)."""
    cat = json.load(open(cat_path or os.path.join(BUILD, "catalogue", "catalogue.json")))
    xg = json.load(open(xg_path or os.path.join(BUILD, "xgov", "xgov.json")))
    xrow = {(r["o"].lower(), r["n"].lower()): r for r in xg["rows"]}
    iso = lambda e: __import__("datetime").datetime.fromtimestamp(e, __import__("datetime").timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if e else None
    lic = lambda c: {"spdxId": LIC_BACK[c]} if c in LIC_BACK else None
    out = {}
    for c in cat["cat"]:
        o = cat["orgs"][c[0]]["org"]
        out[(o.lower(), c[1].lower())] = dict(owner=o, name=c[1], description=c[2], language=c[3] or None, license=lic(c[4]), stargazersCount=c[5], forksCount=c[6],
                                              archived=bool(c[7]), pushedAt=iso(c[8]), createdAt=iso(c[9]), openIssuesCount=None)
    for k, v in cat["extra"].items():
        o, n = k.split("/", 1); x = xrow.get((o, n), {})
        out[(o, n)] = dict(owner=x.get("o", o), name=x.get("n", n), description=x.get("d", ""), language=x.get("l") or None, license=lic(v[2]), stargazersCount=v[0],
                           forksCount=v[1], archived=bool(x.get("a")), pushedAt=iso(v[5]), createdAt=iso(v[3]), openIssuesCount=v[4])
    return out


def previous_names(cat_path=None, xg_path=None):
    """Each account's repositories in the previous snapshot, built the way the GitHub check builds its list (ghverify.expected)."""
    cat = json.load(open(cat_path or os.path.join(BUILD, "catalogue", "catalogue.json")))
    xg = json.load(open(xg_path or os.path.join(BUILD, "xgov", "xgov.json")))
    out = {}
    for r in xg["rows"]: out.setdefault(r["o"], set()).add(r["n"])
    for c in cat["cat"]: out.setdefault(cat["orgs"][c[0]]["org"], set()).add(c[1])
    return out


def check(row):
    url = f"https://github.com/{row['owner']}/{row['name']}"
    for attempt in range(3):
        rc, out, err = git(["ls-remote", "--symref", url, "HEAD"], timeout=60)
        if rc == 0: return "exists", out.split("\n", 1)[0]
        if "Repository not found" in err or "could not read Username" in err or "terminal prompts disabled" in err or "not found" in err.lower():
            return "gone", err.strip().splitlines()[-1][:160] if err.strip() else ""
    return "error", err.strip()[-160:]


def main():
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 12
    new = read_json(os.path.join(H, "sources", "repos.json.gz"))
    have = {(r["owner"].lower(), r["name"].lower()) for r in new if isinstance(r, dict) and r.get("owner") and r.get("name")}
    prev = previous_rows()
    missing = {k: v for k, v in prev.items() if k not in have}
    print(f"{len(prev)} previous, {len(have)} in the new file, {len(missing)} missing from it: checking each with git")
    res = {}
    with cf.ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(check, v): k for k, v in missing.items()}
        for i, f in enumerate(cf.as_completed(futs), 1):
            res[futs[f]] = f.result()
            if i % 250 == 0: print(i, "checked", flush=True)
    carried = [dict(missing[k], carried_from=ASOF["previous"]) for k, (s, _) in res.items() if s == "exists"]
    removed = [dict(owner=missing[k]["owner"], name=missing[k]["name"], checked=ASOF["ref"], why=w) for k, (s, w) in res.items() if s == "gone"]
    errors = [dict(owner=missing[k]["owner"], name=missing[k]["name"], why=w) for k, (s, w) in res.items() if s == "error"]
    per = collections.defaultdict(lambda: [0, 0, 0])
    for r in carried: per[r["owner"]][0] += 1
    for r in removed: per[r["owner"]][1] += 1
    for r in errors: per[r["owner"]][2] += 1
    prev_names = previous_names()
    added = sorted(f"{r['owner']}/{r['name']}" for r in new if isinstance(r, dict) and r.get("owner") and r.get("name") and (r["owner"].lower(), r["name"].lower()) not in prev)
    write_json_gz(os.path.join(H, "sources", "reconcile.json.gz"), dict(checked=ASOF["ref"], previous=ASOF["previous"], carried=sorted(carried, key=lambda r: (r["owner"].lower(), r["name"].lower())),
                                                                       removed=sorted(removed, key=lambda r: (r["owner"].lower(), r["name"].lower())), errors=errors, added=added,
                                                                       previous_names={o: sorted(v, key=str.lower) for o, v in sorted(prev_names.items())}))
    print(f"carried forward {len(carried)}, removed {len(removed)}, could not check {len(errors)}")
    for o, (c, r, e) in sorted(per.items(), key=lambda x: -sum(x[1]))[:20]: print(f"  {o}: {c} carried, {r} removed, {e} errors")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
