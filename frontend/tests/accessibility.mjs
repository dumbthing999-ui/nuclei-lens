import{chromium}from'playwright';import{readFile,writeFile,mkdir}from'node:fs/promises';import{existsSync}from'node:fs';import path from'node:path';import{fileURLToPath}from'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'),target=process.env.NUCLEILENS_DEMO_URL||'http://127.0.0.1:5173';
const browser=await chromium.launch({executablePath:process.env.NUCLEILENS_CHROMIUM_BIN||(!process.env.CI&&existsSync('/usr/bin/chromium')?'/usr/bin/chromium':undefined),headless:true,args:['--no-sandbox']});
const observations=[];
try{const page=await browser.newPage({viewport:{width:1440,height:1080}});await page.goto(target);await page.waitForFunction(()=>document.querySelector('[data-testid=mask-count]')?.textContent?.startsWith('74 '));await page.addScriptTag({content:await readFile(path.join(root,'frontend/node_modules/axe-core/axe.min.js'),'utf8')});
for(const state of ['desktop','benchmark','additional','mobile']){
 if(state==='benchmark'){await page.getByRole('button',{name:'Inspect benchmark detail'}).click();}
 if(state==='additional'){await page.getByText('All six review policies and assessment scope',{exact:true}).click();}
 if(state==='mobile'){await page.setViewportSize({width:390,height:844});}
 const result=await page.evaluate(async()=>window.axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}}));
 observations.push({state,violations:result.violations.map(v=>({id:v.id,impact:v.impact,description:v.description,nodes:v.nodes.map(n=>({target:n.target,failure:n.failureSummary}))})),incomplete:result.incomplete.map(v=>({id:v.id,targets:v.nodes.map(n=>n.target)})),passes:result.passes.length});
}
await mkdir(path.join(root,'evaluation/checks'),{recursive:true});await writeFile(path.join(root,process.env.CI?'evaluation/checks/accessibility-ci.json':'evaluation/checks/accessibility.json'),JSON.stringify({generated_at:new Date().toISOString(),target,tool:'axe-core',observations,scope:'Automated Chromium viewport checks; not full accessibility compliance or assistive-technology user testing.'},null,2)+'\n');
const violations=observations.flatMap(x=>x.violations);if(violations.length)throw Error(JSON.stringify(violations));console.log('PASS: axe WCAG checks in desktop, benchmark, additional-assessment and mobile states; manual checks remain.');
}finally{await browser.close();}
