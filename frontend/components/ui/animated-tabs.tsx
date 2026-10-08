'use client';
// Adapted from EasyUI AnimatedTabs (MIT). See THIRD_PARTY_NOTICES.md.
import {useId,useRef,type ReactNode} from 'react';
import {motion,useReducedMotion} from 'framer-motion';

type Item={id:string;label:string;icon?:ReactNode;badge?:number};
export function AnimatedTabs({items,value,onChange,label,className='',panelId}:{items:Item[];value:string;onChange:(value:string)=>void;label:string;className?:string;panelId?:string}){
 const id=useId(),reduced=useReducedMotion(),buttons=useRef<(HTMLButtonElement|null)[]>([]);
 return <div className={'ui-pills '+className} role={panelId?'tablist':'group'} aria-label={label}>{items.map((item,index)=>{
  const active=item.id===value;
  return <button key={item.id} ref={node=>{buttons.current[index]=node;}} type="button" id={panelId?`${panelId}-tab-${index}`:undefined} role={panelId?'tab':undefined} aria-selected={panelId?active:undefined} aria-pressed={panelId?undefined:active} aria-controls={panelId} tabIndex={panelId&&!active?-1:0} onClick={()=>onChange(item.id)} onKeyDown={event=>{
   const next=event.key==='ArrowRight'?(index+1)%items.length:event.key==='ArrowLeft'?(index+items.length-1)%items.length:event.key==='Home'?0:event.key==='End'?items.length-1:-1;
   if(next>=0){event.preventDefault();onChange(items[next].id);buttons.current[next]?.focus();}
  }} className={active?'is-active':''}>
   {active&&<motion.span className="ui-pill-indicator" layoutId={id} transition={reduced?{duration:0}:{type:'spring',stiffness:420,damping:36}}/>}
   <span className="ui-pill-label">{item.icon}{item.label}{item.badge!==undefined&&<span className="ui-pill-count">{item.badge}</span>}</span>
  </button>;
 })}</div>;
}
