import {useEffect, useRef, useState, useMemo} from 'react';
import {createRoot} from 'react-dom/client';
import type {Analysis, Benchmark, Correction, Sample, GraphEvent} from './types';
import {auditDocument, reviewedTotal, validateCount, compatibleReview, cancellationWitness} from './review';
import {decodeLabelMaps, applyMaskProposal, undoMaskPatch, labelTiff, maskOutline, maskHash, countInstances, type MaskPatch} from './masks';
import './style.css';

const png = (data:string) => `data:image/png;base64,${data}`;

function App() {
  const [samples,setSamples]=useState<Sample[]>([]);
  const [sampleId,setSampleId]=useState('');
  const [analysis,setAnalysis]=useState<Analysis|null>(null);
  const [filename,setFilename]=useState('');
  const [selected,setSelected]=useState(0);
  const [run,setRun]=useState(0);
  const [mode,setMode]=useState<'outlines'|'disagreement'|'image'|'edited'>('outlines');
  const [corrections,setCorrections]=useState<Record<number,Correction>>({});
  const [manualCount,setManualCount]=useState('');
  const [note,setNote]=useState('');
  const [error,setError]=useState('');
  const [status,setStatus]=useState('Opening a real microscopy example…');
  const [busy,setBusy]=useState(false);
  const [engineReady,setEngineReady]=useState(false);
  const [live,setLive]=useState(false);
  const [zoom,setZoom]=useState(false);
  const [showEvidence,setShowEvidence]=useState(false);
  const [policy,setPolicy]=useState<'graph'|'object_disagreement'>('object_disagreement');
  const [benchmark,setBenchmark]=useState<Benchmark|null>(null);
  const [masks,setMasks]=useState<Uint32Array[]|null>(null);
  const [editedMask,setEditedMask]=useState<Uint32Array|null>(null);
  const [patches,setPatches]=useState<MaskPatch[]>([]);
  const [maskStatus,setMaskStatus]=useState('Loading lossless masks…');
  const maskFingerprint=useRef('');
  const editedCount=useMemo(()=>editedMask?countInstances(editedMask):null,[editedMask]);
  const editedOutline=useMemo(()=>editedMask&&analysis?maskOutline(editedMask,analysis.width,analysis.height):null,[editedMask,analysis?.width,analysis?.height]);
  useEffect(()=>{
    if(!analysis){maskFingerprint.current='';setMasks(null);setEditedMask(null);setPatches([]);return;}
    const fingerprint=JSON.stringify([analysis.input_hash,analysis.config,analysis.label_maps]);
    if(maskFingerprint.current===fingerprint)return;
    let active=true;setMasks(null);setEditedMask(null);setPatches([]);setMaskStatus('Loading lossless masks…');
    decodeLabelMaps(analysis).then(decoded=>{if(active){setMasks(decoded);setEditedMask(decoded[0].slice());maskFingerprint.current=fingerprint;setMaskStatus('No mask edits. Inspect an alternative before confirming it.');}}).catch(e=>{if(active)setMaskStatus(String(e.message));});
    return ()=>{active=false;};
  },[analysis]);
  function confirmMask(event:GraphEvent) {
    if(!analysis||!masks||!editedMask)return;
    try {
      const proposal=applyMaskProposal(editedMask,masks[0],masks[event.run_id],event);
      if(patches.length>=20||patches.reduce((n,p)=>n+p.indices.length,0)+proposal.patch.indices.length>1048576)throw new Error('Mask history limit reached. Export or undo before adding more edits.');
      setEditedMask(proposal.mask);setPatches(previous=>[...previous,proposal.patch]);setMode('edited');setError('');
      setMaskStatus(`Confirmed ${event.kind}: ${proposal.patch.before_count} → ${proposal.patch.after_count} mask instances. Tally entries remain separate.`);
    }catch(e){setError(e instanceof Error?e.message:'Mask replacement failed.');}
  }
  function undoMask() {
    if(!editedMask||!patches.length)return;
    const patch=patches[patches.length-1];setEditedMask(undoMaskPatch(editedMask,patch));setPatches(patches.slice(0,-1));setMaskStatus('Last mask edit undone. Tally entries remain separate.');setError('');
  }
  function downloadMask() {
    if(!analysis||!editedMask)return;
    const data=labelTiff(editedMask,analysis.width,analysis.height);
    const url=URL.createObjectURL(new Blob([data],{type:'image/tiff'}));const a=document.createElement('a');a.href=url;a.download=`nucleilens-labels-${analysis.input_hash.slice(0,12)}.tif`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  const previousAnalysis=useRef<Analysis|null>(null);
  const worker=useRef<Worker|null>(null);
  const bytes=useRef<ArrayBuffer|null>(null);
  const input=useRef<HTMLInputElement>(null);
  const requestSequence=useRef(0);
  const timer=useRef<ReturnType<typeof setTimeout>|null>(null);

  function acceptResult(result:Analysis,isLive:boolean) {
    const previous=previousAnalysis.current;
    setCorrections(current=>compatibleReview(previous,result,current));
    previousAnalysis.current=result;setAnalysis(result); setSelected(result.regions.slice().sort((a,b)=>b.comparators.object_disagreement-a.comparators.object_disagreement)[0].id);setRun(0);setZoom(false);setLive(isLive);setBusy(false);
    setStatus(isLive?'Analysis completed on your device.':'Real reference run · rerun to verify on your device');
    if(timer.current) clearTimeout(timer.current);
  }
  function getWorker() {
    if(worker.current) return worker.current;
    const engine=new Worker(new URL('./engine-worker.js',import.meta.url),{type:'module'});
    engine.onmessage=({data})=>{
      if(worker.current!==engine||(data.request_id!==undefined&&data.request_id!==requestSequence.current))return;
      if(data.type==='status') setStatus(data.status);
      if(data.type==='ready') {setEngineReady(true);setStatus('Local analysis engine ready.');}
      if(data.type==='result') acceptResult(data.result,true);
      if(data.type==='error') {
        setError('Local analysis failed: '+data.error);setBusy(false);setStatus('Analysis stopped. Your image was not uploaded.');
        if(timer.current) clearTimeout(timer.current);
        engine.terminate();worker.current=null;setEngineReady(false);
      }
    };
    engine.onerror=()=> {setError('The local engine could not start. Reload or try a sample.');setBusy(false);if(timer.current)clearTimeout(timer.current);engine.terminate();worker.current=null;setEngineReady(false);};
    worker.current=engine;return engine;
  }
  async function openSample(sample:Sample) {
    const sequence=++requestSequence.current;
    setBusy(true);setError('');setStatus('Opening sample…');
    try {
      const [resultResponse,imageResponse]=await Promise.all([fetch(sample.analysis_url),fetch(sample.image_url)]);
      if(!resultResponse.ok||!imageResponse.ok) throw new Error('Sample could not be loaded.');
      const result=await resultResponse.json();const image=await imageResponse.arrayBuffer();
      if(sequence!==requestSequence.current) return;
      bytes.current=image;setSampleId(sample.id);setFilename(sample.filename);acceptResult(result,false);
    } catch(e) {if(sequence===requestSequence.current){setError(e instanceof Error?e.message:'Sample failed.');setBusy(false);}}
  }
  useEffect(()=> {
    let mounted=true;
    fetch('/samples/manifest.json').then(r=>{if(!r.ok) throw new Error('Sample library unavailable.');return r.json();})
      .then(data=>{if(mounted){setSamples(data.samples);void openSample(data.samples[0]);}})
      .catch(e=>setError(e.message));
    fetch('/evidence/test.json').then(r=>r.ok?r.json():null).then(setBenchmark).catch(()=>{});
    return ()=> {mounted=false;worker.current?.terminate();if(timer.current)clearTimeout(timer.current);};
  },[]);
  const region=analysis?.regions.find(r=>r.id===selected);
  const witness=analysis?cancellationWitness(analysis):null;
  useEffect(()=>{
    if(!region) return;
    setManualCount(String(corrections[region.id]?.reviewed_count??region.baseline_count));
    setNote(corrections[region.id]?.note??'');
  },[selected,analysis]);
  function selectRegion(id:number) {setSelected(id);setZoom(false);setRun(analysis?.regions.find(r=>r.id===id)?.events[0]?.run_id??0);}
  async function analyzeFile(payload:ArrayBuffer) {
    const sequence=++requestSequence.current;
    setBusy(true);setError('');setStatus(engineReady?'Comparing segmentations…':'Preparing the local engine. First run downloads scientific libraries.');
    timer.current=setTimeout(()=>{const message='Analysis exceeded 90 seconds. Try a smaller field or use the local Python companion.';cancelAnalysis(message);setError(message);},90000);
    getWorker().postMessage({type:'analyze',buffer:payload.slice(0),request_id:sequence});
  }
  async function upload(file:File) {
    if(file.size>10*1024*1024){setError('Use a file smaller than 10 MB.');return;}
    if(!/\.(png|tiff?|jpe?g)$/i.test(file.name)){setError('Use a PNG, TIFF, or JPEG image.');return;}
    const sequence=++requestSequence.current;setBusy(true);setError('');setStatus('Reading image on your device…');
    try {
      const payload=await file.arrayBuffer();if(sequence!==requestSequence.current)return;
      bytes.current=payload;setFilename(file.name);setSampleId('');setAnalysis(null);setCorrections({});await analyzeFile(payload);
    }catch(e){if(sequence===requestSequence.current){setError(e instanceof Error?e.message:'Image could not be read.');setBusy(false);}}
  }
  function cancelAnalysis(message='Analysis cancelled. Your image stayed on this device.') {
    requestSequence.current++;
    worker.current?.terminate();worker.current=null;setEngineReady(false);setBusy(false);setStatus(message);
    if(timer.current) clearTimeout(timer.current);
  }
  function saveReview() {
    if(!region) return;
    try {
      const count=validateCount(manualCount);setError('');
      setCorrections(previous=>({...previous,[region.id]:{region_id:region.id,baseline_count:region.baseline_count,
        reviewed_count:count,note:note.trim().slice(0,500),at:new Date().toISOString()}}));
    } catch(e){setError(e instanceof Error?e.message:'Invalid count.');}
  }
  async function downloadAudit() {
    if(!analysis) return;
    const audit={...auditDocument(analysis,corrections,filename),schema_version:2,mask_modifications:patches.length>0,
      mask_review:editedMask?{count:editedCount,sha256_uint32_le:await maskHash(editedMask),export_format:'unsigned 32-bit label TIFF; zero=background',
        changes:patches.map(p=>({event:p.event,created_ids:p.created_ids,at:p.at,before_count:p.before_count,after_count:p.after_count,changed_pixels:p.indices.length})),
        semantics:'Human-confirmed replacements from actual sensitivity masks. No correctness or annotation claim. Tally corrections refer to the original baseline and do not modify this mask.'}:null};
    const url=URL.createObjectURL(new Blob([JSON.stringify(audit,null,2)],{type:'application/json'}));
    const a=document.createElement('a');a.href=url;a.download='nucleilens-review.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  const currentSample=samples.find(s=>s.id===sampleId);
  const viewBox=analysis?(zoom&&region?region.bbox.join(' ').split(' ').map((n,i)=>i<2?Number(n):Number(n)-region.bbox[i-2]).join(' '):`0 0 ${analysis.width} ${analysis.height}`):'0 0 696 520';
  const progress=analysis?Object.keys(corrections).length:0;
  return <>
    <header className="masthead"><a href="/" className="brand"><img src="/favicon.svg" alt=""/><span>Nuclei<span className="brand-light">Lens</span></span></a><span className="header-label">Microscopy, open to inspection</span><a href="#method" className="text-link">Method & evidence</a></header>
    <main>
      <section className="intro"><div><div className="eyebrow">NUCLEI COUNTING · HUMAN REVIEW</div><h1>See beyond<br className="mobile-break"/> the count.</h1><p>A total can look right while a merge and a split cancel out. Inspect the alternatives. Decide what belongs.</p></div><div className="privacy-note"><svg width="20" height="22" viewBox="0 0 20 22" fill="none" aria-hidden="true"><path d="M10 2 18 5v6c0 5-8 9-8 9S2 16 2 11V5z" stroke="currentColor" strokeWidth="1.5"/><path d="m6 10 3 3 5-6" stroke="currentColor" strokeWidth="1.5"/></svg><div><strong>Your images stay here.</strong><span>Analysis runs on your device.<br/>No account. No image upload.</span></div></div></section>
      <div className="toolbar"><div className="sample-buttons" role="group" aria-label="Real microscopy examples">{samples.map(s=><button key={s.id} className={sampleId===s.id?'sample selected':'sample'} onClick={()=>void openSample(s)} disabled={busy}>{s.title}<span>BBBC039</span></button>)}</div><div className="toolbar-actions"><input ref={input} type="file" accept=".png,.tif,.tiff,.jpg,.jpeg" hidden onChange={e=>{const file=e.target.files?.[0];if(file)void upload(file);e.target.value='';}}/><button className="primary" disabled={busy} onClick={()=>input.current?.click()}>Open your image</button></div></div>
      {error&&<div className="error" role="alert">{error}<button aria-label="Dismiss error" onClick={()=>setError('')}>×</button></div>}
      <div className="status-row" role="status"><span>{busy&&<span className="spinner"/>}{status}</span>{busy?<button className="text-link" onClick={()=>cancelAnalysis()}>Cancel</button>:<button className="text-link" disabled={!bytes.current} onClick={()=>bytes.current&&void analyzeFile(bytes.current)}>Rerun on this device</button>}</div>
      {analysis?.quality?.warning&&<div className="quality-warning" role="status">{analysis.quality.warning} Zero is a withheld result, not proof of an empty field.</div>}
      {analysis&&witness&&<section className="cancellation-witness" aria-label="Same count counterexample"><div><span className="eyebrow">A TOTAL CAN HIDE THE DIFFERENCE</span><strong>{analysis.raw_count} nuclei. In both runs.</strong><p>The same total contains a split alternative and a merge alternative. Inspect both; neither mask is automatically correct.</p></div><div role="group" aria-label="Inspect opposing alternatives">{([witness.split,witness.merge]).map((event,i)=><button key={i} onClick={()=>{setSelected(event.region_id);setRun(witness.run);setMode('outlines');setZoom(true);}}>{i===0?'Inspect split':'Inspect merge'} · {event.baseline_count} → {event.alternate_count}</button>)}</div></section>}
      <section className="workspace" aria-label="Nuclei review workspace">
        <div className="image-panel"><div className="panel-heading"><div><span className="eyebrow">FIELD OF VIEW</span><h2>{currentSample?.title??(filename?'Your field':'Microscopy field')}</h2></div><span className="metadata">{analysis?`${analysis.width} × ${analysis.height} px`:''}</span></div>
          <div className="viewer-controls"><div role="group" aria-label="Image layers">{(['outlines','edited','disagreement','image'] as const).map(m=><button key={m} className={mode===m?'active':''} onClick={()=>setMode(m)} disabled={m==='edited'&&!editedMask}>{m==='outlines'?'Nucleus outlines':m==='edited'?'Reviewed mask':m==='disagreement'?'Boundary variation':'Image only'}</button>)}</div><button aria-pressed={zoom} disabled={!region} onClick={()=>setZoom(!zoom)}>{zoom?'Full field':'Zoom to region'}</button></div>
          <div className="microscopy-frame" aria-busy={busy}>
            {analysis?<svg className="microscopy" viewBox={viewBox} role="img" aria-label={`Microscopy field with ${analysis.raw_count} baseline nuclei. Select a numbered region from the review queue.`}>
              <image href={png(analysis.image_png)} width={analysis.width} height={analysis.height}/>
              {mode==='outlines'&&<><image href={png(analysis.outline_pngs[0])} width={analysis.width} height={analysis.height}/>{run>0&&<image href={png(analysis.outline_pngs[run])} width={analysis.width} height={analysis.height}/>}</>}
              {mode==='edited'&&editedOutline&&<image href={editedOutline} width={analysis.width} height={analysis.height}/>}
              {mode==='disagreement'&&<image href={png(analysis.boundary_png)} width={analysis.width} height={analysis.height}/>}
              {region?.events.filter(e=>e.run_id===run).map((e,i)=><rect key={`event-${i}`} x={e.bbox[0]-2} y={e.bbox[1]-2} width={e.bbox[2]-e.bbox[0]+4} height={e.bbox[3]-e.bbox[1]+4} fill="none" stroke="#ffbe73" strokeDasharray="4 3" strokeWidth="1.5" pointerEvents="none"/>)}
              {analysis.regions.map(r=><g key={r.id} onClick={()=>selectRegion(r.id)} className="region-overlay"><rect x={r.bbox[0]+1} y={r.bbox[1]+1} width={r.bbox[2]-r.bbox[0]-2} height={r.bbox[3]-r.bbox[1]-2} fill="transparent" stroke={r.id===selected?'#ffbe73':r.score>0?'#dce4fa44':'#dce4fa14'} strokeWidth={r.id===selected?2:1}/><rect x={r.bbox[0]+6} y={r.bbox[1]+6} width="22" height="20" rx="4" fill={r.id===selected?'#ffbe73':'#151b26bb'}/><text x={r.bbox[0]+17} y={r.bbox[1]+20} textAnchor="middle" fontSize="12" fontFamily="monospace" fill={r.id===selected?'#151b26':'#fff'}>{r.id+1}</text></g>)}
            </svg>:<div className="empty-view"><span className="spinner"/><p>{busy?'Analyzing this field locally…':'Open an example or your image to begin.'}</p></div>}
          </div>
          <div className="image-legend">{mode==='edited'?<span><i className="purple"/>Reviewed mask · human choices</span>:<><span><i className="mint"/>Baseline</span><span><i className="amber"/>Alternative outline</span></>}<span>Regions use nucleus centroids</span></div>
          <div className="alternative-control"><label htmlFor="alternative">Compare a sensitivity run</label><select id="alternative" value={run} disabled={!analysis} onChange={e=>setRun(Number(e.target.value))}>{(analysis?.run_names??['baseline']).map((name,i)=><option value={i} key={name}>{name}{analysis?` · ${analysis.run_counts[i]} nuclei`:''}</option>)}</select></div>
          {analysis&&<section className="mask-review" aria-label="Mask correction"><div className="mask-summary"><div><span className="eyebrow">REVIEWED MASK · SEPARATE FROM TALLY</span><strong data-testid="mask-count">{editedCount??'—'} <small>instances</small></strong></div><div><button disabled={!patches.length||busy} onClick={undoMask}>Undo mask edit</button><button disabled={!editedMask||busy} onClick={downloadMask}>Export label TIFF</button></div></div><p role="status">{maskStatus}</p><p>Confirm only what you verify in the image. Replaces the whole graph component with its real alternative; overlapping retained nuclei are rejected. No automatic correction.</p><div className="mask-proposals" role="group" aria-label="Mask alternatives">{region?.events.filter(event=>event.run_id===run).map((event,index)=><button key={index} disabled={!masks||busy} onClick={()=>confirmMask(event)}>Confirm {event.kind} · {event.baseline_count} → {event.alternate_count}</button>)}{run===0&&<span>Select an alternate run or Inspect split / merge above.</span>}</div></section>}
          {currentSample&&<p className="sample-provenance">{currentSample.note} <a href="https://bbbc.broadinstitute.org/BBBC039" target="_blank" rel="noreferrer">Public dataset · CC0</a>. {live?'Recomputed locally.':'Precomputed from the actual image; use Rerun to verify.'}</p>}
        </div>
        <aside className="review-panel"><div className="count-strip"><div><span>BASELINE COUNT</span><strong>{analysis?.raw_count??'—'}</strong></div><div><span>TALLY TOTAL</span><strong>{analysis?reviewedTotal(analysis,corrections):'—'}</strong></div></div>
          <div className="sensitivity"><span>Nine-run sensitivity range</span><b>{analysis?analysis.sensitivity_range.join('–'):'—'}</b><p>A range of outcomes, not a confidence interval.</p></div>
          <div className="queue-header"><h2>Inspect the count</h2><span>{analysis?.flagged_regions??0} flags</span></div><p className="queue-explainer">Graph changes suggest ambiguity. A stable result can still be wrong.</p>
          <label className="policy-control" htmlFor="policy">Review ordering<select id="policy" value={policy} onChange={e=>setPolicy(e.target.value as 'graph'|'object_disagreement')}><option value="graph">Count-changing graph</option><option value="object_disagreement">Object disagreement · measured default</option></select></label>
          <div className="region-queue" role="group" aria-label="Review regions">{analysis?.regions.slice().sort((a,b)=>policy==='graph'?b.score-a.score:b.comparators.object_disagreement-a.comparators.object_disagreement).map(r=><button key={r.id} onClick={()=>selectRegion(r.id)} aria-pressed={selected===r.id} className={`queue-item ${r.id===selected?'current':''}`}><span className="region-number">{corrections[r.id]?'✓':String(r.id+1).padStart(2,'0')}</span><span className="queue-label"><strong>{r.reasons.length?r.reasons.join(' / '):'No count-changing probe'}</strong><small>{r.baseline_count} baseline · alternatives {r.candidate_counts.join(', ')}</small></span><span className="queue-score">{(policy==='graph'?r.score:r.comparators.object_disagreement).toFixed(2)}</span></button>)}</div>
          {region&&<div className="review-form"><div className="eyebrow">REGION {String(region.id+1).padStart(2,'0')}</div><h3>Keep the count, or correct it.</h3><p>Count nuclei whose centers fall within this region. Tally entries change only the tally total. Mask corrections and label exports are separate, in the image panel.</p><div className="candidate-pills" role="group" aria-label="Candidate counts">{region.candidate_counts.map(count=><button key={count} aria-pressed={manualCount===String(count)} onClick={()=>{setManualCount(String(count));const candidate=region.run_counts.findIndex(c=>c===count);setRun(Math.max(0,candidate));setNote(candidate===0?'Selected baseline; human confirmation still required.':`Selected ${analysis?.run_names[candidate]} candidate; human confirmation still required.`);}}>Use {count}{count===region.baseline_count?' · baseline':''}</button>)}</div><div className="count-input"><label htmlFor="count">Reviewed nuclei</label><input id="count" inputMode="numeric" type="number" min="0" max="1000" value={manualCount} onChange={e=>setManualCount(e.target.value)}/></div><label className="note-label" htmlFor="note">Review note <span>(optional)</span></label><textarea id="note" value={note} maxLength={500} onChange={e=>setNote(e.target.value)} placeholder="What did you verify in the image?" rows={2}/><div className="form-actions"><button className="primary" onClick={saveReview}>Confirm region</button>{corrections[region.id]&&<button onClick={()=>{setCorrections(prev=>{const next={...prev};delete next[region.id];return next;});setManualCount(String(region.baseline_count));setNote('');}}>Undo</button>}</div></div>}
          {region&&<details className="graph-detail"><summary>Why this region was flagged</summary>{region.events.length?<><p>These are graph disagreements, not error diagnoses. Inspect the corresponding outline before deciding.</p>{region.events.slice(0,5).map((event,index)=><button key={index} onClick={()=>{setRun(event.run_id);setMode('outlines');setZoom(true);}}><span>{analysis?.run_names[event.run_id]}</span><strong>{event.baseline_count} baseline → {event.alternate_count} alternative</strong><small>{event.kind}</small></button>)}</>:<p>No probe changed the object count here. Stable masks can still be wrong; review remains available.</p>}</details>}
          <div className="audit-footer"><span>{progress}/20 regions reviewed</span><button disabled={!analysis} onClick={()=>void downloadAudit()}>Export review JSON</button></div>
        </aside>
      </section>
      <section className="method" id="method"><div className="section-heading"><div><div className="eyebrow">THE COUNT IS ONLY THE BEGINNING</div><h2>One count. Different explanations.</h2></div><p>Our graph follows nuclei across segmentation variations. A one-to-many match suggests a split; a many-to-one match suggests a merge. Local disagreements remain visible even when their totals cancel.</p></div><div className="method-steps"><article><span>01</span><h3>Segment the field</h3><p>Background correction, thresholding, distance peaks, and watershed produce an inspectable classical baseline.</p></article><article><span>02</span><h3>Perturb the assumptions</h3><p>Nine deterministic runs change threshold, seed spacing, smoothing, and midtone intensity.</p></article><article><span>03</span><h3>Inspect the alternatives</h3><p>Object-overlap graphs reveal count-changing regions. You make the review decision and keep an audit trail.</p></article></div></section>
      <section className="evidence"><div><div className="eyebrow">MEASURED, NOT ASSUMED</div><h2>Does the review queue find actual errors?</h2><p>We compare equal review budgets on the official BBBC039 splits. The benchmark includes random review, pixel and object disagreement, local count variation, and shape flags.</p><button className="text-link" onClick={()=>setShowEvidence(!showEvidence)} aria-expanded={showEvidence}>{showEvidence?'Hide benchmark detail':'Inspect benchmark detail'}</button></div><div className="evidence-summary">{benchmark?<><span>FROZEN TEST · {benchmark.n_images} REAL FIELDS</span><strong>{Math.round(benchmark.methods.object_disagreement.capture_at_20_percent*100)}% <small>error capture</small></strong><p>Object-disagreement queue, reviewing 4 of 20 regions. Random captures 20%. The default queue was selected on validation, before test access. Graph ordering is available for comparison. This is simulated error capture, not measured human time saved.</p></>:<><span>COMPARATIVE EVALUATION</span><h3>Results are being measured.</h3><p>Initial training results do not establish graph superiority. Full validation remains the decision gate.</p></>}</div>
        {showEvidence&&<div className="benchmark-detail">{benchmark?<table><caption>Actual held-out test results · FP + FN at object IoU ≥ 0.5</caption><thead><tr><th>Review policy</th><th>Errors captured at 20% budget</th><th>Bootstrap 95% interval</th></tr></thead><tbody>{Object.entries(benchmark.methods).map(([name,value])=>{const v=value as {capture_at_20_percent:number;capture_ci95:number[]};return <tr key={name}><td>{name.replaceAll('_',' ')}</td><td>{(v.capture_at_20_percent*100).toFixed(1)}%</td><td>{v.capture_ci95.map(n=>(n*100).toFixed(1)+'%').join('–')}</td></tr>;})}</tbody></table>:<p>Benchmark files will appear when the full validation run finishes.</p>}<p>False positives and missed reference nuclei are assigned to fixed image tiles by centroid. Ties are averaged, not reordered to favor a method. Annotations are loaded after inference. Configuration and source hashes were frozen before the 50-image test run; all failures are retained. Validation guided development.</p>{currentSample&&<p>Current reference sample: annotated count {currentSample.reference_count}; baseline instance F1 {currentSample.f1.toFixed(3)}. Annotation count is a benchmark reference, not a model output.</p>}</div>}
      </section>
      <section className="limitations"><h2>What this cannot tell you</h2><p>Agreement does not guarantee correctness. This prototype is evaluated on one U2OS nucleus-stained fluorescence dataset, not general microscopy or clinical diagnosis. Review flags indicate sensitivity, not proven mistakes. Real review-time savings have not been measured.</p><p>Single-field PNG, TIFF, or JPEG · up to 10 MB and 1,048,576 pixels. Color images are converted to grayscale. TIFF preserves the original numeric precision; browser PNG and JPEG decoding uses 8-bit grayscale. First live analysis loads a scientific runtime; bundled examples open immediately.</p></section>
    </main><footer><span>NucleiLens · Research prototype · EurekaDev 2026</span><div><a href="https://bbbc.broadinstitute.org/BBBC039" target="_blank" rel="noreferrer">Dataset & source</a><a href="https://github.com/dumbthing999-ui/nuclei-lens" target="_blank" rel="noreferrer">Source code</a><a href="/licenses/manifest.json" target="_blank" rel="noreferrer">Dependency notices</a><a href="/evidence/test.json" target="_blank" rel="noreferrer">Evaluation JSON</a></div></footer>
  </>;
}
createRoot(document.getElementById('root')!).render(<App/>);
