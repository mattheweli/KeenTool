"""Run the real updater/verification engine with a fake GitHub transport and install fixture."""
from pathlib import Path
import tempfile,subprocess,os,json,tarfile,hashlib,io,copy
root=Path(__file__).resolve().parents[1];php='/tmp/keentool-security-runtime/root/usr/bin/php8.3'
# A coordinated bundle can advance without changing the manager component.
with tempfile.TemporaryDirectory() as td:
 b=Path(td);overview=b/'overview';installed=b/'installed';legacy=b/'legacy'
 components={'KeenTool':'2.0.7','keenetic-pingtool':'2.0.2','keenetic-firewall':'4.0.2','Traffic_manager':'2.0.1','SMB_Backup_tool':'2.0.1'}
 overview.write_text(json.dumps({'suite':'KeenTool','channel':'stable','version':'2.0.8','components':components}))
 installed.write_text(json.dumps({'version':'2.0.7','components':{**components,'keenetic-pingtool':'2.0.1'}}))
 digest='sha256:'+hashlib.sha256(overview.read_bytes()).hexdigest()
 def inspect(action,scope):return subprocess.run([php,'-n',str(root/'support/release_update.php'),action,str(overview),'2.0.8',digest,str(installed),str(legacy),scope],text=True,capture_output=True)
 r=inspect('overview','keenetic-pingtool');assert r.returncode==0 and 'keenetic-pingtool: 2.0.1 -> 2.0.2' in r.stdout and 'KeenTool: 2.0.7 ->' not in r.stdout,r.stdout+r.stderr
 r=inspect('selection','KeenTool');assert r.returncode==0 and r.stdout=='0',r.stdout+r.stderr
 r=inspect('selection','keenetic-pingtool');assert r.returncode==0 and r.stdout=='1',r.stdout+r.stderr
print('PASS: verified bundle 2.0.8 selects Pingtool 2.0.2 while manager 2.0.7 remains current.')

with tempfile.TemporaryDirectory() as td:
 b=Path(td);bin=b/'bin';bin.mkdir();tmp=b/'tmp';tmp.mkdir();payload=b/'payload';payload.mkdir();(payload/'support').mkdir()
 (payload/'RELEASE.json').write_text(json.dumps({'suite':'KeenTool','version':'2.0.0','channel':'stable'}))
 (payload/'install.sh').write_text('#!/bin/bash\nprintf "%s\\n" "$*" >> "$KT_TEST_INSTALL"\n')
 (payload/'support/release_install.php').write_text('<?php // fixture dependency\n')
 long='docs/'+'a'*110+'.md';(payload/'docs').mkdir();(payload/long).write_text('extended tar path')
 def checksums():
  (payload/'CHECKSUMS.sha256').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(payload).as_posix()+'\n' for p in sorted(payload.rglob('*')) if p.is_file() and p.name!='CHECKSUMS.sha256'))
 checksums();archive=b/'archive.tar.gz';sidecar=b/'sidecar';api=b/'api.json';calls=b/'curl-calls';installed=b/'installed.json';legacy=b/'legacy';capture=b/'install-calls';flag=b/'flag'
 def pack(special=None,internal_bad=False):
  with tarfile.open(archive,'w:gz') as tar:
   for p in sorted(payload.rglob('*')):
    if p.is_file():
     if internal_bad and p.name=='install.sh':
      data=b'#!/bin/bash\necho corrupt\n';i=tarfile.TarInfo('keentool-2.0.0/install.sh');i.size=len(data);tar.addfile(i,io.BytesIO(data))
     else:tar.add(p,arcname='keentool-2.0.0/'+p.relative_to(payload).as_posix())
   if special=='traversal':
    i=tarfile.TarInfo('keentool-2.0.0/../../escaped');i.size=1;tar.addfile(i,io.BytesIO(b'x'))
   if special=='symlink':
    i=tarfile.TarInfo('keentool-2.0.0/link');i.type=tarfile.SYMTYPE;i.linkname='/etc';tar.addfile(i)
  sidecar.write_text(hashlib.sha256(archive.read_bytes()).hexdigest()+'  keentool-2.0.0.tar.gz\n')
 def release():
  base='https://github.com/mattheweli/KeenTool/releases/download/v2.0.0/'
  return {'tag_name':'v2.0.0','draft':False,'prerelease':False,'assets':[{'name':'keentool-2.0.0.tar.gz','state':'uploaded','size':archive.stat().st_size,'digest':'sha256:'+hashlib.sha256(archive.read_bytes()).hexdigest(),'browser_download_url':base+'keentool-2.0.0.tar.gz'},{'name':'keentool-2.0.0.tar.gz.sha256','state':'uploaded','size':sidecar.stat().st_size,'browser_download_url':base+'keentool-2.0.0.tar.gz.sha256'}]}
 pack();api.write_text(json.dumps(release()));installed.write_text('{"version":"1.9.0"}')
 curl=bin/'curl';curl.write_text('''#!/usr/bin/env python3
import sys,os,json
from pathlib import Path
a=sys.argv[1:];out=Path(a[a.index('-o')+1]);url=next(x for x in a if x.startswith('https://'));code=os.environ.get('KT_TEST_HTTP','200')
with open(os.environ['KT_TEST_CURL'],'a') as f:f.write(json.dumps(a)+'\\n')
source=os.environ['KT_TEST_API'] if url.endswith('/latest') else os.environ['KT_TEST_SIDECAR'] if url.endswith('.sha256') else os.environ.get('KT_TEST_OVERVIEW',os.environ['KT_TEST_ARCHIVE']) if url.endswith('-manifest.json') else os.environ['KT_TEST_ARCHIVE'];out.write_bytes(Path(source).read_bytes())
if '-w' in a:print(code,end='')
sys.exit(0 if code=='200' else 22)
''');curl.chmod(0o755)
 wrapper=bin/'php-cli';wrapper.write_text('#!/bin/bash\nexec '+php+' -n "$@"\n');wrapper.chmod(0o755)
 env=dict(os.environ,KT_PATH=str(bin)+':'+os.environ['PATH'],KT_UPDATE_PHP=str(wrapper),KT_DEPENDENCIES=str(root/'support/dependencies.sh'),KT_UPDATE_HELPER=str(root/'support/release_update.php'),KT_UPDATE_TMP=str(tmp),KT_UPDATE_BASH='/bin/bash',KT_UPDATE_INSTALLED=str(installed),KT_UPDATE_LEGACY=str(legacy),KT_UPDATE_FLAG=str(flag),KT_TEST_CURL=str(calls),KT_TEST_API=str(api),KT_TEST_SIDECAR=str(sidecar),KT_TEST_ARCHIVE=str(archive),KT_TEST_INSTALL=str(capture))
 def run(*args,extra=None):
  r=subprocess.run(['bash',str(root/'support/keentool_update'),*args],env={**env,**(extra or {})},text=True,capture_output=True);assert not list(tmp.iterdir()),'staging leaked';return r
 r=run('--check');assert r.returncode==0 and 'installed 1.9.0; available 2.0.0' in r.stdout and not capture.exists(),r.stdout+r.stderr
 assert len(calls.read_text().splitlines())==1 and flag.read_text().strip()=='2.0.0'
 r=run('--yes');assert r.returncode==0,r.stdout+r.stderr;assert capture.read_text().splitlines()==['--plan --mode upgrade','--apply --mode upgrade'];capture.unlink()
 for a in map(json.loads,calls.read_text().splitlines()):assert '--proto' in a and '--proto-redir' in a and '--insecure' not in a
 installed.write_text('{"version":"2.0.0"}');r=run('--yes');assert r.returncode==0 and 'is current' in r.stdout and not capture.exists()
 r=run('--yes','--reinstall');assert r.returncode==0 and capture.exists();capture.unlink()
 installed.write_text('{"version":"2.1.0"}');r=run('--yes');assert r.returncode==0 and not capture.exists(),'downgrade attempted'
 installed.unlink();legacy.write_text('# KEENTOOL MANAGER v2.0.0a8\n');r=run('--check');assert 'installed 2.0.0a8; available 2.0.0' in r.stdout
 legacy.write_text('# KEENTOOL MANAGER v1.3.4\n');r=run('--check');assert 'installed 1.3.4; available 2.0.0' in r.stdout
 for code in ['404','403']:
  r=run('--yes',extra={'KT_TEST_HTTP':code});assert r.returncode==(0 if code=='404' else 1) and not capture.exists()
 for field in ['draft','prerelease']:
  j=release();j[field]=True;api.write_text(json.dumps(j));r=run('--yes');assert r.returncode!=0 and not capture.exists()
 j=release();j['assets'][0]['browser_download_url']='https://evil.invalid/archive';api.write_text(json.dumps(j));r=run('--yes');assert r.returncode!=0 and not capture.exists()
 api.write_text(json.dumps(release()));sidecar.write_text('0'*64+'  keentool-2.0.0.tar.gz\n');r=run('--yes');assert r.returncode!=0 and 'SHA-256 mismatch' in r.stderr and not capture.exists()
 for special,bad,reason in [('traversal',False,'Unsafe archive path'),('symlink',False,'links and special'),(None,True,'file checksum mismatch')]:
  pack(special,bad);api.write_text(json.dumps(release()));r=run('--yes');assert r.returncode!=0 and reason in r.stderr and not capture.exists(),r.stdout+r.stderr
 # Safe atomic version flag does not follow a preexisting symlink.
 pack();api.write_text(json.dumps(release()));victim=b/'victim';victim.write_text('keep');flag.unlink(missing_ok=True);flag.symlink_to(victim);r=run('--check');assert r.returncode==0 and victim.read_text()=='keep' and not flag.is_symlink()
 # A receipt is created only after a successful installation, for automatic menu restart.
 receipt=b/'receipt';r=run('--yes',extra={'KT_UPDATE_RECEIPT':str(receipt)});assert r.returncode==0 and receipt.read_text().strip()=='2.0.0';capture.unlink();receipt.unlink()
 # Explicit repair audits source drift; ordinary component checks never audit files.
 candidate=json.loads((payload/'RELEASE.json').read_text());candidate['components']={'keenetic-firewall':'4.0.1'};(payload/'RELEASE.json').write_text(json.dumps(candidate));(payload/'projects/keenetic-firewall/scripts').mkdir(parents=True)
 manifest=[];router=b/'router'
 for name,version in [('firewall_stats.sh','4.0.1'),('firewall_monitor','4.0.0'),('firewall_manager.sh','3.0.0'),('100-firewall.sh','3.0.0')]:
  rel='projects/keenetic-firewall/scripts/'+name;f=payload/rel;f.write_text('# SCRIPT v'+version+'\n');dest=router/'opt/bin'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(f.read_bytes());dest.chmod(0o755);manifest.append(rel+'\t/opt/bin/'+name+'\t755')
 (payload/'INSTALL.tsv').write_text('\n'.join(manifest)+'\n');checksums();pack();api.write_text(json.dumps(release()));installed.write_text(json.dumps(candidate))
 r=run('--component','keenetic-firewall','--repair','--yes',extra={'KT_INSTALL_ROOT':str(router)});assert r.returncode==0 and 'All installed package files match' in r.stdout and not capture.exists(),r.stdout+r.stderr
 (router/'opt/bin/firewall_stats.sh').write_text('# SCRIPT v4.0.0\n')
 r=run('--component','keenetic-firewall','--repair','--check','--yes',extra={'KT_INSTALL_ROOT':str(router)});assert r.returncode==0 and '1 package files are missing, different' in r.stdout and not capture.exists()
 r=run('--component','keenetic-firewall','--repair','--yes',extra={'KT_INSTALL_ROOT':str(router),'KT_UPDATE_RECEIPT':str(receipt)});assert r.returncode==0 and 'keenetic-firewall: installed 4.0.1; available 4.0.1' in r.stdout and receipt.exists(),r.stdout+r.stderr;assert len(capture.read_text().splitlines())==2;capture.unlink()
 installed.write_text('{"version":"2.1.0"}');r=run('--component','keenetic-firewall','--repair','--yes',extra={'KT_INSTALL_ROOT':str(router)});assert r.returncode==0 and 'cannot downgrade' in r.stdout and not capture.exists()
 # Lightweight version checks must be independent, verified and download-free before consent.
 candidate['components']={'KeenTool':'2.0.0','keenetic-firewall':'4.0.1','keenetic-pingtool':'2.0.0','Traffic_manager':'2.0.0','SMB_Backup_tool':'2.0.0'}
 (payload/'RELEASE.json').write_text(json.dumps(candidate));checksums();pack()
 overview=b/'overview.json';env['KT_TEST_OVERVIEW']=str(overview)
 overview.write_text(json.dumps({**candidate,'changes':['Independent component updates and explicit repair.']}))
 def publish_overview():
  j=release();j['assets'].append({'name':'keentool-2.0.0-manifest.json','state':'uploaded','size':overview.stat().st_size,'digest':'sha256:'+hashlib.sha256(overview.read_bytes()).hexdigest(),'browser_download_url':'https://github.com/mattheweli/KeenTool/releases/download/v2.0.0/keentool-2.0.0-manifest.json'});api.write_text(json.dumps(j));return j
 publish_overview();local=copy.deepcopy(candidate);local['version']='1.9.0';local['components']['KeenTool']='1.9.0';installed.write_text(json.dumps(local))
 def reset_calls():calls.unlink(missing_ok=True)
 def urls():return [next(x for x in json.loads(line) if x.startswith('https://')) for line in calls.read_text().splitlines()]
 reset_calls();r=run('--component','keenetic-firewall','--yes');assert r.returncode==0 and 'CURRENT' in r.stdout and 'KeenTool:' not in r.stdout and not capture.exists(),r.stdout+r.stderr
 assert len(urls())==2 and all(not u.endswith('.tar.gz') for u in urls())
 reset_calls();r=run('--check');assert r.returncode==0 and all(name in r.stdout for name in candidate['components']) and 'UPDATE AVAILABLE' in r.stdout and 'Shared runtime' in r.stdout and len(urls())==2 and not capture.exists(),r.stdout+r.stderr
 reset_calls();r=run();assert r.returncode==0 and 'confirm' in r.stdout and len(urls())==2 and not capture.exists(),r.stdout+r.stderr
 # Declining an interactive prompt never fetches the archive/checksum or installs anything.
 master,slave=os.openpty();reset_calls()
 proc=subprocess.Popen(['bash',str(root/'support/keentool_update')],stdin=slave,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,text=True);os.close(slave);os.write(master,b'n\n');out,err=proc.communicate(timeout=20);os.close(master)
 assert proc.returncode==0 and 'Apply this coordinated update' in err and len(urls())==2 and not capture.exists(),out+err
 # A real firewall update reports its own change and all coordinated dependencies before apply.
 local['components']['keenetic-firewall']='4.0.0';installed.write_text(json.dumps(local));reset_calls();r=run('--component','keenetic-firewall','--check')
 assert r.returncode==0 and 'keenetic-firewall: 4.0.0 -> 4.0.1' in r.stdout and 'KeenTool: 1.9.0 -> 2.0.0' in r.stdout and len(urls())==2,r.stdout+r.stderr
 r=run('--component','keenetic-firewall','--yes');assert r.returncode==0 and capture.exists(),r.stdout+r.stderr;capture.unlink()
 # Version checks do not repair stale files at the same declared version.
 installed.write_text(json.dumps(candidate));reset_calls();r=run('--component','keenetic-firewall','--yes',extra={'KT_INSTALL_ROOT':str(router)})
 assert r.returncode==0 and 'CURRENT' in r.stdout and 'package files are missing' not in r.stdout and len(urls())==2 and not capture.exists(),r.stdout+r.stderr
 # A mixed installation with a newer component cannot be downgraded by reinstall/repair.
 newer_local=copy.deepcopy(local);newer_local['components']['keenetic-firewall']='4.0.2';installed.write_text(json.dumps(newer_local));reset_calls();r=run('--yes','--reinstall')
 assert r.returncode!=0 and 'Refusing to downgrade installed component' in r.stderr and len(urls())==2 and not capture.exists(),r.stdout+r.stderr
 installed.write_text(json.dumps(local))
 # Tampered/foreign/oversized/duplicate overviews must stop before package download.
 baseline=overview.read_bytes();overview.write_bytes(baseline+b' ');reset_calls();r=run('--yes');assert r.returncode!=0 and 'Overview SHA-256 mismatch' in r.stderr and len(urls())==2
 overview.write_bytes(baseline)
 for mutation in ['foreign','size','duplicate','digest']:
  j=publish_overview()
  if mutation=='foreign':j['assets'][-1]['browser_download_url']='https://evil.invalid/overview.json'
  elif mutation=='size':j['assets'][-1]['size']=65537
  elif mutation=='digest':j['assets'][-1].pop('digest')
  else:j['assets'].append(copy.deepcopy(j['assets'][-1]))
  api.write_text(json.dumps(j));reset_calls();r=run('--yes');assert r.returncode!=0 and len(urls())==1 and not capture.exists(),r.stdout+r.stderr
 publish_overview();local['components']['keenetic-firewall']='4.0.0';installed.write_text(json.dumps(local))
 # The approved component versions must exactly match the subsequently verified archive.
 altered=copy.deepcopy(candidate);altered['components']['keenetic-firewall']='4.0.2';(payload/'RELEASE.json').write_text(json.dumps(altered));checksums();pack();publish_overview();r=run('--yes');assert r.returncode!=0 and 'do not match the approved overview' in r.stderr and not capture.exists(),r.stdout+r.stderr
 # Install/update verifies every selected component target, not just its version record.
 candidate['components']['Dashboard']='2.0.3';(payload/'RELEASE.json').write_text(json.dumps(candidate))
 targets=[];scopes={};rows=[]
 for line in manifest:
  src,path,mode=line.split('\t');scopes[src]='keenetic-firewall';rows.append((src,path,mode))
 for src,path,owner,text in [('projects/KeenTool/index.html','/opt/var/www/index.html','Dashboard','<!-- KeenTool Dashboard v2.0.3 -->'),('projects/KeenTool/keentool','/opt/bin/keentool','KeenTool','# MANAGER v2.0.0'),('assets/shared.js','/opt/var/www/assets/shared.js','shared','// shared fixture'),('projects/Traffic_manager/traffic.sh','/opt/bin/traffic.sh','Traffic_manager','# TRAFFIC v2.0.0')]:
  f=payload/src;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(text+'\n');rows.append((src,path,'644'));scopes[src]=owner
 (payload/'INSTALL.tsv').write_text(''.join('\t'.join(row)+'\n' for row in rows));(payload/'FILE_SCOPES.json').write_text(json.dumps(scopes))
 import re,shutil
 for src,path,mode in rows:
  f=payload/src;dest=router/path.lstrip('/');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy(f,dest);dest.chmod(int(mode,8));match=re.search(r'\bv([0-9]+\.[0-9]+\.[0-9]+)\b',f.read_text()[:4096])
  targets.append({'source':src,'path':path,'mode':mode,'owner':scopes[src],'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'version':match[1] if match else '-'})
 checksums();pack();overview.write_text(json.dumps({**candidate,'targets':targets,'changes':['Verify all selected component files before consent.']}));publish_overview();installed.write_text(json.dumps(candidate));env['KT_INSTALL_ROOT']=str(router)
 reset_calls();r=run('--component','keenetic-firewall','--check');assert r.returncode==0 and 'Files verified: 5; differences: 0' in r.stdout and len(urls())==2,r.stdout+r.stderr
 monitor=router/'opt/bin/firewall_monitor';monitor.write_text('# MONITOR v3.0.0\n');reset_calls();r=run('--component','keenetic-firewall','--check')
 assert r.returncode==0 and 'Files verified: 5; differences: 1' in r.stdout and 'installed 3.0.0; available 4.0.0' in r.stdout and 'Repair 1' in r.stdout and len(urls())==2 and not capture.exists(),r.stdout+r.stderr
 r=run('--component','keenetic-firewall','--yes');assert r.returncode==0 and capture.exists(),r.stdout+r.stderr;capture.unlink();shutil.copy(payload/'projects/keenetic-firewall/scripts/firewall_monitor',monitor);monitor.chmod(0o755)
 # Unrelated traffic drift cannot trigger a firewall component update.
 (router/'opt/bin/traffic.sh').write_text('old traffic\n');reset_calls();r=run('--component','keenetic-firewall','--yes');assert r.returncode==0 and 'differences: 0' in r.stdout and len(urls())==2 and not capture.exists(),r.stdout+r.stderr
 # Missing files, modes and common dependencies are included in the selected audit.
 stats=router/'opt/bin/firewall_stats.sh';stats.unlink();monitor.chmod(0o644);(router/'opt/var/www/assets/shared.js').write_text('old shared\n');reset_calls();r=run('--component','keenetic-firewall','--check')
 assert r.returncode==0 and 'differences: 3' in r.stdout and 'permissions differ' in r.stdout and 'shared.js' in r.stdout and 'traffic.sh' not in r.stdout and len(urls())==2,r.stdout+r.stderr
 # Dashboard uses its real HTML version, separate from both manager and stale record.
 dashboard=router/'opt/var/www/index.html';dashboard.write_text('<!-- KeenTool Dashboard v2.0.2 -->\n');reset_calls();r=run('--component','Dashboard','--check')
 assert r.returncode==0 and 'Dashboard' in r.stdout and re.search(r'Dashboard\s+2\.0\.2\s+2\.0\.3\s+UPDATE AVAILABLE',r.stdout) and 'firewall_monitor' not in r.stdout and 'KeenTool: 2.0.0' not in r.stdout and len(urls())==2,r.stdout+r.stderr
 # An inconsistent overview target hash cannot be used for an installation.
 j=json.loads(overview.read_text());j['targets'][0]['sha256']='0'*64;overview.write_text(json.dumps(j));publish_overview();r=run('--component','keenetic-firewall','--yes')
 assert r.returncode!=0 and 'Overview installation target mismatch' in r.stderr and not capture.exists(),r.stdout+r.stderr
 # New-capability installers receive explicit retention without changing legacy argv.
 overview.write_text(json.dumps({**candidate,'targets':targets,'changes':['Verified retention policy.']}));publish_overview()
 r=run('--component','keenetic-firewall','--yes','--no-backup');assert r.returncode!=0 and 'older installer cannot discard' in r.stderr,r.stdout+r.stderr
 assert capture.read_text().splitlines()==['--plan --mode upgrade'];capture.unlink()
 policy=b/'backup-policy';env['KT_TEST_POLICY']=str(policy)
 (payload/'install.sh').write_text('#!/bin/bash\n# KT_INSTALL_BACKUP_RETENTION_V1\nprintf "%s\\n" "$*" >> "$KT_TEST_INSTALL"\nif [ "$1" = --apply ];then printf "%s" "$KT_INSTALL_BACKUP_POLICY" > "$KT_TEST_POLICY";fi\n')
 checksums();pack();publish_overview()
 for option,expected in [('--keep-backup','keep'),('--no-backup','discard')]:
  r=run('--component','keenetic-firewall','--yes',option);assert r.returncode==0 and policy.read_text()==expected,r.stdout+r.stderr
  assert capture.read_text().splitlines()==['--plan --mode upgrade','--apply --mode upgrade'];capture.unlink();policy.unlink()
 r=run('--component','keenetic-firewall','--check','--no-backup');assert r.returncode==0 and not capture.exists() and not policy.exists(),r.stdout+r.stderr
 # Explicit HTTPS consent is forwarded only to capable verified installers.
 r=run('--component','keenetic-firewall','--yes','--enable-https');assert r.returncode!=0 and 'cannot safely migrate HTTPS' in r.stderr and not capture.exists(),r.stdout+r.stderr
 (payload/'install.sh').write_text((payload/'install.sh').read_text().replace('# KT_INSTALL_BACKUP_RETENTION_V1','# KT_INSTALL_BACKUP_RETENTION_V1\n# KT_INSTALL_HTTPS_MIGRATION_V1'))
 checksums();pack();publish_overview()
 r=run('--component','keenetic-firewall','--yes','--enable-https');assert r.returncode==0,r.stdout+r.stderr
 assert capture.read_text().splitlines()==['--plan --mode upgrade --enable-https','--apply --mode upgrade --enable-https'],capture.read_text();capture.unlink()
print('PASS: real remote updater, stable-only GitHub metadata/URLs/digests, check versus apply, no downgrade, alpha/public version detection, HTTPS-only curl, 404/403 handling, tar/PAX streaming verification, traversal/symlink/internal checksum rejection, atomic flag and staging cleanup; independent component/all-version overviews, no archive before consent, interactive decline, explicit repair separation, overview digests and archive consistency; GitHub/installer mocked, scoped target/mode verification, stale same-version scripts, shared and unrelated files, independent Dashboard HTML version and target manifest consistency; no network or router writes.')
