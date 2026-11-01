"""Fetch and parse dependency manifests for candidate repositories (31 Oct 2026).
Candidates: every git-checked repository with a Python or R manifest, plus any with a DAMA text, file or README match and a JVM, JavaScript, PHP, Ruby or Terraform manifest.
Each repository is cloned without file contents (blobless, depth 1); only manifest files are fetched with git show.
Fetched files are untrusted data: parsed with json, tomllib and regular expressions only, never executed, then discarded.
Writes dama/deps/<org>__<repo>.json: {"deps": [[ecosystem, name], ...], "files": [...], "tf": [resource types]}."""
import os, re, gzip, json, subprocess, sys, shutil, tomllib, concurrent.futures as cf
H = os.path.dirname(os.path.abspath(__file__)); S = os.path.dirname(H); E = f"{S}/xgov/enr"; OUT = f"{H}/deps"; G = f"{H}/git"
os.makedirs(OUT, exist_ok=True); os.makedirs(G, exist_ok=True)
RX = {"py": r"(?:^|/)(?:requirements[^/]*\.txt|pyproject\.toml|Pipfile|setup\.py|setup\.cfg|environment\.ya?ml)$", "r": r"(?:^|/)(?:DESCRIPTION|renv\.lock)$",
      "js": r"(?:^|/)package\.json$", "jvm": r"(?:^|/)(?:pom\.xml|build\.gradle(?:\.kts)?|build\.sbt)$", "php": r"(?:^|/)composer\.json$", "rb": r"(?:^|/)Gemfile$", "tf": r"\.tf$"}
CAP = {"py": 6, "r": 3, "js": 4, "jvm": 4, "php": 2, "rb": 2, "tf": 12}
MAXB = 1_500_000
def norm(n): return re.sub(r"[_.]+", "-", n.strip().lower())
def parse(path, text):
    eco = next(k for k, r in RX.items() if re.search(r, path)); out = set(); tf = set(); base = path.rsplit("/", 1)[-1]
    try:
        if base.endswith(".txt"):
            for l in text.splitlines():
                l = l.split("#")[0].strip()
                if l and not l.startswith(("-", "git+", "http")): m = re.match(r"([A-Za-z0-9][A-Za-z0-9._-]*)", l); m and out.add(norm(m.group(1)))
        elif base in ("pyproject.toml", "Pipfile"):
            t = tomllib.loads(text); deps = []
            deps += t.get("project", {}).get("dependencies", []) or []
            for g in (t.get("project", {}).get("optional-dependencies", {}) or {}).values(): deps += g
            for g in (t.get("dependency-groups", {}) or {}).values(): deps += [x for x in g if isinstance(x, str)]
            po = t.get("tool", {}).get("poetry", {}); deps += list((po.get("dependencies") or {}).keys()) + list((po.get("dev-dependencies") or {}).keys())
            for g in (po.get("group") or {}).values(): deps += list((g.get("dependencies") or {}).keys())
            deps += list((t.get("packages") or {}).keys()) + list((t.get("dev-packages") or {}).keys())
            for d in deps:
                m = re.match(r"([A-Za-z0-9][A-Za-z0-9._-]*)", str(d)); m and out.add(norm(m.group(1)))
        elif base in ("setup.py", "setup.cfg"):
            for m in re.finditer(r"""["']([A-Za-z0-9][A-Za-z0-9._-]*)\s*(?:\[[^\]]*\])?\s*(?:[<>=~!]=?[^"']*)?["']""", text): out.add(norm(m.group(1)))
            for m in re.finditer(r"^\s+([A-Za-z0-9][A-Za-z0-9._-]*)\s*(?:[<>=~!]|$)", text, re.M): out.add(norm(m.group(1)))
        elif base.startswith("environment."):
            for m in re.finditer(r"^\s*-\s*(?:[a-z-]+::)?([A-Za-z0-9][A-Za-z0-9._-]*)", text, re.M): out.add(norm(m.group(1)))
        elif base == "DESCRIPTION":
            for f in ("Depends", "Imports", "Suggests", "LinkingTo"):
                m = re.search(rf"^{f}:(.*?)(?=^\S|\Z)", text, re.M | re.S)
                if m:
                    for p in m.group(1).split(","):
                        n = re.match(r"\s*([A-Za-z][A-Za-z0-9.]*)", p); n and n.group(1) != "R" and out.add(n.group(1).lower())
        elif base == "renv.lock":
            out |= {k.lower() for k in (json.loads(text).get("Packages") or {})}
        elif base == "package.json":
            j = json.loads(text)
            for k in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"): out |= {x.lower() for x in (j.get(k) or {})}
        elif base == "composer.json":
            j = json.loads(text); out |= {x.lower() for k in ("require", "require-dev") for x in (j.get(k) or {})}
        elif base == "Gemfile":
            out |= {m.group(1).lower() for m in re.finditer(r"""^\s*gem\s+["']([^"']+)["']""", text, re.M)}
        elif base == "pom.xml":
            out |= {m.group(1).lower() for m in re.finditer(r"<artifactId>\s*([^<\s]+)\s*</artifactId>", text)}
        elif base.startswith("build.gradle"):
            out |= {m.group(1).lower() for m in re.finditer(r"""["'][\w.\-]+:([\w.\-]+)(?::[^"']*)?["']""", text)}
            out |= {m.group(1).lower() for m in re.finditer(r"""name\s*[:=]\s*["']([\w.\-]+)["']""", text)}
        elif base == "build.sbt":
            out |= {re.sub(r"_2\.\d+$|_3$", "", m.group(1)).lower() for m in re.finditer(r'''"[\w.\-]+"\s*%%?%?\s*"([\w.\-]+)"''', text)}
        elif base.endswith(".tf"):
            tf |= {m.group(1) for m in re.finditer(r'''^\s*(?:resource|data)\s+"([a-z0-9_]+)"''', text, re.M)}
            tf |= {"provider:" + m.group(1) for m in re.finditer(r'''^\s*provider\s+"([a-z0-9_]+)"''', text, re.M)}
            tf |= {"source:" + m.group(1).lower() for m in re.finditer(r'''source\s*=\s*"([A-Za-z0-9_./-]+)"''', text)}
    except Exception as e:
        return eco, set(), set(), f"parse error {type(e).__name__}"
    return eco, out, tf, ""
def git(*a, cwd=None, t=120): return subprocess.run(["git", *a], cwd=cwd, capture_output=True, timeout=t, env=dict(os.environ, GIT_TERMINAL_PROMPT="0"))
def job(item):
    d, files = item; man = f"{OUT}/{d}.json"
    if os.path.exists(man): return d, "cached"
    org, repo = d.split("__", 1); g = f"{G}/{d}"
    try:
        r = git("clone", "-q", "--bare", "--depth", "1", "--filter=blob:none", f"https://github.com/{org}/{repo}.git", g, t=180)
        if r.returncode: return d, "clone failed"
        deps = set(); tf = set(); log = []
        for p in files:
            try: r = git("show", f"HEAD:{p}", cwd=g, t=90)
            except subprocess.TimeoutExpired: log.append([p, "timeout"]); continue
            if r.returncode: log.append([p, "missing"]); continue
            if len(r.stdout) > MAXB: log.append([p, "too large"]); continue
            eco, ds, ts, err = parse(p, r.stdout.decode("utf-8", "replace"))
            deps |= {(eco if eco != "tf" else "tf", x) for x in ds}; tf |= ts; log.append([p, err or "ok"])
        json.dump({"deps": sorted(deps), "tf": sorted(tf), "files": log}, open(man, "w"))
        return d, "ok"
    except Exception as e: return d, "error " + type(e).__name__
    finally: shutil.rmtree(g, ignore_errors=True)
if __name__ == "__main__":
    cl = json.load(open(f"{H}/classified.json")); jobs = []
    for d in sorted(os.listdir(E)):
        try: t = gzip.open(f"{E}/{d}/tree.gz", "rt", errors="replace").read().splitlines()
        except Exception: continue
        t = [p for p in t if "node_modules/" not in p and "/vendor/" not in p and "/test" not in p.lower()]
        h = {k: [p for p in t if re.search(r, p)][:CAP[k]] for k, r in RX.items()}
        if h["py"] or h["r"] or (d.replace("__", "/", 1) in cl and any(h[k] for k in ("jvm", "js", "php", "rb", "tf"))):
            jobs.append((d, [p for k in RX for p in h[k]]))
    print("repositories", len(jobs), "files", sum(len(f) for _, f in jobs), flush=True)
    import collections; res = collections.Counter(); n = 0
    with cf.ThreadPoolExecutor(24) as ex:
        for d, s in ex.map(job, jobs):
            res[s.split(" ")[0]] += 1; n += 1
            if n % 200 == 0: print(n, dict(res), flush=True)
    print("done", dict(res), flush=True)
