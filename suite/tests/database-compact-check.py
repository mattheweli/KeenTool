"""Real SQLite/PHP-core migration, temporal guards, compatibility and maintenance checks."""
from pathlib import Path
import tempfile,os,sqlite3,subprocess,json,datetime,time
from zoneinfo import ZoneInfo
root=Path(__file__).resolve().parents[1];php='/tmp/keentool-security-runtime/root/usr/bin/php8.3';bins='/tmp/keentool-security-runtime/root/usr/bin'
os.environ['TZ']='Europe/Rome';time.tzset()
def rows(c):return c.execute('select timestamp,ip,count,list_type,resolution from ip_drops order by 1,2,3,4,5').fetchall()
def totals(c):return c.execute('select ip,list_type,sum(count) from ip_drops group by 1,2 order by 1,2').fetchall()
with tempfile.TemporaryDirectory(prefix='kt-compact-') as td:
 p=Path(td);db=p/'fw.db';now=int(datetime.datetime(2026,11,8,13,tzinfo=ZoneInfo('Europe/Rome')).timestamp())
 c=sqlite3.connect(db);c.executescript('CREATE TABLE ip_drops(timestamp INTEGER,ip TEXT,count INTEGER,list_type TEXT,resolution INTEGER NOT NULL DEFAULT 0);CREATE INDEX idx_ip ON ip_drops(ip);CREATE INDEX idx_ip_ts ON ip_drops(timestamp);CREATE INDEX idx_list_ts ON ip_drops(list_type,timestamp);CREATE TABLE drops(timestamp INTEGER,list_name TEXT,count INTEGER);CREATE TABLE ip_info(ip TEXT PRIMARY KEY,port_history TEXT);CREATE TABLE abuse_reports(ip TEXT PRIMARY KEY,last_sent INTEGER);')
 data=[(stamp,ip,3,kind,0) for stamp in range(now-500*86400,now,7200) for ip,kind in [('203.0.113.1','main'),('2001:db8::1','geo')]]
 # Duplicate rows must retain multiplicity, not merely set equality.
 data+=data[:3];c.executemany('insert into ip_drops values(?,?,?,?,?)',data)
 c.execute('insert into drops values(?,?,?)',(now,'AutoBan',99));ports=','.join(str(i)+'/tcp' for i in range(1,65536));c.execute('insert into ip_info values(?,?)',('203.0.113.1',ports));c.execute('insert into abuse_reports values(?,?)',('203.0.113.1',now));c.commit();original=rows(c);before_totals=totals(c);before_bytes=db.stat().st_size;c.close()
 env=dict(os.environ,PATH=bins+':'+os.environ['PATH'],KT_HISTORY_ROOT=td,KT_FW_DB=str(db),KT_FW_DB_BACKUPS=str(p/'backups'),KT_HISTORY_NOW=str(now))
 def run(action,kind='firewall',extra=None):
  return subprocess.run([php,'-n',str(root/'support/database_engine.php'),kind,action],env=dict(env,**(extra or {})),text=True,capture_output=True,timeout=100)
 r=run('compact');assert r.returncode==0,r.stderr;result=json.loads(r.stdout);backup=Path(result['backup']);assert backup.stat().st_mode&0o777==0o600
 c=sqlite3.connect(db);assert rows(c)==original and totals(c)==before_totals;assert db.stat().st_size<before_bytes
 assert c.execute('select port_history from ip_info').fetchone()[0]==ports
 assert c.execute('pragma integrity_check').fetchone()[0]=='ok'
 # Real unmodified four-column collector inserts through the compatibility view.
 c.execute('insert into ip_drops(timestamp,ip,count,list_type) values(?,?,?,?)',(now+1,'198.51.100.2',17,'trap'));c.commit();assert c.execute("select resolution from ip_drops where ip='198.51.100.2'").fetchone()[0]==0
 c.execute("delete from ip_drops where ip='198.51.100.2'");c.commit();assert rows(c)==original;c.close()
 r=run('compact');assert r.returncode==0 and not json.loads(r.stdout)['changed'],r.stderr
 r=run('balanced');assert r.returncode==0,r.stderr;c=sqlite3.connect(db);assert totals(c)==before_totals
 levels=dict(c.execute('select resolution,count(*) from ip_drops group by resolution'));assert set(levels)=={0,3600,86400,2592000},levels
 # Recent samples unchanged; older monthly totals retain their calendar-month sums.
 cutoff=c.execute("select strftime('%s',date(?-2*86400,'unixepoch','localtime'),'utc')",(now,)).fetchone()[0]
 assert c.execute('select * from ip_drops where resolution=0 order by 1,2,3,4,5').fetchall()==[x for x in original if x[0]>=int(cutoff)]
 expected={}
 for stamp,ip,n,kind,level in original:
  k=(datetime.datetime.fromtimestamp(stamp).strftime('%Y-%m'),ip,kind);expected[k]=expected.get(k,0)+n
 actual={(month,ip,kind):n for month,ip,kind,n in c.execute("select strftime('%Y-%m',timestamp,'unixepoch','localtime'),ip,list_type,sum(count) from ip_drops group by 1,2,3")};assert actual==expected
 assert c.execute('select * from drops').fetchall()==[(now,'AutoBan',99)]
 assert c.execute('select * from abuse_reports').fetchall()==[('203.0.113.1',now)]
 stable=rows(c);c.close();r=run('balanced');assert r.returncode==0,r.stderr;c=sqlite3.connect(db);assert rows(c)==stable;c.close()
 # Downgrade storage without discarding events collected after conversion.
 r=run('expand');assert r.returncode==0,r.stderr;c=sqlite3.connect(db);assert rows(c)==stable;assert c.execute("select type from sqlite_master where name='ip_drops'").fetchone()[0]=='table';c.close()
 # Custom indexes are preserved by refusing conversion.
 c=sqlite3.connect(db);c.execute('create index operator_index on ip_drops(count)');c.commit();c.close();r=run('compact');assert r.returncode!=0 and 'Custom IP index' in r.stderr
 # Ping and traffic compaction preserve every row, including exact peaks and counters.
 for kind in ['ping','traffic']:
  other=p/(kind+'.db');c=sqlite3.connect(other)
  for table in ['stats','stats_v6']:
   c.execute(f'create table {table}(id integer primary key,timestamp integer,ping real,jitter real,loss real)')
   c.executemany(f'insert into {table}(timestamp,ping,jitter,loss) values(?,?,?,?)',[(now+i,999.9 if i==50 else 10.,.2,100. if i==51 else 0.) for i in range(1000)])
   c.execute(f'delete from {table} where id>100')
  c.commit();snap=c.iterdump();before='\n'.join(snap);size=other.stat().st_size;c.close()
  extra={'KT_PING_DB':str(other),'KT_VNSTAT_DB':str(other)};r=run('compact',kind,extra);assert r.returncode==0,r.stderr;c=sqlite3.connect(other);assert '\n'.join(c.iterdump())==before;assert other.stat().st_size<size;c.close()
 # Shared writer lock prevents concurrent collection and maintenance.
 lock=p/'firewall-db.lockdir';lock.mkdir();(lock/'pid').write_text(str(os.getpid())+'\n')
 r=subprocess.run(['bash',str(root/'support/keentool_db'),'firewall','compact'],env=dict(env,KT_RUN_DIR=td,KT_COMMON=str(root/'support/common.sh'),KT_HISTORY_PHP=php,KT_DATABASE_ENGINE=str(root/'support/database_engine.php')),capture_output=True,text=True);assert r.returncode!=0 and (lock/'pid').exists()
 print('PASS: compact IP dictionary, exact row multiplicity, all IP/list/month totals, recent raw samples, unchanged ports/global/reporting state, monthly balanced profile, compatible writes, idempotence, current-data expansion, custom-index refusal, private verified backup, ping/traffic lossless VACUUM and shared lock.')
