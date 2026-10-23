from pathlib import Path
import sqlite3,subprocess,tempfile,os,hashlib,json
root=Path(__file__).resolve().parents[1];script=root/'projects/keenetic-firewall/scripts/firewall_stats.sh';binary=Path('/tmp/keentool-security-runtime/root/usr/bin/sqlite3')
def snapshot(path):
 c=sqlite3.connect(path);out={}
 for table,sql in c.execute("SELECT name,sql FROM sqlite_master WHERE type='table' ORDER BY name").fetchall():
  cols=','.join('"'+r[1]+'"' for r in c.execute('PRAGMA table_info("'+table+'")'));h=hashlib.sha256();n=0
  for row in c.execute('SELECT '+cols+' FROM "'+table+'" ORDER BY '+cols):h.update(json.dumps(row,separators=(',',':')).encode()+b'\n');n+=1
  out[table]=(sql,n,h.hexdigest())
 c.close();return out
with tempfile.TemporaryDirectory() as td:
 p=Path(td);bin=p/'bin';bin.mkdir();(bin/'sqlite3').symlink_to(binary)
 # Kernel/capture commands must never run in database-only maintenance.
 for name in ['ipset','iptables','tcpdump']:
  f=bin/name;f.write_text('#!/bin/bash\necho called >> "'+str(p/'kernel-called')+'"\nexit 99\n');f.chmod(0o755)
 db=p/'firewall.db';c=sqlite3.connect(db);c.execute('PRAGMA journal_mode=WAL');c.execute('PRAGMA wal_autocheckpoint=0');c.executescript('CREATE TABLE ip_drops(timestamp INTEGER,ip TEXT,count INTEGER,list_type TEXT);CREATE INDEX idx_list_ts_ip ON ip_drops(list_type,timestamp,ip);CREATE TABLE ip_info(ip TEXT PRIMARY KEY,port_history TEXT);CREATE TABLE drops(timestamp INTEGER,count INTEGER);CREATE TABLE abuse_reports(ip TEXT PRIMARY KEY,last_sent INTEGER);')
 c.executemany('INSERT INTO ip_drops VALUES(?,?,?,?)',[(1700000000+i,'2001:db8::'+str(i%500),i%70,'trap') for i in range(3000)]);c.execute('INSERT INTO ip_info VALUES(?,?)',('2001:db8::1',','.join(str(i)+'/tcp' for i in range(1,65536))));c.execute('INSERT INTO abuse_reports VALUES(?,?)',('203.0.113.1',1700000000));c.commit();writer=c;assert Path(str(db)+'-wal').stat().st_size>0;before=snapshot(db)
 env=dict(os.environ,KT_COMMON=str(root/'support/common.sh'),KT_RUN_DIR=td,KT_FW_DB=str(db),KT_FW_DB_BACKUPS=str(p/'backups'),KT_PATH=str(bin)+':'+os.environ['PATH'])
 def run(extra=None):return subprocess.run(['bash',str(script),'--optimize-db'],env=dict(env,**(extra or {})),text=True,capture_output=True,timeout=60)
 r=run();assert r.returncode==0,r.stdout+r.stderr;assert snapshot(db)==before;assert not (p/'kernel-called').exists();assert not (p/'firewall-db.lockdir').exists()
 backup=next((p/'backups').glob('*/firewall_stats.db'));assert snapshot(backup)==before;assert backup.stat().st_mode&0o777==0o600;writer.close()
 c=sqlite3.connect(db);names={r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='index'")};assert 'idx_list_ts' in names and 'idx_list_ts_ip' not in names;c.close()
 r=run();assert r.returncode==0 and snapshot(db)==before,r.stdout+r.stderr
 # A backup failure must leave the original index in place.
 c=sqlite3.connect(db);c.executescript('DROP INDEX idx_list_ts;CREATE INDEX idx_list_ts_ip ON ip_drops(list_type,timestamp,ip);');c.close();bad=p/'not-a-directory';bad.write_text('fixture');r=run({'KT_FW_DB_BACKUPS':str(bad)});assert r.returncode!=0 and snapshot(db)==before
 c=sqlite3.connect(db);assert c.execute("SELECT count(*) FROM sqlite_master WHERE name='idx_list_ts_ip'").fetchone()[0]==1
 c.executescript('DROP INDEX idx_list_ts_ip;CREATE INDEX idx_list_ts_ip ON ip_drops(ip);');c.close();r=run();assert r.returncode!=0 and 'Unexpected index' in r.stderr;assert snapshot(db)==before
 # The ordinary updater recognizes the new index without restoring the oversized one.
 c=sqlite3.connect(db);c.executescript('DROP INDEX idx_list_ts_ip;CREATE INDEX idx_list_ts ON ip_drops(list_type,timestamp);');c.close()
 text=script.read_text();block=text[text.index('    HAS_LIST_TIME='):text.index('\n    fi',text.index('    HAS_LIST_TIME='))+len('\n    fi')]
 code='sqlite3(){ command "'+str(binary)+'" "$@"; };DB_FILE="$1"\n'+block
 r=subprocess.run(['bash','-c',code,'fixture',str(db)],capture_output=True,text=True);assert r.returncode==0,r.stderr
 c=sqlite3.connect(db);assert c.execute("SELECT count(*) FROM sqlite_master WHERE name='idx_list_ts_ip'").fetchone()[0]==0;c.close()
 print('PASS: actual SQLite optimization, verified online backup, exact table preservation incl. full ports/report state, idempotence, backup failure, unexpected-index rejection, no kernel calls and no old-index recreation.')
