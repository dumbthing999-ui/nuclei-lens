import {chromium} from '@playwright/test';
import{existsSync}from'node:fs';
import path from'node:path';
const root=path.resolve(import.meta.dirname,'../..');
import{writeFile}from'node:fs/promises';
const b=await chromium.launch({headless:true,executablePath:process.env.NUCLEILENS_CHROMIUM_BIN||(!process.env.CI&&existsSync('/usr/bin/chromium')?'/usr/bin/chromium':undefined)});
const p=await b.newPage({reducedMotion:'reduce',viewport:{width:1440,height:1080}});
const report={checked_at:new Date().toISOString(),target:process.env.NUCLEILENS_DEMO_URL||'http://127.0.0.1:5173',scope:'Actual Chromium keyboard focus and reduced-motion CSS, not assistive-tech/physical-device study.'};
try{
await p.goto(report.target);await p.waitForSelector('[data-testid=mask-count]');
await p.keyboard.press('Tab');if(await p.locator(':focus').textContent()!=='Skip to microscopy review')throw Error('Skip link is not first keyboard stop');
const link=await p.locator(':focus').boundingBox();if(!link||link.y<0)throw Error('Focused skip link hidden');
await p.keyboard.press('Enter');if(await p.locator(':focus').getAttribute('id')!=='analysis-workspace')throw Error('Skip target did not gain focus');report.skip_link=true;
// Follow actual Tab traversal to a native disclosure.
let reached=false;for(let i=0;i<100;i++){await p.keyboard.press('Tab');if(await p.locator(':focus').evaluate(e=>e.tagName==='SUMMARY')){reached=true;break;}}
if(!reached)throw Error('Disclosure not reachable');const focus=await p.locator(':focus').evaluate(e=>{const s=getComputedStyle(e);return{width:s.outlineWidth,style:s.outlineStyle,color:s.outlineColor}});if(parseFloat(focus.width)<3||focus.style==='none')throw Error('Disclosure focus ring missing');report.disclosure_focus=focus;
await p.keyboard.press('Space');if(!await p.locator(':focus').evaluate(e=>e.parentElement.open))throw Error('Disclosure keyboard activation failed');report.disclosure_keyboard=true;
// Trigger the real busy state to inspect the real spinner, then cancel via the product.
await p.getByRole('button',{name:'Rerun on this device'}).click();await p.waitForSelector('.spinner');report.spinner_animation=await p.locator('.spinner').evaluate(e=>getComputedStyle(e).animationName);if(report.spinner_animation!=='none')throw Error('Reduced-motion spinner animates');await p.getByRole('button',{name:'Cancel',exact:true}).click();report.reduced_motion=true;report.status='passed';
}catch(e){report.status='failed';report.error=String(e);throw e}finally{await writeFile(path.join(root,process.env.CI?'evaluation/checks/focus-motion-ci.json':'evaluation/checks/focus-motion.json'),JSON.stringify(report,null,2)+'\n');await b.close()}
console.log('PASS: skip link, disclosure keyboard/focus, reduced-motion spinner.');
