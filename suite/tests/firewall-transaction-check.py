from pathlib import Path
import os,subprocess,tempfile,json,shutil
root=Path(__file__).resolve().parents[1]
engine=r'''#!/usr/bin/env python3
import os,sys,json,copy,shlex
from pathlib import Path
name=Path(sys.argv[0]).name;args=sys.argv[1:];base=Path(os.environ['MOCK_FW']);path=base/'kernel.json';state=json.loads(path.read_text());fam='6' if name.startswith('ip6') else '4'
def write():path.write_text(json.dumps(state))
def ruleop(t,a):
 op=a[0];c=a[1]
 if op=='-N':
  if c in t:raise ValueError('exists')
  t[c]=[]
 elif op=='-F':t[c]=[]
 elif op=='-X':
  if t.get(c) or any(c in r for rows in t.values() for r in rows):raise ValueError('referenced')
  del t[c]
 elif op=='-A':t[c].append(a[2:])
 elif op=='-I':t[c].insert(int(a[2])-1,a[3:])
 elif op=='-D':t[c].remove(a[2:])
 else:raise ValueError(op)
try:
 if name=='ipset':
  if args[0]=='list':
   c=args[-1]
   if c not in state['sets']:sys.exit(1)
   if '-n' in args:print(c)
   else:print('Name: '+c+'\nNumber of entries: '+str(len(state['sets'][c])))
  elif args[0]=='create':state['sets'].setdefault(args[1],[]);write()
  elif args[0]=='add':
   if args[2] not in state['sets'][args[1]]:state['sets'][args[1]].append(args[2]);write()
  elif args[0]=='restore':
   for line in sys.stdin:
    a=line.split()
    if a[0]=='create':state['sets'].setdefault(a[1],[])
    elif a[0]=='add':
     if (base/'fail-set').exists():sys.exit(1)
     if a[2] not in state['sets'][a[1]]:state['sets'][a[1]].append(a[2])
   write()
  elif args[0]=='save':
   c=args[1];print('create '+c+' hash:net counters')
   for v in state['sets'][c]:print('add '+c+' '+v)
 elif name.endswith('-save'):
  late=base/'fail-late-save'
  if late.exists():
   count=int(late.read_text() or '0')+1
   if count==7:late.unlink();sys.exit(1)
   late.write_text(str(count))
  print('*filter')
  for c in state[fam]:print(':'+c+' '+('ACCEPT' if c in ['INPUT','OUTPUT','FORWARD'] else '-')+' [0:0]')
  for c,rs in state[fam].items():
   for r in rs:print('-A '+c+' '+' '.join(r))
  print('COMMIT')
 elif name.endswith('-restore'):
  if '--help' in args:print('--test --noflush');sys.exit(0)
  test='--test' in args
  key=('preflight' if test else 'apply')+fam
  if (base/key).exists():
   (base/key).unlink();sys.exit(1)
  t=copy.deepcopy(state[fam])
  for line in sys.stdin:
   line=line.strip()
   if not line or line=='COMMIT' or line.startswith('*'):continue
   if line.startswith(':'):t[line.split()[0][1:]]=[];continue
   ruleop(t,shlex.split(line))
  if not test:state[fam]=t;write()
 else:
  if args and args[0]=='-w':args=args[1:]
  if args[0]=='-C':sys.exit(0 if args[2:] in state[fam].get(args[1],[]) else 1)
  ruleop(state[fam],args);write()
except (ValueError,KeyError) as e:
 print(str(e),file=sys.stderr);sys.exit(1)
'''
with tempfile.TemporaryDirectory() as td:
 b=Path(td);bin=b/'bin';bin.mkdir();(bin/'engine').write_text(engine);(bin/'engine').chmod(0o755)
 for n in ['iptables','ip6tables','iptables-save','ip6tables-save','iptables-restore','ip6tables-restore','ipset']:(bin/n).symlink_to(bin/'engine')
 real_awk=shutil.which('awk');awk=bin/'awk';awk.write_text('#!/bin/bash\nfor arg in "$@";do if [ "$arg" = /dev/stdin ];then echo "awk: /dev/stdin: No such file or directory" >&2;exit 2;fi;done\nexec "'+real_awk+'" "$@"\n');awk.chmod(0o755)
 for n in ['lsmod','logger']:(bin/n).write_text('#!/bin/sh\nexit 0\n');(bin/n).chmod(0o755)
 conf=b/'firewall.conf';conf.write_text('ENABLE_FIREWALL="true"\nENABLE_IPV6="true"\nENABLE_MANUAL="true"\nENABLE_AUTOBAN="false"\nENABLE_BRUTEFORCE="true"\nENABLE_CONNLIMIT="true"\nENABLE_FWD_PROTECTION="false"\nCONNLIMIT_MAX=15\nCONNLIMIT_CUSTOM=150\nBAN_TIMEOUT=86400\nBF_SECONDS=60\nBF_HITCOUNT=5\nTCP_SERVICES="51515 21"\nUDP_SERVICES=""\nTCP_PASSIVE_RANGE=""\n')
 def fresh():
  s={f:{'INPUT':[['-j','ROUTER']], 'FORWARD':[], 'OUTPUT':[], 'ROUTER':[['-j','ACCEPT']]} for f in ['4','6']};s['sets']={};(b/'kernel.json').write_text(json.dumps(s));return s
 env=dict(os.environ,MOCK_FW=str(b),KT_PATH=str(bin)+':'+os.environ['PATH'],PATH=str(bin)+':'+os.environ['PATH'],KT_COMMON=str(root/'support/common.sh'),KT_FW_CONF=str(conf),KT_FW_APPLY=str(root/'support/firewall_apply.sh'),KT_FW_RUNTIME=str(b/'runtime'),KT_RUN_DIR=td,table='filter')
 # Hook PATH must honor the test-specific path.
 def run():return subprocess.run(['bash',str(root/'projects/keenetic-firewall/scripts/100-firewall.sh')],env=env,text=True,capture_output=True)
 def state():return json.loads((b/'kernel.json').read_text())
 original=fresh();r=run();assert r.returncode==0,r.stderr
 s=state();assert s['4']['ROUTER']==original['4']['ROUTER'];assert s['4']['INPUT'].count(['-j','BLOCKLIST_IN'])==1
 for f in ['4','6']:assert not any('--add-set' in r for rs in s[f].values() for r in rs),'AutoBan OFF must never populate sets'
 health=subprocess.run(['bash',str(root/'support/firewall_health')],env=env,text=True,capture_output=True);assert json.loads(health.stdout)['applied'] is True,health.stderr
 s['6']['BLACKLIST6'].pop();(b/'kernel.json').write_text(json.dumps(s));health=subprocess.run(['bash',str(root/'support/firewall_health')],env=env,text=True,capture_output=True);assert json.loads(health.stdout)['applied'] is False
 r=run();assert r.returncode==0,r.stderr;good=state()
 (b/'fail-late-save').write_text('0');r=run();assert r.returncode!=0;assert state()['4']==good['4'] and state()['6']==good['6'],r.stderr
 health=subprocess.run(['bash',str(root/'support/firewall_health')],env=env,text=True,capture_output=True);assert json.loads(health.stdout)['applied'] is True,'old metadata must be recovered after a late failure'
 (b/'preflight6').touch();r=run();assert r.returncode!=0;assert state()['4']==good['4'] and state()['6']==good['6'],'preflight must leave both families unchanged'
 (b/'apply6').touch();r=run();assert r.returncode!=0,r.stderr;assert state()['4']==good['4'] and state()['6']==good['6'],r.stderr
 # Empty original owned state must also recover without leaving new chains.
 fresh();(b/'apply6').touch();r=run();assert r.returncode!=0;assert state()['4']==original['4'] and state()['6']==original['6'],r.stderr
 run();conf.write_text(conf.read_text().replace('ENABLE_IPV6="true"','ENABLE_IPV6="false"'));r=run();assert r.returncode==0,r.stderr;assert 'BLACKLIST6' not in state()['6']
 # Disable clears every owned chain while retaining foreign rules and ipsets.
 conf.write_text(conf.read_text().replace('ENABLE_FIREWALL="true"','ENABLE_FIREWALL="false"'));before_sets=state()['sets'];r=run();assert r.returncode==0,r.stderr;assert state()['4']==original['4'] and state()['6']==original['6'];assert state()['sets']==before_sets
 print('PASS: full hook staging, foreign rules retained, AutoBan OFF, complete health detects missing IPv6 rule, preflight failure, second-family failure rollback with/without prior rules, IPv6 teardown, disable preserves sets.')
# Separate state helper: partially populated sets are completed, never marked on error.
with tempfile.TemporaryDirectory() as td:
 b=Path(td);bin=b/'bin';bin.mkdir();(bin/'ipset').write_text(engine);(bin/'ipset').chmod(0o755)
 state={'4':{},'6':{},'sets':{'FirewallBlock':['192.0.2.1']}};(b/'kernel.json').write_text(json.dumps(state));save=b/'saved';save.mkdir();boot=b/'boot';boot.mkdir()
 (save/'firewall_blocklist.save').write_text('create FirewallBlock hash:net counters\nadd FirewallBlock 192.0.2.1\nadd FirewallBlock 192.0.2.2\n')
 env=dict(os.environ,PATH=str(bin)+':'+os.environ['PATH'],MOCK_FW=td,KT_FW_SAVE_ROOT=str(save),KT_FW_BOOT_DIR=str(boot),KT_FW_STATE_DIR=str(b/'snapshots'))
 code='. "'+str(root/'support/firewall_state.sh')+'";fw_restore_state'
 (b/'fail-set').touch();r=subprocess.run(['bash','-c',code],env=env,capture_output=True,text=True);assert r.returncode!=0 and not (boot/'fw-restored-FirewallBlock').exists()
 (b/'fail-set').unlink();r=subprocess.run(['bash','-c',code],env=env,capture_output=True,text=True);assert r.returncode==0,r.stderr
 assert json.loads((b/'kernel.json').read_text())['sets']['FirewallBlock']==['192.0.2.1','192.0.2.2']
 assert (boot/'fw-restored-FirewallBlock').exists()
 state=json.loads((b/'kernel.json').read_text());state['sets']['AutoBan']=[];(b/'kernel.json').write_text(json.dumps(state))
 snapshots=b/'snapshots';snapshots.mkdir(exist_ok=True);old=snapshots/'AutoBan.save';old.write_text('previous good snapshot\n');(boot/'fw-restored-AutoBan').write_text('')
 checkpoint='. "'+str(root/'support/firewall_state.sh')+'";fw_checkpoint_state'
 r=subprocess.run(['bash','-c',checkpoint],env=env,capture_output=True,text=True);assert r.returncode==0,r.stderr;assert old.read_text()=='previous good snapshot\n'
 (boot/'fw-restored-AutoBan').write_text('complete-v2\n');r=subprocess.run(['bash','-c',checkpoint],env=env,capture_output=True,text=True);assert r.returncode==0 and old.read_text().startswith('create AutoBan')
print('PASS: partial list completion, failed restore keeps snapshot and completion marker absent, retry succeeds.')
