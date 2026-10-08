import {mkdir,copyFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const target=path.join(root,'frontend/public/engine/nuclei_lens');
await mkdir(target,{recursive:true});
for(const file of ['__init__.py','core.py','graph.py','raster.py'])
  await copyFile(path.join(root,'src/nuclei_lens',file),path.join(target,file));
console.log('Shared Python engine synchronized.');
