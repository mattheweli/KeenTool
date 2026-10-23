# Backup and rollback

The installer verifies package checksums and syntax before replacement. It refuses symlink destinations/parents, conflicting jobs, concurrent installation and pending firewall policy changes. Files are replaced atomically on their destination filesystem.

Each apply creates /opt/var/backups/keentool-release/TIMESTAMP-PID-RANDOM. The backup contains transaction.json, INSTALL.tsv, checksums.json, rollback.sh, the rollback engine and copies of every existing file/configuration it will replace. Contents, file modes, uid and gid are recorded. New files and created parent directories are recorded separately. Backups are private.

```sh
/opt/bin/bash /opt/var/backups/keentool-release/PRINTED-DIRECTORY/rollback.sh /opt/var/backups/keentool-release/PRINTED-DIRECTORY
```

Backup hashes are checked before restoration or service stops. Rollback stops package daemons and affected newly started web/logging services, restores previous files/ownership/modes and removes newly installed files. Previously running web/logging/package services are restarted. Existing databases and samples are retained: installation does not normalize, vacuum, prune, rewrite or restore them. New history collected after installation is not deleted by rollback. Existing legacy alpha helper directories are retained for compatibility with restored alpha scripts.

A failure during apply or service startup triggers the same file rollback automatically. Package-manager changes, router kernel state, generated history and manually configured services are outside this transaction. Installation does not apply firewall rules. If you later apply a new hook/configuration, use its guarded rollback separately before restoring an older package. Do not roll back while monitor jobs are active. If a restore reports an error, retain the backup and fix that error before restarting affected services.

The uninstaller remains selective and preserves databases/configuration unless --purge-data is explicitly supplied. Read its plan first. Its separate backup includes coherent SQLite copies; restoration instructions are stored with that archive. Do not use an old web-isolation backup with an incomplete permission ledger.
