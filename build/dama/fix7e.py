import sys
p = sys.argv[1] + "/inv/v7_new.part"; s = open(p).read()
a = 'const topicHit = (id, x) => !!TOPIC_BY[id]?.rx.test(x.q);'
assert a in s
s = s.replace(a, '''const TOPIC_IX = Object.fromEntries(TOPICS.map((t, i) => [t.id, i]));
const topicBits = x => x._tb || (x._tb = TOPICS.map(t => t.rx.test(x.q)));   /* each record is matched once, then cached (performance, V7-6) */
const topicHit = (id, x) => id in TOPIC_IX ? (x.key !== undefined ? topicBits(x)[TOPIC_IX[id]] : TOPIC_BY[id].rx.test(x.q)) : false;''')
a = '  for (const x of ALL) for (const t of TOPICS) if (t.rx.test(x.q)) {'
assert a in s
s = s.replace(a, '  for (const x of ALL) { const tb = topicBits(x); for (const t of TOPICS) if (tb[TOPIC_IX[t.id]]) {')
a = '''if (b >= 0) s.bodies.add(b); }'''
assert a in s
s = s.replace(a, '''if (b >= 0) s.bodies.add(b); } }''')
open(p, "w").write(s); print("ok")
