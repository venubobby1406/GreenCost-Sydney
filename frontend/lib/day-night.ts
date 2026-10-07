// A decorative cycle, not a prediction of local sunrise or astronomical motion.
export const dayNightSeconds=36;
export const moonPhases=['New moon','Waxing crescent','First quarter','Waxing gibbous','Full moon','Waning gibbous','Last quarter','Waning crescent'] as const;
export function skyCycle(elapsed:number){
 const angle=Math.PI/4+elapsed/dayNightSeconds*Math.PI*2;
 const altitude=Math.sin(angle),daylight=Math.max(0,Math.min(1,(altitude+.2)/.65));
 const phaseIndex=(Math.floor(elapsed/dayNightSeconds)+1)%moonPhases.length;
 return {angle,daylight,night:altitude<0,sunVisible:altitude>.025,moonVisible:altitude<-.025&&phaseIndex!==0,phaseAngle:phaseIndex*Math.PI/4,moonPhase:moonPhases[phaseIndex]};
}
