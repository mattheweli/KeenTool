"""Exercise production release installation transactions in an isolated Entware root."""
from pathlib import Path
import tempfile,subprocess,os,shutil,hashlib,json,stat
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
  for n in ['ipset','iptables','ip6tables','iptables-save','ip6tables-save','iptables-restore','ip6tables-restore','vnstat','tcpdump','iprange','lighttpd']:
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
 assert 'HISTORY_RAW_DAYS="7"' in (fresh/'opt/etc/keentool/firewall-history.conf').read_text()
 assert (fresh/'opt/bin/firewall_history').exists() and (fresh/'opt/lib/keentool/history_engine.php').exists()
 assert 'ENABLE_FIREWALL="false"' in (fresh/'opt/etc/firewall.conf').read_text()
 assert (fresh/'opt/etc/keentool/tls/server.pem').stat().st_mode&0o777==0o600
 assert (fresh/'opt/etc/crontab').read_text().count('/opt/bin/pingtool.sh')==1
 assert '--add -i ppp0' in (fresh/'vnstat-commands').read_text()
 assert (fresh/'opt/lib/keentool/common.sh').exists() and not (fresh/'opt/lib/keentool-test').exists()
 r=subprocess.run(['bash',str(backup(fresh)/'rollback.sh'),str(backup(fresh))],env=env,capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
 assert not (fresh/'opt/bin/keentool').exists() and not (fresh/'opt/etc/crontab').exists()
 assert 'S80lighttpd stop' in (fresh/'events').read_text()
 # Upstream migration: literal inline Ping settings, existing cron/database/password unchanged.
 upstream,env=fixture('upstream',True);history=upstream/'opt/etc/keentool/firewall-history.conf';history.write_text('HISTORY_ENABLED="false"\nHISTORY_RAW_DAYS="14"\nHISTORY_HOURLY_DAYS="60"\n');history_before=history.read_bytes();cron=(upstream/'opt/etc/crontab').read_bytes();db=(upstream/'opt/etc/firewall_stats.db').read_bytes();conf=(upstream/'opt/etc/firewall.conf').read_bytes()
 r=call(env,'--apply','--mode','upgrade');assert r.returncode==0,r.stdout+r.stderr
 assert history.read_bytes()==history_before
 p=(upstream/'opt/etc/pingtool.conf').read_text();assert 'PING_TARGET="1.1.1.1"' in p and 'RETENTION_DAYS="90"' in p and 'ENABLE_IPV6="false"' in p
 assert (upstream/'opt/etc/crontab').read_bytes()==cron and (upstream/'opt/etc/firewall_stats.db').read_bytes()==db and (upstream/'opt/etc/firewall.conf').read_bytes()==conf
 assert '# preserve custom line' in (upstream/'opt/etc/ulogd.conf').read_text() and '/opt/var/log/keentool-firewall/' in (upstream/'opt/etc/ulogd.conf').read_text()
 r=subprocess.run(['bash',str(backup(upstream)/'rollback.sh'),str(backup(upstream))],env=env,capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
 assert (upstream/'opt/bin/keentool').read_text()=='# previous manager\n' and (upstream/'opt/bin/keentool').stat().st_mode&0o777==0o750
 assert not (upstream/'opt/etc/pingtool.conf').exists() and '/tmp/fw_syn_ring.pcap' in (upstream/'opt/etc/ulogd.conf').read_text()
 # Alpha migration preserves external settings verbatim; injected service-start failure rolls files back.
 alpha,env=fixture('alpha',True);(alpha/'opt/etc/pingtool.conf').write_text('WAN_LABEL="ppp0"\nMAX_DISPLAY_POINTS=7000\n')
 env['KT_TEST_FAIL']='keentool_security_service start'
 r=call(env,'--apply');assert r.returncode!=0,r.stdout+r.stderr
 assert (alpha/'opt/bin/keentool').read_text()=='# previous manager\n' and (alpha/'opt/etc/pingtool.conf').read_text()=='WAN_LABEL="ppp0"\nMAX_DISPLAY_POINTS=7000\n'
 assert not (alpha/'opt/etc/keentool/maintenance').exists()
 # Symlink refusal and corrupt-backup verification happen before replacement.
 symlink,env=fixture('symlink',True);(symlink/'opt/bin/keentool').unlink();(symlink/'opt/bin/keentool').symlink_to(symlink/'outside')
 r=call(env,'--plan');assert r.returncode!=0 and 'Symlink' in r.stderr
 saved=backup(upstream);m=json.loads((saved/'transaction.json').read_text());first=next(k for k,v in m['before'].items() if v)
 (saved/'files'/first.lstrip('/')).write_text('corrupt')
 r=subprocess.run([str(php),'-n',str(saved/'release_install.php'),'verify-backup',str(saved)],env=dict(env,KT_INSTALL_ROOT=str(upstream)),capture_output=True,text=True)
 assert r.returncode!=0 and 'checksum mismatch' in r.stderr
print('PASS: fresh install/TLS/default schedules, upstream inline settings + PCAP migration, alpha settings, database/credentials/schedule preservation, file-mode rollback, automatic rollback on service failure, symlink rejection and corrupt-backup refusal. Service lifecycle commands mocked; PHP/file/TLS transactions real.')
