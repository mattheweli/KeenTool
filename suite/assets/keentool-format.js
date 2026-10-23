/* KeenTool Number Format v1.0.0 — 2026-10-22. Presentation and localized form input only. */
(() => {
 'use strict';
 const locale='de-DE';
 function number(value,min=0,max=2){
  if(value===null||value===undefined||value===''||typeof value==='boolean')return 'Unavailable';
  const numeric=typeof value==='bigint'?value:(typeof value==='string'&&/^[+-]?\d+$/.test(value)?BigInt(value):Number(value));
  if(typeof numeric!=='bigint'&&!Number.isFinite(numeric))return 'Unavailable';
  return new Intl.NumberFormat(locale,{minimumFractionDigits:min,maximumFractionDigits:max}).format(numeric);
 }
 function integer(value){
  if(typeof value==='string'&&/^[+-]?\d+$/.test(value))return number(BigInt(value),0,0);
  return number(value,0,0);
 }
 function signedInteger(value){const raw=String(value).trim();return (raw.startsWith('+')?'+':'')+integer(raw);}
 function scaled(value,base,units,max=2,min=0){
  if(value===null||value===undefined||typeof value==='boolean'||!Number.isFinite(Number(value))||Number(value)<0)return 'Unavailable';
  let amount=Number(value),unit=0;
  while(amount>=base&&unit<units.length-1){amount/=base;unit++;}
  if(Math.round(amount*10**max)/10**max>=base&&unit<units.length-1){amount/=base;unit++;}
  return number(amount,min,max)+' '+units[unit];
 }
 function bytes(value,base=1024,max=2,min=0){return scaled(value,base,['B','KB','MB','GB','TB','PB'],max,min);}
 function parse(value){
  const raw=String(value).trim();
  if(!/^[+-]?(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d+)?$/.test(raw))throw Error('Use a comma for decimals and a dot for thousands (for example 1.234,56).');
  const numeric=Number(raw.replace(/\./g,'').replace(',','.'));
  if(!Number.isFinite(numeric))throw Error('Enter a finite number.');return numeric;
 }
 window.KTFormat={locale,number,integer,signedInteger,scaled,bytes,parse};
})();
