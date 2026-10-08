import {readLabelTiff} from './labelImport';
import {maskHash} from './masks';
import type {ExternalMaskSource} from './maskComparison';

export const MODEL_EXAMPLE_INPUT_HASH='cf5b84a8d7158291c1f448bf16ec4add17aa88772c54066ceda4651deb7561f8';
const base='/model-examples/training-001/';
const examples=[
  {file:'cellpose_nuclei_mask.tif',name:'Cellpose nuclei · real precomputed example',model:'Cellpose nuclei',version:'3.1.1.2',fileHash:'a7f2ff83ffdfbc9dc732e7eb0761896328fae1020e940536b3ab2944da4e403b',pixelHash:'5fe3c6abf04a14396272230148546eb1645734b2b09f5d7c9ea594a766756475'},
  {file:'stardist_2d_fluo_mask.tif',name:'StarDist fluorescence · real precomputed example',model:'StarDist 2D_versatile_fluo',version:'0.9.2',fileHash:'d5546b4b0597533723cf8bae18ef636e0de0cf5f02b3cf8ffd41c4728b5f5fe1',pixelHash:'658f8368565602cea32f8a6a2e976dfe6c3c69afc98475cb7f2ecf5ee35f393b'},
];
export async function loadModelExamples(inputHash:string,width:number,height:number):Promise<{mask:Uint32Array;source:ExternalMaskSource}[]> {
  if(inputHash!==MODEL_EXAMPLE_INPUT_HASH||width!==696||height!==520)throw Error('These predictions belong only to the equal-count sample field.');
  return Promise.all(examples.map(async example=>{
    const response=await fetch(base+example.file,{signal:AbortSignal.timeout(15000)});
    if(!response.ok)throw Error('Model example could not be loaded. You can still import your own label TIFF.');
    const bytes=await response.arrayBuffer();
    const fileHash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');
    if(fileHash!==example.fileHash)throw Error('Model example file integrity check failed.');
    const mask=await readLabelTiff(bytes,width,height),pixelHash=await maskHash(mask);
    if(pixelHash!==example.pixelHash)throw Error('Model example label integrity check failed.');
    return {mask,source:{kind:'external-label-tiff' as const,name:example.name,file_sha256:fileHash,mask_sha256_uint32_le:pixelHash,
      bundled_example:{model:example.model,version:example.version,provenance_url:base+'provenance.json',input_file_sha256:'f9a51ae558e53416980ca152c740ad9dced85eedbd105261841139aada16b77d'}}};
  }));
}
