"""Guided tours and tutorials (R42).
Persona tours follow the six service design journeys step by step (from service_design.json), so every tour is
designed around a persona and their journey. Tutorials are short, task-based walkthroughs of key content, features and
functionality, each pinned to a user guide level. Writes tours.json for the page and docs/user-guide/tours.md.
Checks: C-TOUR-01 every persona has a tour and every tour step follows its journey; C-TOUR-02 every tutorial has a level,
a goal and 3 to 7 steps, each naming a view and an element on it; C-TOUR-02n negative tests. Run with python3 -I."""
import json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(H))
SD = json.load(open(os.path.join(H, "service_design.json")))
EXAMPLE_REPO = "alphagov/govuk-frontend"   # a well-known public project used wherever a step needs one open

def persona_tours(sd):
    P = {p["id"]: p for p in sd["personas"]}; out = []
    for j in sd["journeys"]:
        p = P[j["persona"]]
        out.append(dict(id="tour-" + j["id"].lower(), kind="persona", persona=p["id"], persona_name=p["name"], journey=j["id"], title=j["title"],
                        intro=f"A tour for a {p['name'].lower()}: {j['title'][0].lower() + j['title'][1:]}. Each stop opens the part of the catalogue that step needs.",
                        steps=[dict(view=s["view"], route=("repo=" + EXAMPLE_REPO) if s["view"] == "profile" else "", sel="", title=s["stage"], text=s["action"] + ".") for s in j["steps"]]))
    return out

T = lambda v, sel, title, text, route="": dict(view=v, sel=sel, title=title, text=text, route=route)
TUTORIALS = [
 dict(id="tut-search", level="beginner", title="Find code about a topic in everyday words", goal="Find projects about something you care about without knowing GitHub's words.", steps=[
   T("search", "#gs-q2", "Type what you're looking for", "Use everyday words, such as 'benefits', 'school data' or 'maps'. The thesaurus also finds the technical words for them."),
   T("search", "#gs-kinds", "Narrow it down", "Choose what kind of thing you want back: projects, organisations, topics, APIs, words and more."),
   T("search", "#gs-res", "Read the results", "Results are grouped by kind, best match first. Select one to open it."),
   T("search", "#dh-search-1", "How search works", "This explains how results are ranked, so you know why something came first.")]),
 dict(id="tut-profile", level="beginner", title="Read a project's profile", goal="Understand what a project does, who it belongs to and whether it's looked after.", steps=[
   T("profile", "#rx-title", "The project at the top", "Its name in plain English, with the GitHub name underneath. Listen to it with the read-aloud button if that helps.", "repo=" + EXAMPLE_REPO),
   T("profile", "#dh-profile-1", "At a glance", "Whether it's live, how recently someone changed it and who publishes it."),
   T("profile", "#dh-profile-3", "Who it belongs to", "The chain from the GitHub account up to the government department."),
   T("profile", "#dh-profile-7", "How well it's looked after", "A simple checklist: description, licence, recent changes, security and tests."),
   T("profile", "#dh-profile-11", "Words explained", "Any technical word on this page, explained in a sentence.")]),
 dict(id="tut-family", level="beginner", title="Find who a project belongs to", goal="Go from a department to the organisations and GitHub accounts where its code lives.", steps=[
   T("family", "#fam-find", "Find an organisation", "Type a department or public body. Matches come from GOV.UK's list of organisations."),
   T("family", "#fam-tree", "The family tree", "Each department with the organisations under it. Open a branch to see more."),
   T("family", "#fam-sel", "The selected organisation", "Its GitHub accounts, its projects and how much of its code is still being worked on.")]),
 dict(id="tut-discover", level="intermediate", title="Explore projects with filters", goal="Use filters, sorting and grouping to find work you could reuse.", steps=[
   T("discover", "#dh-discover-1", "Start with an interest", "Pick a topic tile to start, or skip to searching."),
   T("discover", "#rx-q", "Search in everyday words", "Type words; the line under the box shows which related words were also searched."),
   T("discover", "#rx-sector", "Filter by sector", "Keep only health, education, justice or another sector. Other filters show live projects, reusable ones or those with legacy signals."),
   T("discover", "#rx-sort", "Sort and group", "Sort by recent work, name or size, and group by sector, kind or organisation."),
   T("discover", "#rx-res", "The projects", "Each card says what the project is in plain English. Open one for its full profile.")]),
 dict(id="tut-insights", level="intermediate", title="See patterns across the estate", goal="Use the dashboard to answer estate-wide questions, then check the numbers behind each chart.", steps=[
   T("insights", "#i-sector", "Filter the whole dashboard", "Choose a sector, kind of body, topic or data management area; every chart follows."),
   T("insights", "#dh-insights-1", "Growth over time", "New code projects each year, coloured by whether they are still worked on today."),
   T("insights", "#dh-insights-8", "Who publishes most", "The organisations with most public code. Select a bar to open that organisation."),
   T("insights", "#dh-insights-13", "Legacy at a glance", "Where legacy technology and technical debt show up. Every chart has 'Show the numbers' for a table.")]),
 dict(id="tut-practice", level="intermediate", title="Check good practice against the GDS Way", goal="Judge how well code is looked after and where it falls short of the GDS Way.", steps=[
   T("practice", "#dh-practice-0", "Practice across government", "Signals such as licences, security policies, tests and automated checks, by organisation."),
   T("gdsway", "#dh-gdsway-0", "GDS Way checks", "Each co-cddo repository checked against the GDS Way, with the evidence for each result."),
   T("safe", "#dh-safe-0", "Moving safely", "GitHub's recommended order for changes that can break things.")]),
 dict(id="tut-legacy", level="advanced", title="Find legacy technology and technical debt", goal="Locate legacy signals by organisation and sector, and export the evidence.", steps=[
   T("legacy", "#dh-legacy-1", "The signals", "Each signal, such as retired libraries or code nobody has changed for years, with how many projects show it."),
   T("legacy", "#lg-sector", "Filter", "Narrow by sector, organisation, live projects or the core signals only."),
   T("legacy", "#lg-list", "The projects", "Every project with its signals and the evidence for each."),
   T("legacy", "#lg-csv", "Export", "Download the filtered list as CSV for your own analysis."),
   T("legacy", "#dh-legacy-6", "How accurate it is", "How the signals are found and how precise they were on a checked sample.")]),
 dict(id="tut-knowledge", level="advanced", title="Reuse the knowledge graph and vocabularies", goal="Find any item's connections and download the vocabularies in open formats.", steps=[
   T("knowledge", "#kt-graph", "The knowledge layer", "A graph, lineage, vocabularies, an ontology, a data dictionary and a thesaurus, as tabs."),
   T("knowledge", "#kg-q", "Find an item", "Search the graph for a project, organisation, topic or requirement and see what it connects to."),
   T("knowledge", "#kg-json", "Download", "Every part downloads in open formats: JSON-LD, SKOS, OWL, PROV and CSV.")]),
 dict(id="tut-govukos", level="advanced", title="Join the catalogue to other apps", goal="Use the organisation feeds and crosswalk to join this catalogue with other apps.", steps=[
   T("govukos", "#dh-govukos-0", "How the apps join", "Every app can join on one key: the GOV.UK organisation slug."),
   T("govukos", "#os-orgjson", "The feeds", "Download organisation and repository feeds as JSON, CSV or DCAT."),
   T("govukos", "#xw-app", "The crosswalk", "Other apps' organisation ids matched to GOV.UK slugs, with the reason for every gap.")]),
 dict(id="tut-dmbok", level="intermediate", title="Go from a data management activity to the tools that deliver it", goal="Find what an activity involves, the UK guidance for it, and the tools and code that deliver it.", steps=[
   T("dmbok", "#ak-areas", "Choose a knowledge area", "The eleven areas of the DAMA wheel come first, then five DMBOK2 topics beyond it. Each card shows how many activities and tools it has."),
   T("dmbok", "#ak-list-h", "Find the activity", "Filter by phase, lifecycle stage or whether tools deliver it, or search in your own words, such as 'lineage' or 'retention'."),
   T("dmbok", "#ak-detail-h", "Read the activity", "What it is, its deliverables, who does it, how it is measured, the UK guidance that applies, and the tools and code that deliver it.", "act=DQ-04"),
   T("dmbok", "#ak-life", "See it across the data lifecycle", "How many activities act at each stage, from planning to disposal. Select a number to list them.")]),
 dict(id="tut-tooling", level="intermediate", title="Find out who uses a tool, for what, where and when", goal="See the evidence that a tool is used in the public sector, and by whom.", steps=[
   T("tooling", "#tk-list-h", "Find the tool", "Filter by knowledge area, activity, lifecycle stage, type, evidence or the buyer's sector, then sort by the evidence you care about."),
   T("tooling", "#tk-prof-h", "Read who uses it", "Case studies from the supplier's own site, tender and contract notices with buyer, date, value and supplier, public code, and G-Cloud listings.", "tool=snowflake"),
   T("tooling", "#tk-heat", "See who buys what", "Notices by knowledge area and the buyer's sector. Select a number to filter the tools."),
   T("tooling", "#tk-buyers", "Find the buyers", "The public bodies with the most notices for these tools, and which tools they named.")])
]

# A drawer id such as #dh-legacy-6 is the sixth heading on that view: it moves whenever a section is added above it
# (V716-1: a "Related elsewhere" panel added to the legacy view moved "The signals" step onto the wrong heading and
# left "How accurate it is" pointing at nothing). So every step aimed at a drawer id names the heading it expects, and
# the page harness (T-TOUR-01) checks the element it finds starts with that text.
HEADS = {"#dh-search-1": "How search works", "#dh-profile-1": "At a glance", "#dh-profile-3": "Who it belongs to",
         "#dh-profile-7": "How well it's looked after", "#dh-profile-11": "Words explained", "#dh-discover-1": "1. What are you interested in?",
         "#dh-insights-1": "New code projects each year", "#dh-insights-8": "Who publishes most", "#dh-insights-13": "Legacy and technical debt at a glance",
         "#dh-practice-0": "Engineering practice across government", "#dh-gdsway-0": "GDS Way conformance", "#dh-safe-0": "GitHub's recommended approach",
         "#dh-legacy-1": "Signals", "#dh-legacy-6": "How the signals are found", "#dh-govukos-0": "How this catalogue links to"}
for _t in TUTORIALS:
    for _s in _t["steps"]:
        if _s["sel"] in HEADS: _s["head"] = HEADS[_s["sel"]]

def check_heads(tuts):
    """Every step aimed at a drawer heading id names the heading text it expects."""
    return [f'{t["id"]} {s["sel"]}' for t in tuts for s in t["steps"] if s["sel"].startswith("#dh-") and not s.get("head")]

FAILS, LINES = [], []
def need(ok, cid, msg):
    LINES.append(("PASS " if ok else "FAIL ") + cid + " " + msg); print(LINES[-1])
    if not ok: FAILS.append(cid)

def check_persona(tours, sd):
    J = {j["id"]: j for j in sd["journeys"]}
    covered = {t["persona"] for t in tours} == {p["id"] for p in sd["personas"]}
    follow = all([s["view"] for s in t["steps"]] == [s["view"] for s in J[t["journey"]]["steps"]] for t in tours)
    return covered and follow

def check_tutorials(tuts):
    bad = [t["id"] for t in tuts if t["level"] not in ("beginner", "intermediate", "advanced") or not t["goal"] or not 3 <= len(t["steps"]) <= 7
           or any(not s["view"] or not re.fullmatch(r"#[a-z][a-z0-9-]*", s["sel"]) or not s["text"] for s in t["steps"])]
    levels = {t["level"] for t in tuts} == {"beginner", "intermediate", "advanced"}
    return levels and not bad, bad

def md(tours, tuts):
    s = ["# Guided tours and tutorials", "", "Tours follow a persona's journey through the catalogue. Tutorials walk through one task. Start either from the catalogue's user guide, under Start here.", "", "## Tours by persona", ""]
    for t in tours:
        s += [f"### {t['persona_name']}: {t['title']}", ""] + [f"{n}. **{x['title']}** ({x['view']} view): {x['text']}" for n, x in enumerate(t["steps"], 1)] + [""]
    s += ["## Tutorials", ""]
    for lv, name in (("beginner", "New to GitHub"), ("intermediate", "Intermediate"), ("advanced", "Advanced")):
        s += [f"### {name}", ""]
        for t in [x for x in tuts if x["level"] == lv]:
            s += [f"**{t['title']}.** {t['goal']}", ""] + [f"{n}. **{x['title']}** ({x['view']} view): {x['text']}" for n, x in enumerate(t["steps"], 1)] + [""]
    s += ["Generated by `build/dama/tours.py` from the service design journeys; edit that file, not this one.", ""]
    return "\n".join(s)

if __name__ == "__main__":
    tours = persona_tours(SD)
    need(check_persona(tours, SD), "C-TOUR-01", f"{len(tours)} persona tours: every persona has one and every tour follows its journey's views in order [guards: R42]")
    ok, bad = check_tutorials(TUTORIALS)
    need(ok, "C-TOUR-02", f"{len(TUTORIALS)} tutorials across the three guide levels, each with a goal and 3 to 7 steps naming a view and an element on it (bad {bad}) [guards: R42]")
    # negative tests: a persona without a tour, a tour out of step with its journey, and a tutorial step with no element are all rejected
    broken = [dict(tours[0], steps=tours[0]["steps"][::-1])] + tours[1:]
    n1 = check_persona(tours[1:], SD); n2 = check_persona(broken, SD) if tours[0]["steps"][0]["view"] != tours[0]["steps"][-1]["view"] else False
    n3, _ = check_tutorials([dict(TUTORIALS[0], steps=[dict(TUTORIALS[0]["steps"][0], sel="")] + TUTORIALS[0]["steps"][1:])] + TUTORIALS[1:])
    hb = check_heads(TUTORIALS)
    need(not hb, "C-TOUR-03", f"every tutorial step aimed at a drawer heading ({sum(1 for t in TUTORIALS for x in t['steps'] if x['sel'].startswith('#dh-'))} steps) names the heading it expects, so a heading that moves is caught by the page harness, not followed to the wrong place (missing {hb}) [guards: V716-1]")
    n4 = check_heads([dict(TUTORIALS[0], steps=[dict(x, sel="#dh-x-1", head="") for x in TUTORIALS[0]["steps"]])])
    need(bool(n4), "C-TOUR-03n", "negative test: a step aimed at a drawer heading without the heading it expects is rejected [guards: V716-1]")
    need(not n1 and not n2 and not n3, "C-TOUR-02n", "negative tests: a missing persona tour, a tour out of step with its journey and a tutorial step with no element are each rejected [guards: R42]")
    json.dump(dict(example_repo=EXAMPLE_REPO, tours=tours, tutorials=TUTORIALS), open(os.path.join(H, "tours.json"), "w"), ensure_ascii=False, indent=1)
    D = os.path.join(ROOT, "docs", "user-guide"); os.makedirs(D, exist_ok=True)
    open(os.path.join(D, "tours.md"), "w").write(md(tours, TUTORIALS))
    open(os.path.join(H, "tours_checks.txt"), "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)
