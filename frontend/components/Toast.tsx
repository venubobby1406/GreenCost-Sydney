'use client';
import {useEffect} from 'react';
import {CheckCircle2,X} from 'lucide-react';
export type Notice={message:string;id:number};
export default function Toast({notice,onDismiss}:{notice:Notice|null;onDismiss:()=>void}){
 useEffect(()=>{if(!notice)return;const timer=setTimeout(onDismiss,6000);return()=>clearTimeout(timer);},[notice,onDismiss]);
 if(!notice)return null;
 return <div className="toast" role="status" aria-live="polite"><CheckCircle2 size={19}/><span>{notice.message}</span><button type="button" onClick={onDismiss} aria-label="Dismiss notification"><X size={17}/></button></div>;
}
