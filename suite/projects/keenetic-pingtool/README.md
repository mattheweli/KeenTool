# keenetic-pingtool 2.0.0

Stable component sources for the KeenTool suite. Release date: 2026-10-22.

## Installation and updates

Install the complete KeenTool 2.0.0 release from https://github.com/mattheweli/KeenTool/releases. The shared runtime, assets, authentication and security broker are required. Do not copy this component alone over an older installation.

For an extracted complete package, use /opt/bin/bash ./install.sh --plan and follow docs/INSTALL.md. Existing public-source and local-alpha installations use --mode upgrade. New installations require --interface and reviewed web/logging ownership options. Existing databases, configuration, credentials and upgrade schedules are preserved.

## Changes

- External persistent configuration; migrate supported inline preferences on upgrade. Configurable retention/display points and time-based history windows (hour/day/month/MAX), separate sample and plotted-point counts, optional latency/loss peaks and IPv4/IPv6 coverage.
- Preserve full-resolution database history according to existing retention; plotting aggregation does not replace database rows. External settings survive script replacement.
- Distinguish warning recovery from true all-probe-unreachable recovery; partial loss/latency warning clearance does not emit a WAN-reconnection email. Include WAN/family labels and explain sampled durations.
- Detect PPP transitions incrementally from existing syslog without changing syslog-ng/logrotate; independent scheduled service and retryable notifications. Shared safe email/MTR layout and common browser refresh.
- Stable 2.0.0 page/footer, English interface and uniform numeric presentation; package runtime is required.

## Release baseline

Public main commit: bba63ac0b099f4001b6f91bb7314bc704f08e238. No tags or GitHub Releases existed at preparation time. Stable tag: v2.0.0.

See the complete package's CHANGELOG.md, VERSIONS.md, SECURITY.md and docs/VALIDATION.md for coordinated versions, installation, known feed limitations and test evidence. Development history is archived in docs/history/.
