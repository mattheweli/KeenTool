# KeenTool coordinated package 2.0.8

## Pingtool 2.0.2 / coordinated package 2.0.8 — 2026-10-26

- Include the configured latency threshold in IPv6 ping-warning email bodies, matching IPv4. The shared renderer can now color a healthy latency green when packet loss is the reason for the warning. Threshold comparison and alert triggers are unchanged.
- Update shared Mail Layout to 1.0.1: accept standard MTR report loss fields with or without a percent marker. Normalize the displayed suffix and keep unanswered hops such as `3.|-- ??? 100.0 ...` in their original table position. Retain escaped fallback output for genuinely unsupported diagnostics and MPLS details.
- Extend regressions for actual IPv4/IPv6 alert bodies, below/exact/above-threshold colors, answered/unanswered hops, both loss formats, ordered table rows and diagnostic fallback escaping.

The manager remains **KeenTool 2.0.7**. The complete package advances to **2.0.8** solely to distribute Pingtool 2.0.2 and shared Mail Layout 1.0.1 through verified upgrades. Firewall, Traffic Manager, SMB Backup and Main Dashboard versions are unchanged. No probe algorithm, notification trigger/cooldown, cron, configuration, credentials or database policy changes.

## Update

Run `/opt/bin/bash /opt/bin/keentool --update`, or select Install / Update under Ping Monitor. Install the complete coordinated package so the alert producer and shared mail renderer update together. The manager continues to identify itself as 2.0.7. Only newly generated notifications use the corrected layout; previously delivered emails are unchanged. Existing settings, credentials, schedules and databases are preserved. Automated tests use isolated fixtures; live SMTP delivery and router reboot are not claimed.
