from pathlib import Path
import tempfile, subprocess, sqlite3, os, json
root=Path(__file__).resolve().parents[1]
s=(root/'projects/keenetic-firewall/scripts/firewall_stats.sh').read_text()
fn=s[s.index('get_geo_data()'):s.index('# --- Execute Data Generation ---')]
with tempfile.TemporaryDirectory() as td:
 p=Path(td);(p/'render').mkdir();db=p/'fixture.db';c=sqlite3.connect(db)
 c.executescript('CREATE TABLE ip_drops(ip TEXT,count INTEGER,timestamp INTEGER,list_type TEXT);CREATE TABLE ip_info(ip TEXT PRIMARY KEY,country TEXT,port_history TEXT,target_port TEXT);')
 now=2000000000
 for i in range(150):
  ip=f'203.0.113.{i}';c.execute('INSERT INTO ip_info VALUES(?,?,?,?)',(ip,'US',','.join(f'{p}/tcp' for p in range(1,20)),''));c.execute('INSERT INTO ip_drops VALUES(?,?,?,?)',(ip,100,now-1,'main'))
 for ip,country,count,ts in [('2001:db8::1','CN',1490,now-2),('192.0.2.0/24','XX',196,now-3),('198.51.100.1','',22,now-4),('198.51.100.2','DE',12,now-90000),('198.51.100.3','FR',7,now-40000000)]:
  c.execute('INSERT INTO ip_drops VALUES(?,?,?,?)',(ip,count,ts,'geo'));c.execute('INSERT INTO ip_info VALUES(?,?,?,?)',(ip.split('/')[0],country,'','53/udp'))
 c.commit();c.close()
 shim=p/'sqlite3';shim.write_text('''#!/usr/bin/env python3
import sqlite3,sys
c=sqlite3.connect('file:'+sys.argv[1]+'?mode=ro',uri=True);out=None
for line in sys.stdin:
 if line.startswith('.output '):
  if out:out.close()
  out=open(line.strip().split(' ',1)[1],'w')
 elif not line.startswith('.'):
  try:
   rows=c.execute(line)
   for row in rows:
    if out:out.write('|'.join('' if x is None else str(x) for x in row)+'\\n')
  except Exception as e:print(e,file=sys.stderr);sys.exit(1)
if out:out.close()
''');shim.chmod(0o755)
 env=dict(os.environ,PATH=str(p)+':'+os.environ['PATH'])
 code=fn+'\nKT_WORKDIR="$1";DB_FILE="$2";NOW="$3";get_geo_data\n'
 result=subprocess.run(['bash','-c',code,'test',str(p),str(db),str(now)],env=env,text=True,capture_output=True,check=True)
 data=json.loads(result.stdout)
 assert data['24h']['total']==15000+1490+196+22
 assert data['24h']['countries']['US']['hits']==15000
 assert len(data['24h']['countries']['US']['rows'])==100
 assert data['24h']['countries']['US']['sources']==150
 assert data['24h']['countries']['unknown']['hits']==218
 assert data['24h']['countries']['CN']['rows'][0]['ports']=='53/udp'
 assert data['24h']['countries']['US']['rows'][0]['ports'].endswith('12/tcp, ...')
 assert data['30d']['total']==data['24h']['total']+12
 assert data['1y']['total']==data['30d']['total']
 assert data['all']['total']==data['1y']['total']+7
 # A SQLite error must propagate; it cannot become an empty successful export.
 (p/'bad.db').write_bytes(b'bad')
 bad=subprocess.run(['bash','-c',code,'test',str(p),str(p/'bad.db'),str(now)],env=env,capture_output=True)
 assert bad.returncode!=0
 print('PASS: complete period totals beyond top-10, IPv6/subnets, unknown metadata, bounded detail rows/ports, historical port fallback, time boundaries and SQLite failure propagation.')
