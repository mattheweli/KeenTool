from pathlib import Path
import tempfile,subprocess,os
helper=Path(__file__).resolve().parents[1]/'support/wan_syslog_monitor'
with tempfile.TemporaryDirectory() as td:
 p=Path(td);log=p/'messages';state=p/'state';capture=p/'mail';email=p/'email';inc=p/'incidents'
 email.write_text('#!/bin/bash\nprintf "%s\\n%s\\n" "$1" "$2" >> "$CAPTURE"\n');email.chmod(0o755)
 env=dict(os.environ,KT_COMMON=str(Path(__file__).resolve().parents[1]/'support/common.sh'),LC_ALL='C',TZ='UTC',WAN_SYSLOG_FILE=str(log),KT_WAN_STATE=str(state),KT_WAN_EMAIL=str(email),KT_WAN_INCIDENT_LOG=str(inc),CAPTURE=str(capture),KT_WAN_NOW='1791979200',EMAIL_ALERTS='true',WAN_LABEL='ppp0')
 def run():
  r=subprocess.run(['bash',str(helper)],env=env,text=True,capture_output=True);assert r.returncode==0,r.stderr;return r
 def append(text):
  with log.open('a') as f:f.write(text)
 def line(t,pid,msg):return f'Oct 14 {t} ROUTER pppd[{pid}]: {msg}\n'
 log.write_text(line('00:00:00',10,'Using interface ppp0')+line('00:00:01',10,'local  IP address 192.0.2.1'))
 run();assert not capture.exists(), 'historical events must be silent'
 append(line('01:12:13',10,'Serial link appears to be disconnected.')+line('01:12:19',10,'Connection terminated.')+line('01:12:19',10,'Modem hangup')+line('01:12:19',10,'Exit.')+line('01:12:35',20,'Using interface ppp0')+line('01:12:36',20,'local  LL address fe80::1'))
 run();assert capture.read_text().count('WAN ppp0 disconnected (PPP syslog)')==1 and 'recovered' not in capture.read_text()
 append(line('01:12:36',20,'local  IP address 192.0.2.2'));run();s=capture.read_text();assert '(23 seconds)' in s and 'ppp0 · IPv4' in s
 run();assert capture.read_text()==s,'same log must not notify twice'
 append(line('02:00:00',20,'Modem hangup'));log.rename(p/'messages.1');log.write_text(line('02:00:10',30,'Using interface ppp0')+line('02:00:20',30,'local  IP address 192.0.2.3'));run();assert '(20 seconds)' in capture.read_text()
 # Retry failed transport without losing queued events.
 email.write_text('#!/bin/bash\nexit 1\n');append(line('03:00:00',30,'Connection terminated.'));run();assert list((state/'outbox').glob('[!.]*'))
 email.write_text('#!/bin/bash\nprintf "%s\\n%s\\n" "$1" "$2" >> "$CAPTURE"\n');run();assert not list((state/'outbox').glob('[!.]*'))
 append('Oct 14 03:00:01 ROUTER ndm: Core::System::Clock: system time has been changed.\n'+line('03:00:05',40,'Using interface ppp0')+line('03:00:10',40,'local  IP address 192.0.2.4'));run();assert 'Duration unavailable' in capture.read_text()
 # Complete trailing lines only; retain cursor before a partial line.
 append(line('04:00:00',40,'Modem hangup').rstrip('\n'));before=capture.read_text();run();assert capture.read_text()==before
 append('\n');run();assert capture.read_text().count('WAN ppp0 disconnected (PPP syslog)')==4
 # A different PPP interface must not be misidentified as configured WAN.
 append(line('05:00:00',50,'Using interface ppp1')+line('05:00:01',50,'Modem hangup'));before=capture.read_text();run();assert capture.read_text()==before
print('PASS: initial baseline, actual 23-second PPP outage pattern, repeated-down suppression, IPv6 link-local excluded, unchanged-log dedup, rename rotation, SMTP retry, clock uncertainty, partial lines and interface filtering.')
