#!/opt/bin/bash
# SMB BACKUP TOOL v2.0.1
# Release: 2026-10-23 | Stable. See CHANGELOG.md for release details.

# Description: Backup local folders to remote SMB share

export PATH=${KT_PATH:-/opt/bin:/opt/sbin:/usr/bin:/usr/sbin:/bin:/sbin}
# smb_backup_tool 2.0.1
. "${KT_COMMON:-/opt/lib/keentool/common.sh}" || exit 1


# --- CONFIGURATION ---
VERSION="2.0.1"
CONFIG_FILE="${KT_SMB_CONFIG:-/opt/etc/smb_backup.cfg}"
LOG_FILE="/opt/var/log/smb_backup.log"
TEMP_DIR="" # allocated per backup; never shared between runs
CRON_FILE="/opt/etc/crontab"  # File target per Entware

# Filter harmless log warnings
LOG_FILTER="NT_STATUS_OBJECT_NAME_COLLISION|Can't load|dos charset"

# Colors
CGreen="\e[1;32m"
CRed="\e[1;31m"
CYellow="\e[1;33m"
CBlue="\e[1;34m"
CWhite="\e[1;37m"
CClear="\e[0m"
InvDkGray="\e[1;100m"

# --- UTILITY FUNCTIONS ---

check_and_fix_cron_user() {
    SCRIPT_PATH=$(readlink -f "$0")
    # Check whether the crontab file exists.
    if [ -f "$CRON_FILE" ]; then
        # Find cron entries for this script that are missing the root user field.
        if grep -Fq "$SCRIPT_PATH" "$CRON_FILE" && ! grep -Fq "root $SCRIPT_PATH" "$CRON_FILE"; then
            logger_msg "Detected malformed CRON entry (missing user). Fixing..." "WARN"
            
            # Insert "root " before the script path using sed.
            # Match: (text ending with a space) (/path/to/script).
            # Replace with: \1root \2
            sed -i "s|\(.*\) \($SCRIPT_PATH\)|\1 root \2|" "$CRON_FILE"
            
            # Verify that the correction succeeded.
            if grep -Fq "root $SCRIPT_PATH" "$CRON_FILE"; then
                logger_msg "CRON entry fixed successfully." "INFO"
                restart_cron_service
            else
                logger_msg "Failed to fix CRON entry automatically." "ERROR"
            fi
        fi
    fi
}

logger_msg() {
    TYPE=$2; [ -z "$TYPE" ] && TYPE="INFO"
    echo -e "$(date "+%Y-%m-%d %H:%M:%S") [${TYPE}] $1" >> "$LOG_FILE"
    case $TYPE in
        "ERROR") echo -e "${CRed}[ERROR] $1${CClear}" ;;
        "WARN")  echo -e "${CYellow}[WARN]  $1${CClear}" ;;
        *)       echo -e "${CGreen}[INFO]  $1${CClear}" ;;
    esac
}

load_config() {
    CONFIG_STATUS="MISSING"
    if [ -f "$CONFIG_FILE" ]; then
        source "$CONFIG_FILE"
        [ ! -z "$SMB_PASS_ENC" ] && SMB_PASS=$(echo "$SMB_PASS_ENC" | base64 -d 2>/dev/null)
        [ -z "$AUTO_PURGE" ] && AUTO_PURGE="true"
        [ -z "$CRON_LABEL" ] && CRON_LABEL="Not Configured"

        if [ ! -z "$SMB_HOST" ] && [ ! -z "$SMB_SHARE" ]; then
            CONFIG_STATUS="OK"
        else
            CONFIG_STATUS="INVALID"
        fi
    fi
}

save_config() {
    PASS_ENC=$(echo -n "$SMB_PASS" | base64)
    umask 077
    CFG_TMP=$(mktemp "${CONFIG_FILE}.XXXXXX") || return 1
    for name in SMB_HOST SMB_SHARE SMB_SUBDIR SMB_USER SOURCE_DIR RETENTION_DAYS AUTO_PURGE CRON_LABEL; do
        printf '%s=%q\n' "$name" "${!name}" >> "$CFG_TMP"
    done
    printf 'SMB_PASS_ENC=%q\n' "$PASS_ENC" >> "$CFG_TMP"
    mv "$CFG_TMP" "$CONFIG_FILE" || return 1
    chmod 600 "$CONFIG_FILE"
    logger_msg "Configuration saved to $CONFIG_FILE" "INFO"
    load_config
}

check_dependencies() {
    if ! which smbclient >/dev/null 2>&1; then
        echo -e "${CRed}ERROR: smbclient not found. Run: opkg install samba4-client${CClear}"
        exit 1
    fi
    if [ ! -e /usr/bin/ndmc ] && [ ! -e /bin/ndmc ]; then
         echo -e "${CYellow}WARN: ndmc (CLI) not found. Config backup might fail.${CClear}"
    fi
}

# --- ENTWARE CRON FUNCTIONS (v1.0.2) ---

restart_cron_service() {
    # Restart cron to apply scheduling changes.
    if [ -x /opt/etc/init.d/S10cron ]; then
        /opt/etc/init.d/S10cron restart >/dev/null 2>&1
    elif which crond >/dev/null 2>&1; then
        killall crond 2>/dev/null
        crond
    fi
}

get_cron_status() {
    SCRIPT_PATH=$(readlink -f "$0")
    CRON_CMD="$SCRIPT_PATH -run"
	
	FULL_LINE="$CRON_STR root $CRON_CMD"
    
    if [ -f "$CRON_FILE" ] && grep -Fq "$CRON_CMD" "$CRON_FILE"; then
        echo "ACTIVE"
    else
        echo "INACTIVE"
    fi
}

configure_schedule_wizard() {
    clear
    echo -e "${CBlue}--- AUTOMATIC SCHEDULE WIZARD ---${CClear}"
    echo "This will edit: $CRON_FILE"
    echo ""
    echo "Select Frequency:"
    echo " 1. Daily (Every day)"
    echo " 2. Weekly (Every Sunday)"
    echo " 3. Bi-Weekly (Every 15 days - 1st, 16th, 31st)"
    echo " 4. Monthly (1st of month)"
    echo ""
    read -p "Choice [1-4]: " FREQ_OPT

    echo ""
    read -p "Enter Hour (0-23) [e.g. 03]: " IN_HOUR
    read -p "Enter Minute (0-59) [e.g. 00]: " IN_MIN

    if [ -z "$IN_HOUR" ]; then IN_HOUR="03"; fi
    if [ -z "$IN_MIN" ]; then IN_MIN="00"; fi
    
    [[ "$IN_HOUR" =~ ^[0-9]{1,2}$ && "$IN_MIN" =~ ^[0-9]{1,2}$ ]] && ((10#$IN_HOUR <= 23 && 10#$IN_MIN <= 59)) || { echo 'Invalid time'; return 1; }
    case "$FREQ_OPT" in
        1) # Daily
           CRON_STR="$IN_MIN $IN_HOUR * * *"
           LABEL_STR="Daily at $IN_HOUR:$IN_MIN"
           ;;
        2) # Weekly
           CRON_STR="$IN_MIN $IN_HOUR * * 0"
           LABEL_STR="Weekly (Sun) at $IN_HOUR:$IN_MIN"
           ;;
        3) # Bi-Weekly
           CRON_STR="$IN_MIN $IN_HOUR */15 * *"
           LABEL_STR="Every 15 days at $IN_HOUR:$IN_MIN"
           ;;
        4) # Monthly
           CRON_STR="$IN_MIN $IN_HOUR 1 * *"
           LABEL_STR="Monthly (1st) at $IN_HOUR:$IN_MIN"
           ;;
        *) 
           echo "Invalid option."
           return
           ;;
    esac

    SCRIPT_PATH=$(readlink -f "$0")
    CRON_CMD="$SCRIPT_PATH -run"
    FULL_LINE="$CRON_STR root $CRON_CMD"
    
    # --- WRITE TO FILE (v1.2.8) ---
    if [ ! -f "$CRON_FILE" ]; then touch "$CRON_FILE"; fi
    
    # 1. Remove old entries containing the command (using # as the delimiter).
    sed -i "\#$CRON_CMD#d" "$CRON_FILE"
    
    # 2. Append the new entry.
    echo "$FULL_LINE" >> "$CRON_FILE"
    
    # 3. Update the label and restart the service.
    CRON_LABEL="$LABEL_STR"
    save_config
    restart_cron_service
    
    echo -e "${CGreen}Schedule updated in $CRON_FILE: $LABEL_STR${CClear}"
    logger_msg "Scheduler updated ($CRON_FILE) to: $LABEL_STR" "INFO"
    read -p "Press Enter..."
}

disable_scheduler() {
    SCRIPT_PATH=$(readlink -f "$0")
    CRON_CMD="$SCRIPT_PATH -run"
    
    if [ -f "$CRON_FILE" ]; then
        # Remove the entry from the crontab file
        sed -i "\#$CRON_CMD#d" "$CRON_FILE"
        restart_cron_service
    fi
    
    CRON_LABEL="Disabled"
    save_config
    
    echo -e "${CYellow}Scheduler disabled (entry removed from $CRON_FILE).${CClear}"
    logger_msg "Scheduler disabled by user." "INFO"
    read -p "Press Enter..."
}

scheduler_menu() {
    while true; do
        clear
        STATUS=$(get_cron_status)
        if [ "$STATUS" == "ACTIVE" ]; then STATUS_COL="${CGreen}ACTIVE${CClear}"; else STATUS_COL="${CRed}INACTIVE${CClear}"; fi
        
        echo -e "${CBlue}--- SCHEDULER MENU (Entware) ---${CClear}"
        echo -e "File   : $CRON_FILE"
        echo -e "Status : $STATUS_COL"
        echo -e "Current: $CRON_LABEL"
        echo ""
        echo " 1. Configure New Schedule (Wizard)"
        echo " 2. Disable Scheduler"
        echo " 3. Return to Main Menu"
        echo ""
        read -p "Select: " SCH_OPT
        case "$SCH_OPT" in
            1) configure_schedule_wizard ;;
            2) disable_scheduler ;;
            3) return ;;
        esac
    done
}

# --- SYSTEM DUMP FUNCTIONS ---

dump_system_files() {
    logger_msg "Exporting System Configuration..." "INFO"
    mkdir -p "$TEMP_DIR/sys_dump"
    
    # RUNNING CONFIG (via NDMC)
    logger_msg "Executing 'show running-config' via CLI..." "INFO"
    CONFIG_FILE_TXT="$TEMP_DIR/sys_dump/running-config.txt"
    
    if ndmc -c "show running-config" > "$CONFIG_FILE_TXT" 2>/dev/null; then
         if [ -s "$CONFIG_FILE_TXT" ]; then
             ESC=$(printf '\033')
             sed -i "s/${ESC}\[[0-9;]*[a-zA-Z]//g" "$CONFIG_FILE_TXT"
             sed -i "s/${ESC}\[K//g" "$CONFIG_FILE_TXT"
             tr -d '\r' < "$CONFIG_FILE_TXT" > "$CONFIG_FILE_TXT.tmp" && mv "$CONFIG_FILE_TXT.tmp" "$CONFIG_FILE_TXT"
             logger_msg "Config exported and cleaned successfully." "INFO"
         else
             logger_msg "Config export created an empty file." "WARN"
         fi
    else
         echo "show running-config" | ndmc > "$CONFIG_FILE_TXT" 2>/dev/null
         [ -s "$CONFIG_FILE_TXT" ] && sed -i "s/$(printf '\033')\[[0-9;]*[a-zA-Z]//g" "$CONFIG_FILE_TXT"
         logger_msg "Config exported via pipe fallback." "INFO"
    fi
}

# --- BACKUP LOGIC ---

smb_safe_path() { [[ "$1" != *['";\\']* && "$1" != *$'\n'* && "$1" != *$'\r'* && "/$1/" != *'/../'* ]]; }
validate_backup_config() {
    [[ "$RETENTION_DAYS" =~ ^[0-9]+$ ]] || { logger_msg 'Invalid retention' ERROR; return 1; }
    SOURCE_DIR=$(cd -- "$SOURCE_DIR" 2>/dev/null && pwd -L) || { logger_msg 'Invalid source directory' ERROR; return 1; }
    [ -d "$SOURCE_DIR" ] && [ "$SOURCE_DIR" != / ] && [[ "$SOURCE_DIR" != /opt/tmp && "$SOURCE_DIR" != /opt/tmp/* ]] || { logger_msg 'Invalid source directory' ERROR; return 1; }
    smb_safe_path "$SMB_SUBDIR" && smb_safe_path "$SMB_SHARE" || { logger_msg 'Invalid SMB path' ERROR; return 1; }
    case "$SMB_USER$SMB_PASS" in *$'\n'*|*$'\r'*) logger_msg 'Newlines in credentials are unsupported' ERROR; return 1;; esac
}
smb_run() {
    local commands=$1 output rc auth
    auth=$(mktemp /tmp/keentool_smb_auth.XXXXXX) || return 1
    chmod 600 "$auth"
    printf 'username = %s\npassword = %s\n' "$SMB_USER" "$SMB_PASS" > "$auth"
    output=$(mktemp /tmp/keentool_smb_output.XXXXXX) || { rm -f "$auth"; return 1; }
    timeout 600 smbclient "//${SMB_HOST}/${SMB_SHARE}" -A "$auth" -c "$commands" > "$output" 2>&1
    rc=$?; rm -f "$auth"
    # Some smbclient versions return zero after a failing subcommand.
    if grep -E 'NT_STATUS_' "$output" | grep -v 'NT_STATUS_OBJECT_NAME_COLLISION' >/dev/null; then rc=1; fi
    grep -vE "$LOG_FILTER" "$output" || :
    rm -f "$output"; return "$rc"
}
smb_cd() {
    local folder result=""; local -a folders
    IFS=/ read -r -a folders <<< "$SMB_SUBDIR"
    for folder in "${folders[@]}"; do
        [ -z "$folder" ] && continue
        [ "${1:-}" != create ] || result="$result mkdir \"$folder\";"
        result="$result cd \"$folder\";"
    done
    printf '%s' "$result"
}
test_connection() {
    if smb_run 'ls'; then logger_msg 'SMB Connection Successful' INFO
    else logger_msg 'SMB Connection Failed' ERROR; return 1; fi
}
perform_cleanup() { [ -z "$TEMP_DIR" ] || rm -rf "$TEMP_DIR"; }
perform_backup() {
    [ "$CONFIG_STATUS" = OK ] || { logger_msg 'Configuration invalid or missing' ERROR; return 1; }
    validate_backup_config || return 1
    kt_init smb-backup || return $?
    mkdir -p /opt/tmp
    TEMP_DIR=$(mktemp -d /opt/tmp/keentool-smb.XXXXXX) || return 1
    trap 'perform_cleanup; kt_cleanup' EXIT
    umask 077
    DATE_STR=$(date +%Y%m%d_%H%M%S); REMOTE_FOLDER_NAME="$DATE_STR"
    logger_msg 'Backup started' INFO
    dump_system_files
    [ -s "$TEMP_DIR/sys_dump/running-config.txt" ] || { logger_msg 'Router config export failed' ERROR; return 1; }
    ARCHIVE_SYS="sys_backup_${DATE_STR}.tar.gz"; ARCHIVE_OPT="opt_backup_${DATE_STR}.tar.gz"
    ARCHIVE_SQL="sqlite_backup_${DATE_STR}.tar.gz"
    tar -czf "$TEMP_DIR/$ARCHIVE_SYS" -C "$TEMP_DIR/sys_dump" . || return 1
    local source_parent source_name excluded relative snapshot db
    local -a prune_paths find_args
    source_parent=$(dirname "$SOURCE_DIR"); source_name=$(basename "$SOURCE_DIR")
    : > "$TEMP_DIR/exclude.txt"
    # Tar stores relative member names; a root parent must contribute ONE slash.
    # Runtime sockets, locks, rotating logs and staging files are not restore data.
    prune_paths=(/opt/var/log /opt/var/run /opt/var/lock /opt/tmp /opt/backup_storage)
    for excluded in "${prune_paths[@]}"; do
        if [[ "$excluded" = "$SOURCE_DIR" || "$excluded" = "$SOURCE_DIR"/* ]]; then
            relative=${excluded#"${source_parent%/}/"}
            printf '%s\n' "$relative" >> "$TEMP_DIR/exclude.txt"
        fi
    done
    # Use a checked, NUL-delimited inventory; do not scan excluded runtime trees.
    find_args=("$SOURCE_DIR" '(')
    for excluded in "${prune_paths[@]}"; do
        [ "${#find_args[@]}" -eq 2 ] || find_args+=(-o)
        find_args+=(-path "$excluded")
    done
    find_args+=(')' -prune -o '(' -type s -o '(' -type f -name '*.db' ')' ')' -print0)
    find "${find_args[@]}" > "$TEMP_DIR/inventory" || { logger_msg 'Source inventory failed' ERROR; return 1; }
    mkdir -p "$TEMP_DIR/sqlite_snapshots"
    while IFS= read -r -d '' db; do
        relative=${db#"${source_parent%/}/"}
        if [[ "$relative" = *$'\n'* || "$relative" = *$'\r'* ]]; then
            logger_msg 'Unsupported newline in archive exclusion path' ERROR; return 1
        fi
        if [ -S "$db" ]; then
            printf '%s\n' "$relative" >> "$TEMP_DIR/exclude.txt"
            continue
        fi
        # Encode all 16 header bytes before command substitution (SQLite ends in NUL).
        [ "$(head -c 16 "$db" | base64)" = 'U1FMaXRlIGZvcm1hdCAzAA==' ] || continue
        command -v sqlite3 >/dev/null || { logger_msg 'sqlite3 needed for live DB backup' ERROR; return 1; }
        snapshot="$TEMP_DIR/sqlite_snapshots/$relative"; mkdir -p "$(dirname "$snapshot")"
        kt_sqlite "$db" ".backup '$snapshot'" || return 1
        [ "$(kt_sqlite "$snapshot" 'PRAGMA quick_check;')" = ok ] || return 1
        printf '%s\n' "$relative" "$relative-wal" "$relative-shm" >> "$TEMP_DIR/exclude.txt"
    done < "$TEMP_DIR/inventory"
    tar -X "$TEMP_DIR/exclude.txt" -czf "$TEMP_DIR/$ARCHIVE_OPT" -C "$source_parent" "$source_name" || { logger_msg 'OPT archive failed' ERROR; return 1; }
    tar -czf "$TEMP_DIR/$ARCHIVE_SQL" -C "$TEMP_DIR/sqlite_snapshots" . || return 1
    for archive in "$ARCHIVE_SYS" "$ARCHIVE_OPT" "$ARCHIVE_SQL"; do
        tar -tzf "$TEMP_DIR/$archive" >/dev/null || { logger_msg 'Invalid archive' ERROR; return 1; }
    done
    (cd "$TEMP_DIR" && sha256sum "$ARCHIVE_SYS" "$ARCHIVE_OPT" "$ARCHIVE_SQL" > MANIFEST.sha256) || return 1
    partial=".incomplete_$REMOTE_FOLDER_NAME"; prefix=$(smb_cd create)
    cmds="$prefix mkdir \"$partial\"; cd \"$partial\"; lcd \"$TEMP_DIR\"; put \"$ARCHIVE_SYS\"; put \"$ARCHIVE_OPT\"; put \"$ARCHIVE_SQL\"; put MANIFEST.sha256;"
    smb_run "$cmds" >> "$LOG_FILE" || { logger_msg 'SMB upload failed; retention skipped' ERROR; return 1; }
    # Read back each archive; verify actual remote bytes before marking complete.
    for archive in "$ARCHIVE_SYS" "$ARCHIVE_OPT" "$ARCHIVE_SQL"; do
        smb_run "$(smb_cd) cd \"$partial\"; get \"$archive\" \"$TEMP_DIR/verify.bin\";" >> "$LOG_FILE" || return 1
        expected=$(sha256sum "$TEMP_DIR/$archive"); expected=${expected%% *}
        actual=$(sha256sum "$TEMP_DIR/verify.bin" 2>/dev/null); actual=${actual%% *}
        [ "$actual" = "$expected" ] || { logger_msg 'Remote checksum mismatch; retention skipped' ERROR; return 1; }
        rm -f "$TEMP_DIR/verify.bin"
    done
    smb_run "$(smb_cd) rename \"$partial\" \"$REMOTE_FOLDER_NAME\";" >> "$LOG_FILE" || return 1
    logger_msg "Backup verified: $REMOTE_FOLDER_NAME" INFO
    if [ -x /opt/bin/firewall_security ];then
        /opt/bin/bash /opt/bin/firewall_security backup-event "$REMOTE_FOLDER_NAME" < "$TEMP_DIR/MANIFEST.sha256" || logger_msg 'Verified backup health record could not be saved' WARN
    fi
    [ "$AUTO_PURGE" != true ] || run_retention_check AUTO || return 1
    perform_cleanup; kt_cleanup; trap - EXIT INT TERM
    return 0
}

run_retention_check() {
    MODE=$1 # "AUTO" or empty (Manual)

    if [ -z "$RETENTION_DAYS" ] || [ "$RETENTION_DAYS" -le 0 ]; then
        echo -e "${CYellow}Retention policy is 0 or unset. Nothing to purge.${CClear}"
        return
    fi
    
    if [ "$MODE" != "AUTO" ]; then
        echo -e "${CBlue}Scanning for folders older than ${CWhite}$RETENTION_DAYS days${CBlue}...${CClear}"
    fi
    logger_msg "Starting Purge Check (Limit: $RETENTION_DAYS days)..." "INFO"
    
    smb_safe_path "$SMB_SUBDIR" || return 1
    PATH_CMDS=$(smb_cd)
    LIST=$(smb_run "$PATH_CMDS ls") || return 1
    CUTOFF_TS=$(( $(date +%s) - RETENTION_DAYS * 86400 ))
    
    echo "$LIST" | while read -r LINE; do
        if echo "$LINE" | grep -q " D "; then
             DIRNAME=$(echo "$LINE" | awk '{print $1}')
             if echo "$DIRNAME" | grep -qE '^[0-9]{8}_[0-9]{6}$'; then
                 
                 # FIX DATA PARSING
                 RAW_DATE=$(echo "$DIRNAME" | cut -d'_' -f1)
                 FMT_DATE="${RAW_DATE:0:4}-${RAW_DATE:4:2}-${RAW_DATE:6:2}"
                 DIR_TS=$(date -d "$FMT_DATE" +%s 2>/dev/null)
                 
                 if [ ! -z "$DIR_TS" ] && [ "$DIR_TS" -lt "$CUTOFF_TS" ]; then
                      
                      DO_DELETE="false"

                      if [ "$MODE" != "AUTO" ]; then
                          echo -e "${CYellow}Found OLD backup: ${CWhite}$DIRNAME${CYellow}${CClear}"
                          read -p "Delete this folder? (y/n): " CONFIRM_SINGLE < /dev/tty
                          if [ "$CONFIRM_SINGLE" == "y" ] || [ "$CONFIRM_SINGLE" == "Y" ]; then
                              DO_DELETE="true"
                          else
                              echo -e "${CGreen}Skipped.${CClear}"
                          fi
                      else
                          DO_DELETE="true"
                      fi
                      
                      if [ "$DO_DELETE" == "true" ]; then
                          logger_msg "Purging old backup folder: $DIRNAME" "WARN"
                          echo -e "${CRed}[DELETE] Deleting $DIRNAME ...${CClear}"
                          DEL_CMD="$PATH_CMDS recurse ON; deltree \"$DIRNAME\""
                          smb_run "$DEL_CMD" || return 1
                      fi
                 fi
             fi
        fi
    done
    
    if [ "$MODE" != "AUTO" ]; then
        echo -e "${CGreen}Purge Check Completed.${CClear}"
    fi
}

# --- USER INTERFACE ---

header() {
    clear
    CRON_STATUS=$(get_cron_status)
    if [ "$CRON_STATUS" == "ACTIVE" ]; then
        CRON_MSG="${CGreen}ACTIVE${CClear}"
        [ -z "$CRON_LABEL" ] && CRON_LABEL="Active (Custom)"
        SCHED_MSG="$CRON_LABEL"
    else
        CRON_MSG="${CRed}INACTIVE${CClear}"
        SCHED_MSG="-"
    fi

    echo -e "${InvDkGray}${CWhite} KEENETIC SMB BACKUP TOOL v$VERSION                                   ${CClear}"
    
    if [ "$CONFIG_STATUS" == "OK" ]; then
        echo -e "Status    : ${CGreen}CONFIGURED${CClear}"
        echo -e "Target    : //${SMB_HOST}/${SMB_SHARE}/${SMB_SUBDIR}"
        
        if [ "$AUTO_PURGE" == "true" ]; then
             MSG_AUTO="${CGreen}ON${CClear}"
        else
             MSG_AUTO="${CRed}OFF${CClear}"
        fi
        echo -e "Purge     : ${CYellow}${RETENTION_DAYS} days${CClear} (Auto: ${MSG_AUTO})"
        echo -e "Scheduler : $CRON_MSG ($SCHED_MSG)"
    else
        echo -e "Status    : ${CRed}NOT CONFIGURED ($CONFIG_FILE missing)${CClear}"
    fi
    echo ""
}

setup_wizard() {
    header
    echo -e "${CGreen}--- CONFIGURATION WIZARD ---${CClear}"
    
    read -p "SMB Server IP: " IN_HOST
    [ ! -z "$IN_HOST" ] && SMB_HOST="$IN_HOST"
    
    echo -e "\n${CYellow}NOTE: Share Name ONLY (e.g. VARIE)${CClear}"
    read -p "Share Name: " IN_SHARE
    [ ! -z "$IN_SHARE" ] && SMB_SHARE="$IN_SHARE"

    echo -e "\n${CYellow}NOTE: Full Path (e.g. Backup_ROUTER/KN-1812_Backup)${CClear}"
    read -p "Path [Default: Backup_ROUTER]: " IN_SUB
    if [ ! -z "$IN_SUB" ]; then SMB_SUBDIR="$IN_SUB"; else SMB_SUBDIR="Backup_ROUTER"; fi
    
    echo ""
    read -p "SMB User: " IN_USER
    [ ! -z "$IN_USER" ] && SMB_USER="$IN_USER"
    
    read -s -p "SMB Password: " IN_PASS
    echo ""
    [ ! -z "$IN_PASS" ] && SMB_PASS="$IN_PASS"
    
    echo -e "\n${CYellow}Other Settings${CClear}"
    read -p "Source [Enter for /opt]: " IN_DIR
    if [ ! -z "$IN_DIR" ]; then SOURCE_DIR="$IN_DIR"; else SOURCE_DIR="/opt"; fi
    
    read -p "Retention Days (e.g. 90): " IN_RET
    [ ! -z "$IN_RET" ] && RETENTION_DAYS="$IN_RET"

    echo -e "\n${CYellow}Enable Auto-Purge after backup?${CClear}"
    read -p "Auto Purge (y/n) [Default: y]: " IN_AUTO
    if [ "$IN_AUTO" == "n" ] || [ "$IN_AUTO" == "N" ]; then
        AUTO_PURGE="false"
    else
        AUTO_PURGE="true"
    fi
    
    save_config
}

show_menu() {
    while true; do
        load_config
        header
        
        echo -e "${InvDkGray}${CWhite}-----------------------------------------------------------------------------${CClear}\n"
        echo " 1. Configure Wizard"
        echo " 2. Run Backup Now"
        if [ ! -z "$RETENTION_DAYS" ]; then
             echo " 3. Run Purge Only (Interactive)"
        else
             echo " 3. Run Purge Only (Not Configured)"
        fi
        echo " 4. Test Connection"
        echo " 5. View Log"
        echo " 6. Scheduler (Cron)"
        echo " e. Exit"
        echo ""
        read -p "Choose option: " CHOICE
        case "$CHOICE" in
            1) setup_wizard ;;
            2) perform_backup; read -p "Press Enter..." ;;
            3) run_retention_check; read -p "Press Enter..." ;;
            4) test_connection; read -p "Press Enter..." ;;
            5) tail -n 20 "$LOG_FILE"; read -p "Press Enter..." ;;
            6) scheduler_menu ;;
            e|E) clear; exit 0 ;;
        esac
    done
}

# --- MAIN EXECUTION ---
check_dependencies
load_config
check_and_fix_cron_user

if [ "$1" == "-run" ]; then
    if [ "$CONFIG_STATUS" != "OK" ]; then logger_msg "Missing configuration." "ERROR"; exit 1; fi
    perform_backup
    exit $?
fi

show_menu

