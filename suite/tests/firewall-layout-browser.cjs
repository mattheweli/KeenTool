/* Browser regression for the shipped Firewall markup and shared stylesheet. */
const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium}=require('playwright');
(async()=>{
 const root=path.resolve(__dirname,'..');
 let html=fs.readFileSync(path.join(root,'projects/keenetic-firewall/www/index.html'),'utf8');
 const css=fs.readFileSync(path.join(root,'assets/keentool-ui.css'),'utf8');
 html=html.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,'').replace(/<link\b[^>]*>/gi,'');
 html=html.replace('</head>','<style>'+css+'</style></head>');
 const browser=await chromium.launch({headless:true}); const page=await browser.newPage();
 await page.route('**/*',r=>r.abort()); await page.setContent(html);
 await page.evaluate(()=>{
  document.querySelectorAll('body > *').forEach(e=>{if(!e.contains(document.querySelector('#view_sources')))e.remove()});
  const countRows=Array.from({length:24},(_,i)=>`<tr><td><span>${i===0?'9.999.999':7922-i}</span></td><td><a href="#">2001:db8:1234:5678:abcd:ffff:1234:5678</a><button class="kt-ip-details">Details</button><br><span class="list-badge">:6881/TCP</span><span class="list-badge">:6881/UDP</span><span class="list-badge">:51515/TCP</span><button class="list-badge port-more">(+6.028)</button></td><td class="meta">Risk: 100% - FR<br><small>very-long-organization-name.example.com</small></td></tr>`).join('');
  const portRows=Array.from({length:24},()=>`<tr><td>65535</td><td><a href="#">2001:db8:1234:5678:abcd:ffff:1234:5678</a><br><a href="#">198.51.100.200</a></td><td>9.999.999</td></tr>`).join('');
  document.querySelectorAll('.triple-grid .kt-count-first tbody').forEach(e=>e.innerHTML=countRows);
  document.querySelectorAll('.triple-grid .kt-hits-last tbody').forEach(e=>e.innerHTML=portRows);
 });
 const output=process.env.KT_BROWSER_SCREENSHOTS;
 if(output)fs.mkdirSync(output,{recursive:true});
 let checked=0;
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
    return {columns:grids.map(g=>getComputedStyle(g).gridTemplateColumns.split(' ').length),pageOverflow:document.documentElement.scrollWidth>innerWidth,panels:panels.map(e=>({height:e.clientHeight,overflow:e.scrollWidth>e.clientWidth+1,scroll:e.scrollHeight>e.clientHeight})),clipped:[...section.querySelectorAll('td')].filter(e=>e.scrollWidth>e.clientWidth+1).map(e=>e.textContent),portsIntact:[...section.querySelectorAll('.kt-hits-last td:first-child')].every(e=>getComputedStyle(e).whiteSpace==='nowrap'),sticky:[...section.querySelectorAll('th')].every(e=>getComputedStyle(e).position==='sticky'),wrapping:[...section.querySelectorAll('.meta small')].every(e=>getComputedStyle(e).whiteSpace==='normal')};
   });
   const context=JSON.stringify({width,density,period,info});
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
 await browser.close();console.log(`PASS: ${checked} rendered viewport/density/period combinations; equal-height panels, wrapping, unclipped counts, internal scrolling and sticky headers.`);
})().catch(e=>{console.error(e);process.exit(1)});
