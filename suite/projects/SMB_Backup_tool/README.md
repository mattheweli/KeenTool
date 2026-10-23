# SMB_Backup_tool 2.0.0

Stable component sources for the KeenTool suite. Release date: 2026-10-22.

## Installation and updates

Install the complete KeenTool 2.0.0 release from https://github.com/mattheweli/KeenTool/releases. The shared runtime, assets, authentication and security broker are required. Do not copy this component alone over an older installation.

For an extracted complete package, use /opt/bin/bash ./install.sh --plan and follow docs/INSTALL.md. Existing public-source and local-alpha installations use --mode upgrade. New installations require --interface and reviewed web/logging ownership options. Existing databases, configuration, credentials and upgrade schedules are preserved.

## Changes

- Stable 2.0.0 uses the shared Entware Bash runtime, atomic job locks and maintenance deferral; selective uninstallation preserves configuration/data by default.
- Keep existing backup configuration, shares and schedules across package upgrades. Verify completed backup outcomes and expose verified backup state to Security & Health where available.
- Shared readable HTML/plain notifications and isolated checks for archive/transport failure behavior. No automatic credentials or new SMB backup jobs are introduced by suite installation.

## Release baseline

Public main commit: 48b1a83804c3dc9155b7eeb20f01c942c2f3e3c7. No tags or GitHub Releases existed at preparation time. Stable tag: v2.0.0.

See the complete package's CHANGELOG.md, VERSIONS.md, SECURITY.md and docs/VALIDATION.md for coordinated versions, installation, known feed limitations and test evidence. Development history is archived in docs/history/.
