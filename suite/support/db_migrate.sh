#!/opt/bin/bash
# db_migrate v1.0.0 | 2026-10-22 | Local router validation
# Migration creates a NEW file only. It never swaps the router's live database.
set -e
export PATH=${KT_PATH:-/opt/bin:/opt/sbin:/usr/bin:/usr/sbin:/bin:/sbin}
. "${KT_COMMON:-/opt/lib/keentool/common.sh}"
[ "$#" = 2 ] || { echo 'Usage: firewall_db_migrate SOURCE.db NEW.db' >&2; exit 1; }
source_db=$1; destination=$2
[ -f "$source_db" ] && [ ! -e "$destination" ] || { echo 'Source missing or destination exists' >&2; exit 1; }
case "$source_db$destination" in *"'"*|*$'\n'*|*' '*) echo 'Use paths without spaces, newlines or quotes' >&2; exit 1;;esac
kt_init firewall-migration
snapshot="$KT_WORKDIR/source.db"
kt_sqlite "$source_db" ".backup '$snapshot'"
cp "$snapshot" "$destination"
kt_sqlite "$destination" < "${KT_NORMALIZE_SQL:-/opt/lib/keentool/normalize.sql}"
[ "$(kt_sqlite "$destination" 'PRAGMA integrity_check;')" = ok ]
# Multiset comparison catches changes to values and duplicate multiplicities.
result=$(kt_sqlite "$destination" "ATTACH '$snapshot' AS original; SELECT count(*) FROM (SELECT timestamp,ip,count,list_type,count(*) n FROM original.ip_drops GROUP BY timestamp,ip,count,list_type EXCEPT SELECT timestamp,ip,count,list_type,count(*) n FROM main.ip_drops GROUP BY timestamp,ip,count,list_type); SELECT count(*) FROM (SELECT timestamp,ip,count,list_type,count(*) n FROM main.ip_drops GROUP BY timestamp,ip,count,list_type EXCEPT SELECT timestamp,ip,count,list_type,count(*) n FROM original.ip_drops GROUP BY timestamp,ip,count,list_type);")
[ "$result" = $'0\n0' ] || { echo 'Migration comparison FAILED' >&2; exit 1; }
printf 'Migration verified. Original untouched: %s\nNew database: %s\n' "$source_db" "$destination"
du -h "$source_db" "$destination"
