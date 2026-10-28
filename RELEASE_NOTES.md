# KeenTool coordinated package 2.0.12

## Coordinated package 2.0.12 — 2026-10-28

- After a successful installation/migration, start dedicated web administrator password setup when no credential file exists. This covers first Legacy upgrades and fresh installs without requiring users to discover the password menu afterwards. Password input is hidden, repeated for confirmation and retried after length/confirmation errors. No router username/account password is changed.
- Read the controlling terminal when a legacy updater launches its installer with stdin redirected to /dev/null. Preserve an already configured password and revision byte-for-byte; report an invalid existing credential file for explicit review rather than silently replacing it.
- Noninteractive installation remains possible without a generated or default password: print the pending setup command and leave administrator login unavailable until configured. The password step runs after successful source installation; failure/EOF does not undo the installed package, and interrupted setup can be completed with KeenTool option A.
- Serialize CLI credential writes with a private lock and add a missing-only setter mode so concurrent/manual setup is never overwritten by migration. Passwords travel to the PHP bcrypt setter on stdin, never command arguments or log files. Explicit password reset remains available.

Installer 1.0.4 and the password CLI/setter 1.0.1 carry these changes. Manager 2.0.9, Dashboard 2.0.4, bootstrap/updater 1.0.5 and every other tool keep their versions. Existing credentials, database contents, schedules and firewall policy are preserved. Automated tests use isolated roots and synthetic passwords, not a live router.

## Upgrade

Use KeenTool → u or `keentool --update`. During the first migration without existing web credentials, enter and repeat a dedicated administrator password in the SSH terminal. Existing credentials are preserved. If setup is interrupted or no terminal is available, finish it with KeenTool option A or `/opt/bin/bash /opt/bin/firewall_admin_password`. This password is independent of the router account. Installation recovery-backup retention choices are unchanged.
