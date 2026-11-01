"""Public services, capabilities, processes and workflows across the estate (7.7, R45 to R48).

For every project in the catalogue this classifies, from its name, description, README summary and topics:
  - the local public service it supports, as a local government function (FUNCTIONS: names follow the LGA's Local
    Government Functions List where it has a matching function; see FUNCTION_SOURCE);
  - the business capability it provides (CAPABILITIES), the process step it serves (PROCESSES) and the workflow or
    automation technology it uses (WORKFLOWS) - a model defined for this catalogue, labelled as such on the page;
  - supplier products and platforms it names (SUPPLIERS), which shows where third-party code sits in a service chain.
Each function also names its lead government department (policy owner) and the public service journeys it supports:
both are assessed by Claude from public sources and labelled as assessed, not official.
Input: build/xgov/xgov.json rows and build/catalogue/catalogue.json. Writes services.json and services_checks.txt.
Run with python3 -I. Exit code 1 if a check fails.
"""
import json, os, re, sys, collections
S = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(S); I = re.I
B, E = r"(?<![a-z0-9])", r"(?![a-z0-9])"
w = lambda *a: re.compile(B + "(?:" + "|".join(a) + ")" + E, I)
FUNCTION_SOURCE = "Function names follow the LGA Local Government Functions List (LGFL, esd standards) where it has a matching function"

# id, name, rule, lead department (assessed), journeys supported (assessed), plain description
FUNCTIONS = [
 ("adultcare", "Adult social care", w(r"adult social care", r"adult care", r"asc (?:data|portal|assessment|financial)", r"care act", r"care and support", r"care homes?", r"home care", r"domiciliary care", r"care packages?", r"social care direct payments?", r"direct payments (?:for|to) (?:care|carers|disabled people)", r"carers? assessments?", r"financial assessments? for care", r"care (?:home )?providers? (?:market|portal|data)", r"care quality commission", r"\bcqc\b", r"care needs?", r"reablement", r"day care", r"social workers? for adults", r"safeguarding adults"),
  "Department of Health and Social Care", ["Getting care and support", "Being a carer", "Leaving hospital", "Ageing and later life"], "Assessing and arranging care and support for adults and carers."),
 ("childcare_sc", "Children's social care", w(r"children'?s social care", r"children'?s services", r"child protection", r"safeguarding children", r"looked[- ]after children", r"children in care", r"care leavers?", r"fostering", r"foster carers?", r"adoption (?:services?|web|support|agenc\w+|orders?|cases?|shared)", r"adopters?", r"family hubs?", r"early help", r"children'?s social workers?", r"\bmash\b", r"special guardianship", r"family court", r"public law outline", r"children and families"),
  "Department for Education", ["Having a baby and early years", "Fostering and adoption", "Keeping children safe", "Leaving care"], "Protecting children, children in care, fostering, adoption and early help."),
 ("education", "Education and schools", w(r"schools? admissions?", r"school places?", r"admissions", r"special educational needs", r"\bsend\b(?= )(?=.*(?:support|needs|ehcp|provision))", r"\behcps?\b", r"education,? health and care plans?", r"school transport", r"free school meals", r"pupils?", r"schools?", r"early years", r"nurser(?:y|ies)", r"childcare (?:places?|funding|entitlement)", r"skills (?:bootcamps?|funding)"),
  "Department for Education", ["Starting school", "Moving schools", "Getting help with special educational needs"], "School places and admissions, special educational needs, early years and skills."),
 ("publichealth", "Public health", w(r"public health", r"health protection", r"sexual health", r"smoking cessation", r"stop smoking", r"health visiting", r"health visitors?", r"substance misuse", r"drug and alcohol", r"joint strategic needs assessment", r"\bjsna\b", r"health inequalit\w+", r"obesity", r"vaccinations?", r"immunisation", r"outbreaks?", r"disease surveillance"),
  "Department of Health and Social Care", ["Staying healthy", "Getting help with drugs or alcohol"], "Health improvement, health protection and public health intelligence."),
 ("housing", "Housing", w(r"housing", r"homeless\w*", r"temporary accommodation", r"social housing", r"housing register", r"housing allocations?", r"tenanc(?:y|ies)", r"repairs? (?:service|requests?|online)", r"housing repairs?", r"council homes?", r"right to buy", r"landlords?", r"houses in multiple occupation", r"\bhmos?\b", r"disabled facilities grants?", r"rent accounts?"),
  "Ministry of Housing, Communities and Local Government", ["Finding a home", "Becoming homeless", "Renting a home"], "Housing advice, homelessness, allocations, council homes and private renting."),
 ("planning", "Planning and building control", w(r"planning (?:applications?|permission|policy|data|portal|system|appeals?|enforcement|register)", r"local plans?", r"development management", r"building control", r"building regulations", r"land charges?", r"\bllc1\b", r"conservation areas?", r"listed buildings?", r"tree preservation orders?", r"brownfield", r"planning\.data", r"planning inspectorate", r"section 106", r"\bcil\b", r"community infrastructure levy"),
  "Ministry of Housing, Communities and Local Government", ["Building or extending a home", "Starting a business"], "Planning applications, local plans, building control and land charges."),
 ("revenues", "Revenues and benefits", w(r"council tax", r"business rates", r"non[- ]domestic rates", r"housing benefits?", r"council tax (?:support|reduction)", r"revenues and benefits", r"\bnndr\b", r"discretionary housing payments?", r"local welfare", r"household support fund", r"cost of living payments?"),
  "Ministry of Housing, Communities and Local Government", ["Moving home", "Paying council tax", "Getting help with living costs"], "Council tax, business rates, housing benefit and local welfare support."),
 ("waste", "Waste and recycling", w(r"waste", r"recycling", r"bins?(?! (?:directory|folder|path))", r"bin (?:collections?|days?|calendar)", r"refuse", r"fly[- ]?tipping", r"bulky (?:waste|items?)", r"garden waste", r"household waste", r"litter"),
  "Department for Environment, Food and Rural Affairs", ["Moving home"], "Bin collections, recycling, bulky waste, fly-tipping and waste sites."),
 ("highways", "Roads, highways and transport", w(r"highways? (?:england|authorit\w+|maintenance|assets?|network|inspections?)", r"national highways", r"road(?:s| works| closures?| maintenance| safety)", r"street ?works", r"potholes?", r"street lights?", r"street ?lighting", r"traffic (?:management|regulation orders?|signals?|counts?)", r"\btros?\b", r"parking", r"penalty charge notices?", r"blue badges?", r"concessionary (?:travel|fares)", r"bus passes?", r"bus (?:services?|routes?|open data|stops?)", r"school transport", r"public transport", r"active travel", r"cycl(?:e|ing) (?:lanes?|routes?|infrastructure)", r"electric vehicle charg\w+", r"\bev charg\w+"),
  "Department for Transport", ["Learning to drive and owning a vehicle", "Getting around"], "Road maintenance, street works, parking, blue badges, buses and active travel."),
 ("environment", "Environmental health and protection", w(r"environmental health", r"food (?:hygiene|safety) (?:ratings?|inspections?)", r"food standards", r"noise (?:complaints?|nuisance)", r"pest control", r"air quality", r"contaminated land", r"pollution", r"flood (?:risk|defen[cs]es?|warnings?|alerts?|management)", r"lead local flood", r"climate (?:emergency|action|change)", r"net zero", r"carbon (?:emissions?|reduction|footprint)", r"biodiversity", r"parks? and open spaces?", r"rights of way", r"countryside"),
  "Department for Environment, Food and Rural Affairs", ["Running a food business", "Reporting a problem"], "Food safety, noise and pollution, flooding, climate action, parks and the countryside."),
 ("licensing", "Licensing and regulation", w(r"licen[cs]ing", r"premises licen[cs]es?", r"alcohol licen[cs]es?", r"taxi (?:and private hire )?licen[cs]\w+", r"private hire", r"hackney carriage", r"street trading", r"gambling licen[cs]es?", r"trading standards", r"scams?", r"weights and measures", r"animal (?:licen[cs]\w+|welfare)", r"dog licen[cs]e"),
  "Home Office", ["Starting a business", "Running a food business"], "Premises, taxi, street trading and animal licences, and trading standards."),
 ("culture", "Libraries, culture and leisure", w(r"public librar(?:y|ies)", r"library (?:services?|catalogues?|cards?|members?|loans?)", r"libraries (?:service|unlimited|wales|ni)", r"museums?", r"archives? (?:service|catalogue|collections?)", r"heritage (?:collections?|sites?|assets?|lottery)", r"cultural heritage", r"historic environment", r"leisure centres?", r"sports? (?:centres?|facilities|bookings?)", r"arts? (?:council|centres?|venues?)", r"cultur\w+ (?:services?|venues?|events?)", r"events? (?:bookings?|calendar)", r"allotments?", r"tourism"),
  "Department for Culture, Media and Sport", ["Using local facilities"], "Libraries, museums, archives, leisure, sport, culture and events."),
 ("registration", "Registration and electoral services", w(r"register (?:a )?(?:birth|death|marriage)", r"register offices?", r"registration of (?:births|deaths|marriages)", r"births?,? deaths? and marriages?", r"registrars?", r"citizenship ceremon\w+", r"electoral (?:registration|register|services|roll)", r"elections?", r"polling (?:stations?|cards?|districts?)", r"voters?", r"postal votes?", r"canvass\w*", r"tell us once"),
  "Ministry of Housing, Communities and Local Government", ["Having a baby", "When someone dies", "Getting married", "Voting"], "Registering births, deaths and marriages, citizenship ceremonies, electoral registration and elections."),
 ("community", "Communities, safety and emergencies", w(r"community safety", r"anti[- ]social behaviour", r"domestic abuse", r"cctv", r"emergency planning", r"local resilience forums?", r"community resilience", r"civil contingencies", r"fire (?:and rescue|safety|services?|incidents?)", r"\bfrs\b", r"prevent (?:duty|programme|strategy)", r"community (?:groups?|grants?|centres?|engagement)", r"voluntary (?:sector|organisations?|groups?)", r"volunteer\w*", r"neighbourhood plans?", r"refugee resettlement", r"homes for ukraine", r"ukraine (?:sponsor|resettlement)", r"asylum dispersal"),
  "Ministry of Housing, Communities and Local Government", ["Reporting a problem", "Arriving in the UK as a refugee"], "Community safety, fire and rescue, emergency planning, community grants and resettlement."),
 ("economy", "Economy, business and employment", w(r"economic development", r"business support", r"business grants?", r"business growth", r"inward investment", r"regeneration", r"high streets?", r"town centres?", r"employment support", r"jobs? (?:fairs?|boards?|support)", r"skills (?:support|hub)", r"apprentice\w+", r"\bukspf\b", r"shared prosperity fund", r"levelling up", r"growth deals?", r"enterprise zones?", r"markets? (?:service|traders?)"),
  "Ministry of Housing, Communities and Local Government", ["Starting a business", "Looking for work"], "Business support and grants, regeneration, employment and skills support."),
 ("customer", "Customer services and council business", w(r"my council", r"council (?:customer|contact|services|portal)", r"report it (?:to the council|online)", r"council (?:website|intranet)", r"localgov ?drupal", r"democratic services", r"committee (?:meetings?|papers|minutes)", r"councillors?", r"\bmod\.gov\b", r"moderngov", r"council (?:complaints?|consultations?|open data)", r"local (?:open data|council data)"),
  "Ministry of Housing, Communities and Local Government", ["Reporting a problem", "Contacting the council"], "Websites, customer accounts, contact centres, complaints, democratic services and open data."),
]
CAPABILITIES = [
 ("identity", "Identity and sign-in", w(r"sign[- ]?in", r"log[- ]?in", r"authenticat\w+", r"identity (?:verification|provider|proofing)", r"one login", r"verify (?:your )?identity", r"single sign[- ]on", r"\bsso\b", r"oauth", r"openid", r"oidc", r"\bmfa\b", r"two[- ]factor", r"\bsaml\b")),
 ("payments", "Payments and fees", w(r"payments?", r"pay (?:for|online)", r"govuk pay", r"gov\.uk pay", r"card payments?", r"refunds?", r"invoic\w+", r"direct debits?", r"fees? (?:and payments?|calculation)", r"stripe", r"worldpay")),
 ("notify", "Notifications and messaging", w(r"notifications?", r"notify", r"govuk notify", r"gov\.uk notify", r"\bsms\b", r"text messages?", r"emails? (?:service|alerts?|notifications?|templates?)", r"letters? (?:printing|templates?)", r"reminders?", r"push notifications?")),
 ("forms", "Forms and applications", w(r"forms?(?! (?:of|a|the|part))", r"form builder", r"apply (?:for|online)", r"application (?:forms?|process|service)", r"submissions?", r"questionnaires?", r"surveys?", r"eligibility checkers?", r"check (?:if|whether) you")),
 ("casework", "Case management", w(r"case ?work(?:ers?|ing)?", r"case management", r"\bccd\b", r"cases?(?: (?:api|data|handling|tracking|records?|files?))", r"work ?allocation", r"tasks? (?:management|allocation|lists?)", r"caseload")),
 ("records", "Documents and records", w(r"documents? (?:management|store|storage|generation|upload|service)", r"records? management", r"evidence (?:upload|management)", r"file uploads?", r"pdf (?:generation|service)", r"digital archiv\w+", r"retention", r"scanning", r"bulk scan\w*")),
 ("booking", "Booking and scheduling", w(r"bookings?", r"book (?:a|an|your)", r"appointments?", r"schedul(?:e|ing)", r"calendars?", r"slots?(?! (?:machine|component))", r"rota")),
 ("content", "Content and publishing", w(r"content (?:management|publishing|design|api|store)", r"\bcms\b", r"publish(?:ing|er)", r"websites?", r"wordpress", r"drupal", r"static site", r"blog", r"guidance pages?", r"design system", r"frontend (?:toolkit|components?)")),
 ("data", "Data, analytics and reporting", w(r"data (?:platform|pipelines?|warehouse|lake|science|analysis|analytics|ingest\w*|engineering|products?|models?)", r"analytics", r"dashboards?", r"statistics", r"reporting", r"management information", r"\bmi\b (?:reports?|data)", r"business intelligence", r"power ?bi", r"tableau", r"etl", r"open data")),
 ("integration", "Integration and APIs", w(r"\bapis?\b", r"api gateway", r"integration", r"web ?hooks?", r"messag(?:e|ing) (?:queues?|bus|broker)", r"kafka", r"\bsqs\b", r"event[- ]driven", r"data (?:exchange|sharing|feeds?)", r"adapters?", r"connectors?")),
 ("geo", "Maps, places and addresses", w(r"maps?(?! ?(?:reduce|per|of|to|ping|ped))", r"mapping (?:tool|service|data)", r"geospatial", r"\bgis\b", r"\bgeo\w*", r"addresses?", r"address (?:lookup|base|finder)", r"\buprn\b", r"\busrn\b", r"postcodes?", r"ordnance survey", r"boundar(?:y|ies)", r"locations?")),
 ("search", "Search and discovery", w(r"search(?! engine optim)", r"find (?:a|an|your)", r"finder", r"directory", r"catalogues?", r"lookup", r"registers?")),
 ("calc", "Eligibility, calculation and decisions", w(r"eligibility", r"calculators?", r"calculat(?:e|ion|ions) (?:your|the amount|entitlement|fees?|payments?|tax|benefits?)", r"assessments? (?:engine|tool|rules)", r"rules engine", r"decision (?:engine|tables?|support|making)", r"\bdmn\b", r"means test\w*", r"entitlements?")),
 ("ai", "AI and automation", w(r"\bai\b", r"artificial intelligence", r"machine learning", r"\bml\b", r"\bllms?\b", r"large language models?", r"generative", r"chat ?bots?", r"\brag\b", r"natural language", r"\bnlp\b", r"computer vision", r"copilot", r"robotic process automation")),
 ("infra", "Hosting and infrastructure", w(r"terraform", r"kubernetes", r"\bk8s\b", r"helm", r"infrastructure", r"hosting", r"\baws\b", r"azure", r"gcp", r"cloud ?formation", r"docker", r"platform as a service", r"\bpaas\b", r"ansible")),
 ("security", "Security and monitoring", w(r"security", r"vulnerabilit\w+", r"threat", r"intrusion", r"firewall", r"\bwaf\b", r"monitoring", r"observability", r"logging", r"alerting", r"incident", r"cyber", r"pen(?:etration)? test\w*", r"secrets?")),
]
PROCESSES = [
 ("find", "Find information or a service", w(r"find (?:a|an|your|out)", r"search for", r"look ?up", r"check (?:if|whether|your|what)", r"guidance", r"information (?:service|about)", r"directory", r"signpost\w*")),
 ("apply", "Apply, register or request", w(r"apply(?:ing)? (?:for|online|to)", r"application forms?", r"register(?:ing)? (?:for|a|an|your)", r"registration", r"request(?:ing)? (?:a|an)", r"claims?", r"sign up", r"enrol\w*", r"submit (?:a|an|your)", r"report (?:a|an)")),
 ("verify", "Prove identity or eligibility", w(r"verify", r"verification", r"identity (?:checks?|verification|proofing)", r"eligibility", r"evidence (?:checks?|upload)", r"proof of (?:identity|address|age|eligibility)", r"checks? (?:against|eligibility)", r"right to (?:work|rent)")),
 ("assess", "Assess and decide", w(r"assess\w*", r"decid\w+", r"decisions? (?:on|about|letters?|making)", r"triage", r"reviews? of (?:applications?|cases?|decisions?)", r"approv\w+", r"adjudicat\w+", r"determin\w+", r"case ?work\w*", r"inspections?")),
 ("pay", "Pay or be paid", w(r"payments?", r"pay (?:for|online|a|your)", r"refunds?", r"fees? (?:and payments?|payments?|calculators?)", r"invoic\w+", r"grants? (?:payments?|funding|claims?)", r"reimburs\w+", r"funding (?:claims?|payments?)")),
 ("notify", "Tell people what happens next", w(r"notif\w+", r"notify", r"letters?", r"reminders?", r"alerts?", r"status (?:updates?|tracking|page)", r"track(?:ing)? (?:your|an|a|the) (?:application|case|claim|request)", r"outcomes? letters?")),
 ("deliver", "Deliver the service", w(r"issu(?:e|ing) (?:a|an|the)? ?(?:licen[cs]es?|certificates?|permits?|passports?|badges?)", r"bookings?", r"appointments?", r"(?:bin|waste|refuse) collections?", r"repairs?", r"allocations?", r"placements?", r"support plans?")),
 ("manage", "Manage, renew or change", w(r"manage (?:your|my|a)", r"renew (?:your|a|an)", r"renewals? of (?:licen[cs]es?|permits?|passports?)", r"change (?:your|of|a)", r"update (?:your|details)", r"(?:your|my|customer|user) accounts?", r"self[- ]service", r"cancel\w*", r"amend\w*")),
 ("complain", "Feedback, complaints and appeals", w(r"feedback", r"complaints?", r"appeals?", r"tribunals?", r"reviews? of decisions?", r"mandatory reconsideration", r"ombudsman", r"redress")),
 ("report", "Report, monitor and improve", w(r"report(?:ing|s)", r"returns?(?= (?:data|submissions?|service))", r"statistics", r"dashboards?", r"performance (?:data|indicators?|monitoring|reports?)", r"monitor(?:ing)?", r"audit\w*", r"evaluat\w+", r"management information", r"\bkpis?\b")),
]
WORKFLOWS = [
 ("actions", "GitHub Actions and CI/CD pipelines", w(r"github actions?", r"\.github/workflows", r"ci ?/ ?cd", r"continuous (?:integration|delivery|deployment)", r"pipelines?", r"jenkins", r"circle ?ci", r"travis", r"azure devops", r"gitlab ci", r"concourse")),
 ("bpm", "Business process and decision engines (BPMN, DMN)", w(r"camunda", r"flowable", r"activiti", r"\bbpmn\b", r"\bdmn\b", r"process engine", r"workflow engine", r"business process", r"decision model")),
 ("orchestration", "Data and job orchestration", w(r"airflow", r"dagster", r"prefect", r"luigi", r"step functions?", r"argo (?:workflows?)?", r"temporal", r"cron(?:jobs?)?", r"scheduled (?:jobs?|tasks?)", r"batch (?:jobs?|processing)", r"etl pipelines?", r"data pipelines?")),
 ("lowcode", "Low-code and automation platforms", w(r"power automate", r"power apps?", r"logic apps?", r"zapier", r"\bn8n\b", r"node[- ]red", r"robotic process automation", r"uipath", r"blue ?prism")),
 ("queues", "Messages, events and queues", w(r"kafka", r"rabbitmq", r"\bsqs\b", r"\bsns\b", r"service bus", r"event ?bridge", r"event[- ]driven", r"pub ?/ ?sub", r"message (?:queues?|broker|bus)", r"(?:event|message|queue|kafka) (?:listeners?|consumers?)")),
 ("case_wf", "Case and task workflows", w(r"work allocation", r"task (?:management|allocation|lists?|routing)", r"case (?:workflow|progression|lifecycle|states?)", r"state machines?", r"workflow (?:management|states?|api)", r"approvals? workflow")),
]
# supplier products and platforms named in code: a chain to third parties, read only from what the project itself says
SUPPLIERS = [
 ("Liquidlogic", w(r"liquid ?logic", r"\blcs\b(?= )", r"\blas\b system")), ("Mosaic (Servelec / OLM)", w(r"mosaic (?:case|social|system)", r"servelec")), ("Eclipse (OLM)", w(r"olm eclipse", r"eclipse (?:case|social care)")),
 ("Capita", w(r"capita(?! l)")), ("Civica", w(r"civica")), ("Northgate / NEC", w(r"northgate", r"nec software")), ("Idox (Uniform)", w(r"idox", r"uniform planning")),
 ("Granicus / GovDelivery", w(r"granicus", r"govdelivery", r"firmstep")), ("Jadu", w(r"\bjadu\b")), ("Salesforce", w(r"salesforce")), ("Microsoft Dynamics", w(r"dynamics ?365", r"microsoft dynamics", r"dataverse")),
 ("Netcall / Liberty Create", w(r"netcall", r"liberty create")), ("Whitespace (waste)", w(r"whitespace (?:waste|work)")), ("Bartec (waste)", w(r"bartec")), ("Yotta / Confirm (highways)", w(r"\byotta\b", r"confirm (?:asset|highways)")),
 ("Agilisys", w(r"agilisys")), ("ServiceNow", w(r"servicenow")), ("Zendesk", w(r"zendesk")), ("SAP", w(r"\bsap\b(?! ?ui5)")), ("Oracle", w(r"oracle (?:e-?business|erp|fusion|database)")),
 ("Esri / ArcGIS", w(r"\besri\b", r"arcgis")), ("Ordnance Survey", w(r"ordnance survey", r"os (?:places|names|maps|data hub)")), ("GOV.UK Pay", w(r"gov\.?uk pay", r"govuk-pay", r"pay-connector")), ("GOV.UK Notify", w(r"gov\.?uk notify", r"notifications-api", r"notify client")),
 ("GOV.UK One Login", w(r"one login", r"govuk-one-login")), ("Contentful", w(r"contentful")), ("WordPress", w(r"wordpress")), ("Drupal / LocalGov Drupal", w(r"drupal")),
]

# Precision, judged by Claude on 1 November 2026 from random samples of each category's strongest match (not owner-confirmed).
# Rows: (dimension, sample size, right, what earlier rounds found and fixed). Samples were redrawn after each fix.
PREC = [
 ("Local public services", 80, 73, "16 functions, 5 each. Fixed after round one: 'heritage' in Companies House heritage infrastructure, 'prevent' and 'resilience' as verbs, PCN (primary care networks), NPQ and agent registration, cattle vaccination, technology 'adoption', and generic customer service words now need a council context. Public health and communities were 3 of 5 before their last fix and weren't redrawn."),
 ("Capabilities", 48, 46, "16 capabilities, 3 each. Fixed: 'book' in a book, 'interface' in user interface, RPA (the Rural Payments Agency), generic 'calculate'."),
 ("Processes", 30, 27, "10 steps, 3 each. Fixed: 'application' meaning software, 'delivery' and 'provision' in platform code, 'account' meaning cloud accounts, 'evidence', 'proof of concept', 'inspectorate', 'renewal' of certificates, 'submitting' jobs."),
 ("Workflows", 17, 17, "6 kinds, 3 each (2 for decision engines, which have 2). Fixed: RPA (Rural Payments Agency), generic listeners and consumers."),
]

def rx_hits(rules, text, k=2):
    sc, ev = collections.Counter(), {}
    for i, r in enumerate(rules):
        rx = r[2] if len(r) > 2 and hasattr(r[2], "finditer") else r[1]
        ms = list(rx.finditer(text))
        if ms: sc[i] = len({m.group(0).lower() for m in ms}); ev[i] = max((m.group(0) for m in ms), key=len)
    return [[i, ev[i]] for i, _ in sorted(sc.items(), key=lambda kv: (-kv[1], -len(ev[kv[0]]), kv[0]))[:k]]

NEG = w(r"self assessment", r"public health (?:scotland|wales)(?:'s)?", r"(?:cattle|bovine|animal|livestock|poultry) vaccinations?", r"heritage (?:infrastructure|systems?|code|applications?)", r"(?:product|technology|tool|cloud|platform) adoption", r"health ?checks?", r"(?:dev|test|staging|build|virtual|runtime|python|node|local|development|production|deployment) environments?", r"environment variables?", r"library for", r"python library", r"javascript library", r"component library", r"utility library", r"client library")
def classify(text):
    t = NEG.sub(" ", text)
    return dict(f=rx_hits(FUNCTIONS, t, 2), c=rx_hits(CAPABILITIES, t, 3), p=rx_hits(PROCESSES, t, 2), wf=rx_hits(WORKFLOWS, t, 2), s=[[i, e] for i, e in rx_hits([(n, r) for n, r in SUPPLIERS], t, 4)])

def need(ok, cid, text, lines, fails, guards):
    lines.append(f"{'PASS' if ok else 'FAIL'} {cid} {text} [guards: {guards}]"); print(lines[-1])
    if not ok: fails.append(cid)

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
        if any(c.values()): out[key] = {k: v for k, v in c.items() if v}
    cnt = {k: collections.Counter(v[k][0][0] for v in out.values() if k in v) for k in ("f", "c", "p", "wf")}
    sup = collections.Counter(i for v in out.values() for i, _ in v.get("s", []))
    lines, fails = [], []
    need(all(cnt["f"][i] for i in range(len(FUNCTIONS))), "C-SVC-01", f"{len(FUNCTIONS)} local public service functions, each with a lead department and the journeys it supports, and every function found in at least one project ({sum(cnt['f'].values()):,} projects in all)", lines, fails, "R45, R46")
    need(all(cnt["c"][i] for i in range(len(CAPABILITIES))) and all(cnt["p"][i] for i in range(len(PROCESSES))) and all(cnt["wf"][i] for i in range(len(WORKFLOWS))), "C-SVC-02", f"{len(CAPABILITIES)} capabilities, {len(PROCESSES)} process steps and {len(WORKFLOWS)} kinds of workflow, each found in projects ({sum(cnt['c'].values()):,}, {sum(cnt['p'].values()):,} and {sum(cnt['wf'].values()):,} projects)", lines, fails, "R45")
    traps = {"Cattle vaccination prototype": "f", "Heritage infrastructure in Terraform": "f", "Hooks to prevent secrets being committed": "f", "PCN capacity and access payment": "f", "NPQ registration service": "f", "Python library for parsing dates": "f", "Kubernetes health check endpoint": "f", "Set up the test environment": "f", "Component library for React": "f", "A cron job to rotate logs": "f"}
    real = {"Adult social care financial assessments": ("f", "adultcare"), "Fostering enquiry form for foster carers": ("f", "childcare_sc"), "Report a pothole and street lighting faults": ("f", "highways"), "Book a garden waste bin collection": ("f", "waste"), "Pay your council tax online": ("f", "revenues"), "Camunda BPMN workflow engine for casework": ("wf", "bpm")}
    idx = {"f": {r[0]: i for i, r in enumerate(FUNCTIONS)}, "wf": {r[0]: i for i, r in enumerate(WORKFLOWS)}}
    bad_t = [t for t, k in traps.items() if classify(t)[k]]
    bad_r = [t for t, (k, v) in real.items() if not classify(t)[k] or classify(t)[k][0][0] != idx[k][v]]
    need(not bad_t and not bad_r, "C-SVC-02n", f"negative tests: {len(traps)} phrases that only look like a service get none, and {len(real)} plain service phrases get the right one (wrong: {bad_t + bad_r})", lines, fails, "R45, R46")
    need(all(r / n >= 0.85 for _, n, r, _ in PREC), "C-SVC-03", "precision on judged samples: " + "; ".join(f"{d} {r} of {n}" for d, n, r, _ in PREC) + ", judged by Claude, not owner-confirmed", lines, fails, "R45, R46")
    json.dump(dict(function_source=FUNCTION_SOURCE, functions=[[f[0], f[1], f[3], f[4], f[5]] for f in FUNCTIONS], capabilities=[[c[0], c[1]] for c in CAPABILITIES], processes=[[p[0], p[1]] for p in PROCESSES],
                   workflows=[[x[0], x[1]] for x in WORKFLOWS], suppliers=[s[0] for s in SUPPLIERS], recs=out, assessed="Lead departments and journeys per function: assessed by Claude, 1 November 2026, from public sources; not official.", prec=dict(judged_by="Claude, 1 November 2026 (not owner-confirmed)", rounds=PREC)),
              open(os.path.join(S, "services.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    open(os.path.join(S, "services_checks.txt"), "w").write("\n".join(lines) + "\n")
    for k, rules in (("f", FUNCTIONS), ("c", CAPABILITIES), ("p", PROCESSES), ("wf", WORKFLOWS)): print(k, {rules[i][1]: n for i, n in cnt[k].most_common()})
    print("suppliers", {SUPPLIERS[i][0]: n for i, n in sup.most_common()})
    sys.exit(1 if fails else 0)
