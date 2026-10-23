# KeenTool 2.0.4

Stable component sources for the KeenTool suite. Release date: 2026-10-23.

## Installation and updates

Install the complete KeenTool 2.0.4 release from https://github.com/mattheweli/KeenTool/releases. The shared runtime, assets, authentication and security broker are required. Do not copy this component alone over an older installation.

For an extracted complete package, use /opt/bin/bash ./install.sh --plan and follow docs/INSTALL.md. Existing public-source and local-alpha installations use --mode upgrade. New installations require --interface and reviewed web/logging ownership options. Existing databases, configuration, credentials and upgrade schedules are preserved.

## Current patch

Install / Update verifies every selected component file and shared dependency against release hashes and permissions before confirmation. Main Dashboard has its own version (2.0.3) and update scope within KeenTool; the main menu shows Firewall suite 4.0.1 independently of Monitor/Stats versions. See RELEASE_NOTES.md and suite/docs/UPDATE_RECOVERY.md.

## Earlier stable changes

- New coordinated 2.0.0 suite installation: fresh/upstream/alpha detection, verified file/configuration backups, atomic replacement, automatic/manual rollback and whole-package update entry point.
- Uniform Keenetic-inspired responsive navigation, shared refresh with Off/manual controls, remembered navigation/density, readable tables and a full-width Security & Health overview. Remove development banners and show versions in copyright footers.
- Dot thousands/comma decimals across rendered dashboard values; preserve raw technical data and arithmetic. Full expanded log views, bounded internal transport, log sizes and allowlisted read-only system logs without changing syslog rotation.
- Password-only HTTPS administrator access shared with Settings/Security, typed settings with ranges/presets, revision conflict handling and guarded firewall changes.
- Entware update monitoring/notifications and an explicitly requested maintenance worker that stops/restarts Entware services. Shared HTML/plain notification layout with safe tables, MTR rendering and semantic health colors.
- Independent incremental PPP syslog monitor, root broker, ktweb web-isolation tools, boot scheduler check and private helper paths. BusyBox metadata fallback removes the GNU stat requirement.

## Release baseline

Public main commit: 8d640c8b06968b0f24ce41feb1bc5b0a89c3f541. No tags or GitHub Releases existed at preparation time. Stable tag: v2.0.0.

See the complete package's CHANGELOG.md, VERSIONS.md, SECURITY.md and docs/VALIDATION.md for coordinated versions, installation, known feed limitations and test evidence. Development history is archived in docs/history/.
