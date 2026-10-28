#!/opt/bin/bash
# KeenTool release rollback 1.0.1 — 2026-10-28.
# Restore verified files despite service errors; do not stop untouched daemons.
set -Eeuo pipefail
backup=${1:-};[ -f "$backup/transaction.json" ] && [ -f "$backup/release_install.php" ] || { echo 'Pass the verified release backup path' >&2;exit 1; }
export PATH="${KT_INSTALL_ROOT:-}/opt/bin:/opt/bin:/opt/sbin:/usr/bin:/usr/sbin:/bin:/sbin"
php_cli='';for candidate in "${KT_INSTALL_ROOT:-}/opt/bin/php-cli" "${KT_INSTALL_ROOT:-}/opt/bin/php8" "${KT_INSTALL_ROOT:-}/opt/bin/php";do if [ -x "$candidate" ] && "$candidate" -r 'exit(PHP_SAPI === "cli" ? 0 : 1);' >/dev/null 2>&1;then php_cli=$candidate;break;fi;done
[ -n "$php_cli" ] || exit 1
"$php_cli" "$backup/release_install.php" verify-backup "$backup"
runroot="${KT_INSTALL_ROOT:-}/opt"
if [ "${KT_INSTALL_ROLLBACK:-0}" != 1 ];then
 lock="$runroot/tmp/keentool-install.lockdir"
 mkdir "$lock" || { echo 'Another installer or rollback is active' >&2;exit 75; }
 [ ! -e "$runroot/etc/keentool/maintenance" ] || { rmdir "$lock";echo 'Entware maintenance already active' >&2;exit 75; }
 printf '%s\n' "$$" > "$runroot/etc/keentool/maintenance"
 trap 'rm -f "$runroot/etc/keentool/maintenance";rmdir "$lock" 2>/dev/null || :' EXIT
 for name in pingtool firewall-db firewall-hook firewall-update traffic-manager abuse-reporter vpn-scan smb-backup;do
  owner=$(cat "/tmp/$name.lockdir/pid" 2>/dev/null || :)
  if [[ "$owner" =~ ^[0-9]+$ ]] && kill -0 "$owner" 2>/dev/null;then echo "Job active: $name; retry later" >&2;exit 75;fi
 done
fi
service_run(){ if [ -n "${KT_INSTALL_ROOT:-}" ] && [ -n "${KT_INSTALL_TEST_SERVICE:-}" ];then "$KT_INSTALL_TEST_SERVICE" "$1" "$2";else bash "$1" "$2";fi; }
field(){ "$php_cli" -r '$p=json_decode(file_get_contents($argv[1]."/transaction.json"),true,512,JSON_THROW_ON_ERROR);$v=$p;foreach(explode(".",$argv[2]) as $k)$v=$v[$k]??null;echo is_bool($v)?($v?"1":"0"):(string)$v;' "$backup" "$1"; }
affected(){
 [ -f "$backup/$1-started" ] || [ -f "$backup/$1-stopped" ] && return 0
 # Compatibility with old transactions which did not record stop attempts.
 case "$1" in lighttpd)[ "$(field web)" != 0 ];;ulogd)[ "$(field capture_change)" = 1 ];;vnstat)[ "$(field mode)" = fresh ];;*)return 1;;esac
}
failed=0
attempt(){ if ! service_run "$1" "$2";then echo "Recovery service action failed: $1 $2; continuing file restoration/restart attempts." >&2;failed=1;fi; }
for name in keentool_security_service wan_syslog_service;do [ ! -f "$runroot/bin/$name" ] || attempt "$runroot/bin/$name" stop;done
for name in lighttpd ulogd vnstat;do
 if affected "$name";then
  script=$(field "init.$name");[ -z "$script" ] || attempt "$script" stop
 fi
done
if ! "$php_cli" "$backup/release_install.php" rollback "$backup";then echo 'Source restoration failed; recovery copies retained.' >&2;failed=1;fi
for name in lighttpd ulogd vnstat;do
 if [ -f "$backup/$name-was-running" ];then
  # Repair services stopped by an earlier rollback, while leaving an untouched
  # running daemon (especially vnStat) alone.
  process=$name;[ "$name" != vnstat ] || process=vnstatd
  if affected "$name" || ! pidof "$process" >/dev/null 2>&1;then
   script=$(field "init.$name");[ -z "$script" ] || attempt "$script" start
  fi
 fi
done
for name in wan_syslog_service keentool_security_service;do if [ -f "$backup/$name-was-running" ] && [ -f "$runroot/bin/$name" ];then attempt "$runroot/bin/$name" start;fi;done
if [ "$failed" != 0 ];then echo "Files/rules recovery attempted; service recovery needs attention. Keep $backup and review the errors." >&2;exit 1;fi
