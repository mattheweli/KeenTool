#!/usr/bin/env python3
"""Build repository overlays, draft notes and checksummed assets from the stable suite."""
from pathlib import Path
import argparse,shutil,json,tarfile,hashlib,datetime,subprocess,gzip
p=argparse.ArgumentParser();p.add_argument('--upstream-dir',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
root=Path(__file__).resolve().parents[1];kit=args.output.resolve();kit.mkdir(parents=True,exist_ok=False)
release=json.loads((root/'RELEASE.json').read_text());version=release['version'];epoch=int(datetime.datetime.fromisoformat(release['date']).replace(tzinfo=datetime.timezone.utc).timestamp())
def checksum_tree(base):
 files=sorted(p for p in base.rglob('*') if p.is_file() and p.name!='CHECKSUMS.sha256' and '.git' not in p.parts and '__pycache__' not in p.parts)
 (base/'CHECKSUMS.sha256').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(base).as_posix()+'\n' for p in files))
def archive(base,out,dirname):
 with out.open('wb') as raw, gzip.GzipFile(fileobj=raw,mode='wb',mtime=epoch,filename='') as gz, tarfile.open(fileobj=gz,mode='w') as tar:
  for f in sorted(base.rglob('*')):
   if not f.is_file() or '.git' in f.parts or '__pycache__' in f.parts:continue
   info=tar.gettarinfo(str(f),dirname+'/'+f.relative_to(base).as_posix());info.uid=info.gid=0;info.uname=info.gname='root';info.mtime=epoch
   with f.open('rb') as stream:tar.addfile(info,stream)
 checksum=hashlib.sha256(out.read_bytes()).hexdigest();out.with_name(out.name+'.sha256').write_text(checksum+'  '+out.name+'\n')
checksum_tree(root)
package=kit/('keentool-'+version);shutil.copytree(root,package,ignore=shutil.ignore_patterns('__pycache__','.git'))
assets=kit/'assets';assets.mkdir();subprocess.run(['python3',str(root/'tools/package-suite.py'),str(assets)],check=True)
rows=json.loads((root/'UPSTREAM_BASELINES.json').read_text())
if (root/'PATCH_BASELINES.json').is_file():
 patches=json.loads((root/'PATCH_BASELINES.json').read_text());rows=[{'repository':'mattheweli/'+repo,'version':v['version'],'tag':'v'+v['version'],'baseline_commit':v['main'],'baseline_branch':'main'} for repo,v in patches.items()]
notes=kit/'notes';notes.mkdir()
changelog=(root/'CHANGELOG.md').read_text()
for row in rows:
 repo=row['repository'].split('/')[1];baseline=args.upstream_dir/repo
 actual=subprocess.check_output(['git','-C',str(baseline),'rev-parse','HEAD'],text=True).strip()
 if actual!=row['baseline_commit']:raise SystemExit('Upstream baseline changed: '+repo)
 dest=kit/'repositories'/repo;shutil.copytree(baseline,dest,ignore=shutil.ignore_patterns('.git','__pycache__'))
 shutil.copytree(root/'projects'/repo,dest,dirs_exist_ok=True)
 body=changelog.split('## '+repo+' '+row['version']+'\n',1)[1].split('\n## ',1)[0].strip()
 note='# '+repo+' '+row['version']+'\n\n'+body+'\n\n## Installation and compatibility\n\nInstall/update through the complete KeenTool '+version+' suite asset. Component archives require the coordinated shared runtime; do not replace isolated scripts over older installations. Existing settings, credentials, databases and upgrade schedules are preserved. Read the suite docs/INSTALL.md and SECURITY.md.\n\n## Known feed limitation\n\nIPdeny IPv6 KP may return HTTP 404; incomplete candidates retain the installed GeoBlock6 list. Cached installation time is not source freshness. This is reported explicitly, not silently bypassed.\n\n## Validation\n\nSee suite docs/VALIDATION.md for isolated regression results and the live-router acceptance steps that remain before publication. This prepared release is a draft; no router reboot or public deployment is claimed.\n'
 (dest/'RELEASE.json').write_text(json.dumps({'repository':row['repository'],'version':row['version'],'channel':'stable'},indent=2)+'\n')
 workflow=dest/'.github/workflows/stable-draft.yml';workflow.parent.mkdir(parents=True,exist_ok=True);workflow.write_text((root/'tools/draft-workflow.yml').read_text())
 (notes/(repo+'.md')).write_text(note);(dest/'CHANGELOG.md').write_text('# '+repo+' stable changelog\n\n'+body+'\n');(dest/'RELEASE_NOTES.md').write_text(note)
 if repo=='KeenTool':
  shutil.copy(root/'bootstrap.sh',dest/'bootstrap.sh')
  shutil.copytree(package,dest/'suite')
  workflow=dest/'.github/workflows/release-checks.yml';workflow.parent.mkdir(parents=True,exist_ok=True)
  workflow.write_text('''name: Stable suite checks
on: [push, pull_request, workflow_dispatch]
permissions:
  contents: read
jobs:
  isolated-checks:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - run: sudo apt-get update && sudo apt-get install -y php8.3-cli php8.3-cgi php8.3-sqlite3 sqlite3
      - run: sudo env PATH="$PATH" KT_VALIDATION_RESULTS="$RUNNER_TEMP/keentool-validation.json" python3 suite/tools/check-release.py
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: validation-${{ github.run_id }}-${{ github.run_attempt }}
          path: ${{ runner.temp }}/keentool-validation.json
          if-no-files-found: warn
''')
 checksum_tree(dest);archive(dest,assets/(repo+'-'+row['version']+'-sources.tar.gz'),repo+'-'+row['version'])
(kit/'release-plan.json').write_text(json.dumps(rows,indent=2)+'\n')
(kit/'tools').mkdir();shutil.copy(root/'tools/publish-drafts.sh',kit/'tools/publish-drafts.sh');(kit/'tools/publish-drafts.sh').chmod(0o755)
(kit/'README.md').write_text(f'''# KeenTool stable release kit — {release['date']}

- keentool-{version}/: complete installable suite.
- assets/: complete suite and {len(rows)} changed component source archives, with SHA-256 sidecars.
- repositories/: changed repository overlays preserving baseline files and licenses.
- notes/: English release descriptions.
- release-plan.json: exact main baselines and patch tags.

Upgrade through the verified remote KeenTool updater, or run install.sh --plan --mode upgrade and then --apply --mode upgrade in the complete suite. Read docs/INSTALL.md and docs/FIREWALL_HISTORY.md before applying this update. Verify CHECKSUMS.sha256 before use. Creating this kit does not publish or merge a release.
''')
checksum_tree(kit)
for base in [package]+[kit/'repositories'/r['repository'].split('/')[1] for r in rows]+[kit]:
 for line in (base/'CHECKSUMS.sha256').read_text().splitlines():
  digest,name=line.split('  ',1);assert hashlib.sha256((base/name).read_bytes()).hexdigest()==digest,name
print(str(kit));print('Verified suite, '+str(len(rows))+' repository overlays and kit checksums.')
