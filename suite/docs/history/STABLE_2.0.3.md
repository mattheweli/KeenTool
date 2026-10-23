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
