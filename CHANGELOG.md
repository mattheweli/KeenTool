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

# Stable changelog — 2026-10-23

## KeenTool 2.0.4

Relative to published v2.0.3 (main `9350079e75db877333c0b927562734537e4aecc0`).

- Make Install / Update verify every installed file owned by the selected component, plus shared dependencies, against the published target SHA-256 and expected permissions. A current installed-release.json no longer hides an old Monitor, missing API/helper or modified script. Report every differing path, reason and readable source version before installation consent. Unrelated component source differences do not trigger the selected component.
- Add explicit FILE_SCOPES.json ownership for all 54 installation targets. The lightweight GitHub-digest-verified overview carries source/path/owner/hash/mode/version data; normal checks still do not download the archive. After consent, require the archive's INSTALL.tsv, scopes and source hashes to match the approved overview before applying the coordinated transaction.
- Keep the Main Dashboard in the KeenTool repository while tracking Dashboard 2.0.3 separately from manager 2.0.4. Check the actual installed HTML version and content, including when an old record does not contain a Dashboard entry or incorrectly claims a newer version. The dashboard menu selects Dashboard instead of KeenTool; the global overview includes all six components.
- Display the recorded Firewall suite version in the main tool summary. Keep Monitor and Stats script versions in the firewall submenu; independent script versions are not used as the suite version.
- Retain explicit full-package repair, coordinated file installation, dependency preflight, successful-update menu restart, backup/rollback and preservation of credentials, configuration, databases and schedules. Older version-only overviews explicitly state that files were not verified.
- Add transport/menu regression cases for same-version Monitor 3.0.0 versus expected 4.0.0, scoped file coverage, unrelated component drift, shared dependencies, missing files and bad modes, actual Dashboard HTML versus the record, and mismatched target metadata.

Firewall remains 4.0.1 (Monitor 4.0.0, Stats 4.0.1). Pingtool/Traffic/SMB remain 2.0.0. Installer remains 1.0.2; updater/verifier/bootstrap advance to 1.0.3. No firewall policy, cron or database history change is included. See [Update behavior](docs/UPDATE_RECOVERY.md) and the [2.0.3 changelog](docs/history/STABLE_2.0.3.md).


# Stable changelog — 2026-10-23

## KeenTool 2.0.3

Relative to published v2.0.2 (main `b65b265032a35469db2cdc0c2fdaaceb60a79264`).

- Check a selected tool against its own installed and published component versions. An available KeenTool update does not trigger an update when the selected Firewall, Pingtool, Traffic Manager or SMB component is current.
- Add a main-menu **Check all updates (KeenTool and tools)** overview for the five components, showing installed version, available version and status. Self-update explicitly selects KeenTool.
- Fetch only the GitHub release record and a small component overview during version checks. Bind the overview URL, stable version, size and SHA-256 to the published GitHub release. Before confirmation, disclose every changed component, shared runtime coordination and release changes. Download the full archive only after interactive consent or explicit --yes.
- Preserve coordinated installation, HTTPS-only transport, archive and internal file checksum verification, backup/rollback, dependency preflight and successful-install menu restart. Verify that the downloaded package component versions match the approved overview. Refuse downgrades, including newer component versions within a mixed installation.
- Separate source verification and repair into **Verify / repair installed package files** and explicit --repair. This operation asks before downloading the archive, compares actual files and modes, then asks before applying a repair. --repair --check verifies without installation. Ordinary version checks no longer audit or silently repair files.
- Keep compatibility with older releases without an overview for complete-suite checks and explicit repair; do not invent per-tool versions from the suite number. Publish versioned component overview assets and checksum sidecars with this and future complete releases.
- Extend isolated transport/menu tests for per-tool and global scopes, unchanged components, no archive download before consent, interactive decline, explicit repair, overview tampering and package/overview mismatch.

Installer 1.0.2, Firewall 4.0.1, Pingtool/Traffic/SMB 2.0.0 and database/history behavior are unchanged. Updater/verifier/bootstrap advance to 1.0.2. See [Update recovery](docs/UPDATE_RECOVERY.md) and the [2.0.2 changelog](docs/history/STABLE_2.0.2.md).


# KeenTool changelog

## 2.0.2 — 2026-10-23

Relative to published v2.0.1 (main `64dac8c0c0510822376c098211b470f9aaadf6b4`).

- Share capability-based dependency preflight between the generated standalone/embedded bootstrap and installer. Detect missing or broken PHP CLI, bootstrap commands, full suite executables, PHP functions/session support, CGI startup, SQLite JSON and Entware web/capture modules. Report all missing requirements together; ask before opkg installation and verify again afterward. Check-only and noninteractive paths remain read-only unless dependency installation is explicitly requested. Do not perform a broad package upgrade or rewrite configuration.
- Replace legacy per-file managed menu flows with one coordinated update. Firewall update now returns before legacy dependency/kernel probes, repeated suite updater calls, FastCGI rewrites, daemon restarts and cron edits. Ping/Traffic/Dashboard/SMB update actions similarly avoid obsolete post-install mutations.
- Restart the menu with exec only when an update/repair successfully produces a private installation receipt. Preserve the menu on failure, decline or no-op. Print the actual installed package version from RELEASE.json instead of the fixed 2.0.0 message. An already-loaded older menu needs one reopen during its first upgrade; automatic restart applies to the new menu code.
- Add component-specific version reporting and a verified installed-source audit. Distinguish KeenTool suite 2.0.2, firewall component 4.0.1, Monitor 4.0.0 and Stats 4.0.1. Detect missing/stale source files and unexpected modes even at the same declared suite version, and offer a complete transaction-backed repair without downgrading newer local installations.
- Add dependency/bootstrap and managed-menu integration checks. Extend remote-updater tests for receipts, component audit, same-version repair, check-only behavior and downgrade refusal; extend installer fixtures for the complete runtime capability check.

Firewall 4.0.1 and the unchanged Ping/Traffic/SMB versions are retained. No hook/rule or database-history policy changes are included. See [UPDATE_RECOVERY.md](docs/UPDATE_RECOVERY.md), the [2.0.1 history changelog](docs/history/STABLE_2.0.1.md), and [FIREWALL_HISTORY.md](docs/FIREWALL_HISTORY.md).


## 2.0.1 — 2026-10-23

Relative to published v2.0.0 (`2758f0d7ee8fb9e703ee7c35ea866002e4edb036` on main).

- Add progressive firewall history settings in the CLI Firewall menu and authenticated web Settings, with enabled/raw/hourly thresholds, ranges/presets, revision checks, private configuration backup and cross-field validation. History settings do not reapply the firewall hook.
- Add the coordinated history engine/CLI, default 7-day raw and 30-day hourly detail, installation targets and missing-default configuration migration. Preserve existing history settings, scheduler, credentials and databases during package updates.
- Expose historical bucket precision in dashboard/Security diagnostics and comparisons. Preserve all-time IP/list totals, local calendar-day totals, global counters, full port history and reporting state.
- Patch component versions: manager/dashboard 2.0.1, firewall statistics 4.0.1, firewall page 2.0.1, changed settings/security/installation/uninstall helpers 1.0.1; new history helpers 1.0.0. Unchanged components retain their published versions.


- Existing public Update KeenTool now hands off to a self-contained migration entry before shared libraries load. The entry verifies the full stable suite, preserves interactive consent, handles cancellation/retry and opens the new menu only after successful installation. Pinned alpha installations use the same standalone bootstrap once.

- WAN monitor shutdown waits for in-flight scans and notification work even when a trapped signal interrupts Bash wait.

Baseline: `8d640c8b06968b0f24ce41feb1bc5b0a89c3f541`.

- Remote whole-suite updater and standalone legacy/alpha bootstrap: stable-only release lookup, confirmation, no downgrade, SHA-256/GitHub digest validation, bounded safe TAR/PAX extraction and complete file-manifest verification before the same migration installer. Menu/CLI checks and offline updates remain available.
- New coordinated 2.0.0 suite installation: fresh/upstream/alpha detection, verified file/configuration backups, atomic replacement, automatic/manual rollback and whole-package update entry point.
- Uniform Keenetic-inspired responsive navigation, shared refresh with Off/manual controls, remembered navigation/density, readable tables and a full-width Security & Health overview. Remove development banners and show versions in copyright footers.
- Dot thousands/comma decimals across rendered dashboard values; preserve raw technical data and arithmetic. Full expanded log views, bounded internal transport, log sizes and allowlisted read-only system logs without changing syslog rotation.
- Password-only HTTPS administrator access shared with Settings/Security, typed settings with ranges/presets, revision conflict handling and guarded firewall changes.
- Entware update monitoring/notifications and an explicitly requested maintenance worker that stops/restarts Entware services. Shared HTML/plain notification layout with safe tables, MTR rendering and semantic health colors.
- Independent incremental PPP syslog monitor, root broker, ktweb web-isolation tools, boot scheduler check and private helper paths. BusyBox metadata fallback removes the GNU stat requirement.
