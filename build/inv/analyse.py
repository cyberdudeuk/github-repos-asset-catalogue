"""One rule for telling automated commits from people's commits, used by every layer (defect V717-1: it was never committed).

is_bot(name, email) is True for an author that is a known automation account or that names itself a bot.
It is deliberately narrow: a person whose name merely contains "bot" (for example "Abbott") is not a bot.
Self-test: python3 -I build/inv/analyse.py
"""
import re

_BOT_NAMES = re.compile(r"""(?ix)^(?:
      .*\[bot\]
    | dependabot(?:-preview)?
    | renovate(?:-bot)?
    | github-actions
    | github\ action(?:s)?
    | actions-user
    | snyk(?:-bot)?
    | greenkeeper(?:io)?
    | pre-commit-ci(?:-lite)?
    | allcontributors
    | semantic-release-bot
    | mergify
    | imgbot
    | pyup(?:-bot|\.io\ bot)?
    | deepsource-autofix
    | codecov(?:-io)?
    | stale
    | (?:.*[\s_-])?bot
)$""")
_BOT_EMAILS = re.compile(r"""(?ix)(?:
      \[bot\]@
    | ^(?:\d+\+)?dependabot
    | ^(?:\d+\+)?renovate
    | ^(?:\d+\+)?github-actions
    | ^action@github\.com$
    | ^actions@github\.com$
    | ^noreply@github\.com$
    | ^bot@renovateapp\.com$
    | ^support@dependabot\.com$
    | ^(?:\d+\+)?snyk-bot
    | ^(?:.*[._+-])?bot@
)""")


def is_bot(name, email=""):
    n = (name or "").strip(); e = (email or "").strip()
    return bool(_BOT_NAMES.match(n) or _BOT_EMAILS.search(e))


def self_test():
    at = chr(64)   # addresses are built here, so no email address is written anywhere in the repository (R69)
    e = lambda local, host: local + at + host
    bots = [("dependabot[bot]", e("49699333+dependabot[bot]", "users.noreply.github.com")), ("github-actions[bot]", e("41898282+github-actions[bot]", "users.noreply.github.com")),
            ("Renovate Bot", e("bot", "renovateapp.com")), ("GitHub Action", e("action", "github.com")), ("snyk-bot", e("snyk-bot", "snyk.io")),
            ("pre-commit-ci[bot]", e("66853113+pre-commit-ci[bot]", "users.noreply.github.com")), ("govuk-ci", e("govuk-ci-bot", "example.gov.uk")), ("release bot", e("release-bot", "example.org"))]
    people = [("Jane Abbott", e("jane.abbott", "example.gov.uk")), ("Robert Botham", e("rb", "example.org")), ("A Person", e("12345+someone", "users.noreply.github.com")),
              ("Talbot", e("talbot", "example.org")), ("Botond Kovacs", e("botond", "example.org"))]
    bad = [p for p in bots if not is_bot(*p)] + [p for p in people if is_bot(*p)]
    return bad


if __name__ == "__main__":
    b = self_test()
    print("ok" if not b else f"wrong: {b}")
    raise SystemExit(1 if b else 0)
