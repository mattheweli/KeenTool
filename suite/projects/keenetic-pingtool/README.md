# Keenetic Connection Monitor / Pingtool

**IPv4/IPv6 latency, jitter, packet-loss history and PPP-aware WAN notifications** for Keenetic routers with Entware. Current component: **2.0.1**.

![Connection Monitor with latency, jitter and time-range controls](https://raw.githubusercontent.com/mattheweli/KeenTool/main/docs/screenshots/ping.png)

## Features

- Separate IPv4/IPv6 targets, current results and historical latency/jitter/loss charts.
- Time-based views: one hour, one day, one week, 30 days and maximum available history.
- Original sample counts versus rendered chart points, coverage dates for both families, optional bucket peaks and logarithmic chart axes.
- Warning thresholds, MTR diagnostics and optional email/Telegram integration.
- Incremental PPP syslog monitoring for actual WAN events, independent from scheduled ping sampling.
- Existing syslog-ng and logrotate settings are preserved; rotation/truncation/partial-line handling belongs to the reader.

## Installation and safe updates

These component sources are part of the **coordinated KeenTool suite**. Install the complete package from [KeenTool releases](https://github.com/mattheweli/KeenTool/releases/latest); the shared runtime, security broker, authentication and assets are required. Copying an isolated script over an older installation is not a supported upgrade.

On an existing supported installation:

```sh
/opt/bin/bash /opt/bin/keentool --check-updates
/opt/bin/bash /opt/bin/keentool --update
```

KeenTool's **Check all updates** lists each component independently. A tool's **Install / Update** checks its version, all owned files and shared dependencies against verified SHA-256 hashes and permissions. It reports missing/modified files even when the declared version is current. Review the proposed coordinated installation before confirming the archive download. Configuration, credentials, cron schedules and databases are preserved by the normal transaction-backed upgrade; the printed backup supports file rollback.

For a new router or a legacy/alpha migration, follow the complete [installation guide](https://github.com/mattheweli/KeenTool/blob/main/suite/docs/INSTALL.md). Fresh-install web/logging adoption is explicit: review it before replacing an existing listener or logging pipeline. Use `/opt/bin/bash`, root and Entware mounted at `/opt`. Dependencies are checked before installation; `--install-deps` explicitly permits installing missing Entware packages. No general `opkg upgrade` is performed by the suite updater.

## Configure and run

Use KeenTool → **Ping Monitor** for settings and its schedule. Persistent settings live in `/opt/etc/pingtool.conf`; configure targets, IPv6, thresholds and retention through the supported settings UI/menu.

```sh
/opt/bin/bash /opt/bin/pingtool.sh
/opt/bin/bash /opt/bin/pingtool.sh force
/opt/bin/bash /opt/bin/wan_syslog_service status
```

`force` regenerates the page template and performs a normal measurement cycle. The generated dashboard is `/opt/var/www/ping/index.html`. On a fresh installation the default ping cron runs at minutes 12 and 42; existing schedules remain unchanged.

## Understand samples, chart points and peaks

A **sample** is an original measurement. A **chart point** can be the average of multiple samples in a time bucket, keeping large ranges readable. “Show latency and packet-loss peaks” overlays bucket maxima; it does not turn averages into new measurements or improve collection frequency. A MAX view is bounded by retained database history, not an unlimited archive.

## Notifications and PPP events

Latency/partial-loss warnings indicate sampled instability. Recovery after a complete ping failure is detected at the next scheduled successful check; it is not automatically the duration of a continuous physical WAN outage. PPP daemon events can provide separate disconnect/reconnect timestamps for a monitored interface. Messages identify the WAN and IPv4/IPv6 where applicable.

The WAN reader requires real PPP messages in the existing syslog file. It reads incrementally; it does not rotate or rewrite that log. Configure syslog-ng routing separately when necessary. Review monitor status and the sanitized event timeline if timestamps or events are missing.

## Dependencies and limitations

Requires the coordinated runtime, working ping tools, SQLite and optional MTR/notification dependencies. A healthy public target does not prove every service is reachable; a failing target can also reflect upstream ICMP policy. Probe/schedule settings determine detection latency and resource use. Collection, retention and browser refresh are separate settings.

## Troubleshooting and support

Include the installed suite/component versions, router/Entware architecture, exact command and relevant sanitized output when reporting an issue. Never post passwords, authentication cookies, SMTP credentials or your database.

- [Installation / migration](https://github.com/mattheweli/KeenTool/blob/main/suite/docs/INSTALL.md)
- [Update and repair behavior](https://github.com/mattheweli/KeenTool/blob/main/suite/docs/UPDATE_RECOVERY.md)
- [Backup and rollback](https://github.com/mattheweli/KeenTool/blob/main/suite/docs/ROLLBACK.md)
- [Security and known limitations](https://github.com/mattheweli/KeenTool/blob/main/suite/SECURITY.md)
- [Component versions and changelog](https://github.com/mattheweli/KeenTool/blob/main/suite/VERSIONS.md)

Screenshots are generated from the current application templates with **synthetic documentation data**. They are examples, not live router output or evidence of a real attack/backup. [Reproduce the screenshots](https://github.com/mattheweli/KeenTool/blob/main/suite/docs/demo/README.md).

Created and maintained by **mattheweli**. The repository's existing LICENSE applies. Optional project support: [PayPal](https://paypal.me/MatteoRosettani) · [Revolut](https://revolut.me/matthew_eli).
