import http from 'node:http';
import {readFile} from 'node:fs/promises';
const files={'/':'index.html','/index.html':'index.html','/sim.mjs':'sim.mjs','/app.mjs':'app.mjs'};
http.createServer(async(req,res)=>{const file=files[req.url?.split('?')[0]];if(!file){res.writeHead(404);res.end();return;}try{const data=await readFile(new URL(file,import.meta.url));res.writeHead(200,{'Content-Type':file.endsWith('.html')?'text/html; charset=utf-8':'text/javascript; charset=utf-8'});res.end(data);}catch{res.writeHead(500);res.end('Read error');}}).listen(8765,'127.0.0.1',()=>console.log('PuppyPi virtual lab: http://127.0.0.1:8765'));
