import type {Measure} from '@/lib/types';

type ModelData={
 end_use_baseline_kwh?:Record<string,unknown>;
 efficiency?:Record<string,unknown>;
 solar?:Record<string,unknown>;
 energy_model?:Record<string,unknown>;
};
export type AssumptionRegister={assumptions?:ModelData;measures?:{measures?:Measure[]}};
const number=(group:Record<string,unknown>|undefined,key:string)=>typeof group?.[key]==='number'&&Number.isFinite(group[key])?group[key] as number:null;
const display=(value:number|null,suffix='')=>value===null?'Not available':value.toLocaleString('en-AU',{maximumFractionDigits:1})+suffix;
const percent=(value:number|null)=>display(value===null?null:value*100,'%');

export default function ModelAssumptions({register}:{register:AssumptionRegister}){
 const a=register.assumptions;
 if(!a)return <p role="status">The model assumptions are unavailable. Reconnect the calculator and refresh this page.</p>;
 const uses=[['Heating & cooling','heating_cooling'],['Hot water','hot_water'],['Lighting','lighting'],['Appliances','appliances']];
 const total=uses.reduce((sum,[,key])=>sum+(number(a.end_use_baseline_kwh,key)??0),0);
 const groups=[
  {title:'Electricity use',description:'Your annual electricity use is divided between these activities. These illustrative proportions can differ from the actual building.',rows:uses.map(([label,key])=>[label,total>0?percent((number(a.end_use_baseline_kwh,key)??0)/total):'Not available'])},
  {title:'System efficiency',description:'Indicative efficiency assumptions for comparing systems. Actual performance depends on the equipment and installation.',rows:[['Baseline heating/cooling efficiency',display(number(a.efficiency,'hvac_eer_baseline'))],['Upgraded heating/cooling efficiency',display(number(a.efficiency,'hvac_eer_upgrade'))],['Heat-pump hot-water efficiency',display(number(a.efficiency,'hot_water_cop_upgrade'))]]},
  {title:'Solar generation',description:'An indicative Sydney yield and self-use share. Roof orientation, shading, equipment and electricity demand affect the result.',rows:[['Annual generation per kW of panels',display(number(a.solar,'yield_kwh_per_kw_year'),' kWh/year')],['Self-use without load shifting',percent(number(a.solar,'self_consumption_unmanaged'))],['Self-use with load shifting',percent(number(a.solar,'self_consumption_load_shifted'))],['Maximum modelled array size',display(number(a.solar,'max_kw'),' kW')]]},
  {title:'Water saving',description:'Rainwater savings are limited by roof catchment, tank size and suitable non-drinking demand. Fixed water charges remain payable.',rows:[['Annual rainfall assumption',display(number(a.energy_model,'rainfall_m_per_year')===null?null:number(a.energy_model,'rainfall_m_per_year')!*1000,' mm')],['Rainwater capture assumption',percent(number(a.energy_model,'rainwater_capture_factor'))],['Maximum share of use replaced by rainwater',percent(number(a.energy_model,'max_non_potable_share'))],['Water-use reduction from efficient fixtures',percent(number(a.energy_model,'fixture_water_factor')===null?null:1-number(a.energy_model,'fixture_water_factor')!)]]},
 ];
 return <div className="model-assumptions"><p>These are <strong>indicative modelling assumptions</strong>, not verified building performance or supplier quotes. Your chosen budget, bill rates, financial settings and overrides appear in your comparison and report.</p><div className="assumption-card-grid">{groups.map(group=><section className="assumption-card" key={group.title}><h3>{group.title}</h3><span className="assumption-status">Indicative</span><p>{group.description}</p><dl>{group.rows.map(([label,value])=><div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl></section>)}</div>{register.measures?.measures?.length?<section className="assumption-catalogue"><h3>Features available to compare</h3><p>Choose suitable features in Sustainable design. Already included features are not counted as new upgrades. Prices remain indicative until replaced by comparable installed quotes.</p><div className="assumption-feature-grid">{register.measures.measures.map(m=><article key={m.id}><h4>{m.name}</h4><p>{m.plain_description}</p>{m.guidance_url&&<a href={m.guidance_url} target="_blank" rel="noreferrer">Read Australian guidance ↗</a>}</article>)}</div></section>:null}</div>;
}
