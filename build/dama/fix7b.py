import sys
p = sys.argv[1] + "/inv/docs.py"; d = open(p).read()
anc = ' ("V7-3", '
d = d.replace(anc, ''' ("V7-4", "31 Oct · self-found checking the API view in a browser", "Medium", "GOV.UK Pay was matched to a webhooks repository because one-word API names shared half their words with any longer name, and name matches scoring 100% were labelled as links from the catalogue.", "Similarity on very short names, and the match type read from the score instead of how the match was made.", "A one-word API name only matches a repository with the same name; the label comes from how the match was made.", ["C-API-05", "C-API-02"], "Fixed in 7.0"),
''' + anc, 1)
d = d.replace('["C-API-01", "C-API-02", "C-API-03", "C-API-04", "T-API-01", "P-26"]', '["C-API-01", "C-API-02", "C-API-03", "C-API-04", "C-API-05", "T-API-01", "P-26"]')
open(p, "w").write(d); print("ok")
