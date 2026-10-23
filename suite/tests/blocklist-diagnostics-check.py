from pathlib import Path
import tempfile,subprocess,os,json,hashlib
root=Path(__file__).resolve().parents[1];source=(root/'projects/keenetic-firewall/scripts/update_blocklist.sh').read_text();functions=source[source.index('valid_list()'):source.index('update_sources inet FirewallBlock')]
mock=r'''#!/usr/bin/env python3
import sys,os,json
from pathlib import Path
p=Path(os.environ['FIXTURE']);a=sys.argv[1:];name=Path(sys.argv[0]).name
if name=='curl':
 calls=p/'curl-calls.json';history=json.loads(calls.read_text()) if calls.exists() else [];history.append(a);calls.write_text(json.dumps(history))
 mode=os.environ.get('FETCH_MODE','valid');codes={'http':(22,'404'),'dns':(6,'000'),'connect':(7,'000'),'timeout':(28,'000'),'tls':(60,'000')}
 if mode=='fallback' and '--ipv4' in a:print('000',end='');sys.exit(7)
 if mode in codes:rc,status=codes[mode];print(status,end='');sys.exit(rc)
 Path(a[a.index('-o')+1]).write_text('invalid source\n' if mode=='empty' else '2001:db8::1\n2001:db8::2\n');print('200',end='');sys.exit(0)
f=p/'kernel.json';s=json.loads(f.read_text());op=a[0];target=a[1] if len(a)>1 else ''
def save():f.write_text(json.dumps(s))
if op=='list':
 target=a[-1]
 if target not in s['sets']:sys.exit(1)
 print(target)
elif op=='destroy':s['sets'].pop(target,None);save()
elif op=='create':
 if target.endswith('_TMP') and os.environ.get('CREATE_FAIL'):sys.exit(1)
 s['sets'][target]=[];save()
elif op=='save':
 if target not in s['sets']:sys.exit(1)
 print('create '+target+' hash:net')
 for ip in s['sets'][target]:print('add '+target+' '+ip)
elif op=='restore':
 error=os.environ.get('LOAD_FAIL')
 if error:print({'capacity':'ipset: Hash is full','memory':'ipset: Cannot allocate memory','invalid':'ipset: Error in line 2: Syntax error'}[error],file=sys.stderr);sys.exit(1)
 for line in sys.stdin:
  _,target,ip=line.split();s['sets'][target].append(ip)
 save()
elif op=='swap':
 s['swaps']+=1;save()
 if os.environ.get('SWAP_FAIL')==str(s['swaps']):sys.exit(1)
 s['sets'][target],s['sets'][a[2]]=s['sets'][a[2]],s['sets'][target];save()
'''
with tempfile.TemporaryDirectory() as td:
 top=Path(td);bin=top/'bin';bin.mkdir()
 for name in ['curl','ipset']:
  p=bin/name;p.write_text(mock);p.chmod(0o755)
 url='https://www.ipdeny.com/ipv6/ipaddresses/aggregated/cn-aggregated.zone'
 def run(name,mode='valid',cached=False,success=False,**extra):
  p=top/name;p.mkdir();(p/'cache').mkdir();old=['2001:db8::'+str(i) for i in range(20)];(p/'kernel.json').write_text(json.dumps({'sets':{'GeoBlock6':old},'swaps':0}))
  if cached:(p/'cache'/(hashlib.sha256(('inet6|'+url).encode()).hexdigest()+'.list')).write_text('invalid cached source\n' if cached=='invalid' else '2001:db8::1\n2001:db8::2\n')
  code='set -o pipefail\n'+functions+r'''
kt_log(){ printf '%s\n' "$*" >&2; }
list_security_event(){ LIST_EVENT_WRITTEN=true;printf '%s\0' "$@" >> "$KT_WORKDIR/events"; }
kt_atomic_save_set(){ [ "${PERSIST_FAIL:-0}" != 1 ] || return 1;ipset save "$1" > "$2"; }
KT_WORKDIR="$1";CACHE_DIR="$1/cache";UPDATE_INTERFACE='';BANNED_COUNTRIES=cn;SOURCES_V4='';SOURCES_V6=''
update_sources inet6 GeoBlock6 "$2" "$1/backup" "$1/diff"
'''
  env=dict(os.environ,PATH=str(bin)+':'+os.environ['PATH'],FIXTURE=str(p),FETCH_MODE=mode,**extra);r=subprocess.run(['bash','-c',code,'fixture',str(p),url],env=env,capture_output=True,text=True);assert (r.returncode==0)==success,(name,r.stdout,r.stderr)
  event=(p/'events').read_bytes().split(b'\0')[:-1];assert len(event)==8,(name,event);event=[x.decode() for x in event];state=json.loads((p/'kernel.json').read_text())
  if not success and extra.get('SWAP_FAIL')!='2':assert state['sets']['GeoBlock6']==old,name
  return event,state
 for mode,code in [('connect','download_connect'),('http','download_http'),('dns','download_dns'),('timeout','download_timeout'),('tls','download_tls'),('empty','source_empty')]:
  event,_=run(mode,mode);assert event[5]==code and 'No valid cache' in event[6],event
 event,_=run('exclusion-detail',success=True,GEOIP_V6_EXCLUDE_COUNTRIES='kp');assert 'Explicit IPv6 country exclusions: kp' in event[6] and event[7]==''
 event,_=run('fallback','fallback',success=True);calls=json.loads((top/'fallback/curl-calls.json').read_text());assert len(calls)==2 and '--ipv4' in calls[0] and '--ipv4' not in calls[1] and '--retry-connrefused' in calls[0]
 event,_=run('invalid-cache','http',cached='invalid');assert event[4]=='rejected'
 event,_=run('cache','http',cached=True,success=True);assert event[4]=='installed' and 'HTTP 404' in event[7] and 'cached source used' in event[7]
 for kind,words in [('capacity','capacity'),('memory','memory allocation'),('invalid','line 2')]:
  event,_=run(kind,LOAD_FAIL=kind);assert event[5]=='staging_load' and words in event[6],event
 event,_=run('create',CREATE_FAIL='1');assert event[5]=='staging_create'
 event,_=run('swap',SWAP_FAIL='1');assert event[5]=='swap_failed'
 event,_=run('persistence',PERSIST_FAIL='1');assert event[5]=='persistence_failed' and 'previous kernel set restored' in event[6]
 event,state=run('rollback',PERSIST_FAIL='1',SWAP_FAIL='2');assert event[5]=='rollback_failed' and 'GeoBlock6_TMP' in state['sets']
 print('PASS: real updater functions with mocked feeds/ipset: HTTP/DNS/timeout/TLS/empty input, cache fallback, capacity/memory/line diagnostics, create/swap/save failures and retained recovery set on rollback failure.')

with tempfile.TemporaryDirectory() as td:
 p=Path(td);selection=source.split('# GeoIP uses the same validated cache engine;',1)[1].split('# Source overlap',1)[0]
 for exclude in ['', 'kp']:
  output=p/('default' if not exclude else 'excluded')
  pre='BANNED_COUNTRIES="cn kp";GEOIP_V6_EXCLUDE_COUNTRIES="'+exclude+'";ENABLE_IPV6=true;FAILED=0;kt_log(){ :; };update_sources(){ printf "%s|%s\\n" "$2" "$3" >> "$1"; };'
  # The first function argument is the address family, so capture to a dedicated path instead.
  pre=pre[:pre.index('update_sources(){')]+'update_sources(){ printf "%s|%s\\n" "$2" "$3" >> "'+str(output)+'"; };'
  result=subprocess.run(['bash','-c',pre+selection],capture_output=True,text=True);assert result.returncode==0,result.stderr
  lines=output.read_text().splitlines();assert 'kp-aggregated.zone' in lines[0]
  assert ('kp-aggregated.zone' in lines[1])==(not exclude)
print('PASS: IPv6-only GeoIP exclusions are explicit; IPv4 country selection remains intact and the default keeps all configured countries.')
