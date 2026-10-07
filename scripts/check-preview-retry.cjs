const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const ts=require('../frontend/node_modules/typescript');
const exportsForTest={};let calls=0,reply;
const source=fs.readFileSync(path.join(__dirname,'../frontend/lib/types.ts'),'utf8');
vm.runInNewContext(ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText,{exports:exportsForTest,Response,AbortSignal,fetch:async()=>{calls++;return reply();}});
(async()=>{
 reply=()=>Response.json({detail:{code:'solar_capacity',message:'Review your roof area.',geometry:{max_solar_kw:.04}}},{status:422});
 for(let i=0;i<2;i++)await assert.rejects(exportsForTest.api('/v1/preview',{}),e=>e instanceof exportsForTest.ApiError&&e.status===422&&e.details.code==='solar_capacity'&&e.details.geometry.max_solar_kw===.04);
 assert.equal(calls,2);
 reply=()=>Response.json({detail:'Temporarily unavailable'},{status:503});
 await assert.rejects(exportsForTest.api('/v1/preview',{}),e=>e.status===503&&!e.details);
 reply=()=>Response.json({premium:1234});
 assert.equal((await exportsForTest.api('/v1/preview',{})).premium,1234);
 console.log('Preview regressions passed: input diagnostics, repeat validation, retryable server failure and recovery.');
})().catch(e=>{console.error(e);process.exitCode=1;});
