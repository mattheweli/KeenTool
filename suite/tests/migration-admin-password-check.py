"""Exercise real hidden password setup and preservation in isolated router roots."""
from pathlib import Path
import tempfile,subprocess,os,pty,select,time,shutil,json
suite=Path(__file__).resolve().parents[1];php='/tmp/keentool-security-runtime/root/usr/bin/php8.3'
with tempfile.TemporaryDirectory() as td:
 root=Path(td);binary=root/'opt/bin';binary.mkdir(parents=True);lib=root/'opt/lib/keentool-admin';lib.mkdir(parents=True)
 shutil.copy(suite/'support/set_password.php',lib/'set_password.php')
 wrapper=binary/'php-cli';wrapper.write_text('#!/bin/bash\nexec '+php+' -n "$@"\n');wrapper.chmod(0o755)
 helper=suite/'support/firewall_admin_password';env=dict(os.environ,KT_INSTALL_ROOT=str(root),KT_PHP_CLI=str(wrapper));credentials=root/'opt/etc/keentool/admin/credentials.json'
 def call(*args,secret=None):return subprocess.run(['bash',str(helper),*args],env=env,capture_output=True,text=True,input=secret)
 r=call('--setup-if-missing');assert r.returncode==0 and 'interactive SSH terminal' in r.stderr and not credentials.exists(),r.stdout+r.stderr
 def terminal(answers,background=False,setup=True):
  pid,fd=pty.fork()
  if pid==0:
   os.environ.update(env)
   args=['--setup-if-missing'] if setup else []
   if background:os.execvp('bash',['bash','-c','bash "$1" --setup-if-missing </dev/null & child=$!;wait "$child"','legacy',str(helper)])
   os.execvp('bash',['bash',str(helper),*args])
  output=b'';seen=0;pending=b'';deadline=time.monotonic()+15
  try:
   while time.monotonic()<deadline:
    ready,_,_=select.select([fd],[],[],0.1)
    if not ready:continue
    try:chunk=os.read(fd,4096)
    except OSError:break
    if not chunk:break
    output+=chunk;pending+=chunk
    if (b'Admin password (12-72 bytes): ' in pending or b'Repeat password: ' in pending) and seen<len(answers):
     os.write(fd,answers[seen].encode());seen+=1;pending=b''
   else:os.kill(pid,9);raise AssertionError('Password prompt timed out')
  finally:os.close(fd)
  _,status=os.waitpid(pid,0);return os.waitstatus_to_exitcode(status),output.decode()
 secret='fixture-only-admin-2026'
 rc,out=terminal(['short\n','short\n','fixture-mismatch-1\n','fixture-mismatch-2\n',secret+'\n',secret+'\n'],background=True)
 assert rc==0 and 'Password must contain' in out and 'Passwords differ' in out and 'Admin password configured' in out,out
 assert secret not in out and 'fixture-mismatch' not in out and 'short' not in out,out
 saved=credentials.read_bytes();data=json.loads(saved);assert data['hash']!=secret and len(data['revision'])==64
 assert credentials.stat().st_mode&0o777==0o600
 r=subprocess.run([php,'-n','-r','$c=json_decode(file_get_contents($argv[1]),true);exit(password_verify(stream_get_contents(STDIN),$c["hash"])?0:1);',str(credentials)],input=secret,capture_output=True,text=True);assert r.returncode==0,r.stderr
 r=call('--setup-if-missing');assert r.returncode==0 and 'already configured' in r.stdout and credentials.read_bytes()==saved,r.stdout+r.stderr
 # A concurrent/manual setup cannot be overwritten by an automatic setup writer.
 r=subprocess.run([php,'-n',str(lib/'set_password.php'),'--if-missing'],input='different-fixture-password',env=env,capture_output=True,text=True)
 assert r.returncode==0 and 'preserved' in r.stdout and credentials.read_bytes()==saved,r.stdout+r.stderr
 # Explicit resets continue to work and revoke previous sessions by revision.
 new_secret='replacement-fixture-admin'
 rc,out=terminal([new_secret+'\n',new_secret+'\n'],setup=False);assert rc==0 and new_secret not in out,out
 assert json.loads(credentials.read_bytes())['revision']!=data['revision']
 credentials.write_text('{"hash":"invalid"}');saved=credentials.read_bytes();r=call('--setup-if-missing');assert r.returncode==1 and 'needs review' in r.stderr and credentials.read_bytes()==saved,r.stdout+r.stderr
 credentials.unlink();rc,out=terminal(['\x04']);assert rc!=0 and 'not completed' in out and not credentials.exists(),out
 assert not (root/'opt/etc/passwd').exists() and not (root/'opt/etc/shadow').exists()
print('PASS: actual CLI/bcrypt setup, hidden legacy-background prompts, length/confirmation retry, hash/mode/revision, existing and concurrent credentials preserved, explicit reset, corrupt credentials and EOF; no default password or router-account changes.')
