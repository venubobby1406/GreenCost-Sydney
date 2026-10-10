import type { NextConfig } from 'next';
const config: NextConfig = {
  async rewrites() { return [{source: '/api/:path*', destination: (process.env.GREENCOST_API_URL || 'http://127.0.0.1:8000') + '/api/:path*'}]; },
  devIndicators: false,
  poweredByHeader: false,
  async headers() { return [
    {source:'/:path*',headers:[
      {key:'X-Content-Type-Options',value:'nosniff'},
      {key:'Referrer-Policy',value:'strict-origin-when-cross-origin'},
      {key:'X-Frame-Options',value:'DENY'},
      {key:'Permissions-Policy',value:'camera=(), microphone=(), geolocation=()'},
      {key:'Strict-Transport-Security',value:'max-age=63072000; includeSubDomains; preload'},
      // 'unsafe-inline' is required by Next.js hydration and the static theme bootstrap
      // script. Everything else is locked to self so injected scripts cannot phone home.
      {key:'Content-Security-Policy',value:"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data: https://cdn.fontshare.com; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; object-src 'none'"},
    ]},
    // API responses must never be cached by a shared proxy.
    {source:'/api/:path*',headers:[{key:'Cache-Control',value:'no-store'}]},
  ]; },
};
export default config;
