import sys
S = sys.argv[1]
def ed(p, pairs):
    s = open(p).read()
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:70]); s = s.replace(a, b)
    open(p, "w").write(s)
ed(S + "/inv/v7_insights.part", [
  ('const DREC = DM.recs.map(([key, caps, vend, mask]) => ({key, x: XBY[key], caps: caps.map(([i, k, s]) => ({i, k, s, a: capArea(i)})), vend: vend.map(([i, k, s]) => ({i, k, s})), mask})).filter(r => r.x);\nconst DBY = Object.fromEntries(DREC.map(r => [r.key, r]));',
   'const DRECALL = DM.recs.map(([key, caps, vend, mask]) => ({key, x: XBY[key], caps: caps.map(([i, k, s]) => ({i, k, s, a: capArea(i)})), vend: vend.map(([i, k, s]) => ({i, k, s})), mask})).filter(r => r.x);\n/* DREC: records with a DAMA capability match; DRECALL also holds records matched only by a supplier, used by the suppliers view (V7-10) */\nconst DREC = DRECALL.filter(r => r.caps.length);\nconst DBY = Object.fromEntries(DRECALL.map(r => [r.key, r]));'),
  ('function vUse(i) { const minS = +VS.strength; return DREC.filter(', 'function vUse(i) { const minS = +VS.strength; return DRECALL.filter('),
  ('DREC.every(r => r.vend.every(v => DV[v.i]))', 'DRECALL.every(r => r.vend.every(v => DV[v.i]))') if False else ('const DCAPS = DM.caps,', 'const DCAPS = DM.caps,') if False else ('const DM = DATA.dama,', 'const DM = DATA.dama,')])
ed(S + "/inv/v7_more.part", [('return r ? [...new Set(r.caps.map(c => DAREA[c.a].label))] : ["No data management evidence"]; }],', 'return r && r.caps.length ? [...new Set(r.caps.map(c => DAREA[c.a].label))] : ["No data management evidence"]; }],')])
s = open(S + "/inv/v7_js3.part").read()
s = s.replace("DREC.every(r => r.vend.every(v => DV[v.i]))", "DRECALL.every(r => r.vend.every(v => DV[v.i]))"); open(S + "/inv/v7_js3.part", "w").write(s)
s = open(S + "/inv/v7_insights.part").read()
s = s.replace('const dqTools = DV.map((v, i) => [v, DREC.filter(r => r.vend.some(w => w.i === i))])', 'const dqTools = DV.map((v, i) => [v, DRECALL.filter(r => r.vend.some(w => w.i === i))])')
open(S + "/inv/v7_insights.part", "w").write(s)
d = open(S + "/inv/docs.py").read()
d = d.replace(' ("V7-5", ', ''' ("V7-10", "31 Oct · self-found by page check P-31", "Medium", "Repositories matched only by a supplier (for example code using MongoDB, with no data management capability) were counted as having data management evidence, and the explorer gave them no data management value.", "One list served two meanings: capability matches and supplier matches.", "Two lists: capability matches for the wheel and counts; all matches for the suppliers view.", ["P-31", "P-25"], "Fixed in 7.0"),
 ("V7-5", ''', 1)
open(S + "/inv/docs.py", "w").write(d); print("ok")
