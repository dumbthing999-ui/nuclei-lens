import { cpSync, existsSync, lstatSync, mkdtempSync, readFileSync, renameSync, rmSync } from 'node:fs';
import {createHash} from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const source = path.join(root, 'frontend', 'dist');
const destination = path.join(root, 'dist');
const inputStat = lstatSync(source, { throwIfNoEntry: false });
if (!inputStat?.isDirectory() || inputStat.isSymbolicLink() || !existsSync(path.join(source, 'index.html'))) {
  throw new Error('Build frontend first; frontend/dist/index.html is required.');
}
// Runtime assets are generated/ignored by Git. A successful Vite build alone
// does not prove the on-device engine can start in a fresh deployment.
const runtime=path.join(source,'runtime','pyodide');
for(const name of ['pyodide.mjs','pyodide.js','pyodide.asm.mjs','pyodide.asm.wasm','python_stdlib.zip','pyodide-lock.json']) {
  if(!lstatSync(path.join(runtime,name),{throwIfNoEntry:false})?.isFile())throw new Error('Incomplete scientific runtime: '+name+'. Run node scripts/prepare_runtime.mjs before building.');
}
const manifest=JSON.parse(readFileSync(path.join(root,'evaluation/runtime-manifest.json'),'utf8'));
if(!Array.isArray(manifest.runtime_files)||manifest.runtime_files.length!==6)throw new Error('Runtime file hashes are missing; regenerate the scientific runtime manifest.');
for(const item of [...manifest.runtime_files,...manifest.packages]) {
  if(path.basename(item.file)!==item.file)throw new Error('Invalid runtime package filename.');
  const bytes=readFileSync(path.join(runtime,item.file));
  if(bytes.length!==item.bytes||createHash('sha256').update(bytes).digest('hex')!==item.sha256)throw new Error('Scientific runtime integrity failed: '+item.file);
}
for(const file of ['__init__.py','core.py','graph.py','raster.py']) {
  const built=readFileSync(path.join(source,'engine/nuclei_lens',file));
  if(!built.equals(readFileSync(path.join(root,'src/nuclei_lens',file))))throw new Error('Built scientific source differs: '+file+'. Run node scripts/sync_engine.mjs before building.');
}
const current = lstatSync(destination, { throwIfNoEntry: false });
if (current && (!current.isDirectory() || current.isSymbolicLink())) {
  throw new Error('Refusing to replace a non-directory or symlink at root dist/.');
}

const staging = mkdtempSync(path.join(root, '.site-dist-'));
try {
  const stagedDist = path.join(staging, 'dist');
  cpSync(source, stagedDist, { recursive: true, dereference: false, verbatimSymlinks: true });
  if (!existsSync(path.join(stagedDist, 'index.html'))) throw new Error('Staged Site is missing index.html.');
  if (current) rmSync(destination, { recursive: true });
  renameSync(stagedDist, destination);
} finally {
  rmSync(staging, { recursive: true, force: true });
}
