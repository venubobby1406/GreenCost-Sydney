import type {Analysis} from './types';

export function downloadFile(content:Blob|string,filename:string,type='application/json'){
 const url=URL.createObjectURL(typeof content==='string'?new Blob([content],{type}):content);
 const link=document.createElement('a');link.href=url;link.download=filename;document.body.appendChild(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
export function reportFilename(name:string|undefined,years:number,pdf=false){
 const stem=(name??'').normalize('NFKC').replace(/[^\p{L}\p{N}_ -]/gu,'').replace(/^[ _-]+|[ _-]+$/g,'').slice(0,80).replace(/[ _-]+$/g,'').replace(/\s+/g,'-')||'GreenCost';
 return `${stem}-${years}-year-report.${pdf?'pdf':'html'}`;
}
export function downloadCSV(data:Analysis,years:number){
 const fields=['year','capital','energy','water','maintenance','replacement','other','disposal','residual','nominal_total','pv_total','cumulative_pv'];
 const rows=['scenario,'+fields.join(',')];
 for(const scenario of ['conventional','sustainable'] as const)for(const row of data.periods[String(years)][scenario].cashflows)rows.push([scenario,...fields.map(k=>String(row[k]))].join(','));
 downloadFile(rows.join('\r\n'),'GreenCost-cashflows.csv','text/csv;charset=utf-8');
}
export async function downloadReport(data:Analysis,years:number,pdf=false){
 const status=data.research_status,provider=status?.explanation_provider??(status?.gemini==='complete'?'gemini':'calculated');
 const commentary={years,provider:years===data.project.years?provider:'calculated',paragraphs:years===data.project.years?data.periods[String(years)].explanation.slice(4):[],evidence:data.evidence.slice(0,8).map(e=>({source:e.source,page:e.page||null,source_type:e.source_type,url:e.url??null,text:(e.text??'').slice(0,2000)})),statuses:Object.fromEntries(['openrouter','groq','gemini'].map(p=>[p,status?.[p as 'openrouter'|'groq'|'gemini']??'not_requested']))};
 const response=await fetch(pdf?'/api/report/pdf' :'/api/report',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({project:data.project,rates:data.rates,years,commentary})});
 if(!response.ok)throw new Error('Report could not be generated. Check the backend connection and retry.');
 downloadFile(await response.blob(),reportFilename(data.project.name,years,pdf));
}
export function shareURL(data:Analysis,years:number){
 const project={...data.project,years,rates_snapshot:data.rates,web_research:false};
 const bytes=new TextEncoder().encode(JSON.stringify(project));
 let binary='';for(const b of bytes)binary+=String.fromCharCode(b);
 const encoded=btoa(binary).replaceAll('+','-').replaceAll('/','_').replaceAll('=','');
 return window.location.origin+'/compare?project='+encoded;
}
