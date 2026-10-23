#!/opt/bin/bash
# uninstall v1.0.0 | 2026-10-22 | Stable release
# Selective uninstaller: no shared packages, native router chains or unrelated files.
set -e
export PATH=/opt/bin:/opt/sbin:/usr/bin:/usr/sbin:/bin:/sbin
. "${KT_COMMON:-/opt/lib/keentool/common.sh}"
tool=all; purge=false; apply=false
if [ "${1:-}" = --menu ]; then
    echo 'Select component: all / manager / ping / traffic / firewall / smb / notifications / dashboard'
    read -r tool
    echo 'Delete retained data? type PURGE, or Enter to keep:'; read -r answer
    [ "$answer" != PURGE ] || purge=true
    echo 'Showing preview first; nothing has been removed.'
    "$0" --tool "$tool" "$( [ "$purge" = true ] && echo --purge-data || echo --keep-data )"
    echo 'Type REMOVE to execute this exact plan:'; read -r answer
    [ "$answer" = REMOVE ] || exit 0
    apply=true
else
    while [ "$#" -gt 0 ]; do
        case "$1" in --tool) tool=$2;shift 2;;--keep-data)purge=false;shift;;--purge-data)purge=true;shift;;--apply)apply=true;shift;;*)echo 'Unknown argument' >&2;exit 1;;esac
    done
fi
case "$tool" in all|manager|ping|traffic|firewall|smb|notifications|dashboard);;*)echo 'Invalid tool' >&2;exit 1;;esac
kt_init keentool-uninstall
# Refuse to delete files while any relevant job is running. Cron changes are restored by rollback.
for name in firewall-db firewall-hook firewall-update abuse-reporter firewall-enrichment smb-backup pingtool traffic-manager vpn-scan; do
    if [ -d "/tmp/$name.lockdir" ]; then owner=$(cat "/tmp/$name.lockdir/pid" 2>/dev/null); if [[ "$owner" =~ ^[0-9]+$ ]] && kill -0 "$owner" 2>/dev/null; then echo "Job running: $name; try again after it finishes" >&2;exit 1;fi;fi
done
paths=(); data=(); patterns=()
selected() { [ "$tool" = all ] || [ "$tool" = "$1" ]; }
if selected manager; then paths+=(/opt/bin/keentool);patterns+=(/opt/bin/keentool);data+=(/opt/etc/keentool.id);fi
if selected ping;then paths+=(/opt/bin/wan_syslog_monitor /opt/bin/wan_syslog_service /opt/etc/init.d/S95keentool-wan);paths+=(/opt/bin/pingtool.sh /opt/var/www/ping/index.html /opt/var/www/ping/data.js /opt/var/www/ping/chart.js /opt/var/www/ping/chartjs-adapter-date-fns.js /opt/var/www/ping/chartjs-plugin-zoom.js);patterns+=(/opt/bin/pingtool.sh);data+=(/opt/etc/pingtool /opt/etc/pingtool.conf /opt/var/www/ping/incidents.txt);fi
if selected traffic;then paths+=(/opt/bin/traffic_manager.sh /opt/var/www/vnstat);patterns+=(/opt/bin/traffic_manager.sh);data+=(/opt/var/lib/vnstat);fi
if selected smb;then paths+=(/opt/bin/smb_backup_tool.sh);patterns+=(/opt/bin/smb_backup_tool.sh);data+=(/opt/etc/smb_backup.cfg /opt/var/log/smb_backup.log);fi
if selected dashboard;then paths+=(/opt/var/www/index.html);fi
if selected notifications;then paths+=(/opt/bin/email_sender.mod /opt/bin/telegram_sender.mod /opt/lib/keentool-mail);patterns+=(/opt/bin/email_sender.mod /opt/bin/telegram_sender.mod);data+=(/opt/etc/keentool/mail /opt/etc/keentool/telegram);fi
if selected firewall;then
    paths+=(/opt/bin/firewall_security /opt/bin/keentool_security_service /opt/etc/init.d/S96keentool-security /opt/etc/init.d/S01keentool-web-user /opt/lib/keentool-security /opt/lib/keentool/firewall_guard /opt/bin/firewall_health)
    data+=(/opt/etc/keentool/security /opt/var/log/keentool-security)
    paths+=(/opt/bin/firewall_manager.sh /opt/bin/firewall_monitor /opt/bin/firewall_stats.sh /opt/bin/update_blocklist.sh /opt/bin/vpn_scan.sh /opt/bin/abuse_reporter.sh /opt/bin/firewall_enrich /opt/bin/firewall_db_migrate /opt/etc/ndm/netfilter.d/100-firewall.sh /opt/etc/init.d/S00ipset-load /opt/var/www/firewall /opt/var/www/security /opt/var/www/settings /opt/var/www/assets/keentool-settings.js)
    patterns+=(/opt/bin/firewall_stats.sh /opt/bin/update_blocklist.sh /opt/bin/vpn_scan.sh /opt/bin/abuse_reporter.sh /opt/bin/firewall_enrich)
    data+=(/opt/etc/firewall.conf /opt/etc/firewall_stats.db /opt/etc/firewall_stats.db-wal /opt/etc/firewall_stats.db-shm /opt/etc/AbuseIPDB.key /opt/etc/vpn_banned_ips.txt /opt/etc/firewall_autoban.save /opt/etc/firewall_blocklist.save /opt/etc/firewall_blocklist6.save /opt/etc/firewall_geoblock.save /opt/etc/firewall_geoblock6.save /opt/etc/Blacklist.backup /opt/etc/Blacklist6.backup /opt/etc/keentool/vpn /opt/etc/keentool/blocklist-cache /opt/etc/keentool/firewall-api.token)
fi
if [ "$tool" = all ]; then
    paths+=(/opt/bin/keentool_uninstall /opt/lib/keentool)
    data+=(/opt/etc/keentool /opt/etc/firewall_ip_counters.dat /opt/etc/firewall_v4_diff.dat /opt/etc/firewall_v6_diff.dat /opt/etc/firewall_vpn_diff.dat /opt/etc/firewall_trap_diff.dat /opt/etc/firewall_trap6_diff.dat /opt/etc/firewall_geo_diff.dat /opt/etc/firewall_geo6_diff.dat /opt/etc/firewall_manual_diff.dat /opt/etc/firewall_manual6_diff.dat /opt/etc/firewall_trap_last_size.dat /opt/etc/firewall_trap6_last_size.dat /opt/etc/firewall_geo_last_size.dat /opt/etc/firewall_geo6_last_size.dat /opt/etc/firewall_manual_last_size.dat /opt/etc/firewall_manual6_last_size.dat)
fi
printf 'Uninstall plan: component=%s; delete data=%s\n' "$tool" "$purge"
printf 'Remove program/dashboard: %s\n' "${paths[@]}"
[ "$purge" != true ] || printf 'Delete data: %s\n' "${data[@]}"
echo 'Shared Entware packages and unrelated service configurations are preserved.'
if selected firewall;then echo 'Package web isolation is rolled back and the security service stopped before removal.';fi
[ "$apply" = true ] || { echo 'Preview only. Add --apply to execute.';exit 0; }
backup=/opt/var/backups/keentool-test/uninstall-$(date +%Y%m%d_%H%M%S);mkdir -p "$backup";chmod 700 "$backup"
# Backup selected paths (including coherent SQLite DB) before deleting anything.
for p in "${paths[@]}" "${data[@]}" /opt/etc/crontab;do
    [ ! -e "$p" ] || { mkdir -p "$backup/files$(dirname "$p")";cp -a "$p" "$backup/files$p"; }
done
mkdir -p "$backup/databases/opt/etc"
if [ -f /opt/etc/firewall_stats.db ];then kt_sqlite /opt/etc/firewall_stats.db ".backup '$backup/databases/opt/etc/firewall_stats.db'";fi
if [ -f /opt/etc/pingtool/pingtool.db ];then mkdir -p "$backup/databases/opt/etc/pingtool";kt_sqlite /opt/etc/pingtool/pingtool.db ".backup '$backup/databases/opt/etc/pingtool/pingtool.db'";fi
printf '%s\n' 'Program/configuration copies: files/. Coherent SQLite copies: databases/. Restore only while affected jobs/services are stopped.' > "$backup/RESTORE.txt"
if selected firewall;then
    : > "$backup/ipsets.save"
    for set in FirewallBlock FirewallBlock6 AutoBan AutoBan6 FirewallWhite FirewallWhite6 VPNBlock GeoBlock GeoBlock6 Blacklist Blacklist6 KTManualBan KTManualBan6;do ipset save "$set" >> "$backup/ipsets.save" 2>/dev/null || :;done
fi
if [ -f /opt/etc/crontab ];then
    cp /opt/etc/crontab "$KT_WORKDIR/cron"
    for pattern in "${patterns[@]}";do awk -v p="$pattern" 'index($0,p)==0' "$KT_WORKDIR/cron" > "$KT_WORKDIR/next";mv "$KT_WORKDIR/next" "$KT_WORKDIR/cron";done
    cat "$KT_WORKDIR/cron" > /opt/etc/crontab
    [ ! -x /opt/etc/init.d/S10cron ] || /opt/etc/init.d/S10cron restart
fi
if selected firewall;then
if [ -f /opt/etc/keentool/security/pending.json ] && [ -f /opt/bin/firewall_security ];then
 printf '%s\n' '{"action":"rollback_policy","actor":"local"}' | /opt/bin/bash /opt/bin/firewall_security request || exit 1
fi
    if [ -f /opt/etc/keentool/security/web-hardened ] && [ -f /opt/bin/firewall_security ];then /opt/bin/bash /opt/bin/firewall_security harden-web --rollback;fi
    if [ -f /opt/bin/keentool_security_service ];then /opt/bin/bash /opt/bin/keentool_security_service stop;fi
    [ ! -x /opt/etc/ndm/netfilter.d/100-firewall.sh ] || table=filter /opt/etc/ndm/netfilter.d/100-firewall.sh --disable
    for cmd in iptables ip6tables;do
        for chain in BLOCKLIST_IN BLOCKLIST_FWD SCAN_TRAP BLACKLIST FW_CHK_CONN FW_CHK_BRUTE BLOCKLIST_IN6 BLOCKLIST_FWD6 SCAN_TRAP6 BLACKLIST6 FW_CHK_CONN6 FW_CHK_BRUTE6;do
            "$cmd" -n -L "$chain" >/dev/null 2>&1 && { echo "Chain still present: $chain; aborting deletion" >&2;exit 1; } || :
        done
    done
    for set in FirewallBlock FirewallBlock6 AutoBan AutoBan6 FirewallWhite FirewallWhite6 VPNBlock GeoBlock GeoBlock6 Blacklist Blacklist6 KTManualBan KTManualBan6;do ipset destroy "$set" 2>/dev/null || :;done
fi
if selected ping && [ -f /opt/bin/wan_syslog_service ];then /opt/bin/bash /opt/bin/wan_syslog_service stop;fi
for p in "${paths[@]}";do rm -rf -- "$p";done
if [ "$purge" = true ];then
    for p in "${data[@]}";do rm -rf -- "$p";done
fi
# Selective removal retains shared helpers; complete removal deletes them after loading this script.
printf 'Uninstall completed. Backup: %s\n' "$backup"
