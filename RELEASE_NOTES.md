# KeenTool coordinated package 2.0.26

## Coordinated package 2.0.26 / KeenTool 2.0.13 — 2026-11-12

- Show package-index output and automatically follow Entware upgrade logs in the terminal. Report phases, per-package progress and final exit status. Add entware_manager --follow, keentool --entware-follow and menu option 4 for reconnecting.
- Include /opt/usr/bin and /opt/usr/sbin in manager, Entware worker, installer and bootstrap/updater command paths. Fail with named missing commands before starting maintenance.
- Prepare an independent BusyBox runtime and applet manifest before stopping services. Keep package-script commands available while BusyBox links change; clear Bash command hashes and recreate missing applet links before service restart. Existing files and symlinks are not overwritten.
- Upgrade confirmed packages in individual logged transactions after predownload. Record package exit codes; stop on the first failure and recover services without automatically retrying or claiming a package rollback.
- Isolate the worker process group from terminal Ctrl+C/hangup; closing the live view does not interrupt the upgrade. Record successful manual service recovery separately from the previous opkg result.
- Add regressions reproducing lost sh/mkdir/rm links, opkg exit 134, interrupted terminal viewing, per-package error propagation and successful complete batches. Release CI repeats recovery with pinned BusyBox 1.37.

Package 2.0.26; KeenTool manager 2.0.13; Entware manager 1.0.1; installer 1.0.9; updater/bootstrap 1.0.8. Firewall 4.0.14, Dashboard 2.0.4, Pingtool 2.0.2, Traffic 2.0.1 and SMB 2.0.1 are unchanged.

Update KeenTool using u. Then open p → Upgrade to update Entware; the suite release does not run opkg upgrade automatically. Review and explicitly confirm the Entware package list. Physical-router package upgrades are not independently performed by release CI.
