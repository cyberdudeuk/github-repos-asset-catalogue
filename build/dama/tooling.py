"""Join the tooling register to everything that shows a tool in use across the public sector (R76, R77).

  python3 -I build/dama/tooling.py

Evidence, each with who, what for, where, when, how and through whom:
  repositories   tool_repo_ev.json.gz: a public body's repository depends on, configures, names or mentions the tool
  notices        procure/sources/{fts,cf}.json.gz: a tender or contract notice names the product, or awards its maker
  G-Cloud        procure/sources/gcloud.json.gz: a supplier offers a service built on the tool to the public sector
  case studies   procure/cases.py: the tool's supplier names a public-sector customer on its own website
A maker awarded a contract is only evidence for a tool when the maker sells little else (tools.py leaves the supplier pattern
empty for Microsoft, Amazon, Google, Oracle, SAP, IBM and other makers of many products).
Personal names quoted in notice descriptions are removed with pii.scrub. Writes tooling.json and tooling_checks.txt.
"""
import collections
import json
import os
import re
import sys

H = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(H)
sys.path.insert(0, H); sys.path.insert(0, os.path.join(B, "refresh")); sys.path.insert(0, os.path.join(B, "procure"))
from common import ASOF, read_json
from tools import TOOLS, PRECISION, text_rx, supplier_rx
from cases import CASES
import pii
import clean

PROC = os.path.join(B, "procure", "sources")
pii_scrub = lambda t: (clean.text(t), [])   # one cleaning step for quoted text (clean.py, V717-8)
SECTOR_RX = [("Health and care", r"\bnhs\b|trust\b|health|hospital|ambulance|integrated care|\bicb\b|clinical|care quality"),
             ("Local government", r"council|borough|county|combined authority|city of|metropolitan|district\b|parish|unitary|fire and rescue|\bgla\b|greater london authority"),
             ("Justice and policing", r"police|constabulary|crime|prison|probation|court|justice|crown prosecution|sfo\b"),
             ("Defence and security", r"defence|ministry of defence|\bmod\b|royal navy|army|royal air force|dstl|security"),
             ("Education", r"university|college|school|academy|education|students|ofsted|skills"),
             ("Devolved government", r"scottish government|welsh government|llywodraeth|northern ireland|stormont|\bdaera\b"),
             ("Central government", r"department|ministry|\bhm\b|cabinet office|treasury|home office|office for|agency|commission|executive|authority|revenue|service\b"),
             ("Housing", r"housing|homes")]
SRX = [(s, re.compile(r, re.I)) for s, r in SECTOR_RX]


def sector(name):
    for s, rx in SRX:
        if rx.search(name or ""): return s
    return "Other public body"


def norm_buyer(n):
    n = re.sub(r"\s+", " ", (n or "").strip())
    n = re.sub(r"(?i)^the\s+", "", n)
    return n


def load_notices():
    rows = []
    for src in ("fts", "cf"):
        p = os.path.join(PROC, f"{src}.json.gz")
        if os.path.exists(p): rows += read_json(p)["rows"]
    # one record per procurement (ocid): the award stage wins over the tender stage, then the newest
    best = {}
    rank = lambda r: (("award" in r["tag"] or "contract" in r["tag"]) * 2 + bool(r["suppliers"]), r["date"])
    for r in rows:
        k = r["ocid"] or r["id"]
        if k not in best or rank(r) > rank(best[k]): best[k] = r
    return list(best.values()), len(rows)


def notice_count_problems(d):
    """What is wrong with the notice counts the page states (V717-9). Each stage can only shrink the one before it."""
    bad = []
    for k in ("releases_read", "filtered", "procurements", "matched"):
        if not isinstance(d.get(k), int) or d[k] < 0: bad.append(f"{k} missing")
    if bad: return bad
    if not d["releases_read"] >= d["filtered"] >= d["procurements"] >= d["matched"]: bad.append("a stage is larger than the one before it")
    if "read" in d or "kept" in d: bad.append("an ambiguous label (read, kept) is used")
    return bad


def main():
    checks = []
    def check(ok, cid, msg, guards): checks.append(("PASS " if ok else "FAIL ") + f"{cid} {msg}   [guards: {guards}]"); return ok
    D = json.load(open(os.path.join(H, "dmbok.json")))
    acts = {a["id"]: a for a in D["activities"]}
    T = {t["id"]: t for t in TOOLS}
    bad_acts = [(t["id"], a) for t in TOOLS for a in t["acts"] if a not in acts]
    check(not bad_acts, "C-TOOL-01", f"every one of the {len(TOOLS)} tools names activities that exist ({bad_acts[:3]})", "R76")
    check(len(T) == len(TOOLS), "C-TOOL-02", "every tool has its own identifier", "R76")
    # ---- repositories ----
    RE = read_json(os.path.join(H, "tool_repo_ev.json.gz"))
    cat = json.load(open(os.path.join(B, "catalogue", "catalogue.json")))
    osec = {o["org"].lower(): o["sector"] for o in cat["orgs"]}
    repo_ev = {tid: [[k, kind, pii_scrub(sn)[0] if sn else ""] for k, kind, sn in v] for tid, v in RE["ev"].items() if tid in T}
    # ---- notices ----
    N, raw = load_notices()
    TXT = [(t["id"], text_rx(t)) for t in TOOLS if t["text"]]
    SUP = [(t["id"], supplier_rx(t)) for t in TOOLS if t["supplier"]]
    used, nev = {}, collections.defaultdict(list)
    for r in N:
        text = r["title"] + " " + r["desc"]
        sups = " ; ".join(s.get("name") or "" for s in r["suppliers"])
        hits = {}
        for tid, rx in TXT:
            m = rx.search(text)
            if m: hits[tid] = ["named", re.sub(r"\s+", " ", text[max(0, m.start() - 60):m.end() + 60]).strip()]
        for tid, rx in SUP:
            if tid not in hits and sups and rx.search(sups): hits[tid] = ["supplier", ""]
        if not hits: continue
        k = r["ocid"] or r["id"]
        if k not in used:
            b = norm_buyer(r["buyer"])
            used[k] = len(used)
            used[k] = [len(used) - 1, dict(src=r["src"], id=r["id"], tag=r["tag"], date=r["date"], buyer=b, sector=sector(b), region=r["region"], title=pii_scrub(r["title"])[0],
                                            desc=pii_scrub(r["desc"][:500])[0], value=r["value"], suppliers=sorted({s.get("name") for s in r["suppliers"] if s.get("name")}),
                                            method=r["method"], start=r["start"], end=r["end"], url=r["url"], cpv=r["cpv"][:4])]
        for tid, (how, sn) in hits.items(): nev[tid].append([used[k][0], how, pii_scrub(sn)[0][:200]])
    notices = [v[1] for v in sorted(used.values(), key=lambda x: x[0])]
    for n in notices: n["desc"] = n["desc"][:320]; n["url"] = re.sub(r"^https://www\.(find-tender|contractsfinder)\.service\.gov\.uk/Notice/", "", n["url"])
    NCOLS = ["src", "id", "tag", "date", "buyer", "sector", "region", "title", "desc", "value", "suppliers", "method", "start", "end", "url", "cpv"]
    # ---- G-Cloud ----
    gp = os.path.join(PROC, "gcloud.json.gz")
    G = read_json(gp)["tools"] if os.path.exists(gp) else {}
    gev = {}; GCOLS = ["id", "title", "supplier", "summary", "lot", "framework"]
    for tid, items in G.items():
        if tid not in T: continue
        rx = text_rx(T[tid])
        keep = [dict(i, summary=pii_scrub(i["summary"][:220])[0]) for i in items if rx and rx.search(i["title"] + " " + i["summary"])]
        if keep: gev[tid] = keep
    # ---- case studies ----
    cev = collections.defaultdict(list)
    for c in CASES: cev[c["tool"]].append(c)
    check(all(c["tool"] in T for c in CASES), "C-TOOL-03", f"every case study ({len(CASES)}) names a tool in the register", "R76")
    # ---- per tool summary ----
    out_tools = []
    for t in TOOLS:
        tid = t["id"]; rv = repo_ev.get(tid, []); nv = nev.get(tid, [])
        # value: award and contract notices only, and not frameworks: a notice awarding more than three suppliers carries a
        # ceiling the suppliers share, so it is listed but adds nothing to a tool's value
        vals = [notices[i]["value"] for i, how, _ in nv if notices[i]["value"] and ("award" in notices[i]["tag"] or "contract" in notices[i]["tag"]) and len(notices[i]["suppliers"]) <= 3]
        life = sorted({l for a in t["acts"] for l in acts[a]["life"]}, key=lambda l: ["plan", "create", "store", "process", "use", "share", "archive", "dispose"].index(l))
        out_tools.append(dict(id=tid, name=t["name"], maker=t["maker"], model=t["model"], acts=t["acts"], areas=sorted({acts[a]["area"] for a in t["acts"]}), life=life,
                              n=dict(repos=len(rv), code=sum(1 for _, k, _ in rv if any(c in k for c in "dfi")), orgs=len({k.split("/")[0].lower() for k, _, _ in rv}),
                                     notices=len(nv), named=sum(1 for _, h, _ in nv if h == "named"), buyers=len({notices[i]["buyer"].lower() for i, _, _ in nv}),
                                     value=round(sum(vals)), gcloud=len(gev.get(tid, [])), gsup=len({g["supplier"] for g in gev.get(tid, [])}), cases=len(cev.get(tid, []))),
                              sectors=collections.Counter(osec.get(k.split("/")[0].lower(), "Other") for k, _, _ in rv).most_common() + [],
                              bsectors=collections.Counter(notices[i]["sector"] for i, _, _ in nv).most_common(),
                              years=sorted(collections.Counter(notices[i]["date"][:4] for i, _, _ in nv).items())))
    fw = [n for n in notices if len(n["suppliers"]) > 3 and n["value"]]
    fw_ids = {i for i, n in enumerate(notices) if len(n["suppliers"]) > 3}
    ok_v = all(t["n"]["value"] == round(sum(notices[i]["value"] for i, _, _ in nev.get(t["id"], []) if notices[i]["value"] and ("award" in notices[i]["tag"] or "contract" in notices[i]["tag"]) and i not in fw_ids)) for t in out_tools)
    check(ok_v, "C-TOOL-11", f"a tool's value counts award and contract notices only, never a framework's shared ceiling ({len(fw)} notices award more than three suppliers and are listed without adding to any value)", "V717-8")
    evid = sum(1 for t in out_tools if sum(t["n"][k] for k in ("repos", "notices", "gcloud", "cases")))
    check(evid >= 0.6 * len(out_tools), "C-TOOL-04", f"{evid} of {len(out_tools)} tools have evidence of use in the public sector", "R76")
    no_tool = sorted(a for a in acts if not any(a in t["acts"] for t in TOOLS))
    unexplained = [a for a in no_tool if not acts[a]["people"]]
    check(not [a for a in acts if acts[a]["people"] and a not in no_tool], "C-TOOL-07", "no activity is marked as led by people while the register names a tool for it", "R76")
    check(not unexplained, "C-TOOL-05", f"every activity has a tool that delivers it, or is marked as led by people and decisions ({len(no_tool)} are; unexplained: {unexplained})", "R76")
    neg = [all(x in acts for x in ["NO-01"]), not supplier_rx(dict(supplier="")) is None, not [a for a in ["GOV-04"] if not any(a in t["acts"] for t in TOOLS[:0]) and not acts[a]["people"]]]
    check(not any(neg), "C-TOOL-05n", "negative tests: an unknown activity, an empty supplier pattern and a tool-less activity that is not people-led are each caught", "R76")
    import subprocess
    st = subprocess.run([sys.executable, "-I", os.path.join(B, "procure", "collect.py"), "--self-test"], capture_output=True, text=True)
    src = {k: read_json(os.path.join(PROC, f"{k}.json.gz")) for k in ("fts", "cf") if os.path.exists(os.path.join(PROC, f"{k}.json.gz"))}
    recorded = all("releases_read" in v and "windows_split" in v for v in src.values()) and len(src) == 2
    summary = ", ".join("%s: %s read, %s windows split" % (k, format(v.get("releases_read", 0), ","), v.get("windows_split", 0)) for k, v in src.items())
    check(st.returncode == 0 and recorded, "C-TOOL-09", f"notice lists cut short are caught and read again (self-test: {st.stdout.strip()}); both sources record what they read ({summary})", "V717-6")
    check(not clean.self_test(), "C-TOOL-10", "quoted text is cleaned the same way everywhere: names, email addresses in any field, quoted security classifications and a renamed team's acronym (self-test)", "V717-8")
    import test_tools
    check(test_tools.main() == 0, "C-TOOL-08", "every false match found in the precision samples has a negative test that passes, and every tool kept a positive one", "V717-4")
    leak = [n for n in notices if re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", n["desc"] + n["title"])]
    for n in leak: n["desc"] = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "[address removed]", n["desc"]); n["title"] = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "[address removed]", n["title"])
    check(not [n for n in notices if re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", n["desc"] + n["title"])], "C-TOOL-06", f"no email address is quoted from a notice ({len(leak)} removed)", "contact by form only")
    NC = dict(releases_read=sum(v.get("releases_read", 0) for v in src.values()), filtered=raw, procurements=len(N), matched=len(notices),
              fts="fts" in src, cf="cf" in src, since="2021-01-01")
    neg = [notice_count_problems(dict(NC, read=raw)), notice_count_problems(dict(NC, procurements=raw + 1)), notice_count_problems({})]
    check(not notice_count_problems(NC) and all(neg), "C-TOOL-12",
          f"the page's notice counts are each stage of one funnel: {NC['releases_read']:,} read, {NC['filtered']:,} about software, IT or data, {NC['procurements']:,} procurements, {NC['matched']:,} name a tool (negative tests: an ambiguous label, a stage larger than the one before, missing counts)", "V717-9")
    out = dict(read=ASOF["ref"], sources=dict(
        repos=dict(n=RE["repos"], readmes=RE["readmes"], read=RE["read"], code_read=RE["code_read"]),
        notices=NC,
        gcloud=dict(listings=sum(len(v) for v in gev.values()), framework="G-Cloud 15"), cases=dict(n=len(CASES), read=CASES[0]["read"] if CASES else None)),
        precision=PRECISION, tools=out_tools, no_tool=no_tool, repo_ev=repo_ev, ncols=NCOLS, nrows=[[n[c] for c in NCOLS] for n in notices], notice_ev=dict(nev),
        gcols=GCOLS, gcloud={k: [[g[c] for c in GCOLS] for g in v] for k, v in gev.items()}, cases=dict(cev))
    json.dump(out, open(os.path.join(H, "tooling.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    open(os.path.join(H, "tooling_checks.txt"), "w").write("\n".join(checks) + "\n")
    print("\n".join(checks))
    print(f"{len(notices)} notices name a tool, of {len(N)} procurements ({raw} notices about software, IT or data); G-Cloud {sum(len(v) for v in gev.values())}; bytes {os.path.getsize(os.path.join(H, 'tooling.json')):,}")
    for t in sorted(out_tools, key=lambda t: -(t["n"]["notices"] + t["n"]["repos"]))[:20]: print(" ", t["id"], t["n"])
    return 0 if all(c.startswith("PASS") for c in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
