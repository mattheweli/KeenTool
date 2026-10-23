const fs=require('fs'),vm=require('vm'),assert=require('assert');
const s=fs.readFileSync(__dirname+'/../projects/keenetic-firewall/www/index.html','utf8');
const js=s.slice(s.indexOf("        let adminCsrf"),s.indexOf('        async function checkedAction'));
const nodes={};const node=id=>nodes[id]||(nodes[id]={hidden:false,disabled:false,value:'',textContent:'',addEventListener(t,f){this.listener=f},showModal(){this.open=true},close(){this.open=false},focus(){}});
const panels=[node('ip_control_panel')];const quick=[node('quick1')];quick[0].dataset={};
const writes=[node('write1'),node('write2')];let authenticated=false;const calls=[];
const context={URL,location:{href:'https://router:8080/firewall/',protocol:'https:'},window:{},console,alert:m=>{throw Error(m)},document:{body:{classList:{toggle(){}}},getElementById:node,querySelectorAll:selector=>selector==='[data-admin-only]'?panels:selector.startsWith('a[onclick')?quick:writes},fetch:async(url,opt)=>{
 calls.push({url:String(url),opt});let action=opt.body?JSON.parse(opt.body).action:new URL(url,'https://router/').searchParams.get('action');
 if(action==='login'){assert(!('username' in JSON.parse(opt.body)));assert.equal(opt.headers['X-KT-CSRF'],'guest-csrf');authenticated=true;return {ok:true,json:async()=>({status:'success',authenticated:true,csrf:'admin-csrf'})};}
 if(action==='logout'){assert.equal(opt.headers['X-KT-CSRF'],'admin-csrf');authenticated=false;}
 if(action==='ban'){assert.equal(opt.method,'POST');assert.equal(opt.headers['X-KT-CSRF'],'admin-csrf');assert.equal(JSON.parse(opt.body).ip,'1.2.3.4');}
 return {ok:true,status:200,json:async()=>({status:'success',authenticated,csrf:authenticated?'admin-csrf':'guest-csrf'})};
}};
vm.createContext(context);vm.runInContext(js,context);
(async()=>{
 await vm.runInContext('refreshAdminAuth()',context);assert(writes.every(x=>x.disabled));assert(panels.every(x=>x.hidden));assert(quick.every(x=>x.hidden));
 await vm.runInContext('openAdminLogin()',context);assert(node('admin_dialog').open);
 node('admin_password').value='Dummy-password';await node('admin_login_form').listener({preventDefault(){},submitter:{}});
 assert(!node('admin_dialog').open);assert(writes.every(x=>!x.disabled));assert(panels.every(x=>!x.hidden));assert(quick.every(x=>!x.hidden));quick.push({...node('quick2'),dataset:{}});vm.runInContext('syncQuickUnban()',context);assert(quick.every(x=>!x.hidden));assert.equal(node('admin_password').value,'');
 await vm.runInContext("fwFetch('firewall_api.php?action=ban&ip=1.2.3.4')",context);
 await vm.runInContext('adminLogout()',context);assert(writes.every(x=>x.disabled));assert(panels.every(x=>x.hidden));assert(quick.every(x=>x.hidden));
 const readsBefore=calls.filter(x=>x.url.includes('auth_status')).length;
 await vm.runInContext("fwFetch('firewall_api.php?action=livelog&lines=1000')",context);
 assert.equal(calls.filter(x=>x.url.includes('auth_status')).length,readsBefore);
 assert(!s.includes("prompt('Firewall API token"));assert(!s.includes('autocomplete="username"'));assert(s.includes('data-admin-only hidden'));assert(s.includes('[data-admin-only][hidden]'));console.log('PASS: guest controls, login form, CSRF rotation, protected POST, logout, password-only login, IP panel visibility, no token prompt.');
})().catch(e=>{console.error(e);process.exit(1)});
