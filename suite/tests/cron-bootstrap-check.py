from pathlib import Path
import tempfile,subprocess,os
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as td:
 p=Path(td);opt=p/'opt';bin=opt/'bin';init=opt/'etc/init.d';bin.mkdir(parents=True);init.mkdir(parents=True)
 (bin/'bash').symlink_to('/bin/bash')
 state=p/'running';events=p/'events';cronconf=opt/'etc/crontab';cronconf.write_text('12,42 * * * * root pingtool.sh\n*/10 * * * * root traffic_manager.sh ppp0\n')
 def script(path,body):path.write_text('#!/bin/bash\n'+body);path.chmod(0o755)
 script(bin/'pidof','[ -f '+str(state)+' ] && echo 1234\n')
 script(bin/'keentool_security_service','echo "security-$1" >> '+str(events)+'\n')
 cron=init/'S10cron';script(cron,'echo "$1" >> '+str(events)+'\ntouch '+str(state)+'\n')
 wrapper=init/'S96keentool-security';wrapper.write_text((root/'support/S96keentool-security').read_text().replace('/opt',str(opt)))
 def call(action='ensure-cron'):return subprocess.run(['bash',str(wrapper),action],capture_output=True,text=True)
 original=cronconf.read_bytes();r=call();assert r.returncode==0,r.stderr;assert events.read_text()=='start\n';assert cronconf.read_bytes()==original
 r=call();assert r.returncode==0 and events.read_text()=='start\n'
 state.unlink();r=call('start');assert r.returncode==0 and events.read_text().endswith('start\nsecurity-start\n')
 state.unlink();script(cron,'exit 1\n');assert call().returncode!=0
 cron.unlink();assert call().returncode!=0
 script(cron,'exit 0\n');assert call().returncode!=0 # A zero init exit is insufficient without a daemon.
 other=init/'S20crond';script(other,'exit 0\n');assert call().returncode!=0
 assert cronconf.read_bytes()==original
print('PASS: real init wrapper: start stopped cron at install/boot, leave active daemon alone, reject ambiguous/missing/failed init and false success; schedules unchanged.')
