"""Collect GitHub feature settings for every repository in the catalogue (R49).

Reads which accounts to cover from build/xgov/xgov.json and build/catalogue/catalogue.json, then asks GitHub's GraphQL API,
100 repositories a page, whether Issues, Projects, Wiki and Discussions are switched on, and whether a homepage is set.
Writes build/dama/repo_features.json, which the build picks up so the analytics panel fills in by itself.
Needs a token in GITHUB_TOKEN with read access to public repositories (a GitHub Actions token is enough).
Public data only. It never writes to GitHub. Run: python3 -I build/tools/collect_features.py [--accounts a,b] [--dry-run FILE]
--dry-run FILE parses a saved GraphQL response instead of calling GitHub, which is how the parser is tested.
"""
import datetime as dt, json, os, sys, time, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
Q = """query($login:String!,$after:String){repositoryOwner(login:$login){repositories(first:100,after:$after,privacy:PUBLIC){
 pageInfo{hasNextPage endCursor} nodes{name isArchived hasIssuesEnabled hasProjectsEnabled hasWikiEnabled hasDiscussionsEnabled homepageUrl}}}}"""

def parse(resp, login):
    """One GraphQL page -> ({repo_key: [issues, projects, wiki, discussions, homepage]}, next_cursor or None)."""
    owner = (resp.get("data") or {}).get("repositoryOwner")
    if not owner: return {}, None
    r = owner["repositories"]; out = {}
    for n in r["nodes"]:
        out[f"{login}/{n['name']}"] = {"issues": bool(n["hasIssuesEnabled"]), "projects": bool(n["hasProjectsEnabled"]), "wiki": bool(n["hasWikiEnabled"]), "discussions": bool(n["hasDiscussionsEnabled"]), "homepage": bool(n.get("homepageUrl")), "archived": bool(n["isArchived"])}
    return out, r["pageInfo"]["endCursor"] if r["pageInfo"]["hasNextPage"] else None

def call(login, after, token):
    body = json.dumps({"query": Q, "variables": {"login": login, "after": after}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=body, headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "ghrac-collect-features"})
    with urllib.request.urlopen(req, timeout=60) as f: return json.load(f)

def accounts():
    X = json.load(open(os.path.join(ROOT, "build", "xgov", "xgov.json"))); C = json.load(open(os.path.join(ROOT, "build", "catalogue", "catalogue.json")))
    return sorted({o["org"] for o in X["orgs"]} | {o["org"] for o in C["orgs"]})

def main(argv):
    if "--dry-run" in argv:
        out, cur = parse(json.load(open(argv[argv.index("--dry-run") + 1])), "example"); print(json.dumps(out, indent=1), "next:", cur); return 0
    token = os.environ.get("GITHUB_TOKEN")
    if not token: print("Set GITHUB_TOKEN to a token that can read public repositories."); return 2
    accs = argv[argv.index("--accounts") + 1].split(",") if "--accounts" in argv else accounts()
    repos, failed = {}, []
    for a in accs:
        after = None
        while True:
            try: resp = call(a, after, token)
            except Exception as e: failed.append(f"{a}: {e}"); break
            page, after = parse(resp, a); repos.update(page)
            if not after: break
            time.sleep(0.5)
    out = {"collected": dt.date.today().isoformat(), "source": "GitHub GraphQL API, public repositories", "accounts": len(accs), "failed": failed, "repos": repos}
    json.dump(out, open(os.path.join(ROOT, "build", "dama", "repo_features.json"), "w"), separators=(",", ":"))
    print(f"{len(repos)} repositories from {len(accs)} accounts; {len(failed)} accounts failed")
    return 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
