from pathlib import Path
import tempfile,subprocess,os,time,json
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as td:
 p=Path(td);log=p/'messages';conf=p/'pingtool.conf';mail=p/'email';capture=p/'mail';marker=p/'sending'
 log.write_text('Oct 14 00:00:00 ROUTER pppd[10]: Using interface ppp0\n')
 conf.write_text('WAN_SYSLOG_ENABLED="true"\nWAN_MONITOR_INTERVAL=1\nWAN_LABEL="ppp0"\nEMAIL_ALERTS="true"\n')
 mail.write_text('#!/bin/bash\ntouch "$SENDING"\nsleep 3\nprintf "%s\\n%s\\n" "$1" "$2" >> "$CAPTURE"\n');mail.chmod(0o755)
 env=dict(os.environ,KT_COMMON=str(Path(__file__).resolve().parents[1]/'support/common.sh'),KT_TEST_MODE='true',KT_BASH='/bin/bash',KT_WAN_SERVICE=str(root/'support/wan_syslog_service'),KT_WAN_HELPER=str(root/'support/wan_syslog_monitor'),KT_PING_CONF=str(conf),KT_WAN_PID=str(p/'pid'),KT_WAN_SERVICE_LOG=str(p/'service.log'),WAN_SYSLOG_FILE=str(log),KT_WAN_STATE=str(p/'state'),KT_WAN_EMAIL=str(mail),KT_WAN_INCIDENT_LOG=str(p/'incidents'),CAPTURE=str(capture),SENDING=str(marker),KT_WAN_NOW='1791979200')
 def call(arg):return subprocess.run(['bash',str(root/'support/wan_syslog_service'),arg],env=env,capture_output=True,text=True)
 def until(fn,seconds=8):
  end=time.monotonic()+seconds
  while time.monotonic()<end:
   if fn():return
   time.sleep(.1)
  raise AssertionError((p/'service.log').read_text())
 try:
  r=call('start');assert r.returncode==0,(r.stderr,(p/'service.log').read_text(),list(p.iterdir()))
  until(lambda:(p/'state/state').exists());r=call('start');assert r.returncode==0 and 'already' in r.stdout
  with log.open('a') as f:f.write('Oct 14 01:12:13 ROUTER pppd[10]: Modem hangup\n')
  until(marker.exists)
  with log.open('a') as f:f.write('Oct 14 01:12:35 ROUTER pppd[20]: Using interface ppp0\nOct 14 01:12:36 ROUTER pppd[20]: local  IP address 192.0.2.1\n')
  until(lambda:any('recovered' in x.name for x in (p/'state/outbox').glob('[!.]*')),2.8)
  assert not capture.exists(),'scan must record recovery while transport is still blocked'
  until(lambda:capture.exists() and '(23 seconds)' in capture.read_text(),10)
  r=call('stop');assert r.returncode==0,r.stderr;assert not (p/'pid').exists();assert call('status').returncode!=0
  conf.write_text(conf.read_text().replace('WAN_SYSLOG_ENABLED="true"','WAN_SYSLOG_ENABLED="false"'));r=call('start');assert r.returncode==0 and 'disabled' in r.stdout
 finally:call('stop')
 # Stop while a scan is still writing: TERM must not orphan that scan.
 slow=p/'slow-helper';started=p/'scan-started';finished=p/'scan-finished'
 slow.write_text('#!/bin/bash\n[ "$1" = --scan ] || exit 0\ntouch "$SCAN_STARTED"\nsleep 4\nprintf done > "$SCAN_FINISHED"\n');slow.chmod(0o755)
 conf.write_text('WAN_SYSLOG_ENABLED="true"\nWAN_MONITOR_INTERVAL=1\n')
 env.update(KT_WAN_HELPER=str(slow),SCAN_STARTED=str(started),SCAN_FINISHED=str(finished))
 try:
  assert call('start').returncode==0
  until(started.exists)
  assert not finished.exists()
  r=call('stop');assert r.returncode==0,r.stdout+r.stderr
  assert finished.read_text()=='done','stop returned before the in-flight scanner completed'
  assert not (p/'pid').exists()
 finally:call('stop')
print('PASS: standalone service start/idempotence/stop/status/disabled config; detects PPP recovery during slow SMTP independently of ping jobs.')
