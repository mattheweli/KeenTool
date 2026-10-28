# Installation and migration

## Platform and dependencies

Requires root on Keenetic with Entware mounted at /opt, Entware Bash, IPv4/IPv6 iptables save/restore, ipset hash:net/counters, PHP 8 CLI and CGI with session/password/IP/process/Unix-socket functions, SQLite CLI with -json, curl, vnStat 2, tcpdump, iprange, OpenSSL and lighttpd with matching FastCGI/OpenSSL modules. Optional email/MTR/SMB functions also need mtr, a ping implementation, samba4-client and tar. syslog-ng/logrotate remain administrator-managed. PPP event monitoring requires the existing readable messages file and router PPP events routed to it; configure this logging separately on a new router.

On a new router, install Entware and Bash first. The installer can ask opkg to install userland prerequisites with --apply --install-deps. Package-manager operations are outside the file rollback and may require a network connection; existing package versions are not downgraded by rollback. Kernel modules and router firmware are prerequisites, not replaced by this package.

BusyBox variants without GNU stat -c are supported through PHP core metadata. No nohup or PHP filter extension is required. Router shell commands must explicitly use /opt/bin/bash.

## Verify an extracted package

```sh
cd /opt/tmp/keentool-2.0.0
sha256sum -c CHECKSUMS.sha256
/opt/bin/bash ./install.sh --help
```

Checksums detect corruption; obtain the package through the trusted GitHub release and HTTPS. They are not a detached publisher signature.

## New installation

```sh
/opt/bin/bash ./install.sh --plan --mode fresh --interface ppp0 --configure-web --configure-logging
/opt/bin/bash ./install.sh --apply --mode fresh --interface ppp0 --configure-web --configure-logging
```

Replace ppp0 with the actual WAN interface. If dependencies are missing, first use --apply --install-deps with the same options. The explicit --configure-web option replaces the lighttpd main configuration with a dedicated HTTPS listener on port 8080; --configure-logging adopts ulogd for the NFLOG group-1 PCAP pipeline. Both previous files are backed up. Do not choose these ownership options on a server hosting unrelated sites/logging pipelines without reviewing the plan.

The listener creates a private self-signed certificate only when no certificate exists at /opt/etc/keentool/tls/server.pem. Verify/trust the certificate or replace it with your own PEM before administrator login. There is no HTTP listener created by this configuration. Existing conf.d fragments are not included by the dedicated configuration. Matching lighttpd and OpenSSL/FastCGI plugins are essential; the installer validates with lighttpd -tt and restores the backup on failure.

Without --configure-web the existing listener is checked for syntax. From package 2.0.13, a simple HTTP-only listener can be converted in place with consent; otherwise it is preserved. It must serve /opt/var/www, process PHP and provide HTTPS for administrator requests. The installer does not infer or alter custom virtual hosts. An existing isolated web installation must preserve its listener; the installer rejects --configure-web when web isolation is active.

Fresh installs register the requested interface with vnStat when it is missing and start its native Entware service. New vnStat interface/history data is retained on rollback.

Fresh installs create default jobs for Ping at minutes 12/42, Traffic every ten minutes, Firewall Stats every five minutes and blocklist updates at 04:00. An existing matching command is not duplicated. Firewall filtering starts disabled; countries/services are empty, and email is disabled in a new Ping configuration. Configure these deliberately after installation. An existing firewall.conf is never overwritten with defaults.

## Upgrade from public component sources

```sh
/opt/bin/bash ./install.sh --plan --mode upgrade
/opt/bin/bash ./install.sh --apply --mode upgrade
```

No earlier alpha add-on is required. Missing external pingtool.conf is created by migrating allowlisted literal inline settings, including the supported DB_DIR reference in DB_FILE, rather than executing the old script. Complex shell expressions are refused for manual migration. Existing external settings, firewall.conf, vnStat databases, credentials and every existing cron line are preserved. Missing configuration files get explicit defaults; filtering is disabled when no firewall configuration exists. If an old installation was customized inside the hook rather than firewall.conf, export those settings to firewall.conf before upgrading.

The recognized legacy ulogd PCAP path /tmp/fw_syn_ring.pcap is migrated to /opt/var/log/keentool-firewall/fw_syn_ring.pcap without replacing unrelated configuration lines. A custom capture path requires review or explicit --configure-logging. Exactly one matching executable native init script is required for each affected service. Current PCAP content is retained when switching paths; syslog-ng and logrotate settings are not changed.

## Upgrade from the local alpha

Use the same upgrade commands. Existing alpha helpers are not prerequisites. Stable helpers install to /opt/lib/keentool; old /opt/lib/keentool-test files are retained so the old alpha scripts can be restored. The alpha's external configuration, history, passwords, list snapshots, cron and web isolation remain in place. A pending guarded firewall change must be confirmed/rolled back first. No firewall rules are applied by installation.

## Finish and verify

```sh
/opt/bin/bash /opt/bin/firewall_admin_password
/opt/bin/bash /opt/bin/pingtool.sh force
/opt/bin/bash /opt/bin/traffic_manager.sh ppp0 force
/opt/bin/bash /opt/bin/firewall_stats.sh force
/opt/bin/bash /opt/bin/firewall_security harden-web --check
# Review the plan, then: firewall_security harden-web --apply
/opt/bin/bash /opt/bin/firewall_health
```

Set the password only for a new installation or intentional password change; existing credentials remain valid. Use the router's correct interface. Refresh the browser cache. CLI menu: keentool. HTTPS administrator login is password-only and Settings writes remain protected by CSRF/revision checks. Guest pages remain consultative.

Review firewall.conf, allowed management networks and services before enabling protection. Use the guarded Settings action where available; for an explicitly reviewed CLI configuration apply with table=filter /opt/bin/bash /opt/etc/ndm/netfilter.d/100-firewall.sh and verify firewall_health. Restore saved lists on reboot independently of source downloads.

--no-start stages files without starting services. Any affected previously running services are stopped and remain stopped; use the printed service instructions before using the installation. It is intended for maintenance, not normal interactive installation.

## Future updates directly from KeenTool

Use `keentool --check-updates` to check only. Use `keentool --update` (or menu option s/u) to check the latest published stable KeenTool release, show the installed/available suite version and request confirmation before download/install. For an explicitly unattended invocation use `keentool --update --yes`.

The updater accepts only the complete versioned suite archive and SHA-256 sidecar from mattheweli/KeenTool release assets. It excludes draft/prerelease releases, rejects downgrades, verifies the archive hash (and GitHub asset digest when present), validates archive paths/types, rejects links/special files, verifies every file against CHECKSUMS.sha256 and checks RELEASE.json against the selected release before invoking the transactional installer. No loose files are pulled from main. This trust chain uses GitHub HTTPS and repository ownership; checksums are not a separate publisher signature.

The suite version must advance for every coordinated published bundle, even when the manager component itself is unchanged. Component versions remain independent in the manifest. A same-version reinstall requires --reinstall explicitly; the standalone bootstrap uses this to seed an earlier locally prepared 2.0.0 build. It never permits a downgrade.

Existing public GitHub installations can use their normal Update KeenTool menu option. The historical updater downloads the new manager from main and restarts it. Before loading any shared library, the new manager detects a missing/incomplete suite runtime and starts its embedded, self-contained bootstrap. It offers the verified complete-suite migration and opens the normal menu only after installation succeeds. Checks and unattended invocations never install without explicit --yes. A failed, declined or unavailable migration leaves the entry usable for retry instead of sourcing missing libraries. The embedded verifier is generated from the same sources as bootstrap.sh; no second script from main is downloaded and executed.

Pinned alpha installations have online updates disabled locally. Run the reviewed standalone bootstrap.sh once (no manual package extraction is required), or install the complete package once. It detects the alpha version and uses the same verifier and transactional installer. Neither route offers draft/prerelease assets. Before a stable release exists, it reports this and leaves the suite, settings and databases untouched. A public legacy updater has already replaced the manager at this point; that older updater does not preserve the original manager bytes. The suite transaction backs up the retry-capable migration entry and all files it changes, while an alpha standalone migration backs up the original alpha manager. Do not describe the public legacy handoff as a byte-for-byte rollback of its already-replaced manager.

For first migration, use the manager update before individual component updates. Release maintainers must publish the reviewed complete suite asset before exposing the replacement manager on main. Otherwise legacy users can only retry after publication. After the first migration, all normal updates use published complete-suite releases, not individual main files.

The offline path remains: `keentool --update --local /absolute/path/to/extracted-release`. Existing external settings, credentials, databases and cron are preserved through both paths, with the same backup/rollback. Complex inline shell customizations require manual migration and are rejected before replacement. Physical-router reboot/rollback acceptance remains necessary; isolated tests do not establish every custom installation's compatibility.

## Firewall history in 2.0.1

The next scheduled firewall statistics run enables the default progressive 7/30-day policy after a verified baseline backup. Installation itself preserves the database. Configure it in KeenTool → Firewall → History aggregation settings, or authenticated Settings → Firewall history. Read [FIREWALL_HISTORY.md](FIREWALL_HISTORY.md) before restoring a baseline backup: later events are not in that initial copy, and changing thresholds does not recover aggregated time precision.

## Bootstrap dependency and menu repair changes in 2.0.2

Read [UPDATE_RECOVERY.md](UPDATE_RECOVERY.md) for interactive missing-dependency installation, read-only checks, explicit --install-deps, verified component repair and the one-time menu reopen needed when upgrading an already-running older menu. Existing firewall history settings and databases are preserved.

## Component overview and separate repair in 2.0.3

The main menu checks all five component versions together; a tool menu checks only that tool. Review component changes and coordinated runtime requirements before consenting to archive download. File verification/repair is explicit (--repair) and separate from version checks. See [UPDATE_RECOVERY.md](UPDATE_RECOVERY.md) for commands and compatibility.

## Component file verification in 2.0.4

Install / Update now checks all selected component source files and shared dependencies against the lightweight verified release overview before asking to download/apply the full package. A current declared version does not suppress missing or stale files. Dashboard has its own scope/version within the KeenTool repository. The global overview covers all six components and all 54 targets.

## Recovery backup choice (package 2.0.11+)

The installer asks whether to keep a recovery backup after a successful install. Choose Yes for a permanent manual-rollback copy, or No to remove verified temporary recovery copies when the transaction and service starts complete. Existing backups are not deleted. This is not a full NAS/database backup policy.

Use `install.sh --apply --keep-backup` or `install.sh --apply --no-backup`. For remote updates use `keentool --update --keep-backup` or `keentool --update --no-backup`; add `--yes` to accept an unattended update explicitly. Unattended runs without a backup flag keep recovery copies for compatibility. `--plan` and check-only operations never ask or create recovery copies.

No-backup mode uses a private durable directory under `/opt/var/lib/keentool-release/transactions` while installing. Automatic rollback remains available on errors/signals. Copies are removed after success or a completed automatic restore. If recovery fails or the process is killed without a catchable signal, keep that directory for manual recovery; do not delete it blindly. The updater forwards a resolved choice to its installer, so it is asked once. An installer launched by an older background updater can read the controlling terminal for the first choice.

## Administrator password during migration (package 2.0.12+)

After installation succeeds, an interactive SSH terminal is prompted to set and repeat a dedicated web admin password if no credential file exists. Use 12–72 bytes; input is hidden. This is independent of the router account and does not request a username. Legacy background updater launches can use the controlling terminal. An existing configured password is preserved; invalid existing credentials require explicit review/reset.

A noninteractive run does not invent credentials or read passwords from arguments/environment. It prints the command to complete setup: KeenTool option A or `/opt/bin/bash /opt/bin/firewall_admin_password`. EOF/failure/interrupted setup can be completed later; the successful source installation is retained and administrator access remains unavailable without valid credentials. No password step runs on a failed installation or plan-only check. Existing backup-retention choices are unchanged.

## Legacy HTTP-to-HTTPS conversion (package 2.0.13+)

An interactive install/upgrade detects a simple dedicated lighttpd HTTP listener and asks before enabling TLS on its existing port. For example, port 81 stays 81: open `https://<router-address>:81/` afterwards. PHP/FastCGI and included fragments are preserved. Existing TLS, isolated listeners, virtual hosts/multiple sockets and custom TLS settings are left for review. Noninteractive installs preserve the existing listener unless explicitly authorized with `--enable-https`.

Use `keentool --update --reinstall --enable-https` after installing the new updater, or `install.sh --apply --enable-https` for an extracted verified package. The old `--configure-web` option remains a separate explicit adoption of the dedicated 8080 configuration; these options cannot be combined. TLS conversion requires restart and cannot use `--no-start`. Plan/check mode makes no listener changes.

Before replacement, the installer stages a private candidate and checks it with lighttpd. After replacement/restart it checks local HTTPS with redirects disabled and a bounded timeout, bypassing configured proxies. A failed check triggers the existing verified rollback. Existing certificate files are preserved; a missing certificate is generated privately. Self-signed certificates need deliberate verification/trust in the browser. The local probe uses curl -k to check readiness, not certificate trust. The same installation backup-retention choice covers the listener change. Password setup follows a successful transaction.
