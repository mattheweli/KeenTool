# KeenTool coordinated package 2.0.17

## Coordinated package 2.0.17 / Firewall 4.0.6 — 2026-10-28

- Guarantee a fresh verified database backup for explicit balanced-profile maintenance on storage that is already compact. Reuse only a backup taken by the same invocation's conversion; never treat an older normalization/history baseline as a current recovery copy.
- Test first and repeated balanced maintenance after a separate structural conversion, requiring distinct private recovery files and unchanged current events in the latest backup.
- Correct the README's independent Stats version to 4.0.2. Compact storage, balanced history, lossless Ping/vnStat maintenance and their limitations remain as introduced in 2.0.16.

Database engine advances to 1.0.1, Firewall to 4.0.6 and package to 2.0.17. Stats remains 4.0.2; manager remains 2.0.11. Installation still does not convert databases or change settings.

Includes optional compact IP identifiers and balanced 2/7/365-day history, preserving all hits while reducing old temporal precision; lossless Ping/vnStat compaction; guarded vnStat service lifecycle. See suite/docs/DATABASE_STORAGE.md. Update through KeenTool u, then explicitly request database maintenance.
