"""Data interoperability: layers, semantic and syntactic standards, and the roles projects play (7.8, R51).

Layers follow the European Interoperability Framework (EIF, European Commission 2017): legal, organisational, semantic
and technical; the technical layer is split here into syntax (formats and schemas) and transport (APIs and messaging),
so that semantic and syntactic interoperability can be seen separately.
Roles are what a project does for interoperability: crosswalks and mappings, converters and transformers, validators,
metadata generators, schema and vocabulary publishers, API adapters, identifier matching and data catalogues.
Standards are named open standards found in a project's words (and, for co-cddo, its files).
Input: build/xgov/xgov.json rows and build/catalogue/catalogue.json. Writes interop.json and interop_checks.txt.
Run with python3 -I. Exit code 1 if a check fails.
"""
import json, os, re, sys, collections
S = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(S); I = re.I
B, E = r"(?<![a-z0-9])", r"(?![a-z0-9])"
w = lambda *a: re.compile(B + "(?:" + "|".join(a) + ")" + E, I)
EIF = "European Interoperability Framework (European Commission, 2017): https://interoperable-europe.ec.europa.eu/collection/nifo-national-interoperability-framework-observatory/european-interoperability-framework-detail"
# standard, layer (semantic | syntax | transport | organisational | legal), rule
STANDARDS = [
 ("DCAT", "semantic", w(r"dcat(?:-ap)?(?:-uk)?", r"data catalog(?:ue)? vocabulary")), ("SKOS", "semantic", w(r"skos")), ("OWL", "semantic", w(r"\bowl\b(?= )(?=.*(?:ontolog|rdf|semantic))", r"web ontology language")),
 ("RDF", "semantic", w(r"\brdf\b", r"linked data", r"triple ?store", r"sparql", r"turtle (?:files?|format)", r"\bttl\b")), ("Schema.org", "semantic", w(r"schema\.org")), ("Dublin Core", "semantic", w(r"dublin core", r"dcterms")),
 ("PROV", "semantic", w(r"w3c prov", r"prov-o", r"\bprov\b ontology")), ("SHACL", "semantic", w(r"shacl")), ("Ontologies", "semantic", w(r"ontolog(?:y|ies)", r"knowledge graphs?")),
 ("Controlled vocabularies and code lists", "semantic", w(r"controlled vocabular(?:y|ies)", r"code ?lists?", r"reference data", r"taxonom(?:y|ies)", r"thesaur(?:us|i)", r"(?:standard|industrial|occupational|statistical) classifications?", r"classification (?:codes?|schemes?)", r"\b(?:sic|soc) codes?")),
 ("FHIR", "semantic", w(r"fhir")), ("SNOMED CT", "semantic", w(r"snomed")), ("HL7", "semantic", w(r"\bhl7\b")), ("dm+d", "semantic", w(r"dm\+d", r"dictionary of medicines")),
 ("UPRN and USRN", "semantic", w(r"uprns?", r"usrns?", r"unique property reference")), ("Open Referral UK", "semantic", w(r"open referral")), ("OCDS", "semantic", w(r"\bocds\b", r"open contracting")), ("360Giving", "semantic", w(r"360 ?giving")),
 ("SDMX", "semantic", w(r"sdmx")), ("XBRL and iXBRL", "semantic", w(r"i?xbrl")), ("INSPIRE, GEMINI and ISO 19115", "semantic", w(r"inspire (?:directive|metadata|manual)", r"uk gemini", r"gemini metadata", r"iso ?19115", r"iso ?19139")),
 ("NaPTAN, NeTEx, SIRI and GTFS", "semantic", w(r"naptan", r"netex", r"\bsiri\b", r"gtfs", r"transxchange")), ("CSVW", "syntax", w(r"csvw", r"csv on the web")),
 ("JSON Schema", "syntax", w(r"json ?schemas?")), ("JSON-LD", "syntax", w(r"json-?ld")), ("XML Schema (XSD)", "syntax", w(r"\bxsd\b", r"xml schemas?")), ("XML", "syntax", w(r"\bxml\b")), ("CSV", "syntax", w(r"\bcsv\b")),
 ("GeoJSON", "syntax", w(r"geojson")), ("GML and CityGML", "syntax", w(r"citygml", r"\bgml\b")), ("Avro, Protobuf and Parquet", "syntax", w(r"avro", r"protobuf", r"protocol buffers", r"parquet")), ("YAML", "syntax", w(r"\byaml\b")),
 ("OpenAPI", "transport", w(r"openapi", r"swagger")), ("AsyncAPI", "transport", w(r"asyncapi")), ("GraphQL", "transport", w(r"graphql")), ("SOAP and WSDL", "transport", w(r"\bsoap\b", r"wsdl")), ("REST APIs", "transport", w(r"rest(?:ful)? apis?", r"rest services?")),
 ("Messaging (Kafka, AMQP, MESH)", "transport", w(r"kafka", r"amqp", r"rabbitmq", r"\bmesh\b(?= )(?=.*(?:nhs|message|mailbox))", r"message exchange")),
 ("Data sharing agreements and the DEA", "legal", w(r"data sharing agreements?", r"digital economy act", r"\bdea\b(?= )(?=.*(?:data|sharing|register))", r"information sharing agreements?", r"data protection impact", r"\bdpias?\b")),
 ("Open Government Licence", "legal", w(r"open government licen[cs]e", r"\bogl\b")),
 ("Data standards and governance", "organisational", w(r"data standards? (?:authority|board|catalogue)", r"data governance", r"data ownership", r"data stewards?", r"metadata (?:standards?|model|requirements)", r"interoperability (?:framework|standards?)", r"api standards?", r"technical standards?")),
]
ROLES = [
 ("crosswalk", "Crosswalks and mappings", w(r"crosswalks?", r"concordances?", r"mappings? (?:between|table|file)", r"map(?:s|ping)? (?:codes?|identifiers?|ids?|between)", r"lookup tables?", r"look-?ups? between", r"code mapping", r"data mapping")),
 ("converter", "Converters and transformers", w(r"convert(?:er|ers|s|ing)?", r"conversions?", r"transform(?:er|ers|s|ation|ations)?(?! (?:the way|how|public))", r"translat(?:e|or|ion) (?:between|from|to) (?:formats?|schemas?)", r"to (?:csv|json|xml|rdf|geojson|parquet)", r"(?:csv|json|xml|rdf|excel|xlsx) to ", r"exporters? to", r"parsers?", r"serializ\w+|serialis\w+")),
 ("validator", "Validators and checkers", w(r"validat\w+ (?:data|files?|metadata|schemas?|csv|json|xml|records?|returns?|submissions?|datasets?)", r"(?:data|metadata|schema|csv|json|xml|file|dataset) validat\w+", r"validators? for (?:[\w-]+ ){0,3}(?:data|metadata|schemas?|files?)", r"linters? for (?:data|metadata|schemas?)", r"conformance (?:tests?|checks?|checker)", r"schema checks?", r"data quality (?:checks?|rules|tool)")),
 ("metagen", "Metadata generators and harvesters", w(r"metadata (?:generat\w+|harvest\w*|extract\w*|editor|creation|publishing|tool|catalogue|enrichment)", r"generat\w+ metadata", r"harvest(?:er|ers|ing)?", r"\bckan\b", r"data catalog(?:ue)? (?:generator|builder)", r"datasette", r"auto[- ]?tag\w*")),
 ("schema", "Schemas, models and specifications", w(r"(?:data|information|canonical|logical) models?", r"(?:data|json|xml|message|api|event|interface) schemas?", r"schemas? (?:for|of) (?:data|messages?|records?)", r"(?:data|api|interface|technical) specifications?", r"data standards?", r"data dictionar(?:y|ies)", r"exchange model")),
 ("vocab", "Vocabularies, code lists and registers", w(r"vocabular(?:y|ies)", r"code ?lists?", r"reference data", r"registers? (?:api|service|of)", r"taxonom(?:y|ies)", r"ontolog(?:y|ies)", r"thesaur(?:us|i)", r"classifications?")),
 ("adapter", "API adapters, gateways and connectors", w(r"adapters?", r"connectors?", r"(?:data|integration) gateways?", r"api clients?", r"client librar(?:y|ies) for", r"integration (?:layer|service|framework)", r"proxy for", r"wrapper (?:for|around)")),
 ("identity", "Identifier matching and resolution", w(r"record linkage", r"(?:entity|data|record) (?:matching|resolution)", r"dedup\w*", r"identifier (?:matching|resolution|service)", r"master data", r"golden record", r"address (?:matching|lookup|base)", r"\buprn\b", r"fuzzy match\w*", r"linkage")),
 ("catalogue", "Data catalogues and discovery", w(r"data catalog(?:ue)?s?", r"dataset (?:catalog(?:ue)?|search|discovery)", r"data (?:discovery|marketplace|portal)", r"open data (?:portal|platform)", r"find (?:open )?data")),
]
NEG = w(r"convert\w* (?:the )?(?:code ?base|project|repo\w*|app\w*) to", r"currency convert\w*", r"unit convert\w*", r"image convert\w*", r"video convert\w*", r"pdf convert\w*", r"convert(?:ing)? (?:to )?(?:typescript|python ?3|es6)", r"transform(?:ation)? (?:programme|plan|team|strategy)", r"digital transformation", r"business transformation", r"database schemas? migrations?", r"form validation", r"input validation", r"html validat\w+", r"accessibility (?:validat\w+|checks?)")

def hits(rules, text, k):
    sc, ev = collections.Counter(), {}
    for i, r in enumerate(rules):
        ms = list(r[-1].finditer(text))
        if ms: sc[i] = len({m.group(0).lower() for m in ms}); ev[i] = max((m.group(0) for m in ms), key=len)
    return [[i, ev[i]] for i, _ in sorted(sc.items(), key=lambda kv: (-kv[1], -len(ev[kv[0]]), kv[0]))[:k]]

def classify(text):
    t = NEG.sub(" ", text); st = hits(STANDARDS, t, 6)
    ro = hits(ROLES, t, 3) if st or re.search(r"data|metadata|schema|standard|format|interop|exchange|api|dataset|record|vocab|ontolog|catalog|crosswalk|mapping|convert|validat|harvest|identifier|\bids?\b", t, I) else []
    return {"s": st, "r": ro}

def need(ok, cid, msg, lines, fails):
    lines.append(f"{'PASS' if ok else 'FAIL'} {cid} {msg} [guards: R51]"); print(lines[-1])
    if not ok: fails.append(cid)

# Precision, judged by Claude on 1 November 2026 from random samples of each role's strongest match (not owner-confirmed).
PREC = [("Roles", 26, 24, "9 roles, 3 each (2 for crosswalks, which have 2). Fixed after round one: web 'mapping from' tiles, validation of code annotations and UI tests, pipeline schemas, API gateway authorisers, a payment 'data hub'."),
        ("Standards", 28, 28, "The 10 most common standards, 3 each (1 for CSVW). Fixed after round one: CSVW and other standards read from file contents were dropped in favour of the project's own words, and 'classification' in text classification was narrowed to statistical and industrial classifications.")]

if __name__ == "__main__":
    X = json.load(open(os.path.join(R, "xgov", "xgov.json"))); C = json.load(open(os.path.join(R, "catalogue", "catalogue.json")))
    recs = [(r["o"] + "/" + r["n"], " ".join(str(r.get(k) or "") for k in ("n", "d", "ld", "t")).replace("-", " ").replace("_", " ")) for r in X["rows"]]
    for a in C["cat"]:
        o = dict(zip(C["cf"], a)); recs.append((C["orgs"][o["oi"]]["org"] + "/" + o["n"], (str(o["n"]) + " " + str(o.get("d") or "")).replace("-", " ").replace("_", " ")))

    # crown dependency and overseas territory repositories, verified directly against GitHub (cdot.json)
    _cd = os.path.join(S, "cdot.json")
    if os.path.exists(_cd):
        for _a in json.load(open(_cd))["accounts"]:
            if not _a.get("in_catalogue", True): continue   # only accounts confirmed as official
            for _r in _a["repos"]: recs.append((_a["account"] + "/" + _r["name"], (_r["name"] + " " + (_r.get("description") or "")).replace("-", " ").replace("_", " ")))
    out, seen = {}, set()
    for key, text in recs:
        if key in seen: continue
        seen.add(key); c = classify(text)
        if c["s"] or c["r"]: out[key] = {k: v for k, v in c.items() if v}
    sc = collections.Counter(i for v in out.values() for i, _ in v.get("s", [])); rc = collections.Counter(i for v in out.values() for i, _ in v.get("r", []))
    lines, fails = [], []
    layers = {s[1] for s in STANDARDS}
    need(layers == {"semantic", "syntax", "transport", "organisational", "legal"} and all(rc[i] for i in range(len(ROLES))) and sum(1 for i in range(len(STANDARDS)) if sc[i]) >= 30, "C-INT-01", f"{len(STANDARDS)} standards across the five layers (EIF's legal, organisational and semantic layers, and its technical layer split into syntax and transport) and {len(ROLES)} interoperability roles, every role found in projects and {sum(1 for i in range(len(STANDARDS)) if sc[i])} standards found ({len(out):,} projects in all; none found: {", ".join(STANDARDS[i][0] for i in range(len(STANDARDS)) if not sc[i]) or "none"})", lines, fails)
    traps = ["Currency converter widget", "Digital transformation programme website", "Form validation for the sign-up page", "Database schema migrations for Rails", "Convert the codebase to TypeScript", "An image converter"]
    real = {"Crosswalk between ANA ids and GOV.UK slugs": ("r", "crosswalk"), "Convert CSV to JSON-LD": ("r", "converter"), "Metadata harvester for the data catalogue": ("r", "metagen"), "Validator for DCAT-AP UK metadata": ("r", "validator"), "SKOS vocabulary of code lists": ("s", "SKOS")}
    ix = {"r": {r[0]: i for i, r in enumerate(ROLES)}, "s": {s[0]: i for i, s in enumerate(STANDARDS)}}
    bt = [t for t in traps if classify(t)["r"]]; br = [t for t, (k, v) in real.items() if (k == "r" and (not classify(t)[k] or classify(t)[k][0][0] != ix[k][v])) or (k == "s" and ix[k][v] not in [i for i, _ in classify(t)[k]])]
    need(all(r / n >= 0.85 for _, n, r, _ in PREC), "C-INT-03", "precision on judged samples: " + "; ".join(f"{d} {r} of {n}" for d, n, r, _ in PREC) + ", judged by Claude, not owner-confirmed", lines, fails)
    need(not bt and not br, "C-INT-02n", f"negative tests: {len(traps)} phrases that only look like interoperability work get no role, and {len(real)} plain ones get the right role or standard (wrong: {bt + br})", lines, fails)
    json.dump(dict(framework=EIF, layers=[["semantic", "Semantic", "Shared meaning: vocabularies, ontologies, code lists, data models and identifiers"], ["syntax", "Syntax", "Shared structure: formats and schemas such as CSV, JSON Schema, XML Schema and GeoJSON"], ["transport", "Transport", "Shared exchange: APIs, interface descriptions and messaging"], ["organisational", "Organisational", "Shared governance: data standards, ownership, stewardship and metadata requirements"], ["legal", "Legal", "Shared permission: data sharing agreements, the Digital Economy Act and open licences"]],
                   standards=[[s[0], s[1]] for s in STANDARDS], roles=[[r[0], r[1]] for r in ROLES], recs=out, prec=dict(judged_by="Claude, 1 November 2026 (not owner-confirmed)", rounds=PREC)), open(os.path.join(S, "interop.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    open(os.path.join(S, "interop_checks.txt"), "w").write("\n".join(lines) + "\n")
    print({ROLES[i][1]: n for i, n in rc.most_common()}); print({STANDARDS[i][0]: n for i, n in sc.most_common()})
    sys.exit(1 if fails else 0)
