"""Balanced menu confirmation, saved defaults and automatic first due conversion."""
from pathlib import Path
import os,subprocess,tempfile,json,sqlite3
root=Path(__file__).resolve().parents[1];php='/tmp/keentool-security-runtime/root/usr/bin/php8.3';bins='/tmp/keentool-security-runtime/root/usr/bin'
with tempfile.TemporaryDirectory(prefix='kt-balanced-menu-') as td:
 p=Path(td);mock=p/'database-cli';calls=p/'calls';mock.write_text('#!/bin/bash\nprintf "%s\\n" "$*" >> "$KT_TEST_CALLS"\n');mock.chmod(0o755)
 env=dict(os.environ,KT_HISTORY_PHP=php,KT_HISTORY_ENGINE=str(root/'support/history_engine.php'),KT_DATABASE_CLI=str(mock),KT_TEST_CALLS=str(calls),KT_HISTORY_ROOT=td,PATH=bins+':'+os.environ['PATH'])
 def menu(text):return subprocess.run(['bash',str(root/'support/firewall_history'),'menu'],input=text,env=env,text=True,capture_output=True,timeout=20)
 r=menu('2\nn\n0\n');assert r.returncode==0 and not calls.exists();assert '2. Apply Balanced' in r.stdout
 r=menu('2\ny\n0\n');assert r.returncode==0 and calls.read_text().splitlines()==['firewall balanced'];assert 'permanently' in r.stdout
 r=menu('3\n\n\n\n\n0\n');assert r.returncode==0,r.stderr
 conf=p/'opt/etc/keentool/firewall-history.conf';text=conf.read_text();assert all(x in text for x in ['HISTORY_RAW_DAYS="2"','HISTORY_HOURLY_DAYS="7"','HISTORY_DAILY_DAYS="365"'])
 # Old policy files do not opt in to structural migration by omission.
 conf.write_text('HISTORY_ENABLED="true"\nHISTORY_RAW_DAYS="7"\nHISTORY_HOURLY_DAYS="30"\n')
 db=p/'fw.db';c=sqlite3.connect(db);c.execute('create table ip_drops(timestamp integer,ip text,count integer,list_type text)');c.execute('insert into ip_drops values(100,"203.0.113.1",55,"main")');c.commit();c.close()
 env.update(KT_FW_DB=str(db),KT_FW_DB_BACKUPS=str(p/'backups'),KT_HISTORY_NOW='2000000000',TZ='UTC')
 def engine(action,*args):return subprocess.run([php,'-n',str(root/'support/history_engine.php'),action,*args],env=env,text=True,capture_output=True,timeout=40)
 r=engine('status');s=json.loads(r.stdout);assert s['storage']=='legacy' and not s['compact_requested'] and s['daily_days']==0
 # Installer-written fresh profile enables conversion at first due stats maintenance.
 conf.write_text('HISTORY_ENABLED="true"\nHISTORY_RAW_DAYS="2"\nHISTORY_HOURLY_DAYS="7"\nHISTORY_DAILY_DAYS="365"\nHISTORY_COMPACT="true"\n')
 recent=p/'recent.db';recent_db=sqlite3.connect(recent);recent_db.execute('create table ip_drops(timestamp integer,ip text,count integer,list_type text)');recent_db.execute('insert into ip_drops values(1999999999,"203.0.113.2",7,"main")');recent_db.commit();recent_db.close()
 recent_run=subprocess.run([php,'-n',str(root/'support/history_engine.php'),'run','--due'],env=dict(env,KT_FW_DB=str(recent)),text=True,capture_output=True,timeout=40);assert recent_run.returncode==0,recent_run.stderr;recent_status=json.loads(recent_run.stdout);assert recent_status['storage']=='compact' and recent_status['skipped']=='no old samples' and not recent_status['aggregated']
 recent_db=sqlite3.connect(recent);assert recent_db.execute('select timestamp,count,resolution from ip_drops').fetchall()==[(1999999999,7,0)];recent_db.close()
 r=engine('run','--due');assert r.returncode==0,r.stderr;s=json.loads(r.stdout);assert s['storage']=='compact' and s['compact_requested'];c=sqlite3.connect(db);assert c.execute('select sum(count) from ip_drops').fetchone()[0]==55;c.close()
 r=engine('run','--due');assert r.returncode==0 and json.loads(r.stdout)['skipped']=='not due'
 # Explicit expansion disables future automatic reconversion.
 r=subprocess.run([php,'-n',str(root/'support/database_engine.php'),'firewall','expand'],env=env,text=True,capture_output=True,timeout=40);assert r.returncode==0,r.stderr
 r=engine('status');s=json.loads(r.stdout);assert s['storage']=='legacy' and not s['compact_requested']
 print('PASS: menu consent/decline, exact Balanced command, custom 2/7/365 presets, legacy omission preserves policy, first due automatic compact conversion, totals, cadence and expansion disables reconversion.')
