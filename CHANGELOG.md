# Stable changelog — 2026-10-28

## Coordinated package 2.0.17 / Firewall 4.0.6 — 2026-10-28

- Guarantee a fresh verified database backup for explicit balanced-profile maintenance on storage that is already compact. Reuse only a backup taken by the same invocation's conversion; never treat an older normalization/history baseline as a current recovery copy.
- Test first and repeated balanced maintenance after a separate structural conversion, requiring distinct private recovery files and unchanged current events in the latest backup.
- Correct the README's independent Stats version to 4.0.2. Compact storage, balanced history, lossless Ping/vnStat maintenance and their limitations remain as introduced in 2.0.16.

Database engine advances to 1.0.1, Firewall to 4.0.6 and package to 2.0.17. Stats remains 4.0.2; manager remains 2.0.11. Installation still does not convert databases or change settings.

## Coordinated package 2.0.16 / Firewall 4.0.5 — 2026-10-28

- Add explicit, backup-first compact IP history storage. Repeated IP/subnet text becomes an integer dictionary reference; row multiplicity, timestamps, counts and list classes are verified transactionally before replacing the table with a compatible read/write view. Recognized schemas/indexes only; custom objects are refused. Global counters, metadata, ordered full port histories and reporting state are preserved.
- Add an explicit balanced 2/7/365-day policy: recent original samples, then hourly, daily and older complete calendar-month IP/list buckets. Preserve exact IP/list/month totals and recent raw samples; disclose reduced old day/rolling-boundary and first/last precision. Existing settings are not changed by installing the release. Monthly aggregation is optional in Web Settings (0 disables new monthly rollups).
- Add keentool_db CLI status/maintenance for Firewall, Connection Monitor and vnStat. Ping/vnStat use lossless VACUUM with verified private backups; existing samples, peaks, retention and traffic counters are preserved. vnStat uses its configured database directory and only stops a previously running daemon through a unique init script, restoring its state on success/error and reporting restart failure. No SMB history DB exists; JSON/security/config state is untouched.
- Add expansion back to text storage retaining current collected events for a reviewed runtime downgrade. Package rollback never silently restores a historical database backup or reconstructs already reduced time precision.
- Preserve script header cleanup and donation sections from main. Script changes outside the statistics collector are comment-only; their runtime versions do not advance. Do not infer a future database size cap from compaction measurements. Port normalization is intentionally not applied without a measured storage benefit.
- Add real SQLite/PHP-core regression fixtures for exact conversion, duplicate rows, view writes, monthly totals, idempotence, expansion, backup privacy, custom-index refusal, unchanged Ping/traffic samples and vnStat lifecycle/error paths.

Package 2.0.16, Firewall 4.0.5 and Stats 4.0.2. Manager remains 2.0.11, Ping 2.0.2, Traffic 2.0.1, SMB 2.0.1 and Dashboard 2.0.4. Database conversion/aggregation is explicitly requested after installation; installing the package does not run database maintenance. Tests are isolated and do not prove physical-router speed or custom service behavior.

## Coordinated package 2.0.15 / Firewall 4.0.4 — 2026-10-28

- Fix a compatibility bug introduced by guarded migration in package 2.0.14: minimal BusyBox sleep rejects .1. The independent guardian startup now polls with whole seconds only. Guard regression fixtures force an integer-only sleep implementation rather than relying on GNU sleep or a feature-rich BusyBox build.
- Fix source rollback stopping every daemon marked previously running, including vnStat when an upgrade had not touched it. Stop only affected web/logging/traffic services, record stop intentions in new transactions and support old transaction metadata. Leave an untouched running vnStat daemon alone; retry previously running services that an earlier rollback left stopped.
- Continue verified file restoration and other restart attempts after a service command fails. Report incomplete service recovery and retain the recovery material/marker instead of aborting before restoring source files. Kernel/source/service recovery is not reported successful while a required service action still fails.
- Publish a standalone recover-firewall-upgrade.sh asset and SHA-256 sidecar for an interrupted 2.0.14 transaction. It verifies the matching pending transaction and old recovery-copy hashes, refuses a live installer/maintenance owner, atomically replaces only the private recovery rollback entry with the current implementation, and invokes the original pinned guardian's recover action. It preserves the original rollback entry, all recovery copies, databases, credentials and saved lists. A completed transaction without a pending marker is left untouched.
- Reproduce the reported old rollback/vnStat failure in isolated fixtures, then recover with the release recovery entry. Exercise the exact previous guard/rollback sources, verify old files/rule metadata, confirm web/logging restart attempts, and assert no stop/start of an untouched running vnStat. Recovery entry generation is checked against the current rollback source.

Installer advances to 1.0.7, rollback and firewall guardian to 1.0.1, Firewall component to 4.0.4 and package to 2.0.15. Manager 2.0.11, updater/bootstrap 1.0.7, hook 3.0.1 and the other tool versions do not change. The historical missing web-permission ledger warning is independent and its original permissions are not guessed. Tests use an isolated filesystem and mocked service/kernel commands; no physical router recovery is claimed.

## KeenTool manager 2.0.11 / Firewall 4.0.3 / coordinated package 2.0.14 — 2026-10-28

- Offer guarded application of an updated enabled firewall hook during Legacy/regular upgrades. First review the apply choice; after IPv4/IPv6 verification, type the fresh SSH challenge to confirm continued reachability. A disabled firewall remains disabled. Headless installs cannot apply rules through this path; explicit `--apply-firewall` still requires an interactive terminal.
- Arm an independent HUP-safe guardian before applying rules, with a 120-second monotonic deadline. Failed apply/health, wrong confirmation, lost SSH or missing confirmation restores previous owned rules, rule metadata and the source installation. Preserve foreign router rules and existing IP-set contents. Temporary verified recovery copies remain available until confirmation; the normal retained-backup choice is respected afterwards.
- Hold unsolicited router reapplications of the new hook while the migration is pending. A reboot with an unconfirmed transaction restores previous source before invoking the old hook. Serialize restore/confirmation and retain recovery material with an explicit error if restoration cannot finish.
- When application is deferred, retain the previous boot hook itself, including when retained backups are declined. Print FIREWALL MIGRATION PENDING and the guarded retry command. This intentional old-hook difference remains visible to package file verification until completed. Plan/check never apply rules.
- Add `--apply-firewall` to updater/bootstrap and refuse older installers lacking the guard capability. Hook 3.0.1 and the new private transaction helper 1.0.0 implement the migration; installer 1.0.6, transaction engine 1.0.4, updater/bootstrap 1.0.7 and manager 2.0.11 integrate it. Firewall suite advances to 4.0.3; Stats, Monitor and other tools keep their versions.

Regression fixtures run the real hook/guardian and real file transactions against a mocked kernel: confirmation, rejection, independent restoration after parent SIGKILL, foreign-rule/bans preservation, pending-install exclusion and reboot recovery. Physical-router connectivity/reboot is not claimed by isolated tests. No database pruning, list download, password reset or cron changes are introduced.

## KeenTool manager 2.0.10 / coordinated package 2.0.13 — 2026-10-28

- Detect a simple existing HTTP-only lighttpd listener during installation, including Legacy upgrades, and offer an explicit HTTPS conversion before administrator password setup. Keep the existing port (including 81), document root, FastCGI/PHP settings and included fragments. An existing enabled TLS configuration is preserved.
- Add `--enable-https` to installer/updater/bootstrap. Interactive installs ask for consent; noninteractive installs preserve HTTP unless this option is explicit and print a completion command. Check/plan operations never modify the listener. Existing isolated, conditional/multiple-socket, alternative-root and custom TLS configurations require review rather than a guessed conversion.
- Reuse verified installation recovery copies for the web conversion. Stage a private certificate and test a candidate configuration before replacing live files. Validate the installed configuration, restart the existing lighttpd service and require a real local HTTPS handshake/HTTP response. Failed validation, startup or probing restores the previous package/listener through the normal transaction rollback; retained-backup choices are unchanged.
- Reuse an existing certificate; create a private self-signed certificate only if absent. Report the existing HTTPS port and explain certificate verification/trust. Curl's insecure flag is limited to the local readiness probe; it does not establish certificate trust. Passwords, database contents, cron and firewall policy are unchanged.
- Add native lighttpd/OpenSSL local TLS validation in CI, plus transaction fixtures for port preservation, unchanged PHP/configuration/credentials, current TLS, consent from legacy background terminals, preflight errors, failed handshake rollback and custom configuration refusal. Router reboot and every custom server layout remain outside isolated validation.

Manager 2.0.10 changes because its embedded update/bootstrap supports the new explicit option. Installer 1.0.5, updater/bootstrap 1.0.6 and transaction engine 1.0.3 carry the implementation. All other component versions remain unchanged.

## Coordinated package 2.0.12 — 2026-10-28

- After a successful installation/migration, start dedicated web administrator password setup when no credential file exists. This covers first Legacy upgrades and fresh installs without requiring users to discover the password menu afterwards. Password input is hidden, repeated for confirmation and retried after length/confirmation errors. No router username/account password is changed.
- Read the controlling terminal when a legacy updater launches its installer with stdin redirected to /dev/null. Preserve an already configured password and revision byte-for-byte; report an invalid existing credential file for explicit review rather than silently replacing it.
- Noninteractive installation remains possible without a generated or default password: print the pending setup command and leave administrator login unavailable until configured. The password step runs after successful source installation; failure/EOF does not undo the installed package, and interrupted setup can be completed with KeenTool option A.
- Serialize CLI credential writes with a private lock and add a missing-only setter mode so concurrent/manual setup is never overwritten by migration. Passwords travel to the PHP bcrypt setter on stdin, never command arguments or log files. Explicit password reset remains available.

Installer 1.0.4 and the password CLI/setter 1.0.1 carry these changes. Manager 2.0.9, Dashboard 2.0.4, bootstrap/updater 1.0.5 and every other tool keep their versions. Existing credentials, database contents, schedules and firewall policy are preserved. Automated tests use isolated roots and synthetic passwords, not a live router.

## KeenTool manager 2.0.9 / coordinated package 2.0.11 — 2026-10-27

- Organize CLI update output into package/component versions, grouped missing/changed/permission/unsafe-path file reports, component changes and wrapped release notes. Installation plans group only new/changed/permission targets, summarize matching targets and make clear the complete coordinated transaction still covers all files. Suppress the repeated plan in the apply child after the remote updater has already displayed and revalidated it.
- Add an interactive recovery-backup retention choice to installation and verified updates. Keeping a backup retains the existing manual-rollback archive; declining removes temporary recovery copies only after a successful installation. Verified temporary copies remain mandatory during the transaction so partial failures can roll back safely. Existing permanent backups are never automatically removed.
- Add `--keep-backup` and `--no-backup` to installer/updater CLI. These control retention after success, not in-flight rollback protection. Unattended runs and `--yes` without a backup flag preserve the conservative keep behavior. Old installers reject discard requests rather than silently ignoring them. First upgrades launched by older background updaters can obtain the choice through the controlling terminal.
- Store non-retained transaction copies in a private durable transaction directory. Successful installation or successful automatic rollback removes them; failed recovery or an uncatchable interruption leaves recovery material available for review. Automatic cleanup validates the transaction root/name/retention flag and never follows symlinks into unrelated content.

Manager 2.0.9, installer 1.0.3, remote updater/bootstrap 1.0.5, verifier 1.0.4 and transaction engine 1.0.2 carry these changes. Firewall, Pingtool, Traffic Manager, SMB Backup, Dashboard, credentials, databases, schedules and firewall policy are unchanged. The choice concerns installation recovery copies, not SMB archives or database-maintenance backups.


## Coordinated package 2.0.10 — 2026-10-27

- Install the existing `support/render_cache.sh` library as `/opt/lib/keentool/render_cache.sh` with mode 0644. It was present in the source archive but omitted from INSTALL.tsv, so a clean installation could fail firewall statistics generation with a missing-library/undefined-function error.
- Include that target in FILE_SCOPES.json as a firewall-owned dependency. The verified release overview now tracks its hash and permissions, so global and firewall-scoped checks detect a missing or modified library even when component versions are current. A coordinated update or explicit repair reinstalls it.
- Extend isolated installation regressions: fresh installation loads the installed library through the actual firewall cache-generation block, generates the real SQLite cache files and preserves the input database. Check missing-library detection, same-version repair, migration/upgrade installation and rollback removal of the newly introduced target.

This is a packaging correction. Manager **2.0.8**, Firewall suite **4.0.2**, Stats **4.0.1**, Pingtool **2.0.2**, Traffic/SMB **2.0.1**, Dashboard **2.0.4** and installer **1.0.2** keep their versions and runtime source bytes. Settings, credentials, cron schedules, database contents and firewall rules are unchanged. The separate cron-daemon health question is not inferred from the presence of scheduled jobs.


## KeenTool manager 2.0.8 / coordinated package 2.0.9 — 2026-10-26

- Remove the redundant main-menu `s. Update Keentool (Self)` entry, its interactive single-manager replacement path and its self-only flag display. Use `u. Check / install updates (KeenTool and tools)` to review all components and shared file differences, then confirm the coordinated installation. Keep explicit repair (`r`), component submenus, existing headless notification/check commands and scheduled jobs compatible.
- Recover from a deleted current working directory using Bash builtins before manager startup, menu redraws/update handoff and updater/bootstrap child processes. Preserve a valid current directory. An already-started parent shell/interpreter may emit its initial warning before script code runs; `cd /` before invoking the command repairs that existing shell immediately.
- Shared web-isolation helper 1.0.1: do not invoke awk on a missing legacy `permissions.tsv` file. Keep the warning that original permission rollback is unavailable; do not invent old metadata, create a fake ledger or replace active web configuration.
- Add isolated regressions for deleted directories, update restart/decline/error handling, a unified menu, generated bootstrap parity and missing permission ledgers with rollback refused safely.

The manager advances to **2.0.8** because its behavior changes; the verified package advances to **2.0.9**. The updater/bootstrap advance to 1.0.4. All other component versions and configuration, credentials, schedules, databases and firewall rules are preserved. An update transcript ending in `stable installed` and `Verified GitHub release installed` represents a completed installation even when these historical environment/backup warnings were printed.


## Pingtool 2.0.2 / coordinated package 2.0.8 — 2026-10-26

- Include the configured latency threshold in IPv6 ping-warning email bodies, matching IPv4. The shared renderer can now color a healthy latency green when packet loss is the reason for the warning. Threshold comparison and alert triggers are unchanged.
- Update shared Mail Layout to 1.0.1: accept standard MTR report loss fields with or without a percent marker. Normalize the displayed suffix and keep unanswered hops such as `3.|-- ??? 100.0 ...` in their original table position. Retain escaped fallback output for genuinely unsupported diagnostics and MPLS details.
- Extend regressions for actual IPv4/IPv6 alert bodies, below/exact/above-threshold colors, answered/unanswered hops, both loss formats, ordered table rows and diagnostic fallback escaping.

The manager remains **KeenTool 2.0.7**. The complete package advances to **2.0.8** solely to distribute Pingtool 2.0.2 and shared Mail Layout 1.0.1 through verified upgrades. Firewall, Traffic Manager, SMB Backup and Main Dashboard versions are unchanged. No probe algorithm, notification trigger/cooldown, cron, configuration, credentials or database policy changes.


## KeenTool 2.0.7 — 2026-10-24

Relative to v2.0.6 (main `f01280b85b2ee70a65e514bf0181c7715c5c8211`).

- Fix the Main Menu Entware update counter when `/opt/etc/keentool/entware/available.txt` has not been created by a successful check. Redirect stderr before opening stdin and display a count only on a successful read, so a missing directory/file displays `[unchecked]` without a shell error between the H and p menu entries.
- Preserve the difference between unchecked and zero available updates. Rendering the menu neither creates a fake empty result nor performs an Entware check/upgrade; a successful existing check still displays its package count.
- Extend isolated Entware regression checks to render the actual menu line with missing parent/state, empty and populated results, deleted results and failed reads. Verify silent fallback and no state-directory creation.

Only the KeenTool manager advances to 2.0.7. Dashboard 2.0.4, SMB Backup 2.0.1, Pingtool/Traffic 2.0.1 and Firewall 4.0.2 remain unchanged. Installer, credentials, configuration, cron schedules and databases are unchanged.


## SMB Backup Tool 2.0.1 / KeenTool 2.0.6

- Correct tar exclusion paths when the backup source has `/` as its parent (including the default `/opt`). Previously an extra slash left exclusions absolute, while archive member names were relative; live logs/PCAP could enter the archive and fail backup creation.
- Normalize trailing slashes in source settings. Exclude `/opt/var/run` and `/opt/var/lock` alongside logs, temporary files and local backup staging. Exclude Unix sockets elsewhere in the source using a checked NUL-delimited inventory.
- Inspect the full 16-byte SQLite header after Base64 encoding; binary/non-SQLite `.db` files no longer inject NUL bytes into Bash command substitution. Retain coherent SQLite snapshots and verify their integrity.
- Keep strict archive error handling, remote read-back/checksum verification and retention only after successful verification. Do not stop services or ignore arbitrary tar failures. Configuration and scheduling are preserved.
- Add isolated archive regression coverage for root-parent/trailing-slash sources, volatile paths, real Unix sockets on CI, non-SQLite binary files and SQLite record preservation. Exercise GNU and BusyBox tar where available; NAS transport and router export are mocked.


## KeenTool 2.0.5

Relative to v2.0.4 (main `1e799ec2abade673cd7a728872db0035b7c5fff6`).

- Replace the fixed three-minute Security & Health age warning with the slower configured monitor-production/browser-refresh cadence. Publish monitor_interval in the security snapshot and apply one shared freshness calculation to the top status banner, Checked timestamp and Main Dashboard security summary. Mark yellow only when age is strictly greater than the effective interval; handle Off, missing legacy intervals, exact boundaries and future timestamps without inventing a delay.
- Refresh all page/template shared JavaScript references to prevent browser caches from keeping the old freshness logic. Main Dashboard advances to 2.0.4; shared UI to 1.0.1 and security UI/engine to 1.0.2. Firewall component 4.0.2 (Dashboard 2.0.2), Pingtool 2.0.1 and Traffic Manager 2.0.1 carry updated references; their collection/filtering algorithms are unchanged.
- Rewrite the five GitHub component READMEs with current features, independent versions, complete-suite installation/update instructions, real command/configuration paths, data/precision/security limitations and troubleshooting. Preserve license attribution and optional original project support links.
- Add reproducible screenshots from actual current application templates and the real SMB CLI menu, using synthetic fixtures, example addresses and an explicit documentation watermark. No user logs, credentials, database or NAS contents are used. Include generation source, pinned documentation browser dependencies and a render error report.
- Extend freshness/refresh tests for five-minute polling, long producer intervals, exact threshold, Off/legacy state, cross-tab changes and snapshot interval propagation.

Installer, firewall rule application, history aggregation and preservation/rollback behavior are unchanged. SMB runtime remains 2.0.0; its README is documentation-only.

## keenetic-firewall 4.0.2

Refresh shared UI/security asset references for configured snapshot freshness. No hook, filtering, statistics collection or database policy change. Monitor remains 4.0.0, Stats 4.0.1; firewall HTML advances to 2.0.2. Update the explanatory README with a synthetic interface screenshot.

## keenetic-pingtool 2.0.1

Refresh the generated page shared UI reference for the coordinated security freshness correction. Probe, notification and history algorithms are unchanged. Rewrite the explanatory README with a synthetic Connection Monitor screenshot.

## Traffic_manager 2.0.1

Refresh the generated page shared UI reference for the coordinated security freshness correction. vnStat collection, export retention and history algorithms are unchanged. Rewrite the explanatory README with a synthetic Traffic Monitor screenshot.

# Stable changelog — 2026-10-23

## KeenTool 2.0.4

Relative to published v2.0.3 (main `9350079e75db877333c0b927562734537e4aecc0`).

- Make Install / Update verify every installed file owned by the selected component, plus shared dependencies, against the published target SHA-256 and expected permissions. A current installed-release.json no longer hides an old Monitor, missing API/helper or modified script. Report every differing path, reason and readable source version before installation consent. Unrelated component source differences do not trigger the selected component.
- Add explicit FILE_SCOPES.json ownership for all 54 installation targets. The lightweight GitHub-digest-verified overview carries source/path/owner/hash/mode/version data; normal checks still do not download the archive. After consent, require the archive's INSTALL.tsv, scopes and source hashes to match the approved overview before applying the coordinated transaction.
- Keep the Main Dashboard in the KeenTool repository while tracking Dashboard 2.0.3 separately from manager 2.0.4. Check the actual installed HTML version and content, including when an old record does not contain a Dashboard entry or incorrectly claims a newer version. The dashboard menu selects Dashboard instead of KeenTool; the global overview includes all six components.
- Display the recorded Firewall suite version in the main tool summary. Keep Monitor and Stats script versions in the firewall submenu; independent script versions are not used as the suite version.
- Retain explicit full-package repair, coordinated file installation, dependency preflight, successful-update menu restart, backup/rollback and preservation of credentials, configuration, databases and schedules. Older version-only overviews explicitly state that files were not verified.
- Add transport/menu regression cases for same-version Monitor 3.0.0 versus expected 4.0.0, scoped file coverage, unrelated component drift, shared dependencies, missing files and bad modes, actual Dashboard HTML versus the record, and mismatched target metadata.

Firewall remains 4.0.1 (Monitor 4.0.0, Stats 4.0.1). Pingtool/Traffic/SMB remain 2.0.0. Installer remains 1.0.2; updater/verifier/bootstrap advance to 1.0.3. No firewall policy, cron or database history change is included. See [Update behavior](docs/UPDATE_RECOVERY.md) and the [2.0.3 changelog](docs/history/STABLE_2.0.3.md).


# Stable changelog — 2026-10-23

## KeenTool 2.0.3

Relative to published v2.0.2 (main `b65b265032a35469db2cdc0c2fdaaceb60a79264`).

- Check a selected tool against its own installed and published component versions. An available KeenTool update does not trigger an update when the selected Firewall, Pingtool, Traffic Manager or SMB component is current.
- Add a main-menu **Check all updates (KeenTool and tools)** overview for the five components, showing installed version, available version and status. Self-update explicitly selects KeenTool.
- Fetch only the GitHub release record and a small component overview during version checks. Bind the overview URL, stable version, size and SHA-256 to the published GitHub release. Before confirmation, disclose every changed component, shared runtime coordination and release changes. Download the full archive only after interactive consent or explicit --yes.
- Preserve coordinated installation, HTTPS-only transport, archive and internal file checksum verification, backup/rollback, dependency preflight and successful-install menu restart. Verify that the downloaded package component versions match the approved overview. Refuse downgrades, including newer component versions within a mixed installation.
- Separate source verification and repair into **Verify / repair installed package files** and explicit --repair. This operation asks before downloading the archive, compares actual files and modes, then asks before applying a repair. --repair --check verifies without installation. Ordinary version checks no longer audit or silently repair files.
- Keep compatibility with older releases without an overview for complete-suite checks and explicit repair; do not invent per-tool versions from the suite number. Publish versioned component overview assets and checksum sidecars with this and future complete releases.
- Extend isolated transport/menu tests for per-tool and global scopes, unchanged components, no archive download before consent, interactive decline, explicit repair, overview tampering and package/overview mismatch.

Installer 1.0.2, Firewall 4.0.1, Pingtool/Traffic/SMB 2.0.0 and database/history behavior are unchanged. Updater/verifier/bootstrap advance to 1.0.2. See [Update recovery](docs/UPDATE_RECOVERY.md) and the [2.0.2 changelog](docs/history/STABLE_2.0.2.md).


# KeenTool changelog

## 2.0.2 — 2026-10-23

Relative to published v2.0.1 (main `64dac8c0c0510822376c098211b470f9aaadf6b4`).

- Share capability-based dependency preflight between the generated standalone/embedded bootstrap and installer. Detect missing or broken PHP CLI, bootstrap commands, full suite executables, PHP functions/session support, CGI startup, SQLite JSON and Entware web/capture modules. Report all missing requirements together; ask before opkg installation and verify again afterward. Check-only and noninteractive paths remain read-only unless dependency installation is explicitly requested. Do not perform a broad package upgrade or rewrite configuration.
- Replace legacy per-file managed menu flows with one coordinated update. Firewall update now returns before legacy dependency/kernel probes, repeated suite updater calls, FastCGI rewrites, daemon restarts and cron edits. Ping/Traffic/Dashboard/SMB update actions similarly avoid obsolete post-install mutations.
- Restart the menu with exec only when an update/repair successfully produces a private installation receipt. Preserve the menu on failure, decline or no-op. Print the actual installed package version from RELEASE.json instead of the fixed 2.0.0 message. An already-loaded older menu needs one reopen during its first upgrade; automatic restart applies to the new menu code.
- Add component-specific version reporting and a verified installed-source audit. Distinguish KeenTool suite 2.0.2, firewall component 4.0.1, Monitor 4.0.0 and Stats 4.0.1. Detect missing/stale source files and unexpected modes even at the same declared suite version, and offer a complete transaction-backed repair without downgrading newer local installations.
- Add dependency/bootstrap and managed-menu integration checks. Extend remote-updater tests for receipts, component audit, same-version repair, check-only behavior and downgrade refusal; extend installer fixtures for the complete runtime capability check.

Firewall 4.0.1 and the unchanged Ping/Traffic/SMB versions are retained. No hook/rule or database-history policy changes are included. See [UPDATE_RECOVERY.md](docs/UPDATE_RECOVERY.md), the [2.0.1 history changelog](docs/history/STABLE_2.0.1.md), and [FIREWALL_HISTORY.md](docs/FIREWALL_HISTORY.md).


## 2.0.1 — 2026-10-23

Relative to published v2.0.0 (`2758f0d7ee8fb9e703ee7c35ea866002e4edb036` on main).

- Add progressive firewall history settings in the CLI Firewall menu and authenticated web Settings, with enabled/raw/hourly thresholds, ranges/presets, revision checks, private configuration backup and cross-field validation. History settings do not reapply the firewall hook.
- Add the coordinated history engine/CLI, default 7-day raw and 30-day hourly detail, installation targets and missing-default configuration migration. Preserve existing history settings, scheduler, credentials and databases during package updates.
- Expose historical bucket precision in dashboard/Security diagnostics and comparisons. Preserve all-time IP/list totals, local calendar-day totals, global counters, full port history and reporting state.
- Patch component versions: manager/dashboard 2.0.1, firewall statistics 4.0.1, firewall page 2.0.1, changed settings/security/installation/uninstall helpers 1.0.1; new history helpers 1.0.0. Unchanged components retain their published versions.


- Existing public Update KeenTool now hands off to a self-contained migration entry before shared libraries load. The entry verifies the full stable suite, preserves interactive consent, handles cancellation/retry and opens the new menu only after successful installation. Pinned alpha installations use the same standalone bootstrap once.

- WAN monitor shutdown waits for in-flight scans and notification work even when a trapped signal interrupts Bash wait.

Baseline: `8d640c8b06968b0f24ce41feb1bc5b0a89c3f541`.

- Remote whole-suite updater and standalone legacy/alpha bootstrap: stable-only release lookup, confirmation, no downgrade, SHA-256/GitHub digest validation, bounded safe TAR/PAX extraction and complete file-manifest verification before the same migration installer. Menu/CLI checks and offline updates remain available.
- New coordinated 2.0.0 suite installation: fresh/upstream/alpha detection, verified file/configuration backups, atomic replacement, automatic/manual rollback and whole-package update entry point.
- Uniform Keenetic-inspired responsive navigation, shared refresh with Off/manual controls, remembered navigation/density, readable tables and a full-width Security & Health overview. Remove development banners and show versions in copyright footers.
- Dot thousands/comma decimals across rendered dashboard values; preserve raw technical data and arithmetic. Full expanded log views, bounded internal transport, log sizes and allowlisted read-only system logs without changing syslog rotation.
- Password-only HTTPS administrator access shared with Settings/Security, typed settings with ranges/presets, revision conflict handling and guarded firewall changes.
- Entware update monitoring/notifications and an explicitly requested maintenance worker that stops/restarts Entware services. Shared HTML/plain notification layout with safe tables, MTR rendering and semantic health colors.
- Independent incremental PPP syslog monitor, root broker, ktweb web-isolation tools, boot scheduler check and private helper paths. BusyBox metadata fallback removes the GNU stat requirement.
