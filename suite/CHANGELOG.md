# Stable changelog — 2026-10-23

## KeenTool 2.0.2

Relative to published v2.0.1 (main `64dac8c0c0510822376c098211b470f9aaadf6b4`).

- Share capability-based dependency preflight between the generated standalone/embedded bootstrap and installer. Detect missing or broken PHP CLI, bootstrap commands, full suite executables, PHP functions/session support, CGI startup, SQLite JSON and Entware web/capture modules. Report all missing requirements together; ask before opkg installation and verify again afterward. Check-only and noninteractive paths remain read-only unless dependency installation is explicitly requested. Do not perform a broad package upgrade or rewrite configuration.
- Replace legacy per-file managed menu flows with one coordinated update. Firewall update now returns before legacy dependency/kernel probes, repeated suite updater calls, FastCGI rewrites, daemon restarts and cron edits. Ping/Traffic/Dashboard/SMB update actions similarly avoid obsolete post-install mutations.
- Restart the menu with exec only when an update/repair successfully produces a private installation receipt. Preserve the menu on failure, decline or no-op. Print the actual installed package version from RELEASE.json instead of the fixed 2.0.0 message. An already-loaded older menu needs one reopen during its first upgrade; automatic restart applies to the new menu code.
- Add component-specific version reporting and a verified installed-source audit. Distinguish KeenTool suite 2.0.2, firewall component 4.0.1, Monitor 4.0.0 and Stats 4.0.1. Detect missing/stale source files and unexpected modes even at the same declared suite version, and offer a complete transaction-backed repair without downgrading newer local installations.
- Add dependency/bootstrap and managed-menu integration checks. Extend remote-updater tests for receipts, component audit, same-version repair, check-only behavior and downgrade refusal; extend installer fixtures for the complete runtime capability check.

Firewall 4.0.1 and the unchanged Ping/Traffic/SMB versions are retained. No hook/rule or database-history policy changes are included. See [UPDATE_RECOVERY.md](docs/UPDATE_RECOVERY.md), the [2.0.1 history changelog](docs/history/STABLE_2.0.1.md), and [FIREWALL_HISTORY.md](docs/FIREWALL_HISTORY.md).
