"""Host tests shared by the xgov build and its regression test (CodeQL #1, D-SEC-01)."""


def is_github_pages(host):
    """True for github.io itself or a site under it. Compares whole labels: 'evilgithub.io' is not GitHub Pages."""
    host = (host or "").lower().rstrip(".")
    return host == "github.io" or host.endswith(".github.io")
