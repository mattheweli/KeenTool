#!/usr/bin/env python3
"""Build a self-contained first-upgrade entry point for legacy/alpha installations."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
php=(root/'support/release_update.php').read_text();shell=(root/'support/keentool_update').read_text()
out='''#!/opt/bin/bash
# KeenTool stable bootstrap 1.0.0. Downloaded over trusted GitHub HTTPS; verify its source before running.
set -Eeuo pipefail
umask 077
export PATH=/opt/bin:/opt/sbin:/usr/bin:/usr/sbin:/bin:/sbin
work=$(mktemp -d /opt/tmp/keentool-bootstrap.XXXXXX)
trap 'rm -rf "$work"' EXIT
cat > "$work/release_update.php" <<'KT_BOOTSTRAP_PHP'
'''+php+'''\nKT_BOOTSTRAP_PHP
cat > "$work/keentool_update" <<'KT_BOOTSTRAP_SH'
'''+shell+'''\nKT_BOOTSTRAP_SH
KT_UPDATE_BOOTSTRAP=true KT_UPDATE_HELPER="$work/release_update.php" /opt/bin/bash "$work/keentool_update" --reinstall "$@"
'''
(root/'bootstrap.sh').write_text(out);(root/'bootstrap.sh').chmod(0o755)
