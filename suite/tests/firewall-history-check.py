"""Exercise progressive aggregation with real SQLite and PHP core only; no router/SMTP."""
from pathlib import Path
import sqlite3,subprocess,tempfile,os,json,time,hashlib,datetime
from zoneinfo import ZoneInfo
root=Path(__file__).resolve().parents[1]
php='/tmp/keentool-security-runtime/root/usr/bin/php8.3'
binaries='/tmp/keentool-security-runtime/root/usr/bin'
engine=root/'support/history_engine.php'
def snapshot(db):
 c=sqlite3.connect(db);out={}
 for (name,) in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall():
  out[name]=c.execute('SELECT * FROM "'+name+'" ORDER BY 1,2').fetchall()
 c.close();return out
def totals(c):return c.execute('SELECT ip,list_type,SUM(count) FROM ip_drops GROUP BY ip,list_type ORDER BY 1,2').fetchall()
def days(c):return c.execute("SELECT date(timestamp,'unixepoch','localtime'),ip,list_type,SUM(count) FROM ip_drops GROUP BY 1,2,3 ORDER BY 1,2,3").fetchall()
os.environ['TZ']='Europe/Rome';time.tzset()
with tempfile.TemporaryDirectory(prefix='kt-history-check-') as td:
 p=Path(td);db=p/'fw.db';now=int(datetime.datetime(2026,11,8,13,tzinfo=ZoneInfo('Europe/Rome')).timestamp());rawcut=int(datetime.datetime.fromtimestamp(now-7*86400,ZoneInfo('Europe/Rome')).replace(hour=0,minute=0,second=0).timestamp())
 c=sqlite3.connect(db);c.executescript('PRAGMA journal_mode=WAL;CREATE TABLE ip_drops(timestamp INTEGER,ip TEXT,count INTEGER,list_type TEXT);CREATE INDEX idx_ip ON ip_drops(ip);CREATE INDEX idx_ip_ts ON ip_drops(timestamp);CREATE INDEX idx_list_ts ON ip_drops(list_type,timestamp);CREATE TABLE drops(timestamp INTEGER,list_name TEXT,count INTEGER);CREATE TABLE ip_info(ip TEXT PRIMARY KEY,port_history TEXT);CREATE TABLE abuse_reports(ip TEXT PRIMARY KEY,last_sent INTEGER);CREATE TABLE reported_ips(ip TEXT PRIMARY KEY,last_report INTEGER);')
 rows=[(stamp,ip,offset%19+1,kind) for offset,stamp in enumerate(range(now-90*86400,now,1800)) for ip,kind in [('203.0.113.1','main'),('2001:db8::1','geo'),('198.51.100.2','trap')]]
 # Spring DST data also exercises the 23-hour day; autumn data includes the repeated hour.
 spring=int(datetime.datetime(2026,3,29,tzinfo=ZoneInfo('Europe/Rome')).timestamp());rows.extend((spring+i*1800,'203.0.113.1',3,'main') for i in range(46))
 c.executemany('INSERT INTO ip_drops VALUES(?,?,?,?)',rows);c.execute('INSERT INTO drops VALUES(?,?,?)',(now,'FirewallBlock',9999));c.execute('INSERT INTO ip_info VALUES(?,?)',('203.0.113.1',','.join(str(i)+'/tcp' for i in range(1,65536))));c.execute('INSERT INTO abuse_reports VALUES(?,?)',('203.0.113.1',now));c.execute('INSERT INTO reported_ips VALUES(?,?)',('203.0.113.1',now));c.commit();before=snapshot(db);alltotals=totals(c);alldays=days(c);recent=c.execute('SELECT * FROM ip_drops WHERE timestamp>=? ORDER BY 1,2',(rawcut,)).fetchall();c.close()
 env=dict(os.environ,KT_HISTORY_ROOT=td,KT_FW_DB=str(db),KT_FW_DB_BACKUPS=str(p/'backups'),KT_HISTORY_NOW=str(now),PATH=binaries+':'+os.environ['PATH'])
 def run(action='run',extra=None,args=(),input=None):
  return subprocess.run([php,'-n',str(engine),action,*args],env=dict(env,**(extra or {})),input=input,text=True,capture_output=True,timeout=40)
 r=run();assert r.returncode==0,r.stderr;result=json.loads(r.stdout);assert result['compacted'] and result['after_bytes']<result['before_bytes']
 c=sqlite3.connect(db);assert totals(c)==alltotals;assert days(c)==alldays;assert c.execute('SELECT timestamp,ip,count,list_type FROM ip_drops WHERE resolution=0 ORDER BY 1,2').fetchall()==recent;assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
 fall=int(datetime.datetime(2026,10,25,2,tzinfo=ZoneInfo('Europe/Rome'),fold=0).timestamp());assert c.execute("SELECT count(DISTINCT timestamp) FROM ip_drops WHERE timestamp>=? AND timestamp<? AND resolution=3600",(fall,fall+7200)).fetchone()[0]==2
 levels=dict(c.execute('SELECT resolution,count(*) FROM ip_drops GROUP BY resolution'));assert set(levels)=={0,3600,86400};assert sum(levels.values())<len(rows)//2
 for name,data in before.items():
  if name!='ip_drops':assert snapshot(db)[name]==data,name
 backup=Path(result['backup']);assert snapshot(backup)==before;assert backup.stat().st_mode&0o777==0o600;assert backup.parent.stat().st_mode&0o777==0o700
 stable=c.execute('SELECT * FROM ip_drops ORDER BY 1,2,4,5').fetchall();c.close()
 r=run();assert r.returncode==0,r.stderr;c=sqlite3.connect(db);assert c.execute('SELECT * FROM ip_drops ORDER BY 1,2,4,5').fetchall()==stable;c.close();assert len(list((p/'backups').glob('*/firewall_stats.db')))==1
 r=run(args=('--due',));assert json.loads(r.stdout)['skipped']=='not due'
 r=run(extra={'TZ':'UTC'});assert r.returncode!=0 and 'timezone changed' in r.stderr
 # Expanding retention cannot magically recover existing coarser buckets.
 r=run('configure',input=json.dumps({'HISTORY_RAW_DAYS':90,'HISTORY_HOURLY_DAYS':365}));assert r.returncode==0,r.stderr
 r=run();assert r.returncode==0,r.stderr;c=sqlite3.connect(db);assert c.execute('SELECT * FROM ip_drops ORDER BY 1,2,4,5').fetchall()==stable
 # The four explicit insert columns remain compatible with old/new collectors.
 c.execute('INSERT INTO ip_drops(timestamp,ip,count,list_type) VALUES(?,?,?,?)',(now+1,'203.0.113.2',9,'trap'));c.commit();assert c.execute("SELECT resolution FROM ip_drops WHERE ip='203.0.113.2'").fetchone()[0]==0;c.close()
 r=run('configure',input=json.dumps({'HISTORY_ENABLED':'false'}));assert r.returncode==0
 unchanged=snapshot(db);r=run();assert json.loads(r.stdout)['skipped']=='disabled' and snapshot(db)==unchanged
 config=p/'opt/etc/keentool/firewall-history.conf';saved=config.read_bytes();r=run('configure',input='{"HISTORY_RAW_DAYS":60,"HISTORY_HOURLY_DAYS":30}');assert r.returncode!=0 and config.read_bytes()==saved
 # Initial backup failure must prevent schema/data changes.
 small=p/'other.db';c=sqlite3.connect(small);c.execute('CREATE TABLE ip_drops(timestamp INTEGER,ip TEXT,count INTEGER,list_type TEXT)');c.execute('INSERT INTO ip_drops VALUES(1,"203.0.113.3",5,"main")');c.commit();c.close();original=snapshot(small);bad=p/'blocked';bad.write_text('not a directory')
 isolated=p/'isolated';isolated.mkdir();r=run(extra={'KT_HISTORY_ROOT':str(isolated),'KT_FW_DB':str(small),'KT_FW_DB_BACKUPS':str(bad)});assert r.returncode!=0 and snapshot(small)==original
 # Integer overflow aborts the complete transaction, including new schema columns.
 c=sqlite3.connect(small);c.execute('INSERT INTO ip_drops VALUES(2,"203.0.113.3",9223372036854775807,"main")');c.commit();c.close();original=snapshot(small)
 r=run(extra={'KT_HISTORY_ROOT':str(isolated),'KT_FW_DB':str(small)});assert r.returncode!=0 and 'overflow' in r.stderr and snapshot(small)==original
 # Standalone maintenance uses exactly the collector's firewall-db lock.
 lock=p/'firewall-db.lockdir';lock.mkdir();(lock/'pid').write_text(str(os.getpid())+'\n')
 r=subprocess.run(['bash',str(root/'support/firewall_history'),'run'],env=dict(env,KT_COMMON=str(root/'support/common.sh'),KT_RUN_DIR=td,KT_HISTORY_PHP=php,KT_HISTORY_ENGINE=str(engine)),text=True,capture_output=True);assert r.returncode!=0 and (lock/'pid').exists()
 print('PASS: hourly/daily rollup, 23/25-hour DST days, exact IP/list and calendar-day totals, untouched recent samples/ports/reporting/global counters, verified private backup, idempotence, daily cadence, no detail re-expansion, disabled policy, invalid settings, backup/overflow rollback, shared writer lock and PHP core-only portability.')
