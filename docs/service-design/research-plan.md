# User research plan: testing the plain-English catalogue

GHRAC 7.11.0. Status: **planned, not run.** The personas in this folder are proto-personas, and stay labelled "untested" until these sessions have run.

## What we want to learn

1. Can people who don't use GitHub use the briefing, the glance tiles and the labels to answer their own question, without help? Questions like: "Is anyone in government already doing this?", "Can we reuse it?" and "Who do I ask?"
2. Do people read the labels as estimates, or as facts? Labels include "Is it part of a live service?", "Is it safe to depend on?" and "Account not verified by GitHub".
3. Where do people get lost or stop, and which GitHub words still get in the way?

## Who

Five sessions, one person each, chosen from government and public sector staff:

| Session | Participant | Why |
|---|---|---|
| 1 | Policy or programme lead, never used GitHub | The main audience for the briefing |
| 2 | Delivery or product manager | Decides what to reuse |
| 3 | Commercial or procurement lead | Checks what already exists before buying |
| 4 | Developer or technical architect in a council | Judges reuse and dependencies |
| 5 | Someone who uses assistive technology (a screen reader or magnification) | Accessibility of the new views |

Recruit through the cross-government user research community. Get informed consent, keep recordings and notes in the owner's research repository, and don't put participants' names in this repository.

## Discussion guide (45 minutes)

1. **Warm-up (5 minutes).** Ask about the participant's role, and the last time they needed to find out whether something had been built already.
2. **First look (5 minutes).** Open the catalogue at Home. Ask: "What do you think this is for? Where would you start?" Don't explain anything.
3. **Task 1 (8 minutes).** "Your team wants an online form for applying for a permit. Find out whether another public body has built one you could reuse." Watch for use of the briefing, search and the glance tiles.
4. **Task 2 (8 minutes).** Open a project profile. Ask: "Is this part of a live service? Would you be comfortable depending on it? What makes you say that?" Probe how far they trust the label, and whether they notice the evidence and the accuracy.
5. **Task 3 (7 minutes).** Ask: "Who would you contact about this project?" Watch for "Where to ask".
6. **Task 4 (5 minutes).** Show a project from an account labelled "not verified by GitHub". Ask: "What does this tell you?"
7. **Wrap-up (7 minutes).** Ask which words were confusing, and what was missing. Ask for a rating of how confident they'd be acting on what they found, from 1 to 5.

## Measures

- Task completion, without help.
- Time to first useful answer.
- Each confusing word, noted for the glossary and the office-terms guide.
- How confident participants feel acting on what they found, and whether that confidence matches what the evidence supports. Overconfidence counts as a finding.

## After the sessions

Play findings back to the owner within a week. Then:

- Raise each finding as an issue, with the "user research" label.
- Update the personas from proto to tested where the evidence supports it.
- Add a requirement and a check for every change made.
