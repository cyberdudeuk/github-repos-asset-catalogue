# ADR 0004: A public repository and a private companion

Status: accepted, 2 November 2026. This supersedes the "Next step" in ADR 0002.

## Context

The owner made this repository public on 2 November 2026. The GDS Way makes public the default for code. Some inputs, though, are only for government and public sector users:

- **Slack counts:** how often public repositories are linked from government Slack workspaces, with the names of public channels. The workspace owners haven't agreed to share these beyond government.
- **Life labels drawn from those counts:** for example, "Seen in live operations".
- **The co-cddo move:** the inventory with its proposed destinations and rationales, and the v1 migration workbook layer. The repositories' owners haven't agreed these proposals.

## Decision

- **This repository** holds the code, the public data and the open edition of the page (`dist/index.html`, published to GitHub Pages).
- **The private companion, cyberdudeuk/github-repos-asset-catalogue-internal,** holds the internal-only inputs at the same paths, with HANDLING_INSTRUCTIONS.md. `build/internal.py` lists those paths. `GHRAC_INTERNAL` points the build at a checkout of the companion.
- **The companion's workflow builds both editions.** It checks that the published page here is exactly the open edition built from those inputs, and it keeps the government edition as a downloadable workflow artifact.
- **This repository's own checks** confirm that `dist/index.html` is this commit's code and the open edition (`build/tools/verify_dist.py`, C-DIST-01 and C-DIST-02). C-SAN-01 fails if an internal-only file is ever tracked here. C-SEC-06 checks that both repositories are set up this way.
- **In the open edition,** the co-cddo move hub and the Slack view are left out of navigation. An old link to one of them lands on a short notice.

## Consequences

- Anyone can read, run and reuse the code. A full rebuild needs access to the companion.
- The internal material is still in this repository's history, from before the split. Removing it means rewriting history and force-pushing, which only the owner can decide.
- When the workspace owners agree to share the Slack counts, or the move proposals are agreed, that material can move back here and the companion can retire.
