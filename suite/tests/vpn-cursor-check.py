from pathlib import Path
import subprocess,tempfile,os
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as td:
 b=Path(td);bin=b/'bin';bin.mkdir();log=b/'vpn.log';state=b/'state';bans=b/'bans'
 ipset=bin/'ipset';ipset.write_text('#!/bin/bash\ncase "$1" in test)exit 1;;add)printf "%s\\n" "$3" >> "$BANS";;esac\n');ipset.chmod(0o755)
 logger=bin/'logger';logger.write_text('#!/bin/bash\nexit 0\n');logger.chmod(0o755)
 log.write_text('old TLS handshake failed 203.0.113.1:443\n')
 env=dict(os.environ,KT_PATH=str(bin)+':'+os.environ['PATH'],KT_COMMON=str(root/'support/common.sh'),KT_RUN_DIR=td,KT_VPN_LOG=str(log),KT_VPN_STATE=str(state),KT_VPN_SAVE=str(b/'saved'),KT_FW_CONF=str(b/'missing'),VPN_FAILURE_THRESHOLD='2',VPN_FAILURE_WINDOW='900',VPN_BAN_TIMEOUT='60',BANS=str(bans),KT_NOW='1000')
 def run():
  r=subprocess.run(['bash',str(root/'projects/keenetic-firewall/scripts/vpn_scan.sh')],env=env,capture_output=True,text=True);assert r.returncode==0,r.stderr
 run();assert not bans.exists()
 with log.open('a') as f:f.write('new TLS handshake failed 203.0.113.2:443')
 run();assert (state/'failures').read_text()==''
 with log.open('a') as f:f.write('\nnew TLS handshake failed 203.0.113.2:443\n')
 run();assert bans.read_text().splitlines()==['203.0.113.2']
 before=(state/'failures').read_text();run();assert (state/'failures').read_text()==before
print('PASS: actual VPN scanner skips history, retries incomplete lines, bans only after threshold, unchanged cursor never recounts failures.')
