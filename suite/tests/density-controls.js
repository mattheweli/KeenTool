const fs=require('fs'),vm=require('vm'),assert=require('assert');
const source=fs.readFileSync(__dirname+'/../assets/keentool-ui.js','utf8');
const preferences=source.slice(source.indexOf(' function readPreference'),source.indexOf(' const page='));
const density=source.slice(source.indexOf(' // Density affects'),source.indexOf(' // Focusable scroll containers'));
function run(page,store,blocked=false,hasTables=true){
 const created=[],host={children:[],append(x){this.children.push(x)}};
 const body={dataset:{},prepend(){}};
 const ctx={page,document:{body,createElement(){const e={children:[],append(...x){this.children.push(...x)},setAttribute(k,v){this[k]=v}};created.push(e);return e},querySelector:selector=>selector==='table'&&!hasTables?null:host},localStorage:{getItem:k=>{if(blocked)throw Error('blocked');return store[k]},setItem:(k,v)=>{if(blocked)throw Error('blocked');store[k]=v}}};
 vm.createContext(ctx);vm.runInContext(preferences+density,ctx);
 return{ctx,created,body,select:created.find(e=>e.className==='kt-density-select')};
}
const store={},first=run('firewall',store);assert.equal(first.body.dataset.ktDensity,'comfortable');
first.select.value='compact';first.select.onchange();assert.equal(store.kt_table_density,'compact');assert.equal(first.body.dataset.ktDensity,'compact');
const next=run('traffic',store);assert.equal(next.select.value,'compact');next.select.value='comfortable';next.select.onchange();assert.equal(store.kt_table_density,'comfortable');
assert.equal(run('ping',{kt_table_density:'invalid'}).select.value,'comfortable');
const noStorage=run('firewall',{},true);noStorage.select.value='compact';noStorage.select.onchange();assert.equal(noStorage.body.dataset.ktDensity,'compact');
assert.equal(run('home',store).select,undefined);assert.equal(run('ping',store,false,false).select,undefined);
console.log('PASS: density defaults, switching, persistence across monitor pages, invalid-value fallback, unavailable storage and no irrelevant home control.');
