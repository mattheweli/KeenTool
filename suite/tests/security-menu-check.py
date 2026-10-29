"""Real PHP-core security menu states and helper actions; no live kernel/DB work on redraw."""
from pathlib import Path
import tempfile,subprocess,os,json,time,socket,hashlib
root=Path(__file__).resolve().parents[1];php='/tmp/keentool-security-runtime/root/usr/bin/php8.3';engine=root/'support/security_engine.php'
with tempfile.TemporaryDirectory(prefix='kt-menu-') as td:
 p=Path(td);etc=p/'opt/etc';sec=etc/'keentool/security';sec.mkdir(parents=True);run=p/'opt/var/run';run.mkdir(parents=True);web=p/'opt/var/www/firewall';web.mkdir(parents=True);bin=p/'opt/bin';bin.mkdir(parents=True);deny=p/'deny';deny.mkdir();calls=p/'unexpected-commands'
 for name in ['ipset','iptables','ip6tables','sqlite3','timeout']:
  f=deny/name;f.write_text('#!/bin/sh\necho '+name+' >> "$KT_UNEXPECTED_COMMANDS"\nexit 99\n');f.chmod(0o755)
 cfg=sec/'settings.json';values={'monitor_interval':120,'email_enabled':True,'immediate_alerts':True,'digest_enabled':False,'digest_hour':7,'timezone':'Europe/Rome','management_networks':['203.0.113.0/24']};cfg.write_text(json.dumps(values))
 conf=etc/'firewall.conf';conf.write_text('ENABLE_FIREWALL="true"\nBYPASS_INTERFACES="tun+"\nFW_LOG_RATE="2"\nFW_LOG_BURST="10"\n')
 mail=etc/'keentool/mail';mail.mkdir();(mail/'email.conf').write_text('SMTP_PASSWORD=PRIVATE_DO_NOT_PRINT');(mail/'emailpw.enc').write_text('PRIVATE_ENCRYPTED');sender=bin/'email_sender.mod';sender.write_text('#!/bin/sh\nexit 0\n');sender.chmod(0o755)
 proc=p/'proc/5678';proc.mkdir(parents=True);cmd=proc/'cmdline';cmd.write_bytes((str(bin/'keentool_security_service')+'\0run\0').encode());(run/'keentool-security-service.pid').write_text('5678\n')
 sockets=run/'keentool-security';sockets.mkdir();sock=socket.socket(socket.AF_UNIX);sock.bind(str(sockets/'broker.sock'))
 monitor=sec/'monitor.json';now=int(time.time());monitor.write_text(json.dumps({'last_check':now}));snapshot=web/'security-data.json';payload={'system':{'time':now,'firewall':{'enabled':True,'healthy':True},'web_privileges':'unprivileged detected'}};snapshot.write_text(json.dumps(payload))
 env=dict(os.environ,KT_SECURITY_ROOT=td,PATH=str(deny)+':'+os.environ['PATH'],KT_UNEXPECTED_COMMANDS=str(calls))
 def call(mode):
  r=subprocess.run([php,'-n',str(engine),mode],env=env,text=True,capture_output=True,timeout=10);assert r.returncode==0,r.stderr;return r.stdout
 before=cfg.read_bytes();out=call('menu');assert all(s in out for s in ['Security Monitoring','Notifications','Access and protection','Blocklist warnings and logging','W. Immediate warning email','D. Daily summary email','OK (snapshot)']);assert 'PRIVATE_' not in out
 assert call('summary')=='RUNNING; warnings ON; daily OFF';assert cfg.read_bytes()==before and not calls.exists()
 values.update(email_enabled=False,digest_enabled=True);cfg.write_text(json.dumps(values));out=call('menu');assert 'ON / PAUSED (email OFF)' in out and call('summary')=='RUNNING; warnings PAUSED; daily PAUSED'
 values.update(email_enabled=True,digest_enabled=False);cfg.write_text(json.dumps(values));(mail/'email.conf').unlink();assert 'mail not configured' in call('menu');assert 'warnings PAUSED' in call('summary');(mail/'email.conf').write_text('PRIVATE_DO_NOT_PRINT')
 cmd.unlink();assert call('summary').startswith('STOPPED');assert 'OK (snapshot)' not in call('menu');cmd.write_bytes((str(bin/'keentool_security_service')+'\0run\0').encode())
 # Stale, malformed, missing and future snapshots must not produce a healthy badge.
 for at in [now-1000,now+1000]:
  payload['system']['time']=at;snapshot.write_text(json.dumps(payload));assert 'OK (snapshot)' not in call('menu')
 snapshot.write_text('invalid JSON');assert 'NOT VERIFIED' in call('menu');payload['system']['time']=int(time.time());snapshot.write_text(json.dumps(payload));monitor.unlink();assert 'OK (snapshot)' not in call('menu');monitor.write_text(json.dumps({'last_check':int(time.time())}))
 assert 'Configured policy bypasses' in call('menu-bypasses') and '203.0.113.0/24' in call('menu-bypasses')
 logs=p/'opt/var/log/keentool-security';logs.mkdir(parents=True);audit=logs/'audit.jsonl';audit.write_text(json.dumps({'time':now,'category':'health','event':'Recovered\u001b[31m','outcome':'ok','note':'details'})+'\n');saved=audit.read_bytes();events=call('menu-events');assert 'Recovered' in events and '\x1b' not in events and audit.read_bytes()==saved
 assert not calls.exists(),'menu redraw must not execute kernel/sqlite commands'
 # Immediate warning toggle uses the existing typed settings action and redraws current state.
 r=subprocess.run(['bash',str(root/'support/firewall_security'),'menu'],input='W\nfalse\n0\n',env=dict(env,KT_SECURITY_PHP=php,KT_SECURITY_ENGINE=str(engine),KT_PATH=env['PATH']),text=True,capture_output=True,timeout=10);assert r.returncode==0,r.stderr;updated=json.loads(cfg.read_text());assert updated['immediate_alerts'] is False and updated['digest_enabled'] is False and updated['email_enabled'] is True
 # Main KeenTool entry uses the lightweight summary and degrades cleanly if unavailable.
 s=(root/'projects/KeenTool/keentool').read_text();a=s.index('    SECURITY_SUMMARY="Unavailable"');b=s.index('\n',s.index('    echo " H. Security Monitoring',a));block=s[a:b]
 wrapper=bin/'firewall_security';wrapper.write_text('#!/bin/sh\nexec '+php+' -n '+str(engine)+' "$@"\n');wrapper.chmod(0o755)
 block=block.replace('/opt/bin/bash','bash').replace('/opt/bin/firewall_security',str(wrapper))
 r=subprocess.run(['bash','-c',block],env=env,text=True,capture_output=True);assert r.returncode==0 and 'Security Monitoring' in r.stdout and 'warnings OFF' in r.stdout
 wrapper.write_text('#!/bin/sh\nexit 1\n');r=subprocess.run(['bash','-c',block],env=env,text=True,capture_output=True);assert r.returncode==0 and '[Unavailable]' in r.stdout
 sock.close()
 print('PASS: grouped live settings, effective/paused notifications, service PID/socket validation, missing/stale/future snapshot handling, no redraw kernel/DB commands or credential leakage, read-only events, warning toggle/redraw and main-menu summary fallback.')
