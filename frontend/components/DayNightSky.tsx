'use client';
import {useEffect,useMemo,useRef,type RefObject} from 'react';
import {useFrame,useThree} from '@react-three/fiber';
import * as THREE from 'three';
import {skyCycle} from '@/lib/day-night';

type Props={floors:number;paused:boolean;host:RefObject<HTMLDivElement|null>;onNightChange:(night:boolean)=>void};
export default function DayNightSky({floors,paused,host,onNightChange}:Props){
 const {camera}=useThree();
 const sun=useRef<THREE.Group>(null),moon=useRef<THREE.Group>(null);
 const clouds=useRef<THREE.Group>(null);
 const ambient=useRef<THREE.AmbientLight>(null),key=useRef<THREE.DirectionalLight>(null),hemisphere=useRef<THREE.HemisphereLight>(null);
 const elapsed=useRef(0),lastNight=useRef<boolean|null>(null);
 const colour=useRef(new THREE.Color()),offset=useRef(new THREE.Vector3());
 const day=useRef(new THREE.Color('#eef4ee')),night=useRef(new THREE.Color('#172c42'));
 const cloudMaterial=useMemo(()=>new THREE.MeshBasicMaterial({color:'#fcfdf9'}),[]);
 const cloudDay=useMemo(()=>new THREE.Color('#fcfdf9'),[]),cloudNight=useMemo(()=>new THREE.Color('#455d78'),[]);
 useEffect(()=>()=>cloudMaterial.dispose(),[cloudMaterial]);
 const moonMaterial=useMemo(()=>new THREE.ShaderMaterial({
  uniforms:{phase:{value:Math.PI/4}},
  vertexShader:`varying vec2 moonUv; void main(){moonUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,
  fragmentShader:`
   uniform float phase; varying vec2 moonUv;
   void main(){
    vec2 p=moonUv*2.0-1.0;
    float radius2=dot(p,p); if(radius2>1.0)discard;
    vec3 normal=vec3(p,sqrt(max(0.0,1.0-radius2)));
    vec3 lightDirection=vec3(sin(phase),0.0,-cos(phase));
    float light=smoothstep(-0.04,0.07,dot(normal,lightDirection));
    float crater=1.0;
    crater-=0.14*(1.0-smoothstep(0.10,0.17,length(p-vec2(-0.31,0.29))));
    crater-=0.12*(1.0-smoothstep(0.15,0.22,length(p-vec2(0.24,-0.34))));
    crater-=0.10*(1.0-smoothstep(0.07,0.13,length(p-vec2(0.42,0.33))));
    vec3 colour=mix(vec3(0.12,0.19,0.27),vec3(0.88,0.93,0.98)*crater,light);
    gl_FragColor=vec4(colour,1.0);
   }`,
 }),[]);
 useEffect(()=>()=>moonMaterial.dispose(),[moonMaterial]);
 useEffect(()=>()=>{if(host.current)host.current.style.background='';},[host]);
 useFrame((_,delta)=>{
  if(!paused)elapsed.current+=Math.min(delta,.1);
  const state=skyCycle(elapsed.current);
  moonMaterial.uniforms.phase.value=state.phaseAngle;
  if(lastNight.current!==state.night){lastNight.current=state.night;onNightChange(state.night);}
  const centreY=Math.min(4,Math.max(1,Math.round(floors)))*1.35/2;
  cloudMaterial.color.copy(cloudNight).lerp(cloudDay,state.daylight);
  if(clouds.current){
   clouds.current.children.forEach((cloud,index)=>{
    const baseX=[-3.4,3.5,-.8][index],baseY=[2.6,2.8,3.8][index];
    offset.current.set(baseX+Math.sin(elapsed.current*.06+index)*.3,baseY+Math.max(0,Math.round(floors)-2)*.45,-1).applyQuaternion(camera.quaternion);
    cloud.position.set(0,centreY,1.3).add(offset.current);
    cloud.quaternion.copy(camera.quaternion);
   });
  }
  // Camera-facing sky plane keeps the bodies above the scene when dragged.
  // The moon is always half a cycle behind the sun; only the rising body is shown.
  for(const [body,angle,visible] of [[sun.current,state.angle,state.sunVisible],[moon.current,state.angle+Math.PI,state.moonVisible]] as const){
   if(!body)continue;
   body.visible=visible;
   offset.current.set(Math.cos(angle)*3.5,1.9+Math.max(0,Math.round(floors)-2)*.45+Math.sin(angle)*1.3,0).applyQuaternion(camera.quaternion);
   body.position.set(0,centreY,1.3).add(offset.current);
   body.quaternion.copy(camera.quaternion);
  }
  if(ambient.current)ambient.current.intensity=.8+state.daylight*1.2;
  if(hemisphere.current)hemisphere.current.intensity=.6+state.daylight*.9;
  if(key.current){key.current.intensity=.7+state.daylight*1.8;key.current.color.set(state.night?'#a9c7ef':'#fff2cc');key.current.position.set(Math.cos(state.angle)*6,4+Math.abs(Math.sin(state.angle))*5,5);}
  if(host.current){
   const sky=colour.current.copy(night.current).lerp(day.current,state.daylight).getStyle();
   host.current.style.background=sky;
   const panel=host.current.closest<HTMLElement>('.world-panel');
   if(panel)panel.style.background=sky;
  }
 });
 return <>
  <ambientLight ref={ambient} intensity={2}/><hemisphereLight ref={hemisphere} args={['#fff9e8','#728068',1.5]}/><directionalLight ref={key} position={[4,8,5]} intensity={2.5}/>
  <group ref={sun}><mesh><sphereGeometry args={[.27,24,16]}/><meshBasicMaterial color="#ffce66"/></mesh>{Array.from({length:8},(_,i)=><mesh key={i} rotation={[0,0,i*Math.PI/4]}><boxGeometry args={[.035,.84,.025]}/><meshBasicMaterial color="#efb951"/></mesh>)}</group>
  <group ref={moon} visible={false}><mesh material={moonMaterial}><circleGeometry args={[.34,64]}/></mesh></group>
  <group ref={clouds}>{[1,.8,.65].map((scale,index)=><group key={index} scale={scale}>{[[-.28,0,.21],[0,.1,.29],[.3,0,.22]].map(([x,y,r],i)=><mesh key={i} position={[x,y,0]} scale={[1,.7,.5]} material={cloudMaterial}><sphereGeometry args={[r,16,10]}/></mesh>)}</group>)}</group>
 </>;
}
