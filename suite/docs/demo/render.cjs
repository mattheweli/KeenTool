/* Render real application templates with synthetic data; all browser requests are intercepted. */
const fs=require('fs'),path=require('path'),{chromium}=require('playwright');
const base=path.resolve(process.argv[2]),output=path.resolve(process.argv[3]);fs.mkdirSync(output,{recursive:true});
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.KT_DOC_BROWSER||'/usr/bin/google-chrome',headless:true,args:['--no-sandbox']});
 const context=await browser.newContext({viewport:{width:1440,height:1050},deviceScaleFactor:1,locale:'en-GB',timezoneId:'Europe/Rome',colorScheme:'light'});
 await context.addInitScript(()=>localStorage.setItem('kt_refresh_rate','300000'));
 await context.route('**/*',async route=>{
  const u=new URL(route.request().url());let rel=u.pathname.replace(/^\//,'');
  if(u.hostname!=='keentool.example'){
   if(u.href.includes('jsvectormap')&&!u.href.includes('fonts.googleapis'))rel='assets/'+(u.href.includes('world.js')?'world.js':u.pathname.endsWith('.css')?'jsvectormap.css':'jsvectormap.js');
   else return route.fulfill({status:200,body:'',contentType:'text/css'});
  }
  if(rel==='firewall/firewall_api.php'){
   const action=u.searchParams.get('action');let data={status:'success',enabled:true,healthy:true,applied:true,ipv4_ok:true,ipv6_ok:true,authenticated:false,csrf:'example-only'};
   if(action==='auth_status')data={...data,authenticated:false};
   if(action==='log_sizes')data={status:'success',logs:Object.fromEntries(['main','ulogd','vpn','proxy','scripts','wifi','dhcp'].map(id=>[id,{size:24576,available:true}]))};
   if(['systemlog','livelog','get_log'].includes(action))data={status:'success',log:'Oct 23 18:00:00 demo-router kernel: [example] Firewall rule chains verified\nOct 23 17:59:58 demo-router pppd: PPP connection established on ppp0\n',size:24576,total_bytes:24576,loaded_bytes:196,complete:true,has_more:false};
   return route.fulfill({json:data});
  }
  const file=path.join(base,rel||'index.html');if(!file.startsWith(base+path.sep)||!fs.existsSync(file))return route.fulfill({status:404,body:'Documentation fixture not found'});
  const type={'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml'}[path.extname(file)]||'text/plain';return route.fulfill({body:fs.readFileSync(file),contentType:type});
 });
 const report=[];
 for(const [name,route,ready] of [['dashboard','/index.html','#dashboard_sec_fw'],['security','/security/index.html','#security_fw'],['firewall','/firewall/index.html','#size_main'],['traffic','/vnstat/index.html','#s_td_rx'],['ping','/ping/index.html','#v4_p'],['smb-backup','/smb.html','pre']]){
  const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.clock.install({time:new Date('2026-10-23T16:00:00Z')});await page.goto('https://keentool.example'+route,{waitUntil:'networkidle'});await page.locator(ready).waitFor();await page.waitForFunction(selector=>{const text=document.querySelector(selector)?.textContent.trim();return text&&text!=='-'&&!/unavailable|not detected/i.test(text);},ready);await page.waitForTimeout(1200);
  // A visible documentation label distinguishes examples from actual router output.
  await page.evaluate(()=>{const note=document.createElement('div');note.textContent='DOCUMENTATION EXAMPLE · synthetic data';note.style.cssText='position:fixed;bottom:12px;right:16px;z-index:9999;padding:7px 12px;border:1px solid #b4cbd7;border-radius:5px;background:#fff;color:#526a78;font:12px Arial;box-shadow:0 2px 10px #0001';document.body.append(note);});
  const file=path.join(output,name+'.png');await page.screenshot({path:file,fullPage:false});report.push({name,file,errors,title:await page.title()});await page.close();
 }
 fs.writeFileSync(path.join(output,'render-report.json'),JSON.stringify(report,null,2));await browser.close();if(report.some(r=>r.errors.length)){console.error(report);process.exitCode=1;}else console.log('Rendered all six current interfaces without JavaScript errors.');
})().catch(e=>{console.error(e);process.exitCode=1});
