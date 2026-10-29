# KeenTool coordinated package 2.0.20

## Coordinated package 2.0.20 / Manager 2.0.12 / Firewall 4.0.9 — 2026-10-29

- Reorganize KeenTool Security Monitoring into Overview, Monitoring, Notifications, Access/protection and Blocklist/logging groups. Display current interval, timezone/summary hour, master email, immediate warning and daily summary states, management-network count, isolation, pending policy, change thresholds and NFLOG sampling values.
- Add an immediate-warning email control (W), keeping existing shortcuts including D for daily summaries. Distinguish configured ON from effective PAUSED states caused by the master email switch, missing mail transport or an unavailable monitor. Changing one preference preserves the other email settings.
- Show a compact Security Monitoring state on KeenTool's main H entry. Redraw reads configuration, validated PID/socket state and the latest snapshot without kernel commands, database scans, network calls or backup checksum scans. Missing/stale/future snapshots and stopped services are not shown as healthy. Malformed optional snapshot data falls back to not verified.
- Replace repeated raw JSON menu views with focused formatted health details, recent events and policy bypass review. Explicit health details perform the existing live checks; normal redraw does not. Keep legacy status/request JSON modes unchanged for scripts. Strip terminal control characters and do not print mail credentials.
- Add real PHP-core fixtures for grouped states, paused notifications, PID/socket readiness, stale/missing/future observations, no expensive commands on redraw, read-only events, warning toggles, main-menu fallback and credential non-disclosure.

Package 2.0.20 / KeenTool manager 2.0.12 / Firewall 4.0.9. Security engine 1.0.5, Security CLI 1.0.2 and terminal presentation module 1.0.0. Stats remains 4.0.2; installer 1.0.8 and guardian 1.0.2 are unchanged. No rule, scheduler or notification policy is changed by opening the menu.

Update through KeenTool u, then open H Security Monitoring. Notifications display effective ON/OFF/PAUSED states; W controls immediate warnings, D daily summaries and 7 all Security & Health email. Live health checks are explicit option 1.
