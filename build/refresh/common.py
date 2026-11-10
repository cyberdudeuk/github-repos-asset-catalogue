"""Shared settings for the data refresh (R75): the reference date, where inputs live, and safe git calls.

Every refresh step reads its dates from asof.json, so one edit moves the whole catalogue to a new snapshot.
Repositories are only ever read with git (ls-remote, and bare clones of commit history without file contents).
Nothing from a repository is executed: git runs with hooks off, no credential prompt and no system or global config.
"""
import datetime as dt
import gzip
import json
import os
import subprocess

H = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.dirname(H)
ASOF = json.load(open(os.path.join(H, "asof.json")))
REF = dt.datetime.fromisoformat(ASOF["ref"] + "T12:00:00+00:00")
REFE = int(REF.timestamp())
PREV = ASOF["previous"]


def cut(days):
    return REFE - days * 86400


def ep(s):
    return int(dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()) if s else None


def long_date(d):
    d = dt.date.fromisoformat(d) if isinstance(d, str) else d
    return f"{d.day} {d.strftime('%B %Y')}"


GIT_ENV = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_ASKPASS="/bin/false", SSH_ASKPASS="/bin/false", GIT_CONFIG_NOSYSTEM="1",
               GCM_INTERACTIVE="never", GIT_LFS_SKIP_SMUDGE="1")


def git(args, cwd=None, timeout=120):
    """Run git safely; returns (returncode, stdout, stderr). Hooks are disabled for every call."""
    try:
        p = subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "-c", "credential.helper=", "-c", "protocol.file.allow=never"] + args,
                           cwd=cwd, env=GIT_ENV, capture_output=True, text=True, errors="replace", timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


def read_json(path):
    if path.endswith(".gz"):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return json.load(f)
    return json.load(open(path, encoding="utf-8"))


def write_json_gz(path, obj):
    with gzip.GzipFile(path, "wb", mtime=0) as f:   # mtime 0: the same data gives the same bytes
        f.write(json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8"))
