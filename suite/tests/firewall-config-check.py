from pathlib import Path
import tempfile,subprocess,os
root=Path(__file__).resolve().parents[1];s=(root/'projects/keenetic-firewall/scripts/firewall_manager.sh').read_text();fn=s[s.index('save_config() {'):s.index('# --- PORT EDITOR')]
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'firewall.conf';p.write_text('ENABLE_FIREWALL="true"\nFW_LOG_RATE=2\nFW_LOG_BURST=10\nALLOW_LARGE_LIST_SHRINK=false\nCUSTOM_FUTURE_OPTION="keep"\n')
 r=subprocess.run(['bash','-c',fn+'\nCONF_FILE="$1";ENABLE_FIREWALL=false;save_config','test',str(p)],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
 text=p.read_text();assert 'ENABLE_FIREWALL="false"' in text;assert 'FW_LOG_RATE=2' in text and 'FW_LOG_BURST=10' in text;assert 'ALLOW_LARGE_LIST_SHRINK=false' in text and 'CUSTOM_FUTURE_OPTION="keep"' in text;assert p.stat().st_mode&0o777==0o600
 old=p.read_bytes();r=subprocess.run(['bash','-c',fn+'\nCONF_FILE="$1";mktemp(){ return 1; };save_config','test',str(p)],capture_output=True,text=True);assert r.returncode!=0 and p.read_bytes()==old
 print('PASS: atomic manager config replacement preserves logging/list safety/future options, mode 600 and prior file on temp allocation failure.')
