const fs=require('fs'),vm=require('vm'),assert=require('assert');
const s=fs.readFileSync(__dirname+'/../projects/keenetic-firewall/www/index.html','utf8');
const code=s.slice(s.indexOf('        function setFirewallIndicator'),s.indexOf('        async function checkFirewallStatus'));
let on=false;const label={textContent:''};const ctx={document:{getElementById:id=>id==='fw_rules_led'?{classList:{toggle:(key,value)=>on=value}}:label}};vm.createContext(ctx);vm.runInContext(code,ctx);
vm.runInContext('setFirewallIndicator(true,true)',ctx);assert(on);assert.equal(label.textContent,'Enabled · rules verified');
for(const args of ['true,false','false,true','false,false','true,true,false']){vm.runInContext('setFirewallIndicator('+args+')',ctx);assert(!on);}
const formats=s.slice(s.indexOf('        function formatFirewallCounts'),s.indexOf('        function showAdminState'));
const counts=[{textContent:'12345678'},{textContent:'9.876.543'},{textContent:'9007199254740993'}],cell={querySelector:()=>({textContent:'54321'})};
const history={textContent:'+1234567'};const fmtCtx={window:{},document:{querySelectorAll:q=>q.startsWith('.grid')?counts:q==='td.num'?[history]:q==='.port-more'?[]:[cell]}};vm.createContext(fmtCtx);vm.runInContext(fs.readFileSync(__dirname+'/../assets/keentool-format.js','utf8'),fmtCtx);vm.runInContext(formats,fmtCtx);vm.runInContext('formatFirewallCounts()',fmtCtx);
assert.equal(history.textContent,'+1.234.567');assert.equal(counts[0].textContent,'12.345.678');assert.equal(counts[1].textContent,'9.876.543');assert.equal(counts[2].textContent,'9.007.199.254.740.993');assert(s.includes('FW Enable:'));
console.log('PASS: green only for enabled/linked rules, off on failure/disabled, dot grouping without precision loss.');
