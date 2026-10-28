# KeenTool coordinated package 2.0.18

## Coordinated package 2.0.18 / Firewall 4.0.7 — 2026-10-28

- Expose a confirmed Balanced action through KeenTool: Firewall Suite → History aggregation settings → Apply Balanced profile now. Explain the verified backup, compact IP identifiers, 2/7/365-day policy and irreversible older time precision before consent. Declining performs no maintenance. Retain custom precision settings (including monthly cutoff), status and an explicit saved-policy run action.
- New fresh installations default to Balanced: enabled, two days of original samples, hourly through seven, daily through 365, then calendar-month buckets, with compact IP storage requested. The first due statistics maintenance converts storage after a verified backup. The installer does not convert databases itself.
- Preserve existing saved history configuration byte-for-byte on upgrade, including legacy 7/30-day files. Missing legacy compact/monthly fields remain false/0; an upgrade with no history file retains the legacy policy. Existing installations opt in through the menu or explicit CLI. Add compact-storage control and Balanced presets to Web Settings.
- Explicit storage expansion disables automatic reconversion. Keep current events; prior time precision is not reconstructed. Validate fresh defaults, first due conversion, legacy omission, confirmation/decline, custom presets, shared cadence and expansion behavior in isolated regression checks.

Package 2.0.18 / Firewall 4.0.7. Manager remains 2.0.11; Stats remains 4.0.2. History CLI/engine and database engine advance to 1.0.2, Settings engine to 1.0.3 and release transaction engine to 1.0.5. No filtering rules or unrelated retention policy is changed.

After update use KeenTool 3 → 6 → 2 to apply Balanced to an existing database. Fresh installations are configured automatically for first due statistics maintenance. Existing settings are preserved. See suite/docs/DATABASE_STORAGE.md.
