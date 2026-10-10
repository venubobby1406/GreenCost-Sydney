export function providerStatus(status:string|undefined,configured:boolean,enabled=true){
 if(!enabled||status==='disabled')return 'Off for this comparison';
 const labels:Record<string,string>={complete:'Request succeeded',free_model_required:'Choose an OpenRouter free model',time_limit:'Fallback time limit reached',invalid_model:'Check configured model name',not_configured:'Key not configured',provider_busy:'Provider busy — try again later',quota_reached:'Provider quota reached',invalid_key:'Key rejected — check configuration',permission_denied:'Key permissions need attention',model_unavailable:'Configured model unavailable',unavailable:'Request unavailable — retry when connected',invalid_output:'Response could not be used',rejected_response:'Provider responded; content checks failed — calculated explanation shown',incomplete_response:'Provider returned incomplete text — calculated explanation shown',empty_response:'Provider returned no text',not_requested:'Off for this comparison',budget_or_host_limit:'App request limit or hosted setting reached',empty:'No usable research returned'};
 return status?(labels[status]??'Request did not return usable research'):configured?'Key configured — no request verified yet':'Optional — key not configured';
}
export const retryableProvider=(status:string|undefined)=>['unavailable','provider_busy','invalid_output','rejected_response','incomplete_response','empty_response','empty'].includes(status??'');

/** Short badge label for a full provider status string. Full text stays in `title`. */
export function shortStatus(status:string):string{
  if(status==='Ready'||status==='Checking connection')return status;
  if(status==='Request succeeded')return 'Succeeded';
  if(status==='Key configured — no request verified yet')return 'Configured';
  if(status==='Fetching from Tavily…')return 'Fetching…';
  if(status==='Trying OpenRouter → Groq → Gemini; outcome pending')return 'Pending';
  if(status==='Off for this comparison'||status==='Not needed / not called'||status==='Off')return 'Off';
  if(status==='Key not configured'||status==='Optional — key not configured')return 'Not configured';
  if(status==='Waiting for its stage'||status==='Waiting for explanation stage'||status==='Waiting')return 'Waiting';
  if(/busy|quota|limit|unavailable|retry|check|reject|fail|could not|did not|no usable|choose|attention/i.test(status))return 'Needs attention';
  return status.length>24?status.slice(0,24)+'…':status;
}

const CALM='Off for this comparison|Key not configured|Optional — key not configured|Not needed / not called|Waiting for its stage|Waiting for explanation stage|Trying OpenRouter → Groq → Gemini; outcome pending';
const GOOD='Request succeeded|Key configured — no request verified yet|Fetching from Tavily…';
const BAD='Choose an OpenRouter free model|Fallback time limit reached|Check configured model name|Provider busy — try again later|Provider quota reached|Key rejected — check configuration|Key permissions need attention|Configured model unavailable|Request unavailable — retry when connected|Response could not be used|Provider responded; content checks failed — calculated explanation shown|Provider returned incomplete text — calculated explanation shown|Provider returned no text|Request did not return usable research|No usable research returned|App request limit or hosted setting reached';
/** Maps a provider status string to a badge tone so states are scannable at a glance. */
export function statusTone(status:string):'neutral'|'accent'|'warning'|'danger'{
  if(GOOD.includes(status))return 'accent';
  if(BAD.includes(status))return 'warning';
  if(CALM.includes(status))return 'neutral';
  return 'neutral';
}
