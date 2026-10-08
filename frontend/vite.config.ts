import {defineConfig} from 'vite';
import {createReadStream,existsSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
export default defineConfig({worker:{format:'es'},plugins:[{
  name:'scientific-runtime-static',
  configureServer(server) {
    const root=fileURLToPath(new URL('./public/runtime/pyodide/',import.meta.url));
    server.middlewares.use((request,response,next)=>{
      const pathname=new URL(request.url??'/', 'http://localhost').pathname;
      const prefix='/runtime/pyodide/';
      if(!pathname.startsWith(prefix))return next();
      const filename=pathname.slice(prefix.length);
      if(!/^[a-zA-Z0-9_.-]+$/.test(filename))return next();
      const fullPath=path.join(root,filename);if(!existsSync(fullPath))return next();
      response.setHeader('Content-Type',filename.endsWith('.mjs')||filename.endsWith('.js')?'application/javascript':filename.endsWith('.wasm')?'application/wasm':filename.endsWith('.json')?'application/json':'application/octet-stream');
      createReadStream(fullPath).on('error',next).pipe(response);
    });
  }
}]});
