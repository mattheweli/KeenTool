# KeenTool coordinated package 2.0.9

## KeenTool manager 2.0.8 / coordinated package 2.0.9 — 2026-10-26

- Remove the redundant main-menu `s. Update Keentool (Self)` entry, its interactive single-manager replacement path and its self-only flag display. Use `u. Check / install updates (KeenTool and tools)` to review all components and shared file differences, then confirm the coordinated installation. Keep explicit repair (`r`), component submenus, existing headless notification/check commands and scheduled jobs compatible.
- Recover from a deleted current working directory using Bash builtins before manager startup, menu redraws/update handoff and updater/bootstrap child processes. Preserve a valid current directory. An already-started parent shell/interpreter may emit its initial warning before script code runs; `cd /` before invoking the command repairs that existing shell immediately.
- Shared web-isolation helper 1.0.1: do not invoke awk on a missing legacy `permissions.tsv` file. Keep the warning that original permission rollback is unavailable; do not invent old metadata, create a fake ledger or replace active web configuration.
- Add isolated regressions for deleted directories, update restart/decline/error handling, a unified menu, generated bootstrap parity and missing permission ledgers with rollback refused safely.

The manager advances to **2.0.8** because its behavior changes; the verified package advances to **2.0.9**. The updater/bootstrap advance to 1.0.4. All other component versions and configuration, credentials, schedules, databases and firewall rules are preserved. An update transcript ending in `stable installed` and `Verified GitHub release installed` represents a completed installation even when these historical environment/backup warnings were printed.

## Update

From an existing shell, first run `cd /`, then `/opt/bin/bash /opt/bin/keentool --update`. In the updated menu, use **u** to review and confirm updates. Existing settings, credentials, cron and databases remain preserved. Missing historical web-isolation permission records cannot be reconstructed by this patch; the warning remains accurate and permission rollback stays unavailable for that old backup. Automated validation uses isolated fixtures, not a live router.
