"""Write the repository docs from the same sources the page uses: service design (with Mermaid diagrams),
requirements, defects and releases. Run from the repository root: python3 -I build/dama/write_docs.py"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "build", "inv"))
SD = json.load(open(os.path.join(ROOT, "build", "dama", "service_design.json")))
from docs71 import REQUIREMENTS, DEFECTS, RELEASES, A11Y
D = os.path.join(ROOT, "docs"); SDD = os.path.join(D, "service-design"); os.makedirs(SDD, exist_ok=True)
P = {p["id"]: p for p in SD["personas"]}
note = f"> **Status:** {SD['status']}\n"
def w(path, text): open(path, "w").write(text.rstrip() + "\n")
w(os.path.join(SDD, "personas.md"), "# Personas\n\n" + note + "\n" + "\n".join(f"## {p['id']}: {p['name']}\n\n*{p['role']}*\n\n**Goal:** {p['goal']}\n\n**Needs:** {'; '.join(p['needs'])}\n\n**Pain points:** {'; '.join(p['pains'])}\n\n**Starts at:** {p['entry']}\n\n**Uses:** {', '.join(p['views'])}\n" for p in SD["personas"]))
w(os.path.join(SDD, "user-stories.md"), "# User stories\n\n" + note + "\nEach story names the tests that prove it. The test results are embedded in the built page.\n\n| ID | Story | Where | Acceptance criteria | Proved by |\n|---|---|---|---|---|\n" + "\n".join(f"| {s['id']} | As a {P[s['persona']]['name'].lower()}, I want to {s['want']}, so that {s['so']}. | {s['where']} | {'<br>'.join(s['accept'])} | {', '.join(s['tests'])} |" for s in SD["stories"]))
def jm(j):
    lines = ["```mermaid", "journey", f"  title {j['title']}"]
    score = {0: 2, 1: 3, 2: 3, 3: 4, 4: 5}
    for i, s in enumerate(j["steps"]): lines += [f"  section {s['stage']}", f"    {s['action'].replace(':', ' -')}: {score.get(i, 4)}: {P[j['persona']]['name']}"]
    return "\n".join(lines + ["```"])
w(os.path.join(SDD, "journeys.md"), "# Journeys\n\n" + note + "\nScores are assumed feelings (1 to 5), to be tested with users.\n\n" + "\n\n".join(f"## {j['id']}: {j['title']} ({P[j['persona']]['name']})\n\n{jm(j)}\n\n| Stage | Action | Page | Feeling |\n|---|---|---|---|\n" + "\n".join(f"| {s['stage']} | {s['action']} | {s['view']} | {s['feeling']} |" for s in j["steps"]) + f"\n\n**Known pain point:** {j['pain']}" for j in SD["journeys"]))
w(os.path.join(SDD, "service-blueprints.md"), "# Service blueprints\n\n" + note + "\n" + "\n\n".join(f"## {b['id']}: {b['title']}\n\n| Layer | " + " | ".join(b["stages"]) + " |\n|---|" + "---|" * len(b["stages"]) + "\n" + "\n".join(f"| **{lane}** | " + " | ".join(cells) + " |" for lane, cells in b["lanes"].items()) for b in SD["blueprints"]))
def wf(x):
    ids = [f"S{i}" for i in range(len(x["steps"]))]
    lines = ["```mermaid", "flowchart TD"] + [f'  {ids[i]}["{s.replace(chr(34), "")}"]' for i, s in enumerate(x["steps"])] + [f"  {ids[i]} --> {ids[i+1]}" for i in range(len(ids) - 1)]
    lines += [f'  {ids[-1]} --> D{{"{x["decision"]}"}}', f'  D -- Yes --> Y["{x["yes"]}"]', f'  D -- No --> N["{x["no"]}"]', "```"]
    return "\n".join(lines)
w(os.path.join(SDD, "processes-and-workflows.md"), "# Processes and workflows\n\n" + "\n\n".join(f"## {x['id']}: {x['title']}\n\n{wf(x)}" for x in SD["workflows"]))
w(os.path.join(SDD, "README.md"), "# Service design\n\n" + note + "\n- [Personas](personas.md)\n- [User stories](user-stories.md)\n- [Journeys](journeys.md)\n- [Service blueprints](service-blueprints.md)\n- [Processes and workflows](processes-and-workflows.md)\n\nThe same content is in the page, under About, Service design.")
w(os.path.join(D, "requirements.md"), "# Requirements\n\n| ID | Requirement | Source | Pages | Checks |\n|---|---|---|---|---|\n" + "\n".join(f"| {q[0]} | {q[1]} | {q[2]} | {', '.join(q[3])} | {', '.join(q[4])} |" for q in REQUIREMENTS))
w(os.path.join(D, "defects.md"), "# Defect register\n\nEvery defect has a check that fails on the build that had it and passes on the fix.\n\n| ID | Found | Severity | What went wrong | Cause | Fix | Checks | Status |\n|---|---|---|---|---|---|---|---|\n" + "\n".join("| " + " | ".join(str(c).replace("|", "/") if not isinstance(c, list) else ", ".join(c) for c in d) + " |" for d in DEFECTS))
w(os.path.join(D, "releases.md"), "# Releases\n\n" + "\n".join(f"- **{r[0]}** ({r[1]}): {r[2]}" for r in sorted(RELEASES, key=lambda r: [int(x) for x in r[0].split('.')], reverse=True)))
def md(blocks): return "\n".join(f"## {b[1]}\n" if b[0] == "h" else f"{b[1]}\n" if b[0] == "p" else "\n".join(f"- {i}" for i in b[1]) + "\n" for b in blocks)
w(os.path.join(D, "accessibility-statement.md"), "# Accessibility statement\n\nGenerated from `build/inv/docs71.py`, the same source as the page's statement (About, Accessibility).\n\n" + md(A11Y).replace("Use the contact form", "Use the [contact form](https://github.com/cyberdudeuk/github-repos-asset-catalogue/issues/new?template=contact.yml)"))
print("docs written")
