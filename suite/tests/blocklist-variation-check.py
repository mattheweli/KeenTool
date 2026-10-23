from pathlib import Path
import tempfile,subprocess,os,json
root=Path(__file__).resolve().parents[1];s=(root/'projects/keenetic-firewall/scripts/update_blocklist.sh').read_text();fn=s[s.index('list_security_event()'):s.index('update_sources()')]
mock=r'''#!/usr/bin/env python3
import os,sys,json
from pathlib import Path
p=Path(os.environ['MOCK_LIST_STATE']);s=json.loads(p.read_text());a=sys.argv[1:];op=a[0];name=a[1] if len(a)>1 else ''
def save():p.write_text(json.dumps(s))
if op=='list':
 if '-n' in a:name=a[-1]
 if name not in s:sys.exit(1)
 print(name)
elif op=='create':s[name]=[];save()
elif op=='destroy':s.pop(name,None);save()
elif op=='save':
 if name not in s:sys.exit(1)
 print('create '+name+' hash:net')
 for x in s[name]:print('add '+name+' '+x)
elif op=='restore':
 for line in sys.stdin:
  _,name,value=line.split();s[name].append(value)
 save()
elif op=='swap':s[name],s[a[2]]=s[a[2]],s[name];save()
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td);bin=p/'bin';bin.mkdir();tool=bin/'ipset';tool.write_text(mock);tool.chmod(0o755)
 # This test isolates prefix validation/swap and never invokes the host network stack.
 env=dict(os.environ,MOCK_LIST_STATE=str(p/'state.json'),PATH=str(bin)+':'+os.environ['PATH'])
 code='set -o pipefail\n'+fn+'\nkt_log(){ :; };kt_atomic_save_set(){ ipset save "$1" > "$2"; };KT_WORKDIR="$1";CACHE_DIR="$1";BANNED_COUNTRIES="cn";SOURCES_V4="https://fixture";SOURCES_V6="";swap_list "$2" inet6 "$1/input" "$1/backup" "$1/diff"\n'
 def run(setname,oldcount,newcount,success):
  (p/'state.json').write_text(json.dumps({setname:[f'2001:db8::{i:x}' for i in range(oldcount)]}))
  (p/'input').write_text(''.join(f'2001:db8::{i:x}\n' for i in range(newcount)))
  r=subprocess.run(['bash','-c',code,'test',str(p),setname],env=env,capture_output=True,text=True)
  assert (r.returncode==0)==success,r.stdout+r.stderr
  result=json.loads((p/'state.json').read_text());assert len(result[setname])==(newcount if success else oldcount)
 run('GeoBlock',200,10,True)
 run('GeoBlock',200,1,True)
 run('FirewallBlock',200,10,False)
 run('FirewallBlock',200,180,True)
 run('GeoBlock',200,0,False)
 print('PASS: significant valid nightly GeoIP shrink is installed; main-list >75% shrink and empty GeoIP are rejected, previous installed sets retained.')
