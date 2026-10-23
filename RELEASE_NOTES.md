# KeenTool 2.0.2

Relative to published v2.0.1 (main `64dac8c0c0510822376c098211b470f9aaadf6b4`).

- Share capability-based dependency preflight between the generated standalone/embedded bootstrap and installer. Detect missing or broken PHP CLI, bootstrap commands, full suite executables, PHP functions/session support, CGI startup, SQLite JSON and Entware web/capture modules. Report all missing requirements together; ask before opkg installation and verify again afterward. Check-only and noninteractive paths remain read-only unless dependency installation is explicitly requested. Do not perform a broad package upgrade or rewrite configuration.
- Replace legacy per-file managed menu flows with one coordinated update. Firewall update now returns before legacy dependency/kernel probes, repeated suite updater calls, FastCGI rewrites, daemon restarts and cron edits. Ping/Traffic/Dashboard/SMB update actions similarly avoid obsolete post-install mutations.
- Restart the menu with exec only when an update/repair successfully produces a private installation receipt. Preserve the menu on failure, decline or no-op. Print the actual installed package version from RELEASE.json instead of the fixed 2.0.0 message. An already-loaded older menu needs one reopen during its first upgrade; automatic restart applies to the new menu code.
- Add component-specific version reporting and a verified installed-source audit. Distinguish KeenTool suite 2.0.2, firewall component 4.0.1, Monitor 4.0.0 and Stats 4.0.1. Detect missing/stale source files and unexpected modes even at the same declared suite version, and offer a complete transaction-backed repair without downgrading newer local installations.
- Add dependency/bootstrap and managed-menu integration checks. Extend remote-updater tests for receipts, component audit, same-version repair, check-only behavior and downgrade refusal; extend installer fixtures for the complete runtime capability check.

Firewall 4.0.1 and the unchanged Ping/Traffic/SMB versions are retained. No hook/rule or database-history policy changes are included. See [UPDATE_RECOVERY.md](docs/UPDATE_RECOVERY.md), the [2.0.1 history changelog](docs/history/STABLE_2.0.1.md), and [FIREWALL_HISTORY.md](docs/FIREWALL_HISTORY.md).

## Upgrade

Install the complete verified suite through `/opt/bin/bash /opt/bin/keentool --update`. For this first upgrade from an already-running 2.0.0/2.0.1 menu, reopen KeenTool once afterward, or initiate the update from the shell. The automatic exec restart is part of the new 2.0.2 menu and applies to updates it initiates. The installer now reports the actual manifest version.

The embedded/standalone bootstrap reports missing capabilities and asks before installing missing Entware packages. `--check` does not install packages; `--install-deps` explicitly permits dependency installation. Package-manager changes have their own lifecycle and are not rolled back by suite file restore. No broad opkg upgrade is performed.

A component update performs one coordinated transaction and displays the component and suite versions separately. Its verified source/mode audit detects missing or stale installed files even at the same declared suite version, and offers a full repair. Existing configuration, passwords, schedules and databases are preserved. The managed firewall action no longer executes legacy FastCGI, service-restart or cron logic. Firewall remains 4.0.1 (Monitor 4.0.0, Stats 4.0.1); no new firewall tag or rule change is included.

## Validation

47 isolated local checks passed, including missing/broken PHP CLI, dependency consent and recheck, bootstrap migration, menu exec restart/no-op/failure, single firewall update without legacy side effects, component/script version reporting, file drift, same-version repair and downgrade refusal. Installer/rollback, database history, notifications and UI regression checks remain in the suite. GitHub CI must pass before publishing the checked assets. No physical-router reboot or live SMTP is claimed for this patch. See suite/docs/UPDATE_RECOVERY.md.
