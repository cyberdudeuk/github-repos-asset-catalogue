"""Read the devolved nations' data catalogues in full for datasets that name code (RM-07, R81).

  python3 -I build/catalogues/devolved.py          read every catalogue, then store
  python3 -I build/catalogues/devolved.py --self-test

Each catalogue is small enough to read record by record, so no search engine is trusted to find the mentions:
  dgs    data.gov.scot (CKAN; it replaced statistics.gov.scot)         https://api.data.gov.scot/api/3/action/package_search
  sdi    Scotland's spatial data catalogue (CSW)                        https://www.spatialdata.gov.scot/geonetwork/srv/eng/csw
  dmw    DataMapWales (GeoNode)                                         https://datamap.gov.wales/api/v2/resources
  odni   OpenDataNI (CKAN)                                              https://admin.opendatani.gov.uk/api/3/action/package_search
Kept: how many records each catalogue holds, and each record that mentions GitHub (with its GitHub addresses, if any) in the
same form as data.gov.uk's. A mention with no address, such as "taken from the OS GitHub repository", is counted as a mention
and joins nothing. Writes sources/devolved.json.gz, with its SHA-256 in sources/manifest.json.
"""
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from datagovuk import UA, repos_in, clean, write_json_gz

CATS = {
    "dgs": dict(name="data.gov.scot", nation="Scotland", api="https://api.data.gov.scot/api/3/action/package_search", page="https://data.gov.scot/dataset/"),
    "sdi": dict(name="Scotland's spatial data catalogue", nation="Scotland", api="https://www.spatialdata.gov.scot/geonetwork/srv/eng/csw",
                page="https://www.spatialdata.gov.scot/geonetwork/srv/eng/catalog.search#/metadata/"),
    "dmw": dict(name="DataMapWales", nation="Wales", api="https://datamap.gov.wales/api/v2/resources", page="https://datamap.gov.wales"),
    "odni": dict(name="OpenDataNI", nation="Northern Ireland", api="https://admin.opendatani.gov.uk/api/3/action/package_search", page="https://www.opendatani.gov.uk/@"),
}
GH = re.compile(r"(?i)github")


def fetch(url, kind="json"):
    for i in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=180) as r:
                b = r.read().decode("utf-8", "replace")
                return json.loads(b) if kind == "json" else b
        except Exception:
            time.sleep(3 * 2 ** i)
    raise SystemExit("did not answer: " + url)


def record(cat, rid, name, title, publisher, licence, modified, page, texts, raw=""):
    """One dataset in data.gov.uk's form. texts: [(where, text)] with where in page, resource, description."""
    uniq = {}
    for where, t in texts:
        for o, r in repos_in(t or ""): uniq.setdefault((o, r), where)
    missed = sorted({f"{o}/{r}" for o, r in repos_in(raw)} - {f"{o}/{r}" for o, r in uniq})   # in the raw record but not read from its fields
    return dict(missed=missed, id=f"{cat}:{rid}", name=f"{cat}:{name}", title=clean.text(title or ""), publisher=publisher or "", licence=licence or "", modified=(modified or "")[:10],
                formats=[], url=page, catalogue=cat, github=[[o, r, w] for (o, r), w in uniq.items()])


def ckan(cat):
    c = CATS[cat]; seen, total, start = [], 0, 0
    while True:
        d = fetch(c["api"] + "?" + urllib.parse.urlencode(dict(q="*:*", rows=500, start=start)))["result"]
        total = d["count"]
        for p in d["results"]:
            if not GH.search(json.dumps(p)): seen.append(None); continue
            org = p.get("organization") or {}
            page = c["page"] + (f"{org.get('name')}/{p['name']}" if cat == "odni" else p["name"])
            texts = [("page", p.get("url"))] + [("resource", r.get("url")) for r in p.get("resources") or []] + [("description", " ".join(v for k, v in p.items() if isinstance(v, str) and k not in ("url",)))]   # every text field: data.gov.scot keeps its description in 'description', not 'notes' (V719-1)
            seen.append(record(cat, p["id"], p["name"], p.get("title"), org.get("title"), p.get("license_title"), p.get("metadata_modified"), page, texts, json.dumps(p)))
        start += 500
        if start >= total: break
        time.sleep(0.5)
    return total, len(seen), [s for s in seen if s]


def geonode(cat):
    c = CATS[cat]; url = c["api"] + "?page_size=200&page=1"; n, keep = 0, []
    while url:
        d = fetch(url)
        for r in d.get("resources", []):
            n += 1
            if not GH.search(json.dumps(r)): continue
            owner = r.get("owner") or {}
            keep.append(record(cat, r.get("pk"), str(r.get("pk")), r.get("title"), (r.get("group") or {}).get("name") if isinstance(r.get("group"), dict) else "",
                               (r.get("license") or {}).get("identifier") if isinstance(r.get("license"), dict) else "", r.get("last_updated") or r.get("date"),
                               (r.get("detail_url") or "") if (r.get("detail_url") or "").startswith("http") else c["page"] + (r.get("detail_url") or ""), [("description", r.get("abstract")), ("resource", r.get("doc_url") or "")], json.dumps(r)))
        url = d.get("links", {}).get("next")
        time.sleep(0.3)
    return d.get("total", n), n, keep


def csw(cat):
    c = CATS[cat]; pos, n, keep, total = 1, 0, [], 0
    base = c["api"] + "?service=CSW&version=2.0.2&request=GetRecords&typeNames=csw:Record&resultType=results&elementSetName=full&maxRecords=100&startPosition="
    while pos:
        x = fetch(base + str(pos), "text")
        m = re.search(r'numberOfRecordsMatched="(\d+)"', x); total = int(m.group(1)) if m else total
        for r in re.findall(r"<csw:Record\b.*?</csw:Record>", x, re.S):
            n += 1
            if not GH.search(r): continue
            get = lambda tag: (re.search(rf"<{tag}>(.*?)</{tag}>", r, re.S) or [None, ""])[1]
            rid = get("dc:identifier")
            keep.append(record(cat, rid, rid, get("dc:title"), get("dc:publisher") or get("dc:creator"), get("dc:rights"), get("dc:date") or get("dct:modified"),
                               c["page"] + rid, [("description", re.sub(r"<[^>]+>", " ", r))], r))
        m = re.search(r'nextRecord="(\d+)"', x); pos = int(m.group(1)) if m and int(m.group(1)) > 0 else None
        time.sleep(0.3)
    return total, n, keep


READ = {"dgs": ckan, "odni": ckan, "dmw": geonode, "sdi": csw}


def self_test():
    bad = []
    r = record("x", "1", "a", "A", "P", "", "2026-11-11", "u", [("description", "taken from the OS British National Grid GitHub repository")])
    if r["github"]: bad.append("a mention with no address joined something")
    r = record("x", "1", "a", "A", "P", "", "", "u", [("description", "code at https://github.com/scotgovanalysis/x and again github.com/ScotGovAnalysis/x")])
    if r["github"] != [["scotgovanalysis", "x", "description"]]: bad.append(f"one repository named twice should join once: {r['github']}")
    if not r["name"].startswith("x:"): bad.append("a dataset's name must carry its catalogue so names can't collide across catalogues")
    r = record("x", "1", "a", "A", "P", "", "", "u", [("description", "")], json.dumps({"description": "see https://github.com/scotgovanalysis/y"}))
    if r["missed"] != ["scotgovanalysis/y"]: bad.append("an address in a field the reader doesn't look at was not reported as missed")
    return bad


def main():
    if "--self-test" in sys.argv:
        b = self_test(); print("ok" if not b else b); return 1 if b else 0
    out = dict(read=time.strftime("%Y-%m-%d"), catalogues={})
    for cat, c in CATS.items():
        total, n, keep = READ[cat](cat)
        out["catalogues"][cat] = dict(c, missed=sum(len(k["missed"]) for k in keep), holds=total, read_records=n, mention_github=len(keep), with_address=sum(1 for k in keep if k["github"]), datasets=keep)
        print(f"{cat}: {c['name']}: {total} held, {n} read, {len(keep)} mention GitHub, {sum(1 for k in keep if k['github'])} name a repository", flush=True)
    src = os.path.join(H, "sources", "devolved.json.gz"); write_json_gz(src, out)
    man = os.path.join(H, "sources", "manifest.json"); m = json.load(open(man))
    m["devolved"] = dict(read=out["read"], sha256=hashlib.sha256(open(src, "rb").read()).hexdigest(), catalogues={k: v["read_records"] for k, v in out["catalogues"].items()})
    json.dump(m, open(man, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
