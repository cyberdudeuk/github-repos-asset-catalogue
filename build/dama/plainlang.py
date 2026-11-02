"""Plain language check (7.11, R62): the short texts people meet first, the hub blurbs and the one-line summary of every
view, are measured for reading level. GOV.UK aims for text a 9 year old can read; this checks each summary has sentences of
25 words or fewer and an estimated reading grade (Flesch-Kincaid) of 12 or less, and reports the average. The estimate
counts syllables with a simple rule, so treat it as a guide. Writes plainlang_checks.txt. Run with python3 -I.
"""
import os, re, sys
S = os.path.dirname(os.path.abspath(__file__)); INV = os.path.join(os.path.dirname(S), "inv")
def syll(w):
    w = w.lower(); w = re.sub(r"[^a-z]", "", w)
    if not w: return 0
    n = len(re.findall(r"[aeiouy]+", w)); n -= 1 if w.endswith("e") and not w.endswith(("le", "ee")) and n > 1 else 0
    return max(1, n)
def grade(t):
    sents = [s for s in re.split(r"(?<=[.!?:;])\s+", t.strip()) if s]; words = re.findall(r"[A-Za-z][A-Za-z'-]*", t)
    if not words: return 0, 0
    return round(0.39 * len(words) / max(1, len(sents)) + 11.8 * sum(syll(w) for w in words) / len(words) - 15.59, 1), max(len(re.findall(r"[A-Za-z][A-Za-z'-]*", s)) for s in sents)
if __name__ == "__main__":
    js = open(os.path.join(INV, "v71_js1.part"), encoding="utf-8").read()
    texts = [(k, v) for k, v in re.findall(r'(\w+):"([^"]{25,})"', js[js.index("const VIEW_SUM"):js.index("};", js.index("const VIEW_SUM"))])]
    texts += [("hub " + k, v) for k, v in re.findall(r'id:"(\w+)"[^}]*?blurb:"([^"]+)"', js)]
    res = [(k, *grade(v)) for k, v in texts]
    hard = [(k, g, l) for k, g, l in res if g > 12 or l > 25]
    avg = round(sum(g for _, g, _ in res) / len(res), 1)
    tests = [grade("The cat sat on the mat. It was warm.")[0] < 4, grade("Interoperability considerations necessitate comprehensive organisational harmonisation of heterogeneous infrastructure.")[0] > 12]
    lines = [f"{'PASS' if not hard and all(tests) else 'FAIL'} C-PLN-01 the {len(res)} view summaries and hub blurbs people meet first read at an average estimated grade of {avg}, every one at grade 12 or below with sentences of 25 words or fewer (too hard: {hard[:6]}) [guards: R62]",
             f"{'PASS' if all(tests) else 'FAIL'} C-PLN-01n negative tests: a simple sentence scores below grade 4 and a sentence of long Latinate words scores above grade 12 [guards: R62]"]
    print("\n".join(lines)); open(os.path.join(S, "plainlang_checks.txt"), "w").write("\n".join(lines) + "\n")
    sys.exit(0 if all(l.startswith("PASS") for l in lines) else 1)
