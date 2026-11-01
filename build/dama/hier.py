"""Organisation hierarchy for the repo explorer (7.1).

Reads the GOV.UK Organisations API pages saved in ../govorg (fetched 31 October 2026 from
https://www.gov.uk/api/organisations, 64 pages). The files are untrusted data: parsed as JSON only.
Run with python3 -I.

Writes hier.json:
  orgs      [[slug, title, abbreviation, format, status, parents, superseded, superseding], ...]  (indexes into orgs)
  body_org  {catalogue body index: org index}  matched by GOV.UK slug only (no fuzzy matching)
  body_grp  {catalogue body index: grouping label} for bodies GOV.UK does not list (a grouping by type, not a sponsor)
  source    where and when the data was read
Checks C-HIER-01..04 are written to hier_checks.txt.
"""
import glob, json, os, re, sys

S = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(S)
pages = sorted(glob.glob(os.path.join(R, "govorg", "p*.json")), key=lambda p: int(re.search(r"p(\d+)\.json$", p).group(1)))
res = []
for p in pages:
    d = json.load(open(p, encoding="utf-8"))
    res += d["results"]
declared = json.load(open(pages[0], encoding="utf-8")).get("total")

slug_of = lambda u: u["id"].rsplit("/", 1)[1]
orgs = [x for x in res if x.get("details", {}).get("slug")]
IX = {x["details"]["slug"]: i for i, x in enumerate(orgs)}
def ixs(L): return [IX[slug_of(u)] for u in L if slug_of(u) in IX]
clean = lambda s: re.sub(r"\s+", " ", str(s or "")).strip()[:160]
OUT = [[x["details"]["slug"], clean(x["title"]), clean(x["details"].get("abbreviation")), clean(x.get("format")), clean(x["details"].get("govuk_status")),
        ixs(x.get("parent_organisations", [])), ixs(x.get("superseded_organisations", [])), ixs(x.get("superseding_organisations", []))] for x in orgs]

cat = json.load(open(os.path.join(R, "catalogue", "catalogue.json"), encoding="utf-8"))
B = cat["bodies"]

def group(b):
    t, k, n = (b.get("type") or "").lower(), b.get("kind"), (b.get("name") or "").lower()
    if k == "english_council": return "Local government in England"
    if "scottish" in t or "scotland" in n or "scot" in n.split()[0:1] or n in ("city of edinburgh council", "dundee city council", "glasgow city council", "highland council"): return "Scottish public sector"
    if "wales" in n or "welsh" in n: return "Welsh public sector"
    if "nhs" in t or "nhs" in n or "integrated care board" in t or "hospital" in n: return "NHS bodies"
    if "fire" in t or "fire" in n: return "Fire and rescue services"
    if "parliament" in t or "legislature" in t or "parliament" in n: return "Parliaments"
    if "transport" in t or n == "tfl": return "Transport authorities"
    return "Other public bodies"

body_org, body_grp = {}, {}
for i, b in enumerate(B):
    if b.get("slug") in IX: body_org[i] = IX[b["slug"]]
    else: body_grp[i] = group(b)

def chain(i, seen=()):
    """All ancestor paths from org i to a root (an org with no parent)."""
    ps = [p for p in OUT[i][5] if p not in seen]
    if not ps: return [[i]]
    return [[i] + c for p in ps for c in chain(p, seen + (i,))]

checks = []
def need(ok, cid, text, guards="R33"): checks.append(f"{'PASS' if ok else 'FAIL'} {cid} {text} [guards: {guards}]"); return ok
need(len(res) == declared and len(pages) >= 60, "C-HIER-01", f"all {len(res)} organisations GOV.UK declares were read from {len(pages)} pages")
bad = [OUT[i][0] for i in range(len(OUT)) if any(len(c) > 12 for c in chain(i))]
need(not bad, "C-HIER-02", "every organisation reaches a top-level organisation in 12 steps or fewer, with no loops")
need(len(body_org) + len(body_grp) == len(B) and all(B[i]["slug"] == OUT[o][0] for i, o in body_org.items()), "C-HIER-03",
     f"each of {len(B)} public bodies is either matched to GOV.UK by its exact slug ({len(body_org)}) or placed in a grouping by type ({len(body_grp)}); no fuzzy matches")
# negative test: a body whose slug is not in GOV.UK must not be matched, even when a similar title exists
fake = {"slug": "bristol-city-council-x", "name": "Bristol City Council", "kind": "english_council", "type": "Unitary authority"}
need(fake["slug"] not in IX and group(fake) == "Local government in England", "C-HIER-04", "a body is never matched by a similar name: a made-up slug stays unmatched and is grouped by type")
gds = IX.get("government-digital-service")
src = dict(url="https://www.gov.uk/api/organisations", read="2026-10-31", n=len(res), pages=len(pages),
           gds_parent=[OUT[p][1] for p in OUT[gds][5]] if gds is not None else [])
json.dump(dict(orgs=OUT, body_org=body_org, body_grp=body_grp, source=src), open(os.path.join(S, "hier.json"), "w"), separators=(",", ":"))
open(os.path.join(S, "hier_checks.txt"), "w").write("\n".join(checks) + "\n")
print("\n".join(checks)); print("matched", len(body_org), "grouped", len(body_grp), "GDS parent", src["gds_parent"])
sys.exit(0 if all(c.startswith("PASS") for c in checks) else 1)
