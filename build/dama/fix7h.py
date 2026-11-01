import sys
S = sys.argv[1]
p = S + "/inv/v7_gds.part"; s = open(p).read()
a = '<li>A repository can link to more than one area.</li></ul></div>`;'
assert a in s
s = s.replace(a, '<li>A repository can link to more than one area.</li><li>Precision, from random samples judged by ${esc(GD.prec.judged_by)}: ${GD.prec.rounds.map(r => `${esc(r.what)}, ${r.true} of ${r.n} correct (${esc(r.note)})`).join("; ")}.</li></ul></div>`;')
open(p, "w").write(s)
d = open(S + "/inv/docs.py").read()
d = d.replace(' ("V7-5", ', ''' ("V7-8", "31 Oct · precision review of the GDS links", "Low", "11 of 15 sampled links were right: the NHS digital service manual and NHS prototype kit were counted as GDS's Service Manual, and NHS.UK Frontend as GOV.UK Frontend.", "Product names shared across government design systems.", "NHS equivalents excluded; negative tests added.", ["C-GDS-02"], "Fixed in 7.0"),
 ("V7-5", ''', 1)
open(S + "/inv/docs.py", "w").write(d)
t = open(S + "/jt/t6.js").read(); add = open(S + "/jt/t7add.js").read()
t = t.replace("// Harness for explorer6 (from t5)", "// Harness for explorer7 (from t6)").replace("  // merge external results (axe, contrast)", add + "  // merge external results (axe, contrast)", 1)
open(S + "/jt/t7.js", "w").write(t)
a = open(S + "/jt/axe6.js").read()
a = a.replace("if (t === 'orgs')", "if (t === 'dama') { w.__app.damaGo('meta'); await sleep(5); await run('dama-meta'); }\n    if (t === 'gds') { w.__app.GS7.area = 'components'; w.__app.showTab('gds'); await sleep(5); await run('gds'); }\n    if (t === 'orgs')")
open(S + "/jt/axe7.js", "w").write(a); print("ok")
