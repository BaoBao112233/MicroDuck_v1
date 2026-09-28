export const legs=[{name:'FL',x:.105,z:-.065,phase:0},{name:'FR',x:.105,z:.065,phase:.5},{name:'RL',x:-.105,z:-.065,phase:.5},{name:'RR',x:-.105,z:.065,phase:0}];
export const L=.095;
export function ik(x,down){
 const r=Math.hypot(x,down);if(!Number.isFinite(r)||r>2*L||r<.001)throw new RangeError('Foot outside reachable workspace');
 const knee=2*Math.acos(r/(2*L));const hip=Math.atan2(x,down)-knee/2;
 return {hip,knee,kx:L*Math.sin(hip),ky:-L*Math.cos(hip)};
}
export class Simulator{
 constructor(){this.reset();}
 reset(){this.x=0;this.z=0;this.yaw=0;this.phase=0;this.time=0;this.distance=0;this.mode='stand';this.estop=false;this.height=.145;this.stride=.055;this.lift=.025;this.hz=1.2;this.path=[];}
 command(mode){if(!['stand','forward','backward','left','right'].includes(mode))return false;if(this.estop)return false;this.mode=mode;return true;}
 stop(){this.estop=true;this.mode='stand';}
 step(dt){dt=Math.max(0,Math.min(dt,.05));this.time+=dt;const moving=this.mode!=='stand'&&!this.estop;
 if(moving){this.phase=(this.phase+dt*this.hz)%1;const v=this.stride*this.hz*2;
 if(this.mode==='forward'||this.mode==='backward'){const d=v*dt*(this.mode==='forward'?1:-1);this.x+=Math.cos(this.yaw)*d;this.z+=Math.sin(this.yaw)*d;this.distance+=Math.abs(d);}else this.yaw+=(this.mode==='left'?-1:1)*v/.14*dt;
 if(this.path.length===0||Math.hypot(this.x-this.path.at(-1)[0],this.z-this.path.at(-1)[1])>.012){this.path.push([this.x,this.z]);if(this.path.length>1200)this.path.shift();}}
 }
 pose(){return legs.map(l=>{const active=this.mode!=='stand'&&!this.estop;const p=(this.phase+l.phase)%1;let direction=this.mode==='backward'?-1:1;if(this.mode==='left'||this.mode==='right')direction=(l.z>0?1:-1)*(this.mode==='left'?1:-1);
 const fx=active?direction*this.stride*(p<.5?.5-2*p:2*p-1.5):0;
 const up=active&&p>=.5?this.lift*Math.sin((p-.5)*Math.PI*2):0;
 return {...l,fx,up,contact:up<.001,...ik(fx,this.height-up)};});}
}
