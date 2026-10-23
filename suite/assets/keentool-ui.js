/* KeenTool shared UI v1.0.1. Presentation only; no admin or router mutations. */
(() => {
 'use strict';
 function readPreference(key,fallback){try{return localStorage.getItem(key)||fallback;}catch(_){return fallback;}}
 function writePreference(key,value){try{localStorage.setItem(key,value);}catch(_){}}
 const page=document.body.dataset.ktPage||'home';
 const names={home:'System Dashboard',traffic:'Traffic Monitor',ping:'Connection Monitor',firewall:'Firewall Monitor',security:'Security & Health',settings:'Settings'};
  const top=document.createElement('header');top.className='kt-topbar';top.innerHTML='<a class="kt-brand" href="/index.html">KEENTOOL</a><span class="kt-brand-sub">Network management</span><span class="kt-page-label">'+names[page]+'</span>';
 const nav=document.createElement('nav');nav.className='kt-nav';nav.setAttribute('aria-label','Main navigation');nav.innerHTML='<span class="kt-nav-title">Status & monitoring</span>';
 [['home','/index.html','Dashboard'],['traffic','/vnstat/index.html','Traffic Monitor'],['ping','/ping/index.html','Connection Monitor'],['firewall','/firewall/index.html','Firewall Monitor'],['security','/security/index.html','Security & Health'],['settings','/settings/index.html','Settings']].forEach(([id,href,label])=>{const a=document.createElement('a');a.href=href;const shapes={settings:'<circle cx="12" cy="12" r="4"/><path d="M12 2v3m0 14v3M2 12h3m14 0h3M5 5l2 2m10 10 2 2M5 19l2-2M17 7l2-2"/>',security:'<path d="M12 2l8 4v6c0 5-8 10-8 10S4 17 4 12V6z"/><path d="m8 12 3 3 5-6"/>',home:'<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>',traffic:'<path d="M4 20h16M7 17V9m5 8V4m5 13v-6"/>',ping:'<path d="M2 12h5l3-8 4 16 3-8h5"/>',firewall:'<path d="M12 2l8 4v6c0 5-8 10-8 10S4 17 4 12V6z"/>'};a.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true">'+shapes[id]+'</svg><span>'+label+'</span>';if(id===page)a.setAttribute('aria-current','page');nav.append(a);});
 const foot=document.createElement('div');foot.className='kt-nav-footer';foot.textContent='Entware dashboards';nav.append(foot);document.body.prepend(top,nav);
 const menuToggle=document.createElement('button');menuToggle.className='kt-menu-toggle';menuToggle.type='button';
 function applyMenuState(hidden){document.body.classList.toggle('kt-menu-hidden',hidden);menuToggle.textContent=hidden?'Show menu':'Hide menu';menuToggle.setAttribute('aria-expanded',String(!hidden));setTimeout(()=>document.querySelectorAll('canvas').forEach(c=>window.Chart?.getChart(c)?.resize?.()),0);}
 menuToggle.onclick=()=>{const hidden=!document.body.classList.contains('kt-menu-hidden');writePreference('kt_menu_hidden',hidden?'1':'0');applyMenuState(hidden);};
 top.insertBefore(menuToggle,top.lastElementChild);applyMenuState(readPreference('kt_menu_hidden','0')==='1');
 // Density affects spacing only. It never changes table data or refresh schedules.
 if(page!=='home' && document.querySelector('table')){
 const densityLabel=document.createElement('label');densityLabel.className='kt-density-control';
 const densityText=document.createElement('span');densityText.textContent='Table density';
 const densitySelect=document.createElement('select');densitySelect.className='kt-density-select';densitySelect.id='kt_table_density';
 densitySelect.setAttribute('aria-label','Table density');
 [['comfortable','Comfortable'],['compact','Compact']].forEach(([value,text])=>{const option=document.createElement('option');option.value=value;option.textContent=text;densitySelect.append(option);});
 function applyDensity(value){const density=value==='compact'?'compact':'comfortable';document.body.dataset.ktDensity=density;densitySelect.value=density;}
 const savedDensity=readPreference('kt_table_density','comfortable');
 applyDensity(savedDensity);
 densitySelect.onchange=()=>{applyDensity(densitySelect.value);writePreference('kt_table_density',densitySelect.value);};
 densityLabel.append(densityText,densitySelect);
 const densityHost=document.querySelector('.header-controls,.status-controls');
 if(densityHost)densityHost.append(densityLabel);
 else{const fallback=document.createElement('div');fallback.className='kt-chart-tools';fallback.append(densityLabel);(document.querySelector('.container')||document.body).prepend(fallback);}
 }
 // Focusable scroll containers keep wide tables accessible from the keyboard.
 document.querySelectorAll('.table-container,.table-responsive').forEach((container,index)=>{
  if(!container.querySelector('table'))return;
  container.setAttribute('tabindex','0');container.setAttribute('role','region');
  const heading=container.parentElement && container.parentElement.querySelector('.section-title,.sub-header');
  container.setAttribute('aria-label',heading ? heading.textContent.trim()+' table' : 'Scrollable data table '+(index+1));
 });
 const state=document.createElement('div');state.className='kt-data-state';state.setAttribute('role','status');state.innerHTML='<span class="kt-state-dot"></span><span></span>';
 const anchor=document.querySelector('.container')||document.body;anchor.insertBefore(state,anchor.firstChild);
 // Snapshot production and browser polling are independent; respect the slower cadence.
 let freshnessRefreshMs=60000;
 {const stored=readPreference('kt_refresh_rate','60000');if(['0','30000','60000','300000'].includes(stored))freshnessRefreshMs=Number(stored);}
 function securityFreshness(epoch,monitorInterval){
  const produced=Number(monitorInterval),browser=freshnessRefreshMs/1000;
  const producer=Number.isFinite(produced)&&produced>=30&&produced<=3600?produced:0;
  const limit=Math.max(producer,browser)||null;
  const stamp=Number(epoch),age=Number.isFinite(stamp)&&stamp>0?Math.max(0,Date.now()/1000-stamp):null;
  return {age,limit,stale:age!==null&&limit!==null&&age>limit,label:limit===null?'unavailable':limit%60===0?(limit/60)+' '+(limit===60?'minute':'minutes'):limit+' seconds'};
 }
 window.getKTSecurityFreshness=securityFreshness;
 function parseDate(s){if(!s)return null;const m=String(s).match(/^(\d{2})[/-](\d{2})[/-](\d{4})[, ]+(\d{2}):(\d{2})(?::(\d{2}))?/);return m?new Date(+m[3],+m[2]-1,+m[1],+m[4],+m[5],+(m[6]||0)):null;}
 function updateCopyrightYear(){document.querySelectorAll('[data-kt-year]').forEach(el=>{el.textContent=String(new Date().getFullYear());});}
 function updateState(){updateCopyrightYear();let stamp=null;let text='Waiting for data';
  if(page==='ping')stamp=parseDate(window.PING_DATA?.updated);
  if(page==='firewall')stamp=parseDate(window.FW_DATA?.updated);
  if(page==='traffic'){const freshness=document.getElementById('data_freshness');const epoch=Number(freshness?.dataset.epoch);if(epoch>0)stamp=new Date(epoch);else stamp=parseDate(freshness?.textContent.replace(/^Database updated:\s*/,''));text=freshness?.textContent||text;}
  if(page==='home')text='Overview · select a monitor for detailed history';
  if(page==='settings')text='Settings · configuration and policy';
  if(page==='security'){const epoch=Number(window.KT_SECURITY_DATA?.updated);if(Number.isFinite(epoch)&&epoch>0)stamp=new Date(epoch*1000);text=window.KT_SECURITY_DATA?.status==='error'?'Security data unavailable':'Waiting for security data';}
  const freshness=page==='security'?securityFreshness(window.KT_SECURITY_DATA?.updated,window.KT_SECURITY_DATA?.monitorInterval):null;
  const staleAfter=30;
  const age=stamp?(Date.now()-stamp.getTime())/60000:null;
  const stale=freshness?freshness.stale:age>staleAfter;
  state.dataset.state=stamp?(stale?'stale':'ready'):(['home','settings'].includes(page)?'ready':'missing');
  if(stamp)text=(stale?'Data older than '+(freshness?freshness.label:staleAfter+' minutes'):'Data available')+' · '+stamp.toLocaleString('en-GB')+' (router time)';
  if(page==='security'&&window.KT_SECURITY_DATA?.status==='error')state.dataset.state='error';
  state.lastElementChild.textContent=text;
  if(freshness){state.title='Snapshot interval: '+(window.KT_SECURITY_DATA?.monitorInterval||'unknown')+' seconds; browser refresh: '+(freshnessRefreshMs?freshnessRefreshMs/1000+' seconds':'Off')+'. Freshness uses the slower configured cadence.';const checked=document.getElementById('security_updated');if(stamp&&checked)checked.textContent='Checked: '+stamp.toLocaleString('en-GB')+(stale?' · snapshot older than '+freshness.label:'');}
  const dot=document.getElementById('loading_dot');if(dot?.classList.contains('active'))state.lastElementChild.textContent='Refreshing data…';
  document.querySelectorAll('#fw_drops, #fw_trap, #fw_v4, #fw_v6, #fw_vpn, #fw_geo').forEach(el=>{const raw=el.textContent.replace(/[.,]/g,'').trim();if(/^\d+$/.test(raw))el.textContent=BigInt(raw).toLocaleString('de-DE');});
 }
 window.updateKTDataState=updateState;
 updateState();setInterval(updateState,5000);
 // One persisted browser refresh cadence; router collection schedules are independent.
 const refreshControls=document.createElement('div');refreshControls.className='kt-refresh-controls';
 const refreshLabel=document.createElement('label');refreshLabel.textContent='Auto-refresh';
 const refreshSelect=document.createElement('select');refreshSelect.id='kt_refresh_rate';refreshSelect.setAttribute('aria-label','Auto-refresh interval');
 for(const [value,label] of [['0','Off'],['30000','30 seconds'],['60000','1 minute'],['300000','5 minutes']]){const option=document.createElement('option');option.value=value;option.textContent=label;refreshSelect.append(option);}
 refreshLabel.append(refreshSelect);
 const refreshButton=document.createElement('button');refreshButton.type='button';refreshButton.className='kt-button';refreshButton.textContent='Refresh now';
 const refreshNote=document.createElement('span');refreshNote.className='kt-refresh-note';refreshNote.setAttribute('role','status');
 refreshControls.append(refreshLabel,refreshButton,refreshNote);top.append(refreshControls);
 let refreshTimer=null,refreshBusy=false,refreshRate=60000;
 function scheduleRefresh(){
  if(refreshTimer!==null)clearTimeout(refreshTimer);refreshTimer=null;
  if(refreshRate>0&&!refreshBusy)refreshTimer=setTimeout(async()=>{refreshTimer=null;if(document.hidden){scheduleRefresh();return;}await runRefresh(false);},refreshRate);
 }
 async function runRefresh(manual=true){
  if(refreshBusy)return;
  refreshBusy=true;refreshButton.disabled=true;refreshNote.textContent='Refreshing…';
  if(refreshTimer!==null)clearTimeout(refreshTimer);refreshTimer=null;
  try{if(typeof window.ktRefreshPage!=='function')throw Error('Page is still loading');await window.ktRefreshPage({manual});refreshNote.textContent='';}
  catch(error){refreshNote.textContent='Refresh failed';refreshNote.title=error.message||String(error);}
  finally{refreshBusy=false;refreshButton.disabled=false;updateState();scheduleRefresh();}
 }
 function setRefreshRate(value,persist=false){
  const valid=['0','30000','60000','300000'].includes(String(value))?String(value):'60000';
  refreshRate=Number(valid);freshnessRefreshMs=refreshRate;refreshSelect.value=valid;if(persist)writePreference('kt_refresh_rate',valid);updateState();scheduleRefresh();
 }
 refreshSelect.onchange=()=>setRefreshRate(refreshSelect.value,true);refreshButton.onclick=()=>runRefresh(true);
 window.addEventListener?.('storage',event=>{if(event.key==='kt_refresh_rate')setRefreshRate(event.newValue);});
 window.KTRefresh={run:runRefresh};setRefreshRate(readPreference('kt_refresh_rate','60000'));
 const canvases=document.querySelectorAll('canvas');
 if(canvases.length){const tools=document.createElement('div');tools.className='kt-chart-tools';const button=document.createElement('button');button.className='kt-button';button.textContent='Reset chart zoom';button.onclick=()=>canvases.forEach(c=>window.Chart?.getChart(c)?.resetZoom?.());const note=document.createElement('span');note.textContent=page==='ping'?'Drag to zoom · charts show time-bucket averages':'Use chart tooltips to inspect values';tools.append(button,note);(document.querySelector('.section-header,.main-tabs,.tabs')||state).after(tools);}
})();
