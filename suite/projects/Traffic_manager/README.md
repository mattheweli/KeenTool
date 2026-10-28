# Keenetic Traffic Manager

**vnStat-based interface traffic history and a responsive web dashboard** for Keenetic routers with Entware. Current component: **2.0.1**.

![Traffic Monitor with received/sent doughnuts, totals and interface history](https://raw.githubusercontent.com/mattheweli/KeenTool/main/docs/screenshots/traffic.png)

## Features

- Multi-interface selection and friendly aliases, including PPP and dotted interface names.
- Received/sent totals for today, yesterday, current/previous month and all available history.
- Consistent doughnut colors, estimated usage, readable history tables and complete dates in Top 10 Days.
- Optional monthly quota display and per-interface data exports for the Main Dashboard.
- Last-known-good export retention when vnStat fails, rather than replacing valid data with an empty/error response.
- Shared navigation, table density, number formatting and browser auto-refresh controls.

## Installation and safe updates

These component sources are part of the **coordinated KeenTool suite**. Install the complete package from [KeenTool releases](https://github.com/mattheweli/KeenTool/releases/latest); the shared runtime, security broker, authentication and assets are required. Copying an isolated script over an older installation is not a supported upgrade.

On an existing supported installation:

```sh
/opt/bin/bash /opt/bin/keentool --check-updates
/opt/bin/bash /opt/bin/keentool --update
```

KeenTool's **Check all updates** lists each component independently. A tool's **Install / Update** checks its version, all owned files and shared dependencies against verified SHA-256 hashes and permissions. It reports missing/modified files even when the declared version is current. Review the proposed coordinated installation before confirming the archive download. Configuration, credentials, cron schedules and databases are preserved by the normal transaction-backed upgrade; the printed backup supports file rollback.

For a new router or a legacy/alpha migration, follow the complete [installation guide](https://github.com/mattheweli/KeenTool/blob/main/suite/docs/INSTALL.md). Fresh-install web/logging adoption is explicit: review it before replacing an existing listener or logging pipeline. Use `/opt/bin/bash`, root and Entware mounted at `/opt`. Dependencies are checked before installation; `--install-deps` explicitly permits installing missing Entware packages. No general `opkg upgrade` is performed by the suite updater.

## Interface configuration and refresh

Use KeenTool → **Traffic Manager** to select the actual interface and configure its cron job. For example:

```sh
/opt/bin/bash /opt/bin/traffic_manager.sh ppp0 force
```

Replace `ppp0` with the interface that vnStat actually monitors. A fresh installation registers the selected WAN with vnStat and starts its native service; an upgrade preserves existing databases and schedules. The default new-install export schedule is every ten minutes.

The generated page is `/opt/var/www/vnstat/index.html`. Interface aliases and quota settings are managed through KeenTool/Web Settings. Changing a display alias does not rename the underlying vnStat database/interface.

## Understand the numbers

vnStat supplies persistent traffic totals; the script exports them and renders the interface history. The webpage refresh fetches exports without changing vnStat sampling or cron schedules. Estimates are projections from elapsed time, not guaranteed future usage. Quota display is informational and does not enforce a traffic cap.

Traffic units depend on the displayed formatter; values use dot thousands and comma decimals. Raw exports and technical fields remain machine-readable. Interface availability, daemon state and export freshness are separate signals.

## Troubleshooting missing history

1. Check that `vnstatd` and the router scheduler are running.
2. Confirm the interface exists in vnStat and matches the configured name; avoid an empty or `Unknown` interface.
3. Run the explicit command above and inspect its output. A warning about retaining old data means the previous export remains displayed.
4. Check the database location/permissions and interface registration before assuming historical data was deleted. Never initialize or remove a vnStat database merely to refresh the webpage.

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
