# Bootstrap and managed updates — KeenTool 2.0.4

## Dependency preflight

The standalone and embedded bootstrap carry the same dependency helper as the installer. The first stage verifies a working PHP CLI 8.0+ (CGI is not CLI) and the tools needed for verified download/extraction. An interactive migration lists missing requirements and asks before installing only the necessary Entware packages. `--check` is read-only; `--yes` consents to the suite update, while `--install-deps` explicitly permits missing dependency installation without a TTY. An installed but broken binary is checked again after opkg, and an unresolved loader/library problem stops migration with a diagnostic.

After the complete archive and every file checksum have been verified, the current package checks the full runtime: firewall/kernel command-line tools, SQLite JSON, vnStat, probe/MTR, capture, SMB, core utilities, CLI functions/session support, CGI 8.0+ startup and Entware FastCGI/OpenSSL/NFLOG/PCAP packages. The package manager's installed states allow ok/user/hold selections. Native kernel support and the existing lighttpd configuration are separately validated by their normal checks; administrators still own syslog/logrotate, listener and firewall policy choices.

No dependency scan changes services, rules, credentials or web configuration. Explicit opkg operations have their own lifecycle and are not undone by a suite file rollback. `opkg upgrade` is never used. A failed/declined dependency installation does not replace suite files. A `--plan` installer invocation only reports missing dependencies; `install.sh --apply --install-deps` explicitly installs missing ones before the file transaction.

## One update per menu action

Managed Firewall, Connection Monitor, Traffic Monitor, SMB and Dashboard menu actions use one coordinated update. They return before legacy dependency checks, file-by-file updater calls, page removal, FastCGI rewrites, daemon restarts or cron edits. Shared runtime and component source files continue to ship as one verified bundle. The firewall hook is not applied by this menu action.

A successful menu-triggered installation produces a private receipt and execs the new KeenTool process. A failed, declined or already-current update produces no receipt and does not restart the menu. The installer prints the actual package manifest version rather than a fixed initial version.

An already-running 2.0.0/2.0.1 menu has loaded the previous handoff code. For that first transition, update from the shell and reopen the menu once:

```sh
/opt/bin/bash /opt/bin/keentool --update
/opt/bin/bash /opt/bin/keentool
```

Automatic menu restart applies to updates initiated by 2.0.2 and later. Replacing a script on disk cannot retroactively change code already running in an older Bash process. A 1.3.4 public manager updated from main receives the new self-contained bootstrap before loading shared libraries. A manager stuck at the previous PHP-missing message can install php8-cli and retry; pinned standalone bootstraps need a newly reviewed copy to gain the dependency prompt.

## Independent component checks and global overview

Use **u. Check / install updates (KeenTool and tools)** to review KeenTool, Firewall, Pingtool, Traffic Manager, SMB Backup and Main Dashboard together. The redundant main-menu self-update action is removed; a tool's own action checks its component version, all owned program files and shared dependencies. A current Firewall 4.0.1 does not become an available update because KeenTool advances to 2.0.3. Independent Monitor/Stats/hook script versions still differ legitimately within a firewall component release.

```sh
/opt/bin/bash /opt/bin/keentool --check-updates
/opt/bin/bash /opt/bin/keentool --update
/opt/bin/bash /opt/bin/keentool_update --component keenetic-firewall --check
/opt/bin/bash /opt/bin/keentool_update --component keenetic-firewall
```

Checks fetch the GitHub release record and a small versioned component overview (maximum 64 KiB), verified against the GitHub asset SHA-256. The overview includes the SHA-256, file mode and ownership of every INSTALL.tsv target. Checks compare all selected component files and shared dependencies locally without downloading the suite archive. Global checks inspect all targets. A source mismatch, missing file or incorrect permission triggers a proposed repair even when the declared component version is current. Each difference is reported before consent. Configuration and database files are not installation targets and are excluded. When the selected scope has an update, the report lists all component changes and the coordinated shared runtime before asking **Apply this coordinated update? [y/N]**. Decline or a noninteractive invocation without --yes leaves the archive undownloaded. --yes is explicit installation consent; --check always stops before package download.

An accepted update installs the complete coordinated bundle, including unchanged component files, through the existing backup/rollback transaction. This keeps the manager, security broker and shared assets compatible. The package manifest must match the reviewed overview. Newer installed suite/component versions prevent a downgrade. Settings, credentials and databases remain preserved by the installer. The firewall hook is not applied by this action.

For older published releases without an overview, full-suite checks retain their previous version comparison; component actions explain that per-component metadata is unavailable rather than treating the suite version as a tool version.

## Full-package verification and repair

Use **r. Verify / repair installed package files** separately from version checks:

```sh
/opt/bin/bash /opt/bin/keentool_update --repair
/opt/bin/bash /opt/bin/keentool_update --repair --check
```

Repair asks before downloading the complete verified archive, then compares all INSTALL.tsv program targets against source hashes and modes. It detects missing/stale files even if installed-release.json says the latest version. With differences, it asks again before applying the complete transaction-backed repair; a check-only repair never installs. --yes explicitly authorizes both steps. Deliberate local source changes are reported and replaced only by an accepted repair. Configuration and database files are excluded. --reinstall remains an explicit complete-suite reinstall, also confirmed before download.

Main Dashboard stays in the KeenTool repository but has its own Dashboard version and menu scope. Its actual HTML version is compared separately from the manager, so a 2.0.2 dashboard is not labeled current merely because KeenTool is 2.0.3 or 2.0.4. The main Firewall summary shows the suite version, while Monitor/Stats versions remain separate in its submenu.

This release changes KeenTool/Dashboard/bootstrap/updater/verifier only. Installer 1.0.2 and the firewall repository 4.0.1 are retained; no firewall rule or history policy changes are included.

## Deleted current directory and legacy web backup warnings

If an existing shell prints `getcwd: cannot access parent directories`, its current directory was removed. Run `cd /` before starting KeenTool. The manager, update handoff and standalone updater/bootstrap recover a missing directory before spawning further helpers. They leave a valid current directory unchanged. An interpreter can print one initial warning before any script code runs.

A missing old web-isolation `permissions.tsv` cannot restore historical modes or ownership. The helper retains an explicit warning, skips reading the absent ledger and refuses historical permission rollback. It does not fabricate original metadata or turn this warning into evidence that the coordinated source update failed. Review the separate release transaction backup printed by the installer for source-update rollback.
