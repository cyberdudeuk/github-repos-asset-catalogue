# ADR 0001: One self-contained page

Status: accepted, 7 October 2026

## Context

The catalogue is used by people across government, often on locked-down devices, and some of them never use GitHub. Hosting choices are not settled.

## Decision

The catalogue is published as one HTML file:

- Data, fonts and code are embedded in the file.
- The page makes no network requests.
- A Content-Security-Policy enforces this (C-SEC-02).

## Consequences

- **For:** the page works offline and on any static host. Nobody is tracked, and nothing outside the page can change it at run time.
- **Against:** the file is large, about 13.8 MB against a ceiling of 16 MB. Beyond about 30,000 repositories, the data needs splitting into files served from the same host. See ADR 0002.
