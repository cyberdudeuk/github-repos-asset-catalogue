"""publiccode.yml agrees with CITATION.cff, names no person and publishes no email address (C-PC-01).

publiccode.yml describes the catalogue to public sector software catalogues. It repeats facts CITATION.cff holds
(version, release date, licence), so it can drift when one is updated and not the other. The official parser
(publiccode-parser-go) checks the schema; this checks what the parser cannot.
Run with python3 -I build/tools/check_publiccode.py [--self-test]. Exits 1 on any problem.
"""
import os, re, sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REQUIRED = ("publiccodeYmlVersion", "name", "url", "platforms", "categories", "developmentStatus", "softwareType",
            "description", "legal", "maintenance", "localisation")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def as_list(v):
    return [str(x) for x in (v if isinstance(v, list) else [v]) if x]


def problems(pc, cff, raw):
    found = [f"missing key: {k}" for k in REQUIRED if k not in pc]
    for pkey, ckey in (("softwareVersion", "version"), ("releaseDate", "date-released")):
        if str(pc.get(pkey, "")) != str(cff.get(ckey, "")):  # both absent is agreement too
            found.append(f"{pkey} does not match CITATION.cff {ckey}")
    licence = str(pc.get("legal", {}).get("license", ""))
    found += [f"legal.license does not include the CITATION.cff licence {c}" for c in as_list(cff.get("license")) if c not in licence]
    if EMAIL.search(raw):
        found.append("an email address is published: contact is by the contact form only")
    if any(set(c) - {"name"} for c in pc.get("maintenance", {}).get("contacts", [])):
        found.append("a maintenance contact carries more than a group name")
    en = pc.get("description", {}).get("en", {})
    if len(en.get("shortDescription", "").strip()) > 150:
        found.append("shortDescription is longer than 150 characters")
    if not en.get("features"):
        found.append("description.en.features is empty")
    return found


def load():
    with open(os.path.join(ROOT, "publiccode.yml"), encoding="utf-8") as f:
        raw = f.read()
    with open(os.path.join(ROOT, "CITATION.cff"), encoding="utf-8") as f:
        cff = yaml.safe_load(f)
    return yaml.safe_load(raw), cff, raw


def self_test():
    pc, cff, raw = load()
    en = dict(pc["description"]["en"])
    cases = {
        "softwareVersion": ({**pc, "softwareVersion": "0.0.0"}, raw),
        "releaseDate": ({**pc, "releaseDate": "1999-01-01"}, raw),
        "legal.license": ({**pc, "legal": {"license": "GPL-3.0-only"}}, raw),
        "email address": (pc, raw + "\n# someone@example.org\n"),
        "maintenance contact": ({**pc, "maintenance": {"type": "community", "contacts": [{"name": "x", "email": "x"}]}}, raw),
        "missing key": ({k: v for k, v in pc.items() if k != "legal"}, raw),
        "features": ({**pc, "description": {"en": {**en, "features": []}}}, raw),
    }
    missed = [label for label, (mutated, text) in cases.items() if not any(label in p for p in problems(mutated, cff, text))]
    for label in missed:
        print(f"self-test: the check did not catch a deliberate break: {label}")
    return 1 if missed else 0


def main():
    found = problems(*load())
    for p in found:
        print(f"C-PC-01 {p}")
    if found:
        return 1
    print("publiccode.yml agrees with CITATION.cff")
    return self_test() if "--self-test" in sys.argv else 0


if __name__ == "__main__":
    sys.exit(main())
