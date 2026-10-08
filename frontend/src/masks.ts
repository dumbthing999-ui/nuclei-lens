import type {Analysis, GraphEvent} from './types';
import type {ExternalMaskSource} from './maskComparison';

export interface MaskPatch {
  indices:Uint32Array; before:Uint32Array;
  event:GraphEvent; created_ids:number[]; at:string;
  before_count:number; after_count:number;
  source?:ExternalMaskSource;
}
export const countInstances=(mask:Uint32Array)=>new Set(mask.filter(id=>id!==0)).size;

export async function decodeLabelMaps(analysis:Analysis):Promise<Uint32Array[]> {
  const encoded=analysis.label_maps;
  const pixels=analysis.width*analysis.height;
  if(!encoded||encoded.encoding!=='zlib-base64-uint32-le'||encoded.runs.length!==analysis.run_counts.length||pixels>1048576||pixels<1) throw new Error('Lossless masks unavailable. Rerun the image on this device.');
  return Promise.all(encoded.runs.map(async(text,index)=>{
    if(text.length>pixels*8+1024)throw new Error('Mask asset exceeds the bounded size.');
    const input=Uint8Array.from(atob(text),c=>c.charCodeAt(0));
    const stream=new Blob([input]).stream().pipeThrough(new DecompressionStream('deflate'));
    const reader=stream.getReader();const bytes=new Uint8Array(pixels*4);let offset=0;
    try {while(true){const {done,value}=await reader.read();if(done)break;if(offset+value.length>bytes.length)throw new Error('Expanded mask exceeds image dimensions.');bytes.set(value,offset);offset+=value.length;}}
    finally {await reader.cancel();}
    if(offset!==bytes.length)throw new Error('Mask dimensions do not match the field.');
    const view=new DataView(bytes.buffer);const mask=Uint32Array.from({length:pixels},(_,i)=>view.getUint32(i*4,true));
    if(countInstances(mask)!==analysis.run_counts[index])throw new Error('Mask labels disagree with the reported run count.');
    return mask;
  }));
}

export function applyMaskProposal(current:Uint32Array,baseline:Uint32Array,alternate:Uint32Array,event:GraphEvent):{mask:Uint32Array;patch:MaskPatch} {
  if(!current.length||current.length!==baseline.length||current.length!==alternate.length)throw new Error('Mask dimensions differ.');
  const valid=(ids:number[])=>Array.isArray(ids)&&ids.every(id=>Number.isInteger(id)&&id>0&&id<=0xffffffff)&&new Set(ids).size===ids.length;
  if(!valid(event.baseline_ids)||!valid(event.alternate_ids)||event.baseline_ids.length!==event.baseline_count||event.alternate_ids.length!==event.alternate_count||(!event.baseline_count&&!event.alternate_count))throw new Error('Invalid graph component.');
  const removed=new Set(event.baseline_ids),added=new Set(event.alternate_ids);
  const seenRemoved=new Set<number>(),seenAdded=new Set<number>();let max=0;
  for(let i=0;i<current.length;i++){
    max=Math.max(max,current[i]);
    if(removed.has(baseline[i]))seenRemoved.add(baseline[i]);
    if(added.has(alternate[i]))seenAdded.add(alternate[i]);
    if((removed.has(baseline[i])||removed.has(current[i]))&&baseline[i]!==current[i])throw new Error('This baseline component was already edited. Undo overlapping edits first.');
    if(added.has(alternate[i])&&current[i]!==0&&!removed.has(current[i]))throw new Error('Alternative overlaps a retained nucleus. No pixels were changed.');
  }
  if(seenRemoved.size!==removed.size||seenAdded.size!==added.size)throw new Error('Graph component IDs are missing from the source mask.');
  if(max+added.size>0xffffffff)throw new Error('Instance ID space exhausted.');
  const mapping=new Map(event.alternate_ids.map((id,index)=>[id,max+index+1]));
  const next=current.slice(),indices:number[]=[],before:number[]=[];
  for(let i=0;i<current.length;i++){
    const value=mapping.get(alternate[i])??(removed.has(current[i])?0:current[i]);
    if(value!==current[i]){indices.push(i);before.push(current[i]);next[i]=value;}
  }
  if(!indices.length)throw new Error('This proposal changes no mask pixels.');
  const beforeCount=countInstances(current),afterCount=countInstances(next);
  if(afterCount-beforeCount!==added.size-removed.size)throw new Error('Instance count integrity check failed.');
  return {mask:next,patch:{indices:Uint32Array.from(indices),before:Uint32Array.from(before),event:structuredClone(event),created_ids:[...mapping.values()],at:new Date().toISOString(),before_count:beforeCount,after_count:afterCount}};
}

export function undoMaskPatch(mask:Uint32Array,patch:MaskPatch):Uint32Array {
  const next=mask.slice();for(let i=0;i<patch.indices.length;i++)next[patch.indices[i]]=patch.before[i];return next;
}

/** Lossless single-channel unsigned 32-bit label TIFF, no compression. */
export function labelTiff(mask:Uint32Array,width:number,height:number):Uint8Array<ArrayBuffer> {
  if(!Number.isInteger(width)||!Number.isInteger(height)||width<1||height<1||width*height!==mask.length||mask.length>1048576)throw new Error('Invalid label TIFF dimensions.');
  const tags=10,offset=Math.ceil((8+2+tags*12+4)/4)*4;
  const bytes=new Uint8Array(offset+mask.length*4),view=new DataView(bytes.buffer);
  bytes.set([73,73]);view.setUint16(2,42,true);view.setUint32(4,8,true);view.setUint16(8,tags,true);
  const entries=[[256,4,width],[257,4,height],[258,3,32],[259,3,1],[262,3,1],[273,4,offset],[277,3,1],[278,4,height],[279,4,mask.length*4],[339,3,1]];
  entries.forEach(([tag,type,value],i)=>{const p=10+i*12;view.setUint16(p,tag,true);view.setUint16(p+2,type,true);view.setUint32(p+4,1,true);if(type===3)view.setUint16(p+8,value,true);else view.setUint32(p+8,value,true);});
  for(let i=0;i<mask.length;i++)view.setUint32(offset+i*4,mask[i],true);
  return bytes;
}

export function maskOutline(mask:Uint32Array,width:number,height:number):string {
  const canvas=document.createElement('canvas');canvas.width=width;canvas.height=height;
  const context=canvas.getContext('2d');if(!context)throw new Error('Image rendering unavailable.');
  const image=context.createImageData(width,height);
  for(let y=0;y<height;y++)for(let x=0;x<width;x++){
    const i=y*width+x,id=mask[i];if(!id)continue;
    if(x===0||y===0||x===width-1||y===height-1||[mask[i-1],mask[i+1],mask[i-width],mask[i+width]].some(n=>n!==id))image.data.set([220,165,255,255],i*4);
  }
  context.putImageData(image,0,0);return canvas.toDataURL();
}
export async function maskHash(mask:Uint32Array):Promise<string>{
  const bytes=new Uint8Array(mask.length*4);const view=new DataView(bytes.buffer);for(let i=0;i<mask.length;i++)view.setUint32(i*4,mask[i],true);
  return [...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(n=>n.toString(16).padStart(2,'0')).join('');
}
