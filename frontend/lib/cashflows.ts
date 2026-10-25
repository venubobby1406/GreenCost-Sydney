type CashflowPoint = {year:number;cumulative_pv:number};
type Comparison = {
 conventional:{cashflows:CashflowPoint[]};
 sustainable:{cashflows:CashflowPoint[]};
 break_even_year:number|null;
};

/** Positive advantage means the sustainable design has cost less so far. */
export function compareCashflows(period:Comparison){
 return period.conventional.cashflows.map((row,index)=>{
  const advantage=row.cumulative_pv-period.sustainable.cashflows[index].cumulative_pv;
  return {
   advantage,
   tone:advantage>0.5?'is-saving':advantage<-0.5?'is-cost':'is-neutral',
   breakEven:row.year===period.break_even_year,
  };
 });
}
