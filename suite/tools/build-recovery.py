#!/usr/bin/env python3
"""Build a standalone recovery entry with the exact current rollback implementation."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
rollback=(root/'rollback.sh').read_text()
prefix=r'''#!/opt/bin/bash
# KeenTool interrupted firewall upgrade recovery v1.0.0 — 2026-10-28.
# Verify this release asset's SHA-256 before running. Preserve all recovery copies.
set -Eeuo pipefail
umask 077
[ "$(id -u)" = 0 ] || { echo 'Run as root' >&2;exit 1; }
root=${KT_INSTALL_ROOT:-}
export PATH="$root/opt/bin:/opt/bin:/opt/sbin:/usr/bin:/usr/sbin:/bin:/sbin"
backup=${1:-};marker="$root/opt/etc/keentool/firewall-upgrade.pending"
[ "$#" = 1 ] || { echo 'Usage: recover-firewall-upgrade.sh VERIFIED-RECOVERY-DIRECTORY' >&2;exit 2; }
php_cli=''
for p in "$root/opt/bin/php-cli" "$root/opt/bin/php8" "$root/opt/bin/php";do
 if [ -x "$p" ] && "$p" -r 'exit(PHP_SAPI==="cli"?0:1);' >/dev/null 2>&1;then php_cli=$p;break;fi
done
[ -n "$php_cli" ] || { echo 'PHP CLI is required' >&2;exit 1; }
"$php_cli" -r '$p=$argv[1];$r=rtrim(getenv("KT_INSTALL_ROOT")?:"","/");$a=realpath($r."/opt/var/backups/keentool-release");$b=realpath($r."/opt/var/lib/keentool-release/transactions");$real=realpath($p);exit($real!==false&&!is_link($p)&&in_array(dirname($real),array_filter([$a,$b]),true)&&preg_match("/^[0-9]{8}_[0-9]{6}-[0-9]+-[a-f0-9]{6}$/D",basename($real))?0:1);' "$backup" || { echo 'Invalid recovery directory' >&2;exit 1; }
[ -f "$marker" ] || { echo 'No pending firewall marker. Check installed version, firewall health and service state; recovery copies were left untouched.';exit 0; }
[ "$(sed -n '1p' "$marker")" = "$backup" ] || { echo 'This directory does not match the pending transaction' >&2;exit 1; }
token=$(sed -n '2p' "$marker");[[ "$token" =~ ^[a-f0-9]{48}$ ]] || exit 1
[ "$(sed -n '3p' "$marker")" = "$(cat /proc/sys/kernel/random/boot_id)" ] || { echo 'This transaction belongs to a previous boot; use reviewed boot recovery before retrying.' >&2;exit 1; }
for file in release_install.php rollback.sh firewall_upgrade transaction.json;do [ -f "$backup/$file" ] && [ ! -L "$backup/$file" ] || { echo "Missing regular recovery file: $file" >&2;exit 1; };done
"$php_cli" "$backup/release_install.php" verify-backup "$backup"
maintenance="$root/opt/etc/keentool/maintenance"
if [ -e "$maintenance" ];then
 owner=$(cat "$maintenance")
 [[ "$owner" =~ ^[0-9]+$ ]] || { echo 'Invalid maintenance owner; review before recovery' >&2;exit 1; }
 if kill -0 "$owner" 2>/dev/null;then echo 'An installer/maintenance owner is still running. Wait for it to finish before recovery.' >&2;exit 75;fi
 rm -f "$maintenance"
 rmdir "$root/opt/tmp/keentool-install.lockdir" 2>/dev/null || :
fi
stage=$(mktemp "$backup/.rollback-fix.XXXXXX")
trap 'rm -f "$stage"' EXIT
cat > "$stage" <<'KT_RECOVERY_ROLLBACK'
'''
suffix=r'''
KT_RECOVERY_ROLLBACK
bash -n "$stage"
[ -f "$backup/rollback.sh.before-service-fix" ] || cp -p "$backup/rollback.sh" "$backup/rollback.sh.before-service-fix"
chmod 700 "$stage";mv -f "$stage" "$backup/rollback.sh"
echo 'Verified recovery copies. Restoring previous owned rules/source and retrying affected services.'
if ! bash "$backup/firewall_upgrade" recover "$backup" "$token";then
 echo "Recovery remains incomplete. Keep $backup and review firewall-upgrade/guard.log and the errors above." >&2
 exit 1
fi
echo 'Pending firewall transaction recovered. All recovery copies were retained.'
echo 'Check firewall_health and lighttpd/ulogd/vnstatd, then update to package 2.0.15 or later.'
'''
expected=prefix+rollback.rstrip()+suffix
p=root/'support/recover_firewall_upgrade.sh'
if '--check' in sys.argv:
 if not p.is_file() or p.read_text()!=expected:raise SystemExit('Regenerate recovery entry with tools/build-recovery.py')
else:p.write_text(expected);p.chmod(0o755)
