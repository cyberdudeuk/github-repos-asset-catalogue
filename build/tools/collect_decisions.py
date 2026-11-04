"""Collect the decisions on proposed co-cddo destinations from GitHub issues (R72).

People record a decision with the issue form .github/ISSUE_TEMPLATE/move-decision.yml in the private companion
repository. The internal build workflow lists those issues with GitHub's own CLI and pipes them here:

    gh issue list --repo OWNER/REPO --label move-decision --state all --limit 1000 \
      --json number,body,createdAt,updatedAt,state,stateReason > issues.json
    python3 -I build/tools/collect_decisions.py issues.json build/inv/decisions.json

The output is build/inv/decisions.json in the companion repository's checkout, which the government edition embeds.
For each repository the most recently updated open or completed issue wins; an issue closed as "not planned" is
withdrawn. Only the repository, the decision, the destination, the note, the date and the issue number are kept:
never who wrote it. The page validates every decision again before showing it.
"""
import datetime as dt
import json
import re
import sys

STATES = {"Agree with the proposal": "agreed", "Change the destination": "changed", "Needs discussion": "discuss"}
NOTE_MAX = 2000
# The destinations, as the page and the issue form label them; the build checks all three agree (C-DEC-01)
GROUPS = ["Wave 1: shared dependencies", "Wave 2: active products", "Wave 3: low-activity keepers", "Owner decision (gds-dtx, alphagov or keep)",
          "Consolidate into another repository", "Already archived", "Archive in place", "Delete (empty or unmodified fork)"]


def fields(body):
    """Issue-form bodies are '### Label\\n\\nvalue' sections. Returns {label: value}; '_No response_' is empty."""
    out = {}
    for m in re.finditer(r"(?ms)^### (.+?)\s*\n(.*?)(?=^### |\Z)", body or ""):
        v = m.group(2).strip()
        out[m.group(1).strip()] = "" if v == "_No response_" else v
    return out


def collect(issues, repos, groups):
    """issues: gh issue list JSON; repos: names that exist; groups: destination labels as the form lists them.
    Returns (items, rejected): items is {repo: decision}, rejected counts issues that couldn't be read."""
    items, rejected = {}, 0
    for i in sorted(issues, key=lambda i: (i.get("updatedAt") or i.get("createdAt") or "", i.get("number") or 0)):
        f = fields(i.get("body"))
        repo = f.get("Repository", "").strip().removeprefix("co-cddo/").strip("` ")
        state = STATES.get(f.get("Your decision", "").strip())
        group = f.get("New destination", "").strip()
        if repo not in repos or not state or (state == "changed" and group not in groups) or not isinstance(i.get("number"), int):
            rejected += 1
            continue
        if i.get("state") == "CLOSED" and i.get("stateReason") == "NOT_PLANNED":
            items.pop(repo, None)    # withdrawn
            continue
        at = (i.get("updatedAt") or i.get("createdAt") or "")[:40]
        items[repo] = {"state": state, "group": group if state == "changed" else None, "note": f.get("Note", "")[:NOTE_MAX],
                       "at": at or None, "issue": i["number"]}
    return items, rejected


def self_test():
    """Negative tests: returns a list of problems (empty when the collector behaves)."""
    G = ["Wave 1: shared dependencies", "Archive in place"]
    body = lambda r, d, g="_No response_", n="_No response_": f"### Repository\n\n{r}\n\n### Your decision\n\n{d}\n\n### New destination\n\n{g}\n\n### Note\n\n{n}\n"
    iss = [
        {"number": 1, "body": body("alpha", "Agree with the proposal"), "updatedAt": "2026-11-01T10:00:00Z", "state": "OPEN"},
        {"number": 2, "body": body("alpha", "Change the destination", "Archive in place", "Owner asked"), "updatedAt": "2026-11-02T10:00:00Z", "state": "OPEN"},
        {"number": 3, "body": body("beta", "Change the destination", "Somewhere else"), "updatedAt": "2026-11-02T10:00:00Z", "state": "OPEN"},
        {"number": 4, "body": body("gamma", "Delete everything"), "updatedAt": "2026-11-02T10:00:00Z", "state": "OPEN"},
        {"number": 5, "body": body("nope", "Agree with the proposal"), "updatedAt": "2026-11-02T10:00:00Z", "state": "OPEN"},
        {"number": 6, "body": body("delta", "Needs discussion"), "updatedAt": "2026-11-01T10:00:00Z", "state": "OPEN"},
        {"number": 7, "body": body("delta", "Needs discussion"), "updatedAt": "2026-11-03T10:00:00Z", "state": "CLOSED", "stateReason": "NOT_PLANNED"},
        {"number": 8, "body": body("co-cddo/eps", "Needs discussion", n="x" * 3000), "updatedAt": "2026-11-03T10:00:00Z", "state": "OPEN", "author": {"login": "someone"}},
    ]
    items, rej = collect(iss, {"alpha", "beta", "gamma", "delta", "eps"}, G)
    bad = []
    if items.get("alpha", {}).get("issue") != 2 or items["alpha"]["group"] != "Archive in place": bad.append("the newest issue doesn't win")
    if "beta" in items or "gamma" in items or "nope" in items: bad.append("an unknown destination, decision or repository is accepted")
    if "delta" in items: bad.append("an issue closed as not planned isn't treated as withdrawn")
    if len(items.get("eps", {}).get("note", "")) != NOTE_MAX: bad.append("a long note isn't cut to the limit, or a co-cddo/ prefix isn't read")
    if "someone" in json.dumps(items): bad.append("who wrote the issue is kept")
    if rej != 3: bad.append(f"{rej} issues rejected, expected 3")
    return bad


def main(src, dst, repos, groups):
    issues = json.load(open(src))
    items, rejected = collect(issues, set(repos), groups)
    out = {"read": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "items": dict(sorted(items.items())), "rejected": rejected}
    with open(dst, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"{len(items)} decisions collected, {rejected} issues couldn't be read")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        p = self_test(); print("\n".join(p) or "ok"); sys.exit(1 if p else 0)
    if len(sys.argv) != 4:
        sys.exit("usage: collect_decisions.py ISSUES.json OUT.json DATA.json  (DATA.json: the internal build/inv/data.json, for the repository names)")
    base = json.load(open(sys.argv[3]))
    main(sys.argv[1], sys.argv[2], [r["repo"] for r in base["rows"]], GROUPS)
