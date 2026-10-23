#!/opt/bin/bash
# TRAFFIC MANAGER v2.0.1
# Release: 2026-10-22 | Stable. See CHANGELOG.md for release details.

# ==============================================================================
# TRAFFIC MANAGER v1.1.4 - Keenetic UI Refactor
# Features:
# - FEAT: Added support for custom interface aliases (e.g., WAN, LAN) via Keentool.
# - FIX: Removed literal '\n' text artifacts from HTML generation (tabs and scripts).
# - OPTIMIZATION: HTML generated ONLY on first run or forced. Cache busting via JS.
# - FIX: Forces system Timezone to prevent 1-hour offset in hourly stats.
# - UI: Dashboard redesigned to match native KeeneticOS styles.
# - NEW: Multi-Interface support via single dashboard with tabs.
# ==============================================================================

PATH=${KT_PATH:-/opt/bin:/opt/sbin:/bin:/sbin:/usr/bin:/usr/sbin}
# Traffic Manager 2.0.1
. "${KT_COMMON:-/opt/lib/keentool/common.sh}" || exit 1
kt_init traffic-manager || exit $?


# --- FORCE TIMEZONE ---
if [ -f /etc/TZ ]; then 
    export TZ=$(cat /etc/TZ)
elif [ -f /opt/etc/TZ ]; then 
    export TZ=$(cat /opt/etc/TZ)
fi

VNSTAT="${KT_VNSTAT:-/opt/bin/vnstat}"
BASE_DIR="/opt/var/www"
OUTDIR="${2:-$BASE_DIR/vnstat}"
FORCE_HTML=false
IFACES=""; POSITIONAL=()
for arg in "$@"; do
    case "$arg" in force|--force) FORCE_HTML=true ;; *) POSITIONAL+=("$arg") ;; esac
done
IFACES="${POSITIONAL[0]:-}"; OUTDIR="${POSITIONAL[1]:-${KT_TRAFFIC_WEB:-$BASE_DIR/vnstat}}"


# --- NEW: LOAD ALIASES ---
ALIASES=""
DASH_CONF="/opt/etc/keentool/dashboard.conf"
if [ -f "$DASH_CONF" ]; then
    # Extract the configuration value.
    MONTHLY_QUOTA_GB=$(sed -n 's/^MONTHLY_QUOTA_GB="\([0-9.]*\)"/\1/p' "$DASH_CONF")
    ALIASES=$(grep "^VNSTAT_ALIASES=" "$DASH_CONF" | cut -d'"' -f2)
fi

# --- 1. CONFIGURATION & CHECKS ---
if [ -z "$IFACES" ]; then
  IFACES=$($VNSTAT --dblist 2>/dev/null | grep -v "Database" | grep -v "^$" | head -n 1 | awk '{print $1}')
fi
[ -z "$IFACES" ] && { echo "ERROR: No interfaces found."; exit 1; }

mkdir -p "$OUTDIR"
if [ ! -s "$OUTDIR/chart.js" ]; then
    if [ -s "$BASE_DIR/ping/chart.js" ]; then cp "$BASE_DIR/ping/chart.js" "$OUTDIR/chart.js"
    else kt_download 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js' "$OUTDIR/chart.js" || { echo 'Chart.js unavailable' >&2; exit 1; }; fi
fi
chmod 644 "$OUTDIR/chart.js" || exit 1
HTMLFILE="${OUTDIR}/index.html"

SCRIPT_INCLUDES="<script>window.MONTHLY_QUOTA_GB=${MONTHLY_QUOTA_GB:-0};</script>"
TABS_HTML=""
FIRST_IFACE=""

# --- 2. UPDATE DB & EXPORT JSON ---
# Create an array of aliases to use in the loop
set -- $ALIASES
IDX=1

js_escape() { sed 's/\\/\\\\/g; s/"/\\"/g; s/</\\u003c/g; s/>/\\u003e/g'; }
for IFACE in $IFACES; do
    [[ "$IFACE" =~ ^[a-zA-Z0-9_.:-]+$ ]] || { echo "Invalid interface: $IFACE" >&2; exit 1; }

    [ -z "$FIRST_IFACE" ] && FIRST_IFACE="$IFACE"
    
    $VNSTAT -i "$IFACE" -u >/dev/null 2>&1
    
    echo "Exporting traffic data for $IFACE..."
    JSON_DATA=$($VNSTAT -i "$IFACE" --json);JSON_RC=$?
    DATAFILE="${OUTDIR}/${IFACE}_data.js"

    if [ "$JSON_RC" = 0 ] && [ -n "$JSON_DATA" ] && kt_json_valid "$JSON_DATA"; then
        TMP_DATA=$(mktemp "$OUTDIR/.traffic.XXXXXX") || exit 1
        printf 'window.TRAFFIC_DATA = window.TRAFFIC_DATA || {}; window.TRAFFIC_DATA["%s"] = %s;\n' "$IFACE" "$JSON_DATA" > "$TMP_DATA"
        chmod 644 "$TMP_DATA" || { rm -f "$TMP_DATA"; exit 1; }
        mv "$TMP_DATA" "$DATAFILE"
    else
        echo "WARN: vnStat export failed for $IFACE; retaining last good data" >&2
        if [ ! -f "$DATAFILE" ]; then printf 'window.TRAFFIC_DATA=window.TRAFFIC_DATA||{};window.TRAFFIC_DATA["%s"]={error:true};\n' "$IFACE" > "$DATAFILE"; fi
    fi
    
    [ ! -f "$DATAFILE" ] || chmod 644 "$DATAFILE" || exit 1

    # Get the corresponding alias; if missing, fall back to the interface name
    ALIAS_NAME="${!IDX}"
    [ -z "$ALIAS_NAME" ] && ALIAS_NAME="$IFACE"
    
    SCRIPT_INCLUDES="${SCRIPT_INCLUDES}<script>document.write('<script src=\"${IFACE}_data.js?v=' + Date.now() + '\"><' + '/script>');</script> "
    ALIAS_JS=$(printf '%s' "$ALIAS_NAME" | js_escape)
    TABS_HTML="${TABS_HTML}<button class=\"tab-btn\" id=\"tab_${IFACE}\" data-iface=\"${IFACE}\"></button> "
    SCRIPT_INCLUDES="$SCRIPT_INCLUDES<script>window.TRAFFIC_ALIASES=window.TRAFFIC_ALIASES||{};window.TRAFFIC_ALIASES[\"$IFACE\"]=\"$ALIAS_JS\";</script> "
    
    IDX=$((IDX + 1))
done

# --- 3. GENERATE HTML ---
SIGNATURE=$(printf '%s|%s' "$IFACES" "$ALIASES|${MONTHLY_QUOTA_GB:-0}|2.0.1" | sha256sum)
if [ ! -f "$HTMLFILE" ] || [ "$FORCE_HTML" = true ] || [ "$(cat "$OUTDIR/.signature" 2>/dev/null)" != "$SIGNATURE" ]; then
    echo "Generating HTML Dashboard..."
    
HTML_TMP=$(mktemp "$OUTDIR/.html.XXXXXX") || exit 1
cat <<EOF > "$HTML_TMP"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Keenetic Traffic Monitor</title>
    <link rel="icon" type="image/svg+xml" href="/assets/keentool.svg?v=1.0.0">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <script src="chart.js"></script> 
    
    <style>
        :root { 
            /* === KEENETIC OFFICIAL LIGHT THEME === */
            --dashboard-background: #EDEEF0;
            --background: #fff;
            --primary-text: #000;
            --text-gray: #6e6e6e;
            --primary-color: #0097dc;
            --primary-color-hover: #007ab3;
            --stroke: #bdb7b7;
            --box-shadow-1: 0 5px 20px rgb(0 0 0 / 5%);
            --dashboard-card-border: transparent;
            --th-bg: #fafafa;
            
            --blue: #0097dc; 
            --green: #198754; 
            --purple: #6f42c1; 
            --orange: #fd7e14;
            --est-color: #6e6e6e;
        }
        
        @media (prefers-color-scheme: dark) { 
            :root { 
                /* === KEENETIC OFFICIAL DARK THEME === */
                --dashboard-background: #1b2434;
                --background: #243146; 
                --primary-text: #c2c2c2;
                --text-gray: #949b9f;
                --primary-color: #0097dc;
                --primary-color-hover: #007ab3;
                --stroke: #4d545f;
                --box-shadow-1: 0 0 18px 0 #06080b;
                --dashboard-card-border: #4d545f;
                --th-bg: #1b2434;
                
                --blue: #77bce4;
                --est-color: #949b9f;
            } 
        }
        
        body { 
            font-family: 'Roboto', -apple-system, sans-serif; 
            background: var(--dashboard-background); 
            color: var(--primary-text); 
            padding: 24px; 
            max-width: 1200px; 
            margin: 0 auto; 
            -webkit-font-smoothing: antialiased;
        }
        
        /* HEADER */
        .status-bar { 
            display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; margin-bottom: 16px; gap: 15px;
        }
        .header-title { margin: 0; font-weight: 700; display: flex; align-items: center; gap: 12px; font-size: 20px; text-transform: uppercase; }
        .btn-home { text-decoration: none; font-size: 20px; border-right: 1px solid var(--stroke); padding-right: 12px; transition: opacity 0.2s; color: var(--primary-text); }
        .btn-home:hover { opacity: 0.7; }
        
        .status-controls { display: flex; align-items: center; gap: 16px; }
        
        .btn-refresh { 
            background-color: transparent; color: var(--primary-color); border: 1px solid var(--stroke); 
            padding: 4px 16px; border-radius: 4px; cursor: pointer; text-decoration: none; 
            font-size: 13px; font-weight: 500; font-family: inherit; transition: all 0.2s;
        }
        .btn-refresh:hover { border-color: var(--primary-color); }

        /* TABS */
        .tabs-container { display: flex; gap: 8px; margin-bottom: 24px; border-bottom: 1px solid var(--stroke); padding-bottom: 12px; overflow-x: auto; -webkit-overflow-scrolling: touch; }
        .tab-btn { background: var(--background); border: 1px solid var(--stroke); padding: 8px 20px; border-radius: 6px; color: var(--primary-text); cursor: pointer; font-size: 14px; font-weight: 500; transition: all 0.2s; white-space: nowrap; }
        .tab-btn:hover { border-color: var(--primary-color); }
        .tab-btn.active { background: var(--primary-color); color: #fff; border-color: var(--primary-color); }

        /* SUMMARY CARDS (Keenetic Style) */
        .summary-card { 
            background: var(--background); border: 1px solid var(--dashboard-card-border); 
            border-radius: 8px; box-shadow: var(--box-shadow-1); margin-bottom: 24px; 
            display: flex; flex-wrap: wrap; overflow: hidden; 
        }
        
        .summary-col { 
            flex: 1; min-width: 180px; padding: 20px; border-right: 1px solid var(--stroke); 
            display: flex; flex-direction: column; align-items: center; justify-content: flex-start; position: relative; 
        }
        .summary-col:last-child { border-right: none; background: rgba(0,0,0,0.01); }
        
        .sum-title { font-size: 12px; font-weight: 500; text-transform: uppercase; color: var(--primary-text); margin-bottom: 16px; width: 100%; text-align: left; padding-bottom: 8px; border-bottom: 1px solid var(--stroke); }
        .sum-body { display: flex; gap: 16px; align-items: center; width: 100%; justify-content: space-between; }
        .sum-chart { width: 75px; height: 75px; position: relative; flex-shrink: 0; }
        .sum-data { display: flex; flex-direction: column; gap: 6px; font-size: 13px; min-width: 90px; flex-grow: 1;}
        .stat-row { display: flex; justify-content: space-between; }
        .stat-est { color: var(--est-color); font-weight: 500; font-style: italic; font-size: 12px; margin-top: 4px; display: flex; justify-content: space-between; border-top: 1px dashed var(--stroke); padding-top: 6px; }
        
        .c-rx { color: var(--blue); } .c-tx { color: var(--green); } 
        .c-rx-old { color: var(--purple); } .c-tx-old { color: var(--orange); }
        .c-tot { font-weight: 700; color: var(--primary-text);}

        /* TABLES & CARDS */
        .card { 
            background: var(--background); border-radius: 8px; border: 1px solid var(--dashboard-card-border); 
            margin-bottom: 24px; box-shadow: var(--box-shadow-1); display: flex; flex-direction: column; overflow: hidden;
        }
        .card-head { 
            padding: 16px 20px; font-size: 14px; font-weight: 500; text-transform: uppercase; 
            color: var(--primary-text); letter-spacing: 0; border-bottom: 1px solid var(--stroke);
        }
        
        .table-responsive { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; }
        
        table { width: 100%; border-collapse: collapse; font-size: 13px; table-layout: fixed; min-width: 500px; }
        th { text-align: right; padding: 12px 16px; color: var(--text-gray); border-bottom: 1px solid var(--stroke); font-weight: 500; white-space: nowrap; background: var(--th-bg); font-size: 11px; text-transform: uppercase; }
        
        th:first-child { text-align: left; width: 100px; }
        th.th-graph { text-align: left; width: 25%; } 
        
        td { padding: 10px 16px; border-bottom: 1px solid var(--stroke); text-align: right; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: var(--primary-text);}
        td:first-child { text-align: left; font-weight: 400; color: var(--text-gray); }
        tr:last-child td { border-bottom: none; }
        
        .bar-container { width: 100%; height: 6px; background: var(--stroke); border-radius: 3px; display: flex; overflow: hidden; margin-top: 2px;}
        .bar-rx { height: 100%; background: var(--blue); opacity: 0.9; }
        .bar-tx { height: 100%; background: var(--green); opacity: 0.9; }
        
        .row-est td { color: var(--est-color); font-style: italic; background: rgba(0,0,0,0.02); }
        .row-est .bar-rx { opacity: 0.5; } .row-est .bar-tx { opacity: 0.5; }

        .loading { text-align: center; padding: 50px; color: var(--text-gray); font-size: 14px;}

        @media(max-width: 900px) { 
            .summary-col { border-right: none; border-bottom: 1px solid var(--stroke); } 
            .summary-col:last-child { border-bottom: none; } 
        }
        
        @media(max-width: 768px) {
            body { padding: 16px; }
            .status-bar { flex-direction: column; text-align: center; } 
            .header-title { justify-content: center; }
            .status-controls { width: 100%; justify-content: center; }
            th, td { padding: 8px 10px; font-size: 12px; }
            th:first-child { width: 85px; }
            th.th-graph { width: 20%; }
        }

        /* Match numeric heading alignment to its data cells; override the shared theme. */
        .kt-ui[data-kt-page="traffic"] th.th-number { text-align: right; }
        .kt-ui[data-kt-page="traffic"] th:first-child,
        .kt-ui[data-kt-page="traffic"] td:first-child,
        .kt-ui[data-kt-page="traffic"] th.th-graph,
        .kt-ui[data-kt-page="traffic"] td.td-graph { text-align: left; }
    </style>
<script src="/assets/keentool-format.js?v=1.0.0"></script>
<link rel="stylesheet" href="/assets/keentool-ui.css?v=1.0.0">
<script defer src="/assets/keentool-ui.js?v=1.0.1"></script>
</head>
<body class="kt-ui" data-kt-page="traffic"><div id="data_freshness" style="padding:8px;text-align:center"></div><div id="data_quota" style="padding:4px;text-align:center"></div>

    <div class="status-bar">
        <h2 class="header-title">
            <a href="../index.html" class="btn-home" title="Back to Dashboard">🏠</a>
            <span>Traffic Monitor</span>
        </h2>
        <div class="status-controls">
            <label>Interface <select id="traffic_interface" class="refresh-select" aria-label="Traffic interface" onchange="renderData(this.value)"></select></label>
            <span id="iface_name" style="font-weight:500; color:var(--primary-color); font-size:14px; border:1px solid var(--stroke); padding: 4px 10px; border-radius: 4px;">-</span>
        </div>
    </div>
    
    <div class="tabs-container" id="tabs_container">
        $TABS_HTML
    </div>

    <div id="loading" class="loading">Loading interface data...</div>

    <div id="content" style="display:none">
        
        <p class="sum-chart-note">Actual traffic: blue = received, green = sent. Estimates are shown separately.</p>
        <div class="summary-card">
            <div class="summary-col">
                <div class="sum-title">Today</div>
                <div class="sum-body">
                    <div class="sum-data">
                        <div class="stat-row"><span style="color:var(--text-gray)">Rx:</span> <span class="c-rx" id="s_td_rx">-</span></div>
                        <div class="stat-row"><span style="color:var(--text-gray)">Tx:</span> <span class="c-tx" id="s_td_tx">-</span></div>
                        <div class="stat-row" style="margin-top:2px"><span style="color:var(--text-gray)">Tot:</span> <span class="c-tot" id="s_td_tot">-</span></div>
                        <div class="stat-est"><span>Est:</span> <span id="s_td_est">-</span></div>
                    </div>
                    <div class="sum-chart"><canvas id="pie_today"></canvas></div>
                </div>
            </div>
            <div class="summary-col">
                <div class="sum-title">Yesterday</div>
                <div class="sum-body">
                    <div class="sum-data">
                        <div class="stat-row"><span style="color:var(--text-gray)">Rx:</span> <span class="c-rx-old" id="s_yd_rx">-</span></div>
                        <div class="stat-row"><span style="color:var(--text-gray)">Tx:</span> <span class="c-tx-old" id="s_yd_tx">-</span></div>
                        <div class="stat-row" style="margin-top:2px"><span style="color:var(--text-gray)">Tot:</span> <span class="c-tot" id="s_yd_tot">-</span></div>
                    </div>
                    <div class="sum-chart"><canvas id="pie_yesterday"></canvas></div>
                </div>
            </div>
            <div class="summary-col">
                <div class="sum-title" id="lbl_tm">Month</div>
                <div class="sum-body">
                    <div class="sum-data">
                        <div class="stat-row"><span style="color:var(--text-gray)">Rx:</span> <span class="c-rx" id="s_tm_rx">-</span></div>
                        <div class="stat-row"><span style="color:var(--text-gray)">Tx:</span> <span class="c-tx" id="s_tm_tx">-</span></div>
                        <div class="stat-row" style="margin-top:2px"><span style="color:var(--text-gray)">Tot:</span> <span class="c-tot" id="s_tm_tot">-</span></div>
                        <div class="stat-est"><span>Est:</span> <span id="s_tm_est">-</span></div>
                    </div>
                    <div class="sum-chart"><canvas id="pie_month"></canvas></div>
                </div>
            </div>
            <div class="summary-col">
                <div class="sum-title" id="lbl_lm">Last Month</div>
                <div class="sum-body">
                    <div class="sum-data">
                        <div class="stat-row"><span style="color:var(--text-gray)">Rx:</span> <span class="c-rx-old" id="s_lm_rx">-</span></div>
                        <div class="stat-row"><span style="color:var(--text-gray)">Tx:</span> <span class="c-tx-old" id="s_lm_tx">-</span></div>
                        <div class="stat-row" style="margin-top:2px"><span style="color:var(--text-gray)">Tot:</span> <span class="c-tot" id="s_lm_tot">-</span></div>
                    </div>
                    <div class="sum-chart"><canvas id="pie_lmonth"></canvas></div>
                </div>
            </div>
            <div class="summary-col">
                <div class="sum-title">All Time</div>
                <div class="sum-body">
                    <div class="sum-data">
                        <div class="stat-row"><span style="color:var(--text-gray)">Rx:</span> <span class="c-rx" id="s_all_rx">-</span></div>
                        <div class="stat-row"><span style="color:var(--text-gray)">Tx:</span> <span class="c-tx" id="s_all_tx">-</span></div>
                        <div class="stat-row" style="margin-top:2px"><span style="color:var(--text-gray)">Tot:</span> <span class="c-tot" id="s_all_tot">-</span></div>
                        <div style="margin-top:8px; font-size:11px; color:var(--text-gray); text-align:right;">Since:<br><span id="s_created">-</span></div>
                    </div>
                    <div class="sum-chart"><canvas id="pie_total"></canvas></div>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-head">Last 24 Hours</div>
            <div class="table-responsive">
                <table id="tab_hour">
                    <thead><tr><th>Hour</th><th class="th-number">Rx</th><th class="th-number">Tx</th><th class="th-number">Total</th><th class="th-number">Avg Rate</th><th class="th-graph">Volume</th></tr></thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>

        <div class="card">
            <div class="card-head">Daily History</div>
            <div class="table-responsive">
                <table id="tab_day">
                    <thead><tr><th>Date</th><th class="th-number">Rx</th><th class="th-number">Tx</th><th class="th-number">Total</th><th class="th-number">Avg Rate</th><th class="th-graph">Volume</th></tr></thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>

        <div class="card">
            <div class="card-head">Monthly History</div>
            <div class="table-responsive">
                <table id="tab_mon">
                    <thead><tr><th>Month</th><th class="th-number">Rx</th><th class="th-number">Tx</th><th class="th-number">Total</th><th class="th-number">Avg Rate</th><th class="th-graph">Volume</th></tr></thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>

        <div class="card">
            <div class="card-head">Yearly History</div>
            <div class="table-responsive">
                <table id="tab_year">
                    <thead><tr><th>Year</th><th class="th-number">Rx</th><th class="th-number">Tx</th><th class="th-number">Total</th><th class="th-number">Avg Rate</th><th class="th-graph">Volume</th></tr></thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>

        <div class="card">
            <div class="card-head">Top 10 Days</div>
            <div class="table-responsive">
                <table id="tab_top">
                    <thead><tr><th>Date</th><th class="th-number">Rx</th><th class="th-number">Tx</th><th class="th-number">Total</th><th class="th-number">Avg Rate</th><th class="th-graph">Volume</th></tr></thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>

    </div>

    $SCRIPT_INCLUDES
    
    <script>
        // PRESENT COLORS (Blue / Green)
        const COL_RX = 'rgba(0, 151, 220, 0.85)';
        const COL_TX = 'rgba(25, 135, 84, 0.85)';
        const COL_RX_A = 'rgba(0, 151, 220, 0.15)'; // Ghost
        const COL_TX_A = 'rgba(25, 135, 84, 0.15)';

        // PAST COLORS (Purple / Orange)
        const COL_RX_OLD = 'rgba(111, 66, 193, 0.85)';
        const COL_TX_OLD = 'rgba(253, 126, 20, 0.85)';

        window._chartInstances = [];

        function fmt(bytes) {return window.KTFormat.bytes(bytes,1024,2);}
        function fmtBits(bps) {return window.KTFormat.scaled(bps,1000,['bit/s','kbit/s','Mbit/s','Gbit/s','Tbit/s'],2);}

        function pDate(d, type) {
            if(!d) return "-";
            const h = (d.time && d.time.hour !== undefined) ? d.time.hour : d.hour;
            const D = (d.date) ? d.date : d; 
            const mNames = ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
            
            if(type=='h') return \`\${String(h).padStart(2,'0')}:00\`;
            if(type=='d') return \`\${String(D.day).padStart(2,'0')}/\${String(D.month).padStart(2,'0')}\`;
            if(type=='m') return \`\${mNames[D.month]} '\${String(D.year).substr(2)}\`;
            if(type=='mn') return mNames[D.month];
            if(type=='y') return D.year;
            return \`\${String(D.day).padStart(2,'0')}/\${String(D.month).padStart(2,'0')}/\${D.year}\`;
        }

        function calcRate(bytes, dObj, type, dbDate) {
            let secs = 1;
            const D = (dObj.date) ? dObj.date : dObj;
            
            const isCurrent = (
                (type=='d' && D.day == dbDate.getDate() && D.month == dbDate.getMonth()+1 && D.year == dbDate.getFullYear()) ||
                (type=='m' && D.month == dbDate.getMonth()+1 && D.year == dbDate.getFullYear()) ||
                (type=='y' && D.year == dbDate.getFullYear())
            );

            if(isCurrent) {
                if(type=='d') {
                    secs = (dbDate.getHours()*3600) + (dbDate.getMinutes()*60) + dbDate.getSeconds();
                } else if(type=='m') {
                    secs = ((dbDate.getDate()-1)*86400) + (dbDate.getHours()*3600) + (dbDate.getMinutes()*60);
                } else if(type=='y') {
                    const start = new Date(dbDate.getFullYear(), 0, 1);
                    secs = (dbDate - start) / 1000;
                }
                if(secs < 60) secs = 60; 
            } else {
                if(type=='h') secs = 3600;
                else if(type=='d') secs = 86400;
                else if(type=='m') secs = 86400 * 30; 
                else if(type=='y') secs = 86400 * 365;
            }
            return fmtBits((bytes * 8) / secs);
        }

        // FIXED YEAR ESTIMATE LOGIC
        function getEst(current, type, dbDate) {
            let totalSecs = 0; let passedSecs = 0;
            const D = (current.date) ? current.date : current;

            // Strict year check
            if (type === 'y' && D.year !== dbDate.getFullYear()) return null;
            if (type === 'm' && (D.month !== dbDate.getMonth()+1 || D.year !== dbDate.getFullYear())) return null;
            if (type === 'd' && (D.day !== dbDate.getDate() || D.month !== dbDate.getMonth()+1)) return null;

            if (type === 'd') {
                totalSecs = 86400;
                passedSecs = (dbDate.getHours() * 3600) + (dbDate.getMinutes() * 60) + dbDate.getSeconds();
            } else if (type === 'm') {
                const daysInMonth = new Date(dbDate.getFullYear(), dbDate.getMonth()+1, 0).getDate();
                totalSecs = daysInMonth * 86400;
                passedSecs = ((dbDate.getDate()-1) * 86400) + (dbDate.getHours() * 3600) + (dbDate.getMinutes() * 60);
            } else if (type === 'y') {
                const startOfYear = new Date(dbDate.getFullYear(), 0, 1);
                const endOfYear = new Date(dbDate.getFullYear() + 1, 0, 1);
                totalSecs = (endOfYear - startOfYear) / 1000;
                passedSecs = (dbDate - startOfYear) / 1000;
            } else return null;

            if(passedSecs <= 0) return null;
            const factor = totalSecs / passedSecs;
            return { 
                rx: (current.rx * factor) - current.rx, 
                tx: (current.tx * factor) - current.tx,
                date: "estimated"
            };
        }

        function renderData(ifaceName, aliasName) {
            localStorage.setItem('traffic_interface',ifaceName);
            const picker = document.getElementById('traffic_interface');
            if(!picker.options.length) document.querySelectorAll('[data-iface]').forEach(b=>{const option=document.createElement('option');option.value=b.dataset.iface;option.textContent=(window.TRAFFIC_ALIASES||{})[b.dataset.iface]||b.dataset.iface;picker.append(option);});
            picker.value=ifaceName;
            aliasName = aliasName || (window.TRAFFIC_ALIASES || {})[ifaceName] || ifaceName;
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById('tab_' + ifaceName).classList.add('active');

            document.querySelectorAll('[data-iface]').forEach(b => { b.textContent=(window.TRAFFIC_ALIASES||{})[b.dataset.iface]||b.dataset.iface; b.onclick=()=>renderData(b.dataset.iface); });
            const data = window.TRAFFIC_DATA && window.TRAFFIC_DATA[ifaceName];
            if(!data || data.error) {
                document.getElementById('content').style.display = 'none';
                document.getElementById('loading').style.display = 'block';
                document.getElementById('loading').innerText = "Error: No data available from vnStat for " + ifaceName; 
                return;
            }
            
            const iface = data.interfaces[0];
            const tr = iface.traffic;

            let dbTime = new Date(); 
            if(iface.updated && iface.updated.date) {
                const u = iface.updated;
                dbTime = new Date(u.date.year, u.date.month - 1, u.date.day, u.time.hour, u.time.minute);
            }

            document.getElementById('loading').style.display = 'none';
            document.getElementById('content').style.display = 'block';
            document.getElementById('iface_name').innerText = aliasName ? aliasName : (iface.name || iface.id);
            if(iface.created && iface.created.date) document.getElementById('s_created').innerText = pDate(iface.created.date, 'f');

            document.getElementById('data_freshness').dataset.epoch = iface.updated && iface.updated.date ? String(dbTime.getTime()) : '';
            const age=(Date.now()-dbTime.getTime())/60000;
            document.getElementById('data_freshness').textContent='Database updated: '+dbTime.toLocaleString('en-GB')+(age>30?' — data older than 30 minutes':'');
            // --- 1. SUMMARY ---
            const getLast = (arr, offset) => arr[arr.length - 1 - offset] || {rx:0, tx:0};
            
            const today = getLast(tr.day, 0);
            const yest = getLast(tr.day, 1);
            const tmon = getLast(tr.month, 0);
            const lmon = getLast(tr.month, 1);
            const total = tr.total;

            const fillSum = (pfx, d) => {
                document.getElementById(pfx+'_rx').innerText = fmt(d.rx);
                document.getElementById(pfx+'_tx').innerText = fmt(d.tx);
                document.getElementById(pfx+'_tot').innerText = fmt(d.rx+d.tx);
            };
            fillSum('s_td', today); fillSum('s_yd', yest);
            fillSum('s_tm', tmon);  fillSum('s_lm', lmon);
            fillSum('s_all', total);
            if(window.MONTHLY_QUOTA_GB>0){const used=(tmon.rx+tmon.tx)/1e9;document.getElementById('data_quota').textContent='Monthly quota: '+window.KTFormat.number(used,2,2)+' / '+window.KTFormat.number(window.MONTHLY_QUOTA_GB,0,3)+' GB; remaining '+window.KTFormat.number(Math.max(0,window.MONTHLY_QUOTA_GB-used),2,2)+' GB';}
            
            // FIXED: Passing 'm' format (month+year) for summary headers
            if(tmon.date) document.getElementById('lbl_tm').innerText = pDate(tmon.date, 'm');
            if(lmon.date) document.getElementById('lbl_lm').innerText = pDate(lmon.date, 'm');

            // Estimates
            const remDay = getEst(today, 'd', dbTime);
            const remMon = getEst(tmon, 'm', dbTime);
            
            if(remDay) document.getElementById('s_td_est').innerText = fmt( (today.rx+remDay.rx) + (today.tx+remDay.tx) );
            else document.getElementById('s_td_est').innerText = '-';
            
            if(remMon) document.getElementById('s_tm_est').innerText = fmt( (tmon.rx+remMon.rx) + (tmon.tx+remMon.tx) );
            else document.getElementById('s_tm_est').innerText = '-';
            
            // Clean up charts before rendering
            window._chartInstances.forEach(c => c.destroy());
            window._chartInstances = [];

            const mkPie = (id, cur, rem, isPast) => {
                // Use the same semantic colors for all periods; projections stay in the text summary.
                const style = getComputedStyle(document.body);
                const colRx = style.getPropertyValue('--blue').trim() || '#0097dc';
                const colTx = style.getPropertyValue('--green').trim() || '#1e7049';
                const d = [cur.rx, cur.tx];
                const c = [colRx, colTx];
                const chart = new Chart(document.getElementById(id), {
                    type: 'doughnut',
                    data: { labels:['Received','Sent'], datasets:[{data:d, backgroundColor:c, borderColor:style.getPropertyValue('--background').trim(), borderWidth:2, hoverOffset:2}] },
                    options: { 
                        locale:window.KTFormat.locale,
                        cutout:'72%', 
                        layout: { padding: 2 }, 
                        plugins:{tooltip:{enabled:true,callbacks:{label:ctx=>ctx.label+': '+fmt(ctx.raw)}}, legend:{display:false}}, 
                        maintainAspectRatio:false 
                    }
                });
                window._chartInstances.push(chart);
            };
            
            mkPie('pie_today', today, remDay, false); 
            mkPie('pie_yesterday', yest, null, true);
            mkPie('pie_month', tmon, remMon, false); 
            mkPie('pie_lmonth', lmon, null, true);
            mkPie('pie_total', total, null, false);

            // --- 2. TABLES ---
            const renderTable = (arr, type, tabId, limit, showEst, sortDesc) => {
                let data = arr.slice();
                if(sortDesc) {
                    data.sort((a,b)=>(b.rx+b.tx)-(a.rx+a.tx));
                    data = data.slice(0, limit);
                } else {
                    data = data.slice(-limit).reverse();
                }
                
                const tbody = document.querySelector('#'+tabId+' tbody');
                tbody.innerHTML = ''; // Clear rows before switching the displayed period.
                
                let maxVal = 0;
                data.forEach(d => { if((d.rx+d.tx) > maxVal) maxVal = (d.rx+d.tx); });
                
                if(showEst && !sortDesc && data.length > 0) {
                    const estRem = getEst(data[0], type, dbTime); 
                    if(estRem) {
                        const estTotRx = data[0].rx + estRem.rx;
                        const estTotTx = data[0].tx + estRem.tx;
                        if((estTotRx+estTotTx) > maxVal) maxVal = (estTotRx+estTotTx);
                        data.unshift({ rx: estTotRx, tx: estTotTx, date: "estimated" });
                    }
                }

                data.forEach(x => {
                    const tot = x.rx + x.tx;
                    const pctRx = (x.rx / maxVal) * 100;
                    const pctTx = (x.tx / maxVal) * 100;
                    const isEst = (x.date === "estimated");
                    
                    const r = document.createElement('tr');
                    if(isEst) r.classList.add('row-est');
                    
                    let dateStr = isEst ? "estimated" : pDate(x, tabId === 'tab_top' ? 'f' : type);
                    
                    r.innerHTML = \`
                        <td>\${dateStr}</td>
                        <td class="c-rx">\${fmt(x.rx)}</td>
                        <td class="c-tx">\${fmt(x.tx)}</td>
                        <td class="c-tot">\${fmt(tot)}</td>
                        <td>\${isEst ? '-' : calcRate(tot, x, type, dbTime)}</td>
                        <td class="td-graph">
                            <div class="bar-container">
                                <div class="bar-rx" style="width:\${pctRx}%"></div>
                                <div class="bar-tx" style="width:\${pctTx}%"></div>
                            </div>
                        </td>
                    \`;
                    tbody.appendChild(r);
                });
            };

            renderTable(tr.hour, 'h', 'tab_hour', 24, false, false);
            renderTable(tr.day, 'd', 'tab_day', 30, true, false);
            renderTable(tr.month, 'm', 'tab_mon', 12, true, false);
            renderTable(tr.year, 'y', 'tab_year', 10, true, false);
            renderTable(tr.day, 'd', 'tab_top', 10, false, true);
        }

        window.ktRefreshPage=async()=>{
            const iface=document.getElementById('traffic_interface').value;
            const names=[...new Set([...Object.keys(window.TRAFFIC_DATA||{}),...Array.from(document.querySelectorAll('[data-iface]'),node=>node.dataset.iface)])];
            const exports=await Promise.allSettled(names.map(async name=>{
                const response=await fetch(encodeURIComponent(name)+'_data.js?t='+Date.now(),{cache:'no-store'});
                if(!response.ok)throw Error('Traffic data unavailable');
                return await response.text();
            }));
            const failed=exports.find(item=>item.status==='rejected');if(failed)throw failed.reason;
            for(const item of exports)window.eval(item.value);
            renderData(document.getElementById('traffic_interface').value||iface||names[0]);
        };
        window.onload = function() {
            const firstAlias = "$ALIASES".split(" ")[0] || '$FIRST_IFACE';
            setTimeout(function() {
                const savedInterface = localStorage.getItem('traffic_interface');
                renderData(Object.prototype.hasOwnProperty.call(window.TRAFFIC_DATA || {}, savedInterface) ? savedInterface : '$FIRST_IFACE');
            }, 100);
        };
    </script>
<footer class="kt-page-footer">&copy; <span data-kt-year>2026</span> mattheweli<span class="kt-footer-meta">Traffic Manager 2.0.1</span></footer>
</body>
</html>
EOF
chmod 644 "$HTML_TMP" || { rm -f "$HTML_TMP"; exit 1; }
mv "$HTML_TMP" "$HTMLFILE"
printf '%s\n' "$SIGNATURE" > "$OUTDIR/.signature"

# --- 4. GENERATE JS INDEX FOR DASHBOARD ---
INDEX_FILE="${OUTDIR}/vnstat_index.js"
echo "window.VNSTAT_INTERFACES = \"$IFACES\";" > "$INDEX_FILE"
chmod 644 "$INDEX_FILE" || exit 1

fi

