# KeenTool 2.0.4 — stable source package

KeenTool integrates a router dashboard, dual-stack firewall, connection and traffic history, SMB backups, notifications, Entware maintenance, Security & Health and administrator Settings for Keenetic/Entware.

The complete suite is the supported installation unit. Shared runtime, security broker, administrator authentication and assets ship together. The other repositories remain component source repositories and require this runtime; copying one script over an older installation is not a supported upgrade.

- [Installation and migration](docs/INSTALL.md)
- [Backup, rollback and removal](docs/ROLLBACK.md)
- [Stable changelog](CHANGELOG.md)
- [Component versions](VERSIONS.md)
- [Security and known limitations](SECURITY.md)
- [Validation and live acceptance](docs/VALIDATION.md)
- [GitHub release preparation](docs/RELEASING.md)

Remote update: `keentool --check-updates` checks GitHub; `keentool --update` shows component versions and changes, asks for confirmation, then downloads/verifies and installs the coordinated stable suite. `keentool_update --component keenetic-firewall --check` checks the firewall version, every owned file and shared dependency; `keentool_update --repair` explicitly verifies/repairs the entire installed package. Public legacy installations migrate through their existing Update KeenTool menu, using a self-contained entry before shared libraries load. Pinned alpha installations run bootstrap.sh once.

Release date: 2026-10-23. Installer: 1.0.2. Firewall repository release: 4.0.1; unchanged components keep their published versions. This patch verifies all selected component files during Install / Update, reports the correct Firewall suite version and gives Dashboard 2.0.3 its own update scope within the KeenTool repository. Read [Update recovery](docs/UPDATE_RECOVERY.md). The 7/30-day firewall history policy from 2.0.1 is unchanged. See [Firewall history](docs/FIREWALL_HISTORY.md) for precision, measurements and backup limitations. The original stable and alpha development notes remain archived under docs/history/.

All six pages display their component version in the copyright footer. Development banners are removed. Generated Ping and Traffic pages adopt the new template at their next run or with force.
