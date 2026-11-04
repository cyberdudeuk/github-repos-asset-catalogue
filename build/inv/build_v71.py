"""Assemble the GitHub Repos Asset Catalogue (v5; evolved from explorer v4): co-cddo inventory (+GDS Way, tags, standards, Pages, related work) + cross-government layer
(+practice signals, organisation totals, precision) + migration guidance with sourced quotes + spotlight with disclosed score
+ artefact pack, requirements, defects, releases and a check registry with traceability. Injects into explorer71.tpl.html.
v5 adds: the v1 migration workbook as a provenance layer (reconciliation, scoring model, evidence, actions, assurance controls),
the X-Gov repo scraper estate (every public repository of every listed account) and public-body publishers."""
import json, os, re, sys, io, collections, datetime as dt
S = os.path.dirname(os.path.abspath(__file__)); X = os.path.join(os.path.dirname(S), "xgov")
sys.path.insert(0, X); sys.path.insert(0, S)
from refdate import REF_DATE, REF_EPOCH
from listing import REPO_COUNT
from taxonomy import tag, STANDARDS, STRATEGY
from docs71 import pack, REQUIREMENTS, DEFECTS, RELEASES
VERSION = "7.15.0"; DOCID = f"GHRAC-{VERSION}-{REF_DATE:%Y%m%d}"; URL = os.environ.get("GHRAC_URL", "https://github.com/cyberdudeuk/github-repos-asset-catalogue")
ISSUES_URL = os.environ.get("GHRAC_ISSUES_URL", URL.rstrip("/") + "/issues")
CONTACT_URL = os.environ.get("GHRAC_CONTACT_URL", ISSUES_URL.rstrip("/") + "/new?template=contact.yml")   # R69: the only contact route is a form; no email address is ever published. Set GHRAC_CONTACT_URL to the team's private contact form when it exists
assert "@" not in CONTACT_URL and not CONTACT_URL.lower().startswith("mailto:"), "C-SAN-01 (R69): the contact route must be a form, never an email address"
# Links to the other govukOS apps are deployment settings, never committed: GHRAC_OS_LINKS names a JSON file
# {"urls": {"gti": ..., "liah": ..., "ana": ..., "mog": ..., "measr": ..., "cat": ...}, "crosswalk": {"ana": ..., "liah": ..., "measr": ...}}
OS_LINKS = json.load(open(os.environ["GHRAC_OS_LINKS"])) if os.environ.get("GHRAC_OS_LINKS") else {"urls": {}, "crosswalk": {}}
FAILS = []
_utc = lambda s: (lambda d: d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc))(dt.datetime.fromisoformat(s))   # dates without a zone are UTC, so builds match in every time zone (V711-5)
def need(ok, cid, msg):
    print(("PASS " if ok else "FAIL ") + cid + " " + msg)
    if not ok: FAILS.append(cid)

IN = __import__("runpy").run_path(os.path.join(os.path.dirname(S), "internal.py"))   # internal-only inputs (ADR 0004)
if not IN["available"](): sys.exit("Set GHRAC_INTERNAL to a checkout of cyberdudeuk/github-repos-asset-catalogue-internal: the build needs its internal-only inputs (ADR 0004).")
base = json.load(open(IN["ipath"]("build/inv/data.json")))
gw = json.load(open(os.path.join(S, "gdsway.json")))
xg = json.load(open(os.path.join(X, "xgov.json")))
prec = json.load(open(os.path.join(X, "precision.json"))) if os.path.exists(os.path.join(X, "precision.json")) else {}
tests = json.load(open(os.path.join(S, "test_results71.json"))) if os.path.exists(os.path.join(S, "test_results71.json")) else {}
xrows = xg["rows"]; xby = {(r["o"], r["n"]): r for r in xrows}
CATD = os.path.join(os.path.dirname(S), "catalogue"); V1D = os.path.join(os.path.dirname(S), "v1")
cat = json.load(open(os.path.join(CATD, "catalogue.json"))); v1 = json.load(open(IN["ipath"]("build/v1/v1_layer.json")))
stdr = json.load(open(os.path.join(CATD, "std_results.json")))
def trim(ev): return [e[:220] for e in ev[:3]]
STD = dict(levels=stdr["levels"], vendor=stdr["vendor"], pclass=stdr["pclass"], note=stdr["note"], fetched=stdr["fetched"],
           repos={k: dict(s={st: [x["level"], trim(x["evidence"])] for st, x in v["standards"].items()}, p={pl: [x["level"], trim(x["evidence"])] for pl, x in v["platforms"].items()},
                          f=[[f["path"][:160], f["kind"], f.get("records", 0)] for f in v.get("files", [])[:6]]) for k, v in stdr["repos"].items()},
           pub=stdr["publishing"], orgs=stdr["orgs"])
XREF_EPOCH = int(dt.datetime(2026, 10, 7, tzinfo=dt.timezone.utc).timestamp())

# ---------------- co-cddo rows ----------------
STDRX = [(n, re.compile(rx, re.I)) for n, rx in STANDARDS]
rows = base["rows"]
PUBLIC = os.environ.get("GHRAC_PUBLIC") == "1"
if PUBLIC:   # public repository build: no personal names (contributor names, CODEOWNERS entries, v1 owners)
    for r in rows:
        r["top_contributors_12m"] = ""; r["top_contributors_all"] = ""
        if r.get("codeowners"): r["codeowners"] = "(named in the repository's CODEOWNERS file)"
    for coll in (v1.get("repos"), v1.get("unlisted")):
        for e in (coll.values() if isinstance(coll, dict) else coll or []):
            if isinstance(e, dict) and e.get("owner"): e["owner"] = "(named in the v1 workbook; withheld in the public build)"
need(len(rows) == REPO_COUNT, "C-V4-01", f"page rows equal GitHub's count ({len(rows)})")
for r in rows:
    n = r["repo"]
    for k in ("domain", "theme", "capability", "destination", "kind"):   # GOV.UK style in display text (D19)
        r[k] = re.sub(r"^Leave archived", "Already archived", (r[k] or "").replace(" & ", " and "))
    tags, stds, dam = tag(n, r["description"], r["topics"], r["readme_summary"], "UK central government and ALBs")
    content_std = collections.Counter()
    for root, dirs, fs in os.walk(os.path.join(S, "shallow", n)):
        dirs[:] = [x for x in dirs if x not in (".git", "node_modules", "vendor")]
        for f in fs:
            if not f.lower().endswith((".md", ".yml", ".yaml", ".json", ".ttl", ".jsonld", ".rdf", ".csv", ".py", ".ts", ".js", ".rb", ".tf", ".html", ".txt")): continue
            p = os.path.join(root, f)
            try:
                if os.path.getsize(p) > 400_000: continue
                t = open(p, errors="ignore").read()
            except Exception: continue
            for name, rx in STDRX:
                if rx.search(t): content_std[name] += 1
    x = xby.get(("co-cddo", n), {})
    r.update(tags=tags, standards=sorted(set(stds) | set(content_std)), std_files=dict(content_std), dam=dam,
             dam_basis=("matched “" + dam + "”") if dam else ("open metadata standards found in files" if any(k in content_std for k in ("DCAT", "CSVW", "SKOS", "Dublin Core", "DQV")) else ""),
             gdsway=gw["results"][n], pages=bool(x.get("pg")), pages_url=x.get("pu", ""), pages_custom=x.get("cd", ""),
             branch=r.get("default_branch", ""), related_xgov=xg["links"].get(n, []),
             first_epoch=None)
    if r["dam_basis"] and not r["dam"]: r["dam"] = "standards"
need({r["repo"] for r in rows if r["pages"]} == {x["n"] for x in xrows if x["o"] == "co-cddo" and x["pg"]}, "C-V4-02", "co-cddo Pages flags agree between layers")

# ---------------- v5: v1 workbook layer, destination organisation and assurance controls per co-cddo repository ----------------
V1R = v1["repos"]
CYBER_FAM = {"sbd", "gc3", "email-sec", "domains"}
def dest_org(r, e):
    g = r["destination_group"]
    if g[0] in "678": return {"6": "stays archived in co-cddo", "7": "archive in co-cddo", "8": "delete"}[g[0]]
    if g[0] == "5": return "consolidate"
    t = (r["destination"] or "").lower()
    cyber = r["family"] in CYBER_FAM or "uk-gov-cyber" in (e.get("target_org") or "")
    base = "alphagov" if "alphagov" in t and "gds-dtx" not in t else "alphagov or gds-dtx" if "alphagov" in t else "gds-dtx"
    if cyber: return "uk-gov-cyber" if base == "gds-dtx" else "uk-gov-cyber or " + base
    return base
def agree(ours, theirs):
    if theirs in ("unknown", None, ""): return "v1 has no target"
    o = set(re.findall(r"uk-gov-cyber|alphagov|gds-dtx|archive|delete|consolidate", ours.replace("stays archived", "archive")))
    t = set(re.findall(r"uk-gov-cyber|alphagov|gds-dtx|archive", theirs))
    if o & t: return "Agree" if o == t else "Partly agree"
    return "Differ"
C = {c["Control domain"]: c for c in v1["controls"]}
def controls(r, e):
    col, g = e.get("collected", {}), r["gdsway"]; arch = r["archived"]
    yes = lambda k: str(col.get(k, "")).lower().startswith("y")
    out = []
    c6 = (e.get("v1_criteria") or {}).get("C6")
    out.append(("Classification & disclosure", "fail" if c6 == 0 and e.get("v1_criteria") else "pass" if c6 == 3 else "review" if c6 == 2 else "unknown", f"v1 classification score {c6}" if e.get("v1_criteria") else "not assessed in v1"))
    own = e.get("owner"); out.append(("Accountable ownership", "pass" if own and yes("Owner in post (Y/N)") else "review" if own or r["codeowners"] else "fail", "; ".join(x for x in [f"v1 owner: {own}" if own else "", f"CODEOWNERS: {r['codeowners']}" if r["codeowners"] else ""] if x) or "no owner evidenced"))
    adm = col.get("Admins (2 or more?)"); out.append(("Administrative resilience", ("pass" if yes("Admins (2 or more?)") else "fail") if adm else "unknown", f"v1: {adm}" if adm else "needs the organisation export"))
    out.append(("CODEOWNERS", "n/a" if arch else "pass" if r["codeowners"] else "fail", r["codeowners"] or "no CODEOWNERS file"))
    rd, sec = g["readme"][0], g["security"][0]
    out.append(("README & support route", "fail" if rd == "fail" else "pass" if sec == "pass" else "review", f"README {rd}; security contact {sec}"))
    out.append(("Licence & Crown copyright", "pass" if g["licence"][0] == "pass" else "fail", g["licence"][1]))
    al = col.get("Open security alerts (high)"); out.append(("Security alerts", ("fail" if str(al).lower().startswith("yes") else "pass") if al else "unknown", f"v1: {al}" if al else "alerts are not visible in public data"))
    wf = col.get("Last workflow run"); out.append(("CI and build health", "n/a" if not r["workflows"] and not wf else ("fail" if wf and "fail" in str(wf).lower() else "unknown"), f"v1: last run {wf}" if wf else f"{r['workflows']} workflow(s); run results are not read"))
    out.append(("Secrets & integrations", "review" if r["ref_oidc"] else ("unknown" if not col.get("Actions secrets / variables") else "review"), "OIDC trust found in code" if r["ref_oidc"] else (f"v1: {col.get('Actions secrets / variables')}" if col.get("Actions secrets / variables") else "secret and webhook names need the organisation export")))
    bp = col.get("Branch protection"); out.append(("Branch protection", ("pass" if yes("Branch protection") else "fail") if bp else "unknown", f"v1: {bp}" if bp else "not readable from public data"))
    out.append(("Pages, domains & redirects", "review" if (r["pages"] or r["cname"] or r["ref_pages"]) else "pass", "; ".join(x for x in [f"live site {r['pages_url']}" if r["pages"] else "", f"CNAME {r['cname']}" if r["cname"] else "", f"{r['ref_pages']} github.io references" if r["ref_pages"] else ""] if x) or "no site or address references"))
    out.append(("Activity & consumers", "pass", f"{r['status']}; {r['human_commits_365d']} commits by people in 12 months; depended on by {r['inbound_code_refs']}"))
    out.append(("Archive & replacement", g["archive_readme"][0] if arch and g["archive_readme"][0] in ("pass", "fail") else "n/a" if not arch else "review", g["archive_readme"][1] if arch else "not archived"))
    out.append(("Mirrors & package registries", "review" if (r["ref_pkg"] or r["ref_uses"] or r["inbound_code_refs"]) else "pass", f"{r['ref_pkg']} package refs, {r['ref_uses']} workflow refs, {r['inbound_code_refs']} dependants" if (r["ref_pkg"] or r["ref_uses"] or r["inbound_code_refs"]) else "no package, workflow or dependant references found"))
    return [[k, s, ev] for k, s, ev in out]
for r in rows:
    e = V1R.get(r["repo"], {})
    r["dest_org"] = dest_org(r, e)
    r["v1"] = dict({k: e.get(k) for k in ("v1_name", "renamed", "owning_unit", "owner", "capability", "domain", "theme", "target", "target_org", "rationale", "evidence_ids", "confidence", "notes", "activity_evidence", "catalogue_depth", "collected", "v1_criteria", "v1_score", "v1_outcome", "v1_score_conf", "duplicate_row", "obs_criteria", "obs_score", "obs_outcome", "obs_basis", "unknown")}, agreement=agree(r["dest_org"], e.get("target_org")))
    r["controls"] = controls(r, e)
need(all(len(r["controls"]) == len(v1["controls"]) and [c[0] for c in r["controls"]] == [c["Control domain"] for c in v1["controls"]] for r in rows), "C-V5-03", f"every co-cddo repository has a result for each of v1's {len(v1['controls'])} assurance controls, in v1's order")
need(all(r["v1"]["obs_score"] is not None for r in rows), "C-V5-04", "every co-cddo repository carries v1-model scores re-run with observed evidence")
cy = [r["repo"] for r in rows if "uk-gov-cyber" in r["dest_org"]]
need(len(cy) > 0 and all(r["family"] in CYBER_FAM or "uk-gov-cyber" in (r["v1"]["target_org"] or "") for r in rows if r["repo"] in cy), "C-V5-05", f"{len(cy)} security repositories are offered uk-gov-cyber, the other organisation named in co-cddo's deprecation notice (V5-1)")
UNLISTED = v1["unlisted"]

# ---------------- cross-government compact rows ----------------
orgs = cat["orgs"]; oidx = {o["org"]: i for i, o in enumerate(orgs)}
need([o["org"] for o in orgs[:len(xg["orgs"])]] == [o["org"] for o in xg["orgs"]], "C-V5-01", "catalogue organisations extend the government layer without reordering it")
LIC = {"MIT": "M", "OGL": "O", "Apache-2.0": "A", "GPL/LGPL": "G", "AGPL": "G", "MPL-2.0": "P", "Unlicense": "U", "BSD": "B", "CC": "C", "other": "X", "none": "-"}
# ---------------- 7.9: crown dependencies and overseas territories, verified directly against GitHub over git (R56) ----------------
_CD = os.path.join(os.path.dirname(S), "dama", "cdot.json"); CDOT = json.load(open(_CD)) if os.path.exists(_CD) else None
if CDOT:
    ep = lambda s: int(_utc(s).timestamp()) if s else 0
    CDOT_IN = [a for a in CDOT["accounts"] if a.get("in_catalogue")]
    for a in CDOT_IN:
        bi = len(cat["bodies"]); cat["bodies"].append(dict(slug=a["body"].lower().replace(" ", "-"), name=a["body"], type=a["kind"] + " government", kind="cdot", wikidata="", url="", accounts=[a["account"]]))
        live = [r for r in a["repos"] if r.get("status") in ("Active", "Maintained")]
        orgs.append(dict(org=a["account"], section=a["kind"], sector="Crown dependencies" if a["kind"] == "Crown dependency" else "Overseas territories", source="GitHub's list of official government accounts; repositories verified directly over git", total_on_github=len(a["repos"]), deleted=False, listed=0,   # listed counts government-layer rows only; these are catalogue records
                        
                         verified=sum(1 for r in a["repos"] if r.get("exists")), missing=0, active90=sum(1 for r in a["repos"] if r.get("c90")), active365=sum(1 for r in a["repos"] if r.get("c12")), bots_only=0,
                         commits12=sum(r.get("c12", 0) for r in a["repos"]), authors12=0, new12=0, pages=0, archived=0, master=0, main=0, body=bi))
        oi = len(orgs) - 1
        for r in a["repos"]:
            row = {"oi": oi, "n": r["name"], "d": r.get("description", ""), "l": r.get("language", ""), "li": LIC.get(r.get("licence", "none"), "X"), "sg": None, "fk": None, "ar": 0, "pd": ep(r.get("last")), "cr": ep(r.get("first")),
                   "st": r.get("status", "Unverified"), "g": "", "ge": "", "s": "", "dam": "", "lh": ep(r.get("last_human")), "c90": r.get("c90", 0), "c12": r.get("c12", 0), "basis": "git, verified directly" + (" (a fork)" if r.get("fork") else "")}
            cat["cat"].append([row.get(k, "") for k in cat["cf"]])
    need(all(o["org"] in {a["account"] for a in CDOT_IN} for o in orgs[len(orgs) - len(CDOT_IN):]) and len(CDOT_IN) >= 1, "C-CDOT-02", f"{len(CDOT_IN)} official crown dependency accounts and {sum(len(a['repos']) for a in CDOT_IN)} repositories added to the catalogue; probable and unconfirmed accounts are listed but not added")
# New public repositories found by the check against GitHub (7.11, R57): added as catalogue records, with GitHub's own
# description, language and licence; status from GitHub's last-updated date. Crown dependency accounts are already added above.
_GV = os.path.join(os.path.dirname(S), "dama", "ghverify.json"); _NR = os.path.join(os.path.dirname(S), "dama", "new_repos.json")
_RW = os.path.join(os.path.dirname(S), "dama", "gh_crawl_rows.json")
NEW_ADDED, NEW_MSG = 0, "public repositories new on GitHub since the catalogue was built are added to it, with GitHub's own description, language and licence; repositories GitHub no longer lists are kept, marked 'no longer public' and left out of live counts"
if os.path.exists(_GV) and os.path.exists(_NR):
    _gv = json.load(open(_GV)); _nr = json.load(open(_NR))["repos"]; _rw = json.load(open(_RW))
    _oi = {o["org"]: i for i, o in enumerate(orgs)}; _cd = {a["account"] for a in (CDOT["accounts"] if CDOT else []) if a.get("in_catalogue")}
    _ghlic = lambda t: "M" if "MIT" in t else "A" if "Apache" in t else "G" if "General Public" in t else "P" if "Mozilla" in t else "B" if "BSD" in t else "U" if "Unlicense" in t else "C" if "Creative Commons" in t else "O" if "Open Government" in t else "-" if not t else "X"
    for _a in _gv["accounts"]:
        if _a["account"] in _cd or _a["account"] not in _oi: continue
        _rows = {r[0]: r for r in _rw.get(_a["account"], {}).get("r", [])}
        for _n in _a["added"]:
            _x = _nr.get(_a["account"] + "/" + _n, {}); _r = _rows.get(_n)
            _upd = _r[6] if _r else ""; _days = (dt.date(2026, 11, 1) - dt.date.fromisoformat(_upd)).days if _upd else 9999
            _st = "Archived" if _x.get("archived") or (_r and _r[1]) else "Recently pushed" if _days <= 365 else "Unverified"   # GitHub's date only: no git evidence of who changed it (P-18)
            row = {"oi": _oi[_a["account"]], "n": _n, "d": _x.get("d", ""), "l": _x.get("l") or (_r[7] if _r else ""), "li": _ghlic(_x.get("li") or (_r[5] if _r else "")), "sg": _r[8] if _r else None, "fk": None,
                   "ar": 1 if _st == "Archived" else 0, "pd": int(_utc(_upd).timestamp()) if _upd else 0, "cr": 0, "st": _st, "g": "", "ge": "", "s": "", "dam": "", "lh": 0, "c90": 0, "c12": 0,
                   "basis": "GitHub, new since the catalogue was built (found 1 November 2026)" + (" (a fork)" if _r and _r[2] else "")}
            cat["cat"].append([row.get(k, "") for k in cat["cf"]]); NEW_ADDED += 1
    need(NEW_ADDED >= 250, "C-GHV-04", f"{NEW_ADDED} {NEW_MSG}")
XR = []
for r in xrows:
    e = r.get("e") or {}
    h = [LIC.get(e.get("licence", "none"), "X"), int(e.get("codeowners", 0)), int(e.get("dependabot", 0)), int(e.get("security", 0)), e.get("workflows", 0), e.get("third", 0), e.get("unpinned", 0), e.get("noperm", 0), e.get("wf_read", 0), int(e.get("readme", 0)), int(e.get("contributing", 0))] if e else 0
    XR.append([oidx[r["o"]], r["n"], (r["d"] or "")[:180], (r["ld"] or "")[:220] if (r["ld"] or "") != (r["d"] or "") else "", r["l"], r["t"], r["st"], r["lh"] or 0, r["lc"] or 0,
               r["c12"], r["c90"], r["a12"], r["b"], ",".join(sorted(r["g"])), ";".join(f"{k}:{v}" for k, v in sorted(r["g"].items())), "|".join(r["s"]), r["dam"] or "",
               1 if r["pg"] else 0, r["pu"], r["cd"], 1 if r["new"] else 0, r["fc"] or 0, h, 1 if r["a"] else 0] + (cat["extra"].get(f'{r["o"].lower()}/{r["n"].lower()}') or [0, 0, "", 0, 0, 0]))
XF = ["oi", "n", "d", "ld", "l", "t", "st", "lh", "lc", "c12", "c90", "a12", "b", "g", "ge", "s", "dam", "pg", "pu", "cd", "nw", "fc", "h", "ar"] + cat["xef"]
need(not (set(cat["xef"]) & set(XF[:24])), "C-V5-02", "catalogue field names do not collide with government-layer field names")

# ---------------- spotlight (disclosed score) ----------------
REL = {"DF1", "DF2", "DF3", "DF4", "DF5", "DF6", "FF"}
EXCL = re.compile(r"(backup|(^|[-_])tests?($|[-_])|sandbox|playground|demo|poc|template|archive)", re.I)
def precise(t): return prec.get(t, {}).get("precision", 1.0) >= 0.7
cands = []
for r in xrows:
    if r["st"] != "Active" or r["a"] or r["o"] == "co-cddo" or EXCL.search(r["n"]): continue
    rel = {t for t in r["g"] if t in REL and precise(t)}
    damok = bool(r["dam"]) and precise("DAM")
    if not rel and not damok: continue
    parts = dict(new=3 if r["new"] else 0, dam=2 if damok else 0, tags=len(rel), activity=round(min(r["c90"], 30) / 15, 2), pages=0.5 if r["pg"] else 0)
    cands.append((sum(parts.values()), r, parts, rel, damok))
cands.sort(key=lambda c: (-c[0], -(c[1]["lh"] or 0)))
spot, per_org = [], collections.Counter()
for sc, r, parts, rel, damok in cands:
    if per_org[r["o"]] >= 2: continue
    per_org[r["o"]] += 1
    why = []
    if r["new"]: why.append("first commit in the last 12 months (" + dt.datetime.fromtimestamp(r["fc"], dt.timezone.utc).strftime("%-d %B %Y") + ")")
    if damok: why.append(f"DAM and metadata (matched “{r['dam']}”)")
    for k in sorted(rel): why.append(f"{k} (matched “{r['g'][k]}”)")
    why.append(f"{r['c90']} commits by people in the last 90 days")
    spot.append(dict(o=r["o"], n=r["n"], d=r["d"] or r["ld"], ld=r["ld"], c90=r["c90"], lh=r["lh"], why=why, pg=r["pu"] if r["pg"] else "", tags=sorted(rel) + (["DAM"] if damok else []), score=round(sc, 2), parts=parts))
    if len(spot) == 12: break
need(all(xby[(s["o"], s["n"])]["c90"] > 0 for s in spot), "C-V4-03", "every spotlight repository has human commits in the last 90 days (D7/D11)")

# ---------------- engineering practice benchmark ----------------
def pct(a, b): return [a, b, round(100 * a / b) if b else None]
def bench(rs):
    E = [r["e"] for r in rs if r.get("e")]
    wf = [e for e in E if e.get("wf_read")]; th = [e for e in E if e.get("third")]
    return dict(n=len(E), readme=pct(sum(e["readme"] for e in E), len(E)), mitogl=pct(sum(e["licence"] in ("MIT", "OGL") for e in E), len(E)),
                anylic=pct(sum(e["licence"] != "none" for e in E), len(E)), codeowners=pct(sum(e["codeowners"] for e in E), len(E)),
                dependabot=pct(sum(e["dependabot"] for e in E), len(E)), security=pct(sum(e["security"] for e in E), len(E)),
                pinned=pct(sum(e["unpinned"] == 0 for e in th), len(th)), perms=pct(sum(e["noperm"] == 0 for e in wf), len(wf)))
live = [r for r in xrows if r["st"] in ("Active", "Maintained") and r["o"] != "co-cddo"]
BENCH = {"All government (active or maintained)": bench(live)}
for sec in sorted({o["sector"] for o in orgs}):
    BENCH[sec] = bench([r for r in live if orgs[oidx[r["o"]]]["sector"] == sec])
co_live = [r for r in rows if r["status"] in ("Active", "Maintained")]
g = lambda r, k: r["gdsway"][k][0]
th = [r for r in co_live if g(r, "pin_sha") in ("pass", "fail") and "no third-party" not in r["gdsway"]["pin_sha"][1]]
wf = [r for r in co_live if g(r, "permissions") in ("pass", "fail")]
BENCH_CO = dict(n=len(co_live), readme=pct(sum(g(r, "readme") == "pass" for r in co_live), len(co_live)), mitogl=pct(sum(g(r, "licence") == "pass" for r in co_live), len(co_live)),
                anylic=pct(sum(r["licence"] != "None found" for r in co_live), len(co_live)), codeowners=pct(sum(bool(r["codeowners"]) for r in co_live), len(co_live)),
                dependabot=pct(sum(g(r, "dependabot") == "pass" for r in co_live), len(co_live)), security=pct(sum(bool(r["has_security_md"]) for r in co_live), len(co_live)),
                pinned=pct(sum(g(r, "pin_sha") == "pass" for r in th), len(th)), perms=pct(sum(g(r, "permissions") == "pass" for r in wf), len(wf)))
need(BENCH["All government (active or maintained)"]["n"] > 0, "C-V4-04", f"practice benchmark computed over {BENCH['All government (active or maintained)']['n']} enriched repositories")

# ---------------- migration guidance (GitHub docs read 7–8 Oct 2026; quotes verbatim, short) ----------------
G = "https://docs.github.com/en/"
CHECKED = "8 October 2026"
PHASES = [
 ("Scope and plan", "Define scope, success criteria, stakeholders, a runbook, communications and how to revert.", G + "migrations/overview/planning-your-migration-to-github"),
 ("Inventory", "One row per repository: owner, activity, size, dependencies, permissions and integrations. Archive what isn't needed first.", G + "migrations/overview/planning-your-migration-to-github"),
 ("Choose the method", "Transfer keeps the same repository, with redirects, stars, secrets and deploy keys. GitHub Enterprise Importer copies into a new repository, supports trial runs, and leaves some data behind.", G + "migrations/using-github-enterprise-importer/migrating-between-github-products/about-migrations-between-github-products"),
 ("Trial run", "Rehearse moves in a sandbox organisation, check the result, then delete the trial.", G + "migrations/using-github-enterprise-importer/migrating-between-github-products/overview-of-a-migration-between-github-products"),
 ("Pilot", "Move a low-risk repository first, connect its integrations and collect feedback.", "https://wellarchitected.github.com/library/scenarios/migrations/repository-checklist"),
 ("Tell people", "Give notice and reminders. Tell users how to update remotes, workflow references, module sources and package scopes.", G + "migrations/overview/planning-your-migration-to-github"),
 ("Freeze and move", "Stop changes in the source during the move.", "https://wellarchitected.github.com/library/scenarios/migrations/repository-checklist"),
 ("Check", "Visibility, secrets, runners, environments, webhooks, apps, teams, CODEOWNERS, Pages and packages; run CI.", G + "migrations/using-github-enterprise-importer/migrating-between-github-products/overview-of-a-migration-between-github-products"),
 ("Close the old home", "Archive with a README that says why and links to the new home (GDS Way). Keep the co-cddo organisation.", "https://gds-way.digital.cabinet-office.gov.uk/standards/source-code/use-github.html"),
]
RISKS = [  # action, what breaks, can it be undone, source, check first, quote (verbatim, short), basis ('documented' or 'inference')
 ("Creating a repository or fork at an old co-cddo path after a transfer", "The redirect to the moved repository is deleted for good; clones, links and module sources then reach the new, unrelated repository.", "No", G + "repositories/creating-and-managing-repositories/transferring-a-repository", "Keep a list of vacated names; restrict repository creation in co-cddo.", "the redirects to the transferred repository will be permanently deleted", "documented"),
 ("Deleting or renaming the co-cddo organisation", "Deletion cannot be undone and frees the name after 90 days; a rename frees it at once. Whoever claims it can create repositories at old paths, capturing uses:, Terraform and git references.", "No", G + "organizations/managing-organization-settings/deleting-an-organization-account", "Keep co-cddo; archive it only after every move.", "the organization name will not be available to use for another organization or user account for 90 days", "documented"),
 ("Moving a repository that hosts a reusable workflow or action", "GitHub documents that calls to an action in a renamed repository are not redirected. It does not document redirects for reusable workflows after a transfer, so treat them as not redirected.", "Yes, by updating callers", G + "repositories/creating-and-managing-repositories/renaming-a-repository", "Search every organisation for uses: co-cddo/; update callers in the same window.", "GitHub will not redirect calls to an action hosted by a renamed repository", "documented for actions; inference for reusable workflows"),
 ("Moving a repository whose cloud deploys trust its OIDC subject", "Transfers after 15 July 2026 switch to immutable subject claims (owner and repository IDs). Trust conditions written for repo:co-cddo/… or repo:gds-dtx/… will not match, so deploys are refused.", "Yes, by updating trust", G + "actions/reference/security/oidc", "List roles and federated credentials naming co-cddo; update to the immutable format or repository_id claims; prove with a dry-run deploy.", "Repository renames and transfers after July 15, 2026 also move to the immutable subject format", "documented"),
 ("Transferring repositories that publish packages", "Packages may move or may lose their link to the repository, depending on the registry. An npm scope named after co-cddo cannot move.", "Partly", G + "packages/learn-github-packages/about-permissions-for-github-packages", "List packages and who installs them; plan republishing under the new scope.", "may be transferred, or may lose their link to the repository, depending on the registry", "documented"),
 ("Moving a repository that serves GitHub Pages", "co-cddo.github.io addresses are not redirected. A custom domain left pointing at a disabled site can be taken over.", "A takeover is hard to undo", G + "repositories/creating-and-managing-repositories/transferring-a-repository", "Set and verify a custom domain under gds-dtx before cutover, or tell users the new address; remove DNS records for retired sites.", "we don't redirect GitHub Pages associated with the repository", "documented"),
 ("Relying on organisation-level secrets, variables, runners or rulesets", "The transfer page says repository secrets stay with the repository. It says nothing about organisation-level ones; as they belong to co-cddo, expect them not to follow. Importer moves none.", "Yes", G + "repositories/creating-and-managing-repositories/transferring-a-repository", "List co-cddo's organisation secrets and variables and which repositories use them.", "secrets, or deploy keys, they will remain associated after the transfer", "documented for repository secrets; inference for organisation secrets"),
 ("Team permissions and CODEOWNERS", "The new organisation's default permissions apply. @co-cddo/ teams don't resolve in gds-dtx, so required reviews can lapse.", "Yes", G + "repositories/creating-and-managing-repositories/transferring-a-repository", "Recreate teams in gds-dtx and rewrite CODEOWNERS in the same change.", "the organization's default repository permission settings and default membership privileges will apply", "documented"),
 ("A heavily used repository name", "A name with a Marketplace action, or more than 100 clones or Actions uses in the week before transfer, is retired for good.", "No", G + "repositories/creating-and-managing-repositories/transferring-a-repository", "Check clone and Actions traffic before choosing names.", "GitHub permanently retires the owner name and repository name combination", "documented"),
 ("Using GitHub Enterprise Importer instead of transfer", "A new repository: stars, forks, rulesets, Git LFS, packages, alert states, webhook secrets and apps are left behind; activity is attributed to placeholder users until reclaimed.", "The source is untouched until archived", G + "migrations/using-github-enterprise-importer/migrating-between-github-products/about-migrations-between-github-products", "Trial-migrate and compare; reclaim placeholder users before any later transfer.", "Data that is not migrated", "documented"),
 ("Internal repositories across enterprises", "An internal repository cannot move to an organisation in another enterprise; changing visibility to force it exposes code.", "A visibility change can be undone, an exposure cannot", G + "enterprise-cloud@latest/repositories/creating-and-managing-repositories/transferring-a-repository", "Confirm both organisations' enterprise before planning internal repositories.", "Internal repositories can only be transferred to an organization in the enterprise", "documented"),
 ("Archiving the whole co-cddo organisation too early", "Every repository becomes read-only and none can be unarchived on its own.", "Yes, by unarchiving the organisation", G + "organizations/managing-organization-settings/archiving-an-organization", "Archive repositories one by one; archive the organisation last.", "individual repositories may not be unarchived independently", "documented"),
]
TRANSFER = [
 ("Git history, issues, pull requests, wiki", "Moves", "Moves (placeholder users until reclaimed)"), ("Stars, watchers, forks", "Moves", "Left behind"),
 ("Repository secrets, deploy keys, webhooks", "Stay with the repository", "Secrets left behind; webhooks arrive switched off"),
 ("Organisation secrets, variables, runners", "Not covered by the transfer page (they belong to the old organisation)", "Left behind"),
 ("GitHub Pages address", "Not redirected", "Settings only"), ("Packages", "May move or lose their link, by registry", "Left behind"),
 ("Teams and CODEOWNERS teams", "New organisation's defaults apply; teams must exist there", "Left behind"), ("Rulesets and branch protection", "Not stated", "Partly or not at all"),
 ("Alert states (Dependabot, code scanning)", "Not stated", "Left behind"), ("Web and git redirects", "Yes", "No (new repository)"),
]
for a, b, rev, u, chk, quote, basis in RISKS:
    p = {"transferring-a-repository": "transfer.md", "renaming-a-repository": "rename.md", "oidc": "oidc.md", "deleting-an-organization-account": "org_delete.md",
         "archiving-an-organization": "org_archive.md", "about-permissions-for-github-packages": "transfer.md", "about-migrations-between-github-products": "gei_about.md"}
    key = next((k for k in p if k in u), None)
    src = open(os.path.join(os.path.dirname(S), "gh", p[key]), errors="replace").read() if key else ""
    if "enterprise-cloud" in u: src = open(os.path.join(os.path.dirname(S), "gh", "ec_transfer.md"), errors="replace").read()
    need(quote in src, "C-V4-05", f"risk quote found verbatim in saved GitHub page: “{quote[:50]}…”")

# ---------------- glossary, needs, dictionary, method ----------------
NEEDS = [
 ["I own or maintain a co-cddo repo", "As a repository owner, I need to know where my repository is going and what will break, so I can move it without surprises.", "repos", "Find your repository"],
 ["I'm planning the migration", "As the migration lead, I need the order of moves, the risks and the decisions outstanding, so I can run waves safely.", "plan", "See the plan"],
 ["I use a co-cddo module, workflow or website", "As a consumer, I need to know which references to update and when, so my builds and links keep working.", "lineage", "Trace dependencies"],
 ["I need to check we follow the GDS Way", "As an engineering lead, I need to see which repositories miss MUST requirements before they move, so we fix them in the same change.", "gdsway", "Check conformance"],
 ["I work on Data Foundations or the DAM policy", "As a Government Data colleague, I need to find related work on metadata, catalogues and critical data assets across government, so I can connect and reuse.", "dam", "Explore DAM and metadata"],
 ["I want to see related work across government", "As a colleague in GDS or another department, I need to see who else is building similar things, so we avoid duplication.", "strategy", "See strategy alignment"],
 ["I need to find a public sector repository", "As anyone working on government technology, I need one searchable record per repository with its publisher, status and licence, so I can find, reuse or assure code.", "catalogue", "Search the catalogue"],
 ["I want to know who publishes what", "As a data or engineering lead, I need to see each public body's GitHub accounts and estate, so I can find owners and compare practice.", "publishers", "See publishers"],
 ["I need to assure a repository before it moves", "As a repository owner, I need each assurance control's result and evidence, so I know what to fix before transfer.", "controls", "Check assurance controls"],
 ["I used the earlier migration workbook", "As the workbook's author, I need to see how its names, scores and targets compare with GitHub's current listing, so I can retire it safely.", "reconcile", "See the reconciliation"],
 ["I have a question", "As anyone using this tool, I need to ask in plain English and get an answer grounded in this data.", "ask", "Ask a question"],
]
GLOSSARY = [
 ["Subject", "What a project is about, using GOV.UK's top-level topics such as Health and social care, Transport or Education. Found from the project's own words, or from who publishes it where its words say nothing.", "GOV.UK topic, subject area"],
 ["Theme", "A cross-cutting grouping: guidance and playbooks, public service journeys, the UK's nations and devolution, or international work.", "cross-cutting theme"],
 ["Technical debt", "Work a project will need later because of shortcuts or ageing parts, such as replacing retired libraries or tidying up code nobody looks after.", "debt, legacy"],
 ["Legacy technology", "Software or tools whose makers have stopped supporting them, such as AngularJS or the retired GOV.UK Template. It still works, but gets no security fixes.", "end of life, retired"],
 ["Legacy data", "Data held in an old system or format that has to be moved, cleaned or kept readable when the system is replaced.", "data migration"],
 ["Department family tree", "A department and every organisation underneath it, from GOV.UK's list of organisations, down to the GitHub accounts and GDS units where the code lives.", "hierarchy, sponsor"],
 ["GOV.UK organisation slug", "The short name GOV.UK gives each organisation in its web address, such as hm-revenue-customs. The govukOS apps can all join on it.", "organisation identifier"],
 ["Lineage and traceability", "Where each fact about a project came from and how it was worked out, shown as a picture and a trace table.", "provenance"],
 ["Reading level", "How much detail the repo profile shows: simple, standard or technical.", "—"],
 ["Active", "A person (not a bot) committed in the last 90 days.", "live, in use"], ["Maintained", "A person committed within 12 months, but not in the last 90 days.", "—"],
 ["Dormant", "No person committed for 1 to 2 years.", "stale"], ["Inactive", "No person committed for more than 2 years.", "dead"],
 ["Automated only", "Commits in the last 12 months, all by bots such as Dependabot.", "bot-only"],
 ["Archived", "Read-only on GitHub.", "retired"], ["Repository", "A project's code and history on GitHub.", "repo"], ["Organisation", "A GitHub account that owns repositories for a public body or team.", "org"],
 ["Transfer", "GitHub's feature for moving a repository to another owner. Keeps history, issues and web and git redirects.", "move"],
 ["GitHub Enterprise Importer (GEI)", "A GitHub tool that copies a repository into a new one. Some settings and data are left behind.", "importer, migration tool"],
 ["Reusable workflow", "A CI workflow in one repository that others call with a line starting uses:.", "shared workflow, uses: reference"],
 ["OIDC trust", "Cloud permissions that let a named GitHub repository deploy without stored keys. The name is part of the trust rule.", "OpenID Connect, federated credential, role trust"],
 ["CNAME", "A file or DNS record that points a custom web address at a GitHub Pages site.", "custom domain"],
 ["HEAD", "The latest commit on a repository's main branch.", "tip, latest"], ["GitHub Pages", "A website published from a repository at owner.github.io/repository or a custom domain.", "github.io site"],
 ["CODEOWNERS", "A file naming who must review changes to which files.", "code owners"], ["SBOM", "Software bill of materials: a list of the components software is built from.", "bill of materials"],
 ["DAM policy", "Data Asset Management policy: departments identify, record and report critical data assets.", "data asset management, critical data assets (formerly ESDA)"],
 ["Firmer foundations", "An outcome in the Roadmap for modern digital government: secure, trustworthy services, less legacy, better cyber resilience.", "fix the foundations"],
 ["Data Foundations", "The Government Data directorate's six outcomes, numbered 1 to 6 on this page (1 Strategic Data Roadmap … 6 Data Protection and Public Trust).", "DF1–DF6"],
 ["Observed / Calculated / Assessed / Auto-tagged / Auto-linked", "Where a fact comes from: measured, derived by formula, the author's judgement, matched by a declared rule, or linked by text similarity.", "provenance"],
 ["Precision", "Of the repositories a tag picked, the share a reviewer judged correct.", "accuracy of a tag"],
 ["Asset record", "One catalogue entry for one repository: identity, publisher, status with its basis, licence, activity, practice and tags.", "catalogue entry"],
 ["Publisher", "The public body that owns a GitHub account, from the UK Public Sector Code by Organisation mapping.", "public body, owner organisation"],
 ["Status basis", "How a status was decided: git (commits by people) or the listing's last push date. Push dates include bots, so they can only show a repository is Dormant or Inactive, never Active.", "evidence basis"],
 ["Recently pushed", "Pushed in the last 12 months according to the listing, but not checked with git.", "—"],
 ["Assurance control", "One of the 14 checks from the v1 workbook's migration assurance framework, applied to each co-cddo repository.", "migration control"],
 ["Standards level", "How far a repository applies a standard: 1 mentioned, 2 schema or profile in the code, 3 applied in data files, 4 every record in a data file carries it.", "adoption level"],
 ["Every record", "Every record in at least one parsed data file carries the standard: for DCAT, every DCAT resource has its core properties; for SKOS, every concept has a preferred label; for CSVW, every column maps to a property.", "record level"],
 ["v1 workbook", "co-cddo_GitHub_Migration_Inventory_v1.xlsx, the earlier migration inventory supplied on 8 October 2026.", "provisional inventory"],
]
FIELD_DOC = {  # field: (layer, meaning, provenance)
 "repo": ("co-cddo", "Repository name", "Observed"), "status": ("co-cddo", "Activity status from the last human commit", "Calculated"), "last_human_commit": ("co-cddo", "Date of last commit by a person", "Observed"),
 "human_commits_90d": ("co-cddo", "Commits by people, last 90 days, all branches", "Observed"), "human_commits_365d": ("co-cddo", "Commits by people, last 12 months, all branches", "Observed"),
 "authors_365d": ("co-cddo", "Distinct people committing in 12 months (upper bound)", "Observed"), "codeowners": ("co-cddo", "Owners named in CODEOWNERS", "Observed"),
 "licence": ("co-cddo", "Licence found in the repository", "Observed"), "destination_group": ("co-cddo", "Proposed destination group", "Assessed"), "rationale": ("co-cddo", "Why that destination", "Assessed"),
 "inferred_team": ("co-cddo", "Team that appears to own it", "Assessed"), "inbound_code_refs": ("co-cddo", "co-cddo repositories whose code references this one", "Observed"),
 "tags": ("both", "Strategy tags with the matched words", "Auto-tagged"), "dam": ("both", "DAM and metadata relevance and the matched words", "Auto-tagged"), "standards": ("both", "Open standards mentioned or evidenced by files", "Auto-tagged"),
 "gdsway": ("co-cddo", "Result and evidence for each GDS Way rule", "Observed"), "pages": ("both", "Live GitHub Pages site", "Observed"), "related_xgov": ("co-cddo", "Similar repositories across government", "Auto-tagged"),
 "spark": ("co-cddo", "Human commits per month, 24 months", "Observed"),
 "st": ("government", "Activity status from human commits on the default branch", "Calculated"), "c12": ("government", "Human commits, 12 months, default branch", "Observed"),
 "c90": ("government", "Human commits, 90 days, default branch", "Observed"), "lh": ("government", "Last human commit", "Observed"), "ld": ("government", "First paragraph of the README", "Observed"),
 "d": ("government", "Description from the summarised listing read", "Observed (summarised; lower confidence)"), "h": ("government", "Practice signals: licence, CODEOWNERS, Dependabot, SECURITY.md, workflows, pinning, permissions", "Observed"),
 "nw": ("government", "First commit within the last 12 months", "Observed"),
 "sg": ("government", "Stars (X-Gov repo scraper, 8 October 2026)", "Observed"), "fk": ("government", "Forks (scraper)", "Observed"), "li": ("government", "Licence code from GitHub's licence detection (scraper)", "Observed"),
 "cr": ("government", "Created date (scraper)", "Observed"), "pd": ("government", "Last push date (scraper)", "Observed"), "oiss": ("government", "Open issues (scraper)", "Observed"),
 "dest_org": ("co-cddo", "Proposed destination organisation, including uk-gov-cyber for security work", "Assessed"), "v1": ("co-cddo", "The v1 workbook's owner, target, evidence and scores, plus its model re-run with observed evidence", "Imported and Calculated"),
 "controls": ("co-cddo", "Result and evidence for each of the 14 assurance controls", "Calculated from observed and v1 evidence"), "sector": ("government", "Sector of the owning organisation", "Assessed"), "total_on_github": ("government", "Public repositories GitHub reports for the organisation", "Observed"),
}
need(all(k in rows[0] for k in FIELD_DOC if FIELD_DOC[k][0] == "co-cddo"), "C-DOC-02", "every documented co-cddo field exists in the data")
need(all(k in XF or k in ("sector", "total_on_github") for k in FIELD_DOC if FIELD_DOC[k][0] == "government"), "C-DOC-03", "every documented government field exists in the data")
METHOD = [
 ["co-cddo listing", f"GitHub's own page data for github.com/orgs/co-cddo, read in a browser on {REF_DATE:%-d %B %Y} and checksum-verified on transcription. {REPO_COUNT} public repositories."],
 ["co-cddo activity", "Full git history of every repository, all branches, merge commits excluded. Bots (Dependabot, Renovate, GitHub Actions, names ending -bot) excluded from human counts. Windows are by UTC date."],
 ["Contributors", "Commit authors only; identities merged when they share an email or name, so counts are upper bounds. Names are shown for co-cddo only."],
 ["Code coupling", "Latest commit of each repository searched for co-cddo and cddo.cabinetoffice references, each classified (reusable workflow, OIDC trust, package or module source, Pages address, team, hard-coded name, link)."],
 ["GDS Way", "Rules from Use GitHub, How to store source code and Using GitHub Actions, checked at the latest commit. GDS-owned actions count as first party. Account rules and branch protection can't be read from public data."],
 ["Across government", "219 organisations: GitHub's public list of government organisations (215) plus 4 added. Repositories listed by most recent update and stopped once older than 12 months; each confirmed with git (commits to 7 October 2026). Active and maintained repositories were then read at their latest commit on 8 October 2026 for the README, licence and practice signals."],
 ["Organisation totals", "Public repository counts from GitHub's own page data, 8 October 2026 (checksum-verified). Three organisations in GitHub's list no longer exist."],
 ["GitHub Pages", "Each repository's organisation.github.io address requested, redirects followed; a site counts when the final response is 200. A control address per organisation detects catch-all redirects."],
 ["Strategy and DAM tags", "Declared phrase vocabularies (each linked to its source) matched on name, description, topics and README first paragraph. Precision estimated by an AI reviewer on a labelled sample, shown per tag; tags are leads, not proof."],
 ["Asset catalogue", f"Every public repository listed by the X-Gov open-source repo scraper (nightly repos.json, read 8 October 2026: {cat['source']['scraper_rows']:,} rows, {cat['source']['scraper_unique']:,} unique), joined to the git-verified government layer. Repositories the government layer had not read were checked with git when pushed in the last 12 months; older ones take their status from the push date, which can only show Dormant or Inactive."],
 ["Publishers", "GitHub accounts mapped to public bodies using the UK Public Sector Code by Organisation mapping (MIT licence); body types from the v1 workbook."],
 ["Catalogues and standards", f"Platform and standard signals from names, descriptions, READMEs and file names across the catalogue; then {stdr['fetched']['files_parsed']} metadata, data, schema and configuration files from {stdr['fetched']['repos']} repositories were fetched with git and parsed (RDF with rdflib, ISO XML, CSVW, data packages, DCAT JSON, LinkML, CKAN and DataHub configuration, Terraform). Each standard is graded per repository: mentioned, schema or profile, applied in data, or every record. Ontology and vocabulary files are kept apart from data records."],
 ["v1 workbook", "Imported as a provenance layer: owner knowledge, targets, evidence, actions, its scoring model and assurance controls. Its names were reconciled to GitHub's listing; a rename is accepted only when the old and new names serve the same HEAD commit. Its scoring model was ported and reproduces all of its own scores, then re-run with observed evidence."],
 ["Destinations", "Assessed by the author from name, README, contributors and coupling. Owners confirm or change them on this page."],
]

# ---------------- check registry ----------------
REG = []
def reg_from(path, prefix_ok=True, group=""):
    for l in open(path).read().splitlines():
        m = re.match(r"^(PASS|FAIL) ([A-Z][A-Z0-9-]*\d+n?)\s+(.*?)(\s+\[guards: (.*)\])?$", l)
        if m: REG.append(dict(id=m.group(2), status=m.group(1).lower(), text=m.group(3), guards=m.group(5) or "", group=group))
reg_from(os.path.join(S, "build_checks.txt"), group="Inventory build")
reg_from(os.path.join(X, "xgov_checks.txt"), group="Government scan")
reg_from(os.path.join(CATD, "catalogue_checks.txt"), group="Asset catalogue")
reg_from(IN["ipath"]("build/v1/v1_checks.txt"), group="v1 workbook import")
reg_from(os.path.join(CATD, "std_checks.txt"), group="Catalogues and standards")
DAMAD = os.path.join(os.path.dirname(S), "dama")
reg_from(os.path.join(DAMAD, "export_checks.txt"), group="Data management wheel")
reg_from(os.path.join(DAMAD, "extra_checks.txt"), group="APIs and open data")
reg_from(os.path.join(DAMAD, "gds_checks.txt"), group="GDS responsibilities")
reg_from(os.path.join(DAMAD, "practices_checks.txt"), group="Practice across disciplines")
reg_from(os.path.join(DAMAD, "hier_checks.txt"), group="Organisation family tree")
reg_from(os.path.join(DAMAD, "legacy_checks.txt"), group="Legacy and technical debt")
reg_from(os.path.join(DAMAD, "crosswalk_checks.txt"), group="govukOS organisation crosswalk")
reg_from(os.path.join(DAMAD, "service_design_checks.txt"), group="Service design")
reg_from(os.path.join(DAMAD, "user_guide_checks.txt"), group="User guide")
reg_from(os.path.join(DAMAD, "tours_checks.txt"), group="Guided tours and tutorials")
reg_from(os.path.join(DAMAD, "subjects_checks.txt"), group="Subjects (GOV.UK topics)")
reg_from(os.path.join(DAMAD, "services_checks.txt"), group="Public services, capabilities, processes and workflows")
reg_from(os.path.join(DAMAD, "devolution_checks.txt"), group="Strategic authorities")
reg_from(os.path.join(DAMAD, "features_checks.txt"), group="GitHub feature settings")
reg_from(os.path.join(DAMAD, "interop_checks.txt"), group="Data interoperability")
reg_from(os.path.join(DAMAD, "registers_checks.txt"), group="Registers and authoritative sources")
reg_from(os.path.join(DAMAD, "ghverify_checks.txt"), group="Checked against GitHub")
reg_from(IN["ipath"]("build/dama/collab_checks.txt"), group="Beyond GitHub: Slack")
reg_from(IN["ipath"]("build/dama/life_checks.txt"), group="What each project is")
reg_from(os.path.join(DAMAD, "reuse_checks.txt"), group="Reuse map")
reg_from(os.path.join(DAMAD, "plainlang_checks.txt"), group="Plain language")
os.system(f"cd {DAMAD} && python3 -I roadmap.py > /dev/null")   # R71: roadmap and GitHub connections, one source
reg_from(os.path.join(DAMAD, "roadmap_checks.txt"), group="Roadmap and GitHub")
reg_from(os.path.join(DAMAD, "pii_checks.txt"), group="Personal data")
reg_from(os.path.join(DAMAD, "cdot_checks.txt"), group="Crown dependencies and overseas territories")
REG.append(dict(id="C-GHV-04", status="fail" if "C-GHV-04" in FAILS else "pass", text=f"{NEW_ADDED} {NEW_MSG}", guards="R57", group="Checked against GitHub"))
if CDOT: REG.append(dict(id="C-CDOT-02", status="fail" if "C-CDOT-02" in FAILS else "pass", text=f"{sum(1 for a in CDOT['accounts'] if a.get('in_catalogue'))} official crown dependency accounts and their repositories added to the catalogue from direct verification; probable and unconfirmed accounts are listed but not added", guards="R56", group="Crown dependencies and overseas territories"))
reg_from(os.path.join(DAMAD, "themes_checks.txt"), group="Themes: guidance, journeys, nations, international")
for tf, cid, txt, g in [("test_rules.py", "C-DAMA-06", "DAMA rule regression tests, including a negative test for each false positive found in the precision review", "V7-2"), ("test_parse.py", "C-DAMA-07", "dependency manifest parser tests for nine formats, with negative tests for malformed and commented input", "V7-1")]:
    out = os.popen(f"python3 {DAMAD}/{tf}").read().splitlines(); nf_ = sum(l.startswith("FAIL") for l in out); np_ = sum(l.startswith("PASS") for l in out)
    REG.append(dict(id=cid, status="pass" if np_ and not nf_ else "fail", text=f"{np_} {txt}", guards=g, group="Data management wheel"))
tax = os.popen(f"python3 {X}/test_taxonomy.py").read().splitlines()
tax_fail = sum(1 for l in tax if l.startswith("FAIL"))
REG.append(dict(id="C-TAX-ALL", status="pass" if not tax_fail else "fail", text=f"{sum(1 for l in tax if l.startswith(('PASS','FAIL')))} tagging regression tests, including each reviewed false positive and miss", guards="D7, D-X1–3", group="Tagging"))
REG += [dict(id="GW-1", status="pass", text="GDS Way checker evaluates every repository whose tree lists workflows (assertion in gdsway.py; negative test reintroduces the bug)", guards="GW-1 hidden .github skipped", group="GDS Way"),
        dict(id="GW-2", status="pass", text="No security-contact pass relies on co-cddo's organisation file (assertion in gdsway.py)", guards="D9", group="GDS Way"),
        dict(id="D20", status="pass", text="GDS-owned actions are first party; third-party actions still checked (assertion in gdsway.py)", guards="D20", group="GDS Way"),
        dict(id="C-EXP-01", status="pass", text="Export covers every repository (assertion in export_data.py)", guards="D1", group="Export"),
        dict(id="C-EXP-02", status="pass", text="Monthly series reconciles with the rolling 12-month total (assertion in export_data.py)", guards="windowing", group="Export")]
# C-SR-01 (V713-6): the repository has what a well-kept repository needs, including the README's sections for each kind of reader
_sr = __import__("runpy").run_path(os.path.join(os.path.dirname(os.path.dirname(S)), "build", "tools", "self_routines.py"))
_srg = _sr["assess"](); _srn = bool(_sr["assess"](needed=[("README.md", r"^## No such section")]))
if _srg or not _srn: FAILS.append("C-SR-01"); print("FAIL C-SR-01", _srg, _srn)
REG.append(dict(id="C-SR-01", status="fail" if (_srg or not _srn) else "pass", text="the repository has what a well-kept GitHub repository needs, including the README's sections for beginner, intermediate and advanced readers; it runs on every pull request; negative test: a missing section is caught", guards="V713-6", group="Self-routines"))
# C-LIC-01 (V713-4): the MIT notices of the two projects whose data is republished travel with it
def _lic_problems(text):
    need = ["uk-x-gov-software-community/xgov-opensource-repo-scraper", "chrishylanduk/uk-public-sector-code-by-org"]
    return [n for n in need if n not in text] + ([] if text.count("Permission is hereby granted, free of charge") >= 2 else ["two MIT permission notices"])
_tpn = os.path.join(os.path.dirname(os.path.dirname(S)), "THIRD-PARTY-NOTICES.md")
_lp = _lic_problems(open(_tpn).read() if os.path.exists(_tpn) else ""); _lneg = bool(_lic_problems("xgov-opensource-repo-scraper only"))
if _lp or not _lneg: FAILS.append("C-LIC-01"); print("FAIL C-LIC-01", _lp, _lneg)
REG.append(dict(id="C-LIC-01", status="fail" if (_lp or not _lneg) else "pass", text="THIRD-PARTY-NOTICES.md carries the MIT notices of the X-Gov repo scraper and the UK Public Sector Code by Organisation mapping, whose data the catalogue republishes; negative test: a file naming only one source fails", guards="V713-4", group="Security"))
pk = [t for t in prec if prec[t].get("n", 0) >= 5]
REG.append(dict(id="C-PREC-01", status="pass" if pk else "fail", text=f"Precision measured on a labelled sample for {len(pk)} tags (n ≥ 5 each)", guards="D7 unmeasured precision", group="Tagging"))
for cid in ["C-V4-01", "C-V4-02", "C-V4-03", "C-V4-04", "C-V4-05", "C-DOC-02", "C-DOC-03", "C-V5-01", "C-V5-02", "C-V5-03", "C-V5-04", "C-V5-05"]:
    REG.append(dict(id=cid, status="fail" if cid in FAILS else "pass", text={"C-V4-01": "Page rows equal GitHub's count", "C-V4-02": "co-cddo Pages flags agree between layers", "C-V4-03": "Spotlight repositories have human activity", "C-V4-04": "Practice benchmark computed", "C-V4-05": "Every risk quote is found verbatim in the saved GitHub page", "C-DOC-02": "Data dictionary matches co-cddo fields", "C-DOC-03": "Data dictionary matches government fields", "C-V5-01": "Catalogue organisations extend the government layer without reordering it", "C-V5-02": "Catalogue field names don't collide with government-layer names", "C-V5-03": "Every co-cddo repository has a result for each assurance control", "C-V5-04": "Every co-cddo repository has v1-model scores re-run with observed evidence", "C-V5-05": "Security repositories are offered uk-gov-cyber (V5-1)"}[cid], guards="assembly", group="Assembly"))
PAGE_CHECKS = ["P-%02d" % i for i in range(1, 58)]
HARNESS = ["T-PII-01", "T-INF-01", "T-SVC-01", "T-CLS-01", "T-TOUR-01", "T-TIP-01", "T-UG-01", "T-TH-01", "T-KN-01", "T-SRCH-01", "T-SUP-02", "T-OS-01", "T-CON-02", "T-LEG-01", "T-RX-01", "T-RX-02", "T-RX-03", "T-FAM-01", "T-DEC-01", "T-DEC-02", "T-DEC-03", "T-DEC-04", "T-XSS-01", "T-XSS-02", "T-AXE-01", "T-CON-01", "T-KEY-01", "T-KEY-02", "T-KEY-03", "T-KEY-04", "T-AI-01", "T-AI-02", "T-IMP-01", "T-TXT-01", "T-VIEW-01", "T-VIEW-02", "T-CSV-01", "T-DOC-01", "T-DOC-02", "T-CAT-01", "T-CAT-02", "T-V1-01", "T-CTL-01", "T-STD-01", "T-IA-01", "T-IA-02", "T-IA-03", "T-TOP-01", "T-ORG-01", "T-COL-01", "T-HID-01", "T-WID-01", "T-DAMA-01", "T-SUP-01", "T-API-01", "T-OD-01", "T-INS-01", "T-HERO-01", "T-NAV-01", "T-DRAW-01", "T-GDS-01", "T-PRAC-01", "T-GDSX-01"]
for t in HARNESS:
    res = tests.get(t)
    REG.append(dict(id=t, status=(res or {}).get("status", "not run"), text=(res or {}).get("text", "Harness test (runs before publishing)"), guards=(res or {}).get("guards", ""), group="Page harness"))
# C-TST-01 (V714-2): every registered harness test has a result; a test with none was shown as "not run" without stopping the build
_notrun = [t for t in HARNESS if not tests.get(t) or tests[t].get("status") not in ("pass", "fail")]
_tneg = [t for t in ["T-A", "T-B"] if not {"T-A": {"status": "pass"}}.get(t)] == ["T-B"]
if _notrun or not _tneg: FAILS.append("C-TST-01"); print("FAIL C-TST-01", _notrun)
REG.append(dict(id="C-TST-01", status="fail" if (_notrun or not _tneg) else "pass", text=f"every one of {len(HARNESS)} registered harness, accessibility, width and contrast tests has a recorded result in test_results71.json; none is left 'not run'{': missing ' + ', '.join(_notrun) if _notrun else ''}; negative test: a test with no result is caught", guards="V714-2", group="Page harness"))
for p in PAGE_CHECKS: REG.append(dict(id=p, status="live", text="Runs in your browser on every load (see the list below)", guards="", group="Page self-check"))

PRAC = json.load(open(os.path.join(os.path.dirname(S), "dama", "practices.json")))
_tn = sorted(set(PRAC["types"].values())); PRAC["typeNames"] = _tn; PRAC["types"] = {k: _tn.index(v) for k, v in PRAC["types"].items()}
# ---------------- v6: colour system, token usage, topics, design assessment ----------------
V6 = os.path.join(os.path.dirname(S), "v6")
pal_rc = os.system(f"python3 {V6}/palette.py > {V6}/palette_checks.txt")
PAL = json.load(open(os.path.join(V6, "palette.json")))
if pal_rc != 0: FAILS.append("C-COL-01"); print("FAIL C-COL-01 the colour check did not run (exit", pal_rc, ")")   # V73-2: a missing script no longer passes silently
SAN = os.path.join(os.path.dirname(S), "scan_sensitive.py")
san_rc = os.system(f"python3 -I {SAN} --sources > {S}/scan_sensitive.txt") if os.path.exists(SAN) else None
if san_rc not in (None, 0): FAILS.append("C-SAN-01"); print(open(os.path.join(S, "scan_sensitive.txt")).read()[-1500:])
REG.append(dict(id="C-COL-01", status="pass" if pal_rc == 0 and not PAL["fails"] else "fail", text=f"Every colour pair the page uses meets WCAG 2.2: text 4.5:1 and marks, field borders and diagram strokes 3:1, in light and dark themes ({len(PAL['hues'])} hues, unrounded ratios)", guards="A-2, A-3", group="Colour and design"))
REG.append(dict(id="C-SAN-01", status="pass" if san_rc in (None, 0) else "fail", text="The repository holds no email addresses, links to private apps, protective markings, named owners or contributor names; a self-test plants one of each and must catch all five" + ("" if san_rc is not None else " (not run: outside the repository)"), guards="V73-3, R40", group="Privacy and disclosure"))
REG.append(dict(id="C-COL-01n", status="pass" if PAL["negative_test_rejects_v5"] else "fail", text="Negative test: the colour check rejects the 5.1 field border (1.53:1) and lineage stroke (2.995:1)", guards="A-2, A-3", group="Colour and design"))
tplv6 = open(os.path.join(S, "explorer71.tpl.html")).read()
defined = sorted(set(re.findall(r"--([a-z][a-z0-9-]*):", tplv6)))
def used(tok, text): return bool(re.search(r"var\(--%s\)" % re.escape(tok), text) or re.search(r"[\"'`]--%s[\"'`]" % re.escape(tok), text) or re.search(r"var\(--\$\{", text) and tok in PAL["hues"])
unused = [t for t in ("w1", "w2", "w3", "dec", "cons", "keep", "arch", "del", "line-strong") if not used(t, tplv6)]
neg_ok = used("w2", 'const G = ["x", "y", "--w2"]') and not used("w2", "color: red")
REG.append(dict(id="C-COL-02", status="pass" if not unused and neg_ok else "fail", text=f"Token usage counts var(--x) and quoted '--x' references; every migration and boundary token is used (unused: {unused or 'none'}); negative test on --w2 passes", guards="V6-1", group="Colour and design"))
need(not unused and neg_ok, "C-COL-02", "token usage check")
sys.path.insert(0, V6); from topics import TOPICS
for t in TOPICS: re.compile(t[3])
DESIGN = dict(
 summary="Version 6.0 reorganises the catalogue around the people who use it and the questions they ask, not around how it was built. It was assessed against the GOV.UK Service Manual, the Government Design Principles, GOV.UK content design guidance, Nielsen's usability heuristics, common information architecture schemes (audience, task and topic) and WCAG 2.2.",
 audiences=[["Policy, strategy and briefing", "Who works on my policy area; how open code lines up with priorities; facts for briefings and answers", "Home cards, Topics and priorities, Ask AI"],
  ["Data, metadata and analysis", "Who runs data catalogues and with which supplier; who applies metadata standards; DAM-related work", "Topics and priorities"],
  ["Leaders of departments and arm's-length bodies", "Our estate on a page; how we compare; who does similar work; what to fix first", "Organisations"],
  ["Service and product teams", "Something to reuse before building; who uses common platforms", "Find code, Topics"],
  ["Security, risk and assurance", "How well code is looked after; risky websites; missing licences and contacts", "Good practice, Organisations"],
  ["Engineers and developers", "Search, patterns, practice benchmarks, GDS Way", "Find code, Good practice"],
  ["Commercial, finance and spend controls", "Existing work before funding a build; platforms and suppliers in use", "Find code, Data catalogues and standards"],
  ["co-cddo repository owners and the migration lead", "Where each repository goes, what breaks, the plan", "co-cddo move"]],
 findings=[
  ["The structure followed the build, not the users", "10 of 26 views (38%) served the co-cddo move, which concerns a few dozen people; cross-government content was split across three groups", "Service Manual: start with user needs; IA organisation schemes", "Eight hubs, each led by audience and question; the migration is one hub"],
  ["One audience was assumed: technologists", "Labels such as Reconciliation, Lineage, Traceability, Landscape, Engineering practice; GitHub terms unexplained outside a migration glossary", "Nielsen: match between the system and the real world; GOV.UK content design: plain English", "Plain-English labels, a hub band on every view saying what it is and who it's for, and a 23-term plain-English guide"],
  ["The first screen was about the migration", "Start opened on co-cddo facts; the spotlight carousel sat above the navigation", "Design principles: do the hard work to make it simple", "A question-led home page with eight 'what kind of work do you do?' cards; the spotlight moved under the home page"],
  ["No way to browse by policy area", "Topic work was only reachable by search", "IA: topic scheme alongside audience and task", "15 topics with live counts, organisations and most active projects, each labelled as keyword leads"],
  ["No organisation-level view", "Publishers linked to a filtered list of repositories", "Top task for leaders; priority 1 use 82 in the uses document", "Estate on a page for every public body, with peers and suggested next steps"],
  ["Long flat menu", "26 options in one scrolling rail with internal group names", "Nielsen: recognition rather than recall", "Eight hub buttons; a hub's sections show only when it is open"],
  ["GitHub explained after the numbers", "In 7.12 Home opened with a promotion and a carousel of figures; GitHub itself was explained in a one-line prompt; the user guide sat between the briefing and the repo profile; the plain-English guide was under About", "GOV.UK design principles: start with user needs, do the hard work to make it simple; progressive disclosure", "Start here hub: GitHub in two minutes, what the catalogue is, how to find things, the kind of work you do, then headlines. Then Find code, the lenses, insights and assurance, with About last (R68, P-54)"],
  ["Colour carried little meaning", "Mostly one teal accent; colour density fell as content grew from 55 KB to 220 KB of template", "Data visualisation practice: colour by job", "A validated eight-hue categorical palette with an icon and label wherever colour appears; a single-hue ramp for activity"],
  ["Accessibility gaps automated tests missed", "Field borders 1.53:1; lineage stroke 2.995:1; two group fills under 3:1", "WCAG 2.2: 1.4.11 non-text contrast", "Re-stepped tokens; a build check with a negative test (A-2, A-3)"],
  ["Third-party font requests", "Google Fonts received each viewer's IP address", "Privacy by design", "Fonts embedded in the page"]],
 was={"topics": "", "strategy": "Strategy alignment", "dam": "DAM and metadata", "standards": "Catalogues and standards", "publishers": "Publishers", "landscape": "Landscape", "catalogue": "Search the catalogue", "pages": "GitHub Pages", "practice": "Engineering practice",
      "start": "Start here", "overview": "Overview", "repos": "Repositories", "reconcile": "Reconciliation", "assess": "Assessment", "controls": "Assurance controls", "lineage": "Lineage", "safe": "Moving safely", "plan": "Plan", "gdsway": "GDS Way", "evidence": "Evidence and actions",
      "ask": "Ask a question", "ai": "How AI is used", "docs": "Documents", "trace": "Traceability", "defects": "Defects and releases", "about": "Method and checks", "a11y": "Accessibility"},
 new_views=["home", "guide", "discover", "topics", "orgs", "glossary", "design"],
 colour="Each hub and topic has one of eight hues from a categorical palette validated for colour-blind separation (worst adjacent difference ΔE 9.1 light, 8.4 dark). Every hue has three steps: a mark for bars and fills (3:1 or more), an ink for text and borders (4.5:1 or more, on white and on its own tint) and a light tint for backgrounds. Colour never works alone: every coloured element also has a label, a number or an icon. Activity uses a single blue ramp from dark (active) to light, with grey for archived.",
 next=["Test the home page, topics and organisation profiles with 5 to 8 people from at least four of the audiences, none of whom use GitHub, and change labels that don't work for them.",
       "Measure the precision of each topic on a labelled sample, as was done for strategy and DAM tags, and mark checked topics.",
       "Ask a small number of organisations to check their profile and say whether the next steps are useful.",
       "Run a screen-reader and 400% zoom check of the new views.",
       "Track which hubs and questions people use, with consent, to refine the structure."],
 sources=[["GOV.UK Service Manual", "https://www.gov.uk/service-manual"], ["Government Design Principles", "https://www.gov.uk/guidance/government-design-principles"], ["Content design: planning, writing and managing content", "https://www.gov.uk/guidance/content-design"],
          ["Nielsen Norman Group: 10 usability heuristics", "https://www.nngroup.com/articles/ten-usability-heuristics/"], ["Web Content Accessibility Guidelines (WCAG) 2.2", "https://www.w3.org/TR/WCAG22/"], ["GOV.UK Design System", "https://design-system.service.gov.uk/"]])
REG.append(dict(id="C-ALL", status="pass" if all(r["status"] in ("pass", "live") for r in REG) else "fail", text="Every registered check passes", guards="R14", group="Meta"))
SEC_LATE = {"C-SEC-01", "C-SEC-01n", "C-SEC-02", "C-SEC-03", "C-SEC-04", "C-SEC-05", "C-SEC-06", "C-SEC-07", "C-QR-01", "C-TZ-01", "C-WF-01", "C-SET-01", "C-DIST-01", "C-DIST-02", "C-DEC-01"}   # registered by the security block and the QR code step, which runs on the finished data below
ids = {r["id"] for r in REG} | SEC_LATE
refs = [c for q in REQUIREMENTS for c in q[4]] + [c for d in DEFECTS for c in d[6]]
missing = sorted({c for c in refs if c not in ids})
need(not missing, "C-DOC-01", f"every requirement and defect traces to a registered check (missing: {missing})")
REG.append(dict(id="C-DOC-01", status="pass" if not missing else "fail", text="Every requirement and defect traces to a registered check", guards="broken traceability", group="Assembly"))

# ---------------- artefact pack ----------------
css = open(os.path.join(S, "explorer71.tpl.html")).read()
lt = dict(re.findall(r"--([\w-]+):(#[0-9a-fA-F]{6})", re.search(r":root\{(.*?)\}", css, re.S).group(1)))
dk = dict(re.findall(r"--([\w-]+):(#[0-9a-fA-F]{6})", re.search(r':root\[data-theme="dark"\]\{(.*?)\}', css, re.S).group(1)))
must_gap = sum(1 for r in rows if r["destination_group"][0] in "1234" and any(v[0] == "fail" and next(x for x in gw["rules"] if x["id"] == k)["strength"] == "MUST" for k, v in r["gdsway"].items()))
CODE = ("ref_uses", "ref_oidc", "ref_pkg", "ref_pages", "ref_team", "ref_hardorg")
ctx = dict(n_repos=len(rows), n_active=sum(r["status"] == "Active" for r in rows), n_must_gap=must_gap, n_pages_co=sum(r["pages"] for r in rows),
           n_breaking=sum(sum(r[k] for k in CODE) for r in rows if r["destination_group"][0] in "1234"),
           needs=[[n[0], n[1]] for n in NEEDS], dictionary=[[k, v[0], v[1], v[2]] for k, v in FIELD_DOC.items()], glossary=GLOSSARY,
           groups=["Wave 1: shared dependencies", "Wave 2: active products", "Wave 3: low-activity keepers", "Owner decision (gds-dtx, alphagov or keep)", "Consolidate into another repository", "Already archived", "Archive in place", "Delete (empty or unmodified fork)"],
           strategy=[[s[0], s[2], s[3], s[4]] for s in STRATEGY], families=sorted({r["family"] for r in rows}),
           tokens=[[k, v, dk.get(k, v)] for k, v in lt.items()],
           n_assets=len(XR) + len(cat["cat"]), n_bodies=len(cat["bodies"]), n_accounts=len(orgs), n_v1=len([x for x in v1["reconciliation"] if x["v1"]]),
           n_renamed=sum(1 for x in v1["reconciliation"] if x["status"] == "Old name (renamed)"), n_unlisted=len(UNLISTED), n_added=sum(1 for x in v1["reconciliation"] if x["status"] == "Missing from v1"),
           cf=cat["cf"], controls=[[c["Control domain"], c["Required evidence"], c["Decision rule"]] for c in v1["controls"]])
DOCS = pack(ctx)

# ---------------- colophon ----------------
import qrcode, qrcode.image.svg, barcode
from barcode.writer import SVGWriter
def _qr_svg(text, border=2, mm=0.6):
    """QR code as SVG drawn from the module matrix with whole-number coordinates, so the output is the same on every
    Python version and platform (V711-5: the library's own SVG writer printed decimals differently on the build runner)."""
    q = qrcode.QRCode(border=border); q.add_data(text); q.make(fit=True); m = q.get_matrix(); n = len(m)
    d = "".join(f"M{x},{y}h1v1h-1z" for y, row in enumerate(m) for x, on in enumerate(row) if on)
    w = f"{n * mm:g}mm"
    return f'<svg width="{w}" height="{w}" version="1.1" viewBox="0 0 {n} {n}" xmlns="http://www.w3.org/2000/svg" shape-rendering="crispEdges"><path d="{d}" id="qr-path" fill="#000000"/></svg>'
qr_svg = _qr_svg(URL)
_qr_ok = lambda svg: bool(re.search(r'<path d="(M\d+,\d+h1v1h-1z)+"', svg)) and not re.search(r"\d\.\d", svg.split('d="', 1)[-1].split('"', 1)[0])
_lib = qrcode.make("x", image_factory=qrcode.image.svg.SvgPathImage, box_size=6, border=2).to_string(encoding="unicode")
_qrn = _qr_ok(qr_svg) and not _qr_ok(_lib)
_tzok = int(_utc('2026-10-15').timestamp()) == 1792022400 and int(_utc('2026-10-15T01:00:00+01:00').timestamp()) == 1792022400
need(_tzok, 'C-TZ-01', 'dates without a time zone are read as UTC, so the page is the same in every time zone (V711-5); negative test: a date with its own offset keeps it')
REG.append(dict(id='C-TZ-01', status='pass' if _tzok else 'fail', text='Dates without a time zone are read as UTC, so builds match in every time zone', guards='V711-5', group='Assembly'))
need(_qrn, "C-QR-01", "the QR code is drawn with whole-number coordinates, so the page is byte-for-byte the same on every Python version; negative test: the library's own SVG writer, which printed decimals differently on the build runner, is rejected (V711-5)")
REG.append(dict(id="C-QR-01", status="pass" if _qrn else "fail", text="The QR code is drawn with whole-number coordinates, so builds are reproducible on every Python version; the library's own SVG output is rejected", guards="V711-5", group="Assembly"))
b = io.BytesIO(); barcode.get("code128", DOCID, writer=SVGWriter()).write(b, options=dict(module_height=9, font_size=6, text_distance=3, quiet_zone=2))
bc_svg = b.getvalue().decode(); bc_svg = bc_svg[bc_svg.index("<svg"):]

PLAN = list(base["plan"])
PLAN.insert(next((i for i, p in enumerate(PLAN) if str(p["wave"]).startswith("1")), 1), dict(wave="0 — Agree destinations", action=f"Offer uk-gov-cyber to the owners of the {len(cy)} security repositories (Secure by Design, GC3, domains, email security): co-cddo's deprecation notice names uk-gov-cyber alongside gds-dtx. Record each owner's choice on this page.", why="Source: co-cddo/.github profile README, commit 1896ecb, 11 September 2026."))
meta = dict(base["meta"], repo_count=REPO_COUNT, ref_date=REF_DATE.isoformat(), xref_date="2026-10-07", enr_date="2026-10-08", ref_epoch=REF_EPOCH, xref_epoch=XREF_EPOCH)
data = dict(meta=meta, rows=rows, edges=base["edges"], plan=PLAN, related=base["related"], version=VERSION, docid=DOCID, url=URL, issues_url=ISSUES_URL, contact_url=CONTACT_URL, os_urls=OS_LINKS.get("urls", {}),
            gdsway_rules=gw["rules"], xorgs=orgs, xf=XF, xrows=XR, strategy=xg["strategy"], standards=xg["standards"], spotlight=spot,
            phases=PHASES, risks=RISKS, risks_checked=CHECKED, transfer=TRANSFER, bench=BENCH, bench_co=BENCH_CO, precision=prec,
            needs=NEEDS, glossary=GLOSSARY, method=METHOD, docs=DOCS, requirements=REQUIREMENTS, defects=DEFECTS, releases=RELEASES, registry=REG,
            qr=qr_svg, barcode=bc_svg, cat=cat["cat"], cf=cat["cf"], bodies=cat["bodies"], catsrc=cat["source"], unlisted=UNLISTED,
            topics=[list(t) for t in TOPICS], dama=json.load(open(os.path.join(DAMAD, "dama_data.json"))), apis={k: v for k, v in json.load(open(os.path.join(DAMAD, "apis.json"))).items()}, guide=json.load(open(os.path.join(DAMAD, "user_guide.json"))), tours=json.load(open(os.path.join(DAMAD, "tours.json"))), subjects=json.load(open(os.path.join(DAMAD, "subjects.json"))), services=json.load(open(os.path.join(DAMAD, "services.json"))), devolution=json.load(open(os.path.join(DAMAD, "devolution.json"))), interop=json.load(open(os.path.join(DAMAD, "interop.json"))), cdot=CDOT, pii_skip=sorted(__import__("runpy").run_path(os.path.join(DAMAD, "pii.py"))["NOT_PEOPLE"]), registers=json.load(open(os.path.join(DAMAD, "registers.json"))), ghverify=json.load(open(os.path.join(DAMAD, "ghverify.json"))), collab=json.load(open(IN["ipath"]("build/dama/collab.json"))), life=json.load(open(IN["ipath"]("build/dama/life.json"))), reuse=json.load(open(os.path.join(DAMAD, "reuse.json"))), features=json.load(open(os.path.join(DAMAD, "repo_features.json"))) if os.path.exists(os.path.join(DAMAD, "repo_features.json")) else None, opendata=json.load(open(os.path.join(DAMAD, "opendata.json"))), gds=json.load(open(os.path.join(DAMAD, "gds.json"))), practices=PRAC, hier=json.load(open(os.path.join(DAMAD, "hier.json"))), legacy=json.load(open(os.path.join(DAMAD, "legacy.json"))), crosswalk=(lambda c: {**c, "links": {**c["links"], **OS_LINKS.get("crosswalk", {})}})(json.load(open(os.path.join(DAMAD, "crosswalk_web.json")))), themes=json.load(open(os.path.join(DAMAD, "themes.json"))), service=json.load(open(os.path.join(DAMAD, "service_design.json"))), palette=dict(hues=PAL["hues"], extra=PAL["extra"]), design=DESIGN, std=STD, v1={k: v1[k] for k in ("source", "weights", "thresholds", "criteria", "gates", "dest_rules", "reconciliation", "actions", "evidence", "controls", "sequence", "deprecation_notice")})
# ---------------- security guardrails (7.11, R63): see build/dama/security.py and docs/security/threat-model.md ----------------
SEC = __import__("runpy").run_path(os.path.join(DAMAD, "security.py"))
AUD = os.environ.get("GHRAC_AUDIENCE", "public"); assert AUD in ("gov", "public"), AUD
PROV = json.load(open(os.path.join(DAMAD, "provenance.json")))
data["provenance"] = PROV
data["roadmap"] = json.load(open(os.path.join(DAMAD, "roadmap.json")))
# Decisions on proposed destinations (R72): recorded on GitHub through an issue form in the private companion repository, collected into
# build/inv/decisions.json there by build/tools/collect_decisions.py in the internal workflow, and embedded only in the government edition.
_CD = __import__("runpy").run_path(os.path.join(os.path.dirname(S), "tools", "collect_decisions.py"))
_DECF = IN["ipath"]("build/inv/decisions.json"); _DEC = json.load(open(_DECF)) if os.path.exists(_DECF) else {}
data["decisions"] = _DEC.get("items", {})
data["decisions_src"] = dict(repo=os.environ.get("GHRAC_DECISIONS_REPO", "https://github.com/cyberdudeuk/github-repos-asset-catalogue-internal"), read=_DEC.get("read"))
_dfp = IN["ipath"](".github/ISSUE_TEMPLATE/move-decision.yml"); _dform = open(_dfp).read() if os.path.exists(_dfp) else ""
_dopts = re.findall(r"(?m)^\s+- \"?(.+?)\"?$", _dform.split("id: destination", 1)[1].split("- type:", 1)[0]) if "id: destination" in _dform else []
_cst = _CD["self_test"]()
_cdok = not _cst and _CD["GROUPS"] == ctx["groups"] and _dopts == _CD["GROUPS"] and all(k in _dform for k in ("id: repo", "id: decision", "id: note", "move-decision"))
need(_cdok and _CD["GROUPS"] == ctx["groups"] and _dopts == _CD["GROUPS"] and all(k in _dform for k in ("id: repo", "id: decision", "id: note", "move-decision")), "C-DEC-01",
     "decisions are recorded on GitHub: the companion repository's issue form lists the same destinations as the page and the collector, and the collector keeps the newest issue per repository, treats one closed as not planned as withdrawn, rejects unknown repositories, decisions and destinations, and keeps no author" + (f" (problems: {_cst}{'' if _dopts == _CD['GROUPS'] else '; the form lists other destinations'})" if _cst or _dopts != _CD["GROUPS"] else ""))
REG.append(dict(id="C-DEC-01", status="pass" if _cdok else "fail", text="Decisions are recorded on GitHub through an issue form and collected by a tested script; the form, the collector and the page list the same destinations", guards="R72", group="Security guardrails"))
NCOMM = SEC["protect_communities"](data)
SEC["audience"](data, AUD)
NSCRUB = SEC["scrub"](data)
_left = [u for u in SEC["URL"].findall(json.dumps(data, ensure_ascii=False)) if SEC["is_private"](u)]
def _sec(ok, cid, msg):
    need(ok, cid, msg); REG.append(dict(id=cid, status="pass" if ok else "fail", text=msg, guards="R63", group="Security guardrails"))
_sec(not _left and NSCRUB > 0, "C-SEC-01", f"{NSCRUB} links to sign-in-only or private addresses (SharePoint, Atlassian, Google Docs, Slack, Teams, localhost and private networks) quoted from repository text were replaced with a note; none are left in the page")
_st = SEC["self_test"]()
_sec(not _st, "C-SEC-01n", "negative tests: 11 private or sign-in-only addresses are caught and 7 look-alike public ones are not; takeover-prone hosting and plain http addresses are flagged; a page with an external script, eval, a form, an external font, a new-tab link without noopener, a missing or weakened Content-Security-Policy is caught; an account with no provenance is caught; the open build drops Slack channel names" + (f" (failed: {_st[:3]})" if _st else ""))
_orgnames = {o["org"] for o in orgs}
_extra = sorted({a["account"] for a in json.load(open(_GV))["accounts"]} - _orgnames)
_pp = SEC["provenance_problems"](orgs, _extra, PROV["accounts"])
_unc = sorted(a for a, v in PROV["accounts"].items() if not v["confirmed"])
_sec(not _pp, "C-SEC-03", f"every one of the {len(_orgnames | set(_extra))} accounts shown has provenance: {sum(1 for o in orgs if o['source'] == SEC['PROVENANCE'][0])} from the government.github.com registry and {len(PROV['accounts'])} checked on GitHub on {dt.date.fromisoformat(PROV['read']).day} {dt.date.fromisoformat(PROV['read']):%B %Y}, of which {len(_unc)} have no verified domain and are labelled 'not verified by GitHub'" + (f" (problems: {_pp[:3]})" if _pp else ""))
_pg = SEC["page_problems"](SEC["CSP_META"] + open(os.path.join(S, "explorer71.tpl.html")).read())
_sec(not _pg, "C-SEC-02", f"the page's code: {_pg or 'a Content-Security-Policy allowing no network requests, frames, forms or external scripts, styles and fonts; no eval-like code; no form that submits elsewhere; every new-tab link has rel=noopener'}")
_ROOT = os.path.dirname(os.path.dirname(S)); _rd = lambda f: open(os.path.join(_ROOT, f)).read() if os.path.exists(os.path.join(_ROOT, f)) else ""
_ird = lambda f: open(IN["ipath"](f)).read() if os.path.exists(IN["ipath"](f)) else ""
_hp = SEC["handling_problems"](_ird("HANDLING_INSTRUCTIONS.md"), _ird("README.md"), dt.date.today())
_leak = [f for f in IN["INTERNAL_FILES"] if os.path.exists(os.path.join(_ROOT, f))]
_pub_banner = SEC["README_BANNER"] in _rd("README.md")
_sec(not _hp and not _leak and not _pub_banner, "C-SEC-06", "the public repository holds none of the internal-only inputs and carries no handling banner; the private companion repository holds them, with GDS Way handling instructions (classification, handling group, a responsible role and contact, a review that isn't overdue) and the README banner" + (f" (problems: {(_hp + _leak + (['handling banner in the public README'] if _pub_banner else []))[:4]})" if _hp or _leak or _pub_banner else ""))
_WFD = os.path.join(os.path.dirname(os.path.dirname(S)), ".github", "workflows")
_wf = {f: open(os.path.join(_WFD, f)).read() for f in sorted(os.listdir(_WFD)) if f.endswith((".yml", ".yaml"))} if os.path.isdir(_WFD) else {}
_wp = SEC["workflow_problems"](_wf)
_sec(len(_wf) >= 4 and not _wp, "C-SEC-05", f"all {len(_wf)} automation workflows run with a read-only token unless a write is explained, pin every action to a commit SHA, don't keep the token after checkout, avoid pull_request_target and never put event text into a shell script; negative tests in C-SEC-01n" + (f" (problems: {_wp[:3]})" if _wp else ""))
_runs_build = {f: t for f, t in _wf.items() if "build_v71.py" in t}
_wfdeps = [f for f, t in _runs_build.items() if "pip install qrcode" not in t]
_neg_wf = [f for f, t in {"x.yml": "run: python3 -I build/inv/build_v71.py"}.items() if "pip install qrcode" not in t]
_verifies = [f for f, t in _wf.items() if "verify_dist.py" in t]
_sec(not _wfdeps and _neg_wf == ["x.yml"] and len(_verifies) >= 1, "C-WF-01", f"every workflow that builds the page installs its pinned dependencies first, and the build workflow checks the published page against this commit's code (the self-routines do too); negative test: a workflow that builds without installing them is caught (V711-7)" + (f" (missing in: {_wfdeps})" if _wfdeps else ""))
_SR = __import__("runpy").run_path(os.path.join(_ROOT, "build", "tools", "self_routines.py"))
_bl = json.load(open(os.path.join(_ROOT, ".github", "settings-baseline.json")))
_bl_ok = all(isinstance(v, list) and len(v) == 2 and str(v[1]).strip() for sec, items in _bl.items() if not sec.startswith("_") for v in items.values())
_fake = {"repos/o/r": {"has_wiki": True, "description": "Private"}, "repos/o/r/private-vulnerability-reporting": {"enabled": False}, "repos/o/r/rules/branches/main": [], "repos/o/r/labels?per_page=100": []}
_neg_rows = _SR["settings_audit"]("o/r", fetch=_fake.get, graphql=lambda q: None, baseline=_bl)
_neg_set = {r[0] for r in _neg_rows if r[3] == "drift"} >= {"has_wiki", "description_mentions_private", "private_vulnerability_reporting", "main_protected", "labels"} and any(r[3] == "unreadable" for r in _neg_rows)
_sec(_bl_ok and _neg_set, "C-SET-01", f"the repository's expected settings are written down with a reason for each ({sum(len(v) for k, v in _bl.items() if not k.startswith('_'))} settings), and the weekly self-routines report any drift from them without changing anything; negative test: drifted and unreadable settings are both reported")
if AUD == "public":
    _pub = json.dumps(data, ensure_ascii=False)
    _ml = SEC["move_leaks"](data)
    _sec(not _ml and data["collab"] is None and "public_channels" not in _pub and "ukgovernmentdigital|" not in _pub and "Slack messages" not in _pub, "C-SEC-04", "open edition: the Slack aggregates (including public channel names), the life labels drawn from Slack and the proposed co-cddo move (destinations, rationales, plan, the v1 workbook layer and its assurance results) are left out" + (f" (left in: {_ml[:3]})" if _ml else ""))
else:
    _sec(data["collab"] is not None and data["sec"]["audience"] == "gov", "C-SEC-04", "government build: for internal government and public sector users; the open build (GHRAC_AUDIENCE=public) leaves out the Slack aggregates, proved by C-SEC-01n")
_cl = SEC["community_leaks"](data)
_sec(not _cl and NCOMM["life"] > 0, "C-SEC-07", f"for the {len(SEC['SENSITIVE_COMMUNITIES'])} defence, intelligence and national security accounts, the catalogue lists what they publish but draws no inferences of its own: {NCOMM['life']} life labels, {NCOMM['practice']} sets of practice and security signals, {NCOMM['chat']} links to internal chat and {NCOMM['reuse']} mentions as reuse consumers are withheld, in both audiences; negative tests in C-SEC-01n" + (f" (left in: {_cl[:3]})" if _cl else ""))
_VD = __import__("runpy").run_path(os.path.join(_ROOT, "build", "tools", "verify_dist.py"))
_fake = "<p>x</p><script>const DATA = {\"a\": 1};\nlet y = 2;</script>"
_c, _d = _VD["split_page"](_fake)
_d1 = _c == "<p>x</p><script>const DATA = /*__DATA__*/null;\nlet y = 2;</script>" and _d == {"a": 1} and _VD["split_page"](_fake.replace("let y", "let z"))[0] != _c
_sec(_d1, "C-DIST-01", "the published page's code can be checked against this commit's code without the internal inputs: build/tools/verify_dist.py sets the embedded data and fonts aside and compares the rest with the assembled parts, in the build and Pages workflows; negative test: one changed line is caught")
if AUD == "public":
    _d2 = _VD["open_edition_problems"](data, SEC["CSP_META"])
    _sec(not _d2, "C-DIST-02", "this page is the open edition: no Slack aggregates, no co-cddo move proposals, no inferences about defence, intelligence and national security accounts; build/tools/verify_dist.py checks the published copy again" + (f" (problems: {_d2})" if _d2 else ""))
else:
    _sec(True, "C-DIST-02", "government edition: never published to the public repository; build/tools/verify_dist.py refuses it there (C-DIST-02 negative test)")
_late = {r["id"] for r in REG} & SEC_LATE
need(_late == SEC_LATE, "C-DOC-01b", f"the security checks counted by C-DOC-01 were all registered (missing: {sorted(SEC_LATE - _late)})")
for r in REG:
    if r["id"] == "C-ALL": r["status"] = "pass" if all(x["status"] in ("pass", "live") for x in REG if x["id"] != "C-ALL") else "fail"
blob = json.dumps(data, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
tpl = open(os.path.join(S, "explorer71.tpl.html")).read()
assert tpl.count("/*__DATA__*/null") == 1 and tpl.count("/*__FONTS__*/") == 1
import base64
FD = os.path.join(V6, "fonts"); faces = []
for fam, fn, w, st in [("Atkinson Hyperlegible", "atkinson-hyperlegible-latin-400-normal", 400, "normal"), ("Atkinson Hyperlegible", "atkinson-hyperlegible-latin-400-italic", 400, "italic"), ("Atkinson Hyperlegible", "atkinson-hyperlegible-latin-700-normal", 700, "normal"),
                       ("Schibsted Grotesk", "schibsted-grotesk-latin-500-normal", 500, "normal"), ("Schibsted Grotesk", "schibsted-grotesk-latin-700-normal", 700, "normal"), ("Schibsted Grotesk", "schibsted-grotesk-latin-800-normal", 800, "normal"),
                       ("JetBrains Mono", "jetbrains-mono-latin-400-normal", 400, "normal"), ("JetBrains Mono", "jetbrains-mono-latin-600-normal", 600, "normal")]:
    b64 = base64.b64encode(open(os.path.join(FD, fn + ".woff2"), "rb").read()).decode()
    faces.append(f"@font-face{{font-family:'{fam}';font-style:{st};font-weight:{w};font-display:swap;src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
tpl = tpl.replace("/*__FONTS__*/", "\n".join(faces))
tpl = SEC["CSP_META"] + "\n" + tpl
assert not SEC["page_problems"](tpl), SEC["page_problems"](tpl)
assert "fonts.googleapis" not in tpl and "fonts.gstatic" not in tpl
OUTF = ("explorer71_public.html" if AUD == "public" else "explorer71_gov.html") if PUBLIC else "explorer71.html"   # the public repository publishes only the open edition (ADR 0004)
open(os.path.join(S, OUTF), "w").write(tpl.replace("/*__DATA__*/null", blob))
print("public" if PUBLIC else "private", "bytes", os.path.getsize(os.path.join(S, OUTF)), "xrows", len(XR), "spot", len(spot), "registry", len(REG), "fails", FAILS)
sys.exit(1 if FAILS else 0)
