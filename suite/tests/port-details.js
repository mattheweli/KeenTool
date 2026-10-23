const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync(__dirname+'/../projects/keenetic-firewall/www/index.html','utf8');
const start=html.indexOf('        function showReadOnlyList('),end=html.indexOf('        window.onclick =',start);
const elems={},requests=[];let copied='',download='';
const ctx={window:{URL:{createObjectURL(){return 'blob:fixture'},revokeObjectURL(){}}},document:{getElementById(id){return elems[id]||(elems[id]={style:{},innerText:''})},createElement(){return{click(){download=this.download}}},body:{appendChild(){},removeChild(){}}},fetch:async url=>{requests.push(url);return {ok:true,text:async()=>Array.from({length:110},(_,i)=>(i+1)+'/tcp').join('\n')}},navigator:{clipboard:{writeText:async text=>{copied=text}}},Date,Blob,alert(){},console};
vm.createContext(ctx);vm.runInContext('let currentModalPort="";let currentModalDownloadName="";let modalRequest=0;'+html.slice(start,end),ctx);
(async()=>{
 await ctx.window.showPorts({dataset:{portList:'ipports_'+'a'.repeat(64)+'.txt',ip:'2001:db8::1'}});
 assert.equal(elems.ipModal.style.display,'block');assert.equal(elems.modalTitle.innerText,'Ports targeted on 2001:db8::1');assert.equal(elems.modalBody.innerText.split('\n').length,110);
 assert(requests[0].startsWith('lists/ipports_'));vm.runInContext('copyIPList();downloadIPList()',ctx);assert.equal(copied,elems.modalBody.innerText);assert.equal(download,'targeted_ports_2001_db8__1.txt');
 vm.runInContext('closeModal()',ctx);assert.equal(elems.ipModal.style.display,'none');
 await ctx.window.loadList('p24_53_udp.txt','53');assert.equal(elems.modalTitle.innerText,'Attackers on Port 53');vm.runInContext('downloadIPList()',ctx);assert.equal(download,'attackers_port_53.txt');
 const count=requests.length;ctx.window.showPorts({dataset:{portList:'../../secrets',ip:'fixture'}});assert.equal(requests.length,count);
 ctx.fetch=async()=>({ok:false});await ctx.window.showPorts({dataset:{portList:'ipports_'+'b'.repeat(64)+'.txt',ip:'203.0.113.1'}});assert(elems.modalBody.innerText.includes('List not found'));
 console.log('PASS: public port modal opens/loads all entries, copies/downloads/closes, IPv6 filename safe, existing attacker modal retained, path validation and fetch errors.');
})().catch(e=>{console.error(e);process.exitCode=1});
