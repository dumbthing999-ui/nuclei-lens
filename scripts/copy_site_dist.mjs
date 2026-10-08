import { cpSync, existsSync, lstatSync, mkdtempSync, renameSync, rmSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const source = path.join(root, 'frontend', 'dist');
const destination = path.join(root, 'dist');
const inputStat = lstatSync(source, { throwIfNoEntry: false });
if (!inputStat?.isDirectory() || inputStat.isSymbolicLink() || !existsSync(path.join(source, 'index.html'))) {
  throw new Error('Build frontend first; frontend/dist/index.html is required.');
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
