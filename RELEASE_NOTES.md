# KeenTool 2.0.6

## SMB Backup Tool 2.0.1 / KeenTool 2.0.6

- Correct tar exclusion paths when the backup source has `/` as its parent (including the default `/opt`). Previously an extra slash left exclusions absolute, while archive member names were relative; live logs/PCAP could enter the archive and fail backup creation.
- Normalize trailing slashes in source settings. Exclude `/opt/var/run` and `/opt/var/lock` alongside logs, temporary files and local backup staging. Exclude Unix sockets elsewhere in the source using a checked NUL-delimited inventory.
- Inspect the full 16-byte SQLite header after Base64 encoding; binary/non-SQLite `.db` files no longer inject NUL bytes into Bash command substitution. Retain coherent SQLite snapshots and verify their integrity.
- Keep strict archive error handling, remote read-back/checksum verification and retention only after successful verification. Do not stop services or ignore arbitrary tar failures. Configuration and scheduling are preserved.
- Add isolated archive regression coverage for root-parent/trailing-slash sources, volatile paths, real Unix sockets on CI, non-SQLite binary files and SQLite record preservation. Exercise GNU and BusyBox tar where available; NAS transport and router export are mocked.

## Update

Use the complete verified KeenTool suite: `/opt/bin/bash /opt/bin/keentool --update`, then retry the backup. Runtime sockets, locks, logs and temporary backup files are intentionally omitted; configuration and database snapshots are retained. Existing settings, credentials, cron and databases are preserved by the suite installer. Validation uses isolated fixtures; no live NAS transfer or physical-router reboot is claimed.
