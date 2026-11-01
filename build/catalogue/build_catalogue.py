"""GitHub Repos Asset Catalogue: one asset record per public-sector repository, joining
  (1) the X-Gov open-source repo scraper's nightly repos.json (read 8 Oct 2026, every public repo of every listed account),
  (2) the git-verified government layer (xgov.json: activity from human commits, practice signals, Pages, tags),
  (3) git probes for recently pushed repos the government layer had not read (probe/),
  (4) the public-body mapping (uk-public-sector-code-by-org org-mapping.csv, MIT) and body types from the v1 workbook.
Writes catalogue.json and catalogue_checks.txt. Downloaded files are parsed as data only."""
import json, os, re, sys, csv, collections, datetime as dt
S = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(S)
sys.path.insert(0, os.path.join(ROOT, "xgov")); sys.path.insert(0, os.path.join(ROOT, "inv"))
from taxonomy import tag, sector
from analyse import is_bot
CHECKS = []
def check(ok, cid, msg, guards):
    CHECKS.append(f"{'PASS' if ok else 'FAIL'} {cid} {msg}   [guards: {guards}]"); print(CHECKS[-1])
REF = dt.datetime(2026, 10, 7, 12, tzinfo=dt.timezone.utc); REFE = int(REF.timestamp())
cut = lambda d: REFE - d * 86400
ep = lambda s: int(dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()) if s else None

RJ = json.load(open(os.path.join(ROOT, "xrepos", "repos.json")))
XG = json.load(open(os.path.join(ROOT, "xgov", "xgov.json")))
V1 = json.load(open(os.path.join(ROOT, "v1", "v1_layer.json")))
MAP = list(csv.DictReader(open(os.path.join(ROOT, "pscbo", "src", "public", "data", "org-mapping.csv"))))

# ---- de-duplicate the scraper rows (it lists some repositories twice) ----
seen, R = set(), []
for r in RJ:
    if not isinstance(r, dict) or not isinstance(r.get("owner"), str) or not isinstance(r.get("name"), str): continue
    k = (r["owner"].lower(), r["name"].lower())
    if k in seen: continue
    seen.add(k); R.append(r)
dups = len(RJ) - len(R)
check(len(R) > 20000, "C-CAT-01", f"scraper rows read: {len(RJ)}, unique repositories {len(R)} ({dups} duplicate rows dropped)", "a truncated or failed download treated as the estate")

# ---- organisations: government layer orgs, plus accounts only the scraper lists ----
orgs = [dict(o) for o in XG["orgs"]]; oidx = {o["org"].lower(): i for i, o in enumerate(orgs)}
for r in R:
    o = r["owner"]
    if o.lower() not in oidx:
        oidx[o.lower()] = len(orgs)
        orgs.append(dict(org=o, section="", sector=sector(o, "U.K. Central"), source="X-Gov repo scraper only", total_on_github=None, deleted=False, listed=0, verified=0, missing=0,
                         active90=0, active365=0, bots_only=0, commits12=0, authors12=0, new12=0, pages=0, archived=0, master=0, main=0))

# ---- public bodies (publisher) ----
norm = lambda s: re.sub(r"[^a-z0-9]+", "-", re.sub(r"\s*\([^)]*\)", "", (s or "").lower().replace("&", "and"))).strip("-")
V1B = {norm(b["name"]): b for b in V1["bodies"]}
bodies, acc_body = {}, {}
for m in MAP:
    key = m["site_slug"] or m["govuk_slug"]
    if not key: continue
    b = V1B.get(norm(key.replace("-", " "))) or V1B.get(norm(m["govuk_slug"].replace("-", " ")))
    name = b["name"] if b else key.replace("-", " ").title().replace(" And ", " and ").replace(" Of ", " of ").replace(" For ", " for ").replace(" The ", " the ")
    btype = b["type"] if b else {"english_council": "English council", "gov_uk": "Central government body", "other": "Other public body"}.get(m["org_type"], "Other")
    bodies.setdefault(key, dict(slug=key, name=name, type=btype, kind=m["org_type"], wikidata=m["wikidata_id"], url=m["site_url"], accounts=[]))
    bodies[key]["accounts"].append(m["github_account"]); acc_body[m["github_account"].lower()] = key
BL = sorted(bodies); bidx = {k: i for i, k in enumerate(BL)}
for o in orgs: o["body"] = bidx.get(acc_body.get(o["org"].lower()), -1)
mapped = sum(1 for o in orgs if o["body"] >= 0)
check(mapped >= 0.8 * len([o for o in orgs if not o["deleted"]]), "C-CAT-02", f"{mapped} of {len(orgs)} GitHub accounts mapped to {len(bodies)} public bodies", "publishers left unattributed")

# ---- government-layer rows and scraper rows joined ----
XBY = {(r["o"].lower(), r["n"].lower()): r for r in XG["rows"]}
LIC = {"MIT": "M", "OGL-UK-3.0": "O", "Apache-2.0": "A", "GPL-2.0": "G", "GPL-3.0": "G", "LGPL-2.1": "G", "LGPL-3.0": "G", "AGPL-3.0": "G", "MPL-2.0": "P", "Unlicense": "U", "BSD-2-Clause": "B", "BSD-3-Clause": "B", "CC0-1.0": "C", "CC-BY-4.0": "C", "CC-BY-SA-4.0": "C"}
def lic_code(l):
    if not isinstance(l, dict): return "-"
    sp = l.get("spdxId") or ""
    if sp in LIC: return LIC[sp]
    if "OGL" in sp or "open government" in (l.get("name") or "").lower(): return "O"
    return "X"
def probe_status(o, n, archived, pushed):
    p = os.path.join(S, "probe", f"{o}__{n}.txt")
    if not os.path.exists(p): return None
    L = open(p, errors="replace").read().splitlines(); h = (L[0].split("|") if L else ["?"])
    if h[0] != "ok": return dict(st="Unverified", basis="git probe failed")
    com = [q for q in (l.split("|", 2) for l in L[1:]) if len(q) == 3 and q[0].isdigit() and int(q[0]) >= cut(365)]
    hum = [q for q in com if not is_bot(q[1], q[2])]
    lh = max((int(q[0]) for q in hum), default=None); last = int(h[2]) if len(h) > 2 and h[2].isdigit() else None
    st = "Archived" if archived else "Active" if lh and lh >= cut(90) else "Maintained" if lh else "Automated only" if com else "Dormant" if last and last >= cut(730) else "Inactive"
    return dict(st=st, basis="git (probed 8 October 2026)", lh=lh, c12=len(hum), c90=sum(1 for q in hum if int(q[0]) >= cut(90)), a12=len({q[2].strip().lower() for q in hum}))
EXTRA, CAT = {}, []
probed = 0
for r in R:
    k = (r["owner"].lower(), r["name"].lower()); pushed, created = ep(r.get("pushedAt")), ep(r.get("createdAt"))
    lc = lic_code(r.get("license"))
    if k in XBY:
        EXTRA[k] = [r.get("stargazersCount") or 0, r.get("forksCount") or 0, lc, created or 0, r.get("openIssuesCount") or 0, pushed or 0]
        continue
    desc = re.sub(r"\s+", " ", r.get("description") or "")[:160]
    pr = probe_status(r["owner"], r["name"], r.get("archived"), pushed)
    if pr: probed += 1
    if pr: st, basis = pr["st"], pr["basis"]
    elif r.get("archived"): st, basis = "Archived", "listing"
    elif not pushed: st, basis = "Unverified", "listing (no push date)"
    elif pushed < cut(730): st, basis = "Inactive", "listing: last push more than 2 years ago"
    elif pushed < cut(365): st, basis = "Dormant", "listing: last push 1 to 2 years ago"
    else: st, basis = "Recently pushed", "listing: pushed in the last 12 months, not checked with git"
    o = orgs[oidx[r["owner"].lower()]]
    tags, stds, dam = tag(r["name"], desc, "", "", o["sector"])
    CAT.append([oidx[r["owner"].lower()], r["name"], desc, r.get("language") or "", lc, r.get("stargazersCount") or 0, r.get("forksCount") or 0, 1 if r.get("archived") else 0,
                pushed or 0, created or 0, st, ",".join(sorted(tags)), ";".join(f"{a}:{b}" for a, b in sorted(tags.items())), "|".join(stds), dam or "", (pr or {}).get("lh") or 0, (pr or {}).get("c90", 0), (pr or {}).get("c12", 0), basis])
CF = ["oi", "n", "d", "l", "li", "sg", "fk", "ar", "pd", "cr", "st", "g", "ge", "s", "dam", "lh", "c90", "c12", "basis"]
XEF = ["sg", "fk", "li", "cr", "oiss", "pd"]
gov_only = [k for k in XBY if k not in seen]
check(len(EXTRA) + len(CAT) == len(R), "C-CAT-03", f"every unique scraper repository is in the catalogue once: {len(EXTRA)} joined to git-verified rows, {len(CAT)} catalogue-only", "rows lost or double-counted in the join")
njobs = len([l for l in open(os.path.join(S, "jobs.txt")).read().split("\n") if l.strip()])
check(njobs > 0 and probed >= 0.95 * njobs, "C-CAT-04", f"{probed} of {njobs} recently pushed repositories outside the government layer were checked with git", "recent activity claimed without verification")
co = [c for c in CAT if orgs[c[0]]["org"] == "co-cddo"]; coj = [k for k in EXTRA if k[0] == "co-cddo"]
check(not co and len(coj) == 146, "C-CAT-05", f"all 146 co-cddo repositories join to the inventory (scraper lists {len(coj)})", "the two sources disagreeing on co-cddo")
check(all(c[10] in ("Archived", "Inactive", "Dormant", "Recently pushed", "Unverified", "Active", "Maintained", "Automated only") for c in CAT) and all(c[1] and orgs[c[0]]["org"] for c in CAT), "C-CAT-06", "every catalogue record has an identifier, publisher account and a status with its basis", "records missing mandatory fields")
neg = [c for c in CAT if c[10] in ("Active", "Maintained") and "git" not in c[18]]
check(not neg, "C-CAT-07", "no catalogue-only record is called Active or Maintained without git evidence", "push dates (which include bots) presented as human activity")
OUT = dict(source=dict(scraper="https://www.uk-x-gov-software-community.org.uk/xgov-opensource-repo-scraper/repos.json", scraper_read="2026-10-08", scraper_rows=len(RJ), scraper_unique=len(R),
                       bodies="https://github.com/chrishylanduk/uk-public-sector-code-by-org (public/data/org-mapping.csv, MIT, commit 03cb8b1, 19 September 2026)"),
           orgs=orgs, bodies=[bodies[k] for k in BL], cf=CF, cat=CAT, xef=XEF, extra={f"{k[0]}/{k[1]}": v for k, v in EXTRA.items()}, gov_only=len(gov_only))
json.dump(OUT, open(os.path.join(S, "catalogue.json"), "w"), ensure_ascii=False, separators=(",", ":"))
open(os.path.join(S, "catalogue_checks.txt"), "w").write("\n".join(CHECKS) + "\n")
print(collections.Counter(c[10] for c in CAT), "gov-layer rows not in scraper:", len(gov_only))
sys.exit(1 if any(c.startswith("FAIL") for c in CHECKS) else 0)
