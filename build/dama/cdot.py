"""Crown dependencies and overseas territories: verify their public repositories directly against GitHub (7.9, R56).

Input: cdot_candidates.json, the GitHub accounts found by searching the web and GitHub (including GitHub's own search, signed in), with each repository's GitHub settings (fork, archived, stars, forks, licence, description) read from GitHub's repositories page, each with the evidence that it is
official and the repository names seen on GitHub. Nothing from a third-party feed is used for the facts below.
For every repository this script asks GitHub itself, over git (the original source):
  - git ls-remote: that the repository exists and is public, and its current HEAD commit;
  - a blobless clone (commit history and file tree, file contents only when read): first and last commit dates, commits
    in the last 90 days and 12 months, the file list, and the README, LICENCE, CODEOWNERS, SECURITY, CONTRIBUTING files,
    Dependabot settings and GitHub Actions workflows.
The README's first paragraph becomes the description, with personal names removed. Git can't tell whether GitHub has
archived a repository, or its stars and forks, so those are left as not checked.
Writes cdot.json and cdot_checks.txt. Run with python3 -I build/dama/cdot.py (needs network access to github.com).
"""
import datetime as dt, json, os, re, shutil, subprocess, sys, tempfile, collections
S = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, S)
import pii
EXT = {".py": "Python", ".js": "JavaScript", ".ts": "TypeScript", ".rb": "Ruby", ".java": "Java", ".cs": "C#", ".go": "Go", ".php": "PHP", ".html": "HTML", ".css": "CSS", ".scss": "SCSS", ".r": "R", ".R": "R", ".tf": "HCL", ".sh": "Shell", ".kt": "Kotlin", ".swift": "Swift", ".vue": "Vue", ".jsx": "JavaScript", ".tsx": "TypeScript", ".ipynb": "Jupyter Notebook", ".sql": "SQL", ".rs": "Rust", ".dart": "Dart"}
LIC = [("MIT", r"\bMIT License\b|Permission is hereby granted, free of charge"), ("Apache-2.0", r"Apache License,?\s+Version 2\.0"), ("OGL", r"Open Government Licen[cs]e"), ("GPL/LGPL", r"GNU (?:Lesser |Affero )?General Public License"), ("MPL-2.0", r"Mozilla Public License"), ("BSD", r"Redistribution and use in source and binary forms"), ("Unlicense", r"unlicense|This is free and unencumbered")]
NOW = dt.datetime.now(dt.timezone.utc)

def git(*a, cwd=None, timeout=180):
    return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, timeout=timeout)

def first_para(md):
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S); md = re.sub(r"^[^\n]+\n[=-]{3,}\s*$", "", md, flags=re.M)   # setext headings
    for block in re.split(r"\n\s*\n", md):
        b = block.strip()
        if not b or b.startswith(("#", "!", "[!", "<", "|", "```", "---", "===")) or len(b) < 25: continue
        b = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", b); b = re.sub(r"[*_`]", "", b); b = re.sub(r"\s+", " ", b)
        return pii.scrub(b[:300])[0]
    return ""

def verify(owner, repo):
    url = f"https://github.com/{owner}/{repo}"; r = git("ls-remote", url, "HEAD", timeout=60)
    if r.returncode != 0: return {"exists": False, "error": (r.stderr or "not found").strip()[:160]}
    if not r.stdout.strip(): return {"exists": True, "empty": True, "status": "Empty", "commits": 0, "files": 0, "description": "", "language": "", "licence": "none", "readme": False}   # public, but no commits yet
    head = r.stdout.split()[0]; tmp = tempfile.mkdtemp(prefix="cdot-")
    try:
        c = git("clone", "-q", "--filter=blob:none", "--no-checkout", url, tmp + "/r", timeout=300)
        if c.returncode != 0: return {"exists": True, "head": head, "error": "clone failed: " + c.stderr.strip()[:160]}
        d = tmp + "/r"; log = git("log", "--format=%cI|%an", cwd=d).stdout.strip().splitlines()
        dates = [dt.datetime.fromisoformat(l.split("|")[0]) for l in log if l]; authors = [l.split("|", 1)[1] for l in log if "|" in l]
        human = [t for t, a in zip(dates, authors) if not re.search(r"\[bot\]|dependabot|renovate|github-actions", a, re.I)]
        files = git("ls-tree", "-r", "--name-only", "HEAD", cwd=d).stdout.splitlines()
        show = lambda p: git("show", "HEAD:" + p, cwd=d, timeout=120).stdout if p else ""
        find = lambda rx: next((f for f in files if re.fullmatch(rx, f, re.I)), "")
        readme = find(r"(?:docs/|\.github/)?readme(?:\.md|\.rst|\.txt)?"); lic = find(r"licen[cs]e(?:\.md|\.txt)?|copying(?:\.md|\.txt)?")
        lictext = show(lic)[:6000]; licence = next((n for n, rx in LIC if re.search(rx, lictext, re.I)), "other" if lic else "none")
        langs = collections.Counter(EXT.get(os.path.splitext(f)[1], "") for f in files); langs.pop("", None)
        c90 = sum(1 for t in human if (NOW - t).days <= 90); c12 = sum(1 for t in human if (NOW - t).days <= 365)
        last = max(dates) if dates else None; lasth = max(human) if human else None
        st = "Active" if c90 else "Maintained" if last and (NOW - last).days <= 90 else "Inactive" if lasth and (NOW - lasth).days <= 365 else "Dormant"
        return {"exists": True, "head": head[:12], "commits": len(dates), "first": min(dates).isoformat() if dates else "", "last": last.isoformat() if last else "", "last_human": lasth.isoformat() if lasth else "",
                "c90": c90, "c12": c12, "status": st, "files": len(files), "language": langs.most_common(1)[0][0] if langs else "", "licence": licence,
                "readme": bool(readme), "description": first_para(show(readme)) if readme else "",
                "codeowners": any(re.fullmatch(r"(?:\.github/|docs/)?codeowners", f, re.I) for f in files), "security": any(re.fullmatch(r"(?:\.github/)?security\.md", f, re.I) for f in files),
                "contributing": any(re.fullmatch(r"(?:\.github/)?contributing\.md", f, re.I) for f in files), "dependabot": ".github/dependabot.yml" in files or ".github/dependabot.yaml" in files,
                "workflows": sum(1 for f in files if re.fullmatch(r"\.github/workflows/[^/]+\.ya?ml", f))}
    except subprocess.TimeoutExpired: return {"exists": True, "head": head[:12], "error": "timed out"}
    finally: shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    cand = json.load(open(os.path.join(S, "cdot_candidates.json"))); out, lines, fails = [], [], []
    for a in cand["accounts"]:
        reps = []
        for repo in a["repos"]:
            v = verify(a["account"], repo); v["name"] = repo; reps.append(v); print(a["account"], repo, v.get("status") or v.get("error"))
        for r in reps:
            g = a.get("github", {}).get(r["name"], {}); r["fork"] = bool(g.get("fork")) if g else r["name"] in a.get("forks", [])
            if g: r.update(github_description=g.get("description") or "", stars=g.get("stars"), forks_count=g.get("forks"), github_licence=g.get("licence"), pushed=g.get("pushed"), archived=g.get("type", "").endswith("archive"))
            if g.get("description"): r["description"] = pii.scrub(g["description"])[0]   # GitHub's own description wins over the README's first paragraph
        out.append({**{k: a[k] for k in ("account", "body", "place", "kind", "evidence", "confidence", "in_catalogue")}, "repos": reps})
    n = sum(len(a["repos"]) for a in out); ok = sum(1 for a in out for r in a["repos"] if r.get("exists") and not r.get("error"))
    empty = sum(1 for a in out for r in a["repos"] if r.get("empty"))
    lines.append(f"{'PASS' if ok == n and n else 'FAIL'} C-CDOT-01 {ok} of {n} repositories from {len(out)} crown dependency and overseas territory accounts verified directly against GitHub over git ({empty} public but empty): exists, HEAD commit, commit history and files read from the source [guards: R56]")
    bad = verify("alphagov", "this-repository-does-not-exist-ghrac-test")
    lines.append(f"{'PASS' if bad.get('exists') is False else 'FAIL'} C-CDOT-01n negative test: a repository that doesn't exist on GitHub is reported as not found, not as verified [guards: R56]")
    for l in lines: print(l)
    json.dump(dict(verified=NOW.date().isoformat(), method="git ls-remote and a blobless git clone of each repository on github.com, read directly from the source, with fork, archive, star and description details from each account's repositories page on GitHub", searched=cand.get("searched", []), not_found=cand.get("not_found", []), accounts=out),
              open(os.path.join(S, "cdot.json"), "w"), ensure_ascii=False, indent=1)
    open(os.path.join(S, "cdot_checks.txt"), "w").write("\n".join(lines) + "\n")
    sys.exit(0 if all(l.startswith("PASS") for l in lines) else 1)
