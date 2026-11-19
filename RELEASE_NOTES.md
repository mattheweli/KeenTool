# KeenTool coordinated package 2.0.28

## Coordinated package 2.0.28 / KeenTool 2.0.15 — 2026-11-19

- Show the last successful Entware index refresh in router-local time in menu p and CLI status. The stored timestamp remains numeric.
- Reuse Entware indexes refreshed by KeenTool within 24 hours. Preview the current local package list and verify it again before upgrading. Check updates still forces a refresh.
- Offer a per-upgrade choice to skip Entware configuration and SQLite backups. Backups are enabled by default; logs and the service recovery runtime are retained either way.
- Add Backup Manager (menu B) with local inventory, age and disk usage, retention preview, and confirmed individual deletion. The scheduled purge is opt-in and covers eligible Entware and coordinated release backups.
- Preserve the newest recognized backup per managed category, the latest Entware run and incomplete Entware runs. Defer deletion during maintenance or pending recovery. Database, web and legacy copies are inventory only.

Package 2.0.28; KeenTool manager 2.0.15; Entware manager 1.0.2; Backup Manager 1.0.0; uninstaller 1.0.3. Other components are unchanged.

Update through KeenTool menu u. For backup retention, open menu B, set a retention threshold, preview the selection and configure its schedule.
