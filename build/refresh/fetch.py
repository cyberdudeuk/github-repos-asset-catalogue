"""Step 1 of the refresh (R75): download the two public sources and record exactly what was read.

  python3 -I build/refresh/fetch.py

Writes, all committed so any build can be repeated from the repository alone:
  sources/repos.json.gz        the X-Gov open-source repo scraper's nightly repos.json (OGL), with personal names and email
                               addresses removed from descriptions (the manifest keeps the SHA-256 of the file as read)
  sources/org-mapping.csv      the public-body mapping from uk-public-sector-code-by-org (MIT), as read
  sources/manifest.json        URL, read date, size, SHA-256 and row count of each
Downloaded files are parsed as data only.
"""
import csv
import gzip
import hashlib
import io
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dama"))
from common import ASOF, H
import pii
import re

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


def clean(rows):
    """Personal names and email addresses quoted in descriptions are removed before the file is stored (R54, R69)."""
    n = 0
    for r in rows:
        d = r.get("description") if isinstance(r, dict) else None
        if not d: continue
        t, hits = pii.scrub(d); t = EMAIL.sub("[address removed]", t)
        if t != d: r["description"] = t; n += 1
    return n

SOURCES = [("repos.json", "https://www.uk-x-gov-software-community.org.uk/xgov-opensource-repo-scraper/repos.json"),
           ("org-mapping.csv", "https://raw.githubusercontent.com/chrishylanduk/uk-public-sector-code-by-org/main/public/data/org-mapping.csv")]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "github-repos-asset-catalogue-refresh"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def main():
    out = os.path.join(H, "sources"); os.makedirs(out, exist_ok=True)
    man = {}
    for name, url in SOURCES:
        b = get(url)
        if name.endswith(".json"):
            rows = json.loads(b)
            if not isinstance(rows, list) or len(rows) < 1000: sys.exit(f"{name}: expected a list of repositories, got {type(rows).__name__} of {len(rows)}")
            scrubbed = clean(rows)
            stored = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            with gzip.GzipFile(os.path.join(out, name + ".gz"), "wb", mtime=0) as f: f.write(stored)
            n = len(rows)
        else:
            rows = list(csv.DictReader(io.StringIO(b.decode("utf-8"))))
            if not rows or "github_account" not in rows[0]: sys.exit(f"{name}: no github_account column")
            open(os.path.join(out, name), "wb").write(b)
            n = len(rows)
        man[name] = dict(url=url, read=ASOF["ref"], bytes=len(b), sha256=hashlib.sha256(b).hexdigest(), rows=n)
        if name.endswith(".json"):
            man[name].update(stored_sha256=hashlib.sha256(stored).hexdigest(), descriptions_scrubbed=scrubbed,
                             note="sha256 is of the file as read; the stored copy has personal names and email addresses removed from descriptions")
        print(name, n, "rows")
    json.dump(man, open(os.path.join(out, "manifest.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
