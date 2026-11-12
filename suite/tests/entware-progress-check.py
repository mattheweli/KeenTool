"""Exercise the real detached launcher and live viewer with isolated fake services/opkg."""
from pathlib import Path
import os, pty, signal, subprocess, tempfile, threading, time

root = Path(__file__).resolve().parents[1]
source = (root / 'support/entware_manager').read_text()

def wait_for(predicate, message, seconds=15):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        if predicate():
            return
        time.sleep(.05)
    raise AssertionError(message)

with tempfile.TemporaryDirectory() as td:
    b = Path(td)
    script = b / 'entware_manager'
    # Only relocate the router's Bash interpreter; execute the real launcher/viewer/worker.
    script.write_text(source.replace('/opt/bin/bash', '/bin/bash'))
    script.chmod(0o755)
    init = b / 'init'; init.mkdir()
    service = init / 'S10fixture'
    service.write_text('#!/bin/bash\nprintf "%s\\n" "$1" >> "$FIXTURE/services"\n')
    service.chmod(0o755)
    opkg = b / 'opkg'
    opkg.write_text('''#!/usr/bin/env python3
import os, sys, time
from pathlib import Path
b=Path(os.environ['FIXTURE']);args=sys.argv[1:]
if args==['--help']:print('--download-only');sys.exit(0)
if args==['update']:
 print('Refreshing fixture index',flush=True)
 time.sleep(.3)
 sys.exit(7 if (b/'fail-index').exists() else 0)
if args==['list-upgradable']:print('fixture - 1 - 2');sys.exit(0)
if args==['list-installed']:print('fixture - 2');sys.exit(0)
if '--download-only' in args:print('Downloading fixture package',flush=True);sys.exit(0)
if 'upgrade' in args:
 print('Installing fixture package: live output',flush=True)
 (b/'installing').touch()
 end=time.monotonic()+20
 while not (b/'finish').exists() and time.monotonic()<end:time.sleep(.05)
 print('Package installation finished',flush=True)
 sys.exit(2 if (b/'fail-upgrade').exists() else 0)
sys.exit(9)
''')
    opkg.chmod(0o755)
    env = dict(os.environ, FIXTURE=td, KT_ENTWARE_TEST='true', KT_ENTWARE_STATE=str(b/'state'),
               KT_ENTWARE_RUNS=str(b/'runs'), KT_ENTWARE_LOCK=str(b/'lock'),
               KT_ENTWARE_MAINT=str(b/'maintenance'), KT_ENTWARE_INIT=str(init),
               KT_ENTWARE_OPKG=str(opkg), KT_ENTWARE_EMAIL=str(b/'no-email'))
    def run(*args):
        return subprocess.run(['bash',str(script),*args],env=env,text=True,capture_output=True,timeout=10)
    # opkg update stdout is visible even while the command is still executing.
    (b/'fail-index').touch()
    failed=run('--check')
    assert failed.returncode==1 and failed.stdout.count('Refreshing fixture index')==1,failed.stdout+failed.stderr
    assert 'Index update failed' in failed.stdout
    assert 'Refreshing fixture index' in (b/'state/update.log').read_text()
    (b/'fail-index').unlink()
    master,slave=pty.openpty()
    lines=[]
    launcher=subprocess.Popen(['bash',str(script),'--upgrade'],env=env,stdin=slave,
                              stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,start_new_session=True)
    os.close(slave)
    reader=threading.Thread(target=lambda: lines.extend(iter(launcher.stdout.readline,'')),daemon=True)
    reader.start()
    worker_pid=None
    try:
        os.write(master,b'UPGRADE\n')
        wait_for(lambda:(b/'installing').exists(),'detached worker did not reach installation')
        latest=Path((b/'state/latest-run').read_text().strip())
        worker_pid=int((latest/'pid').read_text())
        assert os.getpgid(worker_pid)!=os.getpgid(launcher.pid)
        wait_for(lambda:any('Installing fixture package: live output' in l for l in lines),'no live output before worker completion')
        assert not (latest/'worker-exit-code').exists()
        assert 'Worker running' in run('--status').stdout
        # Ctrl+C as a terminal process-group signal must not cancel the detached upgrade.
        os.killpg(launcher.pid,signal.SIGINT)
        launcher.wait(timeout=8);reader.join(timeout=2)
        os.kill(worker_pid,0)
        assert not (latest/'worker-exit-code').exists()
        os.killpg(os.getpgid(worker_pid),signal.SIGHUP)
        time.sleep(.1)
        assert (latest/'status').read_text().strip()=='upgrading'
        (b/'finish').touch()
        
        try:wait_for(lambda:(latest/'worker-exit-code').exists(),'worker did not survive view interruption')
        except AssertionError:
            print('VIEW:', ''.join(lines));print('LOG:',(latest/'upgrade.log').read_text());print('STATUS:',(latest/'status').read_text());raise
        assert (latest/'worker-exit-code').read_text().strip()=='0'
        assert (b/'services').read_text().splitlines()==['stop','start']
        replay=run('--follow')
        assert replay.returncode==0 and replay.stdout.count('Installing fixture package: live output')==1,replay.stdout+replay.stderr
        assert 'Upgrade status: completed (worker exit 0)' in replay.stdout
        assert not (b/'maintenance').exists()
        # The viewer reports the actual worker error, including a final partial log line.
        (latest/'worker-exit-code').write_text('2\n')
        (latest/'status').write_text('upgrade-errors (opkg exit 2; services restarted)\n')
        with (latest/'upgrade.log').open('a') as f:f.write('Final partial diagnostic')
        replay=run('--follow')
        assert replay.returncode==2 and replay.stdout.count('Final partial diagnostic')==1,replay.stdout+replay.stderr
        (latest/'worker-exit-code').unlink()
        (latest/'pid').write_text('999999999\n')
        assert 'Worker is no longer running' in run('--follow').stdout
    finally:
        (b/'finish').touch()
        if launcher.poll() is None:
            launcher.terminate();launcher.wait(timeout=5)
        os.close(master)
print('PASS: live index output with failure propagation, real detached interactive launch, progress before completion, terminal Ctrl+C preserves worker/service restart, reconnect replay, worker exit status, partial lines and dead-worker detection; all router services/opkg mocked.')
