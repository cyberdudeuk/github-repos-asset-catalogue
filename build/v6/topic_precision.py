"""Measured precision of each topic (RM-02): recomputed from the judgements in topic_judgements.json under the current rules,
so a rule change can't keep a score it no longer earns.  python3 -I build/v6/topic_precision.py
Writes topic_precision.json (read by the page) and topic_checks.txt."""
import json
import os
import re
import subprocess
import sys

H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from topics import TOPICS, topic_text

BAR = 0.7   # below this a topic is shown as a candidate for review, as strategy tags are


def wilson(k, n, z=1.96):
    """95% interval for a proportion from a small sample (Wilson score), so the page can say how sure the figure is."""
    if not n: return None, None
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return round((c - h) / d, 3), round((c + h) / d, 3)


def measure(judgements, topics=TOPICS):
    out = {}
    for t in topics:
        rx = re.compile(t[3], re.I); J = judgements.get(t[0], {})
        still = [v["ok"] for k, v in J.items() if rx.search(topic_text(t[0], v["q"]))]
        tp, fp, un = still.count(True), still.count(False), still.count(None)
        out[t[0]] = dict(n=len(still), judged=len(J), tp=tp, fp=fp, unsure=un, precision=round(tp / (tp + fp), 3) if tp + fp else None)
        out[t[0]]["low"], out[t[0]]["high"] = wilson(tp, tp + fp)
    return out


def main():
    d = json.load(open(os.path.join(H, "topic_judgements.json")))
    P = measure(d["judgements"])
    checks = []
    def check(ok, cid, msg, guards): checks.append(("PASS " if ok else "FAIL ") + f"{cid} {msg}   [guards: {guards}]")
    check(all(P[t[0]]["n"] for t in TOPICS), "C-TOP-01", f"every one of the {len(TOPICS)} topics has a measured precision from a judged sample "
          f"({sum(p['n'] for p in P.values())} judgements still apply under the current rules, of {sum(p['judged'] for p in P.values())} made)", "RM-02")
    low = [k for k, p in P.items() if p["precision"] is not None and p["precision"] < BAR]
    check(not low, "C-TOP-02", f"every topic is at least {int(BAR * 100)}% precise on its sample (lowest: " +
          ", ".join(f"{k} {round(100 * p['precision'])}%" for k, p in sorted(P.items(), key=lambda x: x[1]["precision"] or 1)[:3]) + f"; below the bar: {low})", "RM-02, V718-2")
    fake = {"place": {"x": dict(ok=False, q="a/" + "transport " * 3), "y": dict(ok=True, q="a/postcode")}}
    neg = measure(fake, [t for t in TOPICS if t[0] == "place"])["place"]
    t = subprocess.run([sys.executable, "-I", os.path.join(H, "test_topics.py")], capture_output=True, text=True)
    check(t.returncode == 0 and neg["fp"] == 1 and neg["precision"] == 0.5, "C-TOP-03",
          f"every false match found in the samples has a negative test that passes ({t.stdout.strip()}); negative test: a judged wrong match lowers the score", "V718-2")
    json.dump(dict(read=d["read"], method=d["method"], bar=BAR, content_only=sorted(__import__("topics").CONTENT_ONLY), topics=P), open(os.path.join(H, "topic_precision.json"), "w"), indent=1)
    open(os.path.join(H, "topic_checks.txt"), "w").write("\n".join(checks) + "\n")
    print("\n".join(checks))
    for k, p in P.items(): print(f"  {k:12} {p['tp']}/{p['tp'] + p['fp']} = {p['precision']}  (unsure {p['unsure']}, judged {p['judged']})")
    return 0 if all(c.startswith("PASS") for c in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
