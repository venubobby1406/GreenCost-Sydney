import type { Metadata } from 'next';
import './globals.css';
import './landing.css';
export const metadata:Metadata={title:'GreenCost Sydney — Design Beyond Day One',description:'An auditable life-cycle cost comparison of conventional and sustainable buildings under Sydney conditions.',icons:{icon:'/favicon.svg'}};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="en-AU"><body>{children}</body></html>;}
