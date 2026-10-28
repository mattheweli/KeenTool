#!/opt/bin/bash
# KeenTool stable installer 1.0.5 — 2026-10-28.
set -Eeuo pipefail
export PATH="${KT_INSTALL_ROOT:-}/opt/bin:${KT_INSTALL_ROOT:-}/opt/sbin:/opt/bin:/opt/sbin:/usr/bin:/usr/sbin:/bin:/sbin"
base=$(cd "$(dirname "$0")" && pwd)
# KT_INSTALL_BACKUP_RETENTION_V1
# KT_INSTALL_HTTPS_MIGRATION_V1
action=plan;mode=auto;iface='';web=0;logging=0;start=true;deps=false;backup_policy=ask
kt_set_backup_policy() {
    local requested=$1
    [ "$backup_policy" = ask ] || [ "$backup_policy" = "$requested" ] || { echo 'Choose either --keep-backup or --no-backup' >&2; return 2; }
    backup_policy=$requested
}
kt_choose_backup_policy() {
    [ "$backup_policy" = ask ] || return 0
    local answer backup_input=0 backup_tty_open=false
    if [ -t 0 ]; then :
    elif [ -t 2 ] && { exec {backup_input}</dev/tty; } 2>/dev/null; then backup_tty_open=true
    else
        backup_policy=keep
        printf '%s\n' 'No interactive terminal: retaining the recovery backup.' 'Use --no-backup to remove recovery copies after a successful installation.' >&2
        return 0
    fi
    printf '\n%s\n%s\n' 'Recovery backup' 'Temporary rollback protection remains active during installation.' >&2
    while true; do
        printf 'Keep a recovery backup after success? [y/N] ' >&2
        if ! IFS= read -r answer <&"$backup_input"; then
            [ "$backup_tty_open" != true ] || exec {backup_input}<&-
            echo 'No backup choice received; installation cancelled.' >&2
            return 1
        fi
        case "$answer" in
            y|Y|yes|YES) backup_policy=keep;break ;;
            ''|n|N|no|NO) backup_policy=discard;break ;;
            *) echo 'Enter y or n.' >&2 ;;
        esac
    done
    [ "$backup_tty_open" != true ] || exec {backup_input}<&-
}

while [ "$#" -gt 0 ];do
 case "$1" in
  --plan)action=plan;; --apply)action=apply;;
  --keep-backup)kt_set_backup_policy keep;; --no-backup)kt_set_backup_policy discard;;
  --mode)[ "$#" -gt 1 ] || exit 2;mode=$2;shift;;
  --interface)[ "$#" -gt 1 ] || exit 2;iface=$2;shift;;
  --configure-web)[ "$web" = 0 ] || [ "$web" = 1 ] || exit 2;web=1;; --enable-https)[ "$web" = 0 ] || [ "$web" = 2 ] || exit 2;web=2;; --configure-logging)logging=1;; --no-start)start=false;; --install-deps)deps=true;;
  --help)echo 'Usage: install.sh [--plan|--apply] [--mode auto|fresh|upgrade] [--interface ppp0] [--configure-web|--enable-https] [--configure-logging] [--no-start] [--install-deps] [--keep-backup|--no-backup]';echo 'Backup options control retention after success; temporary rollback copies are always used.';exit 0;;
  *)echo "Unknown option: $1" >&2;exit 2;;
 esac;shift
done
[ "$backup_policy" != ask ] || backup_policy=${KT_INSTALL_BACKUP_POLICY:-ask}
case "$backup_policy" in ask|keep|discard);;*)echo 'Invalid backup policy' >&2;exit 2;;esac
[ "$(id -u)" = 0 ] || { echo 'Run as root' >&2;exit 1; }
(cd "$base" && sha256sum -c CHECKSUMS.sha256) >/dev/null
. "$base/support/dependencies.sh"
dep_policy=check
if [ "$deps" = true ];then [ "$action" = apply ] || { echo '--install-deps requires --apply' >&2;exit 2; };dep_policy=yes;fi
kt_dep_ensure suite "$dep_policy" || exit 1
php_cli=$KT_DEP_PHP
while IFS=$'\t' read -r src dest perm;do
 case "$src" in *.php)"$php_cli" -l "$base/$src" >/dev/null;"${KT_INSTALL_ROOT:-}/opt/bin/php-cgi" -l "$base/$src" >/dev/null;;*)if head -n 1 "$base/$src" | grep -q '^#!/opt/bin/bash';then bash -n "$base/$src";fi;;esac
done < "$base/INSTALL.tsv"
if [ "$web" != 1 ];then
 [ -f "${KT_INSTALL_ROOT:-}/opt/etc/lighttpd/lighttpd.conf" ] || { echo 'No lighttpd configuration: use --configure-web for the dedicated HTTPS listener' >&2;exit 1; }
 lighttpd -tt -f "${KT_INSTALL_ROOT:-}/opt/etc/lighttpd/lighttpd.conf"
fi
engine="$base/support/release_install.php"
https_changed=false
if [ "$web" != 1 ];then
 tls_state=$("$php_cli" "$engine" https-state)
 tls_field(){ printf '%s' "$tls_state" | "$php_cli" -r '$s=json_decode(stream_get_contents(STDIN),true,512,JSON_THROW_ON_ERROR);echo $s[$argv[1]]??"";' "$1"; }
 tls_kind=$(tls_field state)
 printf 'HTTPS: %s\n' "$(tls_field detail)"
 if [ "$tls_kind" = configured ];then web=0
 elif [ "$web" = 2 ];then
  [ "$tls_kind" = plain ] || { echo 'Cannot automatically convert this listener; review its HTTPS settings.' >&2;exit 1; }
 elif [ "$tls_kind" = plain ];then
  echo 'Available: enable HTTPS on the existing port, preserving PHP and includes.'
  if [ "$action" = apply ] && [ "$start" = true ];then
   tls_fd=0;tls_tty=false;tls_answer=''
   if [ -t 0 ];then tls_tty=true
   elif [ -t 2 ] && { exec {tls_fd}</dev/tty; } 2>/dev/null;then tls_tty=true;fi
   if [ "$tls_tty" = true ];then
    printf 'Enable HTTPS on port %s now? Existing HTTP URLs will become HTTPS. [y/N] ' "$(tls_field port)" >&2
    IFS= read -r -u "$tls_fd" tls_answer || tls_answer=''
    [ "$tls_fd" = 0 ] || exec {tls_fd}<&-
    case "$tls_answer" in y|Y|yes|YES)web=2;;esac
   else echo 'HTTPS not changed without consent. Run keentool --update --reinstall --enable-https to configure it.' >&2;fi
  fi
 fi
fi
if [ "$web" = 2 ];then
 [ "$start" = true ] || { echo '--enable-https requires service restart; omit --no-start.' >&2;exit 2; }
 https_changed=true
fi

# A remote updater already displayed this plan; still validate it before applying.
if [ "$action" = apply ] && [ "${KT_INSTALL_PLAN_REVIEWED:-0}" = 1 ] && [ "$https_changed" = false ];then
 "$php_cli" "$engine" plan "$base" "$mode" "$iface" "$web" "$logging" >/dev/null
else
 "$php_cli" "$engine" plan "$base" "$mode" "$iface" "$web" "$logging"
fi
[ "$action" = apply ] || { echo 'Plan only. Add --apply to install.';exit 0; }
if [ "$web" = 2 ];then "$php_cli" "$engine" https-preflight "$base" "$mode" "$iface" "$web" "$logging";fi
kt_choose_backup_policy
if [ "$backup_policy" = keep ];then echo 'Recovery backup: retain after success.';else echo 'Recovery backup: temporary; remove after success.';fi
runroot="${KT_INSTALL_ROOT:-}/opt"
mkdir -p "$runroot/etc/keentool" "$runroot/tmp"
[ ! -e "$runroot/etc/keentool/maintenance" ] || { echo 'Entware maintenance already active; retry later' >&2;exit 75; }
lock="$runroot/tmp/keentool-install.lockdir"
mkdir "$lock" || { echo 'Another installer or rollback owns the package lock' >&2;exit 75; }
cleanup(){ rm -f "$runroot/etc/keentool/maintenance";rmdir "$lock" 2>/dev/null || :; }
trap cleanup EXIT
printf '%s\n' "$$" > "$runroot/etc/keentool/maintenance"
for name in pingtool firewall-db firewall-hook firewall-update traffic-manager abuse-reporter vpn-scan smb-backup keentool-entware;do
 owner=$(cat "/tmp/$name.lockdir/pid" 2>/dev/null || :)
 if [[ "$owner" =~ ^[0-9]+$ ]] && kill -0 "$owner" 2>/dev/null;then echo "Job active: $name; retry after it finishes" >&2;exit 75;fi
done
backup=$("$php_cli" "$engine" prepare "$base" "$mode" "$iface" "$web" "$logging" "$backup_policy")
if [ "$backup_policy" = keep ];then echo "Verified recovery backup: $backup";else echo "Verified temporary rollback copies: $backup";fi
# Expose only the existing fixed service paths from the recorded transaction.
field(){ "$php_cli" -r '$p=json_decode(file_get_contents($argv[1]."/transaction.json"),true);$v=$p;foreach(explode(".",$argv[2]) as $k)$v=$v[$k]??null;echo is_bool($v)?($v?"1":"0"):(string)$v;' "$backup" "$1"; }
service_run(){ if [ -n "${KT_INSTALL_ROOT:-}" ] && [ -n "${KT_INSTALL_TEST_SERVICE:-}" ];then "$KT_INSTALL_TEST_SERVICE" "$1" "$2";else bash "$1" "$2";fi; }
rollback_error(){
 rc=${1:-$?};trap - ERR INT TERM
 echo 'Installation failed; restoring the verified recovery copies' >&2
 KT_INSTALL_ROLLBACK=1 bash "$backup/rollback.sh" "$backup" || { echo "Automatic restore needs attention; recovery copies retained: $backup" >&2;exit 1; }
 if [ "$backup_policy" = discard ];then "$php_cli" "$engine" discard "$backup" || echo "Temporary recovery cleanup needs attention: $backup" >&2;fi
 exit "$rc"
}
trap rollback_error ERR
trap 'rollback_error 130' INT
trap 'rollback_error 143' TERM
# Remember live state before stopping anything; rollback only restarts prior services.
for name in lighttpd ulogd vnstat;do process=$name;[ "$name" != vnstat ] || process=vnstatd;if pidof "$process" >/dev/null 2>&1;then touch "$backup/$name-was-running";fi;done
for name in keentool_security_service wan_syslog_service;do
 script="$runroot/bin/$name";if [ -f "$script" ];then
  if service_run "$script" status >/dev/null 2>&1;then touch "$backup/$name-was-running";fi
  service_run "$script" stop
 fi
done
ulog_init=$(field init.ulogd);web_init=$(field init.lighttpd)
if [ "$(field capture_change)" = 1 ] && [ -f "$backup/ulogd-was-running" ];then service_run "$ulog_init" stop;fi
if [ "$web" != 0 ] && [ -f "$backup/lighttpd-was-running" ];then service_run "$web_init" stop;fi
"$php_cli" "$engine" commit "$backup"
mkdir -p "$runroot/var/log/lighttpd" "$runroot/var/run" "$runroot/var/www/ping" "$runroot/var/www/vnstat"
[ -d "$runroot/var/log/keentool-firewall" ] || mkdir -m 700 "$runroot/var/log/keentool-firewall"
if [ "$(field capture_change)" = 1 ] && [ -f /tmp/fw_syn_ring.pcap ] && [ ! -e "$runroot/var/log/keentool-firewall/fw_syn_ring.pcap" ];then cp -p /tmp/fw_syn_ring.pcap "$runroot/var/log/keentool-firewall/fw_syn_ring.pcap";chmod 600 "$runroot/var/log/keentool-firewall/fw_syn_ring.pcap";fi
if [ "$web" != 0 ];then lighttpd -tt -f "$runroot/etc/lighttpd/lighttpd.conf";fi
if [ "$start" = true ];then
 if [ "$(field mode)" = fresh ];then
  vnstat --json -i "$iface" >/dev/null 2>&1 || vnstat --add -i "$iface"
  vnstat_init=$(field init.vnstat);touch "$backup/vnstat-started";service_run "$vnstat_init" start
 fi
 if [ "$(field capture_change)" = 1 ];then touch "$backup/ulogd-started";service_run "$ulog_init" start;fi
 if [ "$web" != 0 ];then touch "$backup/lighttpd-started";service_run "$web_init" start;fi
 service_run "$runroot/bin/wan_syslog_service" start
 service_run "$runroot/bin/keentool_security_service" start
 service_run "$runroot/etc/init.d/S96keentool-security" ensure-cron
fi
if [ "$web" = 2 ];then
 tls_probe=$(field tls.probe);tls_ok=false
 for tls_attempt in 1 2 3;do
  if curl -q --noproxy '*' --http1.1 -k -sS -I --connect-timeout 2 --max-time 5 "$tls_probe" >"$backup/tls-probe.log" 2>&1;then tls_ok=true;break;fi
  [ "$tls_attempt" = 3 ] || sleep 1
 done
 if [ "$tls_ok" != true ];then echo 'HTTPS handshake check failed; restoring the previous listener and package.' >&2;rollback_error 1;fi
 echo "HTTPS verified on existing port $(field tls.port). Use https://<router-address>:$(field tls.port)/ and verify/trust its certificate."
fi
trap - ERR INT TERM
installed_version=$("$php_cli" -r '$r=json_decode(file_get_contents($argv[1]),true,512,JSON_THROW_ON_ERROR);echo $r["version"];' "$base/RELEASE.json")
echo "KeenTool coordinated package $installed_version installed."
if [ "$backup_policy" = keep ];then
 echo "Rollback: /opt/bin/bash $backup/rollback.sh $backup"
else
 if "$php_cli" "$engine" discard "$backup";then echo 'Temporary recovery copies removed. No new permanent backup retained.'
 else echo "Installation succeeded; temporary recovery cleanup needs attention: $backup" >&2;fi
fi
echo 'Existing credentials, databases, saved lists and upgrade schedules are preserved.'
echo 'Fresh installations start with firewall filtering disabled.'
echo 'Review /opt/etc/firewall.conf and run the hook separately when ready: table=filter /opt/bin/bash /opt/etc/ndm/netfilter.d/100-firewall.sh'
echo 'Refresh generated pages at the next cron run, or run pingtool.sh force, traffic_manager.sh INTERFACE force and firewall_stats.sh force.'
echo 'Review web privilege separation: firewall_security harden-web --check (then --apply).'
[ "$web" != 1 ] || echo 'HTTPS listens on 8080 using a private self-signed certificate; verify/trust it or install your own certificate.'
[ "$start" = true ] || echo 'Services were not started. Start the affected web/ulogd and KeenTool services before using the dashboards.'

# This post-install step creates a missing password only; it never resets an existing one.
# Legacy updater children may have stdin=/dev/null; the helper uses the controlling TTY.
if ! bash "$runroot/bin/firewall_admin_password" --setup-if-missing;then
 echo 'Package installation completed; administrator password setup needs attention.' >&2
 echo 'Use KeenTool option A or /opt/bin/bash /opt/bin/firewall_admin_password.' >&2
fi
