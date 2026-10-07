// Regression checks for canonical area, automatic counts and saved draft scope.
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const ts=require('../frontend/node_modules/typescript');
function readModule(file){
 const source=fs.readFileSync(path.join(__dirname,'..',file),'utf8');
 const js=ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
 const exports={};vm.runInNewContext(js,{exports,require,Date,Math,Number,JSON});return exports;
}
const {blankProject,changeBuildingType}=readModule('frontend/lib/project.ts');
const {updateApartmentProject:update,restoreDraft}=readModule('frontend/lib/client-planning.ts');
let p=update(blankProject(),{building_type:'Apartment Building',area_basis:'per_floor',entered_area:500,floors:20});
assert.equal(p.area,10000);assert.equal(p.occupants,219);
p=update(p,{floors:50});assert.equal(p.area,25000);assert.equal(p.occupants,547);
p=update(p,{area_basis:'total',entered_area:p.area});
p=update(p,{floors:20});assert.equal(p.area,25000);assert.equal(p.occupants,547);
p=update(p,{area_basis:'per_floor',entered_area:500,floors:null});
assert.equal(p.area,null);assert.equal(p.occupants,null);assert.equal(p.entered_area,500);
p=update(p,{floors:20});assert.equal(p.area,10000);assert.equal(p.occupants,219);
p=update(p,{apartment_average_unit_m2:null});assert.equal(p.occupants,null);
p=update(p,{apartment_average_unit_m2:75,apartment_residential_share:null});assert.equal(p.occupants,null);
p=update(p,{apartment_residential_share:.8,occupant_mode:'manual',occupants:300});
p=update(p,{floors:50});assert.equal(p.occupants,300);
p=update(p,{occupant_mode:'estimate',area_unit:'ft²',entered_area:500/.092903,floors:20});assert.equal(p.occupants,219);
const draft=restoreDraft(JSON.stringify({version:3,project:p,position:{step:2,review:false,period:'monthly'}}));
assert.equal(draft.project.area,p.area);assert.equal(draft.project.floors,20);assert.equal(draft.position.step,2);
const legacy=restoreDraft(JSON.stringify({version:3,project:{...blankProject(),building_type:'Apartment'},position:{step:1}}));
assert.equal(legacy.project.building_type,'Apartment');
console.log('Apartment frontend regressions passed: per-floor/total area, units, blank editing, manual override, draft scope.');

// Reproduce apartment -> Back -> House: hidden floors and overrides cannot leak.
const apartment={...blankProject(),building_type:'Apartment Building',area:250,entered_area:250,floors:5,occupants:30,quantity_overrides:{roof_area_m2:.5,solar_kw:10},conventional_cost:3000000,energy_kwh:100000,water_kl:2000,selected_measures:['solar_pv'],name:'Client project',postcode:'2144',years:50};
const house=changeBuildingType(apartment,'Residential House');
assert.equal(house.floors,1);assert.equal(house.area,null);assert.equal(house.entered_area,null);
assert.equal(Object.keys(house.quantity_overrides).length,0);
assert.equal(house.selected_measures.length,0);assert.equal(house.conventional_cost,null);
assert.equal(house.energy_kwh,null);assert.equal(house.water_kl,null);assert.equal(house.occupants,null);
assert.equal(house.name,'Client project');assert.equal(house.postcode,'2144');assert.equal(house.years,50);
assert.equal(house.tariff_mode,'official');assert.equal(house.occupant_mode,'estimate');
const confirmedHouse={...house,area:250,floors:2};
assert.equal(changeBuildingType(confirmedHouse,'Residential House'),confirmedHouse);
const savedHouse=restoreDraft(JSON.stringify({version:3,project:confirmedHouse,position:{step:2}}));
assert.equal(savedHouse.project.floors,2);assert.equal(savedHouse.project.area,250);
for(const type of ['Apartment Building','Commercial / Other','Apartment']){
 const changed=changeBuildingType(confirmedHouse,type);
 assert.equal(changed.floors,1);assert.equal(changed.area,null);assert.equal(changed.occupants,null);
 assert.equal(changed.building_type,type);
}
console.log('Building type switch regressions passed; same-type edits and saved multi-storey houses preserved.');
