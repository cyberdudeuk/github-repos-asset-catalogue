"""Check the catalogue against GitHub itself: every account's live repository list, and a sample of feature settings (7.9.1, R57, R58).

Input: gh_crawl.json, read on GitHub's own web pages by a signed-in person's browser session, read only (no API token, no
third-party feed). For each account in the catalogue it holds what GitHub listed on the account's repositories page:
how many repositories, how many archived, forks, with a description, with topics, with a licence, pushed in the last
90 and 365 days, and a fingerprint of the sorted lower-case names. Where the fingerprint differs from the catalogue's,
it holds the names GitHub lists that the catalogue lacks (added) and the names the catalogue holds that GitHub no longer
lists (removed: deleted, renamed, moved or made private).
It also holds a stratified random sample of live, non-fork repositories, with the tabs GitHub showed on each repository's
page (Issues, Projects, Wiki, Discussions). A tab is shown when the feature is switched on, as seen by a signed-in
person who isn't a member of the account; a page that couldn't be read is unknown, not 'off'.
Writes ghverify.json (for the page) and ghverify_checks.txt. Run with python3 -I. Exit code 1 if a check fails.
"""
import json, math, os, sys, collections
S = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(S)
FEATURES = [("issues", "Issues"), ("projects", "Projects"), ("wiki", "Wiki"), ("discussions", "Discussions")]
F = ["account", "kind", "n", "archived", "forks", "desc", "topics", "licence", "p90", "p365", "fp"]

PUBLIC = ("P", "A", "T")   # visibility as GitHub labels it: Public, Public archive, Public template

def public_only(rows):
    return [r[0] for r in rows if r[-1] in PUBLIC]

def human(d):
    import datetime as _d
    x = _d.date.fromisoformat(d); return f"{x.day} {x:%B %Y}"

def count_gaps(cnt, orgs):
    """Accounts where the rows read don't equal GitHub's own repository count (both include repositories only members see)."""
    return [a for a in orgs if a not in cnt or cnt[a][0] != cnt[a][1]]

def fnv(s):
    h = 2166136261
    for b in s.encode("utf-8"): h = ((h ^ b) * 16777619) & 0xFFFFFFFF
    return h

def expected():
    X = json.load(open(os.path.join(R, "xgov", "xgov.json"))); C = json.load(open(os.path.join(R, "catalogue", "catalogue.json")))
    g = collections.defaultdict(set)
    for r in X["rows"]: g[r["o"]].add(r["n"])
    for a in C["cat"]:
        o = dict(zip(C["cf"], a)); g[C["orgs"][o["oi"]]["org"]].add(o["n"])
    meta = {o["org"]: o for o in C["orgs"]}
    cd = os.path.join(S, "cdot.json")   # crown dependency and overseas territory accounts, verified over git (cdot.py)
    if os.path.exists(cd):
        for a in json.load(open(cd))["accounts"]:
            if a.get("in_catalogue"):
                g[a["account"]] |= {r["name"] for r in a["repos"]}; meta.setdefault(a["account"], {"sector": "Crown dependencies" if "rown" in a.get("kind", "") else "Overseas territories"})
    return g, meta

def reconcile(acc, exp_names, live):
    """One account: does what GitHub lists match the catalogue, and if not, do the added and removed names explain it?"""
    exp = sorted(x.lower() for x in exp_names); efp = fnv("\n".join(exp))
    if live["fp"] == efp and live["n"] == len(exp): return "same", True
    add, rem = live.get("added"), live.get("removed")
    if add is None or rem is None: return "differs, not explained", False
    explained = len(exp) - len(rem) + len(add) == live["n"] and all(r.lower() in exp for r in rem) and not any(a.lower() in exp for a in add)
    return ("differs, explained" if explained else "differs, not explained"), explained

def mulberry32(seed):
    a = seed & 0xFFFFFFFF
    def nxt():
        nonlocal a
        a = (a + 0x6D2B79F5) & 0xFFFFFFFF; t = a
        t = ((t ^ (t >> 15)) * (1 | t)) & 0xFFFFFFFF
        t = (t + (((t ^ (t >> 7)) * (61 | t)) & 0xFFFFFFFF) ^ t) & 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296
    return nxt

def draw(pop, alloc, seed, order):
    """The sample, redrawn from the seed: each sector's live non-fork repositories sorted, shuffled (Fisher-Yates), first n taken."""
    rnd = mulberry32(seed); out = []
    for s in order:
        L = sorted(pop.get(s, []), key=str.lower)
        for i in range(len(L) - 1, 0, -1):
            j = int(rnd() * (i + 1)); L[i], L[j] = L[j], L[i]
        out += [[k, s] for k in L[:alloc.get(s, 0)]]
    return out

def wilson(y, n, z=1.96):
    if not n: return (0, 0)
    p = y / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round((c - h) / d * 100, 1), round((c + h) / d * 100, 1))

def feature_of(tabs):
    """The feature settings a repository page shows. An empty or unread page is unknown (None), never 'all off'."""
    if not tabs or "code" not in tabs: return None
    return {k: k in tabs for k, _ in FEATURES}

def need(ok, cid, msg, lines, fails, guards):
    lines.append(f"{'PASS' if ok else 'FAIL'} {cid} {msg} [guards: {guards}]"); print(lines[-1])
    if not ok: fails.append(cid)

if __name__ == "__main__":
    G = json.load(open(os.path.join(S, "gh_crawl.json"))); g, orgs = expected(); lines, fails = [], []
    accs = {r[0]: dict(zip(F, r[:len(F)]), added=r[len(F)] if len(r) > len(F) else None, removed=r[len(F) + 1] if len(r) > len(F) + 1 else None) for r in G["accounts"]}
    want = G["catalogue_accounts"]
    unread = [a for a in want if a not in accs or accs[a]["kind"] == "error"]
    cnt = G["github_counts"]; short = count_gaps(cnt, [a for a in want if accs.get(a, {}).get("kind") == "org"])
    need(not unread and not short and len(want) >= 200, "C-GHV-01", f"all {len(want)} GitHub accounts in the catalogue were read directly from GitHub on {human(G['read'])} and GitHub's own repository count matched for each ({sum(1 for a in accs.values() if a['kind'] == 'gone')} no longer exist: GitHub answers 'not found' for the account itself; unread: {unread}; count differs: {short})", lines, fails, "R57")
    out, status = [], collections.Counter()
    for a in want:
        if a not in accs: continue
        v = accs[a]; st, ok = reconcile(a, g.get(a, ()), v); status[st] += 1
        if not ok: fails.append("C-GHV-02:" + a)
        out.append({**{k: v[k] for k in F}, "expected": len(g.get(a, ())), "status": st, "added": v["added"] or [], "removed": v["removed"] or [], "sector": orgs.get(a, {}).get("sector", "")})
    need(status["differs, not explained"] == 0, "C-GHV-02", f"every account reconciles with GitHub: {status['same']} list exactly the same repositories, {status['differs, explained']} differ and every difference is named (repositories added on GitHub since the catalogue was built, or no longer listed there), {status['differs, not explained']} unexplained", lines, fails, "R57")
    need(count_gaps({"a": [31, 31], "b": [60, 30]}, ["a", "b", "c"]) == ["b", "c"], "C-GHV-01n", "negative test: an account whose pages stopped early (30 read of 60), or that was never counted, is caught", lines, fails, "R57")
    t1 = reconcile("test", {"alpha", "beta"}, {"n": 2, "fp": fnv("alpha\ngamma"), "added": None, "removed": None})
    t2 = reconcile("test", {"alpha", "beta"}, {"n": 2, "fp": fnv("alpha\ngamma"), "added": ["gamma"], "removed": ["beta"]})
    t3 = reconcile("test", {"alpha", "beta"}, {"n": 3, "fp": 1, "added": ["gamma"], "removed": ["beta"]})
    need(t1 == ("differs, not explained", False) and t2 == ("differs, explained", True) and t3[1] is False, "C-GHV-02n", "negative tests: a renamed repository with no names given is caught as unexplained, the same change with its names reconciles, and names that don't add up to GitHub's count are caught", lines, fails, "R57")

    # only public repositories: a member's session also sees internal and private ones, which must never reach the catalogue
    RW = json.load(open(os.path.join(S, "gh_crawl_rows.json")))
    vis = collections.Counter(r[-1] for v in RW.values() for r in v["r"])
    names = {(a + "/" + r[0]).lower() for a, v in RW.items() for r in v["r"]}
    leak = [n for a in out for n in a["added"] if (a["account"] + "/" + n).lower() not in names] + [n for n in G["renamed"].values() if n.split("/")[0] in RW and n.lower() not in names]
    need(set(vis) <= set(PUBLIC) and not leak and sum(vis.values()) == sum(a["n"] for a in out), "C-GHV-03", f"only public repositories are used: {sum(vis.values()):,} rows, all public, plain archived or template ({dict(vis)}); {G['non_public_left_out']} repositories that only members can see were left out before anything was stored, and every name shown is one of the public rows (not public: {leak[:3]})", lines, fails, "R57")
    need(public_only([["x", 0, 0, 0, 0, "", "", "", 0, 0, 0, "I"], ["y", 0, 0, 0, 0, "", "", "", 0, 0, 0, "P"], ["z", 0, 0, 0, 0, "", "", "", 0, 0, 0, "X"], ["t", 0, 0, 0, 0, "", "", "", 0, 0, 0, "T"]]) == ["y", "t"], "C-GHV-03n", "negative test: internal and private rows are dropped by the filter, public and template rows are kept", lines, fails, "R57")

    # feature settings from a stratified random sample
    smp = G["sample"]; rows = [(k, sec, feature_of(t)) for k, sec, t in smp["rows"]]; known = [r for r in rows if r[2] is not None]
    by = collections.Counter(r[1] for r in known); secs = sorted({r[1] for r in rows})
    est = []
    for k, label in FEATURES:
        y = sum(1 for r in known if r[2][k]); lo, hi = wilson(y, len(known))
        # weighted by each sector's share of live non-fork repositories, so large sectors don't swamp small ones
        W = smp["population"]; tot = sum(W.values())
        wp = sum(W[s] / tot * (sum(1 for r in known if r[1] == s and r[2][k]) / by[s]) for s in W if by[s])
        est.append(dict(k=k, label=label, yes=y, n=len(known), pct=round(y / len(known) * 100, 1) if known else 0, lo=lo, hi=hi, weighted=round(wp * 100, 1),
                        by={s: [sum(1 for r in known if r[1] == s and r[2][k]), by[s]] for s in secs}))
    need(len(known) >= 300 and all(by[s] >= min(10, smp["population"][s]) for s in secs), "C-FEAT-02", f"feature settings estimated from a stratified random sample of {len(known)} live, non-fork repositories ({len(rows) - len(known)} pages unread, left out), at least 10 in each of {len(secs)} sectors or the whole sector where it has fewer; shown as estimates with 95% intervals: " + "; ".join(f"{e['label']} {e['pct']}% ({e['lo']} to {e['hi']})" for e in est), lines, fails, "R58")
    # the sample can be redrawn from the seed and the live lists, so nobody has to take the choice on trust
    R = RW; sec = {a: (orgs.get(a) or {}).get("sector", "") for a in R}
    pop = collections.defaultdict(list)
    for a, v in R.items():
        for r in v["r"]:
            if not r[1] and not r[2] and a + "/" + r[0] not in smp.get("added_after_draw", []): pop[sec[a]].append(a + "/" + r[0])
    redraw = draw(pop, smp["alloc"], smp["seed"], smp["order"])
    need(redraw == [r[:2] for r in smp["rows"]] and {s: len(v) for s, v in pop.items()} == smp["population"], "C-FEAT-03", f"the sample is reproducible: redrawn here from seed {smp['seed']} and GitHub's live repository lists, it picks exactly the same {len(redraw)} repositories, and each sector's population matches (leaving out {len(smp.get('added_after_draw', []))} repository found on a later re-read, after the sample was drawn)", lines, fails, "R58")
    alt = draw(pop, smp["alloc"], smp["seed"] + 1, smp["order"])
    need(alt != redraw, "C-FEAT-03n", "negative test: a different seed draws a different sample, so the reproducibility check can tell them apart", lines, fails, "R58")
    need(feature_of([]) is None and feature_of(["issues"]) is None and feature_of(["code", "issues", "wiki"]) == {"issues": True, "projects": False, "wiki": True, "discussions": False}, "C-FEAT-02n", "negative tests: a page that couldn't be read, or lacks the Code tab, counts as unknown rather than 'switched off'; a page with Issues and Wiki tabs reads as exactly those two", lines, fails, "R58")
    tot = lambda f: sum(a[f] for a in out)
    json.dump(dict(read=G["read"], method=G["method"], accounts=out, status=dict(status), renamed=G["renamed"], non_public_left_out=G["non_public_left_out"],
                   totals={f: tot(f) for f in ("n", "archived", "forks", "desc", "topics", "licence", "p90", "p365", "expected")},
                   sample=dict(read=G["read"], method=smp["method"], seed=smp["seed"], n=len(known), unread=len(rows) - len(known), population=smp["population"], est=est)),
              open(os.path.join(S, "ghverify.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    open(os.path.join(S, "ghverify_checks.txt"), "w").write("\n".join(lines) + "\n")
    sys.exit(1 if fails else 0)
