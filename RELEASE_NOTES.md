# KeenTool coordinated package 2.0.10

## Coordinated package 2.0.10 — 2026-10-27

- Install the existing `support/render_cache.sh` library as `/opt/lib/keentool/render_cache.sh` with mode 0644. It was present in the source archive but omitted from INSTALL.tsv, so a clean installation could fail firewall statistics generation with a missing-library/undefined-function error.
- Include that target in FILE_SCOPES.json as a firewall-owned dependency. The verified release overview now tracks its hash and permissions, so global and firewall-scoped checks detect a missing or modified library even when component versions are current. A coordinated update or explicit repair reinstalls it.
- Extend isolated installation regressions: fresh installation loads the installed library through the actual firewall cache-generation block, generates the real SQLite cache files and preserves the input database. Check missing-library detection, same-version repair, migration/upgrade installation and rollback removal of the newly introduced target.

This is a packaging correction. Manager **2.0.8**, Firewall suite **4.0.2**, Stats **4.0.1**, Pingtool **2.0.2**, Traffic/SMB **2.0.1**, Dashboard **2.0.4** and installer **1.0.2** keep their versions and runtime source bytes. Settings, credentials, cron schedules, database contents and firewall rules are unchanged. The separate cron-daemon health question is not inferred from the presence of scheduled jobs.

## Update and verify

Run `cd /`, then `/opt/bin/bash /opt/bin/keentool --update`. The update may show all component versions as current while reporting the missing render_cache.sh dependency; confirm that coordinated repair. Then run `/opt/bin/bash /opt/bin/firewall_stats.sh force` to regenerate the dashboard. The manager still identifies itself as 2.0.8. Existing settings, credentials, jobs and databases are preserved. Automated validation uses isolated fixtures and mocked router/service commands, not a live router.
