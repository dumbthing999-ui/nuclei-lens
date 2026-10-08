import {useMemo, useRef, useState, useEffect, useId} from 'react';
import type {Analysis, GraphEvent} from './types';
import {maskHash, maskOutline, type MaskPatch} from './masks';
import {measureMask, measurementsCsv} from './measurements';
import {compareMasks, type ExternalMaskSource, type MaskComparison} from './maskComparison';
import {readLabelTiff} from './labelImport';
import {loadModelExamples,MODEL_EXAMPLE_INPUT_HASH} from './modelExamples';

interface ImportedMask {mask:Uint32Array;source:ExternalMaskSource;comparison:MaskComparison;}
interface Props {
  analysis:Analysis; baseline:Uint32Array; reviewed:Uint32Array; patches:MaskPatch[]; busy:boolean;
  onConfirm:(event:GraphEvent,mask:Uint32Array,source:ExternalMaskSource)=>void;
}
function download(text:string,name:string,type:string) {
  const url=URL.createObjectURL(new Blob([text],{type})),link=document.createElement('a');
  link.href=url;link.download=name;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
const hashBytes=async(bytes:ArrayBuffer)=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');

export function QualityReview({analysis,baseline,reviewed,patches,busy,onConfirm}:Props) {
  const clipId=useId();
  const [imports,setImports]=useState<ImportedMask[]>([]),[selected,setSelected]=useState(0);
  const [loading,setLoading]=useState(false),[error,setError]=useState('');
  const [name,setName]=useState('');
  const [focus,setFocus]=useState<number|null>(null),[page,setPage]=useState(0);
  const input=useRef<HTMLInputElement>(null),generation=useRef(0);
  useEffect(()=>()=>{generation.current++;},[]);
  const before=useMemo(()=>measureMask(baseline,analysis.width,analysis.height),[baseline,analysis.width,analysis.height]);
  const current=useMemo(()=>measureMask(reviewed,analysis.width,analysis.height),[reviewed,analysis.width,analysis.height]);
  const currentDifference=useMemo(()=>{try{return compareMasks(baseline,reviewed,analysis.width,analysis.height);}catch{return null;}},[baseline,reviewed,analysis.width,analysis.height]);
  const active=imports[selected];
  const pairwise=useMemo(()=>imports.flatMap((a,i)=>imports.slice(i+1).map(b=>{
    try{return {first:a.source.name,second:b.source.name,comparison:compareMasks(a.mask,b.mask,analysis.width,analysis.height)};}
    catch{return {first:a.source.name,second:b.source.name,comparison:null};}
  })),[imports,analysis.width,analysis.height]);
  const importedOutline=useMemo(()=>active?maskOutline(active.mask,analysis.width,analysis.height):null,[active?.mask,analysis.width,analysis.height]);
  const focused=focus===null?null:active?.comparison.events[focus];
  const box=focused?.bbox??[0,0,analysis.width,analysis.height];
  const previewBox=[Math.max(0,box[0]-6),Math.max(0,box[1]-6),Math.min(analysis.width,box[2]+6),Math.min(analysis.height,box[3]+6)];
  async function importMask(file:File) {
    if(imports.length>=3){setError('Compare up to three external masks per field. Remove one before adding another.');return;}
    if(file.size>10*1024*1024||!/\.tiff?$/i.test(file.name)){setError('Use an unsigned instance-label TIFF smaller than 10 MB.');return;}
    const token=++generation.current;setLoading(true);setError('');
    try {
      const bytes=await file.arrayBuffer(),mask=await readLabelTiff(bytes,analysis.width,analysis.height);
      const source:ExternalMaskSource={kind:'external-label-tiff',name:(name.trim()||file.name).slice(0,120),file_sha256:await hashBytes(bytes),mask_sha256_uint32_le:await maskHash(mask)};
      const comparison=compareMasks(baseline,mask,analysis.width,analysis.height);
      if(token!==generation.current)return;
      if(imports.some(value=>value.source.mask_sha256_uint32_le===source.mask_sha256_uint32_le))throw new Error('This exact label map is already loaded.');
      setImports(previous=>[...previous,{mask,source,comparison}]);setSelected(imports.length);setName('');setFocus(null);setPage(0);
    }catch(e){if(token===generation.current)setError(e instanceof Error?e.message:'Label TIFF could not be read.');}
    finally{if(token===generation.current)setLoading(false);}
  }
  async function exportCsv() {
    try {download(measurementsCsv(current,await maskHash(reviewed)),'nucleilens-measurements.csv','text/csv');}
    catch(e){setError(e instanceof Error?e.message:'Measurement export failed.');}
  }
  async function importExamples() {
    const token=++generation.current;setLoading(true);setError('');
    try{
      const loaded=await loadModelExamples(analysis.input_hash,analysis.width,analysis.height);
      const additions=loaded.filter(value=>!imports.some(existing=>existing.source.mask_sha256_uint32_le===value.source.mask_sha256_uint32_le))
        .map(value=>({...value,comparison:compareMasks(baseline,value.mask,analysis.width,analysis.height)}));
      if(imports.length+additions.length>3)throw Error('Remove a loaded mask to make room for both model examples.');
      if(token!==generation.current)return;
      if(!additions.length)throw Error('Both model examples are already loaded.');
      setImports(previous=>[...previous,...additions]);setSelected(imports.length);setFocus(null);setPage(0);
    }catch(e){if(token===generation.current)setError(e instanceof Error?e.message:'Model examples could not be loaded.');}
    finally{if(token===generation.current)setLoading(false);}
  }
  async function exportReport() {
    try {
      const [baselineHash,reviewedHash]=await Promise.all([maskHash(baseline),maskHash(reviewed)]);
      const report={schema_version:1,kind:'nucleilens-segmentation-qa',created_at:new Date().toISOString(),
        input_hash:analysis.input_hash,width:analysis.width,height:analysis.height,configuration:analysis.config,
        coordinate_system:'Pixel-edge coordinates; centroids are means of pixel centers (x+0.5, y+0.5). Bounding-box maxima are exclusive.',
        perimeter_definition:'Four-neighbor exposed pixel-edge count; not an isotropic Euclidean perimeter estimate.',
        baseline:{sha256_uint32_le:baselineHash,measurements:before},reviewed:{sha256_uint32_le:reviewedHash,measurements:current},
        original_vs_reviewed:currentDifference,
        comparison_limitation:currentDifference?null:'Detailed correspondence exceeds supported bounds; measurements and hashes remain available.',
        external_masks:imports.map(value=>({source:value.source,comparison_to_original_baseline:value.comparison})),
        external_pairwise_comparisons:pairwise,
        changes:patches.map(p=>({event:p.event,source:p.source??{kind:'sensitivity-run',run_id:p.event.run_id},created_ids:p.created_ids,
          at:p.at,before_count:p.before_count,after_count:p.after_count,changed_label_pixels:p.indices.length})),
        limitations:['No ground truth was loaded: disagreements and equal counts do not establish accuracy or biological errors.',
          'Imported sources are user-described. Model identity, weights and image alignment are not independently verified by an imported TIFF.',
          'Measurements describe label geometry in pixels, not calibrated physical size, intensity, clinical validity or proven human benefit.',
          'Label-value differences include harmless ID renumbering; segmentation_equal_up_to_ids distinguishes exact partition equality.',
          'All labels with the same positive ID form one instance, even if disconnected. No automatic correction or consensus is performed.'],
        prior_art:['https://doi.org/10.3389/fgene.2025.1547788','https://cellpose.readthedocs.io/en/latest/outputs.html','https://github.com/stardist/stardist','https://napari.org/dev/howtos/layers/labels.html']};
      download(JSON.stringify(report,null,2),'nucleilens-segmentation-qa.json','application/json');
    }catch(e){setError(e instanceof Error?e.message:'QA report export failed.');}
  }
  return <section className="quality-review" aria-label="Segmentation quality review">
    <div className="quality-heading"><div><span className="eyebrow">BEYOND THE TOTAL</span><h3>Measure the mask you reviewed.</h3></div><div className="quality-actions">
      <button disabled={busy||loading} onClick={()=>void exportCsv()}>Export measurements CSV</button>
      <button disabled={busy||loading} onClick={()=>void exportReport()}>Export segmentation QA report</button>
    </div></div>
    <p>Measurements recalculate after every mask edit and undo. Review-tally entries do not change geometry. Areas use pixels; no physical calibration or intensity measurement is inferred.</p>
    <dl className="measurement-summary" data-testid="measurement-summary"><div><dt>Instances · original → reviewed</dt><dd>{before.object_count} → {current.object_count}</dd></div>
      <div><dt>Foreground area · px²</dt><dd>{before.foreground_pixels} → {current.foreground_pixels}</dd></div>
      <div><dt>Mean instance area · px²</dt><dd>{before.mean_area_px?.toFixed(1)??'—'} → {current.mean_area_px?.toFixed(1)??'—'}</dd></div></dl>
    <p className="partition-status" role="status">{!currentDifference?'Detailed correspondence exceeds supported bounds; measurements and hashes remain available.':currentDifference.same_total&&!currentDifference.segmentation_equal_up_to_ids?
      'The reviewed mask has the same total but a different segmentation. Equal counts do not establish equal accuracy.':
      currentDifference.segmentation_equal_up_to_ids?'Reviewed and original segmentations match, allowing harmless label-ID renumbering.':'The reviewed instance count and segmentation differ from the original. Accuracy remains unvalidated.'}</p>
    <details><summary>Per-instance measurements ({current.object_count})</summary><div className="measurement-table" role="region" aria-label="Per-instance measurement table" tabIndex={0}><table><caption>First {Math.min(current.objects.length,40)} instances; CSV includes all. Centroids use pixel centers; perimeter counts exposed grid edges.</caption><thead><tr><th>ID</th><th>Area px²</th><th>Centroid x, y px</th><th>Grid perimeter px</th><th>At border</th></tr></thead><tbody>
      {current.objects.slice(0,40).map(row=><tr key={row.label}><td>{row.label}</td><td>{row.area_px}</td><td>{row.centroid_x_px.toFixed(2)}, {row.centroid_y_px.toFixed(2)}</td><td>{row.grid_edge_perimeter_px}</td><td>{row.touches_image_border?'Yes':'No'}</td></tr>)}
    </tbody></table></div></details>
    <details className="external-mask-review"><summary>Compare masks from another model or editor</summary>
      <p>Import already aligned, uncompressed, single-channel instance-label TIFFs from a model or editor. Cellpose and StarDist inference runs separately; this browser does not run their networks. Zero is background; positive integer IDs identify objects. Same dimensions alone do not prove image alignment.</p>
      {analysis.input_hash===MODEL_EXAMPLE_INPUT_HASH&&<div className="model-example"><button disabled={busy||loading} onClick={()=>void importExamples()}>Load real Cellpose + StarDist examples</button><p>Actual predictions on this CC0 training field: both return 68 instances. Explore their different masks; neither is ground truth. Precomputed locally, not neural inference in your browser. <a href="/model-examples/training-001/provenance.json" target="_blank" rel="noreferrer">Model versions, weights and hashes</a></p></div>}
      {pairwise.map(pair=><p className="pairwise-status" role="status" key={pair.first+' / '+pair.second}>{pair.first} vs {pair.second}: {!pair.comparison?'Pairwise correspondence exceeds supported bounds.':<>{pair.comparison.baseline_count} vs {pair.comparison.alternative_count} instances; {pair.comparison.segmentation_equal_up_to_ids?'same segmentation allowing ID renumbering':pair.comparison.same_total?'equal total, different segmentation':'different total and segmentation'}. {pair.comparison.events.length} differing components; {pair.comparison.foreground_difference_pixels} pixels differ in foreground assignment. This does not identify the more accurate model.</>}</p>)}
      <label htmlFor="external-mask-name">Source name (optional, user-described)</label><input id="external-mask-name" value={name} maxLength={120} onChange={e=>setName(e.target.value)} placeholder="For example: Cellpose nuclei, settings A"/>
      <input ref={input} type="file" accept=".tif,.tiff" hidden onChange={e=>{const file=e.target.files?.[0];if(file)void importMask(file);e.target.value='';}}/>
      <button disabled={busy||loading||imports.length>=3} onClick={()=>input.current?.click()}>{loading?'Reading label TIFF…':'Add external label TIFF'}</button>
      {imports.length>0&&<div className="import-select"><label htmlFor="external-mask-select">Loaded mask</label><select id="external-mask-select" value={selected} onChange={e=>{setSelected(Number(e.target.value));setFocus(null);setPage(0);}}>{imports.map((value,index)=><option key={value.source.mask_sha256_uint32_le} value={index}>{value.source.name}</option>)}</select><button disabled={busy||loading} onClick={()=>{setImports(imports.filter((_,i)=>i!==selected));setSelected(0);setFocus(null);setPage(0);}}>Remove selected mask</button></div>}
      {active&&<><p role="status">Original: {active.comparison.baseline_count} instances. Imported: {active.comparison.alternative_count}. {active.comparison.segmentation_equal_up_to_ids?'Exact segmentation match, allowing ID renumbering.':active.comparison.same_total?'Same total; different segmentation. Neither mask is verified truth.':'Different instance count and segmentation. Neither mask is verified truth.'}</p>
        <p>{active.comparison.events.length} differing correspondence components. Edges use intersection / smaller-object area ≥ 0.45. Boundary differences and missing overlaps also appear. Compared with the original baseline; previously edited or conflicting components are rejected. Components with more than 32 total IDs are inspect/export only; use an existing editor for those.</p>
        <div className="external-preview"><svg viewBox={`${previewBox[0]} ${previewBox[1]} ${previewBox[2]-previewBox[0]} ${previewBox[3]-previewBox[1]}`} role="img" aria-label="Current microscopy image with original baseline in mint and imported mask in purple. Correspondence is a hypothesis, not correctness.">
          <defs><clipPath id={clipId}><rect x={previewBox[0]} y={previewBox[1]} width={previewBox[2]-previewBox[0]} height={previewBox[3]-previewBox[1]}/></clipPath></defs><g clipPath={`url(#${clipId})`}>
          <image href={`data:image/png;base64,${analysis.image_png}`} width={analysis.width} height={analysis.height}/>
          <image href={`data:image/png;base64,${analysis.outline_pngs[0]}`} width={analysis.width} height={analysis.height}/>
          {importedOutline&&<image href={importedOutline} width={analysis.width} height={analysis.height}/>}</g></svg></div>
        <p>Mint: original baseline. Purple: imported mask. Inspect the image before confirming a component.</p>
        <div className="external-proposals" role="region" aria-label="External correspondence components" tabIndex={0}>{active.comparison.events.slice(page*30,page*30+30).map((event,offset)=>{const index=page*30+offset;const applied=patches.some(p=>p.source?.mask_sha256_uint32_le===active.source.mask_sha256_uint32_le&&JSON.stringify(p.event.baseline_ids)===JSON.stringify(event.baseline_ids)&&JSON.stringify(p.event.alternate_ids)===JSON.stringify(event.alternate_ids));return <div key={index}><span>Region {event.bbox[0]}, {event.bbox[1]}–{event.bbox[2]}, {event.bbox[3]}</span><button disabled={busy||loading} aria-pressed={focus===index} onClick={()=>setFocus(index)}>Inspect external component {index+1}</button><button disabled={busy||loading||focus!==index||applied||event.baseline_count+event.alternate_count>32} onClick={()=>onConfirm(event,active.mask,active.source)}>{event.baseline_count+event.alternate_count>32?'Large component: inspect/export only':applied?'Component applied':`Confirm external ${event.kind} · ${event.baseline_count} → ${event.alternate_count}`}</button></div>;})}</div>
        {active.comparison.events.length>30&&<div className="component-pages"><button disabled={page===0||busy||loading} onClick={()=>{setPage(page-1);setFocus(null);}}>Previous components</button><span>Page {page+1} of {Math.ceil(active.comparison.events.length/30)}</span><button disabled={(page+1)*30>=active.comparison.events.length||busy||loading} onClick={()=>{setPage(page+1);setFocus(null);}}>Next components</button></div>}
        <p>Imported masks are cleared when opening another field. Export the QA report before leaving this field.</p></>}
    </details>
    {error&&<p role="alert" className="quality-error">{error}<button aria-label="Dismiss import error" onClick={()=>setError('')}>×</button></p>}
  </section>;
}
