// Real Firefox engine smoke test. A narrow check, not mobile/Safari coverage.
import {firefox} from 'playwright';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fromArrayBuffer} from 'geotiff';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const target=process.env.NUCLEILENS_DEMO_URL||'http://127.0.0.1:5174';
const output=path.join(root,'evaluation/checks/firefox-smoke.json');
await mkdir(path.dirname(output),{recursive:true});
let browser;
const errors=[];
try {
  browser=await firefox.launch({headless:true});
  const page=await browser.newPage({viewport:{width:1440,height:1080}});
  page.on('pageerror',error=>errors.push(error.message));
  await page.goto(target);
  await page.waitForFunction(()=>document.querySelector('[data-testid=mask-count]')?.textContent?.startsWith('74 '));
  await page.getByRole('button',{name:'Inspect split · 1 → 2'}).click();
  await page.getByRole('button',{name:'Confirm split alternative · 1 → 2'}).click();
  await page.waitForFunction(()=>document.querySelector('[data-testid=mask-count]')?.textContent?.startsWith('75 '));
  await page.getByRole('button',{name:'Inspect merge · 2 → 1'}).click();
  await page.getByRole('button',{name:'Confirm merge alternative · 2 → 1'}).click();
  await page.waitForFunction(()=>document.querySelector('[data-testid=mask-count]')?.textContent?.startsWith('74 '));
  const labelDownload=page.waitForEvent('download');
  await page.getByRole('button',{name:'Export label TIFF'}).click();
  const labelFile=await(await labelDownload).path();
  const data=await readFile(labelFile);
  const image=await(await fromArrayBuffer(data.buffer.slice(data.byteOffset,data.byteOffset+data.byteLength))).getImage();
  const labels=await image.readRasters({interleave:true});
  if(!(labels instanceof Uint32Array)||new Set(Array.from(labels).filter(n=>n>0)).size!==74)throw new Error('TIFF mask count/type mismatch');
  const bytes=Buffer.alloc(labels.length*4);labels.forEach((id,i)=>bytes.writeUInt32LE(id,i*4));
  const auditDownload=page.waitForEvent('download');
  await page.getByRole('button',{name:'Export review JSON'}).click();
  const audit=JSON.parse(await readFile(await(await auditDownload).path(),'utf8'));
  if(audit.mask_review.sha256_uint32_le!==createHash('sha256').update(bytes).digest('hex')||audit.mask_review.changes.length!==2)throw new Error('Audit mismatch');
  const started=performance.now();
  await page.getByRole('button',{name:'Rerun on this device'}).click();
  await page.waitForFunction(()=>document.querySelector('.status-row')?.textContent?.includes('Analysis completed on your device.')||!!document.querySelector('[role=alert]'),{},{timeout:100000});
  if(await page.locator('[role=alert]').count())throw new Error(await page.locator('[role=alert]').textContent());
  if(await page.locator('.count-strip strong').first().textContent()!=='74')throw new Error('Live/native parity failed');
  const coldMs=performance.now()-started;
  const rerunDownload=page.waitForEvent('download');
  await page.getByRole('button',{name:'Export label TIFF'}).click();
  if(!(await readFile(await(await rerunDownload).path())).equals(data))throw new Error('Mask edits lost on live rerun');
  await page.getByRole('button',{name:'Undo mask edit'}).click();
  await page.getByRole('button',{name:'Undo mask edit'}).click();
  if(!await page.getByRole('button',{name:'Undo mask edit'}).isDisabled())throw new Error('Undo history not cleared');
  await page.setViewportSize({width:390,height:844});
  if(await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth))throw new Error('Narrow viewport overflow');
  if(errors.length)throw new Error(errors.join('\n'));
  const report={status:'passed',generated_at:new Date().toISOString(),target,engine:'Playwright Firefox',version:browser.version(),mask_counts:[74,75,74],tiff_uint32_verified:true,audit_hash_verified:true,live_native_count:74,edits_preserved_on_live_rerun:true,undo:true,cold_browser_ms:Math.round(coldMs),narrow_viewport_overflow:false,page_errors:errors,scope:'One real Firefox desktop engine and resized viewport. Not physical mobile, Safari, assistive technology or biological correction validation.'};
  await writeFile(output,JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report));
} catch(error) {
  await writeFile(output,JSON.stringify({status:'failed',target,generated_at:new Date().toISOString(),error:String(error),page_errors:errors},null,2)+'\n');
  throw error;
} finally {
  await browser?.close();
}
