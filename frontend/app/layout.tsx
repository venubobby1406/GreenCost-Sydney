import type { Metadata } from 'next';
import './globals.css';
import './fonts.css';
import './landing.css';
import './rebuild.css';
import './client-refresh.css';
export const metadata:Metadata={title:'GreenCost — Build better. Spend smarter.',description:'An auditable life-cycle cost comparison of conventional and sustainable buildings under Sydney conditions.',icons:{icon:'/favicon.svg'}};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="en-AU"><body>{children}</body></html>;}
