import sys
p = sys.argv[1] + "/dama/practices.py"; s = open(p).read()
def rep(a, b):
    global s; assert s.count(a) == 1, a[:50]; s = s.replace(a, b)
rep('''        except Exception: continue
        paths = [p for p in paths if "node_modules/" not in p and "/vendor/" not in p]''', '''        except Exception: types[key] = classify_type(o["n"], o.get("d") or "", []); continue   # no tree: type from name and description (V7-9)
        paths = [p for p in paths if "node_modules/" not in p and "/vendor/" not in p]''')
rep('''    return "Other"''', '''    return "Unclassified"''')
rep('''len(types) == len(D["xrows"]) + len({f"{XO[dict(zip(D['cf'], a))['oi']]['org']}/{dict(zip(D['cf'], a))['n']}" for a in D["cat"]} - set(out))''', '''len(types) == len(D["xrows"]) + len(D["cat"])''')
open(p, "w").write(s); print("ok")
