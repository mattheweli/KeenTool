#!/opt/bin/bash
# KEENETIC PINGTOOL v2.0.2
# Release: 2026-10-26 | Stable. See CHANGELOG.md for release details.

export PATH=${KT_PATH:-/opt/bin:/opt/sbin:/bin:/sbin:/usr/bin:/usr/sbin}
# Pingtool 2.0.2
. "${KT_COMMON:-/opt/lib/keentool/common.sh}" || exit 1



# ==============================================================================
# USER CONFIGURATION
# ==============================================================================
ENABLE_IPV6="true"  # Default behavior (can be overridden by -ipv4 flag)
EMAIL_ALERTS="true"
WAN_LABEL=""  # Optional notification label; empty discovers the route interface.
WAN_SYSLOG_FILE="/opt/var/log/messages"
WAN_SYSLOG_ENABLED="true"
PING_TARGET="8.8.8.8"
PING_TARGET_V6="2001:4860:4860::8888"
PING_DURATION=30
TRIGGER_LATENCY=30

WEB_DIR="/opt/var/www/ping"
DB_DIR="/opt/etc/pingtool"
DB_FILE="$DB_DIR/pingtool.db"
LOCK_FILE="/tmp/pingtool.lock"
RETENTION_DAYS=45
MAX_DISPLAY_POINTS=2000

# CDN URLs for Chart.js libraries
URL_CHARTJS="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"
URL_ADAPTER="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"
URL_ZOOM="https://cdnjs.cloudflare.com/ajax/libs/chartjs-plugin-zoom/2.0.1/chartjs-plugin-zoom.min.js"

# ==============================================================================
# External settings survive script updates. Values are root-owned shell assignments.
# ARGUMENT PARSING
# ==============================================================================
PING_CONF="${KT_PING_CONF:-/opt/etc/pingtool.conf}"
[ ! -f "$PING_CONF" ] || . "$PING_CONF"
WEB_DIR="${KT_PING_WEB:-$WEB_DIR}"; DB_FILE="${KT_PING_DB:-$DB_FILE}"; DB_DIR=$(dirname "$DB_FILE")
export LC_ALL=C
sqlite3() { kt_sqlite "$@"; }
[[ "$RETENTION_DAYS" =~ ^[0-9]+$ ]] && [ "$RETENTION_DAYS" -ge 1 ] && [ "$RETENTION_DAYS" -le 3650 ] || { echo 'RETENTION_DAYS must be 1..3650' >&2;exit 1; }
FORCE_HTML_GEN="false"

for arg in "$@"; do
    case $arg in
        -ipv4|--ipv4-only)
            ENABLE_IPV6="false"
            ;;
        force|--force)
            FORCE_HTML_GEN="true"
            ;;
    esac
done

# ==============================================================================
# LOCK MANAGEMENT & INIT
# ==============================================================================
kt_init pingtool || exit $?
echo "[$(date '+%Y-%m-%d %H:%M:%S')] pingtool: Starting test (IPv6: $ENABLE_IPV6)..."

mkdir -p "$DB_DIR"
mkdir -p "$WEB_DIR"

# --- CHECK & DOWNLOAD DEPENDENCIES ---
download_lib() {
    URL=$1; FILE=$2
    if [ ! -s "$WEB_DIR/$FILE" ]; then
        echo " - Missing library $FILE. Downloading..."
        kt_download "$URL" "$WEB_DIR/$FILE"
        if [ $? -eq 0 ]; then echo "   [OK] Downloaded $FILE"; else echo "   [ERR] Failed to download $FILE"; fi
    fi
}

download_lib "$URL_CHARTJS" "chart.js"
download_lib "$URL_ADAPTER" "chartjs-adapter-date-fns.js"
download_lib "$URL_ZOOM" "chartjs-plugin-zoom.js"
for public_asset in chart.js chartjs-adapter-date-fns.js chartjs-plugin-zoom.js; do
    [ ! -f "$WEB_DIR/$public_asset" ] || chmod 644 "$WEB_DIR/$public_asset" || exit 1
done

# --- DB INIT ---
if true; then
    echo " - Checking SQLite schema..."
    sqlite3 "$DB_FILE" "CREATE TABLE IF NOT EXISTS stats (id INTEGER PRIMARY KEY, timestamp INTEGER, ping REAL, jitter REAL, loss REAL);"
    sqlite3 "$DB_FILE" "CREATE INDEX IF NOT EXISTS idx_ts ON stats (timestamp);"
    sqlite3 "$DB_FILE" "CREATE TABLE IF NOT EXISTS stats_v6 (id INTEGER PRIMARY KEY, timestamp INTEGER, ping REAL, jitter REAL, loss REAL);"
    sqlite3 "$DB_FILE" "CREATE INDEX IF NOT EXISTS idx_ts_v6 ON stats_v6 (timestamp);"
fi

# Notification labels describe the route selected at the start of each check.
# WAN_LABEL is a display override; it does not bind ping to an interface.
notification_wan() {
    local family="$1" target="$2" route_label
    if [[ "$WAN_LABEL" =~ ^[a-zA-Z0-9_.:-]+$ ]]; then printf '%s' "$WAN_LABEL"; return; fi
    route_label=$(ip "-$family" route get "$target" 2>/dev/null | awk '{for(i=1;i<NF;i++)if($i=="dev"){print $(i+1);exit}}')
    printf '%s' "${route_label:-WAN unknown}"
}
recovery_message() {
    local label="$1" began="$2" finished="$3" target="$4" elapsed
    printf '%s target reachability restored.\nTarget: %s\n' "$label" "$target"
    if [[ "$began" =~ ^[0-9]+$ ]] && [ "$finished" -ge "$began" ]; then
        elapsed=$((finished-began))
        printf 'Time between first check with 100%% packet loss and first check receiving a reply: %dm %02ds (%s seconds).\nThis is a sampled reachability window, not a measured continuous outage. It does not establish that the WAN or PPP session disconnected.' "$((elapsed/60))" "$((elapsed%60))" "$elapsed"
    else
        printf 'Sampled interval unavailable: invalid timestamp or system clock moved backwards.'
    fi
}
WAN_V4=$(notification_wan 4 "$PING_TARGET")
WAN_V6=$(notification_wan 6 "$PING_TARGET_V6")
LABEL_V4="$WAN_V4 · IPv4"
LABEL_V6="$WAN_V6 · IPv6"

NOW=$(date +%s)

# ==============================================================================
# PARALLEL MEASUREMENTS: both families share the sampling timestamp.
# ==============================================================================
[[ "$PING_DURATION" =~ ^[0-9]+$ ]] && [ "$PING_DURATION" -ge 1 ] && [ "$PING_DURATION" -le 50 ] || { echo 'PING_DURATION must be 1..50' >&2; exit 1; }
TMP_PING="$KT_WORKDIR/v4"; TMP_PING_V6="$KT_WORKDIR/v6"
ping -4 -w "$PING_DURATION" -i 1 "$PING_TARGET" > "$TMP_PING" 2>&1 & PID4=$!
if [ "$ENABLE_IPV6" = true ]; then
    if command -v ping6 >/dev/null 2>&1; then ping6 -w "$PING_DURATION" -i 1 "$PING_TARGET_V6" > "$TMP_PING_V6" 2>&1 &
    else ping -6 -w "$PING_DURATION" -i 1 "$PING_TARGET_V6" > "$TMP_PING_V6" 2>&1 & fi
    PID6=$!
fi
wait "$PID4" || :
[ "$ENABLE_IPV6" != true ] || wait "$PID6" || :
parse_ping() {
    awk '
    /packet loss/ { for(i=1;i<=NF;i++) if($i=="packet" && $(i+1) ~ /^loss/) { loss=$(i-1); gsub(/%/,"",loss) } }
    /time[=<]/ { line=$0; sub(/^.*time[=<]/,"",line); sub(/ .*/,"",line); if(line ~ /^[0-9.]+$/) { t=line+0; sum+=t; n++; if(n>1) {d=t-prev; if(d<0)d=-d; diff+=d}; prev=t } }
    END { if(loss=="")loss=100; if(n>0) printf "%.3f %.3f %.3f\n",sum/n,(n>1?diff/(n-1):0),loss; else printf "NULL NULL %.3f\n",loss }
    ' "$1"
}
read -r AVG_PING JITTER LOSS < <(parse_ping "$TMP_PING")
AVG_PING_V6=NULL; JITTER_V6=NULL; LOSS_V6=0
if [ "$ENABLE_IPV6" = true ]; then read -r AVG_PING_V6 JITTER_V6 LOSS_V6 < <(parse_ping "$TMP_PING_V6"); fi
sqlite3 "$DB_FILE" "BEGIN; INSERT INTO stats(timestamp,ping,jitter,loss) VALUES($NOW,$AVG_PING,$JITTER,$LOSS); COMMIT;" || exit 1
if [ "$ENABLE_IPV6" = true ]; then sqlite3 "$DB_FILE" "INSERT INTO stats_v6(timestamp,ping,jitter,loss) VALUES($NOW,$AVG_PING_V6,$JITTER_V6,$LOSS_V6);" || exit 1; fi
kt_log "v4=$AVG_PING jitter=$JITTER loss=$LOSS%; v6=$AVG_PING_V6 loss=$LOSS_V6%"
# ==============================================================================
# CLEANUP & ALERTS
# ==============================================================================
echo " - Cleaning old records (> $RETENTION_DAYS days)..."
sqlite3 "$DB_FILE" "DELETE FROM stats WHERE timestamp < strftime('%s', 'now', '-$RETENTION_DAYS days');"
if [ "$ENABLE_IPV6" = "true" ]; then
    sqlite3 "$DB_FILE" "DELETE FROM stats_v6 WHERE timestamp < strftime('%s', 'now', '-$RETENTION_DAYS days');"
fi

INCIDENT_LOG="$WEB_DIR/incidents.txt"
EMAIL_MOD="/opt/bin/email_sender.mod"

# --- Alert Logic IPv4 ---
IS_HIGH_V4=$(awk -v p="$AVG_PING" -v t="$TRIGGER_LATENCY" 'BEGIN {print (p != "NULL" && p+0 > t+0 ? 1 : 0)}')

if [ "$(awk -v l="$LOSS" 'BEGIN{print(l+0>0)}')" = 1 ] || [ "$IS_HIGH_V4" -eq 1 ]; then
    echo " ! ALERT IPv4: Anomalous values detected."
    LOG_MSG="[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ $LABEL_V4 Alert: Ping=$AVG_PING ms | Loss=$LOSS%"
    echo "$LOG_MSG" >> "$INCIDENT_LOG"
    
    COOLDOWN_FILE_V4="/tmp/ping_alert_v4.lock"
    
    # Check if an alert was already sent in the last 10 minutes
    if [ -n "$(find /tmp -name 'ping_alert_v4.lock' -mmin -10 2>/dev/null)" ]; then
        echo "   -> Alert sent recently. Skipping email and MTR to prevent spam."
    else
        echo "   -> Starting MTR trace in background..."
        touch "$COOLDOWN_FILE_V4"
        
        # Asynchronous subprocess: MTR and email sending happen in the background
        (
            if command -v mtr >/dev/null 2>&1; then
                MTR_REPORT=$(timeout 40 mtr -4 -r -c 10 -w "$PING_TARGET")
                echo -e "--- MTR IPv4 Report ---\n$MTR_REPORT\n-----------------------" >> "$INCIDENT_LOG"
            else
                MTR_REPORT="(MTR not installed)"
                echo "Error: mtr not found" >> "$INCIDENT_LOG"
            fi

            if [ "$EMAIL_ALERTS" = "true" ] && [ -x "$EMAIL_MOD" ]; then
                EMAIL_BODY="⚠️ Connection Instability Detected ($LABEL_V4)\n\nTarget: $PING_TARGET\nLatency: $AVG_PING ms (Threshold: $TRIGGER_LATENCY ms)\nPacket Loss: $LOSS%\n\n--- Diagnostic Report (MTR) ---\n$MTR_REPORT"
                "$EMAIL_MOD" "Ping Alert: $LABEL_V4" "$EMAIL_BODY"
            fi
        ) &
    fi
fi

# --- Alert Logic IPv6 (Conditional) ---
if [ "$ENABLE_IPV6" = "true" ]; then
    IS_HIGH_V6=$(awk -v p="$AVG_PING_V6" -v t="$TRIGGER_LATENCY" 'BEGIN {print (p != "NULL" && p+0 > t+0 ? 1 : 0)}')
    
    if [ "$(awk -v l="$LOSS_V6" 'BEGIN{print(l+0>0)}')" = 1 ] || [ "$IS_HIGH_V6" -eq 1 ]; then
        echo " ! ALERT IPv6: Anomalous values detected."
        LOG_MSG="[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ $LABEL_V6 Alert: Ping=$AVG_PING_V6 ms | Loss=$LOSS_V6%"
        echo "$LOG_MSG" >> "$INCIDENT_LOG"
        
        COOLDOWN_FILE_V6="/tmp/ping_alert_v6.lock"

        # Check if an alert was already sent in the last 10 minutes
        if [ -n "$(find /tmp -name 'ping_alert_v6.lock' -mmin -10 2>/dev/null)" ]; then
            echo "   -> Alert sent recently. Skipping email and MTR to prevent spam."
        else
            echo "   -> Starting MTR trace in background..."
            touch "$COOLDOWN_FILE_V6"
            
            # Asynchronous subprocess: MTR and email sending happen in the background
            (
                if command -v mtr >/dev/null 2>&1; then
                    MTR_REPORT_V6=$(timeout 40 mtr -6 -r -c 10 -w "$PING_TARGET_V6")
                    echo -e "--- MTR IPv6 Report ---\n$MTR_REPORT_V6\n-----------------------" >> "$INCIDENT_LOG"
                else
                    MTR_REPORT_V6="(MTR not installed)"
                    echo "Error: mtr not found" >> "$INCIDENT_LOG"
                fi

                if [ "$EMAIL_ALERTS" = "true" ] && [ -x "$EMAIL_MOD" ]; then
                    EMAIL_BODY="⚠️ Connection Instability Detected ($LABEL_V6)\n\nTarget: $PING_TARGET_V6\nLatency: $AVG_PING_V6 ms (Threshold: $TRIGGER_LATENCY ms)\nPacket Loss: $LOSS_V6%\n\n--- Diagnostic Report (MTR) ---\n$MTR_REPORT_V6"
                    "$EMAIL_MOD" "Ping Alert: $LABEL_V6" "$EMAIL_BODY"
                fi
            ) &
        fi
    fi
fi

# ==============================================================================
# Warning clearance is logged locally; only complete ping loss opens recovery mail state.
# Legacy incident timestamps describe mixed warnings and must never imply an outage.
for family in v4 v6; do
    [ "$family" != v6 ] || [ "$ENABLE_IPV6" = true ] || continue
    if [ "$family" = v4 ]; then
        l=$LOSS; high=$IS_HIGH_V4; label=$LABEL_V4; target=$PING_TARGET
    else
        l=$LOSS_V6; high=${IS_HIGH_V6:-0}; label=$LABEL_V6; target=$PING_TARGET_V6
    fi
    state="$DB_DIR/incident_$family.ts"
    outage_state="$DB_DIR/ping_unreachable_$family.state"
    if [ "$(awk -v l="$l" -v h="$high" 'BEGIN{print(l+0>0 || h==1)}')" = 1 ]; then
        if [ ! -f "$state" ]; then
            printf '%s\n' "$NOW" > "$state"
            [ ! -x /opt/bin/firewall_security ] || /opt/bin/bash /opt/bin/firewall_security event ping "$label instability detected" "Loss: $l%; latency threshold exceeded: $high" "$NOW" || :
        fi
    elif [ -f "$state" ]; then
        message="$label ping warning cleared. Packet loss and latency are within thresholds."
        printf '[%s] %s\n' "$(date '+%F %T')" "$message" >> "$INCIDENT_LOG"
        [ ! -x /opt/bin/firewall_security ] || /opt/bin/bash /opt/bin/firewall_security event ping "$label warning cleared" "$message" "$NOW" || :
        rm -f "$state"
    fi
    # Do not report recovery of a different target after configuration changes.
    if [ -f "$outage_state" ] && [ "$(sed -n '2p' "$outage_state")" != "$target" ]; then
        rm -f "$outage_state"
    fi
    if [ "$(awk -v l="$l" 'BEGIN{print(l+0>=100)}')" = 1 ]; then
        if [ ! -f "$outage_state" ]; then
            printf '%s\n%s\n' "$NOW" "$target" > "$outage_state"
        fi
    elif [ -f "$outage_state" ]; then
        began=$(sed -n '1p' "$outage_state")
        message=$(recovery_message "$label" "$began" "$NOW" "$target")
        message="$message
Current packet loss: $l%; latency threshold exceeded: $high."
        printf '[%s] %s\n' "$(date '+%F %T')" "$message" >> "$INCIDENT_LOG"
        [ ! -x /opt/bin/firewall_security ] || /opt/bin/bash /opt/bin/firewall_security event ping "$label target reachable again" "$message" "$NOW" || :
        if [ "$EMAIL_ALERTS" = true ] && [ -x "$EMAIL_MOD" ]; then "$EMAIL_MOD" "Ping target reachable again: $label" "$message" & fi
        rm -f "$outage_state"
    fi
done
# ==============================================================================
# PPP session events are collected by S95keentool-wan independently of ping sampling.
# ==============================================================================
# GENERATE DATA.JS
# ==============================================================================
echo -n " - Generating JSON data file (data.js)... "
DATA_JS="$WEB_DIR/data.js"
DATA_TMP=$(mktemp "$WEB_DIR/.data.XXXXXX") || exit 1
DATE_UPDATE=$(date "+%d/%m/%Y %H:%M:%S")

history_json() {
    local table=$1 bucket=$2 since=$3
    sqlite3 "$DB_FILE" "SELECT MAX(timestamp),AVG(ping),AVG(jitter),AVG(loss),MAX(ping),MAX(loss) FROM $table WHERE timestamp >= $since GROUP BY timestamp/$bucket ORDER BY MAX(timestamp);" |
      awk -F'|' '{for(i=2;i<=6;i++)if($i=="")$i="null"; printf "{x:%s000,p:%s,j:%s,l:%s,peak:%s,maxLoss:%s},",$1,$2,$3,$4,$5,$6}' | sed 's/,$//'
}
[[ "$MAX_DISPLAY_POINTS" =~ ^[0-9]+$ ]] && [ "$MAX_DISPLAY_POINTS" -ge 100 ] && [ "$MAX_DISPLAY_POINTS" -le 10000 ] || MAX_DISPLAY_POINTS=2000
period_json() {
 local table=$1 since=$2
 sqlite3 "$DB_FILE" "SELECT COUNT(*),AVG(ping),AVG(jitter),AVG(loss),MIN(timestamp),MAX(timestamp) FROM $table WHERE timestamp >= $since;" |
 awk -F'|' '{for(i=2;i<=6;i++)if($i=="")$i="null";printf "{samples:%d,p:%s,j:%s,l:%s,first:%s,last:%s}",$1,$2,$3,$4,$5,$6}'
}
RANGES_V4=""; RANGES_V6=""; HIST_V4=""; HIST_V6=""; JS_V6_CONFIG=false
for family in v4 v6;do
 [ "$family" != v6 ] || [ "$ENABLE_IPV6" = true ] || continue
 table=stats;[ "$family" != v6 ] || { table=stats_v6;JS_V6_CONFIG=true; }
 hist="";periods=""
 for range in 1 24 7 30 max;do
  case "$range" in
   1) since=$((NOW-3600));bucket=1;;
   24) since=$((NOW-86400));bucket=60;;
   7) since=$((NOW-604800));bucket=300;;
   30) since=$((NOW-2592000));bucket=3600;;
   max) since=0;bucket=3600;;
  esac
  first=$(sqlite3 "$DB_FILE" "SELECT MIN(timestamp) FROM $table WHERE timestamp >= $since;")
  if [[ "$first" =~ ^[0-9]+$ ]];then
   adaptive=$(((NOW-first)/(MAX_DISPLAY_POINTS-1)+1))
   [ "$adaptive" -le "$bucket" ] || bucket=$adaptive
  fi
  key=$family;[ "$range" = 24 ] || key="${family}_$range"
  hist="$hist$key:[$(history_json "$table" "$bucket" "$since")],"
  periods="$periods\"$range\":$(period_json "$table" "$since"),"
 done
 if [ "$family" = v4 ];then HIST_V4=${hist%,};RANGES_V4=${periods%,}
 else HIST_V6=${hist%,};RANGES_V6=${periods%,};fi
done
STATS_V4=$(sqlite3 "$DB_FILE" "SELECT AVG(ping),AVG(jitter),AVG(loss) FROM stats WHERE timestamp >= $((NOW-86400));")
STATS_V6="0|0|0"
[ "$ENABLE_IPV6" != true ] || STATS_V6=$(sqlite3 "$DB_FILE" "SELECT AVG(ping),AVG(jitter),AVG(loss) FROM stats_v6 WHERE timestamp >= $((NOW-86400));")
PING_JS=${AVG_PING/NULL/null}; JITTER_JS=${JITTER/NULL/null}
PING6_JS=${AVG_PING_V6/NULL/null}; JITTER6_JS=${JITTER_V6/NULL/null}
cat <<EOF > "$DATA_TMP"
window.PING_DATA = {
    updated: "$DATE_UPDATE",
    config: { ipv6: $JS_V6_CONFIG },
    targets: { v4: "$PING_TARGET", v6: "$PING_TARGET_V6" },
    current: {
        v4: { ping: $PING_JS, jitter: $JITTER_JS, loss: $LOSS },
        v6: { ping: $PING6_JS, jitter: $JITTER6_JS, loss: $LOSS_V6 }
    },
    averages: {
        v4: { p: "$(echo $STATS_V4 | cut -d'|' -f1 | awk '{printf "%.2f",$1}')", j: "$(echo $STATS_V4 | cut -d'|' -f2 | awk '{printf "%.2f",$1}')", l: "$(echo $STATS_V4 | cut -d'|' -f3 | awk '{printf "%.2f",$1}')" },
        v6: { p: "$(echo $STATS_V6 | cut -d'|' -f1 | awk '{printf "%.2f",$1}')", j: "$(echo $STATS_V6 | cut -d'|' -f2 | awk '{printf "%.2f",$1}')", l: "$(echo $STATS_V6 | cut -d'|' -f3 | awk '{printf "%.2f",$1}')" }
    },
    periods: {v4: {$RANGES_V4}, v6: {$RANGES_V6}},
    history: {$HIST_V4${HIST_V6:+,}$HIST_V6}
};
EOF
chmod 644 "$DATA_TMP" || { rm -f "$DATA_TMP"; exit 1; }
mv "$DATA_TMP" "$DATA_JS"
echo "Done."

# ==============================================================================
# GENERATE STATIC HTML
# ==============================================================================
HTML_FILE="$WEB_DIR/index.html"
# Force regeneration to apply UI changes if requested
if [ ! -f "$HTML_FILE" ] || [ "$FORCE_HTML_GEN" = "true" ] || ! grep -q "KT-PING-2.0.2" "$HTML_FILE"; then
    echo " - Generating new HTML template (Keenetic UI)..."
cat <<'HTML_EOF' > "$HTML_FILE"
<!DOCTYPE html>
<html lang="en"><!-- KT-PING-2.0.2 -->
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Keenetic Dual-Stack Ping Monitor</title>
    <link rel="icon" type="image/svg+xml" href="/assets/keentool.svg?v=1.0.0">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    
    <script src="chart.js"></script>
    <script src="chartjs-adapter-date-fns.js"></script>
    <script src="chartjs-plugin-zoom.js"></script>

    <style>
        :root { 
            /* === KEENETIC OFFICIAL LIGHT THEME === */
            --dashboard-background: #EDEEF0;
            --background: #fff;
            --primary-text: #000;
            --text-gray: #6e6e6e;
            --primary-color: #0097dc;
            --stroke: #bdb7b7;
            --box-shadow-1: 0 5px 20px rgb(0 0 0 / 5%);
            --dashboard-card-border: transparent;
            
            --blue: #0097dc; 
            --orange: #fd7e14; 
            --red: #de3d3d; 
            --teal: #20c997; 
            --purple: #6f42c1; 
            --darkred: #b02a37; 
        }
        
        @media (prefers-color-scheme: dark) { 
            :root { 
                /* === KEENETIC OFFICIAL DARK THEME === */
                --dashboard-background: #1b2434;
                --background: #243146; 
                --primary-text: #c2c2c2;
                --text-gray: #949b9f;
                --stroke: #4d545f;
                --box-shadow-1: 0 0 18px 0 #06080b;
                --dashboard-card-border: #4d545f;

                --blue: #77bce4;
                --red: #ea4c4c;
            } 
        }

        body { 
            font-family: 'Roboto', -apple-system, sans-serif; 
            font-size: 14px;
            background: var(--dashboard-background); 
            color: var(--primary-text); 
            padding: 24px; 
            margin: 0; 
            -webkit-font-smoothing: antialiased;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        
        /* HEADER */
        .status-bar { 
            display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; margin-bottom: 24px; gap: 15px;
        }
        .header-title { margin: 0; font-weight: 700; display: flex; align-items: center; gap: 12px; font-size: 20px; text-transform: uppercase; }
        .btn-home { text-decoration: none; font-size: 20px; border-right: 1px solid var(--stroke); padding-right: 12px; transition: opacity 0.2s; color: var(--primary-text); }
        .btn-home:hover { opacity: 0.7; }
        
        .status-controls { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
        
        /* Refresh Dropdown */
        .refresh-wrapper { position: relative; display: inline-flex; }
        .refresh-select { 
            appearance: none; -webkit-appearance: none; 
            background: var(--background); color: var(--text-gray); 
            border: 1px solid var(--stroke); padding: 4px 28px 4px 12px; 
            border-radius: 4px; font-size: 14px; font-family: inherit;
            cursor: pointer; outline: none; transition: all 0.2s; 
        }
        .refresh-select:hover, .refresh-select:focus { border-color: var(--primary-color); color: var(--primary-text); }
        .refresh-arrow {
            position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
            pointer-events: none; font-size: 10px; color: var(--stroke);
        }

        .btn-refresh { 
            background-color: transparent; color: var(--primary-color); border: 1px solid var(--stroke); 
            padding: 4px 16px; border-radius: 4px; cursor: pointer; text-decoration: none; 
            font-size: 13px; font-weight: 500; font-family: inherit; transition: all 0.2s;
        }
        .btn-refresh:hover { border-color: var(--primary-color); }
        
        /* SECTION TITLES */
        .section-header {
            display: flex; align-items: center; flex-wrap: wrap; gap: 10px;
            font-size: 16px; font-weight: 500; text-transform: uppercase; color: var(--primary-text);
            margin: 32px 0 16px 0; padding-left: 12px;
        }
        .section-header.v4 { border-left: 4px solid var(--blue); }
        .section-header.v6 { border-left: 4px solid var(--teal); }
        
        .badge { background: var(--background); border: 1px solid var(--stroke); padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 400; color: var(--text-gray); }
        .samples { font-size: 12px; font-weight: 400; color: var(--text-gray); margin-left: 4px; }

        /* CONTENT GRIDS */
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 24px; margin-bottom: 24px; }
        
        .card { 
            background: var(--background); padding: 20px 24px; border-radius: 8px; 
            box-shadow: var(--box-shadow-1); border: 1px solid var(--dashboard-card-border); 
            display: flex; flex-direction: column; gap: 4px;
        }
        .card h2 { margin: 0; font-size: 12px; text-transform: uppercase; color: var(--text-gray); font-weight: 500; }
        .val { font-size: 28px; font-weight: 700; line-height: 1.2; }
        .avg { font-size: 12px; color: var(--text-gray); font-weight: 400; margin-top: 4px;}
        
        .chart-box { 
            background: var(--background); padding: 20px 24px; border-radius: 8px; margin-bottom: 24px; 
            box-shadow: var(--box-shadow-1); border: 1px solid var(--dashboard-card-border); 
        }
        .chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; border-bottom: 1px solid var(--stroke); padding-bottom: 12px; }
        .chart-title { font-weight: 500; font-size: 14px; text-transform: uppercase; }
        
        /* Toggle Switch for Log Scale */
        .log-toggle-wrapper { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--text-gray); cursor: pointer; }
        .log-toggle-input { display: none; }
        .log-toggle-track {
            width: 32px; height: 16px; background-color: var(--stroke); border-radius: 10px;
            position: relative; transition: background-color 0.2s;
        }
        .log-toggle-thumb {
            width: 12px; height: 12px; background-color: #fff; border-radius: 50%;
            position: absolute; top: 2px; left: 2px; transition: transform 0.2s;
        }
        .log-toggle-input:checked + .log-toggle-track { background-color: var(--primary-color); }
        .log-toggle-input:checked + .log-toggle-track .log-toggle-thumb { transform: translateX(16px); }

        canvas { touch-action: pan-y !important; height: 220px; width: 100%; }
        .zoom-hint { font-weight: 400; font-size: 11px; color: var(--text-gray); margin-left: 8px; text-transform: none; letter-spacing: 0;}
        
        @media(max-width: 768px) {
            body { padding: 16px; }
            .status-bar { flex-direction: column; text-align: center; } 
            .header-title { justify-content: center; }
            .status-controls { width: 100%; justify-content: center; }
        }
        .status-controls .kt-peaks-control { margin: 0; font-size: 12px; white-space: nowrap; }
    </style>
<script src="/assets/keentool-format.js?v=1.0.0"></script>
<link rel="stylesheet" href="/assets/keentool-ui.css?v=1.0.0">
<script defer src="/assets/keentool-ui.js?v=1.0.1"></script>
</head>
<body class="kt-ui" data-kt-page="ping">
    <div class="container">
        <div class="status-bar">
            <h2 class="header-title">
                <a href="../index.html" class="btn-home" title="Back to Dashboard">🏠</a>
                <span>Connection Monitor</span>
            </h2>
            <div class="status-controls">
                <div style="font-size: 14px; color: var(--text-gray);">Last Update: <span id="lastUpdate" style="font-weight:500; color:var(--primary-text)">Loading...</span></div>
                <div class="refresh-wrapper">
                    <select id="history_range" class="refresh-select" aria-label="History range" title="Select the time range shown in charts and averages" onchange="changeHistory()">
                        <option value="1">History: 1 hour</option>
                        <option value="24" selected>History: 1 day</option>
                        <option value="7">History: 7 days</option>
                        <option value="30">History: 30 days</option>
                        <option value="max">History: MAX</option>
                    </select>
                    <span class="refresh-arrow">▼</span>
                </div>
                <label class="kt-list-note kt-peaks-control" title="Show the maximum latency and packet loss in each time bucket, in addition to the mean"><input type="checkbox" id="show_peaks" onchange="changeHistory()"> Show latency and packet-loss peaks</label>
            </div>
        </div>

        <div class="section-header v4">
            IPv4 Target: <span class="badge" id="targetV4"></span> 
            <span class="samples" title="Samples are original measurements; chart points are time-bucket averages." id="countV4"></span>
        </div>
        
        <div class="grid">
            <div class="card"><h2>Latency</h2><div class="val" style="color:var(--blue)" id="v4_p">-</div><div class="avg">Avg: <span id="v4_avg_p">-</span></div></div>
            <div class="card"><h2>Jitter</h2><div class="val" style="color:var(--primary-text)" id="v4_j">-</div><div class="avg">Avg: <span id="v4_avg_j">-</span></div></div>
            <div class="card"><h2>Loss</h2><div class="val" style="color:var(--primary-text)" id="v4_l">-</div><div class="avg">Avg: <span id="v4_avg_l">-</span></div></div>
        </div>
        
        <div class="chart-box">
            <div class="chart-header">
                <div class="chart-title" style="color:var(--blue)">Latency (ms) <span class="zoom-hint">(Select area to zoom)</span></div>
                <label class="log-toggle-wrapper">
                    <input type="checkbox" class="log-toggle-input" autocomplete="off" onchange="toggleLog(this, 'c_p4')">
                    <div class="log-toggle-track"><div class="log-toggle-thumb"></div></div>
                    Log Scale
                </label>
            </div>
            <div style="position:relative; height:220px"><canvas id="c_p4"></canvas></div>
        </div>
        <div class="chart-box">
            <div class="chart-header">
                <div class="chart-title" style="color:var(--orange)">Jitter (ms)</div>
                <label class="log-toggle-wrapper">
                    <input type="checkbox" class="log-toggle-input" autocomplete="off" onchange="toggleLog(this, 'c_j4')">
                    <div class="log-toggle-track"><div class="log-toggle-thumb"></div></div>
                    Log Scale
                </label>
            </div>
            <div style="position:relative; height:220px"><canvas id="c_j4"></canvas></div>
        </div>
        <div class="chart-box">
            <div class="chart-header"><div class="chart-title" style="color:var(--red)">Packet Loss (%)</div></div>
            <div style="position:relative; height:220px"><canvas id="c_l4"></canvas></div>
        </div>

        <div id="ipv6_section">
            <div class="section-header v6">
                IPv6 Target: <span class="badge" id="targetV6"></span>
                <span class="samples" title="Samples are original measurements; chart points are time-bucket averages." id="countV6"></span>
            </div>
            
            <div class="grid">
                <div class="card"><h2>Latency</h2><div class="val" style="color:var(--teal)" id="v6_p">-</div><div class="avg">Avg: <span id="v6_avg_p">-</span></div></div>
                <div class="card"><h2>Jitter</h2><div class="val" style="color:var(--primary-text)" id="v6_j">-</div><div class="avg">Avg: <span id="v6_avg_j">-</span></div></div>
                <div class="card"><h2>Loss</h2><div class="val" style="color:var(--primary-text)" id="v6_l">-</div><div class="avg">Avg: <span id="v6_avg_l">-</span></div></div>
            </div>

            <div class="chart-box">
                <div class="chart-header">
                    <div class="chart-title" style="color:var(--teal)">Latency (ms) <span class="zoom-hint">(Select area to zoom)</span></div>
                    <label class="log-toggle-wrapper">
                        <input type="checkbox" class="log-toggle-input" autocomplete="off" onchange="toggleLog(this, 'c_p6')">
                        <div class="log-toggle-track"><div class="log-toggle-thumb"></div></div>
                        Log Scale
                    </label>
                </div>
                <div style="position:relative; height:220px"><canvas id="c_p6"></canvas></div>
            </div>
            <div class="chart-box">
                <div class="chart-header">
                    <div class="chart-title" style="color:var(--purple)">Jitter (ms)</div>
                    <label class="log-toggle-wrapper">
                        <input type="checkbox" class="log-toggle-input" autocomplete="off" onchange="toggleLog(this, 'c_j6')">
                        <div class="log-toggle-track"><div class="log-toggle-thumb"></div></div>
                        Log Scale
                    </label>
                </div>
                <div style="position:relative; height:220px"><canvas id="c_j6"></canvas></div>
            </div>
            <div class="chart-box">
                <div class="chart-header"><div class="chart-title" style="color:var(--darkred)">Packet Loss (%)</div></div>
                <div style="position:relative; height:220px"><canvas id="c_l6"></canvas></div>
            </div>
        </div>
    </div>

    <p style="color:var(--text-gray);font-size:12px">Averages use all original samples in the selected period. Chart points group samples over time; MAX covers retained history.</p>
    <div id="ping_coverage" class="kt-list-note" style="white-space:pre-line"></div>
    <script src="data.js"></script>

    <script>
        const commonOptions = {
            locale:window.KTFormat.locale,
            responsive: true, maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { display: false },
                zoom: { zoom: { drag: { enabled: true, backgroundColor: 'rgba(54, 162, 235, 0.2)' }, mode: 'x' } },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            const d = new Date(context[0].parsed.x);
                            return d.toLocaleString([], { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
                        }
                    }
                }
            },
            scales: { 
                x: { 
                    type: 'time', 
                    time: { tooltipFormat: 'dd/MM/yyyy HH:mm', displayFormats: { minute: 'HH:mm', hour: 'dd/MM HH:mm', day: 'dd/MM' } }, 
                    ticks: { maxRotation: 0, autoSkip: true, color: '#6e6e6e' },
                    grid: { color: 'rgba(110,110,110,0.1)' }
                }, 
                y: { 
                    beginAtZero: true,
                    ticks: { color: '#6e6e6e' },
                    grid: { color: 'rgba(110,110,110,0.1)' }
                } 
            },
            elements: { point: { radius: 1, hoverRadius: 5 } }
        };

        function toggleLog(cb, id) { 
            const c = Chart.getChart(id); 
            if(c) { 
                c.options.scales.y = cb.checked ? { type: 'logarithmic', min: 0.1, beginAtZero: false, ticks: { color: '#6e6e6e' }, grid: { color: 'rgba(110,110,110,0.1)' } } : { type: 'linear', beginAtZero: true, ticks: { color: '#6e6e6e' }, grid: { color: 'rgba(110,110,110,0.1)' } };
                c.update(); 
            } 
        }


        

        function selectedHistory(f) { const r=(document.getElementById('history_range')||{}).value||'24'; return window.PING_DATA.history[f+(r==='24'?'':'_'+r)]||[]; }
        function changeHistory() { localStorage.setItem('ping_show_peaks', document.getElementById('show_peaks').checked ? '1' : '0'); localStorage.setItem('ping_history_range', document.getElementById('history_range').value); document.querySelectorAll('canvas').forEach(c=>{const chart=Chart.getChart(c);if(chart)chart.destroy();}); render(); }
        function render() {
            if(typeof window.PING_DATA === 'undefined') return;
            const d = window.PING_DATA;
            const range = document.getElementById('history_range').value;
            const period = f => (d.periods[f] || {})[range] || {samples:0,p:null,j:null,l:null};
            const coverageLine = (family, label) => {
                const selected = period(family);
                if (!selected.samples || selected.first == null || selected.last == null) return label + ' coverage: No samples in this period';
                return label + ' coverage: ' + new Date(selected.first * 1000).toLocaleString('en-GB') + ' — ' + new Date(selected.last * 1000).toLocaleString('en-GB');
            };
            const coverage = [coverageLine('v4', 'IPv4')];
            if (d.config.ipv6) coverage.push(coverageLine('v6', 'IPv6'));
            document.getElementById('ping_coverage').textContent = coverage.join('\n');
            const metric = (v, unit) => v === null ? 'Unavailable' : window.KTFormat.number(v,2,2) + unit;

            // HIDE IPv6 IF DISABLED IN CONFIG
            if (!d.config.ipv6) {
                document.getElementById('ipv6_section').style.display = 'none';
            }

            document.getElementById('lastUpdate').innerText = d.updated;
            document.getElementById('targetV4').innerText = d.targets.v4;
            
            // Populate Sample Counts
            document.getElementById('countV4').innerText = "(" + window.KTFormat.integer(period('v4').samples) + " samples; " + window.KTFormat.integer(selectedHistory('v4').length) + " chart points)";

            // Update DOM V4
            document.getElementById('v4_p').innerText = (d.current.v4.ping === null ? "Unavailable" : window.KTFormat.number(d.current.v4.ping,0,3) + " ms");
            document.getElementById('v4_j').innerText = (d.current.v4.jitter === null ? "Unavailable" : window.KTFormat.number(d.current.v4.jitter,0,3) + " ms");
            document.getElementById('v4_l').innerText = window.KTFormat.number(d.current.v4.loss,0,3) + " %";
            document.getElementById('v4_l').style.color = Number(d.current.v4.loss) > 0 ? 'var(--red)' : 'var(--primary-text)';
            document.getElementById('v4_avg_p').innerText = metric(period('v4').p, ' ms');
            document.getElementById('v4_avg_j').innerText = metric(period('v4').j, ' ms');
            document.getElementById('v4_avg_l').innerText = metric(period('v4').l, ' %');

            const createChart = (id, dArr, color, isBar=false) => {
                if(!document.getElementById(id)) return; // Skip if element hidden/missing
                const config={
                    type: isBar ? 'bar' : 'line',
                    data: { datasets: [{ 
                        label: 'Mean', data: dArr, 
                        borderColor: color, backgroundColor: color, 
                        borderWidth: 1.5, fill: false 
                    }, ...(document.getElementById('show_peaks').checked && /^c_[pl]/.test(id) ? [{label:'Peak',type:'line',data:dArr.map(i=>({x:i.x,y:id.startsWith('c_p')?i.peak:i.maxLoss})),borderColor:'#de3d3d',backgroundColor:'#de3d3d',borderDash:[4,3],borderWidth:1,fill:false,pointRadius:0}] : [])] },
                    options: commonOptions
                };
                const existing=Chart.getChart(id);
                if(existing){existing.data=config.data;existing.update('none');}
                else new Chart(document.getElementById(id),config);
            };

            const isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
            const cBlue = isDark ? '#77bce4' : '#0097dc';
            const cRed = isDark ? '#ea4c4c' : '#de3d3d';

            createChart('c_p4', selectedHistory('v4').map(i=>({...i,x:i.x, y:i.p})), cBlue);
            createChart('c_j4', selectedHistory('v4').map(i=>({...i,x:i.x, y:i.j})), '#fd7e14');
            createChart('c_l4', selectedHistory('v4').map(i=>({...i,x:i.x, y:i.l})), cRed, true);

            // ONLY RENDER IPv6 IF ENABLED
            if (d.config.ipv6) {
                document.getElementById('targetV6').innerText = d.targets.v6;
                document.getElementById('countV6').innerText = "(" + window.KTFormat.integer(period('v6').samples) + " samples; " + window.KTFormat.integer(selectedHistory('v6').length) + " chart points)";
                
                document.getElementById('v6_p').innerText = (d.current.v6.ping === null ? "Unavailable" : window.KTFormat.number(d.current.v6.ping,0,3) + " ms");
                document.getElementById('v6_j').innerText = (d.current.v6.jitter === null ? "Unavailable" : window.KTFormat.number(d.current.v6.jitter,0,3) + " ms");
                document.getElementById('v6_l').innerText = window.KTFormat.number(d.current.v6.loss,0,3) + " %";
            document.getElementById('v6_l').style.color = Number(d.current.v6.loss) > 0 ? 'var(--red)' : 'var(--primary-text)';
                document.getElementById('v6_avg_p').innerText = metric(period('v6').p, ' ms');
                document.getElementById('v6_avg_j').innerText = metric(period('v6').j, ' ms');
                document.getElementById('v6_avg_l').innerText = metric(period('v6').l, ' %');

                createChart('c_p6', selectedHistory('v6').map(i=>({...i,x:i.x, y:i.p})), '#20c997');
                createChart('c_j6', selectedHistory('v6').map(i=>({...i,x:i.x, y:i.j})), '#6f42c1');
                createChart('c_l6', selectedHistory('v6').map(i=>({...i,x:i.x, y:i.l})), '#b02a37', true);
            }

            document.querySelectorAll('canvas').forEach(c => { c.ondblclick = () => Chart.getChart(c).resetZoom(); });
            
        }
        window.ktRefreshPage=async()=>{
            const response=await fetch('data.js?t='+Date.now(),{cache:'no-store'});
            if(!response.ok)throw Error('Connection data unavailable');
            window.eval(await response.text());
            render();
        };
        document.getElementById('show_peaks').checked = localStorage.getItem('ping_show_peaks') === '1';
        const savedRange = localStorage.getItem('ping_history_range');
        if (['1','24','7','30','max'].includes(savedRange)) document.getElementById('history_range').value = savedRange;
        render();
    </script>
<footer class="kt-page-footer">&copy; <span data-kt-year>2026</span> mattheweli<span class="kt-footer-meta">Pingtool 2.0.2</span></footer>
</body>
</html>
HTML_EOF
chmod 644 "$HTML_FILE"
fi

