"""Subjects: what each project is about, classified to GOV.UK's topic taxonomy (level one), 7.6 (R43).

Source of the subject list: GOV.UK content API, https://www.gov.uk/api/content/ links.level_one_taxons (20 taxons, root
updated 18 February 2026, read 1 November 2026). 'Corporate information' is left out: it describes departments' own
publications, not what code is about.
Input: build/xgov/xgov.json rows (name, description, README summary, topics) and build/catalogue/catalogue.json (name,
description). Text is matched on word boundaries with exclusions for code words that look like subjects (health check,
transport layer, test environment). Up to two subjects per project: most distinct matching words first, then the longer, more specific match. Where the text says nothing, three
publisher sectors give a subject (Health and care, Local government, Parliament), marked 'from the publisher'.
Writes subjects.json and subjects_checks.txt. Run with python3 -I. Exit code 1 if a check fails.
"""
import json, os, re, sys, collections
S = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(S); I = re.I
B, E = r"(?<![a-z0-9])", r"(?![a-z0-9])"
w = lambda *a: re.compile(B + "(?:" + "|".join(a) + ")" + E, I)
TAXON_SOURCE = "GOV.UK topic taxonomy, level one (https://www.gov.uk/api/content/ links.level_one_taxons, read 1 November 2026)"
SUBJ = [  # id, GOV.UK title, base path, rule, plain description
 ("health", "Health and social care", "/health-and-social-care", w(r"nhs", r"health(?:care| care| service| services| data| records?| and social care| visitors?| outcomes| inequalit\w+)", r"public health", r"patients?", r"clinical", r"clinicians?", r"hospitals?", r"gp (?:practices?|surgeries|data)", r"general practice", r"social care", r"care homes?", r"adult social", r"medicines?", r"prescri\w+", r"vaccin\w+", r"immunis\w+", r"disease", r"mental health", r"dental", r"pharmac\w+", r"nursing", r"ambulance", r"a&e", r"maternity", r"cancer", r"covid(?:-19)?", r"pandemic", r"epidemiolog\w+", r"snomed", r"fhir", r"hl7"), "Health, care, the NHS and public health."),
 ("money", "Money", "/money", w(r"tax(?:es|ation|payers?| returns?| credits?| codes?)?", r"vat", r"hmrc", r"self assessment", r"customs", r"duty", r"excise", r"tariffs?", r"payroll", r"paye", r"national insurance", r"pensions? tax", r"student loans?", r"debt(?! ?collector)", r"personal finance", r"budget(?:s|ing)? (?:for|planning)", r"public spending", r"spend(?:ing)? data", r"treasury", r"grants?(?: funding| management| applications?)", r"financ(?:e|ial) (?:data|reporting|services|management)", r"accounts? payable", r"invoices?", r"payments?(?! gateway sdk)"), "Tax, payments, public money, grants and personal finance."),
 ("justice", "Crime, justice and law", "/crime-justice-and-law", w(r"courts?(?! of)", r"tribunals?", r"justice", r"prisons?", r"probation", r"offenders?", r"crime", r"criminal", r"police", r"policing", r"legal aid", r"legislation", r"statutory instruments?", r"laws? of", r"case law", r"judges?", r"judicial", r"sentenc\w+", r"victims?", r"fraud", r"counter[- ]fraud", r"youth justice", r"magistrates?"), "Courts, tribunals, prisons, policing, crime and the law."),
 ("defence", "Defence and armed forces", "/defence-and-armed-forces", w(r"defen[cs]e(?! in depth)", r"armed forces", r"military", r"ministry of defence", r"(?<!swiss )army", r"royal navy", r"raf", r"royal air force", r"veterans?", r"dstl", r"nato"), "Defence, the armed forces and veterans."),
 ("work", "Work", "/work", w(r"employ(?:ment|ers?|ees?)", r"jobs?(?:centre| seekers?| market| vacanc\w+)", r"job ?centre", r"recruit\w+", r"apprentice\w+", r"workforce", r"working conditions", r"minimum wage", r"labour market", r"careers? (?:advice|service)", r"pensions?(?! tax)", r"redundanc\w+", r"right to work"), "Jobs, employment, pay, pensions and working life."),
 ("life", "Life circumstances", "/life-circumstances", w(r"births?", r"deaths?", r"bereavement", r"marriages?", r"civil partnerships?", r"disabled people", r"disabilit(?:y|ies)", r"carers?", r"lasting power of attorney", r"power of attorney", r"making a will", r"wills and probate", r"probate", r"tell us once", r"life events?"), "Births, deaths, marriages, disability, caring and life events."),
 ("welfare", "Welfare", "/welfare", w(r"benefits? (?:system|claims?|claimants?|payments?|entitlement|calculator)", r"universal credit", r"welfare", r"dwp", r"child benefit", r"housing benefit", r"jobseeker'?s allowance", r"personal independence payment", r"state pension", r"attendance allowance", r"carer'?s allowance", r"cost of living"), "Benefits, Universal Credit and state support."),
 ("housing", "Housing, local and community", "/housing-local-and-community", w(r"housing", r"homes? (?:england|building)", r"homeless\w*", r"planning (?:applications?|permission|policy|data|system)", r"building (?:regulations|safety|control)", r"hm land registry", r"land (?:registration|ownership|use)", r"property (?:data|market|prices?)", r"council tax", r"social housing", r"tenanc(?:y|ies)", r"landlords?", r"communit(?:y|ies) (?:groups?|cohesion|engagement)", r"local plans?", r"epc", r"energy performance certificates?"), "Housing, planning, land and property, and communities."),
 ("society", "Society and culture", "/society-and-culture", w(r"museums?", r"public librar(?:y|ies)", r"library services?", r"archives? (?:catalogue|collections?|records)", r"heritage", r"culture", r"cultural", r"arts? (?:council|collections?)", r"sports?", r"olympic\w*", r"charit(?:y|ies)", r"volunteer\w*", r"census", r"population (?:estimates|statistics|projections|census)", r"equalit(?:y|ies)", r"diversity", r"religio\w+", r"broadcast\w*", r"news ?papers?", r"gambling", r"lottery", r"tourism"), "Arts, heritage, sport, charities, media and society."),
 ("international", "International", "/international", w(r"international (?:development|aid|trade|relations)", r"foreign (?:office|policy|affairs)", r"fcdo", r"diplomat\w*", r"embass(?:y|ies)", r"overseas development", r"sanctions?", r"treaty", r"treaties", r"united nations", r"trade (?:agreements?|deals?|policy)", r"uk export finance", r"export (?:insurance|finance|licen[cs]\w+|controls?|declarations?|health certificates?|system|movements?)", r"declare exports?", r"imports? (?:and exports?|controls?|licen[cs]\w+)"), "Foreign affairs, international development and trade."),
 ("local", "Regional and local government", "/regional-and-local-government", w(r"local (?:government|authorit(?:y|ies)|councils?|services?)", r"councils?(?! of europe)", r"borough", r"county council", r"district council", r"unitary authorit\w+", r"combined authorit\w+", r"devolution deals?", r"mayor\w*", r"bin collections?", r"waste collections?", r"parking"), "Councils, local services and regional government."),
 ("government", "Government", "/government/all", w(r"civil servants?", r"civil service (?:jobs|hr|learning|people|statistics|pensions?)", r"parliament\w*", r"house of (?:commons|lords)", r"hansard", r"elections?", r"electoral", r"voters?", r"voting", r"machinery of government", r"cabinet office", r"public procurement", r"procurement (?:act|policy|notices?|data|regulations|reform)", r"government procurement", r"government spending", r"transparency (?:data|reports?)", r"freedom of information", r"foi requests?", r"public appointments?", r"ministers?", r"ministerial", r"government (?:departments?|digital|data|technology)", r"digital (?:government|public services)", r"public sector (?:data|digital|technology)"), "Government itself: Parliament, elections, the civil service, procurement and digital government."),
 ("environment", "Environment", "/environment", w(r"environmental", r"environment agency", r"natural environment", r"climate", r"net zero", r"carbon", r"emissions?", r"flood\w*", r"biodiversity", r"wildlife", r"air quality", r"water quality", r"rivers?", r"recycling", r"farming", r"farms?", r"agricultur\w+", r"countryside", r"forestry", r"tree (?:planting|preservation|health)", r"woodlands?", r"fisheries", r"marine", r"weather", r"met office", r"sustainab\w+", r"renewable", r"energy (?:efficiency|use|consumption|data)", r"natural england", r"ecolog\w+", r"pollution", r"animal (?:health|welfare)", r"plant health"), "Climate, nature, farming, flooding, energy use and pollution."),
 ("business", "Business and industry", "/business-and-industry", w(r"businesses", r"business (?:support|rates|grants?|registration|owners?|events?|data|growth|finance|licen[cs]\w+)", r"companies house", r"company (?:data|registers?|information)", r"industr(?:y|ies|ial)", r"manufactur\w+", r"small firms?", r"smes?", r"intellectual property", r"patents?", r"trade ?marks?", r"competition (?:law|markets)", r"consumer protection", r"insolvenc\w+", r"licensing (?:authorit\w+|act|applications?|registers?)", r"premises licen[cs]\w+", r"regulat(?:ed|ory|ion) (?:bodies|markets?|businesses)", r"telecoms?", r"broadband", r"postal"), "Companies, industry, trade marks, regulation and the economy."),
 ("transport", "Transport", "/transport", w(r"transport(?! layer| protocol|s? (?:for|in) (?:node|winston|logging))", r"dvla", r"dvsa", r"driving (?:licen[cs]es?|tests?|standards)", r"drivers?(?! (?:for|install|package))(?<!csi driver)(?<!device driver)(?<!jdbc driver)(?<!database driver)", r"vehicles?", r"roads?(?:map)?(?<!roadmap)", r"traffic", r"railways?", r"rail", r"trains?(?:ing)?(?<!training)", r"bus(?:es)? (?:services?|routes?|open data|data)", r"aviation", r"airports?", r"maritime", r"shipping", r"ports? (?:health|authority)", r"cycling", r"walking and cycling", r"mot", r"highways?", r"journey planner", r"naptan", r"gtfs"), "Roads, rail, buses, aviation, shipping, driving and vehicles."),
 ("education", "Education, training and skills", "/education", w(r"schools?", r"pupils?", r"teachers?", r"teaching", r"education(?:al)?", r"universit(?:y|ies)", r"students?", r"further education", r"higher education", r"colleges?", r"ofsted", r"exams?(?:inations?)?", r"qualifications?", r"curriculum", r"skills? (?:bootcamps?|england|funding)", r"learners?", r"training (?:providers?|courses?)", r"apprenticeships?", r"early years", r"send(?: support| provision)" ), "Schools, colleges, universities, qualifications and skills."),
 ("abroad", "Going and being abroad", "/going-and-being-abroad", w(r"passport (?:applications?|renewals?)", r"apply for a passport", r"travel advice", r"living abroad", r"british nationals? (?:abroad|overseas)", r"consular", r"foreign travel", r"overseas voters?", r"travel (?:documents?|alerts?)"), "Passports, travel advice and British people abroad."),
 ("entering", "Entering and staying in the UK", "/entering-staying-uk", w(r"visas?", r"immigration", r"border(?:s| force| control)", r"asylum", r"refugees?", r"migrants?", r"migration (?:data|statistics|policy)", r"settlement scheme", r"eu settlement", r"right to rent", r"citizenship", r"naturalisation"), "Visas, immigration, borders, asylum and citizenship."),
 ("children", "Parenting, childcare and children's services", "/childcare-parenting", w(r"children'?s (?:services|social care|social work|safeguarding|data)", r"child (?:protection|safeguarding|social care)", r"childcare", r"child ?minders?", r"nurser(?:y|ies)", r"foster(?:ing|ers?| care)", r"adopters?", r"adoption (?:services?|web|support|agenc\w+|orders?|cases?|applications?|shared)", r"child adoption", r"looked[- ]after children", r"children in care", r"safeguarding", r"parent(?:s|ing)(?! (?:node|element|class|directory|pom|folder|id))", r"young people", r"youth (?:services?|work)", r"family hubs?", r"childcare (?:costs?|account)"), "Childcare, parenting, children's services and safeguarding."),
]
NEG = w(r"(?:legal|claim|claimant'?s?|file a|submit a|respond with a) defen[cs]e", r"defen[cs]e (?:response|to (?:the |a )?claim|forms?)", r"prometheus exporters?", r"health ?checks?", r"healthz", r"health endpoint", r"(?:dev|test|staging|build|virtual|runtime|python|node|conda|local|development|production|deployment) environments?", r"environment variables?", r"\.env", r"transport layer", r"git ?parents?", r"tree ?shaking", r"budget ?alerts?", r"aws budgets?", r"cost (?:explorer|reports?) for aws", r"payment ?request api", r"student (?:project|exercise|assignment)s?")
# Precision, judged by Claude on 1 November 2026 from random samples of text-based matches (not owner-confirmed).
# Each row: subject, sample size and number right in the last round, and what earlier rounds found and fixed.
PREC = [("Health and social care", 6, 6, ""), ("Money", 6, 6, ""), ("Crime, justice and law", 6, 6, ""),
 ("Defence and armed forces", 6, 5, "'mod' matched the MoJ modernisation platform and 'army' a Swiss Army knife: both removed; a legal 'defence' in a civil money claims service is still matched"),
 ("Work", 6, 6, ""), ("Life circumstances", 6, 6, "'will' matched the verb and 'disabled' a feature flag: both narrowed"),
 ("Welfare", 6, 6, "'PIP' matched pip (Python) and an unrelated project: removed"), ("Housing, local and community", 6, 6, "'tenants' matched hosting-platform tenants: narrowed to tenancy"),
 ("Society and culture", 6, 6, "'media' and 'library collection' matched code words: removed"), ("International", 6, 6, "'export' matched data exports and Prometheus exporters: narrowed to trade exports"),
 ("Regional and local government", 6, 6, ""), ("Government", 6, 6, "'procurement' of infrastructure and 'civil service' in a platform module: narrowed"),
 ("Environment", 6, 6, "'Defra' as a word and 'tree' in a chart library: removed"), ("Business and industry", 6, 6, "'enterprise', 'business' and 'licensing' were too broad: narrowed"),
 ("Transport", 6, 5, "a Kubernetes 'CSI driver': excluded; 'driver' in a hazardous waste return is still matched"), ("Education, training and skills", 6, 6, "'DfE' as a word: removed"),
 ("Going and being abroad", 5, 5, "'passport' matched the Passport.js library and HM Passport Office code libraries: narrowed"),
 ("Entering and staying in the UK", 6, 6, "'Home Office' as a word covered policing too: removed"), ("Parenting, childcare and children's services", 6, 6, "'adoption' matched technology adoption and 'child services' Docker services: narrowed")]
PUBLISHER = {"Health and care": "health", "Local government": "local", "Parliament": "government"}
SI = {s[0]: i for i, s in enumerate(SUBJ)}

def classify(text):
    t = NEG.sub(" ", text); score = collections.Counter(); ev = {}
    for sid, title, path, rx, desc in SUBJ:
        ms = list(rx.finditer(t))
        if ms: score[sid] = len({m.group(0).lower() for m in ms}); ev[sid] = max((m.group(0) for m in ms), key=len)
    top = [s for s, _ in sorted(score.items(), key=lambda kv: (-kv[1], -len(ev[kv[0]]), SI[kv[0]]))][:2]
    return [(s, ev[s]) for s in top]

def need(ok, cid, text, lines, fails, guards="R43"):
    lines.append(f"{'PASS' if ok else 'FAIL'} {cid} {text} [guards: {guards}]"); print(lines[-1])
    if not ok: fails.append(cid)

if __name__ == "__main__":
    X = json.load(open(os.path.join(R, "xgov", "xgov.json"))); C = json.load(open(os.path.join(R, "catalogue", "catalogue.json")))
    SECT = {o["org"]: o["sector"] for o in X["orgs"]}
    recs = [(r["o"] + "/" + r["n"], " ".join(str(r.get(k) or "") for k in ("n", "d", "ld", "t")).replace("-", " ").replace("_", " "), SECT.get(r["o"], "")) for r in X["rows"]]
    for a in C["cat"]:
        o = dict(zip(C["cf"], a)); org = C["orgs"][o["oi"]]["org"]
        recs.append((org + "/" + o["n"], (str(o["n"]) + " " + str(o.get("d") or "")).replace("-", " ").replace("_", " "), C["orgs"][o["oi"]].get("sector", "")))
    _cd = os.path.join(S, "cdot.json")   # crown dependency and overseas territory repositories, verified directly against GitHub
    if os.path.exists(_cd):
        for _a in json.load(open(_cd))["accounts"]:
            if not _a.get("in_catalogue", True): continue   # only accounts confirmed as official
            for _r in _a["repos"]: recs.append((_a["account"] + "/" + _r["name"], (_r["name"] + " " + (_r.get("description") or "")).replace("-", " ").replace("_", " "), ""))
    out, basis = {}, collections.Counter()
    for key, text, sector in recs:
        if key in out: continue
        c = classify(text)
        if c: out[key] = [[SI[s], ev] for s, ev in c]; basis["text"] += 1
        elif PUBLISHER.get(sector): out[key] = [[SI[PUBLISHER[sector]], ""]]; basis["publisher"] += 1
    by = collections.Counter(SUBJ[v[0][0]][1] for v in out.values())
    lines, fails = [], []
    need(len(SUBJ) == 19 and all(p.startswith("/") for _, _, p, _, _ in SUBJ), "C-SUB-01", f"{len(SUBJ)} subjects, each a GOV.UK level-one taxon with its path ({TAXON_SOURCE}); Corporate information left out on purpose", lines, fails)
    need(len(out) > 0.25 * len({k for k, _, _ in recs}) and all(by[s[1]] > 0 for s in SUBJ), "C-SUB-02", f"{len(out):,} of {len({k for k, _, _ in recs}):,} projects have a subject ({basis['text']:,} from their own text, {basis['publisher']:,} from the publisher); every subject has projects", lines, fails)
    # negative tests: code words that look like subjects must not classify
    traps = ["Enables the AWS EBS CSI driver", "Feature disabled in config", "Technology adoption across the organisation", "Docker compose for child services", "Procurement of infrastructure for the platform", "Prometheus exporter for GitLab CI", "Disable the feature flag", "Component library collection", "Submit a defence to a claim", "The Cyber Swiss Army Knife", "This service will consume events", "Passport.js strategy for sign in", "Export the consignment as a zip", "Kubernetes health check endpoint", "Set up the test environment with environment variables", "SMTP transport layer for nodemailer", "Tree shaking for webpack", "AWS budget alerts for our account", "Development environment for Python"]
    tr = {t: classify(t) for t in traps}
    real = {"NHS patient records": "health", "Universal Credit payments": "welfare", "School pupils and teachers": "education", "Flood risk maps for rivers": "environment", "Visa and immigration casework": "entering", "Driving licence applications at the DVLA": "transport"}
    ok_real = all(classify(t) and classify(t)[0][0] == s for t, s in real.items())
    need(not any(tr.values()) and ok_real, "C-SUB-02n", f"negative tests: {len(traps)} code phrases that only look like subjects (health check, test environment, transport layer, tree shaking, AWS budgets) get no subject, and {len(real)} plain subject phrases get the right one", lines, fails)
    need(len(PREC) == len(SUBJ) and sum(r for _, _, r, _ in PREC) / sum(n for _, n, _, _ in PREC) >= 0.9, "C-SUB-03", f"precision on judged samples: {sum(r for _, _, r, _ in PREC)} of {sum(n for _, n, _, _ in PREC)} right across all {len(PREC)} subjects, judged by Claude, not owner-confirmed", lines, fails)
    json.dump(dict(source=TAXON_SOURCE, subjects=[[s[0], s[1], s[2], s[4]] for s in SUBJ], recs=out, basis=dict(basis), publisher_rule=PUBLISHER, prec=dict(judged_by="Claude, 1 November 2026 (not owner-confirmed)", rounds=PREC)), open(os.path.join(S, "subjects.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    open(os.path.join(S, "subjects_checks.txt"), "w").write("\n".join(lines) + "\n")
    print(dict(by.most_common()))
    sys.exit(1 if fails else 0)
