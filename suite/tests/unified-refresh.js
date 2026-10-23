const fs=require('fs'),vm=require('vm'),assert=require('assert');
const root=__dirname+'/../',source=fs.readFileSync(root+'assets/keentool-ui.js','utf8');
function element(){const classes=new Set();return {children:[],dataset:{},textContent:'',classList:{toggle(k,v){v?classes.add(k):classes.delete(k)},contains:k=>classes.has(k)},append(...x){this.children.push(...x)},prepend(...x){this.children.unshift(...x)},insertBefore(x){this.children.unshift(x)},setAttribute(k,v){this[k]=v},after(){},get lastElementChild(){return this.children.at(-1)},set innerHTML(v){this.children=[element(),element(),element()]}};}
function page(name,store={},blocked=false){
 const created=[],timers=new Map(),listeners={};let serial=0;
 const body=element();body.dataset.ktPage=name;
 const context={document:{body,hidden:false,createElement(){const e=element();created.push(e);return e},querySelector:()=>null,querySelectorAll:()=>[],getElementById:()=>null},window:{addEventListener:(name,cb)=>listeners[name]=cb},localStorage:{getItem:k=>{if(blocked)throw Error('Unavailable');return store[k]||null},setItem:(k,v)=>{if(blocked)throw Error('Unavailable');store[k]=v}},Date,Number,BigInt,console,setTimeout:(cb,ms)=>{if(!ms){cb();return 0;}const id=++serial;timers.set(id,{cb,ms});return id},clearTimeout:id=>timers.delete(id),setInterval:()=>0};
 vm.createContext(context);vm.runInContext(source,context);
 const select=created.find(e=>e.id==='kt_refresh_rate'),button=created.find(e=>e.textContent==='Refresh now');
 return {context,created,timers,listeners,select,button,async fire(){assert.equal(timers.size,1);const [id,timer]=[...timers][0];timers.delete(id);await timer.cb();}};
}
(async()=>{
 const store={},p=page('home',store);let calls=[];
 p.context.window.ktRefreshPage=async options=>calls.push(options.manual);
 assert.equal(p.select.value,'60000');assert.deepEqual(p.select.children.map(e=>e.value),['0','30000','60000','300000']);
 await p.fire();assert.deepEqual(calls,[false]);assert.equal(p.timers.size,1);
 p.select.value='0';p.select.onchange();assert.equal(p.timers.size,0);await p.button.onclick();assert.deepEqual(calls,[false,true]);assert.equal(p.timers.size,0);
 p.select.value='30000';p.select.onchange();assert.equal(store.kt_refresh_rate,'30000');
 const next=page('ping',store);assert.equal(next.select.value,'30000');
 p.context.document.hidden=true;await p.fire();assert.equal(calls.length,2);p.context.document.hidden=false;
 let finish;p.context.window.ktRefreshPage=()=>new Promise(resolve=>finish=resolve);
 const running=p.button.onclick();assert.equal(p.button.disabled,true);assert.equal(p.timers.size,0);await p.button.onclick();
 p.select.value='0';p.select.onchange();finish();await running;assert.equal(p.timers.size,0);assert.equal(p.button.disabled,false);
 p.listeners.storage({key:'kt_refresh_rate',newValue:'300000'});assert.equal(p.select.value,'300000');assert.equal(p.timers.size,1);
 p.context.window.ktRefreshPage=async()=>{throw Error('Network error')};await p.fire();assert(p.created.some(e=>e.textContent==='Refresh failed'));assert.equal(p.timers.size,1);
 const restricted=page('security',{},true);restricted.select.value='0';restricted.select.onchange();assert.equal(restricted.timers.size,0);
 const invalid=page('settings',{kt_refresh_rate:'1000'});assert.equal(invalid.select.value,'60000');
 // Security age is compared to the slower configured producer/browser cadence.
 const fresh=page('security',{'kt_refresh_rate':'300000'}),now=1800000000000;
 fresh.context.Date=class extends Date{static now(){return now;}};
 const age=(seconds,interval)=>fresh.context.window.getKTSecurityFreshness(now/1000-seconds,interval);
 assert.equal(age(240,60).stale,false);assert.equal(age(300,60).stale,false);assert.equal(age(301,60).stale,true);
 assert.equal(age(600,900).stale,false);assert.equal(age(901,900).stale,true);
 fresh.context.window.KT_SECURITY_DATA={updated:now/1000-240,monitorInterval:60,status:'ready'};fresh.context.window.updateKTDataState();
 const indicator=fresh.created.find(e=>e.className==='kt-data-state');assert.equal(indicator.dataset.state,'ready');
 fresh.select.value='30000';fresh.select.onchange();assert.equal(indicator.dataset.state,'stale');
 fresh.select.value='0';fresh.select.onchange();assert.equal(age(59,60).stale,false);assert.equal(age(61,60).stale,true);
 assert.equal(age(10000,undefined).stale,false);assert.equal(age(10000,undefined).limit,null);
 fresh.listeners.storage({key:'kt_refresh_rate',newValue:'300000'});assert.equal(indicator.dataset.state,'ready');
 assert.equal(age(-10,60).age,0);
 // Execute the real Traffic and Ping adapters; neither reloads the document.
 const traffic=fs.readFileSync(root+'projects/Traffic_manager/Script/traffic_manager.sh','utf8');
 const adapter=traffic.slice(traffic.indexOf('        window.ktRefreshPage='),traffic.indexOf('        window.onload = function()'));
 const fetched=[],evaluated=[],rendered=[];const trafficContext={window:{TRAFFIC_DATA:{ppp0:{},'eth.2':{}},eval:text=>evaluated.push(text)},document:{getElementById:()=>({value:'eth.2'}),querySelectorAll:()=>[{dataset:{iface:'ppp0'}},{dataset:{iface:'eth.2'}}]},fetch:async url=>{fetched.push(url);return {ok:true,text:async()=>url}},renderData:iface=>rendered.push(iface),Date,Promise,Error,encodeURIComponent};
 vm.createContext(trafficContext);vm.runInContext(adapter,trafficContext);await trafficContext.window.ktRefreshPage();assert.equal(evaluated.length,2);assert.deepEqual(rendered,['eth.2']);assert(fetched.some(url=>url.startsWith('eth.2_data.js')));
 trafficContext.fetch=async()=>({ok:false});await assert.rejects(()=>trafficContext.window.ktRefreshPage());assert.equal(evaluated.length,2);
 const ping=fs.readFileSync(root+'projects/keenetic-pingtool/scripts/pingtool.sh','utf8');
 const pingAdapter=ping.slice(ping.indexOf('        window.ktRefreshPage='),ping.indexOf("        document.getElementById('show_peaks').checked ="));let renders=0,evals=0;
 const pingContext={window:{eval(){evals++}},fetch:async()=>({ok:true,text:async()=>'{data}'}),render:()=>renders++,Date,Error};vm.createContext(pingContext);vm.runInContext(pingAdapter,pingContext);await pingContext.window.ktRefreshPage();assert.equal(renders,1);assert.equal(evals,1);

 const chartCode=ping.slice(ping.indexOf('            const createChart ='),ping.indexOf('            const isDark ='));
 const chart={options:{scales:{x:{min:10,max:20},y:{type:'logarithmic'}}},update(mode){this.updated=mode}};const savedOptions=chart.options;
 const chartContext={document:{getElementById:()=>({checked:true})},Chart:class{constructor(){throw Error('Existing chart was replaced')}static getChart(){return chart}},commonOptions:{}};
 vm.createContext(chartContext);vm.runInContext(chartCode+"createChart('c_p4',[{x:1,y:2,peak:3}], '#0097dc');",chartContext);
 assert.equal(chart.options,savedOptions);assert.equal(chart.options.scales.y.type,'logarithmic');assert.equal(chart.options.scales.x.min,10);assert.equal(chart.data.datasets.length,2);assert.equal(chart.updated,'none');
 for(const rel of ['projects/KeenTool/index.html','projects/keenetic-firewall/www/index.html','projects/keenetic-pingtool/scripts/pingtool.sh']){const text=fs.readFileSync(root+rel,'utf8');assert(!text.includes('id="refresh_timer"'));assert(!text.includes('changeRefreshRate'));assert(text.includes('window.ktRefreshPage='));}
 assert(!fs.readFileSync(root+'assets/keentool-security.js','utf8').includes('},60000)'));
 console.log('PASS: shared cadence/default/Off/manual, navigation persistence, storage synchronization, hidden tabs, overlap prevention, slow refresh with Off, recovery after errors, blocked storage, real Ping/Traffic adapters and removal of old page timers.');
})().catch(error=>{console.error(error);process.exitCode=1});
