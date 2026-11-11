#!/bin/sh
# The whole data refresh, in order (R75; defect V717-1: the October refresh could not be repeated because these steps
# were never written down). Set the new date in build/refresh/asof.json first ("ref", with "previous" set to the old ref),
# and GHRAC_INTERNAL to a checkout of the private companion repository.
#
# Network steps read public sources only and never write to them. A person reviews the diff and commits it.
set -eu
cd "$(dirname "$0")/../.."
: "${GHRAC_INTERNAL:?set GHRAC_INTERNAL to the internal companion checkout}"
CACHE="${GHRAC_CACHE:-${TMPDIR:-/tmp}/ghrac-refresh}"
mkdir -p "$CACHE"
python3 -I build/inv/analyse.py                                   # the bot rule's self-test
python3 -I build/refresh/fetch.py                                 # 1 scraper file and body mapping, with SHA-256
python3 -I build/refresh/reconcile.py                             # 2 repositories the scraper dropped: still public, or gone
python3 -I build/refresh/probe.py --cache "$CACHE/probe"          # 3 human activity with git, for every repository pushed in 12 months
python3 -I build/refresh/readmes.py --cache "$CACHE/readme"       # 4 READMEs, kept in the cache only
git checkout -- build/xgov/xgov.json                              # 5 the previous snapshot's government layer ...
python3 -I build/refresh/apply.py                                 #   ... brought to the new date
(cd build/catalogue && python3 -I build_catalogue.py)             # 6 one record per repository
python3 -I build/dama/pii.py --apply                              # 7 personal names quoted in descriptions removed (R54)
python3 -I build/dama/tool_repos.py --cache "$CACHE/readme"       # 8 tools named in repositories
python3 -I build/procure/collect.py fts --cache "$CACHE/procure"  # 9 tender and contract notices
python3 -I build/procure/collect.py cf --cache "$CACHE/procure"
python3 -I build/procure/gcloud.py                                #   G-Cloud service listings
python3 -I build/dama/guidance_check.py                           # 10 every guidance address answers
python3 -I build/dama/dmbok.py                                    # 11 the DAMA activity model
python3 -I build/dama/tooling.py                                  # 12 tools joined to activities, repositories, notices, listings and case studies
python3 -I build/dama/pii.py --apply                              #   and the new evidence checked for personal names
echo "Refresh done. Build both editions (build/inv), run the tests, review the diff and commit."
