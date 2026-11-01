"""Guidance, policy and playbooks; public service journeys; the UK's nations, crown dependencies and overseas territories;
international and supranational work, with UK alliances and partners flagged (7.2).

Input: the catalogue records in ../uses/D5.json (name, description, README summary, topics) and practices.json types.
Text is matched on word boundaries; ambiguous short words (WHO, UN, EU, US) are only taken in safe forms.
Writes themes.json and themes_checks.txt. Run with python3 -I.
"""
import json, os, re

S = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(S); I = re.I
B, E = r"(?<![a-z0-9])", r"(?![a-z0-9])"
w = lambda *a: re.compile(B + "(?:" + "|".join(a) + ")" + E, I)

# theme, sub-id, label, rule, plain description
CATS = [
 ("guidance", "playbook", "Playbooks", w(r"(?<!ansible )play ?books?(?! (?:for|to run|run) ansible)"), "Hosts or maintains a playbook: practical, step-by-step guidance for a job or a team."),
 ("guidance", "manual", "Guidance, manuals and handbooks", w(r"guidance", r"service manual", r"team manual", r"handbook", r"(?:user|style|technical|operations|operating|staff) (?:guide|manual)", r"how[- ]to guides?", r"good practice guide", r"design guide"), "Hosts, publishes or maintains written guidance, a manual or a handbook."),
 ("guidance", "policy", "Policy", w(r"government polic(?:y|ies)", r"public polic(?:y|ies)", r"policy (?:papers?|documents?|guidance|framework|statements?|making|makers|analysis|teams?|areas?|development|tool|lab)", r"polic(?:y|ies) and guidance", r"(?:data|ai|open source|cloud|technology|digital|accessibility|records management|retention) polic(?:y|ies)(?! (?:document|attachment|arn|json))"), "About, implementing or publishing a policy."),
 ("guidance", "standard", "Standards and codes of practice", w(r"service standard", r"technology code of practice", r"codes? of practice", r"gds way", r"(?:data|open|technical|metadata|api) standards?(?! library)", r"standards? (?:for|to help|that)"), "Hosts or supports a standard, principles or a code of practice."),
 ("journeys", "journey", "Service journeys", w(r"(?:user|service|customer|citizen|end[- ]to[- ]end) journeys?", r"journey maps?", r"journey mapping", r"journeys? through"), "About how people move through a service, from start to finish."),
 ("journeys", "lifeevent", "Life events", w(r"life events?", r"tell us once", r"(?:register|registering) (?:a )?(?:birth|death)", r"having a baby", r"bereavement", r"when someone dies", r"moving house", r"starting a business", r"start(?:ing)? a business", r"(?:planning (?:for )?)?retirement", r"leaving care", r"becoming a carer"), "Supports a life event that touches many parts of government, such as a birth, a death or starting a business."),
 ("journeys", "wog", "Whole of government", w(r"whole[- ]of[- ]government", r"cross[- ]government", r"across government", r"government[- ]wide", r"pan[- ]government", r"x[- ]?gov", r"one login", r"single sign[- ]on for government"), "Works across government rather than for one department."),
 ("nations", "nations", "The UK's four nations", w(r"scotland", r"scottish", r"(?<!england and )(?<!england & )wales", r"welsh", r"cymru", r"northern ireland", r"\bni\b executive", r"four nations", r"home nations", r"uk[- ]wide", r"pan[- ]uk", r"across the uk", r"gb[- ]wide", r"great britain and northern ireland"), "About, for or across England, Scotland, Wales and Northern Ireland."),
 ("nations", "devolution", "Devolution", w(r"devolv\w+", r"devolution", r"intergovernmental relations", r"barnett", r"sewel", r"devolved administrations?"), "About devolution or the devolved governments."),
 ("nations", "crown", "Crown dependencies", w(r"jersey", r"guernsey", r"isle of man", r"manx", r"alderney", r"sark", r"crown dependenc(?:y|ies)", r"bailiwick"), "About or involving Jersey, Guernsey or the Isle of Man."),
 ("nations", "ot", "Overseas territories", w(r"gibraltar", r"falkland islands?", r"bermuda", r"cayman islands", r"montserrat", r"anguilla", r"british virgin islands", r"turks and caicos", r"st\.? helena", r"saint helena", r"ascension island", r"tristan da cunha", r"pitcairn", r"british antarctic territory", r"british indian ocean territory", r"sovereign base areas?", r"akrotiri", r"dhekelia", r"overseas territor(?:y|ies)", r"south georgia"), "About or involving a British Overseas Territory."),
 ("nations", "exchange", "Data exchange between the UK's nations", None, "Moves or shares data across the UK's nations, crown dependencies or territories: a nations match together with data sharing or exchange words."),
 ("international", "supra", "Supranational and international bodies", w(r"european union", r"european commission", r"eurostat", r"european parliament", r"united nations", r"unece", r"unicef", r"unhcr", r"unesco", r"oecd", r"world bank", r"imf", r"international monetary fund", r"world health organi[sz]ation", r"world trade organi[sz]ation", r"interpol", r"europol", r"icao", r"international maritime organi[sz]ation", r"international telecommunication union", r"council of europe", r"open government partnership", r"sustainable development goals?", r"sdgs?", r"commonwealth secretariat", r"g20", r"g7", r"nato", r"five eyes", r"aukus", r"eu (?:law|regulations?|directives?|exit|withdrawal|settlement|settled status|member states?|funding|data)", r"brexit", r"inspire directive", r"gdpr"), "About or involving the EU, the UN family, the OECD, the World Bank, the IMF, NATO or similar bodies."),
 ("international", "intl", "International work", w(r"international (?:development|aid|trade|data|standards?|partners?|cooperation|comparisons?|benchmarks?)", r"overseas development", r"cross[- ]border", r"global (?:standards?|health|development)", r"foreign (?:aid|office|policy)", r"embass(?:y|ies)", r"consular", r"visas?(?! card)"), "International development, trade, cooperation, cross-border work or consular services."),
 ("international", "partner", "Partner countries", w(r"united states", r"usa", r"u\.s\. government", r"canada", r"canadian", r"australia", r"australian", r"new zealand", r"(?<!northern )ireland", r"irish", r"france", r"french government", r"germany", r"german government", r"netherlands", r"dutch government", r"japan", r"india", r"singapore", r"estonia", r"norway", r"denmark", r"sweden", r"finland", r"ukraine"), "Names a partner country of the UK."),
]
ALLIANCE = w(r"nato", r"five eyes", r"aukus", r"g7", r"g20", r"commonwealth", r"joint expeditionary force", r"european union", r"eu (?:law|regulations?|directives?|data|funding)", r"oecd", r"council of europe", r"united nations", r"united states", r"canada", r"australia", r"new zealand", r"ireland", r"france", r"germany", r"japan", r"ukraine", r"estonia")
EXCH = w(r"data (?:sharing|exchange|flows?|transfers?|linkage|linking)", r"shar(?:e|es|ing) data", r"exchang\w+ (?:data|records|information)", r"interoperab\w+", r"cross[- ]border", r"between (?:england|scotland|wales|northern ireland|the (?:four |home )?nations|the uk and)")
CI = {c[1]: i for i, c in enumerate(CATS)}
CROSS = w(r"four nations", r"home nations", r"uk[- ]wide", r"pan[- ]uk", r"across the uk", r"gb[- ]wide", r"between (?:england|scotland|wales|northern ireland|the (?:four |home )?nations)", r"devolved administrations")
NEG = {"playbook": w(r"ansible", r"playbooks? (?:to|for) (?:deploy|provision|install|configure|set up)", r"infrastructure playbooks"),
       "policy": w(r"iam polic", r"aws iam", r"bucket polic", r"policy document to gain"),
       "crown": w(r"shades jersey", r"jersey (?:client|server|container|servlet|jackson|media|core|common|framework)", r"jax[- ]?rs", r"glassfish", r"apache")}

def snip(t, m): a = max(0, m.start() - 40); return re.sub(r"\s+", " ", t[a:m.end() + 40]).strip()[:120]
def classify(text, ty=None):
    t = text.replace("-", " ").replace("_", " "); out = []
    for i, (th, sid, label, rx, _) in enumerate(CATS):
        if rx is None: continue
        m = rx.search(t)
        if m and not (sid in NEG and NEG[sid].search(t)): out.append([i, snip(t, m)])
    if ty == "Documentation or guidance" and not any(CATS[i][0] == "guidance" for i, _ in out): out.append([CI["manual"], "its files are mainly documentation or guidance"])
    nat = [s for i, s in out if CATS[i][1] in ("nations", "devolution", "crown", "ot")]
    names = {n for n in ("england", "scotland", "wales", "northern ireland") if re.search(B + n + E, t, I)}
    cross = CROSS.search(t) or len(names) >= 2 or any(CATS[i][1] in ("crown", "ot") for i, _ in out)
    if nat and cross and not re.search(r"england (?:and|&) wales", t, I) or (nat and len(names) >= 3):
        m = EXCH.search(t)
        if m: out.append([CI["exchange"], nat[0] + " … " + snip(t, m)])
    ally = bool(ALLIANCE.search(t)) and any(CATS[i][0] == "international" for i, _ in out)
    return out, ally

if __name__ == "__main__":
    D = json.load(open(os.path.join(R, "uses", "D5.json"))); XO = D["xorgs"]; P = json.load(open(os.path.join(S, "practices.json")))
    recs = [(dict(zip(D["xf"], a)), ("n", "d", "ld", "t")) for a in D["xrows"]] + [(dict(zip(D["cf"], a)), ("n", "d")) for a in D["cat"]]
    out, allies = {}, []
    for o, fields in recs:
        key = XO[o["oi"]]["org"] + "/" + o["n"]
        c, ally = classify(" ".join(str(o.get(k) or "") for k in fields), P["types"].get(key))
        if c: out[key] = c
        if ally: allies.append(key)
    checks = []
    def need(ok, cid, text, guards="R37"): checks.append(f"{'PASS' if ok else 'FAIL'} {cid} {text} [guards: {guards}]"); return ok
    ids = lambda text: {CATS[i][1] for i, _ in classify(text)[0]}
    neg = [ids("Ansible playbooks for provisioning servers"), ids("IAM policy JSON for the S3 bucket"), ids("Content security policy headers"), ids("WHO is using this app"), ids("Set up a new user in the UN-registered queue"), ids("Updates the US English spelling dictionary"), ids("hadoop common: shades Jersey and excludes logging"), ids("Playbooks to deploy a Jupyterhub instance"), ids("Criminal courts in England and Wales"), ids("cookie policy pop up component"), ids("Common framework code for Response Management")]
    pos = [ids("A playbook for using AI in government"), ids("GOV.UK Service Manual"), ids("Tell Us Once: report a death to many services"), ids("Data exchange between Scotland and Wales"), ids("Statistics for the Isle of Man and Jersey"), ids("Reporting to Eurostat and the OECD"), ids("Shared with NATO partners")]
    need(not any(neg), "C-TH-01", "look-alike words are not counted: Ansible playbooks, an IAM or content security policy, 'WHO is using', 'UN-registered' and 'US English', the Java Jersey library, Ansible-style deploy playbooks, 'England and Wales' courts, a cookie policy banner and a 'common framework' match nothing (negative tests)")
    need({"playbook"} <= pos[0] and {"manual"} <= pos[1] and {"lifeevent"} <= pos[2] and {"nations", "exchange"} <= pos[3] and {"crown"} <= pos[4] and {"supra"} <= pos[5] and {"supra"} <= pos[6], "C-TH-02", "real cases are found: an AI playbook, the Service Manual, Tell Us Once, data exchange between Scotland and Wales, the Isle of Man and Jersey, Eurostat and the OECD, NATO partners")
    need(all(0 <= a[0] < len(CATS) for v in out.values() for a in v) and set(allies) <= set(out), "C-TH-03", f"{len(out)} repositories carry at least one of {len(CATS)} theme signals; {len(allies)} international ones are flagged as involving a UK alliance or partner")
    prec = [["Playbooks", 6, 4, "Ansible deployment playbooks matched; excluded, then 5 of 5 right"], ["Policy", 6, 5, "a cookie-policy banner matched; then an AWS IAM policy tool: both excluded"],
            ["Standards and codes of practice", 6, 5, "a mention of following GOV.UK design principles; 'design principles' removed"], ["Whole of government", 6, 6, ""], ["Service journeys", 6, 6, ""], ["Life events", 6, 6, ""],
            ["Supranational and international bodies", 6, 6, "GDPR is counted as EU-derived regulation"], ["International work", 6, 6, "visa services counted as consular and international"], ["Partner countries", 6, 4, "'Northern Ireland' matched 'Ireland'; fixed"],
            ["The UK's four nations", 5, 5, "'England and Wales' as a court jurisdiction no longer counts"], ["Crown dependencies", 3, 0, "all three were the Java 'Jersey' library; excluded, none remain"], ["Data exchange between the UK's nations", 1, 0, "an internal 'data transfer' script; now needs two nations or a UK-wide phrase plus data-sharing words, and none remain"]]
    json.dump(dict(cats=[[c[0], c[1], c[2], c[4]] for c in CATS], recs=out, allies=allies, prec=dict(judged_by="Claude, 31 October 2026 (not owner-confirmed)", rounds=prec), source="Names, descriptions, README summaries and topics, read October 2026; 'mainly documentation' from file types."), open(os.path.join(S, "themes.json"), "w"), separators=(",", ":"))
    open(os.path.join(S, "themes_checks.txt"), "w").write("\n".join(checks) + "\n")
    import collections; cnt = collections.Counter(CATS[a[0]][1] for v in out.values() for a in v)
    print("\n".join(checks)); print(len(out), len(allies), cnt.most_common())
