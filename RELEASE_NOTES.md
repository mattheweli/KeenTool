# KeenTool coordinated package 2.0.27

## Coordinated package 2.0.27 / KeenTool 2.0.14 — 2026-11-14

- Restore Legacy-compatible installation analytics from the coordinated installer, strictly after successful commit, service/TLS checks and any required firewall confirmation. Plans, failed installs and rollbacks do not send events.
- Preserve /opt/etc/keentool.id; new IDs are random and independent of hardware identifiers. Send only the existing install/update event and UID query to the existing HTTPS endpoint. No configuration, credentials, traffic history or firewall records are included; the server can observe the source IP.
- Suppress acknowledged duplicate events per release and skip new events for same-version repairs. Persist a bounded private queue after network/HTTP failure; retry one event on the next successful installation or explicit retry. Each curl attempt has a 2-second connection / 3-second total timeout, requires a 2xx response and does not follow redirects. Analytics failure cannot fail installation.
- Add KeenTool menu i and --analytics status/on/off/retry. Disabling clears pending events; --no-analytics persists opt-out during installation/update. Document default enablement, state files and the limitation that exactly-once delivery cannot be guaranteed without server-side idempotency.
- Remove unreachable Legacy analytics senders and integrate selective uninstall data retention. Add mocked endpoint tests and actual installer regressions for success, Legacy migration, repairs, failures, rollback, opt-out and retry.

Package 2.0.27; KeenTool manager 2.0.14; installer 1.0.10; updater/bootstrap 1.0.9; transaction engine 1.0.7; analytics helper 1.0.0. Firewall and other tool versions are unchanged. No live analytics endpoint is contacted by tests.

Update with KeenTool u. Installation analytics defaults to enabled, preserving the Legacy behavior. Use menu i or keentool --analytics off to disable; use --no-analytics during installation/update to opt out before the first event. Physical router upgrades and production endpoint delivery are not independently verified by CI.
