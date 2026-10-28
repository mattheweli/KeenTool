# KeenTool coordinated package 2.0.13

## KeenTool manager 2.0.10 / coordinated package 2.0.13 — 2026-10-28

- Detect a simple existing HTTP-only lighttpd listener during installation, including Legacy upgrades, and offer an explicit HTTPS conversion before administrator password setup. Keep the existing port (including 81), document root, FastCGI/PHP settings and included fragments. An existing enabled TLS configuration is preserved.
- Add `--enable-https` to installer/updater/bootstrap. Interactive installs ask for consent; noninteractive installs preserve HTTP unless this option is explicit and print a completion command. Check/plan operations never modify the listener. Existing isolated, conditional/multiple-socket, alternative-root and custom TLS configurations require review rather than a guessed conversion.
- Reuse verified installation recovery copies for the web conversion. Stage a private certificate and test a candidate configuration before replacing live files. Validate the installed configuration, restart the existing lighttpd service and require a real local HTTPS handshake/HTTP response. Failed validation, startup or probing restores the previous package/listener through the normal transaction rollback; retained-backup choices are unchanged.
- Reuse an existing certificate; create a private self-signed certificate only if absent. Report the existing HTTPS port and explain certificate verification/trust. Curl's insecure flag is limited to the local readiness probe; it does not establish certificate trust. Passwords, database contents, cron and firewall policy are unchanged.
- Add native lighttpd/OpenSSL local TLS validation in CI, plus transaction fixtures for port preservation, unchanged PHP/configuration/credentials, current TLS, consent from legacy background terminals, preflight errors, failed handshake rollback and custom configuration refusal. Router reboot and every custom server layout remain outside isolated validation.

Manager 2.0.10 changes because its embedded update/bootstrap supports the new explicit option. Installer 1.0.5, updater/bootstrap 1.0.6 and transaction engine 1.0.3 carry the implementation. All other component versions remain unchanged.

## Update

Use KeenTool → u and approve HTTPS conversion if a simple HTTP-only listener is detected. Keep the existing port: an HTTP dashboard on port 81 becomes `https://<router-address>:81/`. Verify/trust the certificate before administrator login. Existing HTTPS listeners and passwords are preserved.

After installing the new updater, explicit configuration is also available with `keentool --update --reinstall --enable-https`. Add `--yes --keep-backup` or `--yes --no-backup` only when an unattended installation is intended. Older updater versions do not recognize the new flag: update through u first. Complex configurations receive a manual-review diagnostic without automatic listener changes.
