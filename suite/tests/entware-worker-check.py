from pathlib import Path
import subprocess,tempfile,os,json,hashlib
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as td:
 b=Path(td);init=b/'init';init.mkdir();state=b/'state';opkg=b/'opkg';events=b/'events';packages=b/'packages';packages.write_text('testpkg - 1.0 - 2.0\n');email=b/'email'
 opkg.write_text('''#!/usr/bin/env python3
import os,sys
from pathlib import Path
b=Path(os.environ['FIXTURE']);args=sys.argv[1:]
if args==['--help']:print('--download-only');sys.exit(0)
if args[0]=='list-upgradable':print((b/'packages').read_text(),end='');sys.exit(0)
if args[0]=='list-installed':print('testpkg - 2.0');sys.exit(0)
if args[0]=='update':sys.exit(1 if (b/'fail-index').exists() else 0)
with (b/'events').open('a') as f:f.write(('download' if '--download-only' in args else 'upgrade')+'\\n')
if 'upgrade' in args and '--download-only' not in args:sys.exit(2 if (b/'fail-upgrade').exists() else 0)
''');opkg.chmod(0o755)
 email.write_text('#!/usr/bin/env python3\nimport os,sys,json\nfrom pathlib import Path\nwith (Path(os.environ["FIXTURE"])/"emails").open("a") as f:f.write(json.dumps(sys.argv[1:])+"\\n")\n');email.chmod(0o755)
 for n in ['S10first','S20second']:
  f=init/n;f.write_text('#!/bin/bash\nprintf "'+n+' %s\\n" "$1" >> "$FIXTURE/events"\n');f.chmod(0o755)
 env=dict(os.environ,FIXTURE=td,KT_ENTWARE_TEST='true',KT_ENTWARE_STATE=str(state),KT_ENTWARE_RUNS=str(b/'runs'),KT_ENTWARE_LOCK=str(b/'lock'),KT_ENTWARE_MAINT=str(b/'maintenance'),KT_ENTWARE_INIT=str(init),KT_ENTWARE_OPKG=str(opkg),KT_ENTWARE_EMAIL=str(email))
 def run(*args):return subprocess.run(['bash',str(root/'support/entware_manager'),*args],env=env,text=True,capture_output=True)
 r=run('--check','--notify');assert r.returncode==0,r.stderr;assert len((b/'emails').read_text().splitlines())==1
 run('--check','--notify');assert len((b/'emails').read_text().splitlines())==1
 before=(state/'available.txt').read_bytes();(b/'fail-index').touch();assert run('--check').returncode!=0 and (state/'available.txt').read_bytes()==before;(b/'fail-index').unlink()
 digest=hashlib.sha256(before).hexdigest();rundir=b/'run';rundir.mkdir()
 r=run('--worker',str(rundir),digest);assert r.returncode==0,r.stdout+r.stderr
 assert events.read_text().splitlines()==['download','S20second stop','S10first stop','upgrade','S10first start','S20second start']
 assert (rundir/'status').read_text().strip()=='completed' and not (b/'maintenance').exists()
 events.unlink();(b/'fail-upgrade').touch();r=run('--worker',str(rundir),digest);assert r.returncode==2,r.stdout+r.stderr
 assert events.read_text().splitlines()[-2:]==['S10first start','S20second start'] and not (b/'maintenance').exists()
print('PASS: actual Entware manager check/dedup, failed index retains list, predownload before reverse stop, ascending restart, upgrade failure returns nonzero and restarts services; all opkg/SMTP/services mocked.')
