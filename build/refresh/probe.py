"""Step 3 of the refresh (R75): measure people's activity, with git, in every repository pushed in the last 12 months.

  python3 -I build/refresh/probe.py [--workers 8] [--cache DIR]

For each repository that is not archived and was pushed in the 365 days to the reference date, git fetches only the
default branch's commit history since then (a bare clone with no file contents: --filter=tree:0 --shallow-since).
Commits by automation are told apart with the one shared rule, analyse.is_bot.

Only aggregates are kept: the default branch, the newest commit, the newest human commit, human commits in 90 and
365 days, all commits in 365 days and the number of distinct human authors, per repository and per account. Never a name
or an email address. To count a person once across an account's repositories, the local cache holds author keys hashed
with a random salt that never leaves the machine; the committed file holds only the counts.
Writes sources/probe.json.gz. A cache directory lets an interrupted run carry on where it stopped.
"""
import concurrent.futures as cf
import hashlib
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "inv"))
from analyse import is_bot
from common import ASOF, H, REF, cut, ep, git, read_json, write_json_gz
import datetime as dt

SINCE = (REF - dt.timedelta(days=365)).strftime("%Y-%m-%d")


def targets():
    new = read_json(os.path.join(H, "sources", "repos.json.gz"))
    rec = read_json(os.path.join(H, "sources", "reconcile.json.gz"))
    seen, out = set(), []
    for r in list(new) + rec["carried"]:
        if not isinstance(r, dict) or not r.get("owner") or not r.get("name"): continue
        k = (r["owner"].lower(), r["name"].lower())
        if k in seen: continue
        seen.add(k)
        p = ep(r.get("pushedAt"))
        if not r.get("archived") and p and p >= cut(365): out.append((r["owner"], r["name"]))
    return out


SALT = None


def aggregate(lines, branch, last):
    hum, allc, authors = [], 0, set()
    for l in lines:
        q = l.split("|", 2)
        if len(q) != 3 or not q[0].isdigit() or int(q[0]) < cut(365) or int(q[0]) > cut(-1): continue
        allc += 1
        if not is_bot(q[1], q[2]):
            hum.append(int(q[0])); authors.add(hashlib.sha256((SALT + (q[2] or q[1]).strip().lower()).encode()).hexdigest()[:16])
    return dict(v="ok", b=branch, lc=last, lh=max(hum) if hum else None, c12=len(hum), c90=sum(1 for t in hum if t >= cut(90)), any12=allc, a12=len(authors), ah=sorted(authors))


def probe(o, n):
    url = f"https://github.com/{o}/{n}"
    d = tempfile.mkdtemp(prefix="probe-")
    try:
        rc, out, err = git(["clone", "--bare", "--quiet", "--filter=tree:0", "--no-tags", "--single-branch", f"--shallow-since={SINCE}", url, d], timeout=300)
        if rc != 0 and ("no commits" in err.lower() or "shallow" in err.lower() or "remote did not send all" in err.lower()):
            shutil.rmtree(d, ignore_errors=True); d = tempfile.mkdtemp(prefix="probe-")
            rc, out, err = git(["clone", "--bare", "--quiet", "--filter=tree:0", "--no-tags", "--single-branch", "--depth=1", url, d], timeout=300)
        if rc != 0:
            gone = "could not read Username" in err or "not found" in err.lower()
            return dict(v="missing" if gone else "error", why=err.strip().splitlines()[-1][:160] if err.strip() else str(rc))
        _, br, _ = git(["symbolic-ref", "--short", "HEAD"], cwd=d)
        rc, log, err = git(["log", "--format=%ct|%an|%ae", "HEAD"], cwd=d, timeout=120)
        lines = log.splitlines() if rc == 0 else []
        last = int(lines[0].split("|", 1)[0]) if lines and lines[0].split("|", 1)[0].isdigit() else None
        return aggregate(lines, br.strip(), last)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 8
    cache = sys.argv[sys.argv.index("--cache") + 1] if "--cache" in sys.argv else os.path.join(tempfile.gettempdir(), "ghrac-probe-cache")
    os.makedirs(cache, exist_ok=True)
    global SALT
    sp = os.path.join(cache, "salt")
    if not os.path.exists(sp): open(sp, "w").write(os.urandom(16).hex())
    SALT = open(sp).read().strip()
    T = targets(); print(len(T), "repositories to probe since", SINCE, flush=True)
    key = lambda o, n: os.path.join(cache, hashlib.sha256(f"{o}/{n}".lower().encode()).hexdigest()[:24] + ".json")
    todo = [(o, n) for o, n in T if not os.path.exists(key(o, n))]

    def job(o, n):
        r = probe(o, n)
        if r.get("v") == "error":   # one retry for network trouble
            r = probe(o, n)
        json.dump(r, open(key(o, n), "w"))
        return r
    with cf.ThreadPoolExecutor(workers) as ex:
        for i, _ in enumerate(cf.as_completed([ex.submit(job, o, n) for o, n in todo]), 1):
            if i % 200 == 0: print(i, "of", len(todo), flush=True)
    res, org_auth = {}, {}
    for o, n in T:
        r = json.load(open(key(o, n)))
        org_auth.setdefault(o.lower(), set()).update(r.pop("ah", []))
        res[f"{o}/{n}".lower()] = r
    counts = {}
    for r in res.values(): counts[r["v"]] = counts.get(r["v"], 0) + 1
    write_json_gz(os.path.join(H, "sources", "probe.json.gz"), dict(ref=ASOF["ref"], since=SINCE, repos=res, org_authors12={o: len(v) for o, v in sorted(org_auth.items())}))
    print("probed:", counts)


if __name__ == "__main__":
    main()
