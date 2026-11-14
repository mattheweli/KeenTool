"""Check Legacy-compatible analytics without contacting the production endpoint."""
from pathlib import Path
import tempfile,subprocess,os,json,stat,concurrent.futures
root=Path(__file__).resolve().parents[1]
php=Path('/tmp/keentool-security-runtime/root/usr/bin/php8.3')
helper=root/'support/analytics.php'
with tempfile.TemporaryDirectory() as td:
 b=Path(td);mock=b/'curl';requests=b/'requests'
 mock.write_text('''#!/usr/bin/python3
import os,sys,json
from pathlib import Path
b=Path(os.environ['FIXTURE'])
with (b/'requests').open('a') as f:f.write(json.dumps(sys.argv[1:])+'\\n')
if (b/'fail').exists():sys.exit(28)
print('302' if (b/'redirect').exists() else '204',end='')
''');mock.chmod(0o755)
 env=dict(os.environ,KT_INSTALL_ROOT=td,KT_ANALYTICS_CURL=str(mock),FIXTURE=td)
 def run(*args,**kwargs):return subprocess.run([str(php),'-n',str(helper),*args],env=kwargs.get('env',env),capture_output=True,text=True,timeout=8)
 cfg=b/'opt/etc/keentool';uid=b/'opt/etc/keentool.id'
 assert run('status').returncode==0 and not uid.exists() and not requests.exists()
 assert run('off').returncode==0;assert run('record','install','2.0.27','').returncode==0
 assert not uid.exists() and not requests.exists()
 assert run('on').returncode==0
 uid.write_text('legacy-uuid-12345678\n')
 r=run('record','install','2.0.27','');assert r.returncode==0,r.stderr
 rows=[json.loads(x) for x in requests.read_text().splitlines()]
 assert len(rows)==1 and rows[0][-1]=='https://keentoolstats.laniakear.workers.dev/track/install?uid=legacy-uuid-12345678'
 assert rows[0][rows[0].index('--connect-timeout')+1]=='2' and rows[0][rows[0].index('--max-time')+1]=='3'
 assert '--location' not in rows[0] and '--insecure' not in rows[0]
 run('record','install','2.0.27','');run('record','update','2.0.27','2.0.27')
 assert len(requests.read_text().splitlines())==1 and uid.read_text()=='legacy-uuid-12345678\n'
 (b/'fail').touch();assert run('record','update','2.0.28','2.0.27').returncode==0
 state=json.loads((cfg/'analytics-state.json').read_text());assert len(state['pending'])==1 and state['last_delivery']=='pending'
 (b/'fail').unlink();assert run('retry').returncode==0
 assert json.loads((cfg/'analytics-state.json').read_text())['pending']==[]
 (b/'redirect').touch();run('record','update','2.0.29','2.0.28')
 assert len(json.loads((cfg/'analytics-state.json').read_text())['pending'])==1
 run('off');assert json.loads((cfg/'analytics-state.json').read_text())['pending']==[]
 n=len(requests.read_text().splitlines());run('retry');assert len(requests.read_text().splitlines())==n
 (b/'redirect').unlink();run('on')
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:list(ex.map(lambda _:run('record','update','2.0.30','2.0.29'),range(8)))
 assert len(requests.read_text().splitlines())==n+1
 assert (cfg/'analytics.json').stat().st_mode&0o777==0o600
 assert (cfg/'analytics-state.json').stat().st_mode&0o777==0o600
 uid.write_text('invalid ID with spaces\n');r=run('record','update','2.0.31','2.0.30');assert r.returncode==1 and 'left unchanged' in r.stderr
 assert uid.read_text()=='invalid ID with spaces\n'
 uid.unlink();assert run('record','update','2.0.31','2.0.30').returncode==0
 assert uid.stat().st_mode&0o777==0o600 and len(uid.read_text().strip())==36
 # Default root-isolated fixtures never call a real curl process.
 safeenv=dict(env);safeenv.pop('KT_ANALYTICS_CURL')
 n=len(requests.read_text().splitlines());assert run('record','update','2.0.32','2.0.31',env=safeenv).returncode==0
 assert len(requests.read_text().splitlines())==n and len(json.loads((cfg/'analytics-state.json').read_text())['pending'])==1
 # Source integration: one hook, after all guarded checks and rollback handling.
 installer=(root/'install.sh').read_text()
 hook=installer.index('analytics.php" record')
 assert hook>installer.index('trap - ERR INT TERM') and hook>installer.index('firewall_upgrade" run')
 assert hook>installer.index('"$engine" commit') and installer.count('analytics.php" record')==1
 assert '&& ! "$php_cli" "$runroot/lib/keentool/analytics.php" record' in installer
 manager=(root/'projects/KeenTool/keentool').read_text()
 assert 'send_analytics' not in manager and '--analytics)' in manager and 'i) kt_analytics_menu' in manager
print('PASS: Legacy UID/endpoint, install/update events, same-version repair skip, local dedup/concurrency, timeout/HTTP failure queue and retry, redirects rejected, opt-out clears pending, private state, invalid-ID preservation, no real analytics from fixtures, post-success-only installer hook and menu wiring.')
