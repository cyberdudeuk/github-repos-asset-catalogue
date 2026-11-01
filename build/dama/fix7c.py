import sys
p = sys.argv[1] + "/dama/extra.py"; s = open(p).read()
a = 'w(r"open ?data portal", r"data ?store", r"data portal",'
assert a in s; s = s.replace(a, 'w(r"open ?data portal", r"open data ?store", r"data portal",')
a = '''    ck("C-API-04",'''
s = s.replace(a, '''    PORTAL = OD[2][2]
    ck("C-OD-01", not re.search(PORTAL, "stored in a datastore so the agent can", I) and not re.search(PORTAL, "roles/datastore.user", I) and re.search(PORTAL, "publishes to the London Datastore", I), "a generic 'datastore' (a database) isn't an open data portal; the London Datastore still is (negative and positive tests)", "V7-5")
''' + a, 1)
open(p, "w").write(s); print("ok")
