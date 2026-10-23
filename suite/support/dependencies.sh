#!/opt/bin/bash
# KeenTool dependency preflight 1.0.0. Shared by installer and generated bootstrap.
# Inspect capabilities first. Package-manager changes require explicit consent.
kt_dep_add() {
    KT_DEP_ISSUES+=("$1")
    local package=$2
    [[ " ${KT_DEP_PACKAGES[*]} " = *" $package "* ]] || KT_DEP_PACKAGES+=("$package")
}
kt_dep_scan() {
    local scope=$1 name package candidate output root=${KT_INSTALL_ROOT:-}
    KT_DEP_ISSUES=();KT_DEP_PACKAGES=();KT_DEP_PHP=''
    for candidate in "${KT_UPDATE_PHP:-}" "$root/opt/bin/php-cli" "$root/opt/bin/php8" "$root/opt/bin/php";do
        [ -n "$candidate" ] && [ -x "$candidate" ] || continue
        if "$candidate" -r 'exit(PHP_SAPI==="cli"?0:1);' >/dev/null 2>&1;then KT_DEP_PHP=$candidate;break;fi
    done
    [ -n "$KT_DEP_PHP" ] || kt_dep_add 'PHP CLI is missing or cannot start (php-cgi does not replace CLI)' php8-cli
    for name in curl gzip sha256sum mktemp cat mkdir rm chmod;do
        command -v "$name" >/dev/null 2>&1 && continue
        case "$name" in curl)package=curl;;gzip)package=gzip;;sha256sum)package=coreutils-sha256sum;;mktemp)package=coreutils-mktemp;;*)package=busybox;;esac
        kt_dep_add "Missing bootstrap command: $name" "$package"
    done
    if [ "$scope" = suite ];then
        while read -r name package;do
            command -v "$name" >/dev/null 2>&1 || kt_dep_add "Missing suite command: $name" "$package"
        done <<'KT_DEP_COMMANDS'
bash bash
ip iproute2
logger busybox
readlink coreutils-readlink
dirname coreutils-dirname
basename coreutils-basename
ps procps-ng-ps
iptables iptables
ip6tables iptables
iptables-save iptables
ip6tables-save iptables
iptables-restore iptables
ip6tables-restore iptables
ipset ipset
sqlite3 sqlite3-cli
vnstat vnstat2
vnstatd vnstat2
tcpdump tcpdump
iprange iprange
openssl openssl-util
lighttpd lighttpd
ping iputils-ping
mtr mtr
ulogd ulogd
smbclient samba4-client
tar tar
grep grep
awk gawk
sed sed
sort coreutils-sort
uniq coreutils-uniq
cut coreutils-cut
head coreutils-head
tail coreutils-tail
wc coreutils-wc
tr coreutils-tr
find findutils
cmp diffutils
date coreutils-date
du coreutils-du
pidof busybox
id coreutils-id
cp coreutils-cp
mv coreutils-mv
rmdir coreutils-rmdir
sleep coreutils-sleep
touch coreutils-touch
timeout coreutils-timeout
KT_DEP_COMMANDS
        if command -v opkg >/dev/null 2>&1;then
            for package in lighttpd-mod-fastcgi lighttpd-mod-openssl ulogd-mod-nflog ulogd-mod-pcap;do
                output=$(opkg status "$package" 2>/dev/null) || output=''
                [[ "$output" =~ Status:[[:space:]]+install[[:space:]]+[^[:space:]]+[[:space:]]+installed ]] || kt_dep_add "Missing Entware runtime module: $package" "$package"
            done
        fi
        command -v crond >/dev/null 2>&1 || command -v cron >/dev/null 2>&1 || kt_dep_add 'Cron executable is missing' cron
        if [ -n "$KT_DEP_PHP" ];then
            output=$("$KT_DEP_PHP" -r 'foreach(["inet_pton","inet_ntop","proc_open","stream_socket_server","session_start","password_hash","random_bytes","hash_file","disk_free_space"] as $f)if(!function_exists($f))echo $f," ";' 2>/dev/null) || output='PHP capability check failed'
            if [ -n "$output" ];then
                package=php8-cli;[[ "$output" != *session_start* ]] || package=php8-mod-session
                kt_dep_add "Unavailable PHP CLI functions: $output" "$package"
            fi
        fi
        candidate="$root/opt/bin/php-cgi"
        if [ ! -x "$candidate" ] || ! output=$("$candidate" -v 2>&1);then kt_dep_add 'PHP CGI is missing or cannot start' php8-cgi;fi
        if command -v sqlite3 >/dev/null 2>&1;then
            output=$(sqlite3 -json :memory: 'SELECT 1 AS ok;' 2>/dev/null) || output=''
            [[ "$output" = *'"ok":1'* ]] || kt_dep_add 'SQLite CLI JSON output is unavailable' sqlite3-cli
        fi
    fi
    [ "${#KT_DEP_ISSUES[@]}" = 0 ]
}
kt_dep_ensure() {
    local scope=$1 policy=${2:-ask} issue answer
    kt_dep_scan "$scope" && return 0
    printf 'Dependency preflight (%s):\n' "$scope" >&2
    for issue in "${KT_DEP_ISSUES[@]}";do printf ' - %s\n' "$issue" >&2;done
    printf 'Required Entware packages: %s\n' "${KT_DEP_PACKAGES[*]}" >&2
    [ "$policy" != check ] || return 1
    [ "$policy" = yes ] || {
        [ -t 0 ] || { echo 'No packages installed. Install the listed packages, or rerun with --install-deps explicitly.' >&2;return 1; }
        read -r -p 'Install these missing dependencies through opkg? [y/N] ' answer
        [[ "$answer" = y || "$answer" = Y ]] || return 1
    }
    [ "$(id -u)" = 0 ] && command -v opkg >/dev/null 2>&1 || { echo 'Root and opkg are required to install dependencies.' >&2;return 1; }
    # Do not upgrade all packages, stop services or change web/firewall configuration.
    opkg update && opkg install "${KT_DEP_PACKAGES[@]}" || { echo 'Dependency installation failed; suite files are unchanged.' >&2;return 1; }
    kt_dep_scan "$scope" || {
        echo 'Dependencies are still unavailable after installation. An installed but broken executable may need library repair:' >&2
        for issue in "${KT_DEP_ISSUES[@]}";do printf ' - %s\n' "$issue" >&2;done
        return 1
    }
}
