'use client';
import Link from 'next/link';
export default function ErrorPage({reset}:{reset:()=>void}){return <main className="method-page"><h1>Let’s try that again.</h1><p>The page could not finish loading. Your downloaded projects are safe.</p><button onClick={reset}>Reload this page</button><p><Link href="/">Return to GreenCost</Link></p></main>;}
