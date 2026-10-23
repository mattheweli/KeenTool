#!/usr/bin/env python3
"""Build the installable release asset from the checked-out coordinated suite."""
from pathlib import Path
import hashlib,json,tarfile,gzip,datetime,sys,re
root=Path(__file__).resolve().parents[1];release=json.loads((root/'RELEASE.json').read_text());version=release['version']
assert re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+',version)
epoch=int(datetime.datetime.fromisoformat(release['date']).replace(tzinfo=datetime.timezone.utc).timestamp())
files=sorted(p for p in root.rglob('*') if p.is_file() and p.name!='CHECKSUMS.sha256' and '.git' not in p.parts and '__pycache__' not in p.parts)
(root/'CHECKSUMS.sha256').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(root).as_posix()+'\n' for p in files))
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True);asset=out/('keentool-'+version+'.tar.gz')
with asset.open('wb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=epoch,filename='') as gz,tarfile.open(fileobj=gz,mode='w') as tar:
 for p in sorted(files+[root/'CHECKSUMS.sha256']):
  assert not p.is_symlink();info=tar.gettarinfo(str(p),'keentool-'+version+'/'+p.relative_to(root).as_posix());info.uid=info.gid=0;info.uname=info.gname='root';info.mtime=epoch
  with p.open('rb') as f:tar.addfile(info,f)
asset.with_name(asset.name+'.sha256').write_text(hashlib.sha256(asset.read_bytes()).hexdigest()+'  '+asset.name+'\n')
print(asset)

# Publish a lightweight component overview for checks before package download consent.
overview={key:release[key] for key in ('suite','version','channel','components')}
overview.update(json.loads((root/'UPDATE_NOTES.json').read_text()))
manifest=out/('keentool-'+version+'-manifest.json')
manifest.write_text(json.dumps(overview,indent=2)+'\n')
manifest.with_name(manifest.name+'.sha256').write_text(hashlib.sha256(manifest.read_bytes()).hexdigest()+'  '+manifest.name+'\n')
