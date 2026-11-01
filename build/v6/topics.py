"""Topic definitions for v6 (keyword leads). Same patterns are emitted to JS. Run to see counts and random samples for a precision check."""
import json,re,random,sys,collections
TOPICS=[
 ("health","Health and care","NHS, hospitals, GP and patient services, clinical data",r"\b(nhs|health|healthcare|hospital|clinical|patient|gp|fhir|nhsuk|vaccin\w*|covid|pharmac\w*|dental|maternity|ambulance)\b"),
 ("socialcare","Social care","Adult and children's social care, care homes, safeguarding",r"\b(social[- ]care|adult[- ]social|children'?s[- ]social|care[- ]home\w*|safeguarding|carers?)\b"),
 ("education","Education, skills and young people","Schools, colleges, apprenticeships, students, teachers",r"\b(schools?|education|teachers?|teaching|pupils?|students?|apprenticeships?|skills|ofsted|further[- ]education|universit(y|ies)|early[- ]years|neet|qualifications?|childcare)\b"),
 ("business","Business and the economy","Companies, trade, exports, grants and regulation",r"\b(business(es)?|companies[- ]house|trade|exports?|imports?|grant[- ]funding|grants?[- ](service|scheme|funding|applications?)|procurement|tenders?|economy|economic|insolvency|tariffs?|small[- ]firms?)\b"),
 ("tax","Tax, money and benefits","Tax, customs, pensions, benefits and welfare",r"\b(tax|taxes|vat|income[- ]tax|pensions?|benefits?|universal[- ]credit|welfare|child[- ]benefit|customs|self[- ]assessment|national[- ]insurance)\b"),
 ("justice","Justice, courts and policing","Courts, tribunals, prisons, probation, police",r"\b(courts?|tribunals?|justice|prisons?|probation|police|policing|legal[- ]aid|crime|offender\w*|sentenc\w*)\b"),
 ("environment","Environment, farming and climate","Environment, farming, flooding, nature, climate and weather",r"\b(environmental|environment[- ]agency|farming|farmers?|agricultur\w*|flood\w*|climate|weather|biodiversity|species|marine|fisheries|air[- ]quality|water[- ]quality|carbon|emissions|net[- ]zero|waste)\b"),
 ("place","Maps, land, housing and transport","Geospatial data, addresses, planning, housing, roads and travel",r"\b(geospatial|gis|uprn|postcodes?|ordnance[- ]survey|os[- ]maps?|land[- ]registry|spatial|mapping|planning[- ](application|inspectorate|permission|portal)s?|housing|transport|roads?|rail|railways?|traffic|buses|vehicles?|dvla|dvsa)\b"),
 ("identity","Sign-in, forms, payments and notifications","GOV.UK One Login and other sign-in, form builders, GOV.UK Pay and Notify",r"\b(one[- ]login|govuk[- ]one[- ]login|sign[- ]in|login|authenticat\w*|identity[- ](provider|verification|service)|gov\.uk[- ]verify|verify[- ]hub|notify|govuk[- ]pay|gov\.uk[- ]pay|pay[- ](frontend|connector|api|integration)|form[- ]builder|forms?[- ](runner|service|builder|designer)|govuk[- ]forms)\b"),
 ("design","Design systems and accessibility","Design systems, prototype kits, design histories and accessibility",r"\b(design[- ]systems?|govuk[- ]frontend|nhsuk[- ]frontend|prototype[- ]kit|govuk[- ]prototype|accessib\w*|wcag|a11y|screen[- ]readers?|design[- ]histor(y|ies)|style[- ]guide|pattern[- ]library)\b"),
 ("data","Data, statistics and metadata","Data pipelines, statistics, catalogues, metadata and open data",r"\b(data[- ]?sets?|statistic\w*|metadata|catalogu?e?s?|open[- ]data|data[- ]pipelines?|etl|analytics|dashboards?|census|survey|sdmx|dcat|reproducible[- ]analytical|rap)\b"),
 ("ai","AI and machine learning","Artificial intelligence, large language models, machine learning",r"\b(ai|artificial[- ]intelligence|machine[- ]learning|llms?|gpt|genai|generative|chatbots?|nlp|natural[- ]language|language[- ]models?|embeddings|mcp|copilot|neural[- ]networks?|deep[- ]learning)\b"),
 ("security","Security and resilience","Cyber security, vulnerability scanning, secure configuration",r"\b(security|cyber|vulnerabilit\w*|threat[- ]\w+|siem|pentest\w*|ncsc|firewall|waf|dmarc|tls|hardening|secrets?[- ]scanning)\b"),
 ("cloud","Cloud and infrastructure","Hosting, Terraform, Kubernetes, AWS, Azure and GCP",r"\b(terraform|kubernetes|k8s|aws|azure|gcp|cloud|infrastructure|helm|docker|ansible|paas|hosting)\b"),
 ("welsh","Welsh language","Welsh language and bilingual services",r"\b(welsh|cymraeg|cymru|bilingual)\b"),
]
def load():
    D=json.load(open(sys.argv[1]))
    recs=[]
    for a in D["xrows"]:
        o=dict(zip(D["xf"],a)); org=D["xorgs"][o["oi"]]["org"]; q=" ".join(str(o.get(k) or "") for k in ("n","d","ld","t","l","g","s","dam"))
        recs.append((org+"/"+o["n"],(org+"/"+q).lower(),o["st"]))
    for a in D["cat"]:
        o=dict(zip(D["cf"],a)); org=D["xorgs"][o["oi"]]["org"]; q=" ".join(str(o.get(k) or "") for k in ("n","d","l","g","s","dam"))
        recs.append((org+"/"+o["n"],(org+"/"+q).lower(),o["st"]))
    return recs
if __name__=="__main__":
    recs=load(); random.seed(7)
    for k,l,desc,rx in TOPICS:
        R=re.compile(rx); hit=[r for r in recs if R.search(r[1])]
        live=[r for r in hit if r[2] in ("Active","Maintained")]
        orgs={r[0].split("/")[0] for r in hit}
        print(f"\n## {k}: {len(hit)} records, {len(live)} live, {len(orgs)} orgs")
        for r in random.sample(hit,min(12,len(hit))): print("   ",r[0][:60],"|",r[1][len(r[0]):][:90])
