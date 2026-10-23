# Traffic_manager 2.0.0

Stable component sources for the KeenTool suite. Release date: 2026-10-22.

## Installation and updates

Install the complete KeenTool 2.0.0 release from https://github.com/mattheweli/KeenTool/releases. The shared runtime, assets, authentication and security broker are required. Do not copy this component alone over an older installation.

For an extracted complete package, use /opt/bin/bash ./install.sh --plan and follow docs/INSTALL.md. Existing public-source and local-alpha installations use --mode upgrade. New installations require --interface and reviewed web/logging ownership options. Existing databases, configuration, credentials and upgrade schedules are preserved.

## Changes

- Stable 2.0.0 responsive multi-interface dashboard with aligned table headers/body, full dates in Top 10 Days, paired traffic doughnuts/values and common theme/refresh controls.
- Resolve interface selection from explicit arguments/existing configuration instead of publishing Unknown; validate vnStat JSON and retain the last good export when vnStat fails. Missing data is distinguished from a disabled daemon.
- Preserve vnStat databases, custom interface jobs and existing exports. Uniform grouped values/decimal separators in quotas, rates, totals and tooltips.
- External dashboard settings survive updates. Full-width layouts, shared navigation and version/copyright footer replace the alpha banner.

## Release baseline

Public main commit: 1c5148ef576b2c97fb22f81471a0ace3eae6ea6f. No tags or GitHub Releases existed at preparation time. Stable tag: v2.0.0.

See the complete package's CHANGELOG.md, VERSIONS.md, SECURITY.md and docs/VALIDATION.md for coordinated versions, installation, known feed limitations and test evidence. Development history is archived in docs/history/.
