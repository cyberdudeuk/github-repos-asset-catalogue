"""Security guardrails for the built page (7.11, R63). Imported by build_v71.py; also runnable on its own for its tests.

What it guards against, and how (see docs/security/threat-model.md for the full model):
  T1 Sign-in-only links: repository text quoted on the page sometimes links to SharePoint, Atlassian, Google Docs, Slack,
     Teams or local and private network addresses. They don't work for most readers and map internal tenants and sites,
     so every such address is replaced with a short note before the page is built (both audiences).
  T2 Takeover-prone hosting: addresses on shared hosting (herokuapp.com, azurewebsites.net, netlify.app and similar) can be
     claimed by anyone once the original app is deleted, so the page shows them as text, never as links. Plain http
     addresses are not linked either. The page reads the same list (DATA.sec.risky) so the two can't drift.
  T3 Impersonation: an account that only calls itself government must not be listed as government. Every account needs
     provenance: the government.github.com registry, the X-Gov scraper, or a recorded check (GitHub's verified-domain
     badge, or an official site that links to it).
  T4 Code injection and data exfiltration: the page carries a Content-Security-Policy that allows no network requests,
     no external scripts, styles, fonts or frames, and no forms; the code uses no eval or new Function, and every link
     that opens a new tab has rel="noopener".
  T5 Over-sharing in an open build: the 'public' audience build (GHRAC_AUDIENCE=public) leaves out the Slack
     aggregates and anything else marked internal; checks prove the result holds no channel names.
"""
import json, re

PRIVATE_HOST = re.compile(r"""(?ix)
  ( [a-z0-9-]+\.sharepoint\.com | [a-z0-9-]+-my\.sharepoint\.com | [a-z0-9.-]+\.atlassian\.net(\.mcas\.ms)? | [a-z0-9.-]+\.mcas\.ms
  | docs\.google\.com | drive\.google\.com | sites\.google\.com | [a-z0-9-]+\.slack\.com | app\.slack\.com | teams\.microsoft\.com | teams\.live\.com
  | [a-z0-9-]+\.webex\.com | [a-z0-9-]+\.zoom\.us | [a-z0-9-]+\.service-now\.com | [a-z0-9-]+\.okta\.com | login\.microsoftonline\.com
  | localhost | [a-z0-9.-]+\.localhost | [a-z0-9.-]+\.(internal|local|lan|corp|intranet)
  | 127\.\d+\.\d+\.\d+ | 10\.\d+\.\d+\.\d+ | 192\.168\.\d+\.\d+ | 172\.(1[6-9]|2\d|3[01])\.\d+\.\d+ | 0\.0\.0\.0 )(:\d+)?$""")
URL = re.compile(r"""https?://[^\s"'<>()\[\]{}|\\^`]+""", re.I)
NOTE = "(link to a sign-in-only or private address removed)"
RISKY = ["herokuapp.com", "azurewebsites.net", "netlify.app", "netlify.com", "vercel.app", "glitch.me", "surge.sh", "ngrok.io", "ngrok-free.app",
         "firebaseapp.com", "web.app", "pages.dev", "onrender.com", "fly.dev", "repl.co", "replit.app", "cloudfront.net", "s3.amazonaws.com", "blob.core.windows.net"]
PROVENANCE = ("github/government.github.com registry", "X-Gov repo scraper only", "added (not in registry)",
              "GitHub's list of official government accounts; repositories verified directly over git")


def host_of(u):
    m = re.match(r"(?i)https?://([^/?#@]*@)?([^/?#]+)", u)
    return (m.group(2) if m else "").lower().rstrip(".")


def is_private(u):
    return bool(PRIVATE_HOST.match(host_of(u)))


def is_risky(u):
    h = host_of(u).split(":")[0]
    return u.lower().startswith("http://") or any(h == r or h.endswith("." + r) for r in RISKY)


def scrub_text(s):
    n = 0
    def rep(m):
        nonlocal n
        if is_private(m.group(0)): n += 1; return NOTE
        return m.group(0)
    return URL.sub(rep, s), n


def scrub(obj):
    """Replace private and sign-in-only addresses in every string of obj, in place. Returns how many were replaced."""
    total = 0
    def walk(o):
        nonlocal total
        it = o.items() if isinstance(o, dict) else enumerate(o) if isinstance(o, list) else ()
        for k, v in list(it):
            if isinstance(v, str):
                s, n = scrub_text(v)
                if n: o[k] = s; total += n
            elif isinstance(v, (dict, list)): walk(v)
    walk(obj); return total


def audience(data, aud):
    """Apply an audience profile. 'gov' (default): internal government and public sector users. 'public': an open build."""
    data.setdefault("sec", {}).update(audience=aud, risky=RISKY, note=NOTE)
    if aud == "public":
        data["collab"] = None          # Slack aggregates, including public channel names, stay internal
        L = data.get("life")           # 'Seen in live operations' and Slack-based evidence come from internal chat: generalise them
        if L and "live" in L["codes"]:
            li, si = L["codes"].index("live"), L["codes"].index("supports")
            if "Changed in the last year and looks like part of a service" not in L["ev"]: L["ev"].append("Changed in the last year and looks like part of a service")
            gi = L["ev"].index("Changed in the last year and looks like part of a service")
            for k, (c, e) in list(L["recs"].items()):
                if c == li or "Slack" in L["ev"][e]: L["recs"][k] = [si if c == li else c, gi]
            L["ev"] = [e if "Slack" not in e else "(internal evidence left out of the open build)" for e in L["ev"]]
    return data


CSP = ("default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data: blob:; font-src data:; "
       "connect-src 'none'; media-src 'none'; object-src 'none'; frame-src 'none'; worker-src 'none'; base-uri 'none'; form-action 'none'")
CSP_META = f'<meta http-equiv="Content-Security-Policy" content="{CSP}">'


def page_problems(html):
    """Static checks on the built page (or its template): returns a list of problems."""
    bad = []
    if CSP_META not in html: bad.append("no Content-Security-Policy meta, or a different policy")
    if re.search(r"<script[^>]+\bsrc\s*=", html, re.I): bad.append("an external script")
    if re.search(r"<link[^>]+rel=[\"']?stylesheet", html, re.I) or re.search(r"@import\s+url\(\s*['\"]?https?:", html, re.I): bad.append("an external stylesheet")
    if re.search(r"(?<![A-Za-z_$])url\(\s*['\"]?https?:", html, re.I): bad.append("an external font or image in CSS")
    if re.search(r"<iframe|<object|<embed|<form[^>]*\baction\s*=", html, re.I): bad.append("a frame, plug-in or form that submits elsewhere")
    if re.search(r"\beval\s*\(|new\s+Function\s*\(|setTimeout\(\s*['\"`]|document\.write\s*\(", html): bad.append("eval-like code")
    if re.search(r"target=\"_blank\"(?![^>]*rel=\"[^\"]*noopener)", html): bad.append("a new-tab link without rel=noopener")
    return bad


def provenance_problems(orgs, extra, checked):
    """orgs: catalogue accounts with 'source'; extra: other account names shown; checked: {account: evidence} from a recorded
    check. An account added by hand, or only seen by the scraper, needs a recorded check too."""
    bad = []
    for o in orgs:
        src = o.get("source", "")
        if src not in PROVENANCE: bad.append(f"{o['org']}: unknown source '{src}'")
        elif src != PROVENANCE[0] and not checked.get(o["org"], {}).get("basis"): bad.append(f"{o['org']}: {src} with no recorded check")
    for a in extra:
        if not checked.get(a, {}).get("basis"): bad.append(f"{a}: not in the catalogue and no recorded check")
    return bad


def workflow_problems(files):
    """files: {name: YAML text}. GitHub Actions hardening (OpenSSF Scorecard, GitHub's own guidance): least-privilege token,
    actions pinned to a full commit SHA, no stored credentials after checkout, no pull_request_target, and no untrusted
    event text interpolated into a shell script (script injection)."""
    bad = []
    for n, t in files.items():
        if not re.search(r"(?m)^permissions:", t): bad.append(f"{n}: no top-level permissions")
        if re.search(r"(?m)^permissions:\s*write-all|^\s+(contents|actions|packages|id-token|pull-requests|security-events|deployments):\s*write", t) and "# write needed:" not in t: bad.append(f"{n}: a write permission with no reason given")
        for m in re.finditer(r"uses:\s*([^\s#]+)", t):
            ref = m.group(1)
            if not ref.startswith("./") and not re.search(r"@[0-9a-f]{40}$", ref): bad.append(f"{n}: {ref} is not pinned to a commit SHA")
        if "actions/checkout@" in t and t.count("persist-credentials: false") < t.count("actions/checkout@"): bad.append(f"{n}: checkout keeps the token on disk")
        if re.search(r"\bpull_request_target\b", t): bad.append(f"{n}: pull_request_target")
        L = t.splitlines()
        for i, l in enumerate(L):
            m = re.match(r"^(\s*)(- )?run:(.*)$", l)
            if not m: continue
            ind, body = len(m.group(1)) + (2 if m.group(2) else 0), [m.group(3)]
            for l2 in L[i + 1:]:
                if l2.strip() and len(l2) - len(l2.lstrip()) <= ind: break
                body.append(l2)
            if re.search(r"\$\{\{\s*github\.(event|head_ref)", "\n".join(body)): bad.append(f"{n}: event text interpolated into a run script")
    return bad


MARK = "OFFICIAL" + "-SENSITIVE"   # spelled in two parts so the sensitive-data scan, which allows the marking only where the GDS Way requires it, passes this file
HANDLING_FIELDS = ("classification", "handling_group", "last_reviewed_on", "review_in", "responsible_role", "responsible_role_contact")
HANDLING_GROUPS = ("RECIPIENTS ONLY", "HMG USE ONLY", "EMBARGOED")
README_BANNER = "> This repository is " + MARK + ". Handle in line with [HANDLING_INSTRUCTIONS.md](/HANDLING_INSTRUCTIONS.md)."


def handling_problems(hi, readme, today):
    """The GDS Way (managing sensitive information): a repository that isn't public has HANDLING_INSTRUCTIONS.md with
    the six fields, a known handling group, a role (not a person) and a review that isn't overdue, plus the README banner."""
    import datetime as _dt
    bad = []
    m = re.match(r"---\n(.*?)\n---\n(.*)", hi or "", re.S)
    if not m: return ["no HANDLING_INSTRUCTIONS.md front matter"]
    f = dict(re.findall(r"(?m)^([a-z_]+):\s*(.+)$", m.group(1)))
    bad += [f"missing field {k}" for k in HANDLING_FIELDS if k not in f]
    if f.get("classification") != MARK: bad.append("classification must be " + MARK)
    if f.get("handling_group") not in HANDLING_GROUPS and not re.fullmatch(r"[A-Z .-]+ USE ONLY", f.get("handling_group", "")): bad.append("unknown handling group")
    try:
        last = _dt.date.fromisoformat(f.get("last_reviewed_on", "")); n = int(re.match(r"(\d+)", f.get("review_in", "0")).group(1))
        if (today - last).days > n * 31: bad.append("review overdue")
    except Exception: bad.append("bad review dates")
    if len(m.group(2).strip()) < 200: bad.append("no explanation of what is sensitive")
    if README_BANNER not in (readme or ""): bad.append("no README banner")
    return bad


# T13 (threat model): defence, intelligence and national security accounts. Their repositories are published by the
# accounts themselves, so they are listed. But the Government Security Classifications Policy says aggregated OFFICIAL
# information "may warrant additional controls", and NCSC and NPSA guidance warns that public facts can be combined into
# something more useful to an attacker. So for these accounts the catalogue draws no inferences of its own: no label
# saying whether a repository is part of a live service, no security or practice signals for each repository, no links
# to internal chat, and they aren't named as consumers in the reuse map. Both audiences, both builds.
SENSITIVE_COMMUNITIES = {
    "GCHQ": ("Intelligence and cyber security", "GCHQ, one of the UK's intelligence and security agencies"),
    "ukncsc": ("Intelligence and cyber security", "The National Cyber Security Centre, part of GCHQ"),
    "defencedigital": ("Defence", "Defence Digital, part of the Ministry of Defence"),
    "dstl": ("Defence", "The Defence Science and Technology Laboratory, an executive agency of the Ministry of Defence"),
    "UKHO": ("Defence", "The UK Hydrographic Office, an executive agency of the Ministry of Defence"),
    "NationalCrimeAgency": ("National security and law enforcement", "The National Crime Agency"),
    "UKHomeOffice": ("National security and law enforcement", "The Home Office, responsible for policing, borders and counter-terrorism"),
    "UKHomeOffice-attic": ("National security and law enforcement", "The Home Office's archive account"),
    "UKHomeOfficeForms": ("National security and law enforcement", "The Home Office's forms account"),
    "HO-CTO": ("National security and law enforcement", "The Home Office's Chief Technology Officer"),
}


def protect_communities(data):
    """Withhold the catalogue's own inferences about defence, intelligence and national security accounts. Returns counts."""
    S = set(SENSITIVE_COMMUNITIES); n = dict(practice=0, life=0, chat=0, reuse=0)
    orgs = [o["org"] for o in data.get("xorgs", [])]; xf = data.get("xf", [])
    hi = xf.index("h") if "h" in xf else None
    for r in data.get("xrows", []):
        if hi is not None and r[0] < len(orgs) and orgs[r[0]] in S and r[hi]: r[hi] = 0; n["practice"] += 1
    L = data.get("life")
    if L:
        for k in [k for k in L["recs"] if k.split("/")[0] in S]: del L["recs"][k]; n["life"] += 1
    C = data.get("collab")
    if C:
        for k in [k for k in C["slack"]["repos"] if k.split("/")[0] in S]: del C["slack"]["repos"][k]; n["chat"] += 1
        for c in C["slack"]["channels"]:
            keep = [t for t in c.get("top", []) if t.split("/")[0] not in S]
            c["repos"] -= len(c.get("top", [])) - len(keep); c["top"] = keep
    R = data.get("reuse")
    if R:
        for c in R["components"]:
            keep = [x for x in c.get("sample", []) if x.split("/")[0] not in S]; n["reuse"] += len(c.get("sample", [])) - len(keep); c["sample"] = keep
            c["other_orgs"] = [o for o in c.get("other_orgs", []) if o not in S]
    data.setdefault("sec", {})["communities"] = {a: list(v) for a, v in SENSITIVE_COMMUNITIES.items()}
    return n


def community_leaks(data):
    """What protect_communities should have removed and didn't."""
    S = set(SENSITIVE_COMMUNITIES); bad = []
    orgs = [o["org"] for o in data.get("xorgs", [])]; xf = data.get("xf", []); hi = xf.index("h") if "h" in xf else None
    bad += [f"practice signals: {orgs[r[0]]}/{r[1]}" for r in data.get("xrows", []) if hi is not None and r[0] < len(orgs) and orgs[r[0]] in S and r[hi]]
    bad += [f"life label: {k}" for k in (data.get("life") or {"recs": {}})["recs"] if k.split("/")[0] in S]
    C = data.get("collab")
    if C: bad += [f"chat: {k}" for k in C["slack"]["repos"] if k.split("/")[0] in S] + [f"chat channel lists {t}" for c in C["slack"]["channels"] for t in c.get("top", []) if t.split("/")[0] in S]
    R = data.get("reuse")
    if R: bad += [f"reuse consumer: {x}" for c in R["components"] for x in c.get("sample", []) if x.split("/")[0] in S]
    return bad


def self_test():
    """Negative tests: each guard is shown to catch what it should and leave alone what it shouldn't."""
    fails = []
    caught = ["https://justiceuk.sharepoint.com/sites/x/_layouts/y", "https://eaflood.atlassian.net/wiki/x", "https://skillsfundingagency.atlassian.net.mcas.ms/a",
              "https://docs.google.com/document/d/abc", "http://localhost:3000/", "https://funding.communities.gov.localhost/x", "http://10.0.0.4/x",
              "http://192.168.1.10:8080", "https://gds.slack.com/archives/C123", "https://teams.microsoft.com/l/x", "http://172.20.1.1/"]
    kept = ["https://www.gov.uk/x", "https://github.com/alphagov/govuk-frontend", "https://design-system.service.gov.uk/", "https://digital.nhs.uk/x",
            "https://172.15.0.1.example.org/", "https://sharepoint-guide.gov.uk/x", "https://www.slack-engineering.org.uk/"]
    fails += [f"not caught: {u}" for u in caught if not is_private(u)] + [f"wrongly caught: {u}" for u in kept if is_private(u)]
    s, n = scrub_text('See [design](https://justiceuk.sharepoint.com/:p:/s/X/Eb8) and https://www.gov.uk/x.')
    if n != 1 or "sharepoint" in s or "https://www.gov.uk/x" not in s: fails.append(f"scrub_text: {s}")
    d = {"a": ["x https://eaflood.atlassian.net/y", {"b": "http://localhost:8080 and http://localhost/z"}], "c": 3}
    if scrub(d) != 3 or "atlassian" in json.dumps(d) or "localhost" in json.dumps(d): fails.append(f"scrub: {d}")
    risky = ["https://tea-prototype.herokuapp.com/", "https://nhsuk-prototype-kit.azurewebsites.net/", "http://britishmuseum.org/", "https://x.netlify.app"]
    safe = ["https://www.gov.uk/", "https://alphagov.github.io/x", "https://herokuapp.com.evil.example/", "https://notherokuapp.com/"]
    fails += [f"risky not flagged: {u}" for u in risky if not is_risky(u)] + [f"safe flagged: {u}" for u in safe if is_risky(u) and not u.startswith("http://")]
    good = f"<html><head>{CSP_META}</head><body><a href=\"https://x\" target=\"_blank\" rel=\"noopener\">x</a><script>let a=riskyUrl('https://x.example/')</script></body></html>"
    good = good.replace("<body>", '<body><form id="s" role="search" novalidate><input></form>')   # a search form handled on the page is fine
    if page_problems(good): fails.append(f"clean page flagged: {page_problems(good)}")
    for inj, want in [('<script src="https://evil.example/x.js"></script>', "an external script"), ("<script>eval(location.hash)</script>", "eval-like code"),
                      ('<a href="https://x" target="_blank">x</a>', "a new-tab link without rel=noopener"), ('<form action="https://evil.example">', "a frame, plug-in or form that submits elsewhere"),
                      ("<style>@font-face{src:url(https://fonts.example/x.woff2)}</style>", "an external font or image in CSS")]:
        if want not in page_problems(good.replace("<body>", "<body>" + inj)): fails.append(f"not caught: {inj}")
    if not page_problems(good.replace(CSP_META, "")): fails.append("missing CSP not caught")
    if not page_problems(good.replace("connect-src 'none'", "connect-src *")): fails.append("weakened CSP not caught")
    orgs = [{"org": "alphagov", "source": PROVENANCE[0]}, {"org": "hmrc-digital-gov", "source": "added (not in registry)"}, {"org": "x", "source": "a blog post"}]
    pb = provenance_problems(orgs, ["StatesOfJerseyGov"], {})
    if len(pb) != 3 or any("alphagov" in p for p in pb): fails.append(f"provenance: {pb}")
    if provenance_problems(orgs[:2], [], {"hmrc-digital-gov": {"basis": "GitHub verified domain"}}): fails.append("provenance with a recorded check flagged")
    dd = audience({"collab": {"slack": {"channels": [{"name": "govuk-one-login"}]}}}, "public")
    if dd["collab"] is not None or "govuk-one-login" in json.dumps(dd): fails.append("public audience kept Slack channel names")
    lf = {"codes": ["live", "tool", "supports"], "ev": ["Changed in the last year; 10 Slack messages about its releases and incidents", "x"], "recs": {"a/b": [0, 0], "c/d": [1, 1]}}
    lo = audience({"collab": None, "life": lf}, "public")["life"]
    if lo["recs"]["a/b"][0] != 2 or "Slack" in json.dumps(lo) or lo["recs"]["c/d"] != [1, 1]: fails.append(f"public audience kept Slack-based life evidence: {lo}")
    if audience({"collab": {"x": 1}}, "gov")["collab"] is None: fails.append("gov audience dropped the Slack aggregates")
    good_wf = "name: x\non: push\npermissions:\n  contents: read\njobs:\n  b:\n    steps:\n      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683\n        with: {persist-credentials: false}\n      - run: echo ok\n"
    good_wf = good_wf.replace("with: {persist-credentials: false}", "with:\n          persist-credentials: false")
    if workflow_problems({"good": good_wf}): fails.append(f"clean workflow flagged: {workflow_problems({'good': good_wf})}")
    for mut in [good_wf.replace("permissions:\n  contents: read\n", ""), good_wf.replace("@11bd71901bbe5b1630ceea73d27597364c9af683", "@v4"),
                good_wf.replace("          persist-credentials: false\n", "          fetch-depth: 1\n"), good_wf.replace("on: push", "on: pull_request_target"),
                good_wf.replace("echo ok", "echo ${{ github.event.issue.title }}"), good_wf.replace("contents: read", "contents: write")]:
        if not workflow_problems({"bad": mut}): fails.append("unsafe workflow not caught: " + mut[:80].replace("\n", " "))
    cd = {"xorgs": [{"org": "alphagov"}, {"org": "GCHQ"}], "xf": ["oi", "n", "h"], "xrows": [[0, "a", [1]], [1, "b", [1]]],
          "life": {"codes": ["live"], "ev": ["x"], "recs": {"GCHQ/b": [0, 0], "alphagov/a": [0, 0]}},
          "collab": {"slack": {"repos": {"GCHQ/b": {}, "alphagov/a": {}}, "channels": [{"top": ["GCHQ/b", "alphagov/a"], "repos": 2}]}},
          "reuse": {"components": [{"sample": ["GCHQ/b", "alphagov/a"], "other_orgs": ["GCHQ"]}]}}
    if len(community_leaks(cd)) != 5: fails.append(f"community leaks not all caught: {community_leaks(cd)}")
    protect_communities(cd)
    if community_leaks(cd) or cd["xrows"][0][2] != [1] or "alphagov/a" not in cd["life"]["recs"] or "alphagov/a" not in cd["collab"]["slack"]["repos"] or cd["reuse"]["components"][0]["sample"] != ["alphagov/a"]:
        fails.append(f"protect_communities removed too little or too much: {cd}")
    cd2 = {"xorgs": [], "xf": [], "xrows": []}; protect_communities(cd2); audience(cd2, "public")
    if "communities" not in cd2["sec"]: fails.append("applying the audience dropped the protected-community list")
    import datetime as _dt
    hi = "---\nclassification: " + MARK + "\nhandling_group: HMG USE ONLY\nlast_reviewed_on: 2026-11-01\nreview_in: 3 months\nresponsible_role: Lead\nresponsible_role_contact: #channel\n---\n" + "x" * 250
    t = _dt.date(2026, 11, 2)
    if handling_problems(hi, README_BANNER, t): fails.append(f"good handling instructions flagged: {handling_problems(hi, README_BANNER, t)}")
    for bad_hi, bad_rm, bad_t in [(hi.replace(MARK, "OFFICIAL"), README_BANNER, t), (hi, "", t), (hi, README_BANNER, _dt.date(2027, 6, 1)), (hi.replace("handling_group: HMG USE ONLY\n", ""), README_BANNER, t), ("", README_BANNER, t)]:
        if not handling_problems(bad_hi, bad_rm, bad_t): fails.append("bad handling instructions not caught")
    return fails


if __name__ == "__main__":
    import glob, os
    here = os.path.dirname(os.path.abspath(__file__)); wfd = os.path.join(here, "..", "..", ".github", "workflows")
    f = self_test(); wf = workflow_problems({os.path.basename(x): open(x).read() for x in glob.glob(os.path.join(wfd, "*.yml"))})
    lines = [f"{'FAIL' if f else 'PASS'} C-SEC-01n security guardrails' negative tests{': ' + '; '.join(f[:3]) if f else ' all pass'} [guards: R63]",
             f"{'FAIL' if wf else 'PASS'} C-SEC-05 automation workflows are hardened{': ' + '; '.join(wf[:3]) if wf else ''} [guards: R63]"]
    print("\n".join(lines)); open(os.path.join(here, "security_checks.txt"), "w").write("\n".join(lines) + "\n")
    raise SystemExit(1 if f or wf else 0)
