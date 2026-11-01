"""GDS responsibilities lens (31 Oct 2026): which repositories GDS builds for each area it is responsible for, and which repositories
elsewhere in the public sector are linked to that area (they use its components, name its products, or work on its standards).
Areas follow GDS's published responsibilities and the five teams it was formed from (gov.uk/government/organisations/government-digital-service/about,
read 31 Oct 2026). GDS's internal directorate names aren't published, so the mapping to units is assessed, not official.
Writes dama/gds.json and dama/gds_checks.txt."""
import json, re, gzip, os, sys, collections
H = os.path.dirname(os.path.abspath(__file__)); S = os.path.dirname(H); sys.path.insert(0, H)
from rules import w
ENR = f"{S}/xgov/enr"; DEPS = f"{H}/deps"; I = re.I
AREAS = [
 # id, label, unit (as published), what it covers, owned-repo name rule, cross-government text rule, dependency rule
 ("govuk", "GOV.UK and the GOV.UK app", "GOV.UK (product strategy and delivery)", "The GOV.UK website, its publishing platform, search, the GOV.UK App and GOV.UK Chat.",
  w(r"govuk", r"gov\.uk", r"whitehall", r"publishing", r"publisher", r"content[- ]store", r"router", r"search[- ]api", r"collections", r"frontend", r"govuk[- ]chat", r"smart[- ]answers", r"email[- ]alert", r"signon", r"asset[- ]manager", r"static", r"mainstream"),
  w(r"gov\.uk content api", r"govuk content api", r"content[- ]store", r"gov\.uk search api", r"govuk[- ]chat", r"gov\.uk app", r"govuk app", r"publishing[- ]api"), w(r"gds-api-adapters", r"govuk_publishing_components", r"govuk_app_config", r"slimmer")),
 ("components", "Design system and common components", "GOV.UK common components (Design System, Prototype Kit, Notify, Pay, Forms)", "Shared building blocks every service can use: the GOV.UK Design System and Frontend, the Prototype Kit, GOV.UK Notify, GOV.UK Pay and GOV.UK Forms.",
  w(r"design[- ]system", r"govuk[- ]frontend", r"prototype[- ]kit", r"notif(?:y|ications)", r"pay", r"forms?", r"components?", r"accessibility"),
  w(r"gov\.?uk[- ]frontend", r"gov\.uk design system", r"govuk design system", r"prototype[- ]kit", r"gov\.uk notify", r"govuk notify", r"notify api", r"gov\.uk pay", r"govuk pay", r"gov\.uk forms", r"govuk forms"),
  w(r"govuk-frontend", r"govuk-prototype-kit", r"notifications-python-client", r"notifications-node-client", r"notifications-java-client", r"notifications-ruby-client", r"notifications-net-client", r"govuk-frontend-jinja", r"govuk-frontend-wtf", r"govuk_design_system_formbuilder", r"govuk-components", r"@x-govuk/govuk-prototype-components", r"govuk-frontend-react", r"@ministryofjustice/frontend", r"hmrc-frontend", r"play-frontend-hmrc", r"play-frontend-govuk", r"govuk-react")),
 ("onelogin", "GOV.UK One Login and digital identity", "GOV.UK One Login (with the GOV.UK Wallet)", "Signing in and proving identity once for government services, and the GOV.UK Wallet for digital credentials.",
  w(r"one[- ]?login", r"identity", r"wallet", r"auth", r"di", r"ipv", r"credential"),
  w(r"gov\.?uk one login", r"govuk[- ]one[- ]login", r"one login", r"gov\.uk wallet", r"govuk wallet", r"gov\.uk sign in", r"govuk sign in", r"gov\.uk verify", r"govuk verify"),
  w(r"@govuk-one-login/[a-z0-9-]+", r"di-ipv-[a-z0-9-]+", r"govuk-one-login-[a-z0-9-]+")),
 ("ai", "AI products and adoption", "Incubator for Artificial Intelligence (i.AI) and AI products", "AI tools built for use across government, and the AI accelerator programme.",
  w(r"ai", r"llm", r"genai", r"chat", r"assistant", r"rag", r"model"),
  w(r"i\.ai", r"i-dot-ai", r"incubator for (?:artificial intelligence|ai)", r"humphrey", r"redbox", r"gov\.uk chat"), None),
 ("data", "Government data, standards and the National Data Library", "Government Data (former Central Digital and Data Office data teams) and the National Data Library", "Data standards, metadata, data catalogues and data.gov.uk, the API catalogue, the data marketplace and the National Data Library.",
  w(r"data", r"metadata", r"catalog(?:ue)?", r"dcat", r"api[- ]catalogue", r"registers?", r"standards?", r"ndl", r"datagovuk", r"data[- ]marketplace"),
  w(r"data standards authority", r"national data library", r"data marketplace", r"api catalogue", r"api\.gov\.uk", r"xgov mem", r"metadata exchange model", r"data\.gov\.uk", r"datagovuk", r"gov\.uk registers", r"cross[- ]government metadata"), w(r"ckanapi")),
 ("geo", "Geospatial data and the National Underground Asset Register", "Geospatial Commission (and the National Underground Asset Register)", "Location data, open identifiers for addresses and streets, and the register of underground pipes and cables.",
  w(r"geo", r"geospatial", r"nuar", r"location", r"uprn"),
  w(r"geospatial commission", r"national underground asset register", r"nuar", r"uprn", r"usrn", r"open identifiers"), None),
 ("cyber", "Cyber security and vulnerability scanning", "Cross-government vulnerability scanning and security services", "The cross-government vulnerability scanning service and shared security tools: secure domains, email security, and Secure by Design.",
  w(r"security", r"cyber", r"vulnerabilit(?:y|ies)", r"vulns?", r"(?:gov\.?uk|govuk|service|parked|ukps)[- ]domains?", r"domains?[- ](?:register|management|checker|admin|iac)", r"dns", r"dmarc", r"email[- ]security", r"sbd", r"secure[- ]by[- ]design", r"gc3", r"scanning"),
  w(r"vulnerability scanning service", r"secure by design", r"gc3", r"government cyber coordination", r"mail check", r"web check", r"domain protect", r"cyber assessment framework", r"govassure"), None),
 ("standards", "Digital standards, strategy and performance", "Digital strategy, standards and performance (Service Manual, function leadership)", "Setting digital strategy, the Service Manual and Service Standard, the Technology Code of Practice, measuring digital performance and leading the Government Digital and Data function.",
  w(r"service[- ]manual", r"service[- ]standard", r"standards?", r"strategy", r"performance", r"gds[- ]way", r"maturity", r"spend[- ]control", r"profession", r"function", r"technology code"),
  w(r"(?<!nhs )(?<!nhs digital )service standard", r"(?<!nhs )(?<!nhs digital )service manual", r"technology code of practice", r"gds way", r"digital performance", r"spend controls?", r"service assessments?", r"government digital and data function"), None),
 ("responsible", "Responsible technology and algorithmic transparency", "Responsible Technology Adoption Unit", "The Algorithmic Transparency Recording Standard and guidance for adopting AI and data-driven technology responsibly.",
  w(r"atrs", r"algorithmic", r"transparency", r"responsible", r"assurance", r"fairness", r"model[- ]cards?", r"ethics"),
  w(r"algorithmic transparency", r"atrs", r"responsible ai", r"ai assurance", r"model cards?", r"bias audit", r"fairness toolkit"), None),
 ("procure", "Digital procurement", "Public sector digital procurement reform", "How government buys digital and technology: frameworks, marketplaces and contract data.",
  w(r"procurement", r"marketplace", r"g-?cloud", r"tender", r"contracts?", r"spend"),
  w(r"digital marketplace", r"g-cloud(?: ?\d+| framework)?", r"digital outcomes and specialists", r"open contracting", r"contracts finder", r"find a tender"), None),
 ("platform", "Shared platforms and hosting", "Shared platforms (former GOV.UK PaaS and operations)", "Shared hosting and operations platforms GDS has run for other teams, such as GOV.UK PaaS (now retired).",
  w(r"paas", r"platform", r"infrastructure", r"terraform", r"operations", r"cloud[- ]foundry", r"concourse", r"hosting", r"ops"),
  w(r"gov\.uk paas", r"govuk[- ]paas", r"govuk paas"), None),
]
ACCOUNT_AREA = {"govuk-one-login": "onelogin", "govuk-pay": "components", "govuk-forms": "components", "i-dot-ai": "ai", "datagovuk": "data", "openregister": "data", "ukgovdatascience": "data",
                "govuk-paas": "platform", "gds-operations": "platform", "CDEIUK": "responsible", "govuk-digital-backbone": "platform"}
GDS_ACCOUNTS = {"alphagov", "govuk-once", "i-dot-ai", "govuk-digital-backbone", "govuk-one-login", "govuk-pay", "gds-operations", "co-cddo", "datagovuk", "ukgovdatascience", "govuk-forms", "govuk-paas", "openregister", "gds-dead", "gds-dtx", "CDEIUK"}
ORDER_OWNED = ["components", "onelogin", "ai", "cyber", "data", "responsible", "procure", "geo", "standards", "platform", "govuk"]   # specific before general
def snip(t, m): a = max(0, m.start() - 40); return re.sub(r"\s+", " ", t[a:m.end() + 40]).strip()[:110]
if __name__ == "__main__":
    D = json.load(open(f"{S}/uses/D5.json")); XO = D["xorgs"]
    recs = [(XO[dict(zip(D["xf"], a))["oi"]]["org"], dict(zip(D["xf"], a))["n"], " ".join(str(dict(zip(D["xf"], a)).get(k) or "") for k in ("n", "d", "ld", "t"))) for a in D["xrows"]]
    recs += [(XO[dict(zip(D["cf"], a))["oi"]]["org"], dict(zip(D["cf"], a))["n"], " ".join(str(dict(zip(D["cf"], a)).get(k) or "") for k in ("n", "d"))) for a in D["cat"]]
    A = {a[0]: a for a in AREAS}; owned = {}; linked = {}
    for org, n, basic in recs:
        key = f"{org}/{n}"; bas = basic.replace("-", " ").replace("_", " ") + " " + basic
        if org in GDS_ACCOUNTS:
            ar = ACCOUNT_AREA.get(org)
            if not ar:
                for aid in ORDER_OWNED:
                    if re.search(A[aid][4], bas, I): ar = aid; break
            owned[key] = ar or "other"; continue
        e = f"{ENR}/{org}__{n}"; readme = ""
        if os.path.isdir(e):
            try: readme = open(f"{e}/readme.txt", errors="replace").read()[:20000]
            except FileNotFoundError: pass
        deps = []
        if os.path.exists(f"{DEPS}/{org}__{n}.json"): deps = [x[1] for x in json.load(open(f"{DEPS}/{org}__{n}.json"))["deps"]]
        hits = []
        for a in AREAS:
            ev = []
            dr = a[6]
            if dr:
                dh = next((x for x in deps if re.fullmatch(dr, x, I)), None)
                if dh: ev.append(["dependency", dh])
            m = re.search(a[5], bas, I)
            if m: ev.append(["name", snip(bas, m)])
            elif readme:
                m = re.search(a[5], readme, I)
                if m: ev.append(["readme", snip(readme, m)])
            if ev: hits.append([a[0], "".join(sorted({{"dependency": "d", "name": "n", "readme": "r"}[k[0]] for k in ev})), ev[0][1]])
        if hits: linked[key] = hits
    out = {"areas": [dict(id=a[0], label=a[1], unit=a[2], desc=a[3]) for a in AREAS], "owned": owned, "linked": linked,
           "source": {"url": "https://www.gov.uk/government/organisations/government-digital-service/about", "read": "2026-10-31", "department": "Department for Digital, Culture, Media and Sport (DCMS)",
                      "formed_from": ["Central Digital and Data Office (CDDO)", "Geospatial Commission", "Government Digital Service", "Incubator for Artificial Intelligence (i.AI)", "Responsible Technology Adoption Unit"]},
           "deps_fetched": len(os.listdir(DEPS)),
           "prec": {"judged_by": "Claude, 31 October 2026 (not owner-confirmed)", "rounds": [
              {"what": "links other than the design system and components", "n": 15, "true": 11, "note": "the NHS service manual and prototype kit counted as GDS's; now excluded"},
              {"what": "design system and component links", "n": 10, "true": 9, "note": "NHS.UK frontend counted as GOV.UK Frontend; now excluded"},
              {"what": "GDS repositories placed in the cyber security area (all 68 reviewed)", "n": 68, "true": 55, "note": "'domain' and 'vulnerable' matched the GOV.UK router and a service for vulnerable people; now need security words. Verify and cookie repositories matched 'security' and remain in the area"}]}}
    json.dump(out, open(f"{H}/gds.json", "w"), separators=(",", ":"))
    lines = []
    def ck(cid, ok, text, g=""): lines.append(f"{'PASS' if ok else 'FAIL'} {cid} {text}" + (f" [guards: {g}]" if g else ""))
    ck("C-GDS-01", all(owned[k] in A or owned[k] == "other" for k in owned) and not (set(owned) & set(linked)), f"{len(owned)} GDS repositories each sit in one responsibility area (or 'other'); no GDS repository is also counted as a link from elsewhere", "V7-7")
    ck("C-GDS-02", not re.search(A["components"][5], "notify the user when the form loads", I) and re.search(A["components"][5], "uses GOV.UK Notify to send emails", I) and not re.search(A["procure"][5], "gcloud auth login then deploy", I) and re.search(A["procure"][5], "listed on G-Cloud 14", I) and not re.search(A["standards"][5], "the NHS digital service manual", I) and re.search(A["standards"][5], "meets the GOV.UK Service Standard", I), "cross-government links need the product's own name: 'notify the user' isn't GOV.UK Notify the gcloud tool isn't G-Cloud, and the NHS service manual isn't GDS's (negative tests)", "V7-7")
    ck("C-GDS-04", not re.search(A["cyber"][4], "router in front of GOV.UK to proxy to backend servers on the single domain", I) and not re.search(A["cyber"][4], "service for shielded vulnerable people", I) and re.search(A["cyber"][4], "register a govuk domain", I) and re.search(A["cyber"][4], "vulnerability reporting", I), "GDS's cyber area needs security words: a router on a single domain and a service for vulnerable people are not cyber; registering a GOV.UK domain and vulnerability reporting are (negative tests)", "V7-15")
    ck("C-GDS-03", len(AREAS) == 11 and all(a[2] for a in AREAS), "every area names the published GDS responsibility or unit it maps to", "V7-7")
    open(f"{H}/gds_checks.txt", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines)); print("owned", len(owned), collections.Counter(owned.values())); print("linked", len(linked), collections.Counter(h[0] for v in linked.values() for h in v))
