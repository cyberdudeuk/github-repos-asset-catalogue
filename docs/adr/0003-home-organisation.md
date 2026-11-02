# ADR 0003: Which GitHub organisation should hold the catalogue

Status: **proposed**. This needs a decision by the owning team, and agreement from the destination organisation's owners.

## Context

The repository is in a personal account. The GDS Way expects GDS code to live in a GDS organisation under the GDS GitHub Enterprise:

- members connect a GDS or DSIT email address and use two-factor authentication
- the organisation's owners control access

The co-cddo organisation is being deprecated, and its profile points to gds-dtx and uk-gov-cyber. The GDS Way's organisation table (last reviewed 19 July 2025, review overdue) still lists co-cddo. It doesn't list gds-dtx.

## Options

See docs/security/gds-way-assessment.md, "Which organisation".

## Proposed decision

Move to **gds-dtx**:

- It is GDS Digital Transformation at DSIT.
- Its stated purpose includes "improving reuse across services and departments" and "developing shared patterns, guidance and tooling".
- It has a verified domain on GitHub.
- It already uses internal visibility.
- co-cddo's deprecation notice names it.

The alternative is **alphagov**, if the owning team sits in GDS Digital Products or the gds-dtx owners decline.

Don't move until the machinery-of-government change to the new department has settled which GitHub Enterprise and organisations GDS will use, so the repository only moves once.
