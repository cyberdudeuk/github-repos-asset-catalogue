"""Roadmap and open items, and how the catalogue connects to GitHub (R71).

One source for every open, pending or planned item the catalogue describes, who must act on it, the views it touches and the
GitHub feature or workflow that carries it; and for every portal feature, the GitHub feature or workflow it is joined to.
Writes roadmap.json (read by the page), docs/roadmap.md and roadmap_checks.txt. Run with python3 -I roadmap.py.
Nothing here opens an issue, changes a setting or runs a workflow: each route is a link a person follows."""
import json, os, re, sys, urllib.parse as up
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
REPO = os.environ.get("GHRAC_URL", "https://github.com/cyberdudeuk/github-repos-asset-catalogue").rstrip("/")
PAGES = "https://cyberdudeuk.github.io/github-repos-asset-catalogue/"
INTERNAL = REPO + "-internal"   # the private companion repository (ADR 0004); its links open only for people with access

def form(template, **fields):
    """A link that opens one of this repository's issue forms with fields filled in. GitHub fills a form field from the query parameter named after its id."""
    return REPO + "/issues/new?" + up.urlencode(dict(template=template, **fields))
def track(item, title):
    return form("roadmap-item.yml", title=f"[{item}] {title}", item=item)

STATUS = {"done": "Done", "ready": "Ready: the route is in place, waiting for people to use it",
          "owner": "Needs the owner", "research": "Needs user research", "data": "Needs data work", "external": "Waits on another service",
          "decided": "Decided"}
WHO = {"owner": "Repository owner", "team": "Owning team (blocker B1)", "researcher": "User researcher", "a11y": "Accessibility specialist",
       "orgs": "Public bodies' own teams", "data": "Data engineer", "liah": "LIAH team", "maint": "Maintainers"}
# (id, title, status, who, area, views, what is true today, route kind, route url, route label)
ITEMS = [
 ("RM-01", "Test the catalogue with 5 to 8 people from at least four audiences who don't use GitHub", "ready", "researcher", "Research", ["home", "service", "shape"],
  "Personas and journeys are proto-personas, not yet tested with users. From 7.16.0 the research bundle is ready: a plan with tactical and strategic questions, an invitation to send by email, participant information, consent, a screener, session guides and a sign-up form. It needs facilitators and participants.", "link", PAGES + "#shape", "Help shape the catalogue"),
 ("RM-02", "Measure the precision of each topic on a labelled sample, as was done for strategy and DAM tags", "done", "maint", "Data quality", ["topics", "profile"],
  "Done in 7.18.0: every topic shows how often it is right, from 212 judgements by an AI reviewer (Claude) on seeded samples, with a 95% range; all 15 topics are at least 82% right. People's own checks through 'Check a label' on each project page still add to the sample.", "form", "label-check.yml", "Check a label"),
 ("RM-03", "Ask organisations to check their profile and say whether the next steps are useful", "ready", "orgs", "Organisations", ["orgs"],
  "Every organisation profile now has 'Check this profile', an issue form that names the organisation.", "form", "confirm-profile.yml", "Check a profile"),
 ("RM-04", "Check the catalogue manually with screen readers, magnifiers at 400% zoom and speech input", "owner", "a11y", "Accessibility", ["a11y"],
  "Automated checks pass (axe-core on every view, contrast in light and dark, widths from 320 pixels, keyboard tests). Manual testing hasn't been done.", "form", None, "Track the manual check"),
 ("RM-05", "Publish an accessibility statement with known issues and a way to ask for help", "done", "maint", "Accessibility", ["a11y"],
  "The statement under About, Accessibility, now gives the tests and their dates, the known issues and an assisted route through the contact form; it is also docs/accessibility-statement.md.", "link", REPO + "/blob/main/docs/accessibility-statement.md", "Read the statement"),
 ("RM-06", "Learn which hubs and questions people use, with their consent", "decided", "owner", "Research", ["design"],
  "The page has no analytics and its security policy blocks them, so nothing is tracked. The owner can see visits to the repository in GitHub's traffic insights; GitHub Pages offers no analytics.", "settings", REPO + "/graphs/traffic", "Repository traffic (owner only)"),
 ("RM-07", "Join projects to the datasets they publish or use in data catalogues (data.gov.uk, statistics.gov.scot, Data Map Wales, NHS catalogues)", "data", "data", "Data infrastructure", ["infra", "opendata"],
  "data.gov.uk is done in 7.18.0: 70 datasets whose own record names a repository are joined to 63 projects, shown under Open data pipelines and on each project's page. It also lists datasets that link to code no longer public, and public bodies on GitHub not yet in the catalogue. Scotland's, Wales's and the NHS catalogues are still to join.", "link", REPO + "/blob/main/build/catalogues/datagovuk.py", "How the join is made"),
 ("RM-08", "Add boundaries and locations so nations, authorities and councils can be shown on maps", "done", "data", "Data infrastructure", ["infra", "strategic", "nations"],
  "Done in 7.18.0: ONS boundaries for the four nations and the 218 counties and unitary authorities are held, simplified, in build/geo. Local public services shows councils on the map and Nations shows publishers by nation, each with a table carrying the same numbers.", "link", REPO + "/blob/main/build/geo/geo.py", "How the maps are made"),
 ("RM-09", "Collect GitHub feature settings (Issues, Projects, Wiki, Discussions) for every project, not a sample", "owner", "maint", "Insights", ["ghcheck", "insights"],
  "Feature settings are an estimate from a random sample. The collector is a manual workflow in this repository; a person runs it with a token that can read the accounts.", "workflow", REPO + "/actions/workflows/collect-features.yml", "Run the collector"),
 ("RM-10", "Re-read GitHub so projects found since the catalogue was built are added", "done", "maint", "Insights", ["ghcheck"],
  "Done in 7.17.0: build/refresh/run.sh re-reads the sources, checks with git every repository a source drops, and re-measures activity. A person sets the date and reviews and commits the result.", "issues", REPO + "/blob/main/build/refresh/run.sh", "The refresh, step by step"),
 ("RM-11", "Link repositories to the systems they belong to", "external", "liah", "govukOS", ["govukos"],
  "None of GTI, ANA or LIAH names systems or repositories yet, so these links wait for LIAH to hold real system records.", "form", None, "Track the link"),
 ("RM-12", "A named team accepts ownership: answers issues, reviews pull requests and reviews the catalogue every quarter", "owner", "owner", "Ownership", ["about"],
  "Blocker B1 in the release readiness assessment. The GDS Way asks for review by someone other than the author.", "link", REPO + "/blob/main/docs/security/release-readiness.md", "Release readiness"),
 ("RM-13", "Move the repository to its agreed home organisation", "owner", "owner", "Ownership", ["about"],
  "Blocker B2: gds-dtx is recommended, after its owners agree (ADR 0003).", "link", REPO + "/blob/main/docs/adr", "Decision records"),
 ("RM-14", "Switch on the repository's security settings: private vulnerability reporting, secret scanning with push protection, a ruleset for main, Actions limits and approval for outside contributors", "owner", "owner", "Security", ["about"],
  "Items 3 to 8 in the settings review. Until private vulnerability reporting is on, the Cabinet Office programme is the only private route for security reports.", "settings", REPO + "/settings/security_analysis", "Security settings (owner only)"),
 ("RM-15", "Show the catalogue's address in the repository's About box", "done", "owner", "Ownership", ["home"],
  "Done: the repository's website is " + PAGES + " (read from GitHub on 4 November 2026).", "settings", REPO, "Repository page"),
 ("RM-16", "Create the Discussions category 'Feature assessment' so new GitHub features can be assessed", "owner", "owner", "Taking part", ["about"],
  "The form is ready in .github/DISCUSSION_TEMPLATE/feature-assessment.yml; it appears once the category exists with the slug feature-assessment.", "settings", REPO + "/discussions/categories", "Discussion categories (owner only)"),
 ("RM-17", "Replace the public contact form with the team's private contact form", "owner", "owner", "Contact", ["home", "profile"],
  "Messages in the GitHub contact form are public. Once the team has a private form (for example on GOV.UK Forms), set GHRAC_CONTACT_URL when building.", "link", REPO + "#deployment-settings", "Deployment settings"),
 ("RM-18", "Tag releases and publish release notes from one place", "owner", "owner", "Releases", ["defects"],
  "Blocker B10. Releases and their notes are in docs/releases.md, and the notes for 7.16.0 are ready to paste in docs/release-notes/7.16.0.md. Publishing a release is for a person: an attempt from automation on 11 November was refused.", "settings", REPO + "/releases/new", "Draft a release (owner only)"),
 ("RM-19", "Ask GitHub Support to remove cached views of commits from before the history rewrites", "owner", "owner", "Security", ["about"],
  "The history was rewritten twice on 3 November 2026. Old commits can still be reached by their IDs through pull request references until GitHub Support removes them.", "link", "https://support.github.com/", "GitHub Support"),
 ("RM-20", "Delete the stale branches gds-way-assessment, test-results-7.11.1, readme-assessment and roadmap-github", "owner", "owner", "Housekeeping", ["about"],
  "The first two hold code from before the public and internal split and fail the build; the other two were merged and are no longer needed. Deleting a branch is for a person to do.", "settings", REPO + "/branches", "Branches (owner only)"),
 ("RM-21", "Serve a security.txt that points to the Cabinet Office vulnerability disclosure programme", "external", "owner", "Security", ["about"],
  "The GDS Way asks for /.well-known/security.txt. A GitHub Pages project site can't serve files at the domain's root, so this needs a custom domain or a different host.", "form", None, "Track the decision"),
 ("RM-22", "Data protection screening note, independent security review and a machinery-of-government content check before a wider release", "owner", "team", "Assurance", ["about"],
  "Blockers B5, B6 and B11 in the release readiness assessment.", "link", REPO + "/blob/main/docs/security/release-readiness.md", "Release readiness"),
 ("RM-23", "Create the labels the issue and discussion forms apply: contact, profile check, label check and roadmap", "done", "owner", "Taking part", ["about"],
  "Done on 11 November 2026: the seven labels the forms apply (contact, profile check, label check, roadmap, idea, research and survey-response) were created and read back from GitHub.", "settings", REPO + "/labels", "Labels"),
 ("RM-24", "Require a person to approve each GitHub Pages deployment", "owner", "owner", "Security", ["about"],
  "The pages workflow publishes after its checks pass. A required reviewer on the github-pages environment makes GitHub itself wait for a person, as the catalogue's rules say. Do the same for the companion repository's government edition.", "settings", REPO + "/settings/environments", "Environments (owner only)"),
 ("RM-25", "Create a Q&A category in Discussions, with the slug q-a", "owner", "owner", "Taking part", ["ask"],
  "Ask sends questions it can't answer to Discussions. The form is ready in .github/DISCUSSION_TEMPLATE/q-a.yml; it appears once the category exists. Answers can then be marked so the next person finds them.", "settings", REPO + "/discussions/categories", "Discussion categories (owner only)"),
 ("RM-26", "Run the roadmap as a GitHub project board, with each item an issue", "owner", "owner", "Ownership", ["roadmap"],
  "The roadmap-item form already opens issues. A board gives each a status, an owner and a date on GitHub, and sub-issues can link work to its item. Projects is switched on but unused.", "settings", REPO + "/projects", "Projects (owner only)"),
 ("RM-27", "Signpost the two sister portals from the views where they help, keeping each distinct", "done", "maint", "Taking part", ["dama", "suppliers", "standards", "legacy"],
  "Done in 7.16.0: 'Related elsewhere' on the data management wheel, data tools, catalogues and standards, and legacy views, each naming the portal and its status. The catalogue now uses the sister portals' keys: #dama=DM-GOV and #standard=dcat3 open the same area or standard here, and data/xref.json publishes its keys in the shape they use. A weekly check reads their manifests and the pages linked here.", "link", PAGES + "data/xref.json", "This catalogue's shared keys"),
]
for i, it in enumerate(ITEMS):   # items with no fixed route are tracked with the roadmap-item form
    if it[7] == "form" and it[8] is None: ITEMS[i] = it[:8] + (track(it[0], it[1]),) + it[9:]
    elif it[7] == "form" and it[8].endswith(".yml"): ITEMS[i] = it[:8] + (form(it[8]),) + it[9:]

# (portal feature, where it is in the catalogue, GitHub feature or workflow, link)
CONNECT = [
 ("Contact", "Footer, every project page", "Issue form: contact", REPO + "/issues/new?template=contact.yml"),
 ("Suggest a correction to the catalogue", "Every project page and organisation profile", "Issue form: data correction, with the project or organisation filled in", form("data-correction.yml")),
 ("Check a label", "Every project page", "Issue form: label check, which feeds the measured precision of topics and labels", form("label-check.yml")),
 ("Check this profile", "Every organisation profile", "Issue form: profile check", form("confirm-profile.yml")),
 ("Report a problem with this page", "Every view, under its summary", "Issue form: defect, with the view filled in", form("defect.yml")),
 ("Roadmap and open items", "About, Roadmap and open items", "Issue form: roadmap item, and the issues it creates", form("roadmap-item.yml")),
 ("Assess a new GitHub feature", "Insights; the deck's Universe slide", "Discussions, with the feature assessment form", REPO + "/discussions"),
 ("Ask a question", "Ask", "Discussions, and the contact form with the question filled in, for anything the catalogue's own data can't answer", REPO + "/discussions"),
 ("Record a decision on a proposed destination", "Every co-cddo project page, government edition", "Issue form in the private companion repository; its build workflow collects the issues with gh", INTERNAL + "/issues/new?template=move-decision.yml"),
 ("Get the government edition", "Government edition", "Actions artifact from the companion repository's build workflow, for people with access to it", INTERNAL + "/actions/workflows/build.yml"),
 ("Report a security problem", "Footer", "Security policy and private vulnerability reporting", REPO + "/security/policy"),
 ("Checks on every change", "About, Method and checks", "Actions: build workflow on every pull request", REPO + "/actions/workflows/build.yml"),
 ("Code scanning", "About, Method and checks", "Actions: CodeQL", REPO + "/actions/workflows/codeql.yml"),
 ("Publishing the open edition", "This page", "Actions: pages workflow, then GitHub Pages", REPO + "/actions/workflows/pages.yml"),
 ("Weekly health report", "About, Roadmap and open items", "Actions: self-routines workflow, and one issue labelled health", REPO + "/issues?q=label%3Ahealth"),
 ("GitHub feature settings", "Checked against GitHub; Insights", "Actions: collect GitHub feature settings (run by a person)", REPO + "/actions/workflows/collect-features.yml"),
 ("Dependency updates", "About, Method and checks", "Dependabot, with a 7-day cooldown", REPO + "/blob/main/.github/dependabot.yml"),
 ("New dependencies are safe", "About, Method and checks", "Actions: dependency review on every pull request", REPO + "/actions/workflows/dependency-review.yml"),
 ("This page is the genuine catalogue", "Footer, colophon", "Build provenance (artifact attestations), checked with gh attestation verify", REPO + "/attestations"),
 ("Releases and change log", "About, Defects and releases", "Releases (tags) and docs/releases.md", REPO + "/releases"),
 ("Review of changes", "About, Method and checks", "Pull requests and CODEOWNERS", REPO + "/pulls"),
 ("Each project's own GitHub", "Every project page, 'On GitHub'", "That repository's issues, pull requests, releases, security policy, Actions and dependency graph", "https://github.com/alphagov/govuk-frontend"),
]

def problems(items, connect):
    p = []
    ids = [i[0] for i in items]
    if len(set(ids)) != len(ids): p.append("duplicate ids")
    for it in items:
        if it[2] not in STATUS: p.append(f"{it[0]}: unknown status")
        if it[3] not in WHO: p.append(f"{it[0]}: unknown role")
        if not (it[8] or "").startswith("https://"): p.append(f"{it[0]}: no GitHub or web route")
        if "@" in (it[8] or "") or re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", it[1] + it[6]): p.append(f"{it[0]}: email address")
    for c in connect:
        if not c[3].startswith("https://"): p.append(f"{c[0]}: no link")
    return p

if __name__ == "__main__":
    lines, fails = [], []
    def need(ok, cid, text, guards="R71"):
        lines.append(f"{'PASS' if ok else 'FAIL'} {cid} {text} [guards: {guards}]")
        if not ok: fails.append(cid)
    p = problems(ITEMS, CONNECT)
    need(not p, "C-RM-01", f"every one of {len(ITEMS)} roadmap items has a known status, a role that must act and a GitHub or web route a person can follow, and every one of {len(CONNECT)} portal features names the GitHub feature or workflow it is joined to{': ' + '; '.join(p) if p else ''}")
    bad = [("RM-X", "t", "nope", "owner", "a", [], "w", "link", "", "l"), ("RM-X", "t", "done", "owner", "a", [], "w", "link", "mailto:x" + "@" + "example.org", "l")]
    need(len(problems(bad, [("f", "w", "g", "ftp://x")])) >= 4, "C-RM-01n", "negative tests: an unknown status, a missing route, an email address, a duplicate id and a feature with no link are each caught")
    q = up.parse_qs(up.urlparse(form("data-correction.yml", what="alphagov/govuk-frontend")).query)
    need(q.get("template") == ["data-correction.yml"] and q.get("what") == ["alphagov/govuk-frontend"], "C-RM-02", "pre-filled issue form links carry the form's template and its field ids, so GitHub fills them in (checked on a correction link for one project)")
    out = dict(repo=REPO, pages=PAGES, status=STATUS, who=WHO,
               items=[dict(id=i[0], title=i[1], status=i[2], who=i[3], area=i[4], views=i[5], now=i[6], kind=i[7], url=i[8], label=i[9]) for i in ITEMS],
               connect=[dict(feature=c[0], where=c[1], github=c[2], url=c[3]) for c in CONNECT])
    json.dump(out, open(os.path.join(HERE, "roadmap.json"), "w"), indent=1, ensure_ascii=False)
    md = ["# Roadmap and open items", "", "Generated by `build/dama/roadmap.py` (R71). The same list is in the catalogue, under About, Roadmap and open items. Nothing here opens an issue, changes a setting or runs a workflow: each route is a link a person follows.", ""]
    for s in STATUS:
        rows = [i for i in ITEMS if i[2] == s]
        if not rows: continue
        md += [f"## {STATUS[s]}", "", "| Item | Who | What is true today | Route |", "|---|---|---|---|"]
        md += [f"| **{i[0]}** {i[1]} | {WHO[i[3]]} | {i[6]} | [{i[9]}]({i[8]}) |" for i in rows] + [""]
    md += ["## How the catalogue connects to GitHub", "", "| In the catalogue | Where | GitHub feature or workflow |", "|---|---|---|"]
    md += [f"| {c[0]} | {c[1]} | [{c[2]}]({c[3]}) |" for c in CONNECT] + [""]
    open(os.path.join(ROOT, "docs", "roadmap.md"), "w").write("\n".join(md))
    open(os.path.join(HERE, "roadmap_checks.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines)); sys.exit(1 if fails else 0)
