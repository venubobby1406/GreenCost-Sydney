import type {Analysis} from './types';

export function downloadFile(content:Blob|string,filename:string,type='application/json'){
 const url=URL.createObjectURL(typeof content==='string'?new Blob([content],{type}):content);
 const link=document.createElement('a');link.href=url;link.download=filename;document.body.appendChild(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
export function downloadCSV(data:Analysis,years:number){
 const fields=['year','capital','energy','water','maintenance','replacement','other','disposal','residual','nominal_total','pv_total','cumulative_pv'];
 const rows=['scenario,'+fields.join(',')];
 for(const scenario of ['conventional','sustainable'] as const)for(const row of data.periods[String(years)][scenario].cashflows)rows.push([scenario,...fields.map(k=>String(row[k]))].join(','));
 downloadFile(rows.join('\r\n'),'GreenCost-cashflows.csv','text/csv;charset=utf-8');
}
export async function downloadReport(data:Analysis,years:number,pdf=false){
 const response=await fetch(pdf?'/api/report/pdf':'/api/report',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({project:data.project,rates:data.rates,years})});
 if(!response.ok)throw new Error('Report could not be generated. Check the backend connection and retry.');
 downloadFile(await response.blob(),`GreenCost-${years}-year-report.${pdf?'pdf':'html'}`);
}
export function shareURL(data:Analysis,years:number){
 const project={...data.project,years,rates_snapshot:data.rates,web_research:false};
 const bytes=new TextEncoder().encode(JSON.stringify(project));
 let binary='';for(const b of bytes)binary+=String.fromCharCode(b);
 const encoded=btoa(binary).replaceAll('+','-').replaceAll('/','_').replaceAll('=','');
 return window.location.origin+'/?project='+encoded;
}
