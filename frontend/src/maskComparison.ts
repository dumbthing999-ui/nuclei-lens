import type {GraphEvent} from './types';
import {measureMask} from './measurements';

export interface ExternalMaskSource {
  kind: 'external-label-tiff'; name: string; file_sha256: string; mask_sha256_uint32_le: string;
  bundled_example?: {model:string;version:string;provenance_url:string;input_file_sha256:string};
}
export interface MaskComparison {
  baseline_count: number; alternative_count: number; same_total: boolean;
  segmentation_equal_up_to_ids: boolean; foreground_difference_pixels: number;
  label_value_difference_pixels: number; overlap_min_area_threshold: number;
  events: GraphEvent[];
}

/** Sparse correspondence hypotheses, not annotated errors or automatic consensus. */
export function compareMasks(baseline: Uint32Array, alternative: Uint32Array, width: number, height: number): MaskComparison {
  if (baseline.length !== alternative.length) throw new Error('Mask dimensions differ.');
  const before = measureMask(baseline,width,height), after = measureMask(alternative,width,height);
  const beforeById = new Map(before.objects.map(row=>[row.label,row])), afterById = new Map(after.objects.map(row=>[row.label,row]));
  const intersections = new Map<number,Map<number,number>>();
  let pairs = 0, foregroundDifference = 0, labelDifference = 0;
  for (let i=0; i<baseline.length; i++) {
    const a=baseline[i], b=alternative[i];
    foregroundDifference += Number(Boolean(a)!==Boolean(b)); labelDifference += Number(a!==b);
    if (!a || !b) continue;
    let row=intersections.get(a); if(!row){row=new Map();intersections.set(a,row);}
    if(!row.has(b) && ++pairs>200000) throw new Error('Mask correspondence is too fragmented. Use a smaller field.');
    row.set(b,(row.get(b)??0)+1);
  }
  const nodes=[...before.objects.map(row=>({id:row.label,side:0})),...after.objects.map(row=>({id:row.label,side:1}))];
  const indices=new Map(nodes.map((node,index)=>[`${node.side}:${node.id}`,index]));
  const parent=nodes.map((_,i)=>i);
  function root(i:number):number {while(parent[i]!==i){parent[i]=parent[parent[i]];i=parent[i];}return i;}
  const threshold=0.45;
  for(const [a,row] of intersections) for(const [b,size] of row) {
    if(size/Math.min(beforeById.get(a)!.area_px,afterById.get(b)!.area_px)>=threshold) {
      const left=root(indices.get(`0:${a}`)!), right=root(indices.get(`1:${b}`)!); parent[right]=left;
    }
  }
  const groups=new Map<number,{baseline:number[];alternate:number[]}>();
  nodes.forEach((node,index)=>{const key=root(index);let group=groups.get(key);if(!group){group={baseline:[],alternate:[]};groups.set(key,group);}
    (node.side===0?group.baseline:group.alternate).push(node.id);});
  const events:GraphEvent[]=[];
  let identical=before.object_count===after.object_count && foregroundDifference===0;
  for(const group of groups.values()) {
    const a=group.baseline.length,b=group.alternate.length;
    const exact=a===1 && b===1 && intersections.get(group.baseline[0])?.get(group.alternate[0])===beforeById.get(group.baseline[0])!.area_px &&
      beforeById.get(group.baseline[0])!.area_px===afterById.get(group.alternate[0])!.area_px;
    if(exact) continue;
    identical=false;
    if(events.length>=2000) throw new Error('More than 2,000 differing components. Use a smaller field.');
    const boxes=[...group.baseline.map(id=>beforeById.get(id)!.bbox_xyxy),...group.alternate.map(id=>afterById.get(id)!.bbox_xyxy)];
    const kind=a===1&&b>1?'split alternative':a>1&&b===1?'merge alternative':!a?'addition alternative':!b?'loss alternative':a===1&&b===1?'boundary alternative':'complex alternative';
    events.push({kind,baseline_count:a,alternate_count:b,baseline_ids:group.baseline,alternate_ids:group.alternate,run_id:-1,
      magnitude:Math.abs(a-b),bbox:[Math.min(...boxes.map(r=>r[0])),Math.min(...boxes.map(r=>r[1])),Math.max(...boxes.map(r=>r[2])),Math.max(...boxes.map(r=>r[3]))]});
  }
  events.sort((a,b)=>b.magnitude-a.magnitude||a.bbox[1]-b.bbox[1]||a.bbox[0]-b.bbox[0]);
  return {baseline_count:before.object_count,alternative_count:after.object_count,same_total:before.object_count===after.object_count,
    segmentation_equal_up_to_ids:identical,foreground_difference_pixels:foregroundDifference,label_value_difference_pixels:labelDifference,
    overlap_min_area_threshold:threshold,events};
}
