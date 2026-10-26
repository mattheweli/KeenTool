from pathlib import Path
import tempfile,subprocess
b=Path(__file__).resolve().parents[1];s=(b/'projects/KeenTool/keentool').read_text();start=s.index('configure_pingtool()');end=s.index('\nkt_managed_update() {',start);fn=s[start:end]
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'pingtool.conf';original='PING_TARGET="8.8.8.8"\nPING_TARGET_V6="::1"\nENABLE_IPV6="true"\nPING_DURATION=30\nTRIGGER_LATENCY=30\nRETENTION_DAYS=45\nEMAIL_ALERTS="true"\nCUSTOM_SETTING="preserve"\n';p.write_text(original)
 code='header(){ :; };pause(){ :; };sleep(){ :; };'+fn.replace('P=/opt/etc/pingtool.conf', 'P="'+str(p)+'"')+'\nconfigure_pingtool'
 def run(data):
  r=subprocess.run(['bash','-c',code],input=data,text=True,capture_output=True);assert r.returncode==0,r.stderr;return r.stdout
 run('8\n5000\n0\nn\n');assert 'MAX_DISPLAY_POINTS=5000' in p.read_text();assert original in p.read_text()
 run('8\n1000\n0\nn\n');assert p.read_text().count('MAX_DISPLAY_POINTS=')==1;assert 'MAX_DISPLAY_POINTS=1000' in p.read_text()
 before=p.read_text();out=run('8\n50\n0\n');assert p.read_text()==before and '100 and 10000' in out
 out=run('6\n0\n0\n');assert p.read_text()==before and '1 and 3650' in out
 run('6\n90\n0\nn\n');assert 'RETENTION_DAYS=90' in p.read_text();assert 'CUSTOM_SETTING="preserve"' in p.read_text()
 run('9\nppp0\n0\n');assert 'WAN_LABEL="ppp0"' in p.read_text()
 run('9\nppp1\n0\n');assert p.read_text().count('WAN_LABEL=')==1 and 'WAN_LABEL="ppp1"' in p.read_text()
 before=p.read_text();run('9\nbad name\n0\n');assert p.read_text()==before
 run('9\n\n0\n');assert 'WAN_LABEL=""' in p.read_text()
 run('10\n10\n0\n');assert 'WAN_MONITOR_INTERVAL=10' in p.read_text()
 before=p.read_text();run('10\n0\n0\n');assert p.read_text()==before
print('PASS: menu chart-cap persistence/replacement, invalid values rejected, retention settings and unrelated config preserved.')
