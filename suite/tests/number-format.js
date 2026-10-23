const fs=require('fs'),vm=require('vm'),assert=require('assert');
const root=__dirname+'/../',source=fs.readFileSync(root+'assets/keentool-format.js','utf8'),ctx={window:{}};vm.createContext(ctx);vm.runInContext(source,ctx);const f=ctx.window.KTFormat;
assert.equal(f.number(1234.56,2,2),'1.234,56');assert.equal(f.number(-1234.5,1,1),'-1.234,5');assert.equal(f.integer('9007199254740993'),'9.007.199.254.740.993');assert.equal(f.number('9007199254740993'),'9.007.199.254.740.993');assert.equal(f.signedInteger('+1234567'),'+1.234.567');
assert.equal(f.bytes(116938457088,1000,1),'116,9 GB');assert.equal(f.bytes(1048576,1024,2),'1 MB');assert.equal(f.scaled(1234567,1000,['bit/s','kbit/s','Mbit/s'],2),'1,23 Mbit/s');assert.equal(f.number(null),'Unavailable');assert.equal(f.bytes(0),'0 B');
for(const [text,n] of [['1.234,56',1234.56],['1234,56',1234.56],['2.000',2000],['-12,5',-12.5],['0',0]])assert.equal(f.parse(text),n);
for(const text of ['1.23','1,234.56','1..234','Infinity','','1.2.3.4','2001:db8::1'])assert.throws(()=>f.parse(text));
for(const page of ['projects/KeenTool/index.html','projects/keenetic-firewall/www/index.html','projects/security/index.html','projects/settings/index.html','projects/keenetic-pingtool/scripts/pingtool.sh','projects/Traffic_manager/Script/traffic_manager.sh']){
 const text=fs.readFileSync(root+page,'utf8');assert.equal((text.match(/src="\/assets\/keentool-format.js/g)||[]).length,1,page);assert(text.includes('<script src="/assets/keentool-format.js'));
}
const home=fs.readFileSync(root+'projects/KeenTool/index.html','utf8');assert(home.includes('class="card kt-security-overview"'));assert(!home.includes('Security &amp; System Health</a> ·'));
const nodes={},node=id=>nodes[id]||(nodes[id]={textContent:'',dataset:{}});let snapshot={system:{time:Math.floor(Date.now()/1000),firewall:{healthy:true,enabled:true},web_privileges:'unprivileged detected',disk:{free:116938457088,total:200000000000}},events:Array(1200).fill({})};
const overview={window:{KTFormat:f},document:{getElementById:node},Date,Number,Error,fetch:async()=>({ok:true,json:async()=>snapshot})};vm.createContext(overview);
vm.runInContext(home.slice(home.indexOf('        async function loadDashboardSecurity()'),home.indexOf('        let dashboardLoading=')),overview);
(async()=>{
 await overview.loadDashboardSecurity();assert.equal(node('dashboard_sec_storage').textContent,'116,9 GB');assert.equal(node('dashboard_sec_events').textContent,'1.200');assert.equal(node('dashboard_sec_fw').dataset.health,'ok');
 snapshot.system.firewall.healthy=false;snapshot.system.web_privileges='root detected';snapshot.system.disk.free=0;await overview.loadDashboardSecurity();for(const id of ['dashboard_sec_storage','dashboard_sec_fw','dashboard_sec_web'])assert.equal(node(id).dataset.health,'error');
 overview.fetch=async()=>{throw Error('Offline')};await overview.loadDashboardSecurity();assert.equal(node('dashboard_sec_storage').dataset.health,'unknown');assert.equal(node('dashboard_sec_updated').textContent,'Security data unavailable');
 console.log('PASS: 1.234,56 presentation, exact large integers, signed values, size/rate units, strict localized input, shared formatter on every page and live full-width Dashboard security states.');
})().catch(error=>{console.error(error);process.exitCode=1});
