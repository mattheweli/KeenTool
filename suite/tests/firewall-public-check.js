const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync(__dirname+'/../projects/keenetic-firewall/www/index.html','utf8');
const panel=html.match(/<div[^>]*id="ip_control_panel"[^>]*>/)[0];assert(!/data-admin-only|\bhidden\b/.test(panel));
for(const id of ['ip_input','ip_check_button']){const tag=html.match(new RegExp('<[^>]*id="'+id+'"[^>]*>'))[0];assert(!/data-admin-only|\bhidden\b|\bdisabled\b/.test(tag),id);}
for(const id of ['manual_duration','manual_note']){const tag=html.match(new RegExp('<[^>]*id="'+id+'"[^>]*>'))[0];assert(tag.includes('data-admin-only')&&tag.includes('hidden')&&tag.includes('data-admin-write')&&tag.includes('disabled'),id);}
for(const name of ['banIP()','unbanIP(document.getElementById(\'ip_input\').value)']){
 const tag=html.split('\n').find(l=>l.includes('onclick="'+name+'"'));assert(tag.includes('data-admin-only')&&tag.includes('hidden')&&tag.includes('disabled'),name);
}
class Element{constructor(){this.value='';this.textContent='';this.hidden=true;this.disabled=true;this.listeners={};this.classList={toggle(){}};}addEventListener(k,f){this.listeners[k]=f;}focus(){this.focused=true;}}
const ids=['ip_input','ip_status_result','manual_duration','manual_note','ban','unban','admin_state','admin_login_button','admin_logout_button','security_audit'];
const nodes=Object.fromEntries(ids.map(id=>[id,new Element()])),privateFields=['manual_duration','manual_note','ban','unban'].map(id=>nodes[id]);
const calls=[],explained=[];let authRefreshes=0,loginPrompts=0,active=false;
const ctx={window:{},document:{getElementById:id=>nodes[id],body:{classList:{toggle(){}}},querySelectorAll:s=>s==='[data-admin-only]'||s==='[data-admin-write]'?privateFields:[]},URL,location:{href:'https://router.test:8080/firewall/index.html'},Error,console,syncQuickUnban(){},fetch:async(url,options)=>{calls.push({url:String(url),options});return {ok:true,status:200,json:async()=>({status:'success',lists:[]})};},openAdminLogin:async()=>{loginPrompts++;}};
vm.createContext(ctx);
ctx.refreshAdminAuth=async()=>{authRefreshes++;vm.runInContext('adminCsrf="fixture-csrf";showAdminState('+active+');',ctx);};
const lookup=html.slice(html.indexOf('        async function lookupIP()'),html.indexOf("        let adminCsrf ="));
const state=html.slice(html.indexOf('        function showAdminState('),html.indexOf('        async function authRequest('));
const transport=html.slice(html.indexOf('        async function fwFetch('),html.indexOf('        async function checkedAction('));
vm.runInContext("let adminCsrf='',adminAuthenticated=false;\n"+lookup+state+transport,ctx);
ctx.window.explainIP=async ip=>{explained.push(ip);return ctx.fwFetch('/firewall/firewall_api.php?action=lookup&ip='+encodeURIComponent(ip));};
(async()=>{
 nodes.ip_input.value='203.0.113.9';nodes.manual_note.value='private note';vm.runInContext('showAdminState(false)',ctx);
 assert.equal(nodes.ip_input.value,'203.0.113.9');assert.equal(nodes.manual_note.value,'');assert(privateFields.every(e=>e.hidden&&e.disabled));
 for(const ip of ['203.0.113.9','198.51.100.0/24','2001:db8::9','2001:db8::/64']){
  nodes.ip_input.value=' '+ip+' ';await ctx.lookupIP();assert.equal(explained.at(-1),ip);assert.equal(new URL(calls.at(-1).url).searchParams.get('ip'),ip);
  assert.equal(calls.at(-1).options.method,undefined);assert.equal(calls.at(-1).options.headers['X-KT-CSRF'],undefined);
 }
 assert.equal(authRefreshes,0);assert.equal(loginPrompts,0);
 let prevented=false;nodes.ip_input.value='203.0.113.10';nodes.ip_input.listeners.keydown({key:'Enter',preventDefault(){prevented=true;}});await new Promise(r=>setImmediate(r));assert(prevented);assert.equal(explained.at(-1),'203.0.113.10');
 const before=calls.length;nodes.ip_input.value=' ';await ctx.lookupIP();assert.equal(calls.length,before);assert(nodes.ip_input.focused);assert(nodes.ip_status_result.textContent.includes('Enter an IPv4'));
 nodes.ip_input.value='2001:db8::5';vm.runInContext('showAdminState(false)',ctx);assert.equal(nodes.ip_input.value,'2001:db8::5');
 await assert.rejects(()=>ctx.fwFetch('firewall_api.php?action=unban&ip=203.0.113.9'),/Admin login/);assert.equal(loginPrompts,1);assert.equal(calls.length,before);
 active=true;await ctx.refreshAdminAuth();assert(privateFields.every(e=>!e.hidden&&!e.disabled));
 await ctx.fwFetch('firewall_api.php?action=unban&ip=203.0.113.9');const write=calls.at(-1);assert.equal(write.options.method,'POST');assert.equal(write.options.headers['X-KT-CSRF'],'fixture-csrf');assert.equal(JSON.parse(write.options.body).action,'unban');
 active=false;await ctx.refreshAdminAuth();assert(privateFields.every(e=>e.hidden&&e.disabled));assert.equal(nodes.ip_input.value,'2001:db8::5');
 console.log('PASS: guest IPv4/IPv6/CIDR Check and Enter, input preserved across auth refresh/logout, private fields hidden/disabled and CSRF-protected admin-only writes.');
})().catch(e=>{console.error(e);process.exitCode=1});
