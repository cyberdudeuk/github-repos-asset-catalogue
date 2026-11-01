"""Organisation crosswalk for govukOS: GTI and ANA organisation ids -> GOV.UK organisation slugs (7.1).

Inputs (data only, run with python3 -I):
  ../govorg/app_org_ids.json   tables copied verbatim from GTI and ANA on 31 October 2026
  hier.json                    GOV.UK's organisations list (1,271 organisations, read 31 October 2026)
Rules, strictest first; nothing is matched by similarity:
  1. the app's own table names a slug, and GOV.UK has it           -> "app table, confirmed by GOV.UK"
  2. the app's own table names a slug GOV.UK doesn't have           -> kept, flagged "app table, not on GOV.UK"
  3. no table entry: the organisation's name equals a GOV.UK title  -> "exact name match on GOV.UK"
     (after removing case, punctuation, a leading 'the' and a trailing '(abbreviation)'; '&' read as 'and')
  4. otherwise unresolved, with the reason
Writes crosswalk.json and crosswalk_checks.txt.
"""
import json, os, re

S = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(S)
A = json.load(open(os.path.join(R, "govorg", "app_org_ids.json"), encoding="utf-8"))
H = json.load(open(os.path.join(S, "hier.json"), encoding="utf-8"))
ORGS = H["orgs"]; SLUG = {o[0]: o for o in ORGS}
def norm(s):
    s = str(s or "").lower().replace("&", " and ")
    s = re.sub(r"\([^)]*\)\s*$", "", s); s = re.sub(r"^the\s+", "", s.strip())
    return re.sub(r"[^a-z0-9]+", "", s)
TITLE = {}
for o in ORGS:
    TITLE.setdefault(norm(o[1]), []).append(o[0])
ABBR = {}
for o in ORGS:
    if o[2] and o[4] != "closed": ABBR.setdefault(re.sub(r"[^a-z0-9]", "", o[2].lower()), []).append(o[0])
def by_name(name):
    c = TITLE.get(norm(name), []) or (ABBR.get(re.sub(r"[^a-z0-9]", "", str(name or "").lower()), []) if re.fullmatch(r"[A-Z][A-Za-z&]{1,9}", str(name or "").strip()) else [])
    live = [s for s in c if SLUG[s][4] != "closed"]
    return (live or c)[0] if len(live or c) == 1 else None, len(live or c)

rows = []
# Resolved by hand, each checked against GOV.UK's list on 31 October 2026. Every entry gives its reason.
MANUAL = {
 ("ANA", "fcdo"): ("foreign-commonwealth-development-office", "ANA's name drops 'Office'; GOV.UK title is 'Foreign, Commonwealth & Development Office'"),
 ("ANA", "dcms"): ("department-for-digital-culture-media-and-sport", "GOV.UK closed department-for-culture-media-and-sport; its successor is the Department for Digital, Culture, Media and Sport"),
 ("GTI", "dcms"): ("department-for-digital-culture-media-and-sport", "as for ANA dcms: the closed DCMS's GOV.UK successor"),
 ("GTI", "fcdo"): ("foreign-commonwealth-development-office", "as for ANA fcdo"),
 ("GTI", "cicreg"): ("office-of-the-regulator-of-community-interest-companies", "GOV.UK title is 'Office of the Regulator of Community Interest Companies'"),
}
NOT_GOVUK = {"parliament": "Parliament is not a GOV.UK organisation", "judiciary": "covers two GOV.UK organisations, HM Courts & Tribunals Service and the Judicial Office, so no single slug is right",
  "gro": "not a GOV.UK organisation; the General Register Office sits within HM Passport Office", "enic": "not a GOV.UK organisation; run under contract for the Department for Education",
  "fr": "not a public body on GOV.UK (independent regulator)", "gassafe": "not a public body on GOV.UK (scheme run under contract)", "dps": "not a public body on GOV.UK (government-approved schemes)",
  "la": "a role, not one organisation", "ts": "a local authority service, not one organisation", "eauditor": "a role, not one organisation"}
def add(app, table, oid, name, slugs):
    m = MANUAL.get((app, oid))
    if m and m[0] in SLUG: rows.append(dict(app=app, table=table, id=oid, name=name, govuk_slug=m[0], also=[], method="resolved by hand, confirmed by GOV.UK", reason=m[1], status=SLUG[m[0]][4])); return
    if oid in NOT_GOVUK and not (slugs if isinstance(slugs, list) else slugs): rows.append(dict(app=app, table=table, id=oid, name=name, govuk_slug=None, also=[], method="not a GOV.UK organisation", reason=NOT_GOVUK[oid], status=None)); return
    slugs = [s for s in (slugs if isinstance(slugs, list) else [slugs] if slugs else []) if s]
    if slugs:
        ok = [s for s in slugs if s in SLUG]
        if ok:
            rows.append(dict(app=app, table=table, id=oid, name=name, govuk_slug=ok[0], also=ok[1:], method="app table, confirmed by GOV.UK", status=SLUG[ok[0]][4])); return
        s2, n2 = by_name(name) if name else (None, 0)
        if s2: rows.append(dict(app=app, table=table, id=oid, name=name, govuk_slug=s2, also=[], method="app's slug wrong; exact name match on GOV.UK", given=slugs, status=SLUG[s2][4])); return
        rows.append(dict(app=app, table=table, id=oid, name=name, govuk_slug=None, also=[], method="app table, not on GOV.UK", given=slugs, status=None, reason="the app's slug isn't on GOV.UK and no GOV.UK organisation has this exact name")); return
    s, n = by_name(name) if name else (None, 0)
    if s and not slugs: rows.append(dict(app=app, table=table, id=oid, name=name, govuk_slug=s, also=[], method="exact name match on GOV.UK", status=SLUG[s][4])); return
    if not slugs: rows.append(dict(app=app, table=table, id=oid, name=name, govuk_slug=None, also=[], method="unresolved", reason=("no GOV.UK organisation has this exact name" if n == 0 else f"{n} GOV.UK organisations share this name") if name else "no name given", status=None))

g = A.get("gti") or {}; a = A.get("ana") or {}
names_gti = g.get("bodies") or {}
for oid, slugs in (g.get("gk_org") or {}).items(): add("GTI", "GK_ORG", oid, names_gti.get(oid), slugs)
for oid, nm in (names_gti or {}).items():
    if oid not in (g.get("gk_org") or {}): add("GTI", "bodies", oid, nm, None)
ana_slug = a.get("slug") or {}
ana_names = {d.get("id"): d.get("name") for d in (a.get("depts") or [])}
for d in a.get("depts") or []: add("ANA", "DEPTS", d.get("id"), d.get("name"), ana_slug.get(d.get("id")))
for b in a.get("albs") or []: add("ANA", "arm's-length bodies", b.get("id"), b.get("name"), b.get("id"))
for key, val in (g.get("ana1_org") or {}).items():
    nm = val if isinstance(val, str) else (val or {}).get("name") if isinstance(val, dict) else None
    add("GTI", "ANA1_ORG (estate from ANA 1.0)", key, nm or ana_names.get(key), ana_slug.get(key))

checks = []
def need(ok, cid, text, guards="R35"): checks.append(f"{'PASS' if ok else 'FAIL'} {cid} {text} [guards: {guards}]"); return ok
need(all(r["govuk_slug"] is None or r["govuk_slug"] in SLUG for r in rows), "C-XW-01", f"every one of {sum(1 for r in rows if r['govuk_slug'])} mapped organisation ids points at an organisation in GOV.UK's list")
s1, _ = by_name("Department for Transportation"); s2, _ = by_name("The Department for Transport"); s3, _ = by_name("HM Revenue and Customs (HMRC)")
need(s1 is None and s2 == "department-for-transport" and s3 == "hm-revenue-customs", "C-XW-02", "names match only exactly: 'Department for Transportation' finds nothing, while 'The Department for Transport' and 'HM Revenue and Customs (HMRC)' find their GOV.UK slugs (negative test)")
need(all(r["method"] in ("app table, confirmed by GOV.UK", "app table, not on GOV.UK", "exact name match on GOV.UK", "unresolved", "resolved by hand, confirmed by GOV.UK", "app's slug wrong; exact name match on GOV.UK", "not a GOV.UK organisation") and (r["govuk_slug"] or r.get("reason")) for r in rows), "C-XW-03", "every crosswalk row says how it was matched, or gives the reason it has no GOV.UK slug")
summ = {}
for r in rows: summ.setdefault(r["app"] + " " + r["table"], {}).setdefault(r["method"], 0); summ[r["app"] + " " + r["table"]][r["method"]] += 1
json.dump(dict(rows=rows, summary=summ, source=dict(apps="GTI and ANA tables copied verbatim on 31 October 2026", govuk=H["source"])), open(os.path.join(S, "crosswalk.json"), "w"), indent=0)
open(os.path.join(S, "crosswalk_checks.txt"), "w").write("\n".join(checks) + "\n")
print("\n".join(checks)); print(json.dumps(summ, indent=1))
