'use client';
import {Children,cloneElement,createContext,isValidElement,useContext,useId,useState,type ReactElement,type ReactNode} from 'react';
import {Info} from 'lucide-react';
import NumberInput from './NumberInput';

export const ValidationContext=createContext<{errors:Record<string,string>;clear:(key:string)=>void}>({errors:{},clear:()=>{}});

/** One accessible label, help popover and inline error for every control. */
export default function FormField({label,hint,help,required=false,fieldKey,children}:{label:string;hint?:string;help?:string;required?:boolean;fieldKey?:string;children:ReactNode}){
 const generated=useId(),key=fieldKey??generated,id='field-'+key.replace(/[^a-zA-Z0-9_-]/g,'');
 const {errors,clear}=useContext(ValidationContext),error=errors[key];const [open,setOpen]=useState(false);
 let wired=false;
 function wire(nodes:ReactNode):ReactNode{return Children.map(nodes,node=>{
  if(!isValidElement(node))return node;
  const element=node as ReactElement<Record<string,unknown>>;
  if(!wired&&(element.type===NumberInput||['input','select','textarea'].includes(String(element.type)))){
   wired=true;const oldChange=element.props.onChange as ((event:unknown)=>void)|undefined,oldValue=element.props.onValueChange as ((value:number|null)=>void)|undefined;
   return cloneElement(element,{id,name:key,'data-field-key':key,'data-field-label':label,'aria-label':label,'aria-invalid':!!error,'aria-describedby':[hint?id+'-hint':'',help?id+'-help':'',error?id+'-error':''].filter(Boolean).join(' ')||undefined,required,
    ...(oldChange?{onChange:(event:unknown)=>{clear(key);oldChange(event);}}:{}),...(oldValue?{onValueChange:(value:number|null)=>{clear(key);oldValue(value);}}:{})});
  }
  return element.props.children?cloneElement(element,{children:wire(element.props.children as ReactNode)}):element;
 });}
 return <div className={'field '+(error?'has-error':'')}><div className="field-label"><label htmlFor={id}>{label}{required&&<span className="required-mark" aria-hidden="true"> *</span>}</label>{help&&<span className="field-help"><button type="button" aria-label={'Why we ask for '+label} aria-expanded={open} aria-controls={id+'-help'} onClick={()=>setOpen(v=>!v)} onKeyDown={e=>{if(e.key==='Escape')setOpen(false);}}><Info size={15}/></button><span id={id+'-help'} className="help-content" role="tooltip" data-open={open}>{help}</span></span>}</div>{wire(children)}{hint&&<small id={id+'-hint'}>{hint}</small>}{error&&<small id={id+'-error'} className="inline-field-error">{error}</small>}</div>;
}

export function focusField(key:string){
 const element=[...document.querySelectorAll<HTMLElement>('[data-field-key]')].find(e=>e.dataset.fieldKey===key);
 if(!element)return;
 let parent=element.parentElement;while(parent){if(parent instanceof HTMLDetailsElement)parent.open=true;parent=parent.parentElement;}
 element.focus();element.scrollIntoView({block:'center',behavior:'auto'});
}

export function nativeErrors(form:HTMLFormElement){
 const errors:Record<string,string>={};
 for(const element of Array.from(form.elements)){
  if(!(element instanceof HTMLInputElement||element instanceof HTMLSelectElement||element instanceof HTMLTextAreaElement)||element.disabled||!element.dataset.fieldKey||element.validity.valid)continue;
  const label=element.dataset.fieldLabel??'this value';
  errors[element.dataset.fieldKey]=element.validity.valueMissing?'Please enter '+label.toLowerCase()+'.':element.validity.rangeUnderflow?'Use a value of at least '+(element as HTMLInputElement).min+'.':element.validity.rangeOverflow?'Use a value no higher than '+(element as HTMLInputElement).max+'.':element.validity.stepMismatch?'Enter a whole number.':element.validity.patternMismatch?'Enter a valid four-digit Sydney postcode.':'Check this value.';
 }
 return errors;
}
