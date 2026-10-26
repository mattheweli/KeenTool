"""Exercise actual entry points and menu update handoffs after cwd removal."""
from pathlib import Path
import os, subprocess, tempfile
root=Path(__file__).resolve().parents[1]
manager=(root/'projects/KeenTool/keentool').read_text()
with tempfile.TemporaryDirectory() as td:
 b=Path(td);stage=b/'stage';stage.mkdir()
 env=dict(os.environ,KT_PATH=os.environ['PATH'],KT_UPDATE_BASH='/bin/bash',KT_UPDATE_TMP=str(stage),KT_COMMON=str(b/'missing-common'),KT_UPDATE_INSTALLED=str(b/'missing-installed'),KT_UPDATE_HELPER=str(b/'missing-helper'),KT_UPDATE_COMMAND=str(b/'missing-updater'))
 # Source into an already-running Bash so its cwd can disappear before entry.
 # A newly exec'd interpreter may warn before script code can execute at all.
 for i,script in enumerate([root/'projects/KeenTool/keentool',root/'support/keentool_update',root/'bootstrap.sh']):
  deleted=b/('entry-'+str(i));deleted.mkdir()
  code='cd "$1"; rmdir "$1"; . "$2" --help'
  r=subprocess.run(['bash','-c',code,'fixture',str(deleted),str(script)],env=env,text=True,capture_output=True)
  assert r.returncode==0 and 'getcwd' not in r.stderr and 'shell-init' not in r.stderr and 'chdir:' not in r.stderr,r.stdout+r.stderr
  assert r.stdout and not list(stage.iterdir()),(script,r.stdout,r.stderr)
 fn=manager[manager.index('kt_managed_update() {'):manager.index('kt_entware_update_count() {')]
 updater=b/'updater';updater.write_text('''#!/bin/bash
pwd -P > "$CWD_TRACE"
[ "$MODE" != fail ] || exit 9
[ "$MODE" != install ] || printf '2.0.9\\n' > "$KT_UPDATE_RECEIPT"
''');updater.chmod(0o755)
 new_menu=b/'menu';new_menu.write_text('#!/bin/bash\necho CURRENT_MENU;pwd -P\n');new_menu.chmod(0o755)
 for mode in ['current','declined','fail','install','preserve']:
  cwd=b/('menu-'+mode);cwd.mkdir();trace=b/'cwd-trace'
  script=fn+'\ncd "$FIXTURE_CWD"\n[ "$MODE" = preserve ] || rmdir "$FIXTURE_CWD"\nkt_managed_update; rc=$?;printf "RETURN=%s\\n" "$rc"\n'
  e=dict(env,KT_UPDATE_COMMAND=str(updater),KT_MANAGER_PATH=str(new_menu),KT_RUN_DIR=td,CWD_TRACE=str(trace),MODE=mode,FIXTURE_CWD=str(cwd))
  r=subprocess.run(['bash','-c',script],env=e,text=True,capture_output=True)
  assert r.returncode==0 and not r.stderr,r.stdout+r.stderr
  assert trace.read_text().strip()==(str(cwd) if mode=='preserve' else '/'),trace.read_text()
  if mode=='install':assert 'CURRENT_MENU\n/\n' in r.stdout and 'RETURN=' not in r.stdout,r.stdout
  else:assert ('RETURN=9' if mode=='fail' else 'RETURN=0') in r.stdout and 'CURRENT_MENU' not in r.stdout,r.stdout
  assert not list(b.glob('keentool-menu-update.*'))
 main=manager[manager.index('# --- MAIN MENU ---'):]
 assert 'Update Keentool (Self)' not in main and 's) action_self_update' not in main
 assert 'u) perform_global_scan; pause ;;' in main and 'Check / install updates (KeenTool and tools)' in main
print('PASS: real manager/updater/bootstrap entry recovery, menu update/restart from deleted cwd, valid cwd preserved, no child warning cascade, no restart on decline/current/error, unified u menu; network/installer mocked.')
