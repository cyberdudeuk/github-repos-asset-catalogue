"""Data exchanges each government API catalogue entry relates to (R88, 20 Nov 2026).
Input: sources/ndl_exchanges.json, a pinned copy of the NDL PubSec MCP exchanges feed (read as untrusted data), and
dama/apis.json. Writes dama/exchanges.json and dama/exchanges_checks.txt.

The feed is the master for exchanges; this catalogue links to it and never edits it. Refresh the pin with
  python3 -I build/dama/exchanges.py --pin <path to a downloaded exchanges.json>
which records its SHA-256. "Related" means the feed's keyword search scoped to the parties found the API; it is not
evidence that the exchange uses it, and the page says so."""
import hashlib, json, os, sys
H = os.path.dirname(os.path.abspath(__file__))
FEED = f"{H}/sources/ndl_exchanges.json"
PIN = f"{H}/sources/ndl_exchanges.pin.json"
SOURCE_URL = "https://cyberdudeuk.github.io/ndl-pubsec-mcp/exchanges.json"

def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def key(name, provider): return f"{name.strip().lower()}|{provider.strip().lower()}"

def join(feed, catalogue):
    """Map catalogue entries to the exchanges whose related APIs name them: the same API name and the same provider.
    The merged API catalogue records the provider as an id in one file and as a display name in the other, so the
    feed's provider name and its providerId are both tried. Keys are the catalogue entry's own name|provider."""
    keys = {key(c["name"], c["provider"]) for c in catalogue}
    by, unmatched = {}, []
    for e in feed["exchanges"]:
        for a in e.get("relatedApis", []):
            k = next((k for k in (key(a["name"], a["provider"]), key(a["name"], a.get("providerId") or "")) if k in keys), None)
            if k: by.setdefault(k, []).append(e["id"])
            else: unmatched.append([e["id"], a["name"], a["provider"], bool(a.get("inCatalogue"))])
    return {k: sorted(set(v)) for k, v in by.items()}, unmatched

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--pin":
        src = sys.argv[2]; f = json.load(open(src)); assert isinstance(f.get("exchanges"), list) and f.get("caution")
        open(FEED, "w").write(open(src).read())
        json.dump({"url": SOURCE_URL, "build": f.get("build"), "as_of": f.get("asOf"), "sha256": sha(FEED)}, open(PIN, "w"), indent=1)
        print("pinned", f.get("build")); sys.exit(0)
    feed, pin = json.load(open(FEED)), json.load(open(PIN))
    cat = json.load(open(f"{H}/apis.json"))["catalogue"]
    by, unmatched = join(feed, cat)
    ex = [{k: e.get(k) for k in ("id", "title", "journey", "audience", "parties", "mechanism", "provenance", "portal")} for e in feed["exchanges"]]
    reg = feed["register"]
    out = {"source": {**pin, "name": feed.get("name"), "licence": feed.get("licence"), "master": feed.get("master")}, "caution": feed["caution"],
           "register": {k: reg.get(k) for k in ("title", "url", "read", "agreements", "byStatus", "activeByMethod", "byMethod", "methodField", "limits") if k in reg},
           "exchanges": ex, "by_api": by, "unmatched": unmatched}
    json.dump(out, open(f"{H}/exchanges.json", "w"), ensure_ascii=False)
    lines = []
    def ck(cid, ok, text, g="R88"): lines.append(f"{'PASS' if ok else 'FAIL'} {cid} {text}" + (f" [guards: {g}]" if g else ""))
    ids = {e["id"] for e in feed["exchanges"]}
    ck("C-XCH-01", sha(FEED) == pin["sha256"] and len(ids) == len(feed["exchanges"]) > 0, f"the exchanges feed is the pinned copy (SHA-256 recorded) and lists {len(ids)} distinct exchanges")
    names = {c["name"].strip().lower() for c in cat}
    dropped = [u for u in unmatched if u[1].strip().lower() in names]   # in this catalogue by name, yet not joined
    ck("C-XCH-02", all(i in ids for v in by.values() for i in v) and not dropped,
       f"{len(by)} catalogue entries link to exchanges, every link names an exchange in the feed, and no API this catalogue holds by name is left unjoined ({len(unmatched)} feed APIs are not in this catalogue and are listed, not linked){'; dropped: ' + str(dropped) if dropped else ''}")
    ck("C-XCH-03", "not evidence that the exchange uses it" in feed["caution"], "the caution that related is not the same as used travels with the data")
    _, neg_drop = join({"exchanges": [{"id": "x", "relatedApis": [{"name": "Citizen API", "provider": "Department for Work and Pensions", "providerId": "department-for-work-and-pensions"}]}]}, [{"name": "Citizen API", "provider": "department-for-work-and-pensions"}])
    ck("C-XCH-05", neg_drop == [], "a provider recorded as an id in one catalogue file and as a name in the feed still joins (the cause of only 4 of 22 mentions joining on the first run)")
    neg_by, _ = join({"exchanges": [{"id": "x", "relatedApis": [{"name": "GOV.UK Notify", "provider": "Somebody Else"}]}]}, [{"name": "GOV.UK Notify", "provider": "Government Digital Service"}, {"name": "Other", "provider": "Somebody Else"}])
    ck("C-XCH-04", neg_by == {}, "an API is linked only when name and provider both match exactly (negative test: the same name from another provider links nothing)")
    open(f"{H}/exchanges_checks.txt", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines)); print("linked", len(by), "unmatched", unmatched)
