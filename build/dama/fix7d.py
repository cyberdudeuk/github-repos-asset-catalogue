import sys
S = sys.argv[1]
p = S + "/inv/v7_apis.part"; s = open(p).read()
a = '<li>These are matches on names, descriptions, READMEs, dependencies and files, not owner-confirmed. Precision hasn\'t been sampled yet for this view.</li>'
assert a in s
s = s.replace(a, '<li>These are matches on names, descriptions, READMEs, dependencies and files, not owner-confirmed. Precision, from random samples: ${AP.prec.opendata.map(r => `round ${r.round}, ${r.true} of ${r.n} correct (${esc(r.note)})`).join("; ")}.</li>')
a = '<li><b>Named as an API</b>: the repository\'s name ends in "api" or its description says it\'s an API. Common for microservices behind a service; weaker evidence.</li>'
assert a in s
s = s.replace(a, '<li><b>Named as an API</b>: the repository\'s name ends in "api" or its description says it\'s an API. Common for microservices behind a service; weaker evidence. In a random sample ${AP.prec.api_named[0].true} of ${AP.prec.api_named[0].n} were APIs.</li>')
open(p, "w").write(s)
d = open(S + "/inv/docs.py").read(); anc = ' ("V7-4", '
d = d.replace(anc, ''' ("V7-5", "31 Oct · precision review of the open data view", "Medium", "8 of 15 sampled open data matches were correct: 'datastore' matched ordinary databases, such as a service's own data store or a cloud role name.", "A generic word in the portal rule.", "Only open data datastores count (such as the London Datastore); a second sample found 14 of 15 correct.", ["C-OD-01"], "Fixed in 7.0"),
''' + anc, 1)
d = d.replace('["opendata"], ["T-OD-01", "P-27"]', '["opendata"], ["C-OD-01", "T-OD-01", "P-27"]')
open(S + "/inv/docs.py", "w").write(d); print("ok")
