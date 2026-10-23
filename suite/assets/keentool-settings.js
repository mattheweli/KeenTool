/* KeenTool Settings v1.0.0 — 2026-10-22. Admin-only typed forms; no configuration HTML interpolation. */
(() => {
 'use strict';
 const byId=id=>document.getElementById(id);
 let groups={},active='firewall',loading=false,pending=null,guardTimer=null,checking=false;
 const notice=text=>{byId('settings_notice').textContent=text;};
 function selectGroup(name){active=name;for(const form of byId('settings_forms').children)form.hidden=form.dataset.group!==name;for(const tab of byId('settings_tabs').children)tab.setAttribute('aria-pressed',String(tab.dataset.group===name));}
 function clearSettings(){groups={};pending=null;if(guardTimer)clearInterval(guardTimer);guardTimer=null;byId('settings_guard').hidden=true;byId('settings_forms').replaceChildren();byId('settings_tabs').replaceChildren();notice('Log in to load configuration.');}
 function setGuard(value){
  pending=value;if(guardTimer)clearInterval(guardTimer);guardTimer=null;byId('settings_guard').hidden=!pending;
  document.querySelectorAll('[data-settings-save]').forEach(button=>button.disabled=!!pending);
  if(!pending)return;
  const tick=async()=>{if(!pending)return;const remaining=Math.max(0,Number(pending.confirm_before)-Math.floor(Date.now()/1000));byId('settings_guard_text').textContent='Temporary firewall configuration · '+window.KTFormat.integer(remaining)+' seconds to confirm. If access fails, the previous configuration is restored automatically.';
   if(!remaining&&!checking){checking=true;try{const status=await authRequest('status');if(!status.pending){setGuard(null);notice('Temporary policy finished. Configuration reloaded.');await loadSettings();}}catch(e){notice(e.message);}finally{checking=false;}}
  };tick();guardTimer=setInterval(tick,1000);
 }
 const fmt=(value)=>window.KTFormat.number(value,0,3);
 function presetCaption(value,unit){
  if(unit==='seconds'&&value>0){for(const [base,label] of [[86400,'day'],[3600,'hour'],[60,'minute']])if(value%base===0)return fmt(value/base)+' '+label+(value/base===1?'':'s')+' ('+fmt(value)+' seconds)';}
  return fmt(value)+(unit?' '+unit:'');
 }

 function readField(input){
  if(input.dataset.type==='bool')return input.checked;
  if(!['int','decimal'].includes(input.dataset.type))return input.value;
  const value=input.tagName==='SELECT'?Number(input.value):window.KTFormat.parse(input.value);
  if(!Number.isFinite(value)||(input.dataset.type==='int'&&!Number.isInteger(value)))throw Error('Enter a valid '+(input.dataset.type==='int'?'whole number.':'number.'));
  if(input.dataset.min!==undefined&&value<Number(input.dataset.min)||input.dataset.max!==undefined&&value>Number(input.dataset.max))throw Error('Value outside the displayed allowed range.');
  return value;
 }
 function fieldNode(name,key,field,value){
  const numeric=['int','decimal'].includes(field.type),id=name+'__'+key;
  const outer=document.createElement('div');outer.className='settings-field';
  const text=document.createElement('label');text.textContent=field.label;text.setAttribute('for',id);
  let input;
  if(field.type==='bool'){
   outer.classList.add('settings-boolean');input=document.createElement('input');input.type='checkbox';input.checked=!!value;
   const control=document.createElement('label');control.className='settings-boolean-control';control.setAttribute('for',id);
   const caption=document.createElement('span');caption.setAttribute('aria-hidden','true');
   const updateCaption=()=>{caption.textContent=input.checked?'Enabled':'Disabled';};input.addEventListener('change',updateCaption);updateCaption();
   control.append(input,caption);outer.append(text,control);
  }else if(field.choices){
   input=document.createElement('select');for(const choice of field.choices){const option=document.createElement('option');option.value=String(choice.value);option.textContent=choice.label??String(choice.value);input.append(option);}input.value=String(value);outer.append(text,input);
  }else{
   input=document.createElement(['urls','countries','ports','networks','interfaces'].includes(field.type)?'textarea':'input');
   if(input.tagName==='INPUT')input.type='text';
   input.value=numeric?fmt(value):String(value??'');input.maxLength=2048;
   if(numeric){input.inputMode=field.type==='int'?'numeric':'decimal';input.required=true;input.placeholder=field.type==='decimal'?'1.234,56':'1.234';}
   if(input.tagName==='TEXTAREA'){input.rows=['urls','networks'].includes(field.type)?4:2;outer.classList.add('settings-wide');}
   outer.append(text);
   if(field.presets){
    const select=document.createElement('select');select.id=id+'__preset';select.setAttribute('aria-label',field.label+' preset');if(field.min!==undefined)select.setAttribute('aria-describedby',id+'__range');
    for(const preset of field.presets){const option=document.createElement('option');option.value=String(preset.value);option.textContent=preset.label??(numeric?presetCaption(preset.value,field.unit):String(preset.value));option.disabled=numeric&&(preset.value<field.min||preset.value>field.max);select.append(option);}
    const custom=document.createElement('option');custom.value='__custom';custom.textContent='Custom…';select.append(custom);
    select.value=field.presets.some(preset=>String(preset.value)===String(value))?String(value):'__custom';input.hidden=select.value!=='__custom';
    select.onchange=()=>{input.hidden=select.value!=='__custom';if(input.hidden)input.value=numeric?fmt(Number(select.value)):select.value;else input.focus?.();};outer.append(select);
   }
   outer.append(input);
  }
  input.id=id;input.dataset.key=key;input.dataset.type=field.type;input.dataset.label=field.label;
  if(field.min!==undefined)input.dataset.min=String(field.min);if(field.max!==undefined)input.dataset.max=String(field.max);
  if(field.min!==undefined&&field.max!==undefined){const hint=document.createElement('small');hint.className='settings-range';hint.id=id+'__range';input.setAttribute('aria-describedby',hint.id);hint.textContent='Allowed: '+fmt(field.min)+' – '+fmt(field.max)+(field.unit?' '+field.unit:'')+'. Default: '+fmt(field.default??value)+'.';outer.append(hint);}
  if(field.type==='decimal'){const hint=document.createElement('small');hint.textContent='Decimal comma; optional dot grouping (for example 1.234,56).';outer.append(hint);}
  if(field.help){const help=document.createElement('small');help.textContent=field.help;outer.append(help);}
  return outer;
 }
 async function saveGroup(event,name){
  event.preventDefault();if(!adminAuthenticated){notice('Administrator login required');return;}
  const group=groups[name],form=event.currentTarget,values={};
  try{for(const input of form.querySelectorAll('[data-key]')){let value;try{value=readField(input);}catch(error){input.focus?.();throw Error((input.dataset.label||input.dataset.key)+': '+error.message);}if(JSON.stringify(value)!==JSON.stringify(group.values[input.dataset.key]))values[input.dataset.key]=value;}}catch(error){notice(error.message);return;}
  if(!Object.keys(values).length){notice('No changes to save.');return;}
  const button=form.querySelector('[data-settings-save]');button.disabled=true;
  try{const result=await authRequest('settings_save',{group:name,revision:group.revision,values});notice(result.pending_id?'Firewall settings applied temporarily. Verify access, then confirm below.':result.message||'Settings saved.');await loadSettings();}
  catch(e){notice(e.message);}finally{button.disabled=!!pending;}
 }
 function renderGroups(){
  byId('settings_forms').replaceChildren();byId('settings_tabs').replaceChildren();
  for(const [name,group] of Object.entries(groups)){
   const tab=document.createElement('button');tab.type='button';tab.className='btn-action';tab.dataset.group=name;tab.textContent=group.title;tab.onclick=()=>selectGroup(name);byId('settings_tabs').append(tab);
   const panel=document.createElement('form');panel.className='settings-panel';panel.dataset.group=name;const heading=document.createElement('h2');heading.textContent=group.title;panel.append(heading);
   const note=document.createElement('p');note.className='kt-list-note';note.textContent=group.error||group.note;panel.append(note);
   if(!group.error){
    const sections=new Map();for(const [key,original] of Object.entries(group.fields)){
     const field={...original};if(name==='ping'&&key==='RETENTION_DAYS')field.min=Math.max(field.min,Number(group.values[key]));
     const section=field.section||'General';let fields=sections.get(section);
     if(!fields){const box=document.createElement('fieldset');box.className='settings-section';const legend=document.createElement('legend');legend.textContent=section;box.append(legend);fields=document.createElement('div');fields.className='settings-fields';box.append(fields);panel.append(box);sections.set(section,fields);}
     fields.append(fieldNode(name,key,field,group.values[key]));
    }

    const actions=document.createElement('div');actions.className='settings-actions';const save=document.createElement('button');save.type='submit';save.className='btn-action';save.dataset.settingsSave='';save.textContent=name==='firewall'?'Save and apply with rollback':'Save settings';actions.append(save);panel.append(actions);panel.addEventListener('submit',event=>saveGroup(event,name));}
   byId('settings_forms').append(panel);
  }selectGroup(groups[active]?active:Object.keys(groups)[0]);
 }
 async function loadSettings({preserveEdits=false}={}){
  if(!adminAuthenticated||loading)return;loading=true;
  try{const result=await authRequest('settings_get');if(!adminAuthenticated)return;if(preserveEdits&&hasUnsavedSettings()){notice('Status refreshed. Unsaved configuration changes were preserved.');return;}groups=result.groups||{};renderGroups();setGuard(result.pending||null);}
  catch(e){notice(e.message);}finally{loading=false;}
 }
 async function finishPolicy(action){if(!adminAuthenticated||!pending)return;try{await authRequest(action,{pending_id:pending.pending_id});setGuard(null);notice(action==='confirm_policy'?'Firewall configuration confirmed.':'Previous firewall configuration restored.');await loadSettings();}catch(e){notice(e.message);}}
 function hasUnsavedSettings(){
  for(const form of byId('settings_forms').children){const group=groups[form.dataset.group];if(!group)continue;
   for(const input of form.querySelectorAll('[data-key]')){try{if(JSON.stringify(readField(input))!==JSON.stringify(group.values[input.dataset.key]))return true;}catch(_){return true;}}
  }return false;
 }
 window.ktRefreshPage=async({manual=false}={})=>{
  const session=await authRequest('auth_status');adminCsrf=session.csrf;
  if(!session.authenticated){showAdminState(false);return;}
  if(!adminAuthenticated){showAdminState(true);return;}
  if(hasUnsavedSettings()){
   const status=await authRequest('status');setGuard(status.pending||null);
   if(manual)notice('Status refreshed. Unsaved configuration changes were preserved.');
  }else await loadSettings({preserveEdits:true});
 };
 byId('settings_confirm').addEventListener('click',()=>finishPolicy('confirm_policy'));byId('settings_rollback').addEventListener('click',()=>finishPolicy('rollback_policy'));
 window.loadSettings=loadSettings;window.onAdminStateChange=enabled=>{if(enabled){notice('Configuration loaded.');loadSettings();}else clearSettings();};
 if(adminAuthenticated)loadSettings();
})();
