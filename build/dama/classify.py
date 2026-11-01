"""Classify every catalogue record against the DAMA rules. Evidence per match: where it was found and the matched text.
Inputs: D5.json (catalogue), xgov/enr/<org>__<repo>/{tree.gz, readme.txt}, dama/deps/<org>__<repo>.json (parsed manifests, optional).
Untrusted inputs are only read as text and matched; nothing from a repository is executed."""
import json, re, gzip, os, sys, collections
H = os.path.dirname(os.path.abspath(__file__)); S = os.path.dirname(H); sys.path.insert(0, H)
from rules import AREAS, LIFECYCLE, VENDORS, TERRAFORM, NAME_ONLY
TF = [(re.compile(r), cap, v) for r, cap, v in TERRAFORM]
ENR = f"{S}/xgov/enr"; DEPS = f"{H}/deps"
AMBIG = {"validate": "r", "targets": "r", "drake": "r", "shiny": "r", "shinydashboard": "r", "flexdashboard": "r", "skimr": "r", "assertr": "r", "pointblank": "r", "summarytools": "r", "dataexplorer": "r", "janitor": "r", "synthpop": "r", "sdcmicro": "r", "fastlink": "r", "bigrquery": "r", "rsdmx": "r",
         "dash": "py", "panel": "py", "voila": "py", "faker": "py", "mimesis": "py", "polars": "py", "duckdb": "py", "kedro": "py", "luigi": "py", "prefect": "py", "dedupe": "py", "evidently": "py", "frictionless": "py", "datapackage": "py", "sdv": "py", "arx": "jvm", "jena": "jvm"}
C = lambda rx: re.compile(rx, re.I) if rx else None
CAPS = [(a[0], c[0], C(c[2]), C(c[3]), C(c[4])) for a in AREAS for c in a[4]]
VEND = [(v[0], C(v[5]), C(v[6]), C(v[7])) for v in VENDORS]
LC = [(l[0], C(l[2])) for l in LIFECYCLE]
def dep_ok(rx, deps):
    for eco, name in deps:
        m = rx.fullmatch(name) if rx else None
        if m and (AMBIG.get(name.lower()) in (None, eco)): return name
    return None
def snip(text, m): a = max(0, m.start() - 40); return re.sub(r"\s+", " ", text[a:m.end() + 40]).strip()
def classify(basic, readme, paths, deps, tf=()):
    out = {"caps": {}, "vend": {}, "life": []}
    for area, cap, t, p, d in CAPS:
        ev = []
        if t:
            m = t.search(basic)
            if m: ev.append(["name", snip(basic, m)])
            elif readme and cap not in NAME_ONLY:
                m = t.search(readme)
                if m: ev.append(["readme", snip(readme, m)])
        if p:
            hit = next((x for x in paths if p.search(x)), None)
            if hit: ev.append(["file", hit[:120]])
        if d:
            hit = dep_ok(d, deps)
            if hit: ev.append(["dependency", hit])
        if ev: out["caps"][cap] = ev
    for vid, t, p, d in VEND:
        ev = []
        if t:
            m = t.search(basic) or (t.search(readme) if readme else None)
            if m: ev.append(["name" if t.search(basic) else "readme", snip(basic if t.search(basic) else readme, m)])
        if p:
            hit = next((x for x in paths if p.search(x)), None)
            if hit: ev.append(["file", hit[:120]])
        if d:
            hit = dep_ok(d, deps)
            if hit: ev.append(["dependency", hit])
        if ev: out["vend"][vid] = ev
    for rx, cap, v in TF:
        hit = next((x for x in tf if rx.search(x)), None)
        if hit:
            out["caps"].setdefault(cap, []).append(["infrastructure", hit])
            if v: out["vend"].setdefault(v, []).append(["infrastructure", hit])
    txt = basic + " " + (readme or "")[:4000]
    out["life"] = [lid for lid, rx in LC if rx.search(txt)]
    return out
if __name__ == "__main__":
    D = json.load(open(f"{S}/uses/D5.json")); XO = D["xorgs"]
    recs = []
    for a in D["xrows"]:
        o = dict(zip(D["xf"], a)); recs.append((XO[o["oi"]]["org"], o["n"], " ".join(str(o.get(k) or "") for k in ("n", "d", "ld", "t"))))
    for a in D["cat"]:
        o = dict(zip(D["cf"], a)); recs.append((XO[o["oi"]]["org"], o["n"], " ".join(str(o.get(k) or "") for k in ("n", "d"))))
    res = {}; stats = collections.Counter()
    for org, n, basic in recs:
        key = f"{org}/{n}"; e = f"{ENR}/{org}__{n}"; readme = ""; paths = []; deps = []
        if os.path.isdir(e):
            try: readme = open(f"{e}/readme.txt", errors="replace").read()[:30000]
            except FileNotFoundError: pass
            try: paths = gzip.open(f"{e}/tree.gz", "rt", errors="replace").read().splitlines()
            except Exception: pass
        dp = f"{DEPS}/{org}__{n}.json"
        tf = []
        if os.path.exists(dp): j = json.load(open(dp)); deps = [tuple(x) for x in j["deps"]]; tf = j.get("tf", [])
        basic = basic.replace("-", " ").replace("_", " ") + " " + basic
        r = classify(basic, readme, paths, deps, tf)
        if r["caps"] or r["vend"]: res[key] = r
        stats["readme"] += bool(readme); stats["tree"] += bool(paths); stats["deps"] += bool(deps)
    json.dump(res, open(f"{H}/classified.json", "w"))
    print(len(recs), "records;", len(res), "with any match;", dict(stats))
    ac = collections.Counter(); cc = collections.Counter(); vc = collections.Counter(); kinds = collections.Counter()
    for k, r in res.items():
        for a in {c.split("-")[0] for c in r["caps"]}: ac[a] += 1
        for c, ev in r["caps"].items(): cc[c] += 1; kinds[(c.split("-")[0], max(ev, key=lambda e: ["name","readme","file","infrastructure","dependency"].index(e[0]))[0])] += 1
        for v in r["vend"]: vc[v] += 1
    print("areas", ac.most_common()); print("caps", cc.most_common()); print("vendors", vc.most_common())
