"""Compact the DAMA classification for embedding in the page, with self-checks (31 Oct 2026).
Writes dama/dama_data.json and dama/export_checks.txt (PASS/FAIL lines read by the build's check registry)."""
import json, os, sys, collections
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from rules import AREAS, LIFECYCLE, VENDORS, NAME_ONLY
cl = json.load(open(f"{H}/classified.json")); prec = json.load(open(f"{H}/precision.json"))
CAPS = [c[0] for a in AREAS for c in a[4]]; CI = {c: i for i, c in enumerate(CAPS)}
VI = {v[0]: i for i, v in enumerate(VENDORS)}; LI = {l[0]: i for i, l in enumerate(LIFECYCLE)}
K = {"name": "n", "readme": "r", "file": "f", "infrastructure": "i", "dependency": "d"}
recs = []
for key, r in sorted(cl.items()):
    caps = [[CI[c], "".join(sorted({K[e[0]] for e in ev})), ev[0][1][:110]] for c, ev in r["caps"].items()]
    vend = [[VI[v], "".join(sorted({K[e[0]] for e in ev})), ev[0][1][:110]] for v, ev in r["vend"].items()]
    mask = sum(1 << LI[l] for l in r["life"])
    recs.append([key, caps, vend, mask])
out = dict(areas=[dict(id=a[0], label=a[1], short=a[2], desc=a[3], caps=[dict(id=c[0], label=c[1]) for c in a[4]]) for a in AREAS],
           caps=CAPS, vendors=[dict(id=v[0], name=v[1], supplier=v[2], type=v[3], areas=v[4]) for v in VENDORS],
           life=[dict(id=l[0], label=l[1]) for l in LIFECYCLE], recs=recs, precision=prec, name_only=sorted(NAME_ONLY),
           deps_fetched=len(os.listdir(f"{H}/deps")) if os.path.isdir(f"{H}/deps") else 0)
json.dump(out, open(f"{H}/dama_data.json", "w"), separators=(",", ":"))
lines = []
def ck(cid, ok, text, guards=""): lines.append(f"{'PASS' if ok else 'FAIL'} {cid} {text}" + (f" [guards: {guards}]" if guards else ""))
ck("C-DAMA-01", all(any(c.startswith(a[0] + "-") for c in CAPS) for a in AREAS) and len(set(CAPS)) == len(CAPS), f"{len(AREAS)} DAMA areas each have capabilities; {len(CAPS)} capability ids are unique", "V7-1")
ck("C-DAMA-02", all(0 <= c[0] < len(CAPS) for r in recs for c in r[1]) and all(0 <= v[0] < len(VENDORS) for r in recs for v in r[2]), "every exported match points at a known capability and supplier", "V7-1")
ck("C-DAMA-03", all(set(c[1]) <= set("nrfid") for r in recs for c in r[1]), "every match records how it was found (name, README, file, infrastructure or dependency)", "V7-2")
ck("C-DAMA-04", all(not (CAPS[c[0]] in NAME_ONLY and c[1] == "r") for r in recs for c in r[1]), "no README-only match for capabilities where README mentions proved incidental", "V7-2")
ck("C-DAMA-05", set(prec["areas"]) == {a[0] for a in AREAS}, "precision was sampled for every DAMA area", "V7-2")
open(f"{H}/export_checks.txt", "w").write("\n".join(lines) + "\n")
print("\n".join(lines)); print("records", len(recs), "bytes", os.path.getsize(f"{H}/dama_data.json"))
