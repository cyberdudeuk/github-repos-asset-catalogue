# Journeys

> **Status:** Proto-personas and assumed journeys, written from the requests that shaped the catalogue. Not yet tested with users: research is the first thing to do next.

Scores are assumed feelings (1 to 5), to be tested with users.

## J1: From a policy question to the right team (Policy lead)

```mermaid
journey
  title From a policy question to the right team
  section Arrive
    Opens the catalogue from a link: 2: Policy lead
  section Orient
    Picks 'What are you interested in?' or searches in everyday words: 3: Policy lead
  section Narrow
    Filters to 'being worked on' and their sector: 3: Policy lead
  section Understand
    Opens a profile at Simple reading level: 4: Policy lead
  section Connect
    Follows 'who it belongs to' and raises an issue with the catalogue's maintainers: 5: Policy lead
```

| Stage | Action | Page | Feeling |
|---|---|---|---|
| Arrive | Opens the catalogue from a link | home | Curious, unsure |
| Orient | Picks 'What are you interested in?' or searches in everyday words | discover | Relieved: no jargon |
| Narrow | Filters to 'being worked on' and their sector | discover | Focused |
| Understand | Opens a profile at Simple reading level | profile | Confident |
| Connect | Follows 'who it belongs to' and raises an issue with the catalogue's maintainers | family | Ready to act |

**Known pain point:** Most repositories have no description; summaries are written automatically and marked.

## J2: From estate question to remediation plan (Data leader)

```mermaid
journey
  title From estate question to remediation plan
  section Arrive
    Opens Insights and analytics: 2: Data leader
  section Assess
    Selects their knowledge areas on the DAMA wheel: 3: Data leader
  section Find debt
    Opens Legacy and technical debt for their organisation: 3: Data leader
  section Compare
    Looks at peers in the family tree and organisation profiles: 4: Data leader
  section Act
    Downloads the CSV for a remediation plan: 5: Data leader
```

| Stage | Action | Page | Feeling |
|---|---|---|---|
| Arrive | Opens Insights and analytics | insights | Wants the big picture |
| Assess | Selects their knowledge areas on the DAMA wheel | dama | Sees gaps |
| Find debt | Opens Legacy and technical debt for their organisation | legacy | Concerned |
| Compare | Looks at peers in the family tree and organisation profiles | family | Benchmarking |
| Act | Downloads the CSV for a remediation plan | legacy | In control |

**Known pain point:** Commercial tools used through their own interfaces leave little trace in public code.

## J3: Reuse before build (Service owner)

```mermaid
journey
  title Reuse before build
  section Search
    Searches everything for the capability: 2: Service owner
  section Check APIs
    Looks for an API and its catalogue entry: 3: Service owner
  section Check reuse
    Reads licence, care checklist and activity: 3: Service owner
  section Find guidance
    Finds related playbooks and standards: 4: Service owner
  section Decide
    Records reuse, or contacts the owner: 5: Service owner
```

| Stage | Action | Page | Feeling |
|---|---|---|---|
| Search | Searches everything for the capability | search | Hopeful |
| Check APIs | Looks for an API and its catalogue entry | apis | Assessing |
| Check reuse | Reads licence, care checklist and activity | profile | Cautious |
| Find guidance | Finds related playbooks and standards | guidance | Reassured |
| Decide | Records reuse, or contacts the owner | profile | Decided |

**Known pain point:** 'Can I reuse it?' is often 'Not known' because licences aren't detected.

## J4: Move a co-cddo repository safely (Repository owner moving from co-cddo)

```mermaid
journey
  title Move a co-cddo repository safely
  section Learn
    Reads the migration in six sentences: 2: Repository owner moving from co-cddo
  section Locate
    Finds their repository and its proposed home: 3: Repository owner moving from co-cddo
  section Check
    Reviews dependencies and what breaks: 3: Repository owner moving from co-cddo
  section Decide
    Records a decision: 4: Repository owner moving from co-cddo
  section Move
    Follows GitHub's documented behaviour: 5: Repository owner moving from co-cddo
```

| Stage | Action | Page | Feeling |
|---|---|---|---|
| Learn | Reads the migration in six sentences | start | Wary |
| Locate | Finds their repository and its proposed home | repos | Clear |
| Check | Reviews dependencies and what breaks | lineage | Careful |
| Decide | Records a decision | repos | Committed |
| Move | Follows GitHub's documented behaviour | safe | Done |

**Known pain point:** Pages and links don't redirect; OIDC subjects change.

## J5: Join the catalogue to govukOS (Cross-government architect)

```mermaid
journey
  title Join the catalogue to govukOS
  section Understand
    Reads what each app holds and the shared key: 2: Cross-government architect
  section Resolve ids
    Uses the organisation crosswalk: 3: Cross-government architect
  section Trace
    Follows lineage from source to check: 3: Cross-government architect
  section Exchange
    Downloads feeds and vocabularies: 4: Cross-government architect
  section Link
    Uses the link scheme from other apps: 5: Cross-government architect
```

| Stage | Action | Page | Feeling |
|---|---|---|---|
| Understand | Reads what each app holds and the shared key | govukos | Mapping |
| Resolve ids | Uses the organisation crosswalk | govukos | Unblocked |
| Trace | Follows lineage from source to check | knowledge | Trusting |
| Exchange | Downloads feeds and vocabularies | knowledge | Integrating |
| Link | Uses the link scheme from other apps | govukos | Joined up |

**Known pain point:** The other apps don't yet accept an organisation in their links.

## J6: Raise the standard of public code (Engineering and security lead)

```mermaid
journey
  title Raise the standard of public code
  section Baseline
    Opens Good practice across disciplines: 2: Engineering and security lead
  section Find gaps
    Filters by type and sector: 3: Engineering and security lead
  section Check debt
    Finds retired libraries: 3: Engineering and security lead
  section Check rules
    Checks against the GDS Way: 4: Engineering and security lead
  section Track
    Re-checks after the next scan: 5: Engineering and security lead
```

| Stage | Action | Page | Feeling |
|---|---|---|---|
| Baseline | Opens Good practice across disciplines | practice2 | Measuring |
| Find gaps | Filters by type and sector | practice2 | Specific |
| Check debt | Finds retired libraries | legacy | Prioritising |
| Check rules | Checks against the GDS Way | gdsway | Assuring |
| Track | Re-checks after the next scan | practice2 | Improving |

**Known pain point:** A file shows a practice is set up, not how well it's followed.
