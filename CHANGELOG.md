# KeenTool changelog

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
