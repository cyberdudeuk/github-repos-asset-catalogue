import sys, re
S = sys.argv[1]
def ed(p, pairs):
    s = open(p).read()
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:70]); s = s.replace(a, b)
    open(p, "w").write(s)
ed(S + "/inv/v7_gds.part", [('<div class="gtiles">', '<div class="tiles gtiles">')])
ed(S + "/inv/v7_js1.part", [('tabs:[["insights","Analytics dashboard"],["dama","Data management wheel"],["suppliers","Data tools and suppliers"]]}', 'tabs:[["insights","Analytics dashboard"],["dama","Data management wheel"],["suppliers","Data tools and suppliers"],["gds","GDS responsibilities and connections"]]}'),
   ('const NEW_IN = new Set(["insights", "dama", "suppliers", "apis", "opendata"]);', 'const NEW_IN = new Set(["insights", "dama", "suppliers", "apis", "opendata", "gds"]);'),
   ('  apis:"Every repository', '  gds:"What GDS is responsible for, the code it builds for each area, where the rest of the public sector builds on it, and every way to explore the catalogue.",\n  apis:"Every repository')])
ed(S + "/inv/assemble7.sh", [("v7_apis.part v7_js3.part", "v7_apis.part v7_gds.part v7_js3.part")])
ed(S + "/inv/v7_js3.part", [('  pc.sort((a, b) => a[0].localeCompare(b[0]));', '''  ck("P-29", GOWN.every(r => GA[r.a] || r.a === "other") && GLINK.every(r => r.h.every(h => GA[h.a])) && !GLINK.some(r => GD.owned[r.key]), `every one of ${nf(GOWN.length)} GDS repositories and ${nf(GLINK.length)} linked repositories sits in a known GDS area, and none is counted on both sides`);
  pc.sort((a, b) => a[0].localeCompare(b[0]));'''),
   ("window.__app = {DREC,", "window.__app = {GOWN, GLINK, GS7, g7Filtered, VIEW_TYPES, DREC,")])
ed(S + "/inv/build_v7.py", [('PAGE_CHECKS = ["P-%02d" % i for i in range(1, 29)]', 'PAGE_CHECKS = ["P-%02d" % i for i in range(1, 30)]'),
   ('"T-NAV-01", "T-DRAW-01"]', '"T-NAV-01", "T-DRAW-01", "T-GDS-01"]'),
   ('reg_from(os.path.join(DAMAD, "extra_checks.txt"), group="APIs and open data")', 'reg_from(os.path.join(DAMAD, "extra_checks.txt"), group="APIs and open data")\nreg_from(os.path.join(DAMAD, "gds_checks.txt"), group="GDS responsibilities")'),
   ('opendata=json.load(open(os.path.join(DAMAD, "opendata.json"))),', 'opendata=json.load(open(os.path.join(DAMAD, "opendata.json"))), gds=json.load(open(os.path.join(DAMAD, "gds.json"))),')])
ed(S + "/dama/gds.py", [('w(r"digital marketplace", r"g-?cloud", r"digital outcomes and specialists",', 'w(r"digital marketplace", r"g-cloud(?: ?\\d+| framework)?", r"digital outcomes and specialists",')])
css = '''
/* GDS connections */
.gtiles .tile-n b{font-size:1.4rem}
.net .nlink{fill:none;stroke:var(--hc);opacity:.55} .net .nlink.dim{opacity:.08} .net .nlink:hover{opacity:.9}
.net .nbox{fill:var(--hc-soft);stroke:var(--hc-ink);stroke-width:1.5} .net .nl{fill:var(--fg);font:600 13px var(--f-body)}
.net .nnode[role=button]{cursor:pointer;outline:none} .net .nnode.sel .nbox,.net .nnode[role=button]:focus-visible .nbox{stroke:var(--fg);stroke-width:3}
.dimlist{columns:2 320px;padding-left:18px;margin:6px 0 0} .dimlist li{margin-bottom:4px;break-inside:avoid}
'''
open(S + "/inv/v7_css.part", "a").write(css)
d = open(S + "/inv/docs.py").read()
d = d.replace(' ("R15", "Provide the usual artefact pack', ''' ("R28", "Identify the kinds of view available to explore repositories by the capabilities, domains, themes, topics and subjects that government data, cyber, digital and technology are responsible for, including digital transformation and digital products and services, and connect them to the corresponding GDS units.", "Request 21, 31 Oct 2026", ["gds"], ["C-GDS-01", "C-GDS-02", "C-GDS-03", "T-GDS-01", "P-29"]),
 ("R15", "Provide the usual artefact pack''', 1)
d = d.replace(' ("V7-5", ', ''' ("V7-6", "31 Oct · self-found when the test harness timed out", "Medium", "The analytics dashboard took 1.8 seconds to draw in Chrome (much longer in the test harness) because every chart re-ran 15 topic patterns against every record.", "Topic membership recomputed on every call.", "Each record is matched against the topics once and the result kept.", ["T-INS-01"], "Fixed in 7.0"),
 ("V7-7", "31 Oct · self-found reviewing the GDS links", "Medium", "About 100 repositories were linked to digital procurement because 'gcloud', Google Cloud's command-line tool, matched the G-Cloud framework.", "An optional hyphen in the G-Cloud pattern.", "G-Cloud only matches with its hyphen; GDS links need a product's own name (negative tests).", ["C-GDS-02", "C-GDS-01"], "Fixed in 7.0"),
 ("V7-5", ''', 1)
open(S + "/inv/docs.py", "w").write(d); print("ok")
