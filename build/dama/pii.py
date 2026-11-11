"""Find and remove personal names and other personal data from catalogue text (7.9, R54).

Text quoted from projects (descriptions, README summaries) can name people: 'contact Jane Smith', 'created by ...',
'speak to CJ'. This finds person-like names with three tests, then replaces them with '[name removed]':
  1. a cue before a capitalised name: contact, speak to, ask, email, created/written/maintained/developed/built/owned by, author, lead;
  2. a first name from FIRST (a list of common first names) followed by a capitalised surname;
  3. initials after a cue ('speak to CJ').
Organisation-like words (Council, Team, University, Office ...) after the name stop a match, so 'owned by Orchestration'
or 'created by Team 4' are left alone. Every replacement is listed in pii_report.json for review.
Run with python3 -I build/dama/pii.py [--apply]. Without --apply it only reports.
"""
import json, os, re, sys
S = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(S)
FIRST = set("""aaron abbie abigail adam adrian aidan aisha alan alastair albert alex alexander alexandra alfie ali alice alison alistair amanda amber amelia amy andrea andrew andy angela anna anne annie anthony antonio arthur ashley barbara barry ben benjamin beth bethany bob brian bruce callum cameron carl carlos carol caroline catherine charles charlie charlotte chloe chris christian christine christopher claire clare colin connor craig daisy dan daniel danny darren dave david dean debbie deborah denise derek diana diane dominic donna doug douglas duncan dylan ed edward eleanor elena eliza elizabeth ella ellie emily emma eric erin ethan eva evan faye fiona frances francesca freddie freya gareth gary gavin gemma george georgia gerald gillian gordon graham hannah harriet harry harvey hayley heather helen henry holly hugh iain ian imogen isaac isabel isabella isla jack jackie jacob jade jake james jamie jan jane janet jason jay jean jeff jennifer jenny jeremy jessica jill jim jo joan joanna joe joel john jon jonathan jordan jose joseph josh joshua joy judith julia julie justin karen kate katherine kathryn katie kay keith kelly kevin kieran kim kirsty laura lauren leah lee leo leon lewis liam lily linda lisa lloyd lorna louise lucas lucy luke lydia lynn maggie malcolm marc marcus margaret maria marie mark marta martin mary matt matthew max megan melanie michael michelle mike mohammed muhammad molly natalie nathan neil nicholas nick nicola nicole nigel noah oliver olivia oscar owen paige pamela patricia patrick paul paula peter philip phil phoebe poppy rachel ray rebecca richard rob robert robin rory rose ross ruby russell ruth ryan sally sam samantha samuel sandra sara sarah scott sean shane sharon sheila simon sophia sophie stacey stefan stella stephanie stephen steve steven stuart susan suzanne tara teresa thomas tim timothy tina toby todd tom tony tracy tyler valerie vanessa victoria vincent wayne wendy william zac zara zoe""".split())
ORG = r"(?:Council|Councils|Team|Teams|University|Office|Service|Services|Department|Ministry|Agency|Authority|Trust|Hospital|Group|Library|Archives?|Street|Road|Station|Centre|Center|Park|Programme|Project|Products?|Platform|Lab|Labs|Unit|Board|Partnership|Foundation|Institute|College|School|Limited|Ltd|Plc|Inc|Software|Mapping|Data|Digital|Health|Care|Government|Gov|Kit|Code|API|UK)\b"
NAME = r"[A-Z][a-z]+(?:[-'][A-Z][a-z]+)?"
CUE = r"(?:contact|speak to|talk to|ask|email|e-mail|ping|created by|written by|maintained by|developed by|built by|owned by|authored by|author:?|lead:?|owner:?|thanks to|courtesy of|by)"
RX_CUE = re.compile(rf"\b(?i:{CUE})\s+(?:Dr\.?\s+|Prof\.?\s+)?(?!{ORG})({NAME}(?:\s+(?!{ORG}){NAME}){{0,2}})(?!\s+{ORG})")
STRONG = re.compile(r"(?i:contact|speak to|talk to|created by|written by|maintained by|authored by|thanks to|courtesy of|author|owner|lead)\W*$")
RX_FIRST = re.compile(rf"\b({NAME})\s+(?!{ORG})({NAME})\b(?!\s+{ORG})")
RX_INIT = re.compile(rf"\b(?:speak to|talk to|ask|contact|ping)\s+([A-Z]{{2,3}})\b")
STOP_AFTER_CUE = {"The", "This", "A", "An", "Our", "Your", "Default", "Docker", "Google", "Microsoft", "Amazon", "Apple", "GitHub", "Defra", "Ministry", "Transition", "Unilink", "Scrumconnect", "Land", "Wallet", "Orchestration", "Integration", "Team", "OS"}

NOT_PEOPLE = {"Ruby Gem", "Ruby Script", "Ruby Lambda", "Rose Picker", "Ray Body", "OS", "Form Epic", "Amber Devices", "Clinical Outcomes", "Frank Website", "Frank Alpha", "Design Ops", "Alan Turing", "Ruby Gems", "Ruby on", "Victoria Line", "Grace Period", "Albert Museum", "Elizabeth Memorial", "Tyler Technologies", "Details Verification", "Patrick Finucane",
              # public bodies and places named after people or places, found as buyers in tender notices (7.17.0)
              "Albert Hall", "Joseph Chamberlain", "Lee Valley", "John Kyrle", "Amber Valley", "Christian Malford", "John Hampden", "Peter Port"}
def find(text):
    out = []
    for m in RX_CUE.finditer(text):
        nm = m.group(1); first = nm.split()[0]
        if first in STOP_AFTER_CUE: continue
        strong = bool(STRONG.search(text[:m.start(1)].rstrip()[-20:] + " ")) or bool(STRONG.search(text[:m.start(1)].rstrip()))
        if first.lower() in FIRST or (strong and len(nm.split()) >= 2): out.append(("cue", nm, m.start(1), m.end(1)))
    for m in RX_FIRST.finditer(text):
        if m.group(1).lower() in FIRST and not any(s <= m.start() < e for _, _, s, e in out): out.append(("first", m.group(0), m.start(), m.end()))
    for m in RX_INIT.finditer(text): out.append(("initials", m.group(1), m.start(1), m.end(1)))
    return [h for h in out if h[1] not in NOT_PEOPLE]

def scrub(text):
    hs = sorted(find(text), key=lambda h: -h[2]); t = text
    for _, _, s, e in hs: t = t[:s] + "[name removed]" + t[e:]
    # co-authors listed after a removed name ('A Smith, B Jones and C Brown') are removed too, whatever their first name
    nx = re.compile(rf"(\[name removed\]\**(?:,\s*|\s+and\s+|\s*&\s*))({NAME}(?:\s+{NAME}){{1,2}})(?!\s+{ORG})")
    while True:
        m = nx.search(t)
        if not m or m.group(2) in NOT_PEOPLE or m.group(2).split()[0] in STOP_AFTER_CUE: break
        hs.append(("list", m.group(2), m.start(2), m.end(2))); t = t[:m.start(2)] + "[name removed]" + t[m.end(2):]
    # a personal email cut short by a length limit ('(jane.smi') leaves part of the address: remove it too
    t2 = re.sub(r"(\[name removed\]\s*\()\s*[a-z]+[._][a-z]+[a-z._@-]*", r"\1address removed", t)
    if t2 != t: hs.append(("email fragment", "", 0, 0)); t = t2
    return t, hs

TESTS = {"Rob Akers, Jeyan Thiyagalingam, An Open Data Service": "[name removed], [name removed], An Open Data Service", "Speak to Andy Jones about this": "Speak to [name removed] about this", "speak to CJ for info": "speak to [name removed] for info", "Please contact Marta Villalobos (marta.villalobo": "Please contact [name removed] (address removed",
         "created by Charlotte Evans (Lancaster University) and Chris Fleet": "created by [name removed] (Lancaster University) and [name removed]"}
NEGATIVE = ["Contact Details Verification service", "Ruby Gem for parsing", "Victoria & Albert Museum", "owned by Orchestration for testing", "created by Team 4 in Hack for Health", "built by Unilink to improve", "talk to OS Places", "maintained by Land grants team"]
def self_test():
    bad = [s for s, want in TESTS.items() if scrub(s)[0] != want] + [s for s in NEGATIVE if scrub(s)[1]]
    return bad

if __name__ == "__main__":
    bad = self_test(); ok = not bad
    line = f"{'PASS' if ok else 'FAIL'} C-PII-01 personal names are found after cues (contact, speak to, created by), from common first names and in author lists, and removed; {len(NEGATIVE)} organisation, product and team phrases are left alone (wrong: {bad}) [guards: R54]"
    print(line); open(os.path.join(S, "pii_checks.txt"), "w").write(line + "\n")
    if not ok: sys.exit(1)
    apply = "--apply" in sys.argv; rep = []
    X = json.load(open(os.path.join(R, "xgov", "xgov.json"))); C = json.load(open(os.path.join(R, "catalogue", "catalogue.json")))
    for r in X["rows"]:
        for f in ("d", "ld"):
            if r.get(f):
                t, hs = scrub(r[f])
                if hs: rep.append([r["o"] + "/" + r["n"], f, [h[1] for h in hs], [h[0] for h in hs]]); r[f] = t if apply else r[f]
        e = r.get("e") or {}
        if e.get("lede"):
            t, hs = scrub(e["lede"])
            if hs: rep.append([r["o"] + "/" + r["n"], "e.lede", [h[1] for h in hs], [h[0] for h in hs]]); e["lede"] = t if apply else e["lede"]
    for a in C["cat"]:
        if isinstance(a[2], str) and a[2]:
            t, hs = scrub(a[2])
            if hs: rep.append([C["orgs"][a[0]]["org"] + "/" + a[1], "d", [h[1] for h in hs], [h[0] for h in hs]]); a[2] = t if apply else a[2]
    if apply:
        json.dump(X, open(os.path.join(R, "xgov", "xgov.json"), "w"), ensure_ascii=False, separators=(",", ":")); json.dump(C, open(os.path.join(R, "catalogue", "catalogue.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    # evidence snippets quoted elsewhere in the catalogue's data (official organisation names in hier.json are left as GOV.UK publishes them)
    for f in ("dama/dama_data.json", "dama/opendata.json", "dama/themes.json", "dama/services.json", "dama/subjects.json", "dama/interop.json", "dama/registers.json", "inv/data.json", "dama/cdot.json"):
        p = os.path.join(R, f) if f != "inv/data.json" else __import__("runpy").run_path(os.path.join(R, "internal.py"))["ipath"]("build/inv/data.json")
        if not os.path.exists(p): continue   # internal-only input, not in the public repository (ADR 0004)
        d = json.load(open(p)); n = [0]
        def walk(o, path):
            if isinstance(o, dict): return {k: walk(v, path + [k]) for k, v in o.items()}
            if isinstance(o, list): return [walk(v, path) for v in o]
            if isinstance(o, str) and len(o) > 12:
                s, hs = scrub(o)
                if hs: n[0] += 1; rep.append([f + ":" + "/".join(map(str, path[-2:])), "text", [h[1] for h in hs], [h[0] for h in hs]]); return s if apply else o
            return o
        d2 = walk(d, [])
        if apply and n[0]: json.dump(d2, open(p, "w"), ensure_ascii=False, separators=(",", ":"))
    json.dump(dict(applied=apply, n=len(rep), found=[[k, f, hs] for k, f, hs, _ in rep]), open(os.path.join(S, "pii_report.json"), "w"), ensure_ascii=False, indent=0)
    for k, f, hs, kinds in rep: print(k[:45], f, hs, kinds)
    print(len(rep), "fields with names", "(applied)" if apply else "(report only)")
