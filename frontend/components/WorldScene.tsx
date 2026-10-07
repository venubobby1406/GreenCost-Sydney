'use client';
import {Component,useEffect,useRef,useState,type ReactNode} from 'react';
import {Canvas,useFrame,useThree} from '@react-three/fiber';
import {OrbitControls} from '@react-three/drei';
import {useReducedMotion} from 'framer-motion';
import * as THREE from 'three';
import RoadTraffic from './RoadTraffic';
import DayNightSky from './DayNightSky';
import {Sun,Moon,Pause,Play} from 'lucide-react';

function Fallback(){return <div className="world-fallback architectural-fallback"><span aria-hidden="true">⌂</span><b>A home, thoughtfully improved.</b><small>Compare better insulation, solar and water-saving upgrades.</small></div>;}
class Boundary extends Component<{children:ReactNode},{failed:boolean}>{state={failed:false};static getDerivedStateFromError(){return {failed:true};}render(){return this.state.failed?<Fallback/>:this.props.children;}}
function Box({position,size,color,glass=false}:{position:[number,number,number];size:[number,number,number];color:string;glass?:boolean}){return <mesh position={position} castShadow={!glass} receiveShadow><boxGeometry args={size}/><meshStandardMaterial color={color} roughness={glass?.18:.78} metalness={glass?.3:0}/></mesh>;}
function Tree({x,z}:{x:number;z:number}){return <group position={[x,0,z]}><mesh position={[0,.7,0]} castShadow><cylinderGeometry args={[.055,.08,1.4,8]}/><meshStandardMaterial color="#806954"/></mesh>{[[0,1.7,0,.65],[.3,1.9,.1,.5],[-.25,2,.1,.5],[0,2.35,0,.43]].map(([a,b,c,r],i)=><mesh key={i} position={[a,b,c]} castShadow><icosahedronGeometry args={[r,1]}/><meshStandardMaterial color={i%2?'#68845b':'#8ea17b'} flatShading/></mesh>)}</group>;}
function Home({floors,solar,reduced,night}:{floors:number;solar:boolean;reduced:boolean;night:boolean}){
 const scene=useRef<THREE.Group>(null),flow=useRef<THREE.Group>(null);const height=Math.min(4,Math.max(1,Math.round(floors)));
 useEffect(()=>{if(flow.current)flow.current.position.y=height*1.35+.3;},[height,solar]);
 useFrame(({clock})=>{if(reduced)return;if(scene.current)scene.current.rotation.y=Math.sin(clock.elapsedTime*.14)*.06;if(flow.current){flow.current.rotation.y=clock.elapsedTime*.2;flow.current.position.y=height*1.35+.3+Math.sin(clock.elapsedTime*.9)*.08;}});
 return <group ref={scene}>
  <Box position={[0,-.25,1.3]} size={[7.9,.4,9.9]} color="#acbc9c"/><Box position={[0,-.02,1.3]} size={[7.7,.12,9.7]} color="#d1ddbf"/>
  <RoadTraffic reduced={reduced} night={night}/>
  <Box position={[.9,.06,2]} size={[4,.08,1.8]} color="#e8dfce"/>
  {Array.from({length:height},(_,i)=><group key={i} position={[0,i*1.35,0]}>
   <Box position={[-1,.67,-.5]} size={[2.5,1.3,3.3]} color="#e9e2d3"/>
   <Box position={[1.4,.67,-.95]} size={[2.3,1.3,2.4]} color="#f6f0e5"/>
   <Box position={[.1,1.34,-.5]} size={[5.1,.12,3.55]} color="#657866"/>
   <Box position={[1.4,.7,.29]} size={[2.1,.95,.05]} color="#48695e" glass/>
   <Box position={[-1,.7,1.18]} size={[2.1,.9,.05]} color="#48695e" glass/>
   {Array.from({length:10},(_,n)=><Box key={n} position={[-2.02+n*.225,.7,1.32]} size={[.045,1.15,.17]} color="#ac885f"/>)}
   <Box position={[2.57,.75,-.8]} size={[.05,.9,1.6]} color="#668777" glass/>
  </group>)}
  <Box position={[.1,height*1.35+.07,-.5]} size={[4.8,.13,3.1]} color={solar?'#758e63':'#afaaa0'}/>
  {solar&&[-1.35,0,1.35].map(x=><group key={x} position={[x,height*1.35+.24,-.5]} rotation={[-.15,0,0]}><Box position={[0,0,0]} size={[1.12,.08,1.9]} color="#183c4d"/>{[-.37,0,.37].map(v=><Box key={v} position={[v,.047,0]} size={[.013,.01,1.85]} color="#7aa1a9"/>)}{[-.6,0,.6].map(v=><Box key={v} position={[0,.047,v]} size={[1.1,.01,.013]} color="#7aa1a9"/>)}</group>)}
  <Box position={[-.25,.06,2.8]} size={[1.5,.06,.3]} color="#c0b397"/><Box position={[-.25,.06,2.35]} size={[1.5,.06,.3]} color="#c0b397"/>
  <Tree x={-3.05} z={-.6}/><Tree x={3.1} z={1.8}/><Tree x={-2.9} z={2.2}/>
  {solar&&<><mesh position={[2.9,.7,-2]} castShadow><cylinderGeometry args={[.42,.42,1.4,24]}/><meshStandardMaterial color="#859989"/></mesh><group ref={flow}><mesh position={[0,0,0]} rotation={[-Math.PI/2,0,0]}><torusGeometry args={[3.4,.014,6,64]}/><meshBasicMaterial color="#b19b62" transparent opacity={.5}/></mesh><mesh position={[3.4,0,0]}><sphereGeometry args={[.08,12,12]}/><meshBasicMaterial color="#d2b771"/></mesh></group></>}
 </group>;
}
function CameraRig({floors,reduced}:{floors:number;reduced:boolean}){
 const {camera,invalidate}=useThree();const height=Math.min(4,Math.max(1,Math.round(floors)));
 useEffect(()=>{const distance=height>=3?13.5:11.5;camera.position.set(distance*.8,8.5+(height-2)*1.4,distance+2.5);camera.lookAt(0,height*1.35/2,1.3);camera.updateProjectionMatrix();invalidate();},[camera,height,invalidate,reduced]);
 return <OrbitControls enableZoom={false} enablePan={false} enableDamping={!reduced} minPolarAngle={.45} maxPolarAngle={1.35} target={[0,height*1.35/2,1.3]}/>;
}
export default function WorldScene({floors=2,solar=true}:{floors?:number;solar?:boolean;busy?:boolean}){
 const reduced=!!useReducedMotion(),[supported,setSupported]=useState(false),[visible,setVisible]=useState(true),[night,setNight]=useState(false),[paused,setPaused]=useState(false);const host=useRef<HTMLDivElement>(null);
 useEffect(()=>{const canvas=document.createElement('canvas');try{const context=canvas.getContext('webgl2')||canvas.getContext('webgl');setSupported(!!context);context?.getExtension('WEBGL_lose_context')?.loseContext();}catch{setSupported(false);}const observer=new IntersectionObserver(([entry])=>setVisible(entry.isIntersecting),{rootMargin:'150px'});if(host.current)observer.observe(host.current);const onVisibility=()=>setVisible(!document.hidden);document.addEventListener('visibilitychange',onVisibility);return()=>{observer.disconnect();document.removeEventListener('visibilitychange',onVisibility);};},[]);
 return <div ref={host} style={{height:'100%',width:'100%',position:'relative',borderRadius:'inherit'}}><Boundary>{supported?<Canvas dpr={[1,1.5]} frameloop={reduced||paused||!visible?'demand':'always'} camera={{position:[9.2,8.5,13.5],fov:36}} gl={{alpha:true,antialias:true,powerPreference:'low-power'}} aria-label={`Interactive preview of a ${Math.min(4,Math.max(1,Math.round(floors)))}-storey home with optional solar, a small street, a car and a cyclist; ${night?'night':'day'} lighting`}>
 <DayNightSky floors={floors} paused={reduced||paused} host={host} onNightChange={setNight}/><Home floors={floors} solar={solar} reduced={reduced||paused} night={night}/><CameraRig floors={floors} reduced={reduced||paused}/>
 </Canvas>:<Fallback/>}</Boundary>{supported&&<div className={'sky-cycle-status'+(night?' is-night':'')}><span>{night?<Moon size={13}/>:<Sun size={13}/>} {night?'Night':'Day'}</span>{!reduced&&<button type="button" aria-label={paused?'Resume scene animation':'Pause scene animation'} aria-pressed={paused} onClick={()=>setPaused(!paused)}>{paused?<Play size={12}/>:<Pause size={12}/>}</button>}<small>Illustrative cycle</small></div>}</div>;
}
