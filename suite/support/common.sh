#!/opt/bin/bash
# common v1.0.0 | 2026-10-22 | Stable release
# Shared helpers for the coordinated stable release. No network or router changes on load.
kt_log() { printf '%s [%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "${KT_TOOL:-keentool}" "$*" >&2; }
kt_cleanup() {
    [ -z "${KT_WORKDIR:-}" ] || rm -rf "$KT_WORKDIR"
    if [ -n "${KT_LOCKDIR:-}" ] && [ "$(cat "$KT_LOCKDIR/pid" 2>/dev/null)" = "$$" ]; then
        rm -f "$KT_LOCKDIR/pid"; rmdir "$KT_LOCKDIR" 2>/dev/null || :
    fi
}
kt_init() {
    if [ "$1" != firewall-hook ] && [ -e "${KT_MAINTENANCE_FILE:-/opt/etc/keentool/maintenance}" ]; then
        kt_log 'Entware maintenance active: execution deferred'; return 75
    fi
    KT_TOOL=$1; KT_LOCKDIR="${KT_RUN_DIR:-/tmp}/$1.lockdir"
    if ! mkdir "$KT_LOCKDIR" 2>/dev/null; then
        local owner; owner=$(cat "$KT_LOCKDIR/pid" 2>/dev/null)
        if [[ "$owner" =~ ^[0-9]+$ ]] && ! kill -0 "$owner" 2>/dev/null; then
            rm -f "$KT_LOCKDIR/pid"; rmdir "$KT_LOCKDIR" 2>/dev/null || :
            mkdir "$KT_LOCKDIR" 2>/dev/null || { kt_log 'Already running'; return 75; }
        else kt_log 'Already running'; return 75; fi
    fi
    printf '%s\n' "$$" > "$KT_LOCKDIR/pid"
    KT_WORKDIR=$(mktemp -d "${KT_RUN_DIR:-/tmp}/$1.XXXXXX") || { kt_cleanup; return 1; }
    trap kt_cleanup EXIT
    trap 'exit 130' INT
    trap 'exit 143' TERM
}
kt_sqlite() { command sqlite3 -bail -cmd '.timeout 5000' "$@"; }
kt_atomic_save_set() {
    local dest=$2 tmp
    tmp=$(mktemp "${dest}.XXXXXX") || return 1
    if ipset save "$1" > "$tmp"; then chmod 600 "$tmp"; mv -f "$tmp" "$dest"
    else rm -f "$tmp"; return 1; fi
}
kt_download() {
    local url=$1 dest=$2 tmp
    tmp=$(mktemp "${dest}.XXXXXX") || return 1
    if curl -fsSL --connect-timeout 10 --max-time 60 --retry 2 "$url" -o "$tmp" && [ -s "$tmp" ]; then
        mv -f "$tmp" "$dest"
    else rm -f "$tmp"; return 1; fi
}
kt_validate() {
    local p=$1 first
    first=$(head -n 1 "$p")
    case "$first" in
        '#!'*) /opt/bin/bash -n "$p" ;;
        '<?php'*) if command -v php >/dev/null; then php -l "$p" >/dev/null; else php-cgi -l "$p" >/dev/null; fi ;;
        *) case "$p" in *.html*) grep -qi '<html' "$p" ;; *) [ -s "$p" ] ;; esac ;;
    esac
}

kt_json_valid() {
    local candidate
    for candidate in "${KT_PHP_CLI:-}" /opt/bin/php-cli /opt/bin/php8 /opt/bin/php;do
        [ -n "$candidate" ] && [ -x "$candidate" ] || continue
        "$candidate" -r 'if (PHP_SAPI !== "cli") exit(1); $d=json_decode(stream_get_contents(STDIN),true); exit(json_last_error()===JSON_ERROR_NONE && is_array($d) && isset($d["interfaces"]) && is_array($d["interfaces"]) ? 0 : 1);' <<< "$1"
        return $?
    done
    kt_log 'PHP CLI unavailable for vnStat JSON validation';return 1
}

# GNU stat is optional on Entware; PHP core metadata supports the BusyBox builds without -c.
kt_stat() {
 local format=$1 file=$2 candidate
 if command stat -c "$format" "$file" 2>/dev/null;then return 0;fi
 for candidate in "${KT_PHP_CLI:-}" /opt/bin/php-cli /opt/bin/php8 /opt/bin/php;do
  [ -n "$candidate" ] && [ -x "$candidate" ] || continue
  "$candidate" -r '$s=@stat($argv[2]);if($s===false)exit(1);switch($argv[1]){case "%Y":echo $s["mtime"];break;case "%i":echo $s["ino"];break;case "%s":echo $s["size"];break;case "%d:%i":echo $s["dev"].":".$s["ino"];break;default:exit(1);}' "$format" "$file"
  return $?
 done
 return 1
}
