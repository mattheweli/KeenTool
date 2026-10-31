/* Browser regression for the shipped Firewall markup and shared stylesheet. */
const fs=require('fs'),path=require('path'),assert=require('assert'),os=require('os');
const {spawnSync}=require('child_process');
const {chromium}=require('playwright');
(async()=>{
 const root=path.resolve(__dirname,'..');
 let html=fs.readFileSync(process.env.KT_LAYOUT_HTML||path.join(root,'projects/keenetic-firewall/www/index.html'),'utf8');
 const css=fs.readFileSync(path.join(root,'assets/keentool-ui.css'),'utf8');
 html=html.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,'').replace(/<link\b[^>]*>/gi,'');
 html=html.replace('</head>','<style>'+css+'</style></head>');
 // Execute the exact AWK exporter used by firewall_stats.sh, without running the router script.
 const stats=fs.readFileSync(path.join(root,'projects/keenetic-firewall/scripts/firewall_stats.sh'),'utf8');
 const marker=stats.indexOf('    cat "$KT_WORKDIR/render/port_$ID_PREFIX.rows" | awk');
 assert(marker>=0,'Port exporter not found');
 const begin=stats.indexOf('\n    {',marker)+1,end=stats.indexOf("}'\n}",begin)+1;
 assert(begin>0&&end>begin,'Port exporter boundaries not found');
 const listdir=fs.mkdtempSync(path.join(os.tmpdir(),'kt-port-layout-'));
 let generatedPortRows;
 try{
  const records=Array.from({length:24},(_,i)=>`${['65535/udp','55422/tcp','6881/udp','80/tcp'][i%4]}|198.51.100.200,203.0.113.20,2001:db8:1234:5678:abcd:ffff:1234:5678,192.0.2.99|${i===0?'9999999':23773-i}`).join('\n')+'\n';
  const result=spawnSync('awk',['-F|','-v','listdir='+listdir,'-v','prefix=fixture','-v',"q='",stats.slice(begin,end)],{input:records,encoding:'utf8'});
  assert.equal(result.status,0,result.stderr);generatedPortRows=result.stdout;
  assert(generatedPortRows.includes(':65535/udp')&&generatedPortRows.includes('(+1 others)'),'Expected real port badge and attacker-list control');
 }finally{fs.rmSync(listdir,{recursive:true,force:true});}
 const browser=await chromium.launch({headless:true}); const page=await browser.newPage();
 await page.route('**/*',r=>r.abort()); await page.setContent(html);
 await page.evaluate(generatedPortRows=>{
  document.querySelectorAll('body > *').forEach(e=>{if(!e.contains(document.querySelector('#view_sources')))e.remove()});
  const countRows=Array.from({length:24},(_,i)=>`<tr><td><span>${i===0?'9.999.999':7922-i}</span></td><td><a href="#">2001:db8:1234:5678:abcd:ffff:1234:5678</a><button class="kt-ip-details">Details</button><br><span class="list-badge">:6881/TCP</span><span class="list-badge">:6881/UDP</span><span class="list-badge">:51515/TCP</span><button class="list-badge port-more">(+6.028)</button></td><td class="meta">Risk: 100% - FR<br><small>very-long-organization-name.example.com</small></td></tr>`).join('');
  const portRows=generatedPortRows;
  document.querySelectorAll('.triple-grid .kt-count-first tbody').forEach(e=>e.innerHTML=countRows);
  document.querySelectorAll('.triple-grid .kt-hits-last tbody').forEach(e=>e.innerHTML=portRows);
 },generatedPortRows);
 const output=process.env.KT_BROWSER_SCREENSHOTS;
 if(output)fs.mkdirSync(output,{recursive:true});
 let checked=0,overlapObserved=false;
 for(const width of [1920,1466,1280,1200,1024,800,768,390]){
  await page.setViewportSize({width,height:960});
  for(const density of ['comfortable','compact'])for(const period of ['24h','30d','1y','all']){
   await page.evaluate(({density,period})=>{
    document.body.dataset.ktDensity=density;
    document.querySelectorAll('.tab-content').forEach(e=>e.classList.toggle('active',e.id==='tab_'+period));
   },{density,period});
   const info=await page.evaluate(()=>{
    const section=document.querySelector('.tab-content.active');
    const grids=[...section.querySelectorAll('.triple-grid')];
    const panels=[...section.querySelectorAll('.table-container')];
    const overlaps=[...section.querySelectorAll('.kt-hits-last td:first-child .list-badge')].filter(b=>{const r=b.getBoundingClientRect(),c=b.closest('td').getBoundingClientRect();return r.right>c.right+0.5||r.left<c.left-0.5;}).map(b=>b.textContent);
    return {overlaps,columns:grids.map(g=>getComputedStyle(g).gridTemplateColumns.split(' ').length),pageOverflow:document.documentElement.scrollWidth>innerWidth,panels:panels.map(e=>({height:e.clientHeight,overflow:e.scrollWidth>e.clientWidth+1,scroll:e.scrollHeight>e.clientHeight})),clipped:[...section.querySelectorAll('td')].filter(e=>e.scrollWidth>e.clientWidth+1).map(e=>e.textContent),portsIntact:[...section.querySelectorAll('.kt-hits-last td:first-child')].every(e=>getComputedStyle(e).whiteSpace==='nowrap'),sticky:[...section.querySelectorAll('th')].every(e=>getComputedStyle(e).position==='sticky'),wrapping:[...section.querySelectorAll('.meta small')].every(e=>getComputedStyle(e).whiteSpace==='normal')};
   });
   const context=JSON.stringify({width,density,period,info});
   if(process.env.KT_LAYOUT_EXPECT_OVERLAP==='1'){
    overlapObserved=overlapObserved||info.overlaps.length>0;
    continue;
   }
   assert.equal(info.overlaps.length,0,context);
   assert(info.columns.every(n=>n===(width>=1200?3:width>=800?2:1)),context);
   assert(!info.pageOverflow,context);assert(info.panels.every(p=>p.scroll&&!p.overflow),context);
   assert.equal(new Set(info.panels.map(p=>p.height)).size,1,context);
   assert.equal(info.clipped.length,0,context);assert(info.sticky&&info.wrapping&&info.portsIntact,context);
   const scrolled=await page.evaluate(()=>{
    const panel=document.querySelector('.tab-content.active .table-container'),head=panel.querySelector('th');
    const before=head.getBoundingClientRect().top;panel.scrollTop=250;
    return {moved:panel.scrollTop>0,delta:Math.abs(head.getBoundingClientRect().top-before)};
   });
   assert(scrolled.moved&&scrolled.delta<2,JSON.stringify(scrolled));
   checked++;
   if(output&&period==='24h'&&density==='comfortable'&&[1466,390].includes(width)){
    await page.evaluate(()=>document.querySelectorAll('.table-container').forEach(e=>e.scrollTop=0));
    await page.locator('.tab-content.active').screenshot({path:path.join(output,`firewall-${width}.png`)});
   }
  }
 }
 await browser.close();
 if(process.env.KT_LAYOUT_EXPECT_OVERLAP==='1'){assert(overlapObserved,'Baseline did not reproduce the reported badge overlap');console.log('PASS: reproduced published 2.0.21 port/protocol badge overlap with actual exporter output.');return;}
 console.log(`PASS: ${checked} rendered viewport/density/period combinations; equal-height panels, wrapping, unclipped counts, internal scrolling and sticky headers.`);
})().catch(e=>{console.error(e);process.exit(1)});
