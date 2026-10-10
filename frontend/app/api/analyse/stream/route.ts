export const dynamic='force-dynamic';
export const runtime='nodejs';

// This route is the only path that bypasses the backend's own Origin check, because it
// proxies the analysis stream. Enforcing the allow-list HERE (where the real browser is
// visible) is what stops scripts reaching the expensive endpoint without an Origin.

const ALLOWED=(process.env.ALLOWED_ORIGINS||'http://127.0.0.1:3000,http://localhost:3000')
  .split(',').map(o=>o.trim().replace(/\/+$/,'')).filter(Boolean);

// Bounded per-instance abuse protection. Serverless instances are ephemeral, so this
// caps bursts inside a warm instance; durable limits need a shared store (Upstash/Redis).
const WINDOW_MS=60_000;
const MAX_PER_WINDOW=30;
const MAX_BODY=256_000;
const hits=new Map<string,number[]>();
function limited(ip:string){
  const now=Date.now();
  const recent=(hits.get(ip)??[]).filter(t=>now-t<WINDOW_MS);
  if(recent.length>=MAX_PER_WINDOW){hits.set(ip,recent);return true;}
  recent.push(now);hits.set(ip,recent);
  if(hits.size>5000){for(const [key,list] of hits){if(!list.some(t=>now-t<WINDOW_MS))hits.delete(key);}}
  return false;
}
function clientIp(request:Request){
  // Vercel sets this from the edge; the left-most entry is the originating client.
  const forwarded=request.headers.get('x-forwarded-for');
  return forwarded?.split(',')[0]?.trim()||request.headers.get('x-real-ip')||'unknown';
}
export async function POST(request:Request){
  const origin=request.headers.get('origin');
  // The browser always sends Origin on a same-origin POST. If it is missing or unknown,
  // this is not our frontend talking — reject before spending any compute.
  if(!origin||!ALLOWED.includes(origin.replace(/\/+$/,''))){
    return Response.json({detail:'This website is not an allowed origin.'},{status:403});
  }
  if(limited(clientIp(request)))return Response.json({detail:'Too many requests. Wait a minute and try again.'},{status:429,headers:{'Retry-After':'60'}});
  const base=process.env.GREENCOST_API_URL||'http://127.0.0.1:8000';
  try{
    const body=await request.text();
    if(new TextEncoder().encode(body).length>MAX_BODY)return Response.json({detail:'Project inputs are too large.'},{status:413});
    const response=await fetch(base+'/api/analyse/stream',{method:'POST',headers:{'Content-Type':'application/json',Origin:origin},body,signal:request.signal,cache:'no-store'});
    return new Response(response.body,{status:response.status,headers:{'Content-Type':response.headers.get('Content-Type')||'application/json','Cache-Control':'no-cache, no-transform','X-Accel-Buffering':'no'}});
  }catch{return Response.json({detail:'The calculator connection is unavailable. Your draft is preserved.'},{status:503});}
}
