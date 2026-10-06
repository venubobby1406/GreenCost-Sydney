'use client';
import {useState} from 'react';
import NumberInput from './NumberInput';
import Field from './FormField';
import {money,type Project} from '@/lib/types';
export default function QuotePair({id,project:p,onChange}:{id:string;project:Project;onChange:(p:Project)=>void}){
 const [values,setValues]=useState<{baseline:number|null;upgrade:number|null}>({baseline:p.installed_quotes?.[id]?.baseline??null,upgrade:p.installed_quotes?.[id]?.upgrade??null});
 function edit(side:'baseline'|'upgrade',value:number|null){const next={...values,[side]:value};setValues(next);const pairs={...p.installed_quotes};if(next.baseline!==null&&next.upgrade!==null){pairs[id]={baseline:next.baseline,upgrade:next.upgrade};const overrides={...p.price_overrides};delete overrides[id];onChange({...p,installed_quotes:pairs,price_overrides:overrides});}else{delete pairs[id];onChange({...p,installed_quotes:pairs});}}
 return <details><summary>Compare two installed quotes</summary><p className="small-note">Enter both quotes with the same scope, quantity and GST basis. This replaces a difference override above; Python adds only upgrade minus baseline.</p><div className="field-grid">{(['baseline','upgrade'] as const).map(side=><Field key={side} fieldKey={"installed_quotes."+id+"."+side} label={(side==='baseline'?'Conventional option':'Sustainable option')+' (AUD, installed)'} required={values.baseline!==null||values.upgrade!==null} help="Complete both quotes for the same scope, quantity and GST basis."><NumberInput min={0} value={values[side]} onValueChange={v=>edit(side,v)}/></Field>)}</div>{values.baseline!==null&&values.upgrade!==null?<p className="small-note">Installed difference: {money(values.upgrade-values.baseline)}.</p>:<p className="small-note">Complete both quotes to use their difference. A genuine zero may be entered explicitly.</p>}</details>;
}
