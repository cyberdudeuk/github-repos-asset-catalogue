"""C-FEAT-01: the feature collector parses a GitHub GraphQL page correctly and handles a missing owner (R49).
Writes build/dama/features_checks.txt. Run with python3 -I build/tools/test_collect.py."""
import json, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from collect_features import parse
page = json.load(open(os.path.join(H, "test", "graphql_page.json")))
out, cur = parse(page, "acme")
ok = out == {"acme/alpha": {"issues": True, "projects": False, "wiki": True, "discussions": False, "homepage": True, "archived": False},
             "acme/beta": {"issues": False, "projects": True, "wiki": False, "discussions": True, "homepage": False, "archived": True}} and cur == "Y3Vyc29yOjEwMA=="
neg, ncur = parse({"data": {"repositoryOwner": None}}, "nobody")
line = f"{'PASS' if ok and neg == {} and ncur is None else 'FAIL'} C-FEAT-01 the GitHub feature collector reads Issues, Projects, Wiki, Discussions and homepage from a saved GraphQL page and follows its cursor; negative test: an account GitHub doesn't know gives nothing and stops [guards: R49]"
print(line); open(os.path.join(os.path.dirname(H), "dama", "features_checks.txt"), "w").write(line + "\n")
sys.exit(0 if line.startswith("PASS") else 1)
