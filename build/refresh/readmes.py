"""Step 4 of the refresh (R75): read each repository's README, so tooling can be matched against what a repository says it does.

  python3 -I build/refresh/readmes.py [--workers 16] [--cache DIR]

Reads https://raw.githubusercontent.com/<owner>/<repo>/HEAD/<name> for the usual README names, for every repository in the
refresh that is not archived. Texts stay in the cache (outside the repository), never committed: only evidence snippets
derived from them, with email addresses removed, reach the catalogue. Texts are read as data; nothing is rendered or run.
"""
import concurrent.futures as cf
import hashlib
import os
import sys
import tempfile
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import H, read_json

NAMES = ["README.md", "readme.md", "Readme.md", "README.rst", "README", "README.txt", "README.markdown"]
MAX = 40000


def key(cache, o, n):
    return os.path.join(cache, hashlib.sha256(f"{o}/{n}".lower().encode()).hexdigest()[:24] + ".txt")


def fetch(o, n):
    for nm in NAMES:
        url = f"https://raw.githubusercontent.com/{o}/{n}/HEAD/{nm}"
        for _ in range(3):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "github-repos-asset-catalogue-refresh"}), timeout=30) as r:
                    return r.read(MAX).decode("utf-8", "replace")
            except urllib.error.HTTPError as e:
                if e.code == 404: break
                if e.code == 429: __import__("time").sleep(20)
            except Exception:
                __import__("time").sleep(2)
    return ""


def repos():
    new = read_json(os.path.join(H, "sources", "repos.json.gz")); rec = read_json(os.path.join(H, "sources", "reconcile.json.gz"))
    seen, out = set(), []
    for r in list(new) + rec["carried"]:
        if not isinstance(r, dict) or not r.get("owner") or not r.get("name") or r.get("archived"): continue
        k = (r["owner"].lower(), r["name"].lower())
        if k not in seen: seen.add(k); out.append((r["owner"], r["name"]))
    return out


def text(cache, o, n):
    p = key(cache, o, n)
    return open(p, encoding="utf-8", errors="replace").read() if os.path.exists(p) else None


def main():
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 16
    cache = sys.argv[sys.argv.index("--cache") + 1] if "--cache" in sys.argv else os.path.join(tempfile.gettempdir(), "ghrac-readme-cache")
    os.makedirs(cache, exist_ok=True)
    R = [(o, n) for o, n in repos() if not os.path.exists(key(cache, o, n))]
    print(len(R), "READMEs to read", flush=True)

    def job(o, n):
        t = fetch(o, n); open(key(cache, o, n), "w", encoding="utf-8").write(t); return bool(t)
    got = 0
    with cf.ThreadPoolExecutor(workers) as ex:
        for i, f in enumerate(cf.as_completed([ex.submit(job, o, n) for o, n in R]), 1):
            got += f.result()
            if i % 1000 == 0: print(i, "read,", got, "with a README", flush=True)
    print("done:", got, "of", len(R), "have a README")


if __name__ == "__main__":
    main()
