const fs=require('fs'),vm=require('vm'),assert=require('assert');
function element(){const classes=new Set();return {children:[],dataset:{},textContent:'',attributes:{},classList:{toggle(k,v){v?classes.add(k):classes.delete(k)},contains:k=>classes.has(k)},setAttribute(k,v){this.attributes[k]=v},append(...v){this.children.push(...v)},prepend(...v){this.children.unshift(...v)},insertBefore(v){this.children.unshift(v)},after(){},get lastElementChild(){return this.children.at(-1)},set innerHTML(v){this.children=[element(),element(),element()];}};}
const body=element();body.dataset.ktPage='traffic';const nodes={data_freshness:element()};nodes.data_freshness.textContent='Database updated: 14/10/2026, 12:00:00';
const created=[],store={};let resizeCount=0;
const ctx={Date,Number,Object,document:{body,createElement(){const e=element();created.push(e);return e},querySelector(){return null},querySelectorAll(s){return s==='canvas'?[{}]:[]},getElementById(id){return nodes[id]||null}},window:{Chart:{getChart(){return {resize(){resizeCount++}}}}},localStorage:{getItem:k=>store[k]||null,setItem:(k,v)=>store[k]=v},setTimeout:(f,ms)=>{if(!ms)f();return 1},clearTimeout(){},setInterval:()=>1};
vm.createContext(ctx);vm.runInContext(fs.readFileSync(__dirname+'/../assets/keentool-ui.js','utf8'),ctx);
const toggle=created.find(e=>e.className==='kt-menu-toggle');assert(toggle);assert.equal(toggle.textContent,'Hide menu');toggle.onclick();assert(body.classList.contains('kt-menu-hidden'));assert.equal(store.kt_menu_hidden,'1');assert.equal(toggle.textContent,'Show menu');toggle.onclick();assert(!body.classList.contains('kt-menu-hidden'));assert(resizeCount>=3);
const state=created.find(e=>e.className==='kt-data-state');assert.notEqual(state.dataset.state,'missing');assert(state.lastElementChild.textContent.includes('14/10/2026'));
const css=fs.readFileSync(__dirname+'/../assets/keentool-ui.css','utf8');assert(css.includes('width:100%;max-width:none'));assert(css.includes('grid-template-columns:minmax(0,1fr) 88px'));assert(css.includes('minmax(min(100%,260px),1fr)'));
console.log('PASS: menu collapse/persistence, chart resize, timestamp fallback and full-width/responsive layout declarations.');

// Security publishes its asynchronously loaded snapshot to the shared state banner.
const securityBody=element();securityBody.dataset.ktPage='security';const securityCreated=[];
const securityCtx={...ctx,window:{},document:{...ctx.document,body:securityBody,createElement(){const e=element();securityCreated.push(e);return e},querySelectorAll:()=>[]}};
vm.createContext(securityCtx);vm.runInContext(fs.readFileSync(__dirname+'/../assets/keentool-ui.js','utf8'),securityCtx);
const securityState=securityCreated.find(e=>e.className==='kt-data-state');
assert.equal(securityState.dataset.state,'missing');assert.equal(securityState.lastElementChild.textContent,'Waiting for security data');
securityCtx.window.KT_SECURITY_DATA={status:'ready',updated:Math.floor(Date.now()/1000)};securityCtx.window.updateKTDataState();
assert.equal(securityState.dataset.state,'ready');assert(securityState.lastElementChild.textContent.includes('Data available'));
securityCtx.window.KT_SECURITY_DATA.updated-=240;securityCtx.window.updateKTDataState();assert.equal(securityState.dataset.state,'stale');assert(securityState.lastElementChild.textContent.includes('3 minutes'));
securityCtx.window.KT_SECURITY_DATA={status:'error'};securityCtx.window.updateKTDataState();assert.equal(securityState.dataset.state,'error');assert.equal(securityState.lastElementChild.textContent,'Security data unavailable');
securityCtx.window.KT_SECURITY_DATA={status:'ready'};securityCtx.window.updateKTDataState();assert.equal(securityState.dataset.state,'missing');
console.log('PASS: Security snapshot waiting/ready/stale/error/missing-time states and immediate asynchronous refresh.');
