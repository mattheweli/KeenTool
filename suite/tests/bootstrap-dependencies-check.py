"""Real dependency preflight with isolated Entware binaries and a fake package manager."""
from pathlib import Path
import os,tempfile,subprocess,json
root=Path(__file__).resolve().parents[1];lib=root/'support/dependencies.sh';php=Path('/tmp/keentool-security-runtime/root/usr/bin/php8.3');sqlite=php.with_name('sqlite3')
with tempfile.TemporaryDirectory() as td:
 p=Path(td);bin=p/'opt/bin';bin.mkdir(parents=True);cgi=bin/'php-cgi';cgi.write_text('#!/bin/bash\necho \"PHP 8.3.6 (cgi-fcgi)\"\n');cgi.chmod(0o755)
 code=r'''
. "$KT_LIB"
# Simulate unavailable router capabilities without altering any host tools.
command(){
 if [ "${1:-}" = -v ];then
  case " $KT_MISSING " in *" $2 "*) [ -f "$KT_INSTALL_ROOT/repaired" ] || return 1;;esac
  case "$2" in opkg|iptables|ip6tables|iptables-save|ip6tables-save|iptables-restore|ip6tables-restore|ipset|vnstat|vnstatd|tcpdump|iprange|lighttpd|ping|mtr|ulogd|smbclient|crond|cron)printf '%s\n' "$2";return 0;;esac
 fi
 builtin command "$@"
}
sqlite3(){ "$KT_SQLITE" "$@"; }
opkg(){
 if [ "$1" = status ];then echo 'Status: install ok installed';return 0;fi
 printf '%s\n' "$*" >> "$KT_INSTALL_ROOT/opkg-calls"
 if [ "$1" = install ] && [ "${KT_BREAK_REPAIR:-0}" != 1 ];then
  printf '#!/bin/bash\nexec %s -n "$@"\n' "$KT_REAL_PHP" > "$KT_INSTALL_ROOT/opt/bin/php-cli"
  chmod 755 "$KT_INSTALL_ROOT/opt/bin/php-cli"
  touch "$KT_INSTALL_ROOT/repaired"
 fi
}
kt_dep_ensure "$1" "$2"
'''
 env=dict(os.environ,KT_LIB=str(lib),KT_INSTALL_ROOT=td,KT_REAL_PHP=str(php),KT_SQLITE=str(sqlite),KT_MISSING='')
 def run(scope='bootstrap',policy='check',extra=None):return subprocess.run(['bash','-c',code,'test',scope,policy],env=dict(env,**(extra or {})),capture_output=True,text=True,timeout=15)
 r=run();assert r.returncode and 'PHP CLI' in r.stderr and not (p/'opkg-calls').exists()
 r=run(policy='ask');assert r.returncode and 'No packages installed' in r.stderr and not (p/'opkg-calls').exists()
 r=run(policy='yes');assert r.returncode==0,r.stderr;assert (p/'opkg-calls').read_text().splitlines()==['update','install php8-cli'];assert not (p/'opt/etc').exists()
 (p/'opkg-calls').unlink();(p/'repaired').unlink();r=run('suite',extra={'KT_MISSING':'mtr vnstatd crond cron'});assert r.returncode and all(x in r.stderr for x in ['mtr','vnstat2','cron']) and not (p/'opkg-calls').exists()
 r=run('suite','yes',{'KT_MISSING':'mtr vnstatd crond cron'});assert r.returncode==0,r.stderr;assert (p/'opkg-calls').read_text().splitlines()==['update','install vnstat2 mtr cron']
 (p/'opkg-calls').unlink();(bin/'php-cli').write_text('#!/bin/bash\nexit 127\n');r=run(policy='yes',extra={'KT_BREAK_REPAIR':'1'});assert r.returncode and 'still unavailable' in r.stderr;assert (p/'opkg-calls').read_text().splitlines()==['update','install php8-cli']
 print('PASS: missing/broken PHP CLI, read-only and noninteractive checks, explicit package consent, combined suite capability report, only missing packages installed, no broad upgrade/config changes and failed-repair verification.')
