"""What each project is, in one plain label (7.11, R61): live service code, likely supporting a service, a building block
(library, component, client, template, docs or tooling), a prototype or experiment, archived, or no longer public.

Signals, strongest first:
  - no longer public: the check against GitHub on 1 November 2026 couldn't reach it (ghverify.json);
  - archived: GitHub says so;
  - live service code: Slack messages linking to it in deploy, release, alert or production channels, or at least five
    messages about incidents and releases (collab_slack.json);
  - prototype or experiment / building block: words in its name, description or topics;
  - likely supporting a service: changed in the last year, says it is a service, app, API, frontend or backend, or has its own web address.
Anything else is 'not known'. Labels are judged on samples (PREC below), not confirmed by owners, and the page says so.
Writes life.json ({repo: [label, evidence]}) and life_checks.txt. Run with python3 -I.
"""
import collections, datetime as dt, json, os, re, sys
S = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(S)
B, E = r"(?<![a-z0-9])", r"(?![a-z0-9])"
w = lambda *a: re.compile(B + "(?:" + "|".join(a) + ")" + E, re.I)
PROTO = w(r"prototypes?", r"poc", r"proof[ -]of[ -]concept", r"spike", r"demo", r"hackathon", r"hack ?day", r"sandbox", r"playground", r"experiments?", r"kata", r"tech[ -]test", r"technical[ -]exercise", r"tutorial", r"workshop", r"mvp")
PROTO_NAME = re.compile(r"(^|[-_])(alpha|training|learning|practice|test\d+|lab)([-_]|$)", re.I)
TOOL_NAME = re.compile(r"(^|[-_])(tester|hardening|marketplace|e2e|tests?|acceptance|perf|performance|load|smoke|local|dev-env|devenv|stubs?|mocks?|simulator|fake|samples?|examples?|scanner|checker|metrics|scripts?|tools?|cli|bots?|exporter|monitoring|audit)([-_]|$)", re.I)
TOOL_DESC = w(r"scripts? to", r"test stubs?", r"mock server", r"end[ -]to[ -]end tests?", r"performance tests?", r"acceptance tests?", r"command[ -]line tool", r"example code", r"examples of")
BLOCK_TAIL = re.compile(r"(^|[-_])((github-)?actions?|(docker|base|container|ami)[-_]images?|images?)$", re.I)   # an action or image only at the end of the name
BLOCK_NAME = re.compile(r"(^|[-_])(lib|library|(?<!desktop-)client|sdk|components?|frontend-kit|kit|template|skeleton|boilerplate|design-system|plugin|gem|module|modules|helm-charts?|eslint-config|rubocop|config|docs|manual|schemas?|spec|specs|toolkit|elements|patterns|adapters?|helpers?|utils?|utilities|common)([-_]|$)", re.I)
BLOCK_DESC = w(r"github actions? (?:for|to|that)", r"(?:java|python|node|ruby|go|php|\.net|typescript|javascript)? ?(?:client )?library", r"r[ -]package", r"python package", r"npm packages?", r"sdk", r"design system", r"terraform modules?", r"docker images?", r"base images?", r"helm charts?", r"(?:a |the )?template for", r"technical documentation", r"documentation", r"gem containing", r"service manual", r"api specifications?", r"fhir (?:profiles|implementation guide)")
SERVICE = w(r"service", r"app", r"application", r"api", r"frontend", r"front[ -]end", r"backend", r"back[ -]end", r"admin", r"portal", r"platform", r"website", r"web ?site", r"worker", r"consumer", r"publisher", r"microservice")
NONPROD = re.compile(r"(non-?prod|nonprod|staging|dev|test|sandbox)", re.I)
SERVICE_NAME = re.compile(r"(^|[-_.])(service|frontend|front-end|ui|web|api|backend|admin|portal|app|microservice|worker|consumer|publisher)([-_.]|$)", re.I)
SERVICE_DESC = w(r"microservice", r"this service (?:is|provides|allows|lets|enables)", r"backend for the", r"frontend for the", r"web application", r"public api")
FEEDISH = re.compile(r"(deploy|release|alert|alarm|production|prod\b|incident|on-?call|support)", re.I)
LABELS = {"live": "Seen in live operations", "tool": "Tests, stubs and tooling", "supports": "Likely supports a service", "block": "Building block", "proto": "Prototype or experiment", "archived": "Archived", "gone": "No longer public", "unknown": "Not known"}
PREC = [("live", 15, 14, "One was a shared gem used by live apps rather than a service in its own right."), ("tool", 15, 14, "One was a component library whose README mentions examples."), ("supports", 15, 14, "One was an operational tool for a payments service. Four rounds: 10, 11, 12 and then 14 of 15 as the rules were narrowed to service words in the name."), ("block", 15, 13, "A service frontend named after its users' clients, and an analysis repository named 'profiles'; both rules were tightened after this sample. Earlier rounds: 7, 15 and 12 of 15."), ("proto", 15, 13, "A training course and an accessible version of an outcomes framework.")]

def label(name, text, archived, gone, updated_days, has_site, slack, reused=0):
    if gone: return "gone", "GitHub no longer lists it publicly"
    if archived: return "archived", "Archived on GitHub"
    if reused: return "block", f"Used as a package by {reused} other public projects"
    t = name.replace("-", " ").replace("_", " ") + " " + text
    m = PROTO.search(t) or PROTO_NAME.search(name)
    if m: return "proto", f"Says '{m.group(0).strip('-_')}'"
    m = TOOL_NAME.search(name) or TOOL_DESC.search(text)
    if m: return "tool", f"Says '{m.group(0).strip('-_')}'"
    svc_end = re.search(r"[-_](frontend|ui|web|api|service|backend)$", name, re.I)   # a service named after its users, e.g. agent-client-mandate-frontend
    m = (None if svc_end else (BLOCK_NAME.search(name) or BLOCK_TAIL.search(name))) or BLOCK_DESC.search(text)
    if m: return "block", f"Says '{m.group(0).strip('-_ ')}'"
    crit = (slack or {}).get("cats", {}).get("release", 0) + (slack or {}).get("cats", {}).get("incident", 0)
    feeds = [c for c in (slack or {}).get("public_channels", {}) if FEEDISH.search(c.split("|", 1)[1]) and not NONPROD.search(c.split("|", 1)[1])]
    if feeds: return "live", "Linked in " + ", ".join("#" + c.split("|", 1)[1] for c in feeds[:2])
    if updated_days is not None and updated_days <= 365:
        m = SERVICE_NAME.search(name) or SERVICE_DESC.search(text)
        if m: return "supports", f"Changed in the last year and says '{m.group(0).strip('-_')}'"
        if crit >= 5: return "supports", f"Changed in the last year; {crit} Slack messages about its releases and incidents"
    return "unknown", ""

def need(ok, cid, msg, lines, fails):
    lines.append(f"{'PASS' if ok else 'FAIL'} {cid} {msg} [guards: R61]"); print(lines[-1])
    if not ok: fails.append(cid)

if __name__ == "__main__":
    today = dt.date(2026, 11, 1)
    X = json.load(open(os.path.join(R, "xgov", "xgov.json"))); C = json.load(open(os.path.join(R, "catalogue", "catalogue.json")))
    G = json.load(open(os.path.join(S, "ghverify.json"))); SL = json.load(open(os.path.join(S, "collab_slack.json")))["repos"]
    RW = json.load(open(os.path.join(S, "gh_crawl_rows.json")))
    RU = {c["repo"]: c["consumers"] for c in json.load(open(os.path.join(S, "reuse.json")))["components"] if c["repo"]}   # reuse map: a component others build on is a building block
    rowby = {(a + "/" + r[0]).lower(): r for a, v in RW.items() for r in v["r"]}
    gone = {(a["account"] + "/" + n).lower() for a in G["accounts"] for n in a["removed"] if (a["account"] + "/" + n) not in G.get("renamed", {})}
    recs = []
    for r in X["rows"]: recs.append((r["o"] + "/" + r["n"], " ".join(str(r.get(k) or "") for k in ("d", "ld", "t")), str(r.get("a")) == "True", bool(r.get("cd")) or bool(r.get("pu"))))
    for a in C["cat"]:
        o = dict(zip(C["cf"], a)); recs.append((C["orgs"][o["oi"]]["org"] + "/" + o["n"], str(o.get("d") or ""), bool(o.get("ar")), False))
    added = {(a["account"] + "/" + n) for a in G["accounts"] for n in a["added"]}
    nd = json.load(open(os.path.join(S, "new_repos.json")))["repos"] if os.path.exists(os.path.join(S, "new_repos.json")) else {}
    for k in added: recs.append((k, (nd.get(k) or {}).get("d", ""), False, False))
    out, cnt, seen = {}, collections.Counter(), set()
    for key, text, arch, site in recs:
        if key.lower() in seen: continue
        seen.add(key.lower()); live = rowby.get(key.lower())
        days = (today - dt.date.fromisoformat(live[6])).days if live and live[6] else None
        lab, ev = label(key.split("/", 1)[1], text, arch or bool(live and live[1]), key.lower() in gone, days, site, SL.get(key), RU.get(key, 0))
        cnt[lab] += 1
        if lab != "unknown": out[key] = [lab, ev]
    lines, fails = [], []
    need(all(cnt[k] for k in LABELS if k != "unknown") and sum(cnt.values()) > 20000, "C-LIF-01", f"{sum(cnt.values()):,} projects labelled: " + ", ".join(f"{LABELS[k].lower()} {cnt[k]:,}" for k in LABELS), lines, fails)
    need(all(r / n >= 0.85 for _, n, r, _ in PREC), "C-LIF-02", "precision on the latest judged samples (15 per label, drawn at random, judged by Claude on 2 November 2026, not owner-confirmed): " + "; ".join(f"{LABELS[k]} {r} of {n}" for k, n, r, _ in PREC), lines, fails)
    t = [label("govuk-pay-prototype", "", False, False, 10, False, None)[0] == "proto", label("pay-connector", "", False, False, 10, False, {"public_channels": {"gds|govuk-pay-deploy-alerts": 3}, "cats": {}})[0] == "live",
         label("notifications-python-client", "Python client for GOV.UK Notify", False, False, 10, False, None)[0] == "block", label("forms-e2e-tests", "", False, False, 10, False, {"public_channels": {"gds|govuk-forms-deployment-notifications": 9}, "cats": {}})[0] == "tool", label("moj-frontend", "MOJ Design System", False, False, 10, False, {"public_channels": {"gds|x-release": 2}, "cats": {"release": 9}})[0] == "block", label("anything", "", True, False, 10, False, None)[0] == "archived",
         label("old-service", "A service", False, False, 900, False, None)[0] == "unknown", label("x", "", False, True, 1, False, None)[0] == "gone",
         label("forms-admin", "Admin app for GOV.UK Forms", False, False, 20, False, {"public_channels": {"gds|govuk-forms-tech": 4}, "cats": {"release": 1}})[0] == "supports", label("platform-status-frontend", "", False, False, 30, False, None)[0] == "supports", label("webarchive-discovery", "indexing framework", False, False, 30, False, None)[0] != "proto", label("govuk-frontend", "Code for building user interfaces for government services", False, False, 5, False, {"public_channels": {"gds|design-system-dev": 41}, "cats": {}}, 1219)[0] == "block"]
    need(all(t), "C-LIF-01n", f"negative tests: a prototype, live code linked in a deploy channel, a client library, end-to-end tests linked in a deploy channel (tooling, not live), a design system with release talk (a building block), an archived project, a service untouched for over a year (not known), a project no longer public, a service talked about only in a team channel, a service frontend (not a building block) a search tool named 'discovery' (not a prototype), and GOV.UK Frontend, used as a package by 1,219 other projects (a building block, not a service), each get the right label ({t})", lines, fails)
    # compact for the page: archived and gone are worked out on the page from the record itself; evidence strings stored once
    evs = sorted({v[1] for v in out.values() if v[0] not in ("archived", "gone")}); ei = {e: i for i, e in enumerate(evs)}; codes = [k for k in LABELS if k not in ("archived", "gone", "unknown")]
    compact = {k: [codes.index(v[0]), ei[v[1]]] for k, v in out.items() if v[0] in codes}
    json.dump(dict(labels=LABELS, codes=codes, ev=evs, recs=compact, prec=dict(judged_by="Claude, 2 November 2026 (not owner-confirmed)", rounds=PREC)), open(os.path.join(S, "life.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    open(os.path.join(S, "life_checks.txt"), "w").write("\n".join(lines) + "\n")
    sys.exit(1 if fails else 0)
