"""Boundaries for the catalogue's maps (RM-08).

  python3 -I build/geo/geo.py              build geo.json from the stored boundaries
  python3 -I build/geo/geo.py --fetch      read the boundaries again from the ONS Open Geography Portal first
  python3 -I build/geo/geo.py --self-test

Source: Office for National Statistics, Open Geography Portal, ultra generalised (BUC) boundaries, in British National Grid:
  Countries (December 2025), Counties and Unitary Authorities (December 2025), Local Authority Districts (May 2026, centres only).
Each was simplified again on the server (to 1,500 m for countries, 800 m for the others), which is enough for a map a page wide
and keeps the page small. Contains public sector information licensed under the Open Government Licence v3.0. Source: Office for
National Statistics licensed under the Open Government Licence v3.0. Contains OS data © Crown copyright and database right 2026.

Council accounts are placed by an explicit table, one line each, naming the area exactly as ONS spells it: a county or unitary
authority is drawn as its area; a district council as a point at its district's centre. A body whose area covers several
councils (fire and rescue services) or that no longer has an area (an abolished council) is listed with the reason and not drawn.
Writes geo.json, with every check's result in geo_checks.txt.
"""
import hashlib
import json
import os
import sys
import time
import urllib.request

H = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(H, "sources")
BASE = "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services"
LAYERS = {
    "ctry": ("Countries_December_2025_Boundaries_UK_BUC", "CTRY25CD", "CTRY25NM", 1500),
    "ctyua": ("Counties_and_Unitary_Authorities_December_2025_Boundaries_UK_BUC", "CTYUA25CD", "CTYUA25NM", 800),
    "lad": ("Local_Authority_Districts_May_2026_Boundaries_UK_BUC", "LAD26CD", "LAD26NM", 800),
}
TOP = 1230000   # northings above this are off the map (none are: Shetland's tip is about 1,220 km)
# account -> (layer, area name as ONS spells it), or (None, reason it isn't drawn)
ACCOUNTS = {
    "BathnesDevelopment": ("ctyua", "Bath and North East Somerset"), "BracknellForestCouncil": ("ctyua", "Bracknell Forest"),
    "brighton-hove-gov-uk": ("ctyua", "Brighton and Hove"), "BristolCityCouncil": ("ctyua", "Bristol, City of"), "CamdenCouncil": ("ctyua", "Camden"),
    "cityofyork": ("ctyua", "York"), "coventry-city-council": ("ctyua", "Coventry"), "devoncc": ("ctyua", "Devon"), "DevonCountyCouncil": ("ctyua", "Devon"),
    "Dorset-Council-UK": ("ctyua", "Dorset"), "DundeeCityCouncil": ("ctyua", "Dundee City"), "east-sussex-county-council": ("ctyua", "East Sussex"),
    "edinburghcouncil": ("ctyua", "City of Edinburgh"), "essexcountycouncil": ("ctyua", "Essex"), "Falkirk-Council": ("ctyua", "Falkirk"),
    "HfdsCouncil": ("ctyua", "Herefordshire, County of"), "hull-city-council": ("ctyua", "Kingston upon Hull, City of"), "kentcc": ("ctyua", "Kent"),
    "KLBC-WebTeam": ("lad", "King's Lynn and West Norfolk"), "LambethCouncil": ("ctyua", "Lambeth"), "LBHackney-IT": ("ctyua", "Hackney"),
    "LBHounslow": ("ctyua", "Hounslow"), "lichfield-district-council": ("lad", "Lichfield"), "LiverpoolCityCouncil": ("ctyua", "Liverpool"),
    "LondonBoroughOfBexley": ("ctyua", "Bexley"), "LondonBoroughSutton": ("ctyua", "Sutton"), "LutonCouncil": ("ctyua", "Luton"),
    "openglasgow": ("ctyua", "Glasgow City"), "OxfordshireCountyCouncil": ("ctyua", "Oxfordshire"), "Reading-Borough-Council": ("ctyua", "Reading"),
    "rothgov": ("ctyua", "Rotherham"), "RoyalBoroughKingston": ("ctyua", "Kingston upon Thames"), "rushmoor": ("lad", "Rushmoor"),
    "smbc-digital": ("ctyua", "Stockport"), "surreydigitalservices": ("ctyua", "Surrey"), "thehighlandcouncil": ("ctyua", "Highland"),
    "TraffordCouncil": ("ctyua", "Trafford"), "warwickshire": ("ctyua", "Warwickshire"), "wealden": ("lad", "Wealden"),
    "west-berkshire-council": ("ctyua", "West Berkshire"), "wfcouncil": ("ctyua", "Waltham Forest"),
    "northamptonshire-county-council": (None, "The council was abolished in April 2021; its area is now North and West Northamptonshire."),
    "gmfrs": (None, "A fire and rescue service covering ten councils."), "ukfrs-hertsfrs": (None, "A fire and rescue service covering a county's ten districts."),
    "wmfs": (None, "A fire and rescue service covering seven councils."), "ukfrs-CDDFRS": (None, "A fire and rescue service covering two councils."),
    "LocalGovDrupal": (None, "A shared project of many councils, not one council."),
}


# strategic authorities (R85): each drawn as the union of its member councils' county and unitary areas, so authorities set up in
# 2026, after ONS's December 2025 edition, and London are drawn the same way. Names that differ from ONS's are mapped here.
ALIAS = {"St Helens": "St. Helens", "Bristol": "Bristol, City of", "Hull": "Kingston upon Hull, City of"}
INSIDE = {"Cambridge": "Cambridgeshire", "East Cambridgeshire": "Cambridgeshire", "Fenland": "Cambridgeshire", "Huntingdonshire": "Cambridgeshire",
          "South Cambridgeshire": "Cambridgeshire"}   # districts, drawn by the county they sit in
LONDON = "The 32 London boroughs and the City of London (area)"
ONS_CAUTH = {"Cambridgeshire and Peterborough": "cpca", "Devon and Torbay": "dtcca", "East Midlands": "emcca", "Greater Lincolnshire": "glcca",
             "Greater Manchester": "gmca", "Hull and East Yorkshire": "heyca", "Lancashire": "lancca", "Liverpool City Region": "lcr", "North East": "nema",
             "South Yorkshire": "symca", "Tees Valley": "tvca", "West Midlands": "wmca", "West Yorkshire": "wyca", "West of England": "weca", "York and North Yorkshire": "ynyca"}


def authority_areas(auths, ctyua):
    """{authority id: [county or unitary codes]}, and the member names that resolve to no area."""
    by = {n: c for c, n in ctyua}; out, bad = {}, []
    for a in auths:
        codes = []
        for m in a["constituents"]:
            if m == LONDON: codes += [c for c, n in ctyua if c.startswith("E09")]; continue
            n = ALIAS.get(m, INSIDE.get(m, m))
            if n in by: codes.append(by[n])
            else: bad.append(f"{a['id']}: {m}")
        out[a["id"]] = sorted(set(codes))
    return out, bad


def fetch():
    m = {}
    for k, (svc, _, _, off) in LAYERS.items():
        q = f"where=1%3D1&outFields=*&outSR=27700&f=geojson&geometryPrecision=0&maxAllowableOffset={off}&resultRecordCount=2000"
        url = f"{BASE}/{svc}/FeatureServer/0/query?{q}"
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "github-repos-asset-catalogue-maps"}), timeout=300) as r: b = r.read()
        open(os.path.join(SRC, f"{k}.geojson"), "wb").write(b)
        m[k] = dict(service=svc, read=time.strftime("%Y-%m-%d"), simplified_m=off, sha256=hashlib.sha256(b).hexdigest())
        print(k, len(json.loads(b)["features"]), "features", flush=True)
    url = f"{BASE}/Combined_Authorities_December_2025_Boundaries_EN_BUC/FeatureServer/0/query?where=1%3D1&outFields=*&returnGeometry=false&f=json"
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "github-repos-asset-catalogue-maps"}), timeout=300) as r: b = r.read()
    open(os.path.join(SRC, "cauth_names.json"), "wb").write(b)
    m["cauth_names"] = dict(service="Combined_Authorities_December_2025_Boundaries_EN_BUC (names only)", read=time.strftime("%Y-%m-%d"), sha256=hashlib.sha256(b).hexdigest())
    json.dump(m, open(os.path.join(SRC, "manifest.json"), "w"), indent=1)


def ring_path(ring):
    """A ring in metres as an SVG path in kilometres, with repeated points dropped; None if fewer than three remain."""
    pts = []
    for e, n in ring:
        p = (round(e / 1000), round((TOP - n) / 1000))
        if not pts or p != pts[-1]: pts.append(p)
    if len(pts) > 1 and pts[0] == pts[-1]: pts.pop()
    if len(pts) < 3: return None
    return "M" + " ".join(f"{x} {y}" for x, y in pts) + "Z"


def geom_path(g):
    polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
    return "".join(p for poly in polys for p in (ring_path(r) for r in poly) if p)


def load(k):
    _, code, name, _ = LAYERS[k]
    return [(f["properties"][code], f["properties"][name], f) for f in json.load(open(os.path.join(SRC, f"{k}.geojson")))["features"]]


def place(accounts, ctyua_names, lad_names):
    """Resolve the table: every drawn account names exactly one area in its layer. Returns (placed, problems)."""
    placed, bad = {}, []
    for acc, (layer, area) in accounts.items():
        if layer is None: continue
        pool = ctyua_names if layer == "ctyua" else lad_names
        hits = [c for c, n in pool if n == area]
        if len(hits) != 1: bad.append(f"{acc}: {area!r} names {len(hits)} areas in {layer}")
        else: placed[acc] = [layer, hits[0]]
    return placed, bad


def self_test():
    bad = []
    pool = [("E1", "Devon"), ("E2", "Kent")]
    if place({"x": ("ctyua", "Devon")}, pool, [])[1]: bad.append("a name that exists was refused")
    if not place({"x": ("ctyua", "Devonshire")}, pool, [])[1]: bad.append("a misspelt area was accepted")
    if not place({"x": ("ctyua", "Devon")}, pool + [("E3", "Devon")], [])[1]: bad.append("a name matching two areas was accepted")
    if ring_path([[0, TOP], [400, TOP], [0, TOP]]) is not None: bad.append("a ring that collapses to a point was drawn")
    return bad


def main():
    if "--self-test" in sys.argv:
        b = self_test(); print("ok" if not b else b); return 1 if b else 0
    if "--fetch" in sys.argv: fetch()
    checks = []
    def check(ok, cid, msg, guards): checks.append(("PASS " if ok else "FAIL ") + f"{cid} {msg}   [guards: {guards}]")
    man = json.load(open(os.path.join(SRC, "manifest.json")))
    ok_sha = all(hashlib.sha256(open(os.path.join(SRC, f"{k}.geojson"), "rb").read()).hexdigest() == man[k]["sha256"] for k in LAYERS) and hashlib.sha256(open(os.path.join(SRC, "cauth_names.json"), "rb").read()).hexdigest() == man.get("cauth_names", {}).get("sha256")
    check(ok_sha, "C-GEO-01", "each stored boundary file is the one read from the ONS Open Geography Portal (SHA-256 in sources/manifest.json)", "RM-08")
    ctry, ctyua, lad = load("ctry"), load("ctyua"), load("lad")
    out_ctry = [[c, n, geom_path(f["geometry"])] for c, n, f in ctry]
    out_area = [[c, n, geom_path(f["geometry"])] for c, n, f in ctyua]
    out_lad = {c: [n, round(f["properties"]["BNG_E"] / 1000), round((TOP - f["properties"]["BNG_N"]) / 1000)] for c, n, f in lad}
    check(len(out_ctry) == 4 and all(p for _, _, p in out_ctry) and len(out_area) == 218 and all(p for _, _, p in out_area), "C-GEO-02",
          f"4 countries and {len(out_area)} counties and unitary authorities, every one drawn", "RM-08")
    placed, bad = place(ACCOUNTS, [(c, n) for c, n, _ in ctyua], [(c, n) for c, n, _ in lad])
    st = self_test()
    check(not bad and not st, "C-GEO-03", f"every council account in the table names exactly one ONS area ({len(placed)} placed, "
          f"{sum(1 for v in ACCOUNTS.values() if v[0] is None)} listed with the reason they aren't drawn; problems: {bad}); negative tests "
          f"{'catch' if not st else 'MISS'} a misspelt area, a name matching two areas and a ring that collapses", "RM-08")
    DV = json.load(open(os.path.join(os.path.dirname(H), "dama", "devolution.json")))
    areas, unresolved = authority_areas(DV["authorities"], [(c, n) for c, n, _ in ctyua])
    london = len(areas.get("gla", []))
    neg = authority_areas([dict(id="x", constituents=["Atlantis"])], [(c, n) for c, n, _ in ctyua])[1]
    check(not unresolved and london == 33 and all(areas.values()) and neg, "C-GEO-05", f"every one of the {len(areas)} strategic authorities is drawn from its member councils' areas "
          f"(London: {london} areas; members that resolve to no area: {unresolved}); negative test {'catches' if neg else 'MISSES'} an unknown member", "R85")
    names = [f["attributes"]["CAUTH25NM"] for f in json.load(open(os.path.join(SRC, "cauth_names.json")))["features"]]
    missing = [n for n in names if ONS_CAUTH.get(n) not in areas]
    check(not missing and len(names) == 15, "C-GEO-06", f"every one of ONS's {len(names)} combined authorities (December 2025) is one of the catalogue's strategic authorities (missing: {missing})", "R85")
    out = dict(source="https://geoportal.statistics.gov.uk/", read=man["ctry"]["read"], editions=dict(ctry="December 2025", ctyua="December 2025", lad="May 2026"),
               simplified_m={k: v["simplified_m"] for k, v in man.items() if "simplified_m" in v},
               attribution="Source: Office for National Statistics licensed under the Open Government Licence v3.0. Contains OS data © Crown copyright and database right 2026.",
               units="km on the British National Grid, y measured down from 1,230 km north", ctry=out_ctry, ctyua=out_area,
               lad={c: out_lad[c] for _, (layer, c) in placed.items() if layer == "lad"}, accounts=placed, authorities=areas,
               not_drawn={a: r for a, (layer, r) in ACCOUNTS.items() if layer is None})
    s = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
    check(len(s) < 400_000, "C-GEO-04", f"the map data adds {len(s):,} bytes to the page (limit 400,000)", "page size")
    open(os.path.join(H, "geo.json"), "w").write(s)
    open(os.path.join(H, "geo_checks.txt"), "w").write("\n".join(checks) + "\n")
    print("\n".join(checks))
    return 0 if all(c.startswith("PASS") for c in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
