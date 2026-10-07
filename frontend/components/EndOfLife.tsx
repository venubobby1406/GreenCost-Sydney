'use client';
import {useEffect,useState} from 'react';
import Field from './FormField';
import NumberInput from './NumberInput';
import {money,type Project} from '@/lib/types';

export default function EndOfLife({project:p,onChange}:{project:Project;onChange:(p:Project)=>void}){
 const [range,setRange]=useState<number[]|null>(null),[problem,setProblem]=useState('');
 const mode=p.end_of_life_mode??'manual';
 function change(next:Partial<Project>){onChange({...p,...next});}
 function guideBand(){
  const area=p.area*(p.area_unit==='ft²'?.092903:1);
  // Contractor guide for ordinary accessible houses only. No extrapolation.
  const band=p.floors===2&&area>=200&&area<=350?[32000,55000]:p.floors===1&&area>0&&area<150?[15000,22000]:p.floors===1&&area>=150&&area<=250?[20000,32000]:p.floors===1&&area>250&&area<=350?[28000,42000]:null;
  return p.building_type==='Residential House'?band:null;
 }
 useEffect(()=>{
  if(mode!=='estimate')return;
  const band=guideBand();
  if(!band){setRange(null);setProblem('The building scope changed. Enter a removal quote or choose “Remains in use”.');onChange({...p,end_of_life_mode:'manual',terminal_confirmed:false});return;}
  setRange(band);
  const amount=(band[0]+band[1])/2;
  if(p.disposal_conventional!==amount||p.disposal_sustainable!==amount){onChange({...p,disposal_conventional:amount,disposal_sustainable:amount,terminal_confirmed:false});}
  // Recalculate only when the scope changes; manual edits switch out of estimate mode.
  // eslint-disable-next-line react-hooks/exhaustive-deps
 },[p.area,p.area_unit,p.floors,p.building_type,mode]);
 function estimate(){
  const band=guideBand();
  if(p.building_type!=='Residential House'||!band){setProblem('No suitable house guide range for this scope. Enter an allocated quote or choose “Remains in use”.');return;}
  const midpoint=(band[0]+band[1])/2;setRange(band);setProblem('');change({end_of_life_mode:'estimate',disposal_conventional:midpoint,disposal_sustainable:midpoint,residual_conventional:0,residual_sustainable:0,terminal_confirmed:false,terminal_basis:'Direct Demolition March 2026 house guide midpoint; GST included; accessible site without asbestos; slab, footings and additional site work excluded. Salvage defaults to zero without a recovery quote.'});
 }
 return <section className="end-of-life form-block"><h4>End-of-life costs & recovered materials</h4><p className="small-note">A study ending does not mean the building is demolished. Choose what happens at the end of the period. Removing an existing building now belongs in your initial budget.</p><div className="choice-row"><button type="button" aria-pressed={mode==='retained'} className={mode==='retained'?'selected':''} onClick={()=>{setRange(null);setProblem('');change({end_of_life_mode:'retained',disposal_conventional:0,disposal_sustainable:0,residual_conventional:0,residual_sustainable:0,terminal_confirmed:true,terminal_basis:'Building remains in use. No demolition or recovered-material cash flow is included; property resale value is outside this comparison.'});}}>Remains in use</button><button type="button" aria-pressed={mode==='estimate'} className={mode==='estimate'?'selected':''} onClick={estimate}>Estimate removal</button><button type="button" aria-pressed={mode==='manual'} className={mode==='manual'?'selected':''} onClick={()=>change({end_of_life_mode:'manual',terminal_confirmed:false,terminal_basis:'User-entered end-of-period costs and recovered-material credits.'})}>Enter my costs</button></div>
 {problem&&<p role="status" className="field-error">{problem}</p>}
 {mode==='estimate'&&<div className="rate-summary"><b>Indicative removal {money(p.disposal_conventional)} per building</b>{range&&<p>Guide range: {money(range[0])}–{money(range[1])}. The midpoint is used.</p>}<p>Same allowance for both designs; no automatic sustainable discount. Recovered-material income is conservatively $0 until supported by a quote.</p><p>No asbestos, reasonable access; additional slab/footing removal and site work excluded. Confirm scope and GST with your contractor. This dated guide is escalated by your end-of-life price-growth assumption.</p><a href="https://directdemolition.com.au/blog/demolition-cost-sydney-2026.html" target="_blank" rel="noreferrer">Contractor guide · March 2026</a><button type="button" className="text-link" onClick={()=>change({end_of_life_mode:'manual',terminal_confirmed:false})}>Edit estimated amounts</button></div>}
 {mode!=='retained'&&<><div className="field-grid">{(['disposal_conventional','disposal_sustainable','residual_conventional','residual_sustainable'] as const).map(key=><Field key={key} fieldKey={key} required label={{disposal_conventional:'Conventional removal cost',disposal_sustainable:'Sustainable removal cost',residual_conventional:'Conventional recovered-material income',residual_sustainable:'Sustainable recovered-material income'}[key]} help="Base-year AUD, including GST. Recovery credits must be payable to you and must not already be deducted from the removal quote."><div className="input-unit"><NumberInput min={0} value={p[key]} onValueChange={v=>change({[key]:v,end_of_life_mode:'manual',terminal_confirmed:false})}/><span>AUD</span></div></Field>)}</div><div className="terminal-totals"><span>Conventional net cost <b>{money(p.disposal_conventional-p.residual_conventional)}</b></span><span>Sustainable net cost <b>{money(p.disposal_sustainable-p.residual_sustainable)}</b></span></div><Field fieldKey="terminal_confirmed" required label="Confirm end-of-life assumptions" help="Review your removal scope and recovery credits before including them in the final year."><input type="checkbox" checked={p.terminal_confirmed} onChange={e=>change({terminal_confirmed:e.target.checked})}/><span>I reviewed these amounts and their scope.</span></Field></>}
 {mode==='retained'&&<p className="small-note">No end-of-period removal cost or material-sale income included. Equipment replacements are still calculated separately.</p>}
 </section>;
}
