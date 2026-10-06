'use client';
import {useEffect,useRef,useState,type InputHTMLAttributes} from 'react';

/** Preserve the editing string, including an empty field and partial decimals. */
export default function NumberInput({value,onValueChange,...props}:Omit<InputHTMLAttributes<HTMLInputElement>,'value'|'onChange'> & {value:number|null|undefined;onValueChange:(value:number|null)=>void}){
 const [draft,setDraft]=useState(value==null?'':String(value));
 const editing=useRef(false),last=useRef(value);
 useEffect(()=>{if(!editing.current||value!==last.current){setDraft(value==null?'':String(value));last.current=value;}},[value]);
 return <input {...props} type="number" step={props.step??'any'} value={draft}
  onFocus={e=>{editing.current=true;props.onFocus?.(e);}}
  onChange={e=>{const next=e.target.value;setDraft(next);const parsed=next===''?null:Number(next);if(parsed===null||Number.isFinite(parsed)){last.current=parsed;onValueChange(parsed);}}}
  onBlur={e=>{editing.current=false;setDraft(value==null?'':String(value));props.onBlur?.(e);}}/>;
}
