# KeenTool 2.0.0 — stable source package

KeenTool integrates a router dashboard, dual-stack firewall, connection and traffic history, SMB backups, notifications, Entware maintenance, Security & Health and administrator Settings for Keenetic/Entware.

The complete suite is the supported installation unit. Shared runtime, security broker, administrator authentication and assets ship together. The other repositories remain component source repositories and require this runtime; copying one script over an older installation is not a supported upgrade.

- [Installation and migration](docs/INSTALL.md)
- [Backup, rollback and removal](docs/ROLLBACK.md)
- [Stable changelog](CHANGELOG.md)
- [Component versions](VERSIONS.md)
- [Security and known limitations](SECURITY.md)
- [Validation and live acceptance](docs/VALIDATION.md)
- [GitHub release preparation](docs/RELEASING.md)

Remote update: `keentool --check-updates` checks GitHub; `keentool --update` downloads/verifies a newer published stable suite and asks before installation. Public legacy installations migrate through their existing Update KeenTool menu, using a self-contained entry before shared libraries load. Pinned alpha installations run bootstrap.sh once.

Release date: 2026-10-22. Installer and shared helpers: 1.0.0. Firewall repository release: 4.0.0; component versions are listed individually. The first stable package is based on locally tested 20261020-r50 and verified public upstream commits recorded in UPSTREAM_BASELINES.json. No upstream tags or GitHub Releases existed at inspection time.

All six pages display their component version in the copyright footer. Development banners are removed. Generated Ping and Traffic pages adopt the new template at their next run or with force.
