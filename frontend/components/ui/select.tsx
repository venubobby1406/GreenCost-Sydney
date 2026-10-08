'use client';
import {Children,isValidElement,useEffect,useId,useRef,useState,type ChangeEvent,type ReactElement,type SelectHTMLAttributes} from 'react';
import {Check,ChevronDown} from 'lucide-react';

/** Origin-aware selection menu. Retains a native select for form validation. */
export default function Select({children,onChange,value,className='',id,...props}:SelectHTMLAttributes<HTMLSelectElement>){
 const generated=useId(),controlId=id??generated,listId=controlId+'-options';
 const root=useRef<HTMLDivElement>(null),native=useRef<HTMLSelectElement>(null),trigger=useRef<HTMLButtonElement>(null);
 const [open,setOpen]=useState(false),[cursor,setCursor]=useState(0),typeahead=useRef({text:'',time:0});
 const options=Children.toArray(children).filter(isValidElement).map(node=>{const option=node as ReactElement<{value?:string|number;children?:string;disabled?:boolean}>;return {value:String(option.props.value??option.props.children??''),label:String(option.props.children??''),disabled:!!option.props.disabled};});
 const current=Math.max(0,options.findIndex(option=>option.value===String(value))),selected=options[current];
 useEffect(()=>{if(!open)return;const close=(event:PointerEvent)=>{if(!root.current?.contains(event.target as Node))setOpen(false);};document.addEventListener('pointerdown',close);return()=>document.removeEventListener('pointerdown',close);},[open]);
 function choose(index:number){const option=options[index];if(!option||option.disabled||!native.current)return;native.current.value=option.value;onChange?.({target:native.current,currentTarget:native.current} as ChangeEvent<HTMLSelectElement>);setOpen(false);trigger.current?.focus();}
 function move(direction:number){let next=cursor;for(let i=0;i<options.length;i++){next=(next+direction+options.length)%options.length;if(!options[next].disabled)break;}setCursor(next);}
 return <div ref={root} className={'ui-select '+className} onBlur={event=>{if(!event.currentTarget.contains(event.relatedTarget))setOpen(false);}}>
  <select {...props} ref={native} value={value} onChange={onChange} tabIndex={-1} aria-hidden="true" className="ui-select-native">{children}</select>
  <button ref={trigger} id={controlId} type="button" role="combobox" aria-label={props['aria-label']} aria-describedby={props['aria-describedby']} aria-invalid={props['aria-invalid']} aria-required={props.required} aria-expanded={open} aria-controls={listId} aria-haspopup="listbox" aria-activedescendant={open?listId+'-'+cursor:undefined} disabled={props.disabled} data-field-key={(props as Record<string,unknown>)['data-field-key']} onClick={()=>{setCursor(current);setOpen(!open);}} onKeyDown={event=>{
   if(event.key==='Escape'){setOpen(false);return;}
   if(['ArrowDown','ArrowUp','Home','End'].includes(event.key)){event.preventDefault();if(!open){setCursor(current);setOpen(true);}else if(event.key==='Home')setCursor(0);else if(event.key==='End')setCursor(options.length-1);else move(event.key==='ArrowDown'?1:-1);}
   else if(event.key==='Enter'||event.key===' '){event.preventDefault();if(open)choose(cursor);else{setCursor(current);setOpen(true);}}
   else if(event.key.length===1&&!event.ctrlKey&&!event.metaKey){const now=Date.now(),text=(now-typeahead.current.time<600?typeahead.current.text:'')+event.key.toLowerCase();typeahead.current={text,time:now};const match=options.findIndex(option=>!option.disabled&&option.label.toLowerCase().startsWith(text));if(match>=0){setCursor(match);if(!open)choose(match);}}
  }} className="ui-select-trigger"><span>{selected?.label}</span><ChevronDown size={16}/></button>
  {open&&<div id={listId} role="listbox" aria-label={props['aria-label']} className="ui-select-menu">{options.map((option,index)=><div id={listId+'-'+index} key={option.value} role="option" aria-selected={String(value)===option.value} aria-disabled={option.disabled} className={cursor===index?'is-highlighted':''} onPointerMove={()=>{if(!option.disabled)setCursor(index);}} onMouseDown={event=>event.preventDefault()} onClick={()=>choose(index)}><span>{option.label}</span>{String(value)===option.value&&<Check size={15}/>}</div>)}</div>}
 </div>;
}
