# Keenetic SMB Backup Tool

**Scheduled Entware/router archives to an SMB share**, with connection testing, read-back verification, retention and notifications. Current component: **2.0.1**. This component has a **CLI**, rather than a separate web dashboard.

![SMB Backup Tool CLI rendered with a synthetic NAS configuration](https://raw.githubusercontent.com/mattheweli/KeenTool/main/docs/screenshots/smb-backup.png)

The image renders the actual shell menu with example configuration. No NAS was contacted and no backup was executed to produce it.

## Features

- Interactive configuration of SMB server/share/subdirectory, account, source folder and retention.
- Manual or cron-scheduled backup, connection testing and readable logs.
- BusyBox-compatible archive creation and optional router/system dump collection.
- Check SMB command output as well as exit status; read-back verification before recording a verified backup.
- Credential file handling and staged failure cleanup within the coordinated runtime.
- Optional retention/purge after a successful backup, plus an explicit interactive purge command.

## Installation and safe updates

These component sources are part of the **coordinated KeenTool suite**. Install the complete package from [KeenTool releases](https://github.com/mattheweli/KeenTool/releases/latest); the shared runtime, security broker, authentication and assets are required. Copying an isolated script over an older installation is not a supported upgrade.

On an existing supported installation:

```sh
/opt/bin/bash /opt/bin/keentool --check-updates
/opt/bin/bash /opt/bin/keentool --update
```

KeenTool's **Check all updates** lists each component independently. A tool's **Install / Update** checks its version, all owned files and shared dependencies against verified SHA-256 hashes and permissions. It reports missing/modified files even when the declared version is current. Review the proposed coordinated installation before confirming the archive download. Configuration, credentials, cron schedules and databases are preserved by the normal transaction-backed upgrade; the printed backup supports file rollback.

For a new router or a legacy/alpha migration, follow the complete [installation guide](https://github.com/mattheweli/KeenTool/blob/main/suite/docs/INSTALL.md). Fresh-install web/logging adoption is explicit: review it before replacing an existing listener or logging pipeline. Use `/opt/bin/bash`, root and Entware mounted at `/opt`. Dependencies are checked before installation; `--install-deps` explicitly permits installing missing Entware packages. No general `opkg upgrade` is performed by the suite updater.

## Configure and operate

Open KeenTool → **SMB Backup Tool**, or:

```sh
/opt/bin/bash /opt/bin/smb_backup_tool.sh
```

Use **Configure Wizard**, then **Test Connection**, before enabling a schedule. Enter only the share name in the Share field; specify the remote subdirectory separately. Example values are `192.0.2.10`, share `Backups`, subdirectory `Router`. Replace them with your NAS configuration.

After reviewing settings, run a backup interactively and verify its contents on the destination. Use the Scheduler menu for recurring jobs. For an already configured unattended run:

```sh
/opt/bin/bash /opt/bin/smb_backup_tool.sh -run
```

| Item | Location |
|---|---|
| Private configuration | `/opt/etc/smb_backup.cfg` |
| Log | `/opt/var/log/smb_backup.log` |
| Default source | `/opt` |

Restrict the SMB account to the intended backup share and keep the configuration private. The source can include credentials and configuration; protect destination access accordingly.

## Archive contents

The source archive preserves configuration and ordinary source files. It excludes `/opt/var/log` (including live firewall PCAP), `/opt/var/run`, `/opt/var/lock`, `/opt/tmp`, `/opt/backup_storage` and Unix sockets. These transient files are not restore data. SQLite databases are backed up separately through coherent snapshots; a binary file named `.db` that is not SQLite stays in the source archive. Archive errors still stop the backup, and retention is skipped after any failed upload/read-back verification.

## Retention, verification and restore

Review retention and the remote subdirectory carefully before enabling automatic purge: it removes eligible older backup files. A successful read-back verifies the uploaded object at that time; it is not ongoing proof of remote presence or a full disaster-recovery test. Security & Health distinguishes verified SMB backups from source-file upgrade backups.

A package rollback restores installed source/configuration at its transaction boundary. It does not automatically restore a database from an old baseline or perform a NAS backup restore. Test recovery separately using a copy of the archive and an appropriate isolated router environment.

## Troubleshooting and support

Include the installed suite/component versions, router/Entware architecture, exact command and relevant sanitized output when reporting an issue. Never post passwords, authentication cookies, SMTP credentials or your database.

- [Installation / migration](https://github.com/mattheweli/KeenTool/blob/main/suite/docs/INSTALL.md)
- [Update and repair behavior](https://github.com/mattheweli/KeenTool/blob/main/suite/docs/UPDATE_RECOVERY.md)
- [Backup and rollback](https://github.com/mattheweli/KeenTool/blob/main/suite/docs/ROLLBACK.md)
- [Security and known limitations](https://github.com/mattheweli/KeenTool/blob/main/suite/SECURITY.md)
- [Component versions and changelog](https://github.com/mattheweli/KeenTool/blob/main/suite/VERSIONS.md)

Screenshots are generated from the current application templates with **synthetic documentation data**. They are examples, not live router output or evidence of a real attack/backup. [Reproduce the screenshots](https://github.com/mattheweli/KeenTool/blob/main/suite/docs/demo/README.md).

Created and maintained by **mattheweli**. The repository's existing LICENSE applies.

## Support the project

If you find these tools useful, you can support their development with a voluntary donation. Thank you!

[![Donate with PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/MatteoRosettani)
[![Donate with Revolut](https://img.shields.io/badge/Revolut-black?style=for-the-badge&logo=revolut&logoColor=white)](https://revolut.me/matthew_eli)

Cryptocurrency donations (copy the address):

- **Ethereum (ETH):** `0x8487b6205fd76d7516f07b1117a66966dcf2f0e4`
- **Bitcoin (BTC):** `bc1qvp5dnsnw60e963dfcgk3jfsfrwys86ufccygsw`
