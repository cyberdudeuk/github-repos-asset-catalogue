"""Join public-sector repositories to the datasets that link to them on data.gov.uk (RM-07).

  python3 -I build/catalogues/datagovuk.py           collect, then join
  python3 -I build/catalogues/datagovuk.py --join    join from the stored copy only
  python3 -I build/catalogues/datagovuk.py --self-test

data.gov.uk's catalogue (CKAN, https://ckan.publishing.service.gov.uk/api/action/package_search) is searched for every dataset
whose text or resources mention GitHub. A dataset is joined to a repository only when one of its own addresses names that
repository exactly: github.com/OWNER/REPO, raw.githubusercontent.com/OWNER/REPO or OWNER.github.io/REPO. A mention of GitHub
in passing, or of an account without a repository, is not a join. Each join records where the address was found (the
dataset's page address, a resource, or its description), so the page can say how it knows.

Kept per dataset: name, title, publisher, licence, modified date, the GitHub addresses and the resource formats. Contact
names and email addresses are not kept, and quoted text goes through the same cleaning as every other quoted record
(build/procure/clean.py). Writes sources/datagovuk.json.gz (the stored copy, with its SHA-256 in manifest.json) and
datasets.json (the join).
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request

H = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(H)
sys.path.insert(0, os.path.join(B, "refresh")); sys.path.insert(0, os.path.join(B, "procure"))
from common import long_date, read_json, write_json_gz
import clean

API = "https://ckan.publishing.service.gov.uk/api/action/package_search"
SITE = "https://www.data.gov.uk/dataset/"
QUERIES = ["github", '"github.com"', "notes:github", "res_url:*github*", "res_url:*githubusercontent*", "res_url:*github.io*", "url:*github*"]
UA = "github-repos-asset-catalogue-datasets"
# an address that names one repository; owner and repository as GitHub allows them
NAME = r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})"
REPO = r"[A-Za-z0-9._-]{1,100}"
ADDR = [re.compile(rf"(?i)\bgithub\.com/({NAME})/({REPO})"), re.compile(rf"(?i)\braw\.githubusercontent\.com/({NAME})/({REPO})"),
        re.compile(rf"(?i)\b({NAME})\.github\.io/({REPO})")]
NOT_REPO = {"orgs", "settings", "about", "features", "topics", "search", "marketplace", "sponsors", "apps", "login", "pricing", "collections", "enterprise"}


def repos_in(text):
    """Every (owner, repo) an address in the text names, lower case. Trailing punctuation and .git are dropped."""
    out = []
    for rx in ADDR:
        for m in rx.finditer(text or ""):
            owner, repo = m.group(1).lower(), re.sub(r"(\.git|[.,;:)]+)$", "", m.group(2)).lower()
            if owner in NOT_REPO or not repo or repo in ("", ".", ".."): continue
            if rx is ADDR[2] and repo in ("index.html", "index.htm"): continue
            out.append((owner, repo))
    return out


def get(params):
    url = API + "?" + urllib.parse.urlencode(params)
    for i in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=120) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:
            time.sleep(3 * 2 ** i)
    raise SystemExit("data.gov.uk did not answer: " + url)


def collect():
    seen = {}
    for q in QUERIES:
        start = 0
        while True:
            d = get(dict(q=q, rows=500, start=start))["result"]
            for p in d["results"]: seen[p["id"]] = p
            start += 500
            if start >= d["count"]: break
            time.sleep(0.5)
        print(q, d["count"], "found;", len(seen), "datasets so far", flush=True)
    keep = []
    for p in seen.values():
        res = p.get("resources") or []
        where = []
        for owner, repo in repos_in(p.get("url") or ""): where.append([owner, repo, "page"])
        for r in res:
            for owner, repo in repos_in(r.get("url") or ""): where.append([owner, repo, "resource"])
        for owner, repo in repos_in(p.get("notes") or ""): where.append([owner, repo, "description"])
        uniq = {}
        for owner, repo, w in where: uniq.setdefault((owner, repo), w)   # the first place found is the strongest: page, resource, description
        keep.append(dict(id=p["id"], name=p["name"], title=clean.text(p.get("title") or ""), publisher=(p.get("organization") or {}).get("title") or "",
                         licence=p.get("license_title") or "", modified=(p.get("metadata_modified") or "")[:10],
                         formats=sorted({(r.get("format") or "").strip().upper() for r in res if (r.get("format") or "").strip()}),
                         github=[[o, r, w] for (o, r), w in uniq.items()]))
    keep.sort(key=lambda k: k["name"])
    return keep


def known_repos():
    rows = read_json(os.path.join(B, "refresh", "sources", "repos.json.gz"))
    rec = read_json(os.path.join(B, "refresh", "sources", "reconcile.json.gz"))
    return {(r["owner"].lower(), r["name"].lower()): f"{r['owner']}/{r['name']}" for r in list(rows) + rec["carried"] if isinstance(r, dict) and r.get("owner") and r.get("name")}


def is_public(full):
    """Ask git, as the refresh does (V717-2): a repository that git can't read is not public."""
    try:
        return subprocess.run(["git", "ls-remote", f"https://github.com/{full}.git", "HEAD"], capture_output=True, timeout=60,
                              env=dict(os.environ, GIT_TERMINAL_PROMPT="0")).returncode == 0
    except Exception:
        return None


def check_missing(stored):
    """For an address naming a repository of a listed account that the catalogue doesn't hold, record whether it is public."""
    known = known_repos(); owners = {o for o, _ in known}
    miss = sorted({f"{o}/{r}" for d in stored["datasets"] for o, r, _ in d["github"] if (o, r) not in known and o in owners})
    stored["public"] = {m: is_public(m) for m in miss}
    return stored


STOP = {"of", "for", "the", "and", "&", "in", "on"}


def matches_publisher(owner, publisher):
    """An account is shown as a lead only when its name carries its publisher's own name, initials or first distinctive word.
    Anything else may be a person's account, and people's account names are not published (R54)."""
    o = re.sub(r"[^a-z0-9]", "", owner.lower())
    name = re.sub(r"\s*\(.*?\)", "", publisher).lower()
    words = [w for w in re.findall(r"[a-z0-9]+", name) if w not in STOP]
    if not words: return False
    whole, initials = "".join(words), "".join(w[0] for w in words)
    first = next((w for w in words if len(w) >= 5), "")
    return (len(whole) >= 4 and whole in o) or (len(initials) >= 3 and o.startswith(initials)) or (bool(first) and o.startswith(first))


def join(stored):
    known = known_repos(); owners = {o for o, _ in known}
    by_repo, unmatched, leads = {}, [], {}
    for d in stored["datasets"]:
        for owner, repo, where in d["github"]:
            k = known.get((owner, repo))
            if k: by_repo.setdefault(k, []).append([d["name"], where])
            elif owner in owners: unmatched.append([d["name"], f"{owner}/{repo}", stored.get("public", {}).get(f"{owner}/{repo}")])
            else:
                l = leads.setdefault(owner, dict(datasets=set(), publishers=set())); l["datasets"].add(d["name"]); l["publishers"].add(d["publisher"])
    D = {d["name"]: {x: d[x] for x in ("title", "publisher", "licence", "modified", "formats")} for d in stored["datasets"] if any(known.get((o, r)) for o, r, _ in d["github"])}
    return dict(source=SITE, read=stored["read"], searched=stored["searched"], datasets_read=len(stored["datasets"]),
                with_address=sum(1 for d in stored["datasets"] if d["github"]), joined_datasets=len(D), joined_repos=len(by_repo),
                repos={k: sorted(v) for k, v in sorted(by_repo.items())}, datasets=dict(sorted(D.items())), unmatched=sorted(unmatched),
                not_listed={o: dict(datasets=len(v["datasets"]), publishers=sorted(v["publishers"])) for o, v in sorted(leads.items()) if any(matches_publisher(o, p) for p in v["publishers"])},
                not_listed_withheld=sum(1 for o, v in leads.items() if not any(matches_publisher(o, p) for p in v["publishers"])))


def self_test():
    bad = []
    ok = repos_in("See https://github.com/alphagov/govuk-frontend.git, raw.githubusercontent.com/ONSdigital/eq-runner/main/x and https://co-cddo.github.io/data-standards/")
    if ok != [("alphagov", "govuk-frontend"), ("onsdigital", "eq-runner"), ("co-cddo", "data-standards")]: bad.append(f"addresses read wrongly: {ok}")
    for t in ("we use GitHub for this", "https://github.com/alphagov", "https://github.com/orgs/alphagov/people", "https://alphagov.github.io/", "https://github.com/settings/x"):
        if repos_in(t): bad.append(f"no repository named, but found one in {t!r}")
    for owner, pub in (("greater-london-authority", "Greater London Authority"), ("britishgeologicalsurvey", "British Geological Survey (BGS)"),
                       ("lbr-gis", "London Borough of Redbridge"), ("onsgeo", "Office for National Statistics"), ("tategallery", "Tate"), ("trafforddatalab", "Trafford Council")):
        if not matches_publisher(owner, pub): bad.append(f"{owner} should match its publisher {pub}")
    for owner, pub in (("janesmith", "British Geological Survey (BGS)"), ("kuangdai", "British Geological Survey (BGS)"), ("hanlab-ecol", "Environmental Information Data Centre"),
                       ("datamillfan", "Data Mill North")):
        if matches_publisher(owner, pub): bad.append(f"{owner} must not match {pub}: it may be a person")
    return bad


def save(src, stored):
    """The only way the stored copy is written, so its SHA-256 in the manifest always matches it (C-DS-01)."""
    write_json_gz(src, stored)
    man = os.path.join(H, "sources", "manifest.json")
    m = json.load(open(man)) if os.path.exists(man) else {}
    m["datagovuk"] = dict(source=API, read=stored["read"], datasets=len(stored["datasets"]), sha256=hashlib.sha256(open(src, "rb").read()).hexdigest())
    json.dump(m, open(man, "w"), indent=1)


def main():
    if "--self-test" in sys.argv:
        b = self_test(); print("ok" if not b else b); return 1 if b else 0
    src = os.path.join(H, "sources", "datagovuk.json.gz")
    if "--join" not in sys.argv:
        save(src, check_missing(dict(source=API, searched=QUERIES, read=time.strftime("%Y-%m-%d"), datasets=collect())))
    stored = read_json(src)
    if "public" not in stored:   # a copy collected before the check existed: check now and store it
        stored = check_missing(stored); save(src, stored)
    out = join(stored)
    checks = []
    def check(ok, cid, msg, guards): checks.append(("PASS " if ok else "FAIL ") + f"{cid} {msg}   [guards: {guards}]")
    man = json.load(open(os.path.join(H, "sources", "manifest.json")))
    check(hashlib.sha256(open(src, "rb").read()).hexdigest() == man["datagovuk"]["sha256"], "C-DS-01",
          f"the stored copy of data.gov.uk's datasets is the one read on {long_date(man['datagovuk']['read'])} (SHA-256 in sources/manifest.json)", "RM-07")
    st = self_test()
    check(not st, "C-DS-02", "a dataset joins a repository only when one of its own addresses names that repository; negative tests: a mention of GitHub, "
          "an account address, an organisation's people page, an account's own site and a settings page are each refused", "RM-07")
    known = known_repos(); kl = {v.lower() for v in known.values()}
    check(all(k.lower() in kl for k in out["repos"]) and out["joined_repos"] == len(out["repos"]), "C-DS-03",
          f"{out['joined_datasets']} datasets join {out['joined_repos']} repositories, every one in the catalogue; "
          f"{len(out['unmatched'])} addresses name a repository of a listed account that git can't read ({sum(1 for u in out['unmatched'] if u[2] is False)} no longer public)", "RM-07, V717-2")
    shown_ok = all(any(matches_publisher(o, p) for p in v["publishers"]) for o, v in out["not_listed"].items())
    check(shown_ok and not st, "C-DS-04", f"accounts not in the catalogue are shown only when their name carries their publisher's name ({len(out['not_listed'])} shown, "
          f"{out['not_listed_withheld']} withheld because they may be people's); negative tests refuse a personal name", "R54")
    leak = re.search(r"[A-Za-z0-9._%+-]+" + chr(64) + r"[A-Za-z0-9-]+\.[A-Za-z]{2,}", json.dumps(stored) + json.dumps(out))
    check(not leak, "C-DS-05", "no email address is kept from a dataset record", "contact by form only")
    json.dump(out, open(os.path.join(H, "datasets.json"), "w"), ensure_ascii=False, indent=0)
    open(os.path.join(H, "datasets_checks.txt"), "w").write("\n".join(checks) + "\n")
    print("\n".join(checks))
    print(f"{out['datasets_read']} datasets read, {out['with_address']} name a repository, {out['joined_datasets']} joined to {out['joined_repos']} repositories in the catalogue; {len(out['unmatched'])} name a repository of a listed account that the catalogue doesn't hold ({sum(1 for u in out['unmatched'] if u[2] is False)} no longer public); {len(out['not_listed']) + out['not_listed_withheld']} accounts not listed ({len(out['not_listed'])} shown, {out['not_listed_withheld']} may be people's and are withheld)")
    return 0 if all(c.startswith("PASS") for c in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
