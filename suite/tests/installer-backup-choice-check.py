"""Exercise actual retention prompts, including legacy background updater invocation."""
from pathlib import Path
import os,pty,select,subprocess,tempfile,time
root=Path(__file__).resolve().parents[1]
source=(root/'install.sh').read_text();functions=source[source.index('kt_set_backup_policy()'):source.index('\nwhile [ "$#"')]
with tempfile.TemporaryDirectory() as td:
 script=Path(td)/'choose.sh';script.write_text('set -Eeuo pipefail\nbackup_policy=ask\n'+functions+'\nkt_choose_backup_policy\nprintf "RESOLVED=%s\\n" "$backup_policy"\n')
 r=subprocess.run(['bash',str(script)],capture_output=True,text=True);assert r.returncode==0 and 'RESOLVED=keep' in r.stdout and 'No interactive terminal' in r.stderr
 def interactive(answer,background=False):
  pid,fd=pty.fork()
  if pid==0:
   if background:os.execvp('bash',['bash','-c','bash "$1" </dev/null & child=$!;wait "$child"','legacy',str(script)])
   os.execvp('bash',['bash',str(script)])
  output=b'';sent=False;deadline=time.monotonic()+10
  try:
   while time.monotonic()<deadline:
    ready,_,_=select.select([fd],[],[],0.1)
    if ready:
     try:chunk=os.read(fd,4096)
     except OSError:break
     if not chunk:break
     output+=chunk
     if b'[y/N]' in output and not sent:os.write(fd,answer.encode());sent=True
   else:
    os.kill(pid,9);raise AssertionError('Prompt timed out: '+output.decode())
  finally:os.close(fd)
  _,status=os.waitpid(pid,0);assert status==0,output.decode()
  return output.decode()
 for answer,expected in [('y\n','keep'),('n\n','discard'),('\n','discard'),('invalid\nn\n','discard')]:
  text=interactive(answer);assert 'RESOLVED='+expected in text,text
 text=interactive('n\n',True);assert 'RESOLVED=discard' in text,text
 r=subprocess.run(['bash',str(root/'install.sh'),'--keep-backup','--no-backup','--help'],capture_output=True,text=True)
 assert r.returncode==2 and 'Choose either' in r.stderr
print('PASS: interactive keep/discard/default/retry, noninteractive safe default, conflicting flags, and legacy background child /dev/tty prompt.')
