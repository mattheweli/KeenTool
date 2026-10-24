# Stable changelog — 2026-10-23

## KeenTool 2.0.7 — 2026-10-24

Relative to v2.0.6 (main `f01280b85b2ee70a65e514bf0181c7715c5c8211`).

- Fix the Main Menu Entware update counter when `/opt/etc/keentool/entware/available.txt` has not been created by a successful check. Redirect stderr before opening stdin and display a count only on a successful read, so a missing directory/file displays `[unchecked]` without a shell error between the H and p menu entries.
- Preserve the difference between unchecked and zero available updates. Rendering the menu neither creates a fake empty result nor performs an Entware check/upgrade; a successful existing check still displays its package count.
- Extend isolated Entware regression checks to render the actual menu line with missing parent/state, empty and populated results, deleted results and failed reads. Verify silent fallback and no state-directory creation.

Only the KeenTool manager advances to 2.0.7. Dashboard 2.0.4, SMB Backup 2.0.1, Pingtool/Traffic 2.0.1 and Firewall 4.0.2 remain unchanged. Installer, credentials, configuration, cron schedules and databases are unchanged.


## SMB Backup Tool 2.0.1 / KeenTool 2.0.6

- Correct tar exclusion paths when the backup source has `/` as its parent (including the default `/opt`). Previously an extra slash left exclusions absolute, while archive member names were relative; live logs/PCAP could enter the archive and fail backup creation.
- Normalize trailing slashes in source settings. Exclude `/opt/var/run` and `/opt/var/lock` alongside logs, temporary files and local backup staging. Exclude Unix sockets elsewhere in the source using a checked NUL-delimited inventory.
- Inspect the full 16-byte SQLite header after Base64 encoding; binary/non-SQLite `.db` files no longer inject NUL bytes into Bash command substitution. Retain coherent SQLite snapshots and verify their integrity.
- Keep strict archive error handling, remote read-back/checksum verification and retention only after successful verification. Do not stop services or ignore arbitrary tar failures. Configuration and scheduling are preserved.
- Add isolated archive regression coverage for root-parent/trailing-slash sources, volatile paths, real Unix sockets on CI, non-SQLite binary files and SQLite record preservation. Exercise GNU and BusyBox tar where available; NAS transport and router export are mocked.


## KeenTool 2.0.5

Relative to v2.0.4 (main `1e799ec2abade673cd7a728872db0035b7c5fff6`).

- Replace the fixed three-minute Security & Health age warning with the slower configured monitor-production/browser-refresh cadence. Publish monitor_interval in the security snapshot and apply one shared freshness calculation to the top status banner, Checked timestamp and Main Dashboard security summary. Mark yellow only when age is strictly greater than the effective interval; handle Off, missing legacy intervals, exact boundaries and future timestamps without inventing a delay.
- Refresh all page/template shared JavaScript references to prevent browser caches from keeping the old freshness logic. Main Dashboard advances to 2.0.4; shared UI to 1.0.1 and security UI/engine to 1.0.2. Firewall component 4.0.2 (Dashboard 2.0.2), Pingtool 2.0.1 and Traffic Manager 2.0.1 carry updated references; their collection/filtering algorithms are unchanged.
- Rewrite the five GitHub component READMEs with current features, independent versions, complete-suite installation/update instructions, real command/configuration paths, data/precision/security limitations and troubleshooting. Preserve license attribution and optional original project support links.
- Add reproducible screenshots from actual current application templates and the real SMB CLI menu, using synthetic fixtures, example addresses and an explicit documentation watermark. No user logs, credentials, database or NAS contents are used. Include generation source, pinned documentation browser dependencies and a render error report.
- Extend freshness/refresh tests for five-minute polling, long producer intervals, exact threshold, Off/legacy state, cross-tab changes and snapshot interval propagation.

Installer, firewall rule application, history aggregation and preservation/rollback behavior are unchanged. SMB runtime remains 2.0.0; its README is documentation-only.

## keenetic-firewall 4.0.2

Refresh shared UI/security asset references for configured snapshot freshness. No hook, filtering, statistics collection or database policy change. Monitor remains 4.0.0, Stats 4.0.1; firewall HTML advances to 2.0.2. Update the explanatory README with a synthetic interface screenshot.

## keenetic-pingtool 2.0.1

Refresh the generated page shared UI reference for the coordinated security freshness correction. Probe, notification and history algorithms are unchanged. Rewrite the explanatory README with a synthetic Connection Monitor screenshot.

## Traffic_manager 2.0.1

Refresh the generated page shared UI reference for the coordinated security freshness correction. vnStat collection, export retention and history algorithms are unchanged. Rewrite the explanatory README with a synthetic Traffic Monitor screenshot.
