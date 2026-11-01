# GitHub Repos Asset Catalogue

Every UK public sector code project on GitHub, organised for people who don't use GitHub as well as those who do: by topic, organisation, question and capability, in plain English, with the technical detail one click away.

**Status:** a working tool, not an official publication or government policy.

**Access:** this repository is private, for internal government and public sector users only, while it is reviewed. Don't share its contents outside government and the public sector until it is made public.

**Contact:** raise an issue in this repository.

## What's in it

- **Explore repos and Search everything:** plain-English cards, topic tiles, everyday-word search with a thesaurus, and one search across projects, organisations, accounts, topics, capabilities, tools, APIs, signals, practices, words and pages.
- **Repo profile:** three reading levels, read-aloud, who it belongs to (up to the sponsoring department), lineage and traceability for every fact, life story, care checklist and connections.
- **Department family tree:** every department and its organisations from GOV.UK's organisations list, down to the GitHub accounts and GDS units where code lives.
- **Insights:** analytics dashboard, DAMA data management wheel, data tools and suppliers, legacy and technical debt.
- **Themes:** guidance, policy and playbooks; public service journeys; devolution and the UK's nations; international work with UK alliances and partners flagged.
- **APIs and open data:** a repository-based API catalogue reconciled with the government API catalogue; open data pipelines.
- **govukOS connections:** an organisation crosswalk from GTI and ANA ids to GOV.UK slugs, feeds and a link scheme.
- **Knowledge layer:** knowledge graph, lineage and traceability from sources to defects, controlled vocabularies and taxonomies (SKOS), ontology (OWL), data dictionary and thesaurus.
- **Service design:** personas, user stories, journeys, service blueprints, processes and workflows ([docs/service-design](docs/service-design/README.md)).
- **co-cddo move:** the workspace for moving repositories out of the co-cddo GitHub organisation.

## Use it

Open [`dist/index.html`](dist/index.html) in a browser. It is one self-contained file: no server, no tracking, no calls to other sites. Links into it: `#repo=<account>/<repository>`, `#org=<GOV.UK slug>`, `#legacy=<GOV.UK slug>`, `#account=<GitHub account>`.

## Build it

```sh
pip install qrcode==8.2 python-barcode==0.16.1
cd build/inv
sh assemble71.sh                     # joins the parts into explorer71.tpl.html
GHRAC_PUBLIC=1 python3 build_v71.py  # embeds data, fonts and test results; writes explorer71_public.html
```

### Deployment settings

Nothing deployment-specific is committed. Set these when building, if needed:

- `GHRAC_URL`: the address the page is served from (used for the QR code and as the base of the JSON-LD identifiers). Defaults to this repository's address.
- `GHRAC_ISSUES_URL`: where the contact links point. Defaults to this repository's issues.
- `GHRAC_OS_LINKS`: path to a JSON file with links to the other govukOS apps, in the form `{"urls": {"gti": "", "liah": "", "ana": "", "mog": "", "measr": "", "cat": ""}, "crosswalk": {"ana": "", "liah": "", "measr": ""}}`. Without it, the govukOS connections view shows each app's name and the route to open, with no link. Keep that file out of the repository.

### What was removed before this repository was created

Personal names (contributors, CODEOWNERS entries, owners and people named in the v1 workbook's actions and evidence), email addresses, team and directorate attributions, links to private apps and design projects, descriptions of internal evidence, and the names of repositories that aren't publicly visible (shown as `unlisted-01` to `unlisted-09`). `build/scan_sensitive.py` checks for these on every build.

The build refuses to finish if a requirement or defect doesn't trace to a registered check (check C-DOC-01). The data scripts in `build/dama` regenerate the datasets from public sources (GitHub listing, git, READMEs and manifests, GOV.UK organisations API, the government API catalogue); run them with `python3 -I`. Raw clones and READMEs are not in this repository.

## Test it

The tests in `build/jt` need Node, jsdom, axe-core and Playwright:

- `t71.js`: the behaviour harness (50 tests), run with jsdom.
- `axe7x.js`: accessibility (WCAG 2.2 A and AA plus best practice) across every view.
- `ovf71.js`: no sideways scrolling at 320, 390, 768 and 1366 pixels.
- `con71.js`: rendered contrast of text on coloured blocks, light and dark.
- The page also runs 43 self-checks every time it opens (About, Method and checks).

Every defect found has a check that fails on the build that had it; see [docs/defects.md](docs/defects.md). Requirements and the checks that prove them: [docs/requirements.md](docs/requirements.md). Releases: [docs/releases.md](docs/releases.md).

## Limits

- Public GitHub only. Private and internal repositories, and work held elsewhere, aren't counted.
- Classifications come from names, descriptions, READMEs, file names and dependency names. Text-based ones were checked on samples by Claude, not confirmed by owners; each view shows its accuracy.
- Commercial tools used through their own interfaces rarely leave a trace in public code, so they're under-counted.
- Personas and journeys are proto-personas, not yet tested with users.
- This public build leaves out personal names (repository contributors and owners from the co-cddo inventory).

## Licence

Code: [MIT](LICENSE). Content and data: [Open Government Licence v3.0](LICENCE-CONTENT.md), except where noted. Fonts: SIL Open Font Licence (see `build/v6/fonts`). GitHub Docs excerpts in `build/gh`: CC BY 4.0, © GitHub, Inc. (see `build/gh/NOTICE.md`).
