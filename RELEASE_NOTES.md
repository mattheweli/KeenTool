# KeenTool 2.0.0

Baseline: `8d640c8b06968b0f24ce41feb1bc5b0a89c3f541`.

- Remote whole-suite updater and standalone legacy/alpha bootstrap: stable-only release lookup, confirmation, no downgrade, SHA-256/GitHub digest validation, bounded safe TAR/PAX extraction and complete file-manifest verification before the same migration installer. Menu/CLI checks and offline updates remain available.
- New coordinated 2.0.0 suite installation: fresh/upstream/alpha detection, verified file/configuration backups, atomic replacement, automatic/manual rollback and whole-package update entry point.
- Uniform Keenetic-inspired responsive navigation, shared refresh with Off/manual controls, remembered navigation/density, readable tables and a full-width Security & Health overview. Remove development banners and show versions in copyright footers.
- Dot thousands/comma decimals across rendered dashboard values; preserve raw technical data and arithmetic. Full expanded log views, bounded internal transport, log sizes and allowlisted read-only system logs without changing syslog rotation.
- Password-only HTTPS administrator access shared with Settings/Security, typed settings with ranges/presets, revision conflict handling and guarded firewall changes.
- Entware update monitoring/notifications and an explicitly requested maintenance worker that stops/restarts Entware services. Shared HTML/plain notification layout with safe tables, MTR rendering and semantic health colors.
- Independent incremental PPP syslog monitor, root broker, ktweb web-isolation tools, boot scheduler check and private helper paths. BusyBox metadata fallback removes the GNU stat requirement.

## Installation and compatibility

Install/update through the complete KeenTool 2.0.0 suite asset. Component archives require the coordinated shared runtime; do not replace isolated scripts over older installations. Existing settings, credentials, databases and upgrade schedules are preserved. Read the suite docs/INSTALL.md and SECURITY.md.

## Known feed limitation

IPdeny IPv6 KP may return HTTP 404; incomplete candidates retain the installed GeoBlock6 list. Cached installation time is not source freshness. This is reported explicitly, not silently bypassed.

## Validation

See suite docs/VALIDATION.md for isolated regression results and the live-router acceptance steps that remain before publication. This prepared release is a draft; no router reboot or public deployment is claimed.
