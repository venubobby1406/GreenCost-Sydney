'use client';
import type {Project} from '@/lib/types';
import {apartmentOccupancy,apartmentOccupancySource} from '@/lib/client-planning';
import Field from './FormField';
import NumberInput from './NumberInput';

export default function ApartmentBuildingSize({project:p,onChange}:{project:Project;onChange:(changes:Partial<Project>)=>void}){
 const basis=p.area_basis??'total',automatic=p.occupant_mode==='estimate';
 const entered=p.entered_area??(basis==='total'?p.area:null);
 const average=p.apartment_average_unit_m2===undefined?75:p.apartment_average_unit_m2;
 const share=p.apartment_residential_share===undefined?.8:p.apartment_residential_share;
 const estimate=apartmentOccupancy(p.area,p.area_unit,average,share);
 const format=(value:number)=>value.toLocaleString('en-AU',{maximumFractionDigits:1});
 return <>
  <p className="scope-note">Whole apartment building. Use the same building scope for area, budget, residents and utility bills. Exclude parking-only floors and their area from this residential size estimate.</p>
  <div className="choice-row" role="group" aria-label="Apartment area entry">{(['per_floor','total'] as const).map(value=><button type="button" key={value} aria-pressed={basis===value} className={basis===value?'selected':''} onClick={()=>onChange({area_basis:value,entered_area:p.area>0?(value==='per_floor'&&p.floors>0?p.area/p.floors:p.area):null})}>{value==='per_floor'?'Area per floor':'Total building area (recommended)'}</button>)}</div>
  <div className="field-grid">
   <Field fieldKey="area" required label={basis==='per_floor'?'Average floor area':'Total building floor area'} hint={basis==='per_floor'?'Enter the average area of one residential floor. We multiply it by the number of floors once.':'Enter the combined area of all residential floors, including shared corridors. We do not multiply this total again.'} help="Use consistent drawings or measured area. The estimate separates assumed residential apartment space from common/service areas.">
    <div className="area-control"><NumberInput min={1} value={entered} onValueChange={value=>onChange({entered_area:value})}/><select aria-label="Floor area unit" value={p.area_unit} onChange={e=>onChange({area_unit:e.target.value})}><option>m²</option><option>ft²</option></select></div>
   </Field>
   <Field fieldKey="floors" required label="Number of floors" hint="Count residential storeys across the building, for example 20 or 50." help="Required for the building geometry. With per-floor entry, it also determines the total area used for the occupancy estimate."><NumberInput min={1} max={100} step={1} value={p.floors} onValueChange={value=>onChange({floors:value as number})}/></Field>
  </div>
  <div className="apartment-area-total" role="status">{p.area>0?<><b>Whole-building floor area: {format(p.area)} {p.area_unit}</b><span>{basis==='per_floor'?`${format(entered!)} ${p.area_unit} × ${p.floors} floors`:'Already includes every floor'}</span></>:<span>Enter an area and a whole floor count to calculate the building total.</span>}</div>
  <div className="occupancy-estimate apartment-occupancy">
   <Field fieldKey="occupants" required label={automatic?'Estimated number of occupants':'Number of occupants'} help="The estimate uses residential area, an assumed average apartment size and a dated dwelling-level modelling relationship. It is not legal capacity. Bill consumption determines utility costs." hint={automatic?'A planning estimate across the whole building. Enter the actual count whenever it is known.':'Your manual count stays unchanged when area or floors change.'}>
    <NumberInput min={1} max={100000} step={1} readOnly={automatic} value={p.occupants} onValueChange={value=>onChange({occupants:value as number,occupant_mode:'manual'})}/>
   </Field>
   <button type="button" className="text-link" onClick={()=>onChange({occupant_mode:automatic?'manual':'estimate'})}>{automatic?'Enter actual number':'Use automatic estimate'}</button>
   {estimate&&<p className="small-note">{format(estimate.residentialArea)} m² estimated apartment space ÷ {format(p.apartment_average_unit_m2??75)} m² per apartment × {estimate.perUnit.toFixed(2)} people per apartment. Rounded to {estimate.occupants.toLocaleString('en-AU')} people. {automatic?'':'Your manual count is used instead.'}</p>}
   <details className="form-details"><summary>Review the occupancy assumptions</summary><p className="small-note">The defaults of 75 m² per apartment and 80% residential space are editable planning assumptions, not official Sydney density standards. The dwelling-level relationship comes from NSW BASIX energy guidance dated August 2022. Confirm the actual apartment mix before relying on this estimate.</p>
    <div className="field-grid"><Field fieldKey="apartment_average_unit_m2" label="Average apartment size (m²)" required hint="Apartment interiors only; default 75 m² is illustrative."><NumberInput min={20} max={500} value={average} onValueChange={value=>onChange({apartment_average_unit_m2:value as number})}/></Field><Field fieldKey="apartment_residential_share" label="Area used by apartments (%)" required hint="Exclude assumed corridors, lifts and other shared/service space."><NumberInput min={10} max={100} value={share==null?null:share*100} onValueChange={value=>onChange({apartment_residential_share:(value==null?null:value/100) as number})}/></Field></div>
    <a className="text-link" href={apartmentOccupancySource} target="_blank" rel="noreferrer">View NSW modelling source ↗</a>
   </details>
  </div>
 </>;
}
