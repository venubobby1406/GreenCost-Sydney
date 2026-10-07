import Link from 'next/link';
import {ArrowUpRight,Layers3} from 'lucide-react';
export default function SiteHeader({compare=false}:{compare?:boolean}){
 return <header className="landing-header"><Link href="/" className="landing-brand" aria-label="GreenCost home"><span><Layers3 size={24}/></span><b>greencost</b></Link><nav aria-label="Main navigation"><Link href="/#how-it-works">How it works</Link><Link href="/compare" aria-current={compare?'page':undefined}>Compare</Link><Link href="/methodology">Method & evidence</Link></nav><Link href="/compare" className="header-cta">{compare?'Your comparison':'Start comparison'} <ArrowUpRight size={15}/></Link></header>;
}
