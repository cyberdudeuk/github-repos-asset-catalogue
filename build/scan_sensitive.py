"""Refuse the build if the repository holds personal or internal data (C-SAN-01).
Run with: python3 -I build/scan_sensitive.py [extra files...]. Exit code 1 lists every finding.
Rules: no email addresses, no links to private Claude apps or design projects, no protective markings,
no named owners in the v1 workbook, no contributor names in the page data. A self-test plants one
example of each rule and fails the scan if any is missed (the vaccination for this check)."""
import json, os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES = [
    ("email address", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")),
    ("private app link", re.compile(r"claude\.ai/(?:artifact|design|chat|project)/", re.I)),
    ("protective marking", re.compile(r"OFFICIAL[- ]SENSITIVE|\bTOP SECRET\b")),
    ("former team name", re.compile(r"\bOCDO\b")),
]
ALLOW_EMAIL = {"noreply@anthropic.com", "partnerships@github.com"}   # commit trailer; GitHub's own published address in its documentation excerpts

def findings(name, text):
    out = []
    for rule, rx in RULES:
        for m in rx.finditer(text):
            e = m.group(0).lower()
            if rule == "email address" and (e in ALLOW_EMAIL or e.startswith("git@github.com") or e.endswith(("@example.com", "@nowhere.com"))): continue   # commit trailer, git remotes, documentation placeholders
            if rule == "email address" and re.search(r"\.(png|svg|jpe?g|gif|woff2?)$", m.group(0), re.I): continue   # name@2x.png style asset names
            out.append(f"{name}: {rule}: {text[max(0, m.start() - 30):m.end() + 10]!r}")
    return out

def v1_findings(path):
    d = json.load(open(path)); out = []
    for k, e in d["repos"].items():
        own = (e.get("collected") or {}).get("Named owner", "")
        if e.get("owner") and not e["owner"].startswith("(withheld"): out.append(f"v1 repos.{k}.owner is not withheld")
        if own and not (own.startswith("(withheld") or re.match(r"(None|Not) evidenced", own)): out.append(f"v1 repos.{k} named owner is not withheld")
    for a in d["actions"]:
        if not (a.get("owner", "").startswith("(withheld") and a.get("accountable", "").startswith("(withheld")): out.append(f"v1 action {a['id']} names a person")
    for e in d["evidence"]:
        if e.get("internal") and e.get("link"): out.append(f"v1 evidence {e['id']} links an internal source")
    for u in d["unlisted"]:
        if not re.fullmatch(r"unlisted-\d\d", u["name"]): out.append("v1 unlisted repository name is not withheld")
    return out

def data_findings(path):
    d = json.load(open(path)); out = []
    for r in d.get("rows", []):
        if r.get("top_contributors_12m") or r.get("top_contributors_all"): out.append(f"data.json {r.get('repo')}: contributor names present")
    return out

def self_test():
    planted = ["someone@example.gov.uk", "https://claude.ai/artifact/ABC", "https://claude.ai/design/p/1", "OFFICIAL-SENSITIVE", "the OCDO team"]
    missed = [p for p in planted if not findings("planted", p)]
    clean = findings("clean", "icon@2x.png noreply@anthropic.com OFFICIAL guidance")
    return missed, clean

def main():
    missed, clean = self_test()
    if missed or clean: print("C-SAN-01 self-test failed:", missed, clean); return 1
    args = sys.argv[1:]; sources_only = "--sources" in args; args = [a for a in args if a != "--sources"]
    files = [f for f in subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).split() if not (sources_only and f.startswith("dist/"))] + args   # --sources: during the build, before dist/ is replaced
    out = []
    for f in sorted(set(files)):
        p = f if os.path.isabs(f) else os.path.join(ROOT, f)
        if not os.path.isfile(p) or re.search(r"\.(woff2?|png|jpe?g|gif|ico)$", p): continue
        try: t = open(p, encoding="utf-8", errors="ignore").read()
        except OSError: continue
        out += findings(f, t)
    out += v1_findings(os.path.join(ROOT, "build/v1/v1_layer.json"))
    out += data_findings(os.path.join(ROOT, "build/inv/data.json"))
    for o in out: print(o)
    print(f"C-SAN-01 {'FAIL' if out else 'pass'}: {len(out)} findings in {len(set(files))} files; self-test caught {5 - len(missed)} of 5 planted examples")
    return 1 if out else 0

if __name__ == "__main__": sys.exit(main())
