# KeenTool coordinated package 2.0.14

## KeenTool manager 2.0.11 / Firewall 4.0.3 / coordinated package 2.0.14 — 2026-10-28

- Offer guarded application of an updated enabled firewall hook during Legacy/regular upgrades. First review the apply choice; after IPv4/IPv6 verification, type the fresh SSH challenge to confirm continued reachability. A disabled firewall remains disabled. Headless installs cannot apply rules through this path; explicit `--apply-firewall` still requires an interactive terminal.
- Arm an independent HUP-safe guardian before applying rules, with a 120-second monotonic deadline. Failed apply/health, wrong confirmation, lost SSH or missing confirmation restores previous owned rules, rule metadata and the source installation. Preserve foreign router rules and existing IP-set contents. Temporary verified recovery copies remain available until confirmation; the normal retained-backup choice is respected afterwards.
- Hold unsolicited router reapplications of the new hook while the migration is pending. A reboot with an unconfirmed transaction restores previous source before invoking the old hook. Serialize restore/confirmation and retain recovery material with an explicit error if restoration cannot finish.
- When application is deferred, retain the previous boot hook itself, including when retained backups are declined. Print FIREWALL MIGRATION PENDING and the guarded retry command. This intentional old-hook difference remains visible to package file verification until completed. Plan/check never apply rules.
- Add `--apply-firewall` to updater/bootstrap and refuse older installers lacking the guard capability. Hook 3.0.1 and the new private transaction helper 1.0.0 implement the migration; installer 1.0.6, transaction engine 1.0.4, updater/bootstrap 1.0.7 and manager 2.0.11 integrate it. Firewall suite advances to 4.0.3; Stats, Monitor and other tools keep their versions.

Regression fixtures run the real hook/guardian and real file transactions against a mocked kernel: confirmation, rejection, independent restoration after parent SIGKILL, foreign-rule/bans preservation, pending-install exclusion and reboot recovery. Physical-router connectivity/reboot is not claimed by isolated tests. No database pruning, list download, password reset or cron changes are introduced.

## Upgrade

Use KeenTool → u. If an enabled firewall needs migration, approve guarded application, then type the challenge displayed after rules are verified. Confirm only while this SSH session remains usable. Without confirmation the independent guardian starts rollback at the 120-second deadline. If application is deferred, the previous hook and active rules are retained; finish later from SSH using `keentool --update --reinstall --apply-firewall` after upgrading the updater. No option in this path enables a previously disabled firewall. Settings, passwords, databases, lists and schedules are preserved.
