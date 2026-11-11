"""No two parts of the page may declare the same top-level name (V717-5).

  python3 -I build/tools/js_names.py [build/inv/explorer71.tpl.html]

A function declared twice in one script is silently replaced by the later one, so a new view can break an old one with no
error (7.17.0: a new aFiltered() replaced the API catalogue's). Every top-level function, const, let and class name in the
page's scripts is listed, and any name declared more than once fails. Writes build/inv/js_checks.txt.
"""
import collections
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DECL = re.compile(r"^(?:async\s+)?(?:function\*?\s+([A-Za-z_$][\w$]*)|(?:const|let|class)\s+([A-Za-z_$][\w$]*))", re.M)


def names(js):
    """Top-level declarations: lines that start at column 0 (the page's own style for top-level code)."""
    c = collections.Counter()
    for m in DECL.finditer(js):
        c[m.group(1) or m.group(2)] += 1
    return c


def scripts(html):
    """Every script's text. The end tag may carry spaces or attributes before its '>' (V717-11: '</script >' was missed)."""
    return "\n".join(re.findall(r"<script\b[^>]*>(.*?)</script\b[^>]*>", html, re.S | re.I))


def main(path):
    js = scripts(open(path, encoding="utf-8").read())
    c = names(js); dup = sorted(n for n, k in c.items() if k > 1)
    neg = names("function aFiltered() {}\nfunction aFiltered() {}\nconst x = 1;\n")
    spaced = names(scripts("<script>function a() {}\n</script >\n<script type='module'>\nfunction a() {}\n</SCRIPT\n>"))
    ok_neg = neg["aFiltered"] == 2 and neg["x"] == 1 and spaced["a"] == 2
    lines = [("PASS " if not dup else "FAIL ") + f"C-JS-01 no top-level name is declared twice in the page's scripts ({len(c)} names; twice: {dup[:8]})   [guards: V717-5]",
             ("PASS " if ok_neg else "FAIL ") + "C-JS-01n negative tests: a function declared twice is caught, including in scripts whose end tag carries a space or a line break   [guards: V717-5, V717-11]"]
    open(os.path.join(ROOT, "build", "inv", "js_checks.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if not dup and ok_neg else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "build", "inv", "explorer71.tpl.html")))
