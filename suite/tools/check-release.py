#!/usr/bin/env python3
"""Run the suite's isolated regression checks; never contact a router or SMTP server."""
from pathlib import Path
import concurrent.futures,subprocess,shutil,os,json,re
root=Path(__file__).resolve().parents[1]
if os.geteuid()!=0:raise SystemExit('Isolated installer/rollback fixtures require root; run sudo env PATH="$PATH" python3 tools/check-release.py')
runtime=Path('/tmp/keentool-security-runtime/root/usr/bin');runtime.mkdir(parents=True,exist_ok=True)
for target,choices in {'php8.3':['php8.3','php'],'php-cgi8.3':['php-cgi8.3','php-cgi'],'sqlite3':['sqlite3']}.items():
 p=runtime/target
 if not p.exists():
  binary=next((shutil.which(x) for x in choices if shutil.which(x)),None)
  if not binary:raise SystemExit('Missing test dependency: '+', '.join(choices))
  p.symlink_to(binary)
if not shutil.which('node'):raise SystemExit('Install Node.js for UI fixtures')
for folder in ['support','projects','assets']:
 for p in (root/folder).rglob('*'):
  if not p.is_file() or p.suffix=='.md':continue
  try:s=p.read_text()
  except UnicodeDecodeError:continue
  if 'class="kt-alpha"' in s or re.search(r'\b[1-4]\.0\.0a\d+\b',s):raise SystemExit('Unreleased runtime marker: '+str(p))
  if p.suffix=='.php':subprocess.run([str(runtime/'php8.3'),'-n','-l',str(p)],check=True,stdout=subprocess.DEVNULL)
  elif s.startswith('#!/opt/bin/bash'):subprocess.run(['bash','-n',str(p)],check=True)
for name in ['install.sh','rollback.sh']:subprocess.run(['bash','-n',str(root/name)],check=True)
files=sorted((root/'tests').glob('*.js'))+sorted((root/'tests').glob('*.py'))
def run(p):
 try:
  r=subprocess.run(['node' if p.suffix=='.js' else 'python3',str(p)],cwd=root,capture_output=True,text=True,timeout=150)
  return {'test':p.name,'code':r.returncode,'output':r.stdout+r.stderr}
 except Exception as e:return {'test':p.name,'code':-1,'output':str(e)}
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 for row in ex.map(run,files):
  results.append(row);print(('PASS ' if row['code']==0 else 'FAIL ')+row['test'],flush=True)
  if row['code']:print(row['output'],flush=True)
print(str(sum(r['code']==0 for r in results))+'/'+str(len(results))+' checks passed')
if os.environ.get('KT_VALIDATION_RESULTS'):Path(os.environ['KT_VALIDATION_RESULTS']).write_text(json.dumps(results,indent=2))
raise SystemExit(any(r['code']!=0 for r in results))
