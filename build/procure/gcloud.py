"""Collect G-Cloud service listings that name each tool in the tooling register (R76).

  python3 -I build/procure/gcloud.py

Searches the Digital Marketplace G-Cloud catalogue (https://www.applytosupply.digitalmarketplace.service.gov.uk/g-cloud/search)
for each tool's name, reads every results page, and keeps a listing only when its title or summary matches the tool's own
text pattern. Keeps: service id and address, title, supplier, summary, lot and framework. The pages are parsed as text only.
Writes sources/gcloud.json.gz.
"""
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(H), "refresh")); sys.path.insert(0, os.path.join(os.path.dirname(H), "dama"))
from common import ASOF, write_json_gz
from tools import TOOLS, text_rx

BASE = "https://www.applytosupply.digitalmarketplace.service.gov.uk"
ITEM = re.compile(r'<li class="app-search-result">(.*?)</li>\s*(?=<li class="app-search-result">|</ul>\s*</div>)', re.S)
TAG = re.compile(r"<[^>]+>")


def get(url):
    for i in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "github-repos-asset-catalogue-procurement"}), timeout=90) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:
            time.sleep(3 * 2 ** i)
    return ""


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(TAG.sub(" ", s))).strip()


def parse(page):
    out = []
    for m in ITEM.finditer(page):
        b = m.group(1)
        a = re.search(r'href="(/g-cloud/services/(\d+))">(.*?)</a>', b, re.S)
        if not a: continue
        ps = re.findall(r'<p class="govuk-body[^"]*">(.*?)</p>', b, re.S)
        tags = [clean(t) for t in re.findall(r'<li class="govuk-!-display-inline[^"]*">(.*?)</li>', b, re.S)]
        out.append(dict(id=a.group(2), url=BASE + a.group(1), title=clean(a.group(3)), supplier=clean(ps[0]) if ps else "", summary=clean(ps[1]) if len(ps) > 1 else "",
                        lot=tags[0] if tags else "", framework=tags[1] if len(tags) > 1 else ""))
    return out


def query_for(t):
    return re.sub(r"\s*\(.*?\)", "", t["name"].split(" and ")[0]).strip()


def main():
    res, seen_q = {}, {}
    for t in TOOLS:
        rx = text_rx(t)
        if not rx: continue
        q = query_for(t)
        if q.lower() not in seen_q:
            items, page = [], 1
            while page <= 20:
                h = get(f"{BASE}/g-cloud/search?" + urllib.parse.urlencode({"q": q, "page": page}))
                got = parse(h)
                items += got
                if len(got) < 30 or not re.search(rf'page={page + 1}\b', h): break
                page += 1
            seen_q[q.lower()] = items
            time.sleep(0.5)
        hits = [i for i in seen_q[q.lower()] if rx.search(i["title"] + " " + i["summary"])]
        res[t["id"]] = hits
        print(t["id"], q, len(seen_q[q.lower()]), "results,", len(hits), "name it", flush=True)
    sys.path.insert(0, H); import clean
    write_json_gz(os.path.join(H, "sources", "gcloud.json.gz"), dict(source=BASE + "/g-cloud", read=ASOF["ref"], tools=clean.record(res)))


if __name__ == "__main__":
    main()
