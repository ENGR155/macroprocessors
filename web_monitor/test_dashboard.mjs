import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const html=readFileSync(new URL('dashboard.html',import.meta.url),'utf8');
assert.equal((html.match(/<\/html>/g)||[]).length,1);
assert(!/<script[^>]+src=|<link[^>]+href=https?:/.test(html),'Dashboard must work without internet');
const script=html.match(/<script>([\s\S]*)<\/script>/)[1];
let queued=[],fetches=[],response,aborted=false;
const elements=new Map();
const ctx=new Proxy({}, {get:(t,k)=>t[k]||(()=>{}),set:(t,k,v)=>(t[k]=v,true)});
function element(id){if(!elements.has(id))elements.set(id,{textContent:'',value:id==='metric'?'position':'',disabled:true,clientWidth:900,clientHeight:300,getContext:()=>ctx,events:{},addEventListener(k,f){this.events[k]=f;},click(){}});return elements.get(id);}
const data={result:'ok',ms:1000,sample_ms:975,seq:1,valid:true,age_ms:25,raw:400,position_um:16000,calibrated:false,pid_connected:false,pid_writable:false,kp_milli:0,ki_milli:0,kd_milli:0,revision:0,spi_failures:0,uart_errors:0,bad_requests:0};
response={...data};
const sandbox={document:{getElementById:element,createElement:()=>element('download')},window:{devicePixelRatio:1,addEventListener(){}},location:{search:''},URLSearchParams,AbortController:class{signal={};abort(){aborted=true;}},URL:{createObjectURL:()=>'',revokeObjectURL(){}},Blob,Date,JSON,Math,Number,String,Error,
 setTimeout(fn,ms){queued.push({fn,ms});return fn;},clearTimeout(fn){queued=queued.filter(x=>x.fn!==fn);},setInterval(){},
 async fetch(url,options){fetches.push({url,options});if(response instanceof Error)throw response;return {ok:true,json:async()=>response};}};
vm.createContext(sandbox);vm.runInContext(script,sandbox);
const flush=()=>new Promise(resolve=>setImmediate(resolve));await flush();
assert.equal(element('position').textContent,'16.000 mm');assert.equal(element('apply').disabled,true);
assert.equal(vm.runInContext('history.length',sandbox),1);assert(!aborted);
async function tick(){const i=queued.findIndex(x=>x.ms===100);assert(i>=0,'Poll must reschedule after completion');const [task]=queued.splice(i,1);await task.fn();await flush();}
await tick();assert.equal(vm.runInContext('history.length',sandbox),1,'Repeated sample must not duplicate graph points');
response={...data,ms:1100,sample_ms:1075,seq:2,pid_connected:true,pid_writable:true,kp_milli:1234,revision:7};await tick();
assert.equal(element('livekp').textContent,'1.234');assert.equal(element('apply').disabled,false);
element('kp').value='2.100';element('kp').events.input();
response={...response,ms:1200,revision:8};await tick();assert.equal(element('kp').value,'2.100','Polling must preserve edits');
element('pidform').events.submit({preventDefault(){}});
response={...response,result:'conflict'};await tick();
const save=fetches.at(-1);
assert.equal(save.url,'/api/pid');
assert.equal(save.options.method,'POST');
assert.equal(save.options.headers['X-Maglev-Command'],'1');
assert.equal(save.options.body.toString(),'kp=2.100&ki=0.000&kd=0.000&revision=7','Edit revision must detect conflicting changes');
assert.match(element('message').textContent,/changed elsewhere/);
response=new Error('link down');await tick();assert.equal(element('connection').textContent,'Disconnected');
response={...data,ms:10,sample_ms:10,seq:1};await tick();assert.equal(vm.runInContext('history.length',sandbox),1,'Reboot resets graph');
response={...data,ms:9000,sample_ms:10,seq:1,age_ms:8990};await tick();assert.equal(element('connection').textContent,'Connected / sample stale');
element('metric').value='raw';element('metric').events.change();element('export').events.click();
assert(fetches.length>5);assert(queued.some(x=>x.ms===100));
console.log('PASS dashboard: framing, offline assets, live plot, duplicate suppression, gain readback, edits, revision conflict, disconnection, reboot, stale samples, raw view and CSV');
