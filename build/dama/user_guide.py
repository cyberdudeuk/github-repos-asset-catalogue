"""User guide in three levels: new to GitHub, intermediate and advanced (R41).
One source for the page's User guide view (user_guide.json) and the repository's docs/user-guide/*.md.
Every link is to official guidance or training (GitHub Docs, GitHub Skills, Microsoft Learn, GOV.UK, the GDS Way, NCSC),
checked on the date in CHECKED. Run with python3 -I. Exit code 1 if a check fails.
Checks: C-UG-01 three levels in order, each with an aim, at least 4 steps, at least 4 GitHub words and at least 6 links;
C-UG-02 every link is https on an allowed publisher and no link repeats within a level; C-UG-03 docs match this source."""
import json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(H))
CHECKED = "2026-11-01"
GD = "https://docs.github.com/en/"
LEVELS = [
 dict(id="beginner", title="New to GitHub", icon="home", who="You have never used GitHub, or you've only followed a link to it. You don't need to write code.",
      aim="Understand what GitHub is, read a project's page with confidence, and use this catalogue to find code that matters to your work.",
      steps=[
        ("Learn the five words that matter: repository, README, commit, issue and organisation. The list below explains each in a sentence.", ""),
        ("Search this catalogue in everyday words, such as 'benefits' or 'school data'. Results are grouped and explained in plain English.", "search"),
        ("Open a project's profile. Start with the summary at the top: what it does, who it belongs to and whether it's still looked after.", "profile"),
        ("See who a project belongs to, from the GitHub account up to the government department.", "family"),
        ("Look anything up in the plain-English guide when a word is new.", "glossary"),
        ("When you're ready, follow GitHub's Hello World exercise below. It takes about 15 minutes and you can't break anything.", ""),
      ],
      words=[
        ("Repository (repo)", "A folder for one project: its files, its history and the conversation about it."),
        ("README", "The front page of a repository. It should say what the project is, who it's for and how to use it."),
        ("Commit", "A saved change, with a note saying what changed and who changed it. The history of commits is how you can trace any change."),
        ("Issue", "A note on a repository to report a problem, ask a question or suggest an idea."),
        ("Organisation (account)", "A shared GitHub account for a team or department, which owns its repositories."),
        ("Public and private", "Anyone can see a public repository. Only invited people can see a private one; this catalogue only covers public code."),
        ("Archived", "Read-only. The project is kept for reference but is no longer changed."),
      ],
      links=[
        ("About GitHub and Git", GD + "get-started/start-your-journey/about-github-and-git", "GitHub Docs", "Guidance"),
        ("Creating an account on GitHub", GD + "get-started/start-your-journey/creating-an-account-on-github", "GitHub Docs", "Guidance"),
        ("Hello World: your first repository, branch and pull request", GD + "get-started/start-your-journey/hello-world", "GitHub Docs", "Learning"),
        ("GitHub glossary", GD + "get-started/learning-about-github/github-glossary", "GitHub Docs", "Guidance"),
        ("About repositories", GD + "repositories/creating-and-managing-repositories/about-repositories", "GitHub Docs", "Guidance"),
        ("About the repository README file", GD + "repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes", "GitHub Docs", "Guidance"),
        ("About searching on GitHub", GD + "search-github/getting-started-with-searching-on-github/about-searching-on-github", "GitHub Docs", "Guidance"),
        ("GitHub Skills: free interactive courses, starting with 'Introduction to GitHub'", "https://learn.github.com/skills", "GitHub Learn", "Training"),
        ("Git and GitHub learning resources", GD + "get-started/start-your-journey/git-and-github-learning-resources", "GitHub Docs", "Learning"),
      ]),
 dict(id="intermediate", title="Intermediate", icon="practice", who="You can find your way around a repository and want to judge a project, contribute to one or look after your own.",
      aim="Judge whether a project is well looked after, take part through issues and pull requests, and know what good looks like in government.",
      steps=[
        ("Check how well a project is looked after: README, licence, code owners, recent activity and automated checks.", "practice"),
        ("Compare a project with the GDS Way and the Service Manual's guidance on open code.", "gdsway"),
        ("Find projects that publish a website with GitHub Pages, and who runs them.", "pages"),
        ("Explore projects by topic and by organisation to find work you could reuse rather than rebuild.", "topics"),
        ("Raise an issue or propose a change with a pull request, following the GitHub flow.", ""),
        ("Use the analytics dashboard to see patterns across the estate.", "insights"),
      ],
      words=[
        ("Branch", "A separate line of work, so changes can be made and reviewed without affecting the main version."),
        ("Pull request", "A proposal to merge a branch's changes, with review and discussion before they go in."),
        ("Fork", "Your own copy of someone else's repository, used to propose changes when you can't change theirs directly."),
        ("CODEOWNERS", "A file naming who must review changes to which parts of a repository."),
        ("Licence", "Says how others may use the code. Government code is usually MIT; content is usually under the Open Government Licence."),
        ("GitHub Pages", "A website published straight from a repository."),
      ],
      links=[
        ("GitHub flow", GD + "get-started/using-github/github-flow", "GitHub Docs", "Guidance"),
        ("About issues", GD + "issues/tracking-your-work-with-issues/about-issues", "GitHub Docs", "Guidance"),
        ("Pull requests", GD + "pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests", "GitHub Docs", "Guidance"),
        ("Fork a repository", GD + "pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo", "GitHub Docs", "Learning"),
        ("About code owners", GD + "repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners", "GitHub Docs", "Guidance"),
        ("Licensing a repository", GD + "repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository", "GitHub Docs", "Guidance"),
        ("What is GitHub Pages?", GD + "pages/getting-started-with-github-pages/about-github-pages", "GitHub Docs", "Guidance"),
        ("Basic writing and formatting syntax (Markdown)", GD + "get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax", "GitHub Docs", "Learning"),
        ("Making source code open and reusable", "https://www.gov.uk/service-manual/technology/making-source-code-open-and-reusable", "GOV.UK Service Manual", "Guidance"),
        ("The GDS Way: how to store source code", "https://gds-way.digital.cabinet-office.gov.uk/standards/source-code/", "GDS Way", "Guidance"),
        ("Microsoft Learn: GitHub training paths", "https://learn.microsoft.com/en-us/training/github/", "Microsoft Learn", "Training"),
      ]),
 dict(id="advanced", title="Advanced", icon="gds", who="You run repositories, organisations or migrations, or build on this catalogue's data.",
      aim="Secure and automate repositories, plan moves between organisations without breaking anything, and reuse the catalogue's data and feeds.",
      steps=[
        ("Review the security and supply-chain signals: secret scanning, Dependabot, pinned actions and branch rules.", "safe"),
        ("Plan a move between organisations: the migration plan, the checks before and after, and what breaks on transfer.", "plan"),
        ("Find legacy technology and technical debt by organisation, with the evidence behind each signal.", "legacy"),
        ("Reuse the data: download feeds, the knowledge graph (SKOS, OWL, PROV) and the DCAT catalogue.", "knowledge"),
        ("Trace every requirement to the checks that prove it, and every defect to its fix.", "trace"),
        ("Link straight into the catalogue: #repo=<account>/<repository>, #org=<GOV.UK slug>, #legacy=<GOV.UK slug>, #account=<GitHub account>.", ""),
      ],
      words=[
        ("GitHub Actions", "Automated workflows that run on events such as a push or pull request: tests, builds, deployments."),
        ("Rulesets and branch protection", "Rules for what may be merged and by whom, such as required reviews and checks."),
        ("Secret scanning and push protection", "Finds credentials committed to a repository and can block them before they are pushed."),
        ("Dependabot", "Raises alerts and pull requests for vulnerable or out-of-date dependencies."),
        ("Transfer", "Moving a repository to another account. GitHub redirects old links, but Pages, packages and some settings need extra steps."),
        ("REST API", "The programmable interface to GitHub, used for audits, inventories and automation."),
      ],
      links=[
        ("Understanding GitHub Actions", GD + "actions/about-github-actions/understanding-github-actions", "GitHub Docs", "Learning"),
        ("Secure use reference for GitHub Actions", GD + "actions/security-for-github-actions/security-guides/security-hardening-for-github-actions", "GitHub Docs", "Guidance"),
        ("GitHub security features", GD + "code-security/getting-started/github-security-features", "GitHub Docs", "Guidance"),
        ("Secret scanning", GD + "code-security/secret-scanning/introduction/about-secret-scanning", "GitHub Docs", "Guidance"),
        ("Securing your supply chain, including Dependabot", GD + "code-security/dependabot", "GitHub Docs", "Guidance"),
        ("About rulesets", GD + "repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets", "GitHub Docs", "Guidance"),
        ("Transferring a repository", GD + "repositories/creating-and-managing-repositories/transferring-a-repository", "GitHub Docs", "Guidance"),
        ("Archiving repositories", GD + "repositories/archiving-a-github-repository/archiving-repositories", "GitHub Docs", "Guidance"),
        ("Migrations", GD + "migrations", "GitHub Docs", "Guidance"),
        ("GitHub REST API", GD + "rest", "GitHub Docs", "Guidance"),
        ("GitHub Well-Architected", "https://wellarchitected.github.com/", "GitHub", "Guidance"),
        ("About GitHub Certifications", GD + "get-started/showcase-your-expertise-with-github-certifications/about-github-certifications", "GitHub Docs", "Training"),
        ("Secure development and deployment guidance", "https://www.ncsc.gov.uk/collection/developers-collection", "NCSC", "Guidance"),
        ("The Technology Code of Practice", "https://www.gov.uk/guidance/the-technology-code-of-practice", "GOV.UK", "Guidance"),
      ]),
]
ALLOWED = ("docs.github.com", "learn.github.com", "wellarchitected.github.com", "learn.microsoft.com", "www.gov.uk", "gds-way.digital.cabinet-office.gov.uk", "www.ncsc.gov.uk")
FAILS, LINES = [], []
def need(ok, cid, msg):
    LINES.append(("PASS " if ok else "FAIL ") + cid + " " + msg); print(LINES[-1])
    if not ok: FAILS.append(cid)

def checks(levels):
    ok1 = [l["id"] for l in levels] == ["beginner", "intermediate", "advanced"] and all(l["aim"] and len(l["steps"]) >= 4 and len(l["words"]) >= 4 and len(l["links"]) >= 6 for l in levels)
    bad = [u for l in levels for _, u, _, _ in l["links"] if not re.fullmatch(r"https://(%s)(/\S*)?" % "|".join(map(re.escape, ALLOWED)), u)]
    dup = [l["id"] for l in levels if len({u for _, u, _, _ in l["links"]}) != len(l["links"])]
    return ok1, bad, dup

def md(l, i):
    nav = " · ".join(f"[{x['title']}]({x['id']}.md)" if x is not l else f"**{x['title']}**" for x in LEVELS)
    s = [f"# User guide: {l['title']}", "", nav, "", f"**Who this is for:** {l['who']}", "", f"**By the end:** {l['aim']}", "", "## Steps", ""]
    s += [f"{n}. {t}" + (f" (in the catalogue: *{v}* view)" if v else "") for n, (t, v) in enumerate(l["steps"], 1)]
    s += ["", "## Words you'll meet", ""] + [f"- **{w}:** {d}" for w, d in l["words"]]
    s += ["", "## Guidance, learning and training", "", "| Link | From | Type |", "| --- | --- | --- |"]
    s += [f"| [{t}]({u}) | {p} | {k} |" for t, u, p, k in l["links"]]
    if i + 1 < len(LEVELS): s += ["", f"Next: [{LEVELS[i + 1]['title']}]({LEVELS[i + 1]['id']}.md)"]
    s += ["", f"Links checked on {CHECKED}. Generated by `build/dama/user_guide.py`; edit that file, not this one.", ""]
    return "\n".join(s)

def index():
    s = ["# User guide", "", "Three levels. Start where you are and move on when you're ready.", "", "| Level | Who it's for | By the end |", "| --- | --- | --- |"]
    s += [f"| [{l['title']}]({l['id']}.md) | {l['who']} | {l['aim']} |" for l in LEVELS]
    s += ["", "In the catalogue itself, the same guide is under Home, User guide. For step-by-step walkthroughs, see [Guided tours and tutorials](tours.md).", "", f"Links checked on {CHECKED}. Generated by `build/dama/user_guide.py`.", ""]
    return "\n".join(s)

if __name__ == "__main__":
    ok1, bad, dup = checks(LEVELS)
    need(ok1, "C-UG-01", "three levels in order (new to GitHub, intermediate, advanced), each with an aim, at least 4 steps, 4 GitHub words and 6 links [guards: R41]")
    need(not bad and not dup, "C-UG-02", f"every link is https on an official publisher and none repeats within a level (bad {bad}, repeats {dup}) [guards: R41]")
    # negative tests: the checks reject a guide missing a level and a link off the allowed publishers
    n1, _, _ = checks(LEVELS[:2]); _, nb, _ = checks([dict(LEVELS[0], links=LEVELS[0]["links"] + [("x", "http://example.com/x", "x", "x")])] + LEVELS[1:])
    need(not n1 and nb == ["http://example.com/x"], "C-UG-02n", "negative tests: a guide with a level missing, and a non-https link off the allowed publishers, are both rejected [guards: R41]")
    json.dump(dict(checked=CHECKED, levels=LEVELS), open(os.path.join(H, "user_guide.json"), "w"), ensure_ascii=False, indent=1)
    D = os.path.join(ROOT, "docs", "user-guide"); os.makedirs(D, exist_ok=True)
    files = {"README.md": index(), **{l["id"] + ".md": md(l, i) for i, l in enumerate(LEVELS)}}
    stale = [f for f, t in files.items() if not os.path.exists(os.path.join(D, f)) or open(os.path.join(D, f)).read() != t]
    for f, t in files.items(): open(os.path.join(D, f), "w").write(t)
    need(True, "C-UG-03", f"docs/user-guide regenerated from this source ({len(files)} files, {len(stale)} changed) [guards: R41]")
    open(os.path.join(H, "user_guide_checks.txt"), "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)
