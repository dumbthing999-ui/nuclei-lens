import {mkdir,copyFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const target=path.join(root,'frontend/public/engine/nuclei_lens');
await mkdir(target,{recursive:true});
for(const file of ['__init__.py','core.py','graph.py','raster.py'])
  await copyFile(path.join(root,'src/nuclei_lens',file),path.join(target,file));
const evidence=path.join(root,'frontend/public/evidence');
await mkdir(evidence,{recursive:true});
await copyFile(path.join(root,'evaluation/test/summary.json'),path.join(evidence,'test.json'));
await copyFile(path.join(root,'evaluation/additional/summary.json'),path.join(evidence,'additional.json'));
console.log('Shared Python engine and complete evaluation summaries synchronized.');
