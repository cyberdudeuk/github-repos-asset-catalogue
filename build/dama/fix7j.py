import sys
p = sys.argv[1] + "/dama/practices.py"; s = open(p).read()
def rep(a, b):
    global s; assert s.count(a) == 1, a[:50]; s = s.replace(a, b)
rep(r'''r"(?:^|/)(?:docs/)?(?:adr|adrs|decisions|architecture/decisions|architecture-decision-records?)/[^/]+\.md$|(?:^|/)\d{3,4}-[a-z0-9-]+\.md$(?<=adr/.{0,80})"''', r'''r"(?:^|/)(?:adr|adrs|decisions|architecture-decisions?|architecture/decisions|architecture-decision-records?)/[^/]+\.md$"''')
rep(r'''r"^docs/|^documentation/|(?:^|/)mkdocs\.ya?ml$|(?:^|/)config\.rb$(?<=source/.{0,40})|^source/documentation/"''', r'''r"^docs/|^documentation/|(?:^|/)mkdocs\.ya?ml$|^source/documentation/"''')
rep(''' and not R["health"].search("src/healthy-eating.py") is False,''', ''',''')
open(p, "w").write(s); print("ok")
