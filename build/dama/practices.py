"""Good practice across disciplines, and a type for each repository, from file trees (31 Oct 2026).
Every signal is a file or folder in the repository's default-branch tree, so it shows the practice is set up, not how well it is followed.
Writes dama/practices.json and dama/practices_checks.txt."""
import json, re, gzip, os, collections
H = os.path.dirname(os.path.abspath(__file__)); S = os.path.dirname(H); ENR = f"{S}/xgov/enr"; I = re.I
DISC = [
 ("arch", "Architecture", [
   ("adr", "Architecture decision records", r"(?:^|/)(?:adr|adrs|decisions|architecture-decisions?|architecture/decisions|architecture-decision-records?)/[^/]+\.md$"),
   ("archdoc", "Architecture documentation", r"(?:^|/)ARCHITECTURE\.md$|(?:^|/)docs/architecture(?:/|\.md$)|(?:^|/)architecture/[^/]+\.(?:md|png|svg)$"),
   ("diagrams", "Diagrams as code (C4, PlantUML, Mermaid, Structurizr)", r"\.(?:puml|plantuml|mmd|dsl|drawio)$|(?:^|/)workspace\.dsl$|(?:^|/)c4/"),
   ("apispec", "API specification", r"(?:^|/)(?:openapi|swagger)[^/]*\.(?:ya?ml|json)$|\.raml$|(?:^|/)asyncapi[^/]*\.ya?ml$")]),
 ("devops", "DevOps and delivery", [
   ("ci", "Continuous integration", r"^\.github/workflows/[^/]+\.ya?ml$|(?:^|/)\.gitlab-ci\.yml$|(?:^|/)Jenkinsfile$|^\.circleci/|(?:^|/)azure-pipelines[^/]*\.ya?ml$|(?:^|/)\.travis\.yml$|(?:^|/)concourse/|(?:^|/)buildspec\.ya?ml$"),
   ("cd", "Automated deployment or release", r"^\.github/workflows/[^/]*(?:deploy|release|publish|cd|promote)[^/]*\.ya?ml$|(?:^|/)\.releaserc|(?:^|/)release-please"),
   ("iac", "Infrastructure as code", r"\.tf$|(?:^|/)cdk\.json$|\.bicep$|(?:^|/)Pulumi\.ya?ml$|(?:^|/)(?:cloudformation|cfn)/[^/]+\.ya?ml$|(?:^|/)template\.ya?ml$|(?:^|/)serverless\.ya?ml$"),
   ("containers", "Containers", r"(?:^|/)Dockerfile[^/]*$|(?:^|/)docker-compose[^/]*\.ya?ml$|(?:^|/)compose\.ya?ml$"),
   ("k8s", "Kubernetes or Helm", r"(?:^|/)Chart\.yaml$|(?:^|/)(?:k8s|kubernetes|helm|manifests)/[^/]+\.ya?ml$|(?:^|/)kustomization\.ya?ml$"),
   ("deps", "Automated dependency updates", r"^\.github/dependabot\.ya?ml$|(?:^|/)renovate\.json5?$|(?:^|/)\.renovaterc")]),
 ("sec", "Security", [
   ("secmd", "Security policy (SECURITY.md)", r"(?:^|/)SECURITY\.md$"),
   ("sast", "Security scanning in the pipeline", r"^\.github/workflows/[^/]*(?:codeql|security|trivy|snyk|semgrep|zap|scan|sast|gitleaks|secret)[^/]*\.ya?ml$|(?:^|/)\.snyk$|(?:^|/)\.trivyignore$|(?:^|/)\.semgrep"),
   ("secrets", "Secret detection", r"(?:^|/)\.gitleaks\.toml$|(?:^|/)\.secrets\.baseline$|(?:^|/)\.talismanrc$|(?:^|/)\.git-secrets"),
   ("precommit", "Pre-commit checks", r"(?:^|/)\.pre-commit-config\.ya?ml$|(?:^|/)\.husky/")]),
 ("test", "Testing and code quality", [
   ("tests", "Automated tests", r"(?:^|/)(?:tests?|spec|specs|__tests__|e2e|cypress|playwright)/|_test\.(?:go|py|rb)$|\.(?:spec|test)\.(?:js|ts|jsx|tsx)$|(?:^|/)test_[^/]+\.py$|Spec\.scala$|Test\.(?:java|kt|cs)$"),
   ("lint", "Linting and formatting", r"(?:^|/)\.eslintrc[^/]*$|(?:^|/)eslint\.config\.[mc]?js$|(?:^|/)\.rubocop\.yml$|(?:^|/)\.flake8$|(?:^|/)ruff\.toml$|(?:^|/)\.pylintrc$|(?:^|/)\.prettierrc[^/]*$|(?:^|/)scalastyle-config\.xml$|(?:^|/)\.scalafmt\.conf$|(?:^|/)\.sqlfluff$|(?:^|/)\.stylelintrc[^/]*$|(?:^|/)\.editorconfig$|(?:^|/)\.lintr$"),
   ("coverage", "Test coverage reporting", r"(?:^|/)codecov\.ya?ml$|(?:^|/)\.coveragerc$|(?:^|/)\.nycrc[^/]*$|(?:^|/)\.simplecov$|(?:^|/)jacoco"),
   ("a11ytest", "Accessibility testing", r"(?:^|/)\.pa11yci[^/]*$|pa11y|axe[-_.]|(?:^|/)lighthouserc[^/]*$|accessibility[-_]?tests?")]),
 ("docs", "Documentation and openness", [
   ("readme", "README", r"(?:^|/)README(?:\.[a-z]+)?$"),
   ("docsdir", "Documentation folder or site", r"^docs/|^documentation/|(?:^|/)mkdocs\.ya?ml$|^source/documentation/"),
   ("contrib", "Contribution guide", r"(?:^|/)CONTRIBUTING\.md$"),
   ("coc", "Code of conduct", r"(?:^|/)CODE_OF_CONDUCT\.md$"),
   ("changelog", "Change log", r"(?:^|/)CHANGELOG(?:\.md)?$"),
   ("licence", "Licence file", r"^(?:LICEN[CS]E|COPYING)(?:\.[a-z]+)?$"),
   ("owners", "Named owners (CODEOWNERS)", r"(?:^|/)CODEOWNERS$"),
   ("templates", "Issue or pull request templates", r"^\.github/(?:ISSUE_TEMPLATE/|pull_request_template\.md$|PULL_REQUEST_TEMPLATE)")]),
 ("ops", "Operations and reliability", [
   ("runbook", "Runbooks or operating guides", r"runbooks?|(?:^|/)docs/(?:operations|support|incident)"),
   ("monitor", "Monitoring and alerting as code", r"(?:^|/)(?:alerts?|alerting|monitoring|dashboards?)/[^/]+\.(?:ya?ml|json|tf)$|prometheus|grafana|(?:^|/)sentry\."),
   ("health", "Health checks", r"healthcheck|health[-_]check|(?:^|/)health\.(?:py|js|ts|rb|scala)$")]),
 ("data", "Data practice", [
   ("schemas", "Data schemas", r"\.schema\.json$|(?:^|/)schemas?/[^/]+\.(?:json|ya?ml)$|\.avsc$|\.linkml\.ya?ml$"),
   ("datadict", "Data dictionary or metadata", r"data[-_]?dictionary|(?:^|/)datapackage\.json$|csv-metadata\.json$|\.dcat\.json$"),
   ("datatests", "Data tests", r"(?:^|/)great_expectations/|(?:^|/)soda/|(?:^|/)dbt_project\.yml$|(?:^|/)expectations/"),
   ("migrations", "Managed database migrations", r"(?:^|/)db/migrat(?:e|ions?)/|(?:^|/)alembic/|liquibase|(?:^|/)migrations/V\d")]),
 ("design", "Product and service design", [
   ("prototype", "Prototype", r"(?:^|/)app/views/|govuk-prototype-kit|(?:^|/)prototype"),
   ("designhist", "Design history", r"design[-_]?histor"),
   ("content", "Content or style guidance", r"(?:^|/)content[-_]?(?:guide|design)|style[-_]?guide")]),
]
PRACTICES = [(d[0], p[0], p[1], re.compile(p[2], I)) for d in DISC for p in d[2]]
def classify_type(name, desc, paths):
    n = (name + " " + desc).lower(); ext = collections.Counter(os.path.splitext(p)[1].lower() for p in paths)
    tf = ext[".tf"] + ext[".hcl"]; code = sum(ext[e] for e in (".py", ".js", ".ts", ".rb", ".scala", ".java", ".go", ".cs", ".kt", ".php", ".r"))
    if re.search(r"prototype", n) or any("govuk-prototype-kit" in p or p.startswith("app/views/") for p in paths[:400]) and "prototype" in n: return "Prototype"
    if re.search(r"(?:^|[-_ ])(?:docs?|manual|handbook|guidance|guide|playbook|standards?|way)(?:$|[-_ ])", name.lower()) or (ext[".md"] > 5 and code < 3): return "Documentation or guidance"
    if re.search(r"terraform|infra|ansible|puppet|chef|helm|k8s|kubernetes|deploy|cloudformation|platform-config|aws-|-aws$|concourse|pipelines?$", name.lower()) or (tf > 3 and tf >= code): return "Infrastructure or platform"
    if re.search(r"(?:^|[-_])(?:lib|library|gem|sdk|client|components?|package|plugin|module)(?:$|[-_])", name.lower()): return "Library, component or SDK"
    if re.search(r"(?:^|[-_])api(?:$|[-_])", name.lower()): return "API or backend service"
    if re.search(r"frontend|front-end|(?:^|[-_])(?:web|site|www|ui|admin)(?:$|[-_])", name.lower()): return "Website or user-facing service"
    if ext[".ipynb"] + ext[".rmd"] + ext[".qmd"] > 0 or re.search(r"analysis|analytics|dashboard|statistics|notebook", n): return "Data and analysis"
    if re.search(r"script|tool|cli|utility|utils|bot|automation|action(?:s)?$", name.lower()): return "Tool, script or automation"
    if code: return "Application or service"
    return "Unclassified"
if __name__ == "__main__":
    D = json.load(open(f"{S}/uses/D5.json")); XO = D["xorgs"]
    pids = [p[1] for p in PRACTICES]; out = {}; types = {}
    for a in D["xrows"]:
        o = dict(zip(D["xf"], a)); org = XO[o["oi"]]["org"]; key = f"{org}/{o['n']}"
        try: paths = gzip.open(f"{ENR}/{org}__{o['n']}/tree.gz", "rt", errors="replace").read().splitlines()
        except Exception: types[key] = classify_type(o["n"], o.get("d") or "", []); continue   # no tree: type from name and description (V7-9)
        paths = [p for p in paths if "node_modules/" not in p and "/vendor/" not in p]
        mask = 0
        for i, (_, pid, _, rx) in enumerate(PRACTICES):
            if any(rx.search(p) for p in paths): mask |= 1 << i
        out[key] = mask; types[key] = classify_type(o["n"], o.get("d") or "", paths)
    # catalogue-only records get a type from name and description only
    for a in D["cat"]:
        o = dict(zip(D["cf"], a)); key = f"{XO[o['oi']]['org']}/{o['n']}"
        if key not in types: types[key] = classify_type(o["n"], o.get("d") or "", [])
    res = {"disciplines": [dict(id=d[0], label=d[1], practices=[dict(id=p[0], label=p[1]) for p in d[2]]) for d in DISC], "order": pids, "masks": out, "types": types}
    json.dump(res, open(f"{H}/practices.json", "w"), separators=(",", ":"))
    lines = []
    def ck(cid, ok, text, g=""): lines.append(f"{'PASS' if ok else 'FAIL'} {cid} {text}" + (f" [guards: {g}]" if g else ""))
    R = {p[1]: p[3] for p in PRACTICES}
    ck("C-PRAC-01", len(set(pids)) == len(pids) and len(pids) < 63, f"{len(pids)} practices in {len(DISC)} disciplines, each with a unique id that fits the bitmask", "V7-9")
    ck("C-PRAC-02", bool(R["adr"].search("docs/adr/0001-record-architecture-decisions.md")) and not R["adr"].search("docs/0001-intro.md") and bool(R["ci"].search(".github/workflows/test.yml")) and not R["ci"].search("docs/workflows/test.yml"),
       "practice rules tested: an ADR folder counts and a numbered doc elsewhere doesn't; a workflow outside .github/workflows isn't CI (negative tests)", "V7-9")
    ck("C-PRAC-03", all(t for t in types.values()) and len(types) == len(D["xrows"]) + len(D["cat"]), f"every one of {len(types)} records has exactly one type", "V7-9")
    open(f"{H}/practices_checks.txt", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines)); print("repos with trees", len(out)); print(collections.Counter(types.values()).most_common())
    for i, (d, pid, lab, _) in enumerate(PRACTICES): print(f"  {d:7} {pid:11} {sum(1 for m in out.values() if m >> i & 1):5}  {lab}")
