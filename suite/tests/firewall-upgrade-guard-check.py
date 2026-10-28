"""Exercise the independent upgrade guardian with real file rollback and a mock kernel."""
from pathlib import Path
import ast,os,subprocess,tempfile,json,shutil,pty,select,re,time,signal
suite=Path(__file__).resolve().parents[1];php='/tmp/keentool-security-runtime/root/usr/bin/php8.3'
module=ast.parse((suite/'tests/firewall-transaction-check.py').read_text());engine=next(ast.literal_eval(n.value) for n in module.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='engine' for t in n.targets))
with tempfile.TemporaryDirectory() as td:
 base=Path(td)
 def fixture(name,seconds=20):
  root=base/name;bin=root/'opt/bin';bin.mkdir(parents=True);etc=root/'opt/etc';init=etc/'init.d';init.mkdir(parents=True);run=root/'run';run.mkdir();(etc/'ndm/netfilter.d').mkdir(parents=True);(etc/'keentool').mkdir()
  sleep=bin/'sleep';sleep.write_text('#!/bin/bash\n[[ "$#" = 1 && "$1" =~ ^[0-9]+$ ]] || { echo "sleep: invalid number $*" >&2;exit 1; }\nexec '+shutil.which('sleep')+' "$1"\n');sleep.chmod(0o755)
  (bin/'bash').symlink_to(shutil.which('bash'));(bin/'engine').write_text(engine);(bin/'engine').chmod(0o755)
  for name in ['iptables','ip6tables','iptables-save','ip6tables-save','iptables-restore','ip6tables-restore','ipset']:(bin/name).symlink_to(bin/'engine')
  for name in ['lsmod','logger']:(bin/name).write_text('#!/bin/bash\nexit 0\n');(bin/name).chmod(0o755)
  (bin/'php-cli').write_text('#!/bin/bash\nexec '+php+' -n "$@"\n');(bin/'php-cli').chmod(0o755)
  (bin/'keentool').write_text('# previous manager\n');hook=etc/'ndm/netfilter.d/100-firewall.sh';hook.write_text('#!/bin/bash\necho legacy-called >> "$KT_TEST_LEGACY"\n');hook.chmod(0o750)
  conf=etc/'firewall.conf';conf.write_text('ENABLE_FIREWALL="true"\nENABLE_IPV6="true"\nENABLE_MANUAL="true"\nENABLE_AUTOBAN="false"\nENABLE_BRUTEFORCE="true"\nENABLE_CONNLIMIT="true"\nENABLE_FWD_PROTECTION="false"\nCONNLIMIT_MAX=15\nCONNLIMIT_CUSTOM=150\nBAN_TIMEOUT=604800\nBF_SECONDS=60\nBF_HITCOUNT=5\nTCP_SERVICES="22"\nUDP_SERVICES=""\nTCP_PASSIVE_RANGE=""\n')
  for name in ['S80lighttpd','S11ulogd','S32vnstat2']:(init/name).write_text('#!/bin/bash\nexit 0\n');(init/name).chmod(0o755)
  runner=root/'service-runner';runner.write_text('#!/bin/bash\n[ "$2" != status ]\n');runner.chmod(0o755)
  kernel={f:{'INPUT':[['-j','ROUTER']], 'FORWARD':[], 'OUTPUT':[], 'ROUTER':[['-j','ACCEPT']]} for f in ['4','6']};kernel['sets']={'AutoBan':['198.51.100.99']};(root/'kernel.json').write_text(json.dumps(kernel))
  runtime=etc/'keentool/firewall-runtime';runtime.mkdir();(runtime/'ready').write_text('legacy-ready\n');(runtime/'canonical4').write_text('legacy-canonical\n')
  env=dict(os.environ,KT_INSTALL_ROOT=str(root),KT_PATH=str(bin)+':'+os.environ['PATH'],PATH=str(bin)+':'+os.environ['PATH'],MOCK_FW=str(root),KT_RUN_DIR=str(run),KT_FW_RUNTIME=str(runtime),KT_FW_CONF=str(conf),KT_COMMON=str(root/'opt/lib/keentool/common.sh'),KT_FW_APPLY=str(root/'opt/lib/keentool/firewall_apply.sh'),KT_FW_TEST_SECONDS=str(seconds),KT_TEST_LEGACY=str(root/'legacy.log'),KT_INSTALL_TEST_SERVICE=str(runner),KT_FW_SAVE_ROOT=str(etc),KT_FW_STATE_DIR=str(etc/'keentool/firewall-state'),KT_FW_BOOT_DIR=str(run))
  command=[php,'-n',str(suite/'support/release_install.php')]
  r=subprocess.run(command+['prepare',str(suite),'upgrade','','0','0','keep'],env=env,text=True,capture_output=True);assert r.returncode==0,r.stdout+r.stderr;backup=Path(r.stdout)
  shutil.copy(suite/'support/firewall_upgrade',backup/'firewall_upgrade');token='a'*48
  r=subprocess.run(['bash',str(backup/'firewall_upgrade'),'prepare',str(backup),token],env={**env,'KT_FW_APPLY':str(suite/'support/firewall_apply.sh')},text=True,capture_output=True);assert r.returncode==0,r.stdout+r.stderr
  # An unfinished migration blocks another installation before mutation.
  r=subprocess.run(command+['plan',str(suite),'upgrade','','0','0'],env=env,text=True,capture_output=True);assert r.returncode!=0 and 'guarded firewall migration is pending' in r.stderr,r.stdout+r.stderr
  r=subprocess.run(command+['commit',str(backup)],env=env,text=True,capture_output=True);assert r.returncode==0,r.stdout+r.stderr
  return root,env,backup,token,kernel
 def drive(root,env,backup,token,answer):
  pid,fd=pty.fork()
  if pid==0:os.environ.update(env);os.execvp('bash',['bash',str(backup/'firewall_upgrade'),'run',str(backup),token])
  output=b'';sent=False;deadline=time.monotonic()+45;reaped=None
  try:
   while time.monotonic()<deadline:
    ready,_,_=select.select([fd],[],[],.1)
    if not ready:
     done,status=os.waitpid(pid,os.WNOHANG)
     if done:reaped=status;break
     continue
    try:chunk=os.read(fd,8192)
    except OSError:break
    if not chunk:break
    output+=chunk;match=re.search(rb'Type ([a-f0-9]{8}) within',output)
    if match and not sent:
     if answer=='kill':
      state=json.loads((root/'kernel.json').read_text());state['4']['ROUTER'].append(['-p','udp','-j','ACCEPT']);(root/'kernel.json').write_text(json.dumps(state))
      os.kill(pid,signal.SIGKILL)
     else:
      if answer=='fail-restore':(root/'apply6').touch()
      os.write(fd,(match[1] if answer=='confirm' else b'wrong')+b'\n')
     sent=True
   else:os.kill(pid,signal.SIGKILL);raise AssertionError('Guardian prompt timeout: '+output.decode())
  finally:os.close(fd)
  if reaped is None:_,status=os.waitpid(pid,0)
  else:status=reaped
  return os.waitstatus_to_exitcode(status),output.decode(),sent
 def restored(root,backup,kernel,foreign=False):
  state=json.loads((root/'kernel.json').read_text())
  for family in ['4','6']:
   expected=json.loads(json.dumps(kernel[family]))
   if foreign and family=='4':expected['ROUTER'].append(['-p','udp','-j','ACCEPT'])
   assert state[family]==expected,(state[family],expected)
  assert state['sets']['AutoBan']==kernel['sets']['AutoBan']
  assert (root/'opt/bin/keentool').read_text()=='# previous manager\n'
  hook=root/'opt/etc/ndm/netfilter.d/100-firewall.sh';assert hook.stat().st_mode&0o777==0o750 and 'legacy-called' in hook.read_text()
  assert (root/'opt/etc/keentool/firewall-runtime/ready').read_text()=='legacy-ready\n'
  assert not (root/'opt/etc/keentool/firewall-upgrade.pending').exists()
  assert (backup/'firewall-upgrade/phase').read_text().strip()=='rolled-back'
 root,env,backup,token,kernel=fixture('confirm');rc,out,sent=drive(root,env,backup,token,'confirm');assert rc==0 and sent,out
 assert (backup/'firewall-upgrade/phase').read_text().strip()=='confirmed' and not (root/'opt/etc/keentool/firewall-upgrade.pending').exists()
 state=json.loads((root/'kernel.json').read_text());assert state['4']['ROUTER']==kernel['4']['ROUTER'] and 'BLOCKLIST_IN' in state['4']
 root,env,backup,token,kernel=fixture('reject');rc,out,sent=drive(root,env,backup,token,'reject');assert rc!=0 and sent,out;restored(root,backup,kernel)
 root,env,backup,token,kernel=fixture('apply-failure');(root/'apply6').touch();rc,out,sent=drive(root,env,backup,token,'confirm');assert rc!=0 and not sent,out;restored(root,backup,kernel)
 root,env,backup,token,kernel=fixture('restore-failure');rc,out,sent=drive(root,env,backup,token,'fail-restore');assert rc!=0 and sent,out
 assert (root/'opt/etc/keentool/firewall-upgrade.pending').exists() and (backup/'transaction.json').exists() and (backup/'files').is_dir(),out
 r=subprocess.run(['bash',str(backup/'firewall_upgrade'),'recover',str(backup),token],env=env,text=True,capture_output=True);assert r.returncode==0,r.stdout+r.stderr;restored(root,backup,kernel)
 root,env,backup,token,kernel=fixture('disconnect',12);rc,out,sent=drive(root,env,backup,token,'kill');assert rc!=0 and sent,out
 deadline=time.monotonic()+40
 while time.monotonic()<deadline and (backup/'firewall-upgrade/phase').read_text().strip()!='rolled-back':time.sleep(.1)
 restored(root,backup,kernel,True)
 # Reproduce 2.0.14: an untouched vnStat stop fails before source recovery.
 root,env,backup,token,kernel=fixture('legacy-service-recovery')
 shutil.copy(suite/'tests/fixtures/rollback-1.0.0.sh',backup/'rollback.sh')
 shutil.copy(suite/'tests/fixtures/firewall-upgrade-1.0.0',backup/'firewall_upgrade')
 for name in ['lighttpd','ulogd','vnstat']:(backup/(name+'-was-running')).touch()
 runner=Path(env['KT_INSTALL_TEST_SERVICE']);env['KT_TEST_SERVICE_EVENTS']=str(root/'service-events')
 runner.write_text('#!/bin/bash\nprintf "%s %s\\n" "$1" "$2" >> "$KT_TEST_SERVICE_EVENTS"\nif [[ "$1 $2" = *"S32vnstat2 stop"* ]];then echo "Point right interface(s) to monitor" >&2;exit 1;fi\n[ "$2" != status ]\n')
 pidof=root/'opt/bin/pidof';pidof.write_text('#!/bin/bash\n[ "$1" = vnstatd ]\n');pidof.chmod(0o755)
 r=subprocess.run(['bash',str(backup/'firewall_upgrade'),'recover',str(backup),token],env=env,text=True,capture_output=True)
 assert r.returncode!=0 and 'Point right interface' in r.stderr and (root/'opt/etc/keentool/firewall-upgrade.pending').exists(),r.stdout+r.stderr
 assert (root/'opt/bin/keentool').read_text()!='# previous manager\n'
 (root/'service-events').unlink()
 r=subprocess.run(['bash',str(suite/'support/recover_firewall_upgrade.sh'),str(backup)],env=env,text=True,capture_output=True)
 assert r.returncode==0,r.stdout+r.stderr;restored(root,backup,kernel)
 events=(root/'service-events').read_text();assert 'S32vnstat2 stop' not in events and 'S32vnstat2 start' not in events and 'S80lighttpd start' in events and 'S11ulogd start' in events,events
 assert (backup/'rollback.sh.before-service-fix').read_bytes()==(suite/'tests/fixtures/rollback-1.0.0.sh').read_bytes()
 r=subprocess.run(['python3',str(suite/'tools/build-recovery.py'),'--check'],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
 # Reboot with a prepared/unconfirmed source: restore source before running the old hook.
 root,env,backup,token,kernel=fixture('reboot');marker=root/'opt/etc/keentool/firewall-upgrade.pending';marker.write_text(str(backup)+'\n'+token+'\nprevious-boot\n');(backup/'firewall-upgrade/boot').write_text('previous-boot\n')
 r=subprocess.run(['bash',str(root/'opt/etc/ndm/netfilter.d/100-firewall.sh')],env={**env,'table':'filter'},text=True,capture_output=True);assert r.returncode==0,r.stdout+r.stderr
 restored(root,backup,kernel);assert (root/'legacy.log').read_text().strip()=='legacy-called'
print('PASS: real source/metadata rollback, real hook with mock kernel, interactive challenge confirmation/rejection, independently timed restore after parent SIGKILL/SSH loss, foreign rules and existing bans retained, pending-install exclusion and reboot recovery.')
