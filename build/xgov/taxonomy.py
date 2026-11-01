"""Declared tagging rules, v2 (2026-10-08). Every tag records the words that matched. Rules favour precision over recall:
v1 bare terms ('platform', 'modernisation', 'privacy', 'dns', 'statistics', 'govuk frontend', 'consult', 'focus') produced
false positives found in independent review (defect D7); each is now a regression case in test_taxonomy.py.
Input text: repo name (CamelCase and separators split), GitHub description, topics, and the first prose paragraph of the README."""
import re

R = "https://roadmap-for-modern-digital-government.campaign.gov.uk/"
STRATEGY = [
 # id, short label, long label, group, source URL, regex
 ("DF1", "Strategic data roadmap", "Data Foundations 1 · Strategic Data Roadmap", "Government Data · Data Foundations",
  R + "digital-and-data-infrastructure/frameworks-for-data-use/",
  r"\b(strategic data roadmap|data strateg(y|ies)|public sector data strategy)\b"),
 ("DF2", "National Data Library", "Data Foundations 2 · National Data Library", "Government Data · Data Foundations",
  "https://www.gov.uk/government/publications/national-data-library-progress-update-january-2026/national-data-library-progress-update-january-2026",
  r"\b(national data library|data ?\.? ?gov ?\.? ?uk|datagovuk|ckan|ckanext|curated collections?|data manual)\b"),
 ("DF3", "Public data infrastructure", "Data Foundations 3 · UK Public Data Infrastructure", "Government Data · Data Foundations",
  "https://www.gov.uk/government/collections/metadata-standards-for-sharing-and-publishing-data",
  r"\b((dataset|data|open|descriptive|statistical|geospatial|records?) metadata|metadata (catalog(ue)?s?|standards?|models?|schemas? for (data|datasets)|management|registry|registries|exchange|profiles?|vocabular(y|ies)|repositor(y|ies)|harvest(er|ing)?|publishing)|dcat|data ?catalog(ue)?s?|dataset catalog(ue)?s?|catalogue of (data|datasets)|data marketplace|data sharing agreements?|data sharing|data exchange (model|standards?|format)s?|csvw|linked data|rdf|skos|ontolog(y|ies)|data standards?|reference data|open registers?|api catalog(ue)?|data discovery|data product (catalog(ue)?|marketplace|registry|specification)s?|data vocab(ulary)?|interoperability standards?|data mesh)\b"),
 ("DF4", "Data maturity", "Data Foundations 4 · Data Maturity Service", "Government Data · Data Foundations",
  "https://www.gov.uk/government/publications/data-maturity-assessment-for-government-framework",
  r"\b(data maturity|data maturity assessment|maturity model)\b"),
 ("DF5", "Data value and DAM", "Data Foundations 5 · Data Value (incl. Data Asset Management policy)", "Government Data · Data Foundations",
  "https://www.gov.uk/government/publications/data-asset-management-policy-in-government",
  r"\b(critical data assets?|data assets?|information assets?|(information|data) asset registers?|asset registers?|esda|essential shared data|data ownership|data owners?|data stewardship (framework|model|roles?|policy)|data stewards? (role|network|community)|data quality|dqap|master data|data lineage|data governance|records management|data dictionar(y|ies)|business glossar(y|ies))\b"),
 ("DF6", "Data protection and trust", "Data Foundations 6 · Data Protection and Public Trust", "Government Data · Data Foundations",
  "https://dataingovernment.blog.gov.uk/2025/05/08/making-the-algorithmic-transparency-recording-standard-atrs-mandatory-across-government/",
  r"\b(atrs|algorithmic transparency|data ethics|ethics framework|gdpr|dpia|data protection impact|anonymi[sz](e|ed|ation|ing)|pseudonymi[sz](e|ed|ation|ing)|differential privacy|privacy[- ](enhancing|preserving)|data protection (impact|act|officer|by design|polic(y|ies)|principles)|subject access requests?)\b"),
 ("FF", "Firmer foundations", "Roadmap outcome · Firmer foundations (legacy, cyber, common technology)", "OCTO · Firmer foundations",
  R + "about/progress",
  r"\b(legacy (system|systems|application|applications|code|platform|migration)|mainframe|technical debt|sbom|software bill of materials|vulnerabilit(y|ies)|secure by design|cyber ?security|cyber assessment framework|cyber resilience|finops|cloud costs?|focus (cost|export)s?|cloud maturity|technology code of practice|security ?\.? ?txt|mta ?sts|dmarc|dkim|bimi|zero trust|threat model(l)?ing|threat detection|threat intelligence|siem|incident response|disaster recovery|penetration test(ing)?|asset inventory)\b"),
 ("BP1", "Join up services", "Blueprint 1 · Join up public sector services", "Blueprint / Roadmap",
  R + "join-up-services/",
  r"\b(one ?login|digital identity|identity verification|govuk wallet|gov uk wallet|digital wallet|verifiable credentials?|govuk app|gov uk app|govuk notify|gov uk notify|notify api|govuk pay|gov uk pay|pay api|govuk forms|gov uk forms|single sign[- ]on|customer ?first)\b"),
 ("BP2", "AI for public good", "Blueprint 2 · Use AI for the public good", "Blueprint / Roadmap",
  R + "ai/",
  r"\b(llms?|large language models?|genai|generative ai|gpt|rag|retrieval augmented|chat ?bots?|ai assistants?|machine learning|nlp|natural language processing|speech to text|embeddings?|mcp servers?|model context protocol|agentic|ai agents?|copilot|bedrock|openai|anthropic|langchain|themefinder|redbox|humphrey|artificial intelligence|ai powered|ai)\b"),
 ("BP3", "Digital and data infrastructure", "Blueprint 3 · Strengthen and extend digital and data public infrastructure", "Blueprint / Roadmap",
  R + "digital-and-data-infrastructure/",
  r"\b(digital public infrastructure|digital backbone|api mandate|cross[- ]government (platform|service)s?|government as a platform)\b"),
 ("BP6", "Transparency", "Blueprint 6 · Commit to transparency and accountability", "Blueprint / Roadmap",
  R + "transparency/",
  r"\b(open data|transparency (data|report|reports|publication)|spend (data|over)|performance platform|service performance (data|dashboard)|official statistics publication)\b"),
 ("NHS", "NHS 10 Year Plan", "10 Year Health Plan · analogue to digital", "Sector plans",
  "https://www.gov.uk/government/publications/10-year-health-plan-for-england-fit-for-the-future",
  r"\b(nhs app|patient records?|fhir|hl7|snomed|federated data platform|gp connect|electronic health records?|ehr)\b"),
 ("LOCAL", "Local digital", "Local Digital Declaration / GDS Local", "Sector plans",
  "https://www.localdigital.gov.uk/declaration/",
  r"\b(local government|localgov|local digital|planning applications?|planning data|waste collections?|bin collections?)\b"),
]
STANDARDS = [
 ("DCAT", r"\bdcat( ?ap)?\b"), ("CSVW", r"\bcsvw\b|csv on the web"), ("SKOS", r"\bskos\b"), ("schema.org", r"schema\.org"),
 ("PROV-O", r"\bprov( ?o)?\b(?! ?ider)"), ("DQV", r"\bdqv\b|data quality vocabulary"), ("ODRL", r"\bodrl\b"), ("Dublin Core", r"dublin ?core|\bdcterms\b"),
 ("SDMX", r"\bsdmx\b"), ("DDI", r"\bddi\b"), ("ISO 19115 / UK GEMINI", r"iso ?19115|\buk gemini\b|\binspire directive\b"), ("OGC / GeoJSON", r"\bogc\b|geo ?json|\bwfs\b|\bwms\b"),
 ("OpenAPI", r"openapi|swagger"), ("JSON Schema", r"json ?schema"), ("Frictionless Data Package", r"frictionless|datapackage"),
 ("RDF / OWL / SHACL", r"\brdf\b|\bowl\b|\bshacl\b|\bturtle\b|sparql"), ("FHIR", r"\bfhir\b"), ("SNOMED CT", r"snomed"),
 ("XBRL", r"\bxbrl\b"), ("CKAN API", r"\bckan\b"), ("security.txt (RFC 9116)", r"security ?\.? ?txt"), ("MTA-STS (RFC 8461)", r"mta ?sts"),
 ("CycloneDX / SPDX (SBOM)", r"cyclonedx|\bspdx\b|\bsbom\b"), ("FOCUS (FinOps)", r"finops open cost|focus (cost|export)s?"),
]
# Files whose presence evidences a standard (observed from the repo tree)
STANDARD_FILES = [
 ("OpenAPI", r"(^|/)(openapi|swagger)[^/]*\.(ya?ml|json)$"), ("RDF / OWL / SHACL", r"\.(ttl|rdf|owl|nt|jsonld)$"),
 ("Frictionless Data Package", r"(^|/)datapackage\.json$"), ("CSVW", r"-metadata\.json$|(^|/)csv-metadata\.json$"),
 ("JSON Schema", r"\.schema\.json$|(^|/)schemas?/[^/]+\.json$"), ("OGC / GeoJSON", r"\.geojson$"), ("CycloneDX / SPDX (SBOM)", r"(^|/)(sbom|bom)\.(json|xml)$|\.spdx(\.json)?$|\.cdx\.json$"),
 ("security.txt (RFC 9116)", r"(^|/)security\.txt$"), ("FHIR", r"(^|/)(fhir|structuredefinition)[^/]*\.(json|xml)$"),
]
DAM_RX = r"\b(critical data assets?|data assets?|information assets?|(information|data) asset registers?|asset registers?|esda|essential shared data|(dataset|data|open|descriptive|statistical|geospatial|records?) metadata|metadata (catalog(ue)?s?|standards?|models?|schemas? for (data|datasets)|management|registry|registries|exchange|profiles?|vocabular(y|ies)|repositor(y|ies)|harvest(er|ing)?|publishing)|dcat|data ?catalog(ue)?s?|dataset catalog(ue)?s?|catalogue of (data|datasets)|data marketplace|data discovery|data dictionar(y|ies)|business glossar(y|ies)|data lineage|data ownership|data owners?|data stewardship (framework|model|roles?|policy)|dqap|purview|collibra|open ?metadata|amundsen|ckan|metadata exchange model|records management|data vocab(ulary)?)\b"
# Generic product/service names that collide with DAM terms in a different sense (precision guard)
DAM_EXCLUDE = re.compile(r"\b(data stewardship team|library (book|catalogue)|weather ?data ?hub|datahub (query|metrics)|model[- ]run metadata|image metadata|exif|photo metadata|music metadata)\b", re.I)

CS = {s[0]: re.compile(s[5], re.I) for s in STRATEGY}
STD = [(n, re.compile(rx, re.I)) for n, rx in STANDARDS]
STDF = [(n, re.compile(rx, re.I)) for n, rx in STANDARD_FILES]
DAMC = re.compile(DAM_RX, re.I)

def split_name(s):
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", s or "")       # InformationAsset -> Information Asset
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", s)
    return s

def norm(*parts):
    t = " ".join(split_name(p) for p in parts if p)
    t = re.sub(r"[-_/.]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()

def readme_lede(text, limit=400):
    """First prose paragraph of a README: skips headings, badges, HTML, tables, code fences and link-only lines."""
    if not text: return ""
    out, in_code = [], False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("```"): in_code = not in_code; continue
        if in_code: continue
        if not s:
            if out: break
            continue
        if s.startswith(("#", "!", "[!", "<", "|", "---", "===", "[![", ">", "*", "-", "=")) or re.fullmatch(r"(\[[^\]]*\]\([^)]*\)\s*)+", s):
            if out: break
            continue
        out.append(re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", re.sub(r"`([^`]*)`", r"\1", s)))
        if len(" ".join(out)) > limit: break
    return " ".join(out)[:limit]

def tag(name, desc, topics, lede="", sector=""):
    strong = norm(name, desc, (topics or "").replace(",", " "))
    full = norm(strong, lede)
    tags = {}
    for sid, rx in CS.items():
        m = rx.search(full)
        if not m: continue
        if sid == "LOCAL" and sector != "Local government" and not rx.search(norm(name, (topics or "").replace(",", " "))):
            continue                                         # 'central and local government APIs' is not local digital work
        if sid == "BP2" and m.group(0).lower() == "ai":
            if not re.search(r"(^|\s)ai(\s|$)", strong, re.I): continue   # bare 'AI' counts in name/description/topics, not README prose
        tags[sid] = m.group(0).lower()
    if DAM_EXCLUDE.search(full):                                      # e.g. 'model-run metadata', 'Weather DataHub'
        for k in ("DF3", "DF5"):
            if tags.get(k) in ("metadata", "datahub"): tags.pop(k)
    stds = sorted({n for n, rx in STD if rx.search(full)})
    dm = DAMC.search(full)
    dam = dm.group(0).lower() if dm and not DAM_EXCLUDE.search(full) else None
    return tags, stds, dam

def standards_from_files(paths):
    found = {}
    for n, rx in STDF:
        k = sum(1 for p in paths if rx.search(p))
        if k: found[n] = k
    return found

COMMUNITY = {"osgeouk", "x-govuk", "nhs-r-community", "nhs-oa-community", "ukgovld", "iquod", "localgovdigital", "tanc-ahrc"}
def sector(org, section):
    o = org.lower()
    if o in COMMUNITY: return "Communities and partnerships"
    LOCAL = {"lbhackney-it", "lbhounslow", "rothgov", "wfcouncil", "smbc-digital", "warwickshire", "localgovdrupal",
             "lgss", "cityofyork", "kentcc", "devoncc", "gmfrs", "wmfs", "ukfrs-cddfrs", "ukfrs-hertsfrs", "rushmoor", "wealden", "klbc-webteam", "bathnesdevelopment", "surreydigitalservices", "transportforlondon"}
    if section.endswith("Councils") or o in LOCAL or "council" in o or "borough" in o:
        return "Local government"
    if o.startswith("nhs") or "nhs" in o or o in ("nice-digital", "gosh-dre", "nottmhospitals", "the-strategy-unit", "mhra", "carequalitycommission", "cdu-data-science-team", "birmingham-and-solihull-ics", "nottingham-and-nottinghamshire-ics", "nw-gmsa", "ukhsa-collaboration", "ukhsa-internal", "dhsc-govuk", "technologyenhancedlearning", "111online"):
        return "Health and care"
    if o in ("ukparliament", "ukparlidata", "houseofcommonslibrary", "scottishparliament"):
        return "Parliament"
    if any(k in o for k in ("scot", "edinburgh", "dundee", "glasgow", "highland", "falkirk", "marinescotland")):
        return "Scotland"
    if any(k in o for k in ("wales", "cymru", "nwisbeta", "cdps", "llgc")):
        return "Wales"
    return "UK central government and ALBs"
