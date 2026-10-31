# KeenTool coordinated package 2.0.22 — stable source package

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

Release date: 2026-10-28. Installer: 1.0.8. Firewall 4.0.11; Pingtool 2.0.2; Traffic 2.0.1; SMB 2.0.1; Main Dashboard 2.0.4. Manager 2.0.12 adds grouped CLI plans/release notes and a choice to retain recovery backups. Temporary transaction rollback protection remains enabled. Filtering, collection, history aggregation and upgrade rollback behavior are unchanged.

All six pages display their component version in the copyright footer. Development banners are removed. Generated Ping and Traffic pages adopt the new template at their next run or with force.

The successful installer now prompts for a missing dedicated web admin password, including Legacy migrations. Existing passwords remain unchanged. Noninteractive installation prints the manual setup command without creating default credentials.

The installer offers HTTPS conversion for a simple existing HTTP listener, retaining the current port, PHP backend and includes. Custom TLS/isolated/conditional listeners require review. TLS migration uses the existing backup/rollback transaction and a local readiness probe.

[Guarded firewall upgrade](docs/FIREWALL_UPGRADE.md): enabled installations can confirm application from SSH, with independent timeout recovery of both previous rules and source files. Deferral preserves the previous boot hook.

Minimal-BusyBox guardian startup and rollback service handling are corrected. See FIREWALL_UPGRADE.md for interrupted 2.0.14 recovery before reinstalling.

## Support the project

If you find these tools useful, you can support their development with a voluntary donation. Thank you!

[![Donate with PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/MatteoRosettani)
[![Donate with Revolut](https://img.shields.io/badge/Revolut-black?style=for-the-badge&logo=revolut&logoColor=white)](https://revolut.me/matthew_eli)

Cryptocurrency donations (copy the address):

- **Ethereum (ETH):** `0x8487b6205fd76d7516f07b1117a66966dcf2f0e4`
- **Bitcoin (BTC):** `bc1qvp5dnsnw60e963dfcgk3jfsfrwys86ufccygsw`

See [DATABASE_STORAGE.md](docs/DATABASE_STORAGE.md) for explicit compact Firewall storage, balanced history and lossless Ping/vnStat maintenance. Installation does not convert databases.

See docs/SECURITY_EMAIL.md for the independent summary switch and docs/FIREWALL_UPGRADE.md for automatic verified updates of already adopted hooks.
