"""Where the work around each repository happens beyond GitHub: Slack (7.10, R59).

Much of the conversation about public code happens 'behind closed doors' in chat and documents rather than in GitHub
issues and discussions. This measures it, as aggregates only, from what one signed-in person can see:
  - Slack: the UK Government Digital and GDS workspaces, searched for 'github <account>' for every account in the
    catalogue, keeping only messages that link to github.com/<account>/<repository>;
  - another collaboration platform: the workspace, searched for each account's github.com address (collab_drive.json).
What is kept (decided by the repository owner, 1 November 2026): per repository, message and document counts, the
first and last month mentioned, the workspace, keyword categories (incident, release, security, migration, support,
dependency, review) and the names of PUBLIC channels only. Private channels, group and direct messages count towards
the totals but are never named. No message text, no document titles, no people's names or user IDs are stored, and
only public repositories (as listed by GitHub on the check against GitHub) are kept.
Input: collab_slack_raw.json (scratch, not committed) or collab_slack.json; collab_drive.json; gh_crawl_rows.json.
Writes collab_slack.json (aggregates), collab.json (for the page) and collab_checks.txt. Run with python3 -I.
"""
import collections, json, os, re, sys
S = os.path.dirname(os.path.abspath(__file__))
CATS = ["incident", "release", "security", "migration", "support", "dependency", "review"]
WS = {"ukgovernmentdigital": "UK Government Digital", "gds": "GDS"}
CRITICAL = {"incident", "release", "security"}
FEED = re.compile(r"(notification|(?<!emergency-)alert|alarm|feed|activity|-prs?$|-prs?-|-github$|audit|deploy|-release|-releases|ci-|-ci$|bot\b|dependabot|dependencies)", re.I)   # automated channels, judged from the name   # signals that a live service leans on the repository

def public_names():
    R = json.load(open(os.path.join(S, "gh_crawl_rows.json")))
    return {a: {r[0].lower(): r[0] for r in v["r"]} for a, v in R.items()}

def aggregate(raw, pub):
    """raw: {"ws|account": {"total", "capped", "hits": [[repos], chan_id, private, chan_name, ext_shared, "YYYY-MM", [cats], msg_id]}}.
    Returns per-repository aggregates. Messages are de-duplicated by id within a workspace; non-public repositories dropped."""
    repos, seen, dropped = {}, set(), 0
    chans = collections.defaultdict(lambda: {"name": "", "private": 0, "msgs": 0, "repos": set(), "ws": "", "shared": 0})
    for key, rec in raw.items():
        if key.startswith("__"): continue
        ws, acc = key.split("|", 1)
        names = pub.get(acc, {})
        for repos_l, cid, priv, cname, ext, month, cats, mid in rec["hits"]:
            if (ws, mid) in seen: continue
            seen.add((ws, mid))
            for rl in repos_l:
                if rl not in names: dropped += 1; continue
                k = acc + "/" + names[rl]
                r = repos.setdefault(k, {"msgs": 0, "ws": collections.Counter(), "first": month, "last": month, "cats": collections.Counter(), "pub": collections.Counter(), "private_msgs": 0, "channels": set()})
                r["msgs"] += 1; r["ws"][ws] += 1; r["first"] = min(r["first"], month); r["last"] = max(r["last"], month)
                for c in cats: r["cats"][c] += 1
                r["channels"].add((ws, cid))
                if priv: r["private_msgs"] += 1
                else: r["pub"][ws + "|" + cname] += 1
                ch = chans[(ws, cid)]; ch.update(name="" if priv else cname, private=priv, ws=ws, shared=ext); ch["msgs"] += 1; ch["repos"].add(k)
    return repos, chans, dropped

DESCRIBED = {"method", "source"}   # this repository's own descriptions of how the data was gathered, not gathered text

def safe(obj):
    """Every string in the stored aggregates must be a known kind of value: no free text, ids, user ids or emails."""
    bad = []
    def walk(o, path):
        if isinstance(o, dict): [walk(v, path + [str(k)]) for k, v in o.items() if k not in DESCRIBED] + [walk(k, path + ["key"]) for k in o]
        elif isinstance(o, list): [walk(v, path) for v in o]
        elif isinstance(o, str):
            if "@" in o or re.search(r"\bU[A-Z0-9]{8,}\b", o) or re.search(r"\s", o) and len(o) > 60: bad.append("/".join(path[-3:]) + ": " + o[:40])
    walk(obj, []); return bad

def need(ok, cid, msg, lines, fails):
    lines.append(f"{'PASS' if ok else 'FAIL'} {cid} {msg} [guards: R59]"); print(lines[-1])
    if not ok: fails.append(cid)

if __name__ == "__main__":
    pub = public_names(); lines, fails = [], []
    rawp, aggp = os.path.join(S, "collab_slack_raw.json"), os.path.join(S, "collab_slack.json")
    if os.path.exists(rawp):
        raw = json.load(open(rawp)); repos, chans, dropped = aggregate(raw, pub)
        meta = raw.get("__meta__", {}) if isinstance(raw, dict) else {}
        slack = dict(read=raw["__read__"], method=raw["__method__"], searched={k: {"total": v["total"], "capped": v["capped"]} for k, v in raw.items() if not k.startswith("__")}, dropped_non_public=dropped, privacy=raw.get("__privacy__", {}),
                     repos={k: {"msgs": r["msgs"], "ws": dict(r["ws"]), "first": r["first"], "last": r["last"], "cats": dict(r["cats"]), "public_channels": {c: n for c, n in r["pub"].items()}, "private_msgs": r["private_msgs"], "channels": len(r["channels"])} for k, r in repos.items()},
                     channels=[{"ws": c["ws"], "name": c["name"], "private": c["private"], "feed": 1 if c["name"] and FEED.search(c["name"]) else 0, "shared": c["shared"], "msgs": c["msgs"], "repos": len(c["repos"]), "top": sorted(c["repos"], key=lambda k: -repos[k]["msgs"])[:5] if not c["private"] else []} for c in chans.values()])
        json.dump(slack, open(aggp, "w"), ensure_ascii=False, separators=(",", ":"))
    slack = json.load(open(aggp)); drive = json.load(open(os.path.join(S, "collab_drive.json")))
    # privacy: the stored Slack aggregates name no private channel, hold no text, user ids or emails, and only public repositories
    priv_named = [c for c in slack["channels"] if c["private"] and c["name"]]
    nonpub = [k for k in slack["repos"] if k.split("/", 1)[1].lower() not in pub.get(k.split("/", 1)[0], {})]
    pv = slack.get("privacy", {}); pv_ok = pv.get("checked", 0) >= len(slack["channels"]) and pv.get("private", 1) == sum(1 for c in slack["channels"] if c["private"])
    need(not priv_named and not nonpub and pv_ok and not safe(slack) and not safe(drive), "C-CLB-01", f"Slack aggregates hold no message text, document titles, names, user ids or emails; all {pv.get('checked')} channels in the results were checked with Slack itself, including the {len(slack['channels'])} kept ({pv.get('private')} private, {pv.get('ext_shared')} shared with other organisations), and any private channel or conversation is counted but never named; only public repositories are kept ({slack['dropped_non_public']} links to other repositories dropped)", lines, fails)
    t_raw = {"gds|alphagov": {"total": 3, "capped": False, "hits": [[["govuk-frontend"], "C1", 1, "secret-team", 0, "2026-10", ["incident"], "m1"], [["govuk-frontend", "internal-thing"], "C2", 0, "govuk", 0, "2026-09", [], "m2"], [["govuk-frontend"], "C1", 1, "secret-team", 0, "2026-10", ["incident"], "m1"]]}}
    tr, tc, td = aggregate(t_raw, {"alphagov": {"govuk-frontend": "govuk-frontend"}})
    neg = tr["alphagov/govuk-frontend"]["msgs"] == 2 and td == 1 and all(not c["name"] for c in tc.values() if c["private"]) and safe({"x": "someone@example.com"}) and safe({"u": "U0123456789"}) and not safe({"method": "a long description of how this was gathered, which is this repository's own text"})
    feed_ok = all(bool(FEED.search(n)) == want for n, want in [("govuk-forms-deployment-notifications", True), ("di-face-to-face-prs", True), ("govuk-once-flex-release", True), ("emergency-alerts-support", False), ("github-enterprise-management", False), ("govuk-forms-tech", False), ("platops-help", False)])
    need(feed_ok, "C-CLB-03", "channels named as automated feeds (notifications, alerts, pull request and deploy feeds) are told apart from conversation: 3 feed names and 4 conversation names, including 'emergency-alerts-support', are classed correctly", lines, fails)
    need(neg, "C-CLB-01n", "negative tests: a repeated message counts once, a private channel's name is dropped, a link to a repository that isn't public is dropped, and an email address or a Slack user id in the output is caught", lines, fails)
    # reconciliation: per-workspace message counts add up for every repository
    rec_bad = [k for k, r in slack["repos"].items() if sum(r["ws"].values()) != r["msgs"] or sum(r["public_channels"].values()) + r["private_msgs"] != r["msgs"]]
    need(not rec_bad and len(slack["repos"]) > 0, "C-CLB-02", f"{len(slack['repos']):,} repositories linked from Slack; for each, messages by workspace and by public or private channel add up to its total", lines, fails)
    # the page's view of it
    also = [dict(ws="UK Government API and Data Exchange Community", searched="github, and github.com, in Slack's own search box, 1 November 2026", links=0, note="No message in its searchable history links to GitHub; a control search for 'api' returned only 7 messages, so the history Slack lets you search there is short.")]
    out = dict(read=slack["read"], also=also, slack=dict(read=slack["read"], method=slack["method"], ws=WS, repos=slack["repos"], channels=[c for c in slack["channels"]], searched=slack["searched"]),
               drive=dict(read=drive["read"], source=drive["source"], accounts={a: {k: v for k, v in x.items() if k in ("docs", "by_type", "by_year", "repos")} for a, x in drive["accounts"].items() if x.get("docs")}, totals=drive["totals"], method=drive.get("method", {})),
               cats=CATS, critical=sorted(CRITICAL))
    json.dump(out, open(os.path.join(S, "collab.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    open(os.path.join(S, "collab_checks.txt"), "w").write("\n".join(lines) + "\n")
    sys.exit(1 if fails else 0)
