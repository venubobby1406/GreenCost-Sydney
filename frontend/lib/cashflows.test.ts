import {describe,expect,it} from 'vitest';
import {compareCashflows} from './cashflows';

function comparison(conventional:number[],sustainable:number[],breakEvenYear:number|null){
 const points=(values:number[])=>values.map((cumulative_pv,year)=>({year,cumulative_pv}));
 return compareCashflows({conventional:{cashflows:points(conventional)},sustainable:{cashflows:points(sustainable)},break_even_year:breakEvenYear});
}

describe('cash-flow comparison',()=>{
 it('shows an upfront premium as extra cost until the engine break-even year',()=>{
  const rows=comparison([100,120,140,160],[110,125,140,155],2);
  expect(rows.map(r=>r.advantage)).toEqual([-10,-5,0,5]);
  expect(rows.map(r=>r.tone)).toEqual(['is-cost','is-cost','is-neutral','is-saving']);
  expect(rows.map(r=>r.breakEven)).toEqual([false,false,true,false]);
 });
 it('marks year zero when the sustainable design starts cheaper',()=>{
  const rows=comparison([100,120],[90,105],0);
  expect(rows[0]).toEqual({advantage:10,tone:'is-saving',breakEven:true});
  expect(rows[1].breakEven).toBe(false);
 });
 it('marks equality at year zero consistently with the calculation engine',()=>{
  expect(comparison([100,120],[100,115],0)[0]).toEqual({advantage:0,tone:'is-neutral',breakEven:true});
 });
 it('does not invent break-even when sustainable costs stay higher',()=>{
  const rows=comparison([100,120,140],[110,130,150],null);
  expect(rows.every(r=>r.advantage<0&&r.tone==='is-cost'&&!r.breakEven)).toBe(true);
 });
 it('does not label later reversals or recoveries as the first break-even',()=>{
  const rows=comparison([100,120,140,160,180],[110,115,145,155,175],1);
  expect(rows.map(r=>r.breakEven)).toEqual([false,true,false,false,false]);
  expect(rows[2]).toEqual({advantage:-5,tone:'is-cost',breakEven:false});
 });
 it('keeps sub-dollar differences neutral without changing the signed values',()=>{
  const rows=comparison([100,100,100],[99.75,100.25,100],0);
  expect(rows.map(r=>r.advantage)).toEqual([.25,-.25,0]);
  expect(rows.every(r=>r.tone==='is-neutral')).toBe(true);
 });
});
