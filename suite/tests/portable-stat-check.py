"""Verify production metadata fallback with a stat implementation lacking -c."""
from pathlib import Path
import tempfile,subprocess,os
root=Path(__file__).resolve().parents[1]
php='/tmp/keentool-security-runtime/root/usr/bin/php8.3'
with tempfile.TemporaryDirectory() as td:
 p=Path(td);bad=p/'stat';bad.write_text('#!/bin/bash\nexit 1\n');bad.chmod(0o755);f=p/'log file';f.write_text('hello metadata')
 wrapper=p/'php-cli';wrapper.write_text('#!/bin/bash\nexec '+php+' -n "$@"\n');wrapper.chmod(0o755)
 env=dict(os.environ,PATH=td+':'+os.environ['PATH'],KT_PHP_CLI=str(wrapper));meta=f.stat()
 for fmt,expected in [('%s',meta.st_size),('%i',meta.st_ino),('%Y',int(meta.st_mtime)),('%d:%i',str(meta.st_dev)+':'+str(meta.st_ino))]:
  r=subprocess.run(['bash','-c','. "$1";kt_stat "$2" "$3"','fixture',str(root/'support/common.sh'),fmt,str(f)],env=env,text=True,capture_output=True)
  assert r.returncode==0 and r.stdout.strip()==str(expected),r.stderr+r.stdout
print('PASS: BusyBox stat without -c falls back to PHP core for size, inode, mtime and device/inode identity, including paths with spaces.')
