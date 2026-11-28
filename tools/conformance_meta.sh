#!/bin/sh
# Write the repository settings tools/conformance.py needs, as JSON, using the GitHub CLI (signed in).
# Usage: sh tools/conformance_meta.sh OWNER/REPO > meta.json
# Reads only. A setting the API will not show is left out, so the checker reports it as MANUAL.
set -eu
R="$1"
gh api "repos/$R" --jq '{full_name, visibility, default_branch, has_pages, has_issues}' > /tmp/cm_repo.json
B=$(jq -r .default_branch /tmp/cm_repo.json)
# Protected if a branch protection rule or an active ruleset covers the default branch.
P=null
if gh api "repos/$R/branches/$B" --jq .protected > /tmp/cm_prot 2>/dev/null; then P=$(cat /tmp/cm_prot); fi
if [ "$P" != "true" ] && gh api "repos/$R/rules/branches/$B" --jq 'length > 0' > /tmp/cm_rules 2>/dev/null; then
  [ "$(cat /tmp/cm_rules)" = "true" ] && P=true
fi
V=null
if gh api "repos/$R/private-vulnerability-reporting" --jq .enabled > /tmp/cm_pvr 2>/dev/null; then V=$(cat /tmp/cm_pvr); fi
gh api "repos/$R/commits?per_page=30&sha=$B" --jq '[.[].commit.message | split("\n")[0]]' > /tmp/cm_commits.json
jq --argjson p "$P" --argjson v "$V" --slurpfile c /tmp/cm_commits.json '. + {branch_protected: $p, private_vulnerability_reporting: $v, commit_summaries: $c[0]}' /tmp/cm_repo.json
