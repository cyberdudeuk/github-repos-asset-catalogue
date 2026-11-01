"""Service design pack for the GitHub Repos Asset Catalogue (7.3): personas, user stories, journeys,
service blueprints, processes and workflows. One source, used by the page (service_design.json) and the
repository docs (Markdown with Mermaid). Personas are proto-personas: assumed from the requests that shaped the
catalogue, not from user research. That is stated on every output. Run with python3 -I.
"""
import json, os

S = os.path.dirname(os.path.abspath(__file__))
STATUS = "Proto-personas and assumed journeys, written from the requests that shaped the catalogue. Not yet tested with users: research is the first thing to do next."

PERSONAS = [
 dict(id="P1", name="Policy lead", role="Policy or strategy colleague in a department", goal="Find out who in government already works on my policy area, before commissioning anything.", needs=["Plain words, no GitHub knowledge", "Browse by topic and life event", "Who to talk to"], pains=["Code projects mean nothing to me", "I can't tell what's live from what's abandoned"], entry="Home, then Explore repos or a topic", views=["home", "discover", "topics", "journeys", "profile"], ic="topics", c="violet"),
 dict(id="P2", name="Data leader", role="Chief Data Officer or data governance lead", goal="See my organisation's data estate in code: data quality, catalogues, pipelines, legacy and debt.", needs=["DAMA view of capabilities", "Legacy and debt signals", "Compare with peers"], pains=["Evidence of data practice is scattered", "Legacy risk is invisible until it bites"], entry="Insights and analytics", views=["insights", "dama", "suppliers", "legacy", "orgs", "family"], ic="wheel", c="green"),
 dict(id="P3", name="Service owner", role="Product or service owner building a public service", goal="Reuse what exists before building: components, APIs, journeys and patterns.", needs=["Search everything", "APIs and open data", "Who maintains it and can I reuse it"], pains=["Duplicated builds across departments", "Licences and ownership are unclear"], entry="Search everything", views=["search", "catalogue", "apis", "opendata", "profile", "guidance"], ic="k_app", c="blue"),
 dict(id="P4", name="Engineering and security lead", role="Head of engineering, architect or security lead", goal="Check how well our code is looked after and where the risks are.", needs=["Good practice across disciplines", "Retired technology", "GitHub hygiene"], pains=["Unowned repositories", "Retired libraries still in use"], entry="Good practice", views=["practice", "practice2", "legacy", "gdsway", "gdsx"], ic="practice", c="green"),
 dict(id="P5", name="Repository owner moving from co-cddo", role="Owner of a co-cddo repository", goal="Move my repository to its new home without breaking anything.", needs=["What moves where", "What breaks when it moves", "A decision record"], pains=["Hidden dependencies", "Links and Pages that silently break"], entry="co-cddo move", views=["start", "overview", "repos", "lineage", "safe"], ic="move", c="magenta"),
 dict(id="P6", name="Cross-government architect", role="Architect working across GDS and the govukOS apps", goal="Join this catalogue to GTI, ANA, LIAH and the shared registers on one key.", needs=["Organisation crosswalk", "Feeds in open formats", "Lineage and traceability"], pains=["Three organisation id schemes", "No register entry"], entry="govukOS connections", views=["govukos", "knowledge", "family", "nations", "international"], ic="i_link", c="slate"),
]
STORIES = [
 ("S01", "P1", "find work on my policy area in plain words", "I can join up with teams already working on it", "Explore repos", ["Topic tiles and everyday-word search return matching projects", "Each card says what it is and whether it's being worked on, without jargon"], ["T-RX-01"]),
 ("S02", "P1", "see a project's story on one page", "I understand it without reading code", "Repo profile", ["Three reading levels", "Who it belongs to, up to the department"], ["T-RX-02"]),
 ("S03", "P1", "see which projects support life events and whole-of-government journeys", "I can see where my policy meets real services", "Public service journeys", ["Life events and whole-of-government work listed with evidence"], ["T-TH-01"]),
 ("S04", "P2", "see my organisation's data management capabilities on the DAMA wheel", "I know our strengths and gaps", "Data management wheel", ["Select an area, then a capability, to reach the repositories and evidence"], ["T-DAMA-01"]),
 ("S05", "P2", "find legacy technology and data in my estate", "I can plan remediation", "Legacy and technical debt", ["Signals with evidence, filterable by organisation and sector"], ["T-LEG-01"]),
 ("S06", "P2", "see the tools and suppliers behind data work", "I can judge supplier concentration", "Data tools and suppliers", ["The table follows the chosen knowledge area"], ["T-SUP-02"]),
 ("S07", "P2", "see my department's whole family of organisations", "I see the estate as one", "Department family tree", ["Every branch total equals its parts", "Keyboard-navigable tree"], ["T-FAM-01"]),
 ("S08", "P3", "search the whole catalogue in one place", "I find anything without knowing where it lives", "Search everything", ["Grouped results, exact names first, open where they belong"], ["T-SRCH-01"]),
 ("S09", "P3", "find APIs and see whether they're in the government API catalogue", "I can reuse rather than rebuild", "API catalogue", ["Reconciliation in both directions"], ["T-API-01"]),
 ("S10", "P3", "know whether I can reuse a project", "I avoid licence problems", "Repo profile", ["Licence in plain words, marked 'not legal advice'"], ["T-RX-02"]),
 ("S11", "P3", "find guidance, playbooks and standards held in code", "I follow what already exists", "Guidance, policy and playbooks", ["Playbooks, manuals, policy and standards with evidence"], ["T-TH-01"]),
 ("S12", "P4", "compare good practice across disciplines", "I can target improvement", "Good practice across disciplines", ["Eight disciplines, by sector and type"], ["T-PRAC-01"]),
 ("S13", "P4", "find retired GOV.UK libraries and end-of-life tools", "I can remove them", "Legacy and technical debt", ["Dependency-based signals marked 'in the code'"], ["T-LEG-01"]),
 ("S14", "P5", "see where each co-cddo repository is going and what could break", "I move safely", "co-cddo move", ["Destinations, impacts and decisions recorded"], ["T-DEC-01", "T-IMP-01"]),
 ("S15", "P5", "see what depends on my repository", "I don't break other teams", "Dependencies", ["Family tree, line map and list"], ["T-VIEW-01"]),
 ("S16", "P6", "join GTI and ANA organisation ids to GOV.UK slugs", "the apps can share data", "govukOS connections", ["Every id matched exactly or with a stated reason"], ["T-OS-01"]),
 ("S17", "P6", "trace any requirement to the checks that prove it", "I can trust the catalogue", "Knowledge layer", ["Selecting a requirement lights its checks and sources"], ["T-KN-01"]),
 ("S18", "P6", "download vocabularies, ontology and feeds in open formats", "other portals can harvest them", "Knowledge layer", ["SKOS, OWL, JSON-LD, CSV"], ["T-KN-01", "T-OS-01"]),
 ("S19", "P1", "use the catalogue with a screen reader, keyboard or on a phone", "I'm not excluded", "Every page", ["WCAG 2.2 AA, no sideways scrolling at 320 pixels"], ["T-AXE-01", "T-WID-01", "T-CON-02"]),
 ("S20", "P6", "see work about the UK's nations and international partners", "I can find devolved and partner work", "Devolution and the UK's nations", ["Devolved publishers and alliance flags"], ["T-TH-01"]),
]
JOURNEYS = [
 dict(id="J1", persona="P1", title="From a policy question to the right team", steps=[("Arrive", "Opens the catalogue from a link", "home", "Curious, unsure"), ("Orient", "Picks 'What are you interested in?' or searches in everyday words", "discover", "Relieved: no jargon"), ("Narrow", "Filters to 'being worked on' and their sector", "discover", "Focused"), ("Understand", "Opens a profile at Simple reading level", "profile", "Confident"), ("Connect", "Follows 'who it belongs to' and raises an issue with the catalogue's maintainers", "family", "Ready to act")], pain="Most repositories have no description; summaries are written automatically and marked."),
 dict(id="J2", persona="P2", title="From estate question to remediation plan", steps=[("Arrive", "Opens Insights and analytics", "insights", "Wants the big picture"), ("Assess", "Selects their knowledge areas on the DAMA wheel", "dama", "Sees gaps"), ("Find debt", "Opens Legacy and technical debt for their organisation", "legacy", "Concerned"), ("Compare", "Looks at peers in the family tree and organisation profiles", "family", "Benchmarking"), ("Act", "Downloads the CSV for a remediation plan", "legacy", "In control")], pain="Commercial tools used through their own interfaces leave little trace in public code."),
 dict(id="J3", persona="P3", title="Reuse before build", steps=[("Search", "Searches everything for the capability", "search", "Hopeful"), ("Check APIs", "Looks for an API and its catalogue entry", "apis", "Assessing"), ("Check reuse", "Reads licence, care checklist and activity", "profile", "Cautious"), ("Find guidance", "Finds related playbooks and standards", "guidance", "Reassured"), ("Decide", "Records reuse, or contacts the owner", "profile", "Decided")], pain="'Can I reuse it?' is often 'Not known' because licences aren't detected."),
 dict(id="J4", persona="P5", title="Move a co-cddo repository safely", steps=[("Learn", "Reads the migration in six sentences", "start", "Wary"), ("Locate", "Finds their repository and its proposed home", "repos", "Clear"), ("Check", "Reviews dependencies and what breaks", "lineage", "Careful"), ("Decide", "Records a decision", "repos", "Committed"), ("Move", "Follows GitHub's documented behaviour", "safe", "Done")], pain="Pages and links don't redirect; OIDC subjects change."),
 dict(id="J5", persona="P6", title="Join the catalogue to govukOS", steps=[("Understand", "Reads what each app holds and the shared key", "govukos", "Mapping"), ("Resolve ids", "Uses the organisation crosswalk", "govukos", "Unblocked"), ("Trace", "Follows lineage from source to check", "knowledge", "Trusting"), ("Exchange", "Downloads feeds and vocabularies", "knowledge", "Integrating"), ("Link", "Uses the link scheme from other apps", "govukos", "Joined up")], pain="The other apps don't yet accept an organisation in their links."),
 dict(id="J6", persona="P4", title="Raise the standard of public code", steps=[("Baseline", "Opens Good practice across disciplines", "practice2", "Measuring"), ("Find gaps", "Filters by type and sector", "practice2", "Specific"), ("Check debt", "Finds retired libraries", "legacy", "Prioritising"), ("Check rules", "Checks against the GDS Way", "gdsway", "Assuring"), ("Track", "Re-checks after the next scan", "practice2", "Improving")], pain="A file shows a practice is set up, not how well it's followed."),
]
BLUEPRINTS = [
 dict(id="B1", title="Answering 'who already does this?'", stages=["Ask", "Search", "Understand", "Connect"],
      lanes={"User actions": ["Has a question", "Searches or picks a topic", "Reads a profile", "Raises an issue or contacts the publisher"],
             "Front stage (the page)": ["Home, masthead search", "Grouped results, thesaurus", "Profile: summary, ladder, care, lineage", "Links to GitHub, GOV.UK, the repository's issues"],
             "Back stage (in the page)": ["Search index built in the browser", "Ranking, highlighting", "Signals joined per repository", "Link scheme"],
             "Support processes": ["Nightly listing (X-Gov scraper)", "git checks, README and file reads", "Classifiers with precision samples", "GOV.UK organisations API"],
             "Evidence and checks": ["P-41", "T-SRCH-01", "T-RX-02", "T-OS-01"]}),
 dict(id="B2", title="Publishing a new release of the catalogue", stages=["Gather", "Classify", "Build", "Verify", "Publish"],
      lanes={"Maintainer actions": ["Runs the data scripts", "Reviews precision samples", "Runs the build", "Runs tests and scans", "Publishes the page"],
             "Systems": ["git clones, manifests, GOV.UK API", "Rules with negative tests", "build_v71.py assembles the page", "jsdom harness, axe-core, Playwright", "Artifact and this repository"],
             "Checks": ["C- checks per dataset", "C-TH, C-LEG, C-HIER", "C-DOC-01 refuses untraced work", "T- tests, T-AXE-01, T-WID-01, T-CON-02", "File hash matches the tested file"],
             "Records": ["Source dates in the page", "Precision tables", "Registry of every check", "Defect register", "Release notes"]}),
 dict(id="B3", title="Joining govukOS apps on one organisation key", stages=["Read", "Match", "Resolve", "Share"],
      lanes={"Architect actions": ["Reads each app's ids", "Runs the crosswalk", "Reviews unresolved ids", "Shares feeds"],
             "Front stage": ["govukOS connections page", "Crosswalk table and search", "Reasons for every gap", "Downloads and link scheme"],
             "Back stage": ["GTI and ANA tables copied verbatim", "Exact and abbreviation matches only", "Hand resolutions with reasons", "window.GHRAC_API"],
             "Owners needed": ["App owners", "Organisations register (R3)", "R3 owner confirms 105 ANA bodies", "Studio issues the identifier (R7)"]}),
]
WORKFLOWS = [
 dict(id="W1", title="Refresh the data", steps=["Read the X-Gov repo listing", "Clone changed repositories (blobless) and read READMEs, file trees and manifests", "Run classifiers: DAMA, APIs, open data, GDS, practices, legacy, themes", "Read GOV.UK organisations; rebuild hierarchy and crosswalk", "Sample and judge precision; fix rules with negative tests"], decision="Any check failing?", yes="Fix the rule, add a negative test, rerun", no="Build"),
 dict(id="W2", title="Build and verify", steps=["Assemble the page from parts", "Embed data, fonts and test results", "Run page self-checks on load", "Run the harness (48+ tests)", "Run accessibility, width and contrast tests"], decision="All pass?", yes="Publish", no="Find the root cause, fix, record the defect and its check"),
 dict(id="W3", title="Handle a reported defect", steps=["Reproduce in Chromium", "Find the root cause", "Write a check that fails on the old build", "Fix", "Prove the check passes on the new build", "Record it in the defect register and release notes"], decision="Full suite still green?", yes="Publish a patch release", no="Keep fixing"),
 dict(id="W4", title="Answer a user question with the catalogue", steps=["Search or browse", "Open the profile", "Check status, licence and care", "Follow lineage to the evidence", "Contact the owner"], decision="Reusable?", yes="Reuse and record it", no="Talk to the owner or build"),
 dict(id="W5", title="Add a new classification", steps=["Write the rule with word boundaries", "Write positive and negative tests", "Run it over the catalogue", "Sample 15 and judge", "Publish precision with the view"], decision="Precision acceptable?", yes="Ship, labelled 'judged by Claude, not owner-confirmed'", no="Tighten and resample"),
 dict(id="W6", title="Integrate another govukOS app", steps=["Read its ids and link scheme", "Add its ids to the crosswalk", "Add links out in its format", "Offer feeds keyed by GOV.UK slug", "Write the change for its owner"], decision="Can this session write there?", yes="Make the change with a check", no="Hand over the pack and instructions"),
]
out = dict(status=STATUS, personas=PERSONAS, stories=[dict(id=s[0], persona=s[1], want=s[2], so=s[3], where=s[4], accept=s[5], tests=s[6]) for s in STORIES], journeys=[dict(j, steps=[dict(stage=a, action=b, view=c, feeling=d) for a, b, c, d in j["steps"]]) for j in JOURNEYS], blueprints=BLUEPRINTS, workflows=WORKFLOWS)
checks = []
def need(ok, cid, text, guards="R39"): checks.append(f"{'PASS' if ok else 'FAIL'} {cid} {text} [guards: {guards}]")
P = {p["id"] for p in PERSONAS}
need(all(s[1] in P for s in STORIES) and all(j["persona"] in P for j in JOURNEYS) and all(any(s[1] == p for s in STORIES) for p in P), "C-SD-01", f"{len(PERSONAS)} personas, {len(STORIES)} stories and {len(JOURNEYS)} journeys: every story and journey belongs to a persona, and every persona has stories")
need(all(len(set(len(v) for v in b["lanes"].values()) | {len(b["stages"])}) == 1 for b in BLUEPRINTS), "C-SD-02", f"{len(BLUEPRINTS)} service blueprints: every lane has one entry per stage")
need(all(s[6] for s in STORIES) and all(w["steps"] and w["decision"] for w in WORKFLOWS), "C-SD-03", f"every story names the tests that prove it; {len(WORKFLOWS)} workflows each end in a decision")
json.dump(out, open(os.path.join(S, "service_design.json"), "w"), indent=0)
open(os.path.join(S, "service_design_checks.txt"), "w").write("\n".join(checks) + "\n")
print("\n".join(checks))
