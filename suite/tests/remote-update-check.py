"""Run the real updater/verification engine with a fake GitHub transport and install fixture."""
from pathlib import Path
import tempfile,subprocess,os,json,tarfile,hashlib,io,copy
root=Path(__file__).resolve().parents[1];php='/tmp/keentool-security-runtime/root/usr/bin/php8.3'
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
source=os.environ['KT_TEST_API'] if url.endswith('/latest') else os.environ['KT_TEST_SIDECAR'] if url.endswith('.sha256') else os.environ['KT_TEST_ARCHIVE'];out.write_bytes(Path(source).read_bytes())
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
 # Component checks must compare manifest versions and detect file drift even at the current suite version.
 candidate=json.loads((payload/'RELEASE.json').read_text());candidate['components']={'keenetic-firewall':'4.0.1'};(payload/'RELEASE.json').write_text(json.dumps(candidate));(payload/'projects/keenetic-firewall/scripts').mkdir(parents=True)
 manifest=[];router=b/'router'
 for name,version in [('firewall_stats.sh','4.0.1'),('firewall_monitor','4.0.0'),('firewall_manager.sh','3.0.0'),('100-firewall.sh','3.0.0')]:
  rel='projects/keenetic-firewall/scripts/'+name;f=payload/rel;f.write_text('# SCRIPT v'+version+'\n');dest=router/'opt/bin'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(f.read_bytes());dest.chmod(0o755);manifest.append(rel+'\t/opt/bin/'+name+'\t755')
 (payload/'INSTALL.tsv').write_text('\n'.join(manifest)+'\n');checksums();pack();api.write_text(json.dumps(release()));installed.write_text(json.dumps(candidate))
 r=run('--component','keenetic-firewall','--yes',extra={'KT_INSTALL_ROOT':str(router)});assert r.returncode==0 and 'All installed package files match' in r.stdout and not capture.exists(),r.stdout+r.stderr
 (router/'opt/bin/firewall_stats.sh').write_text('# SCRIPT v4.0.0\n')
 r=run('--component','keenetic-firewall','--check',extra={'KT_INSTALL_ROOT':str(router)});assert r.returncode==0 and '1 package files are missing, different' in r.stdout and not capture.exists()
 r=run('--component','keenetic-firewall','--yes',extra={'KT_INSTALL_ROOT':str(router),'KT_UPDATE_RECEIPT':str(receipt)});assert r.returncode==0 and 'keenetic-firewall: installed 4.0.1; available 4.0.1' in r.stdout and receipt.exists(),r.stdout+r.stderr;assert len(capture.read_text().splitlines())==2;capture.unlink()
 installed.write_text('{"version":"2.1.0"}');r=run('--component','keenetic-firewall','--yes',extra={'KT_INSTALL_ROOT':str(router)});assert r.returncode==0 and 'cannot downgrade' in r.stdout and not capture.exists()
print('PASS: real remote updater, stable-only GitHub metadata/URLs/digests, check versus apply, no downgrade, alpha/public version detection, HTTPS-only curl, 404/403 handling, tar/PAX streaming verification, traversal/symlink/internal checksum rejection, atomic flag and staging cleanup; GitHub/installer mocked, no network or router writes.')
