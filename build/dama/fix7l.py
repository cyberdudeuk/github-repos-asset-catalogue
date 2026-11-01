import sys
S = sys.argv[1]
def ed(p, pairs, append=None):
    s = open(p).read()
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:70]); s = s.replace(a, b)
    if append: s += append
    open(p, "w").write(s)
ed(S + "/inv/v7_more.part", [("const hasP = (k, p) => { const m = PRC.masks[k]; return m !== undefined && !!(m / Math.pow(2, PIDX[p]) & 1); };", "const hasP = (k, p) => { const m = PRC.masks[k]; return m !== undefined && Math.floor(m / 2 ** PIDX[p]) % 2 === 1; };   /* masks exceed 32 bits, so no bitwise operators */")])
ed(S + "/inv/v7_js1.part", [('tabs:[["practice","How well code is looked after"]]}', 'tabs:[["practice","How well code is looked after"],["practice2","Practice across disciplines"]]}'),
   ('tabs:[["orgs","Organisation profile"],["publishers","All organisations"],["landscape","Recent work across government"]]}', 'tabs:[["orgs","Organisation profile"],["gdsx","GDS estate explorer"],["publishers","All organisations"],["landscape","Recent work across government"]]}'),
   ('const NEW_IN = new Set(["insights", "dama", "suppliers", "apis", "opendata", "gds"]);', 'const NEW_IN = new Set(["insights", "dama", "suppliers", "apis", "opendata", "gds", "practice2", "gdsx"]);'),
   ('  apis:"Every repository', '  practice2:"Good practice beyond engineering: architecture, DevOps, security, testing, documentation, operations, data and design, compared across sectors, types and organisations.",\n  gdsx:"GDS\'s own repositories in alphagov, gds-dtx and its other accounts, seen from any point of view and crossed with any other.",\n  apis:"Every repository'),
   ('blurb:"How well public code is looked after: licences, ownership, security contacts and automated updates."', 'blurb:"How well public code is looked after, across engineering, architecture, DevOps, security, testing, documentation, operations, data and design."')])
ed(S + "/inv/assemble7.sh", [("v7_gds.part v7_js3.part", "v7_gds.part v7_more.part v7_js3.part")])
ed(S + "/inv/v7_js3.part", [('  pc.sort((a, b) => a[0].localeCompare(b[0]));', '''  ck("P-30", Object.keys(PRC.masks).every(k => XBY[k]) && Object.values(PRC.types).every(i => PRC.typeNames[i]) && PORDER.every(p => PLABEL[p] && PD_C[PDISC_OF[p]]), `practice flags for ${nf(Object.keys(PRC.masks).length)} repositories and a type for each of ${nf(Object.keys(PRC.types).length)} records all point at known repositories, types and disciplines`);
  const sample = ALL.filter((x, i) => i % 97 === 0); ck("P-31", XDIMS.every(d => sample.every(x => { const v = d[2](x); return Array.isArray(v) && v.length > 0 && v.every(s => typeof s === "string" && s); })), `every one of ${XDIMS.length} explorer dimensions gives at least one value for every record sampled`);
  pc.sort((a, b) => a[0].localeCompare(b[0]));'''),
   ("window.__app = {GOWN,", "window.__app = {PRC, hasP, discShare, pFiltered, PS, XE, XDIMS, xeFiltered, xeCount, GOWN,")])
ed(S + "/inv/build_v7.py", [('PAGE_CHECKS = ["P-%02d" % i for i in range(1, 30)]', 'PAGE_CHECKS = ["P-%02d" % i for i in range(1, 32)]'),
   ('"T-NAV-01", "T-DRAW-01", "T-GDS-01"]', '"T-NAV-01", "T-DRAW-01", "T-GDS-01", "T-PRAC-01", "T-GDSX-01"]'),
   ('reg_from(os.path.join(DAMAD, "gds_checks.txt"), group="GDS responsibilities")', 'reg_from(os.path.join(DAMAD, "gds_checks.txt"), group="GDS responsibilities")\nreg_from(os.path.join(DAMAD, "practices_checks.txt"), group="Practice across disciplines")'),
   ('gds=json.load(open(os.path.join(DAMAD, "gds.json"))),', 'gds=json.load(open(os.path.join(DAMAD, "gds.json"))), practices=PRAC,'),
   ('# ---------------- v6: colour system', '''PRAC = json.load(open(os.path.join(os.path.dirname(S), "dama", "practices.json")))
_tn = sorted(set(PRAC["types"].values())); PRAC["typeNames"] = _tn; PRAC["types"] = {k: _tn.index(v) for k, v in PRAC["types"].items()}
# ---------------- v6: colour system''')])
ed(S + "/inv/v7_css.part", [], '''
.pdot{display:inline-block;width:12px;height:12px;border-radius:50%;background:var(--hc-ink);margin-right:3px;border:1px solid var(--surface)}
.acctset{border:1px solid var(--line);border-radius:var(--r);margin-top:12px;padding:8px 12px;display:flex;flex-wrap:wrap;gap:6px 18px} .acctset legend{font-weight:700;padding:0 4px} .acctset label{display:flex;gap:6px;align-items:center;min-height:28px}
.xchip{cursor:pointer;min-height:28px;font-size:13px;background:var(--surface)} .xchip:hover{border-color:var(--fg)}
''')
d = open(S + "/inv/docs.py").read()
d = d.replace(' ("R15", "Provide the usual artefact pack', ''' ("R29", "Add to good practice every kind beyond engineering, such as architecture and DevOps.", "Request 22, 31 Oct 2026", ["practice2"], ["C-PRAC-01", "C-PRAC-02", "T-PRAC-01", "P-30"]),
 ("R30", "Add a view like the co-cddo one to explore the repositories under alphagov and gds-dtx in detail from different viewpoints across capabilities, domains, themes, topics, subjects, categories, types and any other relevant classification.", "Request 22, 31 Oct 2026", ["gdsx"], ["C-PRAC-03", "T-GDSX-01", "P-31"]),
 ("R15", "Provide the usual artefact pack''', 1)
d = d.replace(' ("V7-5", ', ''' ("V7-9", "31 Oct · self-found by check C-PRAC-03", "Medium", "Repositories without a file tree got no type, so 4,000 records were missing from the type view.", "The type was assigned after the file tree was read, so a missing tree skipped it.", "Records without a tree get a type from their name and description, or 'Unclassified'.", ["C-PRAC-03"], "Fixed in 7.0"),
 ("V7-5", ''', 1)
open(S + "/inv/docs.py", "w").write(d); print("ok")
