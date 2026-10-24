# KeenTool

**A package manager and monitoring dashboard for Keenetic routers running Entware.** Manage the firewall, WAN/PPP connectivity, traffic history, SMB backups, notifications and Entware maintenance from a consistent CLI and web interface.

Current coordinated release: **2.0.7**. The Main Dashboard is independently versioned **2.0.4**, while remaining in this repository.

![System Dashboard: firewall, traffic, connection and security summaries](https://raw.githubusercontent.com/mattheweli/KeenTool/main/docs/screenshots/dashboard.png)

## What is included

| Component | Version | Purpose |
|---|---:|---|
| KeenTool manager | 2.0.7 | Installation, configuration, verified updates and maintenance |
| Main Dashboard | 2.0.4 | Shared overview and readable system/application logs |
| [Firewall](https://github.com/mattheweli/keenetic-firewall) | 4.0.2 | IPv4/IPv6 filtering, blocklists, diagnostics and history |
| [Connection Monitor](https://github.com/mattheweli/keenetic-pingtool) | 2.0.1 | Latency, jitter, packet loss and PPP event correlation |
| [Traffic Manager](https://github.com/mattheweli/Traffic_manager) | 2.0.1 | vnStat history, projections and multi-interface views |
| [SMB Backup](https://github.com/mattheweli/SMB_Backup_tool) | 2.0.1 | Scheduled archives, read-back verification and retention |

Shared pages include **Security & Health** and administrator **Settings**. Version numbers describe the individual component: the manager, dashboard, firewall suite and its scripts need not share a number.

## Web interface

The responsive Keenetic-inspired layout offers common navigation, a remembered auto-refresh interval (Off / 30 seconds / 1 minute / 5 minutes), manual refresh, table density and consistent number formatting. Browser refresh does not change router collection schedules. Expanded logs show their complete content through bounded transfers and display file sizes; existing syslog/logrotate policy is preserved.

Security & Health shows rule verification, web privilege isolation, free storage, database sizes, services, blocklist outcomes, event history and period comparisons. Green indicates verified healthy results, yellow means unknown/waiting/stale, and red indicates a detected failure. Snapshot freshness uses the slower configured monitor/browser cadence, not a fixed three-minute threshold.

![Security and Health: verified rules, web isolation, storage and blocklist status](https://raw.githubusercontent.com/mattheweli/KeenTool/main/docs/screenshots/security.png)

Settings uses HTTPS administrator authentication, typed fields, presets/ranges and revision checks. Viewing public status does not grant permission to change firewall policy. Configure an administrator password with:

```sh
/opt/bin/bash /opt/bin/firewall_admin_password
```

## Installation and safe updates

These component sources are part of the **coordinated KeenTool suite**. Install the complete package from [KeenTool releases](https://github.com/mattheweli/KeenTool/releases/latest); the shared runtime, security broker, authentication and assets are required. Copying an isolated script over an older installation is not a supported upgrade.

On an existing supported installation:

```sh
/opt/bin/bash /opt/bin/keentool --check-updates
/opt/bin/bash /opt/bin/keentool --update
```

KeenTool's **Check all updates** lists each component independently. A tool's **Install / Update** checks its version, all owned files and shared dependencies against verified SHA-256 hashes and permissions. It reports missing/modified files even when the declared version is current. Review the proposed coordinated installation before confirming the archive download. Configuration, credentials, cron schedules and databases are preserved by the normal transaction-backed upgrade; the printed backup supports file rollback.

For a new router or a legacy/alpha migration, follow the complete [installation guide](https://github.com/mattheweli/KeenTool/blob/main/suite/docs/INSTALL.md). Fresh-install web/logging adoption is explicit: review it before replacing an existing listener or logging pipeline. Use `/opt/bin/bash`, root and Entware mounted at `/opt`. Dependencies are checked before installation; `--install-deps` explicitly permits installing missing Entware packages. No general `opkg upgrade` is performed by the suite updater.

## First setup and operation

1. Install Entware/Bash and download the complete release. Verify its checksum and read `install.sh --help` and the installation plan.
2. Select the real WAN interface (for example `ppp0`). Review ownership of web/TLS and ulogd logging on a fresh router; preserve custom configurations on upgrades.
3. Open `/opt/bin/keentool` with Entware Bash. Configure email/Telegram only if required, review cron and configure the individual tools.
4. Review firewall countries, list settings and management bypasses before enabling filtering. Fresh installations start with filtering disabled.
5. Serve `/opt/var/www` through the reviewed HTTPS listener. The optional dedicated configuration uses port **8080**; existing installations retain their configured listener.

```sh
/opt/bin/bash /opt/bin/keentool
/opt/bin/bash /opt/bin/firewall_health
/opt/bin/bash /opt/bin/wan_syslog_service status
/opt/bin/bash /opt/bin/keentool_security_service status
```

CLI **u** checks all components; **r** explicitly verifies/repairs the whole package; **s** selects the manager update. Successful menu updates restart the manager. Tool actions check their own files, but accepted installation remains coordinated for shared-runtime compatibility.

## Notifications and maintenance

HTML/plain email layouts cover summaries, connection warnings, MTR and security state. PPP syslog events and sampled ping failures have distinct meanings: high latency/partial loss is not a measured WAN outage. Entware update checks can notify about available packages; an explicitly requested Entware upgrade uses its maintenance worker and service stop/restart lifecycle.

Firewall historical aggregation keeps recent raw samples, then hourly/daily IP/list totals. It preserves hit totals while reducing older time precision. Read the [history policy](https://github.com/mattheweli/KeenTool/blob/main/suite/docs/FIREWALL_HISTORY.md) before enabling or changing it.

## Repository layout

- Root `keentool`, `index.html`, notification modules and `bootstrap.sh`: manager/dashboard component sources and migration entry.
- `suite/`: the complete installable coordinated runtime, installer, rollback, manifests, all component sources and tests.
- `docs/screenshots/`: generated documentation examples; generation sources are in `suite/docs/demo/`.

## Troubleshooting and support

Include the installed suite/component versions, router/Entware architecture, exact command and relevant sanitized output when reporting an issue. Never post passwords, authentication cookies, SMTP credentials or your database.

- [Installation / migration](https://github.com/mattheweli/KeenTool/blob/main/suite/docs/INSTALL.md)
- [Update and repair behavior](https://github.com/mattheweli/KeenTool/blob/main/suite/docs/UPDATE_RECOVERY.md)
- [Backup and rollback](https://github.com/mattheweli/KeenTool/blob/main/suite/docs/ROLLBACK.md)
- [Security and known limitations](https://github.com/mattheweli/KeenTool/blob/main/suite/SECURITY.md)
- [Component versions and changelog](https://github.com/mattheweli/KeenTool/blob/main/suite/VERSIONS.md)

Screenshots are generated from the current application templates with **synthetic documentation data**. They are examples, not live router output or evidence of a real attack/backup. [Reproduce the screenshots](https://github.com/mattheweli/KeenTool/blob/main/suite/docs/demo/README.md).

Created and maintained by **mattheweli**. The repository's existing LICENSE applies. Optional project support: [PayPal](https://paypal.me/MatteoRosettani) · [Revolut](https://revolut.me/matthew_eli).
