"""No tracked file may hold an unresolved merge (V718-3).  python3 -I build/tools/check_conflicts.py
A merge that stops on conflicts leaves marker lines in files; if they are committed, Python files stop parsing and pages
break. Every file git tracks is read, and any line that starts with a conflict marker fails. Writes build/inv/git_checks.txt."""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MARK = re.compile(r"^(?:<{7}|>{7})(?: |$)", re.M)


def conflicted(text):
    return bool(MARK.search(text))


def main():
    files = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True).stdout.split("\0")
    bad = []
    for f in filter(None, files):
        p = os.path.join(ROOT, f)
        try: t = open(p, encoding="utf-8").read()
        except (UnicodeDecodeError, IsADirectoryError, FileNotFoundError): continue
        if conflicted(t): bad.append(f)
    lt, gt = "<" * 7, ">" * 7
    neg = conflicted(f"a\n{lt} HEAD\nb\n{'=' * 7}\nc\n{gt} origin/main\n") and not conflicted("Heading\n=======\n<<< not a marker\n")
    line = ("PASS " if not bad and neg else "FAIL ") + f"C-GIT-01 no tracked file holds an unresolved merge ({len([f for f in files if f])} files read; with markers: {bad[:5]}); negative tests catch a conflict and leave a heading underline alone   [guards: V718-3]"
    open(os.path.join(ROOT, "build", "inv", "git_checks.txt"), "w").write(line + "\n")
    print(line)
    return 0 if not bad and neg else 1


if __name__ == "__main__":
    sys.exit(main())
