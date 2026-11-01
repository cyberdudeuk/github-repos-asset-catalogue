# Security

Please report security problems privately to the repository's maintainers, using GitHub's private vulnerability reporting for this repository (Security tab, "Report a vulnerability"), rather than opening an issue. We'll acknowledge reports within five working days.

The page is a single static file. It makes no network requests, keeps no data about visitors, and treats all repository text as untrusted: text is escaped before display, and the tests include hostile-input cases (T-XSS-01, T-XSS-02, T-RX-03, T-SRCH-01).

This repository is private, for internal government and public sector users. It must not hold personal data, credentials, email addresses or links to private services; `build/scan_sensitive.py` checks this on every build.
