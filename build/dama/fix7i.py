import sys, re
p = sys.argv[1] + "/inv/v7_insights.part"; s = open(p).read()
a = 'const yOf = x => x.cr ? new Date(x.cr * 1000).getUTCFullYear() : null, grp = x => live(x) ? 0 : x.st === "Archived" ? 2 : 1;'
assert a in s
s = s.replace(a, '''const yOf = x => x._y !== undefined ? x._y : (x._y = x.cr ? new Date(x.cr * 1000).getUTCFullYear() : null), grp = x => live(x) ? 0 : x.st === "Archived" ? 2 : 1;   /* year cached per record (V7-6) */
  const yc = [{}, {}, {}]; for (const x of L) { const y = yOf(x); if (y) { const k = Math.max(2010, y); yc[grp(x)][k] = (yc[grp(x)][k] || 0) + 1; } }''')
i = s.index('  const ser = [["Live now", "green"]'); j = s.index("\n", i)
s = s[:i] + '  const ser = [["Live now", "green"], ["Dormant or inactive now", "orange"], ["Archived", "slate"]].map(([n, c], gi) => ({name: n, c, values: years.map(y => yc[gi][y] || 0)}));' + s[j:]
a = '  const bodies = BODIES.map((b, i) => { const rs = L.filter(x => XO[x.oi]?.body === i); return {i, b, n: rs.length, live: rs.filter(live).length}; }).filter(d => d.n);'
assert a in s
s = s.replace(a, '  const bm = {}; for (const x of L) { const bi = XO[x.oi]?.body; if (bi >= 0) { const o = bm[bi] || (bm[bi] = {n: 0, live: 0}); o.n++; if (live(x)) o.live++; } }\n  const bodies = Object.entries(bm).map(([i, o]) => ({i: +i, b: BODIES[+i], n: o.n, live: o.live}));')
open(p, "w").write(s); print("ok")
