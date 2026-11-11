"""Match the tooling register against every public-sector repository (R77). Needs the README cache from build/refresh/readmes.py.

  python3 -I build/dama/tool_repos.py --cache DIR

Evidence kinds, strongest first:
  d dependency, f file, i infrastructure   from rules.py code evidence (read 8 October 2026; repositories still present only)
  n name or description                     the repository's own name or one-line description names the tool
  r README                                  the README names the tool (it may only mention it: the page says so)
Snippets are at most 90 characters around the match, with email addresses and web addresses removed.
Writes tool_repo_ev.json.gz (committed, so the page can be rebuilt without the cache).
"""
import collections
import json
import os
import re
import sys

H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H); sys.path.insert(0, os.path.join(os.path.dirname(H), "refresh"))
from common import ASOF, read_json, write_json_gz
from tools import TOOLS, text_rx
import readmes
sys.path.insert(0, os.path.join(os.path.dirname(H), "procure")); import clean

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"); URL = re.compile(r"https?://\S+|www\.\S+")
CODE_BLOCK = re.compile(r"```.*?```", re.S)


def snip(text, m):
    a = max(0, m.start() - 40); s = text[a:m.end() + 40]
    s = URL.sub(" ", EMAIL.sub(" ", s)); s = re.sub(r"[#*`>\[\]()|_]+", " ", s)
    return clean.text(re.sub(r"\s+", " ", s).strip()[:90])   # names and quoted markings too (V717-8)


def main():
    cache = sys.argv[sys.argv.index("--cache") + 1]
    new = read_json(os.path.join(os.path.dirname(H), "refresh", "sources", "repos.json.gz"))
    rec = read_json(os.path.join(os.path.dirname(H), "refresh", "sources", "reconcile.json.gz"))
    rows, seen = [], set()
    for r in list(new) + rec["carried"]:
        if not isinstance(r, dict) or not r.get("owner") or not r.get("name"): continue
        k = (r["owner"].lower(), r["name"].lower())
        if k in seen: continue
        seen.add(k); rows.append(r)
    D = json.load(open(os.path.join(H, "dama_data.json")))
    vend_ids = [v["id"] for v in D["vendors"]]
    old = {}
    for repo, _caps, vend, _ in D["recs"]:
        for vi, kinds, sn in vend:
            if any(c in kinds for c in "dfi"): old.setdefault(repo.lower(), {})[vend_ids[vi]] = "".join(c for c in kinds if c in "dfi")
    RX = [(t["id"], text_rx(t)) for t in TOOLS if t["text"]]
    ev = collections.defaultdict(list); nread = 0
    for r in rows:
        key = f"{r['owner']}/{r['name']}"; basic = re.sub(r"[-_.]+", " ", r["name"]) + " " + (r.get("description") or "")
        txt = readmes.text(cache, r["owner"], r["name"]) if not r.get("archived") else None
        if txt is not None: nread += 1
        body = CODE_BLOCK.sub(" ", txt or "")[:20000]
        done = set()
        for tid, kinds in old.get(key.lower(), {}).items():
            ev[tid].append([key, kinds, ""]); done.add(tid)
        for tid, rx in RX:
            if tid in done: continue
            m = rx.search(basic)
            if m: ev[tid].append([key, "n", snip(basic, m)]); continue
            if body:
                m = rx.search(body)
                if m: ev[tid].append([key, "r", snip(body, m)])
    out = dict(read=ASOF["ref"], code_read=ASOF["previous"], repos=len(rows), readmes=nread, ev={k: sorted(v) for k, v in sorted(ev.items())})
    write_json_gz(os.path.join(H, "tool_repo_ev.json.gz"), out)
    print(len(rows), "repositories;", nread, "READMEs read;", sum(len(v) for v in ev.values()), "matches across", len(ev), "tools")
    for tid, v in sorted(ev.items(), key=lambda x: -len(x[1]))[:25]: print(f"  {tid}: {len(v)}  ({collections.Counter(k for _, k, _ in v).most_common()})")


if __name__ == "__main__":
    main()
