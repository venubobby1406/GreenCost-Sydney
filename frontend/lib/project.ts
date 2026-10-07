import type {Project} from './types';

/** A new building scope must not inherit another building's geometry or bills. */
export function changeBuildingType(project:Project,buildingType:string):Project{
 if(buildingType===project.building_type)return project;
 return {...blankProject(),building_type:buildingType,
  name:project.name,postcode:project.postcode,zone:project.zone,area_unit:project.area_unit,
  price_date:project.price_date,years:project.years,discount:project.discount,
  energy_escalation:project.energy_escalation,water_escalation:project.water_escalation,
  maintenance_escalation:project.maintenance_escalation,other_escalation:project.other_escalation,
  terminal_escalation:project.terminal_escalation,web_research:project.web_research,
  occupant_mode:['Residential House','Apartment Building'].includes(buildingType)?'estimate':'manual',
  tariff_mode:['Commercial / Other','Apartment Building'].includes(buildingType)?'user':'official',
  rates_snapshot:null};
}

export function blankProject():Project{
 // Incomplete UI drafts may contain null; the API validates a completed Project.
 const empty=null as unknown as number;
 const local=new Date();local.setMinutes(local.getMinutes()-local.getTimezoneOffset());
 return {area_basis:'total',entered_area:null,apartment_average_unit_m2:75,apartment_residential_share:.8,occupant_mode:'estimate',end_of_life_mode:'retained',terminal_basis:'Building remains in use; no end-of-period demolition assumed.',mode:'itemised',preset:'code_minimum_7star',assumption_version:'2026-10-v1',selected_measures:[],code_required_measures:[],price_overrides:{},quantity_overrides:{},price_scenario:'median',solar_kw:6.6,tank_kl:5,gas_mj:0,gas_rate:0,gas_daily:0,gas_note:'',feed_in_rate:.05,terminal_confirmed:true,name:'',postcode:'',zone:'',building_type:'Residential House',area:empty,area_unit:'m²',floors:1,rooms:3,bathrooms:2,occupants:empty,quality:'Standard',cost_mode:'quick',conventional_cost:null,cost_per_m2:null,historical_index:null,sustainable_cost:null,premium:.1,materials:[],other_construction:0,detailed_complete:false,energy_kwh:empty,water_kl:empty,energy_reduction:.3,water_reduction:.4,maintenance_reduction:.15,performance_source:'research',input_quality:'estimate',features:['solar','insulation','fixtures','durable'],hvac:'User specified',hot_water:'User specified',lighting:'User specified',maintenance_annual:null,maintenance_fraction:.01,replacements:[],water_connected:true,wastewater_connected:true,stormwater:false,drought_tariff:false,tariff_mode:'official',electricity_rate:null,electricity_daily:null,water_rate:null,water_fixed_annual:null,tariff_note:'',price_date:local.toISOString().slice(0,10),years:40,discount:.05,energy_escalation:.03,water_escalation:.025,maintenance_escalation:.025,other_escalation:.025,terminal_escalation:.025,other_annual:0,disposal_conventional:0,disposal_sustainable:0,residual_conventional:0,residual_sustainable:0,web_research:true};
}
