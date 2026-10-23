from pathlib import Path
import tempfile,subprocess,os
root=Path(__file__).resolve().parents[1];source=(root/'projects/SMB_Backup_tool/Script/smb_backup_tool.sh').read_text();functions=source[source.index('smb_safe_path()'):source.index('run_retention_check()')]
with tempfile.TemporaryDirectory() as td:
 b=Path(td);(b/'source').mkdir();(b/'source/config').write_text('fixture data\n')
 code='. "'+str(root/'support/common.sh')+'"\n'+functions.replace('/opt/tmp',str(b/'tmp'))+r'''
logger_msg(){ printf '%s\n' "$*" >> "$TEST_ROOT/log"; }
dump_system_files(){ mkdir -p "$TEMP_DIR/sys_dump";printf 'fixture config\n' > "$TEMP_DIR/sys_dump/running-config.txt"; }
run_retention_check(){ echo retention >> "$TEST_ROOT/events"; }
smb_run(){
 printf '%s\n' "$1" >> "$TEST_ROOT/events"
 if [[ "$1" =~ get[[:space:]]\"([^\"]+)\"[[:space:]]\"([^\"]+)\" ]];then
  archive=${BASH_REMATCH[1]};destination=${BASH_REMATCH[2]}
  if [ "$CORRUPT" = true ];then echo corrupt > "$destination";else cp "$TEMP_DIR/$archive" "$destination";fi
 fi
}
CONFIG_STATUS=OK;SOURCE_DIR="$TEST_ROOT/source";SMB_SUBDIR=backups;SMB_SHARE=backup;SMB_HOST=fixture;SMB_USER=fixture;SMB_PASS=fixture;RETENTION_DAYS=30;AUTO_PURGE=true;LOG_FILE="$TEST_ROOT/log";TEMP_DIR=''
perform_backup
'''
 env=dict(os.environ,TEST_ROOT=td,KT_RUN_DIR=td,CORRUPT='false');r=subprocess.run(['bash','-c',code],env=env,capture_output=True,text=True);assert r.returncode==0,r.stderr
 events=(b/'events').read_text();assert 'rename' in events and 'retention' in events
 (b/'events').unlink();env['CORRUPT']='true';r=subprocess.run(['bash','-c',code],env=env,capture_output=True,text=True);assert r.returncode!=0
 events=(b/'events').read_text();assert 'rename' not in events and 'retention' not in events
 assert 'Remote checksum mismatch' in (b/'log').read_text()
print('PASS: actual SMB backup functions build/test archives and manifest, verify remote readback, rename/purge only after verification; corrupt readback skips retention. SMB transport/router dump mocked.')
