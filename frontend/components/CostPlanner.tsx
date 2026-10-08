'use client';
import {DrawCheckbox} from './ui/draw-checkbox';
import {useEffect,useRef,useState} from 'react';
import {ArrowUpRight,RefreshCw,Plus,Trash2} from 'lucide-react';
import NumberInput from './NumberInput';
import Field,{ValidationContext} from './FormField';
import {useContext} from 'react';
import {api,money,type Material,type Project} from '@/lib/types';

type Plan={midpoint:number;other_construction:number;assumptions:string;rows:(Material&{id:string;total:number})[]};
type Candidate={title:string;url:string;unit:string;unit_price:number|null;status:string;checked_at:string;gst:string;installation:string;delivery:string};
type PriceResponse={status:string;message:string;cached?:boolean;candidates:Candidate[]};
const supplierItems:Record<string,{key:string;unit:string}>={
 'Concrete & foundations':{key:'concrete',unit:'m³'},
 'Structural timber':{key:'timber',unit:'m³'},
 'Roof covering':{key:'roofing',unit:'m²'},
 'Windows & external glazing':{key:'windows',unit:'m²'},
 'Wall insulation':{key:'insulation',unit:'m²'},
 'Internal finishes & fittings':{key:'finishes',unit:'allowance'},
};
function supplierItem(m:Material){const item=supplierItems[m.name];return item?.unit===m.unit?item.key:null;}

export default function CostPlanner({project:p,onChange}:{project:Project;onChange:(p:Project)=>void}){
 const [mode,setMode]=useState<'exact'|'range'|'rate'|'detailed'>(p.cost_mode==='detailed'?'detailed':p.budget_range?'range':p.conventional_cost===null&&p.cost_per_m2?'rate':'exact');
 const [bounds,setBounds]=useState<(number|null)[]>(p.budget_range??[null,null]);
 const [error,setError]=useState(''),[working,setWorking]=useState(false),[checking,setChecking]=useState('');
 const [prices,setPrices]=useState<Record<number,PriceResponse>>({});
 const validation=useContext(ValidationContext);
 const last=useRef(''),latest=useRef(p);latest.current=p;
 const area=p.area*(p.area_unit==='ft²'?.092903:1),signature=JSON.stringify([p.conventional_cost,p.cost_per_m2,p.area,p.area_unit,p.floors,p.bathrooms,p.budget_range]);
 const total=p.cost_mode==='detailed'?p.materials.reduce((s,m)=>s+m.quantity*m.unit_cost,0)+p.other_construction:p.conventional_cost??(p.cost_per_m2??0)*area;
 useEffect(()=>{
  if(mode==='detailed'||!Number.isFinite(total)||total<=0||!(area>0)||!(p.floors>=1)||!(p.bathrooms>=0)||last.current===signature||p.cost_plan_basis===signature)return;
  let active=true;const timer=setTimeout(async()=>{
   setWorking(true);try{const plan=await api<Plan>('/v1/cost-plan',{area,floors:p.floors,bathrooms:p.bathrooms,budget_low:p.budget_range?.[0]??total,budget_high:p.budget_range?.[1]??null});
    if(active){last.current=signature;setPrices({});onChange({...latest.current,materials:plan.rows.map(({name,quantity,unit,unit_cost,service_life,replacement_interval,maintenance})=>({name,quantity,unit,unit_cost,service_life,replacement_interval,maintenance,price_status:'Estimate',price_source:'Budget allocation placeholder'})),other_construction:plan.other_construction,cost_plan_note:plan.assumptions,cost_plan_basis:signature,detailed_complete:true});setError('');}
   }catch(e){if(active)setError((e as Error).message);}finally{if(active)setWorking(false);}
  },600);return()=>{active=false;clearTimeout(timer);};
 // Rebuild only when geometry or budget changes, never on each price edit.
 // eslint-disable-next-line react-hooks/exhaustive-deps
 },[signature,mode]);
 function choose(next:typeof mode){setMode(next);setError('');setPrices({});setBounds([null,null]);onChange({...p,cost_mode:next==='detailed'?'detailed':'quick',budget_range:null,historical_index:null,cost_plan_basis:'',cost_plan_note:next==='detailed'?p.cost_plan_note:'',cost_per_m2:next==='rate'?p.cost_per_m2:null,...(['rate','range'].includes(next)?{conventional_cost:null}:{} )});last.current='';}
 function changeBounds(index:number,value:number|null){const next=[...bounds];next[index]=value;setBounds(next);const valid=next[0]!==null&&next[1]!==null&&next[0]>0&&next[1]>=next[0];onChange({...p,budget_range:valid?next as number[]:null,conventional_cost:valid?(next[0]!+next[1]!)/2:null});}
 function edit(index:number,patch:Partial<Material>){if(patch.name!==undefined||patch.unit!==undefined)setPrices({});onChange({...p,materials:p.materials.map((m,i)=>i===index?{...m,...patch}:m)});}
 async function checkPrice(index:number){const original=p.materials[index],item=supplierItem(original);if(!item)return;setChecking(String(index));try{const response=await api<PriceResponse>('/v1/supplier-price',{item});if(latest.current.materials[index]===original)setPrices(old=>({...old,[index]:response}));}catch(e){setError((e as Error).message);}finally{setChecking('');}}
 function applyPrice(index:number,c:Candidate){edit(index,{unit_cost:c.unit_price!,price_status:'Published supply price',price_source:c.url,price_checked:c.checked_at});}
 async function findAllPrices(){
  setError('');
  let checks=0;
  for(let index=0;index<p.materials.length&&checks<5;index++){
   const original=p.materials[index],item=supplierItem(original);if(!item||item==='finishes'||original.price_status==='Your price')continue;checks++;
   setChecking(String(index));
   try{const response=await api<PriceResponse>('/v1/supplier-price',{item});if(latest.current.materials[index]===original)setPrices(old=>({...old,[index]:response}));
    if(response.status==='budget_or_host_limit')break;
    const matches=response.candidates.filter(c=>c.unit_price!==null&&c.unit===original.unit);
    // Multiple products need user selection. Never overwrite a quote or intervening edit.
    if(matches.length===1&&latest.current.materials[index]===original){const c=matches[0],current=latest.current;onChange({...current,materials:current.materials.map((m,i)=>i===index?{...m,unit_cost:c.unit_price!,price_status:'Published supply price',price_source:c.url,price_checked:c.checked_at}:m)});}
   }catch(e){setError((e as Error).message);break;}
  }
  setChecking('');
 }
 return <section className="form-block"><div className="block-heading"><span className="block-number">01</span><div><h4>What will your building cost?</h4><p>{p.building_type==='Apartment Building'?'Construction budget for the whole building, including all floors and common building services. Excludes land and finance.':'A construction budget, excluding land and finance.'}</p></div></div>
 <div className="choice-row" aria-label="Budget entry method">{([['exact','Exact budget'],['range','Budget range'],['rate','Cost per m²'],['detailed','Detailed costs']] as const).map(([key,label])=><button type="button" key={key} className={mode===key?'selected':''} aria-pressed={mode===key} onClick={()=>choose(key)}>{label}</button>)}</div>
 {mode==='exact'&&<Field label="Total construction budget (AUD)" fieldKey="conventional_cost" required help="The total construction cost, excluding land and finance. Category costs are editable estimates."><NumberInput min={1} value={p.conventional_cost} placeholder="e.g. 720000" onValueChange={v=>onChange({...p,conventional_cost:v,budget_range:null})}/><small>Your total is known; the category breakdown is still an estimate.</small></Field>}
 {mode==='rate'&&<Field label="Construction cost per m² (AUD)" fieldKey="cost_per_m2" required help="Multiplied by your total floor area to estimate the construction budget."><NumberInput min={1} value={p.cost_per_m2} onValueChange={v=>onChange({...p,cost_per_m2:v,conventional_cost:null,budget_range:null})}/><small>Applied to {area?.toFixed(1)} m² of total floor area.</small></Field>}
 {mode==='range'&&<><div className="field-grid"><Field label="Lower budget (AUD)" fieldKey="budget_range.0" required help="The lower end of your construction budget. Results calculate low, midpoint and high cases."><NumberInput min={1} value={bounds[0]} placeholder="e.g. 600000" onValueChange={v=>changeBounds(0,v)}/></Field><Field label="Upper budget (AUD)" fieldKey="budget_range.1" required help="Must be at least the lower budget. The main result uses the midpoint."><NumberInput min={bounds[0]??1} value={bounds[1]} placeholder="e.g. 800000" onValueChange={v=>changeBounds(1,v)}/></Field></div>{p.budget_range?<p className="small-note">Main comparison: {money(total)} midpoint. Low and high budgets are calculated separately in results.</p>:<p className="small-note">Enter both bounds; the upper budget must be at least the lower budget.</p>}</>}
 {error&&<p className="field-error" role="alert">{error}</p>}
 {working&&<p role="status" className="small-note">Preparing your estimated breakdown…</p>}
 {p.materials.length>0&&<details className="form-details cost-breakdown" open={Object.keys(validation.errors).some(k=>k.startsWith('materials.')||k==='other_construction')||undefined}><summary>Review & edit cost breakdown <span>{money(p.materials.reduce((s,m)=>s+m.quantity*m.unit_cost,0)+p.other_construction)}</span></summary><p className="small-note">Quantities and allocations are estimates. Checking a supplier never treats a search snippet as a verified price. Labour, delivery and fees remain separate.</p>
 <button type="button" className="text-link" disabled={!!checking} onClick={()=>void findAllPrices()}><RefreshCw size={14}/>{checking?'Checking available prices…':'Find prices for this breakdown'}</button><p className="small-note">Checks up to five categories with Tavily. Clear, tax-inclusive prices fill automatically when there is one match. Quotes and ambiguous products stay unchanged.</p>
 <div className="cost-table">{p.materials.map((m,i)=><div key={i} className="cost-line"><div className="cost-line-summary"><b>{m.name}</b><span className="price-badge">{m.price_status??'Your price'}</span><strong>{money(m.quantity*m.unit_cost)}</strong></div><details className="cost-row-editor"><summary>Review or edit</summary><div className="field-grid"><Field label="Item name" fieldKey={"materials."+i+".name"} required><input value={m.name} onChange={e=>edit(i,{name:e.target.value})}/></Field><Field label={"Quantity ("+m.unit+")"} fieldKey={"materials."+i+".quantity"} required help="Editable estimate. Use quantities from your drawings where possible."><NumberInput min={0} value={m.quantity} onValueChange={v=>edit(i,{quantity:v as number,price_status:'Your estimate'})}/></Field><Field label={"Price per "+m.unit+" (AUD)"} fieldKey={"materials."+i+".unit_cost"} required help="Supply cost only. Check GST, exact product and delivery separately."><NumberInput min={0} value={m.unit_cost} onValueChange={v=>edit(i,{unit_cost:v as number,price_status:'Your price',price_source:'User input',price_checked:''})}/></Field><Field label="Unit" fieldKey={"materials."+i+".unit"} required><input value={m.unit} onChange={e=>edit(i,{unit:e.target.value,price_status:'Your estimate'})}/></Field></div><details><summary>Replacement & maintenance details</summary><div className="field-grid"><Field label="Replacement interval (years)" fieldKey={"materials."+i+".replacement_interval"}><NumberInput min={1} max={100} step={1} value={m.replacement_interval} onValueChange={v=>edit(i,{replacement_interval:v})}/></Field><Field label="Annual item maintenance (AUD)" fieldKey={"materials."+i+".maintenance"} required><NumberInput min={0} value={m.maintenance} onValueChange={v=>edit(i,{maintenance:v as number})}/></Field></div></details>{m.price_checked&&<p className="small-note">Checked {m.price_checked.slice(0,10)} · {m.price_source}</p>}{mode==='detailed'&&<button type="button" className="text-link" onClick={()=>{setPrices({});onChange({...p,materials:p.materials.filter((_,n)=>n!==i)});}}><Trash2 size={14}/> Remove item</button>}
 {supplierItem(m)&&<button className="text-link" type="button" disabled={!!checking} onClick={()=>void checkPrice(i)}><RefreshCw size={13}/>{checking===String(i)?'Checking supplier…':'Check supplier prices'}</button>}
 {prices[i]&&<div className="supplier-results" role="status"><p>{prices[i].message}{prices[i].cached?' Reusing a price check less than a day old.':''}</p>{prices[i].candidates.map(c=><article key={c.url}><a href={c.url} target="_blank" rel="noopener noreferrer">{c.title}<ArrowUpRight size={12}/></a><small>{c.status} · GST {c.gst} · delivery {c.delivery} · installation {c.installation} · {c.checked_at.slice(0,10)}</small>{c.unit_price!==null&&c.unit===m.unit&&<button type="button" onClick={()=>applyPrice(i,c)}>Use {money(c.unit_price)}/{c.unit} supply price</button>}</article>)}</div>}</details>
 </div>)}</div><Field label="Labour, installation, services, fees & remaining scope (AUD)" fieldKey="other_construction" required help="The remaining cost beyond supply materials. Review labour, fees and site-specific scope."><NumberInput min={0} value={p.other_construction} onValueChange={v=>onChange({...p,other_construction:v as number})}/><small>Initially 25% labour and 35% other scope. These are editable placeholders, not market benchmarks.</small></Field>
 {p.cost_plan_note&&<p className="small-note">{p.cost_plan_note}</p>}
 {mode!=='detailed'&&<><p className="small-note">Your entered budget remains the calculation baseline until you choose to use this edited breakdown.</p><button className="text-link" type="button" onClick={()=>{setMode('detailed');onChange({...p,cost_mode:'detailed',budget_range:null,historical_index:null,detailed_complete:true});}}>Use edited breakdown as construction total</button></>}
 </details>}
 {mode==='detailed'&&<><button type="button" className="text-link" onClick={()=>onChange({...p,materials:[...p.materials,{name:'New item',quantity:1,unit:'allowance',unit_cost:0,service_life:null,replacement_interval:null,maintenance:0}],budget_range:null})}><Plus size={14}/> Add cost item</button><Field fieldKey="detailed_complete" label="I included materials, labour, fees and the full construction scope." required><DrawCheckbox checked={p.detailed_complete} onChange={e=>onChange({...p,detailed_complete:e.target.checked})}/></Field></>}
 </section>;
}
