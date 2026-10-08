'use client';
// Adapted from EasyUI DrawCheckbox (MIT). See THIRD_PARTY_NOTICES.md.
import {forwardRef,useState,type InputHTMLAttributes} from 'react';
import {motion,useReducedMotion} from 'framer-motion';

export const DrawCheckbox=forwardRef<HTMLInputElement,Omit<InputHTMLAttributes<HTMLInputElement>,'type'>>(function DrawCheckbox({checked,defaultChecked,onChange,className='',...props},ref){
 const [internal,setInternal]=useState(!!defaultChecked),reduced=useReducedMotion();
 const active=checked??internal;
 return <span className={'ui-checkbox '+className}>
  <input {...props} ref={ref} type="checkbox" checked={active} onChange={event=>{setInternal(event.target.checked);onChange?.(event);}}/>
  <motion.span className="ui-checkbox-box" aria-hidden="true" initial={false} animate={{scale:active&&!reduced?[.9,1.06,1]:1}} transition={{duration:reduced?0:.25}}>
   <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><motion.path d="M3.5 8 L6.5 11 L12.5 5" initial={false} animate={{pathLength:active?1:0,opacity:active?1:0}} transition={{duration:reduced?0:.2}}/></svg>
  </motion.span>
 </span>;
});
