from pathlib import Path
import tempfile,subprocess,os
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as td:
 p=Path(td);opt=p/'opt';proc=p/'proc';(proc/'123').mkdir(parents=True);(proc/'123/comm').write_text('lighttpd');(proc/'123/status').write_text('Uid:\t1001 1001 1001 1001\n')
 for d in ['bin','sbin','etc/lighttpd/conf.d','etc/init.d','etc/keentool/admin/sessions','etc/keentool/security','var/run/keentool-security','var/log/lighttpd','var/lib/lighttpd/sockets']:(opt/d).mkdir(parents=True,exist_ok=True)
 (opt/'bin/bash').symlink_to('/bin/bash')
 actual_php='/tmp/keentool-security-runtime/root/usr/bin/php8.3'
 php=opt/'bin/php-cli';php.write_text('#!/bin/bash\nif [ "${MOCK_METADATA_FAIL:-0}" = 1 ] && [[ "$*" = *"@stat("* ]];then exit 1;fi\nexec '+actual_php+' "$@"\n');php.chmod(0o755)
 stat=opt/'bin/stat';stat.write_text('#!/bin/bash\necho unexpected-stat >> "'+str(p/'stat-calls')+'"\necho "stat: invalid option -- c" >&2\nexit 1\n');stat.chmod(0o755)
 for name,text in [('id','if [ "$1" = -u ] && [ "${2:-}" != ktweb ];then echo 0;else echo 1001;fi'),('chgrp','exit 0'),('chown','exit 0'),('keentool_security_service','exit 0')]:
  f=opt/'bin'/name;f.write_text('#!/bin/bash\n'+text+'\n');f.chmod(0o755)
 main=opt/'etc/lighttpd/lighttpd.conf';main.write_text('server.port = 8080\ninclude "'+str(opt)+'/etc/lighttpd/conf.d/*.conf"\n')
 fast=opt/'etc/lighttpd/conf.d/30-fastcgi.conf';fast.write_text('fastcgi.server = (".php" => (("socket" => "/old/php.sock", "bin-path" => "'+str(opt)+'/bin/php-cgi")))\n');fast.chmod(0o600)
 init=opt/'etc/init.d/S80lighttpd';init.write_text('#!/bin/bash\necho restart >> "'+str(p/'restarts')+'"\n');init.chmod(0o755)
 light=opt/'sbin/lighttpd';light.write_text('#!/bin/bash\nif [ "${MOCK_FAIL:-0}" = 1 ] && [ -f "'+str(opt)+'/etc/lighttpd/conf.d/99-keentool-user.conf" ];then exit 1;fi\nexit 0\n');light.chmod(0o755)
 (opt/'etc/keentool/admin/credentials.json').write_text('{"hash":"fixture"}');(opt/'etc/keentool/admin/credentials.json').chmod(0o600)
 script=p/'harden.sh';script.write_text((root/'support/harden_web.sh').read_text().replace('/opt',str(opt)).replace('/proc',str(proc)))
 (opt/'etc/keentool/security/web-account').write_text('1001 1001\n')
 comments='# PHP template\n#  "socket" => socket_dir + "/php-fastcgi-1.socket",\n  # "socket" => socket_dir + "/php-fastcgi-2.socket",\n# Rails template "socket" => "/rails.sock"\n'
 fast.write_text(comments+fast.read_text())
 # An examples-only file must not be selected as a second active PHP backend.
 examples=opt/'etc/lighttpd/conf.d/20-examples.conf';examples.write_text('# "bin-path" => "/opt/bin/php-cgi",\n# "socket" => "/example.sock",\n')
 original=fast.read_bytes()
 # Active multiple assignments fail even when placed on the same line.
 for extra in ['\n"socket" => "/second.sock",\n',' "socket" => "/second.sock",']:
  fast.write_bytes(original.rstrip(b'\n')+extra.encode())
  r=subprocess.run(['bash',str(script),'--check'],capture_output=True,text=True);assert r.returncode!=0 and 'Multiple backend sockets' in r.stderr;assert not (p/'restarts').exists()
 fast.write_bytes(original.replace(b'"/old/php.sock"',b'socket_dir + "/old/php.sock"'))
 r=subprocess.run(['bash',str(script),'--check'],capture_output=True,text=True);assert r.returncode!=0 and 'literal path' in r.stderr
 fast.write_bytes(original)
 r=subprocess.run(['bash',str(script),'--check'],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr;assert not (p/'restarts').exists();assert fast.read_bytes()==original
 env=dict(os.environ,MOCK_METADATA_FAIL='1');r=subprocess.run(['bash',str(script),'--apply'],env=env,capture_output=True,text=True);assert r.returncode!=0,r.stdout+r.stderr;assert fast.read_bytes()==original;assert (opt/'etc/keentool/admin/credentials.json').stat().st_mode&0o777==0o600
 env=dict(os.environ,MOCK_FAIL='1');r=subprocess.run(['bash',str(script),'--apply'],env=env,capture_output=True,text=True);assert r.returncode!=0;assert fast.read_bytes()==original;assert not (opt/'etc/lighttpd/conf.d/99-keentool-user.conf').exists()
 r=subprocess.run(['bash',str(script),'--apply'],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
 assert fast.read_bytes()==original.replace(b'"/old/php.sock"',b'"'+str(opt).encode()+b'/var/run/keentool-web/php-fcgi.sock"');assert fast.read_text().startswith(comments);assert examples.read_text()=='# \"bin-path\" => \"/opt/bin/php-cgi\",\n# \"socket\" => \"/example.sock\",\n'
 assert (opt/'etc/keentool/security/web-hardened').is_file();assert 'keentool-web/php-fcgi.sock' in fast.read_text();assert fast.stat().st_mode&0o777==0o600
 assert (opt/'etc/keentool/admin/credentials.json').stat().st_mode&0o777==0o640
 backup=Path((opt/'etc/keentool/security/web-hardened').read_text().strip());ledger=backup/'permissions.tsv';valid=ledger.read_bytes();ledger.write_text('\t'+str(opt)+'/etc/keentool/admin/credentials.json\n')
 active=fast.read_bytes();r=subprocess.run(['bash',str(script),'--check'],capture_output=True,text=True);assert r.returncode==0 and 'Original permissions were not recorded' in r.stderr
 r=subprocess.run(['bash',str(script),'--rollback'],capture_output=True,text=True);assert r.returncode!=0 and fast.read_bytes()==active;assert (opt/'etc/keentool/security/web-hardened').exists()
 r=subprocess.run(['bash',str(script),'--ensure-user'],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
 # A genuinely missing legacy ledger must warn without an awk open error or fake rollback data.
 ledger.unlink()
 r=subprocess.run(['bash',str(script),'--ensure-user'],capture_output=True,text=True)
 assert r.returncode==0 and 'Original permissions were not recorded' in r.stderr and 'awk:' not in r.stderr,r.stdout+r.stderr
 assert not ledger.exists() and fast.read_bytes()==active
 r=subprocess.run(['bash',str(script),'--rollback'],capture_output=True,text=True)
 assert r.returncode!=0 and fast.read_bytes()==active and not ledger.exists()
 ledger.write_bytes(valid)
 assert not (p/'stat-calls').exists()
 r=subprocess.run(['bash',str(script),'--rollback'],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
 assert fast.read_bytes()==original;assert (opt/'etc/keentool/admin/credentials.json').stat().st_mode&0o777==0o600;assert not (opt/'etc/keentool/security/web-hardened').exists()
 print('PASS: web isolation read-only plan, failed config validation restores originals, successful socket/account configuration preserves mode, explicit rollback restores config/permissions; identity, lighttpd and restart mocked.')
