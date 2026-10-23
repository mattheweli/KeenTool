const fs=require('fs'),vm=require('vm'),assert=require('assert');
const source=fs.readFileSync(__dirname+'/../assets/keentool-settings.js','utf8');const ids={};
class Element {
 constructor(tag='div'){this.tagName=tag.toUpperCase();this.children=[];this.dataset={};this.listeners={};this.hidden=false;this.disabled=false;this.checked=false;this.value='';this.textContent='';}
 set id(value){this._id=value;ids[value]=this;} get id(){return this._id;}
 append(...nodes){this.children.push(...nodes);}replaceChildren(...nodes){this.children=[...nodes];}setAttribute(k,v){this[k]=v;}addEventListener(k,v){this.listeners[k]=v;}
 set innerHTML(v){throw Error('Configuration must not be rendered as HTML');}
 querySelectorAll(selector){const out=[];for(const node of this.children){if(selector==='[data-key]'&&'key'in node.dataset||selector==='[data-settings-save]'&&'settingsSave'in node.dataset)out.push(node);out.push(...node.querySelectorAll(selector));}return out;}
 querySelector(selector){return this.querySelectorAll(selector)[0];}get classList(){return {add:name=>{this.className+=' '+name;}};}
}
for(const id of ['settings_notice','settings_guard','settings_guard_text','settings_forms','settings_tabs','settings_confirm','settings_rollback']){const node=new Element();node.id=id;}
const field=(label,type)=>({label,type,min:100,max:10000});
let pending=null,revision='a'.repeat(64),fail=false,calls=[];
const groups={firewall:{title:'Firewall',fields:{ENABLE_FIREWALL:field('Firewall enabled','bool')},values:{ENABLE_FIREWALL:true}},ping:{title:'Connection',fields:{MAX_DISPLAY_POINTS:field('Chart points','int'),PING_TARGET:field('<img src=x>','target')},values:{MAX_DISPLAY_POINTS:2000,PING_TARGET:'example.test'}},traffic:{title:'Traffic',fields:{MONTHLY_QUOTA_GB:field('Quota','decimal')},values:{MONTHLY_QUOTA_GB:500}},security:{title:'Security',fields:{email_enabled:field('Email','bool')},values:{email_enabled:true}}};
const ctx={window:{},adminCsrf:"",adminAuthenticated:false,showAdminState:active=>{ctx.adminAuthenticated=active;ctx.window.onAdminStateChange(active)},document:{getElementById:id=>ids[id],createElement:tag=>new Element(tag),querySelectorAll:selector=>ids.settings_forms.querySelectorAll(selector)},setInterval:()=>1,clearInterval(){},Date,console,authRequest:async(action,payload)=>{
 calls.push({action,payload});if(action==='auth_status')return {authenticated:ctx.adminAuthenticated,csrf:'test-csrf'};if(action==='status')return {pending};if(action==='settings_get')return {status:'success',groups:JSON.parse(JSON.stringify(Object.fromEntries(Object.entries(groups).map(([k,v])=>[k,{...v,note:'Apply safely',revision}])))),pending};
 if(action==='settings_save'){if(fail)throw Error('Configuration changed. Reload Settings before saving.');assert.equal(payload.revision,revision);Object.assign(groups[payload.group].values,payload.values);revision='b'.repeat(64);if(payload.group==='firewall')pending={pending_id:'c'.repeat(48),confirm_before:Math.floor(Date.now()/1000)+120};return {status:'success',pending_id:pending?.pending_id};}
 if(action==='confirm_policy'||action==='rollback_policy'){assert.equal(payload.pending_id,pending.pending_id);pending=null;return {status:'success'};}throw Error(action);
}};
groups.security.fields.digest_hour={label:'Daily summary time',type:'int',min:0,max:23,default:7,choices:Array.from({length:24},(_,i)=>({value:i,label:String(i).padStart(2,'0')+':00'}))};groups.security.values.digest_hour=7;
groups.ping.fields.MAX_DISPLAY_POINTS.presets=[{value:1000},{value:2000},{value:5000}];groups.ping.fields.MAX_DISPLAY_POINTS.unit='points';
vm.createContext(ctx);vm.runInContext(fs.readFileSync(__dirname+'/../assets/keentool-format.js','utf8'),ctx);vm.runInContext(source,ctx);
const flush=()=>new Promise(resolve=>setImmediate(resolve));
(async()=>{
 assert.equal(calls.length,0);assert.equal(ids.settings_forms.children.length,0);
 ctx.adminAuthenticated=true;ctx.window.onAdminStateChange(true);await flush();assert.equal(ids.settings_tabs.children.length,4);assert(ids.ping__PING_TARGET);assert.equal(ids.ping__PING_TARGET.value,'example.test');
 assert.equal(ids.security__digest_hour.tagName,'SELECT');assert.equal(ids.security__digest_hour.children.length,24);
 assert(ids.ping__MAX_DISPLAY_POINTS.hidden);ids.ping__MAX_DISPLAY_POINTS__preset.value='5000';ids.ping__MAX_DISPLAY_POINTS__preset.onchange();assert.equal(ids.ping__MAX_DISPLAY_POINTS.value,'5.000');ids.ping__MAX_DISPLAY_POINTS__preset.value='__custom';ids.ping__MAX_DISPLAY_POINTS__preset.onchange();assert(!ids.ping__MAX_DISPLAY_POINTS.hidden);
 ids.ping__MAX_DISPLAY_POINTS.value='4000';let form=ids.settings_forms.children.find(f=>f.dataset.group==='ping');await form.listeners.submit({preventDefault(){},currentTarget:form});
 const saved=calls.find(c=>c.action==='settings_save');assert.deepEqual(JSON.parse(JSON.stringify(saved.payload.values)),{MAX_DISPLAY_POINTS:4000});assert.equal(groups.ping.values.MAX_DISPLAY_POINTS,4000);

 ids.traffic__MONTHLY_QUOTA_GB.value='1.234,56';let trafficForm=ids.settings_forms.children.find(f=>f.dataset.group==='traffic');await trafficForm.listeners.submit({preventDefault(){},currentTarget:trafficForm});assert.equal(groups.traffic.values.MONTHLY_QUOTA_GB,1234.56);
 ids.security__digest_hour.value='12';let securityForm=ids.settings_forms.children.find(f=>f.dataset.group==='security');await securityForm.listeners.submit({preventDefault(){},currentTarget:securityForm});assert.equal(groups.security.values.digest_hour,12);
 const beforeInvalid=calls.length;ids.ping__MAX_DISPLAY_POINTS.value='2,5';form=ids.settings_forms.children.find(f=>f.dataset.group==='ping');await form.listeners.submit({preventDefault(){},currentTarget:form});assert.equal(calls.length,beforeInvalid);assert(ids.settings_notice.textContent.includes('whole number'));
 ids.ping__MAX_DISPLAY_POINTS.value='12.34';await form.listeners.submit({preventDefault(){},currentTarget:form});assert.equal(calls.length,beforeInvalid);assert(ids.settings_notice.textContent.includes('comma'));
 fail=true;ids.ping__MAX_DISPLAY_POINTS.value='5000';form=ids.settings_forms.children.find(f=>f.dataset.group==='ping');await form.listeners.submit({preventDefault(){},currentTarget:form});assert(ids.settings_notice.textContent.includes('Configuration changed'));assert.equal(groups.ping.values.MAX_DISPLAY_POINTS,4000);fail=false;
 ids.firewall__ENABLE_FIREWALL.checked=false;form=ids.settings_forms.children.find(f=>f.dataset.group==='firewall');await form.listeners.submit({preventDefault(){},currentTarget:form});assert(!ids.settings_guard.hidden);assert(ids.settings_forms.querySelectorAll('[data-settings-save]').every(button=>button.disabled));
 await ids.settings_confirm.listeners.click();assert(ids.settings_guard.hidden);assert(calls.some(c=>c.action==='confirm_policy'));

 const priorRequests=calls.filter(c=>c.action==='settings_get').length;
 ids.ping__MAX_DISPLAY_POINTS.value='6000';const priorInput=ids.ping__MAX_DISPLAY_POINTS;
 await ctx.window.ktRefreshPage({manual:false});assert.equal(ids.ping__MAX_DISPLAY_POINTS,priorInput);assert.equal(ids.ping__MAX_DISPLAY_POINTS.value,'6000');assert.equal(calls.filter(c=>c.action==='settings_get').length,priorRequests);
 await ctx.window.ktRefreshPage({manual:true});assert(ids.settings_notice.textContent.includes('preserved'));
 ids.ping__MAX_DISPLAY_POINTS.value=String(groups.ping.values.MAX_DISPLAY_POINTS);await ctx.window.ktRefreshPage();assert.equal(calls.filter(c=>c.action==='settings_get').length,priorRequests+1);

 const auth=ctx.authRequest;let deliver;ctx.authRequest=async(action,payload)=>action==='settings_get'?new Promise(resolve=>deliver=resolve):auth(action,payload);
 const refreshing=ctx.window.ktRefreshPage({manual:true});await flush();ids.ping__MAX_DISPLAY_POINTS.value='7000';deliver(await auth('settings_get'));await refreshing;assert.equal(ids.ping__MAX_DISPLAY_POINTS.value,'7000');ctx.authRequest=auth;
 ctx.adminAuthenticated=false;ctx.window.onAdminStateChange(false);assert.equal(ids.settings_forms.children.length,0);assert.equal(ids.settings_tabs.children.length,0);
 console.log('PASS: Settings guest gate, typed/schema-safe rendering, changed-values-only writes/revisions, conflict feedback, firewall confirmation controls and clearing private configuration on logout.');
})().catch(e=>{console.error(e);process.exitCode=1});
