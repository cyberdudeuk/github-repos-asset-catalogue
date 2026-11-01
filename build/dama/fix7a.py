import sys
S = sys.argv[1]
p = S + "/dama/extra.py"; s = open(p).read()
a = '                        if rt: j = len(at & rt) / len(at | rt); sc.append((j, k))'
assert a in s
s = s.replace(a, '''                        if rt:
                            if len(at) == 1 and rt != at: continue   # a one-word API name only matches a repository named the same (V7-4)
                            j = len(at & rt) / len(at | rt); sc.append((j, k))''')
s = s.replace('(c["match"][1] == 1.0 and c["match"][0].lower() in allkeys)', '(c["match"][2].startswith("linked") and c["match"][0].lower() in allkeys)')
s = s.replace('''    ck("C-API-04",''', '''    ck("C-API-05", not any(c["match"] and not c["match"][2].startswith("linked") and len(tok(c["name"])) == 1 and tok(c["match"][0].split("/")[1]) != tok(c["name"]) for c in uniq), "a one-word API name (such as 'Pay') only matches a repository with the same name, never a longer one such as pay-webhooks", "V7-4")
    ck("C-API-04",''')
open(p, "w").write(s)
p = S + "/inv/v7_apis.part"; s = open(p).read()
a = 'status: !c.match ? "none" : c.match[1] >= 1 ? "linked" : c.match[1] >= .5 ? "matched" : "possible"'
assert a in s; s = s.replace(a, 'status: !c.match ? "none" : c.match[2].startsWith("linked") ? "linked" : c.match[1] >= .5 ? "matched" : "possible"')
a = '${c.match[1] < 1 ? ` · ${Math.round(c.match[1] * 100)}% of words shared` : ""}'
assert a in s; s = s.replace(a, '${c.status !== "linked" ? ` · ${Math.round(c.match[1] * 100)}% of words shared` : ""}')
open(p, "w").write(s)
p = S + "/inv/v7_insights.part"; s = open(p).read()
def rep(a, b):
    global s; assert s.count(a) == 1, a[:60]; s = s.replace(a, b)
rep('const W = Math.max(320, cats.length * 34),', 'const W = Math.max(720, cats.length * 48),')
rep('''${esc(words.slice(0, Math.ceil(words.length / 2)).join(" "))}</tspan><tspan x="${lx.toFixed(1)}" dy="13">${esc(words.slice(Math.ceil(words.length / 2)).join(" "))}''', '''${esc(words[0])}</tspan><tspan x="${lx.toFixed(1)}" dy="13">${esc(words.slice(1).join(" "))}''')
rep('''daYear = ["dq", "meta", "integ", "dwbi", "sec", "ref"].map(a => ({name: DAREA[a].short, c: {dq: "blue", meta: "violet", integ: "aqua", dwbi: "green", sec: "red", ref: "magenta"}[a],''', '''daYear = ["dq", "meta", "integ", "dwbi", "sec", "ref"].map(a => ({name: DAREA[a].short, c: AREA_C[a],''')
a = '''  ${chartPanel("Who publishes most",'''
j = s.index('''  ${chartPanel("Programming languages",'''); k = s.index('''  ${chartPanel("Good practice by sector",''')
langlic = s[j:k]; s = s[:j] + s[k:]
s = s.replace(a, '''  ${chartPanel("How active is the code", statusStack(L, "Activity status of the selected code projects"), {lede: "Every selected project by its activity status today."})}
''' + langlic + a, 1)
open(p, "w").write(s)
p = S + "/inv/v7_js1.part"; s = open(p).read()
a = 'esc(g.h.textContent.trim().slice(0, 60))'
assert a in s; s = s.replace(a, 'esc(g.h.textContent.trim().length > 64 ? g.h.textContent.trim().slice(0, 62) + "…" : g.h.textContent.trim())')
open(p, "w").write(s); print("ok")
