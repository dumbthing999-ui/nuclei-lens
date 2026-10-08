/* Download a pinned Pyodide runtime and its transitive wheel dependencies. */
import {mkdir, readFile, writeFile, copyFile, readdir, unlink} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const version='314.0.7';
const target=path.join(root,'frontend/public/runtime/pyodide');
const bundled=path.join(root,'frontend/node_modules/pyodide');
await mkdir(target,{recursive:true});
for(const name of ['pyodide.js','pyodide.mjs','pyodide.asm.mjs','pyodide.asm.wasm','python_stdlib.zip','pyodide-lock.json']) {
  await copyFile(path.join(bundled,name),path.join(target,name));
}
const lock=JSON.parse(await readFile(path.join(target,'pyodide-lock.json'),'utf8'));
// Core modules use numerical functions only. Omit optional I/O/plotting extras
// rather than shipping an obsolete Pillow decoder that inference never needs.
lock.packages['scikit-image'].depends=['numpy','scipy','lazy_loader','packaging'];
await writeFile(path.join(target,'pyodide-lock.json'),JSON.stringify(lock));
const packages=new Set();
function include(name) {
  name=name.toLowerCase().replaceAll('_','-').replaceAll('.','-');
  if(packages.has(name)) return;
  const item=lock.packages[name]; if(!item) throw new Error('Missing runtime package '+name);
  packages.add(name); for(const dep of item.depends) include(dep);
}
for(const name of ['numpy','scipy','scikit-image']) include(name);
const hash = data => createHash('sha256').update(data).digest('hex');
const manifest=[];
for(const name of packages) {
  const item=lock.packages[name]; const dest=path.join(target,item.file_name);
  let data;
  try { data=await readFile(dest); if(hash(data)!==item.sha256) data=undefined; } catch {}
  if(!data) {
    const response=await fetch(`https://cdn.jsdelivr.net/pyodide/v${version}/full/${item.file_name}`,{signal:AbortSignal.timeout(120000)});
    if(!response.ok) throw new Error(`Runtime download ${name}: ${response.status}`);
    data=Buffer.from(await response.arrayBuffer());
    if(hash(data)!==item.sha256) throw new Error('Hash mismatch '+name);
    await writeFile(dest,data);
  }
  manifest.push({name,version:item.version,file:item.file_name,sha256:item.sha256,bytes:data.length});
  console.log(`Verified ${name} ${item.version}`);
}
await writeFile(path.join(root,'evaluation/runtime-manifest.json'),JSON.stringify({pyodide:version,source:`https://cdn.jsdelivr.net/pyodide/v${version}/full/`,packages:manifest},null,2)+'\n');
const allowed=new Set(['pyodide.js','pyodide.mjs','pyodide.asm.mjs','pyodide.asm.wasm','python_stdlib.zip','pyodide-lock.json',...manifest.map(p=>p.file)]);
for(const filename of await readdir(target)) if(!allowed.has(filename)) await unlink(path.join(target,filename));
console.log('Browser runtime prepared.');
