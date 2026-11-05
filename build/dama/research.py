"""User research, ideas and prioritisation for the catalogue (R74): the one source.

Writes:
  build/dama/research.json          what the page's "Help shape the catalogue" view shows
  docs/research/*.md                the research bundle, in the repository, worked on in the open
  .github/ISSUE_TEMPLATE/idea.yml, research-signup.yml, survey-catalogue.yml
  research_checks.txt               C-RES-01 to C-RES-03, with negative tests
The email bundle (build/tools/research_bundle.py) is made from the same files.

Personas come from service_design.py, roadmap items from roadmap.json and strategy themes from the government's
roadmap for modern digital government, so nothing here is a second copy. Run with python3 -I research.py.
"""
import json, os, re, runpy

D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(D))
REPO = "https://github.com/cyberdudeuk/github-repos-asset-catalogue"
PAGES = "https://cyberdudeuk.github.io/github-repos-asset-catalogue/"
SD = runpy.run_path(os.path.join(D, "service_design.py"), run_name="research")
PERSONAS = {p["id"]: p for p in SD["PERSONAS"]}
RM = json.load(open(os.path.join(D, "roadmap.json")))
AS_OF = "2026-11-05"

def form(name, **pre):
    from urllib.parse import urlencode
    return REPO + "/issues/new?" + urlencode({"template": name, **pre})

SIGNUP = form("research-signup.yml")
IDEA = form("idea.yml")
SURVEY = form("survey-catalogue.yml")
CONTACT = form("contact.yml")
IDEAS_LIVE = REPO + "/issues?q=" + "is%3Aissue+is%3Aopen+label%3Aidea+sort%3Areactions-%2B1-desc"

# ---------- why we're doing research: tactical (the next few months) and strategic (where the catalogue goes) ----------
OBJECTIVES = [
    ("T1", "tactical", "Can people who are new to GitHub find what they came for, without help?", "Usability tests with the five commonest tasks; time, success and where people hesitate."),
    ("T2", "tactical", "Which questions bring people to the catalogue, and which views answer them?", "Interviews and the survey; compare with the role-based questions on Home."),
    ("T3", "tactical", "Do people understand and trust the evidence labels, such as 'part of a live service', and their measured accuracy?", "Usability tests: ask people to explain a label in their own words, and whether they'd act on it."),
    ("T4", "tactical", "What stops people who use assistive technology from using the catalogue?", "Sessions with screen reader, magnification, voice and switch users; fixes go straight into the backlog."),
    ("T5", "tactical", "Which handovers to the DAM capability playbooks and the DQ Commons help, and which confuse?", "Cross-portal journey tests (the six journeys in the three-portal review)."),
    ("S1", "strategic", "Who needs this catalogue to keep existing, and who should own and fund it?", "Interviews with data leaders, architects and policy leads; the owner's decision on a home (roadmap RM-11)."),
    ("S2", "strategic", "Should it become a registered govukOS node and a source of data feeds for other services?", "Interviews with the teams behind GTI, ANA, LIAH and the shared registers; test the data/xref.json feed."),
    ("S3", "strategic", "How does it serve the government's strategy for data, including the forthcoming Strategic Data Roadmap?", "Map findings to the roadmap for modern digital government; re-map when the Strategic Data Roadmap is published."),
    ("S4", "strategic", "How fresh and complete does the data need to be for people to rely on it?", "Survey and interviews; compare with what refreshing costs (roadmap RM-09 and RM-10)."),
    ("S5", "strategic", "Is the split between the open edition and the government edition right?", "Interviews with government and public sector users, and with people outside government."),
]

# ---------- ways to take part: each says how long it takes, what happens and how to sign up ----------
METHODS = [
    dict(id="M1", name="Conversation about your work", minutes=45, mode="Online, one to one", who="Anyone who might use the catalogue", what="We ask about your work, how you find out what others in government have built, and what gets in the way. No preparation needed.", objectives=["T2", "S1", "S4", "S5"]),
    dict(id="M2", name="Try the catalogue", minutes=45, mode="Online, one to one, sharing your screen", who="Anyone, especially people new to GitHub", what="You try four or five everyday tasks while thinking aloud. We're testing the catalogue, not you.", objectives=["T1", "T3"]),
    dict(id="M3", name="Accessibility session", minutes=60, mode="Online or in person, with your own set-up", who="People who use a screen reader, magnification, voice control, a switch or other assistive technology", what="You use the catalogue with your own set-up and tell us what works and what gets in the way. We pay for interpreters and support.", objectives=["T4"]),
    dict(id="M4", name="Five-minute survey", minutes=5, mode="A GitHub form, in your own time", who="Anyone", what="Seven questions about what you use the catalogue for and what's missing. Only totals are published, and counts under 5 are hidden.", objectives=["T2", "S4"]),
    dict(id="M5", name="Journey across three portals", minutes=60, mode="Online, one to one", who="Data leaders, stewards, architects, service owners", what="You follow a task that starts in one of the DAM playbooks, the DQ Commons or this catalogue and carries on in another.", objectives=["T5", "S2"]),
    dict(id="M6", name="Ideas and votes", minutes=None, mode="GitHub, whenever you like", who="Anyone with a GitHub account", what="Suggest an idea, or add a thumbs-up to the ideas you want most. Votes help us decide what to do next.", objectives=["T2", "S1"]),
]

# ---------- who we need to hear from: quotas are minimums for each round of about 12 people ----------
QUOTAS = [
    ("Central government department or agency", 3), ("Local authority, including outside England", 2),
    ("Devolved government or public body in Scotland, Wales or Northern Ireland", 2), ("NHS or other health and care body", 1),
    ("Arm's length body or regulator", 1), ("Outside government: supplier, academic or civil society", 1),
    ("People who use assistive technology", 2), ("People who have never used GitHub", 4),
    ("People working outside London and the South East", 5), ("Welsh speakers", 1),
]
INCLUSION = [
    "Sessions at different times of day, with breaks, and a phone option.",
    "Captions on video calls; a British Sign Language interpreter on request, paid for from the research budget.",
    "Materials sent in advance, in large print, easy read or Welsh on request.",
    "Your own device and set-up for accessibility sessions; we never ask you to install anything.",
    "Age, sex, ethnicity and disability are asked only if you choose to answer, and reported only as totals, never against a person.",
]

# ---------- rounds: tactical first, strategic once the Strategic Data Roadmap is out ----------
ROUNDS = [
    dict(id="R1", name="Round 1: can people use it?", when="November to December 2026", objectives=["T1", "T2", "T3", "T4"], methods=["M1", "M2", "M3", "M4"], status="recruiting"),
    dict(id="R2", name="Round 2: does it join up?", when="January to February 2027", objectives=["T5", "S2", "S3"], methods=["M5", "M1"], status="planned"),
    dict(id="R3", name="Round 3: where should it go?", when="March 2027", objectives=["S1", "S4", "S5"], methods=["M1", "M4"], status="planned"),
]

# ---------- usability tasks (M2): everyday tasks for each persona ----------
TASKS = [
    ("U1", "P1", "Your minister has asked whether any public body has built a tool for checking addresses. Find out, and who to ask.", "#discover"),
    ("U2", "P2", "Find out what your organisation publishes as code that is about data quality or catalogues.", "#dama=DM-DQ"),
    ("U3", "P3", "You're building a form for a new service. Find a component others in government already use for this.", "#reuse"),
    ("U4", "P4", "Find which of your organisation's projects may rely on technology that is no longer supported.", "#legacy"),
    ("U5", "P6", "Find which organisations use the DCAT standard in their code, and how you'd link to that list from another site.", "#standard=dcat3"),
    ("U6", "P1", "Something in a project's description is wrong. Tell the maintainers.", "#discover"),
]

# ---------- strategy the backlog is checked against (verified 5 November 2026) ----------
STRATEGY = [
    dict(id="G1", name="Join up public sector services", source="Roadmap for modern digital government, 2025 to 2030", url="https://roadmap-for-modern-digital-government.campaign.gov.uk/join-up-services/"),
    dict(id="G2", name="Harness the power of AI for the public good", source="Roadmap for modern digital government, 2025 to 2030", url="https://roadmap-for-modern-digital-government.campaign.gov.uk/ai/"),
    dict(id="G3", name="Strengthen and extend our digital and data public infrastructure", source="Roadmap for modern digital government, 2025 to 2030", url="https://roadmap-for-modern-digital-government.campaign.gov.uk/digital-and-data-infrastructure/"),
    dict(id="G4", name="Elevate leadership, invest in talent", source="Roadmap for modern digital government, 2025 to 2030", url="https://roadmap-for-modern-digital-government.campaign.gov.uk/leadership-talent/"),
    dict(id="G5", name="Fund for outcomes, procure for growth and innovation", source="Roadmap for modern digital government, 2025 to 2030", url="https://roadmap-for-modern-digital-government.campaign.gov.uk/funding-procurement/"),
    dict(id="G6", name="Commit to transparency, drive accountability", source="Roadmap for modern digital government, 2025 to 2030", url="https://roadmap-for-modern-digital-government.campaign.gov.uk/transparency/"),
    dict(id="D1", name="Data Asset Management Policy", source="Cabinet Office and GDS; guidance in the DAM capability playbooks", url="https://cyberdudeuk.github.io/dam-capability-playbooks/dam.html"),
    dict(id="D2", name="Strategic Data Roadmap (forthcoming)", source="Led by the Chief Data Officer. The roadmap for modern digital government planned 'a strategic roadmap for public sector data' for April 2026; a GDS blog post of 3 September 2026 says it is 'due to be published in the autumn'. Not published when this was written, so nothing is mapped to it yet.", url="https://dataingovernment.blog.gov.uk/2026/09/03/connecting-data-to-enable-modern-digital-government/", pending=True),
]

# ---------- how an idea becomes work: transparent, with people deciding ----------
CRITERIA = [
    dict(id="value", name="Value to users", scale="0 to 3", how="3: research shows it blocks people, or it has 10 or more votes. 2: it slows people down, or 5 to 9 votes. 1: a nice-to-have. 0: no evidence yet.", weight=2),
    dict(id="reach", name="Reach", scale="0 to 3", how="How many of the six personas it helps: 1 for one, 2 for two or three, 3 for four or more.", weight=1),
    dict(id="fit", name="Strategic fit", scale="0 to 3", how="How directly it serves the themes above: 3 directly, 2 indirectly, 1 slightly, 0 not at all.", weight=2),
    dict(id="feasible", name="Feasibility", scale="0 to 3", how="3: small, no dependencies. 2: medium, or needs one other team. 1: large, or needs a decision by the owner. 0: not possible now.", weight=1),
]
CAPACITY = "Capacity is a gate, not a score. Each quarter the maintainers say how many points of work they can take on; items go into Now in score order until it's full, then Next. Anything needing the owner's decision waits for it, however high it scores."
LABELS = ["idea", "research", "survey-response", "value:0", "value:1", "value:2", "value:3", "reach:1", "reach:2", "reach:3", "fit:0", "fit:1", "fit:2", "fit:3",
          "feasible:0", "feasible:1", "feasible:2", "feasible:3", "moscow:must", "moscow:should", "moscow:could", "moscow:wont", "now", "next", "later"] + [f"theme:{s['id']}" for s in STRATEGY]

def score(a):
    """The priority score: weighted sum of the four criteria (0 to 18). People still decide; the score orders the discussion."""
    return sum(a.get(c["id"], 0) * c["weight"] for c in CRITERIA)

# ---------- the backlog: open roadmap items, assessed in the open. Proposed by the maintainers; the owner confirms. ----------
ASSESS = {   # roadmap id: value, reach, fit, feasible, themes, why (the reason for the scores, so anyone can challenge them)
    "RM-01": (3, 3, 3, 2, ["G6", "G1"], "Nothing has been tested with users yet; this research bundle starts it. Needs facilitators and participants."),
    "RM-02": (2, 2, 1, 3, ["G3"], "Measured precision for topics, as for other labels; the label-check form already collects the sample."),
    "RM-03": (2, 2, 2, 2, ["G1", "G6"], "Organisations confirming their own profile makes it trustworthy; needs them to take part."),
    "RM-04": (3, 3, 2, 1, ["G6", "G4"], "Manual accessibility testing is the gap automated checks can't close; needs a specialist."),
    "RM-07": (3, 2, 3, 1, ["G3"], "Joining code to the datasets it publishes serves the data infrastructure theme directly; large, and needs the catalogues' data."),
    "RM-08": (2, 2, 2, 1, ["G3"], "Maps help devolved and local users; needs boundary data and design work."),
    "RM-09": (2, 2, 2, 2, ["G3"], "Feature settings for every project replace an estimate; needs a token and a person to run it."),
    "RM-10": (3, 3, 3, 1, ["G3"], "Fresh data is what people will rely on (objective S4); each refresh needs a person."),
    "RM-11": (2, 2, 3, 1, ["G3"], "Linking code to the systems it belongs to supports upgrading legacy systems; depends on LIAH."),
    "RM-12": (3, 3, 3, 1, ["G4", "G6"], "Without a named owning team nothing else is sustainable (objective S1); the owner's decision."),
    "RM-13": (2, 3, 2, 1, ["G3"], "A permanent home keeps links stable; follows RM-12."),
    "RM-23": (2, 3, 1, 3, ["G6"], "Labels make issues filterable and group release notes; minutes for the owner."),
    "RM-24": (1, 1, 2, 3, ["G3"], "A person approves every publish: the catalogue's own rule, enforced by GitHub."),
    "RM-25": (2, 3, 1, 3, ["G6"], "Questions Ask can't answer get a public, searchable answer."),
    "RM-26": (2, 2, 2, 3, ["G6"], "A board shows everyone the status of each item, in the open."),
}

def backlog():
    items = []
    for it in RM["items"]:
        if it["id"] not in ASSESS or it["status"] == "done": continue
        v, r, f, fe, th, why = ASSESS[it["id"]]
        a = dict(value=v, reach=r, fit=f, feasible=fe)
        items.append(dict(id=it["id"], title=it["title"], status=it["status"], who=it.get("who", ""), themes=th, scores=a, score=score(a), why=why,
                          needs_owner=it["status"] == "owner", route=it.get("route", "")))
    items.sort(key=lambda x: (-x["score"], x["id"]))
    for x in items: x["horizon"] = "Waiting for the owner" if x["needs_owner"] else "Waiting for another team" if x["status"] == "external" else "Now" if x["score"] >= 12 else "Next"
    return items

# ---------- the documents ----------
def md_plan():
    o = lambda kind: "\n".join(f"| {i} | {q} | {how} |" for i, k, q, how in OBJECTIVES if k == kind)
    return f"""# Research plan

Last reviewed {AS_OF}. Part of the [research bundle](README.md). Requirement R74.

## Why we're doing research

The catalogue was built from public data, with checks on every figure, but without testing it with the people it is for. Research tells us whether it helps them, what to fix first, and where it should go next. Everything we learn goes into the [backlog and roadmap]({PAGES}#shape), in the open.

### Tactical: the next few months

| Id | What we need to know | How we'll find out |
|---|---|---|
{o("tactical")}

### Strategic: where the catalogue goes

| Id | What we need to know | How we'll find out |
|---|---|---|
{o("strategic")}

## Who we need to hear from

The six personas the catalogue was designed for: {", ".join(f"{p['name']} ({p['id']})" for p in PERSONAS.values())}. Minimums for each round of about 12 people:

| Group | At least |
|---|---|
""" + "\n".join(f"| {g} | {n} |" for g, n in QUOTAS) + """

## Ways to take part

| Id | Activity | Time | How | What happens |
|---|---|---|---|---|
""" + "\n".join(f"| {m['id']} | {m['name']} | {str(m['minutes']) + ' minutes' if m['minutes'] else 'Any time'} | {m['mode']} | {m['what']} |" for m in METHODS) + """

## Rounds

| Round | When | Answers | Activities | Status |
|---|---|---|---|---|
""" + "\n".join(f"| {r['name']} | {r['when']} | {', '.join(r['objectives'])} | {', '.join(r['methods'])} | {r['status'].capitalize()} |" for r in ROUNDS) + """

## Making it inclusive

""" + "\n".join(f"- {x}" for x in INCLUSION) + """

## Looking after what people tell us

- Taking part is voluntary, and people can stop at any time without saying why.
- We record a session only with consent, keep recordings outside GitHub, and delete them within 30 days.
- Notes use session codes (R1-03), never names. Names and contact details stay with the person who arranged the session and are deleted when the round ends.
- Findings are published as themes and totals, in the repository. Counts under 5 are hidden.
- Anyone can withdraw what they said within 30 days, through the contact form or by replying to the person who invited them.
- Nothing about a participant is ever added to the catalogue's data.

## From findings to the backlog

Each finding becomes an issue labelled `research`, with the session codes as evidence and a severity (blocks, slows, annoys). It is then assessed like any idea: see [Backlog and prioritisation](backlog-and-prioritisation.md).
"""

def md_backlog(items):
    rows = "\n".join(f"| {c['name']} | {c['scale']} | ×{c['weight']} | {c['how']} |" for c in CRITERIA)
    th = "\n".join(f"| {s['id']} | {s['name']} | {s['source']} |" for s in STRATEGY)
    bl = "\n".join(f"| {x['id']} | {x['title']} | {x['scores']['value']} | {x['scores']['reach']} | {x['scores']['fit']} | {x['scores']['feasible']} | **{x['score']}** | {', '.join(x['themes'])} | {x['horizon']} |" for x in items)
    return f"""# Backlog and prioritisation

Last reviewed {AS_OF}. Requirement R74. Shown in the catalogue under About, [Help shape the catalogue]({PAGES}#shape).

## How an idea becomes work

1. **Anyone suggests it** with the [idea form]({IDEA}), or a research finding raises it. It is a public issue labelled `idea`.
2. **People vote** with a thumbs-up on the issue. [See the ideas with the most votes]({IDEAS_LIVE}).
3. **The maintainers assess it** every two weeks, in the open, by adding labels to the issue: a score for each criterion below, the strategy themes it serves, and a MoSCoW priority. The reason goes in a comment, so anyone can challenge it.
4. **Capacity decides when.** {CAPACITY}
5. **The roadmap shows it.** Items in Now and Next appear on the catalogue's roadmap, each linked to its issue.

## Criteria

The score orders the discussion; people decide. Score = value × 2 + reach + fit × 2 + feasibility, out of 18.

| Criterion | Scale | Weight | How it's judged |
|---|---|---|---|
{rows}

## Strategy themes

Every item is checked against these. Labels: `theme:G1` and so on.

| Id | Theme | Source |
|---|---|---|
{th}

## The backlog today

Open roadmap items, assessed by the maintainers on {AS_OF}. These scores are proposals for the owner to confirm; challenge any of them on the item's issue.

| Item | What | Value | Reach | Fit | Feasible | Score | Themes | When |
|---|---|---|---|---|---|---|---|---|
{bl}

## Labels

{", ".join(f"`{l}`" for l in LABELS)}. GitHub silently drops a label that doesn't exist, so the owner creates these once (roadmap RM-23).
"""

def md_intro():
    return f"""# Introducing the GitHub Repos Asset Catalogue

**For teams who might use it.** One page, about three minutes to read.

## What it is

A free, open catalogue of the code that UK public bodies publish on GitHub, organised so that people who don't write code can use it. It covers more than 25,000 public code projects from over 200 public sector GitHub accounts, with plain-English descriptions, the organisations behind them, the topics they cover and evidence of whether they're still in use.

Open it at {PAGES}. It needs only a web browser: no account, licence, sign-in or AI service, and it sends nothing anywhere.

## What it helps you do

- **Before you build or buy, look for it.** Find whether another public body has already built what you need, and who to ask.
- **See your organisation's code estate.** What it publishes, how well it's looked after, and where there is legacy technology or debt.
- **Find good practice in data.** Projects that show data quality, catalogues, metadata and standards work, on the DAMA wheel, with links to the DAM capability playbooks and the Data Quality Commons.
- **Find reusable building blocks.** Components, APIs and patterns other services already rely on.

## Who it's for

Policy and strategy colleagues, data leaders, service owners, engineering and security leads, and architects. You don't need to know GitHub: the catalogue explains it as you go.

## How much to trust it

Every figure comes from public GitHub data and can be reproduced. Labels such as "part of a live service" are found by rules, and each shows how accurate it was on a checked sample. It is a working tool, not an official statement of government policy.

## Help us make it better

We're running user research from November 2026. You can:

- **Talk to us for 45 minutes** about your work, or try the catalogue while we watch and learn.
- **Take a five-minute survey**: {SURVEY}
- **Suggest an idea or vote for one**: {IDEAS_LIVE}

What we learn shapes what we build next, and the backlog is public. See the research plan and how we decide what to do: {PAGES}#shape
"""

def md_email():
    return f"""# Invitation email

Send this from your own account to teams who might use the catalogue. It contains no email address of ours: people reply to you, and you arrange sessions.
Attach the introduction, the participant information and the consent form from this bundle.

**Subject:** Help shape a catalogue of public sector code (45 minutes, online)

Hello,

I'd like to introduce the GitHub Repos Asset Catalogue, and ask whether you or someone in your team could help us improve it.

**What it is.** A free, open catalogue of the code UK public bodies publish on GitHub, organised for people who don't write code. It helps you find whether someone in government has already built what you need, see your organisation's code estate, and find good practice in data and standards. It works in any browser, with no account or sign-in: {PAGES}

**What we're asking.** We're running user research from November to December 2026. You could:

- have a 45-minute online conversation about your work, or try the catalogue while thinking aloud
- if you use assistive technology, have a 60-minute session with your own set-up
- take a five-minute survey: {SURVEY}
- suggest an idea, or vote for one: {IDEAS_LIVE}

**Who we'd like to hear from.** Anyone who might use it: policy, data, service, engineering, security and architecture colleagues, in central and local government, the devolved governments, the NHS and arm's length bodies. We especially want to hear from people who have never used GitHub, people who use assistive technology, and people outside London and the South East.

**What happens next.** If you'd like to take part, reply to this email with the kind of session you'd like and any support you need, such as captions, a British Sign Language interpreter, Welsh, or materials in advance. Please don't send anything else about yourself. We'll arrange a time, and send the participant information and consent form first.

Taking part is voluntary. We don't publish names, and we report findings only as themes and totals.

Please pass this on to anyone else who might be interested.

Thank you,

[Your name]
[Your team]
"""

def md_info():
    return f"""# Participant information

**User research for the GitHub Repos Asset Catalogue.** Please read this before your session. Ask about anything that isn't clear.

## What the research is for

To find out whether the catalogue ({PAGES}) helps the people it is for, and what to improve. We are testing the catalogue, not you. There are no wrong answers.

## What happens

- A session of 45 minutes (60 for accessibility sessions), online or in person.
- We'll ask about your work, and may ask you to try some tasks while thinking aloud.
- One person leads the session; a second may take notes.
- You can take breaks, skip any question, or stop at any time without saying why.

## What we keep, and for how long

- **Notes**, with a session code instead of your name.
- **A recording**, only if you agree. Kept outside GitHub and deleted within 30 days.
- **Your name and how to reach you**, only to arrange the session, and deleted when the round of research ends.

## What we publish

Themes and totals in the catalogue's public repository, for example "4 of 12 people couldn't find the search". Never your name, and never your organisation's name unless you ask us to. Counts under 5 are hidden.

## Withdrawing

You can withdraw what you said within 30 days of your session. Reply to the person who invited you, or use the contact form and give only your session code: {CONTACT}

## Support

Tell us what would help: captions, a British Sign Language interpreter, Welsh, breaks, a phone option, large print or easy read materials. We arrange and pay for it.
"""

def md_consent():
    return """# Consent form

**User research for the GitHub Repos Asset Catalogue.** We'll go through this with you at the start of the session. You can say yes or no to each part.

Session code: ____________ Date: ____________

| What you're agreeing to | Yes | No |
|------------------------------------------------------------|----------|----------|
| I've read the participant information, or had it read to me, and had the chance to ask questions. | ☐ | ☐ |
| I understand that taking part is voluntary and that I can stop at any time without giving a reason. | ☐ | ☐ |
| I agree to notes being taken, with a session code instead of my name. | ☐ | ☐ |
| I agree to the session being recorded. The recording is kept outside GitHub and deleted within 30 days. | ☐ | ☐ |
| I agree to anonymous quotes being used in published findings. | ☐ | ☐ |
| I understand that I can withdraw what I said within 30 days of the session. | ☐ | ☐ |

Consent can be given out loud at the start of an online session. The facilitator records the answers against the session code.
"""

def md_screener():
    return f"""# Screener

For the person arranging sessions. Ask these by reply or in a short call; don't put them in a public form. Store the answers against a session code, and delete names and contact details when the round ends.

1. What kind of organisation do you work for? (central department or agency; local authority; devolved government or public body; NHS or health and care; arm's length body or regulator; outside government; other)
2. Which nation do you mainly work in? (England, Scotland, Wales, Northern Ireland, UK-wide)
3. Which is closest to your role? {"; ".join(p['name'] for p in PERSONAS.values())}; other.
4. How often do you use GitHub? (never; sometimes; often)
5. Do you use any assistive technology, such as a screen reader, magnification, voice control or a switch? (no; yes, which; prefer not to say)
6. Which would you like to do? (conversation; try the catalogue; accessibility session; journey across three portals)
7. What would make taking part easier? (time of day; captions; British Sign Language; Welsh; breaks; materials in advance; phone; other)

Recruit until each round meets the minimums in the [research plan](research-plan.md#who-we-need-to-hear-from).
"""

def md_guides():
    tasks = "\n".join(f"| {i} | {PERSONAS[p]['name']} | {t} | `{path}` |" for i, p, t, path in TASKS)
    return f"""# Session guides

For facilitators. Read the [participant information](participant-information.md) and [consent form](consent-form.md) with the participant first.

## M1: Conversation about your work (45 minutes)

| Minutes | Part | Ask |
|---|---|---|
| 5 | Welcome | Introductions, consent, access needs, "we're learning, there are no wrong answers". |
| 10 | Your work | What do you do? When did you last need to know whether someone else in government had built something? What did you do? |
| 15 | Finding things out | Where do you look first? Who do you ask? What has gone wrong? What would you trust? |
| 10 | The catalogue | Show Home. What do you think it's for? Who would use it where you work? What would stop you? |
| 5 | Close | Anything we didn't ask? Would you try a usability session? Thank them; explain withdrawal. |

## M2: Try the catalogue (45 minutes)

Pick four or five tasks that fit the participant's role. Don't help unless asked, or stuck for more than two minutes; note it if you do.

| Task | For | What to ask | Where the answer is |
|---|---|---|---|
{tasks}

For each task record: completed (yes, with help, no), time, the words they used, and where they hesitated. After each, ask "how sure are you of that answer?" (objective T3).

## M3: Accessibility session (60 minutes)

The participant uses their own device and set-up. Use tasks U1, U2 and U6, then ask them to explore freely for 10 minutes. Record each barrier with where it happened and its severity: blocks, slows or annoys. Barriers that block go into the backlog the same week.

## M5: Journey across three portals (60 minutes)

Use the six journeys in the [three-portal review]({PAGES}). Ask the participant to say when they notice they've moved to another portal, whether that helped, and whether they'd know how to get back.

## After every session

Within a day, fill in the [synthesis template](synthesis.md) with the session code, and delete your raw notes once the synthesis is agreed.
"""

def md_synthesis():
    return """# Synthesis template

One row per finding. Use session codes (R1-03), never names.

| Finding | Evidence (session codes) | How many sessions | Severity (blocks, slows, annoys) | Objective | Backlog issue |
|---|---|---|---|---|---|
| | | | | | |

## Round summary

- **Round and dates:**
- **Sessions:** how many, and how the minimums were met (totals only; hide counts under 5)
- **What we learned, by objective:**
- **What changes now:** the issues raised, with their labels
- **What we still don't know:**

Publish the summary in `docs/research/findings/` and link it from the catalogue's Help shape the catalogue view.
"""

def md_readme():
    return f"""# Research bundle

Everything to introduce the catalogue to teams and run user research, worked on in the open. Requirement R74. Shown in the catalogue under About, [Help shape the catalogue]({PAGES}#shape).

| File | For | What it is |
|---|---|---|
| [introducing-the-catalogue.md](introducing-the-catalogue.md) | Teams | One page on what the catalogue is and how to help |
| [invitation-email.md](invitation-email.md) | Whoever sends the invitation | The email, ready to send from your own account |
| [participant-information.md](participant-information.md) | Participants | What happens, what we keep, withdrawing |
| [consent-form.md](consent-form.md) | Participants and facilitators | Consent, part by part |
| [screener.md](screener.md) | Whoever arranges sessions | Questions to recruit a balanced group |
| [session-guides.md](session-guides.md) | Facilitators | Timed guides and tasks |
| [synthesis.md](synthesis.md) | Facilitators | Turning sessions into findings and backlog issues |
| [research-plan.md](research-plan.md) | Everyone | Why, who, how and when |
| [backlog-and-prioritisation.md](backlog-and-prioritisation.md) | Everyone | How ideas and findings become work, and the backlog |

**The email bundle.** `python3 -I build/tools/research_bundle.py` makes a zip of Word files from these, for sending by email. The invitation contains no address of ours: people reply to whoever sent it.

Generated by `build/dama/research.py`; edit that, not these files.
"""

# ---------- issue forms ----------
def yml_idea():
    return f"""name: Suggest an idea
description: Something the catalogue should do, show or change. Others can vote for it with a thumbs-up.
title: "[Idea] "
labels: ["idea"]
body:
  - type: markdown
    attributes:
      value: |
        Thank you. This is **public** and shows your GitHub username. Please don't include personal information or anything with a protective marking.

        Before you add one, [look at the ideas others have suggested]({IDEAS_LIVE}): if yours is there, give it a thumbs-up instead. The maintainers assess every idea in the open: see [how ideas become work]({REPO}/blob/main/docs/research/backlog-and-prioritisation.md).
  - type: textarea
    id: need
    attributes:
      label: What do you need to do?
      description: Describe the task and who it's for, rather than the solution. For example, "As a data leader, I need to see which of our projects use DCAT, so that I can report on it."
    validations: {{required: true}}
  - type: textarea
    id: why
    attributes:
      label: Why does it matter?
      description: Who is affected, how often, and what happens today without it.
  - type: dropdown
    id: role
    attributes:
      label: Which is closest to your role?
      options:
{chr(10).join("        - " + json.dumps(p['name']) for p in PERSONAS.values())}
        - Other
  - type: dropdown
    id: theme
    attributes:
      label: Which government priority does it help most? (optional)
      options:
{chr(10).join("        - " + json.dumps(s['id'] + ': ' + s['name']) for s in STRATEGY if not s.get('pending'))}
        - Not sure
"""

def yml_signup():
    return f"""name: Take part in user research
description: Tell us you'd like to take part. No personal details, please; we reply here to arrange it.
title: "[Research] I'd like to take part"
labels: ["research"]
body:
  - type: markdown
    attributes:
      value: |
        Thank you. This form is **public** and shows your GitHub username, so please **don't** give your name, email address or anything personal. We'll reply on this issue to arrange a time privately with you.

        If you were invited by email, you can reply to that email instead. Read [what happens and what we keep]({REPO}/blob/main/docs/research/participant-information.md).
  - type: checkboxes
    id: activities
    attributes:
      label: What would you like to do?
      options:
{chr(10).join("        - label: " + json.dumps(f"{m['name']} ({str(m['minutes']) + ' minutes' if m['minutes'] else 'any time'})") for m in METHODS if m['id'] in ('M1', 'M2', 'M3', 'M5'))}
  - type: dropdown
    id: org
    attributes:
      label: What kind of organisation do you work for?
      options:
{chr(10).join("        - " + json.dumps(g) for g, _ in QUOTAS[:6])}
        - Other
  - type: dropdown
    id: github
    attributes:
      label: How often do you use GitHub?
      options: ["Never, before today", "Sometimes", "Often"]
  - type: textarea
    id: support
    attributes:
      label: What would make taking part easier? (optional)
      description: For example captions, a British Sign Language interpreter, Welsh, breaks, or materials in advance.
  - type: checkboxes
    id: public
    attributes:
      label: Before you send
      options:
        - label: I understand this is public, and I haven't included my name or contact details.
          required: true
"""

SURVEY_Q = [
    ("role", "Which is closest to your role?", [p["name"] for p in PERSONAS.values()] + ["Other"]),
    ("org", "What kind of organisation do you work for?", [g for g, _ in QUOTAS[:6]] + ["Other"]),
    ("why", "What did you come to the catalogue to do?", ["Find whether something already exists", "See my organisation's code", "Find good practice in data or standards", "Find components or APIs to reuse", "Check legacy or risk", "Move a repository out of co-cddo", "Something else"]),
    ("found", "Did you find what you came for?", ["Yes", "Partly", "No"]),
    ("trust", "How much do you trust what it shows?", ["A lot", "Somewhat", "Not much", "Not sure"]),
    ("github", "How often do you use GitHub?", ["Never, before today", "Sometimes", "Often"]),
]

def yml_survey():
    qs = "\n".join(f"""  - type: dropdown
    id: {i}
    attributes:
      label: {json.dumps(q)}
      options:
{chr(10).join("        - " + json.dumps(o) for o in opts)}
    validations: {{required: true}}""" for i, q, opts in SURVEY_Q)
    return f"""name: "Survey: tell us about the catalogue"
description: About five minutes. Only totals are published, and counts under 5 are hidden.
title: "[Survey] The catalogue"
labels: ["survey-response"]
body:
  - type: markdown
    attributes:
      value: |
        User research. It helps us decide what to improve first. This is **public** and shows your GitHub username, so answer for yourself only if you're happy for that to be seen. Never include names, email addresses or other personal information.
{qs}
  - type: textarea
    id: missing
    attributes:
      label: What's missing, or what would you change? (optional)
"""

# ---------- checks ----------
def problems(items, docs):
    p = []
    for x in items:
        if x["id"] not in {i["id"] for i in RM["items"]}: p.append(f"{x['id']} isn't on the roadmap")
        if not set(x["themes"]) <= {s["id"] for s in STRATEGY if not s.get("pending")}: p.append(f"{x['id']} is mapped to an unknown or unpublished theme")
        if any(not 0 <= v <= 3 for v in x["scores"].values()): p.append(f"{x['id']} has a score out of range")
    for name, text in docs.items():
        if re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text): p.append(f"{name} contains an email address")
        if re.search(r"(?i)\b(mailto:|claude\.ai/artifact)", text): p.append(f"{name} links to an email address or a claude.ai artifact")
    for m in METHODS:
        if not set(m["objectives"]) <= {o[0] for o in OBJECTIVES}: p.append(f"{m['id']} answers an unknown objective")
    for pid in {t[1] for t in TASKS}:
        if pid not in PERSONAS: p.append(f"task persona {pid} isn't a catalogue persona")
    return p

def main():
    items = backlog()
    docs = {"README.md": md_readme(), "research-plan.md": md_plan(), "backlog-and-prioritisation.md": md_backlog(items), "introducing-the-catalogue.md": md_intro(),
            "invitation-email.md": md_email(), "participant-information.md": md_info(), "consent-form.md": md_consent(), "screener.md": md_screener(),
            "session-guides.md": md_guides(), "synthesis.md": md_synthesis()}
    forms = {"idea.yml": yml_idea(), "research-signup.yml": yml_signup(), "survey-catalogue.yml": yml_survey()}
    p = problems(items, {**docs, **forms})
    # negative tests: a planted email address, an unknown theme and an out-of-range score are each caught
    bad_items = [dict(items[0], themes=["G9"]), dict(items[0], scores=dict(items[0]["scores"], value=5))]
    neg = len(problems(bad_items, {"x.md": "write to some" + "one@example" + ".org"})) >= 3
    os.makedirs(os.path.join(ROOT, "docs", "research"), exist_ok=True)
    for n, t in docs.items(): open(os.path.join(ROOT, "docs", "research", n), "w").write(t)
    for n, t in forms.items(): open(os.path.join(ROOT, ".github", "ISSUE_TEMPLATE", n), "w").write(t)
    ideas_p = os.path.join(D, "ideas.json"); ideas = json.load(open(ideas_p)) if os.path.exists(ideas_p) else {"read": None, "items": []}
    out = dict(as_of=AS_OF, objectives=[dict(id=i, kind=k, q=q, how=h) for i, k, q, h in OBJECTIVES], methods=METHODS, quotas=QUOTAS, inclusion=INCLUSION, rounds=ROUNDS,
               tasks=[dict(id=i, persona=PERSONAS[p]["name"], text=t, path=path) for i, p, t, path in TASKS], strategy=STRATEGY, criteria=CRITERIA, capacity=CAPACITY,
               backlog=items, ideas=ideas, links=dict(signup=SIGNUP, idea=IDEA, survey=SURVEY, ideas_live=IDEAS_LIVE, contact=form("contact.yml", about="Feedback or a suggestion"),
               docs=REPO + "/tree/main/docs/research", plan=REPO + "/blob/main/docs/research/research-plan.md", prioritisation=REPO + "/blob/main/docs/research/backlog-and-prioritisation.md"))
    json.dump(out, open(os.path.join(D, "research.json"), "w"), indent=1, ensure_ascii=False)
    lines = [f"{'PASS' if not p and neg else 'FAIL'} C-RES-01 the research bundle, its forms and the backlog come from one source: {len(docs)} documents, {len(forms)} issue forms and {len(items)} assessed items, each mapped to a published strategy theme, with no email address and no claude.ai link; negative tests {'catch' if neg else 'MISS'} a planted address, an unknown theme and a score out of range [guards: R74]" + (f" (problems: {p})" if p else ""),
             f"{'PASS' if all(x['score'] == score(x['scores']) for x in items) and score(dict(value=3, reach=3, fit=3, feasible=3)) == 18 else 'FAIL'} C-RES-02 every backlog score is the published formula (value × 2 + reach + fit × 2 + feasibility, out of 18) [guards: R74]",
             f"{'PASS' if any(s.get('pending') for s in STRATEGY) and not any('D2' in x['themes'] for x in items) else 'FAIL'} C-RES-03 the forthcoming Strategic Data Roadmap is shown as forthcoming, and nothing is mapped to it until it is published [guards: R74]"]
    open(os.path.join(D, "research_checks.txt"), "w").write("\n".join(lines) + "\n"); print("\n".join(lines))
    return 0 if all(l.startswith("PASS") for l in lines) else 1

if __name__ == "__main__":
    raise SystemExit(main())
