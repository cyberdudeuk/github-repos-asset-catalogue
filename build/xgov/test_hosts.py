"""D-SEC-01: a custom domain was detected with endswith("github.io"), so 'evilgithub.io' counted as GitHub Pages.
python3 -I build/xgov/test_hosts.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hosts import is_github_pages

CASES = [("cyberdudeuk.github.io", True), ("github.io", True), ("A.GitHub.IO.", True),
         ("evilgithub.io", False), ("github.io.evil.example", False), ("data.gov.uk", False), ("", False)]
bad = [(h, want) for h, want in CASES if is_github_pages(h) is not want]
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_xgov.py"), encoding="utf-8").read()
uses = "is_github_pages(host)" in src and 'endswith("github.io")' not in src
print(("PASS" if not bad and uses else "FAIL") + f" C-SEC-01 GitHub Pages hosts are matched by whole label ({len(CASES)} cases; wrong: {bad}; build uses the shared test: {uses})   [guards: D-SEC-01]")
sys.exit(0 if not bad and uses else 1)
