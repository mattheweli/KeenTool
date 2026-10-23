# Security and known limitations

Administrator writes require HTTPS, the configured password, a current boot-bound session and CSRF. Credentials and sessions reside outside the web root. Public status/log reads go through an allowlisted broker; the original syslog permissions are retained. The password command accepts no username. Existing users and passwords are not replaced during installation.

After initial setup, review and apply firewall_security harden-web to use the dedicated ktweb account and root command broker. The installer preserves an existing isolated listener; a newly adopted listener initially uses the default lighttpd/FastCGI process privileges until this reviewed migration. Do not expose administrator endpoints to the Internet before verifying TLS, privilege separation and management access.

Filtering uses owned chains, dual-family preflight, checked apply/recovery, bounded NFLOG and independently preserved DROP decisions. Source lists are validated and staged before swap; empty/incomplete candidates retain the installed list. GeoIP size changes are advisory and do not disable the download validation rules. Guarded Settings changes have a confirmation timeout.

Known upstream feed limitation: the configured IPdeny IPv6 KP endpoint may return HTTP 404. A missing source with no cache rejects the complete GeoBlock6 candidate and retains the installed list. Cached source data can be older than its installation timestamp. The email and health page report the cause and recorded attempt/success times; the package does not silently exclude a country. IPv4 HTTP/2 curl errors can also trigger cache fallback. This release documents these cases; it does not claim they are resolved.

Never attach router credentials, databases, address lists or raw private logs to a public issue. This source package contains no router configuration or credential exports. Tests use temporary fixtures and mocked delivery; they do not send mail.
