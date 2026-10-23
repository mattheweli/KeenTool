from pathlib import Path
import subprocess,tempfile,os,json
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as td:
 p=Path(td);out=p/'web';out.mkdir();(out/'chart.js').write_text('// fixture')
 vn=p/'vnstat';vn.write_text('#!/usr/bin/env python3\nimport sys,os\nfrom pathlib import Path\nif "--json" in sys.argv:\n print(Path(os.environ["PAYLOAD"]).read_text());sys.exit(int(os.environ.get("EXPORT_RC","0")))\n');vn.chmod(0o755)
 php=p/'php';php.write_text('#!/usr/bin/env python3\nimport json,sys\ntry:\n d=json.load(sys.stdin);sys.exit(0 if isinstance(d,dict) and isinstance(d.get("interfaces"),list) else 1)\nexcept ValueError:sys.exit(1)\n');php.chmod(0o755)
 payload=p/'payload';payload.write_text(json.dumps({'interfaces':[{'name':'ppp0','traffic':{}}]}))
 env=dict(os.environ,KT_COMMON=str(root/'support/common.sh'),KT_RUN_DIR=td,KT_PHP_CLI=str(php),KT_VNSTAT=str(vn),PAYLOAD=str(payload))
 def run(extra=None):return subprocess.run(['bash',str(root/'projects/Traffic_manager/Script/traffic_manager.sh'),'ppp0 eth3.835',str(out),'force'],env=dict(env,**(extra or {})),capture_output=True,text=True,preexec_fn=lambda:os.umask(0o077))
 r=run();assert r.returncode==0,r.stderr
 for name in ['ppp0_data.js','eth3.835_data.js','index.html','vnstat_index.js','chart.js']:
  assert (out/name).stat().st_mode & 0o777 == 0o644,(name,oct((out/name).stat().st_mode))
 good=(out/'ppp0_data.js').read_text();assert 'TRAFFIC_DATA["ppp0"]' in good and 'TRAFFIC_DATA["eth3.835"]' in (out/'eth3.835_data.js').read_text()
 payload.write_text('ERROR: database unavailable');r=run();assert r.returncode==0 and (out/'ppp0_data.js').read_text()==good
 payload.write_text(json.dumps({'interfaces':[]}));r=run({'EXPORT_RC':'1'});assert (out/'ppp0_data.js').read_text()==good
print('PASS: real traffic script multi-interface export, dotted interface names, malformed/nonzero export retains last-good data; JSON CLI is mocked.')
