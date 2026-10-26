#!/opt/bin/bash
# KEENTOOL WEB ISOLATION v1.0.1 — 2026-10-26, stable.
# Narrow migration for the installed lighttpd + local PHP-CGI layout. No guessed user IDs.
set -Eeuo pipefail
export PATH=/opt/bin:/opt/sbin:/usr/bin:/usr/sbin:/bin:/sbin
CONF=/opt/etc/lighttpd/lighttpd.conf
DIR=/opt/etc/lighttpd/conf.d
MARK=/opt/etc/keentool/security/web-hardened
ACCOUNT=/opt/etc/keentool/security/web-account
PHP_BIN=''
for candidate in "${KT_PHP_CLI:-}" /opt/bin/php-cli /opt/bin/php8 /opt/bin/php;do
 if [ -x "$candidate" ] && "$candidate" -r 'exit(PHP_SAPI==="cli" && function_exists("stat") ? 0 : 1);' >/dev/null 2>&1;then PHP_BIN=$candidate;break;fi
done
[ -n "$PHP_BIN" ] || { echo 'PHP CLI filesystem metadata support required; no changes made' >&2;exit 1; }
metadata(){
 local value
 value=$("$PHP_BIN" -r '$s=@stat($argv[1]);if($s===false)exit(1);printf("%o\t%d\t%d",$s["mode"]&07777,$s["uid"],$s["gid"]);' "$1") || return 1
 [[ "$value" =~ ^[0-7]{3,4}$'\t'[0-9]+$'\t'[0-9]+$ ]] || { echo "Cannot read filesystem metadata: $1" >&2;return 1; }
 printf '%s' "$value"
}
valid_permissions(){
 local mode uid gid path extra
 [ -f "$1" ] || return 1
 [ -s "$1" ] || [ "${2:-}" = allow-empty ] || return 1
 while IFS=$'\t' read -r mode uid gid path extra;do
  [[ "$mode" =~ ^[0-7]{3,4}$ && "$uid" =~ ^[0-9]+$ && "$gid" =~ ^[0-9]+$ && "$path" = /opt/* && -z "$extra" ]] || return 1
 done < "$1"
}
backup_warning(){
 echo "WARNING: Original permissions were not recorded correctly in $1/permissions.tsv. Configuration backups remain available; automatic permission rollback is unavailable. No prior permissions have been guessed." >&2
}
ensure_user(){
 local created=false uid gid managed_uid managed_gid
 if id ktweb >/dev/null 2>&1 && [ ! -f "$ACCOUNT" ];then echo 'Existing ktweb account is not managed by this package; no identity changes made' >&2;return 1;fi
 if ! id ktweb >/dev/null 2>&1;then
  if [ ! -f "$ACCOUNT" ] && grep -qs '^ktweb:' /etc/group /opt/etc/group;then echo 'Existing ktweb group requires manual review' >&2;return 1;fi
  created=true
  if ! grep -qs '^ktweb:' /etc/group /opt/etc/group;then
   if command -v groupadd >/dev/null;then groupadd -r ktweb;else addgroup -S ktweb;fi
  fi
  if command -v useradd >/dev/null;then useradd -r -M -g ktweb -s /bin/false ktweb;else adduser -S -D -H -G ktweb -s /bin/false ktweb;fi
 fi
 id ktweb >/dev/null || { echo 'Cannot provision the dedicated web account' >&2;return 1; }
 uid=$(id -u ktweb);gid=$(id -g ktweb)
 [[ "$uid" =~ ^[0-9]+$ && "$gid" =~ ^[0-9]+$ ]] && [ "$uid" != 0 ] && [ "$gid" != 0 ] || { echo 'The dedicated web account must not use UID/GID 0' >&2;return 1; }
 if [ "$created" = false ];then read -r managed_uid managed_gid < "$ACCOUNT";[ "$uid" = "$managed_uid" ] && [ "$gid" = "$managed_gid" ] || { echo 'Managed web account identity changed unexpectedly' >&2;return 1; };fi
 printf '%s %s\n' "$uid" "$gid" > "$ACCOUNT";chmod 600 "$ACCOUNT"
}
restore(){
 local backup=$1 mode uid gid path
 [ -f "$backup/lighttpd.conf" ] || return 1
 valid_permissions "$backup/permissions.tsv" "${2:-}" || { backup_warning "$backup";return 1; }
 cp -p "$backup/lighttpd.conf" "$CONF"
 rm -f "$DIR/99-keentool-user.conf"
 while IFS= read -r path;do cp -p "$backup/conf.d/$(basename "$path")" "$path";done < "$backup/conf-files"
 while IFS=$'\t' read -r mode uid gid path;do [ ! -e "$path" ] || { chown "$uid:$gid" "$path";chmod "$mode" "$path"; };done < "$backup/permissions.tsv"
 rm -f "$MARK"
 /opt/sbin/lighttpd -tt -f "$CONF"
 [ -z "${INIT:-}" ] || /opt/bin/bash "$INIT" restart
}
case "${1:---check}" in
 --ensure-user)
  ensure_user
  if [ -f "$MARK" ];then
   backup=$(cat "$MARK");[[ "$backup" = /opt/var/backups/keentool-web/* ]] || exit 1
   # The last field remains a managed path even in old records missing metadata.
   valid_permissions "$backup/permissions.tsv" || backup_warning "$backup"
   if [ -f "$backup/permissions.tsv" ];then
    while IFS= read -r path;do [[ "$path" = /opt/* ]] || continue;[ ! -e "$path" ] || chgrp ktweb "$path";done < <(awk -F '\t' '{print $NF}' "$backup/permissions.tsv")
   fi
   for path in /opt/etc/keentool/admin/sessions/*;do [ ! -f "$path" ] || { chgrp ktweb "$path";chmod 660 "$path"; };done
   mkdir -p /opt/var/run/keentool-web;chown ktweb:ktweb /opt/var/run/keentool-web;chmod 770 /opt/var/run/keentool-web
  fi
  exit;;
 --rollback)
  [ -f "$MARK" ] || { echo 'Web isolation is not configured';exit 0; }
  backup=$(cat "$MARK");[[ "$backup" = /opt/var/backups/keentool-web/* ]] || exit 1
  INIT=$(cat "$backup/init");restore "$backup";echo "Previous web configuration restored from $backup";exit;;
 --check|--apply);;
 *)echo 'Usage: firewall_security harden-web [--check|--apply|--rollback]' >&2;exit 1;;
esac
[ "$(id -u)" = 0 ] || { echo 'Run this command from root SSH' >&2;exit 1; }
/opt/sbin/lighttpd -tt -f "$CONF"
[ ! -f "$MARK" ] || { backup=$(cat "$MARK");[[ "$backup" = /opt/var/backups/keentool-web/* ]] || exit 1;echo "Isolation already configured; backup: $backup";valid_permissions "$backup/permissions.tsv" || backup_warning "$backup";exit 0; }
grep -qF 'conf.d/*.conf' "$CONF" || { echo 'Unsupported include layout; no changes made' >&2;exit 1; }
if grep -E '^[[:space:]]*server\.(username|groupname)[[:space:]]*=' "$CONF" "$DIR/"*.conf >/dev/null;then echo 'An explicit web account already exists; review it before this migration' >&2;exit 1;fi
INIT='';for f in /opt/etc/init.d/S*lighttpd;do [ ! -f "$f" ] || INIT=$f;done
[ -n "$INIT" ] || { echo 'Dedicated lighttpd init script not found; no changes made' >&2;exit 1; }
active_conf(){ sed '/^[[:space:]]*#/d' "$1"; }
FAST='';for f in "$DIR/"*.conf;do if active_conf "$f" | grep 'php-cgi' >/dev/null && active_conf "$f" | grep '"socket"[[:space:]]*=>' >/dev/null;then [ -z "$FAST" ] || { echo 'Multiple PHP backends require manual migration' >&2;exit 1; };FAST=$f;fi;done
[ -n "$FAST" ] || { echo 'Local PHP-CGI socket configuration not found; no changes made' >&2;exit 1; }
[ "$(active_conf "$FAST" | grep -oE '"socket"[[:space:]]*=>' | wc -l | tr -d '[:space:]')" = 1 ] || { echo 'Multiple backend sockets require manual migration' >&2;exit 1; }
# Fail closed on concatenated paths or other expressions the narrow rewrite cannot preserve.
active_conf "$FAST" | grep -E '"socket"[[:space:]]*=>[[:space:]]*"[^"]+"[[:space:]]*([,)#]|$)' >/dev/null || { echo 'PHP socket must use a literal path; manual migration required' >&2;exit 1; }
echo 'Plan: dedicated ktweb account; root command broker; group-readable credentials; private writable session/backend directories; validated lighttpd restart with rollback.'
[ "${1:---check}" = --apply ] || exit 0
/opt/bin/bash /opt/bin/keentool_security_service status
ensure_user
backup=/opt/var/backups/keentool-web/$(date +%Y%m%d_%H%M%S)-$$
mkdir -p "$backup/conf.d";chmod 700 "$backup";cp -p "$CONF" "$backup/lighttpd.conf"
printf '%s\n' "$INIT" > "$backup/init";: > "$backup/conf-files";: > "$backup/permissions.tsv"
for f in "$DIR/"*.conf;do cp -p "$f" "$backup/conf.d/";printf '%s\n' "$f" >> "$backup/conf-files";done
remember(){
 local path=$1 value
 if [ -e "$path" ];then value=$(metadata "$path") || return 1;printf '%s\t%s\n' "$value" "$path" >> "$backup/permissions.tsv" || return 1;fi
}
grant(){
 local mode=$1 path=$2
 if [ -e "$path" ];then remember "$path" || return 1;chgrp ktweb "$path" || return 1;chmod "$mode" "$path" || return 1;fi
}
trap 'rc=$?;trap - ERR;echo "Web isolation failed; restoring $backup" >&2;restore "$backup" allow-empty || echo "Automatic web rollback failed; inspect $backup" >&2;exit "$rc"' ERR
metadata "$CONF" >/dev/null || { echo 'Filesystem metadata preflight failed' >&2;false; }
grant 710 /opt/etc/keentool
grant 750 /opt/etc/keentool/admin
grant 640 /opt/etc/keentool/admin/credentials.json
[ -f /opt/etc/keentool/admin/attempts.json ] || printf '{}\n' > /opt/etc/keentool/admin/attempts.json
grant 660 /opt/etc/keentool/admin/attempts.json
grant 770 /opt/etc/keentool/admin/sessions
for f in /opt/etc/keentool/admin/sessions/*;do [ ! -f "$f" ] || grant 660 "$f";done
grant 640 /opt/etc/keentool/firewall-api.token
grant 710 /opt/var/run/keentool-security
grant 660 /opt/var/run/keentool-security/broker.sock
mkdir -p /opt/var/run/keentool-web
chown ktweb:ktweb /opt/var/run/keentool-web;chmod 770 /opt/var/run/keentool-web
# Preserve the existing backend settings; relocate only its socket into its own writable directory.
cp -p "$FAST" "$FAST.kt-new"
sed -E '/^[[:space:]]*#/!s|("socket"[[:space:]]*=>[[:space:]]*)"[^"]*"|\1"/opt/var/run/keentool-web/php-fcgi.sock"|' "$FAST" > "$FAST.kt-new"
mv "$FAST.kt-new" "$FAST"
printf 'server.username = "ktweb"\nserver.groupname = "ktweb"\n' > "$DIR/99-keentool-user.conf"
# These dedicated lighttpd runtime locations are not the system-wide /opt/var/run directory.
for f in /opt/var/log/lighttpd /opt/var/lib/lighttpd /opt/var/lib/lighttpd/sockets;do [ ! -d "$f" ] || grant 770 "$f";done
for f in /opt/var/log/lighttpd/*;do [ ! -f "$f" ] || grant 660 "$f";done
/opt/sbin/lighttpd -p -f "$CONF" | sed -n -E 's/^[[:space:]]*ssl\.(pemfile|privkey)[[:space:]]*=[[:space:]]*"([^"]+)".*/\2/p' > "$backup/tls-files"
while IFS= read -r f;do [ ! -f "$f" ] || grant 640 "$f";done < "$backup/tls-files"
/opt/sbin/lighttpd -tt -f "$CONF"
/opt/bin/bash "$INIT" restart
sleep 3
seen=false;root_seen=false
for f in /proc/[0-9]*/comm;do
 name=$(cat "$f" 2>/dev/null || :)
 case "$name" in lighttpd|php-cgi|php8-cgi)
  seen=true;uid=$(awk '/^Uid:/{print $2}' "${f%/comm}/status" 2>/dev/null || echo unknown)
  [ "$uid" != 0 ] || root_seen=true;;
 esac
done
[ "$seen" = true ] && [ "$root_seen" = false ] || { echo 'Unprivileged web runtime could not be verified' >&2;false; }
printf '%s\n' "$backup" > "$MARK";chmod 600 "$MARK"
trap - ERR
echo "Web isolation active. Backup: $backup"
echo 'Verify dashboard, admin login and read-only log. Rollback: firewall_security harden-web --rollback'
