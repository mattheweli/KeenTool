const fs=require('fs'),vm=require('vm'),assert=require('assert');
const s=fs.readFileSync(__dirname+'/../projects/keenetic-firewall/www/index.html','utf8');
const js=s.slice(s.indexOf('        let ulogdBusy'),s.indexOf('        function downloadUlogd'));
const nodes={};const node=id=>nodes[id]||(nodes[id]={value:'',checked:false,innerText:'',textContent:'',scrollTop:12,scrollHeight:300,clientHeight:100});
node('details_ulogd').open=true;node('ulogd_protocol').value='all';let calls=0;
const ctx={window:{},fetchStats:async()=>{},document:{getElementById:node},setInterval:()=>1,clearInterval:()=>{},Date,fwFetch:async()=>{calls++;return {ok:true,json:async()=>({status:'success',log:'2026-10-14 12:34:56.123456 IP 192.0.2.1.123 > 198.51.100.2.443: Flags [S]\n2026-10-14 12:34:57.123456 IP 192.0.2.2.123 > 198.51.100.3.53: UDP, length 20\n'})};}};
vm.createContext(ctx);vm.runInContext(fs.readFileSync(__dirname+'/../assets/keentool-format.js','utf8'),ctx);
vm.runInContext(js,ctx);
(async()=>{
 await vm.runInContext('fetchUlogd()',ctx);assert.equal(calls,1);assert(node('content_ulogd').textContent.includes('14/10/2026 12:34:56.123'));assert.equal(node('ulogd_filter_count').textContent,'2 / 2 lines');assert.equal(node('content_ulogd').scrollTop,12);
 node('ulogd_protocol').value='udp';vm.runInContext('filterUlogd()',ctx);assert.equal(node('ulogd_filter_count').textContent,'1 / 2 lines');assert(!node('content_ulogd').textContent.includes('Flags'));
 node('ulogd_protocol').value='tcp';node('ulogd_search').value='192.0.2.1';vm.runInContext('filterUlogd()',ctx);assert.equal(node('ulogd_filter_count').textContent,'1 / 2 lines');
 node('ulogd_search').value='<script>';vm.runInContext('filterUlogd()',ctx);assert.equal(node('content_ulogd').textContent,'No matching log entries');
 node('ulogd_pause').checked=true;await vm.runInContext('fetchUlogd()',ctx);assert.equal(calls,1);
 node('ulogd_follow').checked=true;await vm.runInContext('fetchUlogd(true)',ctx);assert.equal(calls,2);assert.equal(node('content_ulogd').scrollTop,300);
 node('details_ulogd').open=false;const count=calls;await ctx.window.ktRefreshPage();assert.equal(calls,count);node('details_ulogd').open=true;node('ulogd_pause').checked=false;await ctx.window.ktRefreshPage();assert.equal(calls,count+1);
 console.log('PASS: readable dates, search/protocol filters, text-only rendering, pause, explicit refresh and follow-tail controls.');
})().catch(e=>{console.error(e);process.exit(1)});
