22 Bash scripts: syntax checked. Pingtool: 70000 synthetic SQLite samples, temporal bounds, retained count, adaptive chart bound, NULL, selected averages and browser preference. Firewall: saved-set mappings, existing capacity mismatch, unchanged timeouts, counters, restore retry/checkpoint failure, public read-only log and guest/admin control checks. PHP runtime lint not available locally; do not infer a router runtime pass. No GitHub write or router deployment performed.
Installer: isolated plan/install/config-preservation/rollback PASS. PHP executable was simulated in the isolated fixture; real CLI and CGI lint are required on the router before any file mutation.
Pingtool 2.0.0a3: single history control positioned before refresh timer in header; English labels; existing period/data/browser tests PASS. 24 Bash syntax checks and isolated installer/rollback checks PASS.
Firewall dashboard 2.0.0a9: structural checks cover all 28 CNT/HITS tables, no fixed 60px numeric headers, nowrap/normal word breaking and intrinsic sizing; existing admin/log regression checks PASS. Visual browser verification remains pending.
Admin quick-link guest/login/new-row/logout tests PASS. Dedicated LED enabled/linked/error cases PASS. Dot grouping including integers beyond Number precision PASS. Bash and firewall inline JS syntax PASS.

Ping notification revision: Bash syntax, ping-notifications-check.py (route/manual labels, latency-only incident lasting 1777 seconds, recovery, invalid/backward clock), ping-settings-check.py (WAN name replacement, automatic reset, invalid name rejection) and ping-history-check.py passed. Notification transport was mocked/disabled; no emails sent and no router runtime test performed.

WAN PPP revision: wan-syslog-check.py passed (23-second event sequence from the uploaded log, baseline silence, repeated-down dedup, IPv6 link-local ignored, unchanged cursor, rename rotation unread tail, SMTP failure/retry, clock uncertainty, incomplete lines, configured PPP interface filter). The complete uploaded syslog was parsed as a silent baseline without sending mail. Bash syntax checks passed across the suite. Existing ping history/settings/notification checks passed. SMTP was mocked; live router and BusyBox execution still require user verification.

## Reliability revision (2026-10-14)
- Bash syntax passed across all 29 executable shell sources.
- firewall-transaction-check.py: complete hook with simulated iptables/ipset kernel, foreign chains retained, AutoBan OFF emits no SET, full health detects missing IPv6 rule, both-family preflight, second-family apply failure rollback with/without previous chains, late metadata failure recovery, IPv6 teardown, global disable preserves sets; partial saved-set restore fails without marker then succeeds on retry.
- wan-syslog-check.py and wan-service-check.py: original 23-second pattern, baseline silence, dedup, IPv6 link-local excluded, rename rotation, clock uncertainty, SMTP retry, partial lines, interface filtering, daemon start/stop/idempotence/config-disabled and recovery recorded while transport sleeps. Process ownership uses the executor's virtual PID test mode; real /proc cmdline validation is retained on the router.
- ping-history/settings/notifications: 70k synthetic SQLite history, range boundaries/raw averages/NULL, point cap and WAN label/interval persistence, observed instability messages.
- traffic-export-check.py: executes real generator with mocked vnStat/JSON CLI, multi-interface/dotted names and invalid/nonzero export preservation.
- entware-worker-check.py: executes real manager with mocked opkg, email and init services; dedup, retained list on failed indexes, download before reverse stop, ascending restart, upgrade failure propagates and services restart. No real package upgrades or emails.
- vpn-cursor-check.py: actual scanner with mocked ipset; history skipped, partial records retried, threshold respected and failures not recounted.
- smb-backup-check.py: actual backup functions/tar/sha256 with mocked router export/SMB; remote bytes checked before rename/purge, corrupt readback skips retention.
- installer-check.py: isolated plan/install/rollback, new helper/init additions, start only WAN service, preserve external config, remove additions on rollback. PHP lint/service actions are mocked in this isolated installer test.
- Four existing JS checks passed: admin controls, firewall LED/count formatting, layout controls and log controls.

Limitations: no real Keenetic kernel, BusyBox executable, PHP CLI/CGI runtime, SMB server, SMTP server or opkg repository was used. Local package installation could not obtain those runtimes in this executor. The router installer runs actual PHP CLI/CGI lint; the separate hook invocation runs actual kernel --test before any filter-chain commit. No GitHub publishing or direct router change was performed.

Firewall Health a2: the kernel hook and WAN daemon were confirmed running by the user's router output; the standalone health reader failed because /dev/stdin is absent. Corrected to awk's standard `-` input. Transaction/health regression now rejects /dev/stdin in its awk shim, reproducing that router restriction. Actual corrected router health result remains to be confirmed by the user.

Pingtool a12: extended history frontend test confirms separate family coverage with different IPv6 dates, explicit empty IPv6 state and no IPv6 line when disabled; existing SQL/history checks and Bash syntax passed.

Port details revision: fetched scripts/firewall_stats.sh and www/index.html from mattheweli/keenetic-firewall default branch (read-only). Upstream +N is a hover tooltip; attacker-per-port list opens a static-file modal. port-details-check.py executes the actual table renderer with a 110-port history and verifies the full file, +107 button, bounded tooltip and no admin-only flag. port-details.js checks public click/load/copy/download/close, IPv6-safe filename, existing attacker modal, path validation and errors. Existing admin-controls.js passed; Bash syntax passed. No live browser/router visual test was performed.

Stats a7: router reported undefined function on AWK line 14, the unspaced tip(...) concatenation. Replaced with sprintf. Port-render regression applies strict function-call recognition, verifies 110 entries and a simulated AWK failure propagates/removes the invalid cache. Exact sed repair tested against a script copy. No BusyBox runtime was available locally.

## Package r19 typography
- Scoped home card headings override the shared compact heading selector: 18px.
- Firewall badge selector overrides shared button font inheritance: spans and +N buttons both use 10px / 1.5 and weight 500.
- Existing port-details JavaScript and strict renderer checks pass; installer Bash syntax passes.
- No browser visual verification performed in this environment.

## Geographic overview r20 (2026-10-15)
- geography-check.py executes the real shell exporter with Python SQLite as a CLI shim: all 150 sources included despite top-10 display limits; consistent period boundaries, IPv6/subnet metadata join, unknown counts, bounded 100-row details, 12-port previews, target_port fallback and export-error propagation. No database writes by the exporter.
- geography.js exercises the actual inline map code using a DOM/vector-map stub: numeric counts and dot grouping, country validity/unknown exclusions, percentages including unknown hits, gradient/tooltip, public source details, selected period, no-data and pending exports.
- Existing port renderer/modal, admin-controls and firewall-indicator checks pass. All 29 Bash executable sources and firewall inline JavaScript syntax checks pass. Isolated installer plan/apply/rollback passes with mocked prerequisites/services.
- No real-browser visual verification or router performance measurement is available in this environment; geographic vector rendering and fullscreen still require confirmation on the installed dashboard.

## Layout and copyright r21
- Geographic columns now stretch to the same outer height; matching 42px minimum header heights align the subnet table and map panel. Browser screenshot confirmation remains required.
- Footer current-year function verified across a simulated 2026 to 2027 rollover without reload. All four page templates have one copyright footer; firewall uptime retained.
- Geography, layout/menu, admin controls, ping history, traffic exports and isolated installer plan/apply/rollback pass. Bash syntax passes across 29 executable sources; shared and static dashboard JavaScript syntax passes.

## Traffic History alignment r22
- CSS numeric selector specificity now exceeds the shared header default; the same selector covers header and body cells. Hour/date/month/year first columns retain left alignment. History cells do not wrap and the existing table container retains horizontal scrolling.
- Existing firewall indicator/count formatting, geography and admin-control checks pass. Firewall inline JavaScript and installer Bash syntax pass. No browser visual check performed.

## Shared readability r23
- density-controls.js: Comfortable default; switch to Compact; persistence across monitor pages; invalid stored values fall back safely; unavailable storage does not prevent density changes; no control on pages without tables.
- Existing layout/menu, geography, admin, LED/count and full port modal checks pass. Ping history, traffic generator and isolated installer/rollback checks pass. All 29 Bash executable sources, shared JS and static dashboard inline JS syntax pass.
- CSS retains explicit numeric header/data alignment, shared port-badge font sizes, log terminal colors, traffic Rx/Tx and risk text colors. Comfortable and Compact differ in spacing; source fixed row height is released only in Compact.
- Table headings stick within bounded scroll containers; geographic source panels preserve matched heights. Visual scrolling, dark-mode contrast and responsive wrapping have not been verified in a real browser in this environment.

## Security and observability r24 (2026-10-15)
- Actual PHP 8.3 CLI and CGI and SQLite 3.45 used for new backend checks; core-only PHP mode caught/removes an unnecessary ctype extension dependency. All PHP sources lint successfully.
- security-engine-check.py: real engine with mocked ipset/iptables/router helpers; IP/CIDR validation, active client/bridge/whitelist overlap protection, duration types, temporary/permanent persistence, expiry/unban, diagnostic metadata/counters/rules, guarded confirm/revert/conflicting edits, independent detached guardian after request exit, GeoIP warnings/baselines, rolling SQL comparisons, settings validation, public/private audit, bounded last-lines capture and verified-backup attestation.
- security-api-check.py: actual PHP-CGI sessions/password verification/cookie rotation, HTTPS/Origin/guest authorization/CSRF and private audit access. Unix transport is stubbed: this execution environment rejects AF_UNIX socket creation. No real root command broker or actual router permission migration was run here.
- web-isolation-check.py: config plan is read-only; failed lighttpd validation restores original files; successful migration preserves config modes; explicit rollback restores credentials/config permissions. Account identity, lighttpd processes/init restart are mocked.
- blocklist-variation-check.py: large valid GeoIP reductions accepted, main-list >75% shrink and empty GeoIP rejected with previous set retained. firewall-config-check.py: atomic manager save preserves NFLOG/list-safety/future fields and prior config on temp failure.
- firewall-counter-check.py: DROP counters retained despite lower NFLOG counts; shared legacy manual chain counted once; scan/connlimit/bruteforce counters summed. security-ui.js: safe text rendering, comparisons, read-only IP details, guest unban hidden and guarded confirmation.
- installer-check.py: 40 targets; WAN/security startup, rollback/removal of additions, unchanged external config. uninstall-security-check.py: plan has no service actions; web isolation reversed before service/kernel teardown; new helper/managed-set removal and keep-data behavior.
- Existing WAN/ping/traffic/SMB/Entware/VPN, hook transaction/preflight/rollback, modal/admin/LED, density/layout and geography checks pass. BusyBox 1.36 awk/sed/grep/stat/date/sort variants additionally pass geography, blocklist variation, configuration preservation and port renderer checks (router uses 1.37).
- A real router check is still required for the new netfilter match flags, Unix socket, process identities and CGI/session/TLS/socket/log permissions across restart/reboot. No browser visual verification or SMTP delivery performed in this environment. No database history was rewritten and no GitHub changes were made.

- Final r24 suite: 28/28 test programs pass. Syntax checks pass for 35 Bash sources, 4 PHP sources and 10 JavaScript files. Real PHP auth checks also cover boot identity mismatch and backward clock invalidation.

## IP diagnostics and standalone Security page r25 (2026-10-15)
- All 29 test programs pass across this revision. The initial counter test lacked the external SQLite test runtime; after restoring that runtime the test passes.
- security-engine-check.py runs real PHP 8.3 with filter_var explicitly disabled. The reported 185.98.170.55 and IPv6 diagnostics succeed; malformed IPs, ports, zone identifiers and out-of-range/multiple CIDR prefixes fail. Existing protected bans, TTL, audit, independent guardian, rollback and comparison regressions pass under the same disabled-function setup.
- security-page.js verifies the independent page, unique IDs, removal of the firewall tab, guest write denial, admin login/logout, absolute same-origin endpoint validation and CSRF-protected unban. security-ui.js additionally verifies that a firewall page without the overview does not fetch/render a Security snapshot. Existing real PHP-CGI authentication/session/CSRF tests pass.
- Installer/rollback tests pass with 42 targets including new page/controller; uninstall also removes the standalone directory. Bash syntax passes for 35 sources, JavaScript syntax for 12 files plus inline static-page scripts, and real PHP lint for all 4 PHP files.
- Source/port cells now retain at least 270px and metadata 145px, with contained horizontal scroll. Three source panels are used only at viewport widths of at least 1900px. No live browser screenshot/layout verification performed.
- Web process identity is still reported from the existing root/unprivileged check. This update explains activation state; it does not silently activate web-user migration or suppress root findings. Router-side IPC/lighttpd/TLS checks remain required.

## Commented FastCGI examples r26
- web-isolation-check.py includes multiple fully commented socket examples (including variable concatenation), a separate commented-only PHP backend file, and one active literal socket. The read-only check succeeds without writes/restarts. Migration changes only the active path byte-for-byte, preserving examples and unrelated backend settings, permissions and rollback.
- Two active sockets remain rejected, including two assignments on one line. An active variable/concatenation expression is rejected before migration. Failed lighttpd validation restores originals; explicit rollback still passes. Account/process identity and lighttpd runtime remain mocked.
- Installer plan/apply/rollback passes with unchanged 42 targets; Bash syntax checks pass for the modified helper and installer. No broad suite rerun for this narrow shell-only fix; r25 results remain recorded above. Actual lighttpd/Entware migration must still be verified on the router.

## BusyBox stat compatibility r27
- web-isolation-check.py supplies a stat executable that fails every invocation, matching a router without stat -c; successful migration/rollback uses no stat command. Metadata comes from real PHP core stat().
- A forced PHP metadata failure stops migration before credential permission changes and restores the unchanged config. ERR propagation and explicit return checks prevent empty metadata from being accepted.
- Valid metadata still restores modes on rollback. A legacy tab/path-only ledger is reported by --check and refused by --rollback before config/marker mutation; early-boot --ensure-user still runs and warns without claiming to recover old permissions.
- Isolated installer plan/apply/rollback and modified Bash syntax pass. Process identities and lighttpd behavior remain mocked. No claim is made that metadata missing from an existing router backup has been recovered.

## Lossless database optimization r28
- firewall-optimize-check.py executes the real stats --optimize-db command with actual SQLite: verified online backup, exact schema/content equality across every user table, full 65,535-port history retention, report-state preservation, repeatability, backup failure, unexpected-index rejection, no kernel/capture calls and no old-index recreation by the ordinary updater.
- The actual uploaded database was backed up to an isolated copy and optimized by that same command: 31,211,520 to 26,206,208 bytes. Full sorted-row SHA-256 comparisons match for all five table schemas and contents, both against the optimized DB and its generated backup. No uploaded/live DB bytes were modified.
- Measured representative top-list/IP-lookup/time-window queries on an isolated compact-index copy return the same results; host timings are comparable, not router performance measurements.
- The online backup remains a separate retained file; the database size reduction does not reclaim the backup's disk usage.

- Final r28 suite: 30/30 test programs pass. Syntax checks pass for 35 Bash sources, 12 JavaScript files and 4 PHP sources. The optimization regression also retains an open WAL-mode connection with committed rows still in the WAL, and verifies those rows in the online backup and optimized database.

## Security page favicon/title r29
- Existing standalone security-page and security-ui tests pass; installer Bash syntax passes. The page references the same installed SVG favicon as the other dashboards and its title is Security & Health. No new tests added for this presentation-only change.

## Security comparison normalization/labels r30
- Real PHP/SQLite security-engine tests add NULL, empty, XX, spaced/lowercase XX, --, ??, missing metadata and US case/space variants. All unknown hits merge into one XX group before ranking, case variants merge, summaries match and future-dated rows are excluded. Exact adjacent 24h bounds are checked.
- Security UI tests exercise day/week heading changes, exact date-range text, Unknown (XX) display and four-column empty-table colspan; standalone page test remains passing.
- Security-only scrollbar-gutter is automatic, header gutter background matches headings and table bodies retain background. No real-browser screenshot confirmation available.

- Targeted installer/rollback, admin, firewall indicator, ping history and traffic export regressions pass; modified Bash/JS syntax and real PHP lint pass.

## Blocklist diagnostics r31 (2026-10-16)
- blocklist-diagnostics-check.py runs actual updater functions with mocked feeds and ipset: HTTP404/DNS/timeout/TLS/empty source, missing cache, successful cached fallback, capacity/memory/invalid-line staging failures, set creation, swap and persistence errors. Old installed sets remain; failed rollback retains the recovery staging set. No host firewall or network is modified by these tests.
- Actual PHP/SQLite engine checks verify persisted error/source-warning fields, last installed count retention, source warnings distinct from size warnings, public failure text with private actor/note excluded, and unknown installed count after rollback failure.
- Security UI checks verify literal safe diagnostic rendering, Details in list/timeline, Not applied instead of false -100%, and rejected status despite baseline. Existing page/auth/maintenance/export tests remain applicable.

- Final r31 suite: 31/31 test programs pass. Syntax checks pass for 35 Bash sources, 12 JavaScript files and 4 PHP sources. Router kernel, actual feed failure, lighttpd, browser layout and SMTP delivery were not exercised. Historical failure details cannot be reconstructed from older records.

## Security typography/layout r32 (2026-10-16)
- Existing standalone-page, Security UI, menu/layout, density and isolated installer/apply/rollback checks pass. Installer Bash syntax and heading markup checks pass.
- New styles are confined to the standalone page: semantic headings, type hierarchy, responsive cards, aligned numeric columns, note wrapping and contained wide tables. Shared CSS/JS remain unchanged; no new mirror tests added for this presentation-only change.
- Browser rendering could not be verified: the Chromium download was unavailable/truncated in this environment. Router browser appearance remains to be checked after a hard refresh; no screenshot or live-router validation claimed. The r31 full-suite record remains applicable to unchanged updater/engine code.

## Unprivileged monitor publication r33 (2026-10-16)
- Eight targeted programs pass: ping history, ping notifications, ping settings, traffic export, dashboard availability, log controls, admin controls and isolated installer/apply/rollback. Modified Bash and dashboard inline JavaScript syntax pass.
- Ping history regression now executes actual chmod/atomic publication under umask 077 and verifies the resulting 0644 mode. Traffic export regression executes the real script under umask 077 and checks chart, HTML, both interface exports and the index modes; failed exports still preserve last-good data.
- Dashboard VM regression distinguishes missing data from disabled services, verifies loaded ping/traffic, actual 100% loss as OFFLINE, and HTTP403 log error visibility without claiming daemon shutdown.
- No host cron/syslog/lighttpd changes, actual ktweb HTTP access or router service state verification performed. Root cause in code is confirmed; attribution of the router symptom requires the supplied router diagnostics. Raw log/DB/credential modes remain unchanged.

## Read-only system logs and scheduler startup r34 (2026-10-16)
- Full suite: 33/33 test programs pass. Syntax checks pass for 35 Bash sources, 13 JavaScript files, 4 PHP sources and the main-dashboard inline JavaScript.
- Actual PHP/SQLite engine regression reads a private 0600 multi-megabyte system log without changing content/mode, returns at most 1000 lines/128 KiB, follows a recreated 0600 file after rotation, and rejects unknown paths and symbolic links.
- Real PHP-CGI API regression (broker transport stub) allows guest systemlog reads while preserving HTTPS/origin checks, private-audit restrictions, admin login/session/CSRF and typed writes. Dashboard regression consumes the bounded JSON preview and displays the limit; rendering remains text-only.
- cron-bootstrap-check.py executes the actual init wrapper against isolated daemon/init fixtures: starts missing cron at install/boot, leaves running cron alone, refuses missing/ambiguous/failed init, rejects false-success init without a process and preserves crontab bytes. Installer/apply/rollback regression includes the new post-install scheduler check.
- Actual router daemon startup/reboot, browser rendering, Unix socket transport and the underlying reason cron previously stopped remain unverified. No host syslog-ng, cron, logrotate or firewall configuration modified during testing.

## Progressive system-log browsing r35 (2026-10-16)
- Full suite: 35/35 test programs pass. Syntax checks pass for 35 Bash sources, 14 JavaScript files, 4 PHP sources and the main-dashboard inline JavaScript.
- systemlog-pagination-check.py executes actual PHP against private log fixtures: complete byte-for-byte reconstruction of 18,000 UTF-8 records, long multibyte lines spanning pages, blank/empty logs, final newline variants, append-stable snapshots and bounded page sizes. No gaps/duplicates; file mode remains private. Renamed/replaced files, smaller truncation and same-size rewritten-tail copytruncate require a fresh view. Malformed/oversized/cross-log cursors and arbitrary paths are rejected.
- log-pagination.js executes actual dashboard functions: prepend with scroll anchoring, pane-only auto-refresh pause, explicit refresh/resume, retry after network failure with content/cursor preserved, per-log isolation and rotation notice without mixing content.
- Real PHP-CGI broker-transport regression verifies guest GET cursor/log-ID forwarding while existing HTTPS/origin/admin/CSRF checks remain intact. Underlying source logs and scheduler settings are unchanged.
- Router browser rendering, actual Unix socket transport and live syslog/logrotate interaction remain unverified; rotation and append behavior were exercised against real local files, frontend behavior in a DOM fixture.

## Complete expanded logs r36 (2026-10-16)
- All 35 test programs pass across the suite and final targeted rerun. The first run exposed shared full-refresh/continuation pacing; separate rate buckets corrected it. Actual PHP pagination, engine and PHP-CGI API regressions then pass. Bash/JavaScript/PHP and dashboard inline-script syntax checks pass.
- Updated dashboard regression verifies automatic continuation to the beginning of the current file, no manual pagination controls, System log open by default, closed-pane skipping, cancellation on collapse, reload on expansion, per-log isolation, full-view automatic refresh, rate-limit retry and retaining the last complete view on partial transfer failure/rotation.
- Actual PHP test verifies independent pacing of new full-view loads and internal continuation requests. Existing complete byte-reconstruction/private-mode/rotation tests remain passing.
- Only completed snapshots replace displayed content; original logs, logrotate, scheduler settings and databases remain unchanged. Router browser performance/visual rendering and actual HTTP/socket interaction remain unverified; local frontend fixtures and real PHP/file tests were used.

## JSON transport and log sizes r37 (2026-10-16)
- Full suite: 35/35 test programs pass. Syntax checks pass for 35 Bash sources, 14 JavaScript files, 4 PHP sources and the main-dashboard inline JavaScript.
- Actual PHP log regression checks each serialized response remains below the observed 65,528-character truncation point, including long Unicode, slash/quote/backslash and control-heavy content. It reconstructs complete logs without byte loss; raw reads are at most 32 KiB and actual compact JSON is bounded to 48,000 bytes. Pretty CLI envelopes remain below 49,000 bytes in fixtures.
- PHP-CGI regression now routes a real large engine-generated log frame through the broker transport fixture and actual API serialization; the response parses completely. Public log_sizes routing is accepted while existing HTTPS/origin/admin/CSRF checks remain intact.
- Root metadata regression verifies private-file size and missing-log handling without content reads. Frontend regression verifies closed/empty log sizes, title updates at the first received block and size retention after content failure.
- The exact router truncation layer is unconfirmed. Local tests exercise PHP-CGI and a simulated 64 KiB cut; actual lighttpd/FastCGI/router HTTP behavior remains to be checked. No server configuration, logrotate or source-log modes changed.

## GeoIP and authenticated Settings r38 (2026-10-17)
- All 36 test programs pass across the full suite and final targeted reruns. Syntax checks pass for 35 Bash sources, 16 JavaScript files and 5 PHP sources, plus the main-dashboard inline script. Settings HTML IDs are unique.
- Actual updater-function fixtures verify refused-connection retries, IPv4-first IPdeny transport followed by automatic-family recovery, invalid-cache rejection, installed-set retention and explicit IPv6-only exclusions without changing IPv4 country selection. Exclusions are informational update details and do not themselves raise a repeated source-failure warning.
- Real PHP/SQLite Settings regressions exercise fixed-file/group/key restrictions, type/range/IP/port/text validation, injection rejection, revision conflicts, preservation of unrelated comments/keys, private modes/backups, no retention reduction, Security management CIDRs and full firewall configuration confirmation/rollback through the existing guardian. Missing PPP interval displays the actual service default of 5 seconds.
- PHP-CGI API regressions deny guest Settings reads/writes, require POST/CSRF for writes and forward typed settings/revisions without credentials/CSRF in the broker payload. Existing HTTPS/origin/session and admin tests remain passing.
- Settings DOM fixture executes actual form generation/save paths: no guest configuration requests, text-safe schema rendering, changed-values-only writes, conflict errors, pending policy controls and private-form clearing on logout. Shared controller tolerates pages without diagnostic modal nodes. Installer plan/apply/rollback checks pass with 45 targets; selective uninstall removes the new page/controller with the security stack.
- Public IPdeny IPv6 index was read during the request and contained no kp entry. No live router download failure was reproduced or reclassified as a confirmed HTTP404/zero-allocation condition. No country is excluded automatically. Router connectivity, actual lighttpd/socket transport and browser visual behavior remain unverified. No GitHub publication, SMTP delivery, database rewrite or host firewall/syslog/cron mutation performed.

## r39 — Ping warning versus target reachability (2026-10-17)
- ping-notifications-check.py PASS: actual production state transitions and executable email capture (no SMTP). Partial loss 3.226% followed by healthy check, latency-only warning and legacy mixed state send no recovery email. Warning -> 100% loss -> partial replies measures from first total loss; no duplicate on later healthy samples. Separate IPv4/IPv6 recovery, state persistence across invocations, target changes, invalid/backward timestamps and route/manual WAN labels are covered.
- ping-history-check.py and ping-settings-check.py PASS: 70000 synthetic samples, temporal ranges, point bounds, retained data, browser controls and configuration persistence.
- wan-syslog-check.py and wan-service-check.py PASS: independent PPP notifications, actual 23-second fixture, deduplication, rotation, SMTP retry and service lifecycle remain valid.
- installer-check.py PASS: isolated 45-target plan/install/rollback and configuration preservation; PHP lint/service effects mocked in this fixture. Pingtool and installer Bash syntax PASS.
- Focused checks only for this notification change; full r38 suite results above remain historical. No live router, real SMTP delivery or GitHub publication performed.

## r40 — Security summary result colors (2026-10-17)
- Existing security-ui.js and security-page.js checks PASS; Security UI JavaScript and installer Bash syntax PASS.
- An ephemeral extension of the existing UI fixture verified all four green states, failed firewall/root web/unverified backup red states, the 5% free-space boundary, zero-byte free storage, intentionally disabled but healthy firewall, and fetch failures clearing old results to red/unavailable.
- Result colors use existing Keenetic --green/--red tokens with their dark-theme overrides. Text descriptions remain present. No new permanent tests were added for this visual change. Live browser/router visual verification remains pending.

## r41 — Three-state health and Security data banner (2026-10-17)
- security-ui.js PASS including verified green, detected failures red, missing evidence/unverified backup yellow, load errors clearing results to unknown, snapshot timestamp publication and immediate banner refresh after failure/success.
- layout-controls.js PASS including Security initial waiting, fresh snapshot ready, older-than-three-minutes stale, load error, and missing timestamp. Existing traffic timestamp fallback and menu checks retained.
- security-page.js, density-controls.js and settings-ui.js PASS. Shared UI JS and Security UI JS syntax and installer Bash syntax PASS. No router/browser visual deployment test performed.

## r42 — More visible OK results (2026-10-17)
- Security OK result styling is scoped to the four summary cards: weight 700, light-theme green #00843d and dark-theme green #5cda91. Calculated contrast against the shared theme backgrounds is 4.81:1 and 7.42:1 respectively.
- Existing security-ui.js and security-page.js checks PASS; installer Bash syntax PASS. No additional tests were added for this visual-only change. Live browser visual verification remains pending.

## r43 — Readable storage and colored security digest (2026-10-17)
- security-digest-check.py PASS using actual PHP helpers: B/KB/MB/GB/TB scaling, rounding across unit boundaries, zero/invalid values, 116938457088 -> 116,9 GB, health colors, HTML escaping and unchanged neutral Recent events line.
- email-sender-check.py PASS: real Bash module with mocked decryption and curl, parsed multipart plain/HTML alternatives, legacy escaped-newline notifications, private temporary message file, cleanup and transport-failure status. No real SMTP sent.
- security-engine-check.py PASS using real PHP/SQLite and mocked router commands, including daily HTML/plain queue creation, optional HTML transport argument, failed delivery retained for retry, successful delivery removed, and existing security/settings/guardian regressions.
- security-ui.js PASS including GB storage and MB database display. security-page.js and isolated installer/rollback checks PASS; installer service/PHP checks mocked. Email/installer Bash syntax and Security Engine actual PHP lint PASS.
- No live router, mail-client visual rendering or SMTP delivery verification performed. Existing configuration, history, schedules and policy remain unchanged. Previously queued messages retain their original content; formatting applies to newly generated digests.

## r44 — Larger Security summary headings (2026-10-17)
- Summary-card heading CSS updated to 20px/600/1.35; result text stays 17px and existing status colors are retained. Existing security-page.js and security-ui.js checks PASS; installer Bash syntax PASS.
- Source review confirms default monitor_interval=60 seconds (configurable 30–3600), browser snapshot refresh=60000ms, and no overlapping monitor jobs. Refresh snapshot fetches the existing JSON rather than triggering a service tick. This revision changes no intervals. Live browser visual verification remains pending.


## r45 — Unified browser refresh (2026-10-17)
- All 13 JavaScript suites PASS. New unified-refresh.js exercises real shared scheduler with a deterministic clock: default, allowed values, Off/manual, navigation persistence, storage-event synchronization, hidden tabs, no overlap, changing to Off during a pending refresh, retry after failure and blocked storage. Real Ping/Traffic refresh adapters are executed; chart updates retain existing zoom/log options.
- Settings fixture confirms manual/automatic refresh preserves dirty fields and revision state, while clean forms can reload. Firewall log fixture covers shared refresh with closed/open panels; full Dashboard log pagination/cancellation/complete-only publication checks remain valid. Shared layout fixture was adapted to model delayed timers rather than executing them immediately.
- ping-history, ping-settings, ping-notifications, traffic-export, installer, port-details and geography Python checks PASS. Existing 70000-sample history/range tests and real generated Traffic export checks are retained. Installer test uses mocked PHP/service actions.
- All Entware Bash sources and four static/Ping inline JavaScript blocks pass syntax checks. Source checks confirm old per-page selectors and network timers are removed; policy safety/countdown and cosmetic clock timers remain.
- No router deployment or live browser visual test performed. Generated Ping/Traffic pages require their next normal generation (or explicit force) to obtain their new templates and asset cache tokens.
- Final refresh race checks PASS: Settings edits entered while a configuration response is in flight are preserved; Traffic fetches configured tab interfaces even after a missing initial export and renders the interface selected when loading finishes. Settings, unified-refresh and real Traffic export checks rerun after these changes.


## r46 — Shared email layout (2026-10-18)
- mail-layout-check.py PASS with actual PHP: ping metric colors, complete standard MTR rows and metadata, IPv6 host/attacker parsing, extra/malformed MTR fallback, firewall IP/port tables, package version tables, PPP/upgrade states, custom Security HTML, escaped unsafe text and quoted-printable round trip.
- email-sender-check.py PASS: real Bash module and PHP renderer with mocked OpenSSL password decryption/curl SMTP; existing two-argument messages become HTML/plain alternatives, custom Security content is retained, encoded HTML lines are bounded, missing/failed renderer falls back without losing the notification, and failed SMTP status/temporary-file permissions/cleanup remain valid.
- Existing security-digest, WAN syslog, Entware worker and ping notification suites PASS. Installer plan/apply/rollback fixture PASS for 46 targets, including new helper creation/removal and preserved config; PHP lint/service effects are mocked there. Existing security uninstaller regression PASS.
- Actual PHP renderer lint and Bash module/installer/uninstaller syntax PASS. No real SMTP email, router deployment or mail-client visual rendering test performed. Presentation varies with recipient mail-client support; the full text alternative is always retained.


## r47 — Numeric presentation, Settings layout and Dashboard Security card (2026-10-18)
- All 14 JavaScript suites PASS. New number-format.js covers 1.234,56, exact large integers, signed counts, bytes/rates, strict comma/dot parsing, invalid/ambiguous input rejection and shared formatter loading on every page. It executes the actual Dashboard Security loader for green/error/unknown states, GB display and 1.200 recent-event count.
- Extended Settings fixture verifies preset/Custom switching, grouped input values, decimal quota typed payload, all 24 summary-hour options, integer/ambiguous-input rejection and existing guest/CSRF/revision/guard/unsaved-edit behavior. Native DOM is represented by fixtures; live browser visual rendering is not verified.
- Actual PHP/SQLite security-engine suite PASS: preset/section/hour metadata, bounded settings response below 48 KiB, existing save validation, retention protection, configuration preservation and policy confirmation/rollback remain valid.
- Seven Python suites PASS: ping history/settings/notifications, Traffic export, isolated 47-target installer/rollback, geography and real CGI security API. Ping retains 70000 synthetic samples and emits localized sample/point labels; raw averages and chart values remain numeric.
- Source audit finds no remaining toFixed-based displayed quantities in the touched pages; the two remaining Firewall toFixed calls produce CSS percentages and correctly retain machine decimal syntax. Date/source-log/identifier formats are intentionally not numeric-format targets.
- All Entware Bash sources, four inline static/Ping JS blocks and modified asset JS syntax PASS; static/Ping HTML IDs unique; actual PHP Settings schema lint PASS. No router deployment or live browser visual test performed.

## r48 — Settings checkbox titles and alignment (2026-10-19)

- JavaScript syntax check and existing Settings UI fixture passed: guest access gate, typed values, presets/custom input, localized parsing, revisions/conflicts, guarded firewall changes and preservation of unsaved edits.
- Existing Security page fixture and installer Bash syntax check passed.
- Reviewed boolean markup and CSS: visible associated title, separate checkbox/state row, 40px minimum control height and responsive inherited grid. No live browser visual inspection or router installation was performed.
- Archive checksums verified against every packaged file.

## r49 — Blocklist diagnostics in security email (2026-10-19)

- Production PHP lint and expanded security-digest-check.py passed using PHP 8.3 with -n: reproduce the provided GeoBlock cached Russia/curl 92 and GeoBlock6 North Korea HTTP 404 records; verify installed counts, localized change, explicit retention, attempt/success timezone dates, missing success/source age, threshold warning, unknown installed state and suppression of rejected candidate -100%. Malicious labels/details remain escaped in HTML and literal in text; HTML line breaks and existing health colors/Recent events are preserved.
- Actual shared mail renderer fixtures passed, including custom security HTML/plain content and quoted-printable handling. No SMTP messages were sent.
- Real PHP/SQLite security-engine integration passed, including daily digest queue, HTML/plain transport arguments, failed transport retry and acknowledgement, protected networks, policy guards, diagnostics, list events and settings validation.
- Isolated 47-target installer plan/apply/rollback fixture and installer Bash syntax passed. Installer PHP/service probes are mocked; no router installation or live mail-client rendering performed.
- Every file checksum in the distributable archive was verified.

## r50 — Dashboard Security card layout (2026-10-20)

- Inspected the supplied screenshot: the apparent extra row was the combination of per-item rules and the checked-time footer; no extra data section was present.
- Existing number-format.js, dashboard-availability.js and unified-refresh.js passed: dashboard security values/colors/unavailable state, monitor availability, shared cadence and preserved adapters. No data loader or operational behavior was changed.
- Structural checks passed: unique Dashboard IDs, one native Security title link, two groups containing four values, one checked-time footer and no redundant action button. Dashboard inline JavaScript and installer Bash syntax passed.
- Reviewed responsive CSS: two Security columns above 900px and one below; inherited row alignment/font size, last-row border removal and home-only card padding. Browser rendering was attempted but unavailable: no browser binary was installed and the browser download returned an invalid archive. No visual desktop/mobile rendering or router installation is claimed.
- Every distributable file checksum was verified.
