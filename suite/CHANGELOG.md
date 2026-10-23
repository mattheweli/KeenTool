# Stable changelog — 2026-10-23

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
