"""Registers and authoritative sources: which projects maintain a public, statutory, regulatory or other legal register,
or an authoritative source of content, data, information or knowledge (7.8, R52).

Found from each project's name, description, README summary and topics. Kinds:
statutory and legal registers; regulatory and licensing registers; official records (births, deaths, judgments, land and
company records); authoritative reference data and code lists; transparency and public-interest registers; systems of
record and single sources of truth; authoritative published content (legislation, GOV.UK content, official statistics).
Classified from text and checked on samples; whether a register is statutory in law is assessed from its description,
not from the legislation, and is labelled as such on the page.
Input: build/xgov/xgov.json rows and build/catalogue/catalogue.json. Writes registers.json and registers_checks.txt.
Run with python3 -I. Exit code 1 if a check fails.
"""
import json, os, re, sys, collections
S = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(S); I = re.I
B, E = r"(?<![a-z0-9])", r"(?![a-z0-9])"
w = lambda *a: re.compile(B + "(?:" + "|".join(a) + ")" + E, I)
KINDS = [
 ("statutory", "Statutory and legal registers", "A register that a law requires a public body to keep, such as the electoral register, the land register or the register of companies.",
  w(r"statutory registers?", r"electoral registers?", r"electoral roll", r"land registers?", r"housing registers?", r"register of (?:title|companies|charities|members|electors|births|deaths|marriages|judgments|interests|lobbyists|sponsors|apprenticeship training providers|learning providers)", r"companies register", r"charit(?:y|ies) register", r"local land charges? register", r"planning registers?", r"register of (?:licen[cs]es|licensed|approved)")),
 ("regulatory", "Regulatory and licensing registers", "A list of who is licensed, registered, approved or regulated, kept by a regulator or licensing body.",
  w(r"public registers?", r"register of (?:providers|regulated|registered)", r"registered (?:providers|bodies|persons|carriers|businesses|childcare)", r"waste carriers?(?: register)?", r"licen[cs]ing (?:registers?|public register)", r"licen[cs]e (?:registers?|holders)", r"approved (?:suppliers|providers|premises|persons) (?:list|register)", r"regulat(?:or|ed) (?:registers?|entities|firms)", r"provider registers?", r"registration (?:scheme|system|service) for (?:providers|businesses|operators|carriers)", r"\bcqc\b registration", r"operator licen[cs]e", r"vehicle operator licen[cs]e", r"marine licen[cs]ing public register", r"food business registration", r"trap registration")),
 ("records", "Official records", "Records of legal effect or official record: civil registration, court judgments, title, company filings and archives of record.",
  w(r"(?:birth|death|marriage) (?:records?|registrations?|certificates?)", r"general register office", r"\bgro\b", r"civil registration", r"case law", r"judgments?", r"court records?", r"company filings?", r"filing history", r"title (?:register|plans?|deeds?)", r"public records?", r"records? of (?:the|official)", r"national archives? (?:catalogue|records)", r"teaching record", r"learner records?", r"criminal records?", r"vehicle records?", r"driver records?")),
 ("reference", "Authoritative reference data and code lists", "The agreed list of something that other systems rely on: organisations, places, schools, codes and classifications.",
  w(r"reference data", r"code ?lists?", r"authoritative (?:list|lists|data|dataset|datasets)", r"canonical (?:list|data|dataset|datasets|model)", r"organisation data service", r"\bods\b (?:codes?|data|api)", r"get information about schools", r"\bgias\b", r"\bukprn\b", r"(?:standard|industrial|occupational) classifications?", r"\b(?:sic|soc) codes?", r"geograph(?:y|ies) (?:codes|lookups?|reference)", r"postcode (?:directory|lookups?)", r"address ?base", r"\bnaptan\b", r"gazetteer", r"registers? api", r"registers\.service", r"govuk registers?", r"gov\.uk registers?")),
 ("transparency", "Transparency and public-interest registers", "Registers published so the public can see how government works: interests, spending, contracts, appointments, petitions and decisions.",
  w(r"register of (?:interests|members'? (?:financial )?interests|lobbying|gifts|hospitality)", r"members'? interests", r"transparency (?:data|register|reports?)", r"spend(?:ing)? (?:over|data)", r"contracts? finder", r"find a tender", r"public appointments?", r"petitions?", r"disclosure logs?", r"freedom of information (?:disclosures?|disclosure logs?)", r"\bfoi\b (?:disclosures?|log)", r"lobbying", r"decision (?:notices?|logs?)", r"publish (?:spending|contracts|data)")),
 ("sor", "Systems of record and single sources of truth", "The system other systems treat as the master copy of some data.",
  w(r"systems? of record", r"single sources? of truth", r"sources? of truth", r"master (?:data|copy|record|list)", r"golden (?:record|source)", r"authoritative sources?", r"primary source of", r"definitive (?:source|list|record)")),
 ("content", "Authoritative published content", "Official published content that others cite: legislation, guidance on GOV.UK, manuals, official statistics and standards.",
  w(r"legislation(?:\.gov\.uk)?", r"statutory instruments?", r"acts of parliament", r"hansard", r"official statistics", r"national statistics", r"statistical releases?", r"(?:content|manuals?|guidance) publisher", r"publishing (?:platform|api|app)", r"content (?:store|api|publisher)", r"publishes? (?:guidance|manuals?|content|statistics|policy) (?:on|to) gov\.uk", r"gov\.uk (?:content|publishing)", r"style guide", r"service manual (?:publisher|on gov\.uk)", r"publishes the service manual", r"technical standards? (?:published|for)")),
]
NEG = w(r"(?:docker|container|npm|helm|package|artifact|model|schema|service) registr(?:y|ies)", r"sources? of truth for (?:\w+ )?(?:config\w*|infrastructure|terraform|deployments?)", r"register (?:a|an|your) (?:account|user|device|interest in fostering)", r"user registration", r"registration (?:form|page|flow) for (?:users|accounts)", r"cpu registers?", r"redux", r"plugin registry")

def hits(text, k=2):
    t = NEG.sub(" ", text); sc, ev = collections.Counter(), {}
    for i, r in enumerate(KINDS):
        ms = list(r[3].finditer(t))
        if ms: sc[i] = len({m.group(0).lower() for m in ms}); ev[i] = max((m.group(0) for m in ms), key=len)
    return [[i, ev[i]] for i, _ in sorted(sc.items(), key=lambda kv: (-kv[1], -len(ev[kv[0]]), kv[0]))[:k]]

# Precision, judged by Claude on 1 November 2026 from random samples of each kind's strongest match (not owner-confirmed).
PREC = [("Registers and authoritative sources", 28, 26, "7 kinds, 4 each. Round one was 21 of 28: 'Land Registry' named as a data source or in a copied template, a 'service manual' in prototype-kit boilerplate, a 'source of truth' for infrastructure settings, and freedom of information request forms. Those were narrowed and the statutory, published content, reference data and transparency kinds redrawn.")]

def need(ok, cid, msg, lines, fails):
    lines.append(f"{'PASS' if ok else 'FAIL'} {cid} {msg} [guards: R52]"); print(lines[-1])
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
        seen.add(key); h = hits(text)
        if h: out[key] = h
    cnt = collections.Counter(v[0][0] for v in out.values())
    lines, fails = [], []
    need(all(cnt[i] for i in range(len(KINDS))), "C-REG-01", f"{len(KINDS)} kinds of register and authoritative source, each found in projects ({len(out):,} projects in all)", lines, fails)
    traps = ["Docker registry mirror", "Register your account to sign in", "Redux store for the app", "Helm chart registry", "User registration form for users"]
    real = {"Electoral register canvass system": "statutory", "Public register of waste carriers": "regulatory", "Find case law judgments": "records", "Reference data and code lists API": "reference", "Register of members' financial interests": "transparency", "The single source of truth for organisation data": "sor", "Publishes guidance on GOV.UK": "content"}
    ix = {k[0]: i for i, k in enumerate(KINDS)}
    bt = [t for t in traps if hits(t)]; br = [t for t, k in real.items() if not hits(t) or hits(t)[0][0] != ix[k]]
    need(all(r / n >= 0.85 for _, n, r, _ in PREC), "C-REG-03", "precision on judged samples: " + "; ".join(f"{d} {r} of {n}" for d, n, r, _ in PREC) + ", judged by Claude, not owner-confirmed", lines, fails)
    need(not bt and not br, "C-REG-02n", f"negative tests: {len(traps)} phrases about software registries and sign-up get no register, and {len(real)} plain register phrases get the right kind (wrong: {bt + br})", lines, fails)
    json.dump(dict(kinds=[[k[0], k[1], k[2]] for k in KINDS], recs=out, prec=dict(judged_by="Claude, 1 November 2026 (not owner-confirmed)", rounds=PREC)), open(os.path.join(S, "registers.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    open(os.path.join(S, "registers_checks.txt"), "w").write("\n".join(lines) + "\n")
    print({KINDS[i][1]: n for i, n in cnt.most_common()})
    sys.exit(1 if fails else 0)
