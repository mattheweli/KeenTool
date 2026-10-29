"""Run the installer's actual firewall-choice block without a terminal or service mutation."""
from pathlib import Path
import tempfile,os,subprocess,json
root=Path(__file__).resolve().parents[1];php='/tmp/keentool-security-runtime/root/usr/bin/php8.3'
s=(root/'install.sh').read_text();a=s.index('unset KT_INSTALL_DEFER_FIREWALL\n');end='[ "$fw_fd" = 0 ] || exec {fw_fd}<&-\n';b=s.index(end,a)+len(end);block=s[a:b]
with tempfile.TemporaryDirectory(prefix='kt-fw-choice-') as td:
 p=Path(td);engine=p/'engine.php';engine.write_text('<?php echo getenv("KT_TEST_STATE");')
 runner=p/'choice.sh';runner.write_text('''#!/bin/bash
set -Eeuo pipefail
php_cli=$KT_TEST_PHP;engine=$KT_TEST_ENGINE;base=$KT_TEST_BASE
action=${KT_TEST_ACTION:-apply};start=${KT_TEST_START:-true}
apply_firewall=false;fw_auto_confirm=false;fw_deferred=false
'''+block+'''printf 'CHOICE:%s:%s:%s:%s\\n' "$apply_firewall" "$fw_auto_confirm" "$fw_deferred" "${KT_INSTALL_DEFER_FIREWALL:-0}"
''')
 state={'enabled':True,'hook_exists':True,'needed':True,'auto_apply':True};env=dict(os.environ,KT_TEST_PHP=php,KT_TEST_ENGINE=str(engine),KT_TEST_BASE=td)
 def run(value,**extra):return subprocess.run(['bash',str(runner)],stdin=subprocess.DEVNULL,env=dict(env,KT_TEST_STATE=json.dumps(value),**extra),capture_output=True,text=True,timeout=10)
 r=run(state);assert r.returncode==0 and 'CHOICE:true:true:false:0' in r.stdout and '[y/N]' not in r.stderr,r.stdout+r.stderr
 r=run(state,KT_TEST_ACTION='plan');assert r.returncode==0 and 'CHOICE:true:true:false:0' in r.stdout
 r=run(state,KT_TEST_START='false');assert r.returncode==0 and 'CHOICE:false:false:true:1' in r.stdout
 r=run(dict(state,auto_apply=False));assert r.returncode==0 and 'CHOICE:false:false:true:1' in r.stdout and '[y/N]' not in r.stderr
 r=run(dict(state,enabled=False));assert r.returncode==0 and 'CHOICE:false:false:false:0' in r.stdout
 r=run(dict(state,needed=False));assert r.returncode==0 and 'CHOICE:false:false:false:0' in r.stdout
 print('PASS: actual installer decision block, headless adopted-hook apply without duplicate prompt, plan consistency, no-start deferral, first-migration deferral and disabled/current preservation.')
