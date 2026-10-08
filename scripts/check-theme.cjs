// The preference bootstrap must work before React and when storage is blocked.
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const ts=require('../frontend/node_modules/typescript');
const source=fs.readFileSync(path.join(__dirname,'../frontend/lib/theme-initialization.ts'),'utf8');
const moduleExports={};
vm.runInNewContext(ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS}}).outputText,{exports:moduleExports});
let cases=0;
for(const [preference,systemDark,expected] of [
 ['light',true,'light'],['dark',false,'dark'],
 [null,true,'dark'],[null,false,'light'],
 ['invalid',true,'dark'],['invalid',false,'light'],
 ['blocked',true,'dark'],['blocked',false,'light'],
]) {
 const root={dataset:{},style:{}};
 vm.runInNewContext(moduleExports.themeInitialization,{
  document:{documentElement:root},
  window:{matchMedia:()=>({matches:systemDark})},
  localStorage:{getItem:key=>{assert.equal(key,'greencost-theme');if(preference==='blocked')throw Error('Storage unavailable');return preference;}},
 });
 assert.equal(root.dataset.theme,expected);
 assert.equal(root.style.colorScheme,expected);
 cases++;
}
console.log(`Theme bootstrap: ${cases} preference/system/storage cases passed.`);
