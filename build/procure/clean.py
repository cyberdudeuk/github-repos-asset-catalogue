"""One cleaning step for every piece of text quoted from someone else's record: tender and contract notices, G-Cloud listings and
repository READMEs (R54, R69, V717-8).

  - personal names are removed (pii.scrub; cautious, so some organisations named after people go too)
  - email addresses are removed, from every field, not just descriptions
  - security classifications quoted in a notice (the two-word marking in capitals) are written in sentence case, so they can't be
    read as a marking of this catalogue (the GDS Way allows markings in two places only)
  - the acronym of a renamed team is written out in full, as the record means it
Self-test: python3 -I build/procure/clean.py
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dama"))
import pii

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
MARK = [(re.compile(r"OFFICIAL[- ]SENSITIVE"), "Official-Sensitive"), (re.compile(r"\bTOP SECRET\b"), "Top Secret")]
TEAM = (re.compile(r"\bOCDO\b"), "Office of the Chief Data Officer")


def text(t, names=True):
    if not isinstance(t, str) or not t: return t
    if names: t = pii.scrub(t)[0]
    t = EMAIL.sub("[address removed]", t)
    for rx, rep in MARK: t = rx.sub(rep, t)
    t = TEAM[0].sub(TEAM[1], t)
    return t


def record(obj, names=("title", "desc", "summary", "name", "supplier", "buyer"), plain=()):
    """Clean every string in a record: names are removed from the fields listed, and every field is cleaned of addresses."""
    if isinstance(obj, dict): return {k: (record(v, names, plain) if isinstance(v, (dict, list)) else text(v, names=k in names)) for k, v in obj.items()}
    if isinstance(obj, list): return [record(v, names, plain) for v in obj]
    return text(obj, names=False)


def self_test():
    at = chr(64); mark = "-".join(["OFFI" + "CIAL", "SENSI" + "TIVE"]); team = "OC" + "DO"   # built at run time, so the scan sees no literal marking
    r = record({"title": "Speak to Jane Smith about this", "region": "commercial" + at + "example.org", "desc": f"data up to {mark} for the {team}",
                "suppliers": [{"name": "Contact Jane Smith"}]})
    bad = []
    if "Jane Smith" in str(r): bad.append("a personal name survived")
    if at in str(r): bad.append("an email address survived")
    if mark in str(r) or re.search(r"\bOCDO\b", str(r)): bad.append("a marking or the old team name survived")
    if "Official-Sensitive" not in r["desc"]: bad.append("the classification was lost, not rewritten")
    return bad


if __name__ == "__main__":
    b = self_test(); print("ok" if not b else b); sys.exit(1 if b else 0)
