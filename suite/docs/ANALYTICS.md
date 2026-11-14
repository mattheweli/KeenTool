# Installation analytics

KeenTool restores the Legacy installation/update counters after a successful coordinated installation. Analytics is **enabled by default**, matching the Legacy behavior. It is independent of the local monitoring dashboards and does not measure page views or routine menu use.

## Data and destination

The HTTPS request remains compatible with the existing service:

- `https://keentoolstats.laniakear.workers.dev/track/install?uid=...`
- `https://keentoolstats.laniakear.workers.dev/track/update?uid=...`

Only the event type and persistent random installation ID are transmitted. `/opt/etc/keentool.id` is reused when present; a new ID does not derive from the router MAC, serial number or hardware. The server can observe the source IP, so these requests should be described as pseudonymous rather than fully anonymous. No configuration, passwords, databases, firewall logs or traffic history are included. The package release version is used for local deduplication; the existing server request format does not add it as a field.

This change does not modify the statistics backend or its retention policy.

## Controls

Use KeenTool menu **i**, or:

```sh
keentool --analytics status
keentool --analytics off
keentool --analytics on
keentool --analytics retry
```

Disabling clears queued events and prevents further requests. Enabling does not send historical events retroactively. The existing ID is kept across both operations.

To persist opt-out before the installation event, pass `--no-analytics` to the extracted package's `install.sh`, bootstrap, or the updated `keentool --update` command. The installation plan displays the analytics state. Previously installed updater versions do not understand this new option; use the new extracted installer/bootstrap for initial opt-out.

## Event and delivery rules

- A fresh successful installation queues `install`; a successful upgrade or Legacy migration queues `update`.
- The installer hook runs after program-file commit, required service/TLS checks and guarded firewall confirmation. A deferred firewall migration retains the previous policy as designed; a successful package installation can still record its update.
- Plan/check/rollback actions and failed installations do not queue events. Reinstalling the same coordinated package does not create a new event.
- A private local ledger suppresses already acknowledged events of the same type/release. A pending queue retains at most 16 entries; acknowledged history retains 256 entries.
- Each successful installation or explicit `retry` attempts at most one pending event. There is no background heartbeat or new cron job. A same-version repair may retry an already pending event without creating another event.
- Curl has a 2-second connection timeout and a 3-second total timeout, accepts only a 2xx response, verifies TLS and does not follow redirects. Delivery/state errors cannot fail or roll back installation.
- A connection can time out after the server accepted a request. Exactly-once delivery therefore cannot be guaranteed by the client alone; server-side idempotency would be needed. Local deduplication prevents normal repeated installation calls from generating acknowledged duplicates.

Settings and delivery state are stored in `/opt/etc/keentool/analytics.json` and `analytics-state.json` with mode 0600. A file lock serializes local delivery. Keep-data uninstall preserves settings/ID; manager/all purge removes them. An invalid existing ID is reported and preserved rather than silently creating a second installation identity.

Automated tests use a mock curl endpoint. Isolated installer roots never send real events unless an explicit mock transport is configured for the fixture.
