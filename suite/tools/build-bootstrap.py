#!/usr/bin/env python3
"""Build standalone and embedded first-upgrade entry points from the same verifier."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
php=(root/'support/release_update.php').read_text();shell=(root/'support/keentool_update').read_text();dependencies=(root/'support/dependencies.sh').read_text()
out='''#!/opt/bin/bash
# KeenTool stable bootstrap 1.0.7. Downloaded over trusted GitHub HTTPS; verify its source before running.
set -Eeuo pipefail
umask 077
# Recover a deleted working directory before starting child processes.
if ! builtin pwd -P >/dev/null 2>&1; then
    builtin cd / 2>/dev/null || { echo "Cannot recover the working directory" >&2; exit 1; }
fi
export PATH=${KT_PATH:-/opt/bin:/opt/sbin:/usr/bin:/usr/sbin:/bin:/sbin}
for essential in mktemp cat rm;do
 command -v "$essential" >/dev/null || { printf 'Missing bootstrap command: %s. Restore the router BusyBox utilities before migration.\n' "$essential" >&2;exit 1; }
done
work=$(mktemp -d "${KT_UPDATE_TMP:-/opt/tmp}/keentool-bootstrap.XXXXXX")
child=''
trap 'rm -rf "$work"' EXIT
cancel(){ trap - INT TERM;[ -z "$child" ] || { kill -TERM "$child" 2>/dev/null || :;wait "$child" || :; };exit 143; }
trap cancel INT TERM
cat > "$work/dependencies.sh" <<'KT_BOOTSTRAP_DEPS'
'''+dependencies+'''\nKT_BOOTSTRAP_DEPS
cat > "$work/release_update.php" <<'KT_BOOTSTRAP_PHP'
'''+php+'''\nKT_BOOTSTRAP_PHP
cat > "$work/keentool_update" <<'KT_BOOTSTRAP_SH'
'''+shell+'''\nKT_BOOTSTRAP_SH
KT_UPDATE_BOOTSTRAP=true KT_DEPENDENCIES="$work/dependencies.sh" KT_UPDATE_HELPER="$work/release_update.php" "${KT_UPDATE_BASH:-/opt/bin/bash}" "$work/keentool_update" --reinstall "$@" <&0 & child=$!
wait "$child";child=''
trap - INT TERM
'''
entry=(root/'support/legacy_entry.sh').read_text().replace('@BOOTSTRAP@',out.split('\n',1)[1].rstrip())
start='# BEGIN GENERATED LEGACY MIGRATION\n';end='# END GENERATED LEGACY MIGRATION\n'
p=root/'projects/KeenTool/keentool';manager=p.read_text()
if start in manager:
 before,rest=manager.split(start,1);_,after=rest.split(end,1)
else:
 before,after=manager.split('# KeenTool 2.0.0\n',1);after='# KeenTool 2.0.0\n'+after
expected=before+start+entry+end+after
if '--check' in sys.argv:
 if (root/'bootstrap.sh').read_text()!=out or manager!=expected:raise SystemExit('Regenerate bootstrap.sh and the manager migration entry with tools/build-bootstrap.py')
else:
 (root/'bootstrap.sh').write_text(out);(root/'bootstrap.sh').chmod(0o755);p.write_text(expected)
