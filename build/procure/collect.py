"""Collect UK public procurement notices about software, IT services and data (R76).

  python3 -I build/procure/collect.py fts|cf [--from 2021-01-01] [--to REF]

Sources (both Open Government Licence v3.0, Open Contracting Data Standard releases):
  fts  Find a Tender service:   https://www.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages   (above-threshold, from 2021)
  cf   Contracts Finder:        https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search (England and non-devolved, lower value too)

A notice is kept when one of its CPV codes is software (48), IT services (72) or a data-related code below, or when its
title or description is about data, analytics, records or software. Only these fields are kept: the notice id, stage,
dates, buyer, suppliers, title, description (first 2,000 characters), value, CPV codes, procedure and contract period.
Responses are parsed as JSON data only. Writes sources/<source>.json.gz, one month per run segment, so a run resumes.
"""
import datetime as dt
import gzip
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(H), "refresh"))
from common import ASOF, write_json_gz

URL = {"fts": "https://www.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages",
       "cf": "https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search"}
CPV_KEEP = re.compile(r"^(48|72|30211|30213|30230|50312|50324|64216|73110|79311|79342|79417|79342|79997|80533|92312)")
TEXT_KEEP = re.compile(r"(?i)\b(data|database|analytics?|business intelligence|dashboards?|metadata|master data|records? management|document management|content management|"
                       r"information management|data warehouse|data lake|lakehouse|etl|integration platform|api management|software|licen[cs]es?|saas|cloud platform|"
                       r"reporting tool|statistical|gis|geospatial|mdm|data quality|data catalogue|data governance|data platform|machine learning|artificial intelligence)\b")


LOG = os.environ.get("GHRAC_PROCURE_LOG")


def note(msg):
    if LOG:
        with open(LOG, "a") as f: f.write(time.strftime("%H:%M:%S ") + msg + "\n")


def get(url, tries=10):
    for i in range(tries):
        try:
            note("GET " + url[-90:])
            req = urllib.request.Request(url, headers={"User-Agent": "github-repos-asset-catalogue-procurement", "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ConnectionError, OSError) as e:
            code = getattr(e, "code", None)
            if code in (400, 404): raise
            wait = min(120, 3 * 2 ** i)
            if code == 429:   # the service asks us to slow down: do as it says
                ra = getattr(e, "headers", {}) and e.headers.get("Retry-After")
                wait = max(wait, int(ra)) if ra and str(ra).isdigit() else max(wait, 30)
            note(f"retry {i + 1} after {type(e).__name__} {code or ''}: waiting {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"gave up on {url}")


def cpvs(rel):
    t = rel.get("tender") or {}
    out = []
    for c in [t.get("classification")] + [i.get("classification") for i in t.get("items") or []] + [a for i in t.get("items") or [] for a in i.get("additionalClassifications") or []]:
        if isinstance(c, dict) and c.get("id"): out.append(str(c["id"])[:8])
    return sorted(set(out))


def slim(rel, src):
    t = rel.get("tender") or {}
    buyer = rel.get("buyer") or {}
    parties = {p.get("id"): p for p in rel.get("parties") or []}
    sup = []
    for a in rel.get("awards") or []:
        for s in a.get("suppliers") or []:
            p = parties.get(s.get("id"), {})
            sup.append(dict(id=s.get("id"), name=s.get("name") or p.get("name"), sme=((p.get("details") or {}).get("scale")), value=(a.get("value") or {}).get("amount")))
    bp = parties.get(buyer.get("id"), {})
    addr = bp.get("address") or {}
    val = (t.get("value") or {}).get("amount")
    if val is None:
        vs = [(a.get("value") or {}).get("amount") for a in rel.get("awards") or [] if (a.get("value") or {}).get("amount") is not None]
        val = sum(vs) if vs else None
    cp = t.get("contractPeriod") or next(((a.get("contractPeriod")) for a in rel.get("awards") or [] if a.get("contractPeriod")), None) or {}
    return dict(src=src, ocid=rel.get("ocid"), id=rel.get("id"), tag=(rel.get("tag") or [""])[0], date=(rel.get("date") or "")[:10],
                buyer=buyer.get("name") or bp.get("name"), buyer_id=buyer.get("id"), region=addr.get("region") or addr.get("locality") or "", postcode=(addr.get("postalCode") or "")[:4],
                title=(t.get("title") or "")[:300], desc=re.sub(r"\s+", " ", t.get("description") or "")[:2000], value=val, cur=(t.get("value") or {}).get("currency"),
                cpv=cpvs(rel), method=t.get("procurementMethodDetails") or t.get("procurementMethod") or "", start=(cp.get("startDate") or "")[:10], end=(cp.get("endDate") or "")[:10],
                suppliers=sup, url=(f"https://www.find-tender.service.gov.uk/Notice/{rel.get('id')}" if src == "fts" else "https://www.contractsfinder.service.gov.uk/Notice/" + re.sub(r"^ocds-[a-z0-9]+-", "", rel.get("ocid") or "")))


def keep(r):
    return any(CPV_KEEP.match(c) for c in r["cpv"]) or bool(TEXT_KEEP.search(r["title"] + " " + r["desc"][:600]))


def months(a, b):
    d = dt.date(a.year, a.month, 1)
    while d <= b:
        n = dt.date(d.year + d.month // 12, d.month % 12 + 1, 1)
        yield max(d, a), min(n, b + dt.timedelta(days=1))
        d = n


def collect(src, a, b, cache, workers=None):
    workers = workers or {"fts": 3, "cf": 2}[src]   # both services answer 429 (too many requests) to more readers than this
    os.makedirs(cache, exist_ok=True)
    todo = [(lo, hi) for lo, hi in months(a, b) if not (os.path.exists(os.path.join(cache, f"{src}-{lo.isoformat()}.json.gz")) and hi <= dt.date.fromisoformat(ASOF["ref"]))]
    import concurrent.futures as cf
    with cf.ThreadPoolExecutor(workers) as ex:
        for f in cf.as_completed([ex.submit(month, src, lo, hi, cache) for lo, hi in todo]): f.result()


def window(src, lo, hi):
    """Every release published (cf) or updated (fts) in [lo, hi). The services page by cursor; if a window's last page is
    full and has no next link, the window may have been cut short (V717-6), so it is split in two and both halves read. A next
    link that leads back to a page already read (V717-7) is treated the same way, so a looping service can't hold a reader."""
    fmt = lambda d: d.strftime("%Y-%m-%dT%H:%M:%S")
    key = "updated" if src == "fts" else "published"
    url = f"{URL[src]}?limit=100&{key}From={fmt(lo)}&{key}To={fmt(hi)}"
    rels, pages, last, seen_urls, looped = [], 0, 0, set(), False
    while url:
        seen_urls.add(url)
        d = get(url); pages += 1
        got = d.get("releases") or []; rels += got; last = len(got)
        url = (d.get("links") or {}).get("next")
        if url in seen_urls:   # the service sent us back to a page already read (V717-7): stop, and read the window in halves
            note("loop: next link already followed"); looped = True; break
    if (last >= 100 or looped) and hi - lo > dt.timedelta(hours=1):
        mid = lo + (hi - lo) / 2
        a, pa, sa = window(src, lo, mid); b, pb, sb = window(src, mid, hi)
        return a + b, pages + pa + pb, sa + sb + 1
    return rels, pages, 0


def month(src, lo, hi, cache):
    part = os.path.join(cache, f"{src}-{lo.isoformat()}.json.gz")
    lo_t = dt.datetime(lo.year, lo.month, lo.day); hi_t = dt.datetime(hi.year, hi.month, hi.day)
    rels, pages, splits = window(src, lo_t, hi_t)
    kept, seen = [], set()
    for rel in rels:
        k = (rel.get("ocid"), rel.get("id"))
        if k in seen: continue
        seen.add(k)
        r = slim(rel, src)
        if keep(r): kept.append(r)
    with gzip.open(part, "wt", encoding="utf-8") as f: json.dump(dict(read=len(seen), pages=pages, splits=splits, rows=kept), f)
    print(src, lo, "read", len(seen), "kept", len(kept), "pages", pages, "splits", splits, flush=True)


def scrub(r):
    """Personal names and email addresses quoted in a notice are removed before it is stored (R54, R69)."""
    if not hasattr(scrub, "pii"):
        sys.path.insert(0, os.path.join(os.path.dirname(H), "dama")); import pii; scrub.pii = pii
    em = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
    for k in ("title", "desc"):
        if r.get(k): r[k] = em.sub("[address removed]", scrub.pii.scrub(r[k])[0])
    return r


def assemble(src, cache):
    rows, seen, read, splits = [], set(), 0, 0
    for f in sorted(os.listdir(cache)):
        if f.startswith(src + "-"):
            with gzip.open(os.path.join(cache, f), "rt", encoding="utf-8") as g:
                part = json.load(g)
                if isinstance(part, dict): read += part["read"]; splits += part["splits"]
                for r in (part["rows"] if isinstance(part, dict) else part):
                    k = (r["ocid"], r["id"])
                    if k in seen: continue
                    seen.add(k); rows.append(scrub(r))
    write_json_gz(os.path.join(H, "sources", f"{src}.json.gz"), dict(source=URL[src], read=ASOF["ref"], releases_read=read, windows_split=splits, rows=rows))
    print(src, "read", read, "releases; kept", len(rows), "notices;", splits, "windows split because a page ended full")


def self_test():
    """A window whose last page is full with no next link is split and read again; a partial last page is trusted (V717-6)."""
    global get
    real = get; calls = []
    def fake(url):
        calls.append(url); q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        lo = dt.datetime.fromisoformat(q["publishedFrom"][0]); hi = dt.datetime.fromisoformat(q["publishedTo"][0])
        n = int((hi - lo).total_seconds() // 3600)          # one release per hour in the window
        if n > 100: return {"releases": [{"ocid": f"x{lo}-{i}", "id": str(i)} for i in range(100)]}   # cut short: full page, no next
        return {"releases": [{"ocid": f"x{lo + dt.timedelta(hours=i)}", "id": "1"} for i in range(n)]}
    def loop(url):   # a service whose next link always points back to the same page, for windows longer than a day
        calls.append(url)
        if len(calls) > 400: raise RuntimeError("the reader kept following a looping next link")
        q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        lo = dt.datetime.fromisoformat(q["publishedFrom"][0]); hi = dt.datetime.fromisoformat(q["publishedTo"][0])
        n = int((hi - lo).total_seconds() // 3600)
        if n > 24: return {"releases": [{"ocid": f"y{lo}-{i}", "id": "1"} for i in range(50)], "links": {"next": url.split("&cursor=")[0] + "&cursor=same"}}
        return {"releases": [{"ocid": f"y{lo + dt.timedelta(hours=i)}", "id": "1"} for i in range(n)]}
    get = fake
    try:
        rels, pages, splits = window("cf", dt.datetime(2024, 1, 1), dt.datetime(2024, 1, 11))   # 240 hours: needs splitting
        short, _, s2 = window("cf", dt.datetime(2024, 1, 1), dt.datetime(2024, 1, 3))         # 48 hours: one partial page
        get = loop; calls.clear()
        lrels, lpages, ls = window("cf", dt.datetime(2024, 1, 1), dt.datetime(2024, 1, 5))    # 96 hours from a looping service
    finally:
        get = real
    ok = splits > 0 and len({r["ocid"] for r in rels}) == 240 and s2 == 0 and len(short) == 48 and ls > 0 and lpages < 50 and len({r["ocid"] for r in lrels if re.fullmatch(r"y\S+ \d\d:\d\d:\d\d", r["ocid"])}) == 96
    print("ok" if ok else f"wrong: {len(rels)} releases, {splits} splits; short window {len(short)} with {s2} splits; looping service {lpages} pages, {ls} splits")
    return 0 if ok else 1


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]: sys.exit(self_test())
    src = sys.argv[1]
    a = dt.date.fromisoformat(sys.argv[sys.argv.index("--from") + 1]) if "--from" in sys.argv else dt.date(2021, 1, 1)
    b = dt.date.fromisoformat(sys.argv[sys.argv.index("--to") + 1]) if "--to" in sys.argv else dt.date.fromisoformat(ASOF["ref"])
    cache = sys.argv[sys.argv.index("--cache") + 1] if "--cache" in sys.argv else os.path.join(H, ".cache")
    os.makedirs(os.path.join(H, "sources"), exist_ok=True)
    collect(src, a, b, cache)
    assemble(src, cache)
