"""Grade data catalogue platforms and metadata/open standards per repository and organisation (8 Oct 2026).
Levels for a standard in a repository:
  1 Mentioned         - named in the name, description, README first paragraph or topics
  2 Schema or profile - a schema, profile, shape or platform configuration for the standard is in the code
  3 Applied in data   - data or metadata files in the repository use the standard's vocabulary or format
  4 Every record      - every record in at least one data file carries the standard (each RDF subject typed or described with it,
                        each catalogue item with its core fields, each ISO file one complete metadata record, each CSVW column mapped to a property)
Platforms: Mentioned, or Code or configuration (config files, extensions, recipes or infrastructure resources found).
Inputs are parsed as data only. Writes std_results.json and std_checks.txt."""
import os, re, json, gzip, collections, warnings, logging
warnings.filterwarnings("ignore"); logging.disable(logging.CRITICAL)
R = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(R); F = f"{R}/std/files"; E = f"{ROOT}/xgov/enr"
import importlib.util, sys
spec = importlib.util.spec_from_file_location("scan", f"{R}/scan_catalogues.py"); scan = importlib.util.module_from_spec(spec)
_out = sys.stdout; sys.stdout = open(os.devnull, "w"); spec.loader.exec_module(scan); sys.stdout = _out
import rdflib
from lxml import etree
CHECKS = []
def check(ok, cid, msg, guards):
    CHECKS.append(f"{'PASS' if ok else 'FAIL'} {cid} {msg}   [guards: {guards}]"); print(CHECKS[-1])

NS = {  # standard: namespace prefixes (RDF)
 "DCAT": ["http://www.w3.org/ns/dcat#"], "Dublin Core": ["http://purl.org/dc/terms/", "http://purl.org/dc/elements/1.1/"], "SKOS": ["http://www.w3.org/2004/02/skos/core#"],
 "PROV-O": ["http://www.w3.org/ns/prov#"], "DQV": ["http://www.w3.org/ns/dqv#"], "schema.org": ["http://schema.org/", "https://schema.org/"], "FOAF": ["http://xmlns.com/foaf/0.1/"],
 "vCard": ["http://www.w3.org/2006/vcard/ns#"], "ADMS": ["http://www.w3.org/ns/adms#"], "ODRL": ["http://www.w3.org/ns/odrl/2/"], "Data Cube (QB)": ["http://purl.org/linked-data/cube#"],
 "SDMX (RDF)": ["http://purl.org/linked-data/sdmx"], "GeoSPARQL": ["http://www.opengis.net/ont/geosparql#"], "SHACL": ["http://www.w3.org/ns/shacl#"], "OWL": ["http://www.w3.org/2002/07/owl#"],
 "CSVW": ["http://www.w3.org/ns/csvw#"], "Croissant": ["http://mlcommons.org/croissant/"],
}
SEM = ["DCAT", "Dublin Core", "SKOS", "PROV-O", "DQV", "schema.org", "ADMS", "ODRL", "Data Cube (QB)", "SDMX (RDF)", "GeoSPARQL", "CSVW", "Croissant"]
RDFT = rdflib.RDF.type
OWL = "http://www.w3.org/2002/07/owl#"; RDFS = "http://www.w3.org/2000/01/rdf-schema#"; SKOSC = "http://www.w3.org/2004/02/skos/core#Concept"
VOCAB_T = {OWL + "Class", OWL + "ObjectProperty", OWL + "DatatypeProperty", OWL + "AnnotationProperty", OWL + "Ontology", RDFS + "Class", "http://www.w3.org/1999/02/22-rdf-syntax-ns#Property", "http://www.w3.org/ns/shacl#NodeShape", "http://www.w3.org/ns/shacl#PropertyShape"}
DCAT_REC = {"http://www.w3.org/ns/dcat#" + c for c in ("Dataset", "DataService", "Catalog", "Distribution", "DatasetSeries")}
DCT = "http://purl.org/dc/terms/"
def grade_rdf(data, path):
    fmt = {"ttl": "turtle", "n3": "n3", "nt": "nt", "nq": "nquads", "trig": "trig", "jsonld": "json-ld", "rdf": "xml", "owl": "xml"}.get(path.rsplit(".", 1)[-1].lower())
    g = rdflib.ConjunctiveGraph() if fmt in ("nquads", "trig") else rdflib.Graph()
    try: g.parse(data=data, format=fmt)
    except Exception:
        if fmt != "xml": return dict(error="unparseable")
        try: g.parse(data=data, format="turtle")
        except Exception: return dict(error="unparseable")
    subs, types = collections.defaultdict(set), collections.defaultdict(set)
    for s_, p, o in g:
        subs[s_].add(str(p))
        if p == RDFT: types[s_].add(str(o)); subs[s_].add("type:" + str(o))
    typed = [x for x in subs if types[x]]
    vocab = [x for x in typed if types[x] & VOCAB_T]; concepts = [x for x in typed if SKOSC in types[x]]
    kind = "ontology or vocabulary" if typed and len(vocab) >= 0.5 * len(typed) else "code list (SKOS)" if typed and len(concepts) >= 0.5 * len(typed) else "data"
    recs = typed or list(subs)
    out = dict(triples=len(g), records=len(recs), kind=kind, standards={})
    for st, pre in NS.items():
        use = [x for x in recs if any(any(y.replace("type:", "").startswith(q) for q in pre) for y in subs[x])]
        if not use: continue
        v = dict(records_using=len(use), share=round(len(use) / max(1, len(recs)), 3))
        if st == "DCAT":   # record level for DCAT = every DCAT resource carries its core properties
            dr = [x for x in typed if types[x] & DCAT_REC]
            ok = [x for x in dr if DCT + "title" in subs[x] and (DCT + "description" in subs[x] or not (types[x] & {"http://www.w3.org/ns/dcat#Dataset"}))]
            v.update(dcat_records=len(dr), complete=len(ok))
        if st == "SKOS" and concepts:
            ok = [x for x in concepts if "http://www.w3.org/2004/02/skos/core#prefLabel" in subs[x]]
            v.update(concepts=len(concepts), complete=len(ok))
        out["standards"][st] = v
    return out
def rdf_level(st, v, r):
    if r["kind"] == "ontology or vocabulary": return 3, "used in an ontology or vocabulary file, not in data records"
    if st == "DCAT" and "dcat_records" in v:
        if v["dcat_records"] >= 1 and v["complete"] == v["dcat_records"]: return 4, f"{v['complete']} of {v['dcat_records']} DCAT resources carry title (and description for datasets)"
        return 3, f"{v['complete']} of {v['dcat_records']} DCAT resources complete"
    if st == "SKOS" and "concepts" in v:
        if v["concepts"] >= 2 and v["complete"] == v["concepts"]: return 4, f"{v['complete']} of {v['concepts']} concepts carry a preferred label"
        return 3, f"{v['complete']} of {v['concepts']} concepts labelled"
    if v["share"] >= 0.9 and r["records"] >= 2: return 4, f"{v['records_using']} of {r['records']} records use it"
    return 3, f"{v['records_using']} of {r['records']} records use it"
ISO = {"gmd": "http://www.isotc211.org/2005/gmd", "mdb": "http://standards.iso.org/iso/19115/-3/mdb/2.0", "gmi": "http://www.isotc211.org/2005/gmi", "csw": "http://www.opengis.net/cat/csw/2.0.2"}
def grade_iso(data):
    try: root = etree.fromstring(data, etree.XMLParser(resolve_entities=False, no_network=True, huge_tree=False))
    except Exception: return dict(error="unparseable")
    nss = set(root.nsmap.values()) if hasattr(root, "nsmap") else set()
    for el in root.iter():
        if isinstance(el.tag, str) and el.tag.startswith("{"): nss.add(el.tag[1:].split("}")[0])
        if len(nss) > 40: break
    if not any(v in nss for v in ISO.values()): return dict(standards={}, records=0)
    recs = [e for e in root.iter() if isinstance(e.tag, str) and e.tag.split("}")[-1] in ("MD_Metadata", "MI_Metadata")]
    def complete(e):
        t = etree.tostring(e)
        return (b"fileIdentifier" in t or b"metadataIdentifier" in t) and (b"title" in t.lower()) and (b"abstract" in t.lower())
    full = sum(1 for e in recs if complete(e))
    gem = b"gemini" in data.lower() or b"UK GEMINI" in data
    st = {"ISO 19115 / 19139": dict(records_using=full, share=round(full / max(1, len(recs)), 3))}
    if gem: st["UK GEMINI"] = dict(records_using=full, share=round(full / max(1, len(recs)), 3))
    return dict(records=len(recs), standards=st)
def grade_csvw(data):
    try: j = json.loads(data)
    except Exception: return dict(error="unparseable")
    ctx = json.dumps(j.get("@context", "")) if isinstance(j, dict) else ""
    if "csvw" not in ctx and "tableSchema" not in json.dumps(j)[:20000]: return dict(standards={}, records=0)
    tables = j.get("tables", [j]) if isinstance(j, dict) else []
    cols = [c for t in tables if isinstance(t, dict) for c in (t.get("tableSchema", {}) or {}).get("columns", []) if isinstance(c, dict)]
    mapped = [c for c in cols if c.get("propertyUrl") or c.get("valueUrl") or c.get("virtual")]
    about = any(isinstance(t, dict) and (t.get("tableSchema", {}) or {}).get("aboutUrl") for t in tables)
    return dict(records=len(cols), standards={"CSVW": dict(records_using=len(mapped), share=round(len(mapped) / max(1, len(cols)), 3), about_url=about)})
def grade_dp(data, path):
    try:
        if path.endswith((".yml", ".yaml")):
            import yaml; j = yaml.safe_load(data)
        else: j = json.loads(data)
    except Exception: return dict(error="unparseable")
    res = j.get("resources", []) if isinstance(j, dict) else []
    withs = [r for r in res if isinstance(r, dict) and isinstance(r.get("schema"), (dict, str))]
    return dict(records=len(res), standards={"Frictionless Data Package": dict(records_using=len(withs), share=round(len(withs) / max(1, len(res)), 3), field_schemas=len(withs))})
CORE = ("title", "description", "identifier", "publisher")
def grade_dcatjson(data):
    try: j = json.loads(data)
    except Exception: return dict(error="unparseable")
    items, kind = [], None
    if isinstance(j, dict) and isinstance(j.get("dataset"), list): items, kind = j["dataset"], "DCAT-US (data.json)" if "conformsTo" in j or "@type" in j else "DCAT-style JSON"
    elif isinstance(j, dict) and isinstance(j.get("@graph"), list): items, kind = j["@graph"], "DCAT JSON-LD"
    elif isinstance(j, dict) and isinstance(j.get("dcat:dataset"), list): items, kind = j["dcat:dataset"], "DCAT JSON-LD"
    if not items: return dict(standards={}, records=0)
    txt = json.dumps(j)[:200000].lower()
    if "dcat" not in txt and kind == "DCAT-style JSON": kind = None
    if not kind: return dict(standards={}, records=0)
    def ok(it):
        if not isinstance(it, dict): return False
        keys = {k.split(":")[-1].lower() for k in it}
        return sum(1 for c in CORE if c in keys) >= 3
    good = sum(1 for it in items if ok(it))
    return dict(records=len(items), kind=kind, standards={"DCAT": dict(records_using=good, share=round(good / max(1, len(items)), 3))})
def grade_profile(data, path):
    t = data[:300000].decode("utf-8", "replace").lower()
    found = {}
    for st, pre in NS.items():
        if st in SEM and any(p.lower() in t for p in pre): found[st] = "namespace in schema or profile"
    if re.search(r"\bdcat\b|dcat:", t): found.setdefault("DCAT", "DCAT terms in schema or profile")
    if "linkml" in t or path.endswith((".linkml.yaml", ".linkml.yml")): found["LinkML"] = "LinkML schema"
    if "sh:nodeshape" in t or "http://www.w3.org/ns/shacl#" in t: found["SHACL"] = "SHACL shapes"
    return found
PLUG = re.compile(r"^\s*ckan\.plugins\s*=\s*(.+)$", re.M)
def grade_ckan(data, path):
    t = data[:200000].decode("utf-8", "replace")
    out = {}
    m = PLUG.search(t)
    if m: out["plugins"] = sorted(set(m.group(1).split()))
    if path.lower().endswith("setup.py") and "ckanext" in t: out["extension"] = re.findall(r"name\s*=\s*['\"](ckanext-[\w-]+)", t)[:3] or ["ckanext"]
    return out
def grade_datahub(data):
    try:
        import yaml; j = yaml.safe_load(data)
    except Exception: return {}
    if not isinstance(j, dict) or "source" not in j: return {}
    src = (j.get("source") or {}).get("type") if isinstance(j.get("source"), dict) else None
    sink = (j.get("sink") or {}).get("type") if isinstance(j.get("sink"), dict) else None
    return dict(source=src, sink=sink) if src else {}
TF = {"Databricks Unity Catalog": r'resource\s+"databricks_(catalog|schema|metastore)', "AWS Glue Data Catalog": r'resource\s+"aws_glue_catalog_(database|table)', "Microsoft Purview": r'resource\s+"azurerm_purview_account'}

# ---------------- grade fetched files ----------------
REPO = collections.defaultdict(lambda: dict(standards={}, platforms={}, files=[]))
def lift(key, st, level, ev):
    cur = REPO[key]["standards"].get(st)
    if not cur or level > cur["level"]: REPO[key]["standards"][st] = dict(level=level, evidence=[ev])
    elif level == cur["level"] and len(cur["evidence"]) < 4: cur["evidence"].append(ev)
def plat(key, p, level, ev):
    if level == "Code or configuration" and re.search(r"(^|/)(examples?|tests?|samples?|demo)(/|_)", ev.split(":")[0].lower()):
        level, ev = "Mentioned", ev + " (example or test file, not counted as configuration)"
    cur = REPO[key]["platforms"].get(p)
    if not cur or (level == "Code or configuration" and cur["level"] != level): REPO[key]["platforms"][p] = dict(level=level, evidence=[ev])
    elif len(cur["evidence"]) < 4 and ev not in cur["evidence"]: cur["evidence"].append(ev)
acc = collections.Counter(); unparse = []
for d in sorted(os.listdir(F)):
    man = json.load(open(f"{F}/{d}/manifest.json")); key = f"{man['org']}/{man['repo']}"
    for f in man["files"]:
        if f["status"] != "ok": acc[f["status"]] += 1; continue
        data = open(f"{F}/{d}/{f['file']}", "rb").read(); cat, path = f["cat"], f["path"]; acc["parsed"] += 1
        if cat == "rdf":
            r = grade_rdf(data, path)
            if r.get("error"): unparse.append((key, path)); continue
            REPO[key]["files"].append(dict(path=path, kind="RDF " + r["kind"], records=r["records"], triples=r["triples"]))
            for st, v in r["standards"].items():
                if st not in SEM: continue
                lvl, why = rdf_level(st, v, r)
                lift(key, st, lvl, f"{path} ({r['kind']}): {why}")
        elif cat == "iso_xml":
            r = grade_iso(data)
            if r.get("error"): unparse.append((key, path)); continue
            for st, v in r["standards"].items():
                lvl = 4 if r["records"] >= 1 and v["share"] >= 0.9 else 3
                lift(key, st, lvl, f"{path}: {r['records']} metadata record(s), {v['records_using']} with identifier, title and abstract")
            if r["standards"]: REPO[key]["files"].append(dict(path=path, kind="ISO XML", records=r["records"]))
        elif cat == "csvw":
            r = grade_csvw(data)
            if r.get("error"): unparse.append((key, path)); continue
            for st, v in r["standards"].items():
                lvl = 4 if v["share"] >= 0.9 and r["records"] else 3
                lift(key, st, lvl, f"{path}: {v['records_using']} of {r['records']} columns mapped to properties" + ("; rows identified (aboutUrl)" if v.get("about_url") else ""))
            if r["standards"]: REPO[key]["files"].append(dict(path=path, kind="CSVW metadata", records=r["records"]))
        elif cat == "datapackage":
            r = grade_dp(data, path)
            if r.get("error"): unparse.append((key, path)); continue
            for st, v in r["standards"].items():
                lift(key, st, 3, f"{path}: {v['records_using']} of {r['records']} resources carry a field schema")
        elif cat == "dcat_json":
            r = grade_dcatjson(data)
            if r.get("error"): unparse.append((key, path)); continue
            for st, v in r["standards"].items():
                lvl = 4 if v["share"] >= 0.9 and r["records"] >= 2 else 3 if v["records_using"] else 2
                lift(key, st, lvl, f"{path} ({r['kind']}): {v['records_using']} of {r['records']} datasets with core fields")
        elif cat == "model_yaml":
            t = data[:300000].decode("utf-8", "replace")
            if re.search(r"^\s*(classes|slots)\s*:", t, re.M) and re.search(r"^\s*prefixes\s*:", t, re.M):
                lift(key, "LinkML", 2, f"{path}: LinkML schema")
                for st, why in grade_profile(data, path).items():
                    if st != "LinkML": lift(key, st, 2, f"{path}: {why} (LinkML schema)")
                if "metadata-exchange-model" in t.lower() or "uk_cross_government_metadata_exchange_model" in t.lower() or "cross-government metadata exchange" in t.lower(): lift(key, "xGov MEM", 2, f"{path}: the xGov MEM schema")
        elif cat == "profile":
            for st, why in grade_profile(data, path).items(): lift(key, st, 2, f"{path}: {why}")
        elif cat == "ckan":
            r = grade_ckan(data, path)
            if r: plat(key, "CKAN", "Code or configuration", f"{path}: " + ("plugins " + ", ".join(r["plugins"][:12]) if r.get("plugins") else "extension " + ", ".join(r.get("extension", []))))
            if any(p.startswith("dcat") or p in ("structured_data", "dcat_json_interface") for p in r.get("plugins", [])): lift(key, "DCAT", 2, f"{path}: CKAN DCAT plugin enabled")
            if any("spatial" in p or "harvest" in p for p in r.get("plugins", [])): lift(key, "ISO 19115 / 19139", 2, f"{path}: CKAN spatial or harvest plugin enabled")
        elif cat == "datahub":
            r = grade_datahub(data)
            if r: plat(key, "DataHub (Acryl/LinkedIn)", "Code or configuration", f"{path}: ingestion recipe, source {r['source']}" + (f", sink {r['sink']}" if r.get("sink") else ""))
        elif cat == "terraform":
            t = data[:300000].decode("utf-8", "replace")
            for p, rx in TF.items():
                if re.search(rx, t): plat(key, p, "Code or configuration", f"{path}: infrastructure resource")
        elif cat == "purview":
            plat(key, "Microsoft Purview", "Code or configuration", f"{path}: Purview integration code")
check(acc["parsed"] > 0 and acc["parsed"] + sum(v for k, v in acc.items() if k != "parsed") == sum(len(json.load(open(f"{F}/{d}/manifest.json"))["files"]) for d in os.listdir(F)), "C-STD-01",
      f"every selected file is accounted for: {acc['parsed']} parsed, {sum(v for k, v in acc.items() if k != 'parsed')} skipped (missing, too large or timed out), {len(unparse)} unparseable", "files silently dropped")

# ---------------- text mentions across the whole catalogue (level 1) ----------------
STD_MAP = {"DCAT": "DCAT", "schema.org Dataset": "schema.org", "Dublin Core": "Dublin Core", "ISO 19115 / UK GEMINI": "ISO 19115 / 19139", "DDI": "DDI", "CSVW": "CSVW", "SKOS": "SKOS", "PROV-O": "PROV-O", "DQV": "DQV",
           "Croissant": "Croissant", "Frictionless Data Package": "Frictionless Data Package", "SDMX": "SDMX (RDF)", "LinkML": "LinkML", "xGov MEM": "xGov MEM", "OpenAPI": "OpenAPI", "JSON Schema": "JSON Schema"}
for st, v in scan.S.items():
    for o, n in v["text"]:
        k = f"{o}/{n}"
        if STD_MAP[st] not in REPO[k]["standards"]: lift(k, STD_MAP[st], 1, "named in name, description, README or topics")
    for o, n, c in v["files"]:
        k = f"{o}/{n}"
        if st in ("OpenAPI", "JSON Schema", "LinkML", "Frictionless Data Package"):
            lift(k, STD_MAP[st], 2 if st != "Frictionless Data Package" else 3, f"{c} file(s) by name")
        elif STD_MAP[st] not in REPO[k]["standards"]: lift(k, STD_MAP[st], 1, f"{c} file name(s) refer to it")
for p, v in scan.P.items():
    for o, n in v["text"]: plat(f"{o}/{n}", p, "Mentioned", "named in name, description, README or topics")
    for o, n, c in v["files"]: plat(f"{o}/{n}", p, "Mentioned", f"{c} file path(s) refer to it")

# ---------------- data publishing signals from trees (no metadata standard implied) ----------------
DATA = {"CSV": r"\.csv$", "Parquet": r"\.parquet$", "GeoJSON or GeoPackage": r"\.(geojson|gpkg)$", "Excel": r"\.(xlsx|xls|ods)$", "RDF": r"\.(ttl|rdf|nt|jsonld)$"}
PUB = {}
for d in os.listdir(E):
    try: tree = gzip.open(f"{E}/{d}/tree.gz", "rt", errors="replace").read().lower().splitlines()
    except Exception: continue
    tree = [p for p in tree if "/node_modules/" not in p and "/test" not in p and "fixture" not in p]
    c = {k: sum(1 for p in tree if re.search(rx, p)) for k, rx in DATA.items()}
    if any(c.values()): PUB["/".join(d.split("__", 1))] = {k: v for k, v in c.items() if v}
for repo in os.listdir(f"{ROOT}/inv/shallow"):   # co-cddo trees come from the inventory's local clones (V5-4)
    tree = []
    for root, dirs, fs in os.walk(f"{ROOT}/inv/shallow/{repo}"):
        dirs[:] = [x for x in dirs if x not in (".git", "node_modules", "vendor")]
        tree += [os.path.join(root, f).lower() for f in fs]
    tree = [p for p in tree if "/test" not in p and "fixture" not in p]
    c = {k: sum(1 for p in tree if re.search(rx, p)) for k, rx in DATA.items()}
    if any(c.values()): PUB[f"co-cddo/{repo}"] = {k: v for k, v in c.items() if v}

# ---------------- negative tests and known positives ----------------
neg_alation = not re.search(scan.PLAT["Alation"][1], "docs/installation.md")
neg_prov = not re.search(scan.STD["PROV-O"][1], "src/provider/index.ts")
check(neg_alation and neg_prov, "C-STD-02", "negative tests: 'installation' does not match Alation and 'provider' does not match PROV-O (V5-3)", "V5-3: substring matching inflated platform and standard counts")
half = b"@prefix dcat: <http://www.w3.org/ns/dcat#> . @prefix ex: <http://e.x/> . ex:a a dcat:Dataset . ex:b a ex:Thing . ex:c a ex:Thing ."
hr = grade_rdf(half, "x.ttl"); full = grade_rdf(b"@prefix dcat: <http://www.w3.org/ns/dcat#> . @prefix ex: <http://e.x/> . ex:a a dcat:Dataset . ex:b a dcat:Distribution .", "x.ttl")
check(hr["standards"]["DCAT"]["share"] < 0.9 and full["standards"]["DCAT"]["share"] >= 0.9, "C-STD-03", "record-level rule: a file where only some records use DCAT is not graded 'every record'; one where all do is (negative and positive test)", "record-level claims from partial use")
onto = grade_rdf(b"@prefix owl: <http://www.w3.org/2002/07/owl#> . @prefix dct: <http://purl.org/dc/terms/> . @prefix ex: <http://e.x/> . ex:A a owl:Class ; dct:description \"a\" . ex:B a owl:Class ; dct:description \"b\" .", "o.ttl")
check(onto["kind"] == "ontology or vocabulary" and rdf_level("Dublin Core", onto["standards"]["Dublin Core"], onto)[0] == 3, "C-STD-06", "negative test: an ontology whose every term uses Dublin Core is not graded 'every record' (vocabulary terms are not data records)", "V5-5: vocabulary terms counted as data records")
lv4 = [(k, s) for k, v in REPO.items() for s, x in v["standards"].items() if x["level"] == 4]
check(all(any(c.isdigit() for c in e) for k, s in lv4 for e in REPO[k]["standards"][s]["evidence"]), "C-STD-04", f"every 'every record' grade ({len(lv4)}) cites counted records from a parsed file", "record-level grades without parsed evidence")
mem = REPO.get("co-cddo/ukgov-metadata-exchange-model", {}).get("standards", {})
check(mem.get("DCAT", {}).get("level", 0) >= 2, "C-STD-05", f"known positive: the xGov MEM repository reaches at least 'schema or profile' for DCAT (got level {mem.get('DCAT', {}).get('level', 0)})", "a grader that misses the reference case")

# ---------------- organisation roll-up for the Directory of Data Catalogues ----------------
cat = json.load(open(f"{R}/catalogue.json")); OIDX = {o["org"].lower(): i for i, o in enumerate(cat["orgs"])}
VENDOR = {"CKAN": ("Open Knowledge Foundation", "Open source"), "DataHub (Acryl/LinkedIn)": ("Acryl Data (open source from LinkedIn)", "Open source with commercial service"), "GeoNetwork / CSW": ("OSGeo GeoNetwork or pycsw", "Open source"),
          "Microsoft Purview": ("Microsoft", "Commercial"), "Databricks Unity Catalog": ("Databricks", "Commercial (open source core)"), "AWS Glue Data Catalog": ("Amazon Web Services", "Commercial cloud service"),
          "Amundsen": ("Linux Foundation (from Lyft)", "Open source"), "Informatica": ("Informatica", "Commercial"), "DKAN": ("CivicActions", "Open source"), "Magda": ("Magda (Data61)", "Open source"),
          "OpenMetadata": ("Collate", "Open source"), "Apache Atlas": ("Apache Software Foundation", "Open source"), "Collibra": ("Collibra", "Commercial"), "Alation": ("Alation", "Commercial"), "Atlan": ("Atlan", "Commercial"),
          "data.world": ("data.world", "Commercial"), "Google Data Catalog / Dataplex": ("Google Cloud", "Commercial cloud service"), "Socrata": ("Tyler Technologies", "Commercial"), "Marquez / OpenLineage": ("Linux Foundation", "Open source")}
ORG = collections.defaultdict(lambda: dict(platforms={}, standards={}, publishing=collections.Counter(), repos=set()))
for k, v in REPO.items():
    o = k.split("/")[0]
    for p, x in v["platforms"].items():
        cur = ORG[o]["platforms"].setdefault(p, dict(level=x["level"], repos=[]))
        if x["level"] == "Code or configuration": cur["level"] = x["level"]
        cur["repos"].append(k)
    for s, x in v["standards"].items():
        cur = ORG[o]["standards"].setdefault(s, dict(level=0, repos=[]))
        cur["level"] = max(cur["level"], x["level"]); cur["repos"].append([k, x["level"]])
    ORG[o]["repos"].add(k)
for k, c in PUB.items():
    o = k.split("/")[0]; ORG[o]["publishing"].update({x: 1 for x in c}); ORG[o]["repos"].add(k)
orgs_out = {}
for o, v in ORG.items():
    i = OIDX.get(o.lower()); b = cat["bodies"][cat["orgs"][i]["body"]] if i is not None and cat["orgs"][i].get("body", -1) >= 0 else None
    orgs_out[o] = dict(body=b["name"] if b else None, body_type=b["type"] if b else None, sector=cat["orgs"][i]["sector"] if i is not None else None,
                       platforms={p: dict(x, vendor=VENDOR.get(p, ("", ""))[0], model=VENDOR.get(p, ("", ""))[1], repos=sorted(set(x["repos"]))[:8], n=len(set(x["repos"]))) for p, x in v["platforms"].items()},
                       standards={s: dict(level=x["level"], n=len(x["repos"]), top=sorted(x["repos"], key=lambda r: -r[1])[:6]) for s, x in v["standards"].items()},
                       publishing=dict(v["publishing"]))
PCLASS = {"CKAN": "Open data catalogue", "DKAN": "Open data catalogue", "Socrata": "Open data catalogue", "Magda": "Open data catalogue", "GeoNetwork / CSW": "Geospatial metadata catalogue",
          "DataHub (Acryl/LinkedIn)": "Enterprise metadata catalogue", "OpenMetadata": "Enterprise metadata catalogue", "Amundsen": "Enterprise metadata catalogue", "Apache Atlas": "Enterprise metadata catalogue",
          "Collibra": "Enterprise metadata catalogue", "Alation": "Enterprise metadata catalogue", "Atlan": "Enterprise metadata catalogue", "Informatica": "Enterprise metadata catalogue",
          "Microsoft Purview": "Enterprise metadata catalogue", "data.world": "Enterprise metadata catalogue", "Databricks Unity Catalog": "Lakehouse or technical metastore",
          "AWS Glue Data Catalog": "Lakehouse or technical metastore", "Google Data Catalog / Dataplex": "Lakehouse or technical metastore", "Marquez / OpenLineage": "Lineage service"}
for o in orgs_out.values():
    for p, x in o["platforms"].items(): x["class"] = PCLASS.get(p, "")
LEVELS = {1: "Mentioned", 2: "Schema or profile", 3: "Applied in data", 4: "Every record"}
OUT = dict(levels=LEVELS, vendor=VENDOR, pclass=PCLASS, repos={k: v for k, v in REPO.items() if v["standards"] or v["platforms"]}, publishing=PUB, orgs=orgs_out,
           fetched=dict(repos=len(os.listdir(F)), files_parsed=acc["parsed"], skipped={k: v for k, v in acc.items() if k != "parsed"}, unparseable=len(unparse)),
           note="Public GitHub only. Absence of a platform does not mean an organisation lacks one: commercial catalogues are mostly configured in the product, not in public code.")
json.dump(OUT, open(f"{R}/std_results.json", "w"), ensure_ascii=False)
open(f"{R}/std_checks.txt", "w").write("\n".join(CHECKS) + "\n")
lv = collections.Counter((s, x["level"]) for v in REPO.values() for s, x in v["standards"].items())
for s in sorted({s for s, _ in lv}): print(f"{s:28s}", " ".join(f"L{l}:{lv[(s, l)]}" for l in (1, 2, 3, 4)))
pc = collections.Counter((p, x["level"]) for v in REPO.values() for p, x in v["platforms"].items()); print(pc)
print("orgs with a platform:", sum(1 for v in orgs_out.values() if v["platforms"]), "| orgs publishing data files:", sum(1 for v in orgs_out.values() if v["publishing"]))
sys.exit(1 if any(c.startswith("FAIL") for c in CHECKS) else 0)
