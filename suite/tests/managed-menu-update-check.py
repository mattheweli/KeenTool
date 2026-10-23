"""Exercise the real managed menu branches and receipt-based exec restart."""
from pathlib import Path
import tempfile,subprocess,os,json,shutil
root=Path(__file__).resolve().parents[1];source=(root/'projects/KeenTool/keentool').read_text();fn=source[source.index('kt_managed_update() {'):source.index('kt_component_version() {')]
with tempfile.TemporaryDirectory() as td:
 p=Path(td);calls=p/'calls';updater=p/'updater';manager=p/'manager'
 updater.write_text('#!/bin/bash\nprintf "%s\\n" "$*" >> "$KT_TEST_CALLS"\n[ "$KT_TEST_MODE" != fail ] || exit 9\n[ "$KT_TEST_MODE" != install ] || printf "2.0.4\\n" > "$KT_UPDATE_RECEIPT"\nexit 0\n');manager.write_text('#!/bin/bash\necho "CURRENT MENU 2.0.4"\n');env=dict(os.environ,KT_RUN_DIR=td,KT_UPDATE_BASH='/bin/bash',KT_UPDATE_COMMAND=str(updater),KT_MANAGER_PATH=str(manager),KT_TEST_CALLS=str(calls))
 for mode in ['current','declined','fail','install']:
  calls.unlink(missing_ok=True);r=subprocess.run(['bash','-c',fn+'\nkt_managed_update keenetic-firewall;rc=$?;echo "OLD MENU AFTER: $rc"'],env=dict(env,KT_TEST_MODE=mode),text=True,capture_output=True)
  assert calls.read_text().splitlines()==['--component keenetic-firewall'];assert not list(p.glob('keentool-menu-update.*'))
  if mode=='install':assert 'CURRENT MENU 2.0.4' in r.stdout and 'OLD MENU AFTER' not in r.stdout
  else:assert 'CURRENT MENU' not in r.stdout and ('OLD MENU AFTER: 9' if mode=='fail' else 'OLD MENU AFTER: 0') in r.stdout
 # Explicit repair uses its own option; self update selects KeenTool, global scan leaves scope open.
 calls.unlink();r=subprocess.run(['bash','-c',fn+'\nkt_managed_update --repair'],env=dict(env,KT_TEST_MODE='current'),text=True,capture_output=True)
 assert r.returncode==0 and calls.read_text().splitlines()==['--repair']
 assert 'true ]; then kt_managed_update KeenTool; return $?; fi' in source[source.index('action_self_update() {'):source.index('perform_global_scan() {')]
 assert 'true ]; then kt_managed_update; return $?; fi' in source[source.index('perform_global_scan() {'):source.index('smart_process() {')]
 assert 'r) kt_managed_update --repair; pause ;;' in source and 'Check all updates (KeenTool and tools)' in source
 # Production firewall menu must not enter the legacy file/dependency/web/cron path.
 firewall=source[source.index('action_firewall() {'):source.index('\n    for PKG in $DEPS_CORE')]
 # End the excerpt at the next function, not its body.
 firewall=firewall[:firewall.index('\n}',firewall.index('action_firewall()'))+2]
 script='''header(){ :; };get_version(){ echo 4.0.0; };pause(){ :; };kt_component_version(){ echo 4.0.1; }
kt_managed_update(){ printf '%s\\n' "$*" >> "$KT_TEST_CALLS"; }
check_and_install_deps(){ echo FORBIDDEN >> "$KT_TEST_CALLS"; };verify_new_firewall_reqs(){ echo FORBIDDEN >> "$KT_TEST_CALLS"; }
smart_process(){ echo FORBIDDEN >> "$KT_TEST_CALLS"; };sanitize_and_reload_cron(){ echo FORBIDDEN >> "$KT_TEST_CALLS"; }
KT_MANAGED_PACKAGE=true;FW_CORE_LOCAL="$KT_MANAGER_PATH";BIN_DIR=/fixture
'''+firewall+'\naction_firewall\n'
 calls.unlink();r=subprocess.run(['bash','-c',script],input='1\n0\n',env=env,text=True,capture_output=True,timeout=10);assert r.returncode==0,r.stderr;assert calls.read_text().splitlines()==['keenetic-firewall'];assert 'Firewall suite: 4.0.1' in r.stdout and 'Monitor script: 4.0.0' in r.stdout
 # Main summary reports the firewall suite, not the monitor entry-point version.
 line=next(line for line in source.splitlines() if 'L3=' in line and 'kt_component_version keenetic-firewall' in line)
 script='KT_MANAGED_PACKAGE=true;FW_CORE_LOCAL="$KT_MANAGER_PATH";GREEN=;RESET=;DIM=;get_version(){ echo 3.0.0; };kt_component_version(){ echo 4.0.1; };'+line+';printf "%s" "$L3"'
 r=subprocess.run(['bash','-c',script],env=env,text=True,capture_output=True);assert r.returncode==0 and r.stdout=='v4.0.1',r.stdout+r.stderr
 dashboard_menu=source[source.index('Main Dashboard Manager'):]
 assert 'kt_managed_update Dashboard;pause;continue;fi' in dashboard_menu
 # Audit independent component/script versions and actual installed content.
 pkg=p/'package';(pkg/'projects/keenetic-firewall/scripts').mkdir(parents=True);(pkg/'RELEASE.json').write_text(json.dumps({'version':'2.0.4','components':{'keenetic-firewall':'4.0.1'}}));installed=p/'installed.json';installed.write_text((pkg/'RELEASE.json').read_text());manifest=[]
 for name,version in [('firewall_stats.sh','4.0.1'),('firewall_monitor','4.0.0'),('firewall_manager.sh','3.0.0'),('100-firewall.sh','3.0.0')]:
  rel='projects/keenetic-firewall/scripts/'+name;f=pkg/rel;f.write_text('# SCRIPT v'+version+'\n');dest=p/'opt/bin'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy(f,dest);dest.chmod(0o755);manifest.append(rel+'\t/opt/bin/'+name+'\t755')
 (pkg/'INSTALL.tsv').write_text('\n'.join(manifest)+'\n');php='/tmp/keentool-security-runtime/root/usr/bin/php8.3'
 def audit():return subprocess.run([php,'-n',str(root/'support/release_update.php'),'component',str(pkg),str(installed),'keenetic-firewall',td],text=True,capture_output=True)
 r=audit();assert r.returncode==0 and 'All installed package files match' in r.stdout and 'keenetic-firewall: installed 4.0.1; available 4.0.1' in r.stdout and 'firewall_monitor: release 4.0.0' in r.stdout,r.stderr
 (p/'opt/bin/firewall_stats.sh').write_text('# SCRIPT v4.0.0\n');r=audit();assert r.returncode==0 and '1 package files are missing, different' in r.stdout
 print('PASS: single coordinated firewall update, independent suite/component/script versions, real file drift audit, no legacy side effects, receipt-based exec reload, no reload on decline/current/failure and receipt cleanup.')
