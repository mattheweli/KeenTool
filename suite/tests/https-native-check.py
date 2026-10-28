"""Validate actual lighttpd expanded settings, TLS config and local HTTPS handshake."""
from pathlib import Path
import tempfile,subprocess,os,json,shutil,socket,time
suite=Path(__file__).resolve().parents[1];php='/tmp/keentool-security-runtime/root/usr/bin/php8.3'
native=shutil.which('lighttpd');assert native,'Install lighttpd and lighttpd-mod-openssl for native TLS validation'
modules=next((str(p.parent) for p in [Path('/usr/lib/lighttpd/mod_openssl.so'),Path('/usr/lib/x86_64-linux-gnu/lighttpd/mod_openssl.so')] if p.exists()),None);assert modules,'Native mod_openssl missing'
with tempfile.TemporaryDirectory() as td:
 root=Path(td);bin=root/'opt/bin';bin.mkdir(parents=True);web=root/'opt/var/www';web.mkdir(parents=True);(web/'index.html').write_text('KeenTool native TLS fixture')
 confdir=root/'opt/etc/lighttpd';confdir.mkdir(parents=True);init=root/'opt/etc/init.d';init.mkdir()
 for name in ['S80lighttpd','S11ulogd']:
  p=init/name;p.write_text('#!/bin/bash\nexit 0\n');p.chmod(0o755)
 (bin/'keentool').write_text('# legacy fixture\n')
 with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
 main=confdir/'lighttpd.conf';main.write_text('server.modules = ( "mod_indexfile", "mod_staticfile", "mod_openssl" )\nserver.document-root = "'+str(web)+'"\nserver.port = '+str(port)+'\nserver.bind = "127.0.0.1"\nserver.pid-file = "'+str(root/'lighttpd.pid')+'"\nserver.errorlog = "'+str(root/'error.log')+'"\nindex-file.names = ( "index.html" )\n')
 original=main.read_bytes()
 wrapper=bin/'lighttpd';wrapper.write_text('''#!/usr/bin/python3
import os,sys,re,tempfile
from pathlib import Path
args=sys.argv[1:];i=args.index('-f')+1;p=Path(args[i]);s=p.read_text();root=os.environ['KT_INSTALL_ROOT']
s=re.sub(r'"(/opt/[^"\\n]*)"',lambda m:'"'+root+m[1]+'"',s)
f=tempfile.NamedTemporaryFile(mode='w',prefix='.native-',suffix='.conf',dir=Path(root)/'opt/etc/lighttpd',delete=False);f.write(s);f.close();args[i]=f.name
os.execv('''+repr(native)+''',['''+repr(native)+''','-m','''+repr(modules)+''',*args])
''');wrapper.chmod(0o755)
 env=dict(os.environ,KT_INSTALL_ROOT=str(root),PATH=str(bin)+':'+os.environ['PATH'])
 engine=suite/'support/release_install.php'
 def run(action,*args):return subprocess.run([php,'-n',str(engine),action,*map(str,args)],env=env,capture_output=True,text=True)
 def plan_action(action):return run(action,suite,'upgrade','','2','0','keep')
 r=run('https-state');assert r.returncode==0,r.stderr;state=json.loads(r.stdout);assert state['state']=='plain' and state['port']==port and state['probe']=='https://127.0.0.1:'+str(port)+'/',state
 r=plan_action('https-preflight');assert r.returncode==0,r.stdout+r.stderr;assert main.read_bytes()==original and not (root/'opt/etc/keentool/tls/server.pem').exists()
 r=plan_action('prepare');assert r.returncode==0,r.stderr;backup=Path(r.stdout);r=run('commit',backup);assert r.returncode==0,r.stderr
 assert main.read_bytes().startswith(original)
 cert=root/'opt/etc/keentool/tls/server.pem';assert cert.stat().st_mode&0o777==0o600
 r=run('https-state');assert r.returncode==0 and json.loads(r.stdout)['state']=='configured',r.stdout+r.stderr
 config=main.read_text().replace('"/opt/etc/keentool/tls/server.pem"','"'+str(cert)+'"');actual=confdir/'native-live.conf';actual.write_text(config)
 server=subprocess.Popen([native,'-D','-m',modules,'-f',str(actual)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
 try:
  result=None
  for _ in range(30):
   result=subprocess.run(['curl','--noproxy','*','--http1.1','-ksSI','--connect-timeout','1','--max-time','2',state['probe']],capture_output=True,text=True)
   if result.returncode==0:break
   if server.poll() is not None:raise AssertionError('Native lighttpd failed: '+server.stderr.read()+' '+(root/'error.log').read_text())
   time.sleep(.1)
  assert result.returncode==0 and '200 OK' in result.stdout,result.stdout+result.stderr
 finally:
  server.terminate()
  try:server.communicate(timeout=5)
  except subprocess.TimeoutExpired:server.kill();server.communicate()
 r=run('rollback',backup);assert r.returncode==0,r.stderr
 assert main.read_bytes()==original and not cert.exists() and (bin/'keentool').read_text()=='# legacy fixture\n'
print('PASS: native lighttpd expanded listener detection, unchanged-config preflight, real certificate/configuration, actual local TLS/HTTP 200, existing TLS recognition and exact file rollback. No router or external network used.')
