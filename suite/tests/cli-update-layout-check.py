"""Check readable complete CLI summaries without changing machine selection output."""
from pathlib import Path
import tempfile,subprocess,json,hashlib
root=Path(__file__).resolve().parents[1];php='/tmp/keentool-security-runtime/root/usr/bin/php8.3'
with tempfile.TemporaryDirectory() as td:
 b=Path(td);components={'KeenTool':'2.0.9','keenetic-firewall':'4.0.2','keenetic-pingtool':'2.0.2','Traffic_manager':'2.0.1','SMB_Backup_tool':'2.0.1'}
 installed=b/'installed.json';installed.write_text(json.dumps({'version':'2.0.10','components':{**components,'KeenTool':'2.0.8'}}))
 targets=[{'source':'support/example'+str(i)+'.sh','path':'/opt/bin/example'+str(i),'mode':'755','owner':'KeenTool','sha256':'a'*64,'version':'1.0.0'} for i in range(12)]
 note='This release explains a longer change in ordinary English so the terminal can wrap the complete sentence and continue the same release note on an indented following line.'
 overview=b/'overview.json';overview.write_text(json.dumps({'suite':'KeenTool','channel':'stable','version':'2.0.11','components':components,'changes':[note],'targets':targets}))
 digest='sha256:'+hashlib.sha256(overview.read_bytes()).hexdigest()
 def run(action):return subprocess.run([php,'-n',str(root/'support/release_update.php'),action,str(overview),'2.0.11',digest,str(installed),str(b/'legacy'),'KeenTool',str(b/'router')],capture_output=True,text=True)
 r=run('overview');assert r.returncode==0,r.stdout+r.stderr
 assert 'Component versions' in r.stdout and 'Component' in r.stdout and 'Installed' in r.stdout and 'Available' in r.stdout and 'Status' in r.stdout,r.stdout
 assert 'Files to install (12)' in r.stdout and all('/opt/bin/example'+str(i)+': missing' in r.stdout for i in range(12)),r.stdout
 assert 'Release notes' in r.stdout and ' '.join(note.split()) in ' '.join(r.stdout.split()),r.stdout
 assert max(map(len,r.stdout.splitlines()))<=78,r.stdout
 r=run('selection');assert r.returncode==0 and r.stdout=='1',r.stdout+r.stderr
print('PASS: aligned columns, all twelve file differences retained, wrapped complete release notes, bounded terminal width and unchanged machine selection.')
