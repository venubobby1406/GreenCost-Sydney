export const dynamic='force-dynamic';
export const runtime='nodejs';
export async function POST(request:Request){
 const base=process.env.GREENCOST_API_URL||'http://127.0.0.1:8000';
 try{
  const body=await request.text();
  if(new TextEncoder().encode(body).length>256000)return Response.json({detail:'Project inputs are too large.'},{status:413});
  const response=await fetch(base+'/api/analyse/stream',{method:'POST',headers:{'Content-Type':'application/json'},body,signal:request.signal,cache:'no-store'});
  return new Response(response.body,{status:response.status,headers:{'Content-Type':response.headers.get('Content-Type')||'application/json','Cache-Control':'no-cache, no-transform','X-Accel-Buffering':'no'}});
 }catch{return Response.json({detail:'The calculator connection is unavailable. Your draft is preserved.'},{status:503});}
}
