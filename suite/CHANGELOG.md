# Stable changelog — 2026-10-22

No tags or GitHub Releases existed in the five repositories when inspected. These changes are relative to their current public main commits, not to an invented published release. Exact baselines are in UPSTREAM_BASELINES.json. The complete r1–r50 development changelog is archived under docs/history/.

## KeenTool 2.0.0

Baseline: `8d640c8b06968b0f24ce41feb1bc5b0a89c3f541`.

- Remote whole-suite updater and standalone legacy/alpha bootstrap: stable-only release lookup, confirmation, no downgrade, SHA-256/GitHub digest validation, bounded safe TAR/PAX extraction and complete file-manifest verification before the same migration installer. Menu/CLI checks and offline updates remain available.
- New coordinated 2.0.0 suite installation: fresh/upstream/alpha detection, verified file/configuration backups, atomic replacement, automatic/manual rollback and whole-package update entry point.
- Uniform Keenetic-inspired responsive navigation, shared refresh with Off/manual controls, remembered navigation/density, readable tables and a full-width Security & Health overview. Remove development banners and show versions in copyright footers.
- Dot thousands/comma decimals across rendered dashboard values; preserve raw technical data and arithmetic. Full expanded log views, bounded internal transport, log sizes and allowlisted read-only system logs without changing syslog rotation.
- Password-only HTTPS administrator access shared with Settings/Security, typed settings with ranges/presets, revision conflict handling and guarded firewall changes.
- Entware update monitoring/notifications and an explicitly requested maintenance worker that stops/restarts Entware services. Shared HTML/plain notification layout with safe tables, MTR rendering and semantic health colors.
- Independent incremental PPP syslog monitor, root broker, ktweb web-isolation tools, boot scheduler check and private helper paths. BusyBox metadata fallback removes the GNU stat requirement.

## keenetic-pingtool 2.0.0

Baseline: `bba63ac0b099f4001b6f91bb7314bc704f08e238`.

- External persistent configuration; migrate supported inline preferences on upgrade. Configurable retention/display points and time-based history windows (hour/day/month/MAX), separate sample and plotted-point counts, optional latency/loss peaks and IPv4/IPv6 coverage.
- Preserve full-resolution database history according to existing retention; plotting aggregation does not replace database rows. External settings survive script replacement.
- Distinguish warning recovery from true all-probe-unreachable recovery; partial loss/latency warning clearance does not emit a WAN-reconnection email. Include WAN/family labels and explain sampled durations.
- Detect PPP transitions incrementally from existing syslog without changing syslog-ng/logrotate; independent scheduled service and retryable notifications. Shared safe email/MTR layout and common browser refresh.
- Stable 2.0.0 page/footer, English interface and uniform numeric presentation; package runtime is required.

## Traffic_manager 2.0.0

Baseline: `1c5148ef576b2c97fb22f81471a0ace3eae6ea6f`.

- Stable 2.0.0 responsive multi-interface dashboard with aligned table headers/body, full dates in Top 10 Days, paired traffic doughnuts/values and common theme/refresh controls.
- Resolve interface selection from explicit arguments/existing configuration instead of publishing Unknown; validate vnStat JSON and retain the last good export when vnStat fails. Missing data is distinguished from a disabled daemon.
- Preserve vnStat databases, custom interface jobs and existing exports. Uniform grouped values/decimal separators in quotas, rates, totals and tooltips.
- External dashboard settings survive updates. Full-width layouts, shared navigation and version/copyright footer replace the alpha banner.

## SMB_Backup_tool 2.0.0

Baseline: `48b1a83804c3dc9155b7eeb20f01c942c2f3e3c7`.

- Stable 2.0.0 uses the shared Entware Bash runtime, atomic job locks and maintenance deferral; selective uninstallation preserves configuration/data by default.
- Keep existing backup configuration, shares and schedules across package upgrades. Verify completed backup outcomes and expose verified backup state to Security & Health where available.
- Shared readable HTML/plain notifications and isolated checks for archive/transport failure behavior. No automatic credentials or new SMB backup jobs are introduced by suite installation.

## keenetic-firewall 4.0.0

Baseline: `85567431ac3b5ba7c7f4e3a965b63db1d9c684ad`.

- Firewall repository 4.0.0 coordinates monitor/statistics 4.0.0, hook/manager/updater/VPN/abuse tools 3.0.0 and dashboard/API/loader 2.0.0. New security helpers are 1.0.0.
- Hook: dual-family staged/preflight apply, owned-chain replacement and recovery, exact jump teardown, bounded NFLOG independent of DROP, explicit bypasses, coherent enable/IPv6 switches and timeout-capable managed manual bans. Avoid global tcpdump termination.
- Restore saved static/GeoIP/manual/dynamic sets before filtering, including partially populated sets; preserve saved timeout semantics and checkpoint only verified state. Persistent PCAP path and incremental cursor survive normal updates/reboot handling.
- Validate/cache each source, stage kernel sets before swap, reject empty/incomplete/main-list catastrophic shrink candidates, retain installed lists on failure. GeoIP size changes use advisory thresholds and explicit policy baselines. Record detailed download/staging/persistence/cache causes, current/previous counts and last successful installation.
- Password-only admin, HTTPS/CSRF/session/boot checks, guest read-only logs and hidden write controls, root command broker and optional reviewed web privilege separation. Manual ban TTL, IP/subnet diagnostics, event timeline, health summaries and typed Settings are supplied by the shared runtime.
- Preserve historical records and full port lists; portable AWK generation, grouped counters, expandable port badges, IPv6 difference/total display, readable ULOGD timestamps, geographic chart improvements and aligned responsive tables.
- Explicit lossless database optimization with verified SQLite backup and integrity checks; no implicit pruning/rollup. Shared HTML/plain periodic reports and detailed colored security digest.
- IPdeny IPv6 KP HTTP 404/cache age limitations remain documented. Source failures never imply automatic exclusion of a country.

## Version policy after publication

Advance the minor version for improvements and bug fixes (2.0.0 → 2.1.0 → 2.2.0), as the project policy. Major revisions use the next major number. Advance only changed components. Development suffixes belong to unpublished work; stable runtime versions contain no aN suffix. Public tag names use vX.Y.Z per repository. Keep the suite dependency manifest synchronized.
