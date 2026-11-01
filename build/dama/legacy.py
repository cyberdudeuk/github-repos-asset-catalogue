"""Legacy data, legacy technology and technical debt signals (7.1).

Inputs: the catalogue records in ../uses/D5.json (name, description, README summary, topics, language, status)
and the parsed dependency manifests in deps/ (names only; versions were not kept, so version-based end-of-life
checks are not possible and are not claimed). Writes legacy.json and legacy_checks.txt. Run with python3 -I.
"""
import glob, json, os, re

S = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(S); I = re.I
B, E = r"(?<![a-z0-9])", r"(?![a-z0-9])"
w = lambda *a: B + "(?:" + "|".join(a) + ")" + E

# id, label, group, plain description, how it is found
SIGS = [
  ("govuk_old", "Retired GOV.UK design libraries", "govuk", "Uses GOV.UK Template, GOV.UK Frontend Toolkit or GOV.UK Elements, which GDS retired in favour of GOV.UK Frontend.", "dependency"),
  ("angularjs", "AngularJS", "tech", "Uses AngularJS (the 'angular' package), whose support ended on 31 December 2021.", "dependency"),
  ("deprecated_js", "Deprecated JavaScript tools", "tech", "Uses a JavaScript tool its makers have deprecated or stopped: Bower, node-sass, TSLint, request, PhantomJS, Protractor or Karma.", "dependency"),
  ("ruby_sass", "Ruby Sass", "tech", "Uses the Ruby 'sass' gem, which reached end of life in 2019.", "dependency"),
  ("old_lang", "Older languages", "lang", "Mainly written in a language few teams now use for new work: CoffeeScript, Pascal, classic ASP or VBA.", "language"),
  ("legacy_about", "About legacy data or systems", "about", "Its name, description or README talks about legacy data or systems, mainframes, decommissioning, data migration or modernisation.", "text"),
  ("self_deprecated", "Says it's deprecated, but still open", "selfdep", "It says it is deprecated, no longer maintained or replaced, but it hasn't been archived.", "text"),
]
SI = {s[0]: i for i, s in enumerate(SIGS)}
DEP = {
  "govuk_old": {("rb", "govuk_template"), ("js", "govuk_template_jinja"), ("js", "govuk_template_mustache"), ("rb", "govuk_frontend_toolkit"), ("js", "govuk_frontend_toolkit"), ("js", "govuk-elements-sass"), ("rb", "govuk_elements_rails")},
  "angularjs": {("js", "angular")},
  "deprecated_js": {("js", "bower"), ("js", "node-sass"), ("js", "tslint"), ("js", "request"), ("js", "phantomjs"), ("js", "phantomjs-prebuilt"), ("rb", "phantomjs"), ("js", "protractor"), ("js", "karma")},
  "ruby_sass": {("rb", "sass")},
}
OLD_LANG = {"CoffeeScript", "Pascal", "ASP", "VBA"}
RX_ABOUT = re.compile(w(r"legacy (?:data|database|databases|systems?|platforms?|applications?|apps?|services?|estate|codebase|code|api|infrastructure)", r"mainframes?", r"decommission\w*",
                        r"data migrations?", r"migrat\w+ (?:data )?(?:from|off|away from) (?:the |a |our )?(?:old|legacy|existing|previous)", r"moderni[sz]\w+(?! platform)(?! ?platform)", r"re-?platform\w*", r"end[- ]of[- ]life (?:software|systems?|technology|versions?|platforms?|services?|hardware|infrastructure)", r"cobol",
                        r"lotus notes", r"ms access", r"access database"), I)
RX_SELF = re.compile(w(r"deprecated", r"no longer (?:maintained|supported|in use|used|updated|active)", r"unmaintained", r"superseded", r"(?:has been|was|is being|now) replaced by", r"do not use", r"obsolete", r"retired"), I)
RX_SELF_NEG = re.compile(w(r"(?:find|finds|finding|detect|detects|list|lists|check|checks|report|reports|flag|flags|warn|warns|remove|removes|removing)s? (?:\w+ ){0,3}(?:deprecated|obsolete|retired)", r"deprecated (?:apis?|actions?|endpoints?|fields?|features?|functions?|methods?) (?:are|were|will be) removed"), I)

def snip(t, m): a = max(0, m.start() - 40); return re.sub(r"\s+", " ", t[a:m.end() + 40]).strip()[:120]
def text_sigs(text, archived):
    out = []; t = text.replace("-", " ").replace("_", " ")
    m = RX_ABOUT.search(t)
    if m: out.append(("legacy_about", snip(t, m)))
    m = RX_SELF.search(t)
    if m and not archived and not RX_SELF_NEG.search(t): out.append(("self_deprecated", snip(t, m)))
    return out

if __name__ == "__main__":
    D = json.load(open(os.path.join(R, "uses", "D5.json"))); XO = D["xorgs"]
    recs = [(dict(zip(D["xf"], a)), ("n", "d", "ld", "t")) for a in D["xrows"]] + [(dict(zip(D["cf"], a)), ("n", "d")) for a in D["cat"]]
    out = {}
    for o, fields in recs:
        key = XO[o["oi"]]["org"] + "/" + o["n"]; s = []
        archived = bool(o.get("ar")) or o.get("st") == "Archived"
        s += text_sigs(" ".join(str(o.get(k) or "") for k in fields), archived)
        if o.get("l") in OLD_LANG: s.append(("old_lang", "main language: " + o["l"]))
        p = os.path.join(S, "deps", key.replace("/", "__", 1) + ".json")
        if os.path.exists(p):
            deps = {(e, n.lower()) for e, n in json.load(open(p))["deps"]}
            for sid, names in DEP.items():
                hit = sorted(n for e, n in deps & names)
                if hit: s.append((sid, "uses " + ", ".join(hit)))
        if s:
            seen = set(); out[key] = [[SI[a], b] for a, b in s if not (a in seen or seen.add(a))]
    checks = []
    def need(ok, cid, text, guards="R34"): checks.append(f"{'PASS' if ok else 'FAIL'} {cid} {text} [guards: {guards}]"); return ok
    need(all(SIGS[i][0] in DEP or SIGS[i][4] != "dependency" for i in range(len(SIGS))) and all(0 <= a[0] < len(SIGS) for v in out.values() for a in v), "C-LEG-01", f"{len(SIGS)} legacy and debt signals, each with a stated way of finding it; {len(out)} repositories have at least one")
    neg = [text_sigs("Legacy Square: a public square in Leeds", False), text_sigs("Tool that finds deprecated GitHub Actions in workflows", False), text_sigs("This repo is deprecated", True), text_sigs("Uses the Dart sass package", False), text_sigs("modernisation platform terraform loadbalancer module", False), text_sigs("Chronic Lung Disease Patients at End of Life", False)]
    pos = [text_sigs("Migrating data from the legacy database to the new platform", False), text_sigs("DEPRECATED: replaced by govuk-frontend", False), text_sigs("Mainframe extract processing", False)]
    need(not any(neg) and all(pos), "C-LEG-02", "text signals need a legacy noun or a self-description: 'Legacy Square', a tool that finds deprecated actions and an archived repo saying it's deprecated the Modernisation Platform (a hosting product's name) and patients at end of life are not flagged; a legacy database migration, a DEPRECATED notice and mainframe processing are (negative tests)")
    need(("js", "sass") not in DEP["ruby_sass"] and ("js", "angular") in DEP["angularjs"] and ("js", "@angular/core") not in DEP["angularjs"], "C-LEG-03", "dependency signals respect the package ecosystem: the Dart 'sass' npm package and modern Angular (@angular/core) are not legacy; the Ruby 'sass' gem and AngularJS are")
    prec = [dict(what="About legacy data or systems, first sample", n=15, true=9, note="the Modernisation Platform (a hosting product) matched 'modernisation'; now excluded"),
            dict(what="About legacy data or systems, second sample", n=15, true=13, note="'end of life' matched a study of patients at end of life (now needs a technology word); Rails 'data migrations' tooling still matches"),
            dict(what="Says it's deprecated, but still open", n=15, true=13, note="two said a folder or some templates were retired, not the repository")]
    json.dump(dict(sigs=[list(s) for s in SIGS], recs=out, prec=dict(judged_by="Claude, 31 October 2026 (not owner-confirmed)", rounds=prec), source=dict(note="Names, descriptions, README summaries, listing language and dependency names read in October 2026. Dependency versions were not kept, so end-of-life versions of languages and frameworks are not detected.")),
              open(os.path.join(S, "legacy.json"), "w"), separators=(",", ":"))
    open(os.path.join(S, "legacy_checks.txt"), "w").write("\n".join(checks) + "\n")
    import collections; c = collections.Counter(SIGS[a[0]][0] for v in out.values() for a in v)
    print("\n".join(checks)); print(len(out), c.most_common())
