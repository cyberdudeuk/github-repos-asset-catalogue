"""The devolved nations' procurement notices for the tooling register (R84), from the Open Contracting Partnership's data registry.

  python3 -I build/procure/registry.py              fetch the yearly files, then keep the notices about software, IT or data
  python3 -I build/procure/registry.py --cached     use the files already in .cache/<source>

Two feeds the catalogue couldn't read directly are taken from the registry (https://data.open-contracting.org), which
republishes them under the Open Government Licence:
  pcs  Public Contracts Scotland, published by the Scottish Procurement and Commercial Directorate (registry publication 39):
       the site itself can't be reached from where the catalogue is built
  s2w  Sell2Wales (registry publication 119): see below
Since 24 February 2025, notices from Wales and Northern Ireland are also on Find a Tender, which is already read. eTendersNI
has no open data feed that could be found, so Northern Ireland's earlier notices are only those on Find a Tender.

Sell2Wales publishes OCDS through its own API (https://api.sell2wales.gov.wales/v1), but on 11 November 2026 every request
answered with a server error ('Error converting data type nvarchar to float'), for every month and notice type tried. The Open
Contracting Partnership's registry (https://data.open-contracting.org/en/publication/119) republishes the same feed as yearly
files under the Open Government Licence: 2022 to 2026; there is no 2021 file, and 2026 is thin because the feed stopped.
Each record is a compiled release, one per procurement. The same steps as Find a Tender and Contracts Finder apply (collect.py:
slim, keep, scrub). A compiled release is an 'award' when it has an active award, otherwise a 'tender', so values count the
same way. A notice's address is its own Sell2Wales page, from its tender documents or elsewhere in its record; the search redirect by
number was found to open a different notice and isn't used. A notice with no page of its own links to the registry's publication
page, and how many do is recorded.
"""
import gzip
import json
import os
import sys
import urllib.request

H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import collect
from collect import slim, keep, scrub, write_json_gz, ASOF

import re
SOURCES = {"s2w": dict(pub=119, years=[2022, 2023, 2024, 2025, 2026], host=r"www\.sell2wales\.gov\.wales"),
           "pcs": dict(pub=39, years=[2021, 2022, 2023, 2024, 2025, 2026], host=r"www\.publiccontractsscotland\.gov\.uk")}
for k, v in SOURCES.items():
    collect.URL.setdefault(k, f"https://data.open-contracting.org/en/publication/{v['pub']}")
    v["page"] = re.compile(rf"https?://{v['host']}/search/show/search_view\.aspx\?ID=[A-Z]{{3}}\d+", re.I)


def page_of(rel, src):
    """The notice's own page on its portal: from its tender documents first, then anywhere in the record."""
    rx = SOURCES[src]["page"]
    for d in (rel.get("tender") or {}).get("documents") or []:
        m = rx.search(d.get("url") or "")
        if m: return m.group(0)
    m = rx.search(json.dumps(rel))
    return m.group(0) if m else ""


def one(rel, src):
    r = slim(rel, src)
    r["tag"] = "award" if any((a.get("status") or "") == "active" for a in rel.get("awards") or []) else "tender"
    r["url"] = page_of(rel, src) or collect.URL[src]   # no page of its own: the registry's publication page, counted as without_page
    return r


def run(src, cached):
    S = SOURCES[src]; cache = os.path.join(H, ".cache", src); os.makedirs(cache, exist_ok=True)
    if not cached:
        for y in S["years"]:
            url = f"https://data.open-contracting.org/en/publication/{S['pub']}/download?name={y}.jsonl.gz"
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "github-repos-asset-catalogue-procurement"}), timeout=600) as f:
                open(os.path.join(cache, f"{y}.jsonl.gz"), "wb").write(f.read())
    rows, seen, read, no_page = [], set(), 0, 0
    for y in S["years"]:
        with gzip.open(os.path.join(cache, f"{y}.jsonl.gz"), "rt", encoding="utf-8") as g:
            for line in g:
                rel = json.loads(line); read += 1
                if (rel.get("date") or "")[:10] < "2021-01-01": continue
                r = one(rel, src)
                if not keep(r) or r["ocid"] in seen: continue
                seen.add(r["ocid"]); no_page += r["url"] == collect.URL[src]
                rows.append(scrub(r))
    write_json_gz(os.path.join(H, "sources", f"{src}.json.gz"), dict(source=collect.URL[src], read=__import__("time").strftime("%Y-%m-%d"), years=S["years"],
                                                                       releases_read=read, windows_split=0, without_page=no_page, rows=rows))
    print(src, "read", read, "compiled releases; kept", len(rows), "notices;", no_page, "without their own page address", flush=True)


def main():
    for src in SOURCES: run(src, "--cached" in sys.argv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
