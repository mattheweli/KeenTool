# Stable changelog — 2026-10-23

## KeenTool 2.0.1

Relative to published v2.0.0 (`2758f0d7ee8fb9e703ee7c35ea866002e4edb036` on main).

- Add progressive firewall history settings in the CLI Firewall menu and authenticated web Settings, with enabled/raw/hourly thresholds, ranges/presets, revision checks, private configuration backup and cross-field validation. History settings do not reapply the firewall hook.
- Add the coordinated history engine/CLI, default 7-day raw and 30-day hourly detail, installation targets and missing-default configuration migration. Preserve existing history settings, scheduler, credentials and databases during package updates.
- Expose historical bucket precision in dashboard/Security diagnostics and comparisons. Preserve all-time IP/list totals, local calendar-day totals, global counters, full port history and reporting state.
- Patch component versions: manager/dashboard 2.0.1, firewall statistics 4.0.1, firewall page 2.0.1, changed settings/security/installation/uninstall helpers 1.0.1; new history helpers 1.0.0. Unchanged components retain their published versions.

## keenetic-firewall 4.0.1

Relative to published v4.0.0 (`55dc2b0404de3ddd0fa87e333ee7a91aeedfd0ca` on main).

- Aggregate older per-IP/list samples into hourly and daily buckets without deleting hit totals or IP/list identities. Leave recent raw samples unchanged. The `resolution` default preserves collector insert compatibility and existing read queries.
- Verify a private SQLite online backup before the first aggregation. Use a single guarded write transaction checking per-IP/list totals, local-day totals and recent samples, plus integrity checks, free-space preflight and the collector's writer lock. Refuse unexpected schema/triggers, invalid counts and timezone changes; preserve data on failure.
- Run maintenance at most daily from the existing statistics schedule, before dashboard export. Keep preview read-only and standalone maintenance independent of kernel/capture reads. Reclaim free pages with VACUUM; retain the original baseline backup separately.
- Respect local calendar days and repeated DST hours; retain existing coarser buckets when thresholds increase. Explain irreversible precision reduction and approximate period boundaries on the dashboard and in Security diagnostics.
- Add isolated real SQLite/PHP-core tests for aggregation, DST, exact totals/recent sample preservation, full port/report/global state, private backups, idempotence, disabled/increased policies, backup failure, integer-overflow rollback and writer locking. Existing installation, updater, security and UI checks remain in the suite.

See [FIREWALL_HISTORY.md](docs/FIREWALL_HISTORY.md) for policy, measured size reduction, configuration and baseline-backup limitations. Previous stable notes remain in [STABLE_2.0.0.md](docs/history/STABLE_2.0.0.md); alpha history is archived separately.
