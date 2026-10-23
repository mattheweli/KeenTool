const fs=require('fs'),vm=require('vm'),assert=require('assert');
class Element{constructor(tag='div'){this.tag=tag;this.children=[];this.style={};this.dataset={};this.value='';this.textContent='';this.classList={contains:()=>false,add(){},remove(){}};this.hidden=false;}appendChild(x){this.children.push(x);return x}replaceChildren(...x){this.children=x}closest(){return {querySelector:()=>({children:Array(4)})}}addEventListener(){}setAttribute(k,v){this[k]=v}querySelectorAll(s){return s==='tr'?this.children:[]}get firstElementChild(){return this.children[0]} }
const els={},get=id=>els[id]||(els[id]=new Element());
const snapshot={system:{time:Math.floor(Date.now()/1000),firewall:{healthy:true,enabled:true},disk:{free:104857600},web_privileges:'unprivileged detected',databases:{'firewall_stats.db':1048576},services:{ulogd:true},lists:{GeoBlock:{installed:500,new:500,delta_percent:-98,result:'installed',warning:true,time:1}},bypasses:{BYPASS_INTERFACES:'tun+'},management_networks:['10.128.1.0/24'],manual_bans:{'203.0.113.9':{expires:Math.floor(Date.now()/1000)+900,created:1}}},events:[{time:1,category:'wan',event:'<script>literal</script>',target:'ppp0',outcome:'info'}],comparisons:{day:{summary:{current:1500,previous:1000},countries:[{country:'US',current:1500,previous:1000}],ports:[{port:'443/tcp',current:1500,previous:1000}]}}};
let confirmations=0;const ctx={document:{getElementById:get,createElement:t=>new Element(t),querySelectorAll:()=>[],querySelector:()=>null},window:{},location:{hash:''},fetch:async()=>({ok:true,json:async()=>snapshot}),Date,Number,Object,JSON,Math,Promise,console,alert:m=>{throw Error(m)},setInterval(){},modalRequest:0,currentModalDownloadName:'',adminAuthenticated:false,refreshAdminAuth:async()=>{},checkFirewallStatus:async()=>{},authRequest:async(action)=>{if(action==='confirm_policy')confirmations++;return {status:'success',events:[]}},fwFetch:async()=>({json:async()=>({status:'success',ip:'203.0.113.9',lists:['KTManualBan'],matches:[{set:'KTManualBan',timeout_remaining:900,packets:7,bytes:350}],metadata:{country:'US'},counters:[{hits:7}],health:{healthy:true},rules:['fixed rule'],explanation:'List membership is not proof of a dropped packet.'})})};
vm.createContext(ctx);vm.runInContext(fs.readFileSync(__dirname+'/../assets/keentool-format.js','utf8'),ctx);vm.runInContext(fs.readFileSync(__dirname+'/../assets/keentool-security.js','utf8'),ctx);
(async()=>{
 await new Promise(resolve=>setImmediate(resolve));
 assert.equal(els.security_fw.textContent,'Rules verified');assert.equal(els.security_events.children[0].children[2].textContent,'<script>literal</script>');
 assert(els.security_comparison_note.textContent.includes('1.500'));assert(els.security_comparison_note.textContent.includes('50,0%'));
 assert.equal(els.security_country_current_heading.textContent,'Last 24h');assert.equal(els.security_port_previous_heading.textContent,'Preceding 24h');assert(els.security_comparison_periods.textContent.includes('browser local time zone'));
 snapshot.comparisons.week={seconds:604800,current_start:1000000,current_end:1604800,previous_start:395200,previous_end:1000000,summary:{current:9,previous:6},countries:[{country:'XX',current:9,previous:6}],ports:[]};els.security_compare_range.value='week';await ctx.window.loadSecurityOverview();assert.equal(els.security_country_current_heading.textContent,'Last 7 days');assert.equal(els.security_port_previous_heading.textContent,'Preceding 7 days');assert.equal(els.security_country_compare.children[0].children[0].textContent,'Unknown (XX)');assert.equal(els.security_port_compare.children[0].children[0].colSpan,4);
 els.security_compare_range.value='day';await ctx.window.loadSecurityOverview();
 snapshot.system.lists.GeoBlock6={installed:900,delta_percent:-100,result:'rejected',baseline:true,detail:'ipdeny.com (cn): HTTP 404 <literal>',time:1};snapshot.events.push({time:2,category:'blocklist',event:'GeoBlock6 update rejected',target:'GeoBlock6',outcome:'error',detail:'HTTP 404 <literal>'});await ctx.window.loadSecurityOverview();
 const failure=els.security_lists.children[1].children;assert.equal(failure[2].textContent,'Not applied');assert.equal(failure[3].textContent,'rejected');assert.equal(failure[4].textContent,'ipdeny.com (cn): HTTP 404 <literal>');assert.equal(els.security_events.children[1].children[5].textContent,'HTTP 404 <literal>');

 assert.equal(ctx.window.KT_SECURITY_DATA.updated,snapshot.system.time);assert.equal(ctx.window.KT_SECURITY_DATA.status,'ready');
 snapshot.system.disk={free:116938457088,total:200000000000};snapshot.system.databases={'firewall_stats.db':29800000};await ctx.window.loadSecurityOverview();assert.equal(els.security_disk.textContent,'116,9 GB free');assert.equal(els.security_databases.children[0].children[1].textContent,'29,8 MB');
 snapshot.system.disk={free:5,total:100};snapshot.system.latest_verified_source_backup=100;
 await ctx.window.loadSecurityOverview();
 for(const id of ['security_fw','security_disk','security_web','security_backup'])assert.equal(els[id].dataset.health,'ok',id);
 snapshot.system.firewall.healthy=false;snapshot.system.disk.free=4;snapshot.system.web_privileges='root detected';delete snapshot.system.latest_verified_source_backup;snapshot.system.latest_source_backup=100;
 await ctx.window.loadSecurityOverview();
 for(const id of ['security_fw','security_disk','security_web'])assert.equal(els[id].dataset.health,'error',id);
 assert.equal(els.security_backup.dataset.health,'unknown');
 snapshot.system.firewall={};snapshot.system.disk={};snapshot.system.web_privileges='not verified';
 await ctx.window.loadSecurityOverview();
 for(const id of ['security_fw','security_disk','security_web','security_backup'])assert.equal(els[id].dataset.health,'unknown',id);
 const originalFetch=ctx.fetch;let refreshes=0;ctx.window.updateKTDataState=()=>refreshes++;
 ctx.fetch=async()=>{throw Error('Network failure')};await ctx.window.loadSecurityOverview();
 assert.equal(refreshes,1);assert.equal(ctx.window.KT_SECURITY_DATA.status,'error');
 for(const id of ['security_fw','security_disk','security_web','security_backup']){assert.equal(els[id].dataset.health,'unknown');assert.equal(els[id].textContent,'Unavailable');}
 ctx.fetch=originalFetch;await ctx.window.loadSecurityOverview();assert.equal(refreshes,2);assert.equal(ctx.window.KT_SECURITY_DATA.status,'ready');
 const actions=els.security_manual.children[0].children[3].children;assert.equal(actions[0].textContent,'Details');assert.equal(actions[1].hidden,true);
 ctx.window.policyGuardUpdate({pending_id:'a'.repeat(48),confirm_before:Math.floor(Date.now()/1000)+120});assert.equal(els.policy_guard.hidden,false);
 await ctx.window.confirmPolicy();assert.equal(confirmations,1);assert.equal(els.policy_guard.hidden,true);
 await ctx.window.explainIP('203.0.113.9');assert(els.modalBody.innerText.includes('900s'));assert(els.modalBody.innerText.includes('List membership is not proof'));assert.equal(els.ipModal.style.display,'block');
 console.log('PASS: security snapshot/timeline render as text, period deltas, public diagnostic modal, guest unban hidden and policy confirmation lifecycle.');
})().catch(e=>{console.error(e);process.exitCode=1});

// The shared diagnostics script must not fetch the overview on the firewall page.
const noOverview={...ctx,window:{},document:{...ctx.document,getElementById:()=>null},fetch:()=>{throw Error('Unexpected overview fetch on firewall page')}};
vm.createContext(noOverview);vm.runInContext(fs.readFileSync(__dirname+'/../assets/keentool-security.js','utf8'),noOverview);
