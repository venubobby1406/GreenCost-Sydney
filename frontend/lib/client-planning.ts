import type {Project} from './types';

export const draftKey='greencost-draft-v3';
export type FormPosition={step:number;review:boolean;period:'annual'|'monthly';zeroConfirmed:boolean};
export const defaultPosition:FormPosition={step:0,review:false,period:'annual',zeroConfirmed:false};
export function suggestedOccupants(area:number,unit:string){
 const m2=area*(unit==='ft²'?0.092903:1);
 if(!Number.isFinite(m2)||m2<=0)return null;
 // Published NSW BASIX energy occupancy assumption, August 2022.
 // All dwelling floors combined, excluding garage; not an occupancy capacity rule.
 return Math.round(Math.min(6,Math.max(1,1.525*Math.log(m2)-4.533)));
}
export const apartmentOccupancySource='https://www.planningportal.nsw.gov.au/sites/default/files/documents/2022/BASIX%20standard%20occupancy%20-%20version%204%20-%2023.08.22%20LMv5.pdf';
export function apartmentOccupancy(area:number,unit:string,averageUnit=75,residentialShare=.8){
 const m2=area*(unit==='ft²'?.092903:1);
 if(!Number.isFinite(m2)||m2<=0||!Number.isFinite(averageUnit)||averageUnit<20||averageUnit>500||!Number.isFinite(residentialShare)||residentialShare<.1||residentialShare>1)return null;
 const perUnit=Math.min(6,Math.max(1,1.525*Math.log(averageUnit)-4.533)),residentialArea=m2*residentialShare,dwellings=residentialArea/averageUnit;
 return {occupants:Math.max(1,Math.round(dwellings*perUnit)),residentialArea,dwellings,perUnit,density:averageUnit/(residentialShare*perUnit)};
}
export function updateApartmentProject(project:Project,changes:Partial<Project>):Project{
 const next={...project,...changes};
 if(next.building_type!=='Apartment Building')return project.building_type==='Apartment Building'?{...next,area_basis:'total',entered_area:null}:next;
 const basis=next.area_basis??'total',entered=next.entered_area??(basis==='total'&&!('entered_area' in changes)?next.area:null);
 next.area=(entered!=null&&Number.isFinite(entered)&&entered>0&&(basis==='total'||Number.isInteger(next.floors)&&next.floors>=1)?entered*(basis==='per_floor'?next.floors:1):null) as number;
 if(next.occupant_mode==='estimate')next.occupants=(apartmentOccupancy(next.area,next.area_unit,next.apartment_average_unit_m2===undefined?75:next.apartment_average_unit_m2,next.apartment_residential_share===undefined?.8:next.apartment_residential_share)?.occupants??null) as number;
 return next;
}
export function waterLabel(kl:number,period='year'){
 return `${(kl*1000).toLocaleString('en-AU',{maximumFractionDigits:2})} L/${period} · ${(kl/1000).toLocaleString('en-AU',{maximumFractionDigits:6})} million litres/${period}`;
}
export function restoreDraft(value:string|null):{project:Project;position:FormPosition}|null{
 if(!value||value.length>512000)return null;
 try{const d=JSON.parse(value);if(d.version!==3||!d.project||typeof d.project.postcode!=='string'||!['Residential House','Apartment','Apartment Building','Commercial / Other'].includes(d.project.building_type)||!Array.isArray(d.project.selected_measures)||!Array.isArray(d.project.materials))return null;
 const f=d.position;return {project:d.project,position:{step:[0,1,2].includes(f?.step)?f.step:0,review:f?.review===true,period:f?.period==='monthly'?'monthly':'annual',zeroConfirmed:f?.zeroConfirmed===true}};
 }catch{return null;}
}
