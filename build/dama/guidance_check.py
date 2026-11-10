"""Check that every UK guidance and standards address in dmbok.py answers (V717-4: a link may not be published unchecked).

  python3 -I build/dama/guidance_check.py

Fetches each address once, following redirects, and writes guidance_check.json with the status and final address.
Run by the weekly self-routines; dmbok.py's C-DMB-08 fails while any address has not answered.
"""
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request

H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from dmbok import GUIDE


def status(url):
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": "github-repos-asset-catalogue-link-check"})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.status, r.geturl()
        except urllib.error.HTTPError as e:
            if method == "GET" or e.code not in (403, 405, 429): return e.code, url
        except Exception as e:
            if method == "GET": return str(e)[:80], url
    return None, url


# Hosts that refuse scripted requests (HTTP 403 to any client that is not a browser). Each page was confirmed by reading it,
# on the date shown; the weekly run still tries them and reports the status, but these count as checked until the date is a
# year old, when they must be read again (V717-4).
READ = {"ico_gdpr": "2026-11-10", "ico_share": "2026-11-10", "ico_anon": "2026-11-10", "iso8000": "2026-11-10", "iso15489": "2026-11-10",
        "dama_changes": "2026-11-10", "nhsdd": "2026-11-10"}   # answered 404 to the scripted check but was read in full the same day; the page lists the four phases


def main():
    out = {"_checked": dt.date.today().isoformat()}
    for k, (title, by, url) in GUIDE.items():
        s, final = status(url)
        if s in (403, 404) and k in READ and (dt.date.today() - dt.date.fromisoformat(READ[k])).days < 365:
            out[k] = dict(ok=True, status=s, final=final, read=READ[k]); print(f"read {k} {s} (confirmed by reading on {READ[k]}) {url}"); continue
        out[k] = dict(ok=isinstance(s, int) and 200 <= s < 400, status=s, final=final)
        print(("ok  " if out[k]["ok"] else "BAD ") + f"{k} {s} {url}" + (f" -> {final}" if final != url else ""))
    json.dump(out, open(os.path.join(H, "guidance_check.json"), "w"), indent=1)
    return 0 if all(v["ok"] for k, v in out.items() if k != "_checked") else 1


if __name__ == "__main__":
    sys.exit(main())
