# Stable release validation — 2026-10-23

## Automated evidence

Package 2.0.11 adds checks for complete grouped/wrapped CLI output, machine-selection compatibility, interactive and legacy-background retention prompts, explicit policy forwarding, success/rollback cleanup, old archive/data preservation, failed-restore retention and constrained symlink-safe cleanup. The current workflow artifact records the results for the exact release commit; the counts below describe earlier baseline evidence.

The 2.0.5 checks additionally verify configured producer/browser freshness, exact thresholds, Off/legacy behavior, cross-tab refresh changes and interval propagation in public snapshots. Documentation screenshot rendering uses actual templates with synthetic fixtures; see docs/demo/.

The 2.0.4 checks cover every selected source target and shared dependency, unchanged-version drift, missing files, bad modes, unrelated component exclusion, actual Dashboard HTML versions, correct Firewall summary and overview/archive target consistency.

The 2.0.3 checks additionally cover independent per-tool/global scopes, metadata-only checks, no archive download before interactive consent, explicit file repair, overview URL/size/digest validation, approved overview/package consistency and mixed-component downgrade rejection.

The 2.0.2 checks additionally cover missing/broken PHP CLI, dependency consent and failed repair, one managed component invocation, no legacy firewall update side effects, independent component/script versions, exact installed-source/mode audit, private update receipts and exec restart, same-version repair and downgrade rejection.

Progressive history aggregation is additionally validated with real SQLite/PHP core, 23/25-hour days, exact IP/list/calendar totals, untouched recent samples and private backups, failure rollback and the shared writer lock. See FIREWALL_HISTORY.md for private-copy size measurements.

47/47 isolated checks passed. The machine-readable list is validation-results.json. Run sudo env PATH="$PATH" python3 tools/check-release.py on a Linux host with Node.js, PHP CLI/CGI and sqlite3; the fixture runtime is staged under /tmp/keentool-security-runtime. On Ubuntu 24.04, install php8.3-cli php8.3-cgi php8.3-sqlite3 sqlite3 and Node.js first. Installer/rollback fixtures require root, matching the production installer requirement. GitHub workflows preserve the isolated check results as an artifact. Tests create temporary fake router roots and mocked mail/service commands; they do not send SMTP or modify a router.

- All 14 JavaScript fixtures: administrator visibility/session flow, numeric formatting, health states, missing versus disabled monitors, expandable port lists, geography, settings types/presets/dirty-state preservation, density/navigation and unified refresh behavior.
- Production PHP/SQLite security integration: bans/expiry, management and whitelist protections, request validation, guarded policy apply/confirm/revert, list events/comparisons, snapshots, settings revisions and HTML/plain digest queue/retry.
- Real PHP CGI administrator API: HTTPS, cookies, CSRF, origin checks, guest reads and write rejection. Web-isolation permission/configuration migration and rollback fixtures.
- Firewall owned-chain staging/preflight/apply/recovery across both families with mocked kernel commands; restored list/timeout behavior, manager settings persistence, source validation/cache fallback/GeoIP thresholds and exact port lists.
- Ping history/configuration/notification semantics, incremental PPP cursor/rotation/partial-line handling, independent service lifecycle/slow mail, deterministic shutdown during an active scan, vnStat export retention and interface selection, SMB backup failure handling and Entware maintenance worker.
- Lossless SQLite optimization/integrity/backup fixture; full log continuation sizes/cursors and readable mail/MTR layouts with escaping/quoted-printable handling.
- New real file transactions in isolated roots: fresh installation/TLS generation/default jobs; public inline Ping settings including DB_DIR expansion; legacy PCAP migration; alpha external settings; byte-for-byte database/password/cron preservation; restored file modes; service-start failure recovery; symlink refusal; corrupted backup refusal. Native service lifecycle commands and lighttpd are mocked here.
- New BusyBox metadata fixture forces stat -c to fail and verifies PHP core size/inode/mtime/device identity fallback, including filenames with spaces.

- Remote updater fixture: stable-only API metadata and canonical asset URLs, SHA-256/GitHub digest checks, alpha/public version detection, check versus apply, no downgrade, explicit reinstall, HTTP 404/403 handling, safe streamed TAR/PAX extraction, rejection of traversal/links/internal checksum failures, atomic cache flags and staging cleanup. Transport and install command are mocked; the verifier/extractor are production code.

- Legacy migration fixture: run the historical 1.3.4 interactive updater function with a real mv/exec handoff and TTY consent; exercise the generated embedded bootstrap before any shared libraries, standalone alpha bootstrap, same-version manager seeding, readiness/restart, check-only/noninteractive behavior, cancellation forwarding, failed install/checksum/no-release behavior and private staging cleanup. GitHub transport and the transaction boundary are mocked; the existing installer fixture independently exercises real file transactions.

Runtime PHP, Bash and JavaScript syntax checks passed. Six pages/templates have no alpha banner and retain automatic-year copyright and their stable version. Package, repository overlays and release assets have verified SHA-256 manifests. Native lighttpd configuration is checked by the installer on the router; no live mail-client rendering is claimed.

## Physical-router acceptance

Automated validation does not claim a fresh physical-router installation, a live router reboot or an actual SMTP send. Review the following after updating the test router:

1. Run the upgrade plan/apply and record the printed backup. Confirm settings/password, existing jobs, database history and interface selection are intact. Check the plan before using web/logging adoption options.
2. Refresh/regenerate all six pages, verify guest read-only logs and administrator Settings/diagnostics. Confirm versions appear only in the footer and common refresh still works.
3. Check firewall_health, wan_syslog_service status and keentool_security_service status. Review web isolation status. Confirm HTTPS/admin access on the existing port without changing the router's own administration interface.
4. Reboot during an agreed maintenance window; verify restore of saved sets, actual rule references, PCAP/log reads and both package services, then check that the existing scheduler continues collecting data.
5. Send an explicitly requested test notification through the router, review the next periodic digest and confirm the known KP source failure is described accurately. Test package rollback in a suitable isolated router installation before recommending it broadly.

Known feed issues are documented in SECURITY.md and the draft notes. They are not hidden by changing source policy or deleting a configured country.

The 2.0.6 checks add root-parent and trailing-slash SMB archive fixtures, runtime/log exclusions, socket handling and coherent SQLite records with GNU/BusyBox tar. Remote SMB and router export are mocked.
