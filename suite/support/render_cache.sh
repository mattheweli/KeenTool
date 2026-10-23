#!/opt/bin/bash
# render_cache v1.0.0 | 2026-10-22 | Local router validation
# Raw cache is private to this run; original DB is never modified here.
prepare_render_cache() {
    local DB_FILE=$1 directory=$2 NOW=$3 TCP_SERVICES=$4 UDP_SERVICES=$5
    local WHERE TYPE QUERY TIME_FILTER EXTRA_SQL ID_PREFIX COUNT_COL
    mkdir -p "$directory" || return 1
    local sql="$directory/cache.sql"
    local TCP_CSV UDP_CSV FULL_CLAUSE CLAUSE_TCP CLAUSE_UDP
    TCP_CSV=$(echo "$TCP_SERVICES" | tr -s ' ' ',' | sed 's/^,//;s/,$//')
    UDP_CSV=$(echo "$UDP_SERVICES" | tr -s ' ' ',' | sed 's/^,//;s/,$//')
    [[ "$TCP_CSV$UDP_CSV" =~ ^[0-9,]*$ ]] || return 1
    CLAUSE_TCP="0"; CLAUSE_UDP="0"
    [ -z "$TCP_CSV" ] || CLAUSE_TCP="(i.target_port IN ($TCP_CSV) AND i.port_history LIKE '%' || i.target_port || '/tcp%')"
    [ -z "$UDP_CSV" ] || CLAUSE_UDP="(i.target_port IN ($UDP_CSV) AND i.port_history LIKE '%' || i.target_port || '/udp%')"
    FULL_CLAUSE="AND ($CLAUSE_TCP OR $CLAUSE_UDP)"
    cat > "$sql" <<EOF
.bail on
.timeout 5000
.mode list
.separator |
PRAGMA temp_store=FILE;
BEGIN;
CREATE TEMP TABLE kt_totals AS SELECT ip,list_type,
 SUM(CASE WHEN timestamp>$((NOW-86400)) THEN count ELSE 0 END) c24,
 SUM(CASE WHEN timestamp>$((NOW-2592000)) THEN count ELSE 0 END) c30,
 SUM(CASE WHEN timestamp>$((NOW-31536000)) THEN count ELSE 0 END) cy,
 SUM(count) ca FROM ip_drops GROUP BY ip,list_type;
CREATE TEMP TABLE kt_metadata AS SELECT i.ip,i.target_port,i.port_history,
 CASE WHEN port_history LIKE '%'||target_port||'/udp%' THEN target_port||'/udp'
 WHEN port_history LIKE '%'||target_port||'/tcp%' THEN target_port||'/tcp'
 ELSE target_port||'' END full_port, CASE WHEN ($CLAUSE_TCP OR $CLAUSE_UDP) THEN 1 ELSE 0 END service_match FROM ip_info i;
CREATE INDEX kt_meta_ip ON kt_metadata(ip);
EOF
    emit_ip_query() {
        WHERE=$1
    QUERY="SELECT sub.ip, sub.total, i.country, i.risk, i.domain, i.target_port, sub.list_type, i.port_history 
           FROM (
               SELECT d.ip, SUM(d.count) as total, d.list_type 
               FROM ip_drops d 
               WHERE $WHERE 
               GROUP BY d.ip 
               ORDER BY total DESC 
               LIMIT 10
           ) sub 
           LEFT JOIN ip_info i ON (
               CASE WHEN INSTR(sub.ip, '/') > 0 THEN SUBSTR(sub.ip, 1, INSTR(sub.ip, '/') - 1) ELSE sub.ip END = i.ip
           ) 
           ORDER BY sub.total DESC;"
    
        printf '.output %s/ip_%s.rows\n%s\n' "$directory" "$3" "$QUERY" >> "$sql"
    }
    emit_port_query() {
        TIME_FILTER=$1; EXTRA_SQL=$2; ID_PREFIX=$3
        case "$TIME_FILTER" in 86400) COUNT_COL=c24;;2592000)COUNT_COL=c30;;31536000)COUNT_COL=cy;;*)COUNT_COL=ca;;esac
        QUERY="SELECT i.full_port,GROUP_CONCAT(DISTINCT d.ip),SUM(d.count) AS total
          FROM (SELECT ip,list_type,$COUNT_COL AS count FROM kt_totals WHERE $COUNT_COL>0) d
          JOIN kt_metadata i ON d.ip=i.ip WHERE i.target_port IS NOT NULL AND i.target_port>0
          $EXTRA_SQL GROUP BY i.full_port ORDER BY total DESC LIMIT 10;"
        printf '.output %s/port_%s.rows\n%s\n' "$directory" "$ID_PREFIX" "$QUERY" >> "$sql"
    }
    emit_ip_query "d.ip LIKE '%:%' AND d.timestamp > $((NOW - 86400))" "1" "ipv6_24h"
    emit_ip_query "d.ip LIKE '%:%' AND d.timestamp > $((NOW - 2592000))" "1" "ipv6_30d"
    emit_ip_query "d.ip LIKE '%:%' AND d.timestamp > $((NOW - 31536000))" "1" "ipv6_1y"
    emit_ip_query "d.ip LIKE '%:%'" "1" "ipv6_all"
    emit_ip_query "d.list_type='trap' AND d.timestamp > $((NOW - 86400))" "" "trap_24h"
    emit_ip_query "d.list_type='main' AND d.ip NOT LIKE '%/%' AND d.timestamp > $((NOW - 86400))" "" "other_24h"
    emit_ip_query "d.list_type='main' AND d.ip LIKE '%/%' AND d.timestamp > $((NOW - 86400))" "" "nets_24h"
    emit_ip_query "d.list_type='trap' AND d.timestamp > $((NOW - 2592000))" "" "trap_30d"
    emit_ip_query "d.list_type='main' AND d.ip NOT LIKE '%/%' AND d.timestamp > $((NOW - 2592000))" "" "other_30d"
    emit_ip_query "d.list_type='main' AND d.ip LIKE '%/%' AND d.timestamp > $((NOW - 2592000))" "" "nets_30d"
    emit_ip_query "d.list_type='trap' AND d.timestamp > $((NOW - 31536000))" "" "trap_1y"
    emit_ip_query "d.list_type='main' AND d.ip NOT LIKE '%/%' AND d.timestamp > $((NOW - 31536000))" "" "other_1y"
    emit_ip_query "d.list_type='main' AND d.ip LIKE '%/%' AND d.timestamp > $((NOW - 31536000))" "" "nets_1y"
    emit_ip_query "d.list_type='trap'" "" "trap_all"
    emit_ip_query "d.list_type='main' AND d.ip NOT LIKE '%/%'" "" "other_all"
    emit_ip_query "d.list_type='main' AND d.ip LIKE '%/%'" "" "nets_all"
    emit_ip_query "d.list_type='geo' AND d.timestamp > $((NOW - 86400))" "" "geo_24h"
    emit_ip_query "d.list_type='geo' AND d.timestamp > $((NOW - 2592000))" "" "geo_30d"
    emit_ip_query "d.list_type='geo' AND d.timestamp > $((NOW - 31536000))" "" "geo_1y"
    emit_ip_query "d.list_type='geo'" "" "geo_all"
    emit_port_query "86400" "" "p24"
    emit_port_query "2592000" "" "p30"
    emit_port_query "31536000" "" "p1y"
    emit_port_query "" "" "pall"
    emit_port_query "86400" "AND d.list_type='trap' AND i.service_match=1" "b24"
    emit_port_query "2592000" "AND d.list_type='trap' AND i.service_match=1" "b30"
    emit_port_query "31536000" "AND d.list_type='trap' AND i.service_match=1" "b1y"
    emit_port_query "" "AND d.list_type='trap' AND i.service_match=1" "ball"
    emit_time_query() {
        local fmt=$1 condition=$2 name=$3
        printf '.output %s/time_%s.rows\n' "$directory" "$name" >> "$sql"
        printf "SELECT %s,SUM(CASE WHEN list_name='FirewallBlock' THEN count ELSE 0 END),SUM(CASE WHEN list_name='FirewallBlock6' THEN count ELSE 0 END),SUM(CASE WHEN list_name='VPNBlock' THEN count ELSE 0 END),SUM(CASE WHEN list_name IN('AutoBan','AutoBan6') THEN count ELSE 0 END),SUM(CASE WHEN list_name IN('GeoBlock','GeoBlock6') THEN count ELSE 0 END),SUM(count) FROM drops %s GROUP BY 1 ORDER BY MAX(timestamp) DESC;\n" "$fmt" "$condition" >> "$sql"
    }
    emit_time_query "strftime('%H:00',timestamp,'unixepoch','localtime')" "WHERE timestamp>=strftime('%s','now','-24 hours')" hourly
    emit_time_query "strftime('%d-%m-%Y',timestamp,'unixepoch','localtime')" "WHERE timestamp>=strftime('%s','now','-30 days')" daily
    emit_time_query "strftime('%m-%Y',timestamp,'unixepoch','localtime')" "WHERE timestamp>=strftime('%s','now','-12 months')" monthly
    emit_time_query "strftime('%Y',timestamp,'unixepoch','localtime')" "" yearly
    printf '.output stdout\nCOMMIT;\n' >> "$sql"
    kt_sqlite "$DB_FILE" < "$sql"
}
