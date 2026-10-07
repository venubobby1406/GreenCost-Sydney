'use client';
import {useRef} from 'react';
import {useFrame} from '@react-three/fiber';
import * as THREE from 'three';

type Point = [number, number, number];
const STREET_STRAIGHT=5.6,STREET_RADIUS=.28;
// A short loop keeps both vehicles on the street, including at each turn.
function streetPosition(distance:number,centre=3.9,radius=STREET_RADIUS):Point{
 const straight=STREET_STRAIGHT,arc=Math.PI*radius;
 let along=distance%(straight*2+arc*2);
 if(along<straight)return [-2.8+along,centre-radius,0];
 along-=straight;
 if(along<arc){const angle=-Math.PI/2+along/radius;return [2.8+radius*Math.cos(angle),centre+radius*Math.sin(angle),-angle-Math.PI/2];}
 along-=arc;
 if(along<straight)return [2.8-along,centre+radius,Math.PI];
 const angle=Math.PI/2+(along-straight)/radius;
 return [-2.8+radius*Math.cos(angle),centre+radius*Math.sin(angle),-angle-Math.PI/2];
}
function Block({at,size,color}:{at:Point;size:Point;color:string}){
 return <mesh position={at}><boxGeometry args={size}/><meshStandardMaterial color={color} roughness={.8}/></mesh>;
}
function Bar({from,to,color,radius=.018}:{from:Point;to:Point;color:string;radius?:number}){
 const start=new THREE.Vector3(...from),end=new THREE.Vector3(...to),delta=end.clone().sub(start);
 const orientation=new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,1,0),delta.clone().normalize());
 return <mesh position={start.add(end).multiplyScalar(.5)} quaternion={orientation}><cylinderGeometry args={[radius,radius,delta.length(),6]}/><meshStandardMaterial color={color}/></mesh>;
}
function Car({reduced}:{reduced:boolean}){
 const car=useRef<THREE.Group>(null),wheels=useRef<THREE.Group>(null),elapsed=useRef(0);
 useFrame((_,delta)=>{if(reduced)return;elapsed.current+=Math.min(delta,.1);const time=elapsed.current;if(car.current){const [x,z,turn]=streetPosition(time*.58+1.3);car.current.position.set(x,.15,z);car.current.rotation.y=turn;}if(wheels.current)wheels.current.children.forEach(wheel=>{wheel.rotation.z=-time*3.4;});});
 return <group ref={car} position={[-1.5,.15,3.65]}>
  <Block at={[0,.25,0]} size={[1.2,.26,.54]} color="#557c70"/>
  <Block at={[-.12,.46,0]} size={[.65,.28,.47]} color="#e2e8de"/>
  <Block at={[-.12,.48,.244]} size={[.56,.18,.014]} color="#344f56"/>
  <Block at={[-.12,.48,-.244]} size={[.56,.18,.014]} color="#344f56"/>
  <Block at={[.22,.48,0]} size={[.018,.19,.42]} color="#344f56"/>
  <Block at={[.61,.25,0]} size={[.018,.075,.41]} color="#fbedd0"/>
  <Block at={[-.61,.25,0]} size={[.018,.07,.4]} color="#b7735f"/>
  <group ref={wheels}>{[-.38,.38].flatMap(x=>[-.28,.28].map(z=><group key={`${x}:${z}`} position={[x,.14,z]}><mesh rotation={[Math.PI/2,0,0]}><cylinderGeometry args={[.145,.145,.065,12]}/><meshStandardMaterial color="#303b37"/></mesh><Block at={[0,0,z>0?.037:-.037]} size={[.16,.028,.008]} color="#b6c3bb"/></group>))}</group>
 </group>;
}
function Bicycle({reduced}:{reduced:boolean}){
 const bicycle=useRef<THREE.Group>(null),wheels=useRef<THREE.Group>(null),pedals=useRef<THREE.Group>(null),elapsed=useRef(0);
 useFrame((_,delta)=>{if(reduced)return;elapsed.current+=Math.min(delta,.1);const time=elapsed.current;if(bicycle.current){const [x,z,turn]=streetPosition(time*.3+9,5.4,.12);bicycle.current.position.set(x,.15,z);bicycle.current.rotation.y=turn;}if(wheels.current)wheels.current.children.forEach(wheel=>{wheel.rotation.z=-time*1.43;});if(pedals.current)pedals.current.rotation.z=-time*2.2;});
 const rear:Point=[-.34,.22,0],front:Point=[.36,.22,0],crank:Point=[0,.22,0],seat:Point=[-.12,.55,0],head:Point=[.23,.53,0];
 return <group ref={bicycle} position={[-2,.15,5.52]} rotation={[0,Math.PI,0]}>
  <group ref={wheels}>{[-.34,.36].map(x=><group key={x} position={[x,.22,0]}><mesh><torusGeometry args={[.21,.024,6,20]}/><meshStandardMaterial color="#35453e"/></mesh>{[0,Math.PI/3,2*Math.PI/3].map(angle=><mesh key={angle} rotation={[0,0,angle]}><boxGeometry args={[.008,.4,.008]}/><meshStandardMaterial color="#afbab1"/></mesh>)}</group>)}</group>
  {[[rear,seat],[seat,crank],[crank,rear],[seat,head],[head,crank],[head,front]].map(([from,to],i)=><Bar key={i} from={from} to={to} color="#b88a4f"/>)}
  <Bar from={head} to={[.24,.65,0]} color="#44564b"/><Bar from={[.24,.65,-.08]} to={[.24,.65,.08]} color="#44564b"/>
  <Block at={[-.12,.59,0]} size={[.16,.04,.09]} color="#344a3e"/>
  <group ref={pedals} position={crank}><Bar from={[0,-.08,0]} to={[0,.08,0]} color="#44564b"/><Block at={[0,.08,.06]} size={[.08,.025,.08]} color="#344a3e"/><Block at={[0,-.08,-.06]} size={[.08,.025,.08]} color="#344a3e"/></group>
  <Bar from={[-.1,.62,0]} to={[0,.87,0]} color="#557768" radius={.075}/>
  <mesh position={[.025,1,0]}><sphereGeometry args={[.095,10,8]}/><meshStandardMaterial color="#cda882"/></mesh>
  <mesh position={[.025,1.055,0]} scale={[1,.65,1]}><sphereGeometry args={[.105,10,8]}/><meshStandardMaterial color="#e1c995"/></mesh>
  {[-.06,.06].map(z=><group key={z}><Bar from={[0,.83,z]} to={[.25,.66,z]} color="#cda882" radius={.025}/><Bar from={[-.1,.61,z]} to={[.12,.4,z]} color="#4c5d54" radius={.034}/><Bar from={[.12,.4,z]} to={[0,.16,z]} color="#4c5d54" radius={.03}/></group>)}
 </group>;
}
export default function RoadTraffic({reduced,night}:{reduced:boolean;night:boolean}){
 return <group>
  <Block at={[0,.08,3.9]} size={[7.65,.1,1.65]} color="#8b9690"/>
  <Block at={[0,.12,3]} size={[7.65,.15,.17]} color="#e1e5da"/>
  <Block at={[0,.12,4.8]} size={[7.65,.15,.17]} color="#e1e5da"/>
  <Block at={[0,.08,5.4]} size={[7.65,.1,.9]} color="#aec4a9"/>
  <Block at={[0,.12,5.92]} size={[7.65,.15,.12]} color="#e1e5da"/>
  <Block at={[0,.11,6.06]} size={[7.65,.13,.16]} color="#d7ddcf"/>
  {[-2,0,2].map(x=><Block key={`cycle:${x}`} at={[x,.137,5.4]} size={[.26,.012,.025]} color="#edf3e6"/>)}
  {[-3,-2,-1,0,1,2,3].map(x=><Block key={x} at={[x,.137,3.96]} size={[.45,.012,.035]} color="#eee9dc"/>)}
  <group visible={!night}><Car reduced={reduced||night}/><Bicycle reduced={reduced||night}/></group>
 </group>;
}
