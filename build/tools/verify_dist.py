"""Check the published page, dist/index.html, without the internal-only inputs (ADR 0004).

The public repository can't rebuild the page, because the full build needs inputs that live in the private companion
repository. So this checks what it can, and the companion repository's workflow rebuilds both editions and compares
them byte for byte.
  C-DIST-01  the page's code is exactly the code in this commit: the parts, assembled, match the page once its
             embedded data and fonts are set aside
  C-DIST-02  the page is the open edition: no Slack aggregates, no co-cddo move proposals, no inferences about
             defence, intelligence and national security accounts, and the Content-Security-Policy is in place
Run with python3 -I build/tools/verify_dist.py. Exit code 1 if a check fails.
"""
import json, os, re, runpy, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SEC = runpy.run_path(os.path.join(ROOT, "build", "dama", "security.py"))


def split_page(html):
    """(code, data): the page with its data blob and font faces replaced by markers, and the parsed data."""
    i = html.index("const DATA = ") + len("const DATA = ")
    data, end = json.JSONDecoder().raw_decode(html[i:])
    code = html[:i] + "/*__DATA__*/null" + html[i + end:]
    code = re.sub(r"@font-face\{[^}]*\}\n?", "", code)
    return code, data


def code_of_template(tpl):
    return tpl.replace("/*__FONTS__*/\n", "").replace("/*__FONTS__*/", "")


def open_edition_problems(data, html):
    bad = []
    if (data.get("sec") or {}).get("audience") != "public": bad.append("not built for the public audience")
    if data.get("collab") is not None: bad.append("holds the Slack aggregates")
    if "public_channels" in json.dumps(data): bad.append("names Slack channels")
    bad += ["co-cddo move: " + x for x in SEC["move_leaks"](data)[:3]]
    bad += ["national security inference: " + x for x in SEC["community_leaks"](data)[:3]]
    if SEC["CSP_META"] not in html: bad.append("no Content-Security-Policy")
    return bad


def main():
    dist = open(os.path.join(ROOT, "dist", "index.html"), encoding="utf-8").read()
    page = dist.split("\n", 3)[3]                                   # the first three lines are the document head
    subprocess.run(["sh", os.path.join(ROOT, "build", "inv", "assemble71.sh")], check=True, capture_output=True)
    tpl = open(os.path.join(ROOT, "build", "inv", "explorer71.tpl.html"), encoding="utf-8").read()
    code, data = split_page(page)
    want = SEC["CSP_META"] + "\n" + code_of_template(tpl)
    same = code == want
    probs = open_edition_problems(data, page)
    # negative tests: a changed line of code, and a government-edition page, are both caught
    neg_code = split_page(page.replace("const DATA = ", "const X = 1;\nconst DATA = ", 1))[0] != want
    gov = json.loads(json.dumps(data)); gov["sec"]["audience"] = "gov"; gov["collab"] = {"slack": {"repos": {}, "channels": []}}
    gov.setdefault("rows", []).append({"repo": "x", "destination": "gds-dtx"})
    neg_gov = len(open_edition_problems(gov, page)) >= 3
    lines = [f"{'PASS' if same and neg_code else 'FAIL'} C-DIST-01 the published page's code is exactly this commit's code (its embedded data and fonts set aside); negative test: one added line is caught",
             f"{'PASS' if not probs and neg_gov else 'FAIL'} C-DIST-02 the published page is the open edition: no Slack aggregates, no co-cddo move proposals, no inferences about defence, intelligence and national security accounts, and a Content-Security-Policy" + (f" (problems: {probs})" if probs else "") + "; negative test: a government-edition page is caught"]
    if not same:
        a, b = code, want
        k = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), min(len(a), len(b)))
        lines.append(f"  first difference at character {k}: page {a[k:k + 80]!r} / code {b[k:k + 80]!r}")
    print("\n".join(lines))
    return 0 if all(l.startswith("PASS") for l in lines[:2]) else 1


if __name__ == "__main__":
    sys.exit(main())
