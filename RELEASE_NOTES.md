# KeenTool 2.0.4

Relative to published v2.0.3 (main `9350079e75db877333c0b927562734537e4aecc0`).

- Make Install / Update verify every installed file owned by the selected component, plus shared dependencies, against the published target SHA-256 and expected permissions. A current installed-release.json no longer hides an old Monitor, missing API/helper or modified script. Report every differing path, reason and readable source version before installation consent. Unrelated component source differences do not trigger the selected component.
- Add explicit FILE_SCOPES.json ownership for all 54 installation targets. The lightweight GitHub-digest-verified overview carries source/path/owner/hash/mode/version data; normal checks still do not download the archive. After consent, require the archive's INSTALL.tsv, scopes and source hashes to match the approved overview before applying the coordinated transaction.
- Keep the Main Dashboard in the KeenTool repository while tracking Dashboard 2.0.3 separately from manager 2.0.4. Check the actual installed HTML version and content, including when an old record does not contain a Dashboard entry or incorrectly claims a newer version. The dashboard menu selects Dashboard instead of KeenTool; the global overview includes all six components.
- Display the recorded Firewall suite version in the main tool summary. Keep Monitor and Stats script versions in the firewall submenu; independent script versions are not used as the suite version.
- Retain explicit full-package repair, coordinated file installation, dependency preflight, successful-update menu restart, backup/rollback and preservation of credentials, configuration, databases and schedules. Older version-only overviews explicitly state that files were not verified.
- Add transport/menu regression cases for same-version Monitor 3.0.0 versus expected 4.0.0, scoped file coverage, unrelated component drift, shared dependencies, missing files and bad modes, actual Dashboard HTML versus the record, and mismatched target metadata.

Firewall remains 4.0.1 (Monitor 4.0.0, Stats 4.0.1). Pingtool/Traffic/SMB remain 2.0.0. Installer remains 1.0.2; updater/verifier/bootstrap advance to 1.0.3. No firewall policy, cron or database history change is included. See [Update behavior](docs/UPDATE_RECOVERY.md) and the [2.0.3 changelog](docs/history/STABLE_2.0.3.md).

## Upgrade

Run `/opt/bin/bash /opt/bin/keentool --update` or use the KeenTool self-update menu. After 2.0.4 is installed, a component's Install / Update compares every owned file and shared dependency against the verified release target hashes and modes, including when the declared version is current. Review differences and coordinated package changes before consenting to the archive download and installation.

Main Dashboard remains in mattheweli/KeenTool but has its own version (2.0.3), update scope and actual HTML check. The main menu reports Firewall suite 4.0.1 rather than using the Monitor entry-point version. Monitor 4.0.0 and Stats 4.0.1 remain legitimate script versions within that suite.

The coordinated installer preserves settings, credentials, schedules and databases through its normal backup/rollback transaction. No firewall policy or history retention change is included. Explicit full-package verification/repair remains available.

## Validation

47 isolated local checks passed, including same-version stale Monitor detection, scoped and shared file coverage, unrelated component exclusion, missing files and wrong permissions, actual Dashboard version versus installed record, correct firewall menu version, and approved overview/archive target consistency. GitHub checks must pass for the exact release commit before publication. No physical-router reboot or live SMTP delivery is claimed.
