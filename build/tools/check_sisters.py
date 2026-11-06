"""Weekly check of the join-up with the two sister portals (R73, threat T10's cousin: links that quietly break).

Reads each sister portal's cross-reference manifest and every page the catalogue links to, and reports:
  - a shared key the catalogue relies on that the sister portal no longer publishes (DAMA codes, standard ids)
  - a page the catalogue links to that doesn't answer with 200
  - a manifest that can't be read
It only reads public web pages: no token, no tracking, and it never changes anything. The weekly self-routines
workflow appends its report to the health issue. Run with python3 -I build/tools/check_sisters.py [--self-test].
"""
import json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def fetch(url, timeout=30):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "ghrac-sister-check"}), timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return 0, ""


def key_problems(snap, live_dam, live_dqc, keys):
    """Keys the catalogue uses that a sister portal's live manifest doesn't hold."""
    bad = []
    if live_dam is None: bad.append("the DAM playbooks' manifest couldn't be read")
    else:
        have = {x["id"] for x in live_dam.get("keys", {}).get("dama_areas", [])}
        bad += [f"DAM playbooks no longer publish DAMA area {k}" for k in keys["dama"].values() if k not in have]
    if live_dqc is None: bad.append("the DQ Commons' manifest couldn't be read")
    else:
        have = {x["id"] for x in live_dqc.get("keys", {}).get("standards", [])}
        bad += [f"DQ Commons no longer publishes standard id {k}" for k in keys["standards"].values() if k not in have]
    return bad


def page_links(html):
    """The sister-portal addresses the published page links to."""
    rel = re.search(r"const REL_P = (\{.*?\});\nconst REL_AT = (\{.*?\});\nfunction relElse", html, re.S)
    if not rel: return []
    base = dict(re.findall(r'(dam|dqc): \{name: "[^"]*", status: "[^"]*", url: "([^"]+)"', rel.group(1)))
    return sorted({base[p] + path.split("#")[0] for p, path in re.findall(r'\["(dam|dqc)", "([^"]+)"', rel.group(2)) if p in base})


def self_test():
    keys = {"dama": {"gov": "DM-GOV"}, "standards": {"DCAT": "dcat3"}}
    ok_dam = {"keys": {"dama_areas": [{"id": "DM-GOV"}]}}; ok_dqc = {"keys": {"standards": [{"id": "dcat3"}]}}
    probs = []
    if key_problems({}, ok_dam, ok_dqc, keys): probs.append("matching manifests reported as drift")
    if not key_problems({}, {"keys": {"dama_areas": []}}, ok_dqc, keys): probs.append("a missing DAMA area isn't caught")
    if not key_problems({}, ok_dam, None, keys): probs.append("an unreadable manifest isn't caught")
    page = 'const REL_P = {\n  dam: {name: "D", status: "s", url: "https://d/"},\n  dqc: {name: "Q", status: "s", url: "https://q/"}};\nconst REL_AT = {\n  dama: [["dam", "a.html#x", "t", "w"], ["dqc", "b.html", "t", "w"]]};\nfunction relElse'
    if page_links(page) != ["https://d/a.html", "https://q/b.html"]: probs.append("links aren't read from the page")
    return probs


def main():
    if "--self-test" in sys.argv:
        p = self_test(); print("\n".join(p) or "ok"); return 1 if p else 0
    snap = json.load(open(os.path.join(ROOT, "build", "dama", "sister_keys.json")))
    html = open(os.path.join(ROOT, "dist", "index.html"), encoding="utf-8").read()
    i = html.index("const DATA = ") + len("const DATA = "); data = json.JSONDecoder().raw_decode(html[i:])[0]
    live = {}
    for k in ("dam", "dqc"):
        code, body = fetch(snap[k]["manifest"])
        try: live[k] = json.loads(body) if code == 200 else None
        except ValueError: live[k] = None
    probs = key_problems(snap, live["dam"], live["dqc"], data["xref_keys"])
    for u in page_links(html):
        code, _ = fetch(u)
        if code != 200: probs.append(f"{u} answered {code or 'nothing'}")
    lines = ["## Sister portals (R73)", "",
             f"- DAM playbooks manifest: {'version ' + live['dam'].get('version', '?') if live['dam'] else 'not readable'}",
             f"- DQ Commons manifest: {'version ' + live['dqc'].get('version', '?') if live['dqc'] else 'not readable'}"]
    lines += [f"- Problem: {p}" for p in probs] or ["- Every shared key and every linked page is in place."]
    report = "\n".join(lines) + "\n"
    print(report)
    if os.path.exists("self_report.md"):
        with open("self_report.md", "a") as f: f.write("\n" + report)
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
