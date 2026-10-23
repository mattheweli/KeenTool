#!/opt/bin/bash
# KeenTool stable installer 1.0.0 — 2026-10-22.
set -Eeuo pipefail
export PATH="${KT_INSTALL_ROOT:-}/opt/bin:${KT_INSTALL_ROOT:-}/opt/sbin:/opt/bin:/opt/sbin:/usr/bin:/usr/sbin:/bin:/sbin"
base=$(cd "$(dirname "$0")" && pwd)
action=plan;mode=auto;iface='';web=0;logging=0;start=true;deps=false
while [ "$#" -gt 0 ];do
 case "$1" in
  --plan)action=plan;; --apply)action=apply;;
  --mode)[ "$#" -gt 1 ] || exit 2;mode=$2;shift;;
  --interface)[ "$#" -gt 1 ] || exit 2;iface=$2;shift;;
  --configure-web)web=1;; --configure-logging)logging=1;; --no-start)start=false;; --install-deps)deps=true;;
  --help)echo 'Usage: install.sh [--plan|--apply] [--mode auto|fresh|upgrade] [--interface ppp0] [--configure-web] [--configure-logging] [--no-start] [--install-deps]';exit 0;;
  *)echo "Unknown option: $1" >&2;exit 2;;
 esac;shift
done
[ "$(id -u)" = 0 ] || { echo 'Run as root' >&2;exit 1; }
(cd "$base" && sha256sum -c CHECKSUMS.sha256) >/dev/null
[ "$deps" != true ] || { [ "$action" = apply ] || { echo '--install-deps requires --apply; package manager changes have their own lifecycle' >&2;exit 1; };opkg update;opkg install bash curl lighttpd lighttpd-mod-fastcgi lighttpd-mod-openssl php8-cli php8-cgi php8-mod-session sqlite3-cli ipset vnstat2 tcpdump iprange iputils-ping mtr ulogd ulogd-mod-nflog ulogd-mod-pcap cron openssl-util samba4-client tar coreutils-date; }
for name in iptables ip6tables iptables-save ip6tables-save iptables-restore ip6tables-restore ipset sqlite3 curl vnstat tcpdump iprange openssl lighttpd;do
 command -v "$name" >/dev/null || { echo "Missing command: $name. See docs/INSTALL.md or use --apply --install-deps." >&2;exit 1; }
done
php_cli='';for candidate in "${KT_INSTALL_ROOT:-}/opt/bin/php-cli" "${KT_INSTALL_ROOT:-}/opt/bin/php8" "${KT_INSTALL_ROOT:-}/opt/bin/php";do
 if [ -x "$candidate" ] && "$candidate" -r 'exit(PHP_SAPI === "cli" ? 0 : 1);' >/dev/null 2>&1;then php_cli=$candidate;break;fi
done
[ -n "$php_cli" ] && [ -x "${KT_INSTALL_ROOT:-}/opt/bin/php-cgi" ] || { echo 'PHP CLI/CGI required' >&2;exit 1; }
"$php_cli" -r 'foreach(["inet_pton","inet_ntop","proc_open","stream_socket_server","session_start","password_hash","random_bytes","hash_file"] as $f)if(!function_exists($f)){fwrite(STDERR,"Missing PHP function: $f\n");exit(1);}'
sqlite3 -json :memory: 'SELECT 1 AS ok;' | grep -q '"ok":1' || { echo 'SQLite JSON output support required' >&2;exit 1; }
while IFS=$'\t' read -r src dest perm;do
 case "$src" in *.php)"$php_cli" -l "$base/$src" >/dev/null;"${KT_INSTALL_ROOT:-}/opt/bin/php-cgi" -l "$base/$src" >/dev/null;;*)if head -n 1 "$base/$src" | grep -q '^#!/opt/bin/bash';then bash -n "$base/$src";fi;;esac
done < "$base/INSTALL.tsv"
if [ "$web" = 0 ];then
 [ -f "${KT_INSTALL_ROOT:-}/opt/etc/lighttpd/lighttpd.conf" ] || { echo 'No lighttpd configuration: use --configure-web for the dedicated HTTPS listener' >&2;exit 1; }
 lighttpd -tt -f "${KT_INSTALL_ROOT:-}/opt/etc/lighttpd/lighttpd.conf"
fi
engine="$base/support/release_install.php"
"$php_cli" "$engine" plan "$base" "$mode" "$iface" "$web" "$logging"
[ "$action" = apply ] || { echo 'Plan only. Add --apply to install.';exit 0; }
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
backup=$("$php_cli" "$engine" prepare "$base" "$mode" "$iface" "$web" "$logging")
echo "Verified file/configuration backup: $backup"
# Expose only the existing fixed service paths from the recorded transaction.
field(){ "$php_cli" -r '$p=json_decode(file_get_contents($argv[1]."/transaction.json"),true);$v=$p;foreach(explode(".",$argv[2]) as $k)$v=$v[$k]??null;echo is_bool($v)?($v?"1":"0"):(string)$v;' "$backup" "$1"; }
service_run(){ if [ -n "${KT_INSTALL_ROOT:-}" ] && [ -n "${KT_INSTALL_TEST_SERVICE:-}" ];then "$KT_INSTALL_TEST_SERVICE" "$1" "$2";else bash "$1" "$2";fi; }
rollback_error(){ rc=${1:-$?};trap - ERR INT TERM;echo 'Installation failed; restoring the verified backup' >&2;KT_INSTALL_ROLLBACK=1 bash "$backup/rollback.sh" "$backup" || { echo "Automatic restore needs attention: $backup" >&2;exit 1; };exit "$rc"; }
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
if [ "$web" = 1 ] && [ -f "$backup/lighttpd-was-running" ];then service_run "$web_init" stop;fi
"$php_cli" "$engine" commit "$backup"
mkdir -p "$runroot/var/log/lighttpd" "$runroot/var/run" "$runroot/var/www/ping" "$runroot/var/www/vnstat"
[ -d "$runroot/var/log/keentool-firewall" ] || mkdir -m 700 "$runroot/var/log/keentool-firewall"
if [ "$(field capture_change)" = 1 ] && [ -f /tmp/fw_syn_ring.pcap ] && [ ! -e "$runroot/var/log/keentool-firewall/fw_syn_ring.pcap" ];then cp -p /tmp/fw_syn_ring.pcap "$runroot/var/log/keentool-firewall/fw_syn_ring.pcap";chmod 600 "$runroot/var/log/keentool-firewall/fw_syn_ring.pcap";fi
if [ "$web" = 1 ];then lighttpd -tt -f "$runroot/etc/lighttpd/lighttpd.conf";fi
if [ "$start" = true ];then
 if [ "$(field mode)" = fresh ];then
  vnstat --json -i "$iface" >/dev/null 2>&1 || vnstat --add -i "$iface"
  vnstat_init=$(field init.vnstat);touch "$backup/vnstat-started";service_run "$vnstat_init" start
 fi
 if [ "$(field capture_change)" = 1 ];then touch "$backup/ulogd-started";service_run "$ulog_init" start;fi
 if [ "$web" = 1 ];then touch "$backup/lighttpd-started";service_run "$web_init" start;fi
 service_run "$runroot/bin/wan_syslog_service" start
 service_run "$runroot/bin/keentool_security_service" start
 service_run "$runroot/etc/init.d/S96keentool-security" ensure-cron
fi
trap - ERR INT TERM
echo 'KeenTool 2.0.0 stable installed.'
echo "Rollback: /opt/bin/bash $backup/rollback.sh $backup"
echo 'Existing credentials, databases, saved lists and upgrade schedules are preserved.'
echo 'Fresh installations start with firewall filtering disabled. Set an admin password: firewall_admin_password'
echo 'Review /opt/etc/firewall.conf and run the hook separately when ready: table=filter /opt/bin/bash /opt/etc/ndm/netfilter.d/100-firewall.sh'
echo 'Refresh generated pages at the next cron run, or run pingtool.sh force, traffic_manager.sh INTERFACE force and firewall_stats.sh force.'
echo 'Review web privilege separation: firewall_security harden-web --check (then --apply).'
[ "$web" != 1 ] || echo 'HTTPS listens on 8080 using a private self-signed certificate; verify/trust it or install your own certificate.'
[ "$start" = true ] || echo 'Services were not started. Start the affected web/ulogd and KeenTool services before using the dashboards.'
