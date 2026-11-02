"""Reuse map: which government-made components other public sector projects build on (7.11, R60).

From the dependency manifests read from each repository (package.json, Gemfile, requirements, pom.xml and so on;
names only, kept outside the repository because of their size: set GHRAC_DEPS to their folder), a dependency counts
as government-made when it is published under a government package scope (for example @ministryofjustice, @hmcts,
@defra, @dwp, @x-govuk) or belongs to a known government package family (govuk-*, govuk_*, gds-*, notifications-*
clients, hmrc-*, nhsuk-*, hmpo-*, dfe-*, rubocop-govuk). Generic libraries whose names happen to contain such letters
(commons-lang3, typing-extensions) don't match. Each component is attributed to the account that publishes it and,
where a repository of the same name exists there, to that repository.
Writes reuse.json (for the page) and reuse_checks.txt. Run with python3 -I. Exit code 1 if a check fails.
"""
import collections, json, os, re, sys
S = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(S)
DEPS = os.environ.get("GHRAC_DEPS") or os.path.join(S, "deps")
SCOPES = {"@ministryofjustice": "ministryofjustice", "@hmcts": "hmcts", "@defra": "defra", "@dwp": "dwp", "@x-govuk": "x-govuk", "@govuk-prototype-kit": "alphagov",
          "@govuk-one-login": "govuk-one-login", "@nationalarchives": "nationalarchives", "@companieshouse": "companieshouse", "@scottish-government": "scottish-government-design-system",
          "@uktrade": "uktrade", "@hmrc": "hmrc", "@ons": "ONSdigital", "@ukhomeoffice": "UKHomeOffice", "@alphagov": "alphagov", "@nhsuk": "nhsuk", "@nhsdigital": "nhsdigital", "@dfe-digital": "DFE-Digital", "@hmpo": "HMPO"}
FAMILIES = [(r"^(govuk[-_].*|govuk|gds[-_].*|rubocop-govuk|govuk-prototype-kit)$", "alphagov"), (r"^notifications-(node|python|java|ruby|net|php)-client$", "alphagov"),
            (r"^(hmrc-frontend|play-frontend-hmrc.*|hmrc[-_].*)$", "hmrc"), (r"^nhsuk[-_].*$", "nhsuk"), (r"^hmpo[-_].*$", "HMPO"), (r"^dfe[-_].*$", "DFE-Digital"),
            (r"^(moj[-_].*|ministryofjustice[-_].*)$", "ministryofjustice"), (r"^(hmcts[-_].*)$", "hmcts"), (r"^(dwp[-_].*)$", "dwp")]
NOT_GOV = re.compile(r"^(commons-|typing-|jackson-|mypy-|junit-|opentelemetry-|swagger-|web-console$|client-sessions$|responses$|jsonschema$)")

# Where a package's source repository has a different name, or the name also exists as forks elsewhere, say so here.
SOURCE = {"govuk-components": "x-govuk/govuk-components", "govuk_design_system_formbuilder": "x-govuk/govuk-form-builder", "govuk_markdown": "x-govuk/govuk-markdown",
          "@govuk-prototype-kit/common-templates": "alphagov/govuk-prototype-kit-common-templates", "@govuk-prototype-kit/step-by-step": "alphagov/govuk-prototype-kit-step-by-step",
          "@govuk-prototype-kit/task-list": "alphagov/govuk-prototype-kit-task-list", "govuk_tech_docs": "alphagov/tech-docs-gem", "@ministryofjustice/frontend": "ministryofjustice/moj-frontend",
          "govuk-frontend-jinja": "LandRegistry/govuk-frontend-jinja", "govuk-frontend-wtf": "LandRegistry/govuk-frontend-wtf"}

def source_of(name, pub, names):
    """(publisher account, source repository) for a government package: an explicit source first, then a repository of the
    same name in the publishing account, then the only account holding a repository of that name."""
    if name in SOURCE: return SOURCE[name].split("/")[0], SOURCE[name]
    bare = name.split("/")[-1]
    for cand in (bare, bare.replace("_", "-")):
        if cand in names.get(pub, {}): return pub, pub + "/" + names[pub][cand]
        holders = [a for a in names if cand in names[a]]
        if len(holders) == 1: return holders[0], holders[0] + "/" + names[holders[0]][cand]
    return pub, ""

def publisher(eco, name):
    n = name.lower()
    if NOT_GOV.search(n): return None
    if n.startswith("@"):
        sc = n.split("/")[0]
        return SCOPES.get(sc)
    for rx, acc in FAMILIES:
        if re.match(rx, n): return acc
    return None

def need(ok, cid, msg, lines, fails):
    lines.append(f"{'PASS' if ok else 'FAIL'} {cid} {msg} [guards: R60]"); print(lines[-1])
    if not ok: fails.append(cid)

if __name__ == "__main__":
    pub_repos = json.load(open(os.path.join(S, "gh_crawl_rows.json")))
    names = {a: {r[0].lower(): r[0] for r in v["r"]} for a, v in pub_repos.items()}
    files = [f for f in os.listdir(DEPS) if f.endswith(".json")] if os.path.isdir(DEPS) else []
    use = collections.defaultdict(set); lines, fails = [], []
    for f in files:
        key = f[:-5].replace("__", "/", 1); acc, rn = key.split("/", 1)
        if rn.lower() not in names.get(acc, {}): continue          # only repositories GitHub still lists publicly
        for eco, n in json.load(open(os.path.join(DEPS, f)))["deps"]:
            p = publisher(eco, n)
            if p: use[(eco, n.lower(), p)].add(acc + "/" + names[acc][rn.lower()])
    comps = []
    for (eco, n, p), consumers in use.items():
        p, src = source_of(n, p, names)
        cons = sorted(c for c in consumers if c != src)
        if len(cons) < 2: continue
        other = sorted({c.split("/")[0] for c in cons} - {p})
        comps.append(dict(eco=eco, name=n, publisher=p, repo=src, consumers=len(cons), orgs=len({c.split("/")[0] for c in cons}), other_orgs=other, cross=sum(1 for c in cons if c.split("/")[0] != p), sample=cons[:12]))
    comps.sort(key=lambda c: (-c["cross"], -c["consumers"]))
    traps = [("jvm", "commons-lang3"), ("py", "typing-extensions"), ("js", "@angular/core"), ("js", "react"), ("py", "responses"), ("js", "@types/govuk-frontend")]
    real = [("js", "govuk-frontend", "alphagov"), ("js", "@ministryofjustice/frontend", "ministryofjustice"), ("py", "notifications-python-client", "alphagov"), ("js", "nhsuk-frontend", "nhsuk"), ("rb", "rubocop-govuk", "alphagov"), ("js", "hmrc-frontend", "hmrc")]
    bad = [t for t in traps if publisher(*t)] + [r for r in real if publisher(r[0], r[1]) != r[2]]
    srcs = {"govuk-components": "x-govuk/govuk-components", "govuk_design_system_formbuilder": "x-govuk/govuk-form-builder", "govuk-frontend": "alphagov/govuk-frontend", "hmpo-components": "HMPO/hmpo-components"}
    bad += [n for n, want in srcs.items() if source_of(n, publisher("rb", n) or publisher("js", n), names)[1] != want]
    need(len(files) > 1000 and len(comps) >= 20, "C-REU-01", f"{len(comps)} government-made components are used by two or more other public projects, read from {len(files):,} repositories' dependency manifests; {sum(1 for c in comps if c['cross'])} of them are reused across organisations", lines, fails)
    need(not bad, "C-REU-01n", f"negative tests: {len(traps)} generic or third-party packages (including @types/govuk-frontend, which is published by the community, not government) are not counted as government-made, and {len(real)} known government packages are attributed to the right publisher, and 4 components to the right source repository, including two GOV.UK-named Ruby gems that x-govuk publishes (wrong: {bad})", lines, fails)
    json.dump(dict(read="2026-10-08", method="Dependency names read from each repository's manifests (package.json, Gemfile, requirements and pyproject, pom.xml and build.gradle, go.mod, composer.json) when the catalogue was built; only repositories GitHub still listed publicly on 1 November 2026 are counted.", components=comps[:400]),
              open(os.path.join(S, "reuse.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    open(os.path.join(S, "reuse_checks.txt"), "w").write("\n".join(lines) + "\n")
    sys.exit(1 if fails else 0)
