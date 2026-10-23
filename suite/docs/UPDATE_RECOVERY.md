# Bootstrap and managed updates — KeenTool 2.0.2

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

## Component version and repair

The firewall menu separates the installed repository component version from the Monitor and Stats script versions. A 4.0.1 firewall bundle can legitimately contain Monitor 4.0.0 and Stats 4.0.1; only changed scripts advance. Updating a component shows its installed/available version from the manifest and labels the coordinated KeenTool suite version separately.

```sh
/opt/bin/bash /opt/bin/keentool_update --component keenetic-firewall --check
/opt/bin/bash /opt/bin/keentool_update --component keenetic-firewall
```

A component check downloads and verifies the complete stable archive, then compares all installed package targets with its source hashes and file modes. This detects a missing/stale script even if installed-release.json claims the current version. A repair asks before a full verified reinstall of the same suite; `--check` never repairs. No older published suite may replace a newer local suite. Deliberate source customizations are reported as different files, and an accepted repair replaces them through the normal backup/rollback transaction. Configuration and database files are outside this source audit.

This release changes KeenTool/bootstrap/updater/installer only. The firewall repository remains 4.0.1. No firewall rule change or new firewall repository tag is implied by KeenTool 2.0.2.
