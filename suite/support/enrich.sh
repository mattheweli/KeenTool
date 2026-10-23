#!/opt/bin/bash
# enrich v1.0.0 | 2026-10-22 | Local router validation
# Bounded metadata enrichment; retry failures later rather than caching XX forever.
export PATH=${KT_PATH:-/opt/bin:/opt/sbin:/usr/bin:/usr/sbin:/bin:/sbin}
. "${KT_COMMON:-/opt/lib/keentool/common.sh}" || exit 1
kt_init firewall-enrichment || exit $?
DB_FILE=${KT_FW_DB:-/opt/etc/firewall_stats.db}
key=$(cat /opt/etc/AbuseIPDB.key 2>/dev/null); [ -n "$key" ] || exit 0
now=$(date +%s); limit=${ENRICH_LIMIT:-10}
[[ "$limit" =~ ^[0-9]+$ ]] && [ "$limit" -le 50 ] || exit 1
kt_sqlite "$DB_FILE" "CREATE TABLE IF NOT EXISTS enrichment_attempts(ip TEXT PRIMARY KEY,last_attempt INTEGER);" || exit 1
kt_sqlite -separator '|' "$DB_FILE" "SELECT ip FROM (SELECT CASE WHEN instr(ip,'/')>0 THEN substr(ip,1,instr(ip,'/')-1) ELSE ip END ip,sum(count) hits FROM ip_drops WHERE timestamp>$((now-2592000)) GROUP BY 1 HAVING hits>=5) d WHERE NOT EXISTS(SELECT 1 FROM ip_info i WHERE i.ip=d.ip AND i.country IS NOT NULL AND i.country NOT IN ('','XX','--') AND i.updated>$((now-604800))) AND NOT EXISTS(SELECT 1 FROM enrichment_attempts a WHERE a.ip=d.ip AND a.last_attempt>$((now-3600))) ORDER BY hits DESC LIMIT $limit;" > "$KT_WORKDIR/ips" || exit 1
while read -r ip; do
    [[ "$ip" =~ ^[0-9a-fA-F.:]+$ ]] || continue
    case "$ip" in 10.*|127.*|192.168.*|169.254.*|172.1[6-9].*|172.2?.*|172.3[01].*|::1|fe80:*) continue;;esac
    kt_sqlite "$DB_FILE" "INSERT OR REPLACE INTO enrichment_attempts VALUES('$ip',$now);" || exit 1
    json=$(curl -fsS --connect-timeout 3 --max-time 5 -G https://api.abuseipdb.com/api/v2/check --data-urlencode "ipAddress=$ip" -d maxAgeInDays=90 -H "Key: $key" -H 'Accept: application/json') || continue
    co=$(printf '%s' "$json" | grep -o '"countryCode"[ ]*:[ ]*"[A-Z][A-Z]"' | sed 's/.*"\([A-Z][A-Z]\)"/\1/')
    risk=$(printf '%s' "$json" | grep -o '"abuseConfidenceScore"[ ]*:[ ]*[0-9]*' | sed 's/.*:[ ]*//')
    domain=$(printf '%s' "$json" | grep -o '"domain"[ ]*:[ ]*"[a-zA-Z0-9._-]*"' | sed 's/.*:[ ]*"\([^"]*\)"/\1/')
    [ -n "$co" ] && [[ "$risk" =~ ^[0-9]+$ ]] || continue
    # UPDATE preserves all accumulated ports and reporter fields.
    kt_sqlite "$DB_FILE" "INSERT OR IGNORE INTO ip_info(ip,country,risk,domain,updated) VALUES('$ip','$co',$risk,'$domain',$now); UPDATE ip_info SET country='$co',risk=$risk,domain='$domain',updated=$now WHERE ip='$ip';" || exit 1
done < "$KT_WORKDIR/ips"
