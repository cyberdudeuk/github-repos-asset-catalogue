# Showcase plan: a deck and a short film

GHRAC 7.11.0. Requirement R64. Status: **planned**. Neither the deck nor the film has been made yet.

The audience is wider than the people who build code. It includes policy, programme, commercial, finance, data and digital leaders across government and the public sector, most of whom have never used GitHub. Both pieces aim to:

1. **Demystify GitHub.** Show what it is, in office terms, and why government code lives there.
2. **Show what already exists.** Make the point that someone in government has probably already built it.
3. **Make the catalogue the place to start.** Then point people to the guide, the briefing and where to ask.

## The deck

About 12 slides, for 20 minutes with questions. It is built from the Slides artifact type, so it can be downloaded as PowerPoint or PDF. Every figure has its source and date in the speaker notes.

| # | Slide | What it says | Evidence on the slide |
|---|---|---|---|
| 1 | Someone in government has probably already built it | The problem: duplicated effort, and code no one can find | Counts: 24,487 public repositories in 230 accounts |
| 2 | GitHub in office terms | A repository is a shared folder with a full history. An issue is a ticket. A pull request is a tracked change with a review. A fork is a copy you're allowed to adapt. | The office-terms table from the beginner guide |
| 3 | Why government code is public | The Service Standard's point 12 and the GDS Way: open by default, and safe to reuse with an MIT or OGL licence | Quotes from the GDS Way |
| 4 | What the catalogue is | One page, in plain English, organised by topic, organisation, question and service | A screenshot of the briefing |
| 5 | Is it part of a live service? | Plain labels, with their evidence and how accurate they are | Life labels and their sampled precision |
| 6 | What government builds on | GOV.UK Frontend, the MOJ and NHS frontends, Notify clients and others | The reuse map: 196 components |
| 7 | Can I reuse it? | The checklist: licence, someone looking after it, security policy, dependency monitoring | A project's "Before you reuse it" panel |
| 8 | Who do I ask? | Where to ask, beyond GitHub | A project's "Where to ask" panel |
| 9 | Safe to share | Guardrails: no sign-in-only links, warnings on unverified accounts, an open build without internal data | C-SEC checks |
| 10 | Checked, not claimed | 283 build checks, 52 page checks, and a negative test for every check | The check registry |
| 11 | What's new on GitHub | Universe 2026, in brief, and how to join the assessment in Discussions | The Discussions category |
| 12 | Start here | Links to the catalogue, the guide, the team inbox, and how to get involved | QR code |

## The film

About 3 minutes, for anyone. It is made from the Animations artifact type, with captions, an audio-described version and a transcript. A BSL version is optional.

**Working title:** *Before you build it, look for it.*

| Time | Scene | Narration (draft) | On screen |
|---|---|---|---|
| 0:00 | The cold open | "Somewhere in government, a team is about to spend six months building something that already exists." | Two teams, two offices, the same sketch on two whiteboards |
| 0:15 | What GitHub is | "Most government code lives on GitHub. Think of it as a shared drive where every change is recorded, every file has a history, and anyone can see it." | A folder that opens out into versions on a timeline |
| 0:45 | Four words you'll hear | "A *repository* is a project's folder. An *issue* is a ticket. A *pull request* is a change waiting for review. A *fork* is your own copy to adapt." | Four simple animated icons with a caption for each |
| 1:15 | Why it's open | "Government publishes its code so others can reuse it. It's safer, cheaper and faster than starting again." | The words of the Service Standard; a reuse arrow between two departments |
| 1:35 | The catalogue | "But there are more than 24,000 public projects. The catalogue organises them in plain English: by topic, by organisation, by service." | Moving through the briefing, topics and a project profile |
| 2:05 | Can I trust it? | "Each project tells you whether it's live, who looks after it, whether you can reuse it, and who to ask." | The glance tiles and the reuse checklist |
| 2:30 | Safe by design | "It only shows public code. It hides private links. And it tells you when an account isn't verified." | The verified-account notice |
| 2:45 | Call to action | "Before you build it, look for it." | The catalogue, the QR code and the team inbox |

**Accessibility:** every colour pairing is checked for contrast, there is no flashing, and captions are burned in and also available as a separate file. The pace allows reading.

## When to release

The showcase should come a week or two after the internal release, once its blockers are cleared (see docs/security/release-readiness.md). The deck's slide 11 and the film's ending can then point to the "Feature assessment" category in Discussions, for questions raised by GitHub Universe 2026.

## How we'll know it worked

- Views of the briefing and the guide in the first month, measured only if visitors consent.
- Questions in Discussions.
- What participants say in the five sessions in docs/service-design/research-plan.md.
