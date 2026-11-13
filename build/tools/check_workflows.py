"""No workflow step may stop on an error it hides (V718-5).  python3 -I build/tools/check_workflows.py
GitHub runs each 'run:' block with 'bash -e', so a command that fails stops the step there. If that command's error
output is also sent to /dev/null, the step fails with only 'exit code 1' and nothing to say why: that is how the weekly
health report never got written, because 'gh label create' fails once the label exists. Every 'run:' block in
.github/workflows is read:
  - 'gh label create' must be idempotent ('--force') or handle its failure ('||');
  - a command that hides its errors ('2>/dev/null' or '&>/dev/null') must handle its failure on the same line ('||'),
    unless the block has turned off stopping on errors ('set +e') before it.
Negative tests feed in the line that had the defect and check that it fails. Writes build/inv/workflow_checks.txt."""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HIDE = re.compile(r"(?:2|&)>\s*/dev/null")
RUN = re.compile(r"^(\s*)(?:-\s+)?run:\s*(.*)$")


def run_blocks(text):
    """Yield (first line number, [lines]) for each run: value, block or single line."""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        m = RUN.match(lines[i])
        if not m:
            i += 1
            continue
        start, ind, val = i + 1, len(m.group(1)), m.group(2).strip()
        if val and val[0] not in "|>":
            yield start, [val]
            i += 1
            continue
        body, i = [], i + 1
        while i < len(lines) and (not lines[i].strip() or len(lines[i]) - len(lines[i].lstrip()) > ind):
            body.append(lines[i].strip())
            i += 1
        yield start + 1, body


def problems(lines):
    """Lines of one run: block that stop the step on an error they hide, or that fail on a second run."""
    out, errexit = [], True
    for n, line in enumerate(lines):
        code = line.split(" #", 1)[0]
        if re.search(r"\bset\s+\+e\b", code): errexit = False
        if re.search(r"\bset\s+-e\b", code): errexit = True
        for cmd in re.split(r";|&&|\bthen\b|\belse\b", code):
            if "gh label create" in cmd and "--force" not in cmd and "||" not in code:
                out.append((n, "gh label create fails once the label exists: add --force"))
            if errexit and HIDE.search(cmd) and "||" not in code:
                out.append((n, "the error is hidden and stops the step: handle it with ||, or let it show"))
    return out


def scan(root=ROOT):
    bad = []
    files = sorted(glob.glob(os.path.join(root, ".github", "workflows", "*.y*ml")))
    for f in files:
        for start, body in run_blocks(open(f, encoding="utf-8").read()):
            for n, why in problems(body):
                bad.append(f"{os.path.relpath(f, root)}:{start + n}: {why}")
    return files, bad


def negative_tests():
    had = 'else gh label create health --color 0B0C0C --description "Weekly self-routines report" 2>/dev/null; gh issue create --label health; fi'
    fixed = 'else gh label create health --color 0B0C0C --description "Weekly self-routines report" --force; gh issue create --label health; fi'
    yml = "jobs:\n  a:\n    steps:\n      - run: |\n          n=1\n          " + had + "\n      - run: echo ok\n"
    return (len(problems([had])) == 2 and problems([fixed]) == []
            and problems(["rm x 2>/dev/null || true"]) == [] and problems(["set +e", "rm x 2>/dev/null"]) == []
            and [len(b) for _, b in run_blocks(yml)] == [2, 1] and problems(list(run_blocks(yml))[0][1]) != [])


def main():
    files, bad = scan()
    neg = negative_tests()
    ok = not bad and neg and bool(files)
    line = ("PASS " if ok else "FAIL ") + f"C-WF-01 no workflow step stops on an error it hides ({len(files)} workflows read; problems: {bad[:5]}); negative tests catch the label step that stopped the weekly health report   [guards: V718-5]"
    open(os.path.join(ROOT, "build", "inv", "workflow_checks.txt"), "w").write(line + "\n")
    print(line)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
