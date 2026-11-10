"""Step 5 of the refresh (R75): bring the git-verified government layer (xgov/xgov.json) up to the reference date.

  python3 -I build/refresh/apply.py

For every row of the layer:
  - no longer publicly readable (reconcile: removed): taken out, and counted in the account's "removed" figure
  - probed with git: branch, newest commit, newest human commit, human commits in 90 and 365 days, all commits and
    authors come from the probe; status follows the same rules as before (Archived, Active, Maintained, Automated only,
    Dormant, Inactive, Unverified)
  - not probed because it was archived or not pushed in 365 days: no commits in the windows by definition; status from
    the newest commit already known
  - archived flag and description from the new scraper file where it has the repository
co-cddo rows keep the deeper inventory's figures (defect D8: the inventory is authoritative for that account).
Enrichment fields (README lede, licence, CODEOWNERS and the other practice signals) stay as read on the previous snapshot
date and are labelled with that date on the page. Writes xgov.json and refresh_checks.txt.
"""
import json
import os
import re
import sys

H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from common import ASOF, BUILD, REFE, cut, ep, read_json

XG = os.path.join(BUILD, "xgov", "xgov.json")


def status(archived, v, lh, any12, lc):
    if archived: return "Archived"
    if v != "ok": return "Unverified"
    if lh and lh >= cut(90): return "Active"
    if lh and lh >= cut(365): return "Maintained"
    if any12: return "Automated only"
    if lc and lc >= cut(730): return "Dormant"
    return "Inactive"


def main():
    xg = json.load(open(XG))
    if xg.get("refresh", {}).get("ref") == ASOF["ref"]:
        sys.exit(f"xgov.json is already at {ASOF['ref']}: restore the previous snapshot's file (git checkout build/xgov/xgov.json) and run again")
    new = {(r["owner"].lower(), r["name"].lower()): r for r in read_json(os.path.join(H, "sources", "repos.json.gz")) if isinstance(r, dict) and r.get("owner") and r.get("name")}
    rec = read_json(os.path.join(H, "sources", "reconcile.json.gz"))
    for r in rec["carried"]: new.setdefault((r["owner"].lower(), r["name"].lower()), r)
    removed = {(r["owner"].lower(), r["name"].lower()) for r in rec["removed"]}
    pr = read_json(os.path.join(H, "sources", "probe.json.gz"))
    P = pr["repos"]; OA = pr.get("org_authors12", {})
    checks = []
    def check(ok, cid, msg, guards): checks.append(("PASS " if ok else "FAIL ") + f"{cid} {msg}   [guards: {guards}]"); return ok
    rows, gone, changed = [], {}, 0
    for r in xg["rows"]:
        k = (r["o"].lower(), r["n"].lower())
        if k in removed and r["o"] != "co-cddo":
            gone[r["o"]] = gone.get(r["o"], 0) + 1; continue
        s = new.get(k)
        if r["o"] != "co-cddo":
            old = (r["st"], r["c12"])
            if s is not None:
                r["a"] = bool(s.get("archived"))
                d = re.sub(r"\s+", " ", s.get("description") or "")[:220]
                if d and not r.get("d"): r["d"] = d
            p = P.get(f"{r['o']}/{r['n']}".lower())
            if p and p.get("v") == "ok":
                r.update(v="ok", b=p["b"] or r.get("b", ""), lc=p["lc"] or r.get("lc"), lh=p["lh"], c12=p["c12"], c90=p["c90"], any12=p["any12"], a12=p["a12"])
            elif p:
                r.update(v=p["v"], c12=0, c90=0, any12=0, a12=0, lh=None)
            else:
                r.update(c12=0, c90=0, any12=0, a12=0, lh=None)
                pushed = ep(s.get("pushedAt")) if s else None
                if pushed and r.get("lc") and pushed < r["lc"]: r["lc"] = pushed
            created = ep(s.get("createdAt")) if s else None
            r["new"] = bool(created and created >= cut(365)); r["fc"] = created if r["new"] else None
            r["st"] = status(r["a"], r.get("v"), r.get("lh"), r.get("any12"), r.get("lc"))
            changed += (r["st"], r["c12"]) != old
        rows.append(r)
    xg["rows"] = rows
    # account figures, recomputed from the rows (co-cddo's inventory rows included)
    for o in xg["orgs"]:
        R = [r for r in rows if r["o"] == o["org"]]
        o.update(listed=len(R), verified=sum(r.get("v") == "ok" for r in R), missing=sum(r.get("v") == "missing" for r in R), archived=sum(bool(r["a"]) for r in R),
                 active90=sum(r["st"] == "Active" for r in R), active365=sum(r["st"] in ("Active", "Maintained") for r in R), bots_only=sum(r["st"] == "Automated only" for r in R),
                 commits12=sum(r["c12"] for r in R), new12=sum(bool(r["new"]) for r in R), pages=sum(bool(r.get("pg")) for r in R),
                 master=sum(r.get("b") == "master" for r in R), main=sum(r.get("b") == "main" for r in R), removed=gone.get(o["org"], 0))
        if o["org"] != "co-cddo":
            o["authors12"] = OA.get(o["org"].lower())
    xg["generated"] = ASOF["ref"]; xg["xref"] = ASOF["ref"]; xg["previous"] = ASOF["previous"]
    xg["refresh"] = dict(ref=ASOF["ref"], probed=sum(1 for v in P.values() if v.get("v") == "ok"), removed=sum(gone.values()), changed=changed,
                         enrichment_read=ASOF["previous"], authors="distinct people per account, counted once across its repositories" if OA else None)
    check(all(r["c12"] == 0 for r in rows if r["o"] != "co-cddo" and not P.get(f"{r['o']}/{r['n']}".lower())), "C-REF-01", "rows not probed claim no commits in the last 12 months", "V717-1")
    bad = [r for r in rows if r["o"] != "co-cddo" and r["st"] in ("Active", "Maintained") and not (r.get("lh") and r["lh"] >= cut(365))]
    check(not bad, "C-REF-02", f"no row is called Active or Maintained without a human commit in the 365 days to {ASOF['ref']} ({len(bad)} found)", "V717-1")
    check(not any((r["o"].lower(), r["n"].lower()) in removed for r in rows if r["o"] != "co-cddo"), "C-REF-03", f"repositories no longer publicly readable are not listed ({sum(gone.values())} taken out)", "V717-2")
    check(bool(OA) and all(o.get("authors12") is not None for o in xg["orgs"] if o["org"] != "co-cddo" and o["active365"]), "C-REF-04", "every account with recent human commits has a distinct author count", "V717-1")
    # negative tests
    neg = [status(False, "ok", REFE - 400 * 86400, 0, None) in ("Active", "Maintained"), status(True, "ok", REFE, 1, REFE) != "Archived", status(False, "missing", REFE, 1, REFE) != "Unverified"]
    check(not any(neg), "C-REF-04n", "negative tests: a 400-day-old human commit, an archived repository and an unreadable one each get the right status", "V717-1")
    json.dump(xg, open(XG, "w"), ensure_ascii=False, separators=(",", ":"))
    open(os.path.join(H, "refresh_checks.txt"), "w").write("\n".join(checks) + "\n")
    print("\n".join(checks)); print(f"{len(rows)} rows; {changed} changed status or commit count; {sum(gone.values())} removed")
    return 0 if all(c.startswith("PASS") for c in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
