"""Reproduce lost BusyBox links and opkg abort without touching the host router paths."""
from pathlib import Path
import os,subprocess,tempfile,hashlib,shutil,json
root=Path(__file__).resolve().parents[1]
source=(root/'support/entware_manager').read_text()
assert '/opt/usr/bin:/opt/usr/sbin' in source
with tempfile.TemporaryDirectory() as td:
 b=Path(td);prefix=b/'opt';(prefix/'bin').mkdir(parents=True);(prefix/'share').mkdir()
 bb=prefix/'bin/busybox'
 real=os.environ.get('KT_TEST_BUSYBOX') or shutil.which('busybox')
 if real:shutil.copy2(real,bb)
 else:
  # Local adapter only; the stable-release CI repeats this with pinned BusyBox 1.37.
  bb.write_text('''#!/usr/bin/python3
import os,sys,shutil
apps=['sh','mkdir','rm','readlink','wc','sleep','pidof','dirname','cat','date','ln','cp']
cmd=sys.argv[1] if os.path.basename(sys.argv[0])=='busybox' else os.path.basename(sys.argv[0])
args=sys.argv[2:] if os.path.basename(sys.argv[0])=='busybox' else sys.argv[1:]
if cmd=='--list':print('\\n'.join(apps));sys.exit(0)
target=next((p+'/'+cmd for p in ['/bin','/usr/bin','/sbin','/usr/sbin'] if os.path.isfile(p+'/'+cmd)),None)
if target is None:sys.exit(127)
os.execv(target,[cmd]+args)
''');bb.chmod(0o755)
 (prefix/'share/busybox_applets.lst.dist').write_text('bin/sh\nbin/mkdir\nbin/rm\n')
 for name in ['sh','mkdir','rm']:(prefix/'bin'/name).symlink_to(bb)
 init=b/'init';init.mkdir();service=init/'S10fixture';service.write_text('#!/bin/bash\necho "$1" >> "$FIXTURE/services"\n');service.chmod(0o755)
 opkg=b/'opkg';opkg.write_text('''#!/usr/bin/python3
from pathlib import Path
import os,sys,subprocess
b=Path(os.environ['FIXTURE']);args=sys.argv[1:]
if args==['--help']:print('--download-only');sys.exit(0)
if args==['list-upgradable']:print('first - 1 - 2\\nsecond - 1 - 2');sys.exit(0)
if args==['list-installed']:print('first - 2');sys.exit(0)
if '--download-only' in args:sys.exit(0)
pkg=args[-1]
with (b/'attempts').open('a') as f:f.write(pkg+'\\n')
assert os.environ['PATH'].split(':')[0].endswith('/rescue/bin')
for name in ['sh','mkdir','rm']:(b/'opt/bin'/name).unlink(missing_ok=True)
# Commands remain executable for opkg children while the installed links are absent.
subprocess.run(['sh','-c','mkdir -p "$FIXTURE/from-rescue"'],check=True)
sys.exit(134 if (b/'fail').exists() else 0)
''');opkg.chmod(0o755)
 env=dict(os.environ,FIXTURE=td,KT_ENTWARE_TEST='true',KT_ENTWARE_STATE=str(b/'state'),KT_ENTWARE_RUNS=str(b/'runs'),KT_ENTWARE_LOCK=str(b/'lock'),KT_ENTWARE_MAINT=str(b/'maintenance'),KT_ENTWARE_INIT=str(init),KT_ENTWARE_OPKG=str(opkg),KT_ENTWARE_EMAIL=str(b/'no-email'),KT_ENTWARE_BUSYBOX=str(bb),KT_ENTWARE_PREFIX=str(prefix))
 digest=hashlib.sha256(b'first - 1 - 2\nsecond - 1 - 2\n').hexdigest()
 def invoke(*args):return subprocess.run(['bash',str(root/'support/entware_manager'),*args],env=env,text=True,capture_output=True,timeout=20)
 for failing in [True,False]:
  if failing:(b/'fail').touch()
  else:(b/'fail').unlink();(b/'services').unlink();(b/'attempts').unlink()
  run=b/('failed-run' if failing else 'good-run');run.mkdir()
  r=invoke('--worker',str(run),digest)
  assert r.returncode==(134 if failing else 0),r.stdout+r.stderr
  assert (b/'services').read_text().splitlines()==['stop','start']
  assert (b/'attempts').read_text().splitlines()==(['first'] if failing else ['first','second'])
  assert (prefix/'bin/sh').exists() and (prefix/'bin/mkdir').exists() and (prefix/'bin/rm').exists()
  assert (b/'from-rescue').is_dir() and not (b/'maintenance').exists()
  assert (run/'opkg-exit-code').read_text().strip()==str(r.returncode)
  assert (run/'worker-exit-code').read_text().strip()==str(r.returncode)
  assert 'Independent BusyBox recovery runtime ready' in r.stdout
  assert 'Restored missing runtime link' in r.stdout
  assert 'upgrade-errors' in (run/'status').read_text() if failing else (run/'status').read_text().strip()=='completed'
 # Resume preserves the opkg failure record while updating service recovery status.
 run=b/'failed-run';(b/'state/latest-run').write_text(str(run)+'\n');(run/'pid').write_text('999999999\n')
 r=invoke('--resume');assert r.returncode==0,r.stdout+r.stderr
 assert 'services-recovered' in (run/'status').read_text()
 assert (run/'opkg-exit-code').read_text().strip()=='134'
 # A missing manifest must abort before any stop/install.
 before=(b/'services').read_text();(prefix/'share/busybox_applets.lst.dist').unlink()
 run=b/'bad-runtime';run.mkdir();r=invoke('--worker',str(run),digest)
 assert r.returncode!=0 and (b/'services').read_text()==before
 assert (run/'status').read_text().strip()=='runtime-preflight-failed'
print('PASS: complete Entware PATH; private runtime survives missing sh/mkdir/rm, per-package failure 134 stops the batch, links recover before service restart, all packages run on success, resume retains package failure separately. BusyBox backend: '+('real' if real else 'local adapter; pinned BusyBox checked in release CI'))
