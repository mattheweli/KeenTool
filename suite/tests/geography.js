const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync(__dirname+'/../projects/keenetic-firewall/www/index.html','utf8');
const code=html.slice(html.indexOf('        // Geography uses'),html.indexOf('        function showReadOnlyList'));
class Element {
 constructor(){this.children=[];this.style={setProperty:(k,v)=>this.style[k]=v};this.classList={toggle(){}};this.hidden=false;this.textContent='';this.attrs={};this.listeners={};}
 append(...els){this.children.push(...els)}appendChild(el){this.append(el);el.parentElement=this}replaceChildren(...els){this.children=els}addEventListener(k,f){this.listeners[k]=f}querySelectorAll(){return []}getBoundingClientRect(){return{width:900}}setAttribute(k,v){this.attrs[k]=v}
}
const els={},get=id=>els[id]||(els[id]=new Element());
let opts,destroyed=0;
const data={total:2000,countries:{US:{hits:1490,sources:2,rows:[{ip:'2001:db8::1',hits:1490,ports:'443/tcp'}]},CN:{hits:300,sources:1,rows:[]},XX:{hits:196,sources:1,rows:[]},unknown:{hits:14,sources:1,rows:[]}}};
const context={Intl,Number,Math,Object,console,document:{getElementById:get,createElement:()=>new Element(),head:new Element(),querySelectorAll:()=>[],addEventListener(){}},window:{FW_DATA:{geography:{'24h':data,'30d':{total:7,countries:{DE:{hits:7,sources:1,rows:[]}}}}},addEventListener(){}},requestAnimationFrame:f=>f(),setTimeout,clearTimeout,jsVectorMap:function(o){opts=o;this.destroy=()=>destroyed++}};
vm.createContext(context);vm.runInContext(fs.readFileSync(__dirname+'/../assets/keentool-format.js','utf8'),context);vm.runInContext(code,context);
vm.runInContext("updateMap('24h')",context);
assert(els.map_stats.textContent.includes('2 countries'));assert(els.map_stats.textContent.includes('2.000'));assert(els.map_coverage.textContent.includes('210 unknown'));
assert.equal(els.map_ranking.children.length,2);assert.equal(els.map_ranking.children[0].children[0].children[1].textContent,'1.490 · 74,5%');
assert(els.dynamic_map_styles.textContent.includes('20.00%'));assert(!els.dynamic_map_styles.textContent.includes('XX'));assert(!els.dynamic_map_styles.textContent.includes('NaN'));
let tip='';opts.onRegionTooltipShow(null,{text:t=>tip=t},'US');assert(tip.includes('1.490'));assert(tip.includes('74,5%'));
els.map_ranking.children[0].children[0].listeners.click();assert.equal(els.map_details.hidden,false);assert.equal(els.map_details_rows.children[0].children[0].textContent,'2001:db8::1');
assert(els.map_details_note.textContent.includes('not limited to this period'));
vm.runInContext("updateMap('30d')",context);assert.equal(els.map_details.hidden,true);assert(els.map_stats.textContent.includes('1 country'));assert(destroyed>0);
assert(!els.dynamic_map_styles.textContent.includes('NaN'));vm.runInContext("mapShowCountry('FR')",context);assert(els.map_details_note.textContent.includes('No recorded'));
context.window.FW_DATA.geography=undefined;vm.runInContext('mapReset()',context);assert(els.map_stats.textContent.includes('pending'));assert.equal(els.map_details.hidden,true);
console.log('PASS: full numeric counts, unknown excluded from country ranking, percentage denominator, gradient/tooltip, public details, period refresh, no-data and pending export.');
