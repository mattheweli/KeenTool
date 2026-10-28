"""Exercise production release installation transactions in an isolated Entware root."""
from pathlib import Path
import tempfile,subprocess,os,shutil,hashlib,json,stat,sqlite3,time,pty,select
src=Path(__file__).resolve().parents[1]
php=Path('/tmp/keentool-security-runtime/root/usr/bin/php8.3')
with tempfile.TemporaryDirectory() as td:
 b=Path(td);pkg=b/'package';shutil.copytree(src,pkg)
 def hashes():
  (pkg/'CHECKSUMS.sha256').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(pkg).as_posix()+'\n' for p in sorted(pkg.rglob('*')) if p.is_file() and p.name!='CHECKSUMS.sha256'))
 hashes()
 def fixture(name,upgrade=False):
  root=b/name;bin=root/'opt/bin';init=root/'opt/etc/init.d';bin.mkdir(parents=True);init.mkdir(parents=True)
  for n in ['php-cli','php-cgi']:
   p=bin/n;p.write_text('#!/bin/bash\nexec '+str(php)+' -n "$@"\n');p.chmod(0o755)
  for n in ['ipset','iptables','ip6tables','iptables-save','ip6tables-save','iptables-restore','ip6tables-restore','vnstat','tcpdump','iprange','lighttpd','vnstatd','mtr','ulogd','smbclient','crond','ping']:
   p=bin/n;p.write_text('#!/bin/bash\nexit 0\n');p.chmod(0o755)
  (bin/'vnstat').write_text('#!/bin/bash\nprintf \"%s\\n\" \"$*\" >> \"$KT_TEST_VNSTAT\"\n[ \"$1\" != --json ]\n')
  (bin/'sqlite3').symlink_to('/tmp/keentool-security-runtime/root/usr/bin/sqlite3')
  for n in ['S11ulogd','S80lighttpd','S32vnstat2']:
   p=init/n;p.write_text('#!/bin/bash\nexit 0\n');p.chmod(0o755)
  runner=root/'service-runner';runner.write_text('#!/bin/bash\nprintf "%s %s\\n" "$1" "$2" >> "$KT_TEST_EVENTS"\nif [ "$2" = status ];then exit 1;fi\nif [ -n "${KT_TEST_FAIL:-}" ] && [[ "$1 $2" = *"$KT_TEST_FAIL"* ]];then exit 1;fi\n');runner.chmod(0o755)
  env=dict(os.environ,KT_INSTALL_ROOT=str(root),KT_INSTALL_TEST_SERVICE=str(runner),KT_TEST_EVENTS=str(root/'events'),KT_TEST_VNSTAT=str(root/'vnstat-commands'))
  webdir=root/'opt/etc/lighttpd';webdir.mkdir();(webdir/'lighttpd.conf').write_text('# existing web listener\n')
  if upgrade:
   (bin/'keentool').write_text('# previous manager\n');(bin/'keentool').chmod(0o750)
   (bin/'pingtool.sh').write_text('#!/opt/bin/bash\nENABLE_IPV6="false"\nEMAIL_ALERTS="true"\nPING_TARGET="1.1.1.1"\nRETENTION_DAYS=90\nPING_DURATION=20\nDB_DIR="/opt/etc/pingtool"\nDB_FILE="$DB_DIR/pingtool.db"\n')
   (root/'opt/etc/crontab').write_text("# custom scheduler\n7 * * * * root /opt/bin/pingtool.sh --ipv4-only\n*/13 * * * * root /opt/bin/traffic_manager.sh 'ppp0'\n")
   (root/'opt/etc/firewall.conf').write_text('ENABLE_FIREWALL="true"\nBANNED_COUNTRIES="cn ru kp"\n')
   (root/'opt/etc/ulogd.conf').write_text('# preserve custom line\n[pcap1]\nfile="/tmp/fw_syn_ring.pcap"\nsync=1\n')
   db=root/'opt/etc/firewall_stats.db';db.write_bytes(b'fixture database bytes\0\xff')
   state=root/'opt/etc/keentool/admin';state.mkdir(parents=True);(state/'credentials.json').write_text('{"hash":"existing"}')
  return root,env
 def call(env,*args):return subprocess.run(['bash',str(pkg/'install.sh'),*args],env=env,capture_output=True,text=True)
 def backup(root):return next((root/'opt/var/backups/keentool-release').iterdir())
 # Fresh install, TLS plan, default jobs, no preexisting alpha add-ons, rollback.
 fresh,env=fixture('fresh')
 r=call(env,'--plan','--mode','fresh','--interface','ppp0','--configure-web','--configure-logging');assert r.returncode==0,r.stdout+r.stderr;assert not (fresh/'events').exists() and not (fresh/'opt/etc/keentool').exists()
 r=call(env,'--apply','--mode','fresh','--interface','ppp0','--configure-web','--configure-logging');assert r.returncode==0,r.stdout+r.stderr
 assert 'Admin password setup requires an interactive SSH terminal.' in r.stderr and not (fresh/'opt/etc/keentool/admin/credentials.json').exists(),r.stdout+r.stderr
 assert 'HISTORY_RAW_DAYS="7"' in (fresh/'opt/etc/keentool/firewall-history.conf').read_text()
 assert (fresh/'opt/bin/firewall_history').exists() and (fresh/'opt/lib/keentool/history_engine.php').exists()
 assert 'ENABLE_FIREWALL="false"' in (fresh/'opt/etc/firewall.conf').read_text()
 assert (fresh/'opt/etc/keentool/tls/server.pem').stat().st_mode&0o777==0o600
 assert (fresh/'opt/etc/crontab').read_text().count('/opt/bin/pingtool.sh')==1
 assert '--add -i ppp0' in (fresh/'vnstat-commands').read_text()
 assert (fresh/'opt/lib/keentool/common.sh').exists() and not (fresh/'opt/lib/keentool-test').exists()
 fresh_backup=backup(fresh)
 # Reproduce the reported missing dependency using installed paths, never source overrides.
 render=fresh/'opt/lib/keentool/render_cache.sh'
 assert render.is_file() and render.read_bytes()==(pkg/'support/render_cache.sh').read_bytes()
 assert render.stat().st_mode&0o777==0o644
 scopes=json.loads((pkg/'FILE_SCOPES.json').read_text());assert scopes['support/render_cache.sh']=='keenetic-firewall'
 stats=(fresh/'opt/bin/firewall_stats.sh').read_text();load=stats[stats.index('. "${KT_RENDER_LIB:'):stats.index('# Port Tables')]
 assert '/opt/lib/keentool/render_cache.sh' in load
 database=b/'render-fixture.db';c=sqlite3.connect(database)
 c.executescript('CREATE TABLE ip_drops(timestamp INTEGER,ip TEXT,count INTEGER,list_type TEXT);CREATE TABLE ip_info(ip TEXT PRIMARY KEY,country TEXT,risk TEXT,domain TEXT,target_port INTEGER,port_history TEXT);CREATE TABLE drops(timestamp INTEGER,list_name TEXT,count INTEGER);')
 now=int(time.time());rows=[(now-60,'203.0.113.7',7,'main'),(now-60,'198.51.100.9',3,'trap'),(now-60,'2001:db8::9',4,'geo')]
 c.executemany('INSERT INTO ip_drops VALUES(?,?,?,?)',rows)
 c.executemany('INSERT INTO ip_info VALUES(?,?,?,?,?,?)',[('203.0.113.7','ZZ','low','main.example.test',443,'443/tcp'),('198.51.100.9','ZZ','low','trap.example.test',22,'22/tcp'),('2001:db8::9','ZZ','low','v6.example.test',53,'53/udp')])
 c.executemany('INSERT INTO drops VALUES(?,?,?)',[(now-60,'FirewallBlock',7),(now-60,'AutoBan',3),(now-60,'GeoBlock6',4)]);c.commit();c.close()
 before=hashlib.sha256(database.read_bytes()).hexdigest();work=b/'render-work';work.mkdir()
 e=dict(os.environ,PATH=str(fresh/'opt/bin')+':'+os.environ['PATH'],KT_RENDER_LIB=str(render),DB_FILE=str(database),KT_WORKDIR=str(work),NOW=str(now),TCP_SERVICES='22 443',UDP_SERVICES='53')
 r=subprocess.run(['bash','-c','. "$1"\n'+load,'fixture',str(fresh/'opt/lib/keentool/common.sh')],env=e,capture_output=True,text=True)
 assert r.returncode==0,r.stdout+r.stderr
 outputs={f.name for f in (work/'render').glob('*.rows')}
 expected={'ip_'+name+'_'+period+'.rows' for name in ['ipv6','trap','other','nets','geo'] for period in ['24h','30d','1y','all']}
 expected|={'port_'+name+'.rows' for name in ['p24','p30','p1y','pall','b24','b30','b1y','ball']}
 expected|={'time_'+name+'.rows' for name in ['hourly','daily','monthly','yearly']}
 assert outputs==expected,(outputs,expected)
 assert '443/tcp|203.0.113.7|7' in (work/'render/port_pall.rows').read_text()
 assert '22/tcp|198.51.100.9|3' in (work/'render/port_ball.rows').read_text()
 assert '2001:db8::9|4|' in (work/'render/ip_ipv6_all.rows').read_text()
 assert before==hashlib.sha256(database.read_bytes()).hexdigest()
 # Verify current-version file audits and coordinated reinstall restore the library.
 assets=b/'assets';r=subprocess.run(['python3',str(pkg/'tools/package-suite.py'),str(assets)],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
 release=json.loads((pkg/'RELEASE.json').read_text());overview=assets/('keentool-'+release['version']+'-manifest.json');digest='sha256:'+hashlib.sha256(overview.read_bytes()).hexdigest()
 def inspect(action):return subprocess.run([str(php),'-n',str(pkg/'support/release_update.php'),action,str(overview),release['version'],digest,str(fresh/'opt/etc/keentool/installed-release.json'),str(fresh/'opt/bin/keentool'),'keenetic-firewall',str(fresh)],capture_output=True,text=True)
 r=inspect('selection');assert r.returncode==0 and r.stdout=='0',r.stdout+r.stderr
 cron_before=(fresh/'opt/etc/crontab').read_bytes();firewall_before=(fresh/'opt/etc/firewall.conf').read_bytes()
 render.unlink();r=inspect('overview');assert r.returncode==0 and '/opt/lib/keentool/render_cache.sh: missing' in r.stdout and 'differences: 1' in r.stdout,r.stdout+r.stderr
 r=inspect('selection');assert r.returncode==0 and r.stdout=='1',r.stdout+r.stderr
 r=call(env,'--apply','--mode','upgrade');assert r.returncode==0,r.stdout+r.stderr
 assert render.read_bytes()==(pkg/'support/render_cache.sh').read_bytes() and render.stat().st_mode&0o777==0o644
 r=inspect('selection');assert r.returncode==0 and r.stdout=='0',r.stdout+r.stderr
 assert (fresh/'opt/etc/crontab').read_bytes()==cron_before and (fresh/'opt/etc/firewall.conf').read_bytes()==firewall_before
 assert before==hashlib.sha256(database.read_bytes()).hexdigest()
 print('PASS: clean installed firewall cache library executes all 32 SQLite outputs; source DB unchanged; current-version missing-file audit selects repair and coordinated reinstall restores mode/hash.')
 r=subprocess.run(['bash',str(fresh_backup/'rollback.sh'),str(fresh_backup)],env=env,capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
 assert not (fresh/'opt/bin/keentool').exists() and not (fresh/'opt/etc/crontab').exists() and not render.exists()
 assert 'S80lighttpd stop' in (fresh/'events').read_text()
 # Upstream migration: literal inline Ping settings, existing cron/database/password unchanged.
 upstream,env=fixture('upstream',True);history=upstream/'opt/etc/keentool/firewall-history.conf';history.write_text('HISTORY_ENABLED="false"\nHISTORY_RAW_DAYS="14"\nHISTORY_HOURLY_DAYS="60"\n');history_before=history.read_bytes();cron=(upstream/'opt/etc/crontab').read_bytes();db=(upstream/'opt/etc/firewall_stats.db').read_bytes();conf=(upstream/'opt/etc/firewall.conf').read_bytes()
 r=call(env,'--apply','--mode','upgrade');assert r.returncode==0,r.stdout+r.stderr
 assert (upstream/'opt/lib/keentool/render_cache.sh').read_bytes()==(pkg/'support/render_cache.sh').read_bytes()
 assert 'Existing admin credential file needs review' in r.stderr and (upstream/'opt/etc/keentool/admin/credentials.json').read_text()=='{"hash":"existing"}',r.stdout+r.stderr
 assert history.read_bytes()==history_before
 p=(upstream/'opt/etc/pingtool.conf').read_text();assert 'PING_TARGET="1.1.1.1"' in p and 'RETENTION_DAYS="90"' in p and 'ENABLE_IPV6="false"' in p
 assert (upstream/'opt/etc/crontab').read_bytes()==cron and (upstream/'opt/etc/firewall_stats.db').read_bytes()==db and (upstream/'opt/etc/firewall.conf').read_bytes()==conf
 assert '# preserve custom line' in (upstream/'opt/etc/ulogd.conf').read_text() and '/opt/var/log/keentool-firewall/' in (upstream/'opt/etc/ulogd.conf').read_text()
 r=subprocess.run(['bash',str(backup(upstream)/'rollback.sh'),str(backup(upstream))],env=env,capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
 assert (upstream/'opt/bin/keentool').read_text()=='# previous manager\n' and (upstream/'opt/bin/keentool').stat().st_mode&0o777==0o750
 assert not (upstream/'opt/lib/keentool/render_cache.sh').exists()
 assert not (upstream/'opt/etc/pingtool.conf').exists() and '/tmp/fw_syn_ring.pcap' in (upstream/'opt/etc/ulogd.conf').read_text()
 # Alpha migration preserves external settings verbatim; injected service-start failure rolls files back.
 alpha,env=fixture('alpha',True);(alpha/'opt/etc/pingtool.conf').write_text('WAN_LABEL="ppp0"\nMAX_DISPLAY_POINTS=7000\n')
 env['KT_TEST_FAIL']='keentool_security_service start'
 r=call(env,'--apply');assert r.returncode!=0,r.stdout+r.stderr
 assert (alpha/'opt/bin/keentool').read_text()=='# previous manager\n' and (alpha/'opt/etc/pingtool.conf').read_text()=='WAN_LABEL="ppp0"\nMAX_DISPLAY_POINTS=7000\n'
 assert not (alpha/'opt/etc/keentool/maintenance').exists() and not (alpha/'opt/lib/keentool/render_cache.sh').exists()
 # Retention is independent of transaction safety; old archives are never removed.
 temporary,env=fixture('temporary',True)
 old=temporary/'opt/var/backups/keentool-release/previous';old.mkdir(parents=True);(old/'keep.txt').write_text('existing archive')
 before_db=(temporary/'opt/etc/firewall_stats.db').read_bytes();before_cron=(temporary/'opt/etc/crontab').read_bytes()
 r=call(env,'--plan','--no-backup');assert r.returncode==0 and 'Installation plan' in r.stdout and 'Install (' in r.stdout and 'Update (' in r.stdout and 'Recovery backup' not in r.stdout,r.stdout+r.stderr
 assert not (temporary/'opt/var/lib/keentool-release/transactions').exists()
 r=call(env,'--apply','--no-backup');assert r.returncode==0 and 'No new permanent backup retained' in r.stdout,r.stdout+r.stderr
 transactions=temporary/'opt/var/lib/keentool-release/transactions';assert list(transactions.iterdir())==[]
 assert list(old.parent.iterdir())==[old] and (old/'keep.txt').read_text()=='existing archive'
 assert (temporary/'opt/etc/firewall_stats.db').read_bytes()==before_db and (temporary/'opt/etc/crontab').read_bytes()==before_cron
 r=call(env,'--plan');assert r.returncode==0 and 'Already matching:' in r.stdout,r.stdout+r.stderr
 engine=pkg/'support/release_install.php'
 def engine_call(env,*args):return subprocess.run([str(php),'-n',str(engine),*map(str,args)],env=env,capture_output=True,text=True)
 r=engine_call(env,'discard',old);assert r.returncode!=0 and old.exists()
 pending,penv=fixture('pending',True)
 r=engine_call(penv,'prepare',pkg,'upgrade','','0','0','discard');assert r.returncode==0,r.stderr
 recovery=Path(r.stdout);outside=b/'outside-directory';outside.mkdir();(outside/'keep.txt').write_text('external')
 (recovery/'external-link').symlink_to(outside,target_is_directory=True)
 r=engine_call(penv,'discard',recovery);assert r.returncode==0 and not recovery.exists() and (outside/'keep.txt').read_text()=='external',r.stderr
 failed,env=fixture('temporary-failed',True);env['KT_TEST_FAIL']='keentool_security_service start'
 r=call(env,'--apply','--no-backup');assert r.returncode!=0 and (failed/'opt/bin/keentool').read_text()=='# previous manager\n',r.stdout+r.stderr
 assert list((failed/'opt/var/lib/keentool-release/transactions').iterdir())==[]
 # If rollback cannot finish, recovery copies survive regardless of retention choice.
 blocked,env=fixture('rollback-blocked',True)
 runner=Path(env['KT_INSTALL_TEST_SERVICE']);runner.write_text('#!/bin/bash\nif [[ "$1 $2" = *"keentool_security_service start"* ]];then touch "$KT_TEST_EVENTS.failed";exit 1;fi\nif [ -f "$KT_TEST_EVENTS.failed" ] && [ "$2" = stop ];then exit 1;fi\n[ "$2" != status ]\n')
 r=call(env,'--apply','--no-backup');assert r.returncode!=0 and 'recovery copies retained' in r.stderr,r.stdout+r.stderr
 retained=list((blocked/'opt/var/lib/keentool-release/transactions').iterdir());assert len(retained)==1 and (retained[0]/'transaction.json').exists()
 print('PASS: grouped plan, explicit retention, successful transaction/rollback cleanup, old archives/data preserved, failed restore retained, constrained symlink-safe cleanup.')
 # Legacy TLS migration: preserve port/includes/credentials and use transaction rollback.
 def tls_fixture(name):
  root,env=fixture(name,True);main=root/'opt/etc/lighttpd/lighttpd.conf'
  main.write_text('server.port = 81\nserver.document-root = "/opt/var/www"\n# custom PHP configuration stays intact\ninclude "/opt/etc/lighttpd/conf.d/*.conf"\n')
  fast=root/'opt/etc/lighttpd/conf.d';fast.mkdir();(fast/'30-fastcgi.conf').write_text('# existing custom PHP backend\n')
  light=root/'opt/bin/lighttpd';light.write_text('#!/usr/bin/python3\nimport os,sys\nfrom pathlib import Path\np=Path(sys.argv[sys.argv.index("-f")+1])\nif "-p" in sys.argv:print(p.read_text())\nif "-tt" in sys.argv and os.environ.get("KT_TEST_TLS_PREFLIGHT_FAIL") and p.name=="lighttpd.conf" and ".kt-tls-" in str(p):sys.exit(1)\n');light.chmod(0o755)
  curl=root/'opt/bin/curl';curl.write_text('#!/bin/bash\nprintf "%s\\n" "$*" >> "$KT_TEST_TLS_PROBES"\n[ "${KT_TEST_TLS_PROBE_FAIL:-0}" != 1 ]\n');curl.chmod(0o755)
  env['KT_TEST_TLS_PROBES']=str(root/'tls-probes');return root,env
 tls,env=tls_fixture('legacy-tls');main=tls/'opt/etc/lighttpd/lighttpd.conf';original=main.read_bytes();db=(tls/'opt/etc/firewall_stats.db').read_bytes();cron=(tls/'opt/etc/crontab').read_bytes();credentials=(tls/'opt/etc/keentool/admin/credentials.json').read_bytes()
 r=call(env,'--plan','--enable-https');assert r.returncode==0 and 'enable TLS on existing port 81' in r.stdout and main.read_bytes()==original and not (tls/'events').exists(),r.stdout+r.stderr
 r=call(env,'--apply','--enable-https','--no-backup');assert r.returncode==0 and 'HTTPS verified on existing port 81' in r.stdout,r.stdout+r.stderr
 assert main.read_bytes().startswith(original) and 'server.port = 8080' not in main.read_text() and 'ssl.engine = "enable"' in main.read_text()
 assert (tls/'opt/etc/lighttpd/conf.d/30-fastcgi.conf').read_text()=='# existing custom PHP backend\n'
 assert (tls/'opt/etc/firewall_stats.db').read_bytes()==db and (tls/'opt/etc/crontab').read_bytes()==cron and (tls/'opt/etc/keentool/admin/credentials.json').read_bytes()==credentials
 cert=tls/'opt/etc/keentool/tls/server.pem';assert cert.stat().st_mode&0o777==0o600;cert_before=cert.read_bytes();main_before=main.read_bytes()
 assert (tls/'tls-probes').read_text().startswith('-q ') and 'https://127.0.0.1:81/' in (tls/'tls-probes').read_text() and '--noproxy *' in (tls/'tls-probes').read_text()
 r=call(env,'--apply','--enable-https','--no-backup');assert r.returncode==0 and main.read_bytes()==main_before and cert.read_bytes()==cert_before,r.stdout+r.stderr
 for name,flag in [('tls-preflight','KT_TEST_TLS_PREFLIGHT_FAIL'),('tls-probe','KT_TEST_TLS_PROBE_FAIL')]:
  root,env=tls_fixture(name);main=root/'opt/etc/lighttpd/lighttpd.conf';before=main.read_bytes();mode=main.stat().st_mode&0o777;env[flag]='1'
  r=call(env,'--apply','--enable-https','--no-backup');assert r.returncode!=0,r.stdout+r.stderr
  assert main.read_bytes()==before and main.stat().st_mode&0o777==mode and not (root/'opt/etc/keentool/tls/server.pem').exists()
  assert (root/'opt/bin/keentool').read_text()=='# previous manager\n'
  if flag=='KT_TEST_TLS_PREFLIGHT_FAIL':assert not (root/'events').exists() and not (root/'opt/var/lib/keentool-release/transactions').exists()
  else:assert list((root/'opt/var/lib/keentool-release/transactions').iterdir())==[] and 'HTTPS handshake check failed' in r.stderr
 custom,env=tls_fixture('tls-custom');main=custom/'opt/etc/lighttpd/lighttpd.conf';main.write_text(main.read_text()+'$SERVER["socket"] == ":8443" { }\n');before=main.read_bytes()
 r=call(env,'--apply','--enable-https');assert r.returncode!=0 and 'manual review' in r.stdout+r.stderr and main.read_bytes()==before and not (custom/'events').exists(),r.stdout+r.stderr
 declined,env=tls_fixture('tls-declined');main=declined/'opt/etc/lighttpd/lighttpd.conf';before=main.read_bytes()
 r=call(env,'--apply','--no-backup');assert r.returncode==0 and 'HTTPS not changed without consent' in r.stderr and main.read_bytes()==before,r.stdout+r.stderr
 # Real installer launched like the old updater: stdin closed, controlling TTY retained.
 prompted,env=tls_fixture('tls-interactive');pid,fd=pty.fork()
 if pid==0:
  os.environ.update(env);os.execvp('bash',['bash','-c','bash "$1" --apply --no-backup </dev/null & child=$!;wait "$child"','legacy',str(pkg/'install.sh')])
 text=b'';sent=False;deadline=time.monotonic()+30
 try:
  while time.monotonic()<deadline:
   ready,_,_=select.select([fd],[],[],.1)
   if not ready:continue
   try:chunk=os.read(fd,8192)
   except OSError:break
   if not chunk:break
   text+=chunk
   if b'Enable HTTPS on port 81 now?' in text and not sent:os.write(fd,b'y\n');sent=True
  else:os.kill(pid,9);raise AssertionError('TLS consent timed out: '+text.decode())
 finally:os.close(fd)
 _,status=os.waitpid(pid,0);assert status==0 and sent and b'HTTPS verified on existing port 81' in text,text.decode()
 assert 'ssl.engine = "enable"' in (prompted/'opt/etc/lighttpd/lighttpd.conf').read_text()
 print('PASS: existing-port TLS plan/apply, unchanged PHP/credentials/data/cron, current TLS/certificate preservation, preflight refusal, TLS-probe rollback, custom socket refusal and noninteractive consent.')
 # Deferral keeps the boot hook itself, even when permanent backups are declined.
 deferred,env=fixture('firewall-deferred',True);oldhook=deferred/'opt/etc/ndm/netfilter.d/100-firewall.sh';oldhook.parent.mkdir(parents=True);oldhook.write_text('#!/bin/bash\n# previous live hook\n');oldhook.chmod(0o750);original_hook=oldhook.read_bytes()
 r=call(env,'--plan','--apply-firewall');assert r.returncode==0 and not (deferred/'events').exists(),r.stdout+r.stderr
 r=call(env,'--apply','--no-backup');assert r.returncode==0 and 'FIREWALL MIGRATION PENDING' in r.stdout and oldhook.read_bytes()==original_hook and oldhook.stat().st_mode&0o777==0o750,r.stdout+r.stderr
 assert not (deferred/'opt/etc/keentool/firewall-upgrade.pending').exists() and list((deferred/'opt/var/lib/keentool-release/transactions').iterdir())==[]
 r=call(env,'--apply','--apply-firewall');assert r.returncode!=0 and 'interactive SSH terminal' in r.stderr and oldhook.read_bytes()==original_hook,r.stdout+r.stderr
 disabled,env=fixture('firewall-disabled',True);conf=disabled/'opt/etc/firewall.conf';conf.write_text(conf.read_text().replace('ENABLE_FIREWALL="true"','ENABLE_FIREWALL="false"'))
 r=call(env,'--apply','--apply-firewall');assert r.returncode!=0 and 'Firewall remains disabled' in r.stderr and not (disabled/'events').exists(),r.stdout+r.stderr
 r=call(env,'--apply','--no-backup');assert r.returncode==0 and 'FIREWALL MIGRATION PENDING' not in r.stdout and 'ENABLE_FIREWALL="false"' in conf.read_text(),r.stdout+r.stderr
 # Symlink refusal and corrupt-backup verification happen before replacement.
 symlink,env=fixture('symlink',True);(symlink/'opt/bin/keentool').unlink();(symlink/'opt/bin/keentool').symlink_to(symlink/'outside')
 r=call(env,'--plan');assert r.returncode!=0 and 'Symlink' in r.stderr
 saved=backup(upstream);m=json.loads((saved/'transaction.json').read_text());first=next(k for k,v in m['before'].items() if v)
 (saved/'files'/first.lstrip('/')).write_text('corrupt')
 r=subprocess.run([str(php),'-n',str(saved/'release_install.php'),'verify-backup',str(saved)],env=dict(env,KT_INSTALL_ROOT=str(upstream)),capture_output=True,text=True)
 assert r.returncode!=0 and 'checksum mismatch' in r.stderr
print('PASS: fresh install/TLS/default schedules, upstream inline settings + PCAP migration, alpha settings, database/credentials/schedule preservation, file-mode rollback, automatic rollback on service failure, symlink rejection and corrupt-backup refusal. Service lifecycle commands mocked; PHP/file/TLS transactions real.')
