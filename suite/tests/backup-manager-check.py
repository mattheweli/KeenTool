"""Run the real backup inventory and deletion paths against disposable backups."""
import os
from pathlib import Path
import pty
import subprocess
import tempfile
import time

script = Path(__file__).resolve().parents[1] / 'support/backup_manager'
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    state = root / 'opt/etc/keentool'
    entware_state = state / 'entware'
    entware_state.mkdir(parents=True)
    (root / 'opt/tmp').mkdir()
    (root / 'tmp').mkdir()
    base = root / 'opt/var/backups'
    env = dict(os.environ, KT_BACKUP_ROOT=td)

    def run(*args):
        return subprocess.run(['bash', script, *args], env=env, text=True,
                              capture_output=True, timeout=10)

    def backup(group, name, days, status='completed'):
        p = base / ('keentool-' + group) / name
        p.mkdir(parents=True)
        if group == 'entware':
            (p / 'status').write_text(status + '\n')
            (p / 'worker-exit-code').write_text('0\n' if status == 'completed' else '1\n')
        if group == 'release':
            (p / 'transaction.json').write_text('{}')
            (p / 'rollback.sh').write_text('# fixture')
        t = time.time() - (days * 86400 + 90)
        os.utime(p, (t, t))
        return p

    old = backup('entware', '20260901_030000-10', 50)
    retained = backup('entware', '20260902_030000-10', 49)
    valid_newest = backup('entware', '20260903_030000-10', 48)
    failed = backup('entware', '20260904_030000-10', 47, 'restart-failed')
    (entware_state / 'latest-run').write_text(str(retained) + '\n')
    release_old = backup('release', '20260901_040000-10-000001', 50)
    release_new = backup('release', '20260902_040000-10-000001', 49)
    release_fresh = backup('release', '20261101_040000-10-000001', 1)
    db = backup('db', 'history-20260901_050000-000001000001', 50)
    unknown = backup('release', 'not-a-managed-backup', 60)
    external = root / 'external'
    external.mkdir()
    (external / 'keep').touch()
    (old / 'link').symlink_to(external)
    t = time.time() - (50 * 86400 + 90)
    os.utime(old, (t, t))
    alias = old.parent / '20260901_030000-11'
    alias.symlink_to(external)
    assert run('--auto').returncode == 0 and old.exists()
    assert run('--set-retention', '30').returncode == 0
    assert run('--set-retention', 'abc').returncode != 0
    plan = run('--preview').stdout
    assert old.name in plan and release_old.name in plan and release_new.name in plan
    assert all(p.name not in plan for p in [retained, failed, valid_newest, release_fresh, db, alias, unknown])
    assert db.name in run('--list').stdout
    assert run('--delete', 'release/../outside').returncode != 0
    assert run('--delete', 'release/' + release_old.name).returncode != 0  # no terminal
    assert run('--set-retention', '0').returncode == 0
    assert run('--auto').returncode == 0 and old.exists()
    assert run('--set-retention', '30').returncode == 0
    (state / 'firewall-upgrade.pending').touch()
    assert run('--auto').returncode == 75 and old.exists()
    (state / 'firewall-upgrade.pending').unlink()
    lock = root / 'tmp/keentool-entware.lockdir'
    lock.mkdir()
    assert run('--auto').returncode == 75 and old.exists()
    lock.rmdir()

    def manual(command, inputs):
        master, slave = pty.openpty()
        try:
            with subprocess.Popen(['bash', script, command], env=env, stdin=slave,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc:
                os.write(master, inputs.encode())
                output, _ = proc.communicate(timeout=10)
                return proc.returncode, output
        finally:
            os.close(master)
            os.close(slave)

    web = backup('web', 'active-web-config', 70)
    (state / 'security').mkdir()
    (state / 'security/web-hardened').write_text(str(web) + '\n')
    unknown_file = unknown.parent / 'unknown file.tar.gz'
    unknown_file.touch()

    def entry_id(path):
        group = path.parent.name.removeprefix('keentool-')
        listing = run('--list').stdout
        return next(line.split()[0] for line in listing.splitlines()
                    if f'{group}/{path.name}' in line)

    assert run('--delete-all').returncode != 0
    assert manual('--delete', '99999\nDELETE\n')[0] != 0
    assert manual('--delete', entry_id(release_old) + '\ncancel\n')[0] == 0 and release_old.exists()
    assert manual('--delete', entry_id(release_old) + '\nDELETE\n')[0] == 0 and not release_old.exists()
    assert manual('--delete', entry_id(failed) + '\nDELETE\n')[0] == 0 and not failed.exists()
    assert manual('--delete', entry_id(unknown) + '\nDELETE\n')[0] == 0 and not unknown.exists()
    assert manual('--delete-all', 'cancel\n')[0] == 0 and old.exists()
    result = run('--auto')
    assert result.returncode == 0, result.stdout + result.stderr
    assert not old.exists() and not release_new.exists()
    assert all(p.exists() for p in [retained, valid_newest, release_fresh, db, alias, web, unknown_file, external / 'keep'])
    (state / 'firewall-upgrade.pending').touch()
    assert manual('--delete-all', 'DELETE ALL\n')[0] == 75 and retained.exists()
    (state / 'firewall-upgrade.pending').unlink()
    rc, output = manual('--delete-all', 'DELETE ALL\n')
    assert rc == 1 and 'Active web rollback copy' in output, output
    assert all(not p.exists() for p in [retained, valid_newest, release_fresh, db, unknown_file])
    assert all(p.exists() for p in [alias, web, external / 'keep'])
    assert not (entware_state / 'latest-run').exists()
    assert not lock.exists() and not (root / 'opt/tmp/keentool-install.lockdir').exists()
print('PASS: numeric selection, confirmation, manual cleanup of unrecognized and incomplete backups, bulk deletion and recovery protections. Automatic retention is unchanged.')
