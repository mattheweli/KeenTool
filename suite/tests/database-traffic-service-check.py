"""vnStat daemon lifecycle during explicit root-only database maintenance."""
from pathlib import Path
import tempfile,subprocess,os,sqlite3
root=Path(__file__).resolve().parents[1];php='/tmp/keentool-security-runtime/root/usr/bin/php8.3';bins='/tmp/keentool-security-runtime/root/usr/bin'
with tempfile.TemporaryDirectory(prefix='kt-db-services-') as td:
 p=Path(td);mock=p/'bin';mock.mkdir();db=p/'vnstat.db';state=p/'running';calls=p/'calls';init=p/'S32vnstat'
 (mock/'pidof').write_text('#!/bin/sh\n[ "$1" = vnstatd ] && [ -f "$KT_DAEMON_STATE" ] && echo 12345\n');(mock/'pidof').chmod(0o755)
 init.write_text('''#!/bin/sh
printf '%s\\n' "$1" >> "$KT_SERVICE_CALLS"
case "$1" in stop) rm -f "$KT_DAEMON_STATE";[ "${KT_STOP_FAIL:-0}" = 0 ];;start) [ "${KT_START_FAIL:-0}" = 0 ] || exit 1;touch "$KT_DAEMON_STATE";;esac
''');init.chmod(0o755)
 def database():
  db.unlink(missing_ok=True);c=sqlite3.connect(db);c.execute('create table interfaces(id integer primary key,name text,total integer)');c.execute("insert into interfaces values(1,'ppp0',123456789)");c.commit();c.close()
 env=dict(os.environ,KT_PATH=str(mock)+':'+bins+':'+os.environ['PATH'],KT_RUN_DIR=td,KT_COMMON=str(root/'support/common.sh'),KT_HISTORY_PHP=php,KT_DATABASE_ENGINE=str(root/'support/database_engine.php'),KT_VNSTAT_DB=str(db),KT_VNSTAT_INIT=str(init),KT_DAEMON_STATE=str(state),KT_SERVICE_CALLS=str(calls),KT_FW_DB_BACKUPS=str(p/'backups'))
 def run(**extra):return subprocess.run(['bash',str(root/'support/keentool_db'),'traffic','compact'],env=dict(env,**extra),text=True,capture_output=True,timeout=40)
 database();state.touch();r=run();assert r.returncode==0,r.stderr;assert calls.read_text().splitlines()==['stop','start'] and state.exists();c=sqlite3.connect(db);assert c.execute('select total from interfaces').fetchone()[0]==123456789;c.close()
 calls.unlink();state.unlink();r=run();assert r.returncode==0 and not state.exists() and not calls.exists()
 state.touch();r=run(KT_STOP_FAIL='1');assert r.returncode!=0 and state.exists();assert calls.read_text().splitlines()==['stop','start'];calls.unlink()
 # Invalid database after stopping still restarts the original daemon.
 db.write_bytes(b'not a database');r=run();assert r.returncode!=0 and state.exists();assert calls.read_text().splitlines()==['stop','start'];calls.unlink()
 database();r=run(KT_START_FAIL='1');assert r.returncode!=0 and not state.exists() and 'incomplete' in r.stderr
 print('PASS: vnStat running/stopped state, exact traffic counters, stop-error restart, database-error restart and explicit restart-failure reporting.')
