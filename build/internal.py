"""Where internal-only inputs live (ADR 0004).

The public repository holds the code, the public data and the open edition of the page. A few inputs are for
government and public sector users only, so they live in the private companion repository,
cyberdudeuk/github-repos-asset-catalogue-internal, at the same relative paths:
the Slack aggregates, the life labels drawn from them, the co-cddo inventory and its migration proposals, the v1
workbook layer, and the handling instructions. Set GHRAC_INTERNAL to a checkout of that repository to build either
edition. Without it, only the scripts that need no internal input can run.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTERNAL_FILES = ["build/dama/collab.json", "build/dama/collab_slack.json", "build/dama/collab_checks.txt", "build/dama/life.json",
                  "build/dama/life_checks.txt", "build/v1/v1_layer.json", "build/v1/v1_checks.txt", "build/inv/data.json", "HANDLING_INSTRUCTIONS.md"]


def base():
    return os.environ.get("GHRAC_INTERNAL", "")


def ipath(rel):
    """Absolute path of an internal file: in the GHRAC_INTERNAL checkout when set, else where it would be in this repository."""
    return os.path.join(base() or ROOT, rel)


def available():
    return bool(base()) and all(os.path.exists(ipath(f)) for f in INTERNAL_FILES if not f.endswith("_checks.txt"))
