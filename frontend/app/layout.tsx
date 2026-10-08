import type { Metadata } from 'next';
import './globals.css';
import './fonts.css';
import './landing.css';
import './rebuild.css';
import './client-refresh.css';
import './component-refresh.css';
import './tensor-theme.css';
import {themeInitialization} from '@/lib/theme-initialization';
export const metadata:Metadata={title:'GreenCost — Build better. Spend smarter.',description:'An auditable life-cycle cost comparison of conventional and sustainable buildings under Sydney conditions.',icons:{icon:'/favicon.svg'}};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="en-AU" suppressHydrationWarning><head>{/* Static bootstrap prevents a theme flash; it contains no user-supplied data. */}
 <link rel="preconnect" href="https://cdn.fontshare.com" crossOrigin="anonymous"/>
 {/* eslint-disable-next-line react/no-danger */}
 <script dangerouslySetInnerHTML={{__html:themeInitialization}}/>
 </head><body>{children}</body></html>;}
