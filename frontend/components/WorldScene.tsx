'use client';

import {Component,useEffect,useRef,useState,type ReactNode} from 'react';
import {Canvas,useFrame} from '@react-three/fiber';
import {ContactShadows,Float,OrbitControls} from '@react-three/drei';
import {useReducedMotion} from 'framer-motion';
import * as THREE from 'three';

class Boundary extends Component<{children:ReactNode},{failed:boolean}>{
 state={failed:false};static getDerivedStateFromError(){return {failed:true};}
 render(){return this.state.failed?<div className="world-fallback"><span>⌂</span><p>Your building. A greener future.</p></div>:this.props.children;}
}

function Agent({busy,reduced}:{busy:boolean;reduced:boolean}){
 const ref=useRef<THREE.Group>(null);
 useFrame(({clock})=>{if(ref.current&&!reduced){ref.current.rotation.y=Math.sin(clock.elapsedTime*.7)*.35;ref.current.position.y=2.9+Math.sin(clock.elapsedTime*(busy?2:1))*.14;}});
 return <group ref={ref} position={[3.6,2.9,.7]} scale={.7}>
  <mesh castShadow><sphereGeometry args={[.72,32,32]}/><meshStandardMaterial color="#f9f5e8" roughness={.35}/></mesh>
  <mesh position={[0,.03,.59]}><boxGeometry args={[.85,.4,.22]}/><meshStandardMaterial color="#143b31" roughness={.3}/></mesh>
  {[-.23,.23].map(x=><mesh key={x} position={[x,.07,.715]}><sphereGeometry args={[.065,16,16]}/><meshBasicMaterial color="#d7ec84"/></mesh>)}
  <mesh position={[0,.8,0]}><sphereGeometry args={[.12,16,16]}/><meshStandardMaterial color="#e0a454"/></mesh>
  <mesh position={[0,.67,0]}><cylinderGeometry args={[.025,.025,.25,8]}/><meshStandardMaterial color="#e0a454"/></mesh>
  <mesh rotation={[Math.PI/2,.25,0]} position={[0,-.26,0]}><torusGeometry args={[.9,.025,10,60]}/><meshStandardMaterial color="#91b67c"/></mesh>
  {[-1,1].map(x=><mesh key={x} position={[x*.78,-.15,0]} rotation={[0,0,x*.4]}><capsuleGeometry args={[.09,.3,4,8]}/><meshStandardMaterial color="#e0a454"/></mesh>)}
 </group>;
}

function House({floors,solar,reduced}:{floors:number;solar:boolean;reduced:boolean}){
 const ref=useRef<THREE.Group>(null);const n=Math.min(4,Math.max(1,floors));
 useFrame(({clock})=>{if(ref.current&&!reduced)ref.current.rotation.y=Math.sin(clock.elapsedTime*.16)*.06;});
 return <group ref={ref} position={[-.5,.2,0]} scale={n>2?2.2/n:1}>
  <mesh castShadow receiveShadow position={[0,-.2,0]}><boxGeometry args={[7,.4,5.6]}/><meshStandardMaterial color="#c1cfaa"/></mesh>
  <mesh receiveShadow position={[0,.04,0]}><boxGeometry args={[6.4,.08,5]}/><meshStandardMaterial color="#dbe3c9"/></mesh>
  <mesh receiveShadow position={[.5,.1,2.1]}><boxGeometry args={[4.8,.06,1.4]}/><meshStandardMaterial color="#f4ecdc"/></mesh>
  {Array.from({length:n},(_,i)=><group key={i} position={[0,i*1.35,0]}>
   <mesh castShadow receiveShadow position={[0,.72,-.2]}><boxGeometry args={[4.4,1.3,3]}/><meshStandardMaterial color="#f1eddf" roughness={.75}/></mesh>
   <mesh castShadow position={[0,1.37,-.2]}><boxGeometry args={[4.7,.17,3.3]}/><meshStandardMaterial color="#fffaf0"/></mesh>
   {[-1.5,-.45,.6,1.65].map(x=><group key={x} position={[x,.75,1.32]}>
    <mesh><boxGeometry args={[.8,.8,.04]}/><meshStandardMaterial color="#375951" metalness={.3} roughness={.25}/></mesh>
    {[-.45,.45].map(a=><mesh key={a} position={[a,0,.055]}><boxGeometry args={[.055,.95,.1]}/><meshStandardMaterial color="#ac805a"/></mesh>)}
   </group>)}
   <mesh position={[2.23,.72,-.2]}><boxGeometry args={[.04,.8,1.8]}/><meshStandardMaterial color="#4e7265" metalness={.3} roughness={.3}/></mesh>
  </group>)}
  <mesh position={[0,n*1.35+.09,-.2]}><boxGeometry args={[4.4,.1,3]}/><meshStandardMaterial color="#859b6b"/></mesh>
  {solar&&[-1.2,0,1.2].map(x=><group key={x} position={[x,n*1.35+.23,-.2]} rotation={[-.18,0,0]}><mesh castShadow><boxGeometry args={[1.04,.07,1.6]}/><meshStandardMaterial color="#1d4052" metalness={.5} roughness={.3}/></mesh>{[-.33,0,.33].map(z=><mesh key={z} position={[z,.04,0]}><boxGeometry args={[.018,.01,1.6]}/><meshBasicMaterial color="#88a6b2"/></mesh>)}</group>)}
  {[-2.75,2.75].map((x,i)=><group key={x} position={[x,0,i===0?-.8:1]}><mesh castShadow position={[0,.55,0]}><cylinderGeometry args={[.06,.08,1.1,8]}/><meshStandardMaterial color="#957351"/></mesh><mesh castShadow position={[0,1.35,0]}><icosahedronGeometry args={[.65,1]}/><meshStandardMaterial color={i===0?'#799560':'#91a774'} flatShading/></mesh><mesh castShadow position={[.1,1.9,0]}><icosahedronGeometry args={[.5,1]}/><meshStandardMaterial color="#8ea16c" flatShading/></mesh></group>)}
  {[-2,-1.4,-.8].map(x=><mesh key={x} position={[x,.2,2]}><sphereGeometry args={[.27,12,12]}/><meshStandardMaterial color="#a2af73"/></mesh>)}
 </group>;
}

export default function WorldScene({floors=2,solar=true,busy=false}:{floors?:number;solar?:boolean;busy?:boolean}){
 const reduced=!!useReducedMotion();const [supported,setSupported]=useState<boolean|null>(null);
 useEffect(()=>{try{const canvas=document.createElement('canvas');setSupported(!!(canvas.getContext('webgl2')||canvas.getContext('webgl')));}catch{setSupported(false);}},[]);
 return <Boundary>{supported?<Canvas shadows dpr={[1,1.5]} frameloop={reduced?'demand':'always'} camera={{position:[9,7,10],fov:36}} gl={{alpha:true,antialias:true}} aria-label="Interactive building and animated research assistant">
  <ambientLight intensity={1.9}/><directionalLight position={[5,10,6]} intensity={3} castShadow shadow-mapSize={[1024,1024]}/>
  <House floors={floors} solar={solar} reduced={reduced}/><Agent busy={busy} reduced={reduced}/>
  <Float speed={reduced?0:1.3} rotationIntensity={.1} floatIntensity={.2}><mesh position={[-3.7,3,-1]} rotation={[.2,.3,.1]}><octahedronGeometry args={[.17]}/><meshStandardMaterial color="#e4b875"/></mesh></Float>
  <ContactShadows position={[0,-.05,0]} opacity={.25} scale={18} blur={3} far={7}/>
  <OrbitControls enablePan={false} enableZoom={false} minPolarAngle={.5} maxPolarAngle={1.4} target={[0,1,0]} enableDamping={!reduced}/>
 </Canvas>:<div className="world-fallback"><span>⌂</span><p>{supported===null?'Preparing your architectural preview…':'Your building. A greener future.'}</p><small>{floors} floors · {solar?'Solar enabled':'Solar disabled'}</small></div>}</Boundary>;
}
