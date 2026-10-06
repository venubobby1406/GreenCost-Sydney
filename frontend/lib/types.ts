export type Material = {name:string;quantity:number;unit:string;unit_cost:number;service_life:number|null;replacement_interval:number|null;maintenance:number;price_status?:string;price_source?:string;price_checked?:string};
export type Replacement = {name:string;scenario:'both'|'conventional'|'sustainable';interval:number;cost:number;escalation:number};
export type Project = {
 budget_range?:number[]|null;cost_plan_note?:string;cost_plan_basis?:string;
 installed_quotes?:Record<string,{baseline:number;upgrade:number}>;
 mode:'itemised'|'literature';preset:'code_minimum_7star'|'legacy_6star';assumption_version:'2026-10-v1';selected_measures:string[];code_required_measures:string[];price_overrides:Record<string,number>;quantity_overrides:Record<string,number>;price_scenario:'low'|'median'|'high';solar_kw:number;tank_kl:number;gas_mj:number;gas_rate:number;gas_daily:number;gas_note:string;feed_in_rate:number;terminal_confirmed:boolean;rates_snapshot?:Record<string,number>|null;
 name:string;postcode:string;zone:string;building_type:string;area:number;area_unit:string;floors:number;rooms:number;bathrooms:number;occupants:number;quality:string;
 cost_mode:string;conventional_cost:number|null;cost_per_m2:number|null;historical_index:number|null;sustainable_cost:number|null;premium:number;materials:Material[];other_construction:number;detailed_complete:boolean;
 energy_kwh:number;water_kl:number;energy_reduction:number;water_reduction:number;maintenance_reduction:number;performance_source:string;input_quality:string;features:string[];
 hvac:string;hot_water:string;lighting:string;maintenance_annual:number|null;maintenance_fraction:number;replacements:Replacement[];
 water_connected:boolean;wastewater_connected:boolean;stormwater:boolean;drought_tariff:boolean;tariff_mode:string;electricity_rate:number|null;electricity_daily:number|null;water_rate:number|null;water_fixed_annual:number|null;tariff_note:string;
 price_date:string;years:number;discount:number;energy_escalation:number;water_escalation:number;maintenance_escalation:number;other_escalation:number;terminal_escalation:number;other_annual:number;web_research:boolean;
 disposal_conventional:number;disposal_sustainable:number;residual_conventional:number;residual_sustainable:number;
};
export type Cashflow = {year:number;cumulative_pv:number;operating:number;nominal_total:number;pv_total:number;events:string[];[key:string]:number|string[]};
export type Scenario = {total_lcc:number;components:Record<string,number>;cashflows:Cashflow[]};
export type Period = {years:number;conventional:Scenario;sustainable:Scenario;savings_aud:number;savings_percent:number|null;break_even_year:number|null;reversal_years:number[];capital_difference:number;component_savings:Record<string,number>;explanation:string[]};
export type Evidence = {source:string;page:number;text:string;source_type:string;url:string|null};
export type Source = {id:string;title:string;organisation:string;url:string;effective_from:string;effective_to:string|null;publication_date:string|null;retrieved_at:string;notes:string;source_category:string;values:Record<string,{value:number;unit:string;evidence:string}>};
export type Analysis = ExtendedAnalysis & {rates:Record<string,number>;id:string;project:Project;periods:Record<string,Period>;sensitivity:{years:number;discount:number;energy_escalation:number;savings_aud:number;savings_percent:number|null}[];confidence:string;confidence_reason:string;usage:{tavily_calls:number;llm_calls:number};research_status?:{gemini:string;tavily:string;vector_db:string};sources:Source[];evidence:Evidence[];assumptions:{name:string;value:number;unit:string;source:string}[];limitations:string[]};
export type Health = {rag_ready:boolean;knowledge:{ready:boolean;documents:number;chunks:number};vector_db:string;gemini_configured:boolean;tavily_configured:boolean;gemini_model:string;uploads_enabled:boolean};
export type Stage = {type:'stage'|'result'|'error';stage?:string;message?:string;result?:Analysis};
export type Measure={id:string;name:string;plain_description:string};
export type MeasureCost={id:string;name:string;premium:number;quantity:number;quantity_driver:string;unit_price:number;low:number;high:number;badge:string;source:string;price_date:string};
export type ExtendedAnalysis={budget_scenarios?:Record<string,Record<string,{conventional:number;sustainable:number;savings_aud:number}>>;measures?:MeasureCost[];measure_contributions?:Record<string,{id:string;name:string;marginal_savings:number;standalone_savings:number;interaction_adjustment:number}[]>;literature_scenarios?:Record<string,Record<string,Period>>;price_sensitivity?:Record<string,Record<string,{savings_aud:number;break_even_year:number|null}>>;assumption_version?:string;price_snapshot_date?:string};
export const money = (v:number) => new Intl.NumberFormat('en-AU',{style:'currency',currency:'AUD',maximumFractionDigits:0}).format(v);
export class ApiError extends Error {constructor(message:string,public fields:Record<string,string>={}){super(message);this.name='ApiError';}}
async function readResponse(response:Response){
 let result;try{result=await response.json();}catch{throw new ApiError('The calculator could not be reached. Check the connection and retry.');}
 if(!response.ok){const detail=result.detail,fields:Record<string,string>={};
  if(Array.isArray(detail))for(const error of detail){const key=error.loc?.filter((v:unknown)=>v!=='body').join('.');if(key)fields[key]=error.msg?.replace('Value error, ','')??'Check this value.';}
  throw new ApiError(Object.keys(fields).length?'Review the highlighted inputs.':typeof detail==='string'?detail:'The calculator could not complete this request. Please retry.',fields);
 }return result;
}
export async function api<T>(path:string, body?:unknown):Promise<T> {
 try{const signal=AbortSignal.timeout(path==='/health'?5000:60000);const response = await fetch('/api'+path,body === undefined ? {signal} : {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal});return await readResponse(response);}catch(error){if(error instanceof ApiError)throw error;throw new ApiError('The calculator connection was interrupted. Your inputs are preserved; please retry.');}
}

export async function streamAnalysis(project:Project,onStage:(event:Stage)=>void):Promise<Analysis>{
 const response=await fetch('/api/analyse/stream',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(project),signal:AbortSignal.timeout(60000)});
 if(!response.ok)await readResponse(response);
 if(!response.body)throw new Error('The response stream is unavailable. Please retry.');
 const reader=response.body.getReader(),decoder=new TextDecoder();let buffer='',analysis:Analysis|undefined;
 function consume(){let boundary;while((boundary=buffer.indexOf('\n\n'))!==-1){const block=buffer.slice(0,boundary);buffer=buffer.slice(boundary+2);const line=block.split('\n').find(l=>l.startsWith('data: '));if(!line)continue;const event:Stage=JSON.parse(line.slice(6));if(event.type==='error')throw new Error(event.message);if(event.type==='result')analysis=event.result;onStage(event);}}
 try{while(true){const {done,value}=await reader.read();if(done)break;buffer+=decoder.decode(value,{stream:true});consume();}buffer+=decoder.decode();consume();}finally{reader.releaseLock();}
 if(!analysis)throw new Error('The connection ended before your analysis finished. Please retry.');
 return analysis;
}
