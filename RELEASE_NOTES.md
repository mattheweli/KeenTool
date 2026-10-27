# KeenTool coordinated package 2.0.11

## KeenTool manager 2.0.9 / coordinated package 2.0.11 — 2026-10-27

- Organize CLI update output into package/component versions, grouped missing/changed/permission/unsafe-path file reports, component changes and wrapped release notes. Installation plans group only new/changed/permission targets, summarize matching targets and make clear the complete coordinated transaction still covers all files. Suppress the repeated plan in the apply child after the remote updater has already displayed and revalidated it.
- Add an interactive recovery-backup retention choice to installation and verified updates. Keeping a backup retains the existing manual-rollback archive; declining removes temporary recovery copies only after a successful installation. Verified temporary copies remain mandatory during the transaction so partial failures can roll back safely. Existing permanent backups are never automatically removed.
- Add `--keep-backup` and `--no-backup` to installer/updater CLI. These control retention after success, not in-flight rollback protection. Unattended runs and `--yes` without a backup flag preserve the conservative keep behavior. Old installers reject discard requests rather than silently ignoring them. First upgrades launched by older background updaters can obtain the choice through the controlling terminal.
- Store non-retained transaction copies in a private durable transaction directory. Successful installation or successful automatic rollback removes them; failed recovery or an uncatchable interruption leaves recovery material available for review. Automatic cleanup validates the transaction root/name/retention flag and never follows symlinks into unrelated content.

Manager 2.0.9, installer 1.0.3, remote updater/bootstrap 1.0.5, verifier 1.0.4 and transaction engine 1.0.2 carry these changes. Firewall, Pingtool, Traffic Manager, SMB Backup, Dashboard, credentials, databases, schedules and firewall policy are unchanged. The choice concerns installation recovery copies, not SMB archives or database-maintenance backups.

## Update

Run `cd /`, then `/opt/bin/bash /opt/bin/keentool --update`. Review the grouped plan and choose whether to retain a recovery backup. For later unattended updates use `--yes --keep-backup` or `--yes --no-backup` explicitly. No-backup mode removes temporary recovery copies after success; it still protects a failed transaction. Existing backups remain untouched. Automated validation uses isolated fixtures and mocked router/service commands, not a live router.
