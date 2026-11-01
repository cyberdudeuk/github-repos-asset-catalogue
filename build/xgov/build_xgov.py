"""Cross-government layer v2 (2026-10-08).
Sources, in order of authority: git probe (existence, default branch, commits in the 12 months to 7 Oct 2026, bots excluded);
git enrichment at HEAD on 8 Oct 2026 (README lede, licence, CODEOWNERS, Dependabot, SECURITY.md, workflow pinning and permissions,
standards evidenced by files); GitHub's own repositoryCount per organisation (browser, 8 Oct 2026, checksum-verified);
the summarised listing read (descriptions, topics, language) — lowest confidence, labelled as such.
co-cddo rows take status and counts from the deeper inventory so both layers agree (defect D8).
Writes xgov.json and xgov_checks.txt. Every check has an ID and names the defect it guards."""
import json, os, re, sys, collections, datetime as dt
S = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, S)
INV = os.path.join(os.path.dirname(S), "inv"); sys.path.insert(0, INV)
from taxonomy import tag, sector, STRATEGY, STANDARDS, readme_lede
from analyse import is_bot                                  # one bot rule for both layers
XREF = dt.date(2026, 10, 7)                                  # probe snapshot date (cross-government activity)
def cut(days):
    d = XREF - dt.timedelta(days=days); return int(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp())
def ddays(e): return (XREF - dt.datetime.fromtimestamp(e, dt.timezone.utc).date()).days
orgs = json.load(open(os.path.join(S, "orgs.json")))
enr = json.load(open(os.path.join(S, "enr.json"))) if os.path.exists(os.path.join(S, "enr.json")) else {}
totals = {l.split("\t")[0]: l.split("\t")[1] for l in open(os.path.join(S, "org_totals.tsv")).read().strip().split("\n")}
inv_rows = {r["repo"]: r for r in json.load(open(os.path.join(INV, "rows.json")))}
checks = []
def check(ok, cid, msg, guards):
    checks.append(("PASS " if ok else "FAIL ") + f"{cid} {msg}   [guards: {guards}]"); return ok

def read_page(o, r):
    p = os.path.join(S, "pages", f"{o}__{r}")
    if not os.path.exists(p): return None
    parts = open(p).read().strip().split("|")
    return dict(url=parts[0], first=parts[1], redirect=parts[2], final=parts[3], effective=parts[4]) if len(parts) >= 5 else None
control = {o: read_page(o, "zz-control-not-a-repo-q7") for o, _, _ in orgs}

rows, orgstat = [], {}
for o, section, src in orgs:
    sec = sector(o, section)
    t = totals.get(o)
    st = orgstat[o] = dict(org=o, section=section, sector=sec, source=src, total_on_github=(None if t in (None, "404") else int(t)), deleted=(t == "404"),
                           listed=0, verified=0, missing=0, active90=0, active365=0, bots_only=0, commits12=0, authors12=set(), new12=0, pages=0, archived=0, master=0, main=0)
    seen = set()
    for i, line in enumerate(open(os.path.join(S, "raw", f"{o}.tsv"), errors="replace")):
        if i == 0 and line.startswith("name"): continue
        f = line.rstrip("\n").split("\t") + [""] * 7
        n = f[0].strip()
        if not n or not re.fullmatch(r"[A-Za-z0-9._-]+", n) or n.lower() in seen: continue
        seen.add(n.lower()); st["listed"] += 1
        status_l = f[5].strip()
        desc = re.sub(r"\s+", " ", f[6].strip())[:220]
        if desc.lower() in ("unknown", "n/a", "none", "(none)", "-", "—") or re.fullmatch(r"[\[(]no description[^\])]*[\])]", desc, re.I): desc = ""
        topics = f[3].strip() if not re.search(r"licen[cs]e|unknown|^n/?a$|^none$", f[3], re.I) else ""
        lang = f[2].strip() if not re.search(r"licen[cs]e|unknown|not specified|^n/?a$", f[2], re.I) else ""
        pr = os.path.join(S, "probe", f"{o}__{n}.txt")
        git = dict(status="unprobed")
        if os.path.exists(pr):
            L = open(pr, errors="replace").read().splitlines()
            h = L[0].split("|") if L else ["?"]
            git = dict(status=h[0], branch=h[1] if len(h) > 1 else "", last=int(h[2]) if len(h) > 2 and h[2].isdigit() else None,
                       shallow=(h[3] if len(h) > 3 else ""), first=int(h[4]) if len(h) > 4 and h[4].isdigit() else None)
            com, allc = [], 0
            for l in L[1:]:
                q = l.split("|", 2)
                if len(q) == 3 and q[0].isdigit() and int(q[0]) >= cut(365):
                    allc += 1
                    if not is_bot(q[1], q[2]): com.append(q)
            git["c12"] = len(com); git["c90"] = sum(1 for q in com if int(q[0]) >= cut(90)); git["any12"] = allc
            git["lh"] = max((int(q[0]) for q in com), default=None)
            git["akeys"] = list({q[2].strip().lower() for q in com})
        archived = "archiv" in status_l.lower()
        lh, lc = git.get("lh"), git.get("last")
        if archived: stt = "Archived"
        elif git["status"] != "ok": stt = "Unverified"
        elif lh and ddays(lh) <= 90: stt = "Active"
        elif lh: stt = "Maintained"
        elif git.get("any12"): stt = "Automated only"
        elif lc and ddays(lc) <= 730: stt = "Dormant"
        else: stt = "Inactive"
        e = enr.get(f"{o}/{n}", {})
        lede = e.get("lede", "")
        tags, stds, dam = tag(n, desc, topics, lede, sec)
        stds = sorted(set(stds) | set(e.get("std_files", {})))
        pg = read_page(o, n)
        live = bool(pg and pg["final"] == "200")
        custom = ""
        if live and pg["first"] in ("301", "302") and pg["redirect"]:
            host = re.sub(r"^https?://", "", pg["redirect"]).split("/")[0]
            if not host.endswith("github.io"): custom = host
        r = dict(o=o, n=n, d=desc, ld=lede, l=lang, t=topics, a=archived, v=git["status"], b=git.get("branch", ""),
                 lc=lc, lh=lh, c12=git.get("c12", 0), c90=git.get("c90", 0), any12=git.get("any12", 0), a12=len(git.get("akeys", [])),
                 new=bool(git.get("shallow") == "0" and git.get("first") and git["first"] >= cut(365)), fc=git.get("first") if git.get("shallow") == "0" else None,
                 g=tags, s=stds, dam=dam, pg=live, pu=(pg["effective"] if live else ""), cd=custom, st=stt, e=e)
        # co-cddo: the inventory is deeper (all branches, re-read 8 Oct) and is authoritative for status and counts (D8)
        if o == "co-cddo" and n in inv_rows:
            ir = inv_rows[n]
            r.update(st=ir["status"], lh=ir["last_human_epoch"], c12=ir["human_commits_365d"], c90=ir["human_commits_90d"], a12=ir["authors_365d"], d=ir["description"] or desc, ld=ir["readme_summary"], a=ir["archived"])
        rows.append(r)
        st["verified"] += r["v"] == "ok"; st["missing"] += r["v"] == "missing"; st["archived"] += r["a"]
        st["active90"] += r["st"] == "Active"; st["active365"] += r["st"] in ("Active", "Maintained"); st["bots_only"] += r["st"] == "Automated only"
        st["commits12"] += r["c12"]; st["authors12"] |= set(git.get("akeys", [])); st["new12"] += r["new"]; st["pages"] += r["pg"]
        st["master"] += r["b"] == "master"; st["main"] += r["b"] == "main"
    # co-cddo repos missing from the summarised listing (D1) are added from the inventory
    if o == "co-cddo":
        for n, ir in inv_rows.items():
            if n.lower() in seen: continue
            pg = read_page(o, n); live = bool(pg and pg["final"] == "200")
            tags, stds, dam = tag(n, ir["description"], ir["topics"], ir["readme_summary"], sec)
            rows.append(dict(o=o, n=n, d=ir["description"], ld=ir["readme_summary"], l=ir["language"], t=ir["topics"], a=ir["archived"], v="ok", b=ir["default_branch"],
                             lc=None, lh=ir["last_human_epoch"], c12=ir["human_commits_365d"], c90=ir["human_commits_90d"], any12=ir["human_commits_365d"], a12=ir["authors_365d"],
                             new=False, fc=None, g=tags, s=stds, dam=dam, pg=live, pu=(pg["effective"] if live else ""), cd="", st=ir["status"], e={}, added_from_inventory=True))
            st["listed"] += 1; st["verified"] += 1; st["active90"] += ir["status"] == "Active"; st["active365"] += ir["status"] in ("Active", "Maintained"); st["pages"] += live; st["commits12"] += ir["human_commits_365d"]
for st in orgstat.values(): st["authors12"] = len(st["authors12"])

# ---- similarity co-cddo <-> rest of government (TF-IDF over name, description, topics, README lede) ----
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
co = list(inv_rows.values())
nz = lambda *x: re.sub(r"[-_.]+", " ", " ".join(v for v in x if v)).lower()
dx = [nz(r["n"], r["d"], r["t"], r["ld"]) for r in rows]
dc = [nz(r["repo"], r["description"], r["readme_summary"], r["topics"]) for r in co]
vec = TfidfVectorizer(stop_words="english", min_df=2, ngram_range=(1, 2), sublinear_tf=True, max_features=200000).fit(dx + dc)
sim = linear_kernel(vec.transform(dc), vec.transform(dx))
links = {}
for i, r in enumerate(co):
    out = []
    for j in sim[i].argsort()[::-1][:80]:
        if sim[i, j] < 0.22: break
        x = rows[j]
        if x["o"] == "co-cddo" or x["st"] in ("Unverified", "Archived"): continue
        out.append([x["o"], x["n"], round(float(sim[i, j]), 2)])
        if len(out) == 6: break
    links[r["repo"]] = out

# ---- checks ----
total = len(rows)
check(len(orgs) == len(orgstat) == 219, "C-X-01", f"{len(orgs)} organisations processed (215 registry + 4 added)", "dropped organisations")
probed = sum(r["v"] != "unprobed" for r in rows)
check(probed == total, "C-X-02", f"every listed repo git-probed ({probed}/{total})", "unverified rows passing as verified")
check(all(r.get("added_from_inventory") or os.path.exists(os.path.join(S, "pages", f"{r['o']}__{r['n']}")) for r in rows), "C-X-03", "every listed repo Pages-probed", "Pages list silently incomplete")
check(all(not r["pg"] or r["pu"] for r in rows), "C-X-04", "every live Pages site has an effective URL", "Pages flag without evidence")
check(all(r["c90"] <= r["c12"] for r in rows), "C-X-05", "90-day human commits <= 12-month human commits", "window arithmetic")
check(all((r["st"] == "Active") == (r["c90"] > 0 and not r["a"] and r["v"] == "ok") for r in rows if r["o"] != "co-cddo"), "C-X-06", "Active if and only if a human commit in the last 90 days", "D8: Active included bot-only activity")
coin = [r for r in rows if r["o"] == "co-cddo"]
check(not any(re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f\ufffd]", (r["ld"] or "") + (r["d"] or "")) for r in rows), "C-X-13", "no control or replacement characters in descriptions or README paragraphs", "V4-3: UTF-16 READMEs read as UTF-8 produced unreadable text")
check(all(r["lh"] == inv_rows[r["n"]]["last_human_epoch"] and r["c90"] == inv_rows[r["n"]]["human_commits_90d"] for r in coin), "C-X-12", "co-cddo rows carry the inventory's last human commit and 90-day count", "V4-1: last human commit taken from the default branch while counts came from all branches")
check({r["n"] for r in coin} == set(inv_rows) and all(r["st"] == inv_rows[r["n"]]["status"] for r in coin), "C-X-07", f"co-cddo rows in both layers match the inventory ({len(coin)} repos, same status)", "D1/D8: layers disagreed on membership and status")
check(sum(st["listed"] for st in orgstat.values()) == total, "C-X-08", "organisation listed counts sum to the repo total", "org/repo drift")
check(all(st["total_on_github"] is None or st["listed"] <= st["total_on_github"] for st in orgstat.values()), "C-X-09", "no organisation lists more repos than GitHub's own total", "phantom rows from summarised listing reads")
ctl = [o for o, c in control.items() if c and c["final"] == "200"]
check(not ctl, "C-X-10", "no organisation serves a page for a non-existent repo (control address)", "org-wide catch-all making every repo look like it has Pages")
check(all(not r["dam"] or not re.search(r"weather ?data ?hub|model[- ]run metadata", (r["d"] + " " + r["ld"]).lower()) for r in rows), "C-X-11", "known DAM false positives stay excluded", "D7 precision")
deleted = [o for o, s in orgstat.items() if s["deleted"]]
checks.append(f"INFO organisations deleted from GitHub since the registry was written: {', '.join(deleted)}")
checks.append(f"INFO enrichment coverage: {sum(1 for r in rows if r['e'] and r['st'] in ('Active','Maintained') and r['o'] != 'co-cddo')} of {sum(1 for r in rows if r['st'] in ('Active','Maintained') and r['o'] != 'co-cddo')} active or maintained repos outside co-cddo ({sum(1 for r in rows if r['e'])} enriched in all)")
json.dump(dict(generated="2026-10-08", xref=XREF.isoformat(), rows=rows, orgs=list(orgstat.values()), links=links,
               strategy=[dict(id=a, short=b, label=c, group=d, url=e) for a, b, c, d, e, _ in STRATEGY], standards=[n for n, _ in STANDARDS]),
          open(os.path.join(S, "xgov.json"), "w"), separators=(",", ":"))
open(os.path.join(S, "xgov_checks.txt"), "w").write("\n".join(checks) + "\n")
print("\n".join(checks))
print(collections.Counter(r["st"] for r in rows), "total", total)
print("pages", sum(r["pg"] for r in rows), "new", sum(r["new"] for r in rows), "dam", sum(bool(r["dam"]) for r in rows), collections.Counter(t for r in rows for t in r["g"]))
sys.exit(1 if any(c.startswith("FAIL") for c in checks) else 0)
