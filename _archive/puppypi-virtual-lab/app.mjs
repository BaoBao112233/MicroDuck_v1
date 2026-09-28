import {Simulator} from './sim.mjs';
const sim=new Simulator(),$=id=>document.getElementById(id),canvas=$('scene'),ctx=canvas.getContext('2d');
let az=.8,elev=.55,zoom=1050,last=0,demo=null,drag=null;
const names={stand:'Đứng',forward:'Đi tiến',backward:'Đi lùi',left:'Quay trái',right:'Quay phải'};
function sync(){document.querySelectorAll('[data-mode]').forEach(b=>b.classList.toggle('active',b.dataset.mode===sim.mode));$('status').textContent=sim.estop?'Đã khóa · mở khóa để tiếp tục':names[sim.mode]+' · mô phỏng';$('unlock').hidden=!sim.estop;}
function cancelDemo(){demo=null;$('demo-status').textContent='Tiến 1 m → quay 90° → đứng.';}
document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>{cancelDemo();sim.command(b.dataset.mode);sync();});
$('stop').onclick=()=>{cancelDemo();sim.stop();sync();};$('unlock').onclick=()=>{sim.estop=false;sync();};
function sliders(){for(const key of ['height','stride','lift','hz']){sim[key]=Number($(key).value)/(key==='hz'?1:1000);$(key+'-val').textContent=$(key).value+(key==='hz'?' Hz':' mm');}}
for(const key of ['height','stride','lift','hz'])$(key).oninput=sliders;sliders();
$('reset').onclick=()=>{sim.reset();az=.8;elev=.55;zoom=1050;cancelDemo();sliders();sync();};
$('demo').onclick=()=>{if(sim.estop){$('demo-status').textContent='Mở khóa dừng khẩn cấp trước khi chạy thử.';return;}demo={stage:0,start:sim.distance,yaw:sim.yaw};sim.command('forward');sync();};
window.addEventListener('keydown',e=>{if(e.code!=='Space'&&e.target.matches('input,button'))return;const mode={w:'forward',s:'backward',a:'left',d:'right'}[e.key.toLowerCase()];if(e.code==='Space'){e.preventDefault();$('stop').click();}else if(mode){cancelDemo();sim.command(mode);sync();}});
document.addEventListener('visibilitychange',()=>{if(document.hidden){sim.command('stand');cancelDemo();sync();}});
canvas.onpointerdown=e=>{drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);};canvas.onpointerup=()=>drag=null;canvas.onpointercancel=()=>drag=null;canvas.onpointermove=e=>{if(drag){az+=(e.clientX-drag[0])*.008;elev=Math.max(.15,Math.min(1.25,elev+(e.clientY-drag[1])*.006));drag=[e.clientX,e.clientY];}};canvas.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(450,Math.min(1900,zoom*Math.exp(-e.deltaY*.001)));},{passive:false});
let W=800,H=540,draws=[];
function project([x,y,z]){x-=sim.x;z-=sim.z;const u=x*Math.cos(az)-z*Math.sin(az),v=x*Math.sin(az)+z*Math.cos(az);return [W/2+u*zoom,H*.62+(v*Math.sin(elev)-y*Math.cos(elev))*zoom,v*Math.cos(elev)+y*Math.sin(elev)];}
function world(x,y,z){return [sim.x+x*Math.cos(sim.yaw)-z*Math.sin(sim.yaw),y,sim.z+x*Math.sin(sim.yaw)+z*Math.cos(sim.yaw)];}
function line(a,b,color,width=1){const p=project(a),q=project(b);draws.push({depth:(p[2]+q[2])/2,paint:()=>{ctx.strokeStyle=color;ctx.lineWidth=width;ctx.lineCap='round';ctx.beginPath();ctx.moveTo(p[0],p[1]);ctx.lineTo(q[0],q[1]);ctx.stroke();}});}
function ball(p,color,r){const q=project(p);draws.push({depth:q[2]+.001,paint:()=>{ctx.fillStyle=color;ctx.beginPath();ctx.arc(q[0],q[1],r,0,Math.PI*2);ctx.fill();}});}
function box(cx,cy,cz,sx,sy,sz){const pts=[];for(let i=0;i<8;i++)pts.push(world(cx+(i&1?sx:-sx)/2,cy+(i&2?sy:-sy)/2,cz+(i&4?sz:-sz)/2));const faces=[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]];faces.forEach((ids,i)=>{const ps=ids.map(n=>project(pts[n]));draws.push({depth:ps.reduce((s,p)=>s+p[2],0)/4,paint:()=>{ctx.fillStyle=['#718c9d','#607a8f','#354d63','#bdd1d7','#77929f','#8ea8b6'][i];ctx.strokeStyle='#263e51';ctx.lineWidth=1;ctx.beginPath();ps.forEach((p,j)=>j?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1]));ctx.closePath();ctx.fill();ctx.stroke();}});});}
function frame(now){const dt=last?(now-last)/1000:0;last=now;sim.step(dt);
 if(demo){if(demo.stage===0){$('demo-status').textContent='Đang tiến: '+(sim.distance-demo.start).toFixed(2)+' / 1.00 m';if(sim.distance-demo.start>=1){demo.stage=1;demo.yaw=sim.yaw;sim.command('left');sync();}}else{$('demo-status').textContent='Đang quay: '+(Math.abs(sim.yaw-demo.yaw)*180/Math.PI).toFixed(0)+' / 90°';if(Math.abs(sim.yaw-demo.yaw)>=Math.PI/2){sim.command('stand');demo=null;$('demo-status').textContent='Hoàn tất: tiến 1 m và quay 90° (động học).';sync();}}}
 const rect=canvas.getBoundingClientRect(),dpr=window.devicePixelRatio||1;if(canvas.width!==Math.round(rect.width*dpr)||canvas.height!==Math.round(rect.height*dpr)){canvas.width=Math.round(rect.width*dpr);canvas.height=Math.round(rect.height*dpr);}W=rect.width;H=rect.height;ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,W,H);draws=[];
 const gx=Math.round(sim.x*10)/10,gz=Math.round(sim.z*10)/10;for(let i=-12;i<=12;i++){line([gx+i*.1,0,gz-1.2],[gx+i*.1,0,gz+1.2],'#2c4154');line([gx-1.2,0,gz+i*.1],[gx+1.2,0,gz+i*.1],'#2c4154');}draws.forEach(d=>d.paint());draws=[];
 for(let i=1;i<sim.path.length;i++)line([sim.path[i-1][0],.002,sim.path[i-1][1]],[sim.path[i][0],.002,sim.path[i][1]],'#369e95',2);draws.forEach(d=>d.paint());draws=[];
 const pose=sim.pose();for(const l of pose){const hip=world(l.x,sim.height,l.z),knee=world(l.x+l.kx,sim.height+l.ky,l.z),foot=world(l.x+l.fx,l.up,l.z);line(hip,knee,'#8ab2c5',12);line(knee,foot,'#507a91',9);ball(hip,'#243a4c',10);ball(knee,'#d9e8ed',7);ball(foot,l.contact?'#62e3bf':'#ffba6b',7);}
 box(0,sim.height+.024,0,.26,.048,.13);box(-.015,sim.height+.058,0,.075,.02,.065);box(.145,sim.height+.032,0,.036,.043,.07);ball(world(.168,sim.height+.036,0),'#68e9d4',8);
 draws.sort((a,b)=>a.depth-b.depth).forEach(d=>d.paint());ctx.fillStyle='#b9cfde';ctx.font='13px system-ui';ctx.fillText('PUPPYPI / 8 JOINTS',22,30);ctx.fillStyle='#83a1b8';ctx.fillText('Góc nhìn bám theo robot',22,H-22);
 $('joints').innerHTML=pose.map(l=>'<tr><td>'+l.name+'</td><td>'+(l.hip*180/Math.PI).toFixed(1)+'°</td><td>'+(l.knee*180/Math.PI).toFixed(1)+'°</td><td>'+(l.contact?'Chạm sàn':'Đang nâng')+'</td></tr>').join('');$('distance').textContent=sim.distance.toFixed(2)+' m';$('yaw').textContent=((sim.yaw*180/Math.PI)%360).toFixed(0)+'°';$('time').textContent=sim.time.toFixed(1)+' s';requestAnimationFrame(frame);
}requestAnimationFrame(frame);
