# KeenTool 2.0.3

Relative to published v2.0.2 (main `b65b265032a35469db2cdc0c2fdaaceb60a79264`).

- Check a selected tool against its own installed and published component versions. An available KeenTool update does not trigger an update when the selected Firewall, Pingtool, Traffic Manager or SMB component is current.
- Add a main-menu **Check all updates (KeenTool and tools)** overview for the five components, showing installed version, available version and status. Self-update explicitly selects KeenTool.
- Fetch only the GitHub release record and a small component overview during version checks. Bind the overview URL, stable version, size and SHA-256 to the published GitHub release. Before confirmation, disclose every changed component, shared runtime coordination and release changes. Download the full archive only after interactive consent or explicit --yes.
- Preserve coordinated installation, HTTPS-only transport, archive and internal file checksum verification, backup/rollback, dependency preflight and successful-install menu restart. Verify that the downloaded package component versions match the approved overview. Refuse downgrades, including newer component versions within a mixed installation.
- Separate source verification and repair into **Verify / repair installed package files** and explicit --repair. This operation asks before downloading the archive, compares actual files and modes, then asks before applying a repair. --repair --check verifies without installation. Ordinary version checks no longer audit or silently repair files.
- Keep compatibility with older releases without an overview for complete-suite checks and explicit repair; do not invent per-tool versions from the suite number. Publish versioned component overview assets and checksum sidecars with this and future complete releases.
- Extend isolated transport/menu tests for per-tool and global scopes, unchanged components, no archive download before consent, interactive decline, explicit repair, overview tampering and package/overview mismatch.

Installer 1.0.2, Firewall 4.0.1, Pingtool/Traffic/SMB 2.0.0 and database/history behavior are unchanged. Updater/verifier/bootstrap advance to 1.0.2. See [Update recovery](docs/UPDATE_RECOVERY.md) and the [2.0.2 changelog](docs/history/STABLE_2.0.2.md).

## Upgrade

Update through `/opt/bin/bash /opt/bin/keentool --update`. Starting with the 2.0.3 menu, **u. Check all updates (KeenTool and tools)** lists all five components; a tool's own update action checks only its version. The report shows changes and coordinated shared-runtime requirements before asking for confirmation and downloading the full archive. Explicit --yes remains available for requested unattended updates. A current firewall is not updated merely because KeenTool has a newer version.

Use **r. Verify / repair installed package files** or `keentool_update --repair` separately for source verification and repair; ordinary version checks do not audit source files. See suite/docs/UPDATE_RECOVERY.md. Full-package installation, backup/rollback, dependency checks, HTTPS/checksum verification, successful-update menu restart and preservation of settings, credentials, schedules and databases remain in place.

## Validation

47 isolated checks pass locally. Coverage includes mocked remote transport with real verifiers, independent tool/all scopes, no archive before consent, interactive decline, explicit repair, overview tampering, package/overview consistency and downgrade refusal; migration, file transactions, history, notifications and UI regression checks remain included. GitHub CI must pass for the exact release commit before publication. No physical-router reboot or live SMTP send is claimed.
