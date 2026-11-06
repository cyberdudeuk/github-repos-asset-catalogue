"""Collect ideas, votes, survey totals and research sign-up counts from the catalogue's public issues (R74).

The weekly self-routines workflow lists the issues with GitHub's own CLI and pipes them here:

    gh issue list --label idea --state all --limit 1000 --json number,title,state,labels,reactionGroups,createdAt,url > ideas_raw.json
    gh issue list --label survey-response --state all --limit 1000 --json number,body,createdAt > survey_raw.json
    gh issue list --label research --state all --limit 1000 --json number,state,createdAt > research_raw.json
    python3 -I build/tools/collect_ideas.py ideas_raw.json survey_raw.json research_raw.json build/dama/ideas.json

The result is uploaded for a person to review and commit: automation never pushes. It keeps only issue numbers, titles,
vote counts, states and the assessment labels for ideas; for the survey, totals per answer, with any count under 5
shown as "fewer than 5"; for research, how many people asked to take part. Never a username or any free text from
the survey or the sign-up form.
"""
import datetime as dt
import json
import re
import sys

SMALL = 5
SCORE_LABELS = ("value", "reach", "fit", "feasible")


def votes(issue):
    for g in issue.get("reactionGroups") or []:
        if g.get("content") == "THUMBS_UP":
            return int((g.get("users") or {}).get("totalCount", g.get("totalCount", 0)) or 0)
    return 0


def labels(issue):
    return [l["name"] if isinstance(l, dict) else str(l) for l in issue.get("labels") or []]


def idea_row(i):
    ls = labels(i)
    a = {}
    for l in ls:
        k, _, v = l.partition(":")
        if k in SCORE_LABELS and v.isdigit(): a[k] = int(v)
    return dict(n=i["number"], title=re.sub(r"^\[Idea\]\s*", "", i.get("title", ""))[:160], state=i.get("state", "").lower(), votes=votes(i), url=i.get("url", ""),
                scores=a, score=(a.get("value", 0) * 2 + a.get("reach", 0) + a.get("fit", 0) * 2 + a.get("feasible", 0)) if len(a) == 4 else None,
                moscow=next((l.split(":", 1)[1] for l in ls if l.startswith("moscow:")), None),
                horizon=next((l for l in ls if l in ("now", "next", "later")), None),
                themes=sorted(l.split(":", 1)[1] for l in ls if l.startswith("theme:")))


def fields(body):
    out = {}
    for m in re.finditer(r"(?ms)^### (.+?)\s*\n(.*?)(?=^### |\Z)", body or ""):
        v = m.group(2).strip(); out[m.group(1).strip()] = "" if v == "_No response_" else v
    return out


def survey_totals(issues, questions):
    """questions: {label: [options]}. Free text is never kept. Counts under 5 are hidden."""
    t = {q: {o: 0 for o in opts} for q, opts in questions.items()}
    for i in issues:
        f = fields(i.get("body"))
        for q, opts in questions.items():
            if f.get(q) in t[q]: t[q][f[q]] += 1
    return {q: {o: (n if n >= SMALL else ("fewer than 5" if n else 0)) for o, n in c.items()} for q, c in t.items()}


def collect(ideas, survey, research, questions):
    rows = [idea_row(i) for i in ideas]
    rows.sort(key=lambda r: (r["state"] != "open", -r["votes"], r["n"]))
    return dict(read=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), items=rows,
                survey=dict(responses=len(survey) if len(survey) >= SMALL or not survey else "fewer than 5", totals=survey_totals(survey, questions)),
                research=dict(signups=len(research) if len(research) >= SMALL or not research else "fewer than 5"))


def self_test():
    Q = {"Did you find what you came for?": ["Yes", "Partly", "No"]}
    ideas = [{"number": 3, "title": "[Idea] Maps", "state": "OPEN", "labels": [{"name": "idea"}, {"name": "value:2"}, {"name": "reach:2"}, {"name": "fit:3"}, {"name": "feasible:1"}, {"name": "theme:G3"}, {"name": "next"}],
              "reactionGroups": [{"content": "THUMBS_UP", "users": {"totalCount": 7}}], "url": "u", "author": {"login": "someone"}},
             {"number": 1, "title": "[Idea] Welsh", "state": "OPEN", "labels": [{"name": "idea"}], "reactionGroups": [{"content": "THUMBS_UP", "users": {"totalCount": 9}}], "url": "u"},
             {"number": 2, "title": "[Idea] Done thing", "state": "CLOSED", "labels": [{"name": "idea"}], "reactionGroups": [], "url": "u"}]
    body = lambda a: f"### Did you find what you came for?\n\n{a}\n\n### What's missing, or what would you change? (optional)\n\nmy name is X\n"
    survey = [{"body": body("Yes")} for _ in range(6)] + [{"body": body("No")} for _ in range(2)]
    out = collect(ideas, survey, [{"number": 9}], Q); probs = []
    if [r["n"] for r in out["items"]] != [1, 3, 2]: probs.append("ideas aren't ranked by open, then votes")
    m = next(r for r in out["items"] if r["n"] == 3)
    if m["score"] != 2 * 2 + 2 + 3 * 2 + 1 or m["themes"] != ["G3"] or m["horizon"] != "next": probs.append("assessment labels aren't read")
    if out["survey"]["totals"]["Did you find what you came for?"] != {"Yes": 6, "Partly": 0, "No": "fewer than 5"}: probs.append("a count under 5 isn't hidden")
    if out["research"]["signups"] != "fewer than 5": probs.append("a small sign-up count isn't hidden")
    if "someone" in json.dumps(out) or "my name" in json.dumps(out): probs.append("a username or free text is kept")
    return probs


def main(a):
    if a[1:] == ["--self-test"]:
        p = self_test(); print("\n".join(p) or "ok"); return 1 if p else 0
    if len(a) != 5: sys.exit(__doc__)
    import runpy, os
    R = runpy.run_path(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dama", "research.py"), run_name="collect")
    questions = {q: opts for _, q, opts in R["SURVEY_Q"]}
    out = collect(json.load(open(a[1])), json.load(open(a[2])), json.load(open(a[3])), questions)
    json.dump(out, open(a[4], "w"), indent=1, ensure_ascii=False)
    print(f"{len(out['items'])} ideas; survey responses: {out['survey']['responses']}; research sign-ups: {out['research']['signups']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
