# KeenTool 2.0.7

## KeenTool 2.0.7 — 2026-10-24

Relative to v2.0.6 (main `f01280b85b2ee70a65e514bf0181c7715c5c8211`).

- Fix the Main Menu Entware update counter when `/opt/etc/keentool/entware/available.txt` has not been created by a successful check. Redirect stderr before opening stdin and display a count only on a successful read, so a missing directory/file displays `[unchecked]` without a shell error between the H and p menu entries.
- Preserve the difference between unchecked and zero available updates. Rendering the menu neither creates a fake empty result nor performs an Entware check/upgrade; a successful existing check still displays its package count.
- Extend isolated Entware regression checks to render the actual menu line with missing parent/state, empty and populated results, deleted results and failed reads. Verify silent fallback and no state-directory creation.

Only the KeenTool manager advances to 2.0.7. Dashboard 2.0.4, SMB Backup 2.0.1, Pingtool/Traffic 2.0.1 and Firewall 4.0.2 remain unchanged. Installer, credentials, configuration, cron schedules and databases are unchanged.

## Update

Run `/opt/bin/bash /opt/bin/keentool --update`. The verified coordinated installer preserves existing settings, credentials, schedules and databases. Only the manager has a new component version. Validation uses isolated fixtures; no live router reboot or live Entware upgrade is claimed.
