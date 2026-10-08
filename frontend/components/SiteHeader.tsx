'use client';
import Link from 'next/link';
import {usePathname} from 'next/navigation';
import {useRef,useState} from 'react';
import {ArrowUpRight,Layers3,Menu,X} from 'lucide-react';
export default function SiteHeader({compare=false}:{compare?:boolean}){
 const path=usePathname(),[open,setOpen]=useState(false),menuButton=useRef<HTMLButtonElement>(null);
 return <header className="landing-header" onKeyDown={event=>{if(event.key==='Escape'&&open){setOpen(false);menuButton.current?.focus();}}}><Link href="/" className="landing-brand" aria-label="GreenCost home"><span><Layers3 size={24}/></span><b>greencost</b></Link><nav id="site-navigation" className={open?'is-open':''} aria-label="Main navigation"><Link href="/#how-it-works" onClick={()=>setOpen(false)}>How it works</Link><Link href="/compare" aria-current={path==='/compare'?'page':undefined} onClick={()=>setOpen(false)}>Compare</Link><Link href="/methodology" aria-current={path==='/methodology'?'page':undefined} onClick={()=>setOpen(false)}>Method & evidence</Link></nav><div className="header-actions"><Link href="/compare" className="header-cta">{compare?'Your comparison':'Start comparison'} <ArrowUpRight size={15}/></Link><button ref={menuButton} type="button" className="navigation-toggle" aria-label={open?'Close navigation':'Open navigation'} aria-expanded={open} aria-controls="site-navigation" onClick={()=>setOpen(!open)}>{open?<X size={20}/>:<Menu size={20}/>}</button></div></header>;
}
