from pathlib import Path
import tempfile,subprocess,os,re,json,shutil
root=Path(__file__).resolve().parents[1];s=(root/'projects/keenetic-firewall/scripts/firewall_stats.sh').read_text();fn=s[s.index('get_ip_table()'):s.index('# Function: Generate Port Stats')]
with tempfile.TemporaryDirectory() as td:
 p=Path(td);(p/'render').mkdir();(p/'lists').mkdir();history=','.join(f'{i}/'+('tcp' if i%2 else 'udp') for i in range(1,111))
 (p/'render/ip_test.rows').write_text('203.0.113.1|123|US|0|fixture|110|trap|'+history+'\n')
 bin=p/'bin';bin.mkdir();real_awk=shutil.which('awk');wrapper=bin/'awk'
 wrapper.write_text(r'''#!/usr/bin/env python3
import sys,re,os
for arg in sys.argv[1:]:
 if '\n' in arg:
  clean=re.sub(r'"(?:\\.|[^"\\])*"','""',arg)
  allowed={'split','tolower','gsub','close','sprintf','if','for','while'}
  for name in re.findall(r'\b([A-Za-z_][A-Za-z0-9_]*)\(',clean):
   if name not in allowed:
    print('Call to undefined function: '+name,file=sys.stderr);sys.exit(2)
  if os.environ.get('FAIL_PORT_RENDER')=='true':sys.exit(3)
os.execv(REAL_AWK,[REAL_AWK]+sys.argv[1:])
'''.replace('REAL_AWK',repr(real_awk)));wrapper.chmod(0o755)
 env=dict(os.environ,PATH=str(bin)+':'+os.environ['PATH'])
 code=fn+'\nKT_WORKDIR="$1";LIST_DIR="$1/lists";get_ip_table "1=1" 1 test'
 r=subprocess.run(['bash','-c',code,'check',str(p)],capture_output=True,text=True,env=env);assert r.returncode==0,r.stderr
 html=r.stdout;assert '(+107)' in html and 'onclick="showPorts(this)"' in html and 'data-admin-only' not in re.search(r'<button.*?</button>',html).group()
 filename=re.search(r'data-port-list="([^"]+)"',html).group(1);entries=(p/'lists'/filename).read_text().splitlines();assert len(entries)==110 and entries[-1]=='110/udp'
 assert 'Other ports: 4/udp' in html and ', ...' in html
 assert len(list((p/'lists').glob('*.txt')))==1
 for cache in p.glob('port_html_*'):cache.unlink()
 r=subprocess.run(['bash','-c',code,'check',str(p)],capture_output=True,text=True,env=dict(env,FAIL_PORT_RENDER='true'))
 assert r.returncode!=0 and not list(p.glob('port_html_*')) and '<tr>' not in r.stdout
 old_code=code.replace('tip=tip sprintf("%s%s",(j>4?", ":""),a[j])','tip=tip(j>4?", ":"")a[j]')
 r=subprocess.run(['bash','-c',old_code,'check',str(p)],capture_output=True,text=True,env=env)
 assert r.returncode!=0 and 'Call to undefined function: tip' in r.stderr
print('PASS: renderer with strict function-call parsing exports 110 ports; +107 public button/tooltip; rendering failure propagates and removes broken cache.')
