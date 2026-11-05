# Backlog and prioritisation

Last reviewed 2026-11-05. Requirement R74. Shown in the catalogue under About, [Help shape the catalogue](https://cyberdudeuk.github.io/github-repos-asset-catalogue/#shape).

## How an idea becomes work

1. **Anyone suggests it** with the [idea form](https://github.com/cyberdudeuk/github-repos-asset-catalogue/issues/new?template=idea.yml), or a research finding raises it. It is a public issue labelled `idea`.
2. **People vote** with a thumbs-up on the issue. [See the ideas with the most votes](https://github.com/cyberdudeuk/github-repos-asset-catalogue/issues?q=is%3Aissue+is%3Aopen+label%3Aidea+sort%3Areactions-%2B1-desc).
3. **The maintainers assess it** every two weeks, in the open, by adding labels to the issue: a score for each criterion below, the strategy themes it serves, and a MoSCoW priority. The reason goes in a comment, so anyone can challenge it.
4. **Capacity decides when.** Capacity is a gate, not a score. Each quarter the maintainers say how many points of work they can take on; items go into Now in score order until it's full, then Next. Anything needing the owner's decision waits for it, however high it scores.
5. **The roadmap shows it.** Items in Now and Next appear on the catalogue's roadmap, each linked to its issue.

## Criteria

The score orders the discussion; people decide. Score = value × 2 + reach + fit × 2 + feasibility, out of 18.

| Criterion | Scale | Weight | How it's judged |
|---|---|---|---|
| Value to users | 0 to 3 | ×2 | 3: research shows it blocks people, or it has 10 or more votes. 2: it slows people down, or 5 to 9 votes. 1: a nice-to-have. 0: no evidence yet. |
| Reach | 0 to 3 | ×1 | How many of the six personas it helps: 1 for one, 2 for two or three, 3 for four or more. |
| Strategic fit | 0 to 3 | ×2 | How directly it serves the themes above: 3 directly, 2 indirectly, 1 slightly, 0 not at all. |
| Feasibility | 0 to 3 | ×1 | 3: small, no dependencies. 2: medium, or needs one other team. 1: large, or needs a decision by the owner. 0: not possible now. |

## Strategy themes

Every item is checked against these. Labels: `theme:G1` and so on.

| Id | Theme | Source |
|---|---|---|
| G1 | Join up public sector services | Roadmap for modern digital government, 2025 to 2030 |
| G2 | Harness the power of AI for the public good | Roadmap for modern digital government, 2025 to 2030 |
| G3 | Strengthen and extend our digital and data public infrastructure | Roadmap for modern digital government, 2025 to 2030 |
| G4 | Elevate leadership, invest in talent | Roadmap for modern digital government, 2025 to 2030 |
| G5 | Fund for outcomes, procure for growth and innovation | Roadmap for modern digital government, 2025 to 2030 |
| G6 | Commit to transparency, drive accountability | Roadmap for modern digital government, 2025 to 2030 |
| D1 | Data Asset Management Policy | Cabinet Office and GDS; guidance in the DAM capability playbooks |
| D2 | Strategic Data Roadmap (forthcoming) | Led by the Chief Data Officer. The roadmap for modern digital government planned 'a strategic roadmap for public sector data' for April 2026; a GDS blog post of 3 September 2026 says it is 'due to be published in the autumn'. Not published when this was written, so nothing is mapped to it yet. |

## The backlog today

Open roadmap items, assessed by the maintainers on 2026-11-05. These scores are proposals for the owner to confirm; challenge any of them on the item's issue.

| Item | What | Value | Reach | Fit | Feasible | Score | Themes | When |
|---|---|---|---|---|---|---|---|---|
| RM-01 | Test the catalogue with 5 to 8 people from at least four audiences who don't use GitHub | 3 | 3 | 3 | 2 | **17** | G6, G1 | Now |
| RM-10 | Re-read GitHub so projects found since the catalogue was built are added | 3 | 3 | 3 | 1 | **16** | G3 | Waiting for the owner |
| RM-12 | A named team accepts ownership: answers issues, reviews pull requests and reviews the catalogue every quarter | 3 | 3 | 3 | 1 | **16** | G4, G6 | Waiting for the owner |
| RM-07 | Join projects to the datasets they publish or use in data catalogues (data.gov.uk, statistics.gov.scot, Data Map Wales, NHS catalogues) | 3 | 2 | 3 | 1 | **15** | G3 | Now |
| RM-04 | Check the catalogue manually with screen readers, magnifiers at 400% zoom and speech input | 3 | 3 | 2 | 1 | **14** | G6, G4 | Waiting for the owner |
| RM-11 | Link repositories to the systems they belong to | 2 | 2 | 3 | 1 | **13** | G3 | Waiting for another team |
| RM-26 | Run the roadmap as a GitHub project board, with each item an issue | 2 | 2 | 2 | 3 | **13** | G6 | Waiting for the owner |
| RM-03 | Ask organisations to check their profile and say whether the next steps are useful | 2 | 2 | 2 | 2 | **12** | G1, G6 | Now |
| RM-09 | Collect GitHub feature settings (Issues, Projects, Wiki, Discussions) for every project, not a sample | 2 | 2 | 2 | 2 | **12** | G3 | Waiting for the owner |
| RM-13 | Move the repository to its agreed home organisation | 2 | 3 | 2 | 1 | **12** | G3 | Waiting for the owner |
| RM-23 | Create the labels the issue and discussion forms apply: contact, profile check, label check and roadmap | 2 | 3 | 1 | 3 | **12** | G6 | Waiting for the owner |
| RM-25 | Create a Q&A category in Discussions, with the slug q-a | 2 | 3 | 1 | 3 | **12** | G6 | Waiting for the owner |
| RM-02 | Measure the precision of each topic on a labelled sample, as was done for strategy and DAM tags | 2 | 2 | 1 | 3 | **11** | G3 | Next |
| RM-08 | Add boundaries and locations so nations, authorities and councils can be shown on maps | 2 | 2 | 2 | 1 | **11** | G3 | Next |
| RM-24 | Require a person to approve each GitHub Pages deployment | 1 | 1 | 2 | 3 | **10** | G3 | Waiting for the owner |

## Labels

`idea`, `research`, `survey-response`, `value:0`, `value:1`, `value:2`, `value:3`, `reach:1`, `reach:2`, `reach:3`, `fit:0`, `fit:1`, `fit:2`, `fit:3`, `feasible:0`, `feasible:1`, `feasible:2`, `feasible:3`, `moscow:must`, `moscow:should`, `moscow:could`, `moscow:wont`, `now`, `next`, `later`, `theme:G1`, `theme:G2`, `theme:G3`, `theme:G4`, `theme:G5`, `theme:G6`, `theme:D1`, `theme:D2`. GitHub silently drops a label that doesn't exist, so the owner creates these once (roadmap RM-23).
