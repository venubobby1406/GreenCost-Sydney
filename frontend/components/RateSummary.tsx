'use client';
import {useEffect,useState} from 'react';
import {api,type Project} from '@/lib/types';
export default function RateSummary({project:p}:{project:Project}){
 const [rates,setRates]=useState<Record<string,number>|null>(null),[error,setError]=useState(''),[retry,setRetry]=useState(0);
 const signature=JSON.stringify({zone:p.zone,building_type:p.building_type,price_date:p.price_date,water_connected:p.water_connected,wastewater_connected:p.wastewater_connected,stormwater:p.stormwater,drought_tariff:p.drought_tariff});
 useEffect(()=>{let active=true;setRates(null);setError('');if(!p.zone)return;api<{rates:Record<string,number>}>('/v1/reference-rates',JSON.parse(signature)).then(r=>{if(active)setRates(r.rates);}).catch(e=>{if(active)setError(e.message);});return()=>{active=false;};},[signature,retry,p.zone]);
 const display=p.rates_snapshot??rates;
 return <div className="actual-rates"><b>{p.rates_snapshot?'Captured rates from your saved project':p.zone?p.zone+' + Sydney Water':'Choose your distributor to see rates'}</b>{display?<dl><div><dt>Electricity usage</dt><dd>${display.electricity_rate.toFixed(4)}/kWh</dd></div><div><dt>Electricity supply</dt><dd>${display.electricity_daily.toFixed(2)}/day</dd></div><div><dt>Water usage</dt><dd>${display.water_rate.toFixed(2)}/kL</dd></div><div><dt>Fixed water services</dt><dd>${display.water_fixed.toFixed(2)}/year</dd></div></dl>:error?<p role="status">Rates could not load. <button type="button" className="text-link" onClick={()=>setRetry(v=>v+1)}>Retry rates</button></p>:p.zone?<p>Loading reference charges…</p>:null}<small>Reference date {p.price_date}. Residential reference charges, including GST; retailer bills can differ. {p.rates_snapshot?'Change a rate or connection setting to use current references.':''}</small></div>;
}
