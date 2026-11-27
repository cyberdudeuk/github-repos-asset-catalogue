#!/usr/bin/env python3
"""conformance.py: is this repository ready to move into gds-dtx, measured against the GDS Way?

Anyone can run it on any repository and get the same answer:

    python3 -I tools/conformance.py PATH/TO/REPO [--meta meta.json] [--write]
    python3 -I tools/conformance.py --self-test

It reads the repository's files. A few checks need repository settings that only GitHub knows
(visibility, default branch, branch protection, private vulnerability reporting). Pass them in a
small JSON file with --meta. `tools/conformance_meta.sh OWNER/REPO` writes that file using the
GitHub CLI. Without --meta those checks are reported as MANUAL, never as a pass.

Every check names the GDS Way page and section it comes from, the strength the page uses
(MUST, SHOULD, CONSIDER) and the page's last review date, as read in alphagov/gds-way at
commit 7bc40fb (25 November 2026). Checks marked GDS-DTX follow what the gds-dtx organisation
does in its own repositories (gds-dtx/gds-dtx-github-users-tf). They are good practice there,
not GDS Way rules, and they never make a repository "not ready".

Statuses: PASS, FAIL, EXCEPTION (a FAIL with a recorded, dated, referenced decision in
docs/compliance/exceptions.yaml), N/A, MANUAL (needs a person or a settings check).

Verdict:
  READY                 every MUST check passes
  READY WITH EXCEPTIONS every MUST check passes or has a recorded exception
  NOT READY             a MUST check fails with no recorded exception
  INCOMPLETE            no MUST check fails, but a MUST check still needs a person (MANUAL)

--write puts docs/conformance/report.md, result.json, badge.svg and badge.json (for a
shields.io endpoint badge) into the repository, so the evidence sits next to the code.

Standard library only. Each check records the defect or rule that made it exist (DEFECTS), and
--self-test proves every check still fails when its defect is put back.
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import re
import sys
import tempfile

GW = "https://gds-way.digital.cabinet-office.gov.uk/standards/"
SRC = "alphagov/gds-way@7bc40fb (25 Nov 2026)"

# id: (strength, title, source url, page last reviewed)
CHECKS = {
    "SC-01": ("MUST", "README", GW + "source-code/#publish-open-source-code", "2026-03-19"),
    "SC-02": ("MUST", "Informative commit messages", GW + "source-code/#publish-open-source-code", "2026-03-19"),
    "SC-03": ("MUST", "MIT and OGL licence files", GW + "source-code/#publish-open-source-code", "2026-03-19"),
    "SC-04": ("MUST", "An email address for security bug reports", GW + "source-code/#publish-open-source-code", "2026-03-19"),
    "SC-05": ("MUST", "If third parties are affected: changelog, release notes, known issues, semantic version", GW + "source-code/#publish-open-source-code", "2026-03-19"),
    "SC-06": ("SHOULD", "Contributing guidelines", GW + "source-code/#publish-open-source-code", "2026-03-19"),
    "SC-07": ("SHOULD", "Tests run in public CI", GW + "source-code/#publish-open-source-code", "2026-03-19"),
    "GT-01": ("SHOULD", "Default branch is main", GW + "source-code/working-with-git.html#default-branch-name", "2025-02-18"),
    "GT-02": ("SHOULD", "Commit summaries of 50 characters or fewer", GW + "source-code/working-with-git.html#structure", "2025-02-18"),
    "UG-01": ("CONSIDER", "Main branch protected", GW + "source-code/use-github.html#configuring-github-repositories", "2025-07-19"),
    "GA-01": ("MUST", "Third-party actions pinned to a full commit SHA", GW + "source-code/using-github-actions.html#pinning-actions", "2025-08-04"),
    "GA-02": ("MUST", "Workflow permissions set to only what is needed", GW + "source-code/using-github-actions.html#permissions", "2025-08-04"),
    "GA-03": ("MUST", "No risky triggers", GW + "source-code/using-github-actions.html#triggers", "2025-08-04"),
    "GA-04": ("MUST", "No script injection from user-controlled event fields", GW + "source-code/using-github-actions.html#script-injections", "2025-08-04"),
    "GA-05": ("MUST", "No personal access tokens in workflows", GW + "source-code/using-github-actions.html#personal-access-tokens", "2025-08-04"),
    "GA-06": ("MUST", "AWS reached with OIDC, not access keys", GW + "source-code/using-github-actions.html#authenticating-with-aws-and-other-external-services", "2025-08-04"),
    "GA-07": ("CONSIDER", "CODEOWNERS covers .github/workflows", GW + "source-code/using-github-actions.html#user-permissions", "2025-08-04"),
    "TD-01": ("SHOULD", "Automated dependency updates", GW + "tracking-dependencies.html", "2026-09-22"),
    "TD-02": ("SHOULD", "Dependency update cooldown", GW + "tracking-dependencies.html", "2026-09-22"),
    "TD-03": ("SHOULD", "Open update pull request limit of 10 or more", GW + "tracking-dependencies.html", "2026-09-22"),
    "MS-01": ("MUST", "Non-public repositories have HANDLING_INSTRUCTIONS.md", GW + "managing-sensitive-information.html", "2025-10-01"),
    "VD-01": ("SHOULD", "Published sites point security.txt at the Cabinet Office programme", GW + "vulnerability-disclosure.html", "2025-02-18"),
    "AD-01": ("SHOULD", "Architecture decisions recorded", GW + "architecture-decisions.html", "n/a"),
    "DX-01": ("GDS-DTX", "Pre-commit hooks with detect-secrets", "https://github.com/gds-dtx/gds-dtx-github-users-tf/blob/main/.pre-commit-config.yaml", "observed 27 Nov 2026"),
    "DX-02": ("GDS-DTX", "Third-party actions listed for the gds-dtx Actions allowlist", "https://github.com/gds-dtx/gds-dtx-github-users-tf/issues/13", "observed 27 Nov 2026"),
}

DEFECTS = {
    "SC-03": "GDS Way asks for MIT and OGL; a repository with only one would pass a 'has a LICENSE' check",
    "SC-04": "Owner rule (3 Nov 2026): no email address anywhere, so this check can only pass by recorded exception",
    "GA-01": "D20 (catalogue): GDS-owned actions (actions/*, github/*, alphagov/*) count as first party; everything else must be a 40-character SHA",
    "GA-02": "A workflow with no permissions block gets the repository default token, which may be write-all",
    "GA-04": "GDS Way 'Script injections': ${{ github.event.pull_request.title }} inside run: executes attacker text",
    "GA-05": "GDS Way: personal access tokens must not be used; only GITHUB_TOKEN or a GitHub App token",
    "MS-01": "GDS Way: internal or private repositories must carry HANDLING_INSTRUCTIONS.md",
    "GA-03": "D-CONF-02 (found by the self-test, 27 Nov 2026): the on: regex used \\s*, which crossed the newline, so mapping-form triggers such as pull_request_target were missed",
    "GA-04 (env)": "D-CONF-03 (found running on dq-commons and cdo-connect-hub, 27 Nov 2026): env: and with: values were flagged as injection; only run: is executed as script",
    "SC-03/04/05": "D-CONF-04 (found running on private repos, 27 Nov 2026): the GDS Way's 'publish open source code' musts were applied to unpublished code; private and internal repos are judged by MS-01 instead",
    "SC-03 (path)": "D-CONF-05 (found on dam-capability-playbooks, 27 Nov 2026): an OGL file at docs/CONTENT-LICENCE.md was not found",
    "SC-04 (route)": "D-CONF-06 (found on github-repos-asset-catalogue, 27 Nov 2026): SECURITY.md pointed to GitHub private reporting while it was switched off, so the 'no email' exception left no working route",
    "SC-04 (vdp url)": "D-CONF-07 (found on github-repos-asset-catalogue, 27 Nov 2026): a SECURITY.md linking the Cabinet Office programme at gov.uk/help/report-vulnerability was read as having no route",
    "badge": "D-CONF-08 (visual check, 27 Nov 2026): the amber INCOMPLETE badge colour failed WCAG AA contrast with white text",
    "verdict": "D-CONF-01: settings checks without evidence must be MANUAL, never PASS, so a badge cannot overstate readiness",
}

# Check names used by the earlier repository-standards checker, so existing registers keep working (reuse, not re-record).
ALIASES = {"wf_risky_triggers": "GA-03", "licence_mit_ogl": "SC-03", "security_contact": "SC-04", "wf_pin_sha": "GA-01", "wf_permissions": "GA-02"}

# D-CONF-07: the programme's GOV.UK page is as valid a route as its HackerOne-backed host.
VDP_URLS = ("vdp.cabinetoffice.gov.uk", "gov.uk/help/report-vulnerability")

FIRST_PARTY = ("actions/", "github/", "alphagov/", "docker://")
RISKY = ("pull_request_target", "workflow_run", "issue_comment", "issues", "discussion_comment", "discussion", "fork", "watch")
INJECT = re.compile(r"\$\{\{\s*github\.(event\.(issue|pull_request|comment|review|review_comment|discussion|pages|commits|head_commit)[^}]*"
                    r"(title|body|label|ref|message|name|email|page_name|default_branch)|head_ref)\s*\}\}")
USES = re.compile(r"^\s*-?\s*uses:\s*['\"]?([^'\"\s#]+)", re.M)
SHA = re.compile(r"@[0-9a-f]{40}$")
SECRET_REF = re.compile(r"secrets\.([A-Za-z0-9_]+)")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def read(p: pathlib.Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def first(root: pathlib.Path, *names: str) -> pathlib.Path | None:
    for n in names:
        for cand in (root / n, root / ".github" / n, root / "docs" / n):
            if cand.is_file():
                return cand
    return None


def load_exceptions(root: pathlib.Path) -> dict:
    """docs/compliance/exceptions.yaml: an exception counts only with check, rationale, reviewed and reference."""
    text = read(root / "docs" / "compliance" / "exceptions.yaml")
    out, cur = {}, None
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("- check:"):
            cur = {"check": line.split(":", 1)[1].strip().strip("\"'")}
            out.setdefault(cur["check"], []).append(cur)
        elif cur is not None and ":" in line and not line.startswith("#"):
            k, _, v = line.partition(":")
            cur[k.strip()] = v.strip().strip("\"'")
    for old, new in ALIASES.items():  # registers written for the earlier repository-standards checker
        if old in out:
            out.setdefault(new, []).extend(out.pop(old))
    return {k: v for k, v in out.items() if any(all(e.get(f) for f in ("rationale", "reviewed", "reference")) for e in v)}


def workflows(root: pathlib.Path) -> list[tuple[str, str]]:
    d = root / ".github" / "workflows"
    return [(p.name, read(p)) for p in sorted(d.glob("*.y*ml"))] if d.is_dir() else []


def triggers(text: str) -> set[str]:
    """Trigger names from the on: key, in flow, list or mapping form."""
    m = re.search(r"^(?:on|\"on\"|'on'|true):[ \t]*(.*)$", text, re.M)  # [ \t], not \s: \s crossed the newline and hid mapping-form triggers
    if not m:
        return set()
    rest = m.group(1).strip()
    if rest:
        return set(re.findall(r"[a-z_]+", rest))
    out, started = set(), False
    for line in text[m.end():].splitlines():
        if line.strip() and not line.startswith((" ", "\t", "-")):
            break
        started = started or bool(line.strip())
        k = re.match(r"^\s{2}(?:-\s*)?([a-z_]+)\s*:?", line)
        if k and (len(line) - len(line.lstrip())) <= 4:
            out.add(k.group(1))
    return out


def run_lines(text: str) -> list[str]:
    """Lines that the runner executes as a script: a run: value and its indented block.

    D-CONF-03: passing user text through env: is the GDS Way's own safe pattern, so only
    interpolation inside run: counts as injection, not interpolation anywhere in the file."""
    out, block = [], None
    for line in text.splitlines():
        ind = len(line) - len(line.lstrip())
        if block is not None:
            if line.strip() and ind <= block:
                block = None
            else:
                out.append(line)
                continue
        m = re.match(r"^(\s*)(?:-\s*)?run:\s*(.*)$", line)
        if m:
            rest = m.group(2).strip()
            if rest in ("|", ">", "|-", ">-", "|+", ">+", ""):
                block = len(m.group(1))
            else:
                out.append(line)
    return out


def evaluate(root: pathlib.Path, meta: dict | None = None) -> dict:
    meta = meta or {}
    exc = load_exceptions(root)
    res: dict[str, tuple[str, str]] = {}
    wfs = workflows(root)

    def put(cid, ok, evidence, na=False, manual=False):
        if na:
            res[cid] = ("N/A", evidence)
        elif manual:
            res[cid] = ("MANUAL", evidence)
        elif ok:
            res[cid] = ("PASS", evidence)
        elif cid in exc:
            e = exc[cid][0]
            res[cid] = ("EXCEPTION", f"{evidence}. Recorded exception (reviewed {e['reviewed']}): {e['rationale']} [{e['reference']}]")
        else:
            res[cid] = ("FAIL", evidence)

    readme = first(root, "README.md", "README", "README.rst")
    put("SC-01", bool(readme) and len(read(readme).split()) >= 50, f"{readme.relative_to(root)}" if readme else "no README")

    msgs = meta.get("commit_summaries")
    if msgs is None:
        put("SC-02", False, "commit history not supplied (--meta commit_summaries)", manual=True)
        put("GT-02", False, "commit history not supplied", manual=True)
    else:
        weak = [m for m in msgs if len(m.strip()) < 10 or re.fullmatch(r"(?i)(update|fix|wip|changes?|misc|test)( [\w./-]+)?", m.strip())]
        put("SC-02", len(weak) <= len(msgs) * 0.1, f"{len(msgs) - len(weak)} of {len(msgs)} recent summaries say what changed" + (f"; weak: {weak[:3]}" if weak else ""))
        long = [m for m in msgs if len(m) > 50]
        put("GT-02", len(long) <= len(msgs) * 0.2, f"{len(msgs) - len(long)} of {len(msgs)} recent summaries are 50 characters or fewer")

    published = meta.get("visibility", "public") == "public"
    lic = first(root, "LICENSE", "LICENSE.md", "LICENCE", "LICENCE.md")
    # D-CONF-05: the OGL file may sit anywhere at the top level or in docs/ under any *LICEN* name (docs/CONTENT-LICENCE.md was missed)
    ogl = [p for pat in ("*LICEN[CS]E*", "docs/*LICEN[CS]E*") for p in sorted(root.glob(pat)) if p.is_file() and "Open Government Licence" in read(p)]
    mit = bool(lic) and "Permission is hereby granted, free of charge" in read(lic)
    lic_ev = f"MIT: {'yes, ' + lic.name if mit else 'no'}; OGL: {'yes, ' + ogl[0].name if ogl else 'no'}"
    put("SC-03", mit and bool(ogl), lic_ev if published else lic_ev + " (applies once the code is published; D-CONF-04)", na=not published)

    sec = first(root, "SECURITY.md")
    sec_email = bool(sec) and bool(EMAIL.search(read(sec)))
    sec_ev = f"{sec.relative_to(root)} " + ("gives an email address" if sec_email else "has no email address") if sec else "no SECURITY.md"
    pvr = meta.get("private_vulnerability_reporting")
    vdp = bool(sec) and any(u in read(sec) for u in VDP_URLS)
    route = sec_email or vdp or pvr is True
    if not sec_email:
        sec_ev += "; private route: " + ", ".join(x for x, on in (("GitHub private vulnerability reporting", pvr is True), ("Cabinet Office VDP", vdp)) if on) if route else "; no working private route"
    if published and not route:  # D-CONF-06: an exception for 'no email' holds only if another private route works
        res["SC-04"] = ("FAIL", sec_ev + (" (GitHub private vulnerability reporting is off)" if pvr is False else ""))
    else:
        put("SC-04", sec_email, sec_ev if published else sec_ev + " (applies once the code is published)", na=not published)

    chg = first(root, "CHANGELOG.md", "CHANGELOG", "CHANGES.md", "HISTORY.md")
    third = meta.get("third_party_impact")
    if not published:
        put("SC-05", True, "applies once the code is published", na=True)
    elif third is False:
        put("SC-05", True, "owner states no third party depends on it", na=True)
    else:
        semver = bool(re.search(r"\b\d+\.\d+\.\d+\b", read(chg))) if chg else False
        known = bool(meta.get("has_issues", True))
        ok = bool(chg) and semver and known
        put("SC-05", ok, f"changelog: {chg.name if chg else 'none'}; semantic version in it: {'yes' if semver else 'no'}; public issues: {'yes' if known else 'off'}")

    put("SC-06", bool(first(root, "CONTRIBUTING.md", "CONTRIBUTING")), "CONTRIBUTING found" if first(root, "CONTRIBUTING.md", "CONTRIBUTING") else "no CONTRIBUTING file")
    ci = [n for n, t in wfs if triggers(t) & {"push", "pull_request"}]
    put("SC-07", bool(ci), f"CI on push or pull request: {', '.join(ci) or 'none'}")

    br = meta.get("default_branch")
    put("GT-01", br == "main", f"default branch {br}" if br else "not supplied", manual=br is None)
    prot = meta.get("branch_protected")
    put("UG-01", bool(prot), "main is protected (ruleset or branch protection)" if prot else "main is not protected", manual=prot is None)

    if not wfs:
        for cid in ("GA-01", "GA-02", "GA-03", "GA-04", "GA-05", "GA-06", "GA-07", "DX-02"):
            put(cid, True, "no workflows", na=True)
    else:
        third_party, unpinned, noperm, writeall, risky, inj, pats, aws = set(), [], [], [], [], [], [], []
        for name, t in wfs:
            for u in USES.findall(t):
                if u.startswith("./") or u.startswith(FIRST_PARTY):
                    continue
                third_party.add(u.split("@")[0])
                if not SHA.search(u):
                    unpinned.append(f"{name}: {u}")
            if not re.search(r"^permissions:", t, re.M):
                noperm.append(name)
            if re.search(r"permissions:\s*write-all", t):
                writeall.append(name)
            bad = triggers(t) & set(RISKY)
            if bad:
                risky.append(f"{name}: {', '.join(sorted(bad))}")
            for line in run_lines(t):
                if INJECT.search(line):
                    inj.append(f"{name}: {line.strip()[:90]}")
            for s in SECRET_REF.findall(t):
                if re.search(r"PAT\b|PERSONAL|_PAT_|GH_TOKEN_USER", s, re.I):
                    pats.append(f"{name}: secrets.{s}")
                if re.search(r"AWS_(ACCESS|SECRET)", s):
                    aws.append(f"{name}: secrets.{s}")
        put("GA-01", not unpinned, "all third-party actions pinned to a SHA" if not unpinned else f"{len(unpinned)} not pinned: {unpinned[:4]}")
        put("GA-02", not noperm and not writeall, "top-level permissions set in every workflow" if not (noperm or writeall) else f"no top-level permissions: {noperm}; write-all: {writeall}")
        put("GA-03", not risky, "no risky triggers" if not risky else f"risky triggers need a recorded security review: {risky}")
        put("GA-04", not inj, "no user-controlled fields interpolated into commands" if not inj else f"possible injection: {inj[:3]}")
        put("GA-05", not pats, "only GITHUB_TOKEN or app tokens" if not pats else f"personal access tokens: {pats}")
        put("GA-06", not aws, "no AWS access keys" if not aws else f"AWS access keys: {aws}", na=not aws and not any("aws" in t.lower() for _, t in wfs))
        co = first(root, "CODEOWNERS")
        cov = bool(co) and bool(re.search(r"^\s*(\*|/?\.github/|/?\.github/workflows/?)\s+@", read(co), re.M))
        put("GA-07", cov, f"{co.relative_to(root)} covers workflows" if cov else "CODEOWNERS missing or does not cover .github/workflows")
        put("DX-02", True, "third-party actions to allowlist: " + (", ".join(sorted(third_party)) or "none"), manual=bool(third_party))

    dep = first(root, "dependabot.yml", "dependabot.yaml", "renovate.json")
    dtext = read(dep) if dep else ""
    put("TD-01", bool(dep), f"{dep.relative_to(root)}" if dep else "no Dependabot or Renovate config")
    put("TD-02", "cooldown" in dtext or "minimumReleaseAge" in dtext, "cooldown set" if "cooldown" in dtext else "no cooldown")
    limits = [int(x) for x in re.findall(r"open-pull-requests-limit:\s*(\d+)", dtext)]
    put("TD-03", bool(limits) and min(limits) >= 10, f"limit {min(limits)}" if limits else "default limit of 5")

    vis = meta.get("visibility")
    hi = (root / "HANDLING_INSTRUCTIONS.md").is_file()
    if vis == "public":
        put("MS-01", True, "public repository", na=True)
    else:
        put("MS-01", hi, f"{vis or 'visibility not supplied'}; HANDLING_INSTRUCTIONS.md {'present' if hi else 'missing'}", manual=vis is None and not hi)

    pages = meta.get("has_pages")
    st = [p for p in (root / ".well-known" / "security.txt", root / "security.txt", root / "dist" / ".well-known" / "security.txt", root / "public" / ".well-known" / "security.txt") if p.is_file()]
    if pages is False:
        put("VD-01", True, "no published site", na=True)
    else:
        good = any("vdp.cabinetoffice.gov.uk" in read(p) for p in st)
        put("VD-01", good, f"{st[0].relative_to(root)} points at vdp.cabinetoffice.gov.uk" if good else "no security.txt pointing at vdp.cabinetoffice.gov.uk", manual=pages is None and not good)

    adr = [d for d in (root / "docs" / "adr", root / "docs" / "decisions", root / "adr") if d.is_dir() and any(d.iterdir())]
    put("AD-01", bool(adr), f"{adr[0].relative_to(root)}" if adr else "no decision records folder")

    pc = read(root / ".pre-commit-config.yaml")
    put("DX-01", "detect-secrets" in pc, "pre-commit with detect-secrets" if "detect-secrets" in pc else "no pre-commit detect-secrets hook")
    return {"checks": res, "verdict": verdict(res)}


def verdict(res: dict) -> dict:
    must = {c: s for c, (s, _) in res.items() if CHECKS[c][0] == "MUST"}
    should = {c: s for c, (s, _) in res.items() if CHECKS[c][0] in ("SHOULD", "CONSIDER")}
    fails = [c for c, s in must.items() if s == "FAIL"]
    manual = [c for c, s in must.items() if s == "MANUAL"]
    excs = [c for c, s in must.items() if s == "EXCEPTION"]
    if fails:
        v = "NOT READY"
    elif manual:
        v = "INCOMPLETE"
    elif excs:
        v = "READY WITH EXCEPTIONS"
    else:
        v = "READY"
    scored = [s for s in must.values() if s != "N/A"]
    sscored = [s for s in should.values() if s not in ("N/A", "MANUAL")]
    return {"verdict": v, "must_met": sum(s in ("PASS", "EXCEPTION") for s in scored), "must_total": len(scored),
            "should_met": sum(s == "PASS" for s in sscored), "should_total": len(sscored),
            "failing": fails, "manual": manual, "exceptions": excs}


COLOURS = {"READY": "#00703c", "READY WITH EXCEPTIONS": "#1d70b8", "INCOMPLETE": "#8a5a00", "NOT READY": "#d4351c"}


def contrast_white(hex_colour: str) -> float:
    """WCAG contrast of white text on the colour (D-CONF-08: amber #b58840 gave 3.2:1, below AA's 4.5:1)."""
    c = [int(hex_colour.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 1.05 / (0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2] + 0.05)


def badge(v: dict) -> tuple[str, dict]:
    label, msg = "gds-dtx readiness", f"{v['verdict'].lower()} · MUST {v['must_met']}/{v['must_total']}"
    colour = COLOURS[v["verdict"]]
    lw, mw = 7 * len(label) + 10, 7 * len(msg) + 10
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{lw + mw}" height="20" role="img" aria-label="{label}: {msg}">'
           f"<title>{label}: {msg}</title>"
           f'<rect width="{lw}" height="20" fill="#505a5f"/><rect x="{lw}" width="{mw}" height="20" fill="{colour}"/>'
           f'<g fill="#fff" font-family="Verdana,DejaVu Sans,sans-serif" font-size="11">'
           f'<text x="{lw / 2}" y="14" text-anchor="middle">{label}</text><text x="{lw + mw / 2}" y="14" text-anchor="middle">{msg}</text></g></svg>')
    return svg, {"schemaVersion": 1, "label": label, "message": msg, "color": colour.lstrip("#")}


def report(name: str, out: dict, today: str) -> str:
    v = out["verdict"]
    lines = [f"# gds-dtx readiness: {name}", "",
             f"**{v['verdict']}**: {v['must_met']} of {v['must_total']} MUST checks met; {v['should_met']} of {v['should_total']} SHOULD checks met.", "",
             f"Checked on {today} with `tools/conformance.py` from [cyberdudeuk/github-repos-asset-catalogue](https://github.com/cyberdudeuk/github-repos-asset-catalogue/blob/main/tools/conformance.py), "
             f"against the GDS Way as published in {SRC}. Rerun it to check this page is still true.", ""]
    if v["failing"]:
        lines += ["**To be ready, fix:** " + ", ".join(f"{c} ({CHECKS[c][1]})" for c in v["failing"]), ""]
    if v["manual"]:
        lines += ["**Needs a person to confirm:** " + ", ".join(f"{c} ({CHECKS[c][1]})" for c in v["manual"]), ""]
    lines += ["| Check | Strength | What the GDS Way asks | Status | Evidence |", "| --- | --- | --- | --- | --- |"]
    order = {"MUST": 0, "SHOULD": 1, "CONSIDER": 2, "GDS-DTX": 3}
    for cid in sorted(out["checks"], key=lambda c: (order[CHECKS[c][0]], c)):
        s, ev = out["checks"][cid]
        strength, title, url, reviewed = CHECKS[cid]
        lines.append(f"| {cid} | {strength} | [{title}]({url}) (page reviewed {reviewed}) | {s} | {ev.replace('|', '/')} |")
    lines += ["", "## What the statuses mean", "",
              "- **PASS**: the evidence shown meets the check.",
              "- **EXCEPTION**: the check is not met, and a decision with a reason, review date and reference is recorded in `docs/compliance/exceptions.yaml`.",
              "- **FAIL**: not met, and no decision is recorded.",
              "- **MANUAL**: a repository setting or a person has to confirm it. It is never counted as a pass.",
              "- **N/A**: the check does not apply here, for the reason shown.",
              "- **GDS-DTX** checks follow what gds-dtx does in its own repositories. They are good practice, not GDS Way rules, and never decide the verdict.", "",
              "## Do the same for your repository", "",
              "1. Copy `tools/conformance.py` and `tools/conformance_meta.sh` from the catalogue, or run them from a clone of it.",
              "2. `sh tools/conformance_meta.sh OWNER/REPO > meta.json` (needs the GitHub CLI, signed in).",
              "3. `python3 -I tools/conformance.py PATH/TO/REPO --meta meta.json --write`",
              "4. Fix each FAIL, or record a decision for it in `docs/compliance/exceptions.yaml` (check, rationale, reviewed, reference).",
              "5. Commit `docs/conformance/` and add the badge to your README.", ""]
    return "\n".join(lines)


def write(root: pathlib.Path, out: dict, name: str) -> None:
    d = root / "docs" / "conformance"
    d.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    svg, endpoint = badge(out["verdict"])
    (d / "badge.svg").write_text(svg, encoding="utf-8")
    (d / "badge.json").write_text(json.dumps(endpoint, indent=1) + "\n", encoding="utf-8")
    (d / "result.json").write_text(json.dumps({"repo": name, "checked": today, "source": SRC, **out}, indent=1) + "\n", encoding="utf-8")
    (d / "report.md").write_text(report(name, out, today), encoding="utf-8")


def self_test() -> int:
    """Build a repository that passes, then put each defect back and prove the check catches it."""
    good_wf = ("name: ci\non:\n  push:\n  pull_request:\npermissions:\n  contents: read\njobs:\n  t:\n    runs-on: ubuntu-latest\n"
               "    steps:\n      - uses: actions/checkout@v5\n      - uses: astral-sh/setup-uv@" + "a" * 40 + "\n      - run: echo ok\n")
    files = {
        "README.md": "word " * 60, "LICENSE": "MIT License\nPermission is hereby granted, free of charge, to any person",
        "LICENCE-CONTENT.md": "Open Government Licence v3.0", "SECURITY.md": "Report to security" + "@example.org",
        "CHANGELOG.md": "## 1.0.0", "CONTRIBUTING.md": "x", ".github/workflows/ci.yml": good_wf,
        ".github/CODEOWNERS": "* @owner", ".github/dependabot.yml": "open-pull-requests-limit: 10\ncooldown: {default-days: 7}",
        ".well-known/security.txt": "Contact: https://vdp.cabinetoffice.gov.uk", "docs/adr/0001.md": "x",
        ".pre-commit-config.yaml": "detect-secrets",
    }
    meta = {"visibility": "public", "default_branch": "main", "branch_protected": True, "has_pages": True, "private_vulnerability_reporting": True,
            "commit_summaries": ["Add the conformance checker"] * 10}
    breaks = {
        "SC-01": ("README.md", None), "SC-03": ("LICENCE-CONTENT.md", None), "SC-04": ("SECURITY.md", "Use the form"),
        "SC-05": ("CHANGELOG.md", None), "GA-01": (".github/workflows/ci.yml", good_wf.replace("@" + "a" * 40, "@v5")),
        "GA-02": (".github/workflows/ci.yml", good_wf.replace("permissions:\n  contents: read\n", "")),
        "GA-03": (".github/workflows/ci.yml", good_wf.replace("  pull_request:\n", "  pull_request_target:\n")),
        "GA-04": (".github/workflows/ci.yml", good_wf.replace("echo ok", "echo ${{ github.event.pull_request.title }}")),
        "GA-05": (".github/workflows/ci.yml", good_wf.replace("echo ok", "echo ${{ secrets.MY_PAT }}")),
        "TD-03": (".github/dependabot.yml", "cooldown: {}"), "VD-01": (".well-known/security.txt", None),
    }
    fails = []
    with tempfile.TemporaryDirectory() as t:
        root = pathlib.Path(t)

        def build(over=None):
            for p in root.rglob("*"):
                if p.is_file():
                    p.unlink()
            for k, v in {**files, **(over or {})}.items():
                if v is None:
                    continue
                (root / k).parent.mkdir(parents=True, exist_ok=True)
                (root / k).write_text(v, encoding="utf-8")

        build()
        base = evaluate(root, meta)
        if base["verdict"]["verdict"] != "READY":
            fails.append(f"clean fixture is not READY: {base['verdict']} {[(c, s) for c, (s, _) in base['checks'].items() if s not in ('PASS', 'N/A')]}")
        for cid, (path, content) in breaks.items():
            build({path: content})
            s = evaluate(root, meta)["checks"][cid][0]
            if s != "FAIL":
                fails.append(f"{cid} not caught when broken ({s})")
        build({"SECURITY.md": "Use the form"})
        (root / "docs" / "compliance").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "compliance" / "exceptions.yaml").write_text("exceptions:\n  - check: SC-04\n    rationale: owner rule\n    reviewed: 2026-11-27\n    reference: docs/x.md\n")
        r = evaluate(root, meta)
        if r["checks"]["SC-04"][0] != "EXCEPTION" or r["verdict"]["verdict"] != "READY WITH EXCEPTIONS":
            fails.append(f"recorded exception not honoured: {r['checks']['SC-04'][0]} {r['verdict']['verdict']}")
        if evaluate(root, {**meta, "private_vulnerability_reporting": False})["checks"]["SC-04"][0] != "FAIL":
            fails.append("D-CONF-06: 'no email' exception accepted with no working private route")
        (root / "SECURITY.md").write_text("Report through the [programme](https://www.gov.uk/help/report-vulnerability)")
        if evaluate(root, {**meta, "private_vulnerability_reporting": False})["checks"]["SC-04"][0] != "EXCEPTION":
            fails.append("D-CONF-07: GOV.UK vulnerability disclosure page not accepted as a route")
        (root / "docs" / "compliance" / "exceptions.yaml").write_text("exceptions:\n  - check: SC-04\n    rationale: owner rule\n")
        if evaluate(root, meta)["checks"]["SC-04"][0] != "FAIL":
            fails.append("an exception without review date and reference was accepted")
        build()
        r = evaluate(root, {})  # D-CONF-01: no settings evidence
        if r["checks"]["UG-01"][0] != "MANUAL" or r["checks"]["SC-02"][0] != "MANUAL" or r["verdict"]["verdict"] == "READY":
            fails.append(f"missing settings evidence was not MANUAL: {r['verdict']['verdict']}")
        build({".github/workflows/ci.yml": good_wf.replace("      - run: echo ok\n", "      - env:\n          T: ${{ github.event.pull_request.title }}\n        run: |\n          echo \"$T\"\n")})
        if evaluate(root, meta)["checks"]["GA-04"][0] != "PASS":
            fails.append("D-CONF-03: env: passing user text was flagged as injection")
        build({".github/workflows/ci.yml": good_wf.replace("      - run: echo ok\n", "      - run: |\n          echo start\n          echo ${{ github.event.issue.body }}\n")})
        if evaluate(root, meta)["checks"]["GA-04"][0] != "FAIL":
            fails.append("injection inside a multi-line run: block not caught")
        build({"LICENCE-CONTENT.md": None, "docs/CONTENT-LICENCE.md": "Open Government Licence v3.0"})
        if evaluate(root, meta)["checks"]["SC-03"][0] != "PASS":
            fails.append("D-CONF-05: OGL file in docs/CONTENT-LICENCE.md not found")
        build({"LICENCE-CONTENT.md": None})
        priv = evaluate(root, {**meta, "visibility": "private"})
        if priv["checks"]["SC-03"][0] != "N/A" or priv["checks"]["MS-01"][0] != "FAIL":
            fails.append(f"D-CONF-04: private repo judged by publish rules: {priv['checks']['SC-03'][0]}, MS-01 {priv['checks']['MS-01'][0]}")
        build()
        (root / ".github" / "workflows" / "ci.yml").write_text(good_wf.replace("on:\n  push:\n  pull_request:\n", "on: [push, workflow_run]\n"))
        if evaluate(root, meta)["checks"]["GA-03"][0] != "FAIL":
            fails.append("flow-style risky trigger not caught")
    for name, colour in {**COLOURS, "label": "#505a5f"}.items():
        if contrast_white(colour) < 4.5:
            fails.append(f"D-CONF-08: badge colour for {name} ({colour}) is below 4.5:1 with white text")
    for f in fails:
        print("FAIL self-test: " + f)
    print(("PASS" if not fails else "FAIL") + f" self-test: clean fixture READY; {len(breaks)} deliberate breaks, exception rules and missing-evidence rule checked")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    if not argv or argv[0].startswith("-"):
        print(__doc__)
        return 2
    root = pathlib.Path(argv[0]).resolve()
    meta = json.loads(pathlib.Path(argv[argv.index("--meta") + 1]).read_text()) if "--meta" in argv else {}
    name = meta.get("full_name", root.name)
    out = evaluate(root, meta)
    if "--write" in argv:
        write(root, out, name)
    v = out["verdict"]
    print(f"{name}: {v['verdict']} (MUST {v['must_met']}/{v['must_total']}, SHOULD {v['should_met']}/{v['should_total']})"
          + (f"; fix {v['failing']}" if v["failing"] else "") + (f"; confirm {v['manual']}" if v["manual"] else ""))
    return 0 if v["verdict"] in ("READY", "READY WITH EXCEPTIONS") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
