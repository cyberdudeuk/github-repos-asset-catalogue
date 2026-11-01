"""APIs and open data pipelines across the catalogue, and reconciliation with the government API catalogue (31 Oct 2026).
Inputs as classify.py, plus apicat/src/data/catalogue*.csv (co-cddo/api-catalogue, read as untrusted data).
Writes dama/apis.json, dama/opendata.json and dama/extra_checks.txt."""
import json, re, gzip, os, sys, csv, collections
H = os.path.dirname(os.path.abspath(__file__)); S = os.path.dirname(H); sys.path.insert(0, H)
from rules import w
ENR = f"{S}/xgov/enr"; DEPS = f"{H}/deps"; AC = f"{S}/apicat/src"
I = re.I
API_FILE = re.compile(r"(?:^|/)(?:openapi|swagger)[^/]*\.(?:ya?ml|json)$|\.oas\.ya?ml$|\.raml$|(?:^|/)asyncapi[^/]*\.ya?ml$|(?:^|/)public/api/conf/[^/]+/application\.(?:raml|ya?ml)$|(?:^|/)schema\.graphqls?$|\.graphqls$", I)
API_PUB = re.compile(r"(?:^|/)public/api/conf/[^/]+/application\.(?:raml|ya?ml)$", I)     # HMRC Developer Hub published API definition
API_DEP = re.compile(w(r"fastapi", r"flask-restx", r"flask-smorest", r"connexion", r"apispec", r"drf-spectacular", r"drf-yasg", r"djangorestframework", r"springdoc-openapi-starter-webmvc-ui", r"springdoc-openapi-ui", r"springfox-swagger2", r"swagger-ui-express", r"@nestjs/swagger", r"express-openapi-validator", r"openapi-backend", r"rswag", r"grape-swagger", r"apollo-server", r"@apollo/server", r"graphql-yoga", r"strawberry-graphql", r"graphene"), I)
API_NAME = re.compile(r"(?:^|[-_ ])api(?:s)?$|^api[-_]|\b(?:rest|graphql|public|open|web) api\b|\bapi (?:service|gateway|platform|specification|definitions?)\b", I)
CLIENT = re.compile(r"\b(?:api )?client\b|\bsdk\b|-client$|-sdk$", I)
OD = [  # id, label, text rule, dependency rule, path rule
 ("dgu", "data.gov.uk", w(r"data\.gov\.uk", r"datagovuk", r"find open data", r"ckanapi", r"ckan api"), w(r"ckanapi"), re.compile(r"(?:^|/)ckanext[^/]*/", I)),
 ("ndl", "National Data Library", w(r"national data library", r"ndl"), None, None),
 ("portal", "An organisation's own data portal", w(r"open ?data portal", r"open data ?store", r"data portal", r"opendatasoft", r"socrata", r"arcgis hub", r"datamill", r"london datastore", r"statistics\.gov\.(?:uk|scot|wales)", r"data\.[a-z]+\.gov\.uk", r"opendata\.[a-z.]+", r"open data (?:site|platform|service)"), w(r"sodapy", r"opendatasoft"), None)]
OPEN = re.compile(w(r"open data", r"opendata", r"open government licence data", r"published data(?:sets?)?", r"public datasets?"), I)
PUSH = re.compile(w(r"publish(?:es|ed|ing)?", r"upload(?:s|ed|ing)?", r"push(?:es|ed|ing)?", r"harvest(?:s|er|ed|ing)?", r"release(?:s|d)? (?:data|statistics)"), I)
PULL = re.compile(w(r"ingest(?:s|ed|ion|ing)?", r"download(?:s|ed|ing)?", r"scrap(?:e|es|er|ing)", r"fetch(?:es|ed|ing)?", r"consum(?:e|es|ed|ing)", r"pull(?:s|ed|ing)?", r"import(?:s|ed|ing)?"), I)
PIPE = re.compile(w(r"pipelines?", r"etl", r"elt", r"airflow", r"dagster", r"prefect", r"scheduled", r"cron", r"github actions?", r"workflow", r"automat(?:e|ed|es|ion)", r"routines?", r"scripts?"), I)
def snip(t, m): a = max(0, m.start() - 40); return re.sub(r"\s+", " ", t[a:m.end() + 40]).strip()[:110]
def tok(s): return {t for t in re.findall(r"[a-z0-9]+", s.lower()) if len(t) > 2 and t not in {"api", "apis", "the", "and", "for", "service", "services", "data", "gov", "government", "uk", "with", "from", "this", "that", "your", "rest", "public", "v1", "v2", "get", "lookup"}}
if __name__ == "__main__":
    D = json.load(open(f"{S}/uses/D5.json")); XO = D["xorgs"]
    recs = []
    for a in D["xrows"]:
        o = dict(zip(D["xf"], a)); recs.append((XO[o["oi"]]["org"], o["n"], " ".join(str(o.get(k) or "") for k in ("n", "d", "ld", "t")), o["oi"]))
    for a in D["cat"]:
        o = dict(zip(D["cf"], a)); recs.append((XO[o["oi"]]["org"], o["n"], " ".join(str(o.get(k) or "") for k in ("n", "d")), o["oi"]))
    apis = {}; od = {}
    for org, n, basic, oi in recs:
        key = f"{org}/{n}"; e = f"{ENR}/{org}__{n}"; readme = ""; paths = []; deps = []; wf = ""
        if os.path.isdir(e):
            try: readme = open(f"{e}/readme.txt", errors="replace").read()[:30000]
            except FileNotFoundError: pass
            try: paths = gzip.open(f"{e}/tree.gz", "rt", errors="replace").read().splitlines()
            except Exception: pass
            if os.path.isdir(f"{e}/wf"): paths_wf = [p for p in paths if p.startswith(".github/workflows/")]; wf = " ".join(paths_wf)
        dp = f"{DEPS}/{org}__{n}.json"
        if os.path.exists(dp): deps = [x[1] for x in json.load(open(dp))["deps"]]
        bas = basic.replace("-", " ").replace("_", " ") + " " + basic
        # APIs
        ev = []; files = [p for p in paths if API_FILE.search(p) and "node_modules/" not in p and "/test" not in p.lower()]
        if files: ev.append(["file", files[0][:110]])
        pub = [p for p in paths if API_PUB.search(p)]
        dhit = next((d for d in deps if API_DEP.fullmatch(d)), None)
        if dhit: ev.append(["dependency", dhit])
        if API_NAME.search(n) or API_NAME.search(basic[:300]): ev.append(["name", n])
        if ev:
            kind = "Published API definition" if pub else "API specification in the code" if files else "API framework in the code" if dhit else "Named as an API"
            if CLIENT.search(n) and not files: kind = "API client or SDK"
            apis[key] = {"kind": kind, "ev": ev, "nspec": len(files), "specs": files[:5]}
        # open data
        txt = bas + " " + readme[:12000]
        hits = []
        for oid, lab, t, d, p in OD:
            m = re.search(t, txt, I)
            if oid == "ndl" and m and not re.search(w(r"national data library"), txt, I) and not OPEN.search(txt): m = None   # bare 'NDL' only with an open data context
            evs = []
            if m: evs.append(["name" if re.search(t, bas, I) else "readme", snip(txt, m)])
            if d:
                dh = next((x for x in deps if re.fullmatch(d, x, I)), None)
                if dh: evs.append(["dependency", dh])
            if p:
                ph = next((x for x in paths if p.search(x)), None)
                if ph: evs.append(["file", ph[:110]])
            if evs: hits.append([oid, evs])
        if hits or OPEN.search(bas):
            om = OPEN.search(txt)
            direction = ("publishes" if PUSH.search(txt) else "") + ("|consumes" if PULL.search(txt) else "")
            pipe = bool(PIPE.search(txt)) or any(p.startswith(".github/workflows/") for p in paths) and bool(om)
            sched = any(re.search(r"schedule|cron", p, I) for p in paths if p.startswith(".github/workflows/"))
            if hits or (om and pipe):
                od[key] = {"portals": hits, "open": snip(txt, om) if om else "", "dir": direction.strip("|"), "pipe": pipe, "wf": len([p for p in paths if p.startswith(".github/workflows/")])}
    # government API catalogue reconciliation
    cat = []
    for f in ("catalogue.csv", "catalogue-from-json-source.csv"):
        for r in csv.DictReader(open(f"{AC}/data/{f}", encoding="utf-8", errors="replace")):
            cat.append({k: r.get(k, "") for k in ("name", "description", "url", "documentation", "provider", "dateAdded", "dateUpdated")} | {"src": f})
    seen = set(); uniq = []
    for c in cat:
        k = (c["name"].strip().lower(), c["url"].strip().lower())
        if k in seen: continue
        seen.add(k); uniq.append(c)
    orgcsv = {r["id"]: r for r in csv.DictReader(open(f"{AC}/data/organisation.csv", encoding="utf-8", errors="replace"))}
    allkeys = {f"{XO[dict(zip(D['xf'], a))['oi']]['org']}/{dict(zip(D['xf'], a))['n']}".lower(): f"{XO[dict(zip(D['xf'], a))['oi']]['org']}/{dict(zip(D['xf'], a))['n']}" for a in D["xrows"]}
    allkeys.update({f"{XO[dict(zip(D['cf'], a))['oi']]['org']}/{dict(zip(D['cf'], a))['n']}".lower(): f"{XO[dict(zip(D['cf'], a))['oi']]['org']}/{dict(zip(D['cf'], a))['n']}" for a in D["cat"]})
    orgs_of = collections.defaultdict(set)   # provider text -> catalogue accounts, through public body names, abbreviations and slugs
    bodies = D["bodies"]
    for c in uniq:
        o = orgcsv.get(c["provider"]); names = {c["provider"].lower().replace("-", " ").strip()} | ({o["name"].lower(), (o.get("alternateName") or "").lower()} - {""} if o else set())
        for p in names:
          for b in bodies:
            nm = b["name"].lower(); ab = re.search(r"\(([^)]+)\)", b["name"]); ab = ab.group(1).lower() if ab else ""
            if p and (p == nm or (len(p) >= 8 and p in nm) or nm.split(" (")[0] == p or (ab and (p == ab or p.split()[-1:] == [ab]))): orgs_of[c["provider"]] |= set(b["accounts"])
    api_keys = list(apis)
    for c in uniq:
        link = re.search(r"github\.com/([^/\s]+)/([^/\s#?]+)", c["url"] + " " + c["documentation"], I)
        best = None
        if link:
            k = f"{link.group(1)}/{link.group(2).removesuffix('.git')}"
            kk = allkeys.get(k.lower())
            if kk: best = [kk, 1.0, "linked from the catalogue entry" + ("" if kk in apis else "; no API evidence found in the repository")]
        if not best:
            accts = orgs_of.get(c["provider"], set()); at = tok(c["name"])
            if accts and at:
                sc = []
                for k in api_keys:
                    if k.split("/")[0] in accts:
                        rt = tok(k.split("/")[1])
                        if rt:
                            if len(at) == 1 and rt != at: continue   # a one-word API name only matches a repository named the same (V7-4)
                            j = len(at & rt) / len(at | rt); sc.append((j, k))
                sc.sort(reverse=True)
                if sc and sc[0][0] >= .5: best = [sc[0][1], round(sc[0][0], 2), "same organisation, similar name"]
                elif sc and sc[0][0] >= .25: best = [sc[0][1], round(sc[0][0], 2), "possible: same organisation, partly similar name"]
        c["match"] = best; c["accounts"] = sorted(orgs_of.get(c["provider"], set()))
    json.dump({"apis": apis, "catalogue": uniq, "catalogue_source": {"repo": "co-cddo/api-catalogue", "commit": os.popen(f"git -C {AC} log -1 --format=%H").read().strip(), "date": os.popen(f"git -C {AC} log -1 --format=%cs").read().strip(), "files": ["data/catalogue.csv", "data/catalogue-from-json-source.csv"]}}, open(f"{H}/apis.json", "w"))
    json.dump(od, open(f"{H}/opendata.json", "w"))
    m = [c for c in uniq if c["match"]]; strong = [c for c in m if c["match"][1] >= .5]
    lines = []
    def ck(cid, ok, text, g=""): lines.append(f"{'PASS' if ok else 'FAIL'} {cid} {text}" + (f" [guards: {g}]" if g else ""))
    ck("C-API-01", len(uniq) >= max(collections.Counter(c["src"] for c in cat).values()) and len(uniq) <= len(cat) and all(c["name"] for c in uniq), f"{len(uniq)} unique government API catalogue entries read from co-cddo/api-catalogue (duplicates across its two files removed)", "V7-3")
    ck("C-API-02", all(c["match"] is None or (c["match"][0] in apis or (c["match"][2].startswith("linked") and c["match"][0].lower() in allkeys)) for c in uniq), "every name-based match points at a repository the API rules found; links from the catalogue point at a catalogue record", "V7-3")
    ck("C-API-03", not any(c["match"] and c["match"][1] < .25 for c in uniq), "no match below the 0.25 name-similarity floor is reported", "V7-3")
    neg = tok("Address Lookup API") & tok("address-lookup-frontend")
    ck("C-API-05", not any(c["match"] and not c["match"][2].startswith("linked") and len(tok(c["name"])) == 1 and tok(c["match"][0].split("/")[1]) != tok(c["name"]) for c in uniq), "a one-word API name (such as 'Pay') only matches a repository with the same name, never a longer one such as pay-webhooks", "V7-4")
    PORTAL = OD[2][2]
    ck("C-OD-01", not re.search(PORTAL, "stored in a datastore so the agent can", I) and not re.search(PORTAL, "roles/datastore.user", I) and re.search(PORTAL, "publishes to the London Datastore", I), "a generic 'datastore' (a database) isn't an open data portal; the London Datastore still is (negative and positive tests)", "V7-5")
    ck("C-API-04", tok("GOV.UK Notify API") == {"notify"} and "api" not in neg, "name similarity ignores generic words such as API, service and data (negative test: they never create a match)", "V7-3")
    open(f"{H}/extra_checks.txt", "w").write("\n".join(lines) + "\n")
    kinds = collections.Counter(a["kind"] for a in apis.values())
    print("\n".join(lines)); print("api repos", len(apis), dict(kinds)); print("catalogue", len(uniq), "matched", len(m), "strong", len(strong), "providers mapped", sum(1 for c in uniq if c["accounts"]))
    print("open data repos", len(od), collections.Counter(p[0] for v in od.values() for p in v["portals"]), "with pipeline", sum(v["pipe"] for v in od.values()))
