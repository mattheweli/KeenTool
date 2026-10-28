# KeenTool coordinated package 2.0.16

## Coordinated package 2.0.16 / Firewall 4.0.5 — 2026-10-28

- Add explicit, backup-first compact IP history storage. Repeated IP/subnet text becomes an integer dictionary reference; row multiplicity, timestamps, counts and list classes are verified transactionally before replacing the table with a compatible read/write view. Recognized schemas/indexes only; custom objects are refused. Global counters, metadata, ordered full port histories and reporting state are preserved.
- Add an explicit balanced 2/7/365-day policy: recent original samples, then hourly, daily and older complete calendar-month IP/list buckets. Preserve exact IP/list/month totals and recent raw samples; disclose reduced old day/rolling-boundary and first/last precision. Existing settings are not changed by installing the release. Monthly aggregation is optional in Web Settings (0 disables new monthly rollups).
- Add keentool_db CLI status/maintenance for Firewall, Connection Monitor and vnStat. Ping/vnStat use lossless VACUUM with verified private backups; existing samples, peaks, retention and traffic counters are preserved. vnStat uses its configured database directory and only stops a previously running daemon through a unique init script, restoring its state on success/error and reporting restart failure. No SMB history DB exists; JSON/security/config state is untouched.
- Add expansion back to text storage retaining current collected events for a reviewed runtime downgrade. Package rollback never silently restores a historical database backup or reconstructs already reduced time precision.
- Preserve script header cleanup and donation sections from main. Script changes outside the statistics collector are comment-only; their runtime versions do not advance. Do not infer a future database size cap from compaction measurements. Port normalization is intentionally not applied without a measured storage benefit.
- Add real SQLite/PHP-core regression fixtures for exact conversion, duplicate rows, view writes, monthly totals, idempotence, expansion, backup privacy, custom-index refusal, unchanged Ping/traffic samples and vnStat lifecycle/error paths.

Package 2.0.16, Firewall 4.0.5 and Stats 4.0.2. Manager remains 2.0.11, Ping 2.0.2, Traffic 2.0.1, SMB 2.0.1 and Dashboard 2.0.4. Database conversion/aggregation is explicitly requested after installation; installing the package does not run database maintenance. Tests are isolated and do not prove physical-router speed or custom service behavior.

See suite/docs/DATABASE_STORAGE.md for commands, backup/precision and downgrade limitations. Update through KeenTool → u.
