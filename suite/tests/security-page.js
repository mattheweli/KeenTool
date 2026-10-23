const fs=require('fs'),vm=require('vm'),assert=require('assert');
const root=__dirname+'/../',html=fs.readFileSync(root+'projects/security/index.html','utf8'),fw=fs.readFileSync(root+'projects/keenetic-firewall/www/index.html','utf8');
assert(html.includes('data-kt-page="security"'));assert(!fw.includes('id="view_security"'));assert(!fw.includes('data-kt-security-tab'));
const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);assert.equal(new Set(ids).size,ids.length);
const elements=Object.fromEntries(ids.map(id=>[id,{id,hidden:false,value:'',textContent:'',style:{},listeners:{},addEventListener(type,cb){this.listeners[type]=cb},replaceChildren(){this.textContent=''},showModal(){this.open=true},close(){this.open=false},focus(){}}]));
const calls=[],admin=[{hidden:true}],alerts=[];let authenticated=false;
const ctx={window:{},document:{getElementById:id=>elements[id],querySelectorAll:()=>admin,addEventListener(){}},location:{protocol:'https:',href:'https://router.test:8080/security/index.html',origin:'https://router.test:8080'},URL,JSON,Error,console,alert:m=>alerts.push(m),confirm:()=>true,fetch:async(url,options)=>{
 calls.push({url:String(url),options});const action=options.body?JSON.parse(options.body).action:new URL(String(url),'https://router.test:8080').searchParams.get('action');
 if(action==='login')authenticated=true;if(action==='logout')authenticated=false;
 return {ok:true,status:200,json:async()=>({status:'success',authenticated,csrf:'session-csrf',remaining:[]})};
}};
vm.createContext(ctx);vm.runInContext(fs.readFileSync(root+'assets/keentool-security-page.js','utf8'),ctx);
(async()=>{
 await new Promise(resolve=>setImmediate(resolve));assert.equal(admin[0].hidden,true);
 await ctx.unbanIP('203.0.113.5');assert(!calls.some(c=>c.options.body?.includes('"action":"unban"')));assert(elements.admin_dialog.open);
 elements.admin_password.value='test password';await elements.admin_login_form.listeners.submit({preventDefault(){},submitter:{}});assert.equal(admin[0].hidden,false);assert.equal(elements.admin_password.value,'');
 await ctx.unbanIP('203.0.113.5');const write=calls.find(c=>c.options.body?.includes('"action":"unban"'));assert(write);assert.equal(write.url,'/firewall/firewall_api.php');assert.equal(write.options.headers['X-KT-CSRF'],'session-csrf');
 await ctx.fwFetch('/firewall/firewall_api.php?action=lookup&ip=203.0.113.5');await assert.rejects(()=>ctx.fwFetch('https://other.test/firewall/firewall_api.php'));
 await ctx.adminLogout();assert.equal(admin[0].hidden,true);assert.equal(elements.security_audit.textContent,'');
 assert(fs.readFileSync(root+'assets/keentool-security.js','utf8').includes("fetch('/firewall/security-data.json?t='"));
 delete elements.ipModal;ctx.closeModal();
 console.log('PASS: standalone Security page, no duplicate IDs/firewall tab, guest write gate, login/logout, absolute same-origin API and CSRF-protected unban.');
})().catch(e=>{console.error(e);process.exitCode=1});
