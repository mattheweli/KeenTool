# KeenTool 2.0.1

Relative to published v2.0.0 (`2758f0d7ee8fb9e703ee7c35ea866002e4edb036` on main).

- Add progressive firewall history settings in the CLI Firewall menu and authenticated web Settings, with enabled/raw/hourly thresholds, ranges/presets, revision checks, private configuration backup and cross-field validation. History settings do not reapply the firewall hook.
- Add the coordinated history engine/CLI, default 7-day raw and 30-day hourly detail, installation targets and missing-default configuration migration. Preserve existing history settings, scheduler, credentials and databases during package updates.
- Expose historical bucket precision in dashboard/Security diagnostics and comparisons. Preserve all-time IP/list totals, local calendar-day totals, global counters, full port history and reporting state.
- Patch component versions: manager/dashboard 2.0.1, firewall statistics 4.0.1, firewall page 2.0.1, changed settings/security/installation/uninstall helpers 1.0.1; new history helpers 1.0.0. Unchanged components retain their published versions.

## Upgrade and history precision

Install the complete KeenTool 2.0.1 suite through `keentool --update`. Component sources require the coordinated runtime; do not install isolated scripts. Existing settings, credentials, schedules and databases are preserved by the installer. Missing history defaults are enabled (7 days of samples, hourly through 30 days, daily thereafter). Aggregation starts at the next normal firewall statistics job, after a verified private baseline backup, and then runs at most daily. Configure it in KeenTool → Firewall → History aggregation settings, or authenticated Settings → Firewall history.

All IP/list and calendar-day hit totals remain exact; older time precision is reduced irreversibly. Period boundaries crossing a bucket and historical first/last timestamps are approximate and labeled. Global counters, full port histories and reporting state are untouched. Increasing thresholds or disabling aggregation cannot reconstruct prior detail. The baseline backup is retained separately and occupies storage; restoring it later would lose events collected since that backup. See suite/docs/FIREWALL_HISTORY.md.

## Validation

45 isolated regression checks passed, including real SQLite/PHP-core aggregation, DST transitions, backup verification, rollback on integer overflow, writer locking and installer/updater compatibility. A private database copy reduced from 46.9 MB to 43.8 MB with all 30,626,489 hits and all metadata/global/report state preserved; production dashboard SQL/geography export passed. No private database is distributed. Physical-router execution/reboot and live SMTP were not independently tested for this patch.
