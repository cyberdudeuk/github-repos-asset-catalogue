# User stories

> **Status:** Proto-personas and assumed journeys, written from the requests that shaped the catalogue. Not yet tested with users: research is the first thing to do next.

Each story names the tests that prove it. The test results are embedded in the built page.

| ID | Story | Where | Acceptance criteria | Proved by |
|---|---|---|---|---|
| S01 | As a policy lead, I want to find work on my policy area in plain words, so that I can join up with teams already working on it. | Explore repos | Topic tiles and everyday-word search return matching projects<br>Each card says what it is and whether it's being worked on, without jargon | T-RX-01 |
| S02 | As a policy lead, I want to see a project's story on one page, so that I understand it without reading code. | Repo profile | Three reading levels<br>Who it belongs to, up to the department | T-RX-02 |
| S03 | As a policy lead, I want to see which projects support life events and whole-of-government journeys, so that I can see where my policy meets real services. | Public service journeys | Life events and whole-of-government work listed with evidence | T-TH-01 |
| S04 | As a data leader, I want to see my organisation's data management capabilities on the DAMA wheel, so that I know our strengths and gaps. | Data management wheel | Select an area, then a capability, to reach the repositories and evidence | T-DAMA-01 |
| S05 | As a data leader, I want to find legacy technology and data in my estate, so that I can plan remediation. | Legacy and technical debt | Signals with evidence, filterable by organisation and sector | T-LEG-01 |
| S06 | As a data leader, I want to see the tools and suppliers behind data work, so that I can judge supplier concentration. | Data tools and suppliers | The table follows the chosen knowledge area | T-SUP-02 |
| S07 | As a data leader, I want to see my department's whole family of organisations, so that I see the estate as one. | Department family tree | Every branch total equals its parts<br>Keyboard-navigable tree | T-FAM-01 |
| S08 | As a service owner, I want to search the whole catalogue in one place, so that I find anything without knowing where it lives. | Search everything | Grouped results, exact names first, open where they belong | T-SRCH-01 |
| S09 | As a service owner, I want to find APIs and see whether they're in the government API catalogue, so that I can reuse rather than rebuild. | API catalogue | Reconciliation in both directions | T-API-01 |
| S10 | As a service owner, I want to know whether I can reuse a project, so that I avoid licence problems. | Repo profile | Licence in plain words, marked 'not legal advice' | T-RX-02 |
| S11 | As a service owner, I want to find guidance, playbooks and standards held in code, so that I follow what already exists. | Guidance, policy and playbooks | Playbooks, manuals, policy and standards with evidence | T-TH-01 |
| S12 | As a engineering and security lead, I want to compare good practice across disciplines, so that I can target improvement. | Good practice across disciplines | Eight disciplines, by sector and type | T-PRAC-01 |
| S13 | As a engineering and security lead, I want to find retired GOV.UK libraries and end-of-life tools, so that I can remove them. | Legacy and technical debt | Dependency-based signals marked 'in the code' | T-LEG-01 |
| S14 | As a repository owner moving from co-cddo, I want to see where each co-cddo repository is going and what could break, so that I move safely. | co-cddo move | Destinations, impacts and decisions recorded | T-DEC-01, T-IMP-01 |
| S15 | As a repository owner moving from co-cddo, I want to see what depends on my repository, so that I don't break other teams. | Dependencies | Family tree, line map and list | T-VIEW-01 |
| S16 | As a cross-government architect, I want to join GTI and ANA organisation ids to GOV.UK slugs, so that the apps can share data. | govukOS connections | Every id matched exactly or with a stated reason | T-OS-01 |
| S17 | As a cross-government architect, I want to trace any requirement to the checks that prove it, so that I can trust the catalogue. | Knowledge layer | Selecting a requirement lights its checks and sources | T-KN-01 |
| S18 | As a cross-government architect, I want to download vocabularies, ontology and feeds in open formats, so that other portals can harvest them. | Knowledge layer | SKOS, OWL, JSON-LD, CSV | T-KN-01, T-OS-01 |
| S19 | As a policy lead, I want to use the catalogue with a screen reader, keyboard or on a phone, so that I'm not excluded. | Every page | WCAG 2.2 AA, no sideways scrolling at 320 pixels | T-AXE-01, T-WID-01, T-CON-02 |
| S20 | As a cross-government architect, I want to see work about the UK's nations and international partners, so that I can find devolved and partner work. | Devolution and the UK's nations | Devolved publishers and alliance flags | T-TH-01 |
