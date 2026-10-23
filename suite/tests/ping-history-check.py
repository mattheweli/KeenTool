from pathlib import Path
import sqlite3,tempfile,subprocess,os,json
b=Path(__file__).resolve().parents[1];s=(b/'projects/keenetic-pingtool/scripts/pingtool.sh').read_text()
with tempfile.TemporaryDirectory() as td:
 t=Path(td);db=t/'test.db';c=sqlite3.connect(db);now=2000000000
 for table in ['stats','stats_v6']:
  c.execute(f'create table {table}(timestamp integer,ping real,jitter real,loss real)')
  c.executemany(f'insert into {table} values(?,?,?,?)',[(now-i*60,10+i%3,2,i%7) for i in range(70000)])
 c.commit();c.close()
 shim=t/'sqlite3';shim.write_text('''#!/usr/bin/env python3
import sqlite3,sys
for row in sqlite3.connect(sys.argv[1]).execute(sys.argv[2]):print('|'.join('' if x is None else str(x) for x in row))
''');shim.chmod(0o755)
 code=s[s.index('history_json()'):s.index('mv "$DATA_TMP" "$DATA_JS"')+len('mv "$DATA_TMP" "$DATA_JS"')]
 pre='umask 077;DATA_JS="$2";DB_FILE="$1";DATA_TMP="$2.tmp";NOW=2000000000;MAX_DISPLAY_POINTS=2000;ENABLE_IPV6=true;AVG_PING=10;JITTER=2;LOSS=0;AVG_PING_V6=NULL;JITTER_V6=NULL;LOSS_V6=100;\n'
 r=subprocess.run(['bash','-c',pre+code,'check',str(db),str(t/'data.js')],env={**os.environ,'PATH':str(t)+':'+os.environ['PATH']},capture_output=True,text=True)
 assert r.returncode==0,r.stderr
 assert (t/'data.js').stat().st_mode & 0o777 == 0o644
 js=(t/'data.js').read_text();(t/'check.js').write_text('global.window={};'+js+';console.log(JSON.stringify(window.PING_DATA));')
 d=json.loads(subprocess.check_output(['node',str(t/'check.js')],text=True))
 assert d['periods']['v4']['1']['samples']==61
 assert d['periods']['v4']['24']['samples']==1441
 assert d['periods']['v4']['max']['samples']==70000
 assert len(d['history']['v4_max'])<=2000
 assert len(d['history']['v4_7'])<=2000
 assert d['current']['v6']['ping'] is None
 assert abs(d['periods']['v4']['1']['p']-sum(10+i%3 for i in range(61))/61)<1e-10
 html=s.split("cat <<'HTML_EOF'",1)[1].split('HTML_EOF',1)[0]
 inline=html.split('<script>')[-1].split('</script>')[0]
 (t/'frontend.js').write_text('''const vm=require('vm'),assert=require('assert');const charts=[];const elems={};const store={ping_history_range:'1'};
const document={getElementById(id){return elems[id]||(elems[id]={value:id==='history_range'?'24':'',style:{},innerText:''});},querySelectorAll(){return [];}};
const ctx={document,window:{PING_DATA:__DATA__,matchMedia(){return {matches:false}}},localStorage:{getItem:k=>store[k]||null,setItem:(k,v)=>store[k]=v},Chart:class{constructor(el,config){charts.push(config)}static getChart(){return null;}},setInterval(){return 1},clearInterval(){},location:{reload(){}}};
vm.createContext(ctx);vm.runInContext(__FORMAT__,ctx);vm.runInContext(__CODE__,ctx);
assert.equal(elems.history_range.value,'1');assert(elems.countV4.innerText.includes('61 samples'));
elems.history_range.value='max';vm.runInContext('changeHistory()',ctx);
assert.equal(store.ping_history_range,'max');
assert(elems.ping_coverage.textContent.includes('IPv4 coverage:'));
assert(elems.ping_coverage.textContent.includes('\\nIPv6 coverage:'));
ctx.window.PING_DATA.periods.v6.max.first=1900000000;ctx.window.PING_DATA.periods.v6.max.last=1900000060;
vm.runInContext('render()',ctx);
const expectedV6=new Date(1900000000*1000).toLocaleString('en-GB');
assert(elems.ping_coverage.textContent.includes('IPv6 coverage: '+expectedV6));
ctx.window.PING_DATA.periods.v6.max.samples=0;vm.runInContext('render()',ctx);
assert(elems.ping_coverage.textContent.includes('IPv6 coverage: No samples in this period'));
ctx.window.PING_DATA.config.ipv6=false;vm.runInContext('render()',ctx);
assert(!elems.ping_coverage.textContent.includes('IPv6'));
ctx.window.PING_DATA.config.ipv6=true;ctx.window.PING_DATA.periods.v6.max.samples=70000;
elems.show_peaks.checked=true;vm.runInContext('changeHistory()',ctx);assert.equal(charts.at(-6).data.datasets.length,2);assert.equal(charts.at(-5).data.datasets.length,1);assert.equal(charts.at(-4).data.datasets.length,2);assert(elems.countV4.innerText.includes('70.000 samples'));
'''.replace('__DATA__',json.dumps(d)).replace('__CODE__',json.dumps(inline)).replace('__FORMAT__',json.dumps((b/'assets/keentool-format.js').read_text())))
 subprocess.run(['node',str(t/'frontend.js')],check=True)
print('PASS: 1h/24h/MAX boundaries, 70000 samples retained, bounded charts, raw weighted averages, NULL latency, browser preference and range changes.')
