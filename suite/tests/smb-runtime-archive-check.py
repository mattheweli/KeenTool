"""Exercise real archive creation with a root-parent source and volatile exclusions."""
from pathlib import Path
import os, shutil, socket, sqlite3, subprocess, tarfile, tempfile
root = Path(__file__).resolve().parents[1]
source = (root/'projects/SMB_Backup_tool/Script/smb_backup_tool.sh').read_text()
functions = source[source.index('smb_safe_path()'):source.index('run_retention_check()')]
busybox = os.environ.get('KT_TEST_BUSYBOX') or shutil.which('busybox')
variants = ['tar']
if busybox:
 help_text = subprocess.run([busybox, 'tar', '--help'], capture_output=True, text=True).stderr
 if '-X' in help_text: variants.append('busybox')
 elif os.environ.get('KT_TEST_BUSYBOX'): raise AssertionError('Required BusyBox lacks tar -X support')
 else: print('NOTE: system BusyBox lacks tar -X; full-feature BusyBox is required for this variant.')
for variant in variants:
 with tempfile.TemporaryDirectory(prefix='kt-smb-source-', dir='/') as src, tempfile.TemporaryDirectory() as work:
  b, w = Path(src), Path(work)
  for d in ['etc', 'var/log/keentool-firewall', 'var/run/keentool-security', 'var/lock', 'tmp', 'backup_storage', 'data']:
   (b/d).mkdir(parents=True, exist_ok=True)
  (b/'etc/settings').write_text('important configuration')
  (b/'data/binary.db').write_bytes(b'\0'*40+b'not sqlite')
  (b/'var/log/keentool-firewall/fw_syn_ring.pcap').write_bytes(b'capture'*1024)
  (b/'var/run/keentool-security/state').write_text('ephemeral')
  (b/'var/lock/service.lock').write_text('lock')
  (b/'backup_storage/old.tar').write_bytes(b'old archive')
  db = sqlite3.connect(b/'data/live.db')
  db.execute('create table events (id integer, value text)')
  db.execute("insert into events values (7, 'preserve me')"); db.commit(); db.close()
  sockets = []
  try:
   for p in [b/'var/run/keentool-security/broker.sock', b/'data/application.sock']:
    s = socket.socket(socket.AF_UNIX); s.bind(str(p)); sockets.append(s)
  except PermissionError:
   if os.environ.get('GITHUB_ACTIONS') == 'true': raise
   print('NOTE: socket creation unavailable locally; CI exercises real Unix sockets.')
  bindir = w/'bin'; bindir.mkdir()
  # Real SQLite engine through Python, independent of the host CLI installation.
  shim = bindir/'sqlite3'
  shim.write_text('''#!/usr/bin/env python3
import sqlite3,sys
c=sqlite3.connect(sys.argv[-2]); q=sys.argv[-1]
if q.startswith(".backup "):
 d=sqlite3.connect(q[8:].strip("'"));c.backup(d);d.close()
else:
 for row in c.execute(q):print('|'.join(str(x) for x in row))
c.close()
'''); shim.chmod(0o755)
  if variant == 'busybox':
   tar = bindir/'tar'; tar.write_text('#!/bin/sh\nexec '+busybox+' tar "$@"\n');tar.chmod(0o755)
  code = '. "'+str(root/'support/common.sh')+'"\n'+functions.replace('/opt',src)+r'''
logger_msg(){ printf '%s\n' "$*" >> "$WORK/log"; }
dump_system_files(){ mkdir -p "$TEMP_DIR/sys_dump";printf 'router configuration\n' > "$TEMP_DIR/sys_dump/running-config.txt"; }
smb_run(){
 printf '%s\n' "$1" >> "$WORK/events"
 if [[ "$1" = *'put MANIFEST.sha256'* ]]; then cp "$TEMP_DIR"/*.tar.gz "$WORK/"; fi
 if [[ "$1" =~ get[[:space:]]\"([^\"]+)\"[[:space:]]\"([^\"]+)\" ]];then cp "$TEMP_DIR/${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}";fi
}
CONFIG_STATUS=OK;SOURCE_DIR="$SOURCE/";SMB_SUBDIR=backups;SMB_SHARE=backup;SMB_HOST=fixture;SMB_USER=fixture;SMB_PASS=fixture;RETENTION_DAYS=30;AUTO_PURGE=false;LOG_FILE="$WORK/log";TEMP_DIR=''
perform_backup
'''
  env = dict(os.environ, SOURCE=src, WORK=work, KT_RUN_DIR=work, PATH=str(bindir)+':'+os.environ['PATH'])
  r = subprocess.run(['bash','-c',code],env=env,text=True,capture_output=True)
  assert r.returncode == 0, r.stdout+r.stderr
  assert 'ignored null byte' not in r.stderr and 'socket ignored' not in r.stderr and 'file changed' not in r.stderr, r.stderr
  with tarfile.open(next(w.glob('opt_backup_*.tar.gz'))) as tar:
   names = tar.getnames(); prefix = b.name+'/'
   assert prefix+'etc/settings' in names and prefix+'data/binary.db' in names, names
   for excluded in ['var/log', 'var/run', 'var/lock', 'tmp', 'backup_storage', 'data/live.db', 'data/application.sock']:
    assert not any(n == prefix+excluded or n.startswith(prefix+excluded+'/') for n in names), (excluded,names)
  with tarfile.open(next(w.glob('sqlite_backup_*.tar.gz'))) as tar:
   member = tar.getmember('./'+b.name+'/data/live.db')
   snap = w/'snapshot.db';snap.write_bytes(tar.extractfile(member).read())
   c = sqlite3.connect(snap);assert c.execute('select * from events').fetchall() == [(7,'preserve me')];c.close()
  assert 'rename' in (w/'events').read_text()
  for failure in ['tar', 'find']:
   (w/'events').unlink(missing_ok=True)
   injected = ('tar(){ if [ "$1" = -X ];then return 2;fi;command tar "$@"; }\n' if failure == 'tar' else 'find(){ return 1; }\n')
   failed = subprocess.run(['bash','-c',code.replace('perform_backup\n', injected+'perform_backup\n')],env=env,text=True,capture_output=True)
   assert failed.returncode != 0, (failure,failed.stdout,failed.stderr)
   assert not (w/'events').exists(), 'Upload attempted after '+failure+' failure'
  for s in sockets:s.close()
  print('PASS: '+variant+' root-parent/trailing-slash archive excludes runtime/logs/sockets, retains config/binary files and coherent SQLite records; SMB transport/router export mocked.')
