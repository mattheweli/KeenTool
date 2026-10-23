"""Exercise the real legacy updater handoff and embedded/standalone migration."""
from pathlib import Path
import tempfile,subprocess,os,json,tarfile,hashlib,pty,select,time,errno,signal
root=Path(__file__).resolve().parents[1]
php='/tmp/keentool-security-runtime/root/usr/bin/php8.3'
subprocess.run(['python3',str(root/'tools/build-bootstrap.py'),'--check'],check=True)
with tempfile.TemporaryDirectory() as td:
 b=Path(td);bin=b/'bin';bin.mkdir();tmp=b/'tmp';tmp.mkdir();runtime=b/'runtime';runtime.mkdir()
 manager=b/'keentool';source=b/'new-manager';calls=b/'calls';opened=b/'opened';trace=b/'install';api=b/'api';archive=b/'archive';sidecar=b/'sidecar'
 # Preserve the production generated entry, replacing only the unrelated UI body.
 entry=(root/'projects/KeenTool/keentool').read_text().split('# END GENERATED LEGACY MIGRATION\n',1)[0]+'# END GENERATED LEGACY MIGRATION\n'
 entry=entry.replace('#!/opt/bin/bash','#!/bin/bash',1)+'printf opened >> "$KT_TEST_OPEN"\nexit 0\n'
 source.write_text(entry);source.chmod(0o755)
 payload=b/'payload';(payload/'support').mkdir(parents=True)
 (payload/'RELEASE.json').write_text('{"suite":"KeenTool","version":"2.0.4","channel":"stable"}')
 (payload/'support/release_install.php').write_text('<?php // mocked transaction boundary\n')
 (payload/'install.sh').write_text('''#!/bin/bash
printf '%s\\n' "$*" >> "$KT_TEST_INSTALL"
[ "$1" = --apply ] || exit 0
[ "${KT_TEST_INSTALL_FAIL:-0}" != 1 ] || exit 7
if [ "${KT_TEST_INSTALL_WAIT:-0}" = 1 ];then
 touch "$KT_TEST_STARTED"
 trap 'exit 143' TERM INT
 while true;do sleep .1;done
fi
cp "$KT_TEST_MANAGER" "$KT_MANAGER_PATH"
printf ready > "$KT_COMMON"
printf updater > "$KT_UPDATE_COMMAND"
printf verifier > "$KT_TEST_READY_HELPER"
printf '{"version":"2.0.4"}' > "$KT_UPDATE_INSTALLED"
''')
 def pack():
  (payload/'CHECKSUMS.sha256').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(payload).as_posix()+'\n' for p in sorted(payload.rglob('*')) if p.is_file() and p.name!='CHECKSUMS.sha256'))
  with tarfile.open(archive,'w:gz') as t:
   for p in sorted(payload.rglob('*')):
    if p.is_file():t.add(p,arcname='keentool-2.0.4/'+p.relative_to(payload).as_posix())
  sidecar.write_text(hashlib.sha256(archive.read_bytes()).hexdigest()+'  keentool-2.0.4.tar.gz\n')
  if api.exists():
   value=json.loads(api.read_text());value['assets'][0].update(size=archive.stat().st_size,digest='sha256:'+hashlib.sha256(archive.read_bytes()).hexdigest());api.write_text(json.dumps(value))
 pack()
 url='https://github.com/mattheweli/KeenTool/releases/download/v2.0.4/'
 release={'tag_name':'v2.0.4','draft':False,'prerelease':False,'assets':[{'name':'keentool-2.0.4.tar.gz','state':'uploaded','size':archive.stat().st_size,'browser_download_url':url+'keentool-2.0.4.tar.gz','digest':'sha256:'+hashlib.sha256(archive.read_bytes()).hexdigest()},{'name':'keentool-2.0.4.tar.gz.sha256','state':'uploaded','size':sidecar.stat().st_size,'browser_download_url':url+'keentool-2.0.4.tar.gz.sha256'}]}
 api.write_text(json.dumps(release))
 curl=bin/'curl';curl.write_text('''#!/usr/bin/env python3
import os,sys,json
from pathlib import Path
a=sys.argv[1:];url=next(x for x in a if x.startswith('https://'));out=Path(a[a.index('-o')+1])
with open(os.environ['KT_TEST_CURL'],'a') as f:f.write(json.dumps(a)+'\\n')
source='KT_TEST_MANAGER' if url.endswith('/keentool') else 'KT_TEST_API' if url.endswith('/latest') else 'KT_TEST_SIDECAR' if url.endswith('.sha256') else 'KT_TEST_ARCHIVE'
out.write_bytes(Path(os.environ[source]).read_bytes());code=os.environ.get('KT_TEST_HTTP','200')
if '-w' in a:print(code,end='')
sys.exit(0 if code=='200' else 22)
''');curl.chmod(0o755)
 wrapper=bin/'php-cli';wrapper.write_text('#!/bin/bash\nexec '+php+' -n "$@"\n');wrapper.chmod(0o755)
 env=dict(os.environ,KT_PATH=str(bin)+':'+os.environ['PATH'],KT_UPDATE_PHP=str(wrapper),KT_UPDATE_TMP=str(tmp),KT_UPDATE_BASH='/bin/bash',KT_COMMON=str(runtime/'common'),KT_UPDATE_INSTALLED=str(runtime/'installed'),KT_UPDATE_HELPER=str(runtime/'helper'),KT_TEST_READY_HELPER=str(runtime/'helper'),KT_UPDATE_COMMAND=str(runtime/'updater'),KT_MANAGER_PATH=str(manager),KT_UPDATE_LEGACY=str(manager),KT_UPDATE_FLAG=str(b/'flag'),KT_TEST_CURL=str(calls),KT_TEST_API=str(api),KT_TEST_SIDECAR=str(sidecar),KT_TEST_ARCHIVE=str(archive),KT_TEST_INSTALL=str(trace),KT_TEST_MANAGER=str(source),KT_TEST_OPEN=str(opened))
 def reset():
  for p in runtime.iterdir():p.unlink()
  for p in [trace,calls,opened]:p.unlink(missing_ok=True)
  manager.write_text(entry);manager.chmod(0o755)
 def run(*args,script=None,extra=None):
  r=subprocess.run(['bash',str(script or manager),*args],env={**env,**(extra or {})},text=True,capture_output=True,timeout=25)
  assert not list(tmp.iterdir()),'bootstrap/updater staging leaked'
  return r
 def interactive(script,answers):
  master,slave=pty.openpty();proc=subprocess.Popen(['bash',str(script)],env=env,stdin=slave,stdout=slave,stderr=slave);os.close(slave);os.write(master,answers);output=b'';deadline=time.monotonic()+30
  try:
   while time.monotonic()<deadline:
    ready,_,_=select.select([master],[],[],.2)
    if ready:
     try:data=os.read(master,65536)
     except OSError as e:
      if e.errno==errno.EIO:break
      raise
     if not data:break
     output+=data
    elif proc.poll() is not None:break
   result=proc.wait(timeout=2)
  finally:
   if proc.poll() is None:proc.kill();proc.wait()
   os.close(master)
  return result,output
 reset();r=run('--help');assert r.returncode==0 and not calls.exists()
 r=run('--check-updates');assert r.returncode==0 and 'available 2.0.4' in r.stdout and not trace.exists() and not opened.exists(),r.stdout+r.stderr
 r=run();assert r.returncode==0 and not trace.exists() and 'interactively' in r.stdout
 r=run('--update','--yes',extra={'KT_TEST_HTTP':'404'});assert r.returncode==0 and not trace.exists() and not opened.exists()
 sidecar.write_text('0'*64+'  keentool-2.0.4.tar.gz\n');r=run('--update','--yes');assert r.returncode!=0 and 'SHA-256 mismatch' in r.stderr and not trace.exists();pack()
 r=run('--update','--yes',extra={'KT_TEST_INSTALL_FAIL':'1'});assert r.returncode==7 and not opened.exists(),r.stdout+r.stderr
 trace.unlink();started=b/'started'
 proc=subprocess.Popen(['bash',str(manager),'--update','--yes'],env={**env,'KT_TEST_INSTALL_WAIT':'1','KT_TEST_STARTED':str(started)},stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
 deadline=time.monotonic()+10
 while not started.exists() and proc.poll() is None and time.monotonic()<deadline:time.sleep(.05)
 try:
  assert started.exists();proc.terminate();out,err=proc.communicate(timeout=10)
 except Exception:
  os.killpg(proc.pid,signal.SIGKILL);out,err=proc.communicate();raise AssertionError(out+err)
 assert proc.returncode==143 and not list(tmp.iterdir()) and not list(runtime.iterdir()),out+err
 trace.unlink();r=run('--update','--yes');assert r.returncode==0 and trace.read_text().splitlines()==['--plan --mode upgrade','--apply --mode upgrade'] and not opened.exists(),r.stdout+r.stderr
 before=calls.read_bytes();r=run();assert r.returncode==0 and opened.read_text()=='opened' and calls.read_bytes()==before
 reset();result,output=interactive(manager,b'n\n');assert result==0 and not trace.exists() and not opened.exists(),output.decode()
 # An alpha starts the same standalone verifier without replacing its manager first.
 reset();manager.write_text('# KEENTOOL MANAGER v2.0.0a8\n');r=run('--yes',script=root/'bootstrap.sh');assert r.returncode==0 and 'installed 2.0.0a8; available 2.0.4' in r.stdout and trace.exists(),r.stdout+r.stderr
 # Run the unmodified historical interactive update function. Only dependencies/UI
 # and its fixed temporary filename are isolated; its mv + exec handoff is real.
 reset();manager.write_text('# KEENTOOL MANAGER v1.3.4\n');old=b/'old-menu'
 fn=(root/'tests/fixtures/public-self-update.sh').read_text().replace('/tmp/keentool.tmp',str(b/'legacy.tmp'))
 old.write_text('''#!/bin/bash
export PATH="$KT_PATH"
T_SELF="KeenTool|$KT_MANAGER_PATH|KeenTool|keentool"
BASE_URL=https://raw.githubusercontent.com/mattheweli
header(){ :; };pause(){ :; };send_analytics(){ :; }
apply_perms(){ chmod +x "$1"; }
get_version(){ sed -n 's/^# KEENTOOL MANAGER v\\([0-9.]*\\).*/\\1/p' "$1" | head -1; }
ver_compare(){ [ "$1" = "$2" ] && return 0;return 1; }
'''+fn+'\naction_self_update\n')
 result,output=interactive(old,b'y\ny\n');assert result==0,output.decode()
 assert opened.read_text()=='opened' and trace.read_text().splitlines()==['--plan --mode upgrade','--apply --mode upgrade'],output.decode()
 assert b'Legacy or incomplete' in output and not list(tmp.iterdir())
print('PASS: actual public updater mv/exec handoff under a TTY, embedded verifier before shared libraries, same-version manager seeding, alpha standalone migration, consent/noninteractive check, cancellation forwarding, no-release/checksum/install failures, readiness/restart and clean staging; GitHub and installer mocked.')
