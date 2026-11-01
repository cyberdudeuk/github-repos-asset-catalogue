"""co-cddo listing metadata from GitHub's own page data (gh_listing.json, read 2026-10-08 in the built-in browser and
checksum-verified on transcription). Replaces the v3 listing, which came from LLM-summarised page reads (defect D1: 5 repos missing).
L[name] = (description, language, topics, stars, forks, status, issues, pull_requests, licence_on_github)"""
import json, os
_S = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(_S, "gh_listing.json")))
REPO_COUNT = G["repositoryCount"]
def _status(t, fork):
    s = "Archived" if "archive" in t else "Template" if "template" in t else "Public"
    return s + (" (fork)" if fork else "")
L = {r[0]: (r[3], r[5], r[4].replace(",", ", "), r[9], r[10], _status(r[1], r[2]), r[7], r[8], r[6]) for r in G["rows"]}
